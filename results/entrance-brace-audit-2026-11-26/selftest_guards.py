"""Check the guard derivation: needed/candidates must encode d_c(x) >= 15 exactly.

For random colourings of all 4848 edges that respect the frozen units, we
recompute d_c(x) from the matrix and compare with the guard arithmetic.
"""
import random
import sys
import guardrow as G

RID = '0404c3a224626a202cbfa4355bb0b19513ec815d182050440c580208861f2296'
ORDER = 58


def lit(u, v, c):
    if u > v:
        u, v = v, u
    return 4 * (u * (2 * ORDER - u - 1) // 2 + (v - u - 1)) + 1 + c


def main(trials=4):
    d = G.row(RID)
    f = G.family_of(d)
    fixed = G.units(f, tuple(d['placement']))
    pinned = {}
    for c in fixed:
        assert len(c) == 1
        l = c[0]
        idx, col = (abs(l) - 1) // 4, (abs(l) - 1) % 4
        pinned[idx] = (('pos', col) if l > 0 else ('neg', col))
    arms = G.arms_of(f)
    rng = random.Random(7)
    for t in range(trials):
        mat = {}
        for i in range(ORDER * (ORDER - 1) // 2):
            if i not in pinned:
                mat[i] = rng.randrange(4)
        for i, (kind, c) in pinned.items():
            mat[i] = c if kind == 'pos' else rng.choice([x for x in range(4) if x != c])
        def col(u, v):
            if u > v:
                u, v = v, u
            return mat[u * (2 * ORDER - u - 1) // 2 + (v - u - 1)]
        ok = 0
        for x in range(1, ORDER):
            c = next(cc for cc, blk in arms.items() if x in blk)
            # in-arm colour-c edges are impossible in any model (triangle with r),
            # so the guard arithmetic counts 1 (for r) + the out-of-arm part.
            deg = 1 + sum(1 for y in range(ORDER)
                          if y != x and y != 0 and y not in arms[c] and col(x, y) == c)
            # recompute the guard arithmetic exactly as guardrow.build does
            pos = {cc[0] for cc in fixed if len(cc) == 1 and cc[0] > 0}
            known = {(l - 1) // 4 for l in pos}
            p, cand = 0, []
            for y in range(ORDER):
                if y == 0 or y == x or y in arms[c]:
                    continue
                e = lit(x, y, c)
                if e in pos:
                    p += 1
                elif (e - 1) // 4 not in known:
                    cand.append(e)
            free = sum(1 for e in cand if col(*divmod_edge(e)) == c)
            needed = 14 - p
            assert deg == 1 + p + free, (x, deg, p, free)
            assert (deg >= 15) == (free >= needed), (x, c, deg, free, needed)
            ok += 1
        print('trial %d: %d vertices, guard arithmetic exact' % (t, ok))


def divmod_edge(e):
    """Edge literal -> its unordered pair."""
    i = (e - 1) // 4
    u = 0
    while True:
        width = ORDER - u - 1
        if i < width:
            return u, u + 1 + i
        i -= width
        u += 1


if __name__ == '__main__':
    main()
