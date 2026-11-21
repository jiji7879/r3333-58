# The `(15,14,14,14)` profile: what one swarm settled, and what it did not

Swarm `smwqx1yfw`, 8 members (deepseek-v4.1-flash, max reasoning, 300 steps,
300 min), run 2026-11-21. **Result: no family refuted, no case closed, no bound
moved.** What it produced is a set of verified negatives that close three
research routes, one calibration object that filters proposed proofs, one exact
reduction, and one reformulation of the cover's plan choice.

Everything marked *(verified here)* was re-derived by the coordinator
independently of the member's code, usually with a different method. Member
reports are copied to `results/swarm-smwqx1yfw/`; the swarm's own directories
(gitignored) hold the scripts named below.

## 0. The target, and the decode

`W2(15,14,14,14)`: no triangle-free 4-colouring of `K_58` has a vertex of
colour-degree profile `(15,14,14,14)` with `H(v) >= 15 = w(v)`. By T2 of
`.ultramath/smwqullhx/m8/lemmas.md` this empties the 381 frozen cases at once.

Case structure *(verified here from `joint_plan.choose_plan`)*: the frozen plans
are `T---` with thresholds `(15,1,1,1)` (308 cases) and `U---` with `(3,5,5,5)`
(73 cases), charge 14 = `w-1` in both. The ledger's per-row `charge` column is
the threshold `t`, not the group charge `copies*(t-1)` — m2's `NOTE.md` §2c read
it as the group charge and so printed ">= 4 senders" where the plan says `>= 5`.
Refuting the cases gives, per family, two separate statements (not one
conjunction): `T---` needs `s_0 <= 14` *and* `s_1 = s_2 = s_3 = 0`; `U---` needs
`s_0 <= 2` and `s_i <= 4`. Either family falls to `H <= 14 < 15`.

## 1. Routes now closed

### 1.1 Linear counting cannot prove Family A (m8, d1)
Take the aggregate variables `m_f(x,Q)` (colour-`f` edges from `x` into part
`Q`) with L1, arm independence, `sum_f d_f = 57`, `9 <= d_f <= 16`, the
part-consistency equations, L3/L3', the Family-A hypotheses, `2e_f(S) = 70` and
the sharp 17-set bounds. The MILP is **integrally feasible**. *(verified here:
I added the part-row-sum equations `sum_f m_f(x,Q) = |Q| - [x in Q]` — which also
encode L3 inside the arms — and `E_f(S,A_f) >= 10` in place of m8's `>= 4`; both
runs are still HiGHS-Optimal.)* So no linear counting argument in these
variables proves Family A; the missing step must correlate two vertices.

### 1.2 The interface route is the target in disguise (m5, d8)
With `A = N_c(v)`, `X = V \ (A u {v})`, `m_x = |N_c(x) cap A|`:
`sum_{x in X} m_x = sum_{a in A}(d_c(a) - 1)` *(verified here on 588 arms)*, so
with `A` fully critical and `|A| = 15`, `sum m_x = 210 + t`, `0 <= t <= 15`,
over 42 vertices: mean `<= 5.357`. Hence "every outside vertex has `>= 6`
colour-0 neighbours in the arm" needs `252 > 225` and is *equivalent* to Family
A being empty — not a lemma. The per-vertex version fails anyway in real
objects (`k50_sanity_f2.col`, `v=4`, `x=48`, `m_x = 1`).

### 1.3 Single-vertex template rigidity is vacuous (m5, d10)
A join type of `x` into the pinned 15-arm is a 4-tuple `(m_0;m_1,m_2,m_3)`,
and `A u {x}` is triangle-free iff each `M_f` is `f`-independent; nothing else
is imposed. All `216 = 6^3` profiles are realised in **both** templates,
including `(0;5,5,5)` *(verified here by 216 MILPs per template)*. So the arm's
internal structure cannot supply the missing constraint.

### 1.4 The same-colour bound is a trap (m7, d2; m8's L2)
`|N_a(x) cap N_a(q)| <= 5` would close a case CNF in 0.1 s and is **false** —
the same-colour intersection reaches 16 in verified K_50 colourings. Recorded
because a 0.1 s "closure" from it would be a fabricated certificate.

