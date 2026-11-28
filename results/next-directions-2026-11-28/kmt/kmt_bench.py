"""Stage 3: matched parent+cube A/B, stock Sinz vs sender-only KMT.

Same convention as results/ams-wall-2026-11-28/conditional-sinz: fresh
CaDiCaL 1.9.5 through the pinned python-sat 1.9.dev22 binding, one subprocess
per call, no proof logging, CPU seconds reported separately from wall time.
"""
import argparse
import hashlib
import json
import math
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SCRATCH = REPO / ".scratch/m7"
EXPECTED = {
    "stock": "8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8",
    "kmt": "fdb46b2f8cddc74053809a8106801a327af32cc0ef191247b8980a0200779afd",
}
ROW = "06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06"


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
        "engine_doc": Cadical195.__doc__.strip(),
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
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--cap", type=int, default=100000)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--out", type=Path, default=HERE / "bench")
    args = parser.parse_args()
    if args.worker is not None:
        assert args.seed is not None
        worker(args.worker, args.seed, args.cap)
        return
    args.out.mkdir(exist_ok=True)
    orders = {0: ["stock", "kmt"], 1: ["kmt", "stock"]}
    records, sequence = [], 0
    for seed in (0, 1):
        for arm in orders[seed]:
            sequence += 1
            path = SCRATCH / f"{arm}-cube.cnf"
            query = digest(path)
            assert query == EXPECTED[arm], (arm, query)
            command = [sys.executable, "-B", str(Path(__file__).resolve()),
                       "--worker", str(path), "--seed", str(seed), "--cap", str(args.cap)]
            record = dict(sequence=sequence, arm=arm, seed=seed, row=ROW,
                          conflict_budget=args.cap, query_sha256=query,
                          query_bytes=path.stat().st_size, command=command,
                          wall_timeout_seconds=args.timeout, cube=[-1413, 1014])
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
                stdout = (result.stdout or b"").decode(errors="replace") if isinstance(
                    result.stdout, bytes) else (result.stdout or "")
                stderr = (result.stderr or b"").decode(errors="replace") if isinstance(
                    result.stderr, bytes) else (result.stderr or "")
            else:
                record["returncode"] = result.returncode
                stdout, stderr = result.stdout, result.stderr
                if result.returncode != 0:
                    record["status"] = "ERROR"
                else:
                    lines = [x for x in stdout.splitlines() if x.startswith("{")]
                    assert len(lines) == 1, (stdout, stderr)
                    record.update(json.loads(lines[0]))
            (args.out / f"{sequence:02d}-{arm}-s{seed}.log").write_text(
                stdout + "\n[stderr]\n" + stderr)
            (args.out / f"{sequence:02d}-{arm}-s{seed}.json").write_text(
                json.dumps(record, indent=2, sort_keys=True) + "\n")
            records.append(record)
            print(json.dumps({k: record.get(k) for k in (
                "sequence", "arm", "seed", "status", "search_process_cpu_seconds",
                "bootstrap_process_cpu_seconds", "parse_process_cpu_seconds",
                "maxrss_kib", "stats")}, sort_keys=True), flush=True)
            (args.out / "summary.json").write_text(
                json.dumps(records, indent=2, sort_keys=True) + "\n")
    ratios, memory = [], {}
    for seed in (0, 1):
        by = {r["arm"]: r for r in records if r["seed"] == seed}
        base, variant = by["stock"], by["kmt"]
        # The two arms have different clause counts, so cap overshoot differs by one
        # or two conflicts; both must be OPEN and both must have hit the cap.
        if (base["status"] == variant["status"] == "OPEN"
                and min(base["stats"]["conflicts"], variant["stats"]["conflicts"]) >= args.cap
                and abs(base["stats"]["conflicts"] - variant["stats"]["conflicts"]) <= 32):
            ratios.append(variant["search_process_cpu_seconds"]
                          / base["search_process_cpu_seconds"])
            memory[str(seed)] = dict(stock_kib=base["maxrss_kib"], kmt_kib=variant["maxrss_kib"])
        else:
            ratios.append(None)
    valid = [x for x in ratios if x is not None]
    geomean = math.prod(valid) ** (1 / len(valid)) if len(valid) == 2 else None
    memory_better = bool(memory) and all(v["kmt_kib"] < v["stock_kib"] for v in memory.values())
    analysis = dict(
        cpu_ratio_kmt_over_stock_by_seed=dict(zip((0, 1), ratios)),
        geometric_mean_ratio=geomean,
        memory=memory,
        memory_reduced=memory_better,
        statuses=[r["status"] for r in records],
        abandon=(geomean is None or geomean > 0.90) and not memory_better,
        favourable_bounded_throughput=(geomean is not None and geomean <= 0.90),
        determinate=any(r["status"] in ("SAT", "UNSAT") for r in records),
        scope=("CNF-only bounded performance on parent+cube; OPEN is not UNSAT; "
               "no physical colouring, ChainReady or bound is claimed"),
    )
    (args.out / "analysis.json").write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n")
    print(json.dumps(analysis, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
