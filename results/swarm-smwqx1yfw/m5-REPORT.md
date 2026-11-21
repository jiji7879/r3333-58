# Calibration of the one-critical ticket mechanism at n = 32..50, and exactly where n = 58 bites

Member m5, direction d8. **Status: partial.** Nothing here refutes Family A or
Family B, and nothing closes a case. It delivers (1) an independent
re-derivation of the ticket census on every verified artefact, (2) one
correction to the swarm's lemma bank, (3) a witness theorem that kills a whole
class of proposed Family-A refutations before anyone spends a run on them,
(4) the encoder-ready form of the arm-mixture lemma L1, verified tight, (5) a
precise statement of the numerical barrier that any proof at n = 58 has to
cross, and - in the **Addendum, section 10**, which answers the judge's lead -
(6) a proof that the colour-0 *interface route is not a reduction* of Family A
(the interface is pinned by an identity, so the proposed per-vertex bound is
equivalent to Family A being empty), with witnesses showing the bound fails in
every known object.

Everything below is produced by four small scripts next to this file and can be
re-run in seconds.

```
python3 analyze.py                 # census of the five verified colourings (n=48,49,50)
python3 analyze.py FILE --mech     # per-vertex mechanism at every ticket root
python3 test_l1plus.py             # tightness of L1 and of the root-occupancy form
python3 candidates.py              # falsification sweep of candidate necessary conditions
python3 interface.py               # the interface identity, every arm, every artefact
```

`analyze.py` reads only the `.col` edge matrix and re-derives `d_c`, the sorted
profile, `w`, `s_c`, `H`, the entrance count `N(v)` and the missing-ticket count
`E(v)` from the definitions in the brief and in
`.ultramath/smwqullhx/m8/lemmas.md` F1-T2. It is independent of
`verify_lemmas.py`; agreement between the two is a check, not a reuse.
No monochromatic triangle is present in any file used (my own triangle count
`triangles()` agrees with `tools/verify_coloring.py` on all five).

---

## 1. Census: the brief's numbers are right, one sentence of lemmas.md R2 is not

`python3 analyze.py` prints, per file, the profile classes with the multiset of
`H - w`:

| file | n | profiles (count) | H-w split |
| --- | ---: | --- | --- |
| `n48_z4z4_f0.col` | 48 | (15,11,11,10) x48 | 0 x48 |
| `k49_from_n48_m5.col` | 49 | (16,11,11,10) x12 ; (15,11,11,11) x36 ; (12,12,12,12) x1 | -1 x12 ; 0 x36 ; +12 x1 |
| `k50_z4z4_m6.col` | 50 | (16,13,12,8) x1 ; (16,11,11,11) x13 ; (15,15,12,7) x1 ; (15,12,11,11) x35 | -9 x1 ; -1 x9, 0 x4 ; -24 x1 ; 0 x8, +1 x12, +2 x15 |
| `k50_blockcayley_Z4xZ4_m4.col` | 50 | (16,11,11,11) x16 ; (15,12,11,11) x32 ; (14,13,13,9) x2 | -1 x16 ; 0 x32 ; +8 x2 |
| `k50_sanity_f2.col` | 50 | (16,11,11,11) x19 ; (15,12,11,11) x29 ; (14,13,12,10) x1 ; (13,13,12,11) x1 | -1 x19 ; 0 x29 ; +9 ; +10 |
| `k32_module_2x16_m1.col` | 32 | all 32 vertices have a 16-critical arm, all 16 send | 0 x32 |

The identity `sum_v H(v) = sum_v w(v)` holds on every file (checked), and
`sum_v (E(v) - N(v)) = 0` on every file (checked, consistent with T1).

The `(15,12,11,11)` class of `k50_z4z4_m6.col` splits **0 : +1 : +2 = 8 : 12 :
15**, exactly as the brief says, and the `(16,11,11,11)` class splits `-1 : 0 =
9 : 4`.

> **Correction to `.ultramath/smwqullhx/m8/lemmas.md` R2.** That section says
> "in `artifacts/k50_z4z4_m6.col` the 35 vertices of profile `(15,12,11,11)`
> have `H(v) = w(v) = 15` (all 15 held-out arm vertices send), i.e. `N(v) = E(v)`
> and the ticket root condition holds with equality". Only **8** of the 35 have
> `H = w`; the other 27 have `H = w + 1` or `H = w + 2`, and for e.g. vertex 1
> (`d = (11,15,11,12)`, `s = (0,15,0,1)`) one has `H = 16`, `N = 1`, `E = 0`.
> The *conclusion* R2 draws (the T2 instance cannot be proved from arm-local
> structure) survives, because the 8 vertices with `N = E = 0` are witnesses
> enough, but the sentence must not be quoted as it stands.

## 2. The strongest calibration available: `n48_z4z4_f0.col` is a Family-A object at every vertex

**Proposition W.** In `artifacts/n48_z4z4_f0.col` (triangle-free 4-colouring of
`K_48`, verified) *every* vertex `v` has

* profile `(15,11,11,10)`, one critical colour, `w(v) = 15`;
* `s_c(v) = 15` in the critical colour and `0` in the other three: the whole
  15-arm sends and all three other arms are **sender-free**;
* `N(v) = 0` and `E(v) = 0`, hence `H(v) = w(v) = 15`.

(Mechanism dump: `python3 analyze.py <file> --mech`; 48 identical lines.)

Consequences, which I think are the useful part for the swarm:

