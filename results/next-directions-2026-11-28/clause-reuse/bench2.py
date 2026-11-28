"""Three-arm matched-cap A/B/A: base vs all-960 vs the 600 nontrivial subset.
Same worker convention as bench.py (PySAT CaDiCaL 1.9.5)."""
import argparse, hashlib, json, resource, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ARMS = {"base": ("parent-cube.cnf", "8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8"),
        "aug960": ("parent-cube-aug.cnf", "603f8de8f9a20924efac885e9436b9968e36fe201c5e66ffeea5538309936ba2"),
        "aug600": ("parent-cube-aug600.cnf", "8c15935b9a0975c12d09142656b135ab1eac1dfcff613ee1aa7200063a13b986")}

def worker(path, seed, cap):
    import pysat
    from pysat.formula import CNF
    from pysat.solvers import Cadical195
    begin = time.process_time(); wall = time.monotonic()
    form = CNF(from_file=str(path)); parsed = time.process_time()
    with Cadical195(bootstrap_with=form.clauses) as solver:
        solver.configure({"seed": seed}); bootstrapped = time.process_time()
        solver.conf_budget(cap); answer = solver.solve_limited(); finished = time.process_time()
        stats = solver.accum_stats()
    print(json.dumps({"engine": "CaDiCaL 1.9.5 via python-sat 1.9.dev22", "seed": seed,
        "conflict_budget": cap, "status": "OPEN" if answer is None else ("SAT" if answer else "UNSAT"),
        "parse_cpu": parsed - begin, "bootstrap_cpu": bootstrapped - parsed,
        "search_cpu": finished - bootstrapped, "total_cpu": finished - begin,
        "wall": time.monotonic() - wall, "stats": stats, "nvars": form.nv,
        "nclauses": len(form.clauses), "proof_logging": False,
        "maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}, sort_keys=True))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=Path); ap.add_argument("--seed", type=int)
    ap.add_argument("--cap", type=int, default=300000)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--out", type=Path, default=HERE / "bench2")
    args = ap.parse_args()
    if args.worker is not None:
        worker(args.worker, args.seed, args.cap); return
    args.out.mkdir(exist_ok=True)
    orders = {0: ["base", "aug960", "aug600"], 1: ["aug600", "aug960", "base"]}
    records, seq = [], 0
    for seed in (0, 1):
        for arm in orders[seed]:
            seq += 1
            name, expected = ARMS[arm]; path = HERE / name
            query = hashlib.sha256(path.read_bytes()).hexdigest(); assert query == expected, (arm, query)
            cmd = [sys.executable, "-B", str(Path(__file__).resolve()), "--worker", str(path),
                   "--seed", str(seed), "--cap", str(args.cap)]
            rec = {"sequence": seq, "arm": arm, "seed": seed, "conflict_budget": args.cap,
                   "query_sha256": query, "query_bytes": path.stat().st_size}
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
            print(json.dumps({k: rec.get(k) for k in ("sequence", "arm", "seed", "status", "search_cpu",
                  "total_cpu", "maxrss_kib", "stats")}, sort_keys=True), flush=True)
    (args.out / "summary.json").write_text(json.dumps(records, indent=2, sort_keys=True) + "\n")
    for seed in (0, 1):
        by = {r["arm"]: r for r in records if r["seed"] == seed}
        b = by["base"]
        print(json.dumps({"seed": seed, **{f"cpu_ratio_{k}_over_base": by[k]["search_cpu"] / b["search_cpu"]
              for k in ("aug960", "aug600")},
              **{f"decisions_{k}": by[k]["stats"]["decisions"] for k in ("base", "aug960", "aug600")},
              **{f"propagations_{k}": by[k]["stats"]["propagations"] for k in ("base", "aug960", "aug600")}},
              sort_keys=True))

if __name__ == "__main__":
    main()
