"""Exact arm-module feasibility and the size of the smallest infeasible sub-arm.

The arm module for an arm of root colour k with word set V is a 3-EDGE-colouring
of K_|V|:  col(x,y) in L(x,y) = {f != k : M_f(x) cap M_f(y) = empty}, and no
monochromatic triangle.  Variables are per (pair, colour); both the root-colour
ban and the M_f-disjointness are necessary conditions of a genuine colouring, and
the mono-triangle condition is triangle-freeness inside the arm -- so UNSAT of
this CSP proves the arm is not realisable in any triangle-free 4-colouring.
"""
import sys, os, json, itertools, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wit import Wit
from pysat.formula import CNF, IDPool
from pysat.solvers import Cadical153

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"

def lists(w, verts, k, no0=False):
    internal = [f for f in range(4) if f != k and not (no0 and f == 0)]
    L = {}
    for x, y in itertools.combinations(verts, 2):
        L[(x, y)] = frozenset(f for f in internal if not (w.M(x, f) & w.M(y, f)))
    return L, internal

def feasible(w, verts, k, no0=False):
    L, internal = lists(w, verts, k, no0)
    for s in L.values():
        if not s:
            return False
    vp = IDPool()
    cnf = CNF()
    for (x, y), s in L.items():
        cnf.append([vp.id(("e", x, y, f)) for f in sorted(s)])
        for f, g in itertools.combinations(sorted(s), 2):
            cnf.append([-vp.id(("e", x, y, f)), -vp.id(("e", x, y, g))])
    for x, y, z in itertools.combinations(verts, 3):
        for f in internal:
            lits = []
            ok = True
            for (a, b) in ((x, y), (x, z), (y, z)):
                key = (a, b) if (a, b) in L else (b, a)
                if f not in L[key]:
                    ok = False
                    break
                lits.append(-vp.id(("e", key[0], key[1], f)))
            if ok:
                cnf.append(lits)
    with Cadical153(bootstrap_with=cnf.clauses) as s:
        return bool(s.solve())

def min_infeasible(w, verts, k, kmax=4, all_subsets=False):
    """Smallest k with an infeasible k-subset, and the number of them."""
    for kk in range(2, kmax + 1):
        hits = []
        for sub in itertools.combinations(verts, kk):
            if not feasible(w, list(sub), k):
                hits.append(sub)
                if not all_subsets and len(hits) > 0:
                    return kk, len(hits), hits[0]
        if hits:
            return kk, len(hits), hits[0]
    return None, 0, None

def main():
    paths = sorted(set(
        glob.glob(os.path.join(ROOT, ".ultramath", "*", "*", "wit", "*.wit")) +
        glob.glob(os.path.join(ROOT, ".ultramath", "*", "*", "*.wit"))))
    out = []
    for p in paths:
        try:
            w = Wit(p)
        except Exception:
            continue
        if not w.arms:
            continue
        for k in sorted(w.arms):
            vs = sorted(w.arms[k])
            if len(vs) < 3:
                continue
            f = feasible(w, vs, k)
            f0 = feasible(w, vs, k, no0=True)
            row = {"witness": os.path.relpath(p, ROOT), "arm": k, "n": len(vs),
                   "arm_feasible": f, "arm_feasible_no0": f0}
            if not f:
                kk, cnt, ex = min_infeasible(w, vs, k, kmax=3, all_subsets=True)
                row["min_infeasible_size"] = kk
                row["count_at_min"] = cnt
                row["example"] = list(ex) if ex else None
            out.append(row)
            print(json.dumps(row), flush=True)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "arm_sat.json"), "w"), indent=1)

if __name__ == '__main__':
    main()
