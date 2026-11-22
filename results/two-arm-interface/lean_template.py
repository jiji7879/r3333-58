"""Reproduce Lean's `K58.template n twisted` and compare with the .col artefacts.

lean/K58/Templates.lean:
  dc : 1->0 2->1 3->1 4->2 5->2 6->2 7->1 8->0 9->2 10->0 11->1 12->0 13->1 14->2
  trade = {21,22,28,31,37,38,44,47,88,91,104,107,140,143,188,191}
  templateCol n twisted u v =
     if twisted && (16*min u v + max u v) in trade then swap01 (dc (u xor v))
     else dc (u xor v)
with swap01 = (0,2,1) i.e. 0->0, 1->2, 2->1.

The file convention (m2's report) is: file colour c is campaign colour c+1.
"""
import itertools
import sys
from tpl import load_col, campaign_edges, triangle_free

DC = {1: 0, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 1, 8: 0, 9: 2, 10: 0, 11: 1, 12: 0, 13: 1, 14: 2}
TRADE = {21, 22, 28, 31, 37, 38, 44, 47, 88, 91, 104, 107, 140, 143, 188, 191}
SWAP01 = {0: 0, 1: 2, 2: 1}


def template_col(n, twisted, u, v):
    if u == v:
        return 0  # unused / junk, matching the diagonal convention
    lo, hi = min(u, v), max(u, v)
    x = DC.get(u ^ v, 0)   # Lean: the wildcard clause `_ => 0`
    if twisted and (16 * lo + hi) in TRADE:
        return SWAP01[x]
    return x


def template(n, twisted):
    return [[(0 if u == v else template_col(n, twisted, u, v)) for v in range(n)]
            for u in range(n)]


def find_iso(M1, M2, n):
    """Backtracking coloured-isomorphism search M1 -> M2 (small n)."""
    # candidate maps: v1 -> v2 must preserve the multiset of colours to all
    # already-mapped vertices.  Order vertices by degree signature.
    def sig(M, v):
        cnt = {}
        for w in range(n):
            if w != v:
                cnt[M[v][w]] = cnt.get(M[v][w], 0) + 1
        return tuple(sorted(cnt.items()))

    sig1 = [sig(M1, v) for v in range(n)]
    sig2 = [sig(M2, v) for v in range(n)]
    order = sorted(range(n), key=lambda v: (sum(1 for w in range(n) if sig1[w] == sig1[v]),))
    cand = [[w for w in range(n) if sig1[v] == sig2[w]] for v in range(n)]
    for sigma in itertools.permutations((0, 1, 2)):
        # search with colour permutation sigma: M1[a][b] -> sigma[M1[a][b]]
        mapd = {}
        used = set()

        def bt(i):
            if i == n:
                return dict(mapd)
            v = order[i]
            for w in cand[v]:
                if w in used:
                    continue
                ok = True
                for v2, w2 in mapd.items():
                    if sigma[M1[v][v2]] != M2[w][w2]:
                        ok = False
                        break
                if ok:
                    mapd[v] = w
                    used.add(w)
                    r = bt(i + 1)
                    if r is not None:
                        return r
                    del mapd[v]
                    used.discard(w)
            return None

        r = bt(0)
        if r is not None:
            return r, sigma
    return None


if __name__ == "__main__":
    import os
    R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../artifacts")
    files = {
        "k15_template_Tminus_aut2_m4": load_col(f"{R}/k15_template_Tminus_aut2_m4.col"),
        "k15_link_Tminus_m5": load_col(f"{R}/k15_link_Tminus_m5.col"),
        "k15_template_Uminus_aut10_m4": load_col(f"{R}/k15_template_Uminus_aut10_m4.col"),
    }
    for twisted in (False, True):
        T = template(15, twisted)
        print(f"== Lean template 15 twisted={twisted}: triangle_free={triangle_free(T)}")
        for name, M in files.items():
            r = find_iso(T, M, 15)
            print(f"   vs {name}: iso={r is not None}"
                  + (f" sigma={r[1]}" if r else ""))
    # also: are the two .col T files iso to each other?
    r = find_iso(files["k15_template_Tminus_aut2_m4"], files["k15_link_Tminus_m5"], 15)
    print("template_Tminus vs link_Tminus iso:", r is not None, r[1] if r else "")


def find_iso_campaign(M1, M2, n):
    """Isomorphism for campaign-coloured templates (0 on the diagonal, 1..3
    off it): a vertex permutation and a permutation of {1,2,3}."""
    def sig(M, v):
        cnt = {}
        for w in range(n):
            if w != v:
                cnt[M[v][w]] = cnt.get(M[v][w], 0) + 1
        return tuple(sorted(cnt.items()))

    order = sorted(range(n), key=lambda v: (len(cand_ok[v]) if False else 0,))
    cand_ok = [[w for w in range(n) if sig(M1, v) == sig(M2, w)] for v in range(n)]
    order = sorted(range(n), key=lambda v: len(cand_ok[v]))
    for sigma in itertools.permutations((1, 2, 3)):
        sig2 = {1: sigma[0], 2: sigma[1], 3: sigma[2]}
        mapd, used = {}, set()

        def bt(i):
            if i == n:
                return dict(mapd)
            v = order[i]
            for w in cand_ok[v]:
                if w in used:
                    continue
                if all(sig2[M1[v][v2]] == M2[w][w2] for v2, w2 in mapd.items()):
                    mapd[v] = w
                    used.add(w)
                    r = bt(i + 1)
                    if r is not None:
                        return r
                    del mapd[v]
                    used.discard(w)
            return None

        r = bt(0)
        if r is not None:
            return r, sig2
    return None
