#!/usr/bin/env python3
"""Structural guard for far_aug.py.

The additions A1-A3 are claimed sound, so they must not change the answer of any
instance they are added to.  The only check with teeth is a *satisfiable* one:
with the same code and nZ = 4 (where the base is satisfiable) the augmented
instance must still be SAT, and the model must be a genuine colouring.

Also evaluates every generated clause on genuine nZ = 4 models: a clause that a
genuine model falsifies is unsound, whether or not the solver notices.
"""
import itertools
import sys

from pysat.solvers import Cadical153

from far_aug import build, nX


def model_of(s):
    return {abs(x): x > 0 for x in s.get_model()}


def verify(model, pool, nZ):
    N = nX + nZ
    g = [[None] * N for _ in range(N)]
    for (i, j, c), lit in pool.items():
        if model.get(lit):
            g[i][j] = g[j][i] = c
    for i in range(N):
        for j in range(N):
            if i != j and g[i][j] is None:
                return f"edge {i}{j} uncoloured"
    mono = [(i, j, k) for i in range(N) for j in range(i + 1, N)
            for k in range(j + 1, N) if g[i][j] == g[i][k] == g[j][k]]
    if mono:
        return f"monochromatic triangles {mono[:3]}"
    if any(g[i][j] == 0 for i in range(nX) for j in range(i + 1, nX)):
        return "colour 0 inside X"
    far = [y for y in range(nX, N) if all(g[y][x] != 0 for x in range(nX))]
    if len(far) != nZ:
        return f"{len(far)} far points, expected {nZ}"
    return None


def main():
    nZ = 4
    for additions in (False, True):
        pool, cls = build(nZ, additions)
        with Cadical153(bootstrap_with=cls) as s:
            sat = s.solve()
            if not sat:
                print(f"nZ={nZ} additions={additions}: UNSAT  <-- WRONG, "
                      f"the base is satisfiable here")
                return 1
            m = model_of(s)
        err = verify(m, pool, nZ)
        print(f"nZ={nZ} additions={additions}: SAT, clauses={len(cls)}, "
              f"model check: {err or 'OK'}")
        if err:
            return 1
        # evaluate every clause on this model
        bad = [c for c in cls if not any(m.get(abs(l), False) == (l > 0) for l in c)]
        print(f"   clauses falsified by the model: {len(bad)}")
        if bad:
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
