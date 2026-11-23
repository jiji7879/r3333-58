"""Offline tests for graphcat.py (decoders, invariants, filters, index, downloads with fake responses).
Run: python -m unittest discover -s skills/graph-catalogs-query/scripts -p 'test_*.py'

GRAPH5 and ICOSAHEDRON_PC are McKay's files graph5.g6 and the first graph of 5reg_12-20.pc from
https://users.cecs.anu.edu.au/~bdm/data/ (Brendan McKay, CC BY 4.0)."""

import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
import math
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("graphcat", Path(__file__).resolve().with_name("graphcat.py"))
graphcat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graphcat)

GRAPH5 = ("D?? D?_ D?o D?w D?{ DCO DCW DCc DCo DCs DCw DC{ DEk DEo DEs DEw DE{ DFw DF{ DQg DQo DQw DQ{ "
          "DTk DTw DT{ DUW DUw DU{ DV{ D]w D]{ D^{ D~{").split()
ICOSAHEDRON_PC = bytes.fromhex(
    "3e3e706c616e61725f636f64653c3c0c0203040506000106070803000102080904000103090a050001040a0b0600"
    "01050b07020002060b0c080002070c09030003080c0a040004090c0b0500050a0c070600070b0a090800")
PETERSEN = "IheA@GUAo"


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        graphcat.main(list(argv))
    return out.getvalue()


def edges(g):
    return sorted(g.edges())


def rook(k):
    """The k x k rook's graph, strongly regular (k^2, 2k-2, k-2, 2)."""
    cells = [(i, j) for i in range(k) for j in range(k)]
    pairs = [(a, b) for a in range(len(cells)) for b in range(a + 1, len(cells))
             if cells[a][0] == cells[b][0] or cells[a][1] == cells[b][1]]
    return graphcat.from_edges(k * k, pairs)


