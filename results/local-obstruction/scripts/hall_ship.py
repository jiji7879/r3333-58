"""Emit the two explicit Hall certificates per witness and re-verify them from
the witness file alone (no shared code with the search)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wit import Wit
from mis import max_inset

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

def zc(w, u, v):
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

def indep0(w, vs):
    return all(zc(w, vs[i], vs[j]) != 0
               for i in range(len(vs)) for j in range(i + 1, len(vs)))

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

certs = []
for name, rel in WITS:
    w = Wit(os.path.join(ROOT, rel))
    n = w.n_arm(); xs = w.nouts(); m = len(xs); r = n + m; N = n + m + 1
    idx = {x: i for i, x in enumerate(xs)}
    Nv, adj = int_adj(w, 0)
    alpha, mask = max_inset(adj, Nv)
    lab = lambda v: ('a', v) if v < n else (('x', xs[v - n]) if v < n + m else ('r',))
    W = [lab(v) for v in range(Nv) if (mask >> v) & 1]
    assert indep0(w, W) and len(W) == alpha
    # ---- general certificate, |S| = 15, margin 14
    Wk = W[:min(alpha, 30)]
    I, S = Wk[:15], Wk[15:]
    assert len(S) == 15
    Nb = {y for s in S for y in I if zc(w, s, y) == 0}
    c_gen = {"I": I, "J": W, "S": S, "N0S_cap_I": len(Nb),
             "margin": len(S) - 1 - len(Nb)}
    # ---- I = A certificate
    best = None
    for T in range(1 << n):
        tsz = bin(T).count("1")
        if tsz > 13:
            continue
        P = [n + i for i, x in enumerate(xs) if all((T >> a) & 1 for a in w.M(x, 0))]
        if len(P) < 15:
            continue
        pm = 0
        for v in P:
            pm |= 1 << v
        sub = list(P); remap = {v: j for j, v in enumerate(sub)}
        subadj = [0] * len(sub)
        for v in sub:
            b = adj[v] & pm
            j = remap[v]
            for u in sub:
                if (b >> u) & 1:
                    subadj[j] |= 1 << remap[u]
        aP, Pmask = max_inset(subadj, len(sub))
        if aP < 15:
            continue
        sc = min(aP, 15) - 1 - tsz
        if best is None or sc > best[0]:
            best = (sc, T, [sub[j] for j in range(len(sub)) if (Pmask >> j) & 1])
    sc, T, pool = best
    S2 = [lab(v) for v in pool[:15]]
    I2 = [('a', a) for a in range(n)]
    assert indep0(w, S2), "pool not 0-independent"
    U = set()
    for s in S2:
        U |= w.M(s[1], 0)
    Nb2 = {y for s in S2 for y in I2 if zc(w, s, y) == 0}
    c_IA = {"T": sorted(a for a in range(n) if (T >> a) & 1), "T_size": bin(T).count("1"),
            "I": I2, "J": S2, "S": S2, "union_size": len(U),
            "N0S_cap_I": len(Nb2), "margin": len(S2) - 1 - len(Nb2)}
    certs.append({"witness": name, "path": rel, "alpha0": alpha,
                  "alpha0_all_colours": None,
                  "max_possible_margin_theory": min(alpha, 30) - 16,
                  "cert_general": c_gen, "cert_I_eq_A": c_IA})
    print("%-30s alpha0=%2d  general margin=%2d |S|=%d   I=A margin=%d |S|=%d |T|=%d"
          % (name, alpha, c_gen["margin"], len(S), c_IA["margin"], len(S2), c_IA["T_size"]))
json.dump(certs, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "hall_certificates.json"), "w"), indent=1)
print("written out/hall_certificates.json")
