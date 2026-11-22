"""The branch model and an independent checker.  Member m8, swarm smwrmwgf7.

Setting (fixed by review/PROFILE_15141414_STATE.md; nothing here derives it).
A triangle-free 4-edge-colouring of K_58 with a root r of profile
(15,14,14,14) and in the *uniform fully-sending* child:

  A = N_0(r)          (15 vertices)   arm B = N_1(r), C = N_2(r), D = N_3(r)
  X = B u C u D       (42 vertices)   V = {r} u A u X

  * no colour-0 edge inside A (it would close a colour-0 triangle with r), so
    the 3-colouring of K(A) uses the campaign colours 1,2,3 and is T15 or U15
    (kernel-checked classification).  Fix a labelled T15 representative.
  * a word: for x in X, W_x : A -> {0,1,2,3}, W_x(a) = colour(x,a).
      - m(x) = 5: exactly five zeros                                (Z)
      - for f in 1..3, M_f(x) = {a : W_x(a) = f} carries no f-edge of A,
        since a-f-a'-x would be a monochromatic triangle             (I)
  * d_0(a) = 15 for every a in A, and r is one of them: every a has exactly
    fourteen colour-0 partners in X = B u C u D.                    (P)
  * L1 / mixture (kernel-checked, K58.mixture): |N_f(x) cap N_g(u)| <= 5 for
    f != g.  With u = r this gives, for every a in A and every arm P,
    s_P(a) := |N_0(a) cap P| <= 5.                                  (M)
  * no monochromatic triangle anywhere.                             (T)

Consequences used as *clauses* (each implied by the above; the proof is in the
comment next to it):

  (C1) s_B(a), s_C(a), s_D(a) <= 5 by (M) and they sum to 14 by (P), so each
       lies in {4,5}; in particular s_B(a) + s_C(a) in {9,10}.  The whole
       point of this file: at two arms the branch still forces the *sum*.
  (C2) t_P(x) := |N_0(x) cap P| <= 5 for every x in X and every arm P, again
       by (M) with u = r (x is in some arm, r is the root).
  (C3) no 6 vertices of an arm are f-free for an allowed colour f: on such a
       six-set every edge has one of the other two colours and R(3,3) = 6
       gives a monochromatic triangle, contradicting (T).

A two-arm model is: words on B u C, pair colours p(x,y) for every pair, and
the constraints above restricted to B u C (the third arm is projected out;
(C1) is exactly what survives of it).
"""
import itertools

# ---------------------------------------------------------------- template

_DC = {1: 0, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 1, 8: 0, 9: 2, 10: 0, 11: 1,
       12: 0, 13: 1, 14: 2}
_TRADE = {21, 22, 28, 31, 37, 38, 44, 47, 88, 91, 104, 107, 140, 143, 188, 191}
_SWAP01 = {0: 0, 1: 2, 2: 1}


