import gzip
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from campaign_cache import CACHE_INVALID, NativeCacheValidator, validate_total_model
from case_queue import (BruteForceVerifier, encode_dimacs, parse_dimacs, sha256)


class CampaignCacheTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parent / ".scratch"
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.root = Path(self.temp.name)
        self.checker = Path("../../tools/selfcontained/wallcc/bin/drat-trim").resolve()
        self.checker_calls = []
        self.validator = NativeCacheValidator(
            sha256, parse_dimacs, self.check_model, self.check_drat)
        self.unsat = encode_dimacs(1, [(1,), (-1,)])
        self.sat = encode_dimacs(2, [(1,), (2,)])
        self.proof = b"0\n"
        # Confirm the real positive and negative checker controls before using
        # them in cache tests.  No SAT solver is called anywhere in this file.
        self.check_drat(self.write("positive.cnf", self.unsat),
                        self.write("positive.drat", self.proof))
        with self.assertRaisesRegex(ValueError, "NOT VERIFIED|failed|VERIFIED"):
            self.check_drat(self.write("negative.cnf", self.sat),
                            self.write("negative.drat", self.proof))

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def json_bytes(value):
        return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()

    @staticmethod
    def binary_clause(clause):
        out = bytearray(b"a")
        for literal in clause:
            value = 2 * abs(literal) + int(literal < 0)
            while value >= 128:
                out.append((value & 127) | 128)
                value >>= 7
            out.append(value)
        out.append(0)
        return bytes(out)

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def check_drat(self, cnf, proof):
        self.checker_calls.append((Path(cnf).read_bytes(), Path(proof).read_bytes()))
        job = subprocess.run([str(self.checker), str(cnf), str(proof), "-i"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if job.returncode or b"s VERIFIED" not in job.stdout:
            raise ValueError(job.stdout[-1000:].decode("utf-8", "replace"))

    @staticmethod
    def check_model(clauses, cube, model, nv):
        formula = encode_dimacs(nv, clauses)
        BruteForceVerifier(max_vars=0).model(
            formula, CampaignCacheTests.json_bytes(model), {})
        if not set(cube) <= set(model):
            raise ValueError("model violates cube")

    def expected(self, plain, query=None, cube=()):
        query = plain if query is None else query
        return {"id": "synthetic", "node": "r", "mode": "stock", "cap": 7,
                "cube": list(cube), "parent_sha256": sha256(plain),
                "plain_sha256": sha256(plain), "query_sha256": sha256(query),
                "cuts": 0, "pair_cuts": 0}

    def install(self, receipt, plain, query=None, name="r-stock-7.json"):
        query = plain if query is None else query
        expected = self.expected(plain, query)
        path = self.write(name, self.json_bytes(dict(expected, **receipt)))
        return path, expected

    def load(self, path, expected, plain, query=None, **kwargs):
        return self.validator.load(path, expected, plain,
                                   plain if query is None else query,
                                   expected["cube"], **kwargs)

    def artifact(self, folder, name, data):
        path = Path(folder) / name
        path.write_bytes(gzip.compress(data, mtime=0))
        return path

    def valid_unsat(self):
        folder = self.root
        self.artifact(folder, "proof.drat.gz", self.proof)
        receipt = {"status": "UNSAT_BASE", "seconds": 0.1, "conflicts": 1,
                   "proof": "proof.drat.gz", "proof_sha256": sha256(self.proof)}
        return self.install(receipt, self.unsat)

    def valid_sat(self):
        model = [1, 2]
        data = self.json_bytes(model)
        self.artifact(self.root, "model.json.gz", data)
        receipt = {"status": "SAT_BASE", "seconds": 0.1, "conflicts": 0,
                   "model": "model.json.gz", "model_sha256": sha256(data)}
        return self.install(receipt, self.sat)

    def assertInvalid(self, result, cached_status):
        self.assertEqual(result["status"], CACHE_INVALID)
        self.assertEqual(result["cached_status"], cached_status)
        self.assertNotIn("proof", result)
        self.assertNotIn("model", result)

    def test_valid_unsat_replays_against_plain(self):
        path, expected = self.valid_unsat()
        before = len(self.checker_calls)
        got = self.load(path, expected, self.unsat)
        self.assertEqual(got["status"], "UNSAT_BASE")
        self.assertEqual(self.checker_calls[-1][0], self.unsat)
        self.assertEqual(len(self.checker_calls), before + 1)

    def test_pending_augmented_replays_query_but_stays_pending(self):
        plain = encode_dimacs(1, [(1,)])
        query = self.unsat
        self.artifact(self.root, "pending.drat.gz", self.proof)
        receipt = {"status": "AUGMENTED_UNSAT_PENDING_BASE", "seconds": 0.2,
                   "conflicts": 7, "proof": "pending.drat.gz",
                   "proof_sha256": sha256(self.proof)}
        path, expected = self.install(receipt, plain, query)
        got = self.load(path, expected, plain, query)
        self.assertEqual(got["status"], "AUGMENTED_UNSAT_PENDING_BASE")
        self.assertEqual(self.checker_calls[-1][0], query)
        self.assertNotEqual(self.checker_calls[-1][0], plain)

    def test_valid_total_model_is_reused(self):
        path, expected = self.valid_sat()
        got = self.load(path, expected, self.sat)
        self.assertEqual(got["status"], "SAT_BASE")

    def test_valid_open_at_cap_is_reused_without_proof_checker(self):
        path, expected = self.install(
            {"status": "OPEN", "seconds": 1.0, "conflicts": 7}, self.sat)
        before = len(self.checker_calls)
        got = self.load(path, expected, self.sat)
        self.assertEqual(got["status"], "OPEN")
        self.assertEqual(len(self.checker_calls), before)

    def test_performance_metrics_are_optional_but_validated_when_present(self):
        path, expected = self.valid_unsat()
        receipt = json.loads(path.read_text())
        del receipt["seconds"], receipt["conflicts"]
        path.write_bytes(self.json_bytes(receipt))
        self.assertEqual(self.load(path, expected, self.unsat)["status"], "UNSAT_BASE")

        path, expected = self.valid_sat()
        receipt = json.loads(path.read_text())
        del receipt["seconds"], receipt["conflicts"]
        path.write_bytes(self.json_bytes(receipt))
        self.assertEqual(self.load(path, expected, self.sat)["status"], "SAT_BASE")

        path, expected = self.install({"status": "OPEN"}, self.sat)
        self.assertEqual(self.load(path, expected, self.sat)["status"], "OPEN")
        receipt = json.loads(path.read_text())
        receipt["conflicts"] = 6
        path.write_bytes(self.json_bytes(receipt))
        self.assertInvalid(self.load(path, expected, self.sat), "OPEN")

    def test_under_cap_and_nonfinite_open_are_invalid(self):
        for receipt in ({"status": "OPEN", "seconds": 0.0, "conflicts": 6},
                        {"status": "OPEN", "seconds": float("nan"), "conflicts": 7}):
            path, expected = self.install(receipt, self.sat, name=self.root.name + "/x.json")
            self.assertInvalid(self.load(path, expected, self.sat), "OPEN")
            path.unlink()

    def test_missing_and_corrupt_proofs_are_invalid(self):
        for content in (None, b"not a gzip stream"):
            path, expected = self.valid_unsat()
            proof = self.root / "proof.drat.gz"
            if content is None:
                proof.unlink()
            else:
                proof.write_bytes(content)
            self.assertInvalid(self.load(path, expected, self.unsat), "UNSAT_BASE")

    def test_missing_and_corrupt_models_are_invalid(self):
        for content in (None, b"not a gzip stream"):
            path, expected = self.valid_sat()
            model = self.root / "model.json.gz"
            if content is None:
                model.unlink()
            else:
                model.write_bytes(content)
            self.assertInvalid(self.load(path, expected, self.sat), "SAT_BASE")

    def test_proof_hash_match_does_not_override_semantic_replay(self):
        hard_unsat = encode_dimacs(2, [(1, 2), (-1, 2), (1, -2), (-1, -2)])
        bad = b"0\n"  # A bare empty clause is not RUP for this XOR obstruction.
        self.artifact(self.root, "proof.drat.gz", bad)
        receipt = {"status": "UNSAT_BASE", "seconds": 0.1, "conflicts": 1,
                   "proof": "proof.drat.gz", "proof_sha256": sha256(bad)}
        path, expected = self.install(receipt, hard_unsat)
        self.assertInvalid(self.load(path, expected, hard_unsat), "UNSAT_BASE")

    def test_proof_against_wrong_formula_is_invalid(self):
        self.artifact(self.root, "proof.drat.gz", self.proof)
        receipt = {"status": "UNSAT_BASE", "seconds": 0.1, "conflicts": 1,
                   "proof": "proof.drat.gz", "proof_sha256": sha256(self.proof)}
        path, expected = self.install(receipt, self.sat)
        self.assertInvalid(self.load(path, expected, self.sat), "UNSAT_BASE")

    def test_corrupt_binary_tag_rejected_despite_warning_suppressed_control(self):
        hard_unsat = encode_dimacs(2, [(1, 2), (-1, 2), (1, -2), (-1, -2)])
        valid = self.binary_clause([2]) + self.binary_clause([])
        self.artifact(self.root, "proof.drat.gz", valid)
        receipt = {"status": "UNSAT_BASE", "seconds": 0.1, "conflicts": 1,
                   "proof": "proof.drat.gz", "proof_sha256": sha256(valid)}
        path, expected = self.install(receipt, hard_unsat)
        self.assertEqual(self.load(path, expected, hard_unsat)["status"], "UNSAT_BASE")

        bad = b"X" + valid[1:]
        bad_path = self.write("bad-tag.drat", bad)
        cnf_path = self.write("bad-tag.cnf", hard_unsat)
        # This counterfactual documents why the production callback uses only
        # -i.  The cache result below must reject what -w incorrectly accepts.
        lenient = subprocess.run([str(self.checker), str(cnf_path), str(bad_path), "-i", "-w"],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(lenient.returncode, 0)
        self.assertIn(b"s VERIFIED", lenient.stdout.splitlines())
        self.artifact(self.root, "proof.drat.gz", bad)
        stored = json.loads(path.read_text())
        stored["proof_sha256"] = sha256(bad)
        path.write_bytes(self.json_bytes(stored))
        self.assertInvalid(self.load(path, expected, hard_unsat), "UNSAT_BASE")

    def test_model_hash_mismatch_is_invalid(self):
        path, expected = self.valid_sat()
        receipt = json.loads(path.read_text())
        receipt["model_sha256"] = "0" * 64
        path.write_bytes(self.json_bytes(receipt))
        self.assertInvalid(self.load(path, expected, self.sat), "SAT_BASE")

    def test_incomplete_duplicate_and_wrong_models_are_invalid(self):
        for model in ([1], [1, -1], [-1, 2], [True, 2], [1, 3]):
            data = self.json_bytes(model)
            self.artifact(self.root, "model.json.gz", data)
            receipt = {"status": "SAT_BASE", "seconds": 0.1, "conflicts": 0,
                       "model": "model.json.gz", "model_sha256": sha256(data)}
            path, expected = self.install(receipt, self.sat)
            self.assertInvalid(self.load(path, expected, self.sat), "SAT_BASE")
            path.unlink()

    def test_artifact_basename_is_mandatory(self):
        path, expected = self.valid_unsat()
        receipt = json.loads(path.read_text())
        receipt["proof"] = "../outside.drat.gz"
        path.write_bytes(self.json_bytes(receipt))
        self.assertInvalid(self.load(path, expected, self.unsat), "UNSAT_BASE")

    def test_malformed_json_and_unknown_status_are_invalid(self):
        expected = self.expected(self.sat)
        path = self.write("bad.json", b"{not json")
        self.assertInvalid(self.load(path, expected, self.sat), None)
        path, expected = self.install(
            {"status": "RAW_UNSAT", "seconds": 0.0, "conflicts": 1}, self.unsat)
        self.assertInvalid(self.load(path, expected, self.unsat), "RAW_UNSAT")

    def test_rule_wave_mismatch_and_suffixed_identity(self):
        path, expected = self.valid_unsat()
        changed = dict(expected, query_sha256="0" * 64)
        self.assertIsNone(self.load(path, changed, self.unsat))
        got = self.load(path, expected, self.unsat, mismatch_is_invalid=True)
        self.assertEqual(got["status"], "UNSAT_BASE")
        got = self.load(path, changed, self.unsat, mismatch_is_invalid=True)
        self.assertEqual(got["status"], CACHE_INVALID)

    def test_model_validator_checks_cube_and_total_assignment(self):
        validate_total_model(self.sat, [1, 2], [1, 2], parse_dimacs, self.check_model)
        with self.assertRaisesRegex(ValueError, "exactly|missing|duplicate"):
            validate_total_model(self.sat, [], [1], parse_dimacs, self.check_model)
        with self.assertRaisesRegex(ValueError, "cube"):
            validate_total_model(self.sat, [-1], [1, 2], parse_dimacs, self.check_model)


if __name__ == "__main__":
    unittest.main(verbosity=2)
