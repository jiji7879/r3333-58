# m3 — direction d9: recolouring (Kempe) invariance at the wall profile

**Status: PARTIAL. No lemma here kills family A or family B; nothing here decides
W2(15,14,14,14).** What is delivered: two proved tools that both family attacks need,
each machine-checked on every artefact (a *Kempe invariance* theorem, and the *link
lemma* with its wall-profile corollary that supplies exactly the "allowed
(d_1,d_2,d_3) for u" that d1 asked for), one proved no-go (Kempe normalisation can
pin the critical colour's edge count on either side of the average, so no argument of
that shape can work), and one abandoned direction with its refutation (the "tickets
balance inside each critical class" idea — it is vacuous).

Everything below is derived only from `R(3,3) = 6`, `R(3,3,3) = 17`,
`sum_c d_c(v) = n-1` and the definitions in the problem statement. Every claim that is
a statement about a particular colouring has been checked on the artefacts with the
scripts named; the commands to rerun are in §7.

---

## 1. Definitions used (as in the problem statement)

For a 4-colouring of the edges of `K_n`: `d_c(v) = |N_c(v)|`; colour `c` is critical at
`v` iff `d_c(v) >= 15`; `w(v)` = sum of the critical `d_c(v)`;
`s_c(v) = #{u in N_c(v) : d_c(u) >= 15}`; `H(v) = sum_c s_c(v)`.

Two arithmetic facts used throughout (both elementary):

* **(A1)** For every `v`, `sum_c d_c(v) = n-1`, and `d_c(v) <= 16` if `n` is such that
  `N_c(v)` can be 3-coloured (always: `N_c(v)` is coloured by the other three colours
  and has no monochromatic triangle, so `d_c(v) <= R(3,3,3) - 1 = 16`).
* **(A2)** At `n = 58`: `w(v) >= 15` for every `v`, and `w(v) = 15` **iff** the profile
  of `v` is exactly `(15,14,14,14)`. Indeed `57 = 4*14 + 1`, so some critical colour
  has degree `>= 15`; if `w(v) = 15` the critical part is a single colour of degree
  exactly 15 and the other three degrees sum to `42` with each `<= 14`, hence each is
  exactly 14. Conversely `(15,14,14,14)` has `w = 15`. So
  **the wall profile is the unique minimum of `w`**, and `57 - 15 = 42 = 3*14` (the
  three non-critical degrees are *equal*) holds only at `n = 58`, never at `n <= 57`.

---

## 2. Tool 1 — Kempe invariance (proved; machine-checked)

Let `C` be a colouring of `K_n` with no monochromatic triangle, `c != c'` two colours,
and `X` a connected component of the subgraph spanned by the `c`- and `c'`-coloured
edges. The **Kempe swap on `X`** exchanges `c` and `c'` on `X`.

**Theorem 1 (invariance).** *After the swap:*

* *(a) the colouring still has no monochromatic triangle;*
* *(b) for every vertex `v` the multiset `{(d_a(v), s_a(v)) : a = 0..3}` is unchanged
  (in particular `w(v)` and `H(v)` are unchanged);*
* *(c) for every vertex `v` the multiset of arms `{N_a(v) : a}` is unchanged as a
  multiset of vertex sets.*

*Proof.* (a) Let `T = {a,b,t}` be a triangle and count `|T cap X|`.
0 in `X`: unchanged. 1 in `X` (say `a in X`): the two edges at `a` leave `X`, so their
colours are not in `{c,c'}` (a `c`- or `c'`-edge at `a` stays inside `X`); the edge
`bt` is untouched; no edge of `T` changes. 2 in `X` (`a,b in X`, `t` not): both cross
edges `at`, `bt` have colours outside `{c,c'}`, so they are untouched and cannot equal
each other *and* `ab` in a way that changes: if `colour(ab) in {c,c'}`, mono is
impossible (the cross colours are outside `{c,c'}`) both before and after; if
`colour(ab)` is outside `{c,c'}`, all three edges are untouched. 3 in `X`: the swap
acts on the three colours by the transposition `(c c')`, which preserves "all equal".
So no triangle becomes monochromatic.

(b) If `v in X`: every `c`- or `c'`-neighbour of `v` lies in `X`, so after the swap the
set of `c`-neighbours of `v` is the old set of `c'`-neighbours and vice versa; likewise
for every `u in X` the degrees `d_c(u)`, `d_{c'}(u)` are exchanged. Hence
`s_c(v) <-> s_{c'}(v)` and `s_a(v)` is unchanged for `a` not in `{c,c'}`, and the same
holds for `d`. If `v` is not in `X`: `v` has no `c`- or `c'`-neighbour in `X` (such an
edge would put `v` in `X`), so every neighbour of `v` keeps the colour of its edge to
`v`, and every neighbour `u in X` keeps all its degrees except `d_c, d_{c'}` — which
are not referred to by `v`'s `s`-values. So all pairs are unchanged. (c) is the
"neighbour sets" half of the same argument.

**Consequences.**

1. **W2 is invariant.** By Theorem 1(b), whether a vertex has profile multiset
   `{15,14,14,14}` and `H(v) >= 15` is unchanged by any Kempe swap and any colour
   permutation. So a colouring can be Kempe-normalised at will without creating or
   destroying a W2 witness: the whole case analysis of the cover is an intrinsic
   property of the colouring, not of the colour labelling.
2. **The cover's case data is canonical.** By 1(c), the multiset of arms at the root
   `r` — `{N_0(r), N_1(r), N_2(r), N_3(r)}` = `{A, B_1, B_2, B_3}` — is a Kempe
   invariant, and the pair `(|B_i|, s_i(r))` is invariantly attached to `B_i`. So
   "family A" (`s_0 = 15`, arms sender-free) versus "family B" (`s_0 >= 3`, `s_i >= 5`)
   is a property of the colouring up to recolouring, and no normalisation can move a
   colouring from one family to the other.
3. **Kempe normalisation is available to everyone on this board** as a sound first
   step: it changes the internal structure of the arms but never the ticket data.

*Machine check:* 40 random Kempe swaps per artefact (random walk in the orbit) on
`n48_z4z4_f0.col`, `k49_from_n48_m5.col`, `k50_z4z4_m6.col`,
`k50_blockcayley_Z4xZ4_m4.col`, `k50_sanity_f2.col`: triangle-freeness kept,
`{(d_a,s_a)}` kept at every vertex (0 violations), arm multisets kept at every vertex
(0 violations). See §7.

---

## 3. Tool 2 — the link lemma, and the wall-profile corollary

**Lemma 2 (link lemma).** *Let `d_c(v) >= 15`. Then `N_c(v)` is 3-coloured by the three
colours different from `c` with no monochromatic triangle, so `d_c(v) <= 16`; and for
every `u in N_c(v)` and every `a != c`, `|N_a(u) cap N_c(v)| <= 5`. The three numbers
`|N_a(u) cap N_c(v)|` (`a != c`) sum to `|N_c(v)| - 1`, hence they are a permutation of
`(5,5,4)` when `|N_c(v)| = 15` and of `(5,5,5)` when `|N_c(v)| = 16`.*

*Proof.* For `w, w' in N_a(u) cap N_c(v)` the triangle `u w w'` has two edges of colour
`a` and one of colour `colour(w,w') in {0..3} \ {a, c}` (it cannot be `a`, mono; it
cannot be `c`, since `w,w' in N_c(v)`); so `N_a(u) cap N_c(v)` is 2-coloured by the two
colours different from `a` and `c`, and therefore has no monochromatic triangle; by
`R(3,3) = 6` it has at most 5 vertices. The sum: `N_c(v) \ {u}` is partitioned by the
three sets `N_a(u) cap N_c(v)`, so the three numbers sum to `|N_c(v)| - 1`. `square`

**Corollary 3 (the wall profile read-off).** *Let `r` have profile `(15,14,14,14)`,
`A = N_0(r)`, `B_i = N_i(r)` (`|B_1| = |B_2| = |B_3| = 14`). For every `x in A` with
`d_0(x) >= 15` (a sender in colour 0), the triple*

  `( |N_0(x) cap B_1| , |N_0(x) cap B_2| , |N_0(x) cap B_3| )`

*is a permutation of `(5,5,4)` if `d_0(x) = 15`, and of `(5,5,5)` if `d_0(x) = 16`.
Consequently, if `S` is the set of senders in `A` and `u = #{x in S : d_0(x) = 16}`,
then each arm `B_i` receives exactly `4|S| + t_i` colour-0 edges from `S`, where
`0 <= t_i <= |S|` and `sum_i t_i = 2|S| + u`; in family A (`|S| = 15`) that is
`60 + t_i` with `sum_i t_i = 30 + u`, and `f_0(A,B) = 210 + u`.*

*Proof.* `N_0(x)` is `{r}` union `(N_0(x) cap B)` and has size `d_0(x) >= 15`, so it is a
link in the sense of Lemma 2; apply it with `v = x`, `c = 0` and `u = r`: `N_a(r) = B_a`
for `a = 1,2,3`, so `|N_0(x) cap B_a| = |N_a(r) cap N_0(x)| <= 5` for each `a`, and the
three numbers sum to `d_0(x) - 1` because `r in N_0(x)` and every other colour-0
neighbour of `x` lies in `B`. Then `d_0(x) - 1 = 14` forces `(5,5,4)` and `15` forces
`(5,5,5)`. The counts follow by summing over `x in S` (a `(5,5,5)`-type vertex
contributes 3 to `sum_i t_i`, a `(5,5,4)`-type contributes 2). `square`

This is exactly d1's "allowed `(d_1,d_2,d_3)` for `u`": the number of colour-0 edges a
sender puts into an arm is 4 or 5, never more, and the three numbers are rigidly tied.

**Corollary 3' (the dual read-off, for family B).** *If `y in B_i` sends in colour `i`
(`d_i(y) >= 15`), then, with `{j,k}` the two arms other than `B_i`,
`( |N_i(y) cap A| , |N_i(y) cap B_j| , |N_i(y) cap B_k| )` is a permutation of `(5,5,4)`
if `d_i(y) = 15` and of `(5,5,5)` if `d_i(y) = 16`.* In particular every sender of an
arm is joined in that colour to exactly **4 or 5** vertices of the 15-arm `A`, so a
family-B arm with `s_i >= 5` senders sends between `20` and `25` colour-`i` edges into
`A`, and a family-A root's arm (`s_i = 0`) still satisfies
`sum_{y in B_i} |N_i(y) cap A| >= 0` — the constraint that bites is the `>= 4` half,
which only applies at senders. *(Proof: Lemma 2 with `v = y`, `c = i`, `u = r`, and
`N_a(r) = B_a`; `r in N_i(y)` because `y in B_i`.)*

*Machine check (0 violations).* Every critical link in all three `K_50` files, in
`k49_from_n48_m5.col` and in `n48_z4z4_f0.col` was expanded: the maximum inner degree is
exactly 5 and the shapes are exactly `(5,5,4)` for `|N_c(v)| = 15` and `(5,5,5)` for 16
(e.g. `k50_z4z4_m6.col`: 555 and 224 vertex-link incidences). The four templates:
every vertex of `k15_template_Tminus_aut2_m4.col` and
`k15_template_Uminus_aut10_m4.col` has colour degrees `(5,5,4)`, every colour class has
exactly 35 edges and independence number 5; the two `K_16` templates have `(5,5,5)`,
40 edges per colour class and independence number 5. So m2's "`alpha = 5`, tight" holds
and is attained on both `K_15` templates.

---

## 4. A proved no-go: the Kempe trade-off

**Proposition 4.** *Fix a colour `c` and a colouring `C` of `K_n`. Over the Kempe orbit
of `C` (swaps plus colour permutations) the number `m_c` of colour-`c` edges can be made
both `<= C(n,2)/4` and `>= C(n,2)/4`. Concretely, there is a member with
`m_c <= floor(C(n,2)/4)` and one with `m_c >= ceil(C(n,2)/4)`; at `n = 58` that is
`413` and `414`.*

*Proof.* Minimise `m_c` over the orbit. For a component `X` of the `(c,d)`-subgraph,
swapping `X` changes `m_c` by `m_d(X) - m_c(X)`, so at a minimiser `m_d(X) >= m_c(X)`
for every `d != c` and every such `X`. Summing over `d` and over the components of the
`(c,d)`-subgraph: every colour-`c` edge lies in exactly one such component for each
`d`, so `m_1 + m_2 + m_3 >= 3 m_c`, and with `sum_d m_d = C(n,2)` this gives
`m_c <= C(n,2)/4`. Maximising gives the mirror inequality. `square`

**Consequence (a no-go).** "The critical colour of the wall vertex has at least (or at
most) the average number of edges" is *not* a Kempe-invariant restriction: recolouring
always produces members of the orbit in which the chosen colour has either `<= 413` or
`>= 414` edges at `n = 58`. So no argument of the form "count the edges of colour 0,
using that it is the critical colour" can yield a contradiction; any such bound is a
normalisation, not a constraint. (My §5 dead end is an instance of the same lesson.)

