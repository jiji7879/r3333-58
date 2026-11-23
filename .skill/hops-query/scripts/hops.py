#!/usr/bin/env python3
"""Query HOPS, the Hierarchy of Parameters: graph parameters, graph classes and graph class
properties, which of them bound which, and the papers behind each result. Standard library only.

    hops.py find WORD ... [--all]             sets whose name, alias, abbreviation or id contains
                                              every WORD (then definitions); first 20 unless --all
    hops.py show SET                          definition, aliases, tags, equivalent sets, links,
                                              the sources of the definition, numbers of relations
    hops.py relation A B                      does bounded A imply bounded B, and conversely: HOPS's
                                              answer in each direction, the results it records for
                                              the pair, or a derivation from recorded results
    hops.py bounds SET [--all]                what bounded SET implies, what implies it, both kinds
                                              of exclusion, and what is unknown to HOPS
    hops.py source KEY [--all]                a source by BibTeX key, HOPS id or words: its BibTeX
                                              entry and the results HOPS records from it (first 40)

SET, A and B are a HOPS id (0oCyaG), a page or API link, or an exact name, alias or abbreviation
(treewidth, tw, "clique width"; case, spaces and hyphens are ignored).

In HOPS a set S is a parameter (a graph class has bounded S), a graph class (a graph class is a
subclass of S) or a property of graph classes. "A implies B" means that every graph class with A
has B; for two parameters, B(G) <= f(A(G)) for a computable f (HOPS: "A upper bounds B"). An
exclusion means some graph class has A and not B. "Unknown to HOPS" means HOPS records and derives
neither in that direction.

The data are the JSON files the HOPS website publishes under /parameters/api/, taken from its
content repository on GitHub (vaclavblazej/parameters): the script downloads that repository's
archive (about 4.3 MB), checks each API file against its GitHub blob id and against the format it was
written for, and caches an index under $XDG_CACHE_HOME/open-math-skills/hops/ (default
~/.cache/open-math-skills/hops/). It looks for a newer commit at most once a day. HOPS says it has
no stable API yet; on any change of format the script stops with an error instead of guessing.
"""
import gzip
import hashlib
import heapq
import http.client
import io
import json
import os
import re
import sys
import tarfile
import time
import unicodedata
import urllib.error
import urllib.request
import zlib
from pathlib import Path

try:
    import fcntl
except ImportError:
    fcntl = None

REPO = "vaclavblazej/parameters"
GITHUB = "https://api.github.com/repos/" + REPO
ARCHIVE = "https://codeload.github.com/" + REPO + "/tar.gz/%s"
SITE = "https://vaclavblazej.github.io/parameters"
AGENT = "open-math-skills/1.0 (hops-query)"
CACHE = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "open-math-skills" / "hops"
INDEX_VERSION = 1
MAX_ARCHIVE = 64 * 2 ** 20
REFRESH_AFTER, RETRY_AFTER = 86400, 600     # with a cached index / with none
FIND_SHOWN, UNKNOWN_SHOWN, RESULTS_SHOWN = 20, 20, 40
SET_ID = re.compile(r"[A-Za-z0-9]{6}")
TYPE_NAMES = ("Parameter", "GraphClass", "Property:Is", "Property:Has")
STATUSES = ("original", "derivative", "assumed", "conjectured", "noted")
SOURCE_ID = re.compile(r"[A-Za-z0-9_]{6}")


class Fail(Exception):
    pass


class Shape(Exception):
    """The downloaded data do not have the format this script was written for."""


def warn(msg):
    print("hops.py: " + msg, file=sys.stderr)


# ---------------------------------------------------------------- network

def retry_after(err):
    value = err.headers.get("Retry-After") if err.headers else None
    try:
        return max(0, int(value)) if value is not None else None
    except ValueError:
        return None


