#!/usr/bin/env python3
"""Query FindStat, the database of combinatorial statistics and maps. Standard library only.

    findstat.py collections               the collections (Cc0001 Permutations, Cc0005 Dyck paths, ...)
    findstat.py names WORD ...            statistics whose name contains every WORD
    findstat.py show ID                   a statistic (St000018: name, collection, description, code,
                                          references) or a map (Mp00062: from, to, description)
    findstat.py values StNNNNNN [--count N]  its values on small objects ("object => value"), default 40
    findstat.py identify COLLECTION FILE [--depth N] [--all]
                                          statistics matching the values in FILE (lines
                                          "object => value"; "-" reads standard input), directly or
                                          after up to N maps (default 2, at most 3); --all lists all

COLLECTION is an id (Cc0005) or a name (Dyck paths, DyckPaths). Objects are written as FindStat
writes them: a permutation [2,1,3], a Dyck path [1,1,0,0], a partition [3,1], a set partition
{{1,3},{2}}, a graph by its edge list and vertex count ([(0,1),(1,2)],3); `values` shows the
format of any collection. Give every object of each size you include (all of sizes 1-4, say);
a match on few values means little. The values you send go to findstat.org, a public service.
"""
import html
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://www.findstat.org/api/"
SITE = "https://www.findstat.org/"
AGENT = "open-math-skills/1.0 (findstat-query)"
CACHE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "open-math-skills" / "findstat"


EXAMPLES = {"Cc0001": "a permutation: [2,1,3]", "Cc0002": "an integer partition: [3,1]",
            "Cc0005": "a Dyck path: [1,1,0,0]", "Cc0007": "a standard tableau: [[1,2],[3]]",
            "Cc0009": "a set partition: {{1,3},{2}}", "Cc0020": "a graph: ([(0,1),(1,2)],3)"}


class Fail(Exception):
    pass


def request(url, data=None, tries=3):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=body, headers={"User-Agent": AGENT})
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read().decode("utf-8", "replace")
            try:
                out = json.loads(raw)
            except ValueError:
                raise Fail("FindStat did not answer with JSON (%s)" % raw[:80].replace("\n", " "))
            if isinstance(out, dict) and "error" in out:
                raise Fail("FindStat: %s" % html.unescape(out["error"]))
            return out
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or i == tries - 1:
                raise Fail("HTTP %s from %s" % (e.code, url))
        except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError) as e:
            if i == tries - 1:
                raise Fail("cannot reach %s: %s" % (url, e))
        time.sleep(2 * (i + 1))


def cached(name, url, section, fields, max_age=86400):
    """A list from FindStat, kept for a day. A refresh that fails or does not have the expected
    shape keeps the older copy, which is then used with a warning."""
    path = CACHE / name
    if path.exists() and time.time() - path.stat().st_mtime < max_age:
        return json.loads(path.read_text())
    try:
        data = request(url)
        rows = data["included"][section]
        if (not isinstance(rows, dict) or not rows
                or any(not isinstance(row, dict) or not all(isinstance(row.get(f), str) for f in fields)
                       for row in rows.values())):
            raise Fail("unexpected shape of FindStat's %s list" % section)
    except (KeyError, TypeError, Fail) as e:
        if path.exists():
            print("findstat.py: refresh failed (%s); using the cached %s from %s" % (
                e, name, time.strftime("%Y-%m-%d", time.localtime(path.stat().st_mtime))), file=sys.stderr)
            return json.loads(path.read_text())
        raise Fail("could not get FindStat's %s list: %s" % (section, e))
    CACHE.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".%d.tmp" % os.getpid())
    tmp.write_text(json.dumps(data))
    os.replace(tmp, path)   # never leave a half-written file for another agent to read
    return data


def collections():
    d = cached("collections.json", API + "CollectionsDatabase/?fields=Name,NamePlural,NameWiki",
               "Collections", ("Name", "NamePlural", "NameWiki"))
    return d["included"]["Collections"]


def collection(arg):
    cs = collections()
    if re.fullmatch(r"Cc\d{4}", arg):
        if arg in cs:
            return arg
    key = re.sub(r"[\s_-]", "", arg).lower()
    for cid, c in cs.items():
        if key in {re.sub(r"[\s_-]", "", c[k]).lower() for k in ("Name", "NamePlural", "NameWiki")}:
            return cid
    raise Fail("unknown collection %r; see: findstat.py collections" % arg)


def statistic_names():
    d = cached("statistics.json", API + "StatisticsDatabase/?fields=Name", "Statistics", ("Name",))
    return {k: v["Name"] for k, v in d["included"]["Statistics"].items()}


