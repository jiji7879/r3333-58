#!/usr/bin/env python3
"""The TICKET LAYER at 42 slots -- my own encoder, written from the branch
definition (review/PROFILE_15141414_STATE.md sections 1, 4, 7).

Object.  r is the root, A = N_0(r) has 15 points (the template: a fixed
triangle-free 3-colouring of K_15, .col file), X = N_1(r) u N_2(r) u N_3(r) is
partitioned into three arms of 14 labelled slots.  Each slot x carries a word
  w_x : A -> {0,1,2,3},
and each pair {x,y} carries a colour q(x,y).

Clauses (family tags in brackets):
  cell1/cell2   every cell (x,a) has exactly one colour
  row5          |w_x^{-1}(0)| = 5                       [m(x)=5, branch]
  partindep     w_x^{-1}(f) independent in the template's colour-f graph
                (f = 1,2,3), i.e. no monochromatic triangle x,a,b
  colcap        per arm R and arm point a:  #{x in R : w_x(a)=0} <= 5   [mixture]
  colfloor      per arm R and arm point a:  #{x in R : w_x(a)=0} >= 4   [hereditary
                full-arm profile: the three arms give 14 = d_0(a)-1 with each
                <= 5, so each is 4 or 5; see finding f7 of swarm smwrmwgf7]
  pair*         q(x,y) in the allowed set; allowed = all 4 colours except the
                arm's root colour when x,y share an arm  [no mono triangle rxy]
  pairdisj      q(x,y)=f  =>  M_f(x) cap M_f(y) = empty  [no mono triangle xya]
  zerodeg       *** THE NEW FAMILY, and the point of this instance ***
                for every slot x:  #{y != x : q(x,y)=0} = 10.
                In the branch d_0(x) = 15 and |N_0(x) cap A| = m(x) = 5, so the
                number of colour-0 partners inside X is exactly 10.  This is a
                sound family that the pair level does NOT imply and that no
                existing encoding of the 42-slot object carries.
  (optional) degcap  p_f(x) + n_f(x) + [f = root colour of x] <= 16, the
                R(3,3,3)=17 bound on d_f(x); p_f = |M_f(x)|, n_f = #q(x,y)=f.

No triangle family is imposed (that is the three-arm instance, a different
object); --tri adds arm-internal triangle-freeness only, as an ablation.

Usage:  python3 ticketenc.py --out f.cnf [--tri] [--degcap] [--zerodeg K]
        python3 ticketenc.py --verify f.cnf model.txt [--tri] [--degcap] [--zerodeg K]
"""
import argparse
import itertools
import sys

R = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"
TPL = R + "/artifacts/k15_link_Tminus_m5.col"


def load_col(path):
    with open(path) as fh:
        t = fh.read().split()
    n, k = int(t[0]), int(t[1])
    vals = list(map(int, t[2:2 + n * n]))
    return n, k, [vals[i * n:(i + 1) * n] for i in range(n)]


class CNF(object):
    def __init__(self):
        self.nv = 0
        self.cl = []
        self.fam = []

    def new(self):
        self.nv += 1
        return self.nv

    def add(self, cl, fam="other"):
        assert len(cl) > 0, "empty clause"
        self.cl.append(tuple(cl))
        self.fam.append(fam)

    def at_most(self, lits, k, fam="card"):
        """Sinz sequential counter: at most k of lits true."""
        n = len(lits)
        if k >= n:
            return
        if k < 0:
            self.add([lits[0]], fam)
            self.add([-lits[0]], fam)
            return
        if k == 0:
            for l in lits:
                self.add([-l], fam)
            return
        s = [[0] * (k + 1) for _ in range(n)]
        for i in range(n):
            for j in range(1, k + 1):
                s[i][j] = self.new()
        self.add([-lits[0], s[0][1]], fam)
        for j in range(2, k + 1):
            self.add([-s[0][j]], fam)
        for i in range(1, n):
            self.add([-lits[i], s[i][1]], fam)
            self.add([-s[i - 1][1], s[i][1]], fam)
            for j in range(2, k + 1):
                self.add([-lits[i], -s[i - 1][j - 1], s[i][j]], fam)
                self.add([-s[i - 1][j], s[i][j]], fam)
            self.add([-lits[i], -s[i - 1][k]], fam)

    def at_least(self, lits, k, fam="card"):
        self.at_most([-l for l in lits], len(lits) - k, fam)

    def exactly(self, lits, k, fam="card"):
        self.at_most(lits, k, fam)
        self.at_least(lits, k, fam)

    def write(self, path):
        with open(path, "w") as fh:
            fh.write("p cnf %d %d\n" % (self.nv, len(self.cl)))
            fh.write("".join(" ".join(map(str, c)) + " 0\n" for c in self.cl))


def structure(nB=14, nD=14, nE=14):
    """Slots: arm 1 (root colour 1) has nB, arm 2 (root colour 2) has nD,
    arm 3 (root colour 3) has nE.  For the 42-slot object all are 14."""
    slots, rootcol = [], {}
    i = 0
    for arm, cnt in ((1, nB), (2, nD), (3, nE)):
        for _ in range(cnt):
            slots.append(i)
            rootcol[i] = arm
            i += 1
    return slots, rootcol