*Machine check.* Greedy descent to the minimum of `m_c` on all five artefacts: the
bound `m_c <= floor(C(n,2)/4)` is attained in every case (e.g. `n48_z4z4_f0.col`
`m = [360,256,256,256] -> 256`, bound `282`; `k50_blockcayley_Z4xZ4_m4.col`
`m = [377,282,282,284]`, bound `306`), and every intermediate colouring stays
triangle-free. See §7.

---

## 5. A dead end I registered and abandoned: per-class ticket balance is vacuous

I first tried (direction d6) to prove: *if every vertex of a `K_58` colouring has profile
`(15,14,14,14)` then, with `V_c = {v : c is the unique critical colour of v}`, no
colour-`c` edge leaves `V_c`* — which would force each `|V_c| >= 16` even and at most
three nonempty classes, `4*16 = 64 > 58`. **That derivation is wrong and the claim is
unproved.** The correction: `H(v) = sum_c |N_c(v) cap V_c|` counts neighbours critical
in the colour *that joins them to `v`*, over all four colours; so

  `sum_{v in V_c} H(v) = 2 e_c(V_c) + sum_{d != c} E_d(V_c, V_d)`,
  `sum_{v in V_c} w(v) = 15|V_c| = sum_{v in V_c} d_c(v) = 2 e_c(V_c) + sum_{d != c} E_c(V_c, V_d)`,

