"""Hall verdict for every .wit in the campaign that has a complete colour-0 graph."""
import sys, os, glob, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wit import Wit
from mis import max_inset

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"

def graph0(w):
    n = w.n_arm(); xs = w.nouts(); m = len(xs); r = n + m; N = n + m + 1
    need = all((min(x, y), max(x, y)) in w.pairs for x, y in itertools.combinations(xs, 2))
    if not need:
        return None, None
    adj = [0] * N
    def add(u, v):
        adj[u] |= 1 << v; adj[v] |= 1 << u
    for a in range(n):
        add(r, a)
    for i, x in enumerate(xs):
        for a in range(n):
            if w.words[x][a] == 0:
                add(n + i, a)
    idx = {x: i for i, x in enumerate(xs)}
    for (x, y), f in w.pairs.items():
        if f == 0:
            add(n + idx[x], n + idx[y])
    return N, adj

rows = []
paths = sorted(set(glob.glob(os.path.join(ROOT, ".ultramath", "*", "*", "wit", "*.wit")) +
                    glob.glob(os.path.join(ROOT, ".ultramath", "*", "*", "*.wit")) +
                    glob.glob(os.path.join(ROOT, "artifacts", "*.col")) ))
for p in paths:
    if p.endswith(".col"):
        toks = open(p).read().split()
        n, k = int(toks[0]), int(toks[1])
        vals = list(map(int, toks[2:2 + n * n]))
        M = [vals[i * n:(i + 1) * n] for i in range(n)]
        alphas = []
        for c in range(k):
            adj = [0] * n
            for i in range(n):
                for j in range(n):
                    if i != j and M[i][j] == c:
                        adj[i] |= 1 << j
            a, _ = max_inset(adj, n)
            alphas.append(a)
        rows.append({"file": os.path.relpath(p, ROOT), "kind": "real colouring",
                     "n": n, "alphas": alphas, "hall_violated": max(alphas[:1]) > (16 if n >= 17 else n) if False else None})
        continue
    try:
        w = Wit(p)
    except Exception:
        continue
    N, adj = graph0(w)
    if N is None:
        continue
    a, _ = max_inset(adj, N)
    # the vacuous-free margin: min(alpha, 30) - 16 when |S| <= 15 and |I| = 15
    marg = min(a, 30) - 16
    rows.append({"file": os.path.relpath(p, ROOT), "kind": "pair-level witness",
                 "n": N, "alpha0": a, "hall_max_margin": marg,
                 "hall_violated": marg > 0})
    print("%-62s n=%d alpha0=%2d  max Hall margin %2d  %s"
          % (os.path.relpath(p, ROOT), N, a, marg, "VIOLATED" if marg > 0 else "holds"))
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "hall_all.json"), "w"), indent=1)
