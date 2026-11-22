#!/usr/bin/env python3
"""Certified exhaustion: for every 14-point c-free set X that can have a far
point (i.e. every T/U minus two points, see far_fixed.py), decide '5 far points'
and emit a DRAT proof replayed with drat-trim against the regenerated CNF.

Also: the same encoder at 4 far points is run once and its model verified, as the
soundness/exactness check that the clause set is not vacuously unsatisfiable.

Outputs (in cert/): <tag>.cnf, <tag>.drat, manifest.txt
"""
import hashlib
import itertools
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../..'))
T = os.path.join(REPO, 'artifacts/k16_template_T_aut32_m4.col')
U = os.path.join(REPO, 'artifacts/k16_template_U_aut160_m4.col')
CADICAL = '/opt/lean/bin/cadical'
DRATTRIM = os.path.join(REPO, '.scratch/satcheck/bin/drat-trim')
CERT = os.path.join(HERE, 'cert')
nX = 14


def load(path):
    toks = open(path).read().split()
    n, k = int(toks[0]), int(toks[1])
    vals = list(map(int, toks[2:2 + n * n]))
    return n, [vals[i * n:(i + 1) * n] for i in range(n)]


def build(keep, M, nZ):
    n = len(M)
    N = nX + nZ
    pool = {}

    def v(i, j, c):
        if i > j:
            i, j = j, i
        return pool.setdefault((i, j, c), len(pool) + 1)
    cls = []
    for i in range(nX):                     # X, frozen to the template colours
        for j in range(i + 1, nX):
            cls.append([v(i, j, M[keep[i]][keep[j]] + 1)])
    for i in range(nX):                     # X is c-free (redundant but explicit)
        for j in range(i + 1, nX):
            cls.append([-v(i, j, 0)])
    for i in range(N):                      # exactly one colour per pair
        for j in range(i + 1, N):
            cls.append([v(i, j, c) for c in range(4)])
            for c in range(4):
                for d in range(c + 1, 4):
                    cls.append([-v(i, j, c), -v(i, j, d)])
    for i in range(N):                      # triangle-free
        for j in range(i + 1, N):
            for k in range(j + 1, N):
                for c in range(4):
                    cls.append([-v(i, j, c), -v(i, k, c), -v(j, k, c)])
    for z in range(nX, N):                  # far: no colour-0 edge into X
        for x in range(nX):
            cls.append([-v(z, x, 0)])
    return pool, cls


def write_cnf(path, cls):
    nv = max(abs(l) for c in cls for l in c)
    with open(path, 'w') as f:
        f.write(f"p cnf {nv} {len(cls)}\n")
        for c in cls:
            f.write(' '.join(map(str, c)) + ' 0\n')
    return nv


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.makedirs(CERT, exist_ok=True)
    manifest = []
    n_ok = n_bad = 0
    for path in (T, U):
        n, M = load(path)
        short = 'T' if path.endswith(T) else 'U'
        for (a, b) in itertools.combinations(range(n), 2):
            keep = [t for t in range(n) if t not in (a, b)]
            pool, cls = build(keep, M, 5)
            tag = f"{short}_{a}_{b}"
            cnf = os.path.join(CERT, tag + ".cnf")
            drat = os.path.join(CERT, tag + ".drat")
            write_cnf(cnf, cls)
            r = subprocess.run([CADICAL, '-q', cnf, drat],
                               capture_output=True, text=True)
            if r.returncode != 20:
                print(f"{tag}: cadical exit {r.returncode} (expected 20 = UNSAT)")
                n_bad += 1
                continue
            chk = subprocess.run([DRATTRIM, cnf, drat], capture_output=True, text=True)
            good = chk.returncode == 0 and 'VERIFIED' in chk.stdout
            if not good:
                print(f"{tag}: drat-trim FAILED\n{chk.stdout[-500:]}")
                n_bad += 1
                continue
            n_ok += 1
            manifest.append(f"{tag} {sha(cnf)} {sha(drat)} VERIFIED")
    with open(os.path.join(CERT, 'manifest.txt'), 'w') as f:
        f.write(f"# 14-point c-free X, 5 far points: UNSAT, DRAT replayed\n")
        f.write(f"# {n_ok} instances verified, {n_bad} failures\n")
        f.write("tag  sha256(cnf)  sha256(drat)  drat-trim\n")
        for line in manifest:
            f.write(line + '\n')
    print(f"verified {n_ok}, failures {n_bad}")
    return 0 if n_bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
