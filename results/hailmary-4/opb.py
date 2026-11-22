#!/usr/bin/env python3
"""Encode a cover case as a pseudo-Boolean problem (.opb) for RoundingSat.

The host CNF is: one colour per edge (pairwise at-most-one plus a 4-clause) and
4 clauses per triangle.  The PB form is strictly better shaped for these
formulas: 'exactly one of four' becomes ONE equality constraint per edge instead
of six clauses, and the triangle clauses become >=1 constraints over negated
literals.  No re-encoding, no auxiliary variables.
"""
import sys
sys.path.insert(0, '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwp3xc7p/m3/w/k58-solver/k58')
from itertools import combinations
from joint_plan import cases
from gluing import host, units
from dense import marked_threshold

ORDER = 58

def build(profile, idx, tier='first'):
    it = cases(tuple(int(x) for x in profile))
    for k, (f, pl, i, ch) in enumerate(it):
        if k == idx:
            break
    else:
        raise SystemExit('no such case')
    lit, _ = host(ORDER)
    fixed = units(f, pl)
    us = sorted({c[0] for c in fixed if isinstance(c, (list, tuple)) and len(c) == 1})
    extra = [c for c in fixed if not (isinstance(c, (list, tuple)) and len(c) == 1)]
    if tier == 'retry':
        extra = extra + marked_threshold(f, fixed, ch, True, True, True)
    return f, lit, us, extra

def opb(profile, idx, path, tier='first'):
    f, lit, us, extra = build(profile, idx, tier)
    nv = 4 * len(list(combinations(range(ORDER), 2)))
    lines = []
    for e_i, (u, v) in enumerate(combinations(range(ORDER), 2)):
        lits = [4 * e_i + 1 + c for c in range(4)]
        lines.append(' '.join('+1 x%d' % x for x in lits) + ' = 1 ;')
    for u, v, w in combinations(range(ORDER), 3):
        for c in range(4):
            lines.append('+1 ~x%d +1 ~x%d +1 ~x%d >= 1 ;' % (lit(u, v, c), lit(u, w, c), lit(v, w, c)))
    def term(l):
        return ('+1 x%d' % l) if l > 0 else ('+1 ~x%d' % (-l))
    for x in us:
        lines.append(term(x) + ' >= 1 ;')
    for cl in extra:
        lines.append(' '.join(term(l) for l in cl) + ' >= 1 ;')
    with open(path, 'w') as fh:
        fh.write('* #variable= %d #constraint= %d\n' % (nv, len(lines)))
        fh.write('\n'.join(lines))
        fh.write('\n')
    return nv, len(lines)

if __name__ == '__main__':
    profile, idx, path = sys.argv[1].split(','), int(sys.argv[2]), sys.argv[3]
    tier = sys.argv[4] if len(sys.argv) > 4 else 'first'
    nv, nc = opb(profile, idx, path, tier)
    print('wrote', path, 'vars', nv, 'constraints', nc)
