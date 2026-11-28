"""Pinned K16 critical templates (FKR2004 seeds T1/T2) and their symmetry groups.

The matrices are taken from the frozen repository module
  tools/color-resolved-wallcc/frozen/gluing.py
  sha256 ca534d9d5dca23f2b29e9180db633114a1c45743b22fdf8262c7793e85227b48
which transcribes Tatarevic's formal/src/R4333Lean/CriticalTemplates.lean
(commit 6c3f2fd): DIFFERENCE_COLORS on GF(2)^4 plus the TRADE edge set.
'U' = untwisted (Greenwood-Gleason; FKR's T2), 'T' = twisted (FKR's T1).
Nothing is re-typed by hand here; every structural claim is recomputed.

Exact integer combinatorics only; no SAT solver in this module.
"""
import itertools
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[4]
FROZEN = REPO / "tools/color-resolved-wallcc/frozen"
if str(FROZEN) not in sys.path:
    sys.path.insert(0, str(FROZEN))

import gluing  # noqa: E402  (frozen, read-only)

KINDS = ("U", "T")


def matrix(kind, size=16):
    return gluing.template(size, kind)


def named_iso_count(c1, c2):
    """Number of vertex bijections phi with c1[u][v] == c2[phi u][phi v] (named colours)."""
    n = len(c1)
    d1 = [tuple(sum(1 for v in range(n) if u != v and c1[u][v] == c)
                 for c in range(3)) for u in range(n)]
    d2 = [tuple(sum(1 for v in range(n) if u != v and c2[u][v] == c)
                 for c in range(3)) for u in range(n)]
    cand = [[v for v in range(n) if d2[v] == d1[u]] for u in range(n)]
    count = 0

    def rec(assign, used):
        nonlocal count
        if len(assign) == n:
            count += 1
            return
        best, bestc = None, None
        for u in range(n):
            if u in assign:
                continue
            cs = [v for v in cand[u] if v not in used and
                  all(c1[u][w] == c2[v][assign[w]] for w in assign)]
            if bestc is None or len(cs) < len(bestc):
                best, bestc = u, cs
                if not cs:
                    break
        for v in bestc:
            assign[best] = v
            used.add(v)
            rec(assign, used)
            used.discard(v)
            del assign[best]

    rec({}, set())
    return count


def named_isos(c1, c2):
    """All vertex bijections phi with c1[u][v] == c2[phi u][phi v]."""
    return vertex_isos(lambda u, v: c1[u][v], lambda u, v: c2[u][v], len(c1))


def vertex_isos(f1, f2, n):
    out = []

    def rec(assign, used):
        if len(assign) == n:
            out.append(tuple(assign[i] for i in range(n)))
            return
        best, bestc = None, None
        for u in range(n):
            if u in assign:
                continue
            cs = [v for v in range(n) if v not in used and
                  all(f1(u, w) == f2(v, assign[w]) for w in assign)]
            if bestc is None or len(cs) < len(bestc):
                best, bestc = u, cs
                if not cs:
                    break
        for v in bestc:
            assign[best] = v
            used.add(v)
            rec(assign, used)
            used.discard(v)
            del assign[best]

    rec({}, set())
    return out


def relabel(c, pi):
    return tuple(tuple(pi[c[u][v]] for v in range(len(c))) for u in range(len(c)))


def weak_group(c):
    """List of (vertex permutation tuple, colour permutation tuple) automorphisms."""
    out = []
    for pi in itertools.permutations(range(3)):
        for phi in named_isos(relabel(c, pi), c):
            out.append((phi, pi))
    return out


def weak_iso_count(c1, c2):
    return sum(named_iso_count(relabel(c1, pi), c2)
               for pi in itertools.permutations(range(3)))


def good(c):
    n = len(c)
    for u, v, w in itertools.combinations(range(n), 3):
        if c[u][v] == c[u][w] == c[v][w]:
            return False
    return True


def degrees(c):
    n = len(c)
    return [tuple(sum(1 for v in range(n) if u != v and c[u][v] == col)
                  for col in range(3)) for u in range(n)]


def deletion(c, drop):
    idx = [v for v in range(len(c)) if v != drop]
    return tuple(tuple(c[u][v] for v in idx) for u in idx)


def main():
    rep = {"source": {
        "module": "tools/color-resolved-wallcc/frozen/gluing.py",
        "sha256": "ca534d9d5dca23f2b29e9180db633114a1c45743b22fdf8262c7793e85227b48",
        "repo_head": "e43e78e"}, "templates": {}}
    mats = {}
    for kind in KINDS:
        c = matrix(kind)
        mats[kind] = c
        wg = weak_group(c)
        aut = [p for p, _ in wg if p in {q for q, pi in wg if pi == (0, 1, 2)}
               ] if False else named_isos(c, c)
        rep["templates"][kind] = {
            "good_triangle_free": good(c),
            "degrees_all_555": all(d == (5, 5, 5) for d in degrees(c)),
            "edge_class_sizes": [sum(1 for u, v in itertools.combinations(range(16), 2)
                                     if c[u][v] == col) for col in range(3)],
            "aut_named_order": len(aut),
            "aut_named_equals_frozen_gluing_assert": sorted(aut) == sorted(
                gluing.automorphisms(16, kind)),
            "weak_group_order": len(wg),
            "colour_perms_realised": sorted({tuple(sorted({pi[0]: pi for pi in [x[1]]}.items()))
                                            for x in []} or
                                           [list(p) for p in sorted({x[1] for x in wg})]),
            "vertex_orbits_under_weak_group": len(
                {frozenset(p[i] for p, _ in wg) for i in range(16)}),
        }
    rep["weak_iso_U_to_T_count"] = weak_iso_count(mats["U"], mats["T"])
    rep["named_iso_U_to_T_count"] = named_iso_count(mats["U"], mats["T"])
    # 15-vertex deletions: named iso classes (FKR p.45-46 / Heinrich)
    dels = []
    for kind in KINDS:
        for drop in range(16):
            dels.append((kind, drop, deletion(mats[kind], drop)))
    classes = []
    for kind, drop, c in dels:
        for cl in classes:
            if named_iso_count(c, cl[0][2]):
                cl.append((kind, drop, c))
                break
        else:
            classes.append([(kind, drop, c)])
    rep["deleted_15_named_classes"] = len(classes)
    rep["deleted_15_class_members"] = [[(k, d) for k, d, _ in cl] for cl in classes]
    rep["aut_order_15_by_class"] = [named_iso_count(cl[0][2], cl[0][2]) for cl in classes]
    print(json.dumps(rep, indent=2))
    return rep


if __name__ == "__main__":
    main()
