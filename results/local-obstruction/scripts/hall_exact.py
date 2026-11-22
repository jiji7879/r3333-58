"""The Hall test, decided exactly, with the true size cap.

Statement (from .scratch/pent/README.md, with the proof made explicit here):
  I a colour-0 independent 15-set, J a colour-0 independent set, S subset of
  J \\ I  ==>  |N_0(S) cap I| >= |S| - 1.
  Proof: (I \\ N_0(S)) u S is colour-0 independent (S is, I is, and no element of
  S is 0-adjacent to a surviving element of I), so its size is <= alpha(G_0) <= 16
  (a 17-set with no 0-edge would be a triangle-free 3-colouring of K_17, and
  R(3,3,3) = 17).  Size = 15 - |N_0(S) cap I| + |S|.

Consequences used here.  Since |J| = 15, always |S| <= 15, and the exchange set
has size 15 - |N_0(S) cap I| + |S| = 16 + margin with
margin = |S| - 1 - |N_0(S) cap I|.  Hence

  (i)  margin <= alpha(G_0) - 16,
  (ii) margin <= 15 - 1 = 14            (cap |S| <= 15, I cap N_0(S) >= 0),
  (iii) the bound min(alpha(G_0), 30) - 16 is attained: take a colour-0
        independent W with |W| = min(alpha_0, 30), I any 15 of it, S the rest.

So the exhaustive answer is a closed form, and each witness is decided by its
alpha(G_0) alone.  The per-witness maximum is recomputed below by an independent
explicit search (max over T of min(alpha(G_0[P(T)]),15) - 1 - |T|, T subset of A)
for the restricted case I = A.
"""
import sys, os, json
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

def zero_colour(w, u, v):
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

def int_adj(w, colour):
    n = w.n_arm(); xs = w.nouts(); m = len(xs); r = n + m; N = n + m + 1
    adj = [0] * N
    def add(u, v):
        adj[u] |= 1 << v; adj[v] |= 1 << u
    if colour == 0:
        for a in range(n): add(r, a)
    for i, x in enumerate(xs):
        for a in range(n):
            if w.words[x][a] == colour: add(n + i, a)
    idx = {x: i for i, x in enumerate(xs)}
    for (x, y), f in w.pairs.items():
        if f == colour: add(n + idx[x], n + idx[y])
    return N, adj

rows = []
for name, rel in WITS:
    w = Wit(os.path.join(ROOT, rel))
    n = w.n_arm(); xs = w.nouts(); m = len(xs); r = n + m; N = n + m + 1
    idx = {x: i for i, x in enumerate(xs)}
    Nv, adj = int_adj(w, 0)
    alpha, mask = max_inset(adj, Nv)
    lab = lambda v: ('a', v) if v < n else (('x', xs[v - n]) if v < n + m else ('r',))
    W = [lab(v) for v in range(Nv) if (mask >> v) & 1]
    assert independent0(w, W)
    # attained margin, general I
    k = min(alpha, 30)
    Wk = W[:k]
    I = Wk[:15]; S = Wk[15:]
    Nb = {y for s in S for y in I if zero_colour(w, s, y) == 0}
    gen_margin = len(S) - 1 - len(Nb)
    # restricted to I = A: max over T of min(alpha(G0[P(T)]),15) - 1 - |T|, |T| <= 13
    best_IA = None
    for T in range(1 << n):
        tsz = bin(T).count("1")
        if tsz > 13:
            continue
        P = [n + i for i, x in enumerate(xs) if all((T >> a) & 1 for a in w.M(x, 0))]
        if not P:
            continue
        pm = 0
        for v in P:
            pm |= 1 << v
        sub = [v for v in P]
        # alpha of the induced graph on P
        # (remap for max_inset)
        remap = {v: j for j, v in enumerate(sub)}
        subadj = [0] * len(sub)
        for v in sub:
            b = adj[v] & pm
            j = remap[v]
            for u in sub:
                if (b >> u) & 1:
                    subadj[j] |= 1 << remap[u]
        aP, _ = max_inset(subadj, len(sub))
        sc = min(aP, 15) - 1 - tsz
        if best_IA is None or sc > best_IA[0]:
            best_IA = (sc, T, aP, len(P))
    row = {
        "witness": name,
        "alpha0": alpha,
        "alpha0_mod30_cap": k,
        "max_margin_general": gen_margin,
        "predicted_min(alpha0,30)-16": k - 16,
        "I": I, "S": S, "N0S_cap_I": len(Nb), "S_0_independent": independent0(w, S),
        "Wk_0_independent": independent0(w, Wk),
        "max_margin_I_eq_A": best_IA[0],
        "argmax_T_size": bin(best_IA[1]).count("1"),
        "argmax_alpha_of_pool": best_IA[2], "pool_size": best_IA[3],
        "argmax_T": sorted(a for a in range(n) if (best_IA[1] >> a) & 1),
    }
    assert gen_margin == k - 16, row
    rows.append(row)
    print(json.dumps(row))
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "hall_exact.json"), "w"), indent=1)