def lean_template(n, twisted):
    """Lean's K58.template n twisted (Templates.lean), file/campaign colour
    0,1,2 -> campaign 1,2,3 done by the caller through +1."""
    M = [[0] * n for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            x = _DC.get(u ^ v, 0)
            if twisted and (16 * min(u, v) + max(u, v)) in _TRADE:
                x = _SWAP01[x]
            M[u][v] = M[v][u] = x
    return M


def template_colours(n, twisted):
    """campaign-coloured template: colour 1,2,3 = file colours 0,1,2."""
    F = lean_template(n, twisted)
    return [[(0 if u == v else F[u][v] + 1) for v in range(n)] for u in range(n)]


def template_edges(M):
    n = len(M)
    return {f: [(a, b) for a in range(n) for b in range(a + 1, n) if M[a][b] == f]
            for f in (1, 2, 3)}


# ---------------------------------------------------------------- checking

def check_two_arm(M, arms, words, pairs, verbose=False):
    """Check a two-arm model from the definition.  Returns a list of failures.

    M       campaign-coloured 15x15 template on A = 0..14
    arms    {1: [slot ids of arm B], 2: [slot ids of arm C]}
    words   {slot: tuple of 15 values in 0..3}
    pairs   {(x,y) with x<y: colour in 0..3}
    Checks Z, I, P/C1, M/C2, pair rule, arm module, cross module, C3.
    """
    n = len(M)
    E = template_edges(M)
    bad = []
    X = list(words)
    armour = {}
    for c, vs in arms.items():
        for v in vs:
            if v in armour:
                bad.append(("slot in two arms", v))
            armour[v] = c
    if sorted(armour) != sorted(X):
        bad.append(("arm partition != slot set", sorted(armour), sorted(X)))
    # Z, I
    for v in X:
        w = words[v]
        if len(w) != n or any(c not in (0, 1, 2, 3) for c in w):
            bad.append(("word shape", v))
            continue
        if w.count(0) != 5:
            bad.append(("Z: not five zeros", v, w.count(0)))
        for f in (1, 2, 3):
            for a, b in E[f]:
                if w[a] == f and w[b] == f:
                    bad.append(("I: word part not independent", v, f, (a, b)))
    # P: coverage per arm point, per arm, and the sum
    two_full_arms = len(arms.get(1) or []) == 14 and len(arms.get(2) or []) == 14
    for a in range(n):
        sB = sum(1 for v in arms.get(1) or [] if words[v][a] == 0)
        sC = sum(1 for v in arms.get(2) or [] if words[v][a] == 0)
        if arms.get(1) and not (4 <= sB <= 5):
            bad.append(("C1: s_B(a) not in {4,5}", a, sB))
        if arms.get(2) and not (4 <= sC <= 5):
            bad.append(("C1: s_C(a) not in {4,5}", a, sC))
        if two_full_arms and not (9 <= sB + sC <= 10):
            bad.append(("C1: s_B+s_C not in {9,10}", a, sB, sC))
    # pair rule
    for x, y in itertools.combinations(X, 2):
        if (x, y) not in pairs:
            bad.append(("missing pair colour", (x, y)))
            continue
        f = pairs[(x, y)]
        if armour[x] == armour[y] == f:
            bad.append(("pair rule: shared arm colour", (x, y), f))
        Mf = [a for a in range(n) if words[x][a] == f]
        Mg = [a for a in range(n) if words[y][a] == f]
        if set(Mf) & set(Mg):
            bad.append(("pair rule: parts not disjoint", (x, y), f, sorted(set(Mf) & set(Mg))))
    # C2: colour-0 caps per slot and per arm
    for v in X:
        for c, vs in arms.items():
            t = sum(1 for u in vs if u != v and pairs[(min(u, v), max(u, v))] == 0)
            if t > 5:
                bad.append(("C2: slot colour-0 degree in an arm > 5", v, c, t))
        tA = words[v].count(0)
        if tA != 5:
            bad.append(("C2: slot colour-0 degree into A != 5", v, tA))
    # T: arm modules
    for c, vs in arms.items():
        for tri in itertools.combinations(vs, 3):
            f = [pairs[(min(u, v), max(u, v))] for u, v in itertools.combinations(tri, 2)]
            if f[0] == f[1] == f[2]:
                bad.append(("T: monochromatic triangle inside an arm", c, tri, f[0]))
    # T: cross-arm modules (2 + 1)
    for a1, a2 in ((1, 2), (2, 1)):
        for pair in itertools.combinations(arms[a1], 2):
            for y in arms[a2]:
                t = tri = (pair[0], pair[1], y)
                f = [pairs[(min(u, v), max(u, v))] for u, v in itertools.combinations(tri, 2)]
                if f[0] == f[1] == f[2]:
                    bad.append(("T: monochromatic cross-arm triangle", tri, f[0]))
    # C3: 6-sets of an arm are never f-free
    for c, vs in arms.items():
        allowed = [f for f in range(4) if f != c]
        for S in itertools.combinations(vs, 6):
            for f in allowed:
                if all(pairs[(min(u, v), max(u, v))] != f for u, v in itertools.combinations(S, 2)):
                    bad.append(("C3: f-free six-set", c, S, f))
    if verbose:
        print(f"checked {len(X)} slots, {len(pairs)} pairs, {len(bad)} failures")
    return bad


def read_witness(path):
    tpl, arms, words, pairs = None, {}, {}, {}
    for line in open(path):
        t = line.split()
        if not t or t[0].startswith("#"):
            continue
        if t[0] == "template":
            tpl = t[1]
        elif t[0] == "arm":
            arms[int(t[1])] = list(map(int, t[2:]))
        elif t[0] == "word":
            words[int(t[1])] = tuple(map(int, t[2:]))
        elif t[0] == "pair":
            pairs[(int(t[1]), int(t[2]))] = int(t[3])
        else:
            raise ValueError(line)
    return tpl, arms, words, pairs
