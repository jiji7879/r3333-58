"""The three-word gluing obstruction: certificate format, generation, verification.

LEMMA (three-word obstruction).
  Let r be a vertex of a triangle-free 4-colouring of K_58 whose outside vertices
  are uniform (m(x) = 5, so x carries a word w_x : A -> {0,1,2,3} with five 0s,
  M_f(x) = {a in A : w_x(a) = f}).  Let k be the root colour of an arm, so every
  vertex of that arm lies in N_k(r).  For x,y in that arm put

      L(x,y) = { f != k : M_f(x) cap M_f(y) = empty }

  -- the colours allowed on the edge xy: colour k is excluded because x,y are
  both k-neighbours of r (a k-edge xy would make a k-triangle rxy), and colour f
  is excluded when M_f(x) cap M_f(y) != empty (that point a is f-adjacent to
  both, and {a,x,y} would be an f-triangle).  The first exclusion is the root
  colour ban, the second is the kernel-checked pair disjointness
  (K58.model_pair_disjoint).

  If three words x,y,z of that arm satisfy L(x,y) = L(x,z) = L(y,z) = {c}, then
  every admissible colouring of the arm gives all three edges colour c, a
  monochromatic triangle.  So the arm has no admissible colouring, the triple is
  an inclusion-minimal infeasible sub-arm (its three pairs are each feasible),
  and no triangle-free 4-colouring of K_58 restricts to this arm.

  Nothing in the argument uses the template except that the words are admissible;
  L depends on the words alone.

CERTIFICATE.  A JSON list of
    {"witness": path, "arm_root_colour": k, "vertices": [x,y,z],
     "words": [w_x, w_y, w_z], "colour": c,
     "pair_lists": [[c],[c],[c]]}
and `verify_obstruction.py` re-derives every field from the witness file.
"""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wit import Wit

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"
WITS = [
 ("W1 pair58_Tminus", ".ultramath/smwr8io45/m6/wit/pair58_Tminus.wit"),
 ("W2 pair58_Tminus_recoloured", ".ultramath/smwr8io45/m4/pair58_Tminus_recoloured.wit"),
 ("W3 wit_big", ".ultramath/smwr8io45/m4/wit_big.wit"),
 ("W4 p58", ".ultramath/smwrfgma5/m4/wit/p58.wit"),
 ("W5 p58_cc", ".ultramath/smwrfgma5/m4/wit/p58_cc.wit"),
]
# NOTE: .ultramath/smwr8io45/m6/wit/L_58.wit is byte-identical to W1 (md5
# de70189fdb0d16285467ea29fda76d15), so these five are the five distinct
# order-58 pair-level witnesses in the repository.

def pairlist(w, x, y, k, internal):
    return frozenset(f for f in internal if not (w.M(x, f) & w.M(y, f)))

def scan(w, k, verts, internal):
    L = {}
    dead = []
    for x, y in itertools.combinations(verts, 2):
        s = pairlist(w, x, y, k, internal)
        L[(x, y)] = s
        if not s:
            dead.append([x, y])
    trip = []
    for x, y, z in itertools.combinations(verts, 3):
        a, b, c = L[(x, y)], L[(x, z)], L[(y, z)]
        if len(a) == 1 and a == b == c:
            trip.append(([x, y, z], sorted(a)[0]))
    return dead, trip

certs = []
summary = []
for name, rel in WITS:
    w = Wit(os.path.join(ROOT, rel))
    rec = {"witness": name, "path": rel, "arms": []}
    for k in sorted(w.arms):
        vs = sorted(w.arms[k])
        internal_full = [f for f in range(4) if f != k]            # colour 0 allowed
        internal_no0 = [f for f in range(4) if f != k and f != 0]  # colour 0 banned
        dead, trip = scan(w, k, vs, internal_full)
        dead0, trip0 = scan(w, k, vs, internal_no0)
        arm = {"arm_root_colour": k, "n_words": len(vs),
               "dead_pairs": len(dead), "mono_forced_triples": len(trip),
               "triples_if_colour0_banned": len(trip0),
               "dead_pairs_if_colour0_banned": len(dead0),
               "triples_by_colour": {}}
        for _, c in trip:
            arm["triples_by_colour"][str(c)] = arm["triples_by_colour"].get(str(c), 0) + 1
        rec["arms"].append(arm)
        # the shipped certificate is the lexicographically first one
        if dead:
            x, y = dead[0]
            certs.append({"witness": name, "path": rel, "arm_root_colour": k,
                          "vertices": [x, y], "words": [w.words[x], w.words[y]],
                          "colour": None,
                          "pair_lists": [sorted(pairlist(w, x, y, k, internal_full))],
                          "obstruction": "dead pair (L = empty)"})
        for (v, c) in trip[:1]:
            x, y, z = v
            certs.append({"witness": name, "path": rel, "arm_root_colour": k,
                          "vertices": [x, y, z],
                          "words": [list(w.words[x]), list(w.words[y]), list(w.words[z])],
                          "colour": c,
                          "pair_lists": [sorted(pairlist(w, v[0], v[1], k, internal_full)),
                                         sorted(pairlist(w, v[0], v[2], k, internal_full)),
                                         sorted(pairlist(w, v[1], v[2], k, internal_full))],
                          "obstruction": "mono-forced triple"})
    summary.append(rec)
    print(json.dumps(rec))

json.dump(summary, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "obstruction_summary.json"), "w"), indent=1)
json.dump(certs, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "three_word_certificates.json"), "w"), indent=1)
tot = sum(a["mono_forced_triples"] for r in summary for a in r["arms"])
dead = sum(a["dead_pairs"] for r in summary for a in r["arms"])
print("\n15 arms: %d inclusion-minimal infeasible triples, %d dead pairs, %d certificates" % (tot, dead, len(certs)))
