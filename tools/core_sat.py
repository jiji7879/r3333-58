#!/usr/bin/env python3
"""The arm-core instance C(p0,p1,p2,0) at n = 58, and a check of a colouring.

A vertex v of a good (triangle-free) 4-colouring of K_58 with profile
(p0,p1,p2,p3), p0 >= p1 >= p2 >= p3, induces a good colouring of
K_{1+p0+p1+p2} on {v} and its three largest colour classes, in which v has
colour-degrees exactly (p0,p1,p2,0).  So L (no vertex has two colour-degrees
<= 14) follows from the unsatisfiability of the seven cores below, one per wall
profile:

    (15,15,14,13) -> C(15,15,14,0) 45      (16,15,14,12) -> C(16,15,14,0) 46
    (16,15,13,13) -> C(16,15,13,0) 45      (15,14,14,14) -> C(15,14,14,0) 44
    (16,16,14,11) -> C(16,16,14,0) 47      (16,16,13,12) -> C(16,16,13,0) 46
    (16,14,14,13) -> C(16,14,14,0) 45

The converse fails: a core model need not extend to K_58.  A core is also
strictly weaker than the campaign's cases, whose models restrict to core
models, so UNSAT(core) is the stronger statement.

    python3 tools/core_sat.py 15 15 12 --cnf c.cnf      # write DIMACS
    python3 tools/core_sat.py 15 15 12 --check model.col  # verify a colouring

Building needs python-sat (CardEnc); checking needs nothing.
"""
import argparse
import sys
from itertools import combinations


def build(p):
    """Clauses of C(p0,p1,p2,0); returns (N, x, clauses, top)."""
    N = 1 + sum(p)
    idx = {e: i for i, e in enumerate(combinations(range(N), 2))}

    def x(i, j, c):
        a, b = (i, j) if i < j else (j, i)
        return 4 * idx[(a, b)] + c + 1

    cls = []
    for (i, j) in idx:
        cls.append([x(i, j, c) for c in range(4)])
        for c in range(4):
            for d in range(c + 1, 4):
                cls.append([-x(i, j, c), -x(i, j, d)])
    for (i, j) in idx:
        for k in range(j + 1, N):
            for c in range(4):
                cls.append([-x(i, j, c), -x(i, k, c), -x(j, k, c)])
    top = 4 * len(idx)
    for c in range(4):
        lits = [x(0, j, c) for j in range(1, N)]
        if p[c] == 0:
            cls.extend([-lit] for lit in lits)
            continue
        from pysat.card import CardEnc
        enc = CardEnc.atleast(lits, bound=p[c], top_id=top)
        top = max(top, enc.nv)
        cls.extend(enc.clauses)
        if p[c] < len(lits):
            enc = CardEnc.atmost(lits, bound=p[c], top_id=top)
            top = max(top, enc.nv)
            cls.extend(enc.clauses)
    return N, x, cls, top


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("p", type=int, nargs=3, help="the three largest colour-degrees")
    ap.add_argument("--cnf", help="write the instance here (DIMACS)")
    ap.add_argument("--check", help="verify this colouring (first line 'N 4', then N rows)")
    a = ap.parse_args()
    p = list(a.p) + [0]
    N, x, cls, top = build(p)
    print("core C%s: N=%d vars=%d clauses=%d" % (tuple(p), N, top, len(cls)))
    if a.cnf:
        with open(a.cnf, "w") as fh:
            fh.write("p cnf %d %d\n" % (top, len(cls)))
            for c in cls:
                fh.write(" ".join(map(str, c)) + " 0\n")
        print("wrote", a.cnf)
    if not a.check:
        return 0
    tok = open(a.check).read().split()
    n, k = int(tok[0]), int(tok[1])
    M = [list(map(int, tok[2 + i * n:2 + (i + 1) * n])) for i in range(n)]
    if n != N:
        print("check: file has %d vertices, core needs %d" % (n, N))
        return 1
    model = {x(i, j, c) for i in range(N) for j in range(i + 1, N) for c in range(4)
             if M[i][j] == c}
    edge_top = 4 * (N * (N - 1) // 2)
    pure = [c for c in cls if max(abs(l) for l in c) <= edge_top]
    bad = [c for c in pure if not any((l in model) if l > 0 else (-l not in model) for l in c)]
    deg = [sum(1 for j in range(1, N) if M[0][j] == c) for c in range(4)]
    print("check: %d of %d edge clauses violated; degrees of vertex 0 = %s, want %s"
          % (len(bad), len(pure), deg, p))
    return 0 if not bad and deg == p else 1


if __name__ == "__main__":
    sys.exit(main())
