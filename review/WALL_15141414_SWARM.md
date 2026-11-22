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

## 8. Accepted: the classification premise is proved (round two, m1)

`K58.Classified 15` and `K58.Classified 16` — "every triangle-free 3-colouring
of `K_n` (`n = 15, 16`) is isomorphic to one of the two templates, up to
relabelling the vertices and the colours" — were **stated and not proved** in
`lean/K58/Templates.lean`, and the whole `n = 58` cover rests on them. They are
now proved, in `lean/port/`, from the pinned `R_4(3) <= 60` development's own
kernel-checked theorems. Build and axioms:

```
bash lean/port/build_port.sh      # 53-54 s, Lean 4.32.1 + the pinned Mathlib
'K58.classified_16' depends on axioms: [propext, Classical.choice, Quot.sound]
'K58.classified_15' depends on axioms: [propext, Classical.choice, Quot.sound]
```

No `sorry`, no `native_decide`, no new axiom. The bridge was checked by hand as
well as by the compiler: `K58.IsoUpToColour` and the upstream `WeakColorEquiv`
are the same relation (a vertex bijection together with a global colour
bijection), `R4333.ThreeColorCatalogueComplete` is the same completeness
statement, both upstream endpoints are unconditional, and the four catalogue
identifications are kernel `decide`s over the edge pairs.

Caveats that travel with it: it is proved under **4.32.1** against the pinned
Mathlib, not under the repository's 4.33.1, so it lives beside `lean/build.sh`
rather than inside it (rebuilding the upstream modules at 4.33.1 is measured at
three patches plus a failure at `CatalogueBaseCNFSemantics`, 26 modules
untried); and `Classified` is used nowhere yet — the marking lemma remains the
critical path. What changes is that the campaign no longer rests on an
unproved premise.
* **The type-level route is closed, and the reason locates the gap (m4).** The
  system on 42 slots — (T) f-part independence, (V) coverage 14 per arm vertex,
  (P) every pair admits a colour with disjoint parts (arm colour excluded inside
  an arm), (Q) every colour occurs on an edge of the 42, (N) non-sending — is
  **feasible** in both templates, with a hand-checkable witness: 14 slots of
  type `(A; empty, empty, empty)` in arm 1 and 14 of `(empty; 5,5,5)` in each of
  arms 2 and 3. So no accounting argument at the type level proves Family A.
  The witness is degenerate and dies as soon as the arms themselves are required
  to be good 3-colourings: in arm 1 every slot has `M_0 = A`, so a colour-0 edge
  there needs `A cap A = empty`, and colour 1 is the arm colour, leaving only
  two colours for the internal edges of a 14-vertex arm — `R(3,3) = 6 <= 14`
  forces a monochromatic triangle. **What a proof must use is the internal
  colouring of the three 14-arms.**
  *Correction (external handoff, 2026-11-22, confirmed here).* That witness is
  not admissible once the kernel-checked saturation bound is included: it has 28
  slots with `M_0 = empty` (14 in arm 2, 14 in arm 3), and `armFar_le_two`
  allows at most **two** vertices outside a 15-set with no colour-0 edge into it.
  So the feasible-witness claim is true only for the relaxation that omits that
  bound, and **the type-level route is not closed**: whether the system with the
  full checked constraint set (the zero bound, the arm-internal caps, the
  per-(`u,y`) rigidity with its hypothesis) is feasible is **open**. The
  "what a proof must use" conclusion survives — the witness dies under (R)
  either way — but the feasibility verdict above does not. Note that the now-proved K15/K16
  classification does not help there: a 14-vertex arm lies outside it.
* **The 16-armed wall profiles force an outside vertex with six (m4, kernel-checked).**
  `K58.forced_six` and `K58.forced_six_two` (`.ultramath/smwr0lr3q/m4/lean/Sixteen.lean`,
  axioms `[propext, Classical.choice, Quot.sound]`): if a colour-0 class of a
  vertex of a triangle-free 4-colouring of `K_58` has 16 points and all of them
  are 0-critical, then one — and in fact two — vertices outside the class have
  at least six colour-0 neighbours in it. The arithmetic is the interface
  identity: `sum_X m_x >= 16*14 = 224` against `5*41 = 205` and
  `16 + 5*40 = 216`. **Profile-level, this is the sharp statement about why
  `(15,14,14,14)` is the boundary case**: `14p <= 5(57-p)` holds iff `p <= 15`,
  so five-per-outside-vertex is exactly saturable at arm size 15 and never at
  16. It applies to the five 16-armed wall profiles (3,472 open cases) and not
  to this one. It is a lower bound with slack: the two vertices it produces are
  unconstrained against each other (`6+6 <= 16` if they are 0-adjacent), so
  unless something bounds `m_x` from above it is inert. **That is now settled:
  inert.** The range at a fully critical 16-arm is `224 <= sum_X m_x <= 240`
  (each arm point sends 14 or 15), the only upper bounds available are 240 from
  the cap and `205 + 11k` with `k >= 2` forced, i.e. 227 or more, and both sit
  above 224; so a contradiction would need `sum_X m_x <= 223`, i.e. a proof that
  17 units of interface are unavailable — a structural fact about the colour-0
  graph on the 42 that the interface language cannot express. The top of the
  range is attained: in `artifacts/k32_module_2x16_m1.col` every vertex's 16-arm
  is fully critical with all 15 outside vertices at `m_x = 16`, sum 240. And
  "at least two" is guaranteed but attained nowhere: the only saturated 16-arms
  in the record are those K32 ones.

