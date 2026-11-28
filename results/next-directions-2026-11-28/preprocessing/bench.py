#!/usr/bin/env python3
"""Matched A/B on one constant host CNF and its one-shot reduced form.

Convention copied deliberately from the accepted KMT benchmark
(`.ultramath/smx06hpp8/m7/kmt_bench.py`): one fresh CaDiCaL 1.9.5 process per
call through the pinned python-sat 1.9.dev22 binding, identical conflict budget
and seed, CPU measured with `time.process_time` inside the worker and separately
with RUSAGE_CHILDREN outside, RSS from `resource`.  Order is swapped between the
two seeds so a linear drift cannot favour one arm.

This measures the *whole* leaf step: DIMACS parse + solver bootstrapping + the
capped search, because the reduced formula changes all three.

OPEN is not UNSAT.  Only a returned False at an uncapped budget would be a
proof-level claim, and this script never makes one.
"""
import argparse
import hashlib
import json
import math
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYTHON = os.environ.get("K58_PYSAT_PYTHON", "")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def worker(path, seed, cap):
    import pysat
    from pysat.formula import CNF
    from pysat.solvers import Cadical195
    begin = time.process_time()
    wall = time.monotonic()
    form = CNF(from_file=str(path))
    parsed = time.process_time()
    with Cadical195(bootstrap_with=form.clauses) as solver:
        solver.configure({"seed": seed})
        bootstrapped = time.process_time()
        solver.conf_budget(cap)
        answer = solver.solve_limited()
        finished = time.process_time()
        stats = solver.accum_stats()
    record = {
        "engine": "CaDiCaL 1.9.5 via python-sat 1.9.dev22",
        "pysat_version": pysat.__version__,
        "seed": seed,
        "conflict_budget": cap,
        "status": "OPEN" if answer is None else ("SAT" if answer else "UNSAT"),
        "parse_process_cpu_seconds": parsed - begin,
        "bootstrap_process_cpu_seconds": bootstrapped - parsed,
        "search_process_cpu_seconds": finished - bootstrapped,
        "total_process_cpu_seconds": finished - begin,
        "wall_seconds": time.monotonic() - wall,
        "stats": stats,
        "nvars": form.nv,
        "nclauses": len(form.clauses),
        "proof_logging": False,
        "maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    print(json.dumps(record, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", action="append", default=[],
                        metavar="NAME=PATH@SHA256")
    parser.add_argument("--seeds", default="0,1")
    parser.add_argument("--caps", default="100000")
    parser.add_argument("--out", type=Path, default=HERE / "work/bench")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--cap", type=int)
    args = parser.parse_args()

    if args.worker is not None:
        worker(args.worker, args.seed, args.cap)
        return 0

    if not PYTHON:
        raise SystemExit("set K58_PYSAT_PYTHON to the interpreter holding python-sat 1.9.dev22")
    if len(args.arm) < 2:
        raise SystemExit("give at least two --arm NAME=PATH@SHA256")
    arms = {}
    for spec in args.arm:
        name, rest = spec.split("=", 1)
        path, expected = rest.rsplit("@", 1)
        path = Path(path).resolve()
        found = digest(path)
        if found != expected:
            raise SystemExit(f"arm {name}: hash mismatch {found} != {expected}")
        arms[name] = (path, found)
    seeds = [int(x) for x in args.seeds.split(",")]
    caps = [int(x) for x in args.caps.split(",")]
    args.out.mkdir(parents=True, exist_ok=True)

    records, sequence = [], 0
    for cap in caps:
        for seed in seeds:
            order = list(arms)
            if (seed + cap // 100000) % 2:
                order.reverse()
            for name in order:
                sequence += 1
                path, found = arms[name]
                command = [PYTHON, "-B", str(Path(__file__).resolve()),
                           "--worker", str(path), "--seed", str(seed), "--cap", str(cap)]
                record = dict(sequence=sequence, arm=name, seed=seed, cap=cap,
                              query_sha256=found, query_bytes=path.stat().st_size,
                              command=command)
                before = resource.getrusage(resource.RUSAGE_CHILDREN)
                started = time.monotonic()
                try:
                    result = subprocess.run(command, capture_output=True, text=True,
                                            timeout=args.timeout, check=False)
                    timed_out = False
                except subprocess.TimeoutExpired as error:
                    result, timed_out = error, True
                after = resource.getrusage(resource.RUSAGE_CHILDREN)
                record["driver_wall_seconds"] = time.monotonic() - started
                record["children_user_cpu_seconds"] = after.ru_utime - before.ru_utime
                record["children_system_cpu_seconds"] = after.ru_stime - before.ru_stime
                if timed_out:
                    record.update(status="OPEN_DRIVER_TIMEOUT", returncode=None)
                    record["stderr"] = ""
                else:
                    record["returncode"] = result.returncode
                    lines = [x for x in result.stdout.splitlines() if x.startswith("{")]
                    if result.returncode != 0 or len(lines) != 1:
                        record.update(status="ERROR", stderr=result.stderr[-2000:])
                    else:
                        record.update(json.loads(lines[0]))
                records.append(record)
                print(json.dumps({k: record.get(k) for k in (
                    "sequence", "arm", "seed", "cap", "status",
                    "search_process_cpu_seconds", "total_process_cpu_seconds",
                    "maxrss_kib", "stats")}, sort_keys=True), flush=True)
                (args.out / "records.json").write_text(
                    json.dumps(records, indent=2, sort_keys=True) + "\n")

    analysis = {"caps": caps, "seeds": seeds, "comparisons": []}
    names = list(arms)
    if len(names) >= 2:
        for cap in caps:
            for seed in seeds:
                by = {r["arm"]: r for r in records if r["seed"] == seed and r["cap"] == cap}
                base, variant = by[names[0]], by[names[1]]
                row = {"cap": cap, "seed": seed,
                       "base": names[0], "variant": names[1],
                       "statuses": [base.get("status"), variant.get("status")]}
                if base.get("status") == variant.get("status") == "OPEN":
                    row["total_cpu_ratio"] = (variant["total_process_cpu_seconds"]
                                              / base["total_process_cpu_seconds"])
                    row["search_cpu_ratio"] = (variant["search_process_cpu_seconds"]
                                               / base["search_process_cpu_seconds"])
                    row["conflict_ratio"] = (variant["stats"]["conflicts"]
                                             / max(base["stats"]["conflicts"], 1))
                    row["propagation_ratio"] = (variant["stats"]["propagations"]
                                                / max(base["stats"]["propagations"], 1))
                    row["rss_ratio"] = variant["maxrss_kib"] / base["maxrss_kib"]
                analysis["comparisons"].append(row)
        ratios = [r["total_cpu_ratio"] for r in analysis["comparisons"]
                  if r.get("total_cpu_ratio")]
        if ratios:
            analysis["total_cpu_geomean"] = math.prod(ratios) ** (1 / len(ratios))
    analysis["scope"] = ("capped CNF-only A/B on one constant host; OPEN is not UNSAT; "
                         "no physical colouring, cover or bound is claimed")
    (args.out / "analysis.json").write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n")
    print(json.dumps(analysis, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
