"""Independent re-implementation of the k54cut ledger primitives (m3, direction d5).

Nothing here imports the archive's src/.  The definitions are re-derived from
data/h42.json and data/placements.json only:

  * a placement fixes a pole and a palette for each of the two H42 templates;
  * the symmetry group of a placement is the set of 54-point permutations
    (A-part, B-part, palette part) that preserve both twists, where a group
    element may exchange the two templates;
  * a marked rectangle is a pair of non-pole pairs, one pair on each side;
  * the weight of a rectangle is the number of inequivalent colourings of its
    four crossing edges with the three ordinary colours, subject to
    triangle-freeness against the two fixed template edges.
"""
from itertools import combinations, product

ORD = 3            # ordinary colours 0,1,2
C = 3              # the crossing colour c


def load_h42(path):
    import json
    return json.load(open(path))


def colour_matrix(H, pal):
    """Colour of edge (u,v) on a template whose palette is `pal`."""
    return [[-1 if u == v else pal[H[u][v]] for v in range(14)] for u in range(14)]


def degenerate(H):
    assert len(H) == 14
    for u in range(14):
        for v in range(14):
            if u != v:
                assert H[u][v] in (0, 1, 2), (u, v, H[u][v])
                assert H[u][v] == H[v][u]


def side_maps(P, Q, p, q, pal):
    """All bijections f from a template coloured P with pole p onto a template
    coloured Q with pole q with Q[f(u)][f(w)] == pal[P[u][w]] for all u,w and
    f(p) == q.  Straight backtracking, no heuristics from the archive."""
    # colour-degree invariant for pruning
    def degs(M):
        return [tuple(sum(M[u][v] == c for v in range(14)) for c in range(3)) for u in range(14)]
    dp, dq = degs(P), degs(Q)
    cand = {}
    for u in range(14):
        want = tuple(dp[u][pal.index(c)] for c in range(3))   # after applying pal
        cand[u] = [v for v in range(14) if dq[v] == want and (u == p) == (v == q)]
    order = sorted(range(14), key=lambda u: (len(cand[u]), u))
    f = {}
    used = set()

    def rec(i):
        if i == 14:
            yield tuple(f[u] for u in range(14))
            return
        u = order[i]
        for v in cand[u]:
            if v in used:
                continue
            ok = True
            for u2, v2 in f.items():
                if Q[v][v2] != pal[P[u][u2]]:
                    ok = False
                    break
            if ok:
                f[u] = v
                used.add(v)
                yield from rec(i + 1)
                used.remove(v)
                del f[u]

    return list(rec(0))


def placement_group(pa, ca, pb, cb, H):
    """54-point permutations (A image, B image, palette image) of the placement."""
    P = colour_matrix(H, ca)
    Q = colour_matrix(H, cb)
    sides = [(P, pa), (Q, pb)]
    elems = set()
    for pal in product(range(3), repeat=3):
        if len(set(pal)) != 3:
            continue
        for sw in (0, 1):
            (SP, sp), (TQ, tq) = sides[0], sides[sw]
            (SP2, sp2), (TQ2, tq2) = sides[1], sides[1 - sw]
            af = side_maps(SP, TQ, sp, tq, pal)
            if not af:
                continue
            bf = side_maps(SP2, TQ2, sp2, tq2, pal)
            if not bf:
                continue
            for a in af:
                for b in bf:
                    elems.add(tuple(x + 14 * sw for x in a) +
                              tuple(x + 14 * (1 - sw) for x in b) +
                              tuple(28 + pal[x] for x in range(3)))
    return sorted(elems)


def act(R, g):
    """Image of the unordered pair-of-pairs rectangle R under g, normalised so
    that the first component is the pair drawn from the A template."""
    a, b = R
    l = tuple(sorted(g[i] for i in a))
    r = tuple(sorted(g[i] for i in b))
    if l[0] >= 14:
        return (r, l)
    return (l, r)


def is_group(gs):
    n = 31
    assert tuple(range(n)) in gs
    s = set(gs)
    for g in gs:
        assert sorted(g) == list(range(n))
    # closure: |G|^2 is tiny here
    for g in gs:
        for h in gs:
            assert tuple(h[g[i]] for i in range(n)) in s, 'not closed'
    return True


def four_constraints(c, d):
    """Indices of words in 3^4 that keep the four template triangles uncoloured
    monochromatically: word order is (a,x),(a,y),(b,x),(b,y); c is the colour of
    the row edge (a,b), d the colour of the column edge (x,y)."""
    out = []
    for w in product(range(3), repeat=4):
        if any(w[j] == c and w[j + 2] == c for j in (0, 1)):
            continue
        if any(w[2 * i] == d and w[2 * i + 1] == d for i in (0, 1)):
            continue
        out.append(w)
    return out


def edge_actions(R, stab):
    """(edge position permutation, palette permutation) induced on the four
    crossing edges by each stabiliser element, as a set."""
    edges = [(i, j) for i in R[0] for j in R[1]]
    index = {e: k for k, e in enumerate(edges)}
    out = set()
    for g in stab:
        pos = []
        for (i, j) in edges:
            pos.append(index[tuple(sorted((g[i], g[j])))])
        out.add((tuple(pos), tuple(g[i] - 28 for i in (28, 29, 30))))
    return tuple(sorted(out))


def weight(R, c, d, stab):
    """Number of inequivalent ordinary colourings of R's four crossing edges."""
    valid = four_constraints(c, d)
    acts = edge_actions(R, stab)
    seen = set()
    reps = []
    for w in valid:
        if w in seen:
            continue
        orb = set()
        for pos, pal in acts:
            z = [None] * 4
            for i in range(4):
                z[pos[i]] = pal[w[i]]
            orb.add(tuple(z))
        assert orb <= set(valid)
        assert not (orb & seen)
        seen |= orb
        reps.append(w)
    assert seen == set(valid)
    return len(reps)
