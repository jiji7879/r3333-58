#!/usr/bin/env python3
"""Encoder for the uniform fully-sending branch at order 58, T^- template.

Two objects are built here:

  PLAIN  = the pair level (words + pair compatibility), i.e. the relaxation the
           campaign already knows to be SAT;
  SIXTH  = PLAIN + the kernel-checked sixth arm lemma (`part_family_le_five`,
           lean/.../Blocked.lean): for one arm b and one colour a != b, at most
           five slots of that arm have pairwise intersecting a-parts.

Every clause family is a theorem about a genuine object of the branch:

  (W1) |M_0(x)| = 5                        -- m(x) = 5 is the branch hypothesis
  (W2) M_f(x) is f-independent, f = 1,2,3  -- else a,x,a' is a mono triangle
  (C1) one colour per cell (x,a)
  (P1) one colour per slot pair
  (P2) colour(x,y) = b forbidden inside arm b -- else x,y,r mono in colour b
  (P3) colour(x,y) = c  =>  M_c(x) cap M_c(y) = empty  -- else x,y,a mono in c
  (D1) each a in A lies in exactly 14 colour-0 supports -- d_0(a) = 15
  (S)  sixth lemma, all 9 (arm b, colour a != b)

`--pin WIT` pins the words of a witness file (for instrument tests).
`--drop` disables a family by name (for falsification tests).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k58lib import Template, Witness

FAMILIES = ["W1", "W2", "C1", "P1", "P2", "P3", "D1", "S", "S2"]
ARMS = {1: list(range(0, 14)), 2: list(range(14, 28)), 3: list(range(28, 42))}
ALL_SLOTS = list(range(42))
A_POINTS = list(range(15))


class Enc:
    def __init__(self):
        self.nv = 0
        self.cls = []
        self.meta = {}
        self.cell = {}
        self.q = {}
        self.B = {}

    def new(self, info=None):
        self.nv += 1
        if info is not None:
            self.meta[self.nv] = info
        return self.nv

    def add(self, cl):
        self.cls.append(list(cl))

    # ---- variable constructors -------------------------------------
    def cellv(self, x, a, f):
        v = self.cell.get((x, a, f))
        if v is None:
            v = self.new(("cell", x, a, f))
            self.cell[(x, a, f)] = v
        return v

    def qv(self, x, y, f):
        key = (min(x, y), max(x, y), f)
        v = self.q.get(key)
        if v is None:
            v = self.new(("q", key[0], key[1], f))
            self.q[key] = v
        return v

    def bv(self, x, y, a):
        key = (min(x, y), max(x, y), a)
        v = self.B.get(key)
        if v is None:
            v = self.new(("B", key[0], key[1], a))
            self.B[key] = v
        return v

    def at_most_one(self, vs):
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                self.add([-vs[i], -vs[j]])

    def exactly_k(self, vs, k, tag=""):
        """Sequential-counter encoding of sum(vs) = k."""
        from pysat.card import CardEnc, EncType
        if k == 0:
            for v in vs:
                self.add([-v])
            return
        if k == len(vs):
            for v in vs:
                self.add([v])
            return
        lits = list(vs)
        cnf = CardEnc.equals(lits=lits, bound=k, top_id=self.nv, encoding=EncType.seqcounter)
        for cl in cnf.clauses:
            self.add(cl)
        self.nv = max(self.nv, cnf.nv)

    def at_most_k(self, vs, k, tag=""):
        from pysat.card import CardEnc, EncType
        lits = list(vs)
        cnf = CardEnc.atmost(lits=lits, bound=k, top_id=self.nv, encoding=EncType.seqcounter)
        for cl in cnf.clauses:
            self.add(cl)
        self.nv = max(self.nv, cnf.nv)

    def write(self, path):
        with open(path, "w") as fh:
            fh.write(f"p cnf {self.nv} {len(self.cls)}\n")
            for cl in self.cls:
                fh.write(" ".join(str(l) for l in cl) + " 0\n")


def build(tmpl, drop=(), pin=None, pin_design=None):
    e = Enc()
    keep = set(FAMILIES) - set(drop)

    # cells
    for x in ALL_SLOTS:
        for a in A_POINTS:
            vs = [e.cellv(x, a, f) for f in range(4)]
            if "C1" in keep:
                e.add(vs)                      # at least one colour
                e.at_most_one(vs)              # at most one colour
    # (W1) exactly five zeros per slot
    if "W1" in keep:
        for x in ALL_SLOTS:
            e.exactly_k([e.cellv(x, a, 0) for a in A_POINTS], 5, f"zeros{x}")
    # (W2) part independence against the template
    if "W2" in keep:
        for f in (1, 2, 3):
            for (a, b) in tmpl.indep[f]:
                for x in ALL_SLOTS:
                    e.add([-e.cellv(x, a, f), -e.cellv(x, b, f)])
    # (P1) one colour per slot pair
    for i in range(42):
        for j in range(i + 1, 42):
            vs = [e.qv(i, j, f) for f in range(4)]
            if "P1" in keep:
                e.add(vs)
                e.at_most_one(vs)
    # (P2) the arm colour never occurs inside its own arm
    if "P2" in keep:
        for b, vs in ARMS.items():
            for i in range(len(vs)):
                for j in range(i + 1, len(vs)):
                    e.add([-e.qv(vs[i], vs[j], b)])
    # (P3) pair disjointness
    if "P3" in keep:
        for i in range(42):
            for j in range(i + 1, 42):
                for f in range(4):
                    q = e.qv(i, j, f)
                    for a in A_POINTS:
                        e.add([-q, -e.cellv(i, a, f), -e.cellv(j, a, f)])
    # (D1) coverage 14 per arm point
    if "D1" in keep:
        for a in A_POINTS:
            e.exactly_k([e.cellv(x, a, 0) for x in ALL_SLOTS], 14, f"cover{a}")
    # (S) the sixth arm lemma, A-part form (sound for every colour a != b):
    # a common colour-a neighbour inside A already blocks the pair.
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
    # (S2) the true stated form of `part_family_le_five` for a != 0: the a-part
    # is N_a(x) cap N_a(r), i.e. the colour-a neighbours of x inside arm a, so
    # the blocking relation is read off the pair-colour variables.
    if "S2" in keep:
        from itertools import combinations
        for b, vs in ARMS.items():
            for a in range(4):
                if a == b:
                    continue
                B = {}
                for i in range(len(vs)):
                    for j in range(i + 1, len(vs)):
                        B[(i, j)] = e.new(("B2", vs[i], vs[j], a))
                for (i, j), v in B.items():
                    for p in (ARMS[a] if a else A_POINTS):
                        e.add([-e.qv(vs[i], p, a), -e.qv(vs[j], p, a), v])
                for idx in combinations(range(14), 6):
                    e.add([-B[(idx[i], idx[j])] for i in range(6) for j in range(i + 1, 6)])
    # optional pin of a colour-0 design (the M_0 parts only)
    if pin_design is not None:
        blocks = {}
        for line in open(pin_design):
            t = [int(v) for v in line.split()]
            blocks[t[0]] = set(t[1:])
        for x in ALL_SLOTS:
            for p in A_POINTS:
                if p in blocks[x]:
                    e.add([e.cellv(x, p, 0)])
                else:
                    e.add([-e.cellv(x, p, 0)])
    # optional pin of a witness's words
    if pin is not None:
        w = Witness(pin)
        for x in ALL_SLOTS:
            word = w.words[x]
            for a in A_POINTS:
                f = word[a]
                for g in range(4):
                    if g != f:
                        e.add([-e.cellv(x, a, g)])
                e.add([e.cellv(x, a, f)])
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--template", default=None)
    ap.add_argument("--drop", default="")
    ap.add_argument("--pin", default=None)
    ap.add_argument("--map", default=None)
    ap.add_argument("--pin-design", default=None)
    a = ap.parse_args()
    repo = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
    tp = a.template or os.path.join(repo, "artifacts/k15_template_Tminus_aut2_m4.col")
    tmpl = Template(tp)
    drop = [s for s in a.drop.split(",") if s]
    e = build(tmpl, drop=drop, pin=a.pin, pin_design=a.pin_design)
    e.write(a.out)
    if a.map:
        with open(a.map, "w") as fh:
            json.dump({str(k): v for k, v in e.meta.items()}, fh)
    print(f"{a.out}: p cnf {e.nv} {len(e.cls)}  drop={drop} pin={a.pin} design={a.pin_design}")


if __name__ == "__main__":
    main()
