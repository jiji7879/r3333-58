#!/usr/bin/env python3
"""Search zbMATH Open, the reviewing and bibliographic database of mathematics, through its
official REST API (api.zbmath.org). Standard library only.

    zbmath.py search QUERY [--limit N] [--page N]   documents matching a zbMATH query, 10 per page,
                                                    with the total: Zbl number, year, authors, title,
                                                    source, MSC codes, whether a review is available
    zbmath.py show ID [--full]                      one document: authors with their author codes,
                                                    source, MSC 2020 codes, keywords, DOI and links, the
                                                    review or summary (cut at 3000 characters unless
                                                    --full)
    zbmath.py authors QUERY [--limit N] [--page N]  author profiles matching a name or an author query
    zbmath.py author CODE                           one profile (wiles.andrew-j): names used, documents
                                                    by role, main fields and awards. With at most 500
                                                    linked documents, list the 10 most recent
    zbmath.py msc CODE|WORDS [--limit N]            an MSC 2020 code (11G05, 11G, 11) with its subclasses
                                                    and number of documents, or the codes whose
                                                    description contains WORDS

QUERY is zbMATH's search syntax. Fields for documents: au: author name, ai: author code, ti:
title words, ut: keyword, cc: MSC code (cc:*11G05 for the primary code only), py: year or range
(py:2000-2015), so: source, dt: type (j article, a collection article, b book, p preprint),
la: language, ab: review or summary text, doi:, arxiv:, an: Zbl number, db: Zbl, JFM or arxiv.
Operators: & (and, the default), | (or), ! (not), * (right wildcard), "a phrase", (grouping).
Words match exactly unless you add *. Authors: au: name, ln: family name, fn: given name, ai:
author code, aw: award, cc: main field, en: external id. Quote the query for the shell.

ID is a Zbl number (0823.11029), a JFM number (30.0424.01), a zbMATH document id, also called the
DE number (783777), arXiv:2412.08738, or a DOI (10.2307/2118559).

Data from zbMATH Open (FIZ Karlsruhe), CC BY-SA 4.0 unless a record names another licence.
"""
import email.utils
import http.client
import json
import math
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.zbmath.org/v1"
AGENT = "open-math-skills/1.0 (zbmath-query)"
CACHE = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "open-math-skills" / "zbmath"
UNAVAILABLE = "zbMATH Open Web Interface contents unavailable due to conflicting licenses."
TIMEOUT = 60
GAP = 1.0                 # seconds between two requests: the API terms ask for a reasonable rate
TEXT_CAP = 3000           # characters of a review or summary shown without --full
RECENT = 10               # an author's most recent documents listed
ROLE_CAP = 500            # documents fetched (100 per request) to count an author's roles
WINDOW = 10000            # the API pages only through the first 10,000 results of a search

DOC_FIELDS = sorted("ab ai an any arxiv au br cc ci db doi dt ed en la li na pt pu py rft rn rv "
                    "se si so st sw ti ut".split())
AUTHOR_FIELDS = sorted("ai any au aw cc cm co en fn ln py rv st".split())
MSC_FIELDS = sorted("any cc ct lv".split())

_last = [0.0]


class Fail(Exception):
    pass


def short(text, width=160):
    text = " ".join(str(text).split())
    return text if len(text) <= width else text[:width - 1] + "…"


def retry_after(value):
    value = value.strip()
    if value.isdigit():
        return int(value)
    try:
        return max(0, email.utils.parsedate_to_datetime(value).timestamp() - time.time())
    except (ValueError, TypeError, OverflowError, OSError):
        return 0


