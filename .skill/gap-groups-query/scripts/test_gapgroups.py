"""Tests for gapgroups.py. Run: python -m unittest discover -s skills/gap-groups-query/scripts -p 'test_*.py'

The Offline tests need no GAP. The WithGap tests run only where python can import Sage or
passagemath with the GAP group libraries, and are skipped otherwise (as in CI)."""

import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("gapgroups", Path(__file__).resolve().with_name("gapgroups.py"))
gapgroups = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gapgroups)
Fail = gapgroups.Fail
HAVE_SAGE = importlib.util.find_spec("sage") is not None


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = gapgroups.main(list(argv))
    return code, out.getvalue()


class Offline(unittest.TestCase):
    def test_generators(self):
        self.assertEqual(gapgroups.parse_generators(["(1,2,3,4,5,6,7,8)", "(1,3)"]),
                         "Group([(1,2,3,4,5,6,7,8), (1,3)])")
        self.assertEqual(gapgroups.parse_generators(["[(1,2,3), (1,2)]"]), "Group([(1,2,3), (1,2)])")
        self.assertEqual(gapgroups.parse_generators(["(1,2)(3,4)", "()"]), "Group([(1,2)(3,4), ()])")
        self.assertEqual(gapgroups.parse_generators(["(١, ٢)"]), "Group([(1,2)])")
        for bad in (["(1,2)(2,3)"], ["(1,1)"], ["(0,1)"], ["1,2"], ["(1,2);Exec(\"x\")"], ["(a,b)"], [""],
                    ["(1 2,3)"], ["(1", "2)"], ["[(1,2)", "(3,4)]"],
                    ["(1,%d)" % (gapgroups.MAX_POINT + 1)]):
            with self.assertRaises(Fail, msg=bad):
                gapgroups.parse_generators(bad)

    def test_named_groups(self):
        self.assertEqual(gapgroups.parse_named(" PSL( 2 , 7 ) "), "PSL(2, 7)")
        self.assertEqual(gapgroups.parse_named("SymmetricGroup(5)"), "SymmetricGroup(5)")
        for bad in ("PSL(2)", "Exec(1)", "SymmetricGroup(5);Exec(1)", "SymmetricGroup(n)", "SL(2,5) x C2", ""):
            with self.assertRaises(Fail, msg=bad):
                gapgroups.parse_named(bad)

    def test_filters(self):
        f = gapgroups.parse_filters(["abelian=no", "centre=4", "soluble", "derived_length=2"], perm=False)
        self.assertEqual([p for _, p in f], ["not IsAbelian(G)", "Size(Centre(G)) = 4", "IsSolvableGroup(G)",
                                             "IsSolvableGroup(G) and DerivedLength(G) = 2"])
        self.assertEqual(gapgroups.predicate(f[:2]), "G -> (not IsAbelian(G)) and (Size(Centre(G)) = 4)")
        self.assertEqual(gapgroups.parse_filters(["primitive", "order=168"], perm=True)[0][1],
                         "IsPrimitive(G, MovedPoints(G))")
        self.assertEqual(gapgroups.parse_filters(["center=٢"], perm=False)[0][1], "Size(Centre(G)) = 2")
        for bad, perm in ((["order=24"], False), (["primitive"], False), (["center=x"], False),
                          (["abelian=maybe"], False), (["huge"], True), (["center=4);Exec(1"], False)):
            with self.assertRaises(Fail, msg=bad):
                gapgroups.parse_filters(bad, perm)

    def test_numbers_ranges_links(self):
        self.assertEqual(gapgroups.positive("24", "ORDER"), 24)
        for bad in ("0", "-3", "2.5", "x", ""):
            with self.assertRaises(Fail):
                gapgroups.positive(bad, "ORDER")
        self.assertEqual(gapgroups.ranges([2, 3, 4, 6, 8, 9]), "2-4, 6, 8-9")
        self.assertIn("Groups/Abstract/24.12", gapgroups.lmfdb_group(24, 12))
        self.assertIsNone(gapgroups.lmfdb_group(1152, 3))      # LMFDB labels can differ there
        self.assertIsNone(gapgroups.lmfdb_group(2048, 1))

    def test_usage(self):
        self.assertEqual(run()[0], 2)
        self.assertEqual(run("--help")[0], 0)
        self.assertEqual(run("bogus")[0], 2)

    def test_missing_gap(self):
        saved, saved_gap = dict(sys.modules), gapgroups._gap
        try:
            gapgroups._gap = None
            for name in [m for m in sys.modules if m == "sage" or m.startswith("sage.")]:
                del sys.modules[name]
            sys.modules["sage"] = None          # makes every import of sage fail
            with self.assertRaises(Fail) as e:
                gapgroups.main(["count", "24"])
            self.assertIn("passagemath-gap", str(e.exception))
        finally:
            sys.modules.clear()
            sys.modules.update(saved)
            gapgroups._gap = saved_gap


