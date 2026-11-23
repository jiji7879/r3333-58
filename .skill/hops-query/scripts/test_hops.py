"""Offline tests for hops.py. Run: python -m unittest discover -s skills/hops-query/scripts -p 'test_*.py'"""

import contextlib
import copy
import importlib.util
import io
import json
import tarfile
import tempfile
import time
import unittest
import urllib.error
from pathlib import Path

spec = importlib.util.spec_from_file_location("hops", Path(__file__).resolve().with_name("hops.py"))
hops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hops)

# A captured sample: content/api/0oCyaG.json (outerplanar) from https://github.com/vaclavblazej/parameters
# at commit b0e680e6ad220a8081e0db59229a158063097636, as the HOPS website serves it at
# https://vaclavblazej.github.io/parameters/api/0oCyaG.json, trimmed to the results about the sets below
# and with related_sets filled in by the test. HOPS content: MIT License, Copyright (c) 2023-2024
# Václav Blažej & contributors. See ../LICENSES/HOPS-MIT.txt for the licence text.
CAPTURED = (
    r'{"id":{"code":"0oCyaG","_marker":null},"name":"outerplanar","typ":"GraphClass","relevance":5'
    r',"aka":[],"abbr":null,"tags":[{"id":{"code":"lJJaYb","_marker":null},"name":"topology"}],"pr'
    r'oviders":[{"provider_name":"ISGCI","set":{"code":"0oCyaG","_marker":null},"url":"https://www'
    r'.graphclasses.org/classes/gc_110.html"}],"timeline":[{"preview":{"id":{"code":"r2Lwky","_mar'
    r'ker":null},"sourcekey":{"Bibtex":{"key":"Diestel2017","name":"Graph Theory by Diestel","entr'
    r'y":"@book{Diestel2017,\nauthor = {Reinhard Diestel},\nedition = {5th},\nisbn = {3662536218},'
    r'\npublisher = {Springer Publishing Company, Incorporated},\ntitle = {Graph Theory},\nyear = '
    r'{2017},\n}","relevance":7}},"time":{"year":2017,"month":null,"day":null}},"source":{"code":"'
    r'r2Lwky","_marker":null},"sourcekey":{"Bibtex":{"key":"Diestel2017","name":"Graph Theory by D'
    r'iestel","entry":"@book{Diestel2017,\nauthor = {Reinhard Diestel},\nedition = {5th},\nisbn = '
    r'{3662536218},\npublisher = {Springer Publishing Company, Incorporated},\ntitle = {Graph Theo'
    r'ry},\nyear = {2017},\n}","relevance":7}},"showed":[{"id":{"code":"6Q0kuL","_marker":null},"t'
    r'ext":"A graph is called outerplanar if it has a drawing in which every vertex lies on the bo'
    r'undary of the outer face.","fact":{"Definition":["Original",{"code":"0oCyaG","_marker":null}'
    r']},"page":{"Pp":115}}]},{"preview":{"id":{"code":"BOFCWg","_marker":null},"sourcekey":{"Bibt'
    r'ex":{"key":"Bodlaender1998","name":"A partial $k$-arboretum of graphs with bounded treewidth'
    r' by Bodlaender","entry":"@article{Bodlaender1998,\nauthor = {Hans L. Bodlaender},\ndoi = {10'
    r'.1016/S0304-3975(97)00228-4},\nissn = {0304-3975},\njournaltitle = {Theoretical Computer Sci'
    r'ence},\nnumber = {1},\npages = {1--45},\ntitle = {A partial $k$-arboretum of graphs with bou'
    r'nded treewidth},\nvolume = {209},\nyear = {1998},\n}","relevance":6}},"time":{"year":1998,"m'
    r'onth":null,"day":null}},"source":{"code":"BOFCWg","_marker":null},"sourcekey":{"Bibtex":{"ke'
    r'y":"Bodlaender1998","name":"A partial $k$-arboretum of graphs with bounded treewidth by Bodl'
    r'aender","entry":"@article{Bodlaender1998,\nauthor = {Hans L. Bodlaender},\ndoi = {10.1016/S0'
    r'304-3975(97)00228-4},\nissn = {0304-3975},\njournaltitle = {Theoretical Computer Science},\n'
    r'number = {1},\npages = {1--45},\ntitle = {A partial $k$-arboretum of graphs with bounded tre'
    r'ewidth},\nvolume = {209},\nyear = {1998},\n}","relevance":6}},"showed":[{"id":{"code":"VdNTH'
    r'Z","_marker":null},"text":"Lemma 78. Every outerplanar graph $G=(V,E)$ has treewidth at most'
    r' 2.","fact":{"Relation":["Original",{"code":"0oCyaG_5Q7fuR","_marker":null}]},"page":{"Pp":3'
    r'4}}]},{"preview":{"id":{"code":"myit4D","_marker":null},"sourcekey":{"Other":{"name":"unknow'
    r'n source","description":"This knowledge was added to the database without tying it to an app'
    r'ropriate resource."}},"time":{"year":null,"month":null,"day":null}},"source":{"code":"myit4D'
    r'","_marker":null},"sourcekey":{"Other":{"name":"unknown source","description":"This knowledg'
    r'e was added to the database without tying it to an appropriate resource."}},"showed":[{"id":'
    r'{"code":"cF8esN","_marker":null},"text":"","fact":{"Relation":[{"Noted":"Todo"},{"code":"0oC'
    r'yaG_Gt22Ik","_marker":null}]},"page":"NotApplicable"}]},{"preview":{"id":{"code":"9kg0oo","_'
    r'marker":null},"sourcekey":{"Other":{"name":"assumed","description":"Is axiomatic knowledge f'
    r'rom the viewpoint of HOPS website."}},"time":{"year":null,"month":null,"day":null}},"source"'
    r':{"code":"9kg0oo","_marker":null},"sourcekey":{"Other":{"name":"assumed","description":"Is a'
    r'xiomatic knowledge from the viewpoint of HOPS website."}},"showed":[{"id":{"code":"ZiCzGe","'
    r'_marker":null},"text":"","fact":{"Relation":["Assumed",{"code":"0oCyaG_loZ5LD","_marker":nul'
    r'l}]},"page":"NotApplicable"},{"id":{"code":"ZiCzGe","_marker":null},"text":"","fact":{"Relat'
    r'ion":["Assumed",{"code":"loZ5LD_0oCyaG","_marker":null}]},"page":"NotApplicable"},{"id":{"co'
    r'de":"_IM7Tf","_marker":null},"text":"assumed","fact":{"Relation":["Original",{"code":"0oCyaG'
    r'_0oCyaG","_marker":null}]},"page":"NotApplicable"}]}],"related_sets":"FILLED BY THE TEST","d'
    r'isplayed_definition":["A planar graph that can be drawin in a way where one face is incident'
    r' to all the vertices."]}'
)

