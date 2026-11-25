"""m3 / direction d8 -- independent recomputation of the rooted-pair tally.

results/global.json reports the number of rooted template pairs per seed,
summing to 1,881,012.  A rooted template is a catalogue row together with a pole
and a named palette; two rooted templates are the same type when a colour-twisted
automorphism of the row carries one to the other.  A rooted pair is an unordered
pair of rooted types modulo the six global permutations of the ordinary colours.
Pairs are charged to the smaller of the two seeds, as the handoff does.

Everything is recomputed here from data/r333_14.mc and data/core-cover.json by
Burnside over the six global colour permutations.
"""
import argparse
import json
import sys
from itertools import permutations
from collections import Counter

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from audit_k15 import decode

REGULAR_EXCLUDED = {17, 19, 20, 22, 23, 24, 25, 40, 69, 70, 77}
PERMS = list(permutations(range(3)))


def twisted_autos(M):
    """All (f, rho) with M[f(u)][f(w)] == rho(M[u][w]) for all u != w."""
    n = len(M)
    degs = [tuple(row.count(c) for c in range(3)) for row in M]
    out = []
    for rho in PERMS:
        pinv = [0, 0, 0]
        for c in range(3):
            pinv[rho[c]] = c
        cand = [[v for v in range(n) if degs[v] == tuple(degs[u][pinv[c]] for c in range(3))]
                for u in range(n)]
        order = sorted(range(n), key=lambda u: (len(cand[u]), u))
        f = {}
        used = set()

        def rec(k):
            if k == n:
                out.append((tuple(f[u] for u in range(n)), rho))
                return
            u = order[k]
            for v in cand[u]:
                if v in used:
                    continue
                if all(M[v][f[u2]] == rho[M[u][u2]] for u2 in f):
                    f[u] = v
                    used.add(v)
                    rec(k + 1)
                    used.remove(v)
                    del f[u]

        rec(0)
    return out


def inv(p):
    q = [0, 0, 0]
    for i, c in enumerate(p):
        q[c] = i
    return tuple(q)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--archive', default=(
        '/workspace/nucleus/work/projects/'
        'p-764e12eeb9f34762ad544edb924f4680/repo/work/k54cut'))
    args = ap.parse_args()
    K = args.archive.rstrip('/') + '/'
    cat14 = [decode(s) for s in open(K + 'data/r333_14.mc').read().splitlines()]
    core = json.load(open(K + 'data/core-cover.json'))
    seeds = [row[1] for row in core]
    assert len(seeds) == 115
    regular = sorted(set(range(1, 116)) - REGULAR_EXCLUDED)

    types = []          # (row, pole, palette)
    classid = {}        # every (row, pole, palette) -> index of its type
    aut_sizes = {}
    for r in regular:
        M = cat14[r - 1]
        aut = twisted_autos(M)
        aut_sizes[r] = len(aut)
        # orbits of (pole, palette) under (v,p) -> (f(v), p o rho^{-1})
        seen = set()
        for v in range(14):
            for p in PERMS:
                if (v, p) in seen:
                    continue
                orbit = {(v, p)}
                frontier = [(v, p)]
                while frontier:
                    vv, pp = frontier.pop()
                    for f, rho in aut:
                        q = inv(rho)
                        nxt = (f[vv], tuple(pp[c] for c in q))
                        if nxt not in orbit:
                            orbit.add(nxt)
                            frontier.append(nxt)
                seen |= orbit
                for t in orbit:
                    classid[(r, t[0], t[1])] = len(types)
                types.append((r, v, p))
    print('automorphism sizes:', Counter(aut_sizes.values()))
    print('rooted types:', len(types), 'over', len(regular), 'rows')
    tid = classid
    assert len(tid) == len(types) * 1 or len(tid) >= len(types)
    assert len(set(tid.values())) == len(types)
    seed_of = [seeds[r - 1] for r, _, _ in types]

    tallies = Counter()
    for g in PERMS:
        perm = [tid[(r, v, tuple(g[c] for c in p))] for r, v, p in types]
        fixed = Counter(seed_of[i] for i, k in enumerate(perm) if i == k)
        for a in fixed:
            tallies[a] += fixed[a] * (fixed[a] + 1) // 2
            for b in fixed:
                if a < b:
                    tallies[a] += fixed[a] * fixed[b]
        for i, j in enumerate(perm):
            if i < j and perm[j] == i:
                tallies[min(seed_of[i], seed_of[j])] += 1
    assert all(v % 6 == 0 for v in tallies.values()), tallies
    scope = {s: tallies[s] // 6 for s in range(1, 13)}
    total = sum(scope.values())
    stored = json.load(open(K + 'results/global.json'))['rooted_pairs_by_seed']
    stored = {int(k): v for k, v in stored.items()}
    print('mine  :', scope, 'total', total)
    print('stored:', stored, 'total',
          json.load(open(K + 'results/global.json'))['total_rooted_pairs'])
    diff = {s: (stored.get(s), scope.get(s)) for s in set(stored) | set(scope)
            if stored.get(s) != scope.get(s)}
    print('mismatches:', diff)
    ok = not diff and total == 1881012
    json.dump(dict(scope=scope, total=total, types=len(types), mismatches=diff,
                   ok=bool(ok)), open('scope.json', 'w'), indent=1)
    print('RESULT:', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
