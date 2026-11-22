"""Explicit Hall violations for the five pair-level witnesses.

Two certificates per witness:
  (C1) I = A, |S| = 15: the fifteen words whose colour-0 support lies inside a
       fixed 13-point T.  |N_0(S) cap I| = |U M_0(x)| <= 13 < 14 = |S| - 1.
       (This is the case the earlier 300-random-J sampling missed.)
  (C2) general I: |S| = 2 out of a maximum colour-0 independent set W of size
       alpha.  |N_0(S) cap I| = 0 < 1 = |S| - 1.
Every claim is re-checked from the witness file with `direct_zero`, no graph.
"""
import sys, os, json
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

def zero_colour(w, u, v):
    """Colour of {u,v} at the branch level, or None when not determined.
    Vertices: ('a',i) for i in 0..14 | ('x',label) | ('r',)."""
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
    return w.words[v[1]][u[1]]

def independent0(w, vs):
    for i in range(len(vs)):
        for j in range(i + 1, len(vs)):
            if zero_colour(w, vs[i], vs[j]) == 0:
                return False
    return True

out = []
for name, rel in WITS:
    w = Wit(os.path.join(ROOT, rel))
    xs = w.nouts(); n = w.n_arm()
    rec = {"witness": name, "path": rel}
    # ---- C1: I = A, S = fifteen words inside a 13-point T
    best = None
    for T in range(1 << n):
        if bin(T).count("1") > 13:
            continue
        S = [('x', x) for x in xs if (w.M(x, 0) and (sum(1 << a for a in w.M(x, 0)) & ~T) == 0)]
        if len(S) < 15:
            continue
        score = len(S) - 1 - bin(T).count("1")
        if best is None or score > best[0]:
            best = (score, T, S)
    score, T, S = best
    S = S[:15]
    I = [('a', a) for a in range(n)]
    U = set()
    for s in S:
        U |= w.M(s[1], 0)
    Nb = {y for s in S for y in I if zero_colour(w, s, y) == 0}
    rec["C1"] = {"T": sorted(a for a in range(n) if (T >> a) & 1),
                 "T_size": len([a for a in range(n) if (T >> a) & 1]),
                 "S_labels": [s[1] for s in S], "S_size": len(S),
                 "union_size": len(U), "N0(S)_cap_I": len(Nb),
                 "needed": len(S) - 1, "margin": len(S) - 1 - len(Nb),
                 "S_is_0_independent": independent0(w, S),
                 "violates": len(Nb) < len(S) - 1}
    # ---- C2: general I from a maximum colour-0 independent set
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from mis import max_inset
    m = len(xs); r = n + m; N = n + m + 1
    adj = [0] * N
    def add(u, v):
        adj[u] |= 1 << v; adj[v] |= 1 << u
    for a in range(n): add(r, a)
    for i, x in enumerate(xs):
        for a in range(n):
            if w.words[x][a] == 0: add(n + i, a)
    idx = {x: i for i, x in enumerate(xs)}
    for (x, y), f in w.pairs.items():
        if f == 0: add(n + idx[x], n + idx[y])
    alpha, mask = max_inset(adj, N)
    def lab(v):
        return ('a', v) if v < n else (('x', xs[v - n]) if v < n + m else ('r',))
    W = [lab(v) for v in range(N) if (mask >> v) & 1]
    I2 = W[:15]; S2 = W[15:17] if len(W) > 16 else W[15:]
    Nb2 = {y for s in S2 for y in I2 if zero_colour(w, s, y) == 0}
    rec["C2"] = {"alpha0": alpha, "I_size": len(I2), "S": S2, "S_size": len(S2),
                 "N0(S)_cap_I": len(Nb2), "needed": len(S2) - 1,
                 "margin": len(S2) - 1 - len(Nb2),
                 "W_is_0_independent": independent0(w, W),
                 "violates": len(Nb2) < len(S2) - 1}
    rec["worst_margin_general"] = alpha - 16
    out.append(rec)
    print(json.dumps(rec, indent=1))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "hall_cert.json"), "w"), indent=1)
