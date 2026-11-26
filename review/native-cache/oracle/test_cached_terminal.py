#!/usr/bin/env python3
"""Executable synthetic audit of frontier.run_native cached-terminal handling.

Run with the campaign venv Python. The only real executable launched is
drat-trim. Kissat is always replaced by a local fake, and cache-hit probes
raise SearchAttempt if the production code tries to invoke it.
"""
from __future__ import annotations

import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

sys.dont_write_bytecode = True
MEMBER = Path(__file__).resolve().parent
REPO = MEMBER.parents[2]
CAMPAIGN = Path(os.environ.get(
    "K58_CAMPAIGN", REPO / ".scratch/campaign-1000/workspace/K58_wall_campaign"))
CHECKER = CAMPAIGN / "tools/drat-trim"
SCRATCH = MEMBER / ".scratch"
sys.path.insert(0, str(MEMBER))
sys.path.insert(0, str(CAMPAIGN / "vendor"))
sys.path.insert(0, str(CAMPAIGN))
import frontier  # noqa: E402
import cached_terminal_oracle as oracle  # noqa: E402

SAT_PARENT = b"p cnf 3 2\n1 0\n2 3 0\n"
SAT_ONE = b"p cnf 1 1\n1 0\n"
UNSAT_TWO = (b"p cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n")
REAL_RUN = subprocess.run


def binary(clause) -> bytes:
    """Independent binary DRAT addition encoder for tiny checker controls."""
    out = bytearray(b"a")
    for lit in clause:
        value = 2 * abs(lit) + int(lit < 0)
        while value >= 128:
            out.append((value & 127) | 128)
            value >>= 7
        out.append(value)
    out.append(0)
    return bytes(out)


EMPTY_CLAUSE_PROOF = binary([])
UNSAT_TWO_PROOF = binary([2]) + binary([])


def model_bytes(model) -> bytes:
    return (json.dumps(model, sort_keys=True, separators=(",", ":")) + "\n").encode()


def extend_dimacs(base: bytes, extra) -> bytes:
    """Independent fixture builder: parse and re-encode the complete formula."""
    nv, clauses = oracle.read_dimacs(base)
    clauses.extend([list(x) for x in extra])
    header = f"p cnf {nv} {len(clauses)}\n".encode()
    return header + b"".join(
        (" ".join(map(str, c)) + (" " if c else "") + "0\n").encode() for c in clauses)


class SearchAttempt(RuntimeError):
    pass