class Formats(unittest.TestCase):
    def test_numbers_from_the_specification(self):
        for n, code in ((30, [93]), (12345, [126, 66, 63, 120]), (460175067, [126, 126, 63, 90, 90, 90, 90, 90])):
            self.assertEqual(list(graphcat.encode_n(n)), code)
            self.assertEqual(graphcat.order([c - 63 for c in code]), (n, len(code)))

    def test_graph6_example(self):
        g = graphcat.graph6(bytes([68, 81, 99]))      # n=5, edges 0-2 0-4 1-3 3-4
        self.assertEqual(edges(g), [(0, 2), (0, 4), (1, 3), (3, 4)])
        self.assertEqual(g.text(), "DQc")
        with self.assertRaises(ValueError):
            graphcat.graph6(b"DQ")                      # too short
        with self.assertRaises(ValueError):
            graphcat.graph6(b"D Q")                     # space is outside ? .. ~

    def test_sparse6_and_incremental_example(self):
        g = graphcat.sparse6(b":Fa@x^")
        self.assertEqual((g.n, edges(g)), (7, [(0, 1), (0, 2), (1, 2), (5, 6)]))
        empty = graphcat.sparse6(b";a@x^", prev=g)      # the same edges again: symmetric difference
        self.assertEqual((empty.n, edges(empty)), (7, []))
        with self.assertRaises(ValueError):
            graphcat.sparse6(b";a@x^")
        loops = graphcat.from_edges(3, [(0, 0), (0, 1), (0, 1)])
        self.assertEqual((loops.get("loops"), loops.multi, loops.simple()), (1, 1, False))

    def test_sparse6_matches_graph6(self):
        for s6, g6 in ((":I`ACWqHKhhccTF", PETERSEN),):
            a, b = graphcat.sparse6(s6.encode()), graphcat.graph6(g6.encode())
            self.assertEqual(a.n, 10)
            self.assertEqual(sorted(a.get("degrees")), [3] * 10)
            self.assertEqual(a.get("girth"), 5)
            self.assertEqual(len(edges(a)), len(edges(b)))

    def test_digraph6_example(self):
        d = graphcat.digraph6(bytes([38, 68, 73, 63, 65, 79, 63]))   # 0->2 0->4 3->1 3->4
        self.assertEqual(sorted(d.edges()), [(0, 2), (0, 4), (3, 1), (3, 4)])
        self.assertEqual(d.text(), "&DI?AO?")
        self.assertEqual(graphcat.Digraph(d.n, d.out).text(), "&DI?AO?")   # re-encoding

    def test_nonzero_padding_is_not_an_encoding(self):
        for decode, text in ((graphcat.graph6, b"A@"), (graphcat.digraph6, b"&@@")):
            with self.assertRaisesRegex(ValueError, "nonzero padding bits"):
                decode(text)
        with self.assertRaisesRegex(ValueError, "nonzero padding bits"):
            graphcat.check_record(b"A@", "graph6", 2)

    def test_tournaments_and_dags(self):
        cyc, trans = graphcat.triangle(b"101", True), graphcat.triangle(b"000", True)
        self.assertEqual(sorted(cyc.edges()), [(0, 1), (1, 2), (2, 0)])
        self.assertTrue(cyc.get("strong") and cyc.get("regular"))
        self.assertFalse(trans.get("strong"))
        self.assertTrue(graphcat.triangle(b"1100101110", True).get("regular"))   # McKay's rt5.txt
        dag = graphcat.triangle(b"011", False)
        self.assertEqual(sorted(dag.edges()), [(0, 2), (1, 2)])
        with self.assertRaises(ValueError):
            graphcat.triangle(b"0110", True)

    def test_planar_code_trees_circulants(self):
        recs = list(graphcat.records_of(io.BytesIO(ICOSAHEDRON_PC), "planarcode"))
        self.assertEqual(len(recs), 1)
        g = graphcat.decode(recs[0], "planarcode")
        old_chunk, graphcat.CHUNK = graphcat.CHUNK, 7        # records split across reads
        try:
            again = list(graphcat.records_of(io.BytesIO(ICOSAHEDRON_PC * 1), "planarcode"))
            self.assertEqual(again, recs)
            with self.assertRaises(ValueError):
                list(graphcat.records_of(io.BytesIO(ICOSAHEDRON_PC[:-5]), "planarcode"))
        finally:
            graphcat.CHUNK = old_chunk
        self.assertEqual((g.n, g.get("edges"), g.get("triangles"), g.get("diameter"), g.multi), (12, 30, 20, 3, 0))
        self.assertTrue(g.get("regular") and g.get("maxdeg") == 5)
        self.assertIsNone(g.get("srg"))                 # distance-regular, not strongly regular
        t = graphcat.edge_list(b"0 4  0 5  1 5  2 5  3 5", 6)
        self.assertEqual((t.get("girth"), t.get("diameter"), t.get("connected")), (math.inf, 3, True))
        c7 = graphcat.circulant(b"3 4", 7)
        self.assertEqual((c7.get("girth"), c7.get("maxdeg")), (7, 2))
        with self.assertRaises(ValueError):
            graphcat.circulant(b"0 7", 7)

    def test_header_is_stripped(self):
        recs = list(graphcat.records_of(io.BytesIO(b">>graph6<<D??\nD?_\n"), "graph6"))
        self.assertEqual(recs, [b"D??", b"D?_"])


class Invariants(unittest.TestCase):
    def test_graph5_counts(self):
        gs = [graphcat.graph6(s.encode()) for s in GRAPH5]
        self.assertEqual(len(gs), 34)
        by_edges = [sum(g.get("edges") == m for g in gs) for m in range(11)]
        self.assertEqual(by_edges, [1, 1, 2, 4, 6, 6, 6, 4, 2, 1, 1])
        self.assertEqual(sum(g.get("connected") for g in gs), 21)
        self.assertEqual(sum(g.get("bipartite") for g in gs), 13)    # bipartite graphs on 5 vertices
        self.assertEqual(sum(g.get("triangles") == 0 for g in gs), 14)  # triangle-free graphs on 5 vertices

    def test_petersen(self):
        g = graphcat.graph6(PETERSEN.encode())
        got = [g.get(x) for x in ("n", "edges", "girth", "diameter", "triangles", "srg", "clique", "alpha", "bipartite")]
        self.assertEqual(got, [10, 15, 5, 2, 0, (10, 3, 0, 1), 2, 4, False])

    def test_srg_and_text_roundtrip(self):
        r = rook(4)
        self.assertEqual(r.get("srg"), (16, 6, 2, 2))
        again = graphcat.graph6(r.text().encode())
        self.assertEqual(edges(again), edges(r))
        self.assertIsNone(graphcat.from_edges(3, [(0, 1), (1, 2), (0, 2)]).get("srg"))   # complete
        two = graphcat.from_edges(4, [(0, 1), (2, 3)])
        self.assertEqual((two.get("components"), two.get("diameter"), two.get("srg")), (2, math.inf, (4, 1, 0, 0)))

    def test_summary_mentions_loops(self):
        g = graphcat.sparse6(b":@^")      # one vertex with a loop
        self.assertIn("loops=1", g.summary())
        self.assertEqual(g.text(), ":@^")


