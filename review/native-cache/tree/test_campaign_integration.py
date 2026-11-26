import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ["INTEGRATION_CHECK_ROOT"])
PATCHED = ROOT / "campaign"
ORIGINAL = Path(os.environ.get(
    "K58_ORIGINAL_CAMPAIGN", HERE.parents[2] / ".scratch/campaign-1000/workspace/K58_wall_campaign"))
sys.dont_write_bytecode = True
sys.path[:0] = [str(PATCHED), str(ORIGINAL), str(ORIGINAL / "vendor")]

import frontier as f
import verify_campaign as v
import coverage
import arm_pairs as ap
from arm_pairs import sha
# The patched copy contains source files only; use the supplied checker in place.
ap.HERE = ORIGINAL

RID = "synthetic-tree"
UNSAT = b"p cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n"
SAT = b"p cnf 2 1\n1 0\n"


def binary_clause(clause):
    out = bytearray(b"a")
    for lit in clause:
        value = 2 * abs(lit) + int(lit < 0)
        while value >= 128:
            out.append((value & 127) | 128)
            value >>= 7
        out.append(value)
    out.append(0)
    return bytes(out)


VALID_PROOF = binary_clause([2]) + binary_clause([])
MALFORMED_PROOF = b"X" + VALID_PROOF[1:]


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


