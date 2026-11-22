#!/usr/bin/env python3
"""mkarmlist.py -- write the 332-element arm alphabet of the (15,14,14,14)
branch as a plain text table.

Each line is:  <index> <e0> <e1> <e2> <g6 of colour-0 graph> <g6 of colour-1 graph>
on 14 vertices; the colour-2 graph is the complement of their union.  Colours are
labelled as in the branch (colour 0 = the critical colour of the profile, the
other two = the branch's colours 2 and 3), and the list is taken modulo the
colour-2 <-> colour-3 swap, which the profile allows.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arm import canon_form, SWAP, to_g6

n = 14
d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'classes_sat14.json')))
reps = d['reps']


def swap(m):
    return [[-1 if m[i][j] < 0 else SWAP[m[i][j]] for j in range(n)] for i in range(n)]


def g6_of(m, c):
    a = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j and m[i][j] == c:
                a[i] |= 1 << j
    return to_g6(a)


orbs = {}
for m in reps:
    cf = canon_form(n, m)
    cf2 = canon_form(n, swap(m))
    key = min(cf, cf2)
    if key not in orbs:
        # canonical representative: prefer the one whose canonical form is
        # lexicographically smaller, so the table is deterministic
        orbs[key] = m if cf <= cf2 else swap(m)

rows = []
for key in sorted(orbs):
    m = orbs[key]
    e = [0, 0, 0]
    for i in range(n):
        for j in range(i + 1, n):
            e[m[i][j]] += 1
    rows.append((e[0], e[1], e[2], g6_of(m, 0), g6_of(m, 1)))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'armtypes14.txt')
with open(out, 'w') as fh:
    fh.write('# triangle-free 3-edge-colourings of K_14 up to vertex permutation and\n')
    fh.write('# the colour swap 2<->3: %d types (the arm alphabet of the branch)\n' % len(rows))
    fh.write('# columns: index e0 e1 e2 graph6(colour 0) graph6(colour 1); colour 2 = rest\n')
    for k, r in enumerate(rows):
        fh.write('%3d %2d %2d %2d %s %s\n' % (k, r[0], r[1], r[2], r[3], r[4]))
print('wrote %s with %d types' % (out, len(rows)))