1. **The Family-A hypothesis set is realisable, at every vertex, at n = 48.**
   So no lemma of the form "a triangle-free 4-colouring has no vertex `v` with a
   15-arm all of whose vertices send while the other three arms are
   sender-free" can be true, and no lemma of the form "`E(v) = 0` and `N(v) = 0`
   is impossible at a one-critical vertex" can be true. Any proposed Family-A
   refutation must be *false* at this object; if a candidate argument does not
   use the arm sizes `(14,14,14)`, or `n = 58`, it is already refuted here.
   (This sharpens the brief's warning "if the argument would also hold at
   n = 50, it is wrong" to: *it must also fail at n = 48, with arms 11,11,10*.)
2. It also shows the n = 60 Section-5 conclusion "no entrance" is realisable at
   n = 48, so `N(v) = 0` cannot be obtained from local structure either.
3. `k50_blockcayley_Z4xZ4_m4.col` (32 one-critical roots) and
   `k50_sanity_f2.col` (29 one-critical roots) are the same kind of object at
   n = 50: every one-critical ticket root there has `E = N = 0` with the
   critical 15-arm sending completely. (Both files also contain vertices with
   **no** critical colour at all - `(14,13,13,9)` and `(14,13,12,10)`,
   `(13,13,12,11)` - which therefore have `w = 0` and are "roots" only
   vacuously. Such vertices cannot occur at n = 58: four parts `<= 14` sum to at
   most 56 < 57, which is m8's F3. So the n = 48/49/50 data contains a second
   kind of ticket root that has no n = 58 analogue, and it must be excluded from
   any calibration statement.)

## 3. L1 in encoder-ready form (root occupancy), with proof and tightness

L1 (m8, = Lemma D of my registration): for distinct colours `f != g` and any
vertices `x, u`, `|N_f(x) cap N_g(u)| <= 5`.

**L1+ (occupancy form).** If in addition a vertex `r` is known to lie in the
intersection, i.e. `r in N_f(x) cap N_g(u)` and `f != g`, then

  `|N_f(x) cap N_g(u)| <= 5` still, hence `|(N_f(x) cap N_g(u)) \ {r}| <= 4`.

This is *not* a new bound - "`<= 5` including `r`" and "`<= 4` excluding `r`" are
the same statement, as the judge pointed out. It is the form in which L1 should
be handed to an encoder: the cardinality is then imposed on the smaller variable
set `(N_f(x) cap N_g(u)) \ {r}`, which at the wall is a set of literals already
present in the case, and it is tight in that form (see below).

*Proof.* L1 gives `<= 5`; `r` is one of the intersection's elements, so at most
four others. ∎

*Instance used at the wall.* Let `r` have profile `(15,14,14,14)`, arms
`A = N_0(r)`, `B = N_1(r)`, `C = N_2(r)`, `D = N_3(r)`, and `S_u = N_0(u)\{r\}`
for `u in A`. For `u in A` and `x in B`: `r in N_0(u)` (since `u in N_0(r)`) and
`r in N_1(x)` (since `x in N_1(r)`), so with `(f,g) = (1,0)`

  `|N_1(x) cap N_0(u)| <= 5`  and  `|N_1(x) cap S_u| <= 4`,

and by the same argument `|N_2(x) cap S_u| <= 4` for `x in C`,
`|N_3(x) cap S_u| <= 4` for `x in D`.

*Tightness (checked).* `python3 test_l1plus.py`: on all five verified colourings
(and on `k32_module_2x16_m1.col`) the maximum of `|N_f(x) cap N_g(u)|` over
`f != g` is exactly 5, and the maximum over triples with a prescribed common
`r` in the intersection is also exactly 5. So L1's constant 5 is attained
*with* the root inside the intersection and the excluded-root constant 4 is
attained too, so nothing is lost in translation. (For machine use: a case
encoding that carries `#{w : u~_0 w, x~_1 w} <= 5` may instead carry
`#{w in S_u : x~_1 w} <= 4`, a cardinality over the literals of `S_u` alone.)

## 4. Mechanism tables: how `H >= w` is actually achieved in the known colourings

`python3 candidates.py` over the five colourings, restricted to one-critical
ticket roots (`H(v) >= w(v)`, one critical colour):

| file | roots | `E = 0 and N = 0` | `E >= 1` | `E >= 2` | `N >= 1` | max senders outside the critical arm | min colour-degree at a root |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `n48_z4z4_f0.col` | 48 | 48 | 0 | 0 | 0 | 0 | 10 |
| `k49_from_n48_m5.col` | 36 | 36 | 0 | 0 | 0 | 0 | 11 |
| `k50_blockcayley_Z4xZ4_m4.col` | 32 | 32 | 0 | 0 | 0 | 0 | 11 |
| `k50_sanity_f2.col` | 29 | 29 | 0 | 0 | 0 | 0 | 11 |
| `k50_z4z4_m6.col` | 39 | 8 | 4 | 0 | 31 | 2 | 11 |

Read off:

* **In every known one-critical ticket root the critical arm sends completely,**
  except in the four `(16,11,11,11)` roots of `k50_z4z4_m6.col` where exactly
  one arm vertex fails (`E = 1: d_c = 16, s_c = 15`). Empirically `E in {0,1}`
  always, and `H - w = N - E <= 2` always.
* **No known one-critical ticket root has a colour-degree `>= 12`.** The
  maxima of the minimum colour-degree over roots are 10 (n = 48) and 11
  (n = 49, 50). This is not an accident of the search: at n = 50 a profile has
  `sum_c d_c = 49`, so `min_c d_c <= 12`.
* Without the root's own critical arm, senders are rare: at most 2 outside
  senders in any known root, and **zero** in all of n = 48, the two other n = 50
  colourings, and n = 32. So Family B's hypothesis (`>= 5` senders in each
  14-arm) has no analogue anywhere in the data, exactly as m8's R6 says for
  two-critical vertices.