def get(url, tries=3, timeout=60, limit=None):
    for i in range(tries):
        wait = None
        try:
            req = urllib.request.Request(url, headers={"User-Agent": AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read(limit + 1) if limit else r.read()
            if limit and len(data) > limit:
                raise Fail("%s is larger than %d MB, more than HOPS data should be; not using it"
                           % (url, limit // 2 ** 20))
            return data
        except urllib.error.HTTPError as e:
            wait = retry_after(e)
            remaining = e.headers.get("X-RateLimit-Remaining") if e.headers else None
            e.close()
            if e.code in (403, 429) and "api.github.com" in url and remaining == "0":
                reset = e.headers.get("X-RateLimit-Reset", "")
                when = (time.strftime("%H:%M UTC", time.gmtime(int(reset))) if reset.isdigit()
                        else "in up to an hour")
                raise Fail("GitHub's API limit for this address is used up (60 requests an hour without "
                           "a token); it resets at %s" % when)
            if e.code not in (429, 500, 502, 503, 504) or i == tries - 1:
                raise Fail("HTTP %s from %s" % (e.code, url))
            if wait is not None and wait > 30:
                raise Fail("%s asks to wait %d seconds (HTTP %s); try again later" % (url, wait, e.code))
        except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError) as e:
            if i == tries - 1:
                raise Fail("cannot reach %s: %s" % (url, getattr(e, "reason", e)))
        time.sleep(wait if wait is not None else 2 * (i + 1))


def get_json(url, tries=3):
    try:
        return json.loads(get(url, tries=tries).decode("utf-8"))
    except (ValueError, UnicodeError):
        raise Fail("%s did not answer with JSON" % url)


# ---------------------------------------------------------------- reading and checking the files

def blob_id(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def api_files(raw, sha, tree):
    """{set id: file bytes} for content/api/<id>.json in the archive of commit SHA, each checked
    against the blob id GitHub's tree lists for it."""
    if not isinstance(tree, dict) or tree.get("truncated") is not False or not isinstance(tree.get("tree"), list):
        raise Fail("GitHub did not list the whole file tree of the HOPS content repository")
    blobs = {e.get("path"): e.get("sha") for e in tree["tree"] if isinstance(e, dict) and e.get("type") == "blob"}
    # content/api/simple.json is a separate, shorter index (sets and inclusions only), not a set
    wanted = {p for p in blobs if isinstance(p, str) and re.fullmatch(r"content/api/[A-Za-z0-9]{6}\.json", p)
              and p != "content/api/simple.json"}
    if not wanted:
        raise Fail("the HOPS content repository has no content/api/<id>.json files at commit %s; its layout "
                   "has changed, so this script cannot read it" % sha[:7])
    files = {}
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as compressed:
            with tarfile.open(fileobj=compressed, mode="r|") as tf:
                for m in tf:
                    top, _, path = m.name.partition("/")
                    if not m.isfile() or path not in wanted:
                        continue
                    if top != "parameters-" + sha:
                        raise Fail("the archive from GitHub is not of commit %s" % sha)
                    data = tf.extractfile(m).read()
                    if blob_id(data) != blobs[path]:
                        raise Fail("%s in the archive does not match GitHub's blob id" % path)
                    files[path[len("content/api/"):-len(".json")]] = data
            while compressed.read(65536):   # let gzip check its trailer
                pass
    except (tarfile.TarError, EOFError, zlib.error, OSError) as e:
        raise Fail("the archive from GitHub is damaged or incomplete (%s)" % e)
    if len(files) != len(wanted):
        raise Fail("the archive lacks %d of the %d API files GitHub lists" % (len(wanted) - len(files), len(wanted)))
    return files


def need(cond, what):
    if not cond:
        raise Shape(what)


def keys(obj, names, where):
    need(isinstance(obj, dict) and set(obj) == set(names),
         "%s should have exactly the fields %s, has %s" % (where, ", ".join(sorted(names)),
                                                         ", ".join(sorted(obj)) if isinstance(obj, dict) else type(obj).__name__))


def code(obj, where, pattern=None):
    keys(obj, ("code", "_marker"), where)
    need(isinstance(obj["code"], str) and obj["_marker"] is None, where + " is not an id")
    need(pattern is None or pattern.fullmatch(obj["code"]), "%s: unexpected id %r" % (where, obj["code"]))
    return obj["code"]


def strs(obj, where):
    need(isinstance(obj, list) and all(isinstance(x, str) for x in obj), where + " should be a list of strings")
    return list(obj)


def one(obj, where):
    """The single (variant, value) of a one-field object such as {"Bibtex": {...}}."""
    need(isinstance(obj, dict) and len(obj) == 1, where + " should be an object with one field")
    return next(iter(obj.items()))


def typ_of(t, where):
    if t in ("Parameter", "GraphClass"):
        return t
    kind, value = one(t, where)
    need(kind == "Property" and value in ("Is", "Has"), "%s: unknown type %r" % (where, t))
    return "Property:" + value


def source_of(sk, where):
    kind, v = one(sk, where)
    if kind == "Bibtex":
        keys(v, ("key", "name", "entry", "relevance"), where)
        need(isinstance(v["key"], str) and all(v[k] is None or isinstance(v[k], str) for k in ("name", "entry")),
             where + ": BibTeX key, name or entry of the wrong type")
        return {"kind": "bibtex", "key": v["key"], "name": v["name"], "entry": v["entry"]}
    if kind == "Online":
        keys(v, ("url",), where)
        need(isinstance(v["url"], str), where + ": url is not text")
        return {"kind": "online", "url": v["url"]}
    need(kind == "Other", "%s: unknown kind of source %r" % (where, kind))
    keys(v, ("name", "description"), where)
    need(isinstance(v["name"], str) and isinstance(v["description"], str), where + ": name or description is not text")
    return {"kind": "other", "name": v["name"], "description": v["description"]}


def status_of(s, where):
    if s in ("Assumed", "Conjectured", "Original", "Derivative"):
        return s.lower(), None
    kind, v = one(s, where)
    need(kind == "Noted", "%s: unknown status %r" % (where, s))
    if v in ("Omitted", "Todo"):
        return "noted", v.lower()
    sub, w = one(v, where)
    if sub == "Text" and isinstance(w, str):
        return "noted", "text: " + w
    need(sub == "Source", "%s: unknown kind of noted source %r" % (where, sub))
    return "noted", "source: " + code(w, where, SOURCE_ID)


def page_of(p, where):
    if p == "NotApplicable":
        return None
    if p == "Unknown":
        return "unknown"
    kind, v = one(p, where)
    need(kind == "Pp" and type(v) is int, "%s: unknown page %r" % (where, p))
    return v


RELATED = ("equivsets", "supersets", "subsets", "super_exclusions", "sub_exclusions", "unknown")
SHORT = {"supersets": "sup", "subsets": "sub", "super_exclusions": "supx", "sub_exclusions": "subx"}


def parse_set(sid, d, names, sources, facts):
    """Check one API file (the HOPS generator's format of September 2025) and turn it into an index
    record; SOURCES and FACTS collect the sources and results it names."""
    where = "content/api/%s.json" % sid
    keys(d, ("id", "name", "typ", "relevance", "aka", "abbr", "tags", "providers", "timeline",
             "related_sets", "displayed_definition"), where)
    need(code(d["id"], where + " id", SET_ID) == sid, where + ": the id inside differs from the file name")
    need(isinstance(d["name"], str) and d["name"].strip(), where + ": no name")
    need(type(d["relevance"]) is int and d["relevance"] >= 0, where + ": relevance is not a number")
    need(d["abbr"] is None or isinstance(d["abbr"], str), where + ": abbr is not text")
    rec = {"name": d["name"], "typ": typ_of(d["typ"], where + " typ"), "rel": d["relevance"],
           "aka": strs(d["aka"], where + " aka"), "abbr": d["abbr"],
           "definition": strs(d["displayed_definition"], where + " displayed_definition"),
           "tags": [], "providers": [], "timeline": []}
    need(isinstance(d["tags"], list) and isinstance(d["providers"], list), where + ": tags or providers is not a list")
    for t in d["tags"]:
        keys(t, ("id", "name"), where + " tag")
        code(t["id"], where + " tag id")
        need(isinstance(t["name"], str), where + ": tag name is not text")
        rec["tags"].append(t["name"])
    for p in d["providers"]:
        keys(p, ("provider_name", "set", "url"), where + " provider")
        need(code(p["set"], where + " provider set") == sid, where + ": a provider link names another set")
        need(isinstance(p["provider_name"], str) and isinstance(p["url"], str), where + ": provider name or url is not text")
        rec["providers"].append([p["provider_name"], p["url"]])
    rs = d["related_sets"]
    keys(rs, RELATED, where + " related_sets")
    related = {}
    for k in RELATED:
        lists = {"all": rs[k]} if k == "equivsets" else rs[k]
        if k != "equivsets":
            keys(lists, ("minimal", "maximal", "all"), "%s related_sets.%s" % (where, k))
        ids = {}
        for part, items in lists.items():
            need(isinstance(items, list), "%s related_sets.%s.%s is not a list" % (where, k, part))
            ids[part] = []
            for x in items:
                keys(x, ("id", "name", "typ", "relevance"), "%s related_sets.%s entry" % (where, k))
                xid = code(x["id"], "%s related_sets.%s id" % (where, k), SET_ID)
                need(names.get(xid) == x["name"], "%s related_sets.%s names %s %r, which is not a set file with that "
                     "name" % (where, k, xid, x["name"]))
                ids[part].append(xid)
        need(set(ids.get("minimal", [])) <= set(ids["all"]) and set(ids.get("maximal", [])) <= set(ids["all"]),
             "%s related_sets.%s: minimal or maximal is not part of all" % (where, k))
        related[k] = sorted(set(ids["all"]))
    rec["eq"] = related["equivsets"]
    for k, short in SHORT.items():
        rec[short] = related[k]
    rec["unknown"] = related["unknown"]
    need(isinstance(d["timeline"], list), where + ": timeline is not a list")
    for t in d["timeline"]:
        keys(t, ("preview", "source", "sourcekey", "showed"), where + " timeline entry")
        sid2 = code(t["source"], where + " timeline source", SOURCE_ID)
        keys(t["preview"], ("id", "sourcekey", "time"), where + " timeline preview")
        need(code(t["preview"]["id"], where + " timeline preview id") == sid2 and t["preview"]["sourcekey"] == t["sourcekey"],
             where + ": a timeline entry's preview and source differ")
        keys(t["preview"]["time"], ("year", "month", "day"), where + " timeline time")
        need(all(v is None or type(v) is int for v in t["preview"]["time"].values()), where + ": a date is not a number")
        src = source_of(t["sourcekey"], where + " sourcekey")
        src.update(t["preview"]["time"])
        need(sources.setdefault(sid2, src) == src, "%s: source %s is described in two different ways" % (where, sid2))
        rec["timeline"].append(sid2)
        need(isinstance(t["showed"], list), where + ": showed is not a list")
        for s in t["showed"]:
            keys(s, ("id", "text", "fact", "page"), where + " showed")
            need(isinstance(s["id"], dict) and isinstance(s["text"], str), where + ": showed id or text has the wrong type")
            fact, value = one(s["fact"], where + " fact")
            need(fact in ("Relation", "Definition") and isinstance(value, list) and len(value) == 2,
                 "%s: unknown kind of result %r" % (where, fact))
            status, noted = status_of(value[0], where + " status")
            ref = code(value[1], where + " fact reference")
            f = {"source": sid2, "id": code(s["id"], where + " showed id"), "status": status, "noted": noted,
                 "page": page_of(s["page"], where + " page"), "text": s["text"]}
            if fact == "Relation":
                m = re.fullmatch(r"([A-Za-z0-9]{6})_([A-Za-z0-9]{6})", ref)
                need(m and sid in m.groups() and all(x in names for x in m.groups()),
                     "%s: relation %r is not between this set and another set file" % (where, ref))
                f.update(kind="relation", a=m.group(1), b=m.group(2))
                if f["a"] == f["b"]:
                    continue   # "every set implies itself", recorded for each set
            else:
                need(ref == sid, "%s: the definition of another set (%s) is listed here" % (where, ref))
                f.update(kind="definition", a=sid, b=None)
            facts[json.dumps(f, sort_keys=True)] = f
    return rec


def check_together(sets):
    """The relations of the sets must mirror each other, and 'unknown' must mean what it meant when
    this script was written (every set that is neither a superset nor a subset)."""
    every = set(sets)
    for a, r in sets.items():
        need(a in r["eq"], "%s is not listed as equivalent to itself" % a)
        need(not set(r["sup"]) & set(r["sub"]), "%s has sets that are both above and below it" % a)
        need(not set(r["sup"]) & set(r["supx"]) and not set(r["sub"]) & set(r["subx"]),
             "%s has a set both implied and excluded" % a)
        need(not set(r["eq"]) & set(r["sup"] + r["sub"] + r["supx"] + r["subx"]),
             "%s has an equivalent set that is also above, below or excluded" % a)
        need(set(r["unknown"]) == every - set(r["sup"]) - set(r["sub"]),
             "the meaning of related_sets.unknown of %s has changed" % a)
        for b in r["eq"]:
            need(a in sets[b]["eq"], "%s and %s are not equivalent both ways" % (a, b))
        for b in r["sup"]:
            need(a in sets[b]["sub"], "%s is above %s but not the reverse" % (b, a))
        for b in r["supx"]:
            need(a in sets[b]["subx"], "%s excludes %s but %s does not record it" % (a, b, b))
        for b in r["sub"]:
            need(b in sets and a in sets[b]["sup"], "%s is below %s but not the reverse" % (b, a))
        for b in r["subx"]:
            need(b in sets and a in sets[b]["supx"], "%s is excluded by %s but %s does not record it" % (a, b, b))
        del r["unknown"]


def build(files):
    """The index of the API files {set id: bytes}."""
    raw = {}
    for sid, data in files.items():
        try:
            raw[sid] = json.loads(data.decode("utf-8"))
        except (ValueError, UnicodeError):
            raise Fail("content/api/%s.json from GitHub is not JSON" % sid)
    try:
        names = {}
        for sid, d in raw.items():
            need(isinstance(d, dict) and isinstance(d.get("name"), str), "content/api/%s.json has no name" % sid)
            names[sid] = d["name"]
        sources, facts = {}, {}
        sets = {sid: parse_set(sid, d, names, sources, facts) for sid, d in sorted(raw.items())}
        check_together(sets)
    except (Shape, KeyError, TypeError, AttributeError) as e:
        what = e if isinstance(e, Shape) else "unexpected structure: %s %s" % (type(e).__name__, e)
        raise Fail("the HOPS data format has changed (%s); this script reads the format the HOPS website "
                   "has published since September 2025 (content commit b0e680e of 2026-02-23), and HOPS says "
                   "its API is not stable yet; report the change to the skill's maintainers" % what)
    return {"version": INDEX_VERSION, "sets": sets, "sources": sources, "facts": list(facts.values())}


# ---------------------------------------------------------------- the cache

def write_atomic(path, text):
    CACHE.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name("%s.%d.tmp" % (path.name, os.getpid()))
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return None


def usable(ix):
    """True when IX is an index of the current version with every field the commands read."""
    try:
        ok = (ix["version"] == INDEX_VERSION and all(isinstance(ix[k], str) for k in ("commit", "date", "fetched"))
              and isinstance(ix["sets"], dict) and ix["sets"] and isinstance(ix["sources"], dict)
              and isinstance(ix["facts"], list))
        for r in ix["sets"].values() if ok else ():
            ok = ok and isinstance(r["name"], str) and r["typ"] in TYPE_NAMES and type(r["rel"]) is int
            ok = ok and (r["abbr"] is None or isinstance(r["abbr"], str))
            ok = ok and all(isinstance(r[k], list) for k in ("aka", "definition", "tags", "providers", "timeline",
                                                              "eq", "sup", "sub", "supx", "subx"))
            ok = ok and all(x in ix["sets"] for k in ("eq", "sup", "sub", "supx", "subx") for x in r[k])
            ok = ok and all(s in ix["sources"] for s in r["timeline"])
        for f in ix["facts"] if ok else ():
            ok = ok and f["source"] in ix["sources"] and f["a"] in ix["sets"] and (f["b"] is None or f["b"] in ix["sets"])
            ok = ok and f["kind"] in ("relation", "definition") and f["status"] in STATUSES
            ok = ok and all(k in f for k in ("id", "noted", "page", "text")) and isinstance(f["text"], str)
        for s in ix["sources"].values() if ok else ():
            fields = {"bibtex": ("key",), "online": ("url",), "other": ("name", "description")}.get(s.get("kind"))
            ok = ok and bool(fields) and all(isinstance(s[k], str) for k in fields) and "year" in s
        return bool(ok)
    except (KeyError, TypeError, AttributeError):
        return False


def read_index():
    ix = read_json(CACHE / "index.json")
    return ix if usable(ix) else None


def refresh(ix):
    head = get_json(GITHUB + "/commits/main", tries=2)
    try:
        sha, tree, date = head["sha"], head["commit"]["tree"]["sha"], head["commit"]["committer"]["date"]
    except (KeyError, TypeError):
        raise Fail("unexpected answer from GitHub about the newest commit of %s" % REPO)
    if (not all(isinstance(x, str) and re.fullmatch(r"[0-9a-f]{40}", x) for x in (sha, tree))
            or not isinstance(date, str) or not re.match(r"\d{4}-\d\d-\d\d", date)):
        raise Fail("unexpected commit, tree or date from GitHub")
    if ix and ix["commit"] == sha:
        return ix
    tree = get_json(GITHUB + "/git/trees/%s?recursive=1" % tree, tries=2)
    raw = get(ARCHIVE % sha, tries=2, timeout=180, limit=MAX_ARCHIVE)
    ix = build(api_files(raw, sha, tree))
    ix.update(commit=sha, date=date[:10], fetched=time.strftime("%Y-%m-%d", time.gmtime()))
    write_atomic(CACHE / "index.json", json.dumps(ix, ensure_ascii=False))
    return ix


def load(now=None):
    """The index, refreshed from GitHub at most once a day (every ten minutes while none is cached)."""
    ix = None
    try:
        if fcntl is None:
            raise Fail("refreshing the HOPS data requires a POSIX file lock")
        CACHE.mkdir(parents=True, exist_ok=True)
        with (CACHE / "refresh.lock").open("a") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            ix = read_index()
            state = read_json(CACHE / "state.json")
            state = state if isinstance(state, dict) else {}
            checked, now = state.get("checked"), time.time() if now is None else now
            pause = REFRESH_AFTER if ix else RETRY_AFTER
            recent = type(checked) in (int, float) and now - pause < checked <= now
            if recent and ix and state.get("commit") == ix["commit"]:
                return ix
            if recent and "error" in state:   # otherwise the cache was damaged since: download again
                raise Fail("the last attempt failed: %s; the next attempt is after %s" % (
                    state["error"], time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(checked + pause))))
            write_atomic(CACHE / "state.json", json.dumps({"checked": now}))
            try:
                ix = refresh(ix)
            except Fail as e:
                write_atomic(CACHE / "state.json", json.dumps({"checked": now, "error": str(e)}))
                raise
            write_atomic(CACHE / "state.json", json.dumps({"checked": now, "commit": ix["commit"]}))
            return ix
    except (OSError, Fail) as e:
        ix = ix or read_index()
        if ix:
            warn("could not check GitHub for newer HOPS data: %s. Using the cached copy of content commit %s "
                 "of %s, downloaded %s." % (e, ix["commit"][:7], ix["date"], ix["fetched"]))
            return ix
        raise Fail("could not get the HOPS data from GitHub: %s. Without it, read the website %s/html/"
                   % (e, SITE))


# ---------------------------------------------------------------- names and words

def norm(s):
    s = unicodedata.normalize("NFKD", s)
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if not unicodedata.combining(c)).lower())


def kind(ix, sid):
    t = ix["sets"][sid]["typ"]
    return {"Parameter": "parameter", "GraphClass": "graph class"}.get(t, "property")


def label(ix, sid):
    return "%s [%s]" % (ix["sets"][sid]["name"], sid)


def link(sid):
    return "%s/html/%s/" % (SITE, sid)


def expand(ix, text):
    """TEXT on one line, with HOPS's [[id]] references replaced by what they name."""
    def name(m):
        x = m.group(1)
        if x in ix["sets"]:
            return label(ix, x)
        if x in ix["sources"]:
            return "%s [%s]" % (source_name(ix["sources"][x]), x)
        return m.group(0)
    text = re.sub(r"\[([^\]\n]*)\]\(\.\./([A-Za-z0-9]{6})/?\)", r"\1 [\2]", re.sub(r"\s+", " ", text).strip())
    return re.sub(r"\[\[([A-Za-z0-9_]{6})\]\]", name, text)


def resolve(ix, arg):
    """The set id ARG names: an id, a link, or an exact name, alias or abbreviation."""
    text = arg.strip()
    if not text or len(text) > 200 or any(ord(c) < 32 for c in text):
        raise Fail("give a set: a HOPS id such as 0oCyaG, or a name such as treewidth")
    m = re.search(r"/(?:html|api)/([A-Za-z0-9]{6})(?:/|\.json)?/?$", text)
    if m:
        text = m.group(1)
    hits = {text} & set(ix["sets"])
    key = norm(text)
    if key:
        for sid, r in ix["sets"].items():
            if key in {norm(x) for x in [r["name"]] + r["aka"] + ([r["abbr"]] if r["abbr"] else []) if norm(x)}:
                hits.add(sid)
    if len(hits) == 1:
        return hits.pop()
    if hits:
        raise Fail("%r names %d sets: %s; give the id" % (arg, len(hits), ", ".join(
            "%s (%s)" % (label(ix, s), kind(ix, s)) for s in sorted(hits, key=lambda s: ix["sets"][s]["name"]))))
    near = matches(ix, [arg])[0][:8]
    raise Fail("no HOPS set is named %r%s" % (arg, "; similar: " + ", ".join(label(ix, s) for s in near) if near
                                              else "; search with: hops.py find WORD"))


def words_of(s):
    """The lowercase words of S, accents removed."""
    s = unicodedata.normalize("NFKD", s)
    return " ".join(re.findall(r"[a-z0-9]+", "".join(c for c in s if not unicodedata.combining(c)).lower()))


def matches(ix, words):
    """(sets whose names contain every word, sets whose definition has words starting with each),
    best first."""
    terms = [norm(w) for w in words]
    if not all(terms):
        raise Fail("give words with letters or digits")
    starts = [re.compile(r"(?<![a-z0-9])" + r"\W*".join(words_of(w).split())) for w in words]
    by_name, by_definition = [], []
    for sid, r in ix["sets"].items():
        names = [norm(x) for x in [r["name"]] + r["aka"] + ([r["abbr"]] if r["abbr"] else [])] + [sid.lower()]
        if all(any(t in n for n in names) for t in terms):
            exact = "".join(terms) in names
            by_name.append((not exact, -r["rel"], r["name"].lower(), sid))
        elif all(p.search(words_of(" ".join(r["definition"]))) for p in starts):
            by_definition.append((-r["rel"], r["name"].lower(), sid))
    return [x[-1] for x in sorted(by_name)], [x[-1] for x in sorted(by_definition)]


def plural(n, one, many=None):
    return "%d %s" % (n, one if n == 1 else many or one + "s")


def footer(ix):
    return "(HOPS data from %s content commit %s of %s; %s/html/)" % (REPO, ix["commit"][:7], ix["date"], SITE)


# ---------------------------------------------------------------- relations

def status(ix, a, b):
    """HOPS's answer to 'does A imply B': eq, yes, no or unknown."""
    r = ix["sets"][a]
    if a == b or b in r["eq"]:
        return "eq"
    return "yes" if b in r["sup"] else "no" if b in r["supx"] else "unknown"


def noun(ix, sid):
    r = ix["sets"][sid]
    return {"Parameter": "bounded %s", "GraphClass": "being a subclass of %s", "Property:Is": "being %s",
            "Property:Has": "having %s"}[r["typ"]] % r["name"]


def verb(ix, sid, positive=True):
    r = ix["sets"][sid]
    forms = {"Parameter": ("has bounded %s", "has unbounded %s"),
             "GraphClass": ("is a subclass of %s", "is not a subclass of %s"),
             "Property:Is": ("is %s", "is not %s"), "Property:Has": ("has %s", "does not have %s")}[r["typ"]]
    return forms[0 if positive else 1] % r["name"]


ANSWER = {"yes": "yes", "no": "no (exclusion)", "unknown": "unknown to HOPS", "eq": "yes (equivalent)"}


def meaning(ix, a, b, st):
    if st in ("yes", "eq"):
        return "Every graph class that %s %s." % (verb(ix, a), verb(ix, b))
    if st == "no":
        return "Some graph class %s but %s." % (verb(ix, a), verb(ix, b, False))
    return "HOPS records no implication and no exclusion in this direction and derives none; that is not the same as open."


def index_facts(ix):
    pairs = {}
    for f in ix["facts"]:
        if f["kind"] == "relation":
            pairs.setdefault((f["a"], f["b"]), []).append(f)
    return pairs


def proved(pairs, a, b):
    return [f for f in pairs.get((a, b), []) if f["status"] != "conjectured"]


def referenced(ix, facts):
    """True when one of FACTS cites a publication or web page (not only 'assumed' or 'unknown source')."""
    return any(ix["sources"][f["source"]]["kind"] != "other" for f in facts)


def chain(ix, pairs, a, b):
    """A path a => ... => b in which HOPS records a result for every step, or None: the fewest steps,
    counting a step whose results cite no publication as two."""
    best, prev, heap = {a: 0}, {a: None}, [(0, a)]
    while heap:
        d, x = heapq.heappop(heap)
        if x == b:
            path = [b]
            while prev[path[-1]] is not None:
                path.append(prev[path[-1]])
            return path[::-1]
        if d > best[x]:
            continue
        r = ix["sets"][x]
        for y in sorted(set(r["sup"]) | set(r["eq"]) - {x}):
            facts = proved(pairs, x, y)
            if not facts:
                continue
            nd = d + (1 if referenced(ix, facts) else 2)
            if nd < best.get(y, nd + 1):
                best[y], prev[y] = nd, x
                heapq.heappush(heap, (nd, y))
    return None


def witness(ix, pairs, a, b):
    """(a2, b2) with a2 => a, b => b2 and a recorded exclusion a2 =/=> b2: the fewest changes of a and
    b, counting an exclusion whose results cite no publication as two more."""
    best = None
    lows = [a] + [x for x in ix["sets"][a]["eq"] if x != a] + ix["sets"][a]["sub"]
    highs = [b] + [x for x in ix["sets"][b]["eq"] if x != b] + ix["sets"][b]["sup"]
    for a2 in lows:
        for b2 in highs:
            facts = proved(pairs, a2, b2) if b2 in ix["sets"][a2]["supx"] else []
            if facts:
                cost = ((a2 != a) + (b2 != b) + (0 if referenced(ix, facts) else 2),
                        ix["sets"][a2]["name"], ix["sets"][b2]["name"])
                if best is None or cost < best[0]:
                    best = (cost, a2, b2)
    return best and best[1:]


def year_of(src):
    return "%s" % src["year"] if src.get("year") else "no year"


def source_name(src):
    if src["kind"] == "bibtex":
        return "%s [BibTeX %s]" % (src["name"] or src["key"], src["key"])
    if src["kind"] == "online":
        return "online: %s" % src["url"]
    return "%s (%s)" % (src["name"], src["description"].rstrip("."))


def describe_status(ix, f):
    if f["status"] == "noted":
        detail = f["noted"] or ""
        if detail.startswith("source: "):
            sid = detail[8:]
            src = ix["sources"].get(sid)
            detail = "in %s" % (source_name(src) + " " + link(sid) if src else "HOPS source " + sid)
        elif detail.startswith("text: "):
            detail = "in " + expand(ix, detail[6:])
        else:
            detail = {"omitted": "no reference given",
                      "todo": "that reference is not yet in HOPS"}.get(detail, detail)
        return "stated as known, proved elsewhere: " + detail
    return {"original": "original result (first or independent)",
            "derivative": "later proof or improvement",
            "assumed": "assumed by HOPS (taken as given)",
            "conjectured": "CONJECTURED (posed as an open problem; HOPS does not use it)"}[f["status"]]


VERDICT = {"yes": "implies", "no": "exclusion", "eq": "equivalent", "unknown": "unknown"}


def print_result(ix, f, indent, ids=False, source=True):
    """One recorded result: its source (unless SOURCE is false), page, the sets it is about (with
    IDS), status and quoted text."""
    src = ix["sources"][f["source"]]
    if source:
        print("%s%s  %s  %s" % (indent, year_of(src), source_name(src), link(f["source"])))
    parts = ["page %s" % f["page"]] if f["page"] is not None else []
    if ids and f["kind"] == "definition":
        parts.append("definition of %s" % label(ix, f["a"]))
    elif ids:
        verdict = VERDICT[status(ix, f["a"], f["b"])]
        parts.append("%s to %s [HOPS: %s]" % (label(ix, f["a"]), label(ix, f["b"]), verdict))
    parts.append(describe_status(ix, f))
    print("%s  - %s" % (indent, "; ".join(parts)))
    if f["text"].strip():
        print("%s    \"%s\"" % (indent, expand(ix, f["text"])))


def explain(ix, pairs, a, b, st):
    """How HOPS can know A => B (yes) or A =/=> B (no) when no result is recorded for the pair."""
    if st in ("yes", "eq"):
        path = chain(ix, pairs, a, b)
        if not path:
            print("    HOPS derives it by a rule this script does not retrace (for example for sums of parameters "
                  "or 'distance to' parameters); see %s" % link(a))
            return
        print("    a chain of results recorded in HOPS: " + " => ".join(ix["sets"][x]["name"] for x in path))
        for x, y in zip(path, path[1:]):
            print("    step %s => %s:" % (ix["sets"][x]["name"], ix["sets"][y]["name"]))
            for f in proved(pairs, x, y):
                print_result(ix, f, "      ")
        return
    w = witness(ix, pairs, a, b)
    if not w:
        print("    HOPS derives it by a rule this script does not retrace; see %s" % link(a))
        return
    a2, b2 = w
    print("    HOPS records that %s does not imply %s:" % (noun(ix, a2), noun(ix, b2)))
    for f in proved(pairs, a2, b2):
        print_result(ix, f, "      ")
    for x, y in ([(a2, a)] if a2 != a else []) + ([(b, b2)] if b2 != b else []):
        print("    and HOPS has that %s implies %s (hops.py relation %s %s shows why)" % (noun(ix, x), noun(ix, y), x, y))
    also = ([verb(ix, a)] if a2 != a else []) + ([verb(ix, b, False)] if b2 != b else [])
    print("    so a graph class that %s but %s also %s." % (verb(ix, a2), verb(ix, b2, False), " and ".join(also)))


def relation(a_arg, b_arg):
    ix = load()
    a, b = resolve(ix, a_arg), resolve(ix, b_arg)
    for x in (a, b):
        print("%s: %s, %s" % (label(ix, x), kind(ix, x), link(x)))
    if a == b:
        print("\nBoth name the same HOPS set.")
        print(footer(ix))
        return
    pairs = index_facts(ix)
    answers = {}
    for x, y in ((a, b), (b, a)):
        st = answers[x, y] = status(ix, x, y)
        print("\nDoes %s imply %s? %s" % (noun(ix, x), noun(ix, y), ANSWER[st]))
        print("  " + meaning(ix, x, y, st))
        recorded = pairs.get((x, y), [])
        if recorded:
            print("  Results recorded in HOPS for the direction %s to %s:" % (
                ix["sets"][x]["name"], ix["sets"][y]["name"]))
            for f in recorded:
                print_result(ix, f, "    ")
        if st != "unknown" and not proved(pairs, x, y):
            print("  HOPS records no result for this direction and derives it from others:")
            explain(ix, pairs, x, y, st)
    ab, ba = answers[a, b], answers[b, a]
    na, nb = noun(ix, a), noun(ix, b)
    if ab == "eq":
        summary = "equivalent in HOPS: a graph class %s exactly when it %s" % (verb(ix, a), verb(ix, b))
    elif "yes" in (ab, ba):
        (s, t), other = ((na, nb), ba) if ab == "yes" else ((nb, na), ab)
        summary = "%s implies %s; the converse %s" % (s, t, {"no": "fails (strict)", "unknown": "is unknown to HOPS"}[other])
    elif ab == ba == "no":
        summary = "incomparable: neither implies the other"
    elif ab == ba == "unknown":
        summary = "unknown to HOPS in both directions"
    else:
        (s, t) = (na, nb) if ab == "no" else (nb, na)
        summary = "%s does not imply %s; the converse is unknown to HOPS" % (s, t)
    print("\nIn short: " + summary + ".")
    print(footer(ix))


# ---------------------------------------------------------------- commands

def find(words, every=False):
    ix = load()
    by_name, by_def = matches(ix, words)
    what = " ".join(words)
    if not by_name and not by_def:
        print("No HOPS set has every word of %r in its name, aliases, abbreviation or definition. Try fewer "
              "or other words." % what)
        print(footer(ix))
        return
    print("%s %r: %d by name, alias or abbreviation, then %d by definition." % (
        plural(len(by_name) + len(by_def), "set matches", "sets match"), what, len(by_name), len(by_def)))
    hits = by_name + by_def
    for sid in hits if every else hits[:FIND_SHOWN]:
        r = ix["sets"][sid]
        extra = [x for x in r["aka"]] + (["abbr. " + r["abbr"]] if r["abbr"] else [])
        print("%s  %-12s %s%s%s" % (sid, kind(ix, sid), r["name"], " (%s)" % "; ".join(extra) if extra else "",
                                    "  [in definition]" if sid in by_def else ""))
    if len(hits) > FIND_SHOWN and not every:
        print("(first %d of %d shown; --all lists them)" % (FIND_SHOWN, len(hits)))
    print(footer(ix))


def show(arg):
    ix = load()
    sid = resolve(ix, arg)
    r = ix["sets"][sid]
    sub = " (%s)" % r["typ"].split(":")[1].lower() if ":" in r["typ"] else ""
    print("%s  [%s]  %s%s  (HOPS relevance %d of 9)" % (r["name"], sid, kind(ix, sid), sub, r["rel"]))
    print(link(sid))
    if r["abbr"]:
        print("abbreviation: " + r["abbr"])
    if r["aka"]:
        print("also known as: " + "; ".join(r["aka"]))
    if r["tags"]:
        print("tags: " + ", ".join(r["tags"]))
    for i, d in enumerate(r["definition"]):
        print("%s %s" % ("definition:" if len(r["definition"]) == 1 else "definition %d:" % (i + 1), expand(ix, d)))
    if not r["definition"]:
        print("definition: none in HOPS")
    eq = [x for x in r["eq"] if x != sid]
    if eq:
        print("equivalent in HOPS (a graph class has one exactly when it has the other): " +
              ", ".join(label(ix, x) for x in eq))
    for name, url in r["providers"]:
        print("also at %s: %s" % (name, url))
    defs = [f for f in ix["facts"] if f["kind"] == "definition" and f["a"] == sid]
    if defs:
        print("definitions in sources:")
        for f in defs:
            print_result(ix, f, "  ")
    print("relations in HOPS: %s implies %s and does not imply %d; %s it and %d do not; "
          "unknown to HOPS: %d one way, %d the other (hops.py bounds %s)" % (
              noun(ix, sid), plural(len(r["sup"]), "set"), len(r["supx"]),
              plural(len(r["sub"]), "set implies", "sets imply"), len(r["subx"]),
              len(unknown_of(ix, sid, "out")), len(unknown_of(ix, sid, "in")), sid))
    n = sum(1 for f in ix["facts"] if sid in (f["a"], f["b"]))
    print("recorded in HOPS: %s from %s" % (plural(n, "result"), plural(len(r["timeline"]), "source")))
    print(footer(ix))


def unknown_of(ix, sid, way):
    """The sets X for which HOPS knows neither SID => X (WAY out) nor its negation, or the same for
    X => SID (WAY in)."""
    r = ix["sets"][sid]
    known = set(r["eq"]) | (set(r["sup"]) | set(r["supx"]) if way == "out" else set(r["sub"]) | set(r["subx"]))
    return [x for x in ix["sets"] if x not in known]


def key_ones(ix, group, keep):
    """The members of GROUP from which the others follow: the strongest (no member implies them
    strictly) or the weakest (they imply no member strictly)."""
    g = set(group)
    if keep == "strongest":
        return [x for x in group if not any(x in ix["sets"][y]["sup"] for y in g)]
    return [x for x in group if not set(ix["sets"][x]["sup"]) & g]


def bounds(arg, every=False):
    ix = load()
    sid = resolve(ix, arg)
    r = ix["sets"][sid]

    def pick(ids):
        return sorted(ids, key=lambda x: ix["sets"][x]["name"].lower())

    n = noun(ix, sid)
    print("%s: %s, %s" % (label(ix, sid), kind(ix, sid), link(sid)))
    eq = pick(x for x in r["eq"] if x != sid)
    if eq:
        print("Equivalent in HOPS: " + ", ".join(label(ix, x) for x in eq))
    groups = [
        (lambda k: "%s implies %s (every graph class with it has each; HOPS: it upper bounds them)"
         % (n, plural(k, "set")), r["sup"], "strongest", "by transitivity"),
        (lambda k: "%s %s %s (every graph class with one of them has it; HOPS: they upper bound it)"
         % (plural(k, "set"), "implies" if k == 1 else "imply", n), r["sub"], "weakest", "by transitivity"),
        (lambda k: "%s does not imply %s (exclusions: for each, some graph class has it and not that set)"
         % (n, plural(k, "set")), r["supx"], "weakest", "with the implications in HOPS"),
        (lambda k: "%s %s %s (exclusions: for each, some graph class has that set and not it)"
         % (plural(k, "set"), "does not imply" if k == 1 else "do not imply", n), r["subx"], "strongest",
         "with the implications in HOPS"),
    ]
    for title, ids, keep, how in groups:
        ids = pick(ids)
        shown = ids if every else key_ones(ix, ids, keep)
        title = title(len(ids))
        print("\n" + title[0].upper() + title[1:] + ":")
        if not ids:
            print("  none in HOPS")
        elif not every and len(shown) < len(ids):
            print("  the %d from which the rest follow %s (--all lists all %d):" % (len(shown), how, len(ids)))
        for x in shown:
            print("  %s  %-12s %s" % (x, kind(ix, x), ix["sets"][x]["name"]))
    for title, way in (("Unknown to HOPS whether %s implies them" % n, "out"),
                       ("Unknown to HOPS whether they imply %s" % n, "in")):
        ids = sorted(pick(unknown_of(ix, sid, way)), key=lambda x: (-ix["sets"][x]["rel"], ix["sets"][x]["name"].lower()))
        print("\n%s: %s%s" % (title, plural(len(ids), "set"), "" if every or len(ids) <= UNKNOWN_SHOWN else
                                 " (the %d most relevant shown; --all lists all)" % UNKNOWN_SHOWN))
        for x in ids if every else ids[:UNKNOWN_SHOWN]:
            print("  %s  %-12s %s" % (x, kind(ix, x), ix["sets"][x]["name"]))
    print("\n(hops.py relation A B gives the results and sources for one pair)")
    print(footer(ix))


def source(words, every=False):
    ix = load()
    text = " ".join(words).strip()
    m = re.search(r"/html/([A-Za-z0-9_]{6})/?$", text)
    text = m.group(1) if m else text
    hits = [s for s in ix["sources"] if s == text]
    hits = hits or [s for s, v in ix["sources"].items() if v["kind"] == "bibtex" and v["key"].lower() == text.lower()]
    if not hits:
        terms = [norm(w) for w in text.split() if norm(w)]
        if not terms:
            raise Fail("give a BibTeX key, a HOPS source id or words of a title")
        hits = [s for s, v in ix["sources"].items()
                if all(t in norm(" ".join(str(v.get(k) or "") for k in ("key", "name", "entry", "url", "description")))
                       for t in terms)]
    if not hits:
        raise Fail("no source in HOPS matches %r; hops.py relation A B names the sources about a pair" % text)
    if len(hits) > 1:
        print("%d sources match %r; give the BibTeX key or id of one:" % (len(hits), text))
        for s in sorted(hits, key=lambda s: (str(ix["sources"][s].get("year") or ""), s))[:FIND_SHOWN]:
            print("  %s  %s  %s" % (s, year_of(ix["sources"][s]), source_name(ix["sources"][s])))
        if len(hits) > FIND_SHOWN:
            print("  (first %d of %d shown; add words)" % (FIND_SHOWN, len(hits)))
        print(footer(ix))
        return
    s = hits[0]
    src = ix["sources"][s]
    print("%s  %s  %s" % (year_of(src), source_name(src), link(s)))
    if src["kind"] == "bibtex":
        print(src["entry"] or "(HOPS has no BibTeX entry for this key)")
    facts = [f for f in ix["facts"] if f["source"] == s]
    print("\n%s recorded in HOPS from it:" % plural(len(facts), "result"))
    for f in facts if every else facts[:RESULTS_SHOWN]:
        print_result(ix, f, "", ids=True, source=False)
    if len(facts) > RESULTS_SHOWN and not every:
        print("(first %d of %d shown; --all lists them)" % (RESULTS_SHOWN, len(facts)))
    print(footer(ix))


COMMANDS = ("find", "show", "relation", "bounds", "source")


def main(argv):
    if argv in (["-h"], ["--help"]):
        print(__doc__)
        return 0
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return 2
    cmd, rest = argv[0], list(argv[1:])
    if rest.count("--all") > 1:
        raise Fail("--all given twice")
    every = "--all" in rest
    rest = [a for a in rest if a != "--all"]
    unknown = [a for a in rest if a.startswith("--")]
    if unknown:
        raise Fail("unknown option %s" % unknown[0])
    if every and cmd not in ("find", "bounds", "source"):
        raise Fail("--all goes with find, bounds and source")
    if cmd == "find":
        if not rest:
            raise Fail("find takes words, such as: hops.py find width")
        find(rest, every)
    elif cmd == "source":
        if not rest:
            raise Fail("source takes a BibTeX key, a HOPS source id or words of a title")
        source(rest, every)
    elif cmd == "relation":
        if len(rest) != 2:
            raise Fail("relation takes two sets, such as: hops.py relation treewidth clique-width")
        relation(rest[0], rest[1])
    else:
        if len(rest) != 1:
            raise Fail("%s takes one set (quote a name with spaces), such as: hops.py %s treewidth" % (cmd, cmd))
        {"show": show, "bounds": lambda s: bounds(s, every)}[cmd](rest[0])
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Fail as e:
        print("hops.py: %s" % e, file=sys.stderr)
        sys.exit(1)