where `E_f(S,T)` is the number of colour-`f` edges between `S` and `T`. The ticket
identity equates these two sums only **after** summing over all classes, and then both
sides are the same double count — a tautology. There is no per-class balance, so the
class sizes are unconstrained at this level. Written up in `why_dead.md`. This is the
natural way to try to use T1 at the wall; it has no content, and anyone else reaching
for "the tickets balance at the root's critical class" should stop.

**Calibration that no uniform-in-`n` version of anything in this report can refute W2**
(measured here with `crit.py`): `n48_z4z4_f0.col` has all 48 vertices at profile
`(15,11,11,10)` — one critical colour each, `w = 15`, and `H = w = 15` at *every*
vertex, `sum_v H = sum_v w = 720`; `k49_from_n48_m5.col` has 36 vertices at
`(15,11,11,11)` with `H = w`, 12 at `(16,11,11,10)` with `H - w = -1`, and one at
`(12,12,12,12)` with `H - w = +12`; `k50_z4z4_m6.col` has 35 vertices at `(15,12,11,11)`
with `H - w = 0,1,2` in counts 8,12,15, 13 at `(16,11,11,11)` with `H - w = -1,0` in
counts 9,4, one at `(15,15,12,7)` (`H - w = -24`) and one at `(16,13,12,8)`
(`H - w = -9`); the other two `K_50` files behave the same way
(`k50_blockcayley_Z4xZ4_m4.col`: 32 at `(15,12,11,11)` with `H = w`, 16 at
`(16,11,11,11)` with `H - w = -1`). So "one critical colour, `w` minimal, `H >= w`" is
realisable at `n = 48, 49, 50`, and the only thing that distinguishes `n = 58` is
`57 - 15 = 42 = 3*14` (A2) together with the arm sizes `14,14,14`.

