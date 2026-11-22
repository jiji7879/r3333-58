"""Consistency check of the arm CSP: whenever the witness's OWN pair colours
restricted to an arm are a legal arm colouring (each in L(x,y), no monochromatic
triangle), the CSP must be SAT.  This catches encoder bugs in the direction that
matters (a false UNSAT would be a false obstruction)."""
import sys, os, itertools, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wit import Wit
from arm_sat import feasible, lists

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"
paths = sorted(set(glob.glob(os.path.join(ROOT, ".ultramath", "*", "*", "wit", "*.wit")) +
                    glob.glob(os.path.join(ROOT, ".ultramath", "*", "*", "*.wit"))))
bad = 0
checked = 0
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
        if not all((min(x, y), max(x, y)) in w.pairs for x, y in itertools.combinations(vs, 2)):
            continue
        L, internal = lists(w, vs, k)
        legal = True
        for x, y in itertools.combinations(vs, 2):
            f = w.pairs[(min(x, y), max(x, y))]
            if f not in L[(x, y)]:
                legal = False
                break
        if legal:
            for x, y, z in itertools.combinations(vs, 3):
                fs = [w.pairs[(min(a, b), max(a, b))] for a, b in ((x, y), (x, z), (y, z))]
                if fs[0] == fs[1] == fs[2]:
                    legal = False
                    break
        if legal:
            checked += 1
            sat = feasible(w, vs, k)
            print("%-58s arm %d: witness colouring legal, CSP says %s"
                  % (os.path.relpath(p, ROOT), k, "SAT" if sat else "UNSAT  <-- BUG"))
            if not sat:
                bad += 1
print("\n%d arms whose own colouring is legal; mismatches: %d" % (checked, bad))
sys.exit(1 if bad else 0)
