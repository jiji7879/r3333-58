"""CNF for the singleton-perfect-balance codegree-14 cases on K58.

One instance = (template M in {U,T}, private labels D with |D| = 2, t in 1..5).

Vertex layout (58 vertices):
   0..13   the 14 shared sites (template labels outside D, increasing)
  14,15    p_{d0}, p_{d1}                     (private, u's side)
  16,17    q_{d0}, q_{d1}                     (private, v's side)
  18       u
  19       v
  20..57   the 38 outside sites, grouped by cell (colour to u, colour to v)

Colours: 0 blue, 1 green, 2 yellow, 3 red.

Laws:
    (L1) exactly one colour per edge
    (L2) no monochromatic triangle
    (L3) red degree in {15,16} at every vertex; blue/green/yellow at most 14
    (L4) every pair of vertices has at most 14 common red neighbours

Strength levels.  0 is exactly "(L1)-(L4) plus the pins", with no symmetry
breaking and no strengthening.  1 and 2 add constraints that every host
satisfies, so they never create a false UNSAT:

  1  every ordinary colour has degree at least 13 at every vertex.  This is a
     consequence of (L3): 57 = red + b + g + y with red in {15,16} and
     b,g,y <= 14 forces b+g+y in {41,42}, hence each of b,g,y >= 13.
  2  additionally, for a SHARED site z with red degree 16, the red neighbours of
     z in each outside cell are exactly (in the (colour to u, colour to v)
     table)  0 in (B,B), 2 in each of (B,G),(B,Y),(G,B),(Y,B),(G,G),(Y,Y),
     1 in each of (G,Y),(Y,G).  Reason: the red chart of z is a triangle-free
     3-coloured K16, hence isomorphic to T or U (the K16 template
     classification, kernel-checked in lean/K58), both roots lie in it and are
     joined blue, and every blue edge of either template has exactly this
     footprint - verified in tools/pb/footprint.py.

Usage:
    python3 tools/pb/encode.py ROW T OUT.cnf [--strength N]
"""
import sys, os, itertools, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pbdata import U, T, ROWS, cells
from pysat.card import CardEnc, EncType
from pysat.formula import CNF

BLUE, GREEN, YELLOW, RED = 0, 1, 2, 3
COLS = (BLUE, GREEN, YELLOW, RED)
CELLORDER = [(0, 1), (0, 2), (1, 0), (2, 0), (1, 1), (1, 2), (2, 1), (2, 2)]
N = 58
FOOTPRINT16 = {(0, 0): 0, (0, 1): 2, (0, 2): 2, (1, 0): 2, (1, 1): 2,
               (1, 2): 1, (2, 0): 2, (2, 1): 1, (2, 2): 2}


def layout(M, D):
    tpl = U if M == 'U' else T
    D = tuple(D)
    S = [l for l in range(16) if l not in D]
    lab2v = {l: i for i, l in enumerate(S)}
    pv = {D[k]: 14 + k for k in range(2)}
    qv = {D[k]: 16 + k for k in range(2)}
    u, v = 18, 19
    pins = {}
    def pin(a, b, c):
        k = (a, b) if a < b else (b, a)
        if k in pins:
            assert pins[k] == c, (k, pins[k], c)
        else:
            pins[k] = c
    for l in S:
        pin(u, lab2v[l], RED); pin(v, lab2v[l], RED)
    for l in D:
        pin(u, pv[l], RED); pin(v, qv[l], RED)
        pin(u, qv[l], BLUE); pin(v, pv[l], BLUE)
        pin(pv[l], qv[l], RED)
    pin(u, v, BLUE)
    for l1, l2 in itertools.combinations(S, 2):
        pin(lab2v[l1], lab2v[l2], int(tpl[l1][l2]))
    if len(D) == 2:
        c = int(tpl[D[0]][D[1]])
        pin(pv[D[0]], pv[D[1]], c); pin(qv[D[0]], qv[D[1]], c)
    for l in D:
        for l2 in S:
            c = int(tpl[l][l2])
            pin(pv[l], lab2v[l2], c); pin(qv[l], lab2v[l2], c)
    return pins, lab2v, pv, qv, u, v


def cellmap(t):
    csz = cells(t)
    assert sum(csz.values()) == 38
    cellof, nxt = {}, 20
    for key in CELLORDER:
        for _ in range(csz[key]):
            cellof[nxt] = key; nxt += 1
    assert nxt == N
    return cellof