* The one two-critical vertex in the data (`k50_z4z4_m6.col`, vertex 49,
  profile `(15,15,12,7)`) is not a ticket root: `H - w = -24`. `R6`'s census is
  confirmed (no vertex in any artefact has two colour-degrees equal to 16).

Interface data at a root's critical arm (root `v`, arm `A = N_c(v)`,
`m_x = |N_0(x) cap A|` for `x` outside `A u {v}`, computed directly):

* `n48_z4z4_f0.col`, `v = 0`, `c = 0`: `|A| = 15`, 32 outside vertices,
  `m_x = 6` for 30 of them and `m_x = 15` for exactly 2.
* `k50_z4z4_m6.col`, `v = 1, 17, 32`, `c = 1`: `|A| = 15`, 34 outside vertices,
  `m_x = 6` for 31 of them, `m_x = 15` for 2, one small value (`2`, `0`).

So in the known objects the colour-0 interface from the critical arm is
essentially uniform (`m_x = 6`), with exactly two "hubs" 0-adjacent to the whole
arm. At n = 58 the same budget is `sum_x m_x in [210, 225]` spread over 42
vertices, i.e. an average of 5.0 to 5.36 - the interface must be *thinner* than
at n = 48, where the average is 210/32 = 6.56.

## 5. What the data cannot calibrate, and what that means

* No artefact contains a ticket root with two critical colours (R6, confirmed),
  so nothing about the five two-critical wall profiles can be calibrated from
  data; any necessary condition proposed for them is unchecked.
* Every known one-critical ticket root has a colour-degree `<= 11`, while at a
  `(15,14,14,14)` vertex all four colour-degrees are `>= 14` and at a
  `(16,14,14,13)` vertex all are `>= 13`. **The whole n = 58 content of the
  one-critical wall profiles is that every colour-degree of the root is
  `>= 13`.** Any argument that would also work with a colour-degree of 11
  present is refuted by Proposition W and its n = 50 analogues.

## 6. What I tried that did not produce a bound (recorded so it is not repeated)

All of the following are consistent, with the slack shown, so none of them
yields a contradiction in Family A (`r` with arms `A` of 15 and `B,C,D` of 14,
all of `A` sending 0-tickets, the three 14-arms sender-free):

1. **Colour-0 interface two-sided count.** `sum_{u in A} |S_u| in [210,225]`
   against `m_x <= 16 - (0-degree of x inside X)`. Gives only
   `|E_0(X)| in [119, 315]` and `sum_{x in X} d_0(x) >= 462`; both compatible.
2. **Block structure of the colour-0 graph.** `A` is 0-independent, and inside
   `X` every arm-block and every arm-pair block has 0-degree `<= 5` per vertex
   (L1: `B` is 1-independent, `C` 2-independent, `D` 3-independent). This gives
   `|E_0(X)| <= 315`, off by a factor 1.4 from what would be needed.
3. **Sender-free arms as a cap on colour-`f` edges.** `e_f(A,B) + e_f(B,C) +
   e_f(B,D) <= 182` for each arm, against the L1 ceiling 210: slack 28.
   Summing the four colour budgets gives `3306 <= 3621`: slack 315.
4. **The "one free arm" obstruction.** For `x in B` the A-part of `N_0(x)` is
   bounded by nothing (`A` is only 0-independent, so L1 does not apply with
   `c = d = 0`), and this is the structural reason every count in items 1-3 has
   slack: the quadratic `sum_f sum_{u in A} d_f(u) = 855` is an identity, not an
   inequality. This is the same conclusion as m8's R5, reached from the other
   side: arm-local counting has a factor ~1.5 of slack at n = 58.

## 7. What follows for the swarm

* **For d1 (Family A) and d2 (Family B):** the target must be a statement that
  fails at `n48_z4z4_f0.col` (Proposition W). Concretely, a candidate lemma
  should be tested against that file *first*; if it holds there, it cannot prove
  Family A. If a candidate uses only L1/L3/L4/L5/L6, `sum_c d_c = 57`,
  `d_c <= 16`, `E = 0`, `N = 0`, it is refuted by that file.
* **For d3 (machine route):** the occupancy form of L1 (section 3) puts the
  cardinality on the literals of `S_u = N_0(u) \ {r}` instead of on all of
  `N_0(u)`: `#{w in S_u : x ~_f w} <= 4`, one constraint per (arm vertex, arm,
  colour), each over at most 15 literals, and tight in that form.
* **For d5 (local search):** `n48_z4z4_f0.col` is the natural testbed for
  "Family A with small arms"; a search that pins `(15,14,14,14)` should be run on
  n = 51..58 only, since the profile cannot occur below 58.

## 8. What I did not verify, and what is not claimed

* I did not verify any ledger row, any case CNF, or the cover reduction; nothing
  in section 4-6 depends on the cover.
* Proposition W is a statement about one verified colouring; I did not classify
  the `Z4 x Z4` family or prove that it is the only way to make a one-critical
  all-sending root.
* The occupancy form of L1 is proved from `R(3,3) = 6` alone and checked tight;
  it is not used here to close anything.