def map_names():
    d = cached("maps.json", API + "MapsDatabase/?fields=Name", "Maps", ("Name",))
    return {k: v["Name"] for k, v in d["included"]["Maps"].items()}


def stat_id(sid):
    m = re.fullmatch(r"(?:St)?0*(\d{1,6})", sid.strip())
    if not m:
        raise Fail("not a statistic id: %r" % sid)
    return "St%06d" % int(m.group(1))


def show(ident):
    cs = collections()
    m = re.fullmatch(r"Mp0*(\d{1,5})", ident.strip())
    if m:
        mid = "Mp%05d" % int(m.group(1))
        d = request(API + "MapsDatabase/%s/?fields=Name,Domain,Codomain,Properties,Description,References" % mid)
        x = d["included"]["Maps"][mid]
        print("%s  %s  %sMapsDatabase/%s" % (mid, x.get("Name", ""), SITE, mid))
        print("from %s %s to %s %s; %s" % (x.get("Domain", ""), cs.get(x.get("Domain"), {}).get("NamePlural", ""),
                                          x.get("Codomain", ""), cs.get(x.get("Codomain"), {}).get("NamePlural", ""),
                                          x.get("Properties", "")))
        fields = ("Description", "References")
    else:
        sid = stat_id(ident)
        d = request(API + "StatisticsDatabase/%s/?fields=Name,Domain,Description,Code,References" % sid)
        x = d["included"]["Statistics"][sid]
        print("%s  %s  %sStatisticsDatabase/%s" % (sid, x.get("Name", ""), SITE, sid))
        dom = x.get("Domain", "")
        print("collection: %s %s" % (dom, cs.get(dom, {}).get("NamePlural", "")))
        fields = ("Description", "Code", "References")
    for field in fields:
        if x.get(field):
            print("\n[%s]\n%s" % (field.lower(), x[field].replace("\r\n", "\n").strip()))


def values(sid, count):
    if count < 1:
        raise Fail("--count must be at least 1")
    if "o" in sid.strip()[2:]:
        raise Fail("%s is a chain: apply its maps in order yourself, then compare with the values of its "
                   "statistic (the St part)" % sid)
    sid = stat_id(sid)
    d = request(API + "StatisticsDatabase/%s/?fields=Values" % sid)
    vals = d["included"]["Statistics"][sid]["Values"]
    for obj, v in vals[:count]:
        print("%s => %s" % (obj, v))
    print("(%d of %d values of %s)" % (min(count, len(vals)), len(vals), sid), file=sys.stderr)


def parse_values(text):
    pairs = []
    for n, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=>" not in line:
            raise Fail("line %d has no '=>': %r" % (n, line))
        obj, val = (x.strip() for x in line.rsplit("=>", 1))
        if not obj or not re.fullmatch(r"-?\d+", val):
            raise Fail("line %d: want 'object => integer', got %r" % (n, line))
        pairs.append((obj, val))
    if len(pairs) < 3:
        raise Fail("give at least 3 values (FindStat's minimum); more make a match meaningful")
    if len(pairs) > 1000:
        raise Fail("at most 1000 values per query (all permutations up to size 6 are 873); send every object "
                   "up to the largest size that fits")
    return pairs


def describe_chain(chain, names, maps):
    """St000008oMp00071oMp00062 is St000008 after Mp00071 after Mp00062: Mp00062 is applied first."""
    parts = chain.split("o")
    steps = ["%s (%s)" % (m, maps.get(m, "?")) for m in reversed(parts[1:])]
    return "apply " + ", then ".join(steps) + ", then %s (%s)" % (parts[0], names.get(parts[0], "?"))


