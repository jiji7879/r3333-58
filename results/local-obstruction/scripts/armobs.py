"""The three-word gluing obstruction.

Setting.  A root r has arms N_1(r), N_2(r), N_3(r) of 14 vertices each, all
outside vertices uniform (m(x) = 5).  A vertex x of an arm carries the word
w_x : A -> {0,1,2,3}, |M_0(x)| = 5, each M_f(x) independent in the arm's
template colour f.  Two vertices x,y may be joined in colour f only if
M_f(x) cap M_f(y) = empty (pair rule), and -- when they lie in the SAME arm of
root colour k -- only if f != k.  So the admissible colours for the edge {x,y}
are

    L(x,y) = { f in {0,1,2,3} \\ {k} : M_f(x) cap M_f(y) = empty }.

An arm is realisable iff K_14 admits a colouring with col(x,y) in L(x,y) and no
monochromatic triangle.

Obstruction.  If three words x,y,z of one arm satisfy
L(x,y) = L(x,z) = L(y,z) = {c}, then every colouring of the triple assigns c to
all three edges: a monochromatic triangle.  The triple is not realisable, so no
arm containing it is.  |L| >= 1 on each pair (else a pair is already dead) makes
this the SMALLEST refutation that the pair rule plus triangle-freeness produces.

This script decides, for every arm of every pair-level witness, whether such a
triple occurs, and reports the minimal refutations (a dead pair if one exists,
otherwise every mono-forced triple).
"""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wit import Wit

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"
WITS = [
 ("W1 pair58_Tminus", ".ultramath/smwr8io45/m6/wit/pair58_Tminus.wit"),
 ("W2 L_58", ".ultramath/smwr8io45/m6/wit/L_58.wit"),
 ("W3 pair58_Tminus_recoloured", ".ultramath/smwr8io45/m4/pair58_Tminus_recoloured.wit"),
 ("W4 p58", ".ultramath/smwrfgma5/m4/wit/p58.wit"),
 ("W5 p58_cc", ".ultramath/smwrfgma5/m4/wit/p58_cc.wit"),
]

def pairlist(w, x, y, k):
    return frozenset(f for f in range(4)
                     if f != k and not (w.M(x, f) & w.M(y, f)))

def arm_report(w, k, verts):
    rep = {"arm_root_colour": k, "size": len(verts), "dead_pairs": [],
           "mono_forced_triples": [], "list_histogram": {}}
    L = {}
    for x, y in itertools.combinations(verts, 2):
        s = pairlist(w, x, y, k)
        L[(x, y)] = s
        rep["list_histogram"][str(sorted(s))] = rep["list_histogram"].get(str(sorted(s)), 0) + 1
        if not s:
            rep["dead_pairs"].append([x, y])
    for x, y, z in itertools.combinations(verts, 3):
        a, b, c = L[(x, y)], L[(x, z)], L[(y, z)]
        if len(a) == 1 and a == b == c:
            rep["mono_forced_triples"].append({"words": [x, y, z], "colour": sorted(a)[0]})
    return rep

out = []
for name, rel in WITS:
    w = Wit(os.path.join(ROOT, rel))
    rec = {"witness": name, "path": rel, "arms": []}
    for k in sorted(w.arms):
        vs = sorted(w.arms[k])
        r = arm_report(w, k, vs)
        rec["arms"].append(r)
        print("%-30s arm %d (root colour %d), %d words: dead pairs %d, "
              "mono-forced triples %d, list histogram %s"
              % (name, k, k, len(vs), len(r["dead_pairs"]),
                 len(r["mono_forced_triples"]), r["list_histogram"]))
        for t in r["mono_forced_triples"][:3]:
            print("      triple %s forced to colour %d" % (t["words"], t["colour"]))
    out.append(rec)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "arm_obstruction.json"), "w"), indent=1)