ID = {"outerplanar": "0oCyaG", "planar": "loZ5LD", "tw": "5Q7fuR", "bw": "lIcmuR", "cw": "wg5HuV",
      "grid": "lfYXuK", "complete": "EhdXNA", "stable": "jHXy6Y", "epm": "Gt22Ik"}
SETS = {  # id: name, type, relevance, aka, abbreviation (the captured outerplanar file has its own)
    "loZ5LD": ("planar", "GraphClass", 8, [], None),
    "5Q7fuR": ("treewidth", "Parameter", 9, [], "tw"),
    "lIcmuR": ("branch width", "Parameter", 4, [], None),
    "wg5HuV": ("clique-width", "Parameter", 7, [], "cw"),
    "lfYXuK": ("grid", "GraphClass", 6, [], None),
    "EhdXNA": ("complete", "GraphClass", 9, [], None),
    "jHXy6Y": ("monadically stable", {"Property": "Is"}, 5, [], None),
    "Gt22Ik": ("excluded planar minor", {"Property": "Has"}, 4, [], None),
}
BIB = {"ZQrXS8": ("courcelle2000", "Upper bounds to the clique width of graphs by Courcelle, Olariu", 2000),
       "XlBXyo": ("Sasak2010", "Comparing 17 graph parameters by Sasák", 2010),
       "A82svt": ("RobertsonSymour1986V", "Graph minors. V. Excluding a planar graph by Robertson, Seymour", 1986),
       "nRO7AG": ("Vatshelle2012", "New Width Parameters of Graphs by Vatshelle", 2012),
       "Cnj001": ("conj2020", "A conjecture paper by Someone", 2020)}