## 9. The position after two rounds

What changed since §1–§3 were written, in the order it matters:

1. **The classification premise is no longer a premise.** `K58.Classified 15`
   and `K58.Classified 16` are kernel-checked in `lean/port/` (built from the
   pinned `R_4(3) <= 60` development, 53 s, axioms
   `[propext, Classical.choice, Quot.sound]`). Nothing in the `n = 58` cover
   rests on an unproved structural assumption any more. `Classified` is still
   *used nowhere*: the marking lemma is the critical path and is unstarted.
2. **The interface language is exhausted in both directions.** At arm size 15
   the export count is `210 + u`, `u <= 15`, and five-per-outside-vertex is
   exactly saturable; at 16 it lies in `[224, 240]` with the top attained
   (`k32_module_2x16_m1.col`), so the forced-six theorem is inert. The boundary
   fact: `14p <= 5(57 - p)` holds iff `p <= 15` — the three 15-armed wall
   profiles are exactly those where the interface has no slack, and
   `(15,14,14,14)` is the one of them with the smallest budget (`w = 15`).
3. **The gap is located, and the type-level route is *not* closed** (corrected
   §7). The witness that made the type-level system feasible has 28 vertices
   with `m_0 = 0`, which the kernel-checked saturation bound forbids (at most
   two); the witness also dies when the three 14-arms must be good 3-colourings.
   So **a proof must use the internal colouring of the 14-arms** — the
   classification does not reach a 14-vertex arm — and whether the system with
   the full checked constraint set is feasible is open.
4. **The model's hypothesis list is kernel-checked** and integrated:
   `lean/K58/Arm.lean`, `Link14.lean`, `Model.lean` (pair disjointness for any
   colour, the per-`(u,y)` rigidity in its correctly paired form with the `= 5`
   case at a 16-arm, the parity invariant, the evenness step, the interface
   identity), registered in `Check.lean`, build green in 42 s.
   `e_i = 35` per colour class of a 15-arm is now unconditional (a corollary of
   the classification, with an independent parity-plus-enumeration check).
5. **Unchanged:** W2 is open, no case of the 381 is closed, no bound has moved,
   and the frozen machine route is dead at every budget tried.

The shortest description of the wall that anyone has produced: every quantity
the ticket argument can see is slack enough to be attained by a real object two
vertices away, and what remains is the interaction of three 14-vertex
3-colourings, each of which is far less rigid than the templates the campaign
has just finished classifying.

## 10. An external handoff bundle (2026-11-22), checked here

Another session read this repository at `89a632c8` and produced
`R3333_project_handoff_and_first_case.zip` (unpacked at `.scratch/handoff/`,
a cache). It contains: our ledger and the 381-row worklist; `first_case/` with
the frozen CNF for `baa4e014…`, its generators, the marked-support sieve and two
pilot children; three certificate bundles under `wall/`; and eleven historical
notes. What follows has been checked here; the rest is its own claim.

**Agreement with this repository (checked).**
* `first_case/original.cnf.gz` is our frozen case **byte for byte**:
  `sha256 71edaaa0b9c0c1556291f569b5dd8d5d09443240ea28f932e04666b0d4d1d338`,
  12,114 variables, 146,098 clauses = 134,995 base + 309 pinned + 10,794 extra,
  with recipe `tables, total_critical, full_root off`. Rebuilt here from the
  ledger row; clause sets equal.
* Both split children rebuild to the exact hashes in its `pilot.json`:
  `8e0b49a9…` (uniform, every `m(x) <= 5`) and `f5324082…` (some-six,
  first vertex in the physical order with `m(x) >= 6`, predecessors `<= 5`).
  So the two pipelines agree at the byte level and a closure from either side
  can be banked on the other.
* Its marked-cut verifier reproduces: 2,194 excluded named four-sets of 18,276
  across 300 surviving orientations, exclusions in 57 orientations; the worked
  example (catalogue row 1, colour 2) gives 40 of 54 four-sets excluded with two
  nine-set witnesses.