class CampaignTreeIntegrationTests(unittest.TestCase):
    def setUp(self):
        scratch = HERE / ".scratch/test-work"
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.root = Path(self.temp.name)
        self.folder = self.root / "runs" / RID
        self.folder.mkdir(parents=True)
        f.RUNS = self.root / "runs"
        v.RUNS = f.RUNS
        row = {"id": RID}
        binding = {"spoke": None, "pentagons": []}
        context = lambda: ({RID: row}, {RID: binding}, {}, {})
        f.context = context
        v.context = context
        f.row_formula = lambda row, tier: self.base
        v.row_formula = lambda row, tier: self.base
        f.bind_parent = lambda row, raw: None
        v.bind_parent = lambda row, raw: None
        v.family_and_pins = lambda row: (None, set())
        v.compile_cas = lambda row, pins: ([], b"", None)
        v.produce = lambda row: ([], b"")
        v.pair_clauses = lambda binding, third=False: []
        self.base = UNSAT

    def tearDown(self):
        self.temp.cleanup()

    def install_tree(self, status="UNSAT_BASE"):
        tree = {"id": RID, "parent_sha256": sha(self.base), "splits": {},
                "closed": {"r": status}, "root_verdict": status}
        (self.folder / "tree.json").write_bytes(json_bytes(tree))
        return tree

    def receipt(self, status="UNSAT_BASE", cap=7):
        return {"id": RID, "node": "r", "mode": "stock", "cap": cap,
                "cube": [], "parent_sha256": sha(self.base),
                "plain_sha256": sha(self.base), "query_sha256": sha(self.base),
                "cuts": 0, "pair_cuts": 0, "status": status,
                "conflicts": cap, "seconds": 0.0}

    def install_receipt(self, receipt):
        path = self.folder / f"r-stock-{receipt['cap']}.json"
        path.write_bytes(json_bytes(receipt))
        return path

    def install_proof(self, data, cap=7):
        name = f"r-stock-{cap}.drat.gz"
        (self.folder / name).write_bytes(gzip.compress(data, mtime=0))
        return name, sha(data)

    def test_forged_terminal_tree_without_receipt_is_invalid_open(self):
        self.install_tree()
        got = f.checked_tree(RID)
        self.assertNotIn("root_verdict", got)
        self.assertEqual(got["closed"], {})
        self.assertEqual(got["cache_status"], "INVALID_CACHE")
        self.assertIn("matching receipt", got["cache_error"])
        # The original object/file is deliberately not rewritten by an export read.
        self.assertEqual(json.loads((self.folder / "tree.json").read_text())["root_verdict"],
                         "UNSAT_BASE")

    def test_valid_cached_proof_is_replayed_and_closure_is_preserved(self):
        self.install_tree()
        receipt = self.receipt()
        receipt["proof"], receipt["proof_sha256"] = self.install_proof(VALID_PROOF)
        self.install_receipt(receipt)
        got = f.checked_tree(RID)
        self.assertEqual(got.get("root_verdict"), "UNSAT_BASE", got)
        self.assertEqual(got["closed"], {"r": "UNSAT_BASE"})
        self.assertNotIn("cache_status", got)

    def test_hash_matching_malformed_prefix_is_revoked_by_strict_replay(self):
        # This exact five-byte corruption is accepted by this drat-trim build
        # under -w; the patched checker has no warning suppression.
        self.install_tree()
        receipt = self.receipt()
        receipt["proof"], receipt["proof_sha256"] = self.install_proof(MALFORMED_PROOF)
        path = self.install_receipt(receipt)
        proof_path = self.folder / receipt["proof"]
        work = self.root / "checker"
        work.mkdir()
        raw = work / "bad.drat"
        cnf = work / "u.cnf"
        raw.write_bytes(MALFORMED_PROOF)
        cnf.write_bytes(UNSAT)
        checker = ORIGINAL / "tools/drat-trim"
        job = subprocess.run([str(checker), str(cnf), str(raw), "-i", "-w"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(job.returncode, 0)
        self.assertIn(b"s VERIFIED", job.stdout.splitlines())
        got = f.checked_tree(RID)
        self.assertNotIn("root_verdict", got)
        self.assertEqual(got["closed"], {})
        self.assertEqual(got["cache_status"], "INVALID_CACHE")
        self.assertTrue(path.is_file() and proof_path.is_file())  # retain bad evidence

    def test_valid_proof_under_unbound_artifact_name_is_rejected(self):
        self.install_tree()
        receipt = self.receipt()
        expected_name, digest = self.install_proof(VALID_PROOF)
        (self.folder / expected_name).rename(self.folder / "borrowed.drat.gz")
        receipt.update(proof="borrowed.drat.gz", proof_sha256=digest)
        self.install_receipt(receipt)
        got = f.checked_tree(RID)
        self.assertNotIn("root_verdict", got)
        self.assertEqual(got["closed"], {})
        self.assertIn("receipt-local", got["cache_error"])

    def test_partial_model_cannot_reopen_as_cached_sat(self):
        self.base = SAT
        self.install_tree("SAT_BASE")
        receipt = self.receipt("SAT_BASE")
        model = json_bytes([1])  # satisfies every original check_model clause, not total for nv=2
        name = "r-stock-7.model.json.gz"
        (self.folder / name).write_bytes(gzip.compress(model, mtime=0))
        receipt.update(model=name, model_sha256=sha(model))
        self.install_receipt(receipt)
        got = f.checked_tree(RID)
        self.assertNotIn("root_verdict", got)
        self.assertEqual(got["closed"], {})
        self.assertEqual(got["cache_status"], "INVALID_CACHE")
        self.assertIn("complete", got["cache_error"])

    def test_valid_total_sat_model_is_preserved(self):
        self.base = SAT
        self.install_tree("SAT_BASE")
        receipt = self.receipt("SAT_BASE")
        model = json_bytes([1, -2])
        name = "r-stock-7.model.json.gz"
        (self.folder / name).write_bytes(gzip.compress(model, mtime=0))
        receipt.update(model=name, model_sha256=sha(model))
        self.install_receipt(receipt)
        got = f.checked_tree(RID)
        self.assertEqual(got.get("root_verdict"), "SAT_BASE", got)
        self.assertEqual(got["closed"], {"r": "SAT_BASE"})

    def test_corrupt_tree_json_is_explicit_nonterminal(self):
        (self.folder / "tree.json").write_bytes(b"{truncated")
        got = f.checked_tree(RID)
        self.assertNotIn("root_verdict", got)
        self.assertEqual(got["closed"], {})
        self.assertEqual(got["cache_status"], "INVALID_CACHE")

    def test_coverage_never_exports_unvalidated_raw_terminal_status(self):
        valid = {"closed": {"r": "UNSAT_BASE"}}
        self.assertEqual(coverage.exported_native_status(
            {"node": "r", "status": "UNSAT_BASE"}, valid), "UNSAT_BASE")
        self.assertEqual(coverage.exported_native_status(
            {"node": "r", "status": "SAT_BASE"}, valid), "UNVERIFIED_SAT_BASE")
        self.assertEqual(coverage.exported_native_status(
            {"node": "r", "status": "UNSAT_BASE"}, {"closed": {}}),
            "UNVERIFIED_UNSAT_BASE")
        self.assertEqual(coverage.exported_native_status(
            {"node": "r", "status": "AUGMENTED_UNSAT_PENDING_BASE"}, valid),
            "UNVERIFIED_AUGMENTED_UNSAT_PENDING_BASE")
        self.assertEqual(coverage.exported_native_status(
            {"node": "r", "status": "OPEN"}, {"closed": {}}), "OPEN")

    def test_run_row_does_not_skip_a_revoked_closed_node(self):
        self.install_tree()  # no receipt: raw tree alone used to return before run_native
        f.bind_parent = lambda row, raw: None
        f.family_and_pins = lambda row: (None, set())
        f.compile_cas = lambda row, pins: ([], b"", None)
        f.produce = lambda row: ([], b"")
        f.pair_clauses = lambda binding, third=False: []
        f.candidates = lambda binding, tables: []
        calls = []
        def invalid_native(*args):
            calls.append(args[6])
            return {"status": "OPEN", "cache_status": "INVALID_CACHE"}
        with mock.patch.object(f, "run_native", side_effect=invalid_native), \
             mock.patch.object(f.subprocess, "run", side_effect=AssertionError("no solver allowed")):
            f.run_row((RID, 0, 7, False, False))
        self.assertEqual(calls, ["r"])
        saved = json.loads((self.folder / "tree.json").read_text())
        self.assertNotIn("root_verdict", saved)
        self.assertEqual(saved["closed"], {})
        self.assertEqual(saved["cache_status"], "INVALID_CACHE")

    def test_positive_tree_keepsordinary_valid_early_return(self):
        self.install_tree()
        receipt = self.receipt()
        receipt["proof"], receipt["proof_sha256"] = self.install_proof(VALID_PROOF)
        self.install_receipt(receipt)
        # f.subprocess.run must remain available for drat-trim during checked_tree.
        # Any solver would have to go through run_native in this zero-depth fixture.
        with mock.patch.object(f, "run_native", side_effect=AssertionError("unexpected re-solve")):
            f.run_row((RID, 0, 7, False, False))
        saved = json.loads((self.folder / "tree.json").read_text())
        self.assertEqual(saved["root_verdict"], "UNSAT_BASE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
