# The `(15,14,14,14)` profile: everything established, as of 2026-11-22

Written after five Ultramath rounds (`smwqx1yfw`, `smwr0lr3q`, `smwr3llof`,
`smwr8io45`, `smwrfgma5`) and two external bundles. The chronological record is
`review/WALL_15141414_SWARM.md` (18 sections); this file is the organised state.

**Status: W2 is open. All 381 cases are OPEN. `R_4(3)` is unmoved at
`[51, 60]`. No case has been closed, no DRAT certificate exists for this
profile, and no bound has moved.** What follows is what is known and what is
excluded, with the check that establishes each item.

## 1. The target and the cover

`R_4(3)` lies in `[51,62]`; a frozen cover reduces `R_4(3) <= 58` to 113,179
cases (79,264 CERTIFIED, 31,751 OPEN). The seven profiles with at most two
critical colours hold the 11,585-case wall; this is the smallest of them.

At a vertex `v` of a triangle-free 4-colouring of `K_58`: `d_c(v) = |N_c(v)| <= 16`
(`R(3,3,3) = 17`), `sum_c d_c(v) = 57`; colour `c` is **critical** at `v` iff
`d_c(v) >= 15`; `w(v)` is the sum of the critical degrees (tickets sent),
`s_c(v) = #{u in N_c(v) : d_c(u) >= 15}` (senders), `H(v) = sum_c s_c(v)`
(tickets received), and `sum_v H = sum_v w`, so some root has `H >= w`.

**W2**: no triangle-free 4-colouring of `K_58` has a vertex of profile
`(15,14,14,14)` with `H(v) >= 15 = w(v)`. By T2 of
`.ultramath/smwqullhx/m8/lemmas.md` this empties the whole group.

The profile forces `n = 58` exactly (15+14+14+14 = 57), so no smaller-order
example exists. The frozen plans: `T---` thresholds `(15,1,1,1)` with 308 cases
(9 marking in the 15-arm, 299 in a 14-arm), `U---` `(3,5,5,5)` with 73 cases
(9 + 64), charge 14 both. Refuting a plan means proving each arm's threshold
fails — two separate statements, not one conjunction: for `T---`,
`s_0 <= 14` **and** `s_1 = s_2 = s_3 = 0`; for `U---`, `s_0 <= 2` and
`s_i <= 4`. *(Decoded from `joint_plan.choose_plan` and the ledger; the ledger's
per-row `charge` is the threshold `t`, not the group charge.)*

A weaker, uniform plan exists: `(6,4,4,4)` costs 313 + 73 rows, is admissible for
both template kinds, and asks only "no arm carries 6 senders (the 15-arm) or 4
(each 14-arm)", i.e. `H <= 5+9 = 14`. It needs no template case split. Its
catalogue is built (386 rows, sha256 `b8cbf0bb…`) and two core cases were probed.

## 2. Proved and kernel-checked

