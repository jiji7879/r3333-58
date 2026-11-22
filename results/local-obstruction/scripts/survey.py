import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wit import Wit

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"
WITS = [
 ".ultramath/smwr8io45/m6/wit/pair58_Tminus.wit",
 ".ultramath/smwr8io45/m6/wit/L_58.wit",
 ".ultramath/smwr8io45/m4/pair58_Tminus_recoloured.wit",
 ".ultramath/smwrfgma5/m4/wit/p58.wit",
 ".ultramath/smwrfgma5/m4/wit/p58_cc.wit",
]
for rel in WITS:
    p = os.path.join(ROOT, rel)
    w = Wit(p)
    errs = w.check()
    n = w.n_arm(); xs = w.nouts()
    print("== %s" % rel)
    print("   words=%d pairs=%d arm=%d template=%s" % (len(w.words), len(w.pairs), n, w.template))
    print("   check errors: %d %s" % (len(errs), errs[:3]))
    cov = w.coverage
    print("   colour-0 coverage of A: min %d max %d  (branch: 14)" % (min(cov), max(cov)))
    N, adj = w.colour0_graph()
    degs = [bin(adj[v]).count("1") for v in range(N)]
    print("   colour-0 graph on %d vertices: edges=%d deg[min,max]=%d,%d" %
          (N, sum(degs)//2, min(degs), max(degs)))
    # distribution of word 0-parts
    from collections import Counter
    c = Counter(w.M(x,0) for x in xs)
    print("   distinct M_0 supports: %d ; max multiplicity %d" % (len(c), max(c.values())))
    # pair colour distribution
    pc = Counter(w.pairs.values())
    print("   pair colours: %s" % dict(sorted(pc.items())))
    # 0-edges inside X
    e0 = sum(1 for (x,y),f in w.pairs.items() if f==0)
    print("   0-edges inside X: %d of %d" % (e0, len(w.pairs)))
