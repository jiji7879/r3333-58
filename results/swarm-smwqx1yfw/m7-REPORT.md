# Family B of `(15,14,14,14)` at n = 58: decode, guard lemma, calibration, machine experiments

Member m7, direction d2. **Status: partial. No family refuted and no case closed.**
Family B (the 73 `U---` cases) is still OPEN; what is established here is (i) an
independent reproduction and decode of the 73 cases, (ii) a general lemma ("guard")
that fully determines the neighbourhood of a single sender, proved and machine
checked on every artefact, (iii) a calibration census of senders per arm size at
n = 48..50, and (iv) two machine results, one of them a warning: a natural-looking
strengthening that closes the cases in 0.1 s is **unsound**.

Everything below is reproducible from the repository root; commands in §7.

---

## 1. What family B is, decoded and reproduced

`decode_cases.py` reads `results/ledger-2026-11-22.tsv.gz` directly and
regenerates every `(15,14,14,14)` case with the frozen encoders
(`.scratch/k58/joint_plan.py`, `gluing.py`, `palette_quotient.py`).

* 381 ledger rows; 381 regenerated; the multisets of
  (kinds, marked_size, arm, branch) are **identical** (the script prints
  `identical: True`).
* The decode of the two families, with the plan charge
  `copies * (threshold - 1)` per arm group:

| kinds | charged arm | threshold `t` | cases | plan charge | family |
| --- | --- | ---: | ---: | ---: | --- |
| `T---` | 0 (the 15-class) | 15 | 9 | 1·14 = 14 | A |
| `T---` | 1 (a 14-arm) | 1 | 299 | 3·0 = 0 | A |
| `U---` | 0 (the 15-class) | 3 | 9 | 1·2 = 2 | B |
| `U---` | 1 (a 14-arm) | 5 | 64 | 3·4 = 12 | B |

* Soundness of the plan (re-derived, not taken on trust): at a
  profile-`(15,14,14,14)` vertex `w(r) = 15` and `H(r) = s_0+s_1+s_2+s_3`, so
  a root has `Σ_c s_c ≥ 15 > Σ_c (t_c − 1) = 14`, hence `s_c ≥ t_c` for some
  colour `c`. Refuting, for each `c`, the single statement "`s_c ≥ t_c`" at
  that kind of root therefore gives `H(r) ≤ 14` there. By the colour symmetry
  of the three 14-arms it suffices to refute arm 1. Both plans have total
  charge exactly `w − 1 = 14`, so **refuting family A gives `H ≤ 14` at every
  `T⁻` root and refuting family B gives `H ≤ 2 + 3·4 = 14` at every `U⁻`
  root**; the two together prove W2.

So each case is one *single-arm* statement, not a conjunction: family B is

> (B1) at a `U⁻` root no 3 vertices of the 15-class send in colour 0 — 9 cases; and
> (B2) at a `U⁻` root no 14-arm has 5 senders in its own colour — 64 cases.

## 2. Anatomy of a frozen case CNF, reproduced clause for clause

`build_case.py --kinds U--- --index 9` emits the frozen case (arm 1, `t = 5`,
marked sender `q = 16`, marked template `U` of size 15): 145,726 clauses,
11,939 variables, 303 unit clauses. Its parts:

* base 134,995 = exactly-one-colour per edge (1,653 edges × 7) **+** all
  no-monochromatic-triangle clauses (4·C(58,3) = 123,424);
* 303 units: the root's four arm blocks (the `U⁻` template on the 15-class, all
  colour-`c` edges from the root into arm `c`), plus the marked sender `q` and
  its own critical neighbourhood, pinned as a `U` template;
* 10,428 clauses: "at least 5 vertices of arm 1 send", encoded with one guard
  variable per arm vertex (`d_1(x) ≥ 15`).

**Two observations that matter for the machine route.**

1. The base contains **no colour-degree cap**: `|N_c(v)| ≤ 16` is nowhere in
   the frozen CNF (for the free vertices, i.e. every vertex outside the root,
   its pinned 15-class and the pinned neighbourhood of `q`), although it follows from
   `R(3,3,3) = 17`. (134,995 is exactly the two counts above, so nothing else
   is present.) Adding it is a free, sound tightening (§5).