def fetch(path, params=None, tries=3):
    """GET API + path. Returns (HTTP status, body) for 200, 400, 404 and 422, whose bodies the API
    fills with JSON (400: a request it refuses; 404: nothing found; 422: a parameter it cannot
    read). Retries 429 and 5xx a bounded number of times. For a Retry-After over 30 s, report
    the wait and stop."""
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    for i in range(tries):
        wait = _last[0] + GAP - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        delay = 2 * (i + 1)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept": "application/json"})
            try:
                response = urllib.request.urlopen(req, timeout=TIMEOUT)
            except urllib.error.HTTPError as e:
                response = e
            with response:
                code = response.code if isinstance(response, urllib.error.HTTPError) else response.status
                if code in (200, 400, 404, 422):
                    return code, response.read().decode("utf-8", "replace")
                retry = retry_after(response.headers.get("Retry-After", "") if response.headers else "")
                message = "HTTP %s from api.zbmath.org for %s" % (code, path)
                if retry > 30 or retry and i == tries - 1:
                    raise Fail(message + "; retry after at least %d seconds" % math.ceil(retry))
                if code not in (429, 500, 502, 503, 504) or i == tries - 1:
                    busy = "; zbMATH is busy or limiting requests: wait a few minutes" if code in (429, 503) else ""
                    raise Fail(message + busy)
                delay = max(delay, retry)
        except (urllib.error.URLError, http.client.HTTPException, socket.timeout, TimeoutError, OSError) as e:
            if i == tries - 1:
                raise Fail("cannot reach api.zbmath.org: %s" % getattr(e, "reason", e))
        time.sleep(delay)


def call(path, params=None):
    """(result, status) from the API; result is None when zbMATH found nothing."""
    code, text = fetch(path, params)
    try:
        d = json.loads(text)
    except ValueError:
        raise Fail("api.zbmath.org did not answer with JSON for %s (HTTP %s): %s" % (path, code, short(text, 80)))
    if code == 422:
        detail = d.get("detail") if isinstance(d, dict) else None
        if isinstance(detail, list):
            detail = "; ".join("%s: %s" % (e.get("loc", ["?"])[-1], e.get("msg")) for e in detail if isinstance(e, dict))
        raise Fail("zbMATH could not read the request (%s)" % short(detail or text, 200))
    if not isinstance(d, dict) or not isinstance(d.get("status"), dict):
        raise Fail("unexpected answer from api.zbmath.org for %s" % path)
    st = d["status"]
    if code == 400:
        raise Fail("zbMATH refused the request: %s" % short(st.get("internal_code") or st.get("execution") or text, 200))
    if st.get("execution_bool") is True and code == 200:
        if "result" not in d:
            raise Fail("api.zbmath.org answered %s without a result" % path)
        return d["result"], st
    note = "%s %s" % (st.get("internal_code", ""), st.get("execution", ""))
    if re.search(r"not found|no results|does not exist", note, re.I):
        return None, st
    raise Fail("zbMATH could not answer %s: %s" % (path, short(note)))


def search(kind, query, limit, page):
    """One page of a syntax search (page counts from 1): (rows, total); ([], 0) for no match."""
    if page * limit > WINDOW:
        raise Fail("zbMATH pages only through the first %s results of a search: narrow the query "
                   "(add py:, cc:, au: or ti:) instead of asking for page %d" % (format(WINDOW, ","), page))
    rows, st = call("/%s/_search" % kind, {"search_string": query, "page": page - 1, "results_per_page": limit})
    if rows is None:
        return [], 0
    total = st.get("nr_total_results")
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows) or type(total) is not int:
        raise Fail("unexpected answer from zbMATH's %s search" % kind)
    return rows, total


FIELD = re.compile(r"(?:^|(?<=[\s(!&|]))([A-Za-z]+):")


def check_query(query, fields, cmd):
    """Refuse what zbMATH would silently answer with "no results": unknown fields, unclosed
    phrases or parentheses, and years that are not years."""
    query = query.strip()
    if not query:
        raise Fail("give a query, for example: zbmath.py %s %s" % (
            cmd, "'au:Wiles ti:Fermat'" if cmd == "search" else "'ln:Wiles fn:Andrew'" if cmd == "authors" else "'elliptic curves'"))
    if query.count('"') % 2:
        raise Fail('the query has an unclosed ": close the phrase (zbMATH answers a malformed query with "no results")')
    bare = re.sub(r'"[^"]*"', lambda m: " " * len(m.group(0)), query)
    depth = 0
    for ch in bare:
        depth += (ch == "(") - (ch == ")")
        if depth < 0:
            break
    if depth:
        raise Fail('unbalanced parentheses in the query (zbMATH answers a malformed query with "no results")')
    for m in FIELD.finditer(bare):
        field = m.group(1).lower()
        if field not in fields:
            raise Fail("unknown field %s: here; the fields are %s (quote a phrase that contains a colon)" % (
                m.group(1), " ".join(f + ":" for f in fields)))
        after_field = query[m.end():]
        rest = after_field.lstrip()
        next_field = after_field != rest and FIELD.match(rest)
        if not rest or rest[0] in "&|)" or next_field or re.match(r'"\s*"', rest):
            raise Fail("give a value after %s:" % field)
        if field == "py" and not rest.startswith("("):
            value = re.match(r'"([^"]*)"|([^\s)|&]+)', rest)
            value = next((x for x in value.groups() if x is not None), "") if value else ""
            years = re.fullmatch(r"(\d{4})(?:-(\d{4}))?", value)
            if not years or years[2] and years[1] > years[2]:
                raise Fail("py: takes a year or an increasing range such as py:1995 or py:2000-2015")
    return query


