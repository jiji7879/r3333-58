"""The frozen row CNF with EXACT criticality guards and an exact root-ticket cell.

For a row (family, placement, charge) of profile p summing to 57:

  vertex 0 is the root r, and the pinned units fix col(r, x) for all x, so
  arm(x) = the root colour of x and A_c = {x : arm(x) = c} with |A_c| = p[c].

  d_c(x) = 1 + (#pinned colour-c neighbours of x outside A_c)
             + (#free colour-c neighbours of x outside A_c)      for x in A_c,
  because x is colour-c adjacent to r and to no other point of A_c (a
  c-monochromatic triangle through r is forbidden by the host clauses).
  Hence  g_x <-> (d_{arm(x)}(x) >= 15) <-> (free count >= 14 - pinned count).

With g_x exact for all 57 arm points,

  w(r) = sum of the pinned class sizes >= 15            (a constant of the row)
  H(r) = #{x : x sends a ticket to r} = sum_x g_x       (definition, K58.Basic)

so the three cells  sum g >= w+1, sum g = w, sum g <= w-1  are an exhaustive
disjunction, and each cell strictly implies the row.

Also re-imposed (as consequences of the row's charge threshold, not as
assumptions): at least `charge` critical points in the marked arm, and at
least 2*critical_mass - 57 critical points in the critical arms, matching
dense.marked_threshold(total_critical=True).
"""
import gzip
import json
import os
import sys

REPO = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo'
sys.path.insert(0, REPO + '/.scratch/k58')
from gluing import Family, host, units          # noqa: E402
from gadgets import atmost, atleast, exactly, exact_guard   # noqa: E402

LEDGER = REPO + '/.scratch/k58/case-ledger.jsonl.gz'
ORDER = 58


def family_of(d):
    f = d['family']
    return Family(tuple(f['profile']), tuple(f['root_kinds']), f['arm'],
                  f['mark_position'], f['marked_size'], f['marked_kind'],
                  f['root_position'])


def row(rid):
    for line in gzip.open(LEDGER, 'rt'):
        d = json.loads(line)
        if d['id'] == rid:
            return d
    raise SystemExit('row %s not found' % rid)


def arms_of(family):
    out, start = {}, 1
    for c, size in enumerate(family.profile):
        out[c] = tuple(range(start, start + size))
        start += size
    return out


def build(rid, cell=None):
    """cell: None | 'strict' (H>=w+1) | 'exact' (H=w) | 'deficient' (H<=w-1)."""
    d = row(rid)
    f = family_of(d)
    lit, base = host(ORDER)
    fixed = units(f, tuple(d['placement']))
    clauses = [list(c) for c in base] + [list(c) for c in fixed]
    arms = arms_of(f)
    pos = {c[0] for c in fixed if len(c) == 1 and c[0] > 0}
    known = {(l - 1) // 4 for l in pos}          # edge already pinned
    top = 4 * (ORDER * (ORDER - 1) // 2)
    guards, always = {}, []                      # always = vertices pinned critical
    for x in range(1, ORDER):
        c = next(c for c, blk in arms.items() if x in blk)
        cand, pinned = [], 0
        for y in range(ORDER):
            if y == 0 or y == x or y in arms[c]:
                continue                          # r counted separately; in-arm gives 0
            e = lit(x, y, c)
            if e in pos:
                pinned += 1
            elif (e - 1) // 4 not in known:
                cand.append(e)
        needed = 14 - pinned
        if needed <= 0:
            always.append(x)
        else:
            top += 1
            g = top
            guards[x] = (g, c, needed, tuple(cand))
            cs, top = exact_guard(cand, needed, top, g)
            clauses.extend(cs)
    w = sum(size for size in f.profile if size >= 15)
    crit_arms = [x for x in range(1, ORDER)
                 if f.profile[next(c for c, blk in arms.items() if x in blk)] >= 15]
    # consequences of the row's charge threshold, re-imposed through exact guards
    extra_bounds = []
    marked = [guards[x][0] for x in arms[f.arm] if x in guards]
    if d['charge'] - 0 > 0:
        extra_bounds.append((marked, d['charge'], len(arms[f.arm])))
    total_goal = 2 * w - 57
    if total_goal > 0:
        extra_bounds.append(([guards[x][0] for x in crit_arms if x in guards],
                             total_goal, len(crit_arms)))
    for lits, minimum, _ in extra_bounds:
        if minimum > len(lits):
            return None, d, f, w, None
        if minimum > 0:
            cs, top = atleast(lits, minimum, top)
            clauses.extend(cs)
    allg = [guards[x][0] for x in sorted(guards)]
    fixed_true = len(always)
    if cell is None:
        pass
    elif cell == 'strict':
        cs, top = atleast(allg, w + 1 - fixed_true, top)
        clauses.extend(cs)
    elif cell == 'exact':
        cs, top = exactly(allg, w - fixed_true, top)
        clauses.extend(cs)
    elif cell == 'deficient':
        cs, top = atmost(allg, w - 1 - fixed_true, top)
        clauses.extend(cs)
    else:
        raise SystemExit('bad cell %r' % cell)
    nv = max([top] + [abs(l) for cl in clauses for l in cl])
    return clauses, d, f, w, (nv, guards, always)


def write(rid, cell, path):
    clauses, d, f, w, meta = build(rid, cell)
    if clauses is None:
        print('row %s cell %s: pins already contradict the threshold' % (rid[:8], cell))
        return None
    nv, guards, always = meta
    with open(path, 'w') as fh:
        fh.write('p cnf %d %d\n' % (nv, len(clauses)))
        for c in clauses:
            fh.write(' '.join(map(str, c)) + ' 0\n')
    import hashlib
    h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    print('%-16s cell=%-9s clauses=%7d nv=%6d w=%2d guards=%2d pinned-critical=%2d sha256=%s'
          % (rid[:16], cell, len(clauses), nv, w, len(guards), len(always), h[:16]))
    return h


if __name__ == '__main__':
    rid = sys.argv[1]
    outdir = sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    for cell in (None, 'strict', 'exact', 'deficient'):
        name = 'row' if cell is None else cell
        write(rid, cell, os.path.join(outdir, '%s-%s.cnf' % (rid[:8], name)))
