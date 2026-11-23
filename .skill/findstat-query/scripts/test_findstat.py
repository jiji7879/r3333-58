"""Offline tests for findstat.py's input checks. Run: python -m unittest discover -s skills/findstat-query/scripts -p 'test_*.py'"""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("findstat", Path(__file__).resolve().with_name("findstat.py"))
findstat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(findstat)


class Values(unittest.TestCase):
    def test_pairs(self):
        text = "# inversions\n[1] => 0\n[1,2] => 0\n[2,1] => 1\n\n{{1,3},{2}} => -2\n"
        self.assertEqual(findstat.parse_values(text),
                         [("[1]", "0"), ("[1,2]", "0"), ("[2,1]", "1"), ("{{1,3},{2}}", "-2")])

    def test_graph_object_keeps_its_commas(self):
        self.assertEqual(findstat.parse_values("([],1) => 0\n([(0,1)],2) => 1\n([],2) => 0\n")[1],
                         ("([(0,1)],2)", "1"))

    def test_refusals(self):
        for bad in ("[1] 0\n[2] 1\n[3] 2\n", "[1] => x\n[2] => 1\n[3] => 2\n", "[1] => 0\n[1,2] => 0\n"):
            with self.assertRaises(findstat.Fail):
                findstat.parse_values(bad)

    def test_ids(self):
        self.assertEqual(findstat.stat_id("18"), "St000018")
        self.assertEqual(findstat.stat_id("St000018"), "St000018")
        with self.assertRaises(findstat.Fail):
            findstat.stat_id("Mp00001")


class Chains(unittest.TestCase):
    def test_order_of_application(self):
        names = {"St000008": "major index of a composition"}
        maps = {"Mp00071": "descent composition", "Mp00062": "Lehmer-code to major-code bijection"}
        self.assertEqual(findstat.describe_chain("St000008oMp00071oMp00062", names, maps),
                         "apply Mp00062 (Lehmer-code to major-code bijection), then Mp00071 "
                         "(descent composition), then St000008 (major index of a composition)")


class Offline(unittest.TestCase):
    """findstat.request replaced by canned answers."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.saved = findstat.CACHE, findstat.request
        findstat.CACHE = Path(self.tmp.name)

    def tearDown(self):
        findstat.CACHE, findstat.request = self.saved
        self.tmp.cleanup()

    def test_a_bad_refresh_keeps_the_old_cache(self):
        good = {"included": {"Maps": {"Mp00001": {"Name": "a map"}}}}
        (findstat.CACHE / "maps.json").write_text(json.dumps(good))
        old = 0   # make the cached copy expired
        import os
        os.utime(findstat.CACHE / "maps.json", (old, old))
        findstat.request = lambda url, data=None: {"included": {}, "data": []}
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(findstat.map_names(), {"Mp00001": "a map"})
        self.assertEqual(json.loads((findstat.CACHE / "maps.json").read_text()), good)

    def test_coverage_comes_from_the_exact_count(self):
        answers = {
            "Statistics": {"included": {"Statistics": {"St000001": {"Name": "full"}, "St000002": {"Name": "partial"},
                                                       "St000003": {"Name": "weak"}}}},
            "Maps": {"included": {"Maps": {"Mp00001": {"Name": "a map"}}}},
            "Collections": {"included": {"Collections": {"Cc0001": {"Name": "Permutation", "NamePlural": "Permutations",
                                                                    "NameWiki": "Permutations"}}}},
        }

        def request(url, data=None):
            if data is not None:
                return {"data": ["St000001", "St000002", "St000003"], "included": {"MatchingStatistics": {
                    "St000001": {"MatchingStatistic": "St000001", "Offset": 0, "Quality": [100, 100], "ValuesKnown": 4},
                    "St000002": {"MatchingStatistic": "St000002", "Offset": 0, "Quality": [100, 100], "ValuesKnown": 3},
                    "St000003": {"MatchingStatistic": "St000003", "Offset": 0, "Quality": [25, 50], "ValuesKnown": 1}}}}
            return next(v for k, v in answers.items() if k in url)

        findstat.request = request
        src = Path(self.tmp.name) / "v.txt"
        src.write_text("[1] => 0\n[1,2] => 0\n[2,1] => 1\n[1,2,3] => 0\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            findstat.identify("Cc0001", str(src))
        text = out.getvalue()
        self.assertIn("St000001  covers 4/4", text)
        self.assertIn("St000002  covers 3/4", text)   # [100, 100] quality, yet one object is missing
        self.assertIn("agrees on 872 of 873", text)
        self.assertIn("Not evidence: 1 statistics", text)
        self.assertIn("St000003  covers 1/4", text)


if __name__ == "__main__":
    unittest.main()
