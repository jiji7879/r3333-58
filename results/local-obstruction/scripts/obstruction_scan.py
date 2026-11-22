"""How general is the three-word obstruction?  Scan every .wit in the campaign."""
import sys, os, json, itertools, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wit import Wit

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"

def scan(w, k, verts):
    L = {}
    dead = 0
    for x, y in itertools.combinations(verts, 2):
        s = frozenset(f for f in range(4) if f != k and not (w.M(x, f) & w.M(y, f)))
        L[(x, y)] = s
        if not s:
            dead += 1
    trip = 0
    for x, y, z in itertools.combinations(verts, 3):
        a, b, c = L[(x, y)], L[(x, z)], L[(y, z)]
        if len(a) == 1 and a == b == c:
            trip += 1
    return dead, trip

paths = sorted(glob.glob(os.path.join(ROOT, ".ultramath", "*", "*", "wit", "*.wit")) +
               glob.glob(os.path.join(ROOT, ".ultramath", "*", "*", "*.wit")) +
               glob.glob(os.path.join(ROOT, ".scratch", "pkg", "witnesses", "*.wit")))
seen = set()
for p in paths:
    if p in seen:
        continue
    seen.add(p)
    try:
        w = Wit(p)
    except Exception as e:
        print("%-70s SKIP %s" % (os.path.relpath(p, ROOT), e))
        continue
    if not w.arms:
        print("%-70s no arms" % os.path.relpath(p, ROOT))
        continue
    rows = []
    for k in sorted(w.arms):
        vs = sorted(w.arms[k])
        if len(vs) < 3:
            rows.append("arm %d: %d words" % (k, len(vs)))
            continue
        d, t = scan(w, k, vs)
        rows.append("arm %d (%d words): dead %d, triples %d" % (k, len(vs), d, t))
    print("%-62s %s" % (os.path.relpath(p, ROOT), " | ".join(rows)))
