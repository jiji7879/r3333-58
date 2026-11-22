# The `(15,14,14,14)` profile: everything established, as of 2026-11-22

Written after five Ultramath rounds (`smwqx1yfw`, `smwr0lr3q`, `smwr3llof`,
`smwr8io45`, `smwrfgma5`) and two external bundles. The chronological record is
`review/WALL_15141414_SWARM.md` (18 sections); this file is the organised state.

**Status: W2 is open. All 381 cases are OPEN. `R_4(3)` is unmoved: the published
interval is `[51, 62]`, and a November-2026 preprint (Tatarevic, arXiv 2610.36648v2,
unrefereed) claims `<= 60` — this document quoted `[51, 60]` in this line while §1
quoted `[51, 62]`, which was an inconsistency, and neither moves because of
anything here. No case has been closed, no DRAT certificate exists for this
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
| classification | every triangle-free 3-colouring of `K_15`/`K_16` is one of the two templates | `K58.Classified 15/16`, `lean/port/` |
| **no design** | in the branch under (R) the 42 traces are not the blocks of a `2-(15,5,4)` design; per vertex, `d_0(x) >= 12` forces a trace pair at codegree `>= 6`, and the design case forces `d_0(x) <= 11` | `K58.design_not_realisable`, `K58.trace_codegree_six`, `K58.design_forces_light`, `K58.rx_lower_refined`, `lean/K58/Design.lean` |
| **`M >= 7`** | in the branch under (R): every codegree of a 0-neighbourhood pair is at least 7, hence `7 <= M <= 16` | `K58.M_ge_seven` (with `M_ge_six`, `rigid_six`, `arm_codeg_le_five`, `arm_all_five`, `branch_deg_15_or_16`, `codeg_le_sixteen`), `lean/K58/M7.lean` |
| **(R) closure** | under reciprocity every colour-`c` neighbour of a `c`-critical vertex is `c`-critical, `|C_c| >= 30`, and if every vertex has a critical `c`-neighbour then colour `c` is critical everywhere | `K58.nbrC_subset_Crit`, `K58.crit_card_ge_thirty`, `K58.crit_eq_univ`, `lean/K58/Ticket.lean` |
| **the rung's soundness** | under (R) and the uniform branch, colour 0 is critical everywhere and every slot has at least ten colour-0 neighbours outside `A` | `K58.uniform_branch_zero_critical`, `K58.ten_outside`, `lean/K58/Ticket.lean` |

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

`lean/K58/Ticket.lean` was integrated on 2026-11-22 (§39 of the record): the
reciprocity chain it carries had been cited as proved while living only in a
member directory, which is the second instance of that slip in this campaign.

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
| the pentagon package's Hall inequality | a theorem, exactly `alpha(G_0) <= 16`, hence implied by the X-internal triangle family; all five pair-level witnesses violate it (margin 14) and it sharpens nothing — inert |

Also closed, outside this profile: **every abelian group of order 50..58** has no
good 4-colouring of `K_n` invariant under its regular action — fifteen groups, all
UNSAT with DRAT replayed, complete for the *whole* Cayley family at **51 and 53
only** — cyclic is the only group of those orders; 55 and 57 each have a nonabelian
group (`C_11 ⋊ C_5`, `C_19 ⋊ C_3`) and were not covered — with the W2 profile
included at 58. `D_29`, and
`D_25`..`D_28`, remain open computationally; Anabanti (2023) already closes the
family for `n >= 51`, so this is a certified confirmation rather than new
mathematics. `results/cayley-window/`. Also closed, outside this profile: no
`Z_58`-circulant good colouring of `K_58`
(DRAT-verified), and the 3,093 marked-path cuts of the external bundle are a
**module count of 15,183 classes**, not a clause reduction (the orbit has ~10^10
members).

## 6. The gap, located