def build(M, D, t, stats=False, strength=0, laws=(1, 2, 3, 4), all16=False, footprint=True, some15=False, z15=-1, fp15=False, all15=False, zonly=None):
    pins, lab2v, pv, qv, u, v = layout(M, D)
    cellof = cellmap(t)
    cellv = {key: [] for key in CELLORDER}
    for w in range(20, N):
        cellv[cellof[w]].append(w)

    def ev(a, b, c):
        if a > b: a, b = b, a
        return (a * N + b) * 4 + c + 1

    cnf = CNF()
    top = ev(N - 2, N - 1, RED)
    def add_enc(enc):
        nonlocal top
        cnf.extend(enc.clauses)
        if enc.nv > top: top = enc.nv
    def newv():
        nonlocal top
        top += 1
        return top

    for a, b in itertools.combinations(range(N), 2):
        lits = [ev(a, b, c) for c in COLS]
        cnf.append(lits)
        for x, y in itertools.combinations(lits, 2):
            cnf.append([-x, -y])
    for (a, b), c in pins.items():
        cnf.append([ev(a, b, c)])
    for w, (cu, cv) in cellof.items():
        cnf.append([ev(u, w, cu)]); cnf.append([ev(v, w, cv)])

    poss = {}
    def pr(a, b):
        k = (a, b) if a < b else (b, a)
        if k in pins: return pins[k] == RED
        return True
    def is_pinned_red(a, b):
        k = (a, b) if a < b else (b, a)
        return pins.get(k) == RED
    def free_lits(a, c):
        return [ev(a, b, c) for b in range(N) if b != a and ((a, b) if a < b else (b, a)) not in pins]

    # ---- (L3) degrees
    if 3 in laws:
        for a in range(N):
            cnt = {c: 0 for c in COLS}
            for b in range(N):
                if b == a: continue
                k = (a, b) if a < b else (b, a)
                if k in pins: cnt[pins[k]] += 1
            rl = free_lits(a, RED)
            lo, hi = 15 - cnt[RED], 16 - cnt[RED]
            if lo > 0 and len(rl) >= lo:
                add_enc(CardEnc.atleast(lits=rl, bound=lo, top_id=top, encoding=EncType.seqcounter))
            add_enc(CardEnc.atmost(lits=rl, bound=hi, top_id=top, encoding=EncType.seqcounter))
            for c in (BLUE, GREEN, YELLOW):
                lits = free_lits(a, c)
                bd = 14 - cnt[c]
                if bd < 0: raise SystemExit('UNSAT by pin: vertex %d colour %d' % (a, c))
                if bd < len(lits):
                    add_enc(CardEnc.atmost(lits=lits, bound=bd, top_id=top, encoding=EncType.seqcounter))
                if strength >= 1:
                    lo2 = 13 - cnt[c]
                    if lo2 > 0 and lo2 <= len(lits):
                        add_enc(CardEnc.atleast(lits=lits, bound=lo2, top_id=top, encoding=EncType.seqcounter))

    # ---- (L4) red codegree
    if 4 in laws:
        for a, b in itertools.combinations(range(N), 2):
            cand, ntrue = [], 0
            for w in range(N):
                if w == a or w == b: continue
                if not pr(a, w) or not pr(b, w): continue
                if is_pinned_red(a, w) and is_pinned_red(b, w): ntrue += 1
                else: cand.append(w)
            bound = 14 - ntrue
            if bound < 0: raise SystemExit('UNSAT by pin: codegree(%d,%d)=%d' % (a, b, ntrue))
            if len(cand) <= bound: continue
            ys = []
            for w in cand:
                y = newv()
                cnf.append([-y, ev(a, w, RED)]); cnf.append([-y, ev(b, w, RED)])
                cnf.append([y, -ev(a, w, RED), -ev(b, w, RED)])
                ys.append(y)
            add_enc(CardEnc.atmost(lits=ys, bound=bound, top_id=top, encoding=EncType.seqcounter))

    # ---- strength 2: footprint of a degree-16 shared site
    if strength >= 2 or all16 or some15 or z15 >= 0 or fp15 or all15:
        d16s = {}
        for z in range(14):
            if zonly is not None and z != zonly: continue
            rl = [ev(z, b, RED) for b in range(N) if b != z]
            d16 = newv(); d16s[z] = d16
            # d16 -> red >= 16   (y <-> l or not d16: vacuous when d16 is false)
            g = []
            for l in rl:
                y = newv(); cnf.append([-y, l, -d16]); cnf.append([-l, y]); cnf.append([d16, y]); g.append(y)
            add_enc(CardEnc.atleast(lits=g, bound=16, top_id=top, encoding=EncType.seqcounter))
            # not d16 -> red <= 15
            h = []
            for l in rl:
                y = newv(); cnf.append([-y, l]); cnf.append([-y, -d16]); cnf.append([y, -l, d16]); h.append(y)
            add_enc(CardEnc.atmost(lits=h, bound=15, top_id=top, encoding=EncType.seqcounter))
            if all16:
                cnf.append([d16])
            if all15:
                cnf.append([-d16])
            if not footprint:
                continue
            if fp15:
                # Heinrich 1977 Theorem 2: a 3-coloured K15 chart is a K16 chart with
                # one vertex deleted, so its footprint is the 16-table with one unit
                # removed from exactly one positive cell - or the full table.
                pos = [(key, FOOTPRINT16[key], [ev(z, w, RED) for w in cellv.get(key, [])])
                       for key in CELLORDER if FOOTPRINT16[key] > 0]
                sel = {}
                for key, c, L in pos:
                    sel[key] = newv()
                allv = [d16] + [sel[k] for k, _, _ in pos]
                add_enc(CardEnc.atmost(lits=allv, bound=1, top_id=top, encoding=EncType.seqcounter))
                cnf.append(list(allv))
                for key, c, L in pos:
                    r, m = sel[key], len(L)
                    # r -> at most c-1 red
                    for S in itertools.combinations(L, c):
                        cnf.append([-r] + [-x for x in S])
                    # r -> at least c-1 red
                    if c - 1 > 0:
                        for S in itertools.combinations(L, m - (c - 1) + 1):
                            cnf.append([-r] + list(S))
                    else:
                        for x in L:
                            cnf.append([-r, -x])
                    # not r -> at most c red
                    for S in itertools.combinations(L, c + 1):
                        cnf.append([r] + [-x for x in S])
                    # not r -> at least c red
                    if c > 0:
                        for S in itertools.combinations(L, m - c + 1):
                            cnf.append([r] + list(S))
            else:
                for key, c in FOOTPRINT16.items():
                    L = [ev(z, w, RED) for w in cellv.get(key, [])]
                    m = len(L)
                    if m == 0 or c >= m: continue
                    for S in itertools.combinations(L, c + 1):
                        cnf.append([-d16] + [-x for x in S])
                    if c > 0:
                        for S in itertools.combinations(L, m - c + 1):
                            cnf.append([-d16] + list(S))

        if some15:
            cnf.append([-d16s[z] for z in range(14)])
        if z15 >= 0:
            cnf.append([-d16s[z15]])

    # ---- strength 3: a 5-cell is a red 5-cycle
    # inside a cell whose two coordinates exclude two colours, the internal edges
    # use only the other two; a vertex with three red neighbours there would have
    # them pairwise non-red, hence a monochromatic triangle.  So at most two red
    # neighbours each, and for a cell of size 5 the totals force exactly two.
    if strength >= 3:
        for key in ((0, 1), (0, 2), (1, 0), (2, 0)):
            cell = cellv.get(key, [])
            if len(cell) != 5: continue
            for A in cell:
                L = [ev(A, B, RED) for B in cell if B != A]
                add_enc(CardEnc.atmost(lits=L, bound=2, top_id=top, encoding=EncType.seqcounter))
                add_enc(CardEnc.atleast(lits=L, bound=2, top_id=top, encoding=EncType.seqcounter))

    # ---- (L2) triangles
    if 2 in laws:
        for a, b, c in itertools.combinations(range(N), 3):
            for col in COLS:
                cnf.append([-ev(a, b, col), -ev(a, c, col), -ev(b, c, col)])

    if stats:
        print('strength %d: vars %d clauses %d' % (strength, cnf.nv, len(cnf.clauses)))
    return cnf, pins, cellof


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('row'); ap.add_argument('t', type=int); ap.add_argument('out')
    ap.add_argument('--strength', type=int, default=0)
    ap.add_argument('--all16', action='store_true')
    ap.add_argument('--no-footprint', action='store_true')
    ap.add_argument('--some15', action='store_true')
    ap.add_argument('--z15', type=int, default=-1)
    ap.add_argument('--fp15', action='store_true')
    ap.add_argument('--all15', action='store_true')
    A = ap.parse_args()
    M, D = [(m, d) for (nm, m, d) in ROWS if nm == A.row][0]
    cnf, pins, cellof = build(M, D, A.t, stats=True, strength=A.strength, all16=A.all16,
                              footprint=not A.no_footprint, some15=A.some15, z15=A.z15, fp15=A.fp15, all15=A.all15)
    cnf.to_file(A.out)
    print('wrote', A.out, 'pins', len(pins))
