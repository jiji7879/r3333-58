"""m3 / direction d5 -- completeness of the 24 rooted H42 placements.

The published mark count 59,925 is the sum, over data/placements.json, of the
number of rectangle orbits of each placement.  That total is only the count of
*all* marked cases if the 24 placements are exactly the equivalence classes of
rooted H42 placements.  This script recomputes those classes from h42.json:

a rooted placement is (p_A, c_A, p_B, c_B): pole and palette of each template,
with the template colouring c o H.  Two rooted placements are equivalent when
some global permutation of the three ordinary colours, some pair of template
relabellings (each of which may itself be twisted by a colour permutation that
the global one then cancels), or the exchange of the two templates carries one
to the other.

Writes placement_classes.json.  Exit status 0 iff the stored list is exactly one
representative per class and the classes number 24.
"""
import argparse
import json
import sys
from itertools import permutations

sys.path.insert(0, __file__.rsplit('/', 1)[0])
import audit_lib as A

DEFAULT = ('/workspace/nucleus/work/projects/'
           'p-764e12eeb9f34762ad544edb924f4680/repo/work/k54cut')
ORDINARY = list(permutations(range(3)))


def twisted_automorphisms(H):
    """All (f, rho) with H[f(u)][f(w)] == rho(H[u][w]) for all u != w."""
    out = []
    degs = [tuple(sum(H[u][v] == c for v in range(14)) for c in range(3)) for u in range(14)]
    for rho in ORDINARY:
        want = [tuple(degs[u][rho.index(c)] for c in range(3)) for u in range(14)]
        cand = [tuple(v for v in range(14) if degs[v] == want[u]) for u in range(14)]
        order = sorted(range(14), key=lambda u: (len(cand[u]), u))
        f = {}
        used = set()

        def rec(i):
            if i == 14:
                out.append((tuple(f[u] for u in range(14)), rho))
                return
            u = order[i]
            for v in cand[u]:
                if v in used:
                    continue
                if all(H[v][f[u2]] == rho[H[u][u2]] for u2 in f):
                    f[u] = v
                    used.add(v)
                    rec(i + 1)
                    used.remove(v)
                    del f[u]

        rec(0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--archive', default=DEFAULT)
    args = ap.parse_args()
    K = args.archive.rstrip('/') + '/'
    H = A.load_h42(K + 'data/h42.json')
    A.degenerate(H)
    pls = json.load(open(K + 'data/placements.json'))

    aut = twisted_automorphisms(H)
    print('colour-permuting automorphisms of H42:', len(aut))
    # vertex classes
    parent = list(range(14))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for f, _ in aut:
        for u in range(14):
            a, b = find(u), find(f[u])
            if a != b:
                parent[a] = b
    classes = {}
    for u in range(14):
        classes.setdefault(find(u), []).append(u)
    reps = sorted(min(v) for v in classes.values())
    print('vertex classes:', sorted(classes.values()), 'representatives', reps)
    for p in (0, 2, 4):
        assert p in reps, p

    # generators on states (pa, ca, pb, cb)
    def state_key(s):
        return tuple([s[0], tuple(s[1]), s[2], tuple(s[3])])

    def orbit(s):
        s = (s[0], tuple(s[1]), s[2], tuple(s[3]))
        seen = {s}
        frontier = [s]
        while frontier:
            pa, ca, pb, cb = frontier.pop()
            nxt = []
            for f, rho in aut:
                finv = [0] * 14
                for u, v in enumerate(f):
                    finv[v] = u
                # relabel side A: colouring ca o rho^{-1} o H at pole finv(pa)
                nca = tuple(ca[rho.index(c)] for c in range(3))
                nxt.append((finv[pa], nca, pb, cb))
                ncb = tuple(cb[rho.index(c)] for c in range(3))
                nxt.append((pa, ca, finv[pb], ncb))
            for pi in ORDINARY:
                nxt.append((pa, tuple(pi[ca[c]] for c in range(3)),
                            pb, tuple(pi[cb[c]] for c in range(3))))
            nxt.append((pb, cb, pa, ca))
            for t in nxt:
                if t not in seen:
                    seen.add(t)
                    frontier.append(t)
        return seen

    allstates = [(pa, ca, pb, cb) for pa in reps for ca in ORDINARY
                 for pb in reps for cb in ORDINARY]
    print('raw rooted placements over the representative poles:', len(allstates))
    seen = set()
    allorbits = []
    for s in allstates:
        if s in seen:
            continue
        ob = orbit(s)
        assert not (ob & seen)
        seen |= ob
        allorbits.append(sorted(ob))
    print('equivalence classes:', len(allorbits))
    for ob in allorbits:
        ob_reps = [t for t in ob if t[0] in reps and t[2] in reps]
        print('  class size', len(ob), 'reps among representative poles:', ob_reps[:6],
              '...' if len(ob_reps) > 6 else '')

    stored = [(pl['a'][0], tuple(pl['a'][1]), pl['b'][0], tuple(pl['b'][1])) for pl in pls]
    print('stored placements:', len(stored), 'distinct:', len(set(stored)))
    ok = True
    for s in stored:
        found = [i for i, ob in enumerate(allorbits) if s in ob]
        if len(found) != 1:
            print('FAIL: stored placement', s, 'in', len(found), 'classes')
            ok = False
        else:
            allorbits[found[0]] = ('USED',)
    if ok:
        missing = [ob for ob in allorbits if ob != ('USED',)]
        print('classes with no stored representative:', len(missing))
        for ob in missing[:10]:
            print('   missing class (size %d) e.g.' % len(ob), ob[0])
        ok = ok and not missing
    json.dump(dict(classes=len([o for o in allorbits]),
                   stored=len(stored), ok=bool(ok)),
              open('placement_classes.json', 'w'), indent=1)
    print('COMPLETENESS:', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
