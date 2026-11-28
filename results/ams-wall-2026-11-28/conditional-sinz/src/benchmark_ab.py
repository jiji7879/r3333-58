#!/usr/bin/env python3
"""Sequential fresh CaDiCaL195 A/B with complete per-call receipts."""
import argparse
import hashlib
import json
import math
import resource
import subprocess
import sys
import time
from pathlib import Path

M = Path(__file__).resolve().parent.parent
R = M / "results"
EXPECTED = {
    "parent": "90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae",
    "naive": "bac8c106d698a0734ca8dbec535b0ccc212d8329f5cd79b49e25f6071420d05b",
    "boundary": "fa8be04c4d10d38f803a0db34109732ee551ea1c85d4e834d369d5a73bd25cdc",
}


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def query(policy):
    return M / "inputs" / "parent.cnf" if policy == "parent" else R / f"wall-two5-{policy}.cnf"


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
    rec = {
        "engine": "CaDiCaL195 via python-sat",
        "pysat_version": pysat.__version__,
        "seed": seed,
        "conflict_budget": cap,
        "status": "OPEN" if answer is None else ("SAT_CNF_UNCERTIFIED" if answer else "UNSAT_CNF_UNCERTIFIED"),
        "parse_process_cpu_seconds": parsed - begin,
        "bootstrap_process_cpu_seconds": bootstrapped - parsed,
        "search_process_cpu_seconds": finished - bootstrapped,
        "total_process_cpu_seconds": finished - begin,
        "wall_seconds": time.monotonic() - wall,
        "stats": stats,
        "proof_logging": False,
        "maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    print(json.dumps(rec, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=Path)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--cap", type=int, default=1000000)
    ap.add_argument("--timeout", type=int, default=240)
    args = ap.parse_args()
    if args.worker is not None:
        assert args.seed is not None
        worker(args.worker, args.seed, args.cap)
        return
    assert args.seed is None
    audit = json.loads((R / "audit.json").read_text())
    assert audit["unsound_projection_results"] == 0
    out = R / "benchmark-1m"
    out.mkdir(exist_ok=False)
    policies = ["parent", "naive", "boundary"]
    records = []
    for seed in (0, 1):
        order = policies if seed == 0 else list(reversed(policies))
        for sequence, policy in enumerate(order, 1 + 3 * seed):
            path = query(policy)
            digest = file_hash(path)
            assert digest == EXPECTED[policy]
            command = [sys.executable, "-B", str(Path(__file__).resolve()),
                       "--worker", str(path), "--seed", str(seed), "--cap", str(args.cap)]
            before = resource.getrusage(resource.RUSAGE_CHILDREN)
            start = time.monotonic()
            rec = {"sequence": sequence, "row": "06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06",
                   "profile": [16, 16, 14, 11], "charge": 7, "policy": policy,
                   "seed": seed, "conflict_budget": args.cap,
                   "query_sha256": digest, "query_bytes": path.stat().st_size,
                   "command": command, "wall_timeout_seconds": args.timeout}
            try:
                result = subprocess.run(command, capture_output=True, text=True,
                                        timeout=args.timeout, check=False)
                timed_out = False
            except subprocess.TimeoutExpired as exc:
                result = exc
                timed_out = True
            after = resource.getrusage(resource.RUSAGE_CHILDREN)
            rec["driver_wall_seconds"] = time.monotonic() - start
            rec["children_user_cpu_delta_seconds"] = after.ru_utime - before.ru_utime
            rec["children_system_cpu_delta_seconds"] = after.ru_stime - before.ru_stime
            if timed_out:
                rec.update(status="OPEN_DRIVER_TIMEOUT", returncode=None)
                stdout = result.stdout or ""
                stderr = result.stderr or ""
                if isinstance(stdout, bytes): stdout = stdout.decode(errors="replace")
                if isinstance(stderr, bytes): stderr = stderr.decode(errors="replace")
            else:
                rec["returncode"] = result.returncode
                stdout, stderr = result.stdout, result.stderr
                if result.returncode != 0:
                    rec["status"] = "ERROR"
                else:
                    lines = [x for x in stdout.splitlines() if x.startswith("{")]
                    assert len(lines) == 1, (stdout, stderr)
                    rec.update(json.loads(lines[0]))
            (out / f"{sequence:02d}-{policy}-s{seed}.log").write_text(stdout + "\n[stderr]\n" + stderr)
            (out / f"{sequence:02d}-{policy}-s{seed}.json").write_text(
                json.dumps(rec, indent=2, sort_keys=True) + "\n")
            records.append(rec)
            print(json.dumps({k: rec.get(k) for k in ("sequence", "policy", "seed", "status",
                  "stats", "search_process_cpu_seconds", "driver_wall_seconds")}, sort_keys=True), flush=True)
            (out / "summary.tmp").write_text(json.dumps(records, indent=2, sort_keys=True) + "\n")
            (out / "summary.tmp").replace(out / "summary.json")
    ratios = []
    for seed in (0, 1):
        by = {r["policy"]: r for r in records if r["seed"] == seed}
        n, b = by["naive"], by["boundary"]
        if (n["status"] == b["status"] == "OPEN" and
                n["stats"]["conflicts"] == b["stats"]["conflicts"] and
                n["stats"]["conflicts"] >= args.cap):
            ratios.append(b["search_process_cpu_seconds"] / n["search_process_cpu_seconds"])
        else:
            ratios.append(None)
    valid = [x for x in ratios if x is not None]
    analysis = {"cpu_ratio_boundary_over_naive_by_seed": dict(zip((0, 1), ratios)),
                "geometric_mean_ratio": math.prod(valid) ** (1 / len(valid)) if len(valid) == 2 else None,
                "favourable_bounded_throughput_preregistered": len(valid) == 2 and all(x < 1 for x in valid) and math.prod(valid) ** 0.5 <= 0.95,
                "scope": "CNF-only bounded performance; no physical colouring or UNSAT certification"}
    (out / "analysis.json").write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n")
    print(json.dumps(analysis, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