def identify(coll, source, limit=10, depth=2):
    cid = collection(coll)
    try:
        text = sys.stdin.read() if source == "-" else Path(source).read_text()
    except (OSError, UnicodeError) as e:
        raise Fail("could not read %s: %s" % (source, e))
    pairs = parse_values(text)
    data = "".join("%s\n====> %s\n" % p for p in pairs)
    try:
        d = request(API + "StatisticsDatabase/", {"Domain": cid, "Data": data, "Depth": depth,
                                                  "fields": "MatchingStatistic,Offset,Quality,ValuesKnown"})
    except Fail as e:
        if "unable to convert" in str(e):
            first = str(e).split("unable to convert", 1)[1].split("into", 1)[0].strip()
            example = EXAMPLES.get(cid, "as `findstat.py values` prints them for a statistic on it")
            raise Fail("FindStat could not read objects such as %s as %s. Write them as FindStat does (%s); "
                       "look for doubled braces or brackets in %s."
                       % (first, collections()[cid]["NamePlural"].lower(), example,
                          "the input" if source == "-" else source))
        raise
    matches = d.get("included", {}).get("MatchingStatistics", {})
    if not d.get("data"):
        print("No statistic on %s matches these %d values, directly or after up to %d maps%s." % (
            cid, len(pairs), depth, "" if depth >= 3 else " (the site's own search uses 3: --depth 3)"))
        return
    names, maps = statistic_names(), map_names()
    total = len(pairs)
    direct, chains, weak = [], [], []
    for key in d["data"]:
        m = matches[key]
        if type(m.get("ValuesKnown")) is not int or not 0 <= m["ValuesKnown"] <= total:
            raise Fail("FindStat did not give the number of values it knows for %s" % key)
        if 2 * m["ValuesKnown"] < total:
            weak.append(key)
        elif "o" in m["MatchingStatistic"]:
            chains.append(key)
        else:
            direct.append(key)

    def label(m):
        return "%s  covers %d/%d  offset %s" % (m["MatchingStatistic"], m["ValuesKnown"], total, m.get("Offset"))

    print("%d values on %s. Read each match as: your value + offset = the FindStat statistic's value. "
          "\"covers k/%d\": FindStat has values for k of your objects, and all of them agree." % (total, cid, total))
    print("Statistics on %s itself:" % cid if direct else "No statistic on %s itself agrees with your values." % cid)
    for key in direct[:limit]:
        m = matches[key]
        print("  %s  %s" % (label(m), names.get(m["MatchingStatistic"], "")))
    if len(direct) > limit:
        print("  (%d more; --all lists them)" % (len(direct) - limit))
    same = [k for k in direct if matches[k]["ValuesKnown"] == total and matches[k].get("Offset") == 0]
    if len(same) > 1:
        print("%d statistics on %s agree with every value at offset 0: these values do not single one out. "
              "Add every object of the next size if it stays within 1000 values, and check the definitions." % (
                  len(same), cid))
    if chains:
        print("Statistics after maps (a coincidence on small objects is common here; check the definitions):")
        for key in chains[:limit]:
            m = matches[key]
            print("  %s  %s" % (label(m), describe_chain(m["MatchingStatistic"], names, maps)))
        if len(chains) > limit:
            print("  (%d more; --all lists them)" % (len(chains) - limit))
    if any(matches[k]["ValuesKnown"] < total for k in direct + chains):
        print("A match covering fewer than all your objects holds only on those FindStat has values for "
              "(often it lacks the smallest, such as [1]); report the count, as in \"agrees on 872 of 873\".")
    if weak:
        print("Not evidence: %d statistics for which FindStat has values on fewer than half of your objects:" % len(weak))
        shown = weak if limit >= len(weak) else weak[:3]
        for key in shown:
            print("  %s" % label(matches[key]))
        if len(shown) < len(weak):
            print("  (%d more; --all lists them)" % (len(weak) - len(shown)))


def option(rest, flag, default):
    if flag not in rest:
        return default
    i = rest.index(flag)
    try:
        value = int(rest[i + 1])
    except (IndexError, ValueError):
        raise Fail("%s takes a number" % flag)
    del rest[i:i + 2]
    return value


def main(argv):
    if not argv or argv[0] not in ("collections", "names", "show", "values", "identify"):
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "collections":
        for cid, c in sorted(collections().items()):
            print(cid, c["NamePlural"])
    elif cmd == "names":
        words = [w.lower() for w in rest]
        if not words:
            raise Fail("give at least one word")
        hits = [(k, v) for k, v in sorted(statistic_names().items()) if all(w in v.lower() for w in words)]
        for k, v in hits[:50]:
            print(k, v)
        print("(%d statistics%s)" % (len(hits), "; first 50 shown" if len(hits) > 50 else ""))
    elif cmd in ("show", "values"):
        count = option(rest, "--count", 40)
        if not rest:
            raise Fail("give an id")
        if cmd == "show":
            show(rest[0])
        else:
            values(rest[0], count)
    else:
        every = "--all" in rest
        rest = [r for r in rest if r != "--all"]
        depth = option(rest, "--depth", 2)
        if not 0 <= depth <= 3:
            raise Fail("--depth is 0 to 3")
        if len(rest) < 2:
            raise Fail("usage: findstat.py identify COLLECTION FILE [--depth N] [--all]")
        identify(" ".join(rest[:-1]), rest[-1], 10 ** 6 if every else 10, depth)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Fail as e:
        print("findstat.py: %s" % e, file=sys.stderr)
        sys.exit(1)
