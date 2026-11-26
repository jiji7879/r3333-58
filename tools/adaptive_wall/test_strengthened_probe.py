import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

import strengthened_probe as probe
from case_queue import parse_dimacs, sha256

TOTAL = 60000
PARENT = "a" * 64


def receipt(node, cube, status, used, cap, plan=None):
    if plan is None:
        plan = {"parent_sha256": PARENT, "depth": 0 if node == "r" else 1,
                "leaf_count": 1 if node == "r" else 2,
                "splits": {} if node == "r" else {"r": 17}}
    return {
        "node": node, "cube": cube, "status": status,
        "conflicts_used": used, "plan_sha256": probe.plan_hash(plan),
        "budget": {"seconds": 60, "conflicts": cap, "proof": "eager"},
    }


def fixture():
    dp = {"parent_sha256": PARENT, "depth": 0, "leaf_count": 1, "splits": {}}
    sp = {"parent_sha256": PARENT, "depth": 1, "leaf_count": 2, "splits": {"r": 17}}
    direct = {"plan": dp, "receipts": [receipt("r", [], "OPEN", TOTAL, TOTAL, dp)],
              "run": {"wall_seconds": 30.0}, "verify": {"wall_seconds": 0.1, "result": {"status": "OPEN"}}}
    split = {"plan": sp,
             "receipts": [receipt("r0", [-17], "OPEN", TOTAL // 2, TOTAL // 2, sp),
                          receipt("r1", [17], "OPEN", TOTAL // 2, TOTAL // 2, sp)],
             "run": {"wall_seconds": 61.0}, "verify": {"wall_seconds": 0.2, "result": {"status": "OPEN"}}}
    return direct, split


class ProbeAnalysisTests(unittest.TestCase):
    def valid(self):
        return fixture()

    def test_both_open_counts_every_child_and_stays_inconclusive(self):
        result = probe.analyze_runs(*self.valid(), TOTAL)
        self.assertEqual(TOTAL, result["direct"]["conflicts_used"])
        self.assertEqual(TOTAL, result["split"]["conflicts_used"])
        self.assertEqual("BOTH_OPEN_INCONCLUSIVE", result["policy"]["outcome"])
        self.assertIn("NOT_EVALUATED", result["original_row_closure"])

    def test_split_closed_supports_split_under_equal_allocation(self):
        direct, split = self.valid()
        split["receipts"] = [
            receipt("r0", [-17], "CHECKED_UNSAT", 20000, TOTAL // 2, split["plan"]),
            receipt("r1", [17], "CHECKED_UNSAT", 19000, TOTAL // 2, split["plan"]),
        ]
        split["verify"]["result"]["status"] = "VERIFIED_UNSAT"
        result = probe.analyze_runs(direct, split, TOTAL)
        self.assertEqual("ONLY_SPLIT_CLOSED_WITHIN_EQUAL_ALLOCATION",
                         result["policy"]["outcome"])
        self.assertTrue(result["policy"]["may_split_on_this_evidence"])

    def test_different_parent_rejected(self):
        direct, split = self.valid()
        split["plan"]["parent_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "hashes differ"):
            probe.analyze_runs(direct, split, TOTAL)

    def test_receipt_from_other_plan_rejected(self):
        direct, split = self.valid()
        direct["receipts"][0]["plan_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "another plan"):
            probe.analyze_runs(direct, split, TOTAL)

    def test_noncomplementary_children_rejected(self):
        direct, split = self.valid()
        split["receipts"][1]["cube"] = [-17]
        with self.assertRaisesRegex(ValueError, "not complementary"):
            probe.analyze_runs(direct, split, TOTAL)

    def test_premature_open_rejected(self):
        direct, split = self.valid()
        split["receipts"][0]["conflicts_used"] -= 1
        with self.assertRaisesRegex(ValueError, "premature OPEN"):
            probe.analyze_runs(direct, split, TOTAL)

    def test_changed_child_budget_rejected(self):
        direct, split = self.valid()
        split["receipts"][0]["budget"]["conflicts"] += 1
        split["receipts"][0]["conflicts_used"] += 1
        with self.assertRaisesRegex(ValueError, "sum to the direct allocation"):
            probe.analyze_runs(direct, split, TOTAL)

    def test_engine_counter_overshoot_cannot_claim_equal_work(self):
        direct, split = self.valid()
        split["receipts"][0]["conflicts_used"] += 2
        direct["receipts"][0]["status"] = "OPEN"
        result = probe.analyze_runs(direct, split, TOTAL)
        self.assertEqual(60002, result["split"]["conflicts_used"])
        self.assertEqual("INVALID_SPLIT_WORK", result["policy"]["outcome"])
        self.assertFalse(result["policy"]["may_split_on_this_evidence"])

    def test_raw_child_labels_do_not_close_without_verify(self):
        direct, split = self.valid()
        for r in split["receipts"]:
            r["status"] = "CHECKED_UNSAT"
        result = probe.analyze_runs(direct, split, TOTAL)
        self.assertEqual("BOTH_OPEN_INCONCLUSIVE", result["policy"]["outcome"])


class FixtureRuleReplayTest(unittest.TestCase):
    def test_actual_square_parent_prepare_and_negative_control(self):
        square = Path(os.environ.get("K58_SQUARE_FIXTURE", "../../.ultramath/smwy2754s/m4/extracted/K58_square_six"))
        checker = Path("../selfcontained/wallcc/bin/drat-trim")
        if not square.is_dir():
            self.skipTest("checked square fixture extraction absent")
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            out = Path(tmp) / "prepared"
            result = probe.prepare(square.resolve(), checker.resolve(), out)
            self.assertTrue(result["positive_verified"])
            self.assertTrue(result["empty_proof_rejected"])
            self.assertEqual("OPEN", result["original_root_status"])
            original, study, additions = probe.load_fixture(square.resolve())
            nv, original_clauses = parse_dimacs(original)
            _, strengthened_clauses = parse_dimacs((out / "strengthened-parent.cnf").read_bytes())
            self.assertEqual(len(original_clauses) + 384, len(strengthened_clauses))
            self.assertEqual(384, len(additions))
            self.assertEqual(probe.EXPECTED_ORIGINAL, result["original_sha256"])
            self.assertNotEqual(result["original_sha256"], result["strengthened_sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
