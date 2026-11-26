import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import types
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ["INTEGRATION_CHECK_ROOT"])
DRIVER_PATH = ROOT / "repo/tools/adaptive_wall/run_unsplit_ablation.py"
RID = "synthetic-row"
BASE = b"p cnf 1 1\n1 0\n"
CAP = 40000
MODES = {"A": "stock", "B": "guided", "C": "guided3"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_driver():
    spec = importlib.util.spec_from_file_location("patched_unsplit_driver", DRIVER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeSubprocess:
    def __init__(self):
        self.calls = 0

    def run(self, command, **kwargs):
        self.calls += 1
        return types.SimpleNamespace(returncode=0,
            stdout=b"c conflicts: 40000\ns UNKNOWN\n")


class FakeFrontier:
    def __init__(self, mode):
        self.subprocess = FakeSubprocess()
        self.mode = mode
        self.native_calls = 0

    def run_native(self, base, cube, cuts, prefix, pairs, rid, node, mode, cap, folder):
        self.native_calls += 1
        name = f"{node}-{mode}-{cap}"
        receipt = {  # Metadata used by the real run_native cache key.
            "id": rid, "node": node, "mode": mode, "cap": cap, "cube": cube,
            "parent_sha256": sha(base), "plain_sha256": sha(base),
            "query_sha256": sha(base), "cuts": len(cuts), "pair_cuts": len(pairs),
            "status": "OPEN", "conflicts": cap, "seconds": 0.0,
        }
        if self.mode == "implicit-cache" or (self.mode == "stale" and folder.joinpath("stale-cache").exists()):
            # Simulate an alternate/faulty implementation returning cached OPEN
            # without a native invocation. The driver must not attest freshness.
            folder.joinpath(name + ".json").write_text(json.dumps(receipt))
            return receipt
        self.subprocess.run([str(folder / "kissat"), "-s", f"--conflicts={cap}",
                             str(folder / "q.cnf"), str(folder / "p.drat")],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        folder.joinpath(name + ".json").write_text(json.dumps(receipt))
        return receipt


class UnsplitFreshBoundaryTests(unittest.TestCase):
    def setUp(self):
        scratch = HERE / ".scratch/test-work"
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.root = Path(self.temp.name)
        self.driver = load_driver()
        self.empty_guard = getattr(self.driver, "require_fresh_case_folder", None)
        if self.empty_guard is None:
            self.empty_guard = self.driver.require_empty_case_directory

    def tearDown(self):
        self.temp.cleanup()

    def test_fresh_folder_helper_rejects_both_receipt_forms_and_is_not_a_solver(self):
        case = self.root / "case"
        case.mkdir()
        self.empty_guard(case)
        for name in ("r-stock-40000.json", "r-stock-40000-0123456789ab.json",
                     "r-stock-40000.drat.gz"):
            path = case / name
            path.write_bytes(b"{}")
            with self.assertRaisesRegex(ValueError, "fresh.empty"):
                self.empty_guard(case)
            path.unlink()
        link = self.root / "link"
        link.symlink_to(case, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "directory"):
            self.empty_guard(link)

    def execute(self, mode):
        campaign = self.root / mode / "campaign"
        campaign.mkdir(parents=True)
        (campaign / "tools").mkdir()
        (campaign / "tools/kissat").write_bytes(b"synthetic executable placeholder; never executed")
        frontier = FakeFrontier(mode)
        variants = {}
        for label, native_mode in MODES.items():
            variants[label] = {"mode": native_mode, "cuts": [], "prefix": b"", "pairs": [],
                               "receipt": {"query_sha256": sha(BASE)}}
        cases = [{"row": {"id": RID}, "base": BASE, "variants": variants}]
        builder = types.SimpleNamespace()
        builder.construct = lambda path: (path, frontier, None, {}, cases)
        builder.public_plan = lambda hashes, cs: {}
        def prepare(root, plan):
            root.mkdir(parents=True)
            for label in MODES:
                (root / RID / label).mkdir(parents=True)
            if mode == "stale":
                # The old driver checked only the canonical name; this alternate
                # cache entered run_native's resume path without being observed.
                (root / RID / "A/stale-cache").write_text("cached")
        builder.prepare = prepare
        expected = {RID: {"plain_bytes": BASE, "variants": {
            label: {"query_sha256": sha(BASE)} for label in MODES}}}
        auditor = types.SimpleNamespace(build_expected=lambda path: expected)
        def audit(path, root, exp, timeout, required):
            return {"verdict": "PASS", "checked_receipts": 3,
                    "status_counts": {"OPEN": 3}, "actual_conflicts_total": 3 * CAP,
                    "over_cap_cases": 0, "maximum_conflict_overshoot": 0,
                    "native_receipt_seconds_total": 0.0,
                    "observed_end_to_end_seconds_total": 0.0,
                    "observed_all_native_conflicts_total": 3 * CAP,
                    "original_parent_scope": "synthetic", "errors": []}
        auditor.audit = audit
        original_loader = self.driver.load_module
        def loader(path, alias):
            if "builder" in str(path): return builder
            if "auditor" in str(path): return auditor
            return original_loader(path, alias)
        run_root = self.root / mode / "run"
        output = self.root / mode / "report.json"
        argv = ["run_unsplit_ablation.py", "--campaign", str(campaign),
                "--builder", "builder.py", "--auditor", "auditor.py",
                "--root", str(run_root), "--output", str(output)]
        with mock.patch.object(self.driver, "load_module", side_effect=loader), \
             mock.patch.object(sys, "argv", argv), \
             mock.patch("builtins.print"):
            self.driver.main()
        return frontier, run_root, output

    def test_ordinary_fresh_open_receipts_still_record_invocations(self):
        frontier, root, output = self.execute("fresh")
        self.assertTrue(output.is_file())
        self.assertEqual(frontier.subprocess.calls, 3)
        for label in MODES:
            obs = json.loads((root / RID / label / "observation.json").read_text())
            self.assertTrue(obs["fresh_directory_created"])
            self.assertFalse(obs["preexisting_receipt"])
            self.assertEqual(len(obs["invocations"]), 1)

    def test_preexisting_alternate_cache_is_rejected_before_native(self):
        with self.assertRaisesRegex(ValueError, "fresh.empty"):
            self.execute("stale")
        # This guard is before FakeFrontier.run_native, so no native/solver call
        # occurred and no measurement report was published.
        self.assertFalse((self.root / "stale/report.json").exists())

    def test_zero_invocation_return_cannot_attest_fresh_execution(self):
        with self.assertRaisesRegex(ValueError, "invocation"):
            self.execute("implicit-cache")


if __name__ == "__main__":
    unittest.main(verbosity=2)