def build(tpl, zerodeg=None, tri=False, degcap=False, nB=14, nD=14, nE=14,
          degmin=None, degmax=None, colsum=False):
    n, nk, M = tpl
    A = list(range(n))
    fedges = {f: [(a, b) for a in range(n) for b in range(a + 1, n)
                  if M[a][b] == f - 1] for f in (1, 2, 3)}
    slots, rootcol = structure(nB, nD, nE)
    X = slots
    cnf = CNF()
    cell = {}
    for x in X:
        for a in A:
            for f in range(4):
                cell[x, a, f] = cnf.new()
    # cell: exactly one colour
    for x in X:
        for a in A:
            cnf.add([cell[x, a, f] for f in range(4)], "cell1")
            for f, g in itertools.combinations(range(4), 2):
                cnf.add([-cell[x, a, f], -cell[x, a, g]], "cell2")
    # row: exactly five zeros
    for x in X:
        cnf.exactly([cell[x, a, 0] for a in A], 5, "row5")
    # part independence
    for x in X:
        for f in (1, 2, 3):
            for (a, b) in fedges[f]:
                cnf.add([-cell[x, a, f], -cell[x, b, f]], "partindep")
    # per-arm column bounds (cap 5 and floor 4)
    for a in A:
        for arm in (1, 2, 3):
            col = [cell[x, a, 0] for x in X if rootcol[x] == arm]
            cnf.at_most(col, 5, "colcap")
            cnf.at_least(col, 4, "colfloor")
    # coverage 14: every arm point has exactly 14 colour-0 partners in X
    # (d_0(a) = 15 in the branch and r contributes the 15th)
    if colsum:
        for a in A:
            cnf.exactly([cell[x, a, 0] for x in X], 14, "colsum")
    # pairs
    q = {}
    for u, v in itertools.combinations(X, 2):
        allowed = [f for f in range(4)
                   if not (rootcol[u] == rootcol[v] == f)]
        for f in allowed:
            q[u, v, f] = cnf.new()
            for a in A:
                cnf.add([-q[u, v, f], -cell[u, a, f], -cell[v, a, f]],
                        "pairdisj")
        cnf.add([q[u, v, f] for f in allowed], "pair1")
        for f, g in itertools.combinations(allowed, 2):
            cnf.add([-q[u, v, f], -q[u, v, g]], "pair1")
    # THE TICKET LAYER: 0-degree inside X
    lo = degmin if degmin is not None else zerodeg
    hi = degmax if degmax is not None else zerodeg
    for x in X:
        lit = []
        for y in X:
            if y == x:
                continue
            u, v = (x, y) if x < y else (y, x)
            lit.append(q[u, v, 0])
        if lo is not None:
            cnf.at_least(lit, lo, "ticketmin")
        if hi is not None and (lo is None or hi != lo):
            cnf.at_most(lit, hi, "ticketmax")
    # ordinary degree caps d_f(x) <= 16 (f = 1,2,3)
    if degcap:
        for x in X:
            rc = rootcol[x]
            for f in (1, 2, 3):
                lit = [cell[x, a, f] for a in A]
                for y in X:
                    if y == x:
                        continue
                    u, v = (x, y) if x < y else (y, x)
                    if (u, v, f) in q:
                        lit.append(q[u, v, f])
                cnf.at_most(lit, 16 - (1 if f == rc else 0), "degcap")
    # ablation only: arm-internal triangle-freeness
    if tri:
        for arm in (1, 2, 3):
            verts = [x for x in X if rootcol[x] == arm]
            allowed = [f for f in range(4) if f != arm]
            for (u, v, w) in itertools.combinations(verts, 3):
                for f in allowed:
                    cnf.add([-q[u, v, f], -q[u, w, f], -q[v, w, f]], "armtri")
    return cnf, cell, q, X, A, rootcol, fedges


# ------------------------------------------------------------------ verifier
def parse_model(path):
    true = set()
    with open(path) as fh:
        for line in fh:
            if line.startswith("s") or line.startswith("c"):
                continue
            for t in line.split():
                if t in ("v", "0"):
                    continue
                try:
                    v = int(t)
                except ValueError:
                    continue
                if v > 0:
                    true.add(v)
    return true