class Fixture:
    cap = 7
    mode = "guided"
    node = "r"
    rid = "tiny-synthetic-case"

    def __init__(self, root: Path, parent: bytes = SAT_PARENT, *, cube=(), cuts=(),
                 paircuts=(), prefix=b"", mode=None):
        self.root = root
        self.parent = parent
        self.cube = list(cube)
        self.cuts = [list(x) for x in cuts]
        self.paircuts = [list(x) for x in paircuts]
        self.prefix = prefix
        self.mode = mode or self.mode
        self.plain = extend_dimacs(parent, [[x] for x in self.cube]) if self.cube else parent
        self.query = (extend_dimacs(self.plain, self.cuts + self.paircuts)
                      if self.cuts or self.paircuts else self.plain)
        self.expected = dict(id=self.rid, node=self.node, mode=self.mode, cap=self.cap,
                             cube=self.cube, parent_sha256=oracle.sha(parent),
                             plain_sha256=oracle.sha(self.plain),
                             query_sha256=oracle.sha(self.query), cuts=len(self.cuts),
                             pair_cuts=len(self.paircuts))
        self.name = f"{self.node}-{self.mode}-{self.cap}"
        self.receipt_path = root / (self.name + ".json")
        self.work = root / "work"

    def use_fallback(self):
        """Force run_native past a stale primary into its query-suffixed resume."""
        stale = dict(self.expected, id="stale-other-case", status="OPEN")
        self.receipt_path.write_bytes(model_bytes(stale))
        self.receipt_path = self.root / (
            self.name + "-" + oracle.sha(self.query)[:12] + ".json")

    def receipt(self, status="OPEN", **extra):
        rec = dict(self.expected, status=status, **extra)
        self.write_receipt(rec)
        return rec

    def write_receipt(self, rec):
        self.receipt_path.write_bytes(model_bytes(rec))

    def read_receipt(self):
        return json.loads(self.receipt_path.read_bytes())

    def proof(self, proof=UNSAT_TWO_PROOF, *, compressed=None, name="proof.drat.gz",
              update_hash=True):
        data = gzip.compress(proof, mtime=0) if compressed is None else compressed
        (self.root / name).write_bytes(data)
        rec = self.read_receipt()
        rec.update(proof=name, proof_sha256=oracle.sha(proof) if update_hash else "0" * 64)
        self.write_receipt(rec)
        return rec

    def model(self, model=(1, 2, 3), *, data=None, compressed=None,
              name="model.json.gz", update_hash=True):
        raw = model_bytes(list(model)) if data is None else data
        packed = gzip.compress(raw, mtime=0) if compressed is None else compressed
        (self.root / name).write_bytes(packed)
        rec = self.read_receipt()
        rec.update(model=name, model_sha256=oracle.sha(raw) if update_hash else "0" * 64)
        self.write_receipt(rec)
        return rec

    def decision(self):
        return oracle.adjudicate(self.receipt_path, self.expected, parent=self.parent,
                                 plain=self.plain, query=self.query, checker=CHECKER,
                                 work=self.work)

    def native(self):
        """Call real cached run_native with Kissat forbidden, returning an outcome."""
        try:
            with mock.patch.object(frontier.subprocess, "run", side_effect=self._no_search):
                rec = frontier.run_native(self.parent, self.cube, self.cuts, self.prefix,
                                          self.paircuts, self.rid, self.node, self.mode,
                                          self.cap, self.root)
            return {"outcome": "RETURN", "status": rec.get("status"),
                    "terminal": rec.get("status") in frontier.DEAD, "receipt": rec}
        except Exception as exc:
            return {"outcome": type(exc).__name__, "status": "NO_RECEIPT_DECISION",
                    "terminal": False, "detail": str(exc)}

    @staticmethod
    def _no_search(command, *args, **kwargs):
        if Path(command[0]).name == "kissat":
            raise SearchAttempt("Kissat invocation forbidden by cached audit")
        return REAL_RUN(command, *args, **kwargs)

    def fresh(self, solver):
        """Call real fresh run_native, faking only Kissat and using real drat-trim."""
        calls = []

        def route(command, *args, **kwargs):
            if Path(command[0]).name == "kissat":
                calls.append(command)
                return solver(command)
            return REAL_RUN(command, *args, **kwargs)

        with mock.patch.object(frontier.subprocess, "run", side_effect=route):
            rec = frontier.run_native(self.parent, self.cube, self.cuts, self.prefix,
                                      self.paircuts, self.rid, self.node, self.mode,
                                      self.cap, self.root)
        return rec, calls


class ContractTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="contract-", dir=SCRATCH)
        self.root = Path(self.tmp.name)
        self.counter = 0

    def tearDown(self):
        self.tmp.cleanup()

    def fixture(self, *args, **kwargs):
        self.counter += 1
        folder = self.root / str(self.counter)
        folder.mkdir()
        return Fixture(folder, *args, **kwargs)

    def assert_invalid(self, fixture: Fixture, reason=None):
        decision = fixture.decision()
        self.assertFalse(decision["terminal"], decision)
        self.assertFalse(decision["cache_valid"], decision)
        self.assertEqual("INVALID_CACHE", decision["status"], decision)
        if reason is not None:
            self.assertEqual(reason, decision["reason"], decision)
        return decision

    def test_valid_terminal_and_nonterminal_controls(self):
        unsat = self.fixture(UNSAT_TWO)
        unsat.receipt("UNSAT_BASE")
        unsat.proof(UNSAT_TWO_PROOF)
        self.assertEqual({"cache_valid": True, "status": "UNSAT_BASE", "terminal": True,
                          "reason": "plain-proof-verified"}, unsat.decision())

        sat = self.fixture(SAT_PARENT)
        sat.receipt("SAT_BASE")
        sat.model([1, 2, 3])
        self.assertTrue(sat.decision()["terminal"])
        self.assertEqual("SAT_BASE", sat.decision()["status"])

        opened = self.fixture(SAT_PARENT)
        opened.receipt("OPEN")
        self.assertEqual({"cache_valid": True, "status": "OPEN", "terminal": False,
                          "reason": "open-is-not-closure"}, opened.decision())

        pending = self.fixture(SAT_ONE, cuts=[[-1]])
        pending.receipt(oracle.PENDING)
        pending.proof(EMPTY_CLAUSE_PROOF)
        self.assertEqual({"cache_valid": True, "status": oracle.PENDING, "terminal": False,
                          "reason": "augmented-only-remains-pending"}, pending.decision())

        # Even a proof valid on plain never upgrades a pending cached status.
        pending_plain = self.fixture(UNSAT_TWO)
        pending_plain.receipt(oracle.PENDING)
        pending_plain.proof(UNSAT_TWO_PROOF)
        self.assertFalse(pending_plain.decision()["terminal"])
        self.assertTrue(pending_plain.decision()["cache_valid"])

    def test_missing_corrupt_and_wrong_binding_receipts(self):
        missing = self.fixture(UNSAT_TWO)
        self.assert_invalid(missing, "missing-receipt")

        corrupt = self.fixture(UNSAT_TWO)
        corrupt.receipt_path.write_bytes(b'{"status":"UNSAT_BASE"')
        self.assert_invalid(corrupt, "invalid-json")

        duplicate = self.fixture(UNSAT_TWO)
        duplicate.receipt_path.write_text('{"status":"OPEN","status":"UNSAT_BASE"}')
        self.assert_invalid(duplicate, "duplicate-json-key")

        for field, value in (("parent_sha256", "0" * 64),
                             ("plain_sha256", "0" * 64),
                             ("query_sha256", "0" * 64),
                             ("id", "another-parent"),
                             ("cube", [99])):
            with self.subTest(field=field):
                f = self.fixture(UNSAT_TWO)
                rec = f.receipt("OPEN")
                rec[field] = value
                f.write_receipt(rec)
                self.assert_invalid(f, "wrong-parent-query-or-case")

        wrong_caller = self.fixture(UNSAT_TWO)
        wrong_caller.receipt("OPEN", query_sha256="0" * 64)
        expected = dict(wrong_caller.expected, query_sha256="0" * 64)
        decision = oracle.adjudicate(wrong_caller.receipt_path, expected,
                                     parent=wrong_caller.parent, plain=wrong_caller.plain,
                                     query=wrong_caller.query, checker=CHECKER,
                                     work=wrong_caller.work)
        self.assertEqual("expected-formula-binding", decision["reason"])
        self.assertFalse(decision["terminal"])

    def test_unsat_artifact_adversaries(self):
        cases = []

        f = self.fixture(UNSAT_TWO); f.receipt("UNSAT_BASE", proof="absent.gz", proof_sha256="0" * 64)
        cases.append(("missing", f, "missing-or-unsafe-artifact"))
        f = self.fixture(UNSAT_TWO); f.receipt("UNSAT_BASE"); f.proof(compressed=b"not gzip")
        cases.append(("corrupt-gzip", f, "corrupt-or-truncated-gzip"))
        packed = gzip.compress(UNSAT_TWO_PROOF, mtime=0)
        f = self.fixture(UNSAT_TWO); f.receipt("UNSAT_BASE"); f.proof(compressed=packed[:-4])
        cases.append(("truncated-gzip", f, "corrupt-or-truncated-gzip"))
        f = self.fixture(UNSAT_TWO); f.receipt("UNSAT_BASE"); f.proof(update_hash=False)
        cases.append(("wrong-hash", f, "proof-hash-mismatch"))
        f = self.fixture(SAT_ONE); f.receipt("UNSAT_BASE"); f.proof(EMPTY_CLAUSE_PROOF)
        cases.append(("hash-matched-false-empty-clause", f, "proof-replay-failed"))
        f = self.fixture(SAT_PARENT); f.receipt("UNSAT_BASE"); f.proof(UNSAT_TWO_PROOF)
        cases.append(("proof-for-different-formula", f, "proof-replay-failed"))
        f = self.fixture(SAT_ONE, cuts=[[-1]]); f.receipt("UNSAT_BASE"); f.proof(EMPTY_CLAUSE_PROOF)
        cases.append(("augmented-only-mislabeled-base", f, "proof-replay-failed"))
        f = self.fixture(UNSAT_TWO); f.receipt("UNSAT_BASE"); f.proof(binary([2])[:-1])
        cases.append(("truncated-inside-first-binary-clause", f, "proof-replay-failed"))
        f = self.fixture(UNSAT_TWO); f.receipt("UNSAT_BASE"); f.proof(b"X" + UNSAT_TWO_PROOF[1:])
        cases.append(("corrupt-proof-tag-with-updated-hash", f, "proof-replay-failed"))
        f = self.fixture(UNSAT_TWO); f.receipt("UNSAT_BASE"); f.proof(name="../escape.drat.gz")
        cases.append(("path-escape", f, "unsafe-artifact-name"))

        for name, fixture, reason in cases:
            with self.subTest(name=name):
                self.assert_invalid(fixture, reason)

    def test_sat_artifact_adversaries(self):
        cases = []
        f = self.fixture(SAT_PARENT); f.receipt("SAT_BASE", model="absent.gz", model_sha256="0" * 64)
        cases.append(("missing", f, "missing-or-unsafe-artifact"))
        f = self.fixture(SAT_PARENT); f.receipt("SAT_BASE"); f.model(compressed=b"bad gzip")
        cases.append(("corrupt-gzip", f, "corrupt-or-truncated-gzip"))
        packed = gzip.compress(model_bytes([1, 2, 3]), mtime=0)
        f = self.fixture(SAT_PARENT); f.receipt("SAT_BASE"); f.model(compressed=packed[:-3])
        cases.append(("truncated-gzip", f, "corrupt-or-truncated-gzip"))
        f = self.fixture(SAT_PARENT); f.receipt("SAT_BASE"); f.model(update_hash=False)
        cases.append(("wrong-hash", f, "model-hash-mismatch"))
        f = self.fixture(SAT_PARENT); f.receipt("SAT_BASE"); f.model([1, 2])
        cases.append(("incomplete-but-satisfying", f, "incomplete-model"))
        f = self.fixture(SAT_PARENT); f.receipt("SAT_BASE"); f.model([1, -2, -3])
        cases.append(("full-but-wrong-physical-model", f, "model-fails-physical-parent"))
        f = self.fixture(SAT_PARENT, cube=[2]); f.receipt("SAT_BASE"); f.model([1, -2, 3])
        cases.append(("full-parent-model-violates-cube", f, "model-violates-cube"))
        f = self.fixture(SAT_PARENT); f.receipt("SAT_BASE"); f.model(data=b"[1, 2,")
        cases.append(("truncated-model-json", f, "invalid-json"))
        f = self.fixture(SAT_PARENT); f.receipt("SAT_BASE"); f.model(data=b'{"1":true}\n')
        cases.append(("model-not-list", f, "incomplete-model"))
        f = self.fixture(SAT_PARENT); f.receipt("SAT_BASE"); f.model([1, 1, 2])
        cases.append(("duplicate-and-missing-variable", f, "incomplete-or-duplicate-model"))
        f = self.fixture(SAT_PARENT); f.receipt("SAT_BASE"); f.model([1, 2, 0])
        cases.append(("zero-literal", f, "invalid-model-literal"))
        for name, fixture, reason in cases:
            with self.subTest(name=name):
                self.assert_invalid(fixture, reason)

    def test_warning_suppressing_helper_accepts_malformed_prefix(self):
        # drat-trim.c's wrong-binary-prefix 'break' is itself guarded by
        # warning != NOWARNING. With -w it skips X, reads NUL as an empty
        # clause, then processes the otherwise valid proof and says VERIFIED.
        malformed = b"X\0" + UNSAT_TWO_PROOF
        f = self.fixture(UNSAT_TWO)
        f.receipt("UNSAT_BASE"); f.proof(malformed)
        cnf, proof = self.root / "warning.cnf", self.root / "warning.drat"
        cnf.write_bytes(UNSAT_TWO); proof.write_bytes(malformed)
        self.assertIsNone(frontier.check_drat(cnf, proof))  # existing -w helper
        self.assert_invalid(f, "proof-replay-failed")       # strict -i oracle

    def test_pending_adversaries_never_close(self):
        f = self.fixture(SAT_ONE, cuts=[[-1]])
        f.receipt(oracle.PENDING, proof="absent.gz", proof_sha256="0" * 64)
        self.assert_invalid(f)
        f = self.fixture(SAT_PARENT)
        f.receipt(oracle.PENDING); f.proof(EMPTY_CLAUSE_PROOF)
        self.assert_invalid(f, "proof-replay-failed")
        f = self.fixture(SAT_ONE, cuts=[[-1]])
        f.receipt(oracle.PENDING); f.proof(update_hash=False)
        self.assert_invalid(f, "proof-hash-mismatch")

    def test_unknown_timeout_and_raw_solver_states_do_not_close(self):
        for status in ("UNKNOWN", "TIMEOUT", "UNSAT", "SAT", "s UNKNOWN", None):
            with self.subTest(status=status):
                f = self.fixture(SAT_PARENT)
                f.receipt(status)
                decision = self.assert_invalid(f, "nonterminal-or-unrecognized-status")
                self.assertNotIn(decision["status"], frontier.DEAD)

    def test_existing_model_checker_accepts_incomplete_assignment(self):
        # This is a separate root cause, visible even on fresh SAT receipts.
        nv, clauses = frontier.read_dimacs(SAT_PARENT)
        self.assertEqual(3, nv)
        self.assertIsNone(frontier.check_model(clauses, [], [1, 2], nv))


class FreshCompatibilityTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="fresh-", dir=SCRATCH)
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def fixture(self, *args, **kwargs):
        folder = self.root / str(len(list(self.root.iterdir())) + 1)
        folder.mkdir()
        return Fixture(folder, *args, **kwargs)

    def test_fresh_valid_sat_receipt_still_verifies(self):
        f = self.fixture(SAT_PARENT)
        rec, calls = f.fresh(lambda command: SimpleNamespace(
            returncode=10, stdout=b"s SATISFIABLE\nv 1 2 3 0\n"))
        self.assertEqual("SAT_BASE", rec["status"])
        self.assertEqual(1, len(calls))
        self.assertTrue(f.decision()["terminal"])

    def test_fresh_valid_unsat_receipt_still_verifies(self):
        f = self.fixture(UNSAT_TWO)
        def solve(command):
            Path(command[-1]).write_bytes(UNSAT_TWO_PROOF)
            return SimpleNamespace(returncode=20, stdout=b"s UNSATISFIABLE\n")
        rec, calls = f.fresh(solve)
        self.assertEqual("UNSAT_BASE", rec["status"])
        self.assertEqual(1, len(calls))
        self.assertTrue(f.decision()["terminal"])

    def test_fresh_open_receipt_remains_open(self):
        f = self.fixture(SAT_PARENT)
        rec, calls = f.fresh(lambda command: SimpleNamespace(
            returncode=0, stdout=b"c conflicts: 7\ns UNKNOWN\n"))
        self.assertEqual("OPEN", rec["status"])
        self.assertFalse(f.decision()["terminal"])
        self.assertEqual(1, len(calls))

    def test_fresh_augmented_pending_receipt_never_becomes_base(self):
        f = self.fixture(SAT_ONE, cuts=[[-1]])
        def solve(command):
            formula = Path(command[-2]).read_bytes()
            if formula == f.query:
                Path(command[-1]).write_bytes(EMPTY_CLAUSE_PROOF)
                return SimpleNamespace(returncode=20, stdout=b"s UNSATISFIABLE\n")
            self.assertEqual(f.plain, formula)
            return SimpleNamespace(returncode=0, stdout=b"c conflicts: 28\ns UNKNOWN\n")
        rec, calls = f.fresh(solve)
        self.assertEqual(oracle.PENDING, rec["status"])
        self.assertEqual(2, len(calls))
        decision = f.decision()
        self.assertTrue(decision["cache_valid"], decision)
        self.assertFalse(decision["terminal"])


