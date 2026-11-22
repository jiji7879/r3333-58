#!/usr/bin/env python3
"""One solver process, one instance, hard wall-clock cap. Prints a summary."""
import argparse
import json
import os
import sys
import threading
import time

from pysat.formula import CNF
from pysat.solvers import Solver


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cnf")
    ap.add_argument("--seconds", type=float, default=120.0)
    ap.add_argument("--solver", default="cadical195")
    ap.add_argument("--model-out", default=None)
    ap.add_argument("--conf-budget", type=int, default=0)
    a = ap.parse_args()

    t0 = time.time()
    cnf = CNF(from_file=a.cnf)
    s = Solver(name=a.solver, bootstrap_with=cnf.clauses)
    if a.conf_budget:
        s.conf_budget(a.conf_budget)

    fired = {"v": False}

    def stop():
        fired["v"] = True
        s.interrupt()

    tm = threading.Timer(a.seconds, stop)
    tm.start()
    try:
        res = s.solve_limited(expect_interrupt=True)
    finally:
        tm.cancel()
        elapsed = time.time() - t0

    st = "SAT" if res is True else ("UNSAT" if res is False else "UNKNOWN")
    stats = {}
    try:
        stats = s.accum_stats()
    except Exception:
        pass
    print(json.dumps({
        "cnf": a.cnf, "solver": a.solver, "status": st,
        "seconds": round(elapsed, 2), "interrupted": fired["v"],
        "stats": {k: str(v) for k, v in stats.items()},
    }))
    if res is True and a.model_out:
        with open(a.model_out, "w") as fh:
            for lit in s.get_model():
                fh.write(f"{lit}\n")
    s.delete()


if __name__ == "__main__":
    main()