class Filters(unittest.TestCase):
    def test_good_filters(self):
        f = graphcat.parse_filters(["n=10", "girth>=5", "connected=yes", "srg=10,3,0,1", "diameter!=inf"], False)
        g = graphcat.graph6(PETERSEN.encode())
        self.assertTrue(graphcat.ok(g, f))
        self.assertFalse(graphcat.ok(g, graphcat.parse_filters(["bipartite=yes"], False)))
        self.assertTrue(graphcat.ok(g, graphcat.parse_filters(["srg=yes", "alpha=4"], False)))

    def test_bad_filters(self):
        for args, directed in ((["girht=5"], False), (["n=10", "n<=5"], False), (["n=5", "n=5"], False),
                               (["n>=8", "n<5"], False), (["connected=maybe"], False), (["n=\u0663"], False),
                               (["edges=inf"], False), (["srg=1,2,3"], False), (["arcs=3"], False),
                               (["edges=3"], True), (["connected=yes", "connected=no"], False), (["n="], False),
                               (["n=5", "n!=5"], False), (["regular<1"], False)):
            with self.assertRaises(graphcat.Fail, msg=args):
                graphcat.parse_filters(args, directed)


class Index(unittest.TestCase):
    def test_bundled_index(self):
        d = graphcat.index()
        self.assertIn("graph5.g6", d["by_path"])
        f = d["by_path"]["graph5.g6"]
        self.assertEqual((f["n"], f["count"], f["bytes"]), (5, 34, 136))
        self.assertEqual(sum(len(t["members"]) for t in d["vt"] if t["n"] == 12), 12)
        twelve = next(t for t in d["vt"] if t["n"] == 12)
        self.assertEqual(sum(m[3] for m in twelve["members"]), 74)
        for row in d["file_list"]:
            self.assertIn(row["c"], d["collections"])
            self.assertTrue(graphcat.SAFE_PATH.fullmatch(row["path"]), row["path"])

    def test_resolve(self):
        self.assertEqual(graphcat.resolve("graph5").path, "graph5.g6")
        self.assertEqual(graphcat.resolve("graph10.g6").path, "graph10.g6.gz")
        t = graphcat.resolve("alltrans12_k=04")
        self.assertEqual([m[0] for m in t.vt_members], ["alltrans12_k=04.gz"])
        self.assertEqual(len(graphcat.resolve("alltrans12").vt_members), 12)
        for bad in ("alltrans9", "alltrans12_k=30", "nonsense-file", "unindexed.g6", "", "graph5.d6",
                    "graph5.g6:x", "../etc/passwd"):
            with self.assertRaises(graphcat.Fail, msg=bad):
                with contextlib.redirect_stderr(io.StringIO()):
                    graphcat.resolve(bad)

    def test_listing_commands(self):
        self.assertIn("srg", run("collections", "strongly"))
        out = run("files", "ramsey", "n=13")
        self.assertIn("r35_13.g6", out)
        self.assertIn("1 stated", out)
        with self.assertRaises(graphcat.Fail):
            run("files", "ramsey", "k=3")
        self.assertIn("alltrans12", run("files", "vertex-transitive", "n<=12"))
        with self.assertRaisesRegex(graphcat.Fail, "file in collection graphs-connected"):
            run("files", "graph8c")
        with self.assertRaisesRegex(graphcat.Fail, "file in collection vertex-transitive"):
            run("files", "alltrans16_k=06")
        self.assertIn("CC BY 4.0", run("cite", "srg"))
        self.assertIn("10.5281/zenodo.4010122", run("cite", "alltrans12_k=04"))


class FakeResponse(io.BytesIO):
    def __init__(self, body, status=200, headers=None):
        super().__init__(body)
        self.status, self.code, self.headers = status, status, headers or {}