* `arm_data/orientations.csv`: 345 orientations, 27 excluded by the
  independent-support equality, 45 by the path/pentagon shapes, 300 surviving.
* The path/pentagon premise is a property of the templates and holds: in both
  `K_15` templates a vertex's `b`-neighbourhood inside the template has 4 points
  inducing `P_4` in each other colour, or 5 inducing `C_5`; in both `K_16`
  templates always 5 inducing `C_5`. *(Checked here by brute force on the four
  template files.)*

**What it corrects in this record.** §7/§9's "the type-level route is closed"
is wrong: the feasible witness has 28 slots with `M_0 = empty` and the
kernel-checked saturation bound allows two. That route is open.

**What it contributes, if its certificates hold.** (i) A 14-arm support
restriction: 45 of 345 orientations admit no fivefold cover by fifteen
admissible supports, so some `x in B` has `m(x) <= 4` and hence some `y` has
`m(y) >= 6` — a six-forcing at the 15-arm boundary, which the interface
argument cannot produce. (ii) The nine-set cuts on marked placements. (iii) An
extremal/word bound: at most 16 extremal vertices in `K_58`, and the uniform
branch needs at least 26 distinct all-four-colour words, with DRAT proofs behind
the 18-extremal and 17-vertex statements.

**A scope fact that limits it.** No `U---` row has charge 15 (the 73 split as 9
with `arm 0, charge 3` and 64 with `arm 1, charge 5`), so all three items —
which assume fifteen fully critical senders or `baa4e014`'s marked four-set —
have no hypothesis among Family B's rows and cannot be ported there.

## 11. The second external bundle, and the type-level question settled

**A stronger marked-path test (verified here).** The companion bundle
`K58_uniform_marked_path_certificates.zip` (unpacked at
`.scratch/handoff/new_marked/`) replaces the nine-point cap by a size-sensitive
inequality. In a uniform 14-arm there are seventy colour-0 incidences and every
support has four or five points, so the fifteen supports are exactly **ten
pentagons and five four-vertex paths** (`5*10 + 4*5 = 70`). With `P` the marked
path and `a_4(H)`/`a_5(H)` the largest intersection of `H` with an allowed path
/ pentagon, every uniform realisation satisfies

    |P cap H| + 4 a_4(H) + 10 a_5(H)  >=  5 |H| ,

so a violated instance excludes that marked placement. I ran both of the
bundle's verifiers: `python3 -S verify.py` certifies 3,093 distinct witnesses
and `python3 verify.py --recount` re-scans every subset of every passing
orientation and confirms the list is **exhaustive for this inequality**. The
counts: 18,276 named marked paths in 300 orientations, 2,194 excluded by the
older nine-point test, **899 additional** by this one, 3,093 in 72
orientations, 15,183 passing. A worked two-point obstruction: catalogue row 1,
`P = {1,5,8,9}`, `H = B \ {0,8}` needs 60 hits and can get at most 59.

**Two further items in the report.** (i) A claimed bound of **4** (not 5) for
the number of outside vertices with no `c`-edge into a 14-point *colour class*,
sharp on local examples — our kernel-checked `armFar_le_five` gives 5 for an
arbitrary 14-set with no `c`-edge inside, so if the stronger form holds it is a
genuine strengthening that the type-level model could use. (ii) A
repeated-overlap lemma: in the reciprocal branch the fifteen supports give ten
pentagons per arm and at most nine colour-0-free pentagons can pairwise
intersect in at most three points, so two senders' supports overlap in four or
five positions; at overlap four the common four induce complementary paths and
the joining edge is forced to colour 0.

**And the type-level question the first bundle reopened is settled — feasible.**
The first bundle correctly showed round two's witness invalid (28 slots with
`M_0 = empty` against the kernel-checked bound of two). A member then produced a
valid one: 42 slots, **every** `m(x) = 5`, coverage exactly 14 per arm point
(`sum = 210`, the `t = 0` case), zero empty `M_0` slots, `(P)` and `(Q)`
satisfied, in both templates. So the type-level route stays closed for the
reason round two gave — and the witness says why more sharply than before: its
largest repeated type occurs 14 times and its slots are pairwise forced to a
single colour, so three of them would form a monochromatic triangle. That is the
obstruction in one line: the type level is feasible, and the colouring of the 42
is not.