All in `lean/`, build `bash lean/build.sh` (88 s wall / 33 s CPU, green),
axioms only `[propext, Classical.choice, Quot.sound]`, no `sorry`, no
`native_decide` (34 declarations on `Check.lean`'s list):

| item | statement | where |
| --- | --- | --- |
| **L1 (mixture)** | `|N_f(x) ∩ N_g(u)| <= 5` for `f != g`, any `x,u` | `K58.mixture` |
| sub-arm form | the bound on any subset of a class | `K58.mixture_subset` |
| 4/5 split | inside an arm, at most five neighbours of any other colour | `K58.arm_part_le_five` |
| interface identity | `sum_{x outside} m_x = sum_{a in A}(d_c(a)-1)` | `K58.interface_count` |
| arm saturation | a 15-point colour-free set has at most 2 vertices outside with no edge into it (5 at 14 points) | `K58.armFar_*` |
| pair disjointness | `colour(x,x') = f => M_f(x) ∩ M_f(x') = empty` | `K58.model_pair_disjoint` |
| per-(`u,y`) rigidity | `u` a sender, `y in N_0(u)`, `f != 0`: the three counts are 4 or 5 (5,5,5 at a 16-arm) | `K58.model_pair_rigidity` |
| parity | `2e_i + n_i = 75`, `n_i` odd, `sum n_i = 15` | `K58.light_count_parity` |
| two-arm restriction | a genuine branch object restricts to a model of the 28-vertex two-arm instance | `K58.TwoArm.two_arm_restriction` |
| uniform child | all 15 arm points 0-critical + `m(x) <= 5` + `|V| = 58` force `d_0(a) = 15` and `m(x) = 5` | `K58.uniform_child` |
| charge 15 = all-critical | `armSenders r 0 = 15` iff every point of `N_0(r)` is 0-critical | `K58.armSenders_zero_eq_fifteen_iff` |
| branch = degenerate balance | balance plus sender-free 14-arms gives `s_0 = 15` | `K58.branch_of_balanced_no_small_arm_sender` |
| **classification** | every triangle-free 3-colouring of `K_15`/`K_16` is one of the two templates | `K58.Classified 15/16`, `lean/port/` |

**Provenance correction (2026-11-22).** `K58.TwoArm.two_arm_restriction` was a
*member artefact*, `.ultramath/smwrfgma5/m5/lean/TwoArm.lean`, and was cited in
§17 of the chronological record and in an earlier revision of this table as
kernel-checked **before it was in `lean/`** (`rg -n TwoArm lean/` was empty, and
`build.sh` built no such module). It is now `lean/K58/TwoArm.lean`, built after
`Arm` and registered in `Check.lean`. The theorem was and is true — the proof was
re-verified from the copied file — so no result that quotes it is void; the
citation was wrong at the time it was made.

The classification is the campaign's only formerly-unproved structural premise;
it is derived in `lean/port/` from the pinned `R_4(3) <= 60` development
(Lean 4.32.1 with that project's Mathlib, 53 s; `bash lean/port/build_port.sh`).
It is *not* citable from Kalbfleisch–Stanton/Heinrich — the upstream project
proves it rather than importing it.

Also proved in the record: the **six-point arm lemma** — at most five vertices
of `N_b(r)` are pairwise `a`-blocked, since six would give a triangle-free
2-colouring of `K_6` (sharp on all seven artefacts); and, under all-tickets-
returned `(R)`, `|C_c| >= 30` with equality forcing the colour-`c` graph on
`C_c` to be exactly `K_{15,15}`, and colour 0 critical everywhere in the uniform
branch (which is the ten-disjoint-partners condition).

## 3. The calibration object, and the filter it imposes

`artifacts/n48_z4z4_f0.col` is a Family-A configuration at **every** vertex:
profile `(15,11,11,10)`, sender vector `(15,0,0,0)`, `H = w = 15`. So any
proposed refutation of Family A that does not use the arm sizes `(14,14,14)` is
already false there. The verified `K_50` objects attain `H = w` at one-critical
vertices, and 7- and 8-arms there carry six and seven senders — so no
arm-size-uniform bound exists either. A good 44-vertex core with profile
`(15,14,14,0)` exists, so no arm core decides the profile.

## 4. The interface, exactly

With `m_x = |N_0(x) ∩ A|` over the 42 outside vertices:
`sum_x m_x = sum_{a in A}(d_0(a) - 1) = 210 + t`, `0 <= t <= 15` (t = number of
arm points with `d_0 = 16`). Five per outside vertex is **exactly saturable** at
arm size 15 (so no per-vertex interface argument can work here); at arm size 16
the count lies in `[224, 240]` with the top attained, so the forced-six theorem
for 16-armed profiles is inert. `14p <= 5(57-p)` holds iff `p <= 15`: the three
15-armed wall profiles are exactly those where the interface has no slack.

In the **uniform child** (`m(x) <= 5` everywhere) all of this is tight:
`d_0(a) = 15` for every arm point and `m(x) = 5` for every outside vertex;
coverage is 14 per arm point and 5 supports per outside vertex (210 both ways);
each `N_0(a)` is a classified template with 35 edges per ordinary colour; **five** senders are deficient per arm (the deficient colour is unique at each
sender, the three counts are odd and sum to 15, and both templates give 5,5,5);
every sender's support sizes are `(5,5,4)`.

The colour-split overlap identity
`sum_{colour-f pairs} |M_0(y) ∩ M_0(z)| = sum_a e_f(N_0(a)) - sum_{z in N_f(r)} m_0(z)`
evaluates to **455 per ordinary colour, 1365 in all** (= `15 * C(14,2)`) — a
*check* on candidate assignments, not a constraint: the total is forced by
coverage and the split by the templates.

## 5. Routes closed (each with the check)

| route | why it fails |
| --- | --- |
| linear counting in the `m_f(x,Q)` aggregates | the MILP is integrally feasible, even with part-row sums and sharper corollaries added |
| per-vertex interface bounds | five per vertex is exactly saturable at arm 15; the bound *is* the target |
| single-vertex template rigidity | all `216 = 6^3` join profiles are realisable in both templates, including `(0;5,5,5)` |
| per-vertex correlation (Theorem B) | the MIP with T-incidence booleans is optimal/feasible in 25 s |
| the type level (216 types) | feasible with a valid witness that satisfies the saturation bound; its 14 same-type slots show why it cannot be realised |
| the **pair level** (words + pair compatibility) | **SAT**, five encodings and five witnesses; no pair-level infeasibility proof can exist |
| the copy bound / `<= 16` extremal as an exclusion | every witness carries 40-42 distinct words; mutually consistent but not implied |
| the cap bundle | excludes 13 of 55,022 random balanced designs — a real but thin constraint |
| machine closure at the frozen encodings | UNKNOWN at every budget tried: 0/42 at 60 s, 0/9 at 300 s, 0/40 at 140 s with sound additions; the full uniform child (25,428 vars / 203,927 clauses) at 4.07 M conflicts; a compact exact child with six constraint families at 600 s |
| the `n = 60` engine's opening step | its criterion `w > (n-1) - L` needs 41 at `n = 58` and wall profiles have `w <= 32` |
| the short-arm ladder rungs | with `m(x)=5` and `d_0(a)=15`, `|X| = 42` is forced — orders 44-56 are different models, not the branch |
| the "gluing core" | the 0.01 s refutation came from an over-constrained CNF (a global mixture cap); the sound instance is UNKNOWN at 300 s |

Also closed, outside this profile: no `Z_58`-circulant good colouring of `K_58`
(DRAT-verified), and the 3,093 marked-path cuts of the external bundle are a
**module count of 15,183 classes**, not a clause reduction (the orbit has ~10^10
members).

## 6. The gap, located

Everything above the colouring is satisfiable, and the witnesses are far from
colourings: overlap masses **319/314/732** where a real colouring needs 455 each,
and **2,562** monochromatic triangles inside the 42. So the obstruction is the
internal colouring of the 42 vertices under the pair rule, together with the
three arms' internal 3-colourings — and the classification does not reach a
14-vertex arm.

## 7. What is live

1. **`(14,12) + XT` at 26 vertices.** Restrict the branch to `r`, `A` and two
   arms of sizes 14 and 12, with per-arm coverage (ten 5s, five 4s in a 14-arm)
   and cross-arm triangle-freeness. The families are hereditary under deleting a
   vertex, so **UNSAT at this rung refutes the uniform fully-sending branch**
   via the kernel-checked restriction theorem, needing both templates. Current:
   UNKNOWN at 400 s / 4.4 M conflicts. Its reach is counted in item 5 below:
   at most 7 of the 381 cases, one child each.
2. **Pair level + arm saturation** — the one kernel-checked constraint every
   known witness violates, never yet put in front of a solver with the pair level.
3. ~~**The `(6,4,4,4)` plan** — a uniform, kind-free statement set at 386 rows.~~
   **Dead**: audited clean (no errata defect) and probed one case per stratum —
   16 of 16 OPEN at 1.21-1.49 M conflicts, so plan choice is not the bottleneck and
   every admissible threshold vector is out of CDCL's reach at these budgets.
4. **Family B (73 cases)**: `s_0 <= 2` and `s_i <= 4`. The external bundle's
   items do not port (no `U---` row has charge 15); thresholds are already
   maximal.

5. **The reach of the branch, counted — the honest scope of items 1–3.**
   The branch is *not* forced by the profile: its criticality half is one
   hypothesis of the cover and its uniformity half (`m(x) <= 5`) a strictly
   stronger one. The frozen encoder splits every case into `all m(x) <= 5` and
   `some m(x) >= 6` (`WALL` §10), so obligations are (case, child) pairs. Under
   uniformity `K58.uniform_child` gives `d_0(a) = 15` for all fifteen arm points,
   so the two charge-15 rows whose marked class has size 16 have **no** uniform
   child (they are some-six only, closed on that side by the kernel lemma alone),
   and the seven with a 15-point marked class have one. **A refutation of the
   uniform fully-sending branch therefore closes 7 uniform children out of 381,
   plus 2 that are already empty — and needs the some-six companion before even
   those 9 rows fall.** No other row is implied: 363 impose a sender in a 14-arm
   and 9 impose `s_0 >= 3`, and no branch object pins either. Certified by
   `w/regen_cases.py` (381 = 381, all OPEN), `w/poset.py` (381 distinct pins, 0
   of 381·380 pairs with `pin_i ⊆ pin_j ∧ charge_i ≤ charge_j`), `w/closure.py`
   (0 of 381 refuted by colour refinement, five controls), and the kernel lemmas
   above; write-up `.ultramath/smwrmwgf7/m11/w/obligations.md`, rows listed in
   `w/seven_cases.txt`.

6. **The `U^-` twin must be built at charge 3, not at `d_0 = 15`.** The `U---`
   stratum's arm-0 threshold is 3, so refuting `s_0 = 15` there decides a formula
   the cover never emits; and at charge 3 heredity is unavailable, because
   `s_0 >= 3` is existential while the interface identity controls only the
   whole-arm sum. The same applies to the 363 arm-1 rows (`s_1 >= 1` or `>= 5`).

## 8. Errors, artefacts, corrections

* **A full 381-case "closure" that was void**: a lex order on twin codes forced
  strictly increasing codes, so a class of 9-10 twins over 4 colours is
  pigeonholed before the graph clauses matter. (§5 of the chronological record.)
* **`dense.marked_threshold` returns a single empty clause** when the requested
  charge exceeds the available guards — a void-closure generator. Reproduced:
  charge 15 gives 10,794 clauses, charge 16 or 20 gives `[[]]`. In `ERRATA.md`.
* **A global mixture cap** in a three-arm gluing instance (`|N_0(a) ∩ all arms|
  <= 5`) contradicted the branch by arithmetic; the "gluing core" it produced
  does not exist. In `ERRATA.md`.
* **My own errors, both corrected by members**: (i) I claimed the
  all-tickets-returned bound was 16 where it is 30 (the two neighbourhoods of
  adjacent vertices are disjoint and both in the class); (ii) I conflated the two
  coverage statements — each arm point is covered 14 times, each outside vertex
  lies in 5 supports.
* **External claims corrected here**: the `(15,14,14,14)` "type-level route
  closed" verdict was too strong until a witness satisfying the saturation bound
  was produced; the "at least 26 all-four-colour words" step is vacuous (about
  254,610 such words exist) and the real statement is "at most 16 of the 42 have
  a missing ordinary colour"; the pair level is satisfiable.

## 9. Where things are

* `review/WALL_15141414_SWARM.md` — the chronological record, 18 sections.
* `review/ERRATA.md` — the encoder defects with reproductions.
* `lean/K58/{Mixture,Corollaries,Arm,TwoArm,Link14,Model}.lean`, `lean/port/` — the
  kernel-checked base and the classification.
* `results/swarm-smwqx1yfw/` — member reports from round one.
* `.ultramath/smwr*/` — each swarm's member directories (gitignored; scripts and
  witnesses). The witnesses named above live there.
* Toolchain: `.scratch/k58/.venv/bin/python` (python-sat 1.9.dev22),
  `.scratch/satcheck/bin/{kissat,drat-trim}`, `python3 tools/verify_coloring.py`.

## 10. The newest layer (rounds four to six)

**Proved.** In the branch under all-tickets-returned, `M = max_{u != v}
|N_0(u) ∩ N_0(v)| >= 7` *(paper proof, six elementary lemmas)*; the arm-pair
codegrees sum to `C(15,2) + 42*C(5,2) = 525`, so the mean is exactly 5 and **some
pair of senders shares at least six points**; the 42 blocks `N_0(x) ∩ A` are not a
`2-(15,5,4)` design.

**Improved lemma.** The independent-14 bound is **`|armFar| <= 4`**, not the 5 that
is kernel-checked — the K59 argument transfers because its only size input is the
exchange rule on 16-sets with a 15-core. So `armFar_le_five` is not tight.

**Type rigidity.** A pair of 15-classes sharing 14 points is necessarily the same
template type; **mixed `T^-`/`U^-` classes overlap in at most 12**, and 12 is
attained. Certified by exact maximum-common-induced-subgraph computation (two
algorithms plus DRAT), and the decisive calibration is that the *same computation
at `K_16` also gives 12* — so K59's "mixed codegree at most 7" is a host-level
fact, not a template fact.

**The high-overlap cluster.** At most 7 senders can pairwise share 14 class
points; at a common 14-core only two spoke vectors occur (clone and deficiency), at
most two classes per vector, so **at most four classes split 2+2**, twin pairs
joined in colour 0 with disjoint arm supports. **Realisable**: valid 20- and
22-vertex colourings carry the 2+1 and 2+2 clusters. So the regime is a small rigid
object that nothing contradicts.

**Routes closed since §5.** The pair level (SAT, five witnesses). The two-arm
instance: **`14+14`, `14+13` and `14+12` are all SAT** (verified witnesses), so
"UNSAT at `14+14` proves the branch" is impossible — and the reason is that with
two arms the columns reach only 8-10, not 14. The "gluing core": its 0.01 s
refutation came from a global mixture cap that contradicts the branch by arithmetic.

**What is left.** The **three-arm instance at order 58** (pair level plus arm and
cross-arm triangle-freeness, columns reaching 14), and the sharpest subsample of it,
**`(14,12) + XT`**: by heredity — everything passes down under deleting an arm
vertex except the per-arm degree profile, which is indexed by arm size — UNSAT
there with the sound families closes the uniform fully-sending branch. The object
is `p cnf 7574 46752`; with the words fixed its pair stage is 531 variables and
solves in under a second. **It cannot be cubed on word choices** (measured
exactly, both templates): the depth-1 pools are 17,846 and 31,731 admissible
words, depth two is already `1.08e8` and `3.14e8` ordered pairs, depth three at
least `1.1e8` and `2.7e8`, each added word multiplies by `6e3`–`1e4`, and all
twelve free is `~1.5e56` multisets. The pool is not `Aut`-invariant, so orbital
counting does not shrink it. Any factorisation has to cube on something else —
pair colours, or the arm's isomorphism class. It has now been **audited exact** (bit-identical
regeneration in both templates, all 46,752 clauses classified with no strays, the
97 cardinality clusters rebuilt from the auxiliary graph and their bounds measured
by SAT, and no global cap, so none of the errata failure modes is present), and
`XT` is **certified non-vacuous**: pinning the recorded `14+12` witness's words
without it is SAT, with it UNSAT and the DRAT replays. A `U^-` twin exists
(`smwrfgma5/m3/cnf/u_14_12_xt.cnf`) and audits identically.

**A tool.** The two-root spoke table at `n = 58`: 56 entries, corner
`|N_0(u) ∩ N_0(v)|`, diagonal zero, and the off-diagonal cap `T[i][l] <= 5` from
mixture; verified on 1,063 tables. **The root can never be in a maximising pair**
(its codegree is 5 for outside vertices, 0 for arm points, while `M >= 6`).