### 1.5 Family B's machine route is exhausted at 140 s (m7, d2)
All 73 family-B CNFs rebuild clause-for-clause identical to the frozen
encoders, and the frozen base carries no *explicit* degree cap (harmless:
`d_c <= 16` follows from `R(3,3,3) = 17`). With the sound additions
`S1 (d_c <= 16)`, `S2`, `S3`, `S6` and the guard clause, 0 of 9/20/40 cases
close at 140 s. This is at the easiest thresholds available: the plan needs
`sum(t-1) <= 14`, and with `t_0 = 3` that forces `t_i <= 5`.

### 1.6 Per-vertex correlation does not close Family A either (m8, d1, second round)
The instruction after m8's first report was to put its three-vertex correlation
inequality (Theorem B) into the MILP. It did, in three strengths: aggregates plus
the theorem in aggregate form (feasible, and the aggregate form is *provably
vacuous*: LHS `>= 9 E_0(S,T) >= 1890` against RHS `<= 825`); per-vertex form with
`T`-internal incidence booleans, row sums and products (MIP **Optimal in 25 s**,
and the witness point re-verified row by row without the solver: 0 of 1438 and
0 of 11781 rows violated, all entries integral); and with `T`-internal
triangle-freeness added (LP feasible, MIP unresolved at 600 s — open, not a
result). So per-vertex Theorem B with the incidence structure is still feasible:
the correlation this swarm could actually state is not enough. What m8 names as
the remaining gap is the per-`(u,y)` rigidity `|N_f(y) cap N_0(u)| in {4,5}`,
which is strictly stronger than its sum — that is the form to try next.

### 1.7 Adding implied constraints does not close a case (m3, d9)
Case `baa4e014` with four implied clause families added (302,954 clauses: the
degree cap, the sender read-off, L1 at the root, `alpha = 5` visibility): Kissat
returns UNKNOWN at 240/240/300 s, no certificate. With m7's family-B result
(§1.5) and the earlier 0/42-at-60 s and 0/9-at-300 s measurements, the machine
route at this profile is dead at every budget tried, with or without the
sound additions.

## 2. What is proved and can be used

### 2.1 The calibration object (m5) — filters proposed Family-A proofs
`artifacts/n48_z4z4_f0.col` is a Family-A configuration at **every** vertex:
profile `(15,11,11,10)`, sender vector `(15,0,0,0)`, `H = w = 15`
*(verified here)*. So any proposed refutation of Family A that does not use the
arm sizes `(14,14,14)` is already false at `(11,11,10)`. This is the standard
test for candidate proofs, alongside the older `k50_*` objects.

### 2.2 Arm-set saturation (m8)
For an `m`-set `X` with no colour-`c` edge inside, the set
`Z = {y notin X : no c-edge into X}` has `|Z| = 0` for `m = 16`, `<= 2` for
`m = 15`, `<= 5` for `m = 14` *(verified here; the `m = 15` bound is attained in
the K_50 objects)*. Corollary `E_f(S,A_f) >= 10` at a fully critical 15-arm —
valid but weak (measured 40/35/35 at `n = 48`).

### 2.3 An exact 42-vertex reformulation of Family A (m5)
Family A is equivalent to: 42 vertices labelled `14/14/14`; each with a join
type into the pinned 15-arm (all 216 available); same-arm edges avoid the arm
colour; for `x, x'` joined in colour `f`, `M_f(x) cap M_f(x') = empty`; no
monochromatic triangle inside the 42; each `a` in the arm has `>= 14` colour-0
neighbours in the 42; every 14-arm vertex non-sending; `d_c <= 16`.
*(Triangle-type analysis checked here.)* The whole difficulty is the internal
colouring of the 42 plus the joint effect of the pair conditions.

### 2.4 The extremal 6-blocks, settled (m5 and m4; corrected twice here)
In the extremal configuration (`t = 0`, all `m_0 = 5`) the types with an empty
part come in exactly **6** configurations per (empty part, ordered colour pair),
in both templates; each configuration splits the arm into `M_0, M_g, M_h` of
size 5 with `M_f` empty. The three block families behave differently
*(recomputed here)*:

* the **`M_0` parts** form a 1-`(15,5,2)` design: each of the 15 arm vertices
  lies in exactly 2 of the 6 blocks, and the 60 pair incidences cover 60 of the
  105 pairs exactly once. m5's "2-(15,5,2)" was the *replication* number 2, not
  `lambda`;
* the **`M_g` and `M_h` parts** are not regular: point degrees 1, 2 and 3 (five
  points of each), pair multiplicities 1 for 40 pairs and 2 for 10.

