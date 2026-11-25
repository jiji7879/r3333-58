#!/usr/bin/env python3
"""Add the gap-four families A and B to a row CNF built by the campaign's encoder.

    python3 tools/gap4/add_families.py ROW.cnf OUT.cnf [--profile 15,15,15,12] [--arm 0]

The row CNF is DIMACS over `gluing.host(58)`'s edge literals: edge (u,v), u<v, colour c is
literal 4*index(u,v)+1+c.  The arm block of colour `arm` is the run of `profile[arm]`
vertices that starts at 1 + sum(profile[:arm]) (the root is 0); the other blocks are the
other runs.  With A0 = the arm block and A_c the block of colour c:

  A  |N_arm(a) cap A_c| <= 5 for every a in A0 and every other block c.
     For y != y' in that set, colour(y,y') is neither `arm` (else a,y,y' is monochromatic
     with a) nor c (else r,y,y' is), so the set is 2-coloured with no monochromatic
     triangle and has at most R(3,3)-1 = 5 vertices.

  B  flag_a -> |N_arm(a) cap A_c| >= 4, for every a in A0 and every other block c,
     where flag_a is a fresh variable defined by a sequential counter as
     "at least 14 vertices outside A0 are colour-`arm` neighbours of a", i.e. d_arm(a) >= 15.
     Proof: N_arm(a) is a triangle-free 3-coloured complete graph of order d_arm(a) <= 16
     (R(3,3,3) = 17), every colour degree in such a colouring is <= 5 (a class of 6 would be
     a triangle-free 2-colouring of K6) and the three colour degrees of r inside N_arm(a)
     sum to d_arm(a)-1 in {14,15}, so each is at least 4.

Both families are satisfied by every triangle-free 4-colouring realising the row, so the
output is a relaxation of the row: UNSAT transfers, SAT decides nothing.
"""
import itertools, sys

N = 58
PAIRS = list(itertools.combinations(range(N), 2))
IDX = {e: i for i, e in enumerate(PAIRS)}


def lit(u, v, c):
    u, v = min(u, v), max(u, v)
    return 4 * IDX[(u, v)] + 1 + c


def threshold(inputs, k, top, clauses):
    top += 1
    truth = top
    clauses.append([truth])
    prev = [truth] + [-truth] * k
    for x in inputs:
        new = [truth]
        for j in range(1, k + 1):
            top += 1
            a, b, p = prev[j], prev[j - 1], top
            clauses.extend([[-a, p], [-b, -x, p], [-p, a, b], [-p, a, x]])
            new.append(p)
        prev = new
    return prev[k], top


def blocks(profile):
    out, start = [], 1
    for d in profile:
        out.append(list(range(start, start + d)))
        start += d
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    profile = (15, 15, 15, 12)
    arm = 0
    for i, a in enumerate(sys.argv):
        if a == '--profile':
            profile = tuple(int(x) for x in sys.argv[i + 1].split(','))
        if a == '--arm':
            arm = int(sys.argv[i + 1])
    clauses, nv = [], 0
    with open(src) as f:
        head = f.readline().split()
        nv = int(head[2])
        for line in f:
            if line.strip():
                clauses.append([int(x) for x in line.split()[:-1]])
    base = len(clauses)
    B = blocks(profile)
    A0 = B[arm]
    outside = [v for v in range(1, N) if v not in A0]
    top = nv
    flags, counters = {}, []
    for a in A0:
        flags[a], top = threshold([lit(a, y, arm) for y in outside], 14, top, counters)
    clauses.extend(counters)
    addA = addB = 0
    for a in A0:
        for c, blk in enumerate(B):
            if c == arm:
                continue
            L = [lit(a, y, arm) for y in blk]
            for S in itertools.combinations(L, 6):
                clauses.append([-x for x in S]); addA += 1
            for S in itertools.combinations(L, len(L) - 3):
                clauses.append([-flags[a]] + list(S)); addB += 1
    with open(dst, 'w') as f:
        f.write('p cnf %d %d\n' % (top, len(clauses)))
        f.write(''.join(' '.join(map(str, c)) + ' 0\n' for c in clauses))
    print('%s -> %s: base %d, counters %d, A %d, B %d, vars %d, clauses %d'
          % (src, dst, base, len(counters), addA, addB, top, len(clauses)))


if __name__ == '__main__':
    main()
