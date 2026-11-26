#!/usr/bin/env python3
"""Synthetic negative controls for probe_audit; no SAT solver is invoked."""
import json
from pathlib import Path
import tempfile
import unittest

import probe_audit as audit


class ProbeAuditTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory(dir=Path(__file__).parent / ".scratch")
        self.root = Path(self.tempdir.name)
        self.parent = b"p cnf 100 1\n1 0\n"
        self.parent_hash = audit.digest(self.parent)

    def tearDown(self):
        self.tempdir.cleanup()

    def make_run(self, name, depth, variable=77, direct_used=60005,
                 split_used=(30005, 17), parent=None):
        run = self.root / name
        parent = self.parent if parent is None else parent
        parent_hash = audit.digest(parent)
        splits = {} if depth == 0 else {"r": variable}
        leaves = [("r", [])] if depth == 0 else [("r0", [-variable]), ("r1", [variable])]
        plan = {
            "schema": 1,
            "origin": {"kind": "dimacs", "source_sha256": parent_hash},
            "parent_sha256": parent_hash, "cas": "off", "depth": depth,
            "lookahead": 12, "variables": 100, "clauses": 1,
            "split_limit": 100, "tables": 0, "cuts": 0,
            "cas_proof_sha256": audit.EMPTY_SHA, "working_sha256": parent_hash,
            "splits": splits, "leaf_count": len(leaves),
        }
        (run / "working.cnf").parent.mkdir(parents=True)
        (run / "parent.cnf").write_bytes(parent)
        (run / "working.cnf").write_bytes(parent)
        (run / "cas.drat").write_bytes(b"")
        (run / "plan.json").write_bytes(audit.json_bytes(plan))
        plan_id = audit.digest(audit.json_bytes(plan))
        for index, (node, cube) in enumerate(leaves):
            cap = 60000 if depth == 0 else 30000
            used = direct_used if depth == 0 else split_used[index]
            folder = run / "leaves" / node
            folder.mkdir(parents=True)
            receipt = {
                "plan_sha256": plan_id, "node": node, "cube": cube,
                "budget": {"seconds": 30, "conflicts": cap,
                           "proof": "eager", "check_seconds": 60},
                "solver": audit.SOLVER, "status": "OPEN",
                "reason": "conflict limit", "conflicts_used": used,
                "elapsed_s": 1.25,
            }
            (folder / "receipt.json").write_bytes(audit.json_bytes(receipt))
        return run

    def receipt_path(self, run, node):
        return run / "leaves" / node / "receipt.json"

    def update_receipt(self, run, node, function):
        path = self.receipt_path(run, node)
        receipt = json.loads(path.read_text())
        function(receipt)
        path.write_bytes(audit.json_bytes(receipt))

    def test_valid_pair_sums_actual_and_allows_cap_overshoot(self):
        direct = self.make_run("direct", 0)
        split = self.make_run("split", 1)
        report = audit.compare_runs(direct, split, self.parent_hash, self.parent_hash)
        self.assertEqual(report["matched_total_allocated_conflicts"], 60000)
        self.assertEqual(report["direct"]["allocated_conflicts_total"], 60000)
        self.assertEqual(report["split"]["allocated_conflicts_total"], 60000)
        self.assertEqual(report["actual_conflicts"]["direct"], 60005)
        self.assertEqual(report["actual_conflicts"]["split"], 30022)
        self.assertTrue(report["actual_conflicts"]["complete"])
        self.assertEqual(report["split"]["split_variable"], 77)
        self.assertEqual([leaf["cube"] for leaf in report["split"]["leaves"]],
                         [[-77], [77]])

    def test_auxiliary_numbered_split_variable_is_recorded_not_forbidden(self):
        direct = self.make_run("direct", 0)
        split = self.make_run("split", 1, variable=99)
        report = audit.compare_runs(direct, split, self.parent_hash, self.parent_hash)
        self.assertEqual(report["split"]["split_variable"], 99)

    def test_wall_timeout_makes_actual_unknown_not_cap(self):
        direct = self.make_run("direct", 0)
        split = self.make_run("split", 1)
        def timeout(receipt):
            del receipt["conflicts_used"]
            receipt["reason"] = "wall-time limit"
        self.update_receipt(split, "r1", timeout)
        report = audit.compare_runs(direct, split, self.parent_hash, self.parent_hash)
        self.assertEqual(report["split"]["allocated_conflicts_total"], 60000)
        self.assertIsNone(report["actual_conflicts"]["split"])
        self.assertFalse(report["actual_conflicts"]["complete"])
        self.assertEqual(report["split"]["unknown_actual_conflict_nodes"], ["r1"])

    def test_wrong_child_cap_rejected(self):
        direct = self.make_run("direct", 0)
        split = self.make_run("split", 1)
        self.update_receipt(split, "r0", lambda r: r["budget"].update(conflicts=30001))
        with self.assertRaisesRegex(ValueError, "wrong conflict allocation"):
            audit.compare_runs(direct, split, self.parent_hash, self.parent_hash)

    def test_same_sign_or_wrong_receipt_cube_rejected(self):
        direct = self.make_run("direct", 0)
        split = self.make_run("split", 1)
        self.update_receipt(split, "r1", lambda r: r.update(cube=[-77]))
        with self.assertRaisesRegex(ValueError, "binding/cube mismatch"):
            audit.compare_runs(direct, split, self.parent_hash, self.parent_hash)

    def test_missing_open_child_receipt_rejected(self):
        direct = self.make_run("direct", 0)
        split = self.make_run("split", 1)
        self.receipt_path(split, "r1").unlink()
        with self.assertRaisesRegex(ValueError, "missing receipt"):
            audit.compare_runs(direct, split, self.parent_hash, self.parent_hash)

    def test_non_exact_two_child_tree_rejected(self):
        split = self.make_run("split", 1)
        plan_path = split / "plan.json"
        plan = json.loads(plan_path.read_text())
        plan["splits"]["r0"] = 88
        plan_path.write_bytes(audit.json_bytes(plan))
        with self.assertRaisesRegex(ValueError, "exactly one root split"):
            audit.expected_leaves(plan)

    def test_deferred_second_pass_rejected_for_matched_probe(self):
        direct = self.make_run("direct", 0)
        split = self.make_run("split", 1)
        self.update_receipt(direct, "r", lambda r: r["budget"].update(proof="deferred"))
        with self.assertRaisesRegex(ValueError, "eager"):
            audit.compare_runs(direct, split, self.parent_hash, self.parent_hash)

    def test_deferred_accounting_can_sum_two_passes_when_explicitly_allowed(self):
        direct = self.make_run("direct", 0)
        def deferred(receipt):
            receipt["budget"]["proof"] = "deferred"
            receipt["search_conflicts"] = 100
            receipt["conflicts_used"] = 200
        self.update_receipt(direct, "r", deferred)
        report = audit.inspect_run(direct, self.parent_hash, 0, 60000,
                                   self.parent_hash, require_eager=False)
        self.assertEqual(report["actual_conflicts_total"], 300)
        self.assertEqual(report["allocated_conflicts_total"], 60000)

    def test_changed_parent_rejected(self):
        direct = self.make_run("direct", 0)
        other_parent = b"p cnf 100 1\n-1 0\n"
        split = self.make_run("split", 1, parent=other_parent)
        with self.assertRaisesRegex(ValueError, "changed or unexpected"):
            audit.compare_runs(direct, split, self.parent_hash, self.parent_hash)

    def test_changed_nonconflict_budget_rejected(self):
        direct = self.make_run("direct", 0)
        split = self.make_run("split", 1)
        self.update_receipt(split, "r0", lambda r: r["budget"].update(seconds=31))
        with self.assertRaisesRegex(ValueError, "settings differ"):
            audit.compare_runs(direct, split, self.parent_hash, self.parent_hash)

    def test_changed_lookahead_rejected(self):
        split = self.make_run("split", 1)
        plan_path = split / "plan.json"
        plan = json.loads(plan_path.read_text())
        plan["lookahead"] = 13
        plan_path.write_bytes(audit.json_bytes(plan))
        with self.assertRaisesRegex(ValueError, "lookahead"):
            audit.inspect_run(split, self.parent_hash, 1, 30000, self.parent_hash)


if __name__ == "__main__":
    unittest.main(verbosity=2)