# ---- documents ---------------------------------------------------------------------------------

def label(r):
    ident, db = r.get("identifier"), r.get("database") or ""
    if ident and ident != "None":
        return "%s %s" % (db, ident) if db in ("Zbl", "JFM") else ident
    return "zbMATH id %s" % r.get("id")


def title_of(r):
    t = r.get("title") if isinstance(r.get("title"), dict) else {}
    out = (t.get("title") or "(no title)").strip()
    if t.get("subtitle"):
        out += ". " + t["subtitle"].strip()
    if t.get("addition"):
        out += " (%s)" % t["addition"].strip()
    return out


def people(r, key="authors"):
    return [a for a in ((r.get("contributors") or {}).get(key) or []) if isinstance(a, dict)]


def names(r, cap=5):
    ns = [a.get("name") or "?" for a in people(r)]
    if not ns:
        eds = [a.get("name") or "?" for a in people(r, "editors")]
        return "; ".join(eds[:cap]) + " (eds.)" if eds else "(no authors listed)"
    return "; ".join(ns[:cap]) + (" and %d more" % (len(ns) - cap) if len(ns) > cap else "")


def texts(r):
    return [e for e in (r.get("editorial_contributions") or []) if isinstance(e, dict)]


def text_note(r):
    """What kind of review or summary text the API gives for this record."""
    kinds = []
    for e in texts(r):
        kind = e.get("contribution_type") or "text"
        if (e.get("text") or "").strip() == UNAVAILABLE:
            kinds.append("%s not in the API (licence)" % kind)
        elif kind == "review":
            sign = (e.get("reviewer") or {}).get("sign") or (e.get("reviewer") or {}).get("name")
            kinds.append("review by %s" % sign if sign else "review")
        else:
            kinds.append(kind)
    return ", ".join(kinds) or "no review or summary"


def doi_of(r):
    for link in r.get("links") or []:
        if isinstance(link, dict) and link.get("type") == "doi" and link.get("identifier"):
            return link["identifier"]
    return None


def print_rows(rows, first):
    for n, r in enumerate(rows, first):
        msc = [m.get("code") for m in r.get("msc") or [] if isinstance(m, dict) and m.get("code")]
        print("%d. %s | %s | %s" % (n, label(r), r.get("year") or "?", names(r)))
        print("   %s" % short(title_of(r), 200))
        src = ((r.get("source") or {}).get("source") or "").strip()
        if src:
            print("   %s" % short(src, 200))
        extra = ["MSC " + " ".join(msc) if msc else "no MSC", text_note(r)]
        if doi_of(r):
            extra.append("doi:" + doi_of(r))
        extra.append(r.get("zbmath_url") or "")
        print("   %s" % " | ".join(x for x in extra if x))


def more(last, total, page, limit):
    if last >= total:
        return ""
    if (page + 1) * limit > WINDOW:
        return "; zbMATH shows only the first %s: narrow the query" % format(WINDOW, ",")
    return "; next: --page %d" % (page + 1)


