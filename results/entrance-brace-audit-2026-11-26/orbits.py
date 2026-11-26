"""Automorphism groups of the two K16 templates and orbit reduction of supports."""
import itertools
import sys

REPO = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo'
sys.path.insert(0, REPO + '/.scratch/k58')
from gluing import template                     # noqa: E402
import supports as S                            # noqa: E402

SIZE = 16


def auts(kind):
    """All position permutations preserving every edge colour of `kind`."""
    mat = template(SIZE, kind)
    deg = [tuple(sum(1 for v in range(SIZE) if v != u and mat[u][v] == c)
                 for c in range(3)) for u in range(SIZE)]
    out = []
    perm = [-1] * SIZE
    used = [False] * SIZE

    def compatible(i, j):
        for k in range(i):
            if mat[i][k] != mat[j][perm[k]]:
                return False
        return True

    def rec(i):
        if i == SIZE:
            out.append(tuple(perm))
            return
        for j in range(SIZE):
            if used[j] or deg[j] != deg[i]:
                continue
            perm[i] = j
            if compatible(i, j):
                used[j] = True
                rec(i + 1)
                used[j] = False
            perm[i] = -1
    rec(0)
    return out


def support_sets(kind, i, pal, size=5):
    """All position sets carrying the reference two-colouring for arm colour i."""
    mat = template(SIZE, kind)
    out = []
    for T in itertools.combinations(range(SIZE), size):
        lab = S.reference_labelling(lambda u, v: mat[u][v], T, i, pal)
        if lab is not None:
            out.append((tuple(T), tuple(lab)))
    return out


def orbits(entries, group):
    index = {}
    for s, lab in entries:
        index[tuple(sorted(s))] = (s, lab)
    seen, reps = set(), []
    for key in sorted(index):
        if key in seen:
            continue
        orbit = set()
        for g in group:
            orbit.add(tuple(sorted(g[p] for p in key)))
        seen |= orbit
        reps.append(index[key])
    return reps, seen


if __name__ == '__main__':
    for kind in ('U', 'T'):
        g = auts(kind)
        print('%s: |Aut| = %d' % (kind, len(g)))
        for i in (0, 1, 2):
            ent = support_sets(kind, i, (0, 1, 2))
            reps, _ = orbits(ent, g)
            print('   5-supports for arm colour %d: %d, orbits %d' % (i, len(ent), len(reps)))
            ent4 = support_sets(kind, i, (0, 1, 2), size=4)
            reps4, _ = orbits(ent4, g)
            print('   4-supports for arm colour %d: %d, orbits %d' % (i, len(ent4), len(reps4)))
