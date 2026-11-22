"""The I = A case, decided exactly, over *all* S (no size cap, no sampling).

With I = A the Hall inequality is  |U_{x in S} M_0(x)| >= |S| - 1  for every
S subset of the outside vertices, where M_0(x) = {a in A : word_x(a) = 0} has
|M_0(x)| = 5.  Write c(T) = #{x : M_0(x) subset of T}.  Then

    (forall S)  |U M_0(x)| >= |S| - 1     <=>     (forall T subset of A) c(T) <= |T| + 1

  (=>) S = {x : M_0(x) subset T} has |U| <= |T|.
  (<=) T = U_{x in S} M_0(x) contains all of S.

So the test over all S is a zeta transform over 2^15 = 32768 subsets: every one of
the 2^42 subsets S is covered, with no sampling.

CAUTION.  This transformation drops one hypothesis: S must itself be colour-0
independent (it is a subset of the colour-0 independent set J).  So the numbers
printed here (max over |T| <= 13 of c(T) - |T| - 1, i.e. 7..10) are an UPPER bound
on the I = A margin, not the answer.  The exact value, with 0-independence
enforced, is computed in `hall_exact.py` by maximising min(alpha(G_0[P(T)]),15) - 1
- |T| over all T, and is 2 for every witness.
"""
import sys, os, json
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
res = []
for name, rel in WITS:
    w = Wit(os.path.join(ROOT, rel))
    n = w.n_arm(); xs = w.nouts()
    cnt = [0] * (1 << n)
    for x in xs:
        m = 0
        for a, c in enumerate(w.words[x]):
            if c == 0:
                m |= 1 << a
        cnt[m] += 1
    # zeta transform: cnt[T] = #{x : M_0(x) subset of T}
    z = cnt[:]
    for b in range(n):
        bit = 1 << b
        for T in range(1 << n):
            if T & bit:
                z[T] += z[T ^ bit]
    # the size cap: S subset of J\I with |J| = 15 forces |S| <= 15, and the
    # argument needs |S| = |T| + 2, so only |T| <= 13 can violate.
    cand = [T for T in range(1 << n) if bin(T).count("1") <= 13]
    worst = max(z[T] - bin(T).count("1") - 1 for T in cand)
    arg = max(cand, key=lambda T: z[T] - bin(T).count("1") - 1)
    worst_nocap = max(z[T] - bin(T).count("1") - 1 for T in range(1 << n))
    # also: max margin |S|-1-|U| over S, which equals max_T (c(T)-1-|T|)
    row = {"witness": name, "max_over_T<=13(c(T)-|T|-1)": worst,
           "max_over_all_T_nocap": worst_nocap,
           "argmax_T": arg, "argmax_T_size": bin(arg).count("1"), "c(argmax)": z[arg],
           "I=A_ever_violated": worst > 0,
           "support_multiplicities": sorted(set(cnt))[1:] if False else None}
    # multiplicities of supports
    from collections import Counter
    mult = Counter(w.M(x, 0) for x in xs)
    row["distinct_supports"] = len(mult)
    row["max_support_multiplicity"] = max(mult.values())
    res.append(row)
    print(json.dumps(row))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "hall_IA.json"), "w"), indent=1)
