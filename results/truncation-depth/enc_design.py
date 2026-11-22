#!/usr/bin/env python3
"""Design-level relaxation of the branch's colour-0 side.

42 slots, 15 arm points, cells c(x,p) = "p in M_0(x)".
  (Z)  each slot carries exactly five points            -- m(x) = 5
  (D)  each point lies in exactly fourteen supports      -- d_0(a) = 15
  (S0) inside one arm, no six slots are pairwise A-intersecting
       -- a sound (A-part) instance of the sixth lemma at colour 0.

UNSAT here would refute the branch: a genuine object's 42 supports satisfy all
three.  SAT gives a skeleton design for the full word problem.
"""
import argparse
import os
import sys
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enc import Enc

ARMS = {1: list(range(0, 14)), 2: list(range(14, 28)), 3: list(range(28, 42))}


def build(points=15, nslots=42, per_slot=5, per_point=14, clique=6, drop=()):
    e = Enc()
    cell = {}
    for x in range(nslots):
        for p in range(points):
            cell[(x, p)] = e.new(("cell", x, p))
    keep = set(["Z", "D", "S0"]) - set(drop)
    if "Z" in keep:
        for x in range(nslots):
            e.exactly_k([cell[(x, p)] for p in range(points)], per_slot)
    if "D" in keep:
        for p in range(points):
            e.exactly_k([cell[(x, p)] for x in range(nslots)], per_point)
    if "S0" in keep:
        for b, vs in ARMS.items():
            B = {}
            for i in range(len(vs)):
                for j in range(i + 1, len(vs)):
                    B[(vs[i], vs[j])] = e.new(("B", vs[i], vs[j]))
            for (x, y), v in B.items():
                for p in range(points):
                    e.add([-cell[(x, p)], -cell[(y, p)], v])
            for S in combinations(vs, clique):
                e.add([-B[(S[i], S[j])] for i in range(len(S)) for j in range(i + 1, len(S))])
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--drop", default="")
    ap.add_argument("--clique", type=int, default=6)
    a = ap.parse_args()
    e = build(clique=a.clique, drop=[s for s in a.drop.split(",") if s])
    e.write(a.out)
    print(f"{a.out}: p cnf {e.nv} {len(e.cls)}")


if __name__ == "__main__":
    main()
