"""Independent cross-check of the colour-0 independence numbers by SAT.

For each witness and each colour c we ask a SAT solver whether there is an
independent set of size a+1 (expect UNSAT) and of size a (expect SAT), where a
is the value returned by the bitset search.  Completely different code path.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wit import Wit
from mis import max_inset
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"
WITS = [
 ("W1 pair58_Tminus", ".ultramath/smwr8io45/m6/wit/pair58_Tminus.wit"),
 ("W3 pair58_Tminus_recoloured", ".ultramath/smwr8io45/m4/pair58_Tminus_recoloured.wit"),
 ("W4 p58", ".ultramath/smwrfgma5/m4/wit/p58.wit"),
 ("W5 p58_cc", ".ultramath/smwrfgma5/m4/wit/p58_cc.wit"),
]

def graph_for_colour(w, c):
    n = w.n_arm(); xs = w.nouts(); m = len(xs); r = n + m; N = n + m + 1
    adj = [0] * N
    def add(u, v):
        adj[u] |= 1 << v; adj[v] |= 1 << u
    if c == 0:
        for a in range(n): add(r, a)
    for i, x in enumerate(xs):
        for a in range(n):
            if w.words[x][a] == c: add(n + i, a)
    idx = {x: i for i, x in enumerate(xs)}
    for (x, y), f in w.pairs.items():
        if f == c: add(n + idx[x], n + idx[y])
    return N, adj

def sat_inset(adj, N, k, expect):
    vp = IDPool()
    cnf = CNF()
    for v in range(N):
        vp.id(("v", v))
    for v in range(N):
        for u in range(v + 1, N):
            if (adj[v] >> u) & 1:
                cnf.append([-vp.id(("v", v)), -vp.id(("v", u))])
    lits = [vp.id(("v", v)) for v in range(N)]
    card = CardEnc.atleast(lits=lits, bound=k, encoding=EncType.seqcounter, vpool=vp)
    for cl in card.clauses:
        cnf.append(cl)
    with Cadical153(bootstrap_with=cnf.clauses) as s:
        r = s.solve()
    return r

rows = []
for name, rel in WITS:
    w = Wit(os.path.join(ROOT, rel))
    for c in (0, 1, 2, 3):
        N, adj = graph_for_colour(w, c)
        a, _ = max_inset(adj, N)
        r_hi = sat_inset(adj, N, a + 1, False)
        r_lo = sat_inset(adj, N, a, True)
        ok = (r_hi is False) and (r_lo is True)
        row = {"witness": name, "colour": c, "alpha": a,
               "SAT_at_alpha+1": r_hi, "SAT_at_alpha": r_lo, "agrees": ok}
        rows.append(row)
        print(json.dumps(row), flush=True)
        assert ok, row
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "crosscheck.json"), "w"), indent=1)
print("ALL AGREE")