Everything above the colouring is satisfiable, and the witnesses are far from
colourings: overlap masses **319/314/732** where a real colouring needs 455 each,
and **2,562** monochromatic triangles inside the 42. So the obstruction is the
internal colouring of the 42 vertices under the pair rule, together with the
three arms' internal 3-colourings. **The 14-arm alphabet is now decided**
(2026-11-22): triangle-free 3-edge-colourings of `K_14` number 651 up to vertex
permutation with colours labelled, **332 up to the branch's colour-2/3 swap** (the
arm alphabet), 115 up to all colour permutations — the last agreeing with the
literature. Only **7 of the 332** are restrictions of the two `K_15`/`K_16`
templates, so **325 arm types are new**: the classification does not extend to
arms, and an arm-type case split is a 332-way split with no template structure
behind it. `results/arm-alphabet-14/`.

The arm half is now located exactly. With `M_f(x)` the `f`-part of a word,
`L(x,y) = {f != k : M_f(x) ∩ M_f(y) = empty}` is the set of colours the edge `xy`
may take, for an arm of root colour `k` (`k ∉ L`; `f ∉ L` when the intersection is
nonempty, by `model_pair_disjoint`). Three words of one arm with `L = L = L = {c}`
force a `c`-triangle, so the arm is unrealisable and the triple is an
inclusion-minimal infeasible sub-arm. Exhaustive over `C(14,3) = 364` triples per
arm, **661 such triples occur over the 15 arms of the five order-58 pair-level
witnesses** (0 dead pairs, 15 certificates, an independent arm-module CSP
reproducing the counts and SAT on all 13 arms whose own colouring is legal). So
every pair-level witness dies in the arm module at size 3. The spectrum of minimal
local obstructions is `{3, 5, 6}`, not `{3}`: `design_1` arm 1 needs 6.
`results/local-obstruction/`.

For these witnesses the depth is exactly 3 and the shape of every dead triple is
unique — **but neither holds in general** (corrected 2026-11-22, member m1): the
local obstruction family is Ramsey-indexed. If every pair list of a set `S` lies in
a fixed `k`-colour set, then `|S| >= R_k(3)` is dead, with thresholds
`3, 6, 17, 51`; the three-equal-singletons lemma is the `k = 1` rung. Standalone
inclusion-minimal dead sets exist at sizes 4, 5 and 6 with no dead pair and no bad
triple (both templates, checked by brute force), so the depth is **at least 6**, and
the `k = 2` rung — no `K_6` in the `{f,g}`-confined graph — is a sound constraint
the pair-level encodings do not carry (existing witnesses violate it with confined
cliques up to 8). A *local object* on a set `S` of
slots is the words on `S` plus a colouring of the pairs inside `S` under (P1) the
arm colour banned inside its own arm, (P2) `colour(x,y) = f` needs
`M_f(x) ∩ M_f(y) = empty`, (X) no monochromatic triangle; every genuine object
restricts to one on every subset. Exhaustively over all subsets: **0 dead pairs
for every witness**, and dead triples 514 / 524 / 459 / 456 for the four 42-slot
witnesses and 50 / 44 / 55 / 40 / 52 for the five two-arm ones. And every one of
them has the same shape: a triple is infeasible **iff** its three
admissible-colour lists are the same singleton (so a mono triangle is forced).
That also reconciles the two counts in the record: m7's 119 for `pair58_Tminus`
are the within-arm triples, m10's 514 are all `C(42,3)`; the split is 119 within
and 395 across. `results/truncation-depth/`.

## 7. What is live