For `T^-`, empty part 0, `g = 1`, `h = 2` the six `M_g` blocks are
`(0,6,7,10,11) (1,5,6,9,10) (2,3,7,11,14) (2,3,8,12,13) (2,5,6,11,13) (4,5,8,9,13)`.
An earlier version of this note called the family "not a design" — that was
computed on the `M_g` parts and, as m4 pointed out, answered a different
question from the one m5 asked. Both descriptions are now above, with the
objects named.

### 2.5 The guard / read-off lemma (m3, m7; general in `n`)
If `x in N_c(v)` and `d_c(x) >= 15`, then `N_c(x)` meets each of the three
other arms of `v` in exactly 4 or 5 vertices (the `(5,5,4)` / `(5,5,5)` split),
so the colour-`c` interface from a fully critical arm is `210 + u` with
`0 <= u <= 15` *(verified here on 148 fully critical 15-arms)*.

### 2.6 The plan choice is a free knob, and the frozen plan is the hardest one (m6, d4)
Any threshold vector with `sum(t-1) <= 14` is admissible, and admissible for
**both** template kinds. The frozen `T---` plan `(15,1,1,1)` demands the trivial
`s_0 <= 14` and the hardest possible statement `s_i <= 0`. The balanced
`(6,4,4,4)` — `sum(t-1) = 14` — asks only "no arm carries 6 senders (the
15-arm) or 4 (each 14-arm)", i.e. `H <= 14`, with **no template case split**,
at 313 + 73 cases. *(Pricing verified here from `joint_plan.arm_options`: the
template arm costs 23 cases for `t <= 3`, 14 for `4 <= t <= 12`, 9 for
`t >= 13`; the three `-` arms are one orbit each and cost 299 (`T`) or 64 (`U`)
for every `t`, so `(15,1,1,1) = 308`, `(6,4,4,4) = 313`, `(3,5,5,5) = 322`,
`U` always 73.)* For family B, `(3,5,5,5)` is already optimal.
A catalogue for `(6,4,4,4)` was built (`catalogue_6444.jsonl`, 386 rows,
sha256 `b8cbf0bb...`) and two core arm cases probed: UNKNOWN at 300k conflicts
in 38 s and 33 s. That experiment was cut off by the swarm's budget.