def cmd_search(args):
    opts, rest = options(args, {"--limit": int, "--page": int})
    limit, page = opts.get("--limit", 10), opts.get("--page", 1)
    if not 1 <= limit <= 100 or page < 1:
        raise Fail("--limit is 1 to 100 and --page at least 1")
    query = check_query(" ".join(rest), DOC_FIELDS, "search")
    rows, total = search("document", query, limit, page)
    if not rows:
        if page > 1:
            print("No results on page %d for %s: the query has fewer results (page 1 gives the total)." % (page, query))
        else:
            print("No documents match %s. Words match exactly: add * for other endings (geometr*), check the "
                  "spelling and field names, or drop a condition. No result is not proof that no such paper "
                  "exists." % query)
        return
    first = (page - 1) * limit + 1
    print("%s documents match %s:" % (format(total, ","), query))
    print_rows(rows, first)
    last = first + len(rows) - 1
    print("(results %d-%d of %s%s)" % (first, last, format(total, ","), more(last, total, page, limit)))
    if total > 1000:
        print("Many results: narrow with au:, ti:, ut:, cc:, py: or so: rather than reading further pages.")


DOC_ID = [
    (re.compile(r"(?:zbl[\s:]*)?(\d{4}\.\d{5})", re.I), "{}"),
    (re.compile(r"(?:jfm[\s:]*)?(\d{2}\.\d{4}\.\d{2})", re.I), "{}"),
    (re.compile(r"(?:de[\s:]*|zbmath[\s:]*)?(\d{1,10})", re.I), "{}"),
]
ARXIV = re.compile(r"(?:arxiv:\s*|https?://arxiv\.org/abs/)(\d{4}\.\d{4,5}|[a-z-]+(?:\.[a-z]{2})?/\d{7})(?:v\d+)?", re.I)


def doc_ref(text):
    """('id', path part) for a direct lookup, or ('doi', DOI) or ('arxiv', arXiv id) for a search."""
    s = text.strip()
    m = re.match(r"https?://(?:www\.)?zbmath\.org/(?:\?.*?\bq=an(?::|%3A))?([^&#\s]+)$", s, re.I)
    if m:
        s = urllib.parse.unquote(m.group(1)).strip("/")
    m = re.fullmatch(r"(?:doi:\s*|https?://(?:dx\.)?doi\.org/)?(10\.\d{4,9}/\S+)", s, re.I)
    if m:
        return "doi", m.group(1)
    m = ARXIV.fullmatch(s)
    if m:
        return "arxiv", m.group(1)
    for pattern, form in DOC_ID:
        m = pattern.fullmatch(s)
        if m:
            return "id", form.format(m.group(1))
    raise Fail("not a zbMATH document id: %r. Give a Zbl number (0823.11029), a JFM number (30.0424.01), a "
               "zbMATH id or DE number (783777), arXiv:2412.08738 or a DOI (10.2307/2118559)" % text)


def find_doc(ident):
    kind, value = doc_ref(ident)
    if kind == "id":
        r, _ = call("/document/" + urllib.parse.quote(value, safe=":"))
        if r is None:
            raise Fail("no document %s in zbMATH Open (check the number; find it with zbmath.py search)" % value)
        if not isinstance(r, dict):
            raise Fail("unexpected answer from zbMATH for document %s" % value)
        return r
    # The external-ID field handles DOI punctuation that the DOI field can drop.
    query = 'en:"%s"' % value if kind == "doi" else "arxiv:%s" % value
    rows, total = search("document", query, 10, 1)
    if not rows and kind == "doi":
        raise Fail("zbMATH Open returned no document for DOI %s. Search by title and author "
                   "(zbmath.py search 'ti:... au:...') and verify the DOI on the result." % value)
    if not rows:
        raise Fail("no document in zbMATH Open links arXiv:%s; search by title and author instead" % value)
    if total > 1:
        print("%d documents carry %s %s (a preprint and its published version, say); show one by its "
              "number:" % (total, "DOI" if kind == "doi" else "arXiv id", value))
        print_rows(rows, 1)
        return None
    return rows[0]


