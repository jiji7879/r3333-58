#!/usr/bin/env python3
"""Find small graphs in Brendan McKay's Combinatorial Data collection and in Gordon Royle and Derek
Holt's census of vertex-transitive graphs on 10 to 47 vertices. Standard library only.

    graphcat.py collections [WORD ...]          the collections in the bundled file index
    graphcat.py files COLLECTION [n=N] [--all]  a collection's files: order, stated count, size
    graphcat.py graphs FILE [FILTER ...] [--limit N | --all] [--edges] [--max-mb N]
                                                graphs matching every FILTER, with invariants
    graphcat.py count FILE [FILTER ...] [--by INVARIANT] [--max-mb N]
                                                exact number of matches, or how often each value
                                                of INVARIANT occurs among them
    graphcat.py lines FILE [--limit N | --all] [--max-mb N]
                                                records as stored (Latin squares, ...)
    graphcat.py cite FILE|COLLECTION            the source, licence and credits to cite

FILE is a path from `files` (graph5.g6, crit/crit_9_4.g6, extremal/c4_n10e16.s6), the same
without its extension (graph5), a vertex-transitive census file (alltrans12 for every degree,
alltrans12_k=04 for degree 4), or ARCHIVE:MEMBER for a member of a McKay tar file.

A FILTER is INVARIANT OP VALUE with OP one of = != < > <= >=. Graph invariants: n, edges,
mindeg, maxdeg, regular (yes/no), components, connected (yes/no), bipartite (yes/no),
triangles, girth and diameter (a number or inf), srg (yes/no or v,k,lambda,mu), clique and alpha
(up to 64 vertices), loops, multi. Digraph invariants: n, arcs, loops, digons, minout, maxout, minin, maxin,
regular, strong, connected (weakly). Quote filters containing < or > for the shell.

Downloads larger than --max-mb (default 25) are refused. Vertices are numbered from 0.
"""
import bz2
import email.utils
import gzip
import http.client
import json
import math
import os
import re
import socket
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    import fcntl
except ImportError:  # not on Windows; downloads are then not locked against each other
    fcntl = None

INDEX = Path(__file__).resolve().with_name("graphcat_index.json")
CACHE = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "open-math-skills" / "graph-catalogs"
MCKAY = "https://users.cecs.anu.edu.au/~bdm/data/"
ZENODO = "https://zenodo.org/api/records/4010122/files/"
VT_DOI = "https://doi.org/10.5281/zenodo.4010122"
AGENT = "open-math-skills/1.0 (graph-catalogs-query)"
TIMEOUT = 120
GAP = 1.0                  # seconds between two requests to the same service
LIMIT_MB = 25              # default download limit
SHOWN = 20                 # graphs printed without --all
RECHECK = 30 * 86400       # a cached McKay file is compared with the server after 30 days
BIG = 64                   # clique and alpha are computed up to this order
FAR = 2000                 # girth and diameter are computed up to this order
CHUNK = 1 << 20

EXT_FORMAT = {".g6": "graph6", ".s6": "sparse6", ".is6": "isparse6", ".d6": "digraph6", ".pc": "planarcode"}
TEXT_FORMAT = {"tournaments": "tournament", "self-converse-tournaments": "tournament",
               "regular-tournaments": "tournament", "doubly-regular-tournaments": "tournament",
               "locally-transitive-tournaments": "tournament", "acyclic-digraphs": "dag",
               "trees": "edges", "homeomorphically-irreducible-trees": "edges", "circulant": "circulant"}
GRAPH_FORMATS = {"graph6", "sparse6", "isparse6", "planarcode", "edges", "circulant"}
DIGRAPH_FORMATS = {"digraph6", "tournament", "dag"}
SAFE_PATH = re.compile(r"[A-Za-z0-9][A-Za-z0-9._=-]*(/[A-Za-z0-9][A-Za-z0-9._=-]*)?")

_last = {}


class Fail(Exception):
    pass


def warn(msg):
    print("graphcat.py: %s" % msg, file=sys.stderr)


def mb(n):
    return "%.1f MB" % (n / 1e6) if n >= 1e5 else "%d bytes" % n


def popcount(x):
    return bin(x).count("1")


def bits(x):
    while x:
        low = x & -x
        yield low.bit_length() - 1
        x ^= low


# ---- the bundled index -------------------------------------------------------------------------

_index = []


def index():
    if _index:
        return _index[0]
    try:
        d = json.loads(INDEX.read_text(encoding="utf-8"))
        assert isinstance(d["built"], str) and isinstance(d["collections"], dict)
        files = [dict(zip(d["fields"], row)) for row in d["files"]]
        assert all(isinstance(f["path"], str) and f["c"] in d["collections"] for f in files)
        vt = d["vt"]
        assert all(isinstance(t["path"], str) and isinstance(t["members"], list) for t in vt)
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as e:
        raise Fail("the bundled index %s is missing or damaged (%s): reinstall the skill" % (INDEX, e))
    d["by_path"] = {f["path"]: f for f in files}
    d["file_list"] = files
    _index.append(d)
    return d


def stem(path):
    p = re.sub(r"\.(gz|bz2)$", "", path)
    return re.sub(r"\.(g6|s6|is6|d6|pc|txt|tar)$", "", p)


def fmt_of(path, collection):
    p = re.sub(r"\.(gz|bz2)$", "", path)
    if p.endswith(".tar"):
        return "archive"
    ext = os.path.splitext(p)[1]
    if ext in EXT_FORMAT:
        return EXT_FORMAT[ext]
    if ext == ".txt":
        return TEXT_FORMAT.get(collection, "raw")
    return "raw"


class Target:
    """A file to read: a McKay file (whole), a member of a McKay archive, or members of a
    vertex-transitive census tar on Zenodo."""

    def __init__(self, source, path, entry=None, member=None, vt=None, vt_members=None):
        self.source, self.path, self.entry, self.member = source, path, entry, member
        self.vt, self.vt_members = vt, vt_members

    @property
    def collection(self):
        return "vertex-transitive" if self.source == "vt" else (self.entry or {}).get("c")

    def name(self):
        if self.source == "vt":
            if len(self.vt_members) == 1:
                return self.vt_members[0][0][:-3]
            return stem(self.vt["path"])
        return self.path + (":" + self.member if self.member else "")


def resolve(name):
    name = name.strip()
    if not name:
        raise Fail("give a file name (graphcat.py files COLLECTION lists them)")
    d = index()
    archive, _, member = name.partition(":")
    if member:
        t = resolve(archive)
        if t.source == "vt":
            hits = [m for m in t.vt_members if m[0] in (member, member + ".gz")]
            if not hits:
                raise Fail("%s has no member %r; its members are %s" % (
                    t.vt["path"], member, ", ".join(m[0] for m in t.vt["members"])))
            return Target("vt", t.path, vt=t.vt, vt_members=hits)
        if fmt_of(t.path, t.collection) != "archive":
            raise Fail("%s is not an archive; drop :%s" % (t.path, member))
        if not SAFE_PATH.fullmatch(member):
            raise Fail("not a member name: %r" % member)
        t.member = member
        return t
    m = re.fullmatch(r"(alltrans([0-9]+))(\.tar)?(_k=([0-9]+))?(\.gz)?", name)
    if m:
        vt = next((t for t in d["vt"] if t["path"] == "alltrans%s.tar" % m.group(2)), None)
        if vt is None:
            raise Fail("the vertex-transitive census covers 10 to 47 vertices; there is no %s" % name)
        members = vt["members"]
        if m.group(5) is not None:
            k = int(m.group(5))
            members = [x for x in members if x[0] == "alltrans%s_k=%02d.gz" % (m.group(2), k)]
            if not members:
                raise Fail("the census has no graphs of degree %d on %s vertices (%s has degrees %s)" % (
                    k, m.group(2), vt["path"], ", ".join(str(int(x[0][-5:-3])) for x in vt["members"])))
        return Target("vt", vt["path"], vt=vt, vt_members=members)
    if name in d["by_path"]:
        return Target("mckay", name, entry=d["by_path"][name])
    same = [f for f in d["file_list"] if name in (stem(f["path"]), stem(f["path"].rsplit("/", 1)[-1]),
                                                 re.sub(r"\.(gz|bz2)$", "", f["path"]))]
    if len(same) == 1:
        return Target("mckay", same[0]["path"], entry=same[0])
    if len(same) > 1:
        raise Fail("%r matches %s: give the full name" % (name, ", ".join(f["path"] for f in same)))
    near = [f["path"] for f in d["file_list"] if name.lower() in f["path"].lower()][:8]
    raise Fail("no file %r in the index%s (graphcat.py files COLLECTION lists them)" % (
        name, "; similar: %s" % ", ".join(near) if near else ""))