---

## 6. Where `n = 58` is used, and what is deliberately not claimed

* Theorem 1, Lemma 2 and Proposition 4 hold for every `n` and every threshold; they are
  *tools*, not steps of a kill, and I claim nothing about `R_4(3)` from them.
* `n = 58` enters only in (A2) (the wall profile is the unique minimum of `w`, using
  `57 = 4*14+1` and `d_c <= 16`) and in Corollary 3 through the arm sizes `14,14,14`.
* I make **no** claim that any of this decides W2, family A or family B.

---

## 7. Reproducing every check

All scripts are in this directory; run them from the repository root.

```
python3 .ultramath/smwqx1yfw/m3/crit.py artifacts/n48_z4z4_f0.col artifacts/k49_from_n48_m5.col \
        artifacts/k50_z4z4_m6.col artifacts/k50_blockcayley_Z4xZ4_m4.col artifacts/k50_sanity_f2.col
        # profiles, w, H, H-w distribution, ticket identity sum_v H = sum_v w
python3 .ultramath/smwqx1yfw/m3/tools_check.py artifacts/n48_z4z4_f0.col artifacts/k49_from_n48_m5.col \
        artifacts/k50_z4z4_m6.col artifacts/k50_blockcayley_Z4xZ4_m4.col artifacts/k50_sanity_f2.col
        # Tool 1 (Kempe invariance of {(d_c,s_c)} and of the arm multisets), Tool 2 (link lemma)
python3 .ultramath/smwqx1yfw/m3/templates.py artifacts/k15_template_Tminus_aut2_m4.col \
        artifacts/k15_template_Uminus_aut10_m4.col artifacts/k16_template_U_aut160_m4.col \
        artifacts/k16_template_T_aut32_m4.col
        # (5,5,4)/(5,5,5), 35/40 edges per colour class, alpha = 5
python3 .ultramath/smwqx1yfw/m3/kempe_tradeoff.py artifacts/n48_z4z4_f0.col artifacts/k49_from_n48_m5.col \
        artifacts/k50_z4z4_m6.col artifacts/k50_blockcayley_Z4xZ4_m4.col artifacts/k50_sanity_f2.col
        # Proposition 4, constructive side
```