def verify(modelpath, tpl, zerodeg=None, tri=False, degcap=False,
           nB=14, nD=14, nE=14, degmin=None, degmax=None, colsum=False):
    """Independent check of the mathematical content, from the model file."""
    n, nk, M = tpl
    A = list(range(n))
    fedges = {f: [(a, b) for a in range(n) for b in range(a + 1, n)
                  if M[a][b] == f - 1] for f in (1, 2, 3)}
    cnf, cell, q, X, A, rootcol, fedges = build(
        tpl, zerodeg=zerodeg, tri=tri, degcap=degcap, nB=nB, nD=nD, nE=nE,
        degmin=degmin, degmax=degmax, colsum=colsum)
    lo = degmin if degmin is not None else zerodeg
    hi = degmax if degmax is not None else zerodeg
    true = parse_model(modelpath)
    bad = []
    word = {}
    for x in X:
        w = {}
        for a in A:
            cs = [f for f in range(4) if cell[x, a, f] in true]
            if len(cs) != 1:
                bad.append(("cell", x, a, cs))
                cs = cs or [0]
            w[a] = cs[0]
        word[x] = w
        if sum(1 for a in A if w[a] == 0) != 5:
            bad.append(("five-zeros", x))
        for f in (1, 2, 3):
            part = [a for a in A if w[a] == f]
            for i in range(len(part)):
                for j in range(i + 1, len(part)):
                    if (part[i], part[j]) in fedges[f]:
                        bad.append(("part-indep", x, f, part[i], part[j]))
    qv = {}
    for u, v in itertools.combinations(X, 2):
        allowed = [f for f in range(4) if not (rootcol[u] == rootcol[v] == f)]
        chosen = [f for f in allowed if q[u, v, f] in true]
        if len(chosen) != 1:
            bad.append(("pair-colour", u, v, chosen))
            chosen = chosen or allowed
        f = chosen[0]
        qv[u, v] = f
        for a in A:
            if word[u][a] == f and word[v][a] == f:
                bad.append(("pair-disjoint", u, v, f, a))
    for a in A:
        tot = 0
        for arm in (1, 2, 3):
            c = sum(1 for x in X if rootcol[x] == arm and word[x][a] == 0)
            tot += c
            if c > 5:
                bad.append(("col>5", a, arm, c))
            if c < 4:
                bad.append(("col<4", a, arm, c))
        if colsum and tot != 14:
            bad.append(("colsum", a, tot))
    if lo is not None or hi is not None:
        for x in X:
            d0 = sum(1 for y in X if y != x
                     and qv[(x, y) if x < y else (y, x)] == 0)
            if lo is not None and d0 < lo:
                bad.append(("0-degree<", x, d0))
            if hi is not None and d0 > hi:
                bad.append(("0-degree>", x, d0))
    if degcap:
        for x in X:
            for f in (1, 2, 3):
                pf = sum(1 for a in A if word[x][a] == f)
                nf = sum(1 for y in X if y != x
                         and qv[(x, y) if x < y else (y, x)] == f)
                tot = pf + nf + (1 if rootcol[x] == f else 0)
                if tot > 16:
                    bad.append(("degcap", x, f, tot))
    if tri:
        for arm in (1, 2, 3):
            verts = [x for x in X if rootcol[x] == arm]
            allowed = [f for f in range(4) if f != arm]
            for (u, v, w) in itertools.combinations(verts, 3):
                quv = qv[(u, v) if u < v else (v, u)]
                quw = qv[(u, w) if u < w else (w, u)]
                qvw = qv[(v, w) if v < w else (w, v)]
                if quv == quw == qvw and quv in allowed:
                    bad.append(("mono-triangle", arm, u, v, w, quv))
    return bad, word, qv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tpl", default=TPL)
    ap.add_argument("--out", default=None)
    ap.add_argument("--zerodeg", type=int, default=None)
    ap.add_argument("--degmin", type=int, default=None)
    ap.add_argument("--degmax", type=int, default=None)
    ap.add_argument("--no-zerodeg", action="store_true")
    ap.add_argument("--tri", action="store_true")
    ap.add_argument("--degcap", action="store_true")
    ap.add_argument("--nB", type=int, default=14)
    ap.add_argument("--nD", type=int, default=14)
    ap.add_argument("--nE", type=int, default=14)
    ap.add_argument("--colsum", action="store_true")
    ap.add_argument("--verify", nargs=2, default=None, metavar=("CNF", "MODEL"))
    a = ap.parse_args()
    tpl = load_col(a.tpl)
    zd = None if a.no_zerodeg else a.zerodeg
    lo = None if a.no_zerodeg else a.degmin
    hi = None if a.no_zerodeg else a.degmax
    if a.verify:
        bad, word, qv = verify(a.verify[1], tpl, zerodeg=zd, tri=a.tri,
                               degcap=a.degcap, nB=a.nB, nD=a.nD, nE=a.nE,
                               degmin=lo, degmax=hi, colsum=a.colsum)
        if bad:
            print("MODEL BAD:", len(bad), "violations; e.g.", bad[:6])
            return 1
        print("MODEL OK:", len(word), "slots, every family holds")
        return 0
    cnf, *_ = build(tpl, zerodeg=zd, tri=a.tri, degcap=a.degcap,
                    nB=a.nB, nD=a.nD, nE=a.nE, degmin=lo, degmax=hi,
                    colsum=a.colsum)
    if a.out:
        cnf.write(a.out)
    from collections import Counter
    fam = Counter(cnf.fam)
    print("%s: vars %d, clauses %d" % (a.out, cnf.nv, len(cnf.cl)))
    print("  families:", dict(sorted(fam.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