# ---- network -----------------------------------------------------------------------------------

def retry_after(value):
    value = (value or "").strip()
    if value.isdigit():
        return int(value)
    try:
        return max(0, email.utils.parsedate_to_datetime(value).timestamp() - time.time())
    except (ValueError, TypeError, OverflowError, OSError):
        return 0


def open_url(url, method="GET", headers=None, tries=3):
    """An open response for url (status 200 or 206). Retries 429 and 5xx a bounded number of
    times, spacing requests GAP seconds apart; a Retry-After above 30 s is reported, not slept."""
    host = urllib.parse.urlsplit(url).netloc
    for i in range(tries):
        wait = _last.get(host, 0) + GAP - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[host] = time.time()
        delay = 2 * (i + 1)
        try:
            req = urllib.request.Request(url, method=method, headers=dict({"User-Agent": AGENT}, **(headers or {})))
            return urllib.request.urlopen(req, timeout=TIMEOUT)
        except urllib.error.HTTPError as e:
            try:
                retry = retry_after(e.headers.get("Retry-After") if e.headers else "")
                if e.code in (404, 410):
                    raise Fail("%s answered %s for %s: the file is not there (the index may be out of date)" % (
                        host, e.code, url))
                if e.code == 416:
                    raise Fail("%s refused the byte range for %s (HTTP 416)" % (host, url))
                if retry > 30 or (retry and i == tries - 1):
                    raise Fail("HTTP %s from %s; retry after at least %d seconds" % (e.code, host, math.ceil(retry)))
                if e.code not in (429, 500, 502, 503, 504) or i == tries - 1:
                    raise Fail("HTTP %s from %s for %s" % (e.code, host, url))
                delay = max(delay, retry)
            finally:
                e.close()
        except (urllib.error.URLError, http.client.HTTPException, socket.timeout, TimeoutError, OSError) as e:
            if i == tries - 1:
                raise Fail("cannot reach %s: %s" % (host, getattr(e, "reason", e)))
        time.sleep(delay)


def head(url):
    """(bytes, Last-Modified date, ETag) of a McKay file from a HEAD request."""
    with open_url(url, method="HEAD") as r:
        kind = (r.headers.get("Content-Type") or "").lower()
        size = r.headers.get("Content-Length")
        if kind.startswith("text/html"):
            raise Fail("%s answered with a web page instead of a data file" % url)
        if not (size or "").isdigit():
            raise Fail("%s did not state the file's size" % url)
        return int(size), r.headers.get("Last-Modified") or "", r.headers.get("ETag") or ""


def day(http_date):
    try:
        return email.utils.parsedate_to_datetime(http_date).strftime("%Y-%m-%d")
    except (TypeError, ValueError, IndexError):
        return http_date or "unknown date"


# ---- cache -------------------------------------------------------------------------------------