@unittest.skipUnless(HAVE_SAGE, "needs Sage or passagemath with GAP")
class WithGap(unittest.TestCase):
    def test_count_and_small(self):
        self.assertIn("order 24: 15 groups", run("count", "24")[1])
        self.assertIn("does not contain the groups", run("count", "1024")[1])
        with self.assertRaises(Fail):
            run("count", "2048")
        out = run("small", "8", "4")[1]
        self.assertIn("StructureDescription Q8", out)
        self.assertIn("centre of order 2;", out)
        self.assertIn("5 conjugacy classes", out)
        self.assertIn("Abstract/8.4", out)
        with self.assertRaises(Fail):
            run("small", "24", "16")

    def test_list(self):
        out = run("list", "60", "simple")[1]
        self.assertIn("1 of the 13 groups of order 60 match simple", out)
        self.assertIn("60.5  A5", out)
        out = run("list", "16", "abelian=no")[1]
        self.assertTrue(out.startswith("9 of the 14 groups"))
        out = run("list", "64")[1]
        self.assertIn("... 217 more; add --all", out)
        self.assertEqual(len(run("list", "64", "--all")[1].splitlines()), 268)
        with self.assertRaises(Fail):
            run("list", "512", "abelian")       # 10494213 groups: refused, not scanned
        with self.assertRaisesRegex(Fail, "408641062 groups, too many"):
            run("list", "1536", "--all")

    def test_identify(self):
        out = run("identify", "(1,2,3,4,5,6,7,8)", "(1,3)")[1]
        self.assertIn("order 1152", out)
        self.assertIn("8T47", out)
        self.assertIn("imprimitive", out)
        self.assertNotIn("Abstract/1152", out)
        out = run("identify", "--group", "PSL(2,7)")[1]
        self.assertIn("SmallGroup id [ 168, 42 ]", out)
        self.assertIn("8T37", out)
        self.assertIn("PrimitiveGroup(8, 4)", out)
        self.assertIn("simple; perfect", out)
        self.assertIn("intransitive on its 6 moved points; orbit lengths [ 2, 2, 2 ]",
                      run("identify", "(1,2)(3,4)", "(5,6)")[1])

    def test_transitive_and_primitive(self):
        out = run("transitive", "8", "48")[1]
        self.assertIn("E(8):L_7=AL(8)", out)
        self.assertIn("order 1344", out)
        self.assertIn("PrimitiveGroup(8, 3)", out)
        self.assertIn("affine", out)
        out = run("transitive", "6", "abelian=no", "solvable")[1]
        self.assertTrue(out.startswith("11 of the 16 transitive groups of degree 6"))
        out = run("primitive", "8")[1]
        self.assertIn("7 primitive groups of degree 8", out)
        self.assertIn("PrimitiveGroup(8, 4)  PSL(2, 7)  order 168", out)
        out = run("primitive", "8", "order=168")[1]
        self.assertTrue(out.startswith("2 of the 7 primitive groups"))
        self.assertIn("type 4c (product action, component of type 2)", run("primitive", "25", "23")[1])
        with self.assertRaises(Fail):
            run("transitive", "1", "1")

    def test_version(self):
        out = run("version")[1]
        self.assertIn("smallgrp", out)
        self.assertIn("Besche", out)
        self.assertIn("primitive groups: degrees up to", out)


if __name__ == "__main__":
    unittest.main()