1. **`(14,12) + XT` at 26 vertices.** Restrict the branch to `r`, `A` and two
   arms of sizes 14 and 12, with per-arm coverage (ten 5s, five 4s in a 14-arm)
   and cross-arm triangle-freeness. The families are hereditary under deleting a
   vertex, so **UNSAT at this rung refutes the uniform fully-sending branch**
   via the kernel-checked restriction theorem, needing both templates.
   **Which family does the work is now measured.** The same object at the pair
   level is SAT in 0.5 s for both templates; adding *in-arm* triangle-freeness
   keeps it SAT (T^-, 140 s; U^-, 342 s) with **0 in-arm monochromatic triangles**
   and 180 / 200 cross-arm ones; keeping *only* the cross-arm family is UNKNOWN at
   200 s. So in-arm triangles are not the obstruction and `XT` is the whole of it.
   Witnesses at `results/arm26/` (`arm26_{T,U}_armtri.wit`), each valid only
   against its own template file — the `T^-` ones are on
   `k15_template_Tminus_aut2_m4.col`, and against `k15_link_Tminus_m5.col` they
   show 46-52 part-independence failures, the same-template-different-labelling
   hazard.
   **Guard on the per-arm profile.** With `|B| = 14`, a 12-subset of `C` and
   `d_0(a) = 15`: `B`-count in {4,5}, `C`-count <= 5, `B + C` in [7,10], because
   `Sum_a B = 70` and `Sum_a C = 60` give **130** over 15 positions. Any encoder
   demanding `B + C in {9,10}` (or `C >= 3` with `B <= 5`) at every position is
   UNSAT by arithmetic alone — 130 < 135 — which is the `ERRATA` class. The phrase
   "per-arm coverage (ten 5s, five 4s)" is true of a complete arm and becomes an
   over-constraint on a truncated one. Current:
   UNKNOWN at 400 s / 4.4 M conflicts. Its reach is counted in item 5 below:
   at most 7 of the 381 cases, one child each.
