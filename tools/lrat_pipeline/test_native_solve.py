#!/usr/bin/env python3
"""Fail-closed tests for native_solve.py on an already closed, hash-pinned input.

This is a local integration test, not a benchmark or wall search. Inputs and a
reviewed lrat-trim binary must already exist. Missing prerequisites are an
explicit SKIP, never a pass. Large proof artifacts are temporary, not deliverables.
"""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import io
import json
import os
import resource
import sys
import tempfile
import time

import native_solve as N

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CNF = REPO / ".scratch/k58-0404-word-search/H8-word0.cnf"
CUBE_HASH = "e8cc97847a6cab9c277933d2dd0d6112c79b061bebb5af221d57df5d6d6a2229"
CHECKER = REPO / ".ultramath/smx06hpp8/m5/.scratch/tools/lrat-trim-423194927df747528d5b7364806b5b77b2660c12/lrat-trim"


def job(root, name, expected, conflicts=50000, checksum=CUBE_HASH):
    return SimpleNamespace(cnf=CNF, expect_sha256=checksum, out=root / name,
                           checker=CHECKER, cadical=N.CADICAL, conflicts=conflicts,
                           seconds=20, check_seconds=60, expected_outcome=expected)


def main():
    if not CNF.is_file():
        print(f"SKIP: closed CNF not present at {CNF}")
        return 0
    if not CHECKER.is_file():
        print(f"SKIP: reviewed lrat-trim binary not present at {CHECKER}")
        return 0
    root = Path(tempfile.mkdtemp(prefix="native-solve-test-", dir=REPO / ".scratch"))
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_before = before.ru_utime + before.ru_stime
    started = time.monotonic()
    receipt = N.solve(job(root, "closed", "UNSAT"))
    assert receipt["solver"]["outcome"] == "UNSAT"
    assert receipt["solver"]["stats"]["conflicts"] == 49226
    assert receipt["solver"]["stats"]["restarts"] == 3189
    assert receipt["raw_proof"]["sha256"] == "05f0d7f11d28e0a784cab3a1a737960fdc8bc5414cc246242d743bb668bd7b34"
    assert receipt["artifact"]["sha256"] == "ae25a7a40dfe91ceb1111c2012adf3a7290b86b2bd49b534f3e61a1deaaf41d4"
    assert receipt["artifact"]["bytes"] == 6503105
    assert receipt["validation"]["state"] == "VERIFIED_UNSAT_BY_TWO_UNVERIFIED_LRAT_CHECKERS"
    for key in ("backward_replay", "forward_replay", "independent_rup_replay", "raw_trim_check"):
        assert receipt["validation"][key] is True
    # Explicit OPEN semantics: a partial LRAT stream is not a refutation.
    opened = N.solve(job(root, "capped", "OPEN", conflicts=1))
    assert opened["solver"]["outcome"] == "OPEN" and opened["solver"]["exit"] == 0
    assert opened["solver"]["stats"]["conflicts"] == 1 and opened["artifact"] is None
    assert not (root / "capped/leaf.lrat").exists()
    # A closed case is not relabelled as OPEN by asking for that outcome.
    try:
        N.solve(job(root, "wrong-outcome", "OPEN"))
    except RuntimeError as error:
        assert "unexpected outcome UNSAT" in str(error)
    else:
        raise AssertionError("UNSAT incorrectly relabelled as expected OPEN")
    assert not (root / "wrong-outcome/leaf.lrat").exists()
    # Input-hash failure happens before output creation or solving.
    try:
        N.solve(job(root, "badhash", "UNSAT", checksum="0" * 64))
    except RuntimeError as error:
        assert "input CNF SHA-256" in str(error)
    else:
        raise AssertionError("incorrect input hash accepted")
    assert not (root / "badhash").exists()
    # Existing outputs cannot be overwritten.
    (root / "reuse").mkdir()
    try:
        N.solve(job(root, "reuse", "UNSAT"))
    except RuntimeError as error:
        assert "refusing to reuse output directory" in str(error)
    else:
        raise AssertionError("existing output accepted")
    assert list((root / "reuse").iterdir()) == []
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_after = after.ru_utime + after.ru_stime
    summary = {"checks": "PASS", "input_sha256": CUBE_HASH,
               "solver_conflicts": receipt["solver"]["stats"]["conflicts"],
               "trimmed_sha256": receipt["artifact"]["sha256"],
               "trimmed_bytes": receipt["artifact"]["bytes"],
               "native_processing_cpu_seconds": receipt["native_processing_cpu_seconds"],
               "total_cpu_seconds_including_second_checker": receipt["total_cpu_seconds"],
               "elapsed_wall_seconds_of_all_controls": round(time.monotonic() - started, 6),
               "children_cpu_seconds_of_all_controls": round(cpu_after - cpu_before, 6),
               "scope": "one closed case plus bad hash, wrong expected outcome, capped OPEN and collision controls; no speedup theorem"}
    summary_file = REPO / "results/next-directions-2026-11-28/lrat/adapter-test-receipt.json"
    summary_file.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    # Drop only this command's large temporary CNFs/proofs, after all identity checks.
    import shutil
    shutil.rmtree(root / "closed")
    shutil.rmtree(root / "capped")
    shutil.rmtree(root / "wrong-outcome")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
