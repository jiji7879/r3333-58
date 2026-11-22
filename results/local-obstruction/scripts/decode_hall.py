"""Decode the maximum colour-0 independent sets; verify them directly from the
witness file (no graph object reused) and print an explicit Hall violation."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wit import Wit
from mis import max_inset

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"
WITS = [
 ("W1 pair58_Tminus", ".ultramath/smwr8io45/m6/wit/pair58_Tminus.wit"),
 ("W2 L_58", ".ultramath/smwr8io45/m6/wit/L_58.wit"),
 ("W3 pair58_Tminus_recoloured", ".ultramath/smwr8io45/m4/pair58_Tminus_recoloured.wit"),
 ("W4 p58", ".ultramath/smwrfgma5/m4/wit/p58.wit"),
 ("W5 p58_cc", ".ultramath/smwrfgma5/m4/wit/p58_cc.wit"),
]

def direct_zero(w, u, v):
    """Colour of edge {u,v} at the branch level, or None if not determined.
    Vertices: ('a',i) i in 0..n-1, ('x',label), ('r',)."""
    n = w.n_arm()
    if u == ('r',) or v == ('r',):
        o = v if u == ('r',) else u
        return 0 if o[0] == 'a' else None
    if u[0] == 'a' and v[0] == 'a':
        return None
    if u[0] == 'x' and v[0] == 'x':
        a, b = sorted([u[1], v[1]])
        return w.pairs.get((a, b))
    if u[0] == 'x':
        u, v = v, u
    # u = ('a', i), v = ('x', lab)
    return w.words[v[1]][u[1]]

for name, rel in WITS:
    w = Wit(os.path.join(ROOT, rel))
    n = w.n_arm(); xs = w.nouts(); m = len(xs); r = n + m; N = n + m + 1
    idx = {x: i for i, x in enumerate(xs)}
    adj = [0] * N
    def add(u, v):
        adj[u] |= 1 << v; adj[v] |= 1 << u
    for a in range(n): add(r, a)
    for i, x in enumerate(xs):
        for a in range(n):
            if w.words[x][a] == 0: add(n + i, a)
    for (x, y), f in w.pairs.items():
        if f == 0: add(n + idx[x], n + idx[y])
    alpha, mask = max_inset(adj, N)
    W = [v for v in range(N) if (mask >> v) & 1]
    def lab(v):
        if v < n: return ('a', v)
        if v < n + m: return ('x', xs[v - n])
        return ('r',)
    labs = [lab(v) for v in W]
    # independent check straight from the witness file
    bad = 0
    for i in range(len(labs)):
        for j in range(i + 1, len(labs)):
            if direct_zero(w, labs[i], labs[j]) == 0:
                bad += 1
    from collections import Counter
    cnt = Counter(t[0] for t in labs)
    print("%-30s alpha0=%2d  composition A/X/r = %d/%d/%d  bad 0-edges in W = %d"
          % (name, alpha, cnt['a'], cnt['x'], cnt['r'], bad))
    # explicit Hall violation: I = first 15 of W, J = W, S = W \ I
    I = labs[:15]; J = labs; S = labs[15:]
    if len(S) < 2:
        print("   (no 2-element violation from this W)"); continue
    Nb = set()
    for s in S:
        for y in I:
            if direct_zero(w, s, y) == 0:
                Nb.add(y)
    marg = len(S) - 1 - len(Nb)
    print("   violation: |I|=%d |J|=%d |S|=%d  |N0(S) cap I| = %d  needs >= %d  margin = %d"
          % (len(I), len(J), len(S), len(Nb), len(S) - 1, marg))
    print("   I = %s" % (I,))
    print("   S = %s" % (S,))