2. `mycase.py` re-implements `dense.marked_threshold` (returning the guard
   variables as well) and rebuilds **all 73 family-B cases** to clause-for-clause
   identical CNFs (sorted clause multisets compared for every case:
   **0 mismatches**, sizes 145,722..146,136 clauses, nv 11,939..12,138; case 9
   alone is 145,726 clauses / nv 11,939 / 303 units). All strengthenings in §5
   are added on top of that rebuilt object, so the provenance of the
   strengthened formula is exact.

## 3. The guard lemma: a sender's neighbourhood is completely rigid

Notation as in the brief: `N_c(v)` is the colour-`c` neighbourhood, and `x`
*sends* in colour `c` when `d_c(x) = |N_c(x)| ≥ 15`.

> **Lemma G (guard).** Let `v` be any vertex of a triangle-free 4-colouring of
> `K_n`, `c` any colour, and `x ∈ N_c(v)` a vertex that sends in colour `c`.
> Then for each of the three colours `D ≠ c`, the colour-`c` support of `x` in
> the arm `N_D(v)` satisfies
> `4 ≤ |N_c(x) ∩ N_D(v)| ≤ 5`.

*Proof.* `N_c(x) ∩ N_c(v) = ∅`: a common colour-`c` neighbour would give a
monochromatic colour-`c` triangle with `v`. The four sets `N_D(v)` (`D ≠ c`)
together with `{v}` cover `V ∖ N_c(v)`, so
`N_c(x) = {v} ⊔ ⊔_{D ≠ c} (N_c(x) ∩ N_D(v))`, giving
`Σ_{D ≠ c} |N_c(x) ∩ N_D(v)| = d_c(x) − 1 ≥ 14`. Each summand is `≤ 5` by L1 of
the m8 lemma bank (`|N_d(y) ∩ N_c(v)| ≤ 5` for `d ≠ c`, here `d = c`, arm colour
`D ≠ c`, so the intersection is 2-coloured with no monochromatic triangle and
`R(3,3) = 6` bounds it by 5). Three summands, each `≤ 5`, summing to `≥ 14`,
are each `≥ 4`. ∎

At a profile-`(15,14,14,14)` root the four arms are exactly `V ∖ {r}`, so the
lemma is exactly the n = 60 §7.1 "guard" statement at n = 58: **a sender in a
14-arm has exactly 4 or 5 colour-`c` neighbours in the 15-class and exactly 4 or
5 in each of the other two 14-arms**, and its whole critical arm is those
supports plus `r`. In particular the local structure of one sender is rigid:
no single-sender counting argument can contradict anything, which is the
precise reason the wall is not local.

**Machine check** (`check_structure.py`, C3, all `c`, all `v`, all senders):

| file | n | mono triangles | max `d_c` | max mixed (C2) | guard violations | support multisets |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| k50_z4z4_m6.col | 50 | 0 | 16 | 5 | 0 | (5,5,5):224, (4,5,5):555 |
| k50_blockcayley_Z4xZ4_m4.col | 50 | 0 | 16 | 5 | 0 | (5,5,5):256, (4,5,5):480 |
| k50_sanity_f2.col | 50 | 0 | 16 | 5 | 0 | (5,5,5):304, (4,5,5):435 |
| k49_from_n48_m5.col | 49 | 0 | 16 | 5 | 0 | (5,5,5):192, (4,5,5):540 |
| n48_z4z4_f0.col | 48 | 0 | 15 | 5 | 0 | (4,5,5):720 |
| k32_module_2x16_m1.col | 32 | 0 | 16 | 5 | 0 | (5,5,5):512 |
| 4 K_15/K_16 templates, 2 links | 15,16 | 0 | 5 | 2 | 0 | — (no sender: n < 16) |

The same run also re-certifies `sum_v H(v) = sum_v w(v)` on all ten complete
colourings (values in `census.jsonl`).

## 4. Calibration: how many senders does an arm actually have at n = 48..50?

From `check_structure.py` (arm census: size → number of arms, maximum senders in
one arm, total senders):

