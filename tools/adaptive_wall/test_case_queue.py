import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from case_queue import (
    Artifact, BruteForceVerifier, CaseQueue, SplitEvidence, TransportCandidate,
    RupVerifier, VerificationError, encode_dimacs, identity_matcher, object_hash, sha256,
)

CHECKER = {"name": "tiny-exhaustive-test-verifier", "version": 1}


class QueueTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parent / ".scratch"
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        root = Path(self.temp.name)
        self.q = CaseQueue(root / "queue.sqlite", root / "artifacts",
                           BruteForceVerifier(max_vars=12), identity_matcher,
                           "identity-test-v1")

    def tearDown(self):
        self.q.close()
        self.temp.cleanup()

    def case(self, clauses, nv=3, name="case", **kwargs):
        return self.q.register_case({"name": name}, encode_dimacs(nv, clauses), **kwargs)

    def measured(self, parent, conflicts=100, status="COMPLETED", metric="solver_conflicts"):
        return self.q.record_attempt(parent, "measurement", status,
                                     metrics={metric: conflicts, "wall_seconds": 1.25})

    def evidence(self, attempt, metric="solver_conflicts"):
        return SplitEvidence(metric, 100, 40, (attempt,), "paired local measurements")

    def test_timeout_unknown_and_raw_unsat_stay_open(self):
        case, parent = self.case([(-1,)], name="attempts")
        for status in ("TIMEOUT", "UNKNOWN", "CONFLICT_LIMIT", "RAW_UNSAT"):
            self.q.record_attempt(parent, "solve", status,
                                  budgets={"seconds": 1}, metrics={"solver_conflicts": 7})
            self.assertEqual(self.q.case_status(case), "OPEN")
        tasks = self.q.open_tasks()
        self.assertEqual([(t["task"], t["parent_id"]) for t in tasks], [("SOLVE", parent)])
        work = self.q.work_summary(case)
        self.assertEqual(work["cost_totals_do_not_mix_units"]["solver_conflicts"], 28)
        self.assertEqual(work["independently_replayed_parent_closures"], 0)

    def test_invalid_proof_and_missing_bytes_cannot_close(self):
        case, parent = self.case([(1,)], name="sat")
        with self.assertRaises(VerificationError):
            self.q.close_original(case, b"claimed proof", CHECKER)
        self.assertEqual(self.q.case_status(case), "OPEN")
        with self.assertRaises(FileNotFoundError):
            self.q.store.get(Artifact("0" * 64, 1))

    def test_exact_root_replay_closes_and_prunes(self):
        case, parent = self.case([(1,), (-1,)], name="root-unsat")
        self.q.close_original(case, b"drat", CHECKER)
        self.assertEqual(self.q.case_status(case), "VERIFIED_UNSAT")
        self.assertEqual(self.q.open_tasks(), [])

    def test_rule_ids_are_deterministic_and_completed_scans_cached(self):
        case, parent = self.case([(1,)], name="stable-rule-id")
        class NoisyVerifier(BruteForceVerifier):
            def __init__(self):
                super().__init__(max_vars=4)
                self.serial = 0
            def unsat(self, formula, proof, checker):
                self.serial += 1
                return super().unsat(formula, proof, checker) + f"; timing-noise={self.serial}"
        self.q.verifier = NoisyVerifier()
        source = encode_dimacs(2, [(2,), (-2,)])
        first = self.q.register_rule("REFUTATION", source, b"core", checker=CHECKER)
        second = self.q.register_rule("REFUTATION", source, b"core", checker=CHECKER)
        self.assertEqual(first, second)
        self.assertEqual(self.q.db.execute("SELECT COUNT(*) FROM rules").fetchone()[0], 1)
        calls = []
        def counting_matcher(rule, parent_row, source_bytes, target_bytes):
            calls.append((rule["rule_id"], parent_row["parent_id"]))
            return identity_matcher(rule, parent_row, source_bytes, target_bytes)
        self.q.matcher = counting_matcher
        self.assertEqual(self.q.apply_rules(), 0)
        self.assertEqual(self.q.apply_rules(), 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.q.case_status(case), "OPEN")

    def test_binary_cover_requires_composition_then_root_replay(self):
        case, parent = self.case([(1, 2), (-1, 2), (-2,)], name="cover")
        attempt = self.measured(parent)
        split, yes, no = self.q.split(parent, 1, self.evidence(attempt))
        self.q.close_parent(yes, b"yes", CHECKER)
        self.assertEqual(self.q.case_status(case), "OPEN")
        self.assertNotIn("COMPOSE", [t["task"] for t in self.q.open_tasks()])
        self.q.close_parent(no, b"no", CHECKER)
        tasks = self.q.open_tasks()
        self.assertEqual([(t["task"], t["parent_id"]) for t in tasks], [("COMPOSE", parent)])
        self.assertEqual(self.q.case_status(case), "OPEN")
        self.q.close_original(case, b"merged-drat", CHECKER)
        self.assertEqual(self.q.case_status(case), "VERIFIED_UNSAT")
        self.assertEqual(self.q.open_tasks(), [])
        states = {p["parent_id"]: p["state"] for p in self.q.snapshot(case)["parents"]}
        # Root pruning does not erase either independently checked leaf receipt.
        self.assertEqual(states[yes], "CLOSED_VERIFIED_UNSAT")
        self.assertEqual(states[no], "CLOSED_VERIFIED_UNSAT")

    def test_new_refutation_targets_split_ancestor_and_prunes_descendants(self):
        case, parent = self.case([(1,), (-1,)], name="late-ancestor-rule")
        attempt = self.measured(parent)
        self.q.split(parent, 2, self.evidence(attempt))
        self.assertEqual(len(self.q.open_tasks()), 2)
        # Learn/register only after the split; identity maps match its root units.
        self.q.register_rule("REFUTATION", encode_dimacs(1, [(1,), (-1,)]),
                             b"successful-child-core", checker=CHECKER)
        self.q.apply_rules()
        self.assertEqual(self.q.case_status(case), "VERIFIED_UNSAT")
        self.assertEqual(self.q.open_tasks(), [])

    def test_ancestor_closure_prunes_open_children(self):
        case, parent = self.case([(1,), (-1,)], name="prune")
        attempt = self.measured(parent)
        _, yes, no = self.q.split(parent, 2, self.evidence(attempt))
        self.assertEqual(len(self.q.open_tasks()), 2)
        self.q.close_original(case, b"root-proof", CHECKER)
        self.assertEqual(self.q.open_tasks(), [])
        states = {p["parent_id"]: p["state"] for p in self.q.snapshot(case)["parents"]}
        self.assertEqual(states[yes], "PRUNED_BY_ANCESTOR")
        self.assertEqual(states[no], "PRUNED_BY_ANCESTOR")

    def test_rule_runs_before_requested_split(self):
        case, parent = self.case([(1,), (-1,)], name="rule-first")
        attempt = self.measured(parent)
        self.q.register_rule("REFUTATION", encode_dimacs(1, [(1,), (-1,)]), b"core", checker=CHECKER)
        with self.assertRaisesRegex(ValueError, "closed|pruned|superseded"):
            self.q.split(parent, 2, self.evidence(attempt))
        self.assertEqual(self.q.case_status(case), "VERIFIED_UNSAT")

    def test_rule_inherited_by_signed_split_child_only(self):
        case, parent = self.case([(1,), (-1,)], name="inherit")
        # No branch assumption -2 occurs at the root, so this rule waits.
        self.q.register_rule("REFUTATION", encode_dimacs(2, [(1,), (-1,), (-2,)]),
                             b"learned-child-core", checker=CHECKER)
        attempt = self.measured(parent)
        _, yes, no = self.q.split(parent, 2, self.evidence(attempt))
        tasks = self.q.open_tasks()
        self.assertEqual(self.q.case_status(case), "OPEN")
        self.assertEqual([(t["parent_id"]) for t in tasks], [yes])
        self.assertEqual(self.q.snapshot(case)["parents"][-1]["signed_assumptions"][-1]["literal"], -2)

    def test_signed_cross_map_transport_and_bad_sign_control(self):
        target = encode_dimacs(2, [(2,), (-2,)])
        case, parent = self.case([(2,), (-2,)], nv=2, name="renamed")
        rule = self.q.register_rule("REFUTATION", encode_dimacs(1, [(1,), (-1,)]),
                                    b"source-proof", checker=CHECKER)
        self.q.matcher = lambda r, p, s, t: [
            TransportCandidate({"1": 1}),  # absent signed source units: reject
            TransportCandidate({"1": 2}),  # nonidentity but lacks target proof: reject
            TransportCandidate({"1": 2}, b"renamed-target-proof"),
        ]
        self.q.apply_rules()
        self.assertEqual(self.q.case_status(case), "VERIFIED_UNSAT")
        statuses = list(self.q.db.execute("SELECT status FROM rule_matches ORDER BY created_ns"))
        self.assertEqual([s[0] for s in statuses], ["REJECTED", "REJECTED", "APPLIED"])

    def test_wrong_sign_cannot_match_signed_parent(self):
        case, parent = self.case([(1,), (2,)], nv=2, name="wrong-sign")
        self.q.register_rule("REFUTATION", encode_dimacs(1, [(1,), (-1,)]), b"p", checker=CHECKER)
        self.q.matcher = lambda r, p, s, t: [TransportCandidate({"1": 1}, b"bad")]
        self.q.apply_rules()
        self.assertEqual(self.q.case_status(case), "OPEN")
        row = self.q.db.execute("SELECT status,receipt_json FROM rule_matches").fetchone()
        self.assertEqual(row["status"], "REJECTED")
        self.assertIn("absent", json.loads(row["receipt_json"])["error"])

    def test_forward_reverse_H_and_unnamespaced_H_do_not_mix(self):
        forward = {"forward_H": {"dimension": "forward", "relation": ">=", "value": 11,
                                 "source": "forward-receipt"}}
        reverse = {"reverse_H": {"dimension": "reverse", "relation": ">=", "value": 11,
                                 "source": "reverse-receipt"}}
        case, parent = self.case([(1,), (-1,)], name="H-control", context=forward)
        self.q.register_rule("REFUTATION", encode_dimacs(1, [(1,), (-1,)]), b"p",
                             required_context=reverse, checker=CHECKER)
        self.q.apply_rules()
        self.assertEqual(self.q.case_status(case), "OPEN")
        with self.assertRaisesRegex(ValueError, "unnamespaced"):
            self.case([(1,)], name="bare-H", context={"H": 13})

    def test_H_root_ticket_and_contact_statistic_dimensions_checked(self):
        with self.assertRaisesRegex(ValueError, "mixed|dimension"):
            self.case([(1,)], name="mixed-H", context={
                "root_ticket_H": {"dimension": "reverse", "relation": ">=", "value": 4,
                                  "source": "ticket"}})

    def test_entailed_cut_materializes_once_then_is_redundant(self):
        case, parent = self.case([(1,)], nv=2, name="cut")
        self.q.register_rule("ENTAILED_CUT", encode_dimacs(2, [(1,)]),
                             b"rup-prefix", additions=[(1, 2)], checker=CHECKER)
        self.assertEqual(self.q.apply_rules(), 2)  # materialize, then no-op on derived parent
        leaves = self.q._live_leaf_ids()
        self.assertEqual(len(leaves), 1)
        self.assertNotEqual(leaves[0], parent)
        links = self.q.db.execute("SELECT kind,certificate_json FROM links").fetchall()
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["kind"], "ENTAILED_CUT")
        self.assertEqual(self.q.case_status(case), "OPEN")
        self.assertEqual(self.q.apply_rules(), 0)
        # A conclusion-only variable still must have a legal target map.
        self.q.register_rule("ENTAILED_CUT", encode_dimacs(3, [(1,)]),
                             b"rup-prefix", additions=[(1, 3)], checker=CHECKER)
        self.q.apply_rules()
        self.assertEqual(len(self.q._live_leaf_ids()), 1)
        self.assertEqual(self.q.db.execute(
            "SELECT COUNT(*) FROM links WHERE kind='ENTAILED_CUT'").fetchone()[0], 1)

    def test_independent_rup_entailment_and_negative_control(self):
        verifier = RupVerifier()
        formula = encode_dimacs(2, [(1,)])
        self.assertIn("VERIFIED", verifier.entailment(formula, [(1, 2)], b"1 2 0\n", CHECKER))
        with self.assertRaisesRegex(VerificationError, "not RUP"):
            verifier.entailment(formula, [(2,)], b"2 0\n", CHECKER)
        with self.assertRaises(ValueError):
            verifier.entailment(formula, [(1, 2)], b"2 0\n", CHECKER)

    def test_independent_rup_whole_refutation_and_drat_trim(self):
        formula = encode_dimacs(2, [(1, 2), (-1, 2), (-2,)])
        rup = RupVerifier()
        self.assertIn("VERIFIED", rup.unsat(formula, b"0\n", CHECKER))
        with self.assertRaises(VerificationError):
            rup.unsat(encode_dimacs(1, [(1,)]), b"0\n", CHECKER)
        with self.assertRaisesRegex(VerificationError, "missing or duplicate"):
            rup.model(encode_dimacs(1, [(-1,)]), b"[1,-1]", CHECKER)
        checker_path = Path("../../tools/selfcontained/wallcc/bin/drat-trim")
        if checker_path.exists():
            from case_queue import DratTrimVerifier
            drat = DratTrimVerifier(checker_path, timeout_seconds=10)
            checker = {"name": "drat-trim", "sha256": sha256(checker_path.read_bytes())}
            self.assertIn("s VERIFIED", drat.unsat(formula, b"0\n", checker))
            with self.assertRaises(VerificationError):
                drat.unsat(encode_dimacs(1, [(1,)]), b"0\n", checker)
            # Proof: add unit 2 by RUP, then the empty clause.  The valid
            # certificate passes; changing its first binary tag must fail.
            hard = encode_dimacs(2, [(1, 2), (-1, 2), (1, -2), (-1, -2)])
            valid = b"a\x04\x00a\x00"
            self.assertIn("s VERIFIED", drat.unsat(hard, valid, checker))
            with self.assertRaisesRegex(VerificationError, "exact DRAT replay failed"):
                drat.unsat(hard, b"X" + valid[1:], checker)

    def test_nonentailed_cut_rejected_at_registration(self):
        with self.assertRaises(VerificationError):
            self.q.register_rule("ENTAILED_CUT", encode_dimacs(2, [(1,)]), b"bad",
                                 additions=[(2,)], checker=CHECKER)

    def test_closed_strengthening_does_not_silently_close_original(self):
        case, parent = self.case([(1,), (-1,)], nv=2, name="strengthening")
        self.q.register_rule("ENTAILED_CUT", encode_dimacs(2, [(1,)]),
                             b"prefix", additions=[(1, 2)], checker=CHECKER)
        self.q.apply_rules()
        derived = self.q._live_leaf_ids()[0]
        self.q.close_parent(derived, b"residual-proof", CHECKER)
        self.assertEqual(self.q.case_status(case), "OPEN")
        self.assertEqual([t["task"] for t in self.q.open_tasks()], ["COMPOSE"])
        self.q.close_original(case, b"prefix-plus-residual", CHECKER)
        self.assertEqual(self.q.case_status(case), "VERIFIED_UNSAT")

    def test_relaxation_receipt_does_not_close_another_case(self):
        original_case, original = self.case([(1,)], name="original-sat")
        relaxed_case, relaxed = self.case([(1,), (-1,)], name="reported-relaxation")
        self.q.record_attempt(original, "imported-relaxation", "RAW_UNSAT",
                              receipt={"relaxed_parent_id": relaxed})
        self.q.close_parent(relaxed, b"only-relaxation", CHECKER)
        self.assertEqual(self.q.case_status(relaxed_case), "VERIFIED_UNSAT")
        self.assertEqual(self.q.case_status(original_case), "OPEN")
        with self.assertRaises(VerificationError):
            self.q.close_original(original_case, b"only-relaxation", CHECKER)

    def test_split_policy_rejects_unmeasured_timeout_and_metric_mix(self):
        case, parent = self.case([(1, 2)], name="split-policy")
        timeout = self.measured(parent, status="TIMEOUT")
        with self.assertRaisesRegex(ValueError, "completed measurements"):
            self.q.split(parent, 1, self.evidence(timeout))
        done = self.measured(parent)
        with self.assertRaisesRegex(ValueError, "same-metric"):
            self.q.split(parent, 1, SplitEvidence("solver_conflicts", 0, 0, (done,), "no gain"))
        with self.assertRaisesRegex(ValueError, "same-metric"):
            self.q.split(parent, 1, SplitEvidence("solver_conflicts", float("nan"), 2,
                                                  (done,), "NaN is not a measurement"))
        self.assertIsNotNone(self.q.split(parent, 1, self.evidence(done)))

    def test_signed_assumptions_must_be_exact_units(self):
        assumptions = [{"literal": 1, "kind": "signed-pin", "label": "edge-12-color-0"}]
        case, parent = self.case([(1,)], assumptions=assumptions, name="pins")
        self.assertEqual(self.q.snapshot(case)["parents"][0]["signed_assumptions"], assumptions)
        with self.assertRaisesRegex(ValueError, "exact formula unit"):
            self.case([(1, 2)], assumptions=assumptions, name="invented-pin")

    def test_original_units_are_explicit_by_default(self):
        case, parent = self.case([(1,), (-2,), (1, 2, 3)], name="automatic-units")
        assumptions = self.q.snapshot(case)["parents"][0]["signed_assumptions"]
        self.assertEqual([a["literal"] for a in assumptions], [-2, 1])
        self.assertTrue(all(a["kind"] == "original-signed-unit" for a in assumptions))

    def test_artifacts_are_reread_and_tampering_detected(self):
        case, parent = self.case([(1,), (-1,)], name="tamper")
        row = self.q._parent(parent)
        path = self.q.store.path(row["formula_sha256"])
        path.write_bytes(b"p cnf 1 1\n1 0\n")
        with self.assertRaisesRegex(ValueError, "hash/size"):
            self.q.close_original(case, b"proof", CHECKER)
        self.assertEqual(self.q.case_status(case), "OPEN")

    def test_shared_lease_and_immutable_parent_identity(self):
        case, parent = self.case([(1, 2)], name="lease")
        other = CaseQueue(self.q.database, self.q.store.root, BruteForceVerifier(), identity_matcher)
        try:
            claimed = self.q.claim_next("worker-A")
            self.assertEqual(claimed["parent_id"], parent)
            self.assertIsNone(other.claim_next("worker-B"))
            with self.assertRaisesRegex(ValueError, "not held"):
                self.q.release(parent, "worker-B")
            self.q.release(parent, "worker-A")
            self.assertIsNotNone(other.claim_next("worker-B"))
            with self.assertRaises(sqlite3.IntegrityError):
                self.q.db.execute("UPDATE parents SET formula_sha256='changed' WHERE parent_id=?", (parent,))
        finally:
            other.close()

    def test_k58_identity_recomputes_real_supplied_row(self):
        fixture = Path(os.environ.get("K58_ROW_JSON", "../../.scratch/shared-learning-pilot/K58_shared_learning/cases/0dafe3363dab/row.json"))
        if not fixture.exists():
            self.skipTest("checked installation absent")
        row = json.loads(fixture.read_text())
        core = {key: row[key] for key in ("family", "placement", "charge")}
        self.assertEqual(object_hash(core), row["id"])
        identity, source = self.q.k58_identity(row, "first")
        self.assertEqual(source, row["id"])
        with self.assertRaisesRegex(ValueError, "does not hash"):
            self.q.k58_identity(dict(row, id="0" * 64), "first")
        formula = encode_dimacs(1, [(1,)])
        with self.assertRaisesRegex(ValueError, "did not bind"):
            self.q.register_k58_case(
                row, "retry", formula,
                lambda r, tier, data: {"validator": "bad-control", "formula_sha256": "0" * 64})
        case, parent = self.q.register_k58_case(
            row, "retry", formula,
            lambda r, tier, data: {"validator": "fixture-byte-binding-v1",
                                   "formula_sha256": sha256(data), "scope": "test-only"})
        binding = self.q.snapshot(case)["identity"]["original_formula_validation"]
        self.assertEqual(binding["formula_sha256"], sha256(formula))
        self.assertEqual(binding["validator"], "fixture-byte-binding-v1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