Observed: `crit.py` — ticket identity `sum_v H = sum_v w` holds on all five files
(720/732/…), and the `H - w` distributions quoted in §5. `tools_check.py` — 0
violations on all files. `templates.py` — exactly `(5,5,4)`/`(5,5,5)`, 35/40 edges,
`alpha = 5`. `kempe_tradeoff.py` — bound attained in all five cases, colourings stay
triangle-free.

## 8. What I did not verify

* I did not verify the frozen ledger, the encoders or the two-family decode; I used no
  case data at all (that is d4's and d1/d2's work).
* I did not produce any DRAT certificate and did not run a SAT solver: the machine
  direction belongs to d3 on this board, and my one attempt at a machine target
  (the all-tight case `w = 15` everywhere at `n = 58`) was refused as a duplicate of it.
* The invariance and link statements are proved for all `n`; their *usefulness* at
  `n = 58` rests on (A2), which is arithmetic and does not depend on any colouring
  existing.
* No claim is made about the truth of `R_4(3) <= 58`.

## 9. Honest status

**Partial.** Proved and machine-checked: Kempe invariance of the ticket data and of the
arm multiset (so W2 and the cover's family split are recolouring-invariant), the link
lemma and the wall-profile read-off (Corollary 3 — the missing input for the family-A
double count), and the Kempe trade-off. Refuted: the per-class ticket balance (my own
earlier claim). Nothing here decides W2, family A or family B.
