#!/usr/bin/env python3
"""Sequential matched native-CaDiCaL runs with complete per-call receipts."""
import argparse
import hashlib
import json
import re
import resource
import subprocess
import time
from pathlib import Path

PATTERNS = {key: re.compile(r"^c " + key + r":\s+(\d+)", re.M)
            for key in ("conflicts", "decisions", "propagations", "fixed", "learned")}


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--ranks", default="1200,1300")
    ap.add_argument("--policies", default="stock,direct,old-selectors,factored,factored-exact,factored-seq")
    ap.add_argument("--caps", default="60000")
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--cadical", default="/opt/lean/bin/cadical")
    ap.add_argument("--seconds", type=int, default=280)
    ap.add_argument("--reverse", action="store_true")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    records = []
    jobs = [(int(rank), policy, int(cap), int(seed))
            for rank in args.ranks.split(",")
            for cap in args.caps.split(",")
            for seed in args.seeds.split(",")
            for policy in args.policies.split(",")]
    if args.reverse:
        # Reverse policies within each rank/cap/seed group, not rank order.
        jobs = [(r, p, c, s) for r in args.ranks.split(",")
                for c in args.caps.split(",") for s in args.seeds.split(",")
                for p in reversed(args.policies.split(","))]
        jobs = [(int(r), p, int(c), int(s)) for r, p, c, s in jobs]
    version = subprocess.run([args.cadical, "--version"], check=True,
                             capture_output=True, text=True).stdout.strip()
    for sequence, (rank, policy, cap, seed) in enumerate(jobs, 1):
        query = args.build / str(rank) / (policy + ".cnf")
        command = [args.cadical, "-n", "-c", str(cap), "-t", str(args.seconds),
                   "--seed=" + str(seed), str(query)]
        rec = {"sequence": sequence, "rank": rank, "policy": policy,
               "conflict_budget": cap, "seed": seed, "query": str(query),
               "query_bytes": query.stat().st_size, "query_sha256": sha(query),
               "cadical": args.cadical, "cadical_version": version,
               "command": command, "wall_seconds_limit_native": args.seconds}
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        wall = time.monotonic()
        try:
            result = subprocess.run(command, capture_output=True, text=True,
                                    timeout=args.seconds)
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            result = exc
            timed_out = True
        rec["wall_seconds"] = time.monotonic() - wall
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        rec["user_cpu_seconds"] = after.ru_utime - before.ru_utime
        rec["system_cpu_seconds"] = after.ru_stime - before.ru_stime
        rec["maxrss_kib_delta_not_size"] = after.ru_maxrss  # retained raw high-water mark
        if timed_out:
            rec.update(returncode=None, status="OPEN_CALL_TIMEOUT")
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            if isinstance(stdout, bytes): stdout = stdout.decode(errors="replace")
            if isinstance(stderr, bytes): stderr = stderr.decode(errors="replace")
        else:
            rec["returncode"] = result.returncode
            stdout, stderr = result.stdout, result.stderr
            if result.returncode == 20:
                rec["status"] = "UNSAT"
            elif result.returncode == 10:
                rec["status"] = "SAT"
            elif result.returncode == 0:
                rec["status"] = "OPEN"
            else:
                rec["status"] = "ERROR"
        (args.out / f"{sequence:03d}-{rank}-{policy}-c{cap}-s{seed}.log").write_text(
            "$ " + " ".join(command) + "\n" + stdout + "\n[stderr]\n" + stderr)
        rec["stdout_tail"] = "\n".join(stdout.splitlines()[-8:])
        rec["stderr_tail"] = "\n".join(stderr.splitlines()[-8:])
        for key, pattern in PATTERNS.items():
            found = pattern.findall(stdout)
            rec[key] = int(found[-1]) if found else None
        match = re.findall(r"^c total process time since initialization:\s+([0-9.]+)", stdout, re.M)
        rec["cadical_total_process_seconds"] = float(match[-1]) if match else None
        match = re.findall(r"^c total real time since initialization:\s+([0-9.]+)", stdout, re.M)
        rec["cadical_total_real_seconds"] = float(match[-1]) if match else None
        (args.out / f"{sequence:03d}-{rank}-{policy}-c{cap}-s{seed}.json").write_text(
            json.dumps(rec, indent=2, sort_keys=True) + "\n")
        records.append(rec)
        print(json.dumps({k: rec[k] for k in ("sequence", "rank", "policy", "seed",
                         "conflict_budget", "status", "conflicts", "propagations",
                         "user_cpu_seconds", "wall_seconds")}), flush=True)
    (args.out / "summary.json").write_text(json.dumps(records, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