* The empirical patterns of section 4 (`E in {0,1}`, `H - w <= 2`, at most 2
  outside senders, at most 2 hubs per arm) are **calibration, not theorems**. I
  did not prove any of them, and none of them is claimed to hold at n = 58.
* The correction in section 1 is a correction of a sentence in another member's
  file; that file is not mine to edit and I have not edited it.

## 9. Appendix: the frozen ledger's (15,14,14,14) block, read directly

Not part of my direction, but it is the cheapest independent check of one claim
of the brief and it tells the family-attack members exactly which rows are
which. From `.scratch/k58/case-ledger.jsonl.gz`, the 381 rows with
`family.profile == [15,14,14,14]` (all with `status == OPEN`), grouped by
`(root_kinds[0], marked_size, marked_kind, arm, charge)`:

| root kind | marked size | marked kind | arm | charge | rows |
| --- | ---: | --- | ---: | ---: | ---: |
| T | 15 | T | 0 | 15 | 5 |
| T | 15 | T | 1 | 1 | 231 |
| T | 15 | U | 0 | 15 | 2 |
| T | 15 | U | 1 | 1 | 49 |
| T | 16 | T | 0 | 15 | 1 |
| T | 16 | T | 1 | 1 | 15 |
| T | 16 | U | 0 | 15 | 1 |
| T | 16 | U | 1 | 1 | 4 |
| U | 15 | T | 0 | 3 | 5 |
| U | 15 | T | 1 | 5 | 46 |
| U | 15 | U | 0 | 3 | 2 |
| U | 15 | U | 1 | 5 | 12 |
| U | 16 | T | 0 | 3 | 1 |
| U | 16 | T | 1 | 5 | 4 |
| U | 16 | U | 0 | 3 | 1 |
| U | 16 | U | 1 | 5 | 2 |

Total 381; **308 rows have `root_kinds[0] = T` and 73 have `U`**, which is the
brief's Family A / Family B split, read straight off the ledger rather than from
the prose. Two further numbers that may be useful to the family attacks and to
the canonical-form pass:

* only **18** rows have `arm = 0` (the marked second critical class meets the
  root in the root's own 15-class: 9 T-roots, 9 U-roots); the other **363** have
  `arm = 1`, i.e. the marked vertex sits in one of the three 14-arms;
* every row pins two critical classes of sizes from `{15,16}` whose kinds are in
  `{T,U}` independently: 287 T-roots and 65 U-roots have `marked_size = 15`,
  the other 21 and 8 have `marked_size = 16`.

I have **not** checked how `arm`, `charge`, `placement` and `branch` map onto
the CNF's unit clauses (that is d4's audit), and nothing in sections 1-6 depends
on them. The grouping above is a plain `collections.Counter` over the JSON rows
and is reproducible in one command.

# Addendum (second submission): the interface route is not a reduction

The judge's lead was: if every `x` outside the root's 15-arm has at least 6
colour-0 neighbours in the arm, then the colour-0 interface is `>= 6*42 = 252 >
225`, contradicting the arm-side bound `225`. Here I prove the identity behind
that bound and show that the proposed per-vertex bound cannot exist inside
Family A at all. **The route is therefore a reformulation of the target, not a
reduction of it**, and the calibration data agrees: the bound holds at n = 48 and
fails at n = 49 and n = 50, at vertices that are not senders.

Code: `python3 interface.py` (this directory) prints every identity check.

## 10.1 The interface identity

Setup: `v = r`, colour `c`, arm `A = N_c(r)` with `|A| in {15,16}`,
`X = V \ (A u {r})`, and `m_x = |N_c(x) cap A|` for `x in X`.

> **Theorem I1.** `sum_{x in X} m_x = sum_{a in A} (d_c(a) - 1)`.

*Proof.* Both sides count the colour-`c` edges between `A` and `X`. From the
`X` side, that is `sum_x |N_c(x) cap A| = sum_x m_x`. From the `A` side: `A` is
colour-`c` independent (two `c`-neighbours of `r` would form a `c`-triangle with
`r`), so each `a in A` has no colour-`c` edge inside `A`, and its only
colour-`c` neighbour outside `X` is `r`; hence `|N_c(a) cap X| = d_c(a) - 1`. ∎

> **Corollary I2.** If every `a in A` is `c`-critical (`d_c(a) >= 15`) then, by
> `d_c(a) <= 16` (F1),
> `15(|A| - 1) <= sum_{x in X} m_x <= 15|A|`,
> so with `t = #{a in A : d_c(a) = 16}`,
> `sum_{x in X} m_x = 15(|A| - 1) + t`, `0 <= t <= |A|`.
> At `n = 58`, `|A| = 15`, `|X| = 42`: the interface is `210 + t` with
> `0 <= t <= 15`, and the **mean of `m_x` over `X` is `(210+t)/42 <= 5.357`**.

(Checked on every arm of every artefact by `interface.py`: `I1` holds in all
cases, including the `|A| = 16` arms, where the two sides are
`sum_a (d_c(a)-1)` rather than `15*15 + t`.)

## 10.2 Consequence: the proposed per-vertex bound is equivalent to the target

> **Corollary I3.** In Family A (so all 15 vertices of `A` are 0-critical),
> `"m_x >= 6 for every x in X"` holds **iff Family A is empty**.

*Proof.* If Family A is empty the statement is vacuous. Conversely the statement
gives `sum_{x} m_x >= 6*42 = 252`, while I2 gives `sum_x m_x = 210 + t <= 225`.
∎

