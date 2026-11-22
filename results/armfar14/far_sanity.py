#!/usr/bin/env python3
"""Sanity check of the frozen-X encoder on the satisfiable side: at 4 far points
some (indeed most) X admit a model.  Every model is decoded and re-checked.

If the encoder were over-constrained in the way that kills the 5-far instances,
it would show up as an unexplained UNSAT here too.
"""
import itertools
import subprocess
import sys

from pysat.solvers import Cadical153

from far_certify import build, load, T, U, nX


def main():
    nZ = 4
    N = nX + nZ
    sat = unsat = 0
    verified = 0
    for path in (T, U):
        n, M = load(path)
        for (a, b) in itertools.combinations(range(n), 2):
            keep = [t for t in range(n) if t not in (a, b)]
            pool, cls = build(keep, M, nZ)
            with Cadical153(bootstrap_with=cls) as s:
                if not s.solve():
                    unsat += 1
                    continue
                sat += 1
                val = {abs(x): x > 0 for x in s.get_model()}
            M2 = [[0] * N for _ in range(N)]
            for (i, j, c), lit in pool.items():
                if val.get(lit):
                    M2[i][j] = M2[j][i] = c
            # independent re-check
            mono = sum(1 for i in range(N) for j in range(i + 1, N)
                       for l in range(j + 1, N) if M2[i][j] == M2[i][l] == M2[j][l])
            inside = any(M2[i][j] == 0 for i in range(nX) for j in range(i + 1, nX))
            far = [y for y in range(nX, N) if all(M2[y][x] != 0 for x in range(nX))]
            ok = mono == 0 and not inside and len(far) == nZ
            if ok:
                verified += 1
            else:
                print(f"FAIL {path} del({a},{b}): mono={mono} inside0={inside} "
                      f"far={len(far)}")
    print(f"nZ={nZ}: SAT {sat}, UNSAT {unsat}, models re-checked OK {verified}")
    return 0 if verified == sat and sat > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