def cmd_show(args):
    opts, rest = options(args, {"--full": bool})
    if not rest:
        raise Fail("usage: zbmath.py show ID [--full]")
    r = find_doc(" ".join(rest))
    if r is None:
        return
    print("%s  %s  (zbMATH id %s)" % (label(r), r.get("zbmath_url") or "", r.get("id")))
    print("title:      %s" % title_of(r))
    original = r["title"].get("original") if isinstance(r.get("title"), dict) else None
    if original:
        print("original:   %s" % original)

    def who(key):
        return "; ".join("%s [%s]" % (a.get("name") or "?", ", ".join(a.get("codes") or []) or "no author code")
                         for a in people(r, key))
    print("authors:    %s" % (who("authors") or "(none listed)"))
    if people(r, "editors"):
        print("editors:    %s" % who("editors"))
    if people(r, "author_references"):
        print("also:       %s (other contributions, such as a foreword)" % who("author_references"))
    print("source:     %s" % (((r.get("source") or {}).get("source") or "").strip() or "?"))
    lang = ", ".join(l for l in (r.get("language") or {}).get("languages") or [] if l)
    dtype = (r.get("document_type") or {}).get("description")
    print("year:       %s | %s | %s | database %s" % (r.get("year") or "?", dtype or "type not given",
                                                      lang or "language not given", r.get("database") or "?"))
    msc = [m for m in r.get("msc") or [] if isinstance(m, dict)]
    for i, m in enumerate(msc):
        scheme = "" if m.get("scheme") in (None, "msc2020") else " [%s]" % m.get("scheme")
        print("%s%s%s %s%s" % ("MSC 2020:   " if i == 0 else " " * 12, m.get("code"), " (primary)" if i == 0 else "",
                               m.get("text") or "", scheme))
    if not msc:
        print("MSC 2020:   none")
    if r.get("keywords"):
        print("keywords:   %s" % "; ".join(str(k) for k in r["keywords"]))
    for i, link in enumerate(l for l in r.get("links") or [] if isinstance(l, dict)):
        print("%s%s %s %s" % ("links:      " if i == 0 else " " * 12, link.get("type"), link.get("identifier") or "",
                              link.get("url") or ""))
    if r.get("license"):
        print("licence:    %s (named in this record)" % ", ".join(str(x) for x in r["license"]))
    refs = [x for x in r.get("references") or [] if isinstance(x, dict)]
    if refs:
        matched = sum(1 for x in refs if (x.get("zbmath") or {}).get("document_id"))
        print("references: %d, %d of them matched to zbMATH documents" % (len(refs), matched))
    for e in texts(r):
        kind = e.get("contribution_type") or "text"
        rev = e.get("reviewer") or {}
        head = kind
        if rev.get("name") or rev.get("sign"):
            head += " by %s" % (rev.get("name") or rev.get("sign"))
            if rev.get("sign") and rev.get("name") and rev["sign"] != rev["name"]:
                head += " (signed %s)" % rev["sign"]
        if e.get("language"):
            head += ", %s" % e["language"]
        body = re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t\r]+\n", "\n", (e.get("text") or "").strip()))
        print("\n[%s]" % head)
        if body == UNAVAILABLE:
            print("Not available through the API (zbMATH: \"contents unavailable due to conflicting licenses\"). "
                  "Read it on the zbMATH page or at the publisher (DOI link).")
        elif len(body) > TEXT_CAP and not opts.get("--full"):
            print(body[:TEXT_CAP] + "\n… (%d characters in all; --full prints everything)" % len(body))
        else:
            print(body or "(empty)")
    if not texts(r):
        print("\nNo review or summary in zbMATH Open for this document.")
    print("\nzbMATH Open data, CC BY-SA 4.0 unless the record names another licence; a review is by the "
          "reviewer named above.")


# ---- authors -----------------------------------------------------------------------------------