So the interface count is not a small lemma that kills Family A; it is Family A's
emptiness written in a different alphabet. In particular no per-vertex argument
can supply it: in *any* Family A configuration (if one existed) the mean of `m_x`
is at most 5.357, so some vertex would have `m_x <= 5`. The number that would be
needed, 6, is **above the mean**, and the mean is pinned by an identity that uses
only F1 and the definition of the arm.

For reference, the same arithmetic as a function of `n`: with `|A| = 15`,
`|X| = n - 16`, the count `6|X| > 15|A|` needs `|X| >= 38`, i.e. `n >= 54`. At
`n = 58` the gap is `252 - 225 = 27`, but by I3 the hypothesis cannot be true
there; it is only *at all* consistent for `n <= 53`.

## 10.3 The per-vertex bound fails in every known object anyway

The other half of the judge's question -"work out whether the non-0 count is
forced" - has a clean answer: **no**. The non-0 count of `x` in `A` is
`|A| - m_x`, and Corollary I2 makes its *total* over `X` equal to
`|A||X| - 15(|A|-1) - t`, whose mean at `n = 58` is at least `9.64`. So some
outside vertex must have 10 or more non-0 neighbours in the arm. Concrete
witnesses, all with **every** vertex of the arm `c`-critical (`interface.py`,
and `analyze.py --mech` for the sender status):

| file | root `v`, colour `c` | `|A|` | `x` | `m_x` | `d_c(x)` | profile of `x` | arm mean `m` |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| `k50_sanity_f2.col` | `v=4`, `c=1` | 15 | 48 | **1** | 10 | (14,13,12,10) | 6.500 |
| `k50_sanity_f2.col` | `v=13`, `c=1` | 15 | 49 | **0** | 11 | (13,13,12,11) | 6.235 |
| `k50_z4z4_m6.col` | `v=46`, `c=1` | 15 | 48 | **0** | 8 | (16,13,12,8) | 6.176 |
| `k50_z4z4_m6.col` | `v=8`, `c=1` | 15 | 49 | **0** | 7 | (15,15,12,7) | 6.235 |
| `k49_from_n48_m5.col` | `v=8..23`, `c=0` | 15 | 48 | **3** | 12 | (12,12,12,12) | 6.455 |
| `n48_z4z4_f0.col` | `v=0`, `c=0` | 15 | - | min **6** | - | - | 6.562 |

The witnesses are **not senders** in the arm colour (`d_c(x) <= 14` in every
row), so the sender-freeness hypothesis of Family A does not repair the bound.
Nor does the `n = 58` degree floor (F1 + F2, all colour-degrees `>= 9`) exclude
them: the n = 49 witness has profile `(12,12,12,12)` and there are n = 50
witnesses with profiles `(14,13,12,10)`, `(13,13,12,11)` and `(14,13,13,9)`, all
with minimum colour-degree `>= 9`. (The two `k50_z4z4_m6.col` witnesses do have
degrees 7 and 8, so those two *are* excluded at n = 58 - but the others are not.)
What excludes all of them at `n = 58` is only the arithmetic of the mean
(Corollary I3), i.e. the very thing that makes the bound unprovable.

The `n = 48` row is the one place where the bound is attained with equality
(`min m_x = 6`), and there the mean is `6.562 > 6`, which is consistent precisely
because `|X| = 32` is small: `6*32 = 192 <= 210`.

## 10.4 The "two hubs" at n = 48, and a correction

The judge asked why the n = 48 object has exactly two vertices with `m_x = 15`.
The answer is arithmetic, not structural: at `v = 0`, `c = 0` the 32 values of
`m_x` are `6` (thirty times) and `15` (twice), and the identity I2 pins their sum
to `210 = 15*14 + 0`. If `k` of the 32 vertices are hubs then
`6(32-k) + 15k = 210`, i.e. `9k = 18`, i.e. `k = 2`. The hub count is determined
by the interface identity and the two observed values, with no further structure.

**Correction to the hub argument in the judge's note.** The note infers from
`m_x = 15` that if `d_0(x) = 16` then `A u {x,y}` would be a 17-set with no
colour-0 edge, contradicting `R(3,3,3) = 17`. That inference does not hold: a hub
is 0-adjacent to *all* of `A`, so `A u {x}` is very far from being colour-0-free
(for `n48_z4z4_f0.col`, `A u {27,41}` carries 30 colour-0 edges). The correct
statement is: `m_x = 15` and `d_0(x) <= 16` give `N_0(x) = A` or `A u {y}`; hubs
are pairwise non-0-adjacent (two of them plus any `a in A` would be a
0-triangle), and every hub lies in `N_0(a)` for every `a in A`, so `{r} u (hubs)`
sits inside a 0-independent set of size at most 16 - a bound of 15 hubs, not 1.
Both the n = 48 file (2 hubs at every vertex) and the n = 50 files (2 hubs at
`v=1,17,32`) confirm that two is possible.

## 10.5 What this leaves

The interface is pinned, so the interface route is a reformulation. The one
positive thing the identity gives is a sharp **fingerprint of the wall profile**:

* at `n = 58` in Family A the mean of `m_x` over the 42 outside vertices is at
  most `5.357`, whereas among the 180 arms of the five verified files whose
  `15`/`16` vertices are *all* `c`-critical the smallest mean is `6.176`
  (`k50_z4z4_m6.col`, `v=46`, `c=1`; n = 50), `6.455` at n = 49 and `6.562` at
  n = 48;
* hence any Family A configuration must contain an `x` with `m_x <= 5`, i.e. a
  vertex with **at least 10 non-0 neighbours in the root's 15-arm** - and by the
  table above such a vertex is perfectly possible in an object that satisfies
  every arm-local hypothesis, is not a sender, and has all colour-degrees `>= 9`.

