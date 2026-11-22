#!/usr/bin/env python3
"""Word-only relaxation of the branch: pair level *minus* the pair-colour
variables, plus the depth-3 obstruction condition.

A set of 42 words is admissible here iff
  (W1) every word has exactly five 0s,
  (W2) every ordinary part is independent in the template,
  (D1) every arm point lies in exactly fourteen colour-0 supports,
  (T3) no triple of slots {x,y,z} and colour c has all three admissible-colour
       lists equal to the singleton {c}.

(T3) is necessary for a genuine object: restricting its own pair colouring to
{x,y,z} is a valid colouring, so a triple whose three lists are the same
singleton is impossible.  A *pair* whose list is empty is impossible for the same
reason; that case is covered because an empty list cannot be a singleton and is
excluded separately by (T2) below.

  (T2) no pair of slots has an empty admissible-colour list.

This is a relaxation of the `(14,12)+XT` / three-arm objects (it drops the
per-triple colour consistency and the per-pair colour variables), and a
strengthening of the pair level (which permits dead triples).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enc import Enc, ARMS, ALL_SLOTS, A_POINTS
from k58lib import Template, Witness

COLOURS = (0, 1, 2, 3)


def armof(x):
    for b, vs in ARMS.items():
        if x in vs:
            return b
    raise KeyError(x)


def build(tmpl, drop=(), pin=None):
    e = Enc()
    keep = set(["W1", "W2", "D1", "T2", "T3", "S"]) - set(drop)
    cell = {}
    for x in ALL_SLOTS:
        for p in A_POINTS:
            cell[(x, p)] = [e.cellv(x, p, f) for f in range(4)]
    for x in ALL_SLOTS:
        for p in A_POINTS:
            e.add(cell[(x, p)])
            e.at_most_one(cell[(x, p)])
    if "W1" in keep:
        for x in ALL_SLOTS:
            e.exactly_k([e.cellv(x, p, 0) for p in A_POINTS], 5)
    if "W2" in keep:
        for f in (1, 2, 3):
            for (a, b) in tmpl.indep[f]:
                for x in ALL_SLOTS:
                    e.add([-e.cellv(x, a, f), -e.cellv(x, b, f)])
    if "D1" in keep:
        for a in A_POINTS:
            e.exactly_k([e.cellv(x, a, 0) for x in ALL_SLOTS], 14)

    # (S) the sixth arm lemma in its A-part form: inside one arm, no six slots
    # have pairwise intersecting colour-a parts (a != arm colour).  Word-level.
    if "S" in keep:
        from itertools import combinations
        for b, vs in ARMS.items():
            for a in range(4):
                if a == b:
                    continue
                B = {}
                for i in range(len(vs)):
                    for j in range(i + 1, len(vs)):
                        B[(i, j)] = e.new(("B", vs[i], vs[j], a))
                for (i, j), v in B.items():
                    for p in A_POINTS:
                        e.add([-e.cellv(vs[i], p, a), -e.cellv(vs[j], p, a), v])
                for idx in combinations(range(14), 6):
                    e.add([-B[(idx[i], idx[j])] for i in range(6) for j in range(i + 1, 6)])

    # allowed colour sets per pair (arm-colour ban folded in)
    def allowed(x, y):
        base = [c for c in COLOURS if armof(x) != armof(y) or c != armof(x)]
        return base

    N = {}
    E = {}
    for i in range(42):
        for j in range(i + 1, 42):
            x, y = i, j
            for c in allowed(x, y):
                Es = []
                for p in A_POINTS:
                    v = e.new(("E", x, y, c, p))
                    a1, a2 = e.cellv(x, p, c), e.cellv(y, p, c)
                    e.add([-v, a1])
                    e.add([-v, a2])
                    e.add([-a1, -a2, v])
                    Es.append(v)
                n = e.new(("N", x, y, c))
                for v in Es:
                    e.add([-v, n])
                e.add([-n] + Es)
                N[(x, y, c)] = n
    # (T2) non-empty list per pair
    if "T2" in keep:
        # at least one colour is admissible on every pair, i.e. NOT all blocked
        for i in range(42):
            for j in range(i + 1, 42):
                x, y = i, j
                e.add([-N[(x, y, c)] for c in allowed(x, y)])
    # D(x,y,c) = "the admissible list of {x,y} is exactly {c}"
    D = {}
    for i in range(42):
        for j in range(i + 1, 42):
            x, y = i, j
            for c in allowed(x, y):
                others = [f for f in allowed(x, y) if f != c]
                d = e.new(("D", x, y, c))
                D[(x, y, c)] = d
                e.add([-d, -N[(x, y, c)]])
                for f in others:
                    e.add([-d, N[(x, y, f)]])
                e.add([N[(x, y, c)]] + [-N[(x, y, f)] for f in others] + [d])
    # (T3)
    if "T3" in keep:
        from itertools import combinations
        for (x, y, z) in combinations(range(42), 3):
            for c in COLOURS:
                if (x, y, c) in D and (y, z, c) in D and (x, z, c) in D:
                    e.add([-D[(x, y, c)], -D[(y, z, c)], -D[(x, z, c)]])
    if pin is not None:
        w = Witness(pin)
        for x in ALL_SLOTS:
            for p in A_POINTS:
                f = w.words[x][p]
                for g in range(4):
                    if g != f:
                        e.add([-e.cellv(x, p, g)])
                e.add([e.cellv(x, p, f)])
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--template", default=None)
    ap.add_argument("--drop", default="")
    ap.add_argument("--pin", default=None)
    ap.add_argument("--map", default=None)
    a = ap.parse_args()
    repo = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
    tp = a.template or os.path.join(repo, "artifacts/k15_link_Tminus_m5.col")
    tmpl = Template(tp)
    e = build(tmpl, drop=[s for s in a.drop.split(",") if s], pin=a.pin)
    e.write(a.out)
    if a.map:
        import json
        json.dump({str(k): v for k, v in e.meta.items()}, open(a.map, "w"))
    print(f"{a.out}: p cnf {e.nv} {len(e.cls)}  drop={a.drop} pin={a.pin}")


if __name__ == "__main__":
    main()