def msc_top_names(max_age=30 * 86400):
    """{'11': 'Number theory', ...}: the 63 top-level MSC 2020 classes, cached for 30 days. Names
    are a convenience: on failure the codes are printed alone."""
    path = CACHE / "msc-top.json"

    def valid(d):
        return (isinstance(d, dict) and len(d) >= 60
                and all(re.fullmatch(r"\d{2}", k) and isinstance(v, str) and v for k, v in d.items()))
    old = None
    try:
        old = json.loads(path.read_text())
        if not valid(old):
            old = None
        elif time.time() - path.stat().st_mtime < max_age:
            return old
    except (OSError, ValueError):
        old = None
    try:
        rows, total = search("classification", "lv:0", 100, 1)
        top = {str(x.get("code"))[:2]: x.get("short_title") for x in rows
               if re.fullmatch(r"\d{2}-XX", str(x.get("code"))) and isinstance(x.get("short_title"), str)}
        if not valid(top) or len(top) != total:
            raise Fail("unexpected list of MSC classes")
    except Fail as e:
        if old:
            print("zbmath.py: could not refresh the MSC names (%s); using the copy of %s" % (
                e, time.strftime("%Y-%m-%d", time.localtime(path.stat().st_mtime))), file=sys.stderr)
            return old
        print("zbmath.py: MSC names unavailable (%s); codes shown alone" % e, file=sys.stderr)
        return {}
    try:
        CACHE.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name("%s.%d.tmp" % (path.name, os.getpid()))
        tmp.write_text(json.dumps(top))
        os.replace(tmp, path)   # never leave a half-written file for another run to read
    except OSError:
        pass
    return top


def fields_line(profile, top, cap=5):
    out = []
    for f in (profile.get("main_fields") or [])[:cap]:
        if isinstance(f, dict) and f.get("field"):
            code = str(f["field"])
            out.append("%s%s (%s)" % (code, " " + top[code] if code in top else "", f.get("count", "?")))
    return "; ".join(out)


def awards_line(profile, cap=6):
    aw = ["%s %s" % (a.get("title") or "?", a.get("year") or "") for a in profile.get("awards") or [] if isinstance(a, dict)]
    return "; ".join(x.strip() for x in aw[:cap]) + (" and %d more" % (len(aw) - cap) if len(aw) > cap else "")


def author_code(text):
    code = text.strip().lower()
    m = re.match(r"https?://(?:www\.)?zbmath\.org/authors/(?:\?q=ai(?::|%3a))?([^&#\s/]+)", code)
    if m:
        code = urllib.parse.unquote(m.group(1))
    code = re.sub(r"^ai:", "", code)
    if not re.fullmatch(r"[a-z0-9][a-z0-9'_.-]*", code):
        raise Fail("not a zbMATH author code: %r (they look like wiles.andrew-j); find it with: "
                   "zbmath.py authors %s" % (text, json.dumps(text, ensure_ascii=False)))
    return code


def role(doc, codes):
    """author, editor or other (a foreword, an interview) for the profile with these codes."""
    for key, name in (("authors", "author"), ("editors", "editor"), ("author_references", "other")):
        if any(set(codes) & set(a.get("codes") or []) for a in people(doc, key)):
            return name
    return "linked"


