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
    ap.add_argument("--cadical", default=None,
                    help="optional external CaDiCaL executable, used with --engine cadical")
    ap.add_argument("--kissat", default=str(Path(__file__).resolve().parents[2] / 'bin' / 'kissat'))
    ap.add_argument("--engine", choices=('cadical', 'kissat'), default='kissat')
    ap.add_argument("--checker", required=True)
    ap.add_argument("--conflicts", type=int, default=60000)
    ap.add_argument("--seconds", type=int, default=280)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    clause = tuple(map(int, args.clause.split(",")))
    raw = args.stock.read_bytes()
    query = args.out / "query.cnf"
    query.write_bytes(serialize(raw, [[-lit] for lit in clause]))
    # A true proof on an arbitrary CNF is not a proof for the named rank.
    # Rebuild the exact historical parent and compare its complete bytes.
    from two5_encoder import original as historical_original
    expected_record, _, expected_raw = historical_original(args.rank)
    if raw != expected_raw:
        raise SystemExit('stock CNF is not the exact named historical full-root parent')
    assert sha(args.stock) == expected_record['input_sha256']
    if args.engine == 'kissat':
        solver = args.kissat
        command = [solver, '--quiet', '--time=' + str(args.seconds),
                   '--conflicts=' + str(args.conflicts), '--seed=0',
                   str(query), str(args.out / 'proof.drat')]
    else:
        if not args.cadical:
            raise SystemExit('--engine cadical requires an explicit --cadical executable')
        solver = args.cadical
        command = [solver, '-n', '-c', str(args.conflicts), '-t', str(args.seconds),
                   '--seed=0', str(query), str(args.out / 'proof.drat')]
    rec = {"rank": args.rank, "clause": clause,
           "false_cube_units": [-lit for lit in clause],
           "stock_sha256": sha(args.stock), "query_sha256": sha(query),
           "cadical_command": command, "conflict_limit": args.conflicts,
           "native_seconds_limit": args.seconds, "engine": args.engine}
    if args.conflicts < 1 or args.seconds < 1:
        raise SystemExit('both --conflicts and --seconds must be positive finite budgets')
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
    # CaDiCaL emits (pseudo)unit deletions that some drat-trim modes warn about.
    # Do not hide them: retain every addition, drop d records only, and enforce
    # strict warning-free RUP checking on the normalized proof.
    import sys
    normalizer = Path(__file__).with_name("normalize_replay.py")
    command = [sys.executable, str(normalizer), str(args.out), "--checker", args.checker]
    try:
        check = subprocess.run(command, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        rec["verified"] = False
        rec["replay_failure"] = "strict replay exceeded 300 seconds"
        args.out.joinpath("receipt.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
        print(json.dumps(rec, indent=2, default=list))
        raise SystemExit(1)
    strict_path = args.out / "strict-replay.json"
    if strict_path.exists():
        rec["strict_replay"] = json.loads(strict_path.read_text())
        rec["verified"] = rec["strict_replay"]["strict_accepted"]
        negative = subprocess.run([sys.executable, str(Path(__file__).with_name('strict_negative.py')),
                                   str(args.out)], capture_output=True, text=True, timeout=300)
        rec["negative_control"] = json.loads((args.out / "negative-replay.json").read_text())
        rec["verified"] = rec["verified"] and negative.returncode == 0 and rec["negative_control"]["rejected"]
        rec["original_proof_bytes"] = rec["strict_replay"]["original_proof_bytes"]
        rec["original_proof_sha256"] = rec["strict_replay"]["original_proof_sha256"]
        rec["normalization"] = "only d records removed; all additions retained in original order"
    else:
        rec["verified"] = False
        rec["replay_failure"] = check.stdout[-2000:] + check.stderr[-2000:]
    (args.out / "receipt.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(json.dumps(rec, indent=2, default=list))
    if not rec["verified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