class Downloads(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.saved = graphcat.CACHE, graphcat.open_url, graphcat._index[:]
        graphcat.CACHE = Path(self.tmp.name) / "cache"
        self.calls = []
        self.files = {}

        def fake(url, method="GET", headers=None, tries=3):
            self.calls.append((method, url, (headers or {}).get("Range")))
            body, ctype = self.files[url.split("/")[-1] if "zenodo" not in url else url.split("/")[-2]]
            if isinstance(body, Exception):
                raise body
            hdr = {"Content-Length": str(len(body)), "Last-Modified": "Sun, 05 Aug 2001 12:30:43 GMT", "Content-Type": ctype}
            if headers and "Range" in headers:
                a, b = (int(x) for x in headers["Range"][6:].split("-"))
                hdr["Content-Range"] = "bytes %d-%d/%d" % (a, b, len(body))
                return FakeResponse(body[a:b + 1], 206, hdr)
            return FakeResponse(b"" if method == "HEAD" else body, 200, hdr)
        graphcat.open_url = fake

    def tearDown(self):
        graphcat.CACHE, graphcat.open_url = self.saved[:2]
        graphcat._index[:] = self.saved[2]
        self.tmp.cleanup()

    def test_fetch_filter_and_cache(self):
        self.files["graph5.g6"] = ("\n".join(GRAPH5).encode() + b"\n", "text/plain")
        out = run("graphs", "graph5", "edges=4", "connected=yes", "--edges")
        self.assertIn("(3 of 34 graphs in graph5.g6 match the filters)", out)
        self.assertIn("edges: ", out)
        self.assertIn("2  edges=2", run("count", "graph5", "--by", "edges"))
        with self.assertRaisesRegex(graphcat.Fail, "invariant for this file"):
            run("count", "graph5", "--by", "outdeg")
        self.assertIn("21 of 34 graphs", run("count", "graph5", "connected=yes"))
        gets = [c for c in self.calls if c[0] == "GET"]
        self.assertEqual(len(gets), 1)                     # cached after the first download

    def test_size_limit_and_bad_downloads(self):
        self.files["graph10.g6.gz"] = (b"x" * 30_000_000, "application/x-gzip")
        with self.assertRaises(graphcat.Fail) as e:
            run("count", "graph10.g6.gz")
        self.assertIn("above the 25 MB limit", str(e.exception))
        self.assertFalse([c for c in self.calls if c[0] == "GET"])
        self.files["graph6.g6"] = (b"<html>error</html>", "text/html")
        with self.assertRaises(graphcat.Fail):
            run("count", "graph6.g6")
        self.files["graph7.g6"] = (b"F??\nnot graph6\n", "text/plain")
        with self.assertRaises(graphcat.Fail):
            run("count", "graph7.g6")
        self.assertFalse([p for p in (graphcat.CACHE / "mckay").glob("graph7.g6*") if p.suffix != ".lock"])
        temp = Path(self.tmp.name) / "download"
        response = io.BytesIO(b"0123456789")
        with self.assertRaisesRegex(graphcat.Fail, "exceeded"):
            graphcat.stream_to(response, temp, 2)
        self.assertEqual(response.tell(), 3)
        self.assertLessEqual(temp.stat().st_size, 2)

    def test_stale_cache_is_kept_when_the_server_is_down(self):
        self.files["graph5.g6"] = ("\n".join(GRAPH5).encode() + b"\n", "text/plain")
        run("count", "graph5.g6")
        meta_file = graphcat.CACHE / "mckay" / "graph5.g6.json"
        meta = json.loads(meta_file.read_text())
        meta["checked"] = 0
        meta_file.write_text(json.dumps(meta))
        self.files["graph5.g6"] = (graphcat.Fail("cannot reach users.cecs.anu.edu.au"), None)
        out = io.StringIO()
        with contextlib.redirect_stderr(io.StringIO()) as err, contextlib.redirect_stdout(out):
            graphcat.main(["count", "graph5"])
        self.assertIn("34 of 34 graphs", out.getvalue())
        self.assertIn("using the copy downloaded on", err.getvalue())

    def test_interrupted_transfer_is_not_cached(self):
        body = "\n".join(GRAPH5).encode() + b"\n"

        class Broken(FakeResponse):
            def read(self, n=-1):
                if self.tell() > 20:
                    raise ConnectionResetError("reset by peer")
                return super().read(10)
        self.files["graph5.g6"] = (body, "text/plain")
        real = graphcat.open_url

        def broken(url, method="GET", headers=None, tries=3):
            r = real(url, method, headers, tries)
            return r if method == "HEAD" else Broken(body, 200, r.headers)
        graphcat.open_url = broken
        with self.assertRaises(graphcat.Fail) as e:
            run("count", "graph5.g6")
        self.assertIn("interrupted", str(e.exception))
        self.assertFalse([p for p in (graphcat.CACHE / "mckay").glob("graph5.g6*") if p.suffix != ".lock"])

    def test_expired_tree_archive_is_checked_once_per_query(self):
        name = "tree4.all.tar.gz"
        archive = io.BytesIO()
        with tarfile.open(fileobj=archive, mode="w:gz") as tf:
            tree = b"0 1 1 2 2 3\n"
            member = tarfile.TarInfo("tree4.3.txt")
            member.size = len(tree)
            tf.addfile(member, io.BytesIO(tree))
        self.files[name] = (archive.getvalue(), "application/x-gzip")
        run("count", name)
        path = graphcat.mckay_path(name)
        meta = graphcat.read_meta(path)
        meta["checked"] = 0
        graphcat.write_meta(path, meta)
        self.files[name] = (graphcat.Fail("cannot reach users.cecs.anu.edu.au"), None)
        self.calls.clear()
        self.assertIn("1 of 1 graphs", run("count", name))
        self.assertEqual([method for method, *_ in self.calls], ["HEAD"])

    def test_date_matches_the_downloaded_revision(self):
        original = graphcat.open_url
        self.files["graph5.g6"] = (b"D??\n", "text/plain")

        def changed(url, method="GET", headers=None, tries=3):
            answer = original(url, method, headers, tries)
            if method == "GET":
                answer.headers["Last-Modified"] = "Mon, 06 Aug 2001 12:30:43 GMT"
            return answer

        with patch.object(graphcat, "open_url", changed):
            run("count", "graph5")
        self.assertIn("server last modified 2001-08-06", run("cite", "graph5"))

    def census_tar(self, name, lines):
        data = gzip.compress("\n".join(lines).encode() + b"\n")
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w", format=tarfile.PAX_FORMAT) as tf:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.pax_headers = {"comment": "x" * 10}
            tf.addfile(info, io.BytesIO(data))
        raw = buf.getvalue()
        with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
            m = tf.getmember(name)
            return raw, [name, m.offset_data - 512, m.size, len(lines)]

    def test_census_member_by_range(self):
        petersen_k3 = [PETERSEN]
        raw, member = self.census_tar("alltrans10_k=03.gz", petersen_k3)
        d = graphcat.index()
        fake_vt = dict(next(t for t in d["vt"] if t["n"] == 10), members=[member], bytes=len(raw),
                       md5=hashlib.md5(raw).hexdigest())
        graphcat._index[0] = dict(d, vt=[fake_vt if t["n"] == 10 else t for t in d["vt"]])
        self.files["alltrans10.tar"] = (raw, "application/octet-stream")
        out = run("graphs", "alltrans10", "maxdeg=3", "srg=yes")
        self.assertIn("srg=(10,3,0,1)", out)
        self.assertIn("(1 of 1 graphs", out)
        self.assertTrue(all(c[2] for c in self.calls))     # only range requests
        bad = [member[0].replace("k=03", "k=05")] + member[1:]
        fake_vt["members"] = [bad]
        with self.assertRaises(graphcat.Fail):
            graphcat.fetch_vt(fake_vt, bad)

    def test_raw_lines(self):
        self.files["had8.txt"] = (b"FF AA CC 99 F0 A5 C3 96\n", "text/plain")
        out = run("lines", "hadamard/had8.txt")
        self.assertIn("FF AA CC 99", out)
        self.assertIn("(1 record)", out)
        with self.assertRaises(graphcat.Fail):
            run("graphs", "hadamard/had8.txt")

    def test_lines_reports_member_position(self):
        sources = [(label, "raw", None, lambda: io.BytesIO(b"data\n"), None)
                   for label in ("tar:member1", "tar:member2")]
        with patch.object(graphcat, "sources", return_value=sources):
            out = run("lines", "alltrans12")
        self.assertIn("tar:member1 #1: data\ntar:member2 #1: data\n(2 records)", out)


if __name__ == "__main__":
    unittest.main()
