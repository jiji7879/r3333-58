#!/usr/bin/env python3
"""One matched A/B on the exact retained parent+cube, incumbent CaDiCaL 1.9.5.

Arms
  baseline : parent_cube.cnf                      (19533 vars, 184337 clauses)
  sms      : parent_cube.cnf + the 765 verified one-colour clauses
             (augmented.cnf, produced by verify_clauses.py)
  corrupted: parent_cube.cnf + the same 765 clauses with the last literal of each
             negated (a *trajectory* control only: this instance is not sound and
             must never be used for any status claim)

Both arms are run in fresh processes with the same PySAT build (1.9.dev22,
solver Cadical195 = CaDiCaL 1.9.5), jobs=1, conflict cap 200000.  The wrapper
runs the arms in both orders so each arm is measured twice.

Status is reported as-is.  ``None`` means the conflict cap was hit: OPEN, not
UNSAT.  A SAT/UNSAT answer would change this into a full model/proof-gate
experiment and is not claimed here.
"""
import argparse
import json
import resource
import time
from pathlib import Path

from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent


def clauses(path):
    with open(path) as stream:
        header = stream.readline().split()
        nvars, nclauses = int(header[2]), int(header[3])
        count = 0
        for line in stream:
            yield [int(x) for x in line.split()[:-1]]
            count += 1
    assert count == nclauses, (count, nclauses)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("baseline", "sms", "corrupted"), required=True)
    parser.add_argument("--conflicts", type=int, default=200000)
    parser.add_argument("--seed-label", type=int, default=0)
    args = parser.parse_args()

    path = HERE / {"baseline": "parent_cube.cnf", "sms": "augmented.cnf",
                   "corrupted": "corrupted.cnf"}[args.arm]
    start = time.monotonic()
    cpu0 = time.process_time()
    solver = Cadical195(bootstrap_with=clauses(path), use_timer=True)
    prep_cpu = time.process_time() - cpu0
    solver.conf_budget(args.conflicts)
    solve0 = time.process_time()
    status = solver.solve_limited()
    solve_cpu = time.process_time() - solve0
    stats = solver.accum_stats()
    solver.delete()
    total_cpu = time.process_time() - cpu0
    receipt = {
        "arm": args.arm,
        "input": path.name,
        "conflict_cap": args.conflicts,
        "status": {None: "UNKNOWN", True: "SAT", False: "UNSAT"}[status],
        "solve_cpu_s": round(solve_cpu, 3),
        "prep_cpu_s": round(prep_cpu, 3),
        "total_cpu_s": round(total_cpu, 3),
        "wall_s": round(time.monotonic() - start, 3),
        "stats": stats,
        "peak_rss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "solver": "pysat Cadical195 (CaDiCaL 1.9.5)",
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
