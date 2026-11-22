import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wit import Wit
from mis import max_inset

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"
WITS = [
 ("W1 pair58_Tminus", ".ultramath/smwr8io45/m6/wit/pair58_Tminus.wit"),
 ("W2 L_58 (byte-identical to W1)", ".ultramath/smwr8io45/m6/wit/L_58.wit"),
 ("W3 pair58_Tminus_recoloured", ".ultramath/smwr8io45/m4/pair58_Tminus_recoloured.wit"),
 ("W4 p58", ".ultramath/smwrfgma5/m4/wit/p58.wit"),
 ("W5 p58_cc", ".ultramath/smwrfgma5/m4/wit/p58_cc.wit"),
]

def graph_for_colour(w, c):
    """Adjacency masks of the colour-c graph on A | X | r."""
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

rows = []
for name, rel in WITS:
    w = Wit(os.path.join(ROOT, rel))
    errs = w.check()
    N, adj0 = graph_for_colour(w, 0)
    a0, mask0 = max_inset(adj0, N)
    # A itself is a 0-independent 15-set
    Amask = (1 << w.n_arm()) - 1
    okA = all((adj0[a] & Amask) == 0 for a in range(w.n_arm()))
    line = {"witness": name, "path": rel, "parse_errors": len(errs),
            "alpha0": a0, "alpha0_witness_mask": mask0,
            "A_is_0_independent": okA}
    for c in (1, 2, 3):
        _, adjc = graph_for_colour(w, c)
        ac, _ = max_inset(adjc, N)
        line["alpha%d" % c] = ac
    rows.append(line)
    print(json.dumps(line))
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "alpha.json"), "w"), indent=1)
