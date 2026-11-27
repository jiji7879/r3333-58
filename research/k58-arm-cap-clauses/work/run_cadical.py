#!/usr/bin/env python3
"""Fresh-process matched CaDiCaL runs on an immutable generated panel.

Timing runs never request a proof.  Exit 10 is SAT, 20 is UNSAT, and 0 with
s UNKNOWN (including conflict/time limits) is OPEN.  Other exits are failures.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time

CADICAL = Path("/opt/lean/bin/cadical")
FIELDS = ("conflicts", "decisions", "propagations", "restarts", "learned",
          "fixed", "eliminated", "reduced", "subsumed", "strengthened")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def version():
    return subprocess.check_output([str(CADICAL), "--version"], text=True).strip()


def one(cnf, seed, seconds, log_path):
    limit = str(int(seconds)) if float(seconds).is_integer() else str(seconds)
    cmd = [str(CADICAL), "-t", limit, "--seed=" + str(seed), "-n", str(cnf)]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.perf_counter()
    timed_out = False
    try:
        with log_path.open("wb") as log:
            run = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT,
                                 timeout=seconds + 10)
        rc = run.returncode
    except subprocess.TimeoutExpired:
        rc = None
        timed_out = True
    wall = time.perf_counter() - started
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    text = log_path.read_text(errors="replace") if log_path.exists() else ""
    lines = [line.strip() for line in text.splitlines() if line.startswith("s ")]
    result = {"command": cmd, "query_sha256": sha(cnf), "seed": seed,
              "native_time_limit_seconds": seconds, "returncode": rc,
              "wall_seconds": wall, "search_plus_parse_cpu_seconds": cpu,
              "external_timeout": timed_out, "status_lines": lines,
              "log": log_path.name, "cadical_version": version()}
    if rc == 10 and lines == ["s SATISFIABLE"]:
        result["status"] = "SAT"
    elif rc == 20 and lines == ["s UNSATISFIABLE"]:
        result["status"] = "UNSAT"
    elif rc == 0 and lines == ["s UNKNOWN"]:
        result["status"] = "OPEN"
    elif timed_out:
        result["status"] = "OPEN_EXTERNAL_TIMEOUT"
    else:
        result["status"] = "ERROR"
    for field in FIELDS:
        prefix = "c " + field + ":"
        matches = [line[len(prefix):].strip().split() for line in text.splitlines()
                   if line.startswith(prefix)]
        if matches:
            result[field] = int(matches[-1][0].replace(",", ""))
    matches = [line for line in text.splitlines()
               if line.startswith("c total process time since initialization:")]
    if matches:
        result["cadical_total_process_seconds"] = float(matches[-1].split(":")[-1].strip().split()[0])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--ranks", default="1300")
    parser.add_argument("--policies", default="stock,ternary,direct,signed,wide")
    parser.add_argument("--seeds", default="0")
    parser.add_argument("--seconds", type=float, default=290)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    assert 0 < args.seconds <= 290
    assert not args.out.exists(), "refusing to overwrite a run"
    args.out.mkdir(parents=True)
    policies = args.policies.split(",")
    records = []
    by_hash = {}
    for seed in map(int, args.seeds.split(",")):
        for rank in map(int, args.ranks.split(",")):
            ordered = policies if (rank + seed) % 2 else list(reversed(policies))
            for policy in ordered:
                cnf = args.panel / str(rank) / (policy + ".cnf")
                digest = sha(cnf)
                identity = (digest, seed)
                if identity in by_hash:
                    old = by_hash[identity]
                    rec = {"rank": rank, "policy": policy, "seed": seed,
                           "status": "ALIAS_NOT_RERUN", "query_sha256": digest,
                           "alias_of": {"rank": old["rank"], "policy": old["policy"],
                                        "seed": old["seed"]}}
                    print(json.dumps(rec, sort_keys=True), flush=True)
                else:
                    rec = one(cnf, seed, args.seconds,
                              args.out / f"r{rank}-{policy}-s{seed}.log")
                    rec.update(rank=rank, policy=policy)
                    by_hash[identity] = rec
                    print(json.dumps(rec, sort_keys=True), flush=True)
                records.append(rec)
                temp = args.out / "results.json.tmp"
                temp.write_text(json.dumps(records, indent=2, sort_keys=True) + "\n")
                temp.replace(args.out / "results.json")
                assert rec["status"] not in ("SAT", "ERROR"), rec


if __name__ == "__main__":
    main()
