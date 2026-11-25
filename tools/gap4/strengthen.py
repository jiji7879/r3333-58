#!/usr/bin/env python3
"""Add three implied constraint families to a GAP-FOUR pilot CNF.

WARNING: the arm partition is hard-coded to profile (15,15,15,12), arm 0
(A0 = 1..15, A1 = 16..30, A2 = 31..45, A3 = 46..57).  It is UNSOUND on any other
profile -- in particular on the nine (15,14,14,14) charge-15 rows.  For any other
profile use add_families.py, which takes --profile and --arm.

    python3 tools/gap4/strengthen.py PILOT.cnf OUT.cnf [--families ABC]

A "gap-four" row has profile (15,15,15,12), arm 0, charge 11; its pilot CNF (built by
the bundle's campaign/gap_four.py) is

    host(58) + units(family, placement) + "at least 11 of the 15 arm vertices a
    have >= 14 colour-0 neighbours among the 42 vertices outside the arm".

Write A0 = 1..15, A1 = 16..30, A2 = 31..45, A3 = 46..57, x_c(a) = #{y in A_c :
colour(a,y) = 0}, m(y) = #{a in A0 : colour(a,y) = 0}.  The three families below are
implied by ANY triangle-free 4-colouring of K58 realising the row, so adding them keeps
the formula a relaxation of the row and UNSAT still transfers:

  A  x_c(a) <= 5 for every a in A0, c in {1,2,3}.
     S = N_0(a) cap A_c: for y != y' in S, colour(y,y') is neither 0 (else a,y,y' is
     monochromatic) nor c (else r,y,y' is), so S is 2-coloured with no monochromatic
     triangle and |S| <= R(3,3)-1 = 5.

  B  flag_a -> x_c(a) >= 4 for every a in A0, c in {1,2,3}.
     flag_a says d_0(a) >= 15.  N_0(a) has all internal colours in {1,2,3} and no
     monochromatic triangle, so it is a triangle-free 3-coloured K_15 or K_16: any
     3-colouring of K17 has a monochromatic triangle, so d_0(a) <= 16.  In such a
     colouring every colour degree is <= 5 (a colour class of size 6 would be a
     triangle-free 2-colouring of K6), and the three colour degrees sum to 14 or 15,
     hence each is at least 4.  The vertex r has colour-c degree x_c(a) inside N_0(a).

  C  m(y) <= 12 for every y in A1 u A2.
     d_0(y) = m(y) + (colour-0 degree of y inside its own arm) + (colours 0 to the
     other arms) and d_0(y) <= 16.  The arm carries a T/U template whose three colour
     classes have degrees 4 and 5, so the in-arm colour-0 degree of y is 4 or 5.

Family A and C are encoded as the standard at-most clauses, B as at-least clauses
conditioned on the flag literal.
"""
import itertools, sys

N = 58
PROFILE = (15, 15, 15, 12)
A0 = list(range(1, 16))
ARMS = [list(range(16, 31)), list(range(31, 46)), list(range(46, 58))]
IDX = {(u, v): i for i, (u, v) in enumerate(itertools.combinations(range(N), 2))}


def lit(u, v, c):
    u, v = min(u, v), max(u, v)
    return 4 * IDX[(u, v)] + 1 + c


def threshold(inputs, k, top, clauses):
    """The sequential counter used by the bundle's campaign/gap_four.py."""
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


def flag_vars():
    """Variable number of flag_a for a in A0, rebuilt exactly as gap_four.py builds it."""
    top = 4 * N * (N - 1) // 2
    extra, flags = [], {}
    for a in A0:
        flags[a], top = threshold([lit(a, x, 0) for x in range(16, 58)], 14, top, extra)
    return flags


def main():
    src, dst = sys.argv[1], sys.argv[2]
    families = 'ABC'
    if '--families' in sys.argv:
        families = sys.argv[sys.argv.index('--families') + 1]
    clauses, nv = [], 0
    with open(src) as f:
        head = f.readline().split()
        nv = int(head[2])
        for line in f:
            if line.strip():
                clauses.append([int(x) for x in line.split()[:-1]])
    base = len(clauses)
    flags = flag_vars()
    assert max(flags.values()) <= nv, 'flag variable outside the pilot header'
    added = {'A': 0, 'B': 0, 'C': 0}
    if 'A' in families:
        for a in A0:
            for arm in ARMS:
                for S in itertools.combinations([lit(a, y, 0) for y in arm], 6):
                    clauses.append([-x for x in S]); added['A'] += 1
    if 'B' in families:
        for a in A0:
            for arm in ARMS:
                L = [lit(a, y, 0) for y in arm]
                for S in itertools.combinations(L, len(L) - 3):
                    clauses.append([-flags[a]] + list(S)); added['B'] += 1
    if 'C' in families:
        for y in ARMS[0] + ARMS[1]:
            for S in itertools.combinations([lit(a, y, 0) for a in A0], 13):
                clauses.append([-x for x in S]); added['C'] += 1
    with open(dst, 'w') as f:
        f.write('p cnf %d %d\n' % (nv, len(clauses)))
        f.write(''.join(' '.join(map(str, c)) + ' 0\n' for c in clauses))
    print('%s -> %s: base %d, A %d, B %d, C %d, total %d'
          % (src, dst, base, added['A'], added['B'], added['C'], len(clauses)))


if __name__ == '__main__':
    main()
