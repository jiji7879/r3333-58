#!/usr/bin/env python3
"""Validation of the case split on a real object.

The sharpness witness far18.col has a 14-point colour-0-free X with a far point,
so by the reduction of PROOF.md §3 its X must be isomorphic (as a 3-coloured graph
on the three ordinary colours, up to a permutation of those three colours) to
(U or T) minus two points.  If it were not, the case split would be incomplete.

Iso test: per-vertex invariant (sorted colour-degree triple + sorted multiset of
incident colours), then backtracking with consistency pruning.
"""
import itertools
import sys

from far_certify import load, T, U, nX

NC = 3


def restrict(M, keep, off):
    """3-coloured matrix on keep, colours mapped c -> c - off, diagonal = -1."""
    n = len(keep)
    return [[-1 if a == b else M[keep[a]][keep[b]] - off for b in range(n)]
            for a in range(n)]


def signature(A, i):
    n = len(A)
    degs = tuple(sorted(sum(1 for j in range(n) if j != i and A[i][j] == c)
                        for c in range(NC)))
    cols = tuple(sorted(A[i][j] for j in range(n) if j != i))
    return (degs, cols)


def iso(A, B):
    n = len(A)
    if n != len(B):
        return False
    sigA = [signature(A, i) for i in range(n)]
    sigB = [signature(B, j) for j in range(n)]
    if sorted(sigA) != sorted(sigB):
        return False
    order = sorted(range(n),
                   key=lambda i: -sum(1 for j in range(n) if sigB[j] == sigA[i]))
    mapping = {}

    def rec(t):
        if t == n:
            return True
        i = order[t]
        for j in range(n):
            if j in mapping.values() or sigB[j] != sigA[i]:
                continue
            if all(A[i][i2] == B[j][j2] for i2, j2 in mapping.items()):
                mapping[i] = j
                if rec(t + 1):
                    return True
                del mapping[i]
        return False
    return rec(0)


def main():
    rows = [r.split() for r in open('far18.col').read().split('\n')[1:] if r.strip()]
    M = [[int(x) for x in r] for r in rows]
    base = [[-1 if i == j else M[i][j] - 1 for j in range(nX)] for i in range(nX)]
    found = []
    perms = list(itertools.permutations(range(NC)))
    for path, tag in ((U, 'U'), (T, 'T')):
        n, MM = load(path)
        for (a, b) in itertools.combinations(range(n), 2):
            keep = [v for v in range(n) if v not in (a, b)]
            B = restrict(MM, keep, 0)
            for perm in perms:
                A = [[-1 if i == j else perm[base[i][j]] for j in range(nX)]
                     for i in range(nX)]
                if iso(A, B):
                    found.append(f"{tag} minus ({a},{b}) colour-perm {perm}")
                    break
    print("X of far18.col is isomorphic to:")
    for f in found:
        print("   ", f)
    if not found:
        print("    NONE -- case split incomplete!")
    return 0 if found else 1


if __name__ == '__main__':
    sys.exit(main())
