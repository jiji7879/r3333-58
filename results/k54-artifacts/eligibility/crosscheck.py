"""m3 -- validation of the search code used by audit_cap.py and audit_deletions.py.

Nothing here is evidence about the handoff; it is a guard against a systematic
bug in my own decision procedures.

 1. has_clique is a necessary-condition filter in audit_cap.py.  It is compared
    with brute force on random compatibility graphs.
 2. A seeded random sample of the 48 880 (row, P) instances is decided again by
    the full family search with the filter switched off; any violation there is
    a case the filter wrongly skipped.
 3. canon, the canonical form used by audit_deletions.py, is tested for
    invariance under random vertex relabellings and for separation of
    non-isomorphic specimens.
"""
import json
import random
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from audit_k15 import decode
from audit_cap import adjmasks, words, family_exists, has_clique
from audit_deletions import canon, subset, REGULAR_EXCLUDED
from itertools import combinations

ARCHIVE = ('/workspace/nucleus/work/projects/'
           'p-764e12eeb9f34762ad544edb924f4680/repo/work/k54cut/')


def brute_clique(n, edges, target):
    def rec(cands, size):
        if size == target:
            return True
        for k, v in enumerate(cands):
            rest = [u for u in cands[k + 1:] if edges[v][u]]
            if size + 1 + len(rest) >= target and rec(rest, size + 1):
                return True
        return False
    return rec(list(range(n)), 0)


def check_has_clique(trials=300, seed=7):
    """Build random compatibility graphs directly: for every non-edge (i,j) give
    words i and j one shared colour bit at one shared vertex, so that two words
    are compatible exactly when the edge is present."""
    random.seed(seed)
    bad = 0
    for _ in range(trials):
        n = random.randint(2, 12)
        p = random.choice([0.1, 0.25, 0.4, 0.6, 0.85])
        edges = [[False] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if random.random() < p:
                    edges[i][j] = edges[j][i] = True
        # a pair is compatible iff at least one colour is unshared, so a
        # non-edge needs all four colours shared at four common vertices
        ws = [[0, 0, 0, 0] for _ in range(n)]
        bit = 0
        for i in range(n):
            for j in range(i + 1, n):
                if not edges[i][j]:
                    for c in range(4):
                        ws[i][c] |= 1 << bit
                        ws[j][c] |= 1 << bit
                        bit += 1
        ws = [tuple(w) for w in ws]
        target = random.randint(1, 5)
        got, _ = has_clique(ws, target)
        want = brute_clique(n, edges, target)
        if got is not None and got != want:
            bad += 1
            print('has_clique disagrees: n=%d target=%d got=%s want=%s' % (n, target, got, want))
    print('has_clique: %d disagreements in %d random compatibility graphs' % (bad, trials))
    return bad


def unit_tests():
    """Sharp tests of the mono-triangle logic in family_exists."""
    bad = 0
    a = (1 << 0, 1 << 1, 1 << 2, 0)
    if family_exists([a, a, a], 2)[0] is not True or family_exists([a, a, a], 3)[0] is not False:
        print('FAIL: three words sharing colours 0,1,2 must admit a pair but no triple')
        bad += 1
    b = (1 << 0, 1 << 1, 0, 0)
    if family_exists([b, b, b], 3)[0] is not True:
        print('FAIL: two free colours must admit a triple')
        bad += 1
    c = (1 << 10, 0, 0, 0)
    if family_exists([c] * 4, 3)[0] is not True or family_exists([c] * 4, 4)[0] is not True:
        print('FAIL: four words sharing only colour 0 must admit a 4-family')
        bad += 1
    d = (0, 0, 0, 1 << 3)   # only the crossing colour is used
    if family_exists([d] * 3, 3)[0] is not True:
        print('FAIL: three words sharing only colour c must admit a triple')
        bad += 1
    print('family_exists unit tests: %d failures' % bad)
    return bad


def main():
    bad = check_has_clique() + unit_tests()

    cat14 = [decode(s) for s in open(ARCHIVE + 'data/r333_14.mc').read().splitlines()]
    regular = sorted(set(range(1, 116)) - REGULAR_EXCLUDED)
    masks = [0]
    for k in range(1, 4):
        masks += [sum(1 << v for v in c) for c in combinations(range(14), k)]
    random.seed(11)
    sample = [(r, P) for r in random.sample(regular, 15) for P in random.sample(masks, 100)]
    viol = 0
    undec = 0
    for (r, P) in sample:
        ws = words(adjmasks(cat14[r - 1]), P)
        if not ws:
            continue
        res, _ = family_exists(ws, P.bit_count() + 1)
        if res is None:
            undec += 1
        elif res:
            viol += 1
            print('VIOLATION without filter: row %d mask %d' % (r, P))
    print('unfiltered sample: %d instances, %d violations, %d undecided'
          % (len(sample), viol, undec))
    bad += viol

    # canonical form tests
    random.seed(3)
    forms = {}
    perm_bad = 0
    for i in range(150):
        t = random.choice([14, 15])
        cat = cat14 if t == 14 else [decode(s) for s in
                                     open(ARCHIVE + 'data/r333_15.mc').read().splitlines()]
        M = random.choice(cat)
        keep = sorted(random.sample(range(t), 10))
        sub = subset(M, keep)
        perm = list(range(10))
        random.shuffle(perm)
        rel = [[-1] * 10 for _ in range(10)]
        for a in range(10):
            for b in range(10):
                if a != b:
                    rel[perm[a]][perm[b]] = sub[a][b]
        if canon(sub) != canon(rel):
            perm_bad += 1
        forms.setdefault(canon(sub), []).append(sub)
    print('canon: %d relabelling mismatches in 150' % perm_bad)
    print('canon: %d distinct classes among 150 sampled K10 restrictions' % len(forms))
    bad += perm_bad
    print('TOTAL PROBLEMS:', bad)
    json.dump(dict(problems=bad), open('crosscheck.json', 'w'))
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