# (source, showed id, status, relation "A_B" or definition "def:A", page, text), besides the captured ones
FACTS = [
    ("BOFCWg", "L88aaa", "Original", "lfYXuK_5Q7fuR", {"Pp": 37}, "Lemma 88. The treewidth of an $n \\times n$ grid"),
    ("ZQrXS8", "cw0001", "Original", "5Q7fuR_wg5HuV", {"Pp": 18}, "$cwd(G) \\le 2^{twd(G)+1}+1$"),
    ("XlBXyo", "sa0001", "Original", "EhdXNA_5Q7fuR", {"Pp": 17}, "Theorem 2.2"),
    ("myit4D", "uk0001", {"Noted": "Todo"}, "EhdXNA_wg5HuV", "NotApplicable", ""),
    ("myit4D", "uk0002", {"Noted": "Todo"}, "lfYXuK_wg5HuV", "NotApplicable", ""),
    ("9kg0oo", "as0001", "Assumed", "lfYXuK_loZ5LD", "NotApplicable", ""),
    ("9kg0oo", "as0002", "Assumed", "EhdXNA_loZ5LD", "NotApplicable", ""),
    ("A82svt", "gm0001", {"Noted": {"Text": "Robertson, Seymour, Graph minors V"}}, "Gt22Ik_5Q7fuR", "Unknown",
     "see [[A82svt]] and [planar](../loZ5LD)"),
    ("nRO7AG", "va0001", "Original", "5Q7fuR_lIcmuR", {"Pp": 40}, "Theorem 4.2.5."),
    ("nRO7AG", "va0001", "Original", "lIcmuR_5Q7fuR", {"Pp": 40}, "Theorem 4.2.5."),
    ("nRO7AG", "va0002", "Derivative", "def:lIcmuR", {"Pp": 39}, "Branch width is ..."),
    ("Cnj001", "cj0001", "Conjectured", "jHXy6Y_wg5HuV", "NotApplicable", "We conjecture that ..."),
]
INCLUSIONS = ["0oCyaG_loZ5LD", "0oCyaG_5Q7fuR", "0oCyaG_Gt22Ik", "5Q7fuR_lIcmuR", "lIcmuR_5Q7fuR", "5Q7fuR_wg5HuV",
              "EhdXNA_wg5HuV", "lfYXuK_loZ5LD", "Gt22Ik_5Q7fuR"]
EXCLUSIONS = ["loZ5LD_0oCyaG", "lfYXuK_5Q7fuR", "EhdXNA_5Q7fuR", "EhdXNA_loZ5LD", "lfYXuK_wg5HuV"]


def cid(x):
    return {"code": x, "_marker": None}