So the only remaining form of the interface route is: *prove that at `n = 58` a
vertex `x` with `m_x <= 5` in a sender-free arm must itself be a sender*. That
statement is not implied by the local bounds (the n = 50 witnesses satisfy them),
and it is not refuted either (no `n = 58` object exists). It is the sharpest
concrete target this route leaves, and it should be attacked directly or not at
all.

# Addendum II (direction d10): the join type of an outside vertex to the pinned arm

Status: **partial / a verified no-go plus a verified classification.** Nothing
here refutes a family. It settles the "template rigidity" question: the pinned
`T-minus`/`U-minus` 15-arm imposes **nothing** on how an outside vertex may be
joined to it beyond the arm-mixture bound L1, so no shallow structural argument
can extract a bound on a "poor" vertex from the arm's internal colouring.

Code: `python3 join.py` (prints everything below in about 25 s).

## 11.1 The join types, exactly

Setup: at a `(15,14,14,14)` root, `A = N_0(r)` is `0`-independent, so the
colouring of `A` is a triangle-free 3-colouring by the other three colours. An
outside vertex `x` labels each `a in A` with the colour of `xa`, giving a
partition

  `A = M_0 u M_1 u M_2 u M_3`, `M_f = A cap N_f(x)`.

**Proposition J1.** `A u {x}` is triangle-free **iff** for each `f != 0` the set
`M_f` contains no edge of colour `f`.

*Proof.* A pair `{a,a'}` inside `M_f` gives the triangle `x a a'` with `xa, xa'`
both of colour `f`, so it must not have colour `f`. Conversely, every
monochromatic triangle in `A u {x}` either lies in `A` (impossible, `A` is
triangle-free) or has the form `x a a'` with `xa, xa'` the same colour `f`, which
`J1` forbids; and a pair `a in M_f`, `a' in M_g` with `f != g` cannot complete a
monochromatic triangle through `x` at all. (Pairs in `A` never have colour `0`,
so `M_0` carries no condition.) ∎

Consequently `|M_f| <= 5` for `f != 0` is automatic (such an `M_f` is
2-coloured and triangle-free inside `A`, so `R(3,3) = 6`), and the only
information a join type carries is the profile
`(|M_0|, |M_1|, |M_2|, |M_3|)`.

## 11.2 The templates are flexible: all 216 L1-compatible profiles occur

`join.py` enumerates every labelling of both pinned 15-vertex templates
(`k15_template_Tminus_aut2_m4.col`, `k15_template_Uminus_aut10_m4.col`, with the
arm colour playing the role of colour 0) subject to J1:

| template | `|Aut|` | labelings | distinct profiles | profiles with `m_arm <= 5` |
| --- | ---: | ---: | ---: | ---: |
| `T-minus` | **2** | 3,700,504 | **216** | 56 |
| `U-minus` | **10** | 3,699,148 | **216** | 56 |

`216 = 6^3` is exactly the number of profiles allowed by L1 alone (`m_1,m_2,m_3`
each in `0..5`, `m_0` determined). Both templates realise **every** one of them:

> **Proposition J2 (verified by exhaustive enumeration).** For `A` either pinned
> 15-template and any `(m_0,m_1,m_2,m_3)` with `m_f <= 5` for `f != 0` and
> `sum m_f = 15`, there is a labelling of `A` realising it that keeps
> `A u {x}` triangle-free. Hence the template's internal structure imposes no
> constraint on the join type beyond L1.

The set of poor join types (`m_arm <= 5`) is therefore also exactly the
L1-compatible one: all 56 profiles occur, including

* `(m_arm; other three) = (5; 5,5,0)` — realised by 6 labelings in each
  template, i.e. a poor vertex whose non-arm adjacencies into the arm are
  *maximal in two colours and empty in the third*; and
* `(0; 5,5,5)` — a vertex with **no** arm-colour edge into `A` at all (this is
  the `m_x = 0` case that the k = 50 artefacts also exhibit).

The only thing that *is* forced is arithmetic: `m_arm <= 5` gives
`m_1 + m_2 + m_3 >= 10` over three parts each `<= 5`, hence `max_f m_f >= 4`
(and that bound is attained, e.g. `(5;5,5,0)` has `max = 5`, the profile
`(5;4,5,5)`... every poor profile has `max >= 4`).

## 11.3 Consequence, and what it rules out

Combined with the interface identity of section 10:

* the arm-side data at a Family-A root (a pinned template, all of `A`
  `0`-critical, arms `14,14,14`) determines the *average* interface
  `(210+t)/42 <= 5.357` but leaves each individual join type essentially free;
* **template rigidity cannot supply the missing lemma.** In particular the live
  form of the interface route -"at n = 58, a vertex `x` with `m_x <= 5` in a
  sender-free arm must itself be a sender (`d_1(x) >= 15`)"- cannot be decided
  from the structure of `A`: the join type `(5;5,5,0)` and even `(0;5,5,5)` are
  available, and nothing in them involves the three 14-arms where `d_1(x)`'s
  remaining terms live.

So the arm's internal colouring is *not* where the wall's obstruction is. What is
left, as the judge put it, is the machine route (d3) or a genuinely global
argument.

## 11.4 Verified classification data (independent of the file names)

`join.py` also computes `|Aut|` of each template by backtracking with
colour-degree invariants, confirming the artefact claims:

