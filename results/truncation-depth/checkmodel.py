#!/usr/bin/env python3
"""Evaluate a CNF's clauses under the assignment induced by a witness file.

Used as the falsification instrument for the encoder: if the witness is a model
of the pair level, no clause of the PLAIN instance may be violated.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k58lib import Witness, Template


def read_cnf(path):
    cls = []
    with open(path) as fh:
        hdr = fh.readline().split()
        nv, nc = int(hdr[2]), int(hdr[3])
        for line in fh:
            t = [int(v) for v in line.split()]
            assert t[-1] == 0
            cls.append(t[:-1])
    return nv, cls


def main(cnfpath, mappath, witpath):
    nv, cls = read_cnf(cnfpath)
    meta = json.load(open(mappath))
    meta = {int(k): v for k, v in meta.items()}
    w = Witness(witpath)
    val = {}
    for x in range(42):
        for a in range(15):
            f = w.words[x][a]
            for g in range(4):
                v = None
                for vv, info in meta.items():
                    if info[0] == "cell" and info[1] == x and info[2] == a and info[3] == g:
                        v = vv
                        break
                if v is None:
                    continue
                val[v] = (g == f)
    for (xx, yy), c in w.pairs.items():
        for vv, info in meta.items():
            if info[0] == "q" and info[1] == xx and info[2] == yy and info[3] == c:
                val[vv] = True
    # unassigned variables count as "free" -> a clause is violated only if all
    # its literals are assigned false
    bad = []
    for cl in cls:
        sat = False
        for lit in cl:
            v = abs(lit)
            if v not in val:
                sat = True
                break
            if val[v] == (lit > 0):
                sat = True
                break
        if not sat:
            bad.append(cl)
    print(f"clauses {len(cls)}, violated {len(bad)}")
    for cl in bad[:10]:
        info = [meta.get(abs(l), ("aux", abs(l))) for l in cl]
        print("  ", cl, info[:6])


if __name__ == "__main__":
    main(*sys.argv[1:])