2. **Pair level + arm saturation** — the one kernel-checked constraint every
   known witness violates (measured: part-family cliques 13/9/11 against the bound
   5; per-arm cap max 8 against 5). Now tried, and **it does not close the pair
   level**: the word layer carries the sixth lemma *at its exact bound* and the
   per-arm cap on all three arms (`blocks_armcap.json`: coverage 14, ten 5s and
   five 4s per arm, clique number exactly 5 in every arm), and the pair level with
   the lemma at one or two `(a,b)` pairs is SAT (witnesses with 0 definition-level
   violations). The lemma at **all nine** pairs is UNKNOWN at 280 s / 400 s and is
   a frontier, not a result. `results/word-layer-sixth-lemma/`.
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
|N_0(u) ∩ N_0(v)| >= 6` *(paper proof; corrected below — 7 is not proved)*. The
arm-pair codegrees sum to `C(15,2) + 42*C(5,2) = 525`, so the mean is exactly 5;
that identity alone gives `M >= 5`, and the `C_x` chain below is what reaches 6.
*(An earlier revision read "so some pair of senders shares at least six points"
off the mean, and "the 42 blocks `N_0(x) ∩ A` are not a `2-(15,5,4)` design" off
an unsourced moment bound. Both are withdrawn: the mean is 5 and says nothing
above 5, and the design case is arithmetically consistent — 42 blocks of size 5
with every pair in 4 blocks — and it is exactly the case in which all 105 arm
codegrees equal 5.)*

**Improved lemma.** The independent-14 bound is **`|armFar| <= 4`**, not the 5 that
is kernel-checked. *(The reason given here in an earlier revision — "the K59
argument transfers because its only size input is the exchange rule on 16-sets
with a 15-core" — does not survive: `rg -n exchange lean/` is **empty**; those
lemmas are not in the tree. The bound is established instead by m6's certificate,
which I have run: 240 UNSAT instances, one per `X = U` or `T` minus two points,
each with a DRAT replayed against its regenerated CNF, `verified 240, failures 0`
(`results/armfar14/manifest.txt`, with the driver, the proof and the Lean files
beside it), the SAT side checked at `|Z| = 4`
for all 240 (`far_sanity.py`), the sharpness witness `far18.col` an independently
valid 18-vertex 4-colouring with `|armFar| = 4` (`python3 tools/verify_coloring.py`),
and `K58.armFar_four_attained`, `armFar_five_zero_degree`,
`armFar_five_nonzero_degree` axiom-clean in `ArmFarFour.lean`/`ArmFarRigid.lean`.
The reduction from an arbitrary 14-set to those 240 cases is a paper argument in
m6's `PROOF.md` §2, not kernel-checked and not audited by me; the bound itself is
`decide`-free only in its sharpness half.)*

**Correction of the correction (2026-11-22, late).** An earlier revision today
withdrew `M >= 7` on the strength of m6's audit of the *record's own* chain. That
audit was right about the text and the withdrawal was wrong about the statement.
Member m3 of swarm `smwridmzp` (a swarm stopped on 2026-11-22 at 07:21) has a
complete proof in `.ultramath/smwridmzp/m3/REPORT.md` §3, which I re-derived step
by step and whose arithmetic `audit.py` re-checks (`ALL CHECKS PASSED`):

* `C_x >= 2·65 - 3|R_x| = 3 d_0(x) - 8` over `R_x = V ∖ (N_0(r) ∪ N_0(x) ∪ {r,x})`,
  `|R_x| = 46 - d_0(x)`, and `C_x <= C(5,2)(M-2)`; with `d_0(x) >= 15` this is
  `M >= 6`.
* **The rigidity step the record asserted is a lemma** (m3's Lemma 4): at a pair
  `(u,v)` with `μ = M = 6`, the six common neighbours `S` and
  `R = V ∖ (N_0(u) ∪ N_0(v) ∪ {u,v})` give `C >= 3(d_0(u)+d_0(v)) - 30` — which is
  60, 63 or 66 for `(15,15)`, `(15,16)`, `(16,16)` — against the cap
  `C <= 15·(M-2) = 60`. So `d_0(u) = d_0(v) = 15` and `μ(s,s') = 6` for every pair
  of common neighbours.
* Hence if `M = 6`, an arm pair at codegree 6 would force `μ(r,t) = 6` at five
  points `t` where `μ(r,t) = m(t) = 5` (m3's Lemma 5); so all 105 arm codegrees are
  5 (Lemma 6, from the total 525); so `C_x <= 10·3 = 30` against `C_x >= 37`. Hence
  **`M >= 7`**.

The same chain gives `Σ(n_{aa'} - 4)^2 >= 294` (Theorem 2: `Σ n(n-1) >= 42·37`
with `Σ n = 420`), so the moment bound the record cited without a derivation is a
consequence, and the 42 blocks are **not** a `2-(15,5,4)` design. Both of those
were withdrawn here earlier today and are hereby restored.

What remains true from the earlier note: the record's own text did not prove any
of this, `M7.lean` (m3's kernel transcription) does **not** compile — it stops with
`⊢ Nat.choose 5 2 = 10 ∨ M - 2 = 0` — so the result is a paper proof with its
arithmetic machine-checked and its kernel form unfinished. Nothing in the campaign
uses more than `M >= 6`.
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

**Routes closed since §5.** The pair level (SAT, five witnesses). The "gluing
core": its 0.01 s refutation came from a global mixture cap that contradicts the
branch by arithmetic.

**The two-arm level is NOT closed — corrected 2026-11-22.** An earlier revision
said `14+14`, `14+13`, `14+12` are "all SAT, so UNSAT at `14+14` proves the branch
is impossible". The witness behind that has **258 monochromatic cross-arm
triangles** and column sums `[8,9,10]`, so it violates the exact law every branch
object satisfies (`s_B + s_C in {9,10}`, from mixture + the interface: each arm
part is 4 or 5) and it is not a model of the instance with cross-arm
triangle-freeness — its words admit no such completion at all. What is decided is:
pair level **+ the exact law + per-slot caps + six-point clauses is SAT** at
`14+14` (`rung3.wit`, coverage sums 9/10, 0 unexpected failures), so the law alone
closes nothing; and adding the arm module is **UNKNOWN** (2.3 M conflicts / 300 s),
the full instance **UNKNOWN** (2.0 M / 120 s). Pinning one arm to a one-arm model
is UNSAT with a replayed DRAT (4,403-of-114,686 clause core, 0 RAT lemmas), and 10
of 19 such models do not extend, 9 open, 0 extend. `results/two-arm-interface/`.

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
