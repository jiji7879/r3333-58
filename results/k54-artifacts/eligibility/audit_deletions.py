"""m3 / direction d8 -- independent check of the admissible-deletion bound.

README: "For each such row [the 104 admissible catalogue rows], enumerate its
four-point deletions whose complementary K10 can appear in one of the two
ordinary K15 templates.  The union of all admissible deletion sets has at most
eight vertices, and for H42 it is empty."  results/global.json records, per row,
the number of admissible deletions and the size of the union of their vertices.

This script, from data/r333_{14,15}.mc only:
  1. builds the set of isomorphism classes (vertex permutations only, colours
     kept as labels) of the 10-vertex restrictions of the two K15 rows, over all
     six colour permutations of the K15 colouring;
  2. for every catalogue row and every 10-vertex subset, records the complement
     four-set when that K10 falls in the set;
  3. compares the per-row deletion counts and union sizes with results/global.json
     and checks the two published bounds (union <= 8; empty for H42).
"""
import argparse
import json
import sys
from itertools import combinations, permutations

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from audit_k15 import decode, well_formed

REGULAR_EXCLUDED = {17, 19, 20, 22, 23, 24, 25, 40, 69, 70, 77}


def adjmasks(M, perm=None):
    n = len(M)
    out = []
    for v in range(n):
        row = [0, 0, 0]
        for u in range(n):
            if u != v:
                c = M[v][u]
                if perm is not None:
                    c = perm[c]
                row[c] |= 1 << u
        out.append(tuple(row))
    return out


def refine(adj, parts):
    while True:
        new = []
        for cell in parts:
            m = 0
            for v in cell:
                m |= 1 << v
            buckets = {}
            for v in cell:
                sig = tuple((adj[v][c] & m).bit_count() for c in range(3))
                buckets.setdefault(sig, []).append(v)
            for k in sorted(buckets):
                new.append(tuple(buckets[k]))
        new = tuple(new)
        if len(new) == len(parts):
            return new
        parts = new


def canon(M):
    """Canonical form of a small 3-coloured complete graph under vertex
    permutations (colour labels are kept).  Equitable refinement, then
    individualisation of a smallest non-singleton cell, minimum over leaves."""
    n = len(M)
    adj = adjmasks(M)
    best = [None]

    def rec(parts):
        parts = refine(adj, parts)
        big = [i for i, c in enumerate(parts) if len(c) > 1]
        if not big:
            order = [c[0] for c in parts]
            s = tuple(M[order[i]][order[j]] for i in range(n) for j in range(i + 1, n))
            if best[0] is None or s < best[0]:
                best[0] = s
            return
        k = min(big, key=lambda i: (len(parts[i]), i))
        cell = parts[k]
        for v in cell:
            nxt = parts[:k] + ((v,),) + (tuple(u for u in cell if u != v),) + parts[k + 1:]
            rec(tuple(c for c in nxt if c))

    rec((tuple(range(n)),))
    return best[0]


def degfilter(M):
    return tuple(sorted(tuple(row.count(c) for c in range(3)) for row in M))


def subset(M, keep):
    idx = list(keep)
    return [[M[a][b] for b in idx] for a in idx]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--archive', default=(
        '/workspace/nucleus/work/projects/'
        'p-764e12eeb9f34762ad544edb924f4680/repo/work/k54cut'))
    args = ap.parse_args()
    K = args.archive.rstrip('/') + '/'
    cat14 = [decode(s) for s in open(K + 'data/r333_14.mc').read().splitlines()]
    cat15 = [decode(s) for s in open(K + 'data/r333_15.mc').read().splitlines()]

    targets = {}
    for j, t in enumerate(cat15):
        for p in permutations(range(3)):
            for keep in combinations(range(15), 10):
                sub = subset(t, keep)
                targets.setdefault(canon(sub), (j, p, keep))
    print('K15 K10 classes (colours labelled):', len(targets))
    tgt_filter = {}
    for key, (j, p, keep) in targets.items():
        sub = subset(cat15[j], keep)
        tgt_filter.setdefault(degfilter(sub), []).append(key)
    print('distinct colour-degree filters among them:', len(tgt_filter))

    counts = {}
    unions = {}
    for r, M in enumerate(cat14, 1):
        masks = []
        for keep in combinations(range(14), 10):
            sub = subset(M, keep)
            f = degfilter(sub)
            if f not in tgt_filter:
                continue
            if canon(sub) in targets:
                mask = 0
                for v in range(14):
                    if v not in keep:
                        mask |= 1 << v
                masks.append(mask)
        counts[r] = len(masks)
        u = 0
        for m in masks:
            u |= m
        unions[r] = u.bit_count()

    stored = json.load(open(K + 'results/global.json'))
    regular = set(range(1, 116)) - REGULAR_EXCLUDED
    bad = 0
    for key, mine in (('admissible_deletions', counts),
                      ('deletion_union_sizes', unions)):
        theirs = {int(k): v for k, v in stored[key].items()}
        diff = {k: (theirs.get(k), mine.get(k)) for k in set(theirs) | set(mine)
                if (k in regular or k in theirs) and theirs.get(k) != mine.get(k)}
        print(key, 'mismatches:', len(diff), dict(list(diff.items())[:8]))
        bad += len(diff)
    print('rows covered by global.json:', len(stored['deletion_union_sizes']),
          'expected', len(regular))
    print('max union over the 104 admissible rows (mine):',
          max(unions[r] for r in regular))
    print('H42 (row 42) deletions:', counts[42], 'union:', unions[42])
    print('excluded 11 rows are exactly those with deletion union 14:',
          {r for r in range(1, 116) if unions[r] == 14} == REGULAR_EXCLUDED)
    over = [(r, unions[r]) for r in regular if unions[r] > 8]
    print('rows with union > 8:', over)
    # rows outside the 104 for information
    print('union sizes outside the 104:',
          {r: unions[r] for r in range(1, 116) if r not in regular and unions[r]})
    ok = bad == 0 and not over and counts[42] == 0
    json.dump(dict(counts=counts, unions=unions, mismatches=bad, ok=bool(ok)),
              open('deletions.json', 'w'), indent=1)
    print('RESULT:', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