def cmd_author(args):
    _, rest = options(args, {})
    if not rest:
        raise Fail("usage: zbmath.py author CODE; find codes with zbmath.py authors NAME")
    code = author_code(" ".join(rest))
    p, _ = call("/author/" + urllib.parse.quote(code, safe=""))
    if p is None:
        raise Fail("no author profile %s in zbMATH Open; find codes with: zbmath.py authors NAME" % code)
    if not isinstance(p, dict):
        raise Fail("unexpected answer from zbMATH for author %s" % code)
    if p.get("code") and p["code"] != code:
        print("(%s is another code of the profile %s)" % (code, p["code"]))
        code = p["code"]
    codes = [code] + [str(a) for a in p.get("aliases") or []]
    print("%s  %s  %s" % (code, p.get("name") or "?", p.get("zbmath_url") or ""))
    spell = ["%s (%s)" % (s.get("name"), s.get("count")) for s in p.get("spellings") or [] if isinstance(s, dict)]
    if spell:
        print("published as: %s" % "; ".join(spell[:8]) + (" and %d more" % (len(spell) - 8) if len(spell) > 8 else ""))
    docs, total, page = [], None, 1
    while True:
        rows, t = search("document", "ai:" + code, 100, page)
        total = t if total is None else total
        docs += rows
        if not rows or total > ROLE_CAP or len(docs) >= total or len(rows) < 100:
            break
        page += 1
    if not total:
        print("documents:    none linked to %s" % code)
    elif len(docs) >= total:
        roles = {}
        for d in docs:
            roles.setdefault(role(d, codes), []).append(d)
        years = sorted(int(d["year"]) for d in roles.get("author", []) if str(d.get("year") or "").isdigit())
        parts = ["%d as author%s" % (len(roles.get("author", [])), " (%d-%d)" % (years[0], years[-1]) if years else "")]
        if roles.get("editor"):
            parts.append("%d as editor" % len(roles["editor"]))
        if roles.get("other"):
            parts.append("%d other contributions (forewords and the like)" % len(roles["other"]))
        if roles.get("linked"):
            parts.append("%d without a role in the record" % len(roles["linked"]))
        print("documents:    %d linked to %s: %s" % (total, code, ", ".join(parts)))
    else:
        print("documents:    %s linked to %s (roles and recent documents need a complete set of at most %d "
              "documents; use zbmath.py search 'ai:%s py:YYYY-YYYY')" % (format(total, ","), code, ROLE_CAP, code))
    top = msc_top_names() if p.get("main_fields") else {}
    if p.get("main_fields"):
        print("main fields:  %s  (MSC class, documents)" % fields_line(p, top))
    if p.get("awards"):
        print("awards:       %s" % awards_line(p))
    ext = ["%s %s" % (x.get("type"), x.get("external_id")) for x in p.get("external_ids") or [] if isinstance(x, dict)]
    if ext:
        print("external ids: %s" % "; ".join(ext))
    for key, lab in (("aliases", "aliases"), ("in_collective", "member of"), ("collective_of", "members")):
        if p.get(key):
            print("%-13s %s" % (lab + ":", "; ".join(str(x) for x in p[key][:10])))
    if docs and len(docs) >= total:
        docs.sort(key=lambda d: str(d.get("year") or ""), reverse=True)
        print("\nmost recent documents (%d of %d):" % (min(RECENT, len(docs)), total))
        for d in docs[:RECENT]:
            print("  %s  %-16s %-7s %s" % (d.get("year") or "????", label(d), role(d, codes), short(title_of(d), 90)))
    print("\nAll documents: zbmath.py search 'ai:%s' (add py:, cc: or ti: to narrow)." % code)


def cmd_authors(args):
    opts, rest = options(args, {"--limit": int, "--page": int})
    limit, page = opts.get("--limit", 10), opts.get("--page", 1)
    if not 1 <= limit <= 100 or page < 1:
        raise Fail("--limit is 1 to 100 and --page at least 1")
    query = check_query(" ".join(rest), AUTHOR_FIELDS, "authors")
    rows, total = search("author", query, limit, page)
    if not rows:
        print("No results on page %d: the query has fewer results." % page if page > 1 else
              "No author profile matches %s. Try the family name alone (ln:NAME) or a wildcard (ln:Shla*)." % query)
        return
    top = msc_top_names()
    first = (page - 1) * limit + 1
    print("%s author profiles match %s:" % (format(total, ","), query))
    for n, p in enumerate(rows, first):
        print("%d. %s  %s" % (n, p.get("code") or "?", p.get("name") or "?"))
        extra = [x for x in (fields_line(p, top, 3) and "fields " + fields_line(p, top, 3), awards_line(p, 3)) if x]
        if extra:
            print("   %s" % " | ".join(extra))
    last = first + len(rows) - 1
    print("(profiles %d-%d of %s%s)" % (first, last, format(total, ","), more(last, total, page, limit)))
    if total > 1:
        print("A name can belong to several people: choose by fields, awards and a paper you know "
              "(zbmath.py show ID lists each author's code); then zbmath.py author CODE.")


# ---- MSC ---------------------------------------------------------------------------------------

def msc_code(text):
    """Canonical MSC 2020 code (11-XX, 11Gxx, 11G05, 11-02) or None if text is not one."""
    s = text.strip()
    for pattern, form in ((r"(\d{2})(?:-?xx)?", "{0}-XX"), (r"(\d{2})([a-z])(?:xx)?", "{0}{1}xx"),
                          (r"(\d{2})([a-z])(\d{2})", "{0}{1}{2}"), (r"(\d{2})-(\d{2})", "{0}-{1}")):
        m = re.fullmatch(pattern, s, re.I)
        if m:
            g = [x.upper() for x in m.groups()]
            return form.format(*g)
    return None