| file | arms of size 15 | size 16 | size 12 | size 11 | size 14 | size 7/8/9/10 |
| --- | --- | --- | --- | --- | --- | --- |
| k50_z4z4_m6 | 37, max 15, 525 | 14, max 15, 195 | 37, max 2, 42 | 109, max 1, 4 | — | 7: 1 arm, 6; 8: 1 arm, 7 |
| k50_blockcayley | 32, max 15, 480 | 16, max 15, 240 | 32, max 0 | 112, max 0 | 2, **max 0** | 9: 2 arms, max 8 |
| k50_sanity_f2 | 29, max 15, 435 | 19, max 15, 285 | 31, max 0 | 116, max 1, 10 | 1, **max 0** | 10: 1 arm, 9; 13: 3 arms, 0 |

Reading, in the order of how much it constrains a proof:

1. **The artefacts do not refute family B.** Every 14-arm in the three
   `K_50` colourings has **zero** senders; 13- and 12-arms have 0 or ≤ 2. The
   transition to "all vertices send" happens at arm size 15. So (B2) — "no 14-arm
   has 5 senders" — is consistent with all the data, and so is (A)'s stronger
   "no sender in a 14-arm".
2. **But no arm-size-uniform or n-uniform bound of the required strength
   exists**: arms of size 7 and 8 have 6 and 7 senders (nearly all of them), and
   the totals for `k50_z4z4_m6` reproduce m2's figure exactly (6+7+4+42+0 = 59
   tickets sent along a colour that is non-critical at the receiver, out of 779).
3. Consequently a proof of (B2) must use *all four* arms being at least 14 —
   i.e. `57 = 15+14+14+14`, the fact that at n = 58 the "deficit budget"
   `Σ_c (16 − d_c(v)) = 7` is spread over arms of size ≥ 14 — not any property of
   a single arm. This is the same conclusion m8 reaches from the other side
   (their R5: the all-arms-send hypothesis leaves a factor 1.5 of counting
   slack), and my §3 explains its structural cause: one sender is rigid, so
   only correlations between senders (or the global sum) can contradict.

## 5. Machine experiments: sound strengthenings do not move the wall

`mycase.py` adds only constraints satisfied by **every** triangle-free
4-colouring of `K_58` (so UNSAT of the result implies UNSAT of the frozen case):

* **S1** `|N_c(v)| ≤ 16` for all `v,c` (R(3,3,3) = 17) — *absent from the frozen base*;
* **S2** `|N_c(v)| ≥ 9` for all `v,c` (`Σ_c d_c = 57`, S1);
* **S3** `|N_f(x) ∩ N_c(root)| ≤ 5` for `f ≠ c` (L1), all `x`, all four arms;
* **S6** the same against the marked sender's pinned template, `f ≠ a` (L1);
* **G** the guard: for every arm vertex `x` with guard "`x` sends", each of the
  three other arms of the root contains `≥ 4` and `≤ 5` colour-`a` neighbours
  of `x` (Lemma G).

Results (Kissat 4.0.4, `.scratch/satcheck/bin/kissat`, one process at a time):

| formula | budget | result |
| --- | ---: | --- |
| frozen case 9 (arm 1, t=5) | 40 s | UNKNOWN |
| + S1 | 40 s | UNKNOWN |
| + S1 + S3 | 40 s | UNKNOWN |
| + S1 + S2 + S3 + S6 + G (cases 0, 9, 20, 40; ~738k clauses) | 140 s each | UNKNOWN |
| + G + forcing named extra senders in arm 1 (2 or 5 forced) | 30 s | UNKNOWN |

The branching is a *sound* case split worth recording: the case asserts `≥ 5`
senders in arm 1 and pins `q`, so at least 4 of the other 13 arm vertices send;
forcing them one at a time (13 branches), two at a time (78), or a fixed
4-subset at a time (715) covers every model. It does not help at these budgets.

### 5b. Negative calibration: an unsound strengthening closes these cases instantly

