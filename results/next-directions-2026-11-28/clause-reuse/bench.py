"""Matched parent+cube A/B: retained request (sha 8791f6...) versus the same
bytes plus 960 checked square/matching clauses for the same row (sha 603f8d...).

Same convention as results/next-directions-2026-11-28/kmt/kmt_bench.py: fresh
CaDiCaL 1.9.5 through the pinned python-sat 1.9.dev22 binding, one subprocess
per call, no proof logging, CPU reported separately from wall time. Arms are run
in both orders at matched seeds and conflict caps. OPEN is not a verdict.
"""
import argparse, hashlib, json, resource, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
EXPECTED = {"base": "8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8",
            "aug": "603f8de8f9a20924efac885e9436b9968e36fe201c5e66ffeea5538309936ba2"}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def worker(path, seed, cap):
    import pysat
    from pysat.formula import CNF
    from pysat.solvers import Cadical195
    begin = time.process_time(); wall = time.monotonic()
    form = CNF(from_file=str(path)); parsed = time.process_time()
    with Cadical195(bootstrap_with=form.clauses) as solver:
        solver.configure({"seed": seed})
        bootstrapped = time.process_time()
        solver.conf_budget(cap)
        answer = solver.solve_limited()
        finished = time.process_time()
        stats = solver.accum_stats()
    print(json.dumps({
        "engine": "CaDiCaL 1.9.5 via python-sat 1.9.dev22",
        "pysat_version": pysat.__version__,
        "seed": seed, "conflict_budget": cap,
        "status": "OPEN" if answer is None else ("SAT" if answer else "UNSAT"),
        "parse_cpu": parsed - begin, "bootstrap_cpu": bootstrapped - parsed,
        "search_cpu": finished - bootstrapped, "total_cpu": finished - begin,
        "wall": time.monotonic() - wall, "stats": stats,
        "nvars": form.nv, "nclauses": len(form.clauses), "proof_logging": False,
        "maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}, sort_keys=True))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=Path); ap.add_argument("--seed", type=int)
    ap.add_argument("--cap", type=int, default=100000)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--out", type=Path, default=HERE / "bench")
    args = ap.parse_args()
    if args.worker is not None:
        worker(args.worker, args.seed, args.cap); return
    args.out.mkdir(exist_ok=True)
    orders = {0: ["base", "aug"], 1: ["aug", "base"]}
    records, seq = [], 0
    for seed in (0, 1):
        for arm in orders[seed]:
            seq += 1
            path = HERE / ("parent-cube.cnf" if arm == "base" else "parent-cube-aug.cnf")
            query = digest(path); assert query == EXPECTED[arm], (arm, query)
            cmd = [sys.executable, "-B", str(Path(__file__).resolve()), "--worker", str(path),
                   "--seed", str(seed), "--cap", str(args.cap)]
            rec = {"sequence": seq, "arm": arm, "seed": seed, "conflict_budget": args.cap,
                   "query_sha256": query, "query_bytes": path.stat().st_size, "command": cmd}
            before = resource.getrusage(resource.RUSAGE_CHILDREN); started = time.monotonic()
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout, check=False)
            after = resource.getrusage(resource.RUSAGE_CHILDREN)
            rec["driver_wall_seconds"] = time.monotonic() - started
            rec["children_user_cpu_seconds"] = after.ru_utime - before.ru_utime
            rec["children_system_cpu_seconds"] = after.ru_stime - before.ru_stime
            rec["returncode"] = res.returncode
            assert res.returncode == 0, (res.stdout, res.stderr)
            lines = [x for x in res.stdout.splitlines() if x.startswith("{")]
            assert len(lines) == 1, (res.stdout, res.stderr)
            rec.update(json.loads(lines[0]))
            (args.out / f"{seq:02d}-{arm}-s{seed}.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
            records.append(rec)
            print(json.dumps({k: rec.get(k) for k in ("sequence", "arm", "seed", "status",
                  "search_cpu", "total_cpu", "maxrss_kib", "stats")}, sort_keys=True), flush=True)
    (args.out / "summary.json").write_text(json.dumps(records, indent=2, sort_keys=True) + "\n")
    for seed in (0, 1):
        by = {r["arm"]: r for r in records if r["seed"] == seed}
        b, a = by["base"], by["aug"]
        print(json.dumps({"seed": seed,
            "cpu_ratio_aug_over_base": a["search_cpu"] / b["search_cpu"],
            "conflicts_base": b["stats"].get("conflicts"), "conflicts_aug": a["stats"].get("conflicts"),
            "rss_ratio": a["maxrss_kib"] / b["maxrss_kib"]}, sort_keys=True))

if __name__ == "__main__":
    main()