def all_rows(kind, query, cap=500):
    rows, total, page = [], None, 1
    while True:
        got, t = search(kind, query, 100, page)
        total = t if total is None else total
        rows += got
        if not got or len(rows) >= min(total, cap) or len(got) < 100:
            return rows, total
        page += 1


def cmd_msc(args):
    opts, rest = options(args, {"--limit": int})
    limit = opts.get("--limit", 20)
    if not 1 <= limit <= 100:
        raise Fail("--limit is 1 to 100")
    if not rest:
        raise Fail("give an MSC code (11G05, 11G, 11) or words (elliptic curves)")
    code = msc_code(rest[0]) if len(rest) == 1 else None
    if code is None:
        query = check_query(" ".join(rest), MSC_FIELDS, "msc")
        rows, total = search("classification", query, limit, 1)
        if not rows:
            print("No MSC 2020 code matches %s. Try fewer or shorter words (elliptic*), or the code itself." % query)
            return
        for c in rows:
            print("%-6s %s" % (c.get("code"), c.get("long_title") or c.get("short_title") or ""))
        print("(%d of %d MSC 2020 codes%s)" % (len(rows), total, "; --limit 100 for more" if len(rows) < total else ""))
        return
    c, _ = call("/classification/" + urllib.parse.quote(code, safe=""))
    if not isinstance(c, dict) or str(c.get("code", "")).upper() != code.upper():
        # zbMATH can answer with an unrelated code (/classification/11 gave 11R18): check the one it returns
        raise Fail("no MSC 2020 code %s (zbMATH has MSC 2020 only; a code from MSC 2010 may have changed). "
                   "Find codes by words: zbmath.py msc WORDS" % code)
    # the level follows from the form of the code (the API calls 11-02 level 1)
    if code.endswith("-XX"):
        level, term = "top-level class", code[:2]
    elif code.endswith("xx"):
        level, term = "second level", code[:3]
    else:
        level, term = "five-character code", code
    print("%s  %s" % (c.get("code"), c.get("long_title") or c.get("short_title") or ""))
    print("%s%s  %s" % (level, "; parent %s" % c["parent"] if c.get("parent") else "", c.get("zbmath_url") or ""))
    _, count = search("document", "cc:" + term, 1, 1)     # cc:11 and cc:11G count the whole class
    _, primary = search("document", "cc:*" + term, 1, 1)
    print("documents in zbMATH Open: %s with %s, %s with it as primary code (searches 'cc:%s' and 'cc:*%s')"
          % (format(count, ","), "this code" if term == code else "a code in %s" % code, format(primary, ","), term, term))
    if term != code:
        rows, _ = all_rows("classification", "cc:%s*" % term)
        kids = sorted((x for x in rows if x.get("parent") == c.get("code")), key=lambda x: str(x.get("code")))
        print("\n%d subclasses:" % len(kids))
        for x in kids:
            print("  %-6s %s" % (x.get("code"), x.get("short_title") or ""))


# ---- command line ------------------------------------------------------------------------------

def options(args, spec):
    """Split flags from words. spec maps a flag to int or bool."""
    opts, rest, i = {}, [], 0
    while i < len(args):
        a = args[i]
        if a in spec:
            if spec[a] is bool:
                opts[a] = True
                i += 1
                continue
            if i + 1 >= len(args):
                raise Fail("%s takes a number" % a)
            try:
                opts[a] = int(args[i + 1])
            except ValueError:
                raise Fail("%s takes a number, not %r" % (a, args[i + 1]))
            i += 2
            continue
        if a.startswith("--"):
            raise Fail("unknown option %s; options of this command: %s" % (a, " ".join(spec) or "none"))
        rest.append(a)
        i += 1
    return opts, rest


COMMANDS = {"search": cmd_search, "show": cmd_show, "authors": cmd_authors, "author": cmd_author, "msc": cmd_msc}


def main(argv):
    if argv in (["-h"], ["--help"]):
        print(__doc__)
        return 0
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return 2
    COMMANDS[argv[0]](argv[1:])
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except AttributeError:
        pass
    try:
        sys.exit(main(sys.argv[1:]))
    except Fail as e:
        print("zbmath.py: %s" % e, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