| file | `|Aut|` claimed by its name | computed |
| --- | ---: | ---: |
| `k15_template_Tminus_aut2_m4.col` | 2 | **2** |
| `k15_template_Uminus_aut10_m4.col` | 10 | **10** |
| `k16_template_T_aut32_m4.col` | 32 | **32** |
| `k16_template_U_aut160_m4.col` | 160 | **160** |
| `k15_link_Tminus_m5.col`, `k15_link_Uminus_m5.col` | - | 2, 10 |
| `k16_link_T_m5.col`, `k16_link_U_m5.col` | - | 32, 160 |

(The link files have the same automorphism orders as the templates of the
corresponding name, so they are isomorphic to them.)

## 11.5 What is not done here

* I did not enumerate the 16-vertex join types (the naive DFS is `4^16`; the
  labelled enumeration for `n = 15` already takes ~25 s and the 16-vertex
  version was stopped). The 16-arm case matters for Family B and for
  `(16,14,14,13)`.
* I did not prove that the two 15-vertex templates are the *only* critical
  3-colourings of `K_15`; I only verified their automorphism groups and that
  they are non-isomorphic (different `|Aut|`). That classification is assumed by
  d1/d2 and by the ledger decode.
* Nothing here is used to close a case.

# Addendum III (direction d10, second submission): the pair level

Status: **partial.** Two proved statements (the pair criterion and an exact
reformulation of Family A as a finite combinatorial problem), one verified design
structure, and two verified *infeasibility* results for the natural pair-level
schemes. Nothing here refutes a family.

Code: `python3 j3.py` reproduces J6 and the two infeasibility searches of 12.4 in
about 5 s; J3/J5 are proofs, not computations.

## 12.1 Set-up

`r` has profile `(15,14,14,14)`, `A = N_0(r)` (15 vertices, `0`-independent, and
*by premise* one of the two pinned templates so that its internal 3-colouring is
known), and arms `B = N_1(r)`, `C = N_2(r)`, `D = N_3(r)` of 14 each,
sender-free. `X = B u C u D`, `|X| = 42`. For `x in X`: `arm(x)` is the colour of
`rx` (so `x in N_c(r)` iff `arm(x) = c`), and the **join type** `J(x)` is the
partition `A = M_0 u M_1 u M_2 u M_3`, `M_f = N_f(x) cap A`.

## 12.2 The pair criterion

**J3.** For `x, x' in X` with `f = colour(xx')`, the colouring of
`A u {x, x'}` is triangle-free **iff** `M_f(x) cap M_f(x') = empty`.

*Proof.* The triangle `{x, x', a}` is monochromatic iff `colour(xa) =
colour(x'a) = f`, i.e. iff `a in M_f(x) cap M_f(x')`. Every other triangle
meeting `{x,x'}` in two vertices and one vertex of `A` is of this form, and the
one meeting only one vertex of `A` is handled by J1. ∎

**Corollary J4.** A join type `J` is compatible with a copy of itself iff some
part of `J` is empty; the corresponding colour is then a *free colour* of `J`.
Hence if every vertex of `X` is given a type with an empty part, **every pair is
compatible**: colour `xx'` with any empty colour of `J(x)` or of `J(x')`. The
only restriction is that a vertex must not be placed in the arm of its own
(free) colour, since `x, x' in B` requires `colour(xx') != 1`.

**J5 (exact reformulation).** A Family-A colouring of `K_58` exists **iff** there
are: arm labels `arm(x) in {1,2,3}` on `X` (14 of each); join types `J(x)`
satisfying J1; and a colouring of the edges of `X` such that

 (i) `colour(xx') != arm(x)` whenever `arm(x) = arm(x')` (triangles `r x x'`),
 (ii) `colour(xx')` is a free colour of the pair, i.e. `M_f(x) cap M_f(x') = empty`
     (triangles `a x x'`),
 (iii) no monochromatic triangle inside `X` (triangles `x x' x''`),

together with the degree conditions

 (iv) `1 + #{x : a in M_0(x)} >= 15` for every `a in A` (all of `A` is
      `0`-critical);
 (v) `1 + |M_c(x)| + #{x' : colour(xx') = c} <= 14` for `x` with `arm(x) = c`
      (the three 14-arms are sender-free);
 (vi) `d_c(x) <= 16` for all `c`, and `max_c d_c(x) >= 15` (F1 and F3).

*Proof.* Every triangle of `K_58` contains `r`, or lies in `A`, or is of type
`a a' x`, `r a x`, `r x x'`, `a x x'`, `x x' x''`. Colours of the first five
kinds are fixed (`ra` is `0`, `aa'` is in `{1,2,3}`, `rx` is `arm(x)`), so they
are never monochromatic except for `r x x'` (condition (i)) and `a a' x`
(condition J1); `a x x'` is (ii) and `x x' x''` is (iii). ∎

So Family A is a finite list-colouring-plus-degree problem on 42 vertices; the
missing lemma must live in (i)-(vi) jointly. This is the sharpest form I can
give the swarm's target.

## 12.3 The design structure of the extremal types (verified)

Call a type *extremal* if its arm-colour part has size 5 and exactly one of its
three internal parts is empty, the other two having size 5, i.e. profile
`(5;5,5,0)` up to permutation of the internal colours. These are the types with
the **smallest possible** `m_x` among types having an empty part (an empty part
of size `s` forces `m_x >= 15 - 2*5 = 5`).