def universe():
    """{id: API file} for the nine sets, with relations closed as HOPS closes them."""
    captured = json.loads(CAPTURED)
    ids = sorted(SETS) + ["0oCyaG"]
    inc = {(a, a) for a in ids} | {tuple(r.split("_")) for r in INCLUSIONS}
    for k in ids:
        for i in ids:
            for j in ids:
                if (i, k) in inc and (k, j) in inc:
                    inc.add((i, j))
    # x =/=> y, x => a and b => y give a =/=> b
    exc = {(a, b) for a in ids for b in ids for x, y in (r.split("_") for r in EXCLUSIONS)
           if (x, a) in inc and (b, y) in inc}
    assert not inc & exc
    names = {i: SETS[i][0] for i in SETS}
    names["0oCyaG"] = "outerplanar"
    typs = {i: SETS[i][1] for i in SETS}
    typs["0oCyaG"] = "GraphClass"

    def preview(x):
        return {"id": cid(x), "name": names[x], "typ": typs[x], "relevance": 1}

    def group(xs):
        xs = [preview(x) for x in sorted(xs)]
        return {"minimal": xs, "maximal": xs, "all": xs}

    def related(a):
        eq = {b for b in ids if (a, b) in inc and (b, a) in inc}
        sup = {b for b in ids if (a, b) in inc} - eq
        sub = {b for b in ids if (b, a) in inc} - eq
        return {"equivsets": [preview(x) for x in sorted(eq)], "supersets": group(sup), "subsets": group(sub),
                "super_exclusions": group(b for b in ids if (a, b) in exc),
                "sub_exclusions": group(b for b in ids if (b, a) in exc),
                "unknown": group(set(ids) - sup - sub)}

    sources = {t["source"]["code"]: (t["sourcekey"], t["preview"]["time"]) for t in captured["timeline"]}
    for sid, (key, name, year) in BIB.items():
        sources[sid] = ({"Bibtex": {"key": key, "name": name, "entry": "@article{%s,\n}" % key, "relevance": 3}},
                        {"year": year, "month": None, "day": None})
    facts = list(FACTS)
    for t in captured["timeline"]:
        for s in t["showed"]:
            kind, (status, ref) = next(iter(s["fact"].items()))
            facts.append((t["source"]["code"], s["id"]["code"], status,
                          ref["code"] if kind == "Relation" else "def:" + ref["code"], s["page"], s["text"]))
    files = {}
    for a in ids:
        if a == "0oCyaG":
            d = copy.deepcopy(captured)
        else:
            name, typ, rel, aka, abbr = SETS[a]
            timeline = []
            for src in sorted({f[0] for f in facts}, key=lambda s: -(sources[s][1]["year"] or 0)):
                showed = []
                for s, sid, status, ref, page, text in facts:
                    if s != src or a not in ref[4:].split("_") and a != ref[4:] and a not in ref.split("_"):
                        continue
                    fact = ({"Definition": [status, cid(ref[4:])]} if ref.startswith("def:")
                            else {"Relation": [status, cid(ref)]})
                    showed.append({"id": cid(sid), "text": text, "fact": fact, "page": page})
                if showed:
                    key, when = sources[src]
                    timeline.append({"preview": {"id": cid(src), "sourcekey": key, "time": when}, "source": cid(src),
                                     "sourcekey": key, "showed": showed})
            d = {"id": cid(a), "name": name, "typ": typ, "relevance": rel, "aka": aka, "abbr": abbr, "tags": [],
                 "providers": [], "timeline": timeline, "related_sets": None,
                 "displayed_definition": ["see [[i56ihO]]"] if a == "5Q7fuR" else []}
        d["related_sets"] = related(a)
        files[a] = d
    return files


def encode(files):
    return {k: json.dumps(v, ensure_ascii=False).encode() for k, v in files.items()}


def index():
    ix = hops.build(encode(universe()))
    ix.update(commit="b" * 40, date="2026-02-23", fetched="2026-11-21")
    return ix