### 2.7 Kempe invariance, multiset level only (m3, d9)
A Kempe swap on a component of the `(c,c')`-subgraph keeps triangle-freeness
and the **multiset** of `(d_a(v), s_a(v))` at every vertex *(checked here on
five artefacts via m3's script)*. It does not keep the labelled degrees, so no
argument may assume "colour 0 is still the 15-arm at `r`" after normalisation.

### 2.8 L1 is now kernel-checked in the repository's own development (m5, d11)
The lemma every other member's argument uses is formalised against the
repository's definitions and landed in `lean/`:

| file | contents |
| --- | --- |
| `lean/K58/Mixture.lean` | `nbr`, `nbr_card`, `nbr_indep`, `card_ne_ne`, **`mixture`** (= L1: `#(nbr G x f ∩ nbr G u g) ≤ 5` for `f ≠ g`, any `x u`, no adjacency hypothesis) |
| `lean/K58/Corollaries.lean` | **`mixture_subset`** (the bound on a sub-arm — the encoder-ready form) and **`arm_part_le_five`** (the 4/5 split inside an arm) |
| `lean/K58/Check.lean` | the four `#print axioms` lines, alongside the existing 31 |

`mixture` is proved by taking a 6-subset of the intersection, observing that
every edge inside it avoids both colours, and contradicting the repository's
`two_colour_six` (R(3,3) ≤ 6). Located by the coordinator: the member's files
were built independently in its own directory, then copied in, `build.sh`
extended (order `... DegreeCap Mixture Corollaries Templates ...`), and the full
build re-run: **green in 25 s, all four theorems axiom-clean**
(`[propext, Classical.choice, Quot.sound]`, no `sorry`). Not formalised: the
interface identity I1 (its `deg - 1` partition step did not get through the
elaborator) and J1/J3. So the swarm's most-used lemma, and only that, is now a
kernel-checked fact of the repository.

## 3. What is still open

* `W2` itself, and the two statements of §0. The profile is now known to need a
  *correlation* between at least two outside vertices; nothing local, linear or
  single-vertex suffices.
* The pair-level distribution problem of §2.3: 42 join types with
  `sum m_0 = 210 + t`, `t <= 15`, pairwise compatible in the colour of the edge
  between them, 14 per arm, every arm vertex non-sending. Infeasible would be a
  proof; feasible would pin down exactly what a missing lemma must say.
* The balanced-plan experiment of §2.6, unfinished: build the `(6,4,4,4)`
  catalogue, run a stratified sample at 90-120 s, and compare with the frozen
  baseline (0 of 42 at 60 s, 0 of 9 at 300 s).
* Campaign-level and untouched here: the marking lemma, the Lean bridge at
  `n = 58`, and the classification of critical 15-colourings
  (`Templates.Classified n`, stated and unproved).

## 4. Reproduction

* Reports: `results/swarm-smwqx1yfw/*.md`; scripts in `.ultramath/smwqx1yfw/m*/`.
* Coordinator's independent checks: the profile/ticket script
  (`.scratch/prof_probe.py`), the MILP strengthening (`.scratch/m8check.py`),
  the 216-per-template join enumeration and the 6-block enumeration (inline in
  the session; both reproduced in the member scripts `m5/join.py`, `m5/j3.py`).
* One case at a 15 s budget:
  `.scratch/k58/.venv/bin/python tools/solve_weak.py --bundle .scratch/k58
  --out <dir> --kissat .scratch/satcheck/bin/kissat --workers 1 --seconds 15
  --limit 1 --shuffle 3`.

## 5. A void closure, caught

One member (m1, direction d7 — canonical forms) produced
`.ultramath/smwqx1yfw/m1/work/sweep/`: 381 DRAT files, a log with every case
`UNSAT, verified: true`, ~500 KB per proof, against cases that resist 300 s at
the pinned solver. Its construction adds lex-leader symmetry breaking for the
twin classes of the pinned units (classes of size 10, 9, 9 in the first case).
**The closures are void: the lex clause set is unsatisfiable whenever two twins
of one class share the colour of an edge to the first witness, so a class of 9
or 10 twins over 4 colours is refuted by pigeonhole before the case is looked
at.**

The symmetry claim itself is sound — I checked all 117 transpositions of the
three classes of case `5da5b4ca…` against the 309 pinned units: every one is an
automorphism. The bug is in `lex_case.lex_clauses`. For the first witness the
prefix is empty (`head = []`), and the clause `[-eq] + head` becomes the unit
`[-eq]`; the surrounding clauses force `eq` true exactly when the two vertices
have the same colour at that witness. So the encoding forces *strictly
increasing* codes, not non-decreasing ones. Measured directly on the clause set
(all code assignments to a class of `k` twins over `m` witnesses, SAT check per
orbit): for `k = 2` every assignment whose codes agree at the first witness has
no representative (4 of 16 at `m = 1`, 64 of 256 at `m = 2`), and for `k = 3`
the representatives require all `k` colours at the first witness to be
distinct — 2560 of 4096 assignments have none. A class of `k >= 5` twins
therefore makes the broken formula unsatisfiable outright, and I measured it:
with one witness, the clause set admits **0 of 1024** code assignments at
`k = 5` and **0 of 1,048,576** at `k = 10`. The swept cases have classes of
size 10, 9, 9, so every one of them is unsatisfiable by pigeonhole alone.

Consequence: no case was closed. The correct form of the constraint sorts by a
*non-decreasing* code, and the encoder needs `[-eq]` replaced by a clause that
is vacuous when the prefix is empty. This is the failure mode the handoff warns
about — an over-constrained CNF invalidates every closure it produces — and it
is why a closure built on an added constraint needs the constraint's soundness
certified separately from the DRAT replay.

## 6. Honest status

No family refuted, no case closed, no DRAT certificate produced, `R_4(3)` not
moved. The three closed routes and the `n = 48` calibration object are the parts
that should survive; the rest is bookkeeping. The one apparent full closure this
session produced (§5) is void, and it is recorded here because it is the exact
kind of result this campaign must not bank.

## 7. Round two: first results (swarm `smwr0lr3q`)

One member (m4) has reported; its items are checked here.

* **The interface identity is now kernel-checked.** `.ultramath/smwr0lr3q/m4/lean/Interface.lean`
  proves `interface_sum`, `interface` (the
  `sum_{x outside} m_x = sum_{a in A}(d_c(a) - 1)` double count), the degree cap
  `indep_le_sixteen`/`deg_le_sixteen` and all three arm-saturation bounds
  (`armFar_le_two`, `armFar_eq_empty`, `armFar_le_five`). It builds against the
  repository's development and is axiom-clean, so the two lemmas of §2.2 and
  the identity of §1.2 are no longer hand arguments.
* **A new constraint, and the only one nobody in this campaign had used.** If
  the 42 vertices outside the root's arm carried no edge of colour `f`, they
  would be 3-coloured with no monochromatic triangle and so have at most 16
  vertices; `42 > 16` forces a colour-`f` edge inside the 42, and any such edge
  `{x,y}` gives `M_f(x) cap M_f(y) = empty` by triangle-freeness through the
  arm (for `f = 0`, also `|M_0(x)| + |M_0(y)| <= 15`). Kernel-checked as
  `exists_disjoint_arm_parts` (`Colours.lean`). It is a constraint on the pair
  distribution of §3 and its natural home is the finite system named there.
* **A dead end for the core route.** The 44-vertex arm core `C(15,14,14,0)` is
  satisfiable: `m4/core_C15_14_14_0.col` passes `tools/verify_coloring.py` (44
  vertices, vertex 0 at degrees `(15,14,14,0)`). Together with the concurrent
  session's 43-vertex `C(15,15,12,0)`, no arm core decides a wall profile.
* **The §2.4 block question is settled** and this note was wrong on it; see §2.4
  now.
* **Why the `n = 60` engine does not port (m1).** The published engine's opening
  step fires only when `w(v) > (n-1) - L(v)` with `L(v) = max_i d_i(v)`. At
  `n = 58` the right side is at least 41 while a vertex with at most two
  critical colours has `w <= 32`, so it fails at all seven wall profiles; with
  three critical colours `w = 57 - d_min` and the condition is `d_min < L`,
  which holds. The same criterion reproduces the published `n = 60` split
  (profiles A, B, D, E versus C1, C2), so it is the engine's own applicability
  condition. *(m1's second bullet, that the `31+31 > 60` step becomes
  `|N_a| + |N_b| > 58`, is wrong: the 31 is `w(v)`, so the analogue is
  `w(u) + w(v) > 58`, which holds at the two-critical wall profiles.)*
* **The classification premise: not citable, but portable (m1, corrected here).**
  The K15/K16 template classification — every good 3-colouring of `K_16` is
  weakly isomorphic to U or T, every good `K_15` a deletion — is *not* imported
  from Kalbfleisch–Stanton/Heinrich by the project that proves `R_4(3) <= 60`.
  Its `publication/CLASSIFICATION_PROVENANCE.md` says so in terms: "Published
  accounts provide historical context; their theorem statements or reported
  computations are not imported as axioms", the classical authors being the
  historical origin only. What does establish it there is a kernel-checked
  derivation: `R4333.k16CriticalCatalogue_complete` and
  `R4333.k15CriticalCatalogue_complete`, with no completeness hypothesis, over
  32 modules and 55 CNF/LRAT pairs (5,081,743 bytes of payload), axioms
  `[propext, Classical.choice, Quot.sound]`. So this campaign's
  `K58.Templates.Classified` cannot be discharged by citing the literature; it
  can be discharged by porting those two theorems, and the port turns on a
  definitional match with `K58.EdgeCol`/`TriangleFree`. That is the concrete
  form of what the campaign's notes call its best route to the marking lemma.
* **The one-vertex layer is settled (m2).** The join type of an outside vertex
  into the pinned 15-arm is exactly L1 plus bookkeeping: all 216 profiles occur
  in both templates, and at `m_0 = 0` the three L1 bounds are simultaneously
  tight, so no single-vertex argument can give W2. The only pair consequence at
  that level is `m_0(x) = m_0(y) = 0 => colour(xy) = 0` (a 0-independent 17-set
  otherwise).
* **The per-`(u,y)` rigidity, stated correctly (m8's gap, m2's correction,
  verified here).** For a 0-sender `u` in the 15-arm and `y in N_0(u)`, the
  vector `(|N_f(y) cap N_0(u)|)_{f != 0}` is a permutation of `(5,5,4)` or
  `(5,5,5)` — L3 at `u`, and measured on 41,300 such pairs across five
  artefacts with 0 violations. Without the hypothesis `y in N_0(u)` the values
  2 and 3 occur, which is what m2's counterexamples show; the statement needs
  the colour-0 adjacency, and with it the constraint is available as the
  S-side-to-T-internal coupling that m8's still-feasible model lacked.
