#!/usr/bin/env python3
"""Fresh matched runs isolating guard removal from intra-gadget clause order."""
import json
import resource
import subprocess
import sys
import time
from pathlib import Path
from benchmark_ab import file_hash, EXPECTED

M = Path(__file__).resolve().parent.parent
R = M / "results"
EXPECTED["naive-split"] = "02fc6b42b7edb93aa7647b5bbcc384a1a1328b64e6d1a1afba96657fdbe00f5d"


def main():
    cap, timeout = 1000000, 240
    audit = json.loads((R / "audit-order.json").read_text())
    assert audit["legacy_vs_split_clause_multiset_mismatches"] == 0
    assert audit["split_vs_boundary_positional_mismatches"] == 0
    assert audit["unsound_split_projection_results"] == 0
    out = R / "benchmark-order-1m"
    out.mkdir(exist_ok=False)
    orders = {0: ["naive-split", "boundary", "naive"],
              1: ["naive", "boundary", "naive-split"]}
    records = []
    sequence = 0
    for seed in (0, 1):
        for policy in orders[seed]:
            sequence += 1
            path = R / f"wall-two5-{policy}.cnf"
            digest = file_hash(path)
            assert digest == EXPECTED[policy]
            worker = M / "src" / "benchmark_ab.py"
            command = [sys.executable, "-B", str(worker), "--worker", str(path),
                       "--seed", str(seed), "--cap", str(cap)]
            before = resource.getrusage(resource.RUSAGE_CHILDREN)
            start = time.monotonic()
            rec = {"sequence": sequence, "row": "06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06",
                   "profile": [16, 16, 14, 11], "charge": 7, "policy": policy,
                   "seed": seed, "conflict_budget": cap, "query_sha256": digest,
                   "query_bytes": path.stat().st_size, "command": command,
                   "wall_timeout_seconds": timeout, "stage": "clause-order-control"}
            try:
                result = subprocess.run(command, capture_output=True, text=True,
                                        timeout=timeout, check=False)
                timed_out = False
            except subprocess.TimeoutExpired as exc:
                result, timed_out = exc, True
            after = resource.getrusage(resource.RUSAGE_CHILDREN)
            rec["driver_wall_seconds"] = time.monotonic() - start
            rec["children_user_cpu_delta_seconds"] = after.ru_utime - before.ru_utime
            rec["children_system_cpu_delta_seconds"] = after.ru_stime - before.ru_stime
            if timed_out:
                rec.update(status="OPEN_DRIVER_TIMEOUT", returncode=None)
                stdout, stderr = result.stdout or "", result.stderr or ""
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


if __name__ == "__main__":
    main()