**Item 3 of the first bundle, audited here.** All 108 stored refutations (92 for
the 17-vertex theorem, 10 local 18/19 statements, 6 pair bounds) replay against
CNFs regenerated from the bundle's encoders: 519,805 steps, 338,587 lemmas, all
RUP, no RAT, empty clause RUP, `verified=108 failed=0`. The check ignores
deletions and verifies every step as RUP — sound because RUP is monotone in the
clause set, and **stronger** than `drat-trim`, which checks only the backward
core from the empty clause (a strict all-deletions reading fails on all 108).
An independent encoder confirms the same statements with controls: coverage at
17 and at 18 UNSAT, 19 excluded, 17 SAT unblocked, no failing anchors, in both
templates; and it reproduces the word count (18 words, six per missing colour),
the 1-(15,5,2) design, the five anchor zero-hits and the 48-vertex calibration.

**One step of item 3 is vacuous and one is real.** "The uniform branch requires
at least 26 distinct all-four-colour words" is no constraint: about 254,610 (T)
and 254,070 (U) such words exist, so 26 distinct ones are available many times
over. What the verified argument actually gives is a **count**: at most 16 of
the 42 vertices can have a missing ordinary colour — equivalently at least 26
carry all four parts non-empty. That is the statement to carry forward.

**The uniform child is pinned, and one correlation identity is exact.** In the
uniform child (`m(x) <= 5` for all 42) the case forces `d_0(a) >= 15` for the
fifteen arm vertices, and the kernel interface identity then closes both bounds
at once: `d_0(a) = 15` for every `a in A` **and** `m(x) = 5` every outside
vertex. Nothing at the interface is slack. Consequences: each `N_0(a)` is a
classified template with 35 edges per ordinary colour, one deficit arm per
sender, five deficient senders per arm, coverage exactly five per arm vertex.

A new identity decomposes the pairwise overlap of the colour-0 parts by
*colour*: for each colour `f`,

    sum over colour-f pairs {y,z} of X of |M_0(y) cap M_0(z)|
      = sum_{a in A} e_f(N_0(a))  -  sum_{z in N_f(r) cap X} m_0(z)

*(checked here independently: 1,758 identities across `n48_z4z4_f0.col`,
`k49_from_n48_m5.col`, `k50_z4z4_m6.col`, zero failures).* In the uniform child
it evaluates to `15*35 - 14*5 = 455` for each ordinary colour, `1365` in all —
which also equals `15 * C(14,2)`, so the total is forced by the coverage and the
colour split is the new content. It gives `>= 91` colour-`f` pairs with
overlapping colour-0 parts — **and no more than that.** The total 1365 is
`sum_a C(14,2)` once every arm vertex is covered fourteen times, i.e. forced by
coverage alone for any label multiset, and the 455-per-colour split is forced by
the templates (`15*35 - 14*5`, every ordinary colour alike). So the identity is
a **check** — a candidate assignment must reproduce 455/455/455 — and not a
constraint; the design structure cannot cap the overlap below it. Recorded so
that nobody re-derives it hoping for a contradiction.

**A claimed flaw in the split is itself wrong (checked).** A member reported
that the bundle's some-six child forces `m(x) >= 6` for all 42 vertices. It does
not: running the bundle's own `start.py` reproduces both child hashes
(`8e0b49a9…` at-most-five, `f5324082…` some-six) and the some-six CNF contains
exactly one clause built from all 42 flags — "at least one `m(x) >= 6`". The
children are disjoint and exhaustive; the pilots are a valid split.

**A structured family excluded by DRAT (existence side).** There is no
`Z_58`-circulant triangle-free 4-colouring of `K_58`: the instance is exact for
the family (116 variables = 29 difference classes × 4 colours, one colour per
class, one clause per triangle and colour over all 30,856 triangles), CaDiCaL
refutes it in 16.5 s and `drat-trim` returns `s VERIFIED` (14 s, 1177 of 123,627
clauses in the core, 0 RAT lemmas). *Checked here.* This is existence-side work:
it removes a family of candidate colourings and does not advance the cover.
`2 × Z_29` and `3 × Z_19 + 1` were UNKNOWN at 400 s and 540 s; the latter is the
shape of the known good `K_50` and the only structured family at this order
where a positive answer is plausible.

**The bundle's orientation table reproduced independently, and one clause-family
scope question closed.** A member recomputed the 14-arm orientation table with
its own parser, a tighter family and an exact ILP: 300 of 345 surviving,
agreement 345/345, 18,276 four-sets, 2,194 excluded in 57 orientations. It also
closed the shape-scope question — the part `S_b = N_b(r) cap T` lies inside the
sender's own classified class `T = N_b(x)`, so the P₄/C₅ shapes are template
properties; 248 instances over 4 templates × 4 sender colours × every vertex,
both other palette colours, zero violations, and restricting the shapes to
template parts adds no clause. It withdrew a build of its own whose auxiliary
polarity made the child look closed at 400k conflicts — the same
over-constraint failure mode as §5 — and the child, rebuilt to the pilot hash
with the marked cuts transferred as sound clauses plus five other families
(212,730 clauses), is UNKNOWN at 400k/600k/1.2M.
