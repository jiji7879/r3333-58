#!/usr/bin/env python3
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

import cubelearn as cl

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CHECKER = REPO / "tools/selfcontained/wallcc/bin/drat-trim"
SOLVER = REPO / "tools/selfcontained/wallcc/bin/kissat"
SCRATCH = HERE / ".scratch" / "tests"


class CubeLearnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert CHECKER.is_file() and SOLVER.is_file()
        SCRATCH.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(dir=SCRATCH))
        self.write_cnf("parent.cnf", 3, [(1, 2), (-1, 2)])
        self.write_json("cube.json", [-2, 3])

    def tearDown(self):
        shutil.rmtree(self.work)

    def path(self, name):
        return self.work / name

    def write_json(self, name, value):
        path = self.path(name)
        cl.write_json(path, value)
        return path

    def write_cnf(self, name, nv, clauses):
        path = self.path(name)
        path.write_bytes(cl.dimacs_bytes(nv, clauses))
        return path

    def solved_raw(self, parent="parent.cnf", cube="cube.json", name="raw"):
        parent, cube = self.path(parent), self.path(cube)
        child = self.path(name + ".cnf")
        proof = self.path(name + ".drat")
        child.write_bytes(cl.freeze_bytes(parent, cl.read_cube(cube)))
        verdict, log = cl.solve_kissat(SOLVER, child, proof, 5, 2000)
        self.assertEqual("UNSAT", verdict, log)
        return parent, cube, child, proof

    def extracted(self, name="rule"):
        parent, cube, _, proof = self.solved_raw()
        rule = self.path(name)
        cl.extract_rule(parent, cube, proof, CHECKER, rule, 5)
        return rule

    def test_extract_discards_unused_assumption_and_replays(self):
        rule = self.extracted()
        data = cl.load_rule(rule)
        self.assertEqual([-2], data["cube_core"])
        self.assertEqual([2], data["learned_clause"])
        self.assertEqual("VERIFIED", data["validation"]["core_replay"]["status"])
        self.assertEqual("VERIFIED", data["validation"]["exact_child_replay"]["status"])
        # The unused assumption 3 cannot become a matching obligation.
        self.assertEqual([0], data["core"]["selected_cube_indices"])

    def test_minimization_accepts_reproved_deletion_and_checks_necessity(self):
        # Both branch units contradict a different parent unit. Keeping the full
        # child as the initial core deliberately prevents pre-trimming from doing
        # the minimizer's work for this test.
        parent = self.write_cnf("two-parent.cnf", 3, [(2,), (-3,)])
        cube = self.write_json("two-cube.json", [-2, 3])
        _, _, child, raw = self.solved_raw("two-parent.cnf", "two-cube.json", "two-raw")
        initial = self.path("two-initial")
        # The trace is binary and the full child is a valid (non-minimal) core.
        cl.bind_rule(parent, cube, raw, child, CHECKER, initial, 5)
        self.assertEqual([-2, 3], cl.load_rule(initial)["cube_core"])
        out = self.path("minimized")
        summary = cl.minimize_rule(initial, SOLVER, CHECKER, out, 5, 2000, 8)
        self.assertEqual([3], summary["final_cube_core"])
        self.assertEqual("TESTED_MINIMAL", summary["deletion_minimality"])
        self.assertEqual([], summary["unresolved_literals"])
        verdicts = [(r["removed_candidate"], r["solver_verdict"], r["acceptance"])
                    for r in summary["attempts"]]
        self.assertEqual(-2, verdicts[0][0])
        self.assertEqual("UNSAT", verdicts[0][1])
        self.assertIn("ACCEPTED", verdicts[0][2])
        self.assertEqual(3, verdicts[1][0])
        self.assertEqual("SAT", verdicts[1][1])
        self.assertIn("REJECTED", verdicts[1][2])
        self.assertTrue((out / "attempts/0002/model.json").is_file())

    def test_attempt_cap_means_minimality_unknown_not_minimal(self):
        rule = self.extracted("cap-source")
        out = self.path("cap-out")
        summary = cl.minimize_rule(rule, SOLVER, CHECKER, out, 5, 2000, 0)
        self.assertEqual("UNKNOWN", summary["deletion_minimality"])
        self.assertEqual([-2], summary["unresolved_literals"])
        self.assertEqual([], summary["attempts"])

    def mapped_target(self, rule):
        data = cl.load_rule(rule)
        variables = set(data["proof"]["variables"])
        _, core = cl.read_dimacs(rule / "core.cnf")
        variables.update(abs(x) for c in core for x in c)
        self.assertEqual({1, 2}, variables)
        mapping = self.write_json("map.json", {"variables": {"1": -4, "2": 5}})
        target = self.write_cnf("target.cnf", 6, [(-4, 5), (4, 5), (-5,), (6, -6)])
        return mapping, target

    def test_cross_map_transport_and_missing_signed_obligation(self):
        rule = self.extracted("transport-source")
        mapping, target = self.mapped_target(rule)
        out = self.path("transported")
        result = cl.transport_rule(rule, target, mapping, CHECKER, out, 5)
        self.assertEqual("VERIFIED_UNSAT", result["status"])
        self.assertEqual("CLOSED_UNSAT", result["target_status"])
        self.assertEqual("VERIFIED", result["exact_target_replay"]["status"])
        # Removing the mapped signed unit leaves a SAT relaxation and must not close it.
        relaxation = self.write_cnf("relaxation.cnf", 6, [(-4, 5), (4, 5), (6, -6)])
        negative = cl.transport_rule(rule, relaxation, mapping, CHECKER,
                                     self.path("transport-negative"), 5)
        self.assertEqual("NOT_APPLICABLE", negative["status"])
        self.assertEqual("OPEN", negative["target_status"])
        self.assertGreaterEqual(negative["missing_clause_count"], 1)

    def test_incomplete_map_fails_before_any_closure(self):
        rule = self.extracted("map-source")
        _, target = self.mapped_target(rule)
        partial = self.write_json("partial-map.json", {"variables": {"1": -4}})
        with self.assertRaisesRegex(cl.LearningError, "omits"):
            cl.transport_rule(rule, target, partial, CHECKER, self.path("partial-out"), 5)
        self.assertFalse(self.path("partial-out").exists())

    def test_timeout_and_rejected_target_replay_leave_open(self):
        for forced in ("OPEN", "REJECTED"):
            with self.subTest(forced=forced):
                rule = self.extracted("forced-source-" + forced)
                mapping, target = self.mapped_target(rule)
                real = cl.run_checker
                calls = 0

                def fake(*args, **kwargs):
                    nonlocal calls
                    calls += 1
                    if calls == 2:
                        return cl.CheckResult(forced, 0.001, None, "forced control", ["control"])
                    return real(*args, **kwargs)

                out = self.path("forced-out-" + forced)
                with mock.patch("cubelearn.run_checker", side_effect=fake):
                    result = cl.transport_rule(rule, target, mapping, CHECKER, out, 5)
                self.assertEqual(forced if forced == "OPEN" else "PROOF_REJECTED", result["status"])
                self.assertEqual("OPEN", result["target_status"])

    def test_artifact_hash_tamper_is_rejected(self):
        rule = self.extracted("hash-source")
        with (rule / "trim.drat").open("ab") as f:
            f.write(b"\0")
        with self.assertRaisesRegex(cl.LearningError, "hash mismatch"):
            cl.load_rule(rule)

    def test_rat_is_not_entailment_while_rup_is(self):
        rat_cnf = self.write_cnf("rat.cnf", 2, [(1, 2)])
        rat_proof = self.path("rat.drat")
        rat_proof.write_text("1 0\n")
        generic = cl.derivation_control(rat_cnf, rat_proof, CHECKER, 5, False)
        rup = cl.derivation_control(rat_cnf, rat_proof, CHECKER, 5, True)
        self.assertEqual("VERIFIED", generic.status)
        self.assertEqual("REJECTED", rup.status)
        # x=false,y=true satisfies the source and falsifies the added unit x.
        self.assertTrue(any(lit in {-1, 2} for lit in (1, 2)))
        self.assertNotIn(1, {-1, 2})
        # A derivation prefix with no empty clause is not a refutation certificate.
        self.assertEqual("REJECTED", cl.run_checker(CHECKER, rat_cnf, rat_proof, 5,
                                                    ascii_proof=True).status)

        rup_cnf = self.write_cnf("rup.cnf", 2, [(1, 2), (-1, 2)])
        rup_proof = self.path("rup.drat")
        rup_proof.write_text("2 0\n")
        checked = cl.derivation_control(rup_cnf, rup_proof, CHECKER, 5, True)
        self.assertEqual("VERIFIED", checked.status)
        for x, y in itertools.product((False, True), repeat=2):
            source = (x or y) and ((not x) or y)
            if source:
                self.assertTrue(y)

    def test_binary_tags_and_proof_extension_variables(self):
        # Explicit a/d tags are required for a safe byte-preserving round trip.
        steps = [(97, (1, 99)), (100, (-2,)), (97, ())]
        trace = self.path("tagged.drat")
        cl.put_binary(trace, steps)
        self.assertEqual(steps, cl.binary_steps(trace))
        self.assertEqual(97, trace.read_bytes()[0])
        # Variable 99 is proof-only. The parent target declares one variable;
        # only core literals, not DRAT extension variables, are header-bounded.
        parent = self.write_cnf("extension.cnf", 1, [(1,), (-1,)])
        cube = self.write_json("empty-cube.json", [])
        proof = self.path("extension.drat")
        cl.put_binary(proof, [(97, (99,)), (97, ())])
        rule = self.path("extension-rule")
        cl.bind_rule(parent, cube, proof, parent, CHECKER, rule, 5)
        result = cl.transport_rule(rule, parent, None, CHECKER,
                                   self.path("extension-transport"), 5)
        self.assertEqual("VERIFIED_UNSAT", result["status"])

    def test_checker_timeout_is_open(self):
        cnf = self.write_cnf("timeout.cnf", 1, [(1,)])
        proof = self.path("timeout.drat")
        proof.write_bytes(b"")
        with mock.patch("cubelearn.subprocess.run",
                        side_effect=subprocess.TimeoutExpired(["drat-trim"], 0.001)):
            result = cl.run_checker(CHECKER, cnf, proof, 0.001)
        self.assertEqual("OPEN", result.status)
        self.assertIsNone(result.returncode)


if __name__ == "__main__":
    unittest.main(verbosity=2)
