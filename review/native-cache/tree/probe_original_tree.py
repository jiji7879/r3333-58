"""Solver-free before-control: original run_row trusts a terminal tree alone."""
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest import mock

HERE = Path(__file__).resolve().parent
CAMPAIGN = Path(os.environ.get(
    "K58_ORIGINAL_CAMPAIGN", HERE.parents[2] / ".scratch/campaign-1000/workspace/K58_wall_campaign"))
sys.dont_write_bytecode = True
sys.path[:0] = [str(CAMPAIGN), str(CAMPAIGN / "vendor")]
import frontier as f
from arm_pairs import sha

RID = "original-tree-control"
BASE = b"p cnf 1 2\n1 0\n-1 0\n"
scratch = HERE / ".scratch/original-control"
scratch.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(dir=scratch) as tmp:
    f.RUNS = Path(tmp) / "runs"
    folder = f.RUNS / RID
    folder.mkdir(parents=True)
    row = {"id": RID}
    f.context = lambda: ({RID: row}, {RID: {"spoke": None, "pentagons": []}}, {}, {})
    f.row_formula = lambda row, tier: BASE
    f.bind_parent = lambda row, raw: None
    tree = {"id": RID, "parent_sha256": sha(BASE), "splits": {},
            "closed": {"r": "UNSAT_BASE"}, "root_verdict": "UNSAT_BASE"}
    (folder / "tree.json").write_text(json.dumps(tree))
    with mock.patch.object(f.subprocess, "run",
                           side_effect=AssertionError("solver must not run")) as solver:
        returned = f.run_row((RID, 0, 7, False, False))
        # The early return precedes any run_native/cache/artifact access.
        assert returned == RID and solver.call_count == 0
    assert not list(folder.glob("*.drat.gz"))
    result = {"schema": "k58-original-tree-cache-control/v1",
              "terminal_tree_accepted_without_receipt": True,
              "root_verdict_after_run_row": f.read_tree(RID).get("root_verdict"),
              "native_receipt_count": len(list(folder.glob("r-*.json"))),
              "proof_artifact_count": len(list(folder.glob("*.drat.gz"))),
              "solver_calls": solver.call_count,
              "note": "Original control demonstrates the bypass; patched tests require OPEN/INVALID_CACHE."}
    output = HERE / "original-tree-control.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
