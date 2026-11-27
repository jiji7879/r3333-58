#!/usr/bin/env python3
"""Prove that proof-bearing tools cannot shed their checks under python -O."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ["assemble.py", "cadical_leaf.py", "compare.py", "cube_probe.py",
         "queue_refine.py", "verify_release.py", "review_quickstart.py"]


class OptimizedGuardTests(unittest.TestCase):
    def test_every_proof_bearing_tool_fails_immediately(self):
        for name in TOOLS:
            with self.subTest(tool=name):
                path = ROOT / "tools" / "refinement" / name
                run = subprocess.run([sys.executable, "-O", "-c",
                                      f"import runpy; runpy.run_path({str(path)!r})"],
                                     cwd=ROOT, text=True, capture_output=True, timeout=15)
                self.assertNotEqual(run.returncode, 0,
                                    f"{name} ran with its proof gates optimized away")
                self.assertIn("Refinement verification requires Python assertions",
                              run.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