class Lock:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.f = open(self.path, "a")
        except OSError as e:
            raise Fail("cannot write the cache folder %s (%s): set XDG_CACHE_HOME to a writable folder" % (
                self.path.parent, e))
        if fcntl:
            fcntl.flock(self.f, fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        if fcntl:
            fcntl.flock(self.f, fcntl.LOCK_UN)
        self.f.close()


def read_meta(path):
    try:
        meta = json.loads(Path(str(path) + ".json").read_text(encoding="utf-8"))
        if (isinstance(meta, dict) and type(meta.get("bytes")) is int and type(meta.get("records")) is int
                and type(meta.get("fetched")) in (int, float) and path.is_file()
                and path.stat().st_size == meta["bytes"]):
            return meta
    except (OSError, ValueError):
        pass
    return None


def fetched(meta):
    return time.strftime("%Y-%m-%d", time.localtime(meta["fetched"]))


def write_meta(path, meta):
    tmp = Path("%s.json.%d.tmp" % (path, os.getpid()))
    tmp.write_text(json.dumps(meta), encoding="utf-8")
    os.replace(tmp, str(path) + ".json")


def stream_to(resp, tmp, expect, skip=0):
    """Copy exactly expect bytes of a response to tmp. Return the first skip bytes separately."""
    got, first = 0, b""
    try:
        with open(tmp, "wb") as out:
            while True:
                block = resp.read(min(CHUNK, expect - got + 1))
                if not block:
                    break
                got += len(block)
                if got > expect:
                    raise Fail("the response exceeded the expected %d bytes; try again" % expect)
                if len(first) < skip:
                    take = skip - len(first)
                    first, block = first + block[:take], block[take:]
                out.write(block)
    except (http.client.HTTPException, socket.timeout, TimeoutError, OSError) as e:
        raise Fail("the download was interrupted after %d of %d bytes (%s); try again" % (got, expect, e))
    if got != expect:
        raise Fail("the download stopped after %d of %d bytes; try again" % (got, expect))
    return first


def local_file(t, max_mb, quiet=False):
    """Paths of the verified local copies for target t, downloading what is missing."""
    if t.source == "vt":
        need = [m for m in t.vt_members if read_meta(vt_path(t.vt, m)) is None]
        total = sum(m[2] for m in need)
        if total > max_mb * 1e6:
            raise Fail("%s needs a %s download (%d file%s), above the %d MB limit; ask before raising it with "
                       "--max-mb %d" % (t.name(), mb(total), len(need), "" if len(need) == 1 else "s", max_mb,
                                        math.ceil(total / 1e6) + 1))
        if need and not quiet:
            warn("downloading %d degree file%s of %s (%s) from Zenodo" % (
                len(need), "" if len(need) == 1 else "s", t.vt["path"], mb(total)))
        return [fetch_vt(t.vt, m) for m in t.vt_members]
    path = fetch_mckay(t.path, t.entry, max_mb, quiet)
    meta = read_meta(path)
    stated = t.entry.get("count")
    if (meta and stated is not None and fmt_of(t.path, t.collection) != "archive"
            and meta["records"] != stated):
        warn("%s has %d records; the index (from McKay's page) states %d%s" % (
            t.path, meta["records"], stated, " (" + t.entry["note"] + ")" if t.entry["note"] else ""))
    return [path]


def vt_path(vt, member):
    return CACHE / "royle-holt" / stem(vt["path"]) / member[0]


def fetch_vt(vt, member):
    """One gzipped member of a census tar, read with an HTTP range request; checked against the tar
    header that precedes it and by decompressing it. Zenodo's published files do not change."""
    path = vt_path(vt, member)
    name, start, size = member[0], member[1], member[2]
    with Lock(path.with_name(name + ".lock")):
        if read_meta(path):
            return path
        url = ZENODO + vt["path"] + "/content"
        tmp = path.with_name("%s.%d.tmp" % (name, os.getpid()))
        span = "%d-%d" % (start, start + 512 + size - 1)
        try:
            with open_url(url, headers={"Range": "bytes=" + span}) as r:
                if r.status != 206 or r.headers.get("Content-Range") != "bytes %s/%d" % (span, vt["bytes"]):
                    raise Fail("Zenodo did not answer the byte-range request for %s as expected" % name)
                header = stream_to(r, tmp, 512 + size, skip=512)
            try:
                info = tarfile.TarInfo.frombuf(header, "utf-8", "surrogateescape")
            except tarfile.TarError as e:
                raise Fail("the tar header before %s is not valid (%s)" % (name, e))
            if info.name != name or info.size != size:
                raise Fail("the tar header at that position names %r, not %s" % (info.name, name))
            n = vt["n"]
            records = verify(tmp, "graph6", "gz", n_hint=n)
            os.replace(tmp, path)
        finally:
            tmp.unlink() if tmp.exists() else None
        write_meta(path, {"bytes": size, "records": records, "fetched": time.time(), "source": url, "member": name})
        return path


def mckay_path(path):
    return CACHE / "mckay" / path


def fetch_mckay(rel, entry, max_mb, quiet):
    path = mckay_path(rel)
    url = MCKAY + urllib.parse.quote(rel)
    with Lock(path.with_name(path.name + ".lock")):
        meta = read_meta(path)
        if meta and time.time() - meta.get("checked", 0) < RECHECK:
            return path
        try:
            size, modified, etag = head(url)
        except Fail as e:
            if meta:
                warn("cannot check %s for changes (%s); using the copy downloaded on %s" % (
                    rel, e, fetched(meta)))
                return path
            raise
        if (meta and meta["bytes"] == size and meta.get("modified") == modified
                and meta.get("etag", "") == etag and (modified or etag)):
            meta["checked"] = time.time()
            write_meta(path, meta)
            return path
        if size > max_mb * 1e6:
            msg = "%s is %s, above the %d MB limit; ask before raising it with --max-mb %d" % (
                rel, mb(size), max_mb, math.ceil(size / 1e6) + 1)
            if meta:
                warn("%s changed on the server, but %s; using the copy downloaded on %s" % (rel, msg, fetched(meta)))
                return path
            raise Fail(msg)
        if not quiet:
            warn("downloading %s (%s) from users.cecs.anu.edu.au" % (rel, mb(size)))
        tmp = path.with_name("%s.%d.tmp" % (path.name, os.getpid()))
        try:
            with open_url(url) as r:
                if (r.headers.get("Content-Type") or "").lower().startswith("text/html"):
                    raise Fail("%s answered with a web page instead of a data file" % url)
                stream_to(r, tmp, size)
                modified = r.headers.get("Last-Modified") or ""
                etag = r.headers.get("ETag") or ""
            fmt = fmt_of(rel, entry.get("c"))
            records = verify(tmp, fmt, compression(rel))
            os.replace(tmp, path)
        except Fail as e:
            if meta:
                warn("%s; using the copy downloaded on %s" % (e, fetched(meta)))
                return path
            raise
        finally:
            tmp.unlink() if tmp.exists() else None
        write_meta(path, {"bytes": size, "records": records, "fetched": time.time(), "checked": time.time(),
                          "modified": modified, "etag": etag, "source": url})
        return path


def compression(path):
    return "gz" if path.endswith(".gz") else "bz2" if path.endswith(".bz2") else None


def opener(path, comp):
    if comp == "gz":
        return gzip.open(str(path), "rb")
    if comp == "bz2":
        return bz2.open(str(path), "rb")
    return open(str(path), "rb")


def verify(path, fmt, comp, n_hint=None):
    """Count the records of a downloaded file, checking that each one is well formed (and, with
    n_hint, of that order). Raises Fail on damage."""
    try:
        if fmt == "archive":
            with tarfile.open(str(path), "r:*") as tf:
                members = [m for m in tf.getmembers() if m.isfile()]
            if not members:
                raise Fail("the archive %s is empty" % path.name)
            return len(members)
        count = 0
        for rec in records_of(opener(path, comp), fmt):
            check_record(rec, fmt, n_hint)
            count += 1
        return count
    except (OSError, EOFError, ValueError, tarfile.TarError, zlibError()) as e:
        raise Fail("the downloaded %s is damaged or not in the expected format (%s)" % (path.name, e))


def zlibError():
    import zlib
    return zlib.error


def check_record(rec, fmt, n_hint):
    """A quick shape check (full decoding is left to the queries)."""
    if fmt == "graph6":
        n, length = graph6_shape(rec)
        if n_hint is not None and n != n_hint:
            raise ValueError("a graph has %d vertices, not %d" % (n, n_hint))
    elif fmt in ("sparse6", "isparse6"):
        if rec[:1] not in (b":", b";") or any(c < 63 or c > 126 for c in rec[1:]):
            raise ValueError("not sparse6: %r" % rec[:40])
    elif fmt == "digraph6":
        digraph6(rec)
    elif fmt in ("tournament", "dag"):
        if rec.strip(b"01"):
            raise ValueError("not a 0/1 string: %r" % rec[:40])
        triangle_order(len(rec))
    elif fmt == "planarcode":
        pass  # parsed completely by records_of
    else:
        rec.decode("ascii")


# ---- decoding ----------------------------------------------------------------------------------

def six(data):
    """Values 0..63 of graph6-style bytes."""
    v = [c - 63 for c in data]
    if any(x < 0 or x > 63 for x in v):
        raise ValueError("a character outside the graph6 range ? to ~")
    return v


def order(v, i=0):
    """N(n) at v[i:]: (n, index after it)."""
    if i >= len(v):
        raise ValueError("no number of vertices")
    if v[i] != 63:
        return v[i], i + 1
    if i + 1 < len(v) and v[i + 1] != 63:
        if i + 4 > len(v):
            raise ValueError("truncated number of vertices")
        return (v[i + 1] << 12) | (v[i + 2] << 6) | v[i + 3], i + 4
    if i + 8 > len(v):
        raise ValueError("truncated number of vertices")
    x = 0
    for c in v[i + 2:i + 8]:
        x = x << 6 | c
    return x, i + 8


def strip_header(rec):
    for h in (b">>graph6<<", b">>sparse6<<", b">>digraph6<<"):
        if rec.startswith(h):
            return rec[len(h):]
    return rec


def graph6_shape(rec):
    v = six(rec)
    n, i = order(v)
    length = n * (n - 1) // 2
    check_bit_vector(v[i:], length, "graph6", rec, n)
    return n, length


def check_bit_vector(body, length, fmt, rec, n):
    if len(body) != (length + 5) // 6:
        raise ValueError("%s string %r has the wrong length for %d vertices" % (fmt, rec[:40], n))
    padding = -length % 6
    if padding and body[-1] & ((1 << padding) - 1):
        raise ValueError("%s string %r has nonzero padding bits" % (fmt, rec[:40]))


def to_int(vals):
    x = 0
    for c in vals:
        x = x << 6 | c
    return x


def graph6(rec):
    v = six(rec)
    n, i = order(v)
    length = n * (n - 1) // 2
    body = v[i:]
    check_bit_vector(body, length, "graph6", rec, n)
    if n > 20000:
        raise ValueError("%d vertices is too many for this script" % n)
    x = to_int(body) >> (6 * len(body) - length)
    adj = [0] * n
    for j in range(1, n):
        col = (x >> (length - j * (j + 1) // 2)) & ((1 << j) - 1)   # bits for (0,j) .. (j-1,j)
        if col:
            mask = int(format(col, "0%db" % j)[::-1], 2)
            adj[j] = mask
            for i2 in bits(mask):
                adj[i2] |= 1 << j
    return Graph(n, adj, line=rec)


def sparse6(rec, prev=None):
    incremental = rec[:1] == b";"
    if rec[:1] not in (b":", b";"):
        raise ValueError("sparse6 starts with ':'")
    v = six(rec[1:])
    if incremental:
        if prev is None:
            raise ValueError("an incremental sparse6 line needs the graph before it")
        n, i = prev.n, 0
    else:
        n, i = order(v)
    if n > 1000000:
        raise ValueError("%d vertices is too many for this script" % n)
    k = (n - 1).bit_length() if n > 1 else 0
    rest = v[i:]
    total = 6 * len(rest)
    x = to_int(rest)
    pos, cur, pairs = 0, 0, []
    while pos + 1 + k <= total:
        b = (x >> (total - 1 - pos)) & 1
        pos += 1
        val = (x >> (total - pos - k)) & ((1 << k) - 1) if k else 0
        pos += k
        if b:
            cur += 1
        if val > cur:
            cur = val
        elif cur < n:
            pairs.append((val, cur))
    if incremental:
        adj, loops = list(prev.adj), prev.loop_mask
        for a, b in pairs:
            if a == b:
                loops ^= 1 << a
            else:
                adj[a] ^= 1 << b
                adj[b] ^= 1 << a
        return Graph(n, adj, loop_mask=loops, line=rec)
    return from_edges(n, pairs, line=rec)


def from_edges(n, pairs, line=None, halves=False):
    """A Graph from an edge list (halves: every edge is listed from both ends)."""
    adj, loops, seen, multi = [0] * n, 0, {}, 0
    for a, b in pairs:
        if not (0 <= a < n and 0 <= b < n):
            raise ValueError("vertex out of range in an edge list")
        if a == b:
            loops |= 1 << a
            multi += seen.get((a, a), 0) > 0
            seen[(a, a)] = seen.get((a, a), 0) + 1
            continue
        key = (min(a, b), max(a, b))
        seen[key] = seen.get(key, 0) + 1
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    for key, c in seen.items():
        if key[0] != key[1]:
            extra = c // 2 - 1 if halves else c - 1
            multi += max(0, extra)
    return Graph(n, adj, loop_mask=loops, multi=multi, line=line)


def digraph6(rec):
    if rec[:1] != b"&":
        raise ValueError("digraph6 starts with '&'")
    v = six(rec[1:])
    n, i = order(v)
    length = n * n
    body = v[i:]
    check_bit_vector(body, length, "digraph6", rec, n)
    if n > 20000:
        raise ValueError("%d vertices is too many for this script" % n)
    x = to_int(body) >> (6 * len(body) - length)
    out = [0] * n
    for r in range(n):
        row = (x >> (length - (r + 1) * n)) & ((1 << n) - 1)
        if row:
            out[r] = int(format(row, "0%db" % n)[::-1], 2)
    return Digraph(n, out, line=rec)


def triangle_order(length):
    n = (1 + math.isqrt(1 + 8 * length)) // 2
    if n * (n - 1) // 2 != length:
        raise ValueError("a 0/1 string of length %d is not an upper triangle" % length)
    return n


def triangle(rec, tournament):
    """Upper triangle of the adjacency matrix in row order: (0,1), (0,2), ..., (1,2), ...; '1' at
    (i,j) is the arc i->j. In a tournament '0' is the arc j->i; in an acyclic digraph, no arc."""
    s = rec.decode("ascii")
    if s.strip("01"):
        raise ValueError("not a 0/1 string: %r" % s[:40])
    n = triangle_order(len(s))
    out, pos = [0] * n, 0
    for i in range(n):
        for j in range(i + 1, n):
            if s[pos] == "1":
                out[i] |= 1 << j
            elif tournament:
                out[j] |= 1 << i
            pos += 1
    return Digraph(n, out, line=None, tournament=tournament)


def edge_list(rec, n_hint):
    nums = [int(t) for t in rec.decode("ascii").split()]
    if len(nums) % 2:
        raise ValueError("an edge list with an odd number of entries")
    pairs = list(zip(nums[0::2], nums[1::2]))
    n = max([n_hint or 0] + [max(p) + 1 for p in pairs] + [len(pairs) + 1 if pairs else 1])
    return from_edges(n, pairs)


def circulant(rec, n):
    if not n:
        raise ValueError("the number of vertices of a circulant graph comes from its file name")
    steps = [int(t) for t in rec.decode("ascii").split()]
    if any(not 0 < s < n for s in steps):
        raise ValueError("a circulant step outside 1..%d" % (n - 1))
    adj = [0] * n
    for x in range(n):
        for s in steps:
            y = (x + s) % n
            adj[x] |= 1 << y
            adj[y] |= 1 << x
    return Graph(n, adj)


def records_of(f, fmt):
    """Records of an open binary file: lines, or planar-code graphs (as lists of neighbour lists)."""
    with f:
        if fmt == "planarcode":
            yield from planar_code(f)
            return
        first = True
        for line in f:
            line = line.rstrip(b"\r\n")
            if first:
                line, first = strip_header(line), False
            if line:
                yield line


def planar_code(f):
    """Graphs of a planar-code stream: per graph a byte n, then for each vertex its neighbours
    (numbered from 1) in clockwise order, ended by 0. Read in blocks."""
    data = f.read(max(CHUNK, 64))
    m = re.match(rb">>planar_code( [lb]e)?<<", data)
    pos = m.end() if m else 0
    while True:
        if pos >= len(data):
            more = f.read(CHUNK)
            if not more:
                return
            data, pos = data[pos:] + more, 0
        n = data[pos]
        if n == 0:
            raise ValueError("planar code with more than 255 vertices is not supported")
        nbrs, p = [], pos + 1
        while len(nbrs) < n:
            end = data.find(b"\0", p)
            if end < 0:
                more = f.read(CHUNK)
                if not more:
                    raise ValueError("the planar code ends inside a graph")
                data, p, pos = data[pos:] + more, p - pos, 0
                continue
            nbrs.append(list(data[p:end]))
            p = end + 1
        if any(not 0 < w <= n for row in nbrs for w in row):
            raise ValueError("planar code neighbour out of range")
        pos = p
        yield nbrs


def decode(rec, fmt, n_hint=None, prev=None):
    if fmt == "graph6":
        return graph6(rec)
    if fmt in ("sparse6", "isparse6"):
        return sparse6(rec, prev)
    if fmt == "digraph6":
        return digraph6(rec)
    if fmt in ("tournament", "dag"):
        return triangle(rec, fmt == "tournament")
    if fmt == "edges":
        return edge_list(rec, n_hint)
    if fmt == "circulant":
        return circulant(rec, n_hint)
    if fmt == "planarcode":
        n = len(rec)
        return from_edges(n, [(v, w - 1) for v, row in enumerate(rec) for w in row], halves=True)
    raise ValueError("format %s holds no graphs" % fmt)


# ---- graphs and invariants ---------------------------------------------------------------------

def degree_text(degs):
    counts = {}
    for d in degs:
        counts[d] = counts.get(d, 0) + 1
    return " ".join("%d^%d" % (d, counts[d]) for d in sorted(counts, reverse=True)) or "-"


def encode_n(n):
    if n <= 62:
        return bytes([n + 63])
    if n <= 258047:
        return bytes([126] + [((n >> s) & 63) + 63 for s in (12, 6, 0)])
    return bytes([126, 126] + [((n >> s) & 63) + 63 for s in (30, 24, 18, 12, 6, 0)])


def encode_bits(bitstring):
    bitstring += "0" * (-len(bitstring) % 6)
    return bytes(int(bitstring[i:i + 6], 2) + 63 for i in range(0, len(bitstring), 6))


class Graph:
    directed = False

    def __init__(self, n, adj, loop_mask=0, multi=0, line=None):
        self.n, self.adj, self.loop_mask, self.multi, self.line = n, adj, loop_mask, multi, line
        self.memo = {}

    def simple(self):
        return not self.loop_mask and not self.multi

    def text(self):
        """A standalone source encoding where available, or graph6 of the underlying simple graph."""
        if self.line is not None and not self.line.startswith(b";"):
            return self.line.decode("ascii")
        n, adj = self.n, self.adj
        s = "".join("1" if adj[i] >> j & 1 else "0" for j in range(1, n) for i in range(j))
        return (encode_n(n) + encode_bits(s)).decode("ascii")

    def edges(self):
        return [(i, j) for i in range(self.n) for j in bits(self.adj[i]) if j > i]

    def get(self, name):
        if name not in self.memo:
            self.memo[name] = getattr(self, "inv_" + name)()
        return self.memo[name]

    def inv_n(self):
        return self.n

    def inv_degrees(self):
        return [popcount(a) for a in self.adj]

    def inv_edges(self):
        return sum(self.get("degrees")) // 2

    def inv_mindeg(self):
        return min(self.get("degrees"), default=0)

    def inv_maxdeg(self):
        return max(self.get("degrees"), default=0)

    def inv_regular(self):
        return self.get("mindeg") == self.get("maxdeg")

    def inv_loops(self):
        return popcount(self.loop_mask)

    def inv_multi(self):
        return self.multi

    def comps(self):
        if "comps" not in self.memo:
            out, seen = [], 0
            full = (1 << self.n) - 1
            while seen != full:
                start = (~seen & full) & -(~seen & full)
                comp = frontier = start
                levels = [start]
                while frontier:
                    nxt = 0
                    for v in bits(frontier):
                        nxt |= self.adj[v]
                    frontier = nxt & ~comp
                    comp |= frontier
                    if frontier:
                        levels.append(frontier)
                seen |= comp
                out.append(levels)
            self.memo["comps"] = out
        return self.memo["comps"]

    def inv_components(self):
        return len(self.comps())

    def inv_connected(self):
        return self.get("components") == 1

    def inv_bipartite(self):
        return all(not (self.adj[v] & level) for levels in self.comps() for level in levels for v in bits(level))

    def inv_triangles(self):
        t = 0
        for u in range(self.n):
            au = self.adj[u]
            for v in bits(au >> (u + 1)):
                v += u + 1
                t += popcount(au & self.adj[v] & ~((2 << v) - 1))
        return t

    def inv_girth(self):
        if self.n > FAR:
            raise Fail("girth is computed for at most %d vertices" % FAR)
        best = math.inf
        nb = [list(bits(a)) for a in self.adj]
        for r in range(self.n):
            dist, parent, queue = {r: 0}, {r: -1}, [r]
            for u in queue:
                if 2 * dist[u] + 1 >= best:
                    break
                for w in nb[u]:
                    if w not in dist:
                        dist[w], parent[w] = dist[u] + 1, u
                        queue.append(w)
                    elif parent[u] != w:
                        best = min(best, dist[u] + dist[w] + 1)
        return best

    def inv_diameter(self):
        if self.n > FAR:
            raise Fail("diameter is computed for at most %d vertices" % FAR)
        if not self.get("connected"):
            return math.inf
        full, best = (1 << self.n) - 1, 0
        for r in range(self.n):
            seen = frontier = 1 << r
            ecc = 0
            while seen != full:
                nxt = 0
                for v in bits(frontier):
                    nxt |= self.adj[v]
                frontier = nxt & ~seen
                seen |= frontier
                ecc += 1
            best = max(best, ecc)
        return best

    def inv_srg(self):
        """(v, k, lambda, mu) when the graph is strongly regular and neither complete nor edgeless."""
        n, k = self.n, self.get("maxdeg")
        if not self.get("regular") or k == 0 or k == n - 1:
            return None
        lam, mu = set(), set()
        for u in range(n):
            for w in range(u + 1, n):
                c = popcount(self.adj[u] & self.adj[w])
                (lam if self.adj[u] >> w & 1 else mu).add(c)
                if len(lam) > 1 or len(mu) > 1:
                    return None
        return (n, k, lam.pop(), mu.pop())

    def inv_clique(self):
        return max_clique(self.adj, self.n)

    def inv_alpha(self):
        full = (1 << self.n) - 1
        return max_clique([full & ~a & ~(1 << v) for v, a in enumerate(self.adj)], self.n)

    def summary(self):
        parts = ["n=%d" % self.n, "edges=%d" % self.get("edges"), "degrees=%s" % degree_text(self.get("degrees"))]
        if not self.simple():
            parts.append("loops=%d multi-edges=%d (the other invariants ignore both)" % (
                self.get("loops"), self.multi))
        c = self.get("components")
        parts.append("connected" if c == 1 else "components=%d" % c)
        parts.append("bipartite=%s" % yes(self.get("bipartite")))
        parts.append("triangles=%d" % self.get("triangles"))
        if self.n <= FAR:
            parts.append("girth=%s diameter=%s" % (num(self.get("girth")), num(self.get("diameter"))))
        srg = self.get("srg")
        if srg:
            parts.append("srg=(%d,%d,%d,%d)" % srg)
        return "  ".join(parts)


def max_clique(adj, n):
    if n > BIG:
        raise Fail("clique and alpha are computed for at most %d vertices" % BIG)
    best = [0]

    def grow(size, cand):
        if not cand:
            best[0] = max(best[0], size)
            return
        if size + popcount(cand) <= best[0]:
            return
        pivot = max(bits(cand), key=lambda u: popcount(cand & adj[u]))
        for v in bits(cand & ~adj[pivot]):
            grow(size + 1, cand & adj[v])
            cand &= ~(1 << v)
            if size + popcount(cand) <= best[0]:
                return

    grow(0, (1 << n) - 1)
    return best[0]


class Digraph:
    directed = True

    def __init__(self, n, out, line=None, tournament=False):
        self.n, self.out, self.line = n, out, line
        self.inn = [0] * n
        for v in range(n):
            for w in bits(out[v]):
                self.inn[w] |= 1 << v
        self.memo = {}

    def text(self):
        if self.line is not None:
            return self.line.decode("ascii")
        n = self.n
        s = "".join("1" if self.out[i] >> j & 1 else "0" for i in range(n) for j in range(n))
        return "&" + (encode_n(n) + encode_bits(s)).decode("ascii")

    def edges(self):
        return [(i, j) for i in range(self.n) for j in bits(self.out[i])]

    def get(self, name):
        if name not in self.memo:
            self.memo[name] = getattr(self, "inv_" + name)()
        return self.memo[name]

    def inv_n(self):
        return self.n

    def inv_loops(self):
        return sum(self.out[v] >> v & 1 for v in range(self.n))

    def inv_outdeg(self):
        return [popcount(self.out[v] & ~(1 << v)) for v in range(self.n)]

    def inv_indeg(self):
        return [popcount(self.inn[v] & ~(1 << v)) for v in range(self.n)]

    def inv_arcs(self):
        return sum(self.get("outdeg"))

    def inv_digons(self):
        return sum(popcount(self.out[v] & self.inn[v] & ~((2 << v) - 1)) for v in range(self.n))

    def inv_minout(self):
        return min(self.get("outdeg"), default=0)

    def inv_maxout(self):
        return max(self.get("outdeg"), default=0)

    def inv_minin(self):
        return min(self.get("indeg"), default=0)

    def inv_maxin(self):
        return max(self.get("indeg"), default=0)

    def inv_regular(self):
        degs = set(self.get("outdeg")) | set(self.get("indeg"))
        return len(degs) <= 1

    def reach(self, masks, start):
        seen = frontier = 1 << start
        while frontier:
            nxt = 0
            for v in bits(frontier):
                nxt |= masks[v]
            frontier = nxt & ~seen
            seen |= frontier
        return seen

    def inv_strong(self):
        if self.n == 0:
            return False
        full = (1 << self.n) - 1
        return self.reach(self.out, 0) == full and self.reach(self.inn, 0) == full

    def inv_connected(self):
        if self.n == 0:
            return False
        both = [self.out[v] | self.inn[v] for v in range(self.n)]
        return self.reach(both, 0) == (1 << self.n) - 1

    def summary(self):
        parts = ["n=%d" % self.n, "arcs=%d" % self.get("arcs")]
        if self.get("loops"):
            parts.append("loops=%d" % self.get("loops"))
        parts += ["digons=%d" % self.get("digons"), "out-degrees=%s" % degree_text(self.get("outdeg")),
                  "in-degrees=%s" % degree_text(self.get("indeg")), "strong=%s" % yes(self.get("strong"))]
        if not self.get("strong"):
            parts.append("weakly connected=%s" % yes(self.get("connected")))
        return "  ".join(parts)


def edge_text(g):
    sep = ">" if g.directed else "-"
    return "    %s: %s" % ("arcs" if g.directed else "edges",
                           " ".join("%d%s%d" % (a, sep, b) for a, b in g.edges()) or "(none)")


def yes(b):
    return "yes" if b else "no"


def num(x):
    return "inf" if x == math.inf else str(x)


# ---- filters -----------------------------------------------------------------------------------

GRAPH_INV = {"n": "int", "edges": "int", "mindeg": "int", "maxdeg": "int", "regular": "bool",
             "components": "int", "connected": "bool", "bipartite": "bool", "triangles": "int",
             "girth": "int", "diameter": "int", "srg": "srg", "clique": "int", "alpha": "int",
             "loops": "int", "multi": "int"}
DIGRAPH_INV = {"n": "int", "arcs": "int", "loops": "int", "digons": "int", "minout": "int", "maxout": "int",
               "minin": "int", "maxin": "int", "regular": "bool", "strong": "bool", "connected": "bool"}
FILTER = re.compile(r"^([a-z]+)\s*(!=|<=|>=|=|<|>)\s*(.*)$")


def parse_filters(args, directed):
    known = DIGRAPH_INV if directed else GRAPH_INV
    out, seen, bounds = [], set(), {}
    for a in args:
        m = FILTER.match(a.strip())
        if not m:
            raise Fail("not a filter: %r (want INVARIANT=VALUE or INVARIANT<=VALUE; quote < and > for the shell)" % a)
        name, op, raw = m.group(1), m.group(2), m.group(3).strip()
        if name not in known:
            other = GRAPH_INV if directed else DIGRAPH_INV
            kind, alt = ("digraph", "graph") if directed else ("graph", "digraph")
            raise Fail("%s is not a %s invariant%s; use one of %s" % (
                name, kind, " (it is a %s invariant)" % alt if name in other else "", ", ".join(sorted(known))))
        if not raw:
            raise Fail("give a value after %s%s" % (name, op))
        kind = known[name]
        if (name, op, raw) in seen:
            raise Fail("duplicate filter %s%s%s" % (name, op, raw))
        seen.add((name, op, raw))
        if kind == "bool":
            if op not in ("=", "!="):
                raise Fail("%s is yes or no; use %s=yes or %s=no" % (name, name, name))
            if raw.lower() not in ("yes", "no", "true", "false", "y", "n"):
                raise Fail("%s takes yes or no, not %r" % (name, raw))
            val = raw.lower() in ("yes", "true", "y")
            if op == "!=":
                op, val = "=", not val
        elif kind == "srg":
            if op not in ("=", "!="):
                raise Fail("srg takes = or != with yes, no or v,k,lambda,mu")
            if raw.lower() in ("yes", "no"):
                val = raw.lower() == "yes"
            else:
                parts = raw.strip("()").split(",")
                if len(parts) != 4 or not all(re.fullmatch(r"[0-9]+", p.strip()) for p in parts):
                    raise Fail("srg takes yes, no or four numbers v,k,lambda,mu such as srg=16,6,2,2")
                val = tuple(int(p) for p in parts)
        else:
            if raw.lower() in ("inf", "infinity", "none"):
                if name not in ("girth", "diameter"):
                    raise Fail("%s=%s: only girth and diameter can be inf" % (name, raw))
                val = math.inf
            elif re.fullmatch(r"[0-9]+", raw):
                val = int(raw)
            else:
                raise Fail("%s takes a whole number (ASCII digits), not %r" % (name, raw))
            lo, hi, ne = bounds.get(name, (-math.inf, math.inf, set()))
            if op == "=":
                lo, hi = max(lo, val), min(hi, val)
            elif op == "<":
                hi = min(hi, val - 1 if val != math.inf else val)
            elif op == "<=":
                hi = min(hi, val)
            elif op == ">":
                lo = max(lo, val + 1 if val != math.inf else val)
            elif op == ">=":
                lo = max(lo, val)
            else:
                ne = ne | {val}
            if lo > hi or (lo == hi and lo in ne) or (op == ">" and val == math.inf):
                raise Fail("the filters on %s contradict each other: no value satisfies them" % name)
            bounds[name] = (lo, hi, ne)
        out.append((name, op, val))
    bools = {}
    for name, op, val in out:
        if known[name] == "bool":
            if bools.setdefault(name, val) != val:
                raise Fail("the filters on %s contradict each other" % name)
    return out


def ok(g, filters):
    for name, op, val in filters:
        x = g.get(name)
        if isinstance(val, bool):
            x = bool(x)
            if (x == val) != (op == "="):
                return False
        elif isinstance(val, tuple):
            if (x == val) != (op == "="):
                return False
        else:
            if not {"=": x == val, "!=": x != val, "<": x < val, ">": x > val, "<=": x <= val, ">=": x >= val}[op]:
                return False
    return True


# ---- reading files -----------------------------------------------------------------------------

def kind_of(fmt):
    if fmt in GRAPH_FORMATS:
        return "graph"
    if fmt in DIGRAPH_FORMATS:
        return "digraph"
    return "raw"


def sources(t, max_mb, quiet=False):
    """(label, format, n hint, opener, local file) for each part of the target, downloading as
    needed."""
    paths = local_file(t, max_mb, quiet)
    out = []
    if t.source == "vt":
        for path, m in zip(paths, t.vt_members):
            out.append((m[0][:-3], "graph6", t.vt["n"], lambda p=path: gzip.open(str(p), "rb"), path))
        return out
    path = paths[0]
    fmt = fmt_of(t.path, t.collection)
    if fmt != "archive":
        return [(t.path, fmt, t.entry.get("n"), lambda: opener(path, compression(t.path)), path)]
    tf = tarfile.open(str(path), "r:*")
    members = [m for m in tf.getmembers() if m.isfile()]
    if t.member:
        members = [m for m in members if m.name == t.member or m.name.split("/")[-1] == t.member]
        if not members:
            names = [m.name for m in tf.getmembers() if m.isfile()]
            raise Fail("%s has no member %r; it has %s%s" % (t.path, t.member, ", ".join(names[:30]),
                                                            " ..." if len(names) > 30 else ""))
    for m in members:
        mfmt = fmt_of(m.name, t.collection)
        if mfmt == "raw" and t.collection == "circulant":
            mfmt = "circulant"
        hint = None
        mm = re.search(r"(?:circ|tree)([0-9]+)\.[0-9]+\.txt$|_n([0-9]+)e[0-9]+", m.name)
        if mm:
            hint = int(mm.group(1) or mm.group(2))
        if mfmt == "circulant" and hint is None:
            raise Fail("cannot tell the number of vertices of %s from its name" % m.name)
        out.append(("%s:%s" % (t.path, m.name), mfmt, hint,
                    lambda m=m: gzip_or_plain(tf.extractfile(m), m.name), path))
    return out


def gzip_or_plain(f, name):
    if name.endswith(".gz"):
        return gzip.GzipFile(fileobj=f)
    if name.endswith(".bz2"):
        return bz2.BZ2File(f)
    return f


def objects(t, max_mb, archive_parts=None):
    """Yield (label, position, object) for every graph or digraph in the target."""
    parts = sources(t, max_mb) if archive_parts is None else archive_parts
    for label, fmt, hint, op, where in parts:
        if kind_of(fmt) == "raw":
            raise Fail("%s holds %s, not graphs: use graphcat.py lines %s" % (
                label, "an archive" if fmt == "archive" else "text records", t.name()))
        prev = None
        try:
            for pos, rec in enumerate(records_of(op(), fmt), 1):
                g = decode(rec, fmt, hint, prev)
                prev = g if fmt in ("sparse6", "isparse6") else None
                yield label, pos, g
        except (ValueError, OSError, EOFError, tarfile.TarError, zlibError()) as e:
            raise Fail("cannot read %s (%s); the cached copy may be damaged: delete %s and run the command "
                       "again" % (label, e, where))


# ---- commands ----------------------------------------------------------------------------------

def cmd_collections(words):
    d = index()
    words = [w.lower() for w in words]
    counts = {}
    for f in d["file_list"]:
        counts.setdefault(f["c"], []).append(f)
    shown = 0
    for key, c in d["collections"].items():
        text = " ".join([key, c["title"], c.get("about", "")]).lower()
        if not all(w in text for w in words):
            continue
        shown += 1
        if key == "vertex-transitive":
            files = d["vt"]
            ns = [t["n"] for t in files]
            size = "%d tar files, %d degree files" % (len(files), sum(len(t["members"]) for t in files))
        else:
            files = counts.get(key, [])
            ns = [f["n"] for f in files if f["n"] is not None]
            size = "%d file%s" % (len(files), "" if len(files) == 1 else "s")
        span = " n=%d..%d" % (min(ns), max(ns)) if ns else ""
        print("%-34s %s (%s%s; %s)" % (key, c["title"], size, span, c["format"]))
    print("(%d of %d collections; graphcat.py files COLLECTION lists the files; index built %s)" % (
        shown, len(d["collections"]), d["built"]))


def n_filter(args):
    out = []
    for a in args:
        m = re.fullmatch(r"n\s*(=|<=|>=|<|>)\s*([0-9]+)", a.strip())
        if not m:
            raise Fail("files takes only n filters such as n=12 or \"n<=10\", not %r" % a)
        out.append(("n", m.group(1), int(m.group(2))))
    return out


def cmd_files(args, every):
    if not args:
        raise Fail("give a collection (graphcat.py collections lists them)")
    d = index()
    key = args[0]
    if key not in d["collections"]:
        try:
            t = resolve(key)
        except Fail:
            t = None
        if t is not None:
            raise Fail("%r is a file in collection %s; use it with graphs, count, lines or cite" % (
                key, "vertex-transitive" if t.source == "vt" else t.entry["c"]))
        near = [k for k in d["collections"] if key.lower() in k][:6]
        raise Fail("no collection %r%s" % (key, "; did you mean %s?" % ", ".join(near) if near else ""))
    flt = n_filter(args[1:])
    c = d["collections"][key]
    print("%s: %s" % (key, c["title"]))
    print("  %s" % c["about"])
    if c.get("credit"):
        print("  credit: %s" % c["credit"])
    print("  page: %s" % (VT_DOI if key == "vertex-transitive" else MCKAY + c["page"]))
    rows = []
    if key == "vertex-transitive":
        for t in d["vt"]:
            if not all(cmp(t["n"], op, v) for _, op, v in flt):
                continue
            total = sum(m[2] for m in t["members"])
            counted = [m[3] for m in t["members"]]
            known = sum(x for x in counted if x is not None)
            rows.append("  %-16s n=%-3d %2d degree files  %s%s" % (
                stem(t["path"]), t["n"], len(t["members"]), mb(total).rjust(10),
                "  %d graphs (counted)" % known if None not in counted else "  graph count not in the index"))
    else:
        for f in d["file_list"]:
            if f["c"] != key or not all(f["n"] is not None and cmp(f["n"], op, v) for _, op, v in flt):
                continue
            count = "" if f["count"] is None else "%s %s" % (format(f["count"], ","), "stated")
            rows.append("  %-34s %-6s %-30s %s %s%s" % (
                f["path"], "n=%d" % f["n"] if f["n"] is not None else "", f["label"][:30],
                (mb(f["bytes"]) if f["bytes"] is not None else "?").rjust(10), count,
                "  [%s]" % f["note"] if f["note"] else ""))
    for r in rows if every else rows[:60]:
        print(r)
    more = ", first 60 shown, --all lists them" if len(rows) > 60 and not every else ""
    counts = "counts from the downloaded files" if key == "vertex-transitive" else "counts stated on McKay's page"
    print("(%d file%s%s; sizes and %s as of %s)" % (
        len(rows), "" if len(rows) == 1 else "s", more, counts, d["built"]))


def cmp(x, op, v):
    return {"=": x == v, "<": x < v, ">": x > v, "<=": x <= v, ">=": x >= v}[op]


def directed_and_sources(t, max_mb):
    """Whether the target holds digraphs, with any opened archive parts."""
    if t.source == "vt":
        return False, None
    fmt = fmt_of(t.path, t.collection)
    if fmt != "archive":
        return kind_of(fmt) == "digraph", None
    parts = sources(t, max_mb)
    return {kind_of(src[1]) for src in parts} == {"digraph"}, parts


def cmd_graphs(name, filters, limit, every, show_edges, max_mb):
    t = resolve(name)
    if t.source == "vt":
        t = narrow_vt(t, filters)
    directed, parts = directed_and_sources(t, max_mb)
    flt = parse_filters(filters, directed)
    total = matched = 0
    shown = limit if not every else math.inf
    for label, pos, g in objects(t, max_mb, parts):
        total += 1
        if not ok(g, flt):
            continue
        matched += 1
        if matched <= shown:
            print("%s #%d: %s" % (label, pos, g.text()))
            print("    %s" % g.summary())
            if show_edges:
                print(edge_text(g))
    what = "digraphs" if directed else "graphs"
    print("(%d of %d %s in %s match%s%s)" % (
        matched, total, what, t.name(), " the filters" if flt else "",
        "; first %d shown, --all prints every one" % limit if matched > limit and not every else ""))


def narrow_vt(t, filters):
    """Only the census files a degree filter can match (each file holds one degree)."""
    want = None
    for a in filters:
        m = re.fullmatch(r"\s*(mindeg|maxdeg)\s*=\s*([0-9]+)\s*", a)
        if m:
            want = int(m.group(2))
    if want is None:
        return t
    members = [m for m in t.vt_members if int(m[0][-5:-3]) == want]
    if not members:
        raise Fail("the census has no graphs of degree %d on %d vertices" % (want, t.vt["n"]))
    return Target("vt", t.path, vt=t.vt, vt_members=members)


def cmd_count(name, filters, by, max_mb):
    t = resolve(name)
    if t.source == "vt":
        t = narrow_vt(t, filters)
    fmt = fmt_of(t.path, t.collection) if t.source == "mckay" else "graph6"
    if fmt != "archive" and kind_of(fmt) == "raw":
        if filters or by:
            raise Fail("%s holds text records, not graphs: filters and --by do not apply" % t.path)
        n = sum(1 for _ in records_of(sources(t, max_mb)[0][3](), "raw"))
        print("%d records in %s" % (n, t.path))
        return
    directed, parts = directed_and_sources(t, max_mb)
    flt = parse_filters(filters, directed)
    if by:
        known = DIGRAPH_INV if directed else GRAPH_INV
        sequences = ("outdeg", "indeg") if directed else ("degrees",)
        if by not in known and by not in sequences:
            raise Fail("--by takes an invariant for this file: %s" % ", ".join(sorted((*known, *sequences))))
    total = matched = 0
    dist = {}
    for label, pos, g in objects(t, max_mb, parts):
        total += 1
        if ok(g, flt):
            matched += 1
            if by:
                v = g.get(by)
                if isinstance(v, list):
                    key = degree_text(v)
                elif isinstance(v, tuple):
                    key = "(%d,%d,%d,%d)" % v
                else:
                    key = "none" if v is None else yes(v) if isinstance(v, bool) else num(v)
                dist[key] = dist.get(key, 0) + 1
    what = "digraphs" if directed else "graphs"
    if by:
        def order_key(kv):
            k = kv[0]
            return (0, int(k)) if k.isdigit() else (1, k)
        rows = sorted(dist.items(), key=order_key)
        for k, v in rows[:60]:
            print("%10d  %s=%s" % (v, by, k))
        if len(rows) > 60:
            print("(first 60 of %d values shown)" % len(rows))
    print("%d of %d %s in %s match%s" % (matched, total, what, t.name(), " the filters" if flt else ""))


def cmd_lines(name, limit, every, max_mb):
    t = resolve(name)
    shown = total = 0
    for label, fmt, hint, op, where in sources(t, max_mb):
        if fmt == "planarcode":
            raise Fail("%s is binary planar code: use graphcat.py graphs %s" % (label, name))
        for pos, rec in enumerate(records_of(op(), fmt), 1):
            total += 1
            if every or shown < limit:
                shown += 1
                print("%s #%d: %s" % (label, pos, rec.decode("ascii", "replace")))
    more = "; first %d shown, --all prints every one" % limit if total > limit and not every else ""
    print("(%d record%s%s)" % (total, "" if total == 1 else "s", more))


def cmd_cite(name):
    d = index()
    if name in d["collections"] or name == "vertex-transitive":
        key, t = name, None
    else:
        t = resolve(name)
        key = t.collection
    if key == "vertex-transitive":
        part = ""
        if t and len(t.vt_members) <= 3:
            part = ", file %s, member %s" % (t.vt["path"], ", ".join(m[0] for m in t.vt_members))
        print("Gordon Royle and Derek Holt, Vertex-transitive Graphs On Fewer Than 48 Vertices, version 1.0.0,")
        print("  Zenodo, 2020, doi:10.5281/zenodo.4010122%s." % part)
        print("Licence: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).")
        print("Paper: Derek Holt and Gordon Royle, A census of small transitive groups and vertex-transitive graphs,")
        print("  Journal of Symbolic Computation 101 (2020) 51-60, arXiv:1811.09015.")
        return
    c = d["collections"].get(key) or {}
    page = MCKAY + c["page"] if c.get("page") else MCKAY
    print("Brendan D. McKay, Combinatorial Data, %s (index compiled %s)." % (page, d["built"]))
    if t:
        print("Data file: %s%s%s" % (MCKAY, urllib.parse.quote(t.path), " member %s" % t.member if t.member else ""))
        meta = read_meta(mckay_path(t.path))
        if meta:
            print("Local copy downloaded %s, server last modified %s." % (fetched(meta), day(meta.get("modified"))))
    credit = (t.entry.get("credit") if t else None) or c.get("credit")
    if credit:
        print("Credit: %s" % credit)
    print("Licence: McKay releases the data files of the collection under CC BY 4.0")
    print("  (https://creativecommons.org/licenses/by/4.0/), except data the pages say someone else compiled:")
    print("  credit those authors too and check their terms. The web pages themselves are not under that licence.")


def take(argv, flag, conv=str):
    if flag not in argv:
        return None
    i = argv.index(flag)
    if i + 1 >= len(argv):
        raise Fail("%s needs a value" % flag)
    val = argv[i + 1]
    del argv[i:i + 2]
    try:
        return conv(val)
    except ValueError:
        raise Fail("%s takes %s, not %r" % (flag, "a whole number" if conv is int else "a value", val))


def positive(text):
    if not re.fullmatch(r"[0-9]+", text) or int(text) < 1:
        raise ValueError(text)
    return int(text)


def main(argv):
    argv = list(argv)
    if argv in (["-h"], ["--help"]) or not argv:
        print(__doc__)
        return 0 if argv else 2
    cmd, rest = argv[0], argv[1:]
    every = "--all" in rest
    show_edges = "--edges" in rest
    rest = [a for a in rest if a not in ("--all", "--edges")]
    limit = take(rest, "--limit", positive)
    max_mb = take(rest, "--max-mb", positive) or LIMIT_MB
    by = take(rest, "--by")
    if limit and every:
        raise Fail("give --limit or --all, not both")
    for a in rest:
        if a.startswith("--"):
            raise Fail("unknown option %s" % a)
    if cmd == "collections":
        cmd_collections(rest)
    elif cmd == "files":
        cmd_files(rest, every)
    elif cmd == "cite":
        if len(rest) != 1:
            raise Fail("cite takes one file or collection name")
        cmd_cite(rest[0])
    elif cmd == "graphs":
        if not rest:
            raise Fail("give a file name (graphcat.py files COLLECTION lists them)")
        cmd_graphs(rest[0], rest[1:], limit or SHOWN, every, show_edges, max_mb)
    elif cmd == "count":
        if not rest:
            raise Fail("give a file name (graphcat.py files COLLECTION lists them)")
        cmd_count(rest[0], rest[1:], by, max_mb)
    elif cmd == "lines":
        if len(rest) != 1:
            raise Fail("lines takes one file name")
        cmd_lines(rest[0], limit or SHOWN, every, max_mb)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Fail as e:
        print("graphcat.py: %s" % e, file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print("graphcat.py: file error: %s (check the disk space and the cache folder %s)" % (e, CACHE), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