class CurrentVulnerabilityTests(unittest.TestCase):
    """Baseline probes: these assert the bug in unmodified HEAD/runtime."""
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="current-", dir=SCRATCH)
        self.root = Path(self.tmp.name)
        self.counter = 0

    def tearDown(self):
        self.tmp.cleanup()

    def fixture(self, *args, **kwargs):
        self.counter += 1
        folder = self.root / str(self.counter); folder.mkdir()
        return Fixture(folder, *args, **kwargs)

    def test_cached_unsat_accepts_hash_matched_false_proof(self):
        f = self.fixture(SAT_ONE)
        f.receipt("UNSAT_BASE"); f.proof(EMPTY_CLAUSE_PROOF)
        result = f.native()
        self.assertEqual("RETURN", result["outcome"])
        self.assertEqual("UNSAT_BASE", result["status"])
        self.assertTrue(result["terminal"])
        self.assertFalse(f.decision()["terminal"])

    def test_cached_sat_accepts_missing_model(self):
        f = self.fixture(SAT_PARENT)
        f.receipt("SAT_BASE", model="absent.gz", model_sha256="0" * 64)
        result = f.native()
        self.assertEqual("SAT_BASE", result["status"])
        self.assertTrue(result["terminal"])

    def test_cached_sat_accepts_incomplete_model(self):
        f = self.fixture(SAT_PARENT)
        f.receipt("SAT_BASE"); f.model([1, 2])
        result = f.native()
        self.assertEqual("SAT_BASE", result["status"])
        self.assertTrue(result["terminal"])
        self.assertFalse(f.decision()["terminal"])

    def test_cached_unsat_accepts_missing_proof(self):
        f = self.fixture(UNSAT_TWO)
        f.receipt("UNSAT_BASE", proof="absent.gz", proof_sha256="0" * 64)
        result = f.native()
        self.assertEqual("UNSAT_BASE", result["status"])
        self.assertTrue(result["terminal"])

    def test_corrupt_cached_receipt_has_no_clean_nonterminal_decision(self):
        f = self.fixture(UNSAT_TWO)
        f.receipt_path.write_bytes(b"{")
        result = f.native()
        self.assertEqual("JSONDecodeError", result["outcome"])
        self.assertFalse(result["terminal"])


if __name__ == "__main__":
    if not CHECKER.is_file():
        raise SystemExit(f"missing checker: {CHECKER}")
    unittest.main(verbosity=2)
