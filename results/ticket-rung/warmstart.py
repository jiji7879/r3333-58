#!/usr/bin/env python3
"""Warm-started solve: give the solver the polarities of a previous model.

usage: warmstart.py CNF PHASEMODEL [conf_budget] [solver]

The decision variables of ticketenc.build come *before* the ticket-layer
auxiliaries, so a model of the k-instance supplies phases for the (k+1)-instance
directly; this is the natural iterative deepening for the ticket-layer ladder
(minimum colour-0 degree per slot goes up by one at a time).
"""
import sys
import time

from pysat.solvers import Solver


def parse_model(path):
    ph = []
    with open(path) as fh:
        for line in fh:
            if line.startswith("s") or line.startswith("c"):
                continue
            for tok in line.split():
                if tok in ("v", "0"):
                    continue
                try:
                    v = int(tok)
                except ValueError:
                    continue
                ph.append(v)
    return ph


def main():
    cnf, modelpath = sys.argv[1], sys.argv[2]
    budget = int(sys.argv[3]) if len(sys.argv) > 3 else 2000000
    name = sys.argv[4] if len(sys.argv) > 4 else "cadical153"
    phases = parse_model(modelpath)
    t0 = time.time()
    cls = []
    for line in open(cnf):
        if line.startswith("p") or line.startswith("c"):
            continue
        lits = [int(t) for t in line.split()]
        if lits and lits[-1] == 0:
            lits = lits[:-1]
        if lits:
            cls.append(lits)
    with Solver(name=name, bootstrap_with=cls) as s:
        s.set_phases(phases)
        s.conf_budget(budget)
        res = s.solve_limited(expect_interrupt=True)
        dt = time.time() - t0
        print("result:", res, "time: %.1fs" % dt, "conflicts:",
              s.accum_stats().get("conflicts"))
        if res:
            out = open("runs/warm_model.out", "w")
            out.write("s SATISFIABLE\n")
            m = [l for l in s.get_model() if l > 0]
            for i in range(0, len(m), 20):
                out.write("v " + " ".join(map(str, m[i:i + 20])) + "\n")
            out.write("v 0\n")
            out.close()
            print("wrote runs/warm_model.out")
    return 0


if __name__ == "__main__":
    sys.exit(main())
