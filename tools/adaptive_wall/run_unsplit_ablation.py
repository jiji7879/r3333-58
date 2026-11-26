#!/usr/bin/env python3
"""Capture launch provenance for the verified four-row unsplit A/B/C run.

Construction and execution use direction A's abc_audit.py. Receipt and
observation validation use direction B's audit_ablation.py. This wrapper only
records native Kissat calls and timing; it does not change their commands,
recipes, roots, cases, or solver options. It then independently audits all 12.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

CAP = 40000


def require_empty_case_directory(folder: Path) -> None:
    if (folder.is_symlink() or not folder.is_dir() or any(folder.iterdir())):
        raise ValueError(f"case directory is not a fresh empty directory: {folder}")


def require_observed_native_call(invocations) -> None:
    if not invocations:
        raise ValueError("no Kissat invocation observed; refusing cached/fresh provenance claim")


def load_module(path: Path, alias: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument("--builder", required=True, type=Path)
    parser.add_argument("--auditor", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    campaign = args.campaign.resolve()
    root = args.root.resolve()
    output = args.output.resolve()
    if output.exists():
        parser.error("choose a new report path")
    builder = load_module(args.builder, "abc_construction_and_execution")
    auditor = load_module(args.auditor, "abc_receipt_and_observation_audit")
    campaign, frontier, problem, hashes, cases = builder.construct(campaign)
    plan = builder.public_plan(hashes, cases)
    builder.prepare(root, plan)
    (root / "execution-started.json").write_text(json.dumps({
        "pid": os.getpid(), "unix_time": time.time(), "calls": 12,
        "workers": 1, "cap": CAP,
    }, indent=2, sort_keys=True) + "\n")
    expected = auditor.build_expected(campaign)
    for rid in expected:
        native = expected[rid]["plain_bytes"]
        variant = expected[rid]["variants"]
        if next(c["base"] for c in cases if c["row"]["id"] == rid) != native:
            raise ValueError(f"independent parent mismatch: {rid}")
        for name in ("A", "B", "C"):
            if expected[rid]["variants"][name]["query_sha256"] != next(
                    c["variants"][name]["receipt"]["query_sha256"]
                    for c in cases if c["row"]["id"] == rid):
                raise ValueError(f"independent query mismatch: {rid}/{name}")

    solver_sha = hashlib.sha256((campaign / "tools/kissat").read_bytes()).hexdigest()
    original = frontier.subprocess.run
    current_case = None
    started_wall = time.monotonic()

    def observed_run(command, **kwargs):
        nonlocal current_case
        if not command or Path(command[0]).name != "kissat":
            return original(command, **kwargs)
        assert current_case is not None
        case = current_case
        start = time.monotonic()
        try:
            answer = original(command, **kwargs)
        finally:
            log = getattr(locals().get("answer", None), "stdout", b"")
            if log is None:
                log = b""
            assert isinstance(log, bytes), type(log)
            number = len(case["invocations"]) + 1
            raw_time = time.monotonic() - start
            cap_match = re.search(rb"--conflicts=(\d+)", b" ".join(str(x).encode() for x in command))
            if not cap_match:
                raise ValueError("native invocation has no explicit conflicts cap")
            entry = {
                "sequence": number,
                "cap": int(cap_match[1]),
                "returncode": answer.returncode,
                "conflicts": None,
                "seconds": round(raw_time, 3),
                "stdout_file": f"kissat-{number}.log",
                "stdout_sha256": hashlib.sha256(log).hexdigest(),
            }
            match = re.search(rb"^c conflicts:\s+(\d+)", log, re.M)
            if match is None:
                raise ValueError("native invocation produced no conflicts count")
            entry["conflicts"] = int(match[1])
            (case["dir"] / entry["stdout_file"]).write_bytes(log)
            case["invocations"].append(entry)
        return answer

    def observe(rid, variant_name, variant, base, cuts, prefix, pairs, folder):
        nonlocal current_case
        mode = variant["mode"]
        require_empty_case_directory(folder)
        current_case = {"dir": folder, "invocations": []}
        call_start = time.monotonic()
        started_ns = time.time_ns()
        try:
            result = frontier.run_native(base, [], cuts, prefix, pairs, rid, "r", mode, CAP, folder)
        finally:
            assert current_case is not None
            require_observed_native_call(current_case["invocations"])
            obs = {
                "schema": "k58-native-observation/v1",
                "row_id": rid,
                "variant": {"stock": "A", "guided": "B", "guided3": "C"}[variant_name],
                "fresh_directory_created": True, "preexisting_receipt": False,
                "worker_count": 1,
                "solver_sha256": solver_sha, "solver_options": ["-s"],
                "started_wall_ns": started_ns,
                "end_to_end_seconds": time.monotonic() - call_start,
                "materialization_seconds": 0.0,
                "run_native_call_seconds": time.monotonic() - call_start,
                "invocations": current_case["invocations"],
                "materialization_note": "recipe and rule construction occurred before this observed native call",
            }
            (folder / "observation.json").write_text(json.dumps(obs, sort_keys=True) + "\n")
            current_case = None
        return result

    frontier.subprocess.run = observed_run
    try:
        for case in cases:
            for variant in case["variants"].values():
                folder = root / case["row"]["id"] / variant["mode"].replace("guided3", "C").replace("guided", "B").replace("stock", "A")
                observe(case["row"]["id"], variant["mode"], variant, case["base"], variant["cuts"],
                        variant["prefix"], variant["pairs"], folder)
    finally:
        frontier.subprocess.run = original
    (root / "execution-completed.json").write_text(json.dumps({
        "unix_time": time.time(), "calls": 12,
    }, indent=2, sort_keys=True) + "\n")
    (root / "coordinator-walls.json").write_text(json.dumps({
        "wall_seconds_all_native_calls_and_order": time.monotonic() - started_wall,
        "worker_count": 1, "cap": CAP, "cases": len(cases),
        "observation_contract": "k58-native-observation/v1", "order": "A,B,C per row; no split",
    }, indent=2, sort_keys=True) + "\n")
    report = auditor.audit(campaign, root, expected, 600.0, True)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: report[k] for k in (
        "verdict", "checked_receipts", "status_counts", "actual_conflicts_total",
        "over_cap_cases", "maximum_conflict_overshoot", "native_receipt_seconds_total",
        "observed_end_to_end_seconds_total", "observed_all_native_conflicts_total",
        "original_parent_scope", "errors")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