Adding the **same-colour** common-neighbourhood bound
`|N_a(x) ∩ N_a(q)| ≤ 5` (the `c = d` case of L1, which L1 does *not* license)
turns every family-B case into `s UNSATISFIABLE` in ~0.1 s, and so does the
unsound form of S3 that reads "at most 5 of *all* of `x`'s colour-`f`
neighbours". Both are false statements about the objects:
`artifacts/k50_z4z4_m6.col` has pairs with a common colour-`c` neighbourhood of
**16** vertices (m8's L2; reproduced by C2 in `check_structure.py` only for
`c ≠ d`, and by m8's witness `verify_lemmas.py`). **Lesson for the machine
route:** an "instant" closure of a wall case is a red flag for exactly this
error; a closure that arrives in under a second at this scale should be treated
as unsound until the same constraint has been checked against the artefacts.

## 6. What I did *not* do

* I did not refute family A or family B, and I did not close a single one of the
  381 cases; no DRAT certificate is claimed.
* I did not verify the U/T classification theorem (that every good 3-colouring
  of `K_15` is a vertex-deletion of `U` or `T`); it is used only as the premise
  of the frozen case split, which is d4/m6's audit.
* The machine results are budget statements (40–140 s per case). They do not
  contradict the brief's dead-end 1 (bigger budgets, unstrengthened encoding);
  they extend it: the natural *sound* strengthenings do not close the cases
  either, while the one strengthening that does close them is false.
* Lemma G is uniform in n and is machine-checked on ten complete colourings
  (n = 32..50) plus four templates. It says nothing about *two* senders.

## 7. Reproduction

```bash
cd <repo>                                # frozen encoders are under .scratch/k58
# 1. decode + provenance check of all 381 cases (uses the frozen ledger)
.scratch/k58/.venv/bin/python .ultramath/smwqx1yfw/m7/decode_cases.py
# 2. structural checks: degree caps, L1, guard lemma, ticket identity, arm census
python3 .ultramath/smwqx1yfw/m7/check_structure.py artifacts/k50_z4z4_m6.col \
    artifacts/k50_blockcayley_Z4xZ4_m4.col artifacts/k50_sanity_f2.col \
    artifacts/k49_from_n48_m5.col artifacts/n48_z4z4_f0.col \
    artifacts/k32_module_2x16_m1.col
# 3. rebuild a frozen case CNF (identical object), then add sound strengthenings
mkdir -p .ultramath/smwqx1yfw/m7/cnf
.scratch/k58/.venv/bin/python .ultramath/smwqx1yfw/m7/build_case.py \
    .ultramath/smwqx1yfw/m7/cnf/c9.cnf --kinds U--- --index 9
.scratch/k58/.venv/bin/python .ultramath/smwqx1yfw/m7/mycase.py \
    .ultramath/smwqx1yfw/m7/cnf/FB9.cnf --index 9 --s1 --s2 --s3 --s6 --guard
.scratch/satcheck/bin/kissat --quiet --time=140 \
    .ultramath/smwqx1yfw/m7/cnf/FB9.cnf .ultramath/smwqx1yfw/m7/cnf/FB9.drat
# 4. the branching split (sound): force a second sender by vertex number
.scratch/k58/.venv/bin/python .ultramath/smwqx1yfw/m7/mycase.py \
    .ultramath/smwqx1yfw/m7/cnf/br17.cnf --index 9 --s1 --s3 --s6 --guard \
    --force-sender 17
```

(The `cnf/` directory is scratch: CNFs there are regenerated in ~2 s each.)

## 8. What I would attack next, given §3 and §4

Lemma G makes a single sender rigid, so the next useful target is a
**two-sender** statement inside one 14-arm: two senders `x, y` of arm `a` each
have 4–5 colour-`a` neighbours in the 15-class and in each other arm, and
`colour(xy) ≠ a`; the question is what the two support triples force about the
`U⁻` template on the 15-class. That is a finite statement about two 4/5-subsets
of a fixed 15-vertex graph and can be settled by exhaustive enumeration over
the template, uncoloured vertices being ignored. It must be calibrated on the
`K_50` 15/16-arms, where all 15 arm vertices send and two senders share 15 or 16
of 16 neighbours (m8 L2), so the statement has to use that the arm has size 14.
