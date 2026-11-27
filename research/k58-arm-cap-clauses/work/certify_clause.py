#!/usr/bin/env python3
"""Prepare and strictly replay a selected clause's original-parent false cube."""
import argparse
import hashlib
import json
import os
import resource
import subprocess
import time
from pathlib import Path

from counter_encoding import serialize


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rank", type=int, required=True)
    ap.add_argument("--clause", required=True, help="comma-separated signed DIMACS lits")
    ap.add_argument("--stock", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--cadical", default="/opt/lean/bin/cadical")
    ap.add_argument("--checker", required=True)
    ap.add_argument("--conflicts", type=int, default=60000)
    ap.add_argument("--seconds", type=int, default=280)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    clause = tuple(map(int, args.clause.split(",")))
    raw = args.stock.read_bytes()
    query = args.out / "query.cnf"
    query.write_bytes(serialize(raw, [[-lit] for lit in clause]))
    command = [args.cadical, "-n", "-c", str(args.conflicts), "-t", str(args.seconds),
               "--seed=0", str(query), str(args.out / "proof.drat")]
    rec = {"rank": args.rank, "clause": clause,
           "false_cube_units": [-lit for lit in clause],
           "stock_sha256": sha(args.stock), "query_sha256": sha(query),
           "cadical_command": command, "conflict_limit": args.conflicts,
           "native_seconds_limit": args.seconds}
    wall = time.monotonic()
    result = subprocess.run(command, capture_output=True, text=True, timeout=args.seconds)
    rec["search_wall_seconds"] = time.monotonic() - wall
    rec["cadical_returncode"] = result.returncode
    rec["search_status"] = {10: "SAT", 20: "UNSAT", 0: "OPEN"}.get(result.returncode, "ERROR")
    (args.out / "cadical.log").write_text(result.stdout + "\n[stderr]\n" + result.stderr)
    if result.returncode != 20:
        (args.out / "receipt.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
        print(json.dumps(rec, default=list))
        return
    proof = args.out / "proof.drat"
    rec["proof_bytes"] = proof.stat().st_size
    rec["proof_sha256"] = sha(proof)
    check = [args.checker, str(query), str(proof), "-i", "-U", "-W", "-t", "300"]
    rec["checker_command"] = check
    wall = time.monotonic()
    checked = subprocess.run(check, capture_output=True, text=True, timeout=300)
    rec["replay_wall_seconds"] = time.monotonic() - wall
    rec["checker_returncode"] = checked.returncode
    log = checked.stdout + "\n[stderr]\n" + checked.stderr
    (args.out / "checker.log").write_text(log)
    rec["verified"] = (checked.returncode == 0 and
                       checked.stdout.count("s VERIFIED") == 1 and
                       "s NOT VERIFIED" not in checked.stdout and
                       "WARNING" not in log.upper() and "ERROR" not in log.upper())
    rec["checker_output_tail"] = log.splitlines()[-20:]
    (args.out / "receipt.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(json.dumps(rec, indent=2, default=list))
    if not rec["verified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
