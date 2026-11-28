#!/usr/bin/env python3
"""Opt-in native-LRAT solving and independent replay for a hash-pinned CNF.

This is deliberately a STANDALONE case adapter, not a cover-tree proof
composition tool. It reduces certificate processing cost on suitable closed
inputs; it does not change search, physical Ramsey semantics, or production
DRAT/finalise. It cannot infer a row/profile closure from one case.

On UNSAT, a trimmed binary LRAT artifact is retained only after lrat-trim
backward/forward replay and conversion to ASCII plus the separate Python
RUP-only checker. Both checker implementations are unverified programs, not a
formally verified certificate kernel. Every output is opt-in and fails closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CADICAL = REPO / "tools/color-resolved-wallcc/bin/cadical-2.1.2"
PYCHECK = HERE / "lrat_rup_check.py"
CADICAL_SHA256 = "a4a6dc61458f4fbb86cd4084e0249b0e93aae239816d58c3fb707a0a0bc7e48b"
CHECKER_SHA256 = "f1eb1a4486274c35f4accf7bc13b595cfdbcf2d7c9aa6b46fb281f19d0d52895"
PYCHECK_SHA256 = "f0eb3f5d419f23b9843fcc5a5aba8f5b512db2a4dbfd8a9b469d7e11df4771b2"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def executable(path, expected, label):
    path = Path(path).resolve()
    require(path.is_file() and os.access(path, os.X_OK), f"missing executable {label}: {path}")
    actual = sha256(path)
    require(actual == expected, f"unexpected {label} SHA-256 {actual}; expected {expected}")
    return str(path), actual


def children_cpu():
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return r.ru_utime + r.ru_stime


def run_stage(name, command, timeout, include_stdout=False):
    import time
    start, cpu = time.monotonic(), children_cpu()
    try:
        completed = subprocess.run(list(map(str, command)), capture_output=True,
                                   text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"{name} exceeded its wall-time limit") from None
    result = {"command": list(map(str, command)),
              "exit": completed.returncode,
              "wall_seconds": round(time.monotonic() - start, 6),
              "child_cpu_seconds": round(children_cpu() - cpu, 6),
              "stdout_tail": completed.stdout[-1600:],
              "stderr_tail": completed.stderr[-1600:]}
    if include_stdout:
        # Markers can precede long profiling/statistics sections; this private
        # stream is for validation only, never for the compact receipt.
        result["_stdout"] = completed.stdout
    return result


def solver_statistics(lines):
    stats = {}
    for line in lines:
        fields = line.split()
        for key in ("conflicts", "decisions", "propagations", "restarts"):
            if line.startswith(f"c {key}:"):
                stats[key] = int(fields[2])
        if line.startswith("c total process time since initialization:"):
            require(fields[-1] == "seconds", "unexpected CaDiCaL time units")
            stats["cpu_seconds"] = float(fields[-2])
        if line.startswith("c maximum resident set size of process:"):
            require(fields[-1] == "MB", "unexpected CaDiCaL memory units")
            stats["rss_mib"] = float(fields[-2])
    require("conflicts" in stats, "CaDiCaL omitted conflict statistics")
    return stats


def verified(stage, needle="s VERIFIED"):
    return (stage["exit"] == 20
            and needle in stage["stdout_tail"].splitlines())


def formula_report_path(out):
    """Atomic non-overwriting installation of a computed artifact in a fresh directory."""
    def install(source, name):
        target = out / name
        require(not target.exists(), f"refusing to overwrite existing output {target}")
        with target.open("xb") as stream:
            with Path(source).open("rb") as origin:
                shutil.copyfileobj(origin, stream, length=8 << 20)
            stream.flush()
            os.fsync(stream.fileno())
        return target
    return install


def solve(args):
    cadical, cadical_hash = executable(args.cadical, CADICAL_SHA256, "CaDiCaL 2.1.2")
    checker, checker_hash = executable(args.checker, CHECKER_SHA256, "lrat-trim")
    require(PYCHECK.is_file(), f"missing Python RUP checker source: {PYCHECK}")
    pycheck_hash = sha256(PYCHECK)
    require(pycheck_hash == PYCHECK_SHA256,
            f"unexpected Python RUP checker source SHA-256 {pycheck_hash}")
    pycheck = str(PYCHECK)
    cnf = args.cnf.resolve()
    require(cnf.is_file(), f"input CNF is missing: {cnf}")
    input_hash = sha256(cnf)
    require(input_hash == args.expect_sha256,
            f"input CNF SHA-256 {input_hash} != expected {args.expect_sha256}")
    out = args.out.resolve()
    require(not out.exists(), f"refusing to reuse output directory {out}; choose a fresh one")
    out.mkdir(parents=True)
    install = formula_report_path(out)
    solver_cmd = [cadical, "--seed=0", "--lrat", "--binary=true",
                  "-c", str(args.conflicts), "-t", str(args.seconds), str(cnf)]
    receipt = {
        "scope": "standalone exact-CNF certificate processing; no wall/profile or Ramsey-bound inference",
        "input": {"path": str(cnf), "expected_sha256": args.expect_sha256,
                  "sha256": input_hash, "bytes": cnf.stat().st_size},
        "cadical": {"path": cadical, "sha256": cadical_hash, "version": "2.1.2", "seed": 0},
        "limits": {"conflicts": args.conflicts, "solver_seconds": args.seconds,
                   "check_seconds": args.check_seconds},
        "expected_outcome": args.expected_outcome,
        "proof_format": "native binary LRAT, trimmed by lrat-trim",
        "trust_boundary": ("lrat-trim and a separate Python RUP checker are two "
                           "independent unverified implementations, not a verified checker"),
    }
    backend_note = {"checker": {"path": checker, "source_commit":
                                      "423194927df747528d5b7364806b5b77b2660c12"},
                    "lrat_trim_sha256": checker_hash,
                    "python_checker_sha256": pycheck_hash}
    receipt["checkers"] = backend_note
    total_cpu = 0.0
    with tempfile.TemporaryDirectory(prefix="work-", dir=out) as name:
        work = Path(name)
        raw = work / "raw.lrat"
        try:
            result = run_stage("CaDiCaL", [*solver_cmd, str(raw)], args.seconds + 20,
                           include_stdout=True)
        except BaseException:
            # The output directory contains no retained partial evidence.
            (out / "failure.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            raise
        total_cpu += result["child_cpu_seconds"]
        require(result["exit"] in (0, 10, 20),
                f"CaDiCaL failed ({result['exit']}): {result['stderr_tail']}")
        lines = result.pop("_stdout").splitlines()
        result["stats"] = solver_statistics(lines)
        marker = {0: "c UNKNOWN", 10: "s SATISFIABLE", 20: "s UNSATISFIABLE"}[result["exit"]]
        require(marker in lines, "CaDiCaL exit code and result marker disagree")
        outcome = {0: "OPEN", 10: "SAT", 20: "UNSAT"}[result["exit"]]
        receipt["solver"] = {**result, "outcome": outcome, "status_line": marker}
        require(outcome == args.expected_outcome,
                f"unexpected outcome {outcome}, requested {args.expected_outcome}")
        if outcome == "SAT":
            raise RuntimeError("this refutation adapter does not certify SAT models; no proof retained")
        if outcome == "OPEN":
            receipt["artifact"] = None
            receipt["note"] = "OPEN is not UNSAT. Any partial proof stream was discarded."
            receipt["total_cpu_seconds"] = round(total_cpu, 6)
            (out / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            return receipt

        require(raw.is_file(), "solver reported UNSAT without an LRAT proof")
        receipt["raw_proof"] = {"sha256": sha256(raw), "bytes": raw.stat().st_size}
        trimmed = work / "trimmed.lrat"
        trim = run_stage("lrat-trim trim", [checker, cnf, raw, trimmed], args.check_seconds)
        total_cpu += trim["child_cpu_seconds"]
        require(verified(trim), f"native LRAT failed trim/check: {trim}")
        receipt["trim"] = trim
        replay = run_stage("lrat-trim backward replay", [checker, cnf, trimmed], args.check_seconds)
        total_cpu += replay["child_cpu_seconds"]
        require(verified(replay), f"trimmed LRAT failed backward replay: {replay}")
        forward = run_stage("lrat-trim forward replay", [checker, "-S", cnf, trimmed], args.check_seconds)
        total_cpu += forward["child_cpu_seconds"]
        require(verified(forward), f"trimmed LRAT failed forward replay: {forward}")
        receipt["replays"] = {"backward": replay, "forward": forward}
        ascii_proof = work / "trimmed.ascii.lrat"
        convert = run_stage("LRAT ASCII conversion", [checker, "-a", cnf, trimmed, ascii_proof],
                            args.check_seconds)
        total_cpu += convert["child_cpu_seconds"]
        require(verified(convert), f"ASCII LRAT conversion failed: {convert}")
        second = run_stage("independent Python RUP replay", [sys.executable, pycheck, cnf, ascii_proof],
                           args.check_seconds)
        total_cpu += second["child_cpu_seconds"]
        require(verified(second, "s VERIFIED (independent RUP-only replay)"),
                f"second LRAT checker rejected the proof: {second}")
        receipt["ascii_conversion"] = convert
        receipt["second_checker"] = second
        receipt["total_cpu_seconds"] = round(total_cpu, 6)
        receipt["native_processing_cpu_seconds"] = round(
            result["child_cpu_seconds"] + trim["child_cpu_seconds"]
            + replay["child_cpu_seconds"] + forward["child_cpu_seconds"], 6)
        artifact = install(trimmed, "leaf.lrat")
        receipt["artifact"] = {"path": artifact.name, "sha256": sha256(artifact),
                               "bytes": artifact.stat().st_size}
        receipt["validation"] = {"raw_trim_check": True, "backward_replay": True,
                                  "forward_replay": True, "independent_rup_replay": True,
                                  "state": "VERIFIED_UNSAT_BY_TWO_UNVERIFIED_LRAT_CHECKERS"}

    assert receipt["artifact"]["sha256"] == sha256(out / "leaf.lrat")
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def positive(value):
    result = int(value)
    if result <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cnf", required=True, type=Path)
    p.add_argument("--expect-sha256", required=True)
    p.add_argument("--out", required=True, type=Path,
                   help="fresh output directory; never reused or overwritten")
    p.add_argument("--checker", required=True, type=Path,
                   help="reviewed lrat-trim binary (its recorded source hash is checked)")
    p.add_argument("--cadical", type=Path, default=CADICAL)
    p.add_argument("--conflicts", type=positive, default=50000)
    p.add_argument("--seconds", type=positive, default=20)
    p.add_argument("--check-seconds", type=positive, default=60)
    p.add_argument("--expected-outcome", choices=("UNSAT", "OPEN"), required=True)
    args = p.parse_args(argv)
    result = solve(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError) as error:
        raise SystemExit(f"native-solve: {error}")