def run(fn, *args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        fn(*args)
    return out.getvalue(), err.getvalue()


class Cached(unittest.TestCase):
    """Commands run against the fixture index in a temporary cache that was refreshed just now."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = hops.CACHE
        hops.CACHE = Path(self.tmp.name)
        self.ix = index()
        (hops.CACHE / "index.json").write_text(json.dumps(self.ix))
        (hops.CACHE / "state.json").write_text(json.dumps({"checked": time.time(), "commit": "b" * 40}))

    def tearDown(self):
        hops.CACHE = self.old
        self.tmp.cleanup()

    def main(self, *argv):
        return run(hops.main, list(argv))


class Parse(unittest.TestCase):
    def test_captured_sample(self):
        ix = index()
        self.assertTrue(hops.usable(ix))
        o = ix["sets"]["0oCyaG"]
        self.assertEqual((o["name"], o["typ"], o["rel"], o["tags"]), ("outerplanar", "GraphClass", 5, ["topology"]))
        self.assertEqual(o["providers"], [["ISGCI", "https://www.graphclasses.org/classes/gc_110.html"]])
        self.assertEqual(o["timeline"], ["r2Lwky", "BOFCWg", "myit4D", "9kg0oo"])
        self.assertEqual(ix["sources"]["BOFCWg"]["key"], "Bodlaender1998")
        self.assertEqual(ix["sources"]["myit4D"]["kind"], "other")
        mine = [f for f in ix["facts"] if "0oCyaG" in (f["a"], f["b"])]
        self.assertEqual(sorted((f["kind"], f["status"], f["noted"], f["page"]) for f in mine), [
            ("definition", "original", None, 115), ("relation", "assumed", None, None),
            ("relation", "assumed", None, None), ("relation", "noted", "todo", None),
            ("relation", "original", None, 34)])   # the self-relation outerplanar => outerplanar is left out
        self.assertEqual(ix["sets"]["jHXy6Y"]["typ"], "Property:Is")
        gm = [f for f in ix["facts"] if f["id"] == "gm0001"][0]
        self.assertEqual((gm["noted"], gm["page"]), ("text: Robertson, Seymour, Graph minors V", "unknown"))

    def test_relations(self):
        ix = index()
        st = lambda a, b: hops.status(ix, ID[a], ID[b])
        self.assertEqual([st("outerplanar", "cw"), st("cw", "tw"), st("tw", "bw"), st("tw", "planar"),
                          st("stable", "cw"), st("planar", "outerplanar")], ["yes", "no", "eq", "unknown", "unknown", "no"])

    def assertChanged(self, files, words):
        with self.assertRaises(hops.Fail) as c:
            hops.build(encode(files))
        self.assertIn("format has changed", str(c.exception))
        self.assertIn(words, str(c.exception))

    def test_format_changes_are_refused(self):
        f = universe()
        f["0oCyaG"]["transfers"] = []
        self.assertChanged(f, "exactly the fields")
        f = universe()
        f["5Q7fuR"]["timeline"][0]["showed"][0]["fact"] = {"Relation": ["Disputed", cid("5Q7fuR_wg5HuV")]}
        self.assertChanged(f, "status")
        f = universe()
        f["loZ5LD"]["typ"] = "Hypergraph"
        self.assertChanged(f, "typ")
        f = universe()
        f["loZ5LD"]["related_sets"]["subsets"] = {"minimal": [], "maximal": [], "all": []}
        self.assertChanged(f, "not the reverse")
        f = universe()
        f["loZ5LD"]["related_sets"]["unknown"] = {"minimal": [], "maximal": [], "all": []}
        self.assertChanged(f, "meaning of related_sets.unknown")
        f = universe()
        f["loZ5LD"]["id"] = cid("lfYXuK")
        self.assertChanged(f, "differs from the file name")
        f = universe()
        f["0oCyaG"]["timeline"][1]["showed"][0]["page"] = {"Section": 3}
        self.assertChanged(f, "unknown page")
        with self.assertRaises(hops.Fail):
            hops.build({"loZ5LD": b"<html>maintenance</html>"})

    def test_expand(self):
        ix = index()
        self.assertEqual(hops.expand(ix, "see [[5Q7fuR]] and  [planar](../loZ5LD)\n[[zzzzzz]]"),
                         "see treewidth [5Q7fuR] and planar [loZ5LD] [[zzzzzz]]")


def archive(files, sha, top=None, extra=()):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for path, data in list(files.items()) + list(extra):
            info = tarfile.TarInfo("%s/%s" % (top or "parameters-" + sha, path))
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


class Archive(unittest.TestCase):
    def setUp(self):
        self.sha = "a" * 40
        self.files = {"content/api/%s.json" % k: v for k, v in encode(universe()).items()}
        self.files["content/api/simple.json"] = b'{"date": "2025-10-29", "sets": [], "relations": []}'
        self.files["README.md"] = b"readme"
        self.tree = {"truncated": False, "tree": [{"path": p, "type": "blob", "sha": hops.blob_id(d)}
                                                   for p, d in self.files.items()]}

    def test_verified(self):
        got = hops.api_files(archive(self.files, self.sha), self.sha, self.tree)
        self.assertEqual(sorted(got), sorted(ID.values()))   # simple.json is not a set file
        self.assertEqual(len(hops.build(got)["sets"]), 9)

    def test_refused(self):
        bad = dict(self.files, **{"content/api/loZ5LD.json": b"{}"})
        for raw, tree, words in [
                (archive(bad, self.sha), self.tree, "blob id"),
                (archive(self.files, self.sha, top="parameters-" + "c" * 40), self.tree, "not of commit"),
                (archive(self.files, self.sha)[:-200], self.tree, "damaged"),
                (archive(self.files, self.sha), dict(self.tree, truncated=True), "whole file tree"),
                (archive({k: v for k, v in self.files.items() if "loZ5LD" not in k}, self.sha), self.tree, "lacks 1"),
                (archive(self.files, self.sha), {"truncated": False, "tree": []}, "layout has changed")]:
            with self.assertRaises(hops.Fail) as c:
                hops.api_files(raw, self.sha, tree)
            self.assertIn(words, str(c.exception))


class Commands(Cached):
    def test_relation_chain_and_witness(self):
        out, _ = self.main("relation", "outerplanar", "CW")
        self.assertIn("Does being a subclass of outerplanar imply bounded clique-width? yes", out)
        self.assertIn("a chain of results recorded in HOPS: outerplanar => treewidth => clique-width", out)
        self.assertIn("Lemma 78. Every outerplanar graph", out)
        self.assertIn("Does bounded clique-width imply being a subclass of outerplanar? no (exclusion)", out)
        self.assertIn("In short: being a subclass of outerplanar implies bounded clique-width; the converse fails", out)
        out, _ = self.main("relation", "clique width", "https://vaclavblazej.github.io/parameters/html/5Q7fuR/")
        self.assertIn("HOPS records that being a subclass of complete does not imply bounded treewidth:", out)
        self.assertIn("and HOPS has that being a subclass of complete implies bounded clique-width", out)
        self.assertIn("so a graph class that is a subclass of complete but has unbounded treewidth also has bounded "
                      "clique-width.", out)

    def test_relation_kinds(self):
        out, _ = self.main("relation", "planar", "cw")
        self.assertIn("In short: incomparable: neither implies the other.", out)
        out, _ = self.main("relation", "planar", "outerplanar")
        self.assertIn("Results recorded in HOPS for the direction planar to outerplanar:", out)
        self.assertNotIn("planar => outerplanar", out)
        out, _ = self.main("relation", "tw", "branch width")
        self.assertIn("yes (equivalent)", out)
        self.assertIn("equivalent in HOPS: a graph class has bounded treewidth exactly when it has bounded branch", out)
        out, _ = self.main("relation", "monadically stable", "cw")
        self.assertIn("Does being monadically stable imply bounded clique-width? unknown to HOPS", out)
        self.assertIn("CONJECTURED (posed as an open problem; HOPS does not use it)", out)
        self.assertIn("unknown to HOPS in both directions", out)
        out, _ = self.main("relation", "excluded planar minor", "tw")
        self.assertIn("stated as known, proved elsewhere: in Robertson, Seymour, Graph minors V", out)
        self.assertIn("converse is unknown to HOPS", out)
        out, _ = self.main("relation", "tw", "5Q7fuR")
        self.assertIn("Both name the same HOPS set.", out)

    def test_bounds(self):
        out, _ = self.main("bounds", "outerplanar")
        self.assertIn("Being a subclass of outerplanar implies 5 sets", out)
        self.assertIn("the 2 from which the rest follow by transitivity (--all lists all 5):\n"
                      "  Gt22Ik  property     excluded planar minor\n  loZ5LD  graph class  planar\n", out)
        self.assertIn("0 sets imply being a subclass of outerplanar", out)
        out, _ = self.main("bounds", "complete")
        self.assertIn("Being a subclass of complete implies 1 set (", out)
        self.assertIn("\n2 sets do not imply being a subclass of complete", out)
        out, _ = self.main("bounds", "outerplanar", "--all")
        self.assertIn("Being a subclass of outerplanar implies 5 sets (every graph class with it has each; HOPS: it "
                      "upper bounds them):\n  lIcmuR  parameter    branch width\n", out)
        self.assertNotIn("from which the rest follow", out)
        out, _ = self.main("bounds", "jHXy6Y")
        self.assertIn("Unknown to HOPS whether being monadically stable implies them: 8 sets", out)

    def test_find_show_source(self):
        out, _ = self.main("find", "width")
        self.assertIn("3 sets match 'width': 3 by name", out)
        self.assertIn("5Q7fuR  parameter    treewidth (abbr. tw)", out)
        out, _ = self.main("find", "incident")
        self.assertIn("1 set matches 'incident': 0 by name, alias or abbreviation, then 1 by definition.", out)
        self.assertIn("outerplanar  [in definition]", out)
        out, _ = self.main("show", "TREE-WIDTH")
        self.assertIn("definition: see [[i56ihO]]", out)    # a source this fixture does not have stays as is
        self.assertIn("equivalent in HOPS (a graph class has one exactly when it has the other): branch width", out)
        self.assertIn("relations in HOPS: bounded treewidth implies 1 set and does not imply 0; 2 sets imply it", out)
        self.assertIn("recorded in HOPS: 7 results from 5 sources\n", out)
        out, _ = self.main("source", "bodlaender1998")
        self.assertIn("@article{Bodlaender1998,", out)
        self.assertIn("2 results recorded in HOPS from it", out)
        out, _ = self.main("source", "graph")
        self.assertIn("sources match 'graph'", out)

    def test_names(self):
        self.assertEqual(hops.resolve(self.ix, "https://vaclavblazej.github.io/parameters/api/0oCyaG.json"), "0oCyaG")
        for bad, words in (("width", "similar: "), ("pathwidth", "hops.py find"), ("", "give a set")):
            with self.assertRaises(hops.Fail) as c:
                hops.resolve(self.ix, bad)
            self.assertIn(words, str(c.exception))
        self.ix["sets"]["lIcmuR"]["aka"] = ["TW"]
        with self.assertRaises(hops.Fail) as c:
            hops.resolve(self.ix, "tw")
        self.assertIn("names 2 sets", str(c.exception))

    def test_bad_arguments(self):
        for argv, words in ((["show"], "takes one set"), (["relation", "tw"], "two sets"),
                            (["find"], "takes words"), (["show", "tw", "--all"], "--all goes with"),
                            (["find", "w", "--all", "--all"], "given twice"),
                            (["show", "tw", "--json"], "unknown option"),
                            (["find", "--", "-"], "unknown option"), (["source"], "BibTeX key"),
                            (["find", "..."], "letters or digits")):
            with self.assertRaises(hops.Fail) as c:
                self.main(*argv)
            self.assertIn(words, str(c.exception), argv)
        self.assertEqual(run(hops.main, ["help"])[0].count("hops.py relation A B"), 1)


class Cache(Cached):
    def setUp(self):
        super().setUp()
        self.calls = []
        self.orig = hops.refresh

    def tearDown(self):
        hops.refresh = self.orig
        super().tearDown()

    def fake(self, result):
        def refresh(ix):
            self.calls.append(ix and ix["commit"])
            if isinstance(result, Exception):
                raise result
            return result
        hops.refresh = refresh

    def test_fresh_cache_is_not_refreshed(self):
        self.fake(hops.Fail("should not be called"))
        self.assertEqual(hops.load()["commit"], "b" * 40)
        self.assertEqual(self.calls, [])

    def test_failed_refresh_keeps_the_old_copy(self):
        self.fake(hops.Fail("GitHub is down"))
        _, err = run(lambda: self.assertEqual(hops.load(time.time() + 2 * 86400)["commit"], "b" * 40))
        self.assertEqual(len(self.calls), 1)
        self.assertIn("GitHub is down", err)
        self.assertIn("could not check GitHub for newer HOPS data: GitHub is down. Using the cached copy of "
                      "content commit bbbbbbb of 2026-02-23", err)

    def test_no_copy_retries_after_ten_minutes(self):
        (hops.CACHE / "index.json").unlink()
        (hops.CACHE / "state.json").unlink()
        self.fake(hops.Fail("cannot reach codeload"))
        now = time.time()
        for t in (now, now + 60):
            with self.assertRaises(hops.Fail) as c:
                hops.load(t)
        self.assertIn("the last attempt failed: cannot reach codeload; the next attempt is after", str(c.exception))
        self.assertIn("cannot reach codeload", str(c.exception))
        self.assertEqual(len(self.calls), 1)
        self.fake(self.ix)
        self.assertEqual(hops.load(now + 601)["commit"], "b" * 40)
        self.assertEqual(len(self.calls), 2)

    def test_damaged_cache(self):
        for text in ('{"version": 1, "sets": []}', "[1, 2", json.dumps(dict(self.ix, version=0))):
            (hops.CACHE / "index.json").write_text(text)
            self.assertIsNone(hops.read_index())
        self.fake(self.ix)
        self.assertEqual(hops.load()["commit"], "b" * 40)    # state names a commit, but the index is unusable

    def test_refresh_same_commit_downloads_nothing(self):
        hops.refresh = self.orig
        head = {"sha": "b" * 40, "commit": {"tree": {"sha": "c" * 40}, "committer": {"date": "2026-02-23T15:15:29Z"}}}
        old_get, old_json = hops.get, hops.get_json
        hops.get_json = lambda url, tries=3: head
        hops.get = lambda *a, **k: self.fail("downloaded again")
        try:
            self.assertIs(hops.refresh(self.ix), self.ix)
            head["sha"] = "not a sha"
            with self.assertRaises(hops.Fail):
                hops.refresh(self.ix)
        finally:
            hops.get, hops.get_json = old_get, old_json


class Network(unittest.TestCase):
    def setUp(self):
        self.urlopen, self.sleep = hops.urllib.request.urlopen, hops.time.sleep
        hops.time.sleep = lambda s: None

    def tearDown(self):
        hops.urllib.request.urlopen, hops.time.sleep = self.urlopen, self.sleep

    def answer(self, *results):
        results = list(results)

        def urlopen(req, timeout=None):
            r = results.pop(0)
            if isinstance(r, Exception):
                raise r
            return _Body(r)
        hops.urllib.request.urlopen = urlopen

    def http(self, code, headers=None):
        import email.message
        msg = email.message.Message()
        for k, v in (headers or {}).items():
            msg[k] = v
        return urllib.error.HTTPError("https://api.github.com/x", code, "x", msg, io.BytesIO(b""))

    def test_errors(self):
        for results, url, words in (
                ([self.http(404)], "https://codeload.github.com/x", "HTTP 404"),
                ([self.http(503, {"Retry-After": "120"})], "https://codeload.github.com/x", "asks to wait 120"),
                ([self.http(403, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "0"})],
                 "https://api.github.com/repos/x", "API limit"),
                ([OSError("offline")] * 3, "https://api.github.com/repos/x", "cannot reach")):
            self.answer(*results)
            with self.assertRaises(hops.Fail) as c:
                hops.get(url)
            self.assertIn(words, str(c.exception))

    def test_retry_and_limit(self):
        self.answer(self.http(500), b'{"ok": 1}')
        self.assertEqual(hops.get_json("https://api.github.com/x"), {"ok": 1})
        self.answer(b"x" * 11)
        with self.assertRaises(hops.Fail):
            hops.get("https://codeload.github.com/x", limit=10)
        self.answer(b"<html>")
        with self.assertRaises(hops.Fail):
            hops.get_json("https://api.github.com/x")


class _Body(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


if __name__ == "__main__":
    unittest.main()