> **J6 (verified by exhaustive enumeration, both templates).** For each internal
> colour `f`, the arm-parts `M_0` of the extremal types with empty part `f` are
> exactly **6 five-subsets of `A` forming a 2-`(15,5,2)` design**: every vertex
> of `A` lies in exactly 2 of the 6 blocks. The three families (one per `f`) are
> three *different* such designs.

## 12.4 The natural pair-level schemes are infeasible (verified)

If every vertex is given an extremal type then `sum_x m_x = 42*5 = 210`, so
`t = 0` (no vertex of `A` has `d_0 = 16`) and the coverage condition (iv) reads
`#{x : a in M_0(x)} = 14` for every `a in A`: the 42 blocks must form a
`1-(15,5,14)` design. By J4 all pairs are then compatible, so this is the
cleanest possible family of witnesses. Exhaustive search over the
multiplicities gives:

| scheme | `T-minus` | `U-minus` |
| --- | --- | --- |
| 28 vertices from one family + 14 from another (all `m_0 = 5`), coverage exactly 14 | **none** | **none** |
| 14 vertices from each of the three families with the *same* multiplicity vector, coverage 14 or 15 | **none** | **none** |

So the natural extremal schemes admit **no** pair-level witness in either
template. Any Family-A object must therefore either use a vertex with `m_x >= 6`
(so `t >= 1`, i.e. some vertex of `A` has `d_0 = 16`), or use a type with **no**
empty part (all four parts non-empty), in which case pairs are compatible only
through disjointness of their parts.

What I did **not** decide is the general case (mixed arm-part sizes, or types
without an empty part). That is the remaining gap between this analysis and a
kill: a witness of that general kind, or a proof that none exists, is what would
settle Family A at the pair level.

## 12.5 Honest summary of what 12 has added

* J3/J5: an exact reformulation of Family A as a 42-vertex list-colouring problem
  with degree conditions - proved, and cheap to encode (42 arm labels + 42 types
  instead of 630 edge colours).
* J6: the extremal arm-parts form 2-`(15,5,2)` designs (6 blocks each) in both
  templates.
* 12.4: the two natural extremal pair-level schemes are infeasible in both
  templates, so a Family-A object needs `t >= 1` or a type with four non-empty
  parts. That is a new necessary condition on a hypothetical witness, but it is
  not a contradiction.

## 12.6 CORRECTION (must be read with 12.3-12.4: they are withdrawn as stated)

The judge is right and my J6 is wrong. **A 2-`(15,5,lambda)` design has
`b = 105 lambda / 10 = 10.5 lambda` blocks, so `b = 6` is impossible for any
integer `lambda`; "6 blocks forming a 2-`(15,5,2)` design" was an overstatement
of a computation that only verified constant *point* degrees.** I also cannot
reproduce the judge's six blocks, so the block lists themselves are
convention-dependent and I must not present mine as canonical. Here is exactly
what I verified and with which convention.

Convention of `j3.py`: the template file uses colours `0,1,2` inside `A` and the
arm colour (absent inside `A`) is the file colour `3`; a configuration is a
partition `A = S u U u V` with `|S| = |U| = |V| = 5`, `U` independent in file
colour `g`, `V` independent in file colour `h`, `S` unconstrained (it is the
arm-colour part `M_arm`), and `(g,h)` the ordered pair of the other two internal
colours. In that convention, for each of the three choices of empty part `f`:

* the number of configurations is **6** (this agrees with the judge's count of
  6, and is the part of J6 that stands);
* the six arm-parts of the **T-minus** template for `f = 0`, `(g,h) = (1,2)` are
  `(0,1,2,7,11) (0,5,6,10,14) (1,4,6,9,13) (2,4,5,8,12) (3,7,8,9,10) (3,11,12,13,14)`;
  in this list every vertex of `A` lies in exactly 2 of the six, and every pair
  in at most 1 (a 2-regular linear 5-uniform hypergraph on 15 points, *not* a
  design: only 60 of the 105 pairs occur);
* the same six lists appear for the **U-minus** template under this convention,
  which is itself a reason to distrust the convention rather than to trust the
  list (the two templates are non-isomorphic: `|Aut|` 2 versus 10).

The judge's list for `T-minus`, "empty part 0, `g=1`, `h=2`", is
`(0,6,7,10,11) (1,5,6,9,10) (2,3,7,11,14) (2,3,8,12,13) (2,5,6,11,13) (4,5,8,9,13)`,
with point degrees 1,2,3. It is not my list, so at least one of us is using a
different labelling of the template's colours or vertices, and I have not been
able to determine which. **Consequently:**

* **J6 is withdrawn except for the count 6.** The claim that the extremal
  arm-parts have design structure is false.
* **The infeasibility claims of 12.4 are withdrawn as statements about Family
  A.** They were computed on *my* block lists (12.4(a): 28 vertices from one
  list + 14 from another with coverage exactly 14; 12.4(b): one common
  multiplicity vector over the three lists, coverage 14 or 15). Since the lists
  are convention-dependent and disagree with the judge's, those searches do not
  establish anything about the pinned templates. They do establish, for the
  record, that *for my lists* both searches are empty - reproducible with
  `python3 j3.py`, which prints the lists themselves, so the calculation can be
  redone under any other convention in a few seconds.
* **The conclusion "any Family-A object needs a vertex with `m_0 >= 6` or a type
  with four non-empty parts" is withdrawn.** What survives from section 12 is
  J3 (the pair criterion), J5 (the exact reformulation), and the count of 6
  configurations per (empty part, ordered colour pair).

This is the honest position: three of my four statements in this addendum stand
and one does not, and the failure was mine - I inferred a design from constant
point degrees.
