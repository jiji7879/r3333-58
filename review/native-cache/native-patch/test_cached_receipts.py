#!/usr/bin/env python3
"""Tiny, no-search regressions for run_native cached terminal replay."""
from __future__ import annotations

import contextlib
import gzip
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest

sys.dont_write_bytecode = True
MEMBER = Path(__file__).resolve().parent
ROOT = MEMBER.parents[2]
CAMPAIGN = Path(os.environ.get(
    "K58_ORIGINAL_CAMPAIGN", ROOT / ".scratch/campaign-1000/workspace/K58_wall_campaign"))
SCRATCH = MEMBER / ".scratch"
sys.path.insert(0, str(CAMPAIGN / "vendor"))
sys.path.insert(0, str(CAMPAIGN))


def load(alias: str, path: Path):
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


ORIGINAL = load("frontier_original_for_cache_test", CAMPAIGN / "frontier.py")
PATCHED = load("frontier_patched_for_cache_test", MEMBER / "frontier.py")
# Binary DRAT: add unit 2, then the empty clause. This is nontrivial on UNSAT.
PROOF = b"a\x04\x00a\x00"
UNSAT = b"p cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n"
SAT = b"p cnf 2 2\n1 2 0\n-1 2 0\n"
UNIT = b"p cnf 1 1\n1 0\n"


@contextlib.contextmanager
def fake_kissat(module, handler, processes=None):
    """Fake only Kissat; delegate drat-trim to the unchanged real subprocess."""
    real_run = subprocess.run

    def run(command, **kwargs):
        if processes is not None:
            processes.append(list(command))
        if command and Path(str(command[0])).name == "kissat":
            return handler(command)
        return real_run(command, **kwargs)

    module.subprocess.run = run
    try:
        yield
    finally:
        module.subprocess.run = real_run


def no_solver(_command):
    raise AssertionError("cached validation attempted a Kissat search")


def fresh_open(_command):
    return types.SimpleNamespace(returncode=0, stdout=b"c conflicts:     7\ns UNKNOWN\n")


class NativeCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.folder = Path(self.tmp.name)
        self.calls = []

    def tearDown(self):
        self.tmp.cleanup()

    def invoke(self, base, folder=None, *, cuts=None, cube=None, module=PATCHED,
               cap=7, mode="stock", node="r", handler=no_solver, processes=None):
        folder = folder or self.folder
        cuts = cuts or []
        cube = cube or []
        with fake_kissat(module, handler, processes):
            return module.run_native(base, cube, cuts, b"", [], "tiny", node, mode,
                                     cap, folder)

    def metadata(self, base, *, cube=None, cuts=None, cap=7, mode="stock", node="r"):
        cube = cube or []
        cuts = cuts or []
        _, plain = PATCHED.append(base, [[v] for v in cube]) if cube else (None, base)
        _, query = PATCHED.append(plain, cuts) if cuts else (None, plain)
        return dict(id="tiny", node=node, mode=mode, cap=cap, cube=cube,
                    parent_sha256=PATCHED.sha(base), plain_sha256=PATCHED.sha(plain),
                    query_sha256=PATCHED.sha(query), cuts=len(cuts), pair_cuts=0)

    def seed(self, base, status, *, proof=None, model=None, artifact=True,
             cube=None, cuts=None, cap=7, mode="stock", node="r", folder=None,
             receipt_name=None):
        folder = folder or self.folder
        record = self.metadata(base, cube=cube, cuts=cuts, cap=cap, mode=mode,
                               node=node)
        record.update(status=status, seconds=0.001, conflicts=cap)
        stem = receipt_name or f"{node}-{mode}-{cap}"
        receipt = folder / f"{stem}.json"
        if proof is not None:
            record.update(proof=f"{stem}.drat.gz", proof_sha256=PATCHED.sha(proof))
            if artifact:
                (folder / record["proof"]).write_bytes(
                    gzip.compress(proof, compresslevel=3, mtime=0))
        if model is not None:
            modeldata = PATCHED.json_bytes(model)
            record.update(model=f"{stem}.model.json.gz", model_sha256=PATCHED.sha(modeldata))
            if artifact:
                (folder / record["model"]).write_bytes(gzip.compress(modeldata, mtime=0))
        receipt.write_bytes(PATCHED.json_bytes(record))
        return receipt, record

    def assert_invalid(self, base, **kwargs):
        result = self.invoke(base, **kwargs)
        self.assertEqual(result["status"], "OPEN")
        self.assertEqual(result["cache_status"], "INVALID_CACHE")
        self.assertNotIn(result["status"], PATCHED.DEAD)
        return result

    def test_original_accepts_missing_terminal_artifacts_and_patch_does_not(self):
        for status, base, evidence in (("UNSAT_BASE", UNSAT, {"proof": PROOF}),
                                       ("SAT_BASE", SAT, {"model": [1, 2]})):
            with self.subTest(status=status):
                nested = self.folder / status
                nested.mkdir()
                self.seed(base, status, artifact=False, folder=nested, **evidence)
                with fake_kissat(ORIGINAL, no_solver):
                    before = ORIGINAL.run_native(base, [], [], b"", [], "tiny", "r",
                                                 "stock", 7, nested)
                self.assertEqual(before["status"], status)
                after = self.assert_invalid(base, folder=nested)
                self.assertIn("FileNotFoundError", after["cache_error"])

    def test_valid_cached_unsat_is_replayed(self):
        self.seed(UNSAT, "UNSAT_BASE", proof=PROOF)
        calls = []
        real_check = PATCHED.check_native_drat

        def checked(cnf, proof):
            calls.append((Path(cnf).read_bytes(), Path(proof).read_bytes()))
            return real_check(cnf, proof)

        processes = []
        PATCHED.check_native_drat = checked
        try:
            result = self.invoke(UNSAT, processes=processes)
        finally:
            PATCHED.check_native_drat = real_check
        self.assertEqual(result["status"], "UNSAT_BASE")
        self.assertEqual(calls, [(UNSAT, PROOF)])
        drat = [command for command in processes
                if Path(str(command[0])).name == "drat-trim"]
        self.assertEqual(len(drat), 1)
        self.assertIn("-i", drat[0])
        self.assertNotIn("-w", drat[0])
        self.assertNotIn("-W", drat[0])

    def test_valid_cached_complete_sat_model(self):
        self.seed(SAT, "SAT_BASE", model=[1, 2])
        result = self.invoke(SAT)
        self.assertEqual(result["status"], "SAT_BASE")

    def test_warning_suppression_malformed_tag_control(self):
        malformed = b"X" + PROOF[1:]
        cnf = self.folder / "tiny.cnf"
        proof = self.folder / "malformed.drat"
        cnf.write_bytes(UNSAT)
        proof.write_bytes(malformed)
        # The old helper accepts precisely because -w also suppresses the parser break.
        ORIGINAL.check_drat(cnf, proof)
        with self.assertRaises(ValueError):
            PATCHED.check_native_drat(cnf, proof)
        self.seed(UNSAT, "UNSAT_BASE", proof=malformed)
        self.assert_invalid(UNSAT)

    def test_cached_open_stays_open_without_solver(self):
        self.seed(SAT, "OPEN")
        result = self.invoke(SAT)
        self.assertEqual(result["status"], "OPEN")
        self.assertNotIn("cache_status", result)

    def test_missing_corrupt_hash_and_replay_invalid_proofs(self):
        cases = []
        nested = self.folder / "missing"
        nested.mkdir()
        self.seed(UNSAT, "UNSAT_BASE", proof=PROOF, artifact=False, folder=nested)
        cases.append(("missing", nested))

        nested = self.folder / "corrupt"
        nested.mkdir()
        receipt, record = self.seed(UNSAT, "UNSAT_BASE", proof=PROOF, folder=nested)
        (nested / record["proof"]).write_bytes(b"not gzip")
        cases.append(("corrupt", nested))

        nested = self.folder / "hash"
        nested.mkdir()
        receipt, record = self.seed(UNSAT, "UNSAT_BASE", proof=PROOF, folder=nested)
        record["proof_sha256"] = "0" * 64
        receipt.write_bytes(PATCHED.json_bytes(record))
        cases.append(("wrong hash", nested))

        for name, bad_proof in (("truncated", b"a"), ("wrong formula", b"a\x00")):
            nested = self.folder / name.replace(" ", "-")
            nested.mkdir()
            # Recompute the digest: these failures require proof replay, not hashes.
            self.seed(UNSAT, "UNSAT_BASE", proof=bad_proof, folder=nested)
            cases.append((name, nested))

        nested = self.folder / "alias"
        nested.mkdir()
        receipt, record = self.seed(UNSAT, "UNSAT_BASE", proof=PROOF, folder=nested)
        record["proof"] = "../alias.drat.gz"
        receipt.write_bytes(PATCHED.json_bytes(record))
        cases.append(("artifact alias", nested))

        for name, nested in cases:
            with self.subTest(case=name):
                self.assert_invalid(UNSAT, folder=nested)

    def test_incomplete_wrong_and_corrupt_models(self):
        cases = []
        for name, model in (("partial satisfying", [2]), ("wrong full", [-1, -2]),
                            ("duplicate variable", [1, 1]), ("extra variable", [1, 2, 3]),
                            ("contradictory", [1, -1])):
            nested = self.folder / name.replace(" ", "-")
            nested.mkdir()
            self.seed(SAT, "SAT_BASE", model=model, folder=nested)
            cases.append((name, nested))

        for name, data in (("corrupt model", b"not gzip"), ("bad model json", None)):
            nested = self.folder / name.replace(" ", "-")
            nested.mkdir()
            receipt, record = self.seed(SAT, "SAT_BASE", model=[1, 2], folder=nested)
            target = nested / record["model"]
            if data is None:
                target.write_bytes(gzip.compress(b"{bad json", mtime=0))
            else:
                target.write_bytes(data)
            cases.append((name, nested))

        nested = self.folder / "missing-model"
        nested.mkdir()
        self.seed(SAT, "SAT_BASE", model=[1, 2], artifact=False, folder=nested)
        cases.append(("missing model", nested))

        nested = self.folder / "model-hash"
        nested.mkdir()
        receipt, record = self.seed(SAT, "SAT_BASE", model=[1, 2], folder=nested)
        record["model_sha256"] = "0" * 64
        receipt.write_bytes(PATCHED.json_bytes(record))
        cases.append(("model hash", nested))

        for name, nested in cases:
            with self.subTest(case=name):
                self.assert_invalid(SAT, folder=nested)

    def test_augmented_proof_never_becomes_base_closure(self):
        cuts = [[-1]]
        augmented_proof = b"a\x00"  # binary addition of the empty clause
        self.seed(UNIT, "AUGMENTED_UNSAT_PENDING_BASE", proof=augmented_proof,
                  cuts=cuts, mode="guided")
        result = self.invoke(UNIT, cuts=cuts, mode="guided")
        self.assertEqual(result["status"], "AUGMENTED_UNSAT_PENDING_BASE")
        self.assertNotIn(result["status"], PATCHED.DEAD)

        nested = self.folder / "mislabeled"
        nested.mkdir()
        self.seed(UNIT, "UNSAT_BASE", proof=augmented_proof, cuts=cuts,
                  mode="guided", folder=nested)
        self.assert_invalid(UNIT, folder=nested, cuts=cuts, mode="guided")

    def test_raw_solver_or_unknown_cached_statuses_are_invalid_nonterminal(self):
        for status in ("UNSAT", "SAT", "UNKNOWN", "TIMEOUT", None):
            with self.subTest(status=status):
                nested = self.folder / str(status)
                nested.mkdir()
                receipt, _ = self.seed(UNSAT, "OPEN", folder=nested)
                record = json.loads(receipt.read_bytes())
                record["status"] = status
                receipt.write_bytes(PATCHED.json_bytes(record))
                self.assert_invalid(UNSAT, folder=nested)

    def test_corrupt_receipt_json_is_nonterminal(self):
        (self.folder / "r-stock-7.json").write_bytes(b"{not json")
        self.assert_invalid(UNSAT)

    def test_wrong_parent_and_query_cannot_return_old_terminal(self):
        for key in ("parent_sha256", "query_sha256", "plain_sha256"):
            with self.subTest(key=key):
                nested = self.folder / key
                nested.mkdir()
                receipt, record = self.seed(UNSAT, "UNSAT_BASE", proof=PROOF,
                                            folder=nested)
                record[key] = "f" * 64
                receipt.write_bytes(PATCHED.json_bytes(record))
                # A true mismatch remains a cache miss. The tiny fresh UNKNOWN control
                # demonstrates that the old terminal itself is not returned or trusted.
                result = self.invoke(UNSAT, folder=nested, handler=fresh_open)
                self.assertEqual(result["status"], "OPEN")
                self.assertNotIn("proof", result)
                self.assertNotEqual(receipt.read_bytes(), PATCHED.json_bytes(result))

    def test_query_suffixed_fallback_still_replays_valid_proof(self):
        receipt, primary = self.seed(UNSAT, "OPEN")
        primary["query_sha256"] = "0" * 64
        receipt.write_bytes(PATCHED.json_bytes(primary))
        query_hash = self.metadata(UNSAT)["query_sha256"]
        nested_name = f"r-stock-7-{query_hash[:12]}"
        alternate = self.folder / f"{nested_name}.json"
        self.seed(UNSAT, "UNSAT_BASE", proof=PROOF, receipt_name=nested_name)
        result = self.invoke(UNSAT)
        self.assertEqual(result["status"], "UNSAT_BASE")
        self.assertTrue(receipt.exists())
        self.assertTrue(alternate.exists())

    def test_fresh_valid_receipts_and_cached_resume(self):
        for name, base, stdout, code, expected in (
                ("unsat", UNSAT, b"c conflicts: 2\ns UNSATISFIABLE\n", 20, "UNSAT_BASE"),
                ("sat", SAT, b"c conflicts: 2\ns SATISFIABLE\nv 1 2 0\n", 10, "SAT_BASE"),
                ("open", SAT, b"c conflicts: 7\ns UNKNOWN\n", 0, "OPEN")):
            with self.subTest(case=name):
                nested = self.folder / name
                nested.mkdir()
                solver_calls = []

                def fresh(command, *, code=code, stdout=stdout):
                    solver_calls.append(list(command))
                    if code == 20:
                        Path(command[-1]).write_bytes(PROOF)
                    return types.SimpleNamespace(returncode=code, stdout=stdout)

                result = self.invoke(base, folder=nested, handler=fresh)
                self.assertEqual(result["status"], expected)
                self.assertEqual(len(solver_calls), 1)
                resumed = self.invoke(base, folder=nested)
                self.assertEqual(resumed["status"], expected)
                self.assertEqual(len(solver_calls), 1)

    def test_fresh_partial_model_is_rejected_before_receipt(self):
        def partial(_command):
            return types.SimpleNamespace(
                returncode=10,
                stdout=b"c conflicts: 1\ns SATISFIABLE\nv 2 0\n")

        with self.assertRaisesRegex(ValueError, "complete"):
            self.invoke(SAT, handler=partial)
        self.assertFalse((self.folder / "r-stock-7.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
