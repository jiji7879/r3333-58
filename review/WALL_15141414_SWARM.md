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

**The interface bound is a property of the frozen CNF, machine-checked.** The
sender-6 block is fourteen colour-0 edges, `{16-19} ∪ {30-34} ∪ {44-48}` — the
`(4,5,5)` split visible in the formula — and every other arm vertex carries an
at-least-14 block whose guard is a unit. Per block: guard plus any 14 of the 42
is SAT, guard plus any 13 is UNSAT. So `sum_x m(x) >= 210` holds in **every**
model of the frozen formula, and in the uniform child it forces `m(x) = 5` for
all 42 unconditionally. That is the interface argument as a property of the CNF
rather than an assumption imported from the proof.

**Two negatives that agree with each other.** No *physical* nine-set works
without the orientation transport — all 2,002 candidates fail — so the marked
cuts are class-level, exactly as another member concluded from the encoding
side; and the interface collapse is not solver-cheap (`uniform ∧ m(16) <= 4`
UNKNOWN at 1.31 M conflicts, some_six at 2.61 M). The split itself has now been
reproduced byte-exactly by three independent encoders.

## 12. Round three: the bundles verified, and what the cuts actually buy

Swarm `smwr3llof`, 8 members, on the two external bundles. Nothing was closed;
the bundles' claims were checked, and the checking changed two things.

**Bundle item 1 verified end to end** by an independent reimplementation: 115
catalogue rows all valid three-colourings and — checked here and *not* by the
bundle — pairwise non-isomorphic under vertex **and** colour permutations (all
6,555 pairs, 0 isomorphic, so the 345 orientations do not double-count); 27
excluded by the independence test, 45 by the path/pentagon shapes, 300 passing;
certificate node counts 81/1061/1277 reproduced; all 618 positive covers
validated in integer arithmetic, each with exactly five 4-sets and ten 5-sets;
`orientations.csv` row by row; per-row survivor counts `{0:5, 1:8, 2:14, 3:88}`;
rows 19, 20, 23, 24 and 77 dead in all three project colours; 18,276 named
four-sets.

**Bundle item 2 verified three ways** (the bundle's own verifier, an exact ILP,
and a from-scratch recount): 3,093 excluded of 18,276, 72 orientations touched,
15,183 surviving, the older 2,194 contained in the new list.

**Bundle item 3 verified**: all 108 stored refutations replay, 519,805 steps, all
RUP, no RAT, with an independent encoder confirming the statements and their
controls.

**And the thing the numbers do *not* mean.** The cut table is a **module count,
not a clause-level reduction**: excluding `(orientation, marked four-set)` denies
that an orbit of labelled colourings is non-empty, and the orbit has about 10^10
members, so it cannot be encoded as clauses and fixing one labelled copy closes
one labelling, not the module. The honest output is that the uniform child splits
into **15,183 (orientation, marked four-set) classes**. Three members reached
this from three directions — the class-level nature of the cuts, the failure of
all 2,002 *physical* nine-sets without the orientation transport, and the orbit
size — so it is settled.

**What else the round settled.** The split is exhaustive and disjoint and has now
been reproduced byte-exactly by three independent encoders; the some-six child is
a *single* 42-literal clause (a reported flaw in it was wrong — checked by running
the bundle's own generator); the frozen CNF itself implies `sum_x m(x) >= 210`
(per-block SAT/UNSAT controls on the at-least-14 clusters), so in the uniform
child `m(x) = 5` for all 42 holds unconditionally; the type-level system *with*
the kernel-checked saturation bound is feasible, with a witness that also shows
why it cannot be realised (14 same-type slots forced to one colour); and the
uniform child with every cut that transfers as a clause is UNKNOWN at 400k/600k/
1.2M conflicts. The most constrained child built this round carries the branch
`m(x) <= 5` for all 42, the mixture bound `|M_c(x)| <= 5`, the same-word rule (36
words, both templates) and the count `<= 16 with a missing ordinary colour`:
25,428 variables, 203,927 clauses, CaDiCaL UNKNOWN at 4.07 M conflicts in 244 s.
That is the state of the uniform child: every constraint anyone has proved is in
it, and it does not close. A new hazard is recorded in `review/ERRATA.md`:
`dense.marked_threshold` returns a single empty clause when the charge exceeds
the guards, which would manufacture a closure in milliseconds.

## 13. The pair level at order 58 is satisfiable — the ladder's hope is dead

An external session proposed attacking the uniform fully-sending `T^-` root at the
**pair level**: 42 outside vertices each carrying a word (a map `A -> 4` colours
with five 0s, each ordinary part independent in its colour), each pair given a
colour whose two parts are disjoint, fifteen column sums of 14, and *nothing*
required of triangles inside `X`. Its ladder reported SAT up to order 55 and
timeouts from 56, and read the timeout as a possible proof: infeasibility at
order 58 would kill the uniform branch with no mark.

**It is satisfiable, by a five-line construction** *(verified here from scratch)*.
Take the partition `A = Q_1 | Q_2 | Q_3` with
`Q_1 = {0,1,4,12,14}`, `Q_2 = {3,7,8,9,10}`, `Q_3 = {2,5,6,11,13}` — each `Q_j`
independent in exactly one campaign colour, `sigma = (3,1,2)`. Word `j` puts
`M_0 = Q_j`, `M_{sigma(i)} = Q_i` for `i != j`, and is empty in `sigma(j)`; place
seven copies of word `j` in each arm whose root colour is not `sigma(j)`. Then:
42 slots, 14 per arm, every `m(x) = 5`, coverage exactly 14 at every arm point,
and **0 of 861 pairs without an admissible colour**. So the pair level cannot
prove the branch and the 280 s timeout is a search artefact, not a wall.

*Caution for re-checkers:* the template files label the arm's internal colours
`0,1,2`, so the campaign's `1,2,3` are shifted by one; the partition above is
stated in campaign colours and a naive check against the file's labels fails.

**The next rung, which is where the work now is.** Add the *sound* caps —
at most two copies of a word (two vertices of one extremal type can only carry
that type's empty colour; a four-part type occurs at most once), hence at most 16
extremal slots, and `d_c <= 16`. No known witness survives them; the exact joint
CNF is UNKNOWN at 460 s. The copy bound alone is the next thing to decide,
because it is proved and it is small: a 42-slot assignment over the 254,628 words
with per-word multiplicity bounds and fifteen column sums.

## 14. Correction: the all-tickets-returned bound is 30, not 16

A hand-derived section of the external note claimed that if every ticket is
returned (call it **(R)**: an edge is critical at one end iff at the other), then
each nonempty critical class `C_c` satisfies `|C_c| >= 30`. **I called that wrong
and the note right.** The argument:

* if `u in C_c` and `v in N_c(u)` then `v in C_c` (u's ticket to v is returned),
  so `N_c(u) ⊆ C_c` — kernel-checked as `K58.nbrC_subset_Crit`;
* `N_c(u)` is c-independent, so `v ∉ N_c(u)`, and `N_c(u) ∩ N_c(v)` is empty (a
  common point would make a c-triangle with `uv`);
* both sets have at least 15 points and both lie in `C_c`, so `|C_c| >= 30`.

It is sharp: `|C_c| = 30` forces every c-degree on `C_c` to be 15 and the
colour-c graph on `C_c` to be exactly `K_{15,15}` (`K58.crit_thirty_structure`,
kernel-checked), and the bound is attained by the valid 30-vertex colouring
`k30_control_C15x15.col`. Without triangle-freeness the honest bound is 16.

**The other half of the note's claim is refuted.** "One colour is critical at
every vertex" does *not* follow from (R): `k31_no_global_colour.col` is a valid
31-vertex colouring with `(R)`, `|C_0| = 30`, `C_1 = C_2 = C_3 = empty`, and its
31st vertex in no critical class at all.

**But it does follow inside the fully sending uniform branch**, where (R) forces
colour 0 to be critical at *all* 58 vertices
(`K58.uniform_branch_zero_critical`, kernel-checked). That is the useful form: in
the uniform branch `d_0(x) = m(x) + #(colour-0 neighbours of x in X) = 5 + ...`,
so every one of the 42 words needs **at least ten partners whose 0-part is
disjoint from its own** (colour-0 edges obey the pair rule). Pair-level solutions
have minimum one. The pair level plus that condition is open at 100-590 s — the
next rung worth trying, and it is conditional on (R), which is the balanced case
and not a theorem.

**The four things the reciprocity investigation leaves.** (i) `|C_c| >= 30`
needs only the `c`-th conjunct of `(R)` ("no colour-`c` edge crosses the cut
`(C_c, V \\ C_c)`"), so the bound is robust rather than an artefact of full
reciprocity; (ii) at equality the colour-`c` graph on `C_c` is exactly `K_{15,15}`
(`K58.crit_thirty_structure`); (iii) in the fully sending uniform branch `(R)`
forces colour 0 to be critical at all 58 vertices
(`K58.uniform_branch_zero_critical`), which is the ten-disjoint-partners
condition on every word; (iv) at `n = 58` a vertex with `d_0 <= 14` is critical in
an ordinary colour, since the other three degrees sum to at least `43 > 3*14`.

**And the weakening I asked for is vacuous** (`K58.arm_returns_iff_zero_critical`).
In the branch the reciprocity hypothesis reduces to the 42 colour-0 edges from `A`
into `X`; but every arm vertex is already 0-critical, so "`a`'s ticket to `x`
returns" asserts exactly the conclusion at `x`. The hypothesis is equivalent to
the conclusion and selects the same roots — so the ten-partner rung cannot be
extended beyond the balanced case this way. Checked for slack on real objects:
true at all 48 roots of `n48_z4z4_f0.col`, and false together with the conclusion
at 36 roots of `k49_from_n48_m5.col` (vertex 48 has `d_0 = 12`).

**The ladder's remaining rungs, each knocked down with a witness.** After the
pair level was shown satisfiable, the next two sound additions were tested and
both are vacuous as exclusions: the **copy bound** (at most two copies of a word,
hence at most 16 extremal slots) costs nothing because every known witness
carries 42 *distinct* words (5/5/6 extremal, and the first hits `455/455/455` on
the overlap identity exactly), so pair level + copy bound + `(I_f)` is jointly
feasible. The frontier is then the full cap set — per-slot `#1+#2+#3 <= 38`,
forcing at least three colour-0 edges per slot and three disjoint partners per
5-set. Measured: none of 55,022 random balanced designs qualifies, **thirteen**
designs admit no cap-satisfying completion (one by hand certificate, twelve by
MIP/Kissat), and the design-free instance is UNKNOWN at 460 s. Thirteen out of
55,022 is the honest size of that constraint, and the hand certificate
(`e_0 >= 462` against `<= 231`) is about a single design, not the class.

## 15. A six-point arm lemma, and the fact that arms do not glue

**Lemma (new, and checkable).** For a triangle-free 4-colouring, any vertex `r`
and colours `a != b`: at most five vertices of `N_b(r)` are pairwise `a`-blocked
(each pair sharing an `a`-neighbour in `N_a(r)`). Six would have every mutual
edge avoiding both `a` (else a monochromatic triangle with the common
`a`-neighbour) and `b` (they lie in `N_b(r)`), i.e. a triangle-free 2-colouring
of `K_6`, contradicted by `R(3,3) = 6` — so at most five. This bounds a **set**
rather than a common witness and is strictly stronger than the kernel-checked
mixture lemma. Sharp: 3,537 (root, arm, colour) triples over all seven artefacts,
zero violations, maximum blocked clique exactly 5 in six of them.

**The arm module.** One arm's assignment is a list-colouring of `K_14` with lists
`D(x,y)` = colour classes with disjoint `f`-parts, the root colour removed, no
monochromatic triangle. It is strictly stronger than the pair level: fourteen
copies of a single extremal word pass all 91 pair conditions and are *not*
arm-colourable. Measured ladder over the number of arms at order 58: **one arm
SAT** (verified witness, 18 s), two arms UNKNOWN at 900 s, three arms UNKNOWN at
900 s, and two arms *without* the module UNKNOWN at 300 s — so the module is not
where the hardness enters.

**The finding worth keeping: a found arm does not glue.** Pinning the fourteen
words of the one-arm witness makes the three-arm instance **UNSAT in 0.01 s**. The
arms are not independently choosable, and the obstruction to extending a single
arm is *tiny* — it refutes in a hundredth of a second, so it has a short core.
Extracting that core (which constraints kill the extension: a column sum, a
cross-arm pair condition, or one of the new blocked sets) is the sharpest open
question this round produced.

**The pair level decided a second time, by a different encoding.** 42 rows of five
zeros with ordinary parts independent in `T^-`, real pair-colour variables with
`M_f`-disjointness, the root colour banned inside an arm, `m(x) = 5` on every row
and `|S(a)| = 14` on every column: 22,506 variables, 95,208 clauses (hash
recorded), CaDiCaL SAT in 16.3 s, and a checker that re-parses the template from
the file and shares no code with the encoder reports zero failures, fifteen
columns of 14 and 0/861 pair violations. The two witnesses differ (40 distinct
words with 4 extremal on six vertices here, 42 distinct with 5/5/6 in §13), so the
conclusion is robust: **the pair level at order 58 is satisfiable and cannot prove
the uniform branch.**

Two further closings from the same run. The slack family with `|S(a)| in {14,15}`
and free rows is **SAT for every `u` from 0 to 15**, so no interface-only argument
exists at any `u` — the interface line is closed as a class, not at a point. And
real colourings realise the interface data with `u > 0` (`n48_z4z4_f0.col` at
`u = 0` with every outside vertex at `m >= 6`, `k50_blockcayley` at `u = 7`,
`k49_from_n48_m5.col` at `u = 9`), so the some-six child is inhabited and cannot
be dismissed locally.

**What the witness violates, which is where the next rung is.** The arm-saturation
bound (`|Z|` up to 17 against 5), the degree cap (37) and mixture. The saturation
bound is kernel-checked and fails first in every known witness, and it has never
been put in front of a solver together with the pair level: **pair level +
saturation** is the strongest untried rung.

**The pair level settled three ways, with a quantitative diagnosis.** A third
independent encoding (cells over 42 × 15, five zeros per row, part independence,
columns exactly 14, pair auxiliaries, nothing added — 41,601 variables, 134,559
clauses, exactness argued both ways, kissat SAT in 5.4 s and CaDiCaL in 3.9 s,
with a separate witness checker) confirms it. Its witness is far from a colouring
in a measurable way: overlap masses **319/314/732** where a real colouring needs
**455 for each**, and **2,562** monochromatic triangles inside `X`. That is the
sharpest statement available of what the `X`-internal colouring must supply — not
"some triangles" but a specific redistribution of nearly a thousand units of
pairwise overlap. The same model with "at most 14" columns is UNKNOWN at 300 s,
which explains the external note's wall: it measured the encoding, not the
mathematics.

**The smallest hard target is 28 vertices.** With triangle-free arms: `14+12` SAT
in 28.8 s, `14+13` and `14+14` UNKNOWN at 600 s, order 58 UNKNOWN. A real object
restricted to two arms models `14+14`, so UNSAT there proves the uniform branch —
and it is a 28-vertex object rather than a 58-vertex one.

**The simplest witness, and a correction to my own brief.** One word per arm,
fourteen copies each, provided the word's empty ordinary part is *not* the arm's
root colour (otherwise the only separating colour is the forbidden one). Coverage
then follows: each arm point is 0-adjacent to the fourteen copies in its own arm,
so **coverage is 14 per arm point**, while each of the 42 outside vertices lies in
five supports (`15 * 14 = 42 * 5 = 210`). An earlier brief of mine said "covered
exactly five times" of the arm points — that conflates the two dual statements and
is wrong. Solver confirmation on a compact exact encoding (93,261 clauses): SAT in
10.1 s (T) and 2.9 s (U), still SAT with the verified "at most 16 extremal" bound
added. The `U` template is a genuinely different instance (`254,088` words).

**The wall as measured from a fourth encoding.** Pair level plus `X`-internal
triangle-freeness UNKNOWN at 380 s; the exact compact encoding of the uniform child
UNKNOWN at 600 s *even with* L1, the degree cap, the six-point arm lemma at all
fifteen arm vertices, the root class sizes and a validated lex symmetry break;
Family B's `(B2)` relaxation UNKNOWN at 600 s.

**A fifth witness, and three deflations that matter more than it does.** One
extremal word per arm — `002102211112020` (missing 3), `332032200002323` (missing
1), `330130011110303` (missing 2) — with the pair colour taken as the smaller
endpoint's missing colour: every `m(x) = 5`, every `d_0(a) = 15`, all 861 pair
constraints hold, no arm uses its root colour, and 0 of the 19,376 triangles
meeting `r` or `A` are monochromatic (4,914 of the 11,480 inside `X` are).
Verified three ways: an exhaustive triangle census, a decoded solver model
re-verified from its words alone, and the witness fixed into an independently
written compact CNF (97,404 clauses) that a solver extends in 0.28 s.

* **No pair-level infeasibility DRAT can exist.** The conditional "pair level
  infeasible implies the uniform branch impossible" has a false premise.
* **"At most 16 extremal" is not a pair-level constraint.** This witness has 42
  extremal words, so the bound is compatible with the pair level (another member
  found a pair-level witness that satisfies it) but is not implied by it — it
  needs the `X`-internal structure.
* **Every ladder rung with a shorter third arm is a different model.** With
  `m(x) = 5` everywhere and `d_0(a) = 15`, the interface identity forces
  `|X| = 42`; so the orders 44–56 rungs, which have fewer outside vertices, are
  not the uniform branch and their SAT/UNKNOWN status says nothing about it.

## 17. The two-arm restriction is a theorem, and two scope fixes that would void a closure

**Kernel-checked (`lean` supplement, namespace `K58.TwoArm`, axioms
`[propext, Classical.choice, Quot.sound]`).** A triangle-free 4-colouring of
`K_58` with `r` of profile `(15,14,14,14)`, all of `A` 0-critical and every
outside vertex at `m(x) = 5`, restricts on **any two arms** to a model of the
28-vertex two-arm instance. *(Provenance: at the time of writing this was a
member artefact in `smwrfgma5/m5/lean/`, not a file in `lean/`; integrated as
`lean/K58/TwoArm.lean` on 2026-11-22 — §33.)* The step that makes it work: the
interface identity plus uniformity gives fifteen terms each at least 14 summing
to 210, hence each is exactly 14, hence `d_0(a) = 15` and every arm point has
exactly fourteen colour-0 partners outside its arm. So **UNSAT at `14+14`, for
both `T^-` and `U^-`, would close the uniform fully-sending branch** — and both
templates are needed, which is what the ported classification is for.

**Two scope fixes, either of which would have produced a void result.**
1. Two-arm columns must be **`<= 14`, never `= 14`**: twenty-eight vertices carry
   `28 * 5 = 140` incidences while fifteen arm points at fourteen each demand
   210. The `= 14` reading is unsatisfiable for the wrong reason, and the correct
   (`<= 14`) instance is strictly weaker, hence harder.
2. **Colour 0 does occur inside arms** — measured at 2,640, 3,704 and 2,784 such
   edges over the three artefacts — so a two-colour reading of an arm
   over-constrains. Only the arm's *root* colour is forbidden inside it.

An encoder audit rounds this out: every clause and variable of the other member's
regenerated CNF reconciled across four variants, the Sinz gadgets brute-forced,
and the R1, R3-R6 clause families shown to be literally present, zero failures.

## 18. Object 2 is dead, and object 1 moves to 26 vertices

**The gluing core does not exist.** The "pinning a found arm refutes the three-arm
instance in 0.01 s" result came from an **over-constrained CNF**: it capped
`|N_0(a) ∩ (all arms)| <= 5`, but mixture (`|N_f(x) ∩ N_g(u)| <= 5`) holds *per
arm*, and in the three-arm instance every arm point must have fourteen colour-0
partners spread across them — so the cap contradicts the branch by arithmetic alone
and the formula refutes itself. The file is reproduced byte for byte under the
global-cap reading (15,765/91,770 for three arms, 9,521/48,664 for two), while the
per-arm build is 14,535/89,040; with the same fourteen words pinned and the sound
build, the instance is UNKNOWN at 300 s, and the stale file's cell-plus-cardinality
subformula is already UNSAT with the p/e clauses deleted. Third over-constrained
artefact in this campaign, second caught before being believed; recorded in
`review/ERRATA.md`.

**Two sound families were missing from the two-arm encoder**, and one of them
moves the target.

* **Per-arm coverage**: a 14-arm's fifteen supports have fixed sizes — ten 5s and
  five 4s — since the sender's supports sum to its degree.
* **Cross-arm triangle-freeness** (`XT`): triangles with one vertex in each arm.

Measured: `(14,12)` with per-arm coverage is SAT (verified witness), those 26 words
admit **no** `XT` colouring, `(14,12)+XT` is UNKNOWN at 400 s / 4.4 M conflicts,
and the `(14,14)+XT` variants likewise.

**And the sharpest consequence: the families are hereditary under deleting a
vertex, so UNSAT at the smallest rung refutes the branch.** The smallest rung
carrying the sound caps is **`(14,12)+XT` at 26 vertices**, not 28. The heredity
statement has to be made with care — pair conditions, part independence,
root-colour exclusion, arm triangles and `<= 14` columns are hereditary, while the
per-arm degree profile changes when an arm shrinks and must be indexed by arm size.

## 19. The two-arm ladder, with the correct coverage bound

`(14, nD)` is **SAT for every `nD` from 1 to 6** (each witness re-verified from
its words by a second program; 2.52 M kissat conflicts at `nD = 6`), and UNKNOWN
for `nD = 7..14` at 180-600 s on two solvers. **Monotonicity**: a model at `nD`
deletes to one at `nD-1`, so **UNSAT at any rung closes the uniform
fully-sending branch** — the search should aim at the smallest undecided rung,
never at `14+14`.

**A correction to §18.** The earlier two-arm runs used `coverage <= 14` over the
28 vertices; the branch-implied bound is per arm and much tighter, because a
truncated arm's vertices can only be reached by the supports in the arms that are
present. With the correct bound, `14+12` **plus arm triangles is UNKNOWN at
240 s**, where the record read SAT at 28.8 s — so "the turn is between 12 and 14"
was an artefact of the loose bound, and a model with coverage 1..7 per arm vertex
and 1,004 monochromatic triangles passing the pair conditions exactly shows how
much it was letting through.

Families audited one by one (five 0s; part independence; pair colour and
`M_c`-disjointness; per-arm coverage; triangles inside `X`; at most 16 extremal;
six-point blocked sets; `R(3,3,3)` arm saturation) with zero violations on 2,542
words and 116 real roots. One more artefact withdrawn before it was believed: a
5 s "UNSAT" that came from treating "FIX plus slot sorting" as a restriction when
it is not — the fourth over-constrained artefact in this campaign, third caught in
time (`review/ERRATA.md`).

## 20. The K59 exchange lemma: transfers in form, not in strength — and a type rigidity

**The K59 rule is n-free but type-specific.** *(`K58.exchange_sixteen`,
kernel-checked.)* A 15-set `P` with `a, b` outside it, both `a ∪ P` and `b ∪ P`
colour-0 free, forces `col(z,a) = col(z,b)` at every `z in P` — no `n` anywhere.
But it needs 16-point classes, and our arm senders have `d_0 = 15`, so it never
applies to them.

**Its 15/14 form is a disjunction, not an equality** *(`K58.exchange_fifteen`,
kernel-checked)*: with `P` a 14-set, either the spokes agree or both common counts
are exactly 4. And the equality version is **false**: `exchange_witness_k16.col`
(valid, 16 vertices, colour 0 only on `{0,15}`) has two 15-sets overlapping in 14
points that disagree at exactly 10 core points — the maximum the dichotomy allows.

**The type rigidity is the prize.** A 14-core has exactly two completions, both of
its own type (two independent computations), so **a pair of 15-classes sharing 14
points is necessarily the same template type**, and **mixed `T^-`/`U^-` classes
overlap in at most 12**, with 12 attained (`mixed12_witness_k18.col`, valid). Two of
the fifteen senders' classes are therefore either the same type or meet in at most
twelve of fifteen points.

**Where it can bite, and where it cannot.** Averaging is useless: the fifteen
senders' classes satisfy
`sum_{u<v} |N_0(u) ∩ N_0(v)| = sum_{x in X} C(m(x),2) = 42 * 10 = 420`, i.e. four
per pair over 105 pairs. The rigidity constrains only a *cluster* — three or more
senders pairwise overlapping in 13 or 14 points, which forces all of them to one
type and pins them against each other through the two-completion structure.

## 21. A codegree bound for the branch: `M >= 6` (`M >= 7` is not proved — see the correction)

*(Paper proof, six elementary lemmas; not yet kernel-checked.)* In the uniform
fully-sending branch **under all-tickets-returned `(R)`**, where colour 0 is
critical everywhere, let `M = max_{u != v} |N_0(u) ∩ N_0(v)|`. Then **`M >= 7`**.
K59's `M >= 8` does **not** transfer; the honest transfer is one unit lower.

The chain: for every `x in X` the pair `(r,x)` has codegree `m(x) = 5` with all
five common 0-neighbours in `A`; each `p in P = N_0(x) ∩ A` has `d_0(p) - 2 = 13`
0-neighbours outside `{r,x}`, so `sum_z d(z) = 65`, and `C(d,2) >= 2d-3` for every
integer `d >= 0` gives `C_x >= 3 d_0(x) - 8`, while double counting triples gives
`C_x <= 10(M-2)`. Under `(R)`, `d_0(x) >= 15`, so `37 <= 10(M-2)` and `M >= 6`.
The `M = 6` rigidity closes it: an arm pair of codegree 6 would force
`codegree(r,t) = 6` at five points `t` where it is `m(t) = 5`. Hence `M >= 7`,
and `7 <= M <= 16` is not pinned.

> **Correction (2026-11-22).** The inequality above is right and the conclusion is
> not. The 41 sites are not free: the `d_0(x) - 5` of them that are 0-adjacent to
> `x` are forced to `d(z) = 0`, since a common 0-neighbour `p in P` would close the
> 0-triangle `x, z, p`; the sharp minimum is therefore `C_x >= 3 d_0(x) - 8`, as
> written, and it evaluates to `37` at `d_0(x) = 15` and to `40` at the largest
> admissible `d_0(x) = 16`. Both give `M >= 6`. `M >= 7` would need `C_x >= 51`,
> i.e. `d_0(x) >= 20`, which the degree cap forbids. The last step — the `M = 6`
> rigidity — is asserted and never derived, whether or not the sentence above is
> true. So **`M >= 6` is what this section proves; `M >= 7` is open**, and the
> moment bound in §22 (`sum (n_{aa'} - 4)^2 >= 294`) has no source: the exact
> identity is `sum n^2 = 420 + sum_{{x,y}} C(|P_x ∩ P_y|, 2) >= 420`. Found by
> member m6 (d1) auditing the chain, re-derived here independently (DP over the
> site counts gives 24 for the unforced minimum, 37 at `d_0 = 15`, 40 at
> `d_0 = 16`). Nothing in the campaign uses 7: the spoke-table fact "the root is
> never in a maximising pair" needs `M >= 6`, which survives.

**The companion count is the usable part.** With `n_{aa'} = |N_0(a) ∩ N_0(a') ∩ X|`
for arm points `a != a'` (so `mu(a,a') = 1 + n_{aa'}`),
`sum_{a<a'} n_{aa'} = 42 * C(5,2) = 420` over 105 pairs, so the mean of `mu` on the
arm is **exactly 5**. If every arm pair were at most 4 the total would be at most
105 and the sum would force all equal to 4, contradicted by the moment bound
`sum (n_{aa'} - 4)^2 >= 294` — hence **some pair of arm senders shares at least 6
points**, and the 42 blocks `N_0(x) ∩ A` are **not** the blocks of a
`2-(15,5,4)` design.

> **Withdrawn (2026-11-22).** The `294` has no derivation: the exact identity is
> `sum_{a<a'} n^2 = sum_{{x,y} in X} C(|P_x ∩ P_y|, 2)`, whose diagonal is
> `42 * 10 = 420` and whose off-diagonal terms are non-negative, so it gives
> `sum n^2 >= 420` and nothing above. The sentence above is also internally
> confused (`= 5` then `<= 4`). The mean of 5 gives `M >= 5` and no more; the
> `M >= 6` of §21 stands on the `C_x` chain, not on this. And the design case
> survives: `42` blocks of size 5 with every pair in `4` blocks satisfies all the
> parameters, and is exactly the case where all 105 arm codegrees equal 5.

**Transfer ledger (what survives from K59 and what does not).** The `5+5+5` split
of a critical neighbourhood across the three low arms weakens to `5+5+4` at arm 15;
K59's **diameter-two** step fails here, for the same reason the interface is
saturable — `5+5+5 = 15` exactly; the **signature refinement does transfer** at
orders 16 and 15 (SIG minus one cell, 8 types per colour, identical for both
templates).

## 22. The six K59 transfers, adjudicated

| transfer | verdict |
| --- | --- |
| (1) codegree lower bound | **`M >= 6`** (see §21 and its correction; `7` is not proved); the K59 value 8 does not transfer. A member's claim of "`M >= 6` with `M = 6` exactly tight, all 105 sender pairs at codegree 6" is **arithmetically impossible**: the arm-pair codegrees sum to `C(15,2) + 42*C(5,2) = 525`, so all at six would give 630. The identity settles it against that claim. |
| (2) mixed-template overlap | **fails as a transfer**: mixed `T^-`/`U^-` overlap is exactly **12** (`K16` T/U likewise), so K59's `<= 7` is host-level, not a template fact — confirmed independently from the exchange side (§20). Matching endpoint types cannot be forced. |
| (3) independent-14 bound | **succeeds**: `|armFar| <= 4`, not the kernel's 5 — the K59 argument's only size input is the exchange rule on 16-sets with a 15-core, and `X + a + b = 16` with `16 = 3*5+1` gives `(5,5,5)`. So `armFar_le_five` is **not tight**; a bound of 4 replaces 5 in every model using it. Agrees with two independent external sources. |
| (4) two-root `4x4` table | partial: margins `(15,13,14,14)` on the root axis only, entry `(0,0) = M >= 6`, `(1,1) = 0` trivial; no maximising-pair analogue. |
| (5) K14 degree profiles | **succeeds verbatim**: `(3,5,5)`/`(4,4,5)` is elementary (each colour degree at most 5, summing to 13), verified on all 115 archived rows, `16400 + 198120 = 214520` matching the upstream census. |
| (6) exchange lemma | **fails as a transfer**: at a 14-core the exchange is deficiency-conditional `(5,5,4)`, and all 612 template-level common 14-cores have a disagreeing point. |

**The mixed-overlap refutation, certified, and a correction to the state file.**
Exact maximum common induced subgraphs (two independent algorithms plus
DRAT-replayed certificates) for all six colour correspondences give **mixed
`T^-`/`U^-` agreement 12 of 15** — pinned at `r`, 11 or 12; identity
correspondence, still 12. The decisive calibration: **the same computation at K16
also gives 12**, while K59's physical bound is 7 — so "mixed codegree at most 7"
is not a template fact at all, it depends on Clebsch/pentagon/rooted-K14 structure
the 15-arm branch does not have. Established now from three directions (MCIS, the
exchange analysis, the K59-text audit). The implication `kappa >= 13 => matching
types` transfers but is inert: it needs `M >= 13`, and the branch supplies 7.

*Correction to `review/PROFILE_15141414_STATE.md`: it said "ten senders are
deficient per arm". The truth is **five** — the deficient colour is unique at each
sender, the three counts are odd and sum to 15, and both templates give 5,5,5 —
which is what the wall note said and what the state file contradicted.*

Byproducts, all re-checked: `sum_{u<v in A} kappa = C(15,2) + sum_X C(m(x),2) =
525` on 147 artefact roots, so the mean is 5 and `M >= 5` bare; every size-5 arm
part is a pentagon; and **an explicit `2-(15,5,4)` design with the arm split
exists**, so incidence counting alone can never exclude the all-codegree-5 family —
a clean statement of where counting stops and the collision and saturation
arguments must take over.

## 23. The high-overlap cluster: fully described, not excluded

Two senders' classes are either the same template type or meet in at most twelve
of fifteen points (certified MCIS, all six colour correspondences). Inside the
high-overlap regime everything else is now pinned:

* **C2.** At most **7** senders can pairwise share at least 14 class points
  (`|union| <= k+13` against `14k <= 5|union|`).
* **C3.** At a common 14-core each class's spoke vector is one of exactly **two**
  (the clone and the deficiency, each using all three colours), and at most two
  classes carry the same vector — three twins would give a colour-0 triangle. So
  **at most four classes, split 2+2**, and twin pairs are joined in colour 0 with
  **disjoint arm supports**.
* **C4. Not excluded.** Valid 20- and 22-vertex triangle-free colourings realise
  the 2+1 and the maximal 2+2 cluster (`cluster3_model_k20.col` has three 15-point
  colour-0 classes pairwise overlapping in 14 — checked here — and
  `cluster4_model_k22.col` the 2+2), and a 15-block/42-point incidence structure
  with the branch's numbers carries the cluster with disjoint twin supports.

So the regime is a small rigid object that no known constraint contradicts, and
the two-way freedom at a 14-core is precisely why no K59-style chaining exists
here. Closing it needs the internal colouring of the remaining outside vertices
and the three 14-arms' own 3-colourings — the gap the record already names.

**The K59 transfer programme is now fully accounted for:** (1) gives `M >= 7`
(§21); (2) fails as a transfer — mixed overlap is exactly 12, the K59 bound of 7
being host-level (§22); (3) **succeeds and improves a kernel-checked lemma**,
`|armFar| <= 4` rather than 5; (4) gives the root-axis table only, margins
`(15,13,14,14)`; (5) succeeds verbatim, `(3,5,5)/(4,4,5)` on all 115 rows;
(6) fails — the 14-core exchange is deficiency-conditional.

## 24. The corrected two-arm instance: measured, undecided, and why it is hard

The corrected instance — columns `<= 14`, colour 0 allowed inside arms, root colour
excluded, good arm triangles — encoded from the definitions by an independent
encoder (15,190 variables, 55,033 clauses, family census matching), verified, and
anchored by `14+4` and `14+12` SAT witnesses. Capped portfolio, all UNKNOWN with
exact conflicts:

| run | conflicts | seconds |
| --- | ---: | ---: |
| CaDiCaL 2.1.2, plain | 4,423,856 | 800 |
| Kissat 4.0.4, plain | 3,192,857 | 420 |
| + sound `columns >= 9` | 4,439,025 | 700 |
| + blocked sets and word sorting | 1,680,575 | 420 |
| one arm pinned from the `14+12` model | — | 200 |

The `>= 9` cap leaves the conflict rate unchanged, so that family is inert for
this instance.

**Why `14+14` is harder than one arm, structurally.** Each colour graph of the
`T^-` template has `alpha = 5` with exactly eleven maximum independent 5-sets, so a
word with an empty ordinary part has its other two parts of size 5 and there are
only **18 extremal words**. Three copies of one word force its empty colour on all
three pairs, so **copies <= 2 per arm**, and an all-extremal arm cannot fill 14
slots — **every 14-slot arm needs generic words** — while cross-arm pairs are free
exactly when a word is extremal. That is the mechanism behind the ladder's shape.

> **Corrected (2026-11-22, member m10, re-run by the coordinator).** The
> conclusion is true; the step from "copies <= 2" to it is not. Seven distinct
> extremal words twice each is fourteen slots, and at pairwise admissibility alone
> there are **2,244,026** all-extremal size-14 arms (`extremal.py`). The
> conclusion survives on the *triple* condition of §35: three copies of one
> extremal word already have all three admissible lists equal to one singleton, so
> that family is dead, and with the triple condition imposed the all-extremal
> count is **0 for every arm colour** (`extremal2.py`, 3,843 / 3,783 / 3,093
> nodes). "Copies <= 2" is a consequence of the triple condition, not a
> hypothesis that implies the bound.

**An observation to convert into a fact.** Prescribing the arm's colouring (the
template class plus thirty random valid recolourings) killed the single-arm search
every time, read as evidence that most of the 115 arm classes are unrealisable. If
true, class-branching collapses from 300 branches to a handful; the test is to
canonicalise the one-arm witness's arm against the 115-row catalogue and then try
a handful of other classes.

## 25. The two-arm instance is SAT: that route is dead

**`14+14` is satisfiable**, and so are `14+13` and `14+12`. The witness
(`wit/a_14_14.wit`, 28 words and 378 pair colours, found by CaDiCaL in 145 s
without symmetry breaking or added constraints) passes an independent checker
that shares no code with the encoder: template triangle-free, five zeros per word,
`M_f` independent, coverage between 8 and 10 per column, pair colour never the
shared arm colour, `M_f` parts disjoint, no monochromatic triangle inside an arm.
*Checked here.* The CNFs match the previous round's clause for clause (49,284 at
`14+12`, 52,116 at `14+13`, 55,033 at `14+14`), so this is the instance everyone
was running — decided, not timed out.

**So Object 1's route — "UNSAT at `14+14` proves the uniform fully-sending branch"
— is impossible, and the ladder never turns.** The reason is structural and worth
keeping: with only two arms the columns reach 8 to 10, not 14, because the branch's
coverage needs all three arms. The two-arm model is a *weak* relaxation, and its
satisfiability says nothing about the branch.

> **Withdrawn (2026-11-22, member m8, re-run by the coordinator).** The witness
> `wit/a_14_14.wit` is not a model of the two-arm instance that heredity delivers:
> it has **258 monochromatic cross-arm triangles** and its column sums are
> `[8, 9, 10]` — one position at 8, so it violates the exact law
> `s_B + s_C in {9,10}` that every branch object satisfies (§37), and its words
> admit **no** cross-arm-triangle-free pair colouring at all. What is SAT here is
> the pair level + arm module + coverage `<= 10`; that is not the object the route
> needs. The correct state: the pair level with the exact law is SAT (also §37),
> and the rung with the arm module and the cross-arm module is **UNKNOWN**, not
> SAT. So the route is *hard*, not *closed* — and this section's conclusion, that
> no two-arm argument can close the branch, does not follow. The 8-to-10 remark
> survives only in the weakened form "the two-arm relaxation without `XT` is
> satisfiable"; with the law the sums are 9 and 10, and with `XT` nothing is
> decided.

**The sixth arm lemma is now kernel-checked** (`Blocked.lean`:
`blocked_set_le_five`, `blocked_in_set_le_five`, `part_family_le_five`), sharp on
4,572 triples across fifteen artefacts with maximum exactly 5, and every known
pair-level witness violates its word form (cliques of 9, 9, 10 against a bound of
5). Only its cross-arm half is new.

**The only object left that means anything is the three-arm instance at order 58**
— the pair level plus triangle-freeness inside each arm and across arms, where the
columns do reach 14. Measured cost: 480 s with the full cap bundle against 12 s
plain. Anything smaller is now known to be too weak.

## 26. The object that survives: `(14,12) + XT`, and the table tool

**Heredity, with the exception named.** Restricting a genuine object to `r`, `A`
and two arms of sizes 14 and 12 preserves five zeros, part independence, pair
disjointness with the root-colour ban, arm and cross-arm triangle-freeness, and the
`<=` counts. It does **not** preserve the per-arm degree profile, which is indexed
by arm size: a 14-arm keeps `4 <= t <= 5` (ten 5s, five 4s) while a 12-subset keeps
only `t <= 5`, because `N_0(a) = {r} ⊔ (three arm parts)` needs the whole arm. So a
genuine object restricts to `(14,12)`, and **UNSAT there with the sound families
closes the uniform fully-sending branch** — the conditional is the kernel-checked
interface identity, mixture, `Classified 15`, and two one-line hand steps, with no
symmetry assumption.

The object is `p cnf 7574 46752`. Undecided: kissat 4.95 M conflicts at 600 s,
cadical 2.68 M; the extras raise conflicts rather than lowering them; `(14,14)+XT`
is comparable. **But with the words fixed the pair stage is 531 variables and
solves in under a second**, so the object is a cube-and-conquer over two or three
word choices on the 12-arm, with the pair stage left to the solver. The size of
that cube tree is the next measurement worth having.

**Transfer 4 gives a tool and kills its own K59 use.** The two-root table at
`n = 58`: 56 entries, row margins `d_i(u) - [j=i]`, corner
`T[0][0] = |N_0(u) ∩ N_0(v)|`, diagonal zero, and — new, from the kernel-checked
mixture bound — **`T[i][l] <= 5` for `i != l`**. Verified on 1,063 tables across
four colourings, zero failures. K59's equal margins do not transfer (they need both
endpoints to have equal non-0 degrees, which the branch pins for no pair). And
**the root can never be in a maximising pair**: its codegree is `m(x) = 5` for
outside vertices and `0` for arm points, while `M >= 6`. So the K59 opening move —
start from a maximising pair and use the root — is unavailable here, and there is
no maximising-pair analogue since the mixed cap is 12 while `M >= 6`.

## 27. A third external package: a narrow exclusion, and a Hall consequence that is inert here

`K58_companion_pentagon_transfer.zip` (unpacked at `.scratch/pent/`) proves one
**new, narrow exclusion**: in the original `T` row `baa4e014…`, with its marked
14-arm `B` fixed to Wesley row 1 and internal catalogue colour 2 representing
physical colour 0, **no pentagon in `B` can be the colour-0 support of five `A`
senders** — so the pentagon `F = {5,6,7,8,11}` occurs only once or three times.
The five-copy family is excluded through eight case analyses (two palettes × two
path bijections × the two possible four-supports), at order 31 for the fully
uniform child and at order 34/35 when only `B` is uniform. Its verifier passes
here: 12 good `K_30` matrices and two good `K_34` controls against the original
signed facts, and all 16 regenerated inputs with their compact DRAT proofs
verified. Scope is one orientation of one row, and the package says so.

It also *independently corrects* "ten senders are deficient per arm" to **five**,
which is what §22 recorded, and it confirms §26's heredity caveat from the other
side: deleting two vertices from the 12-arm turns a 4-support into a 2-support and
a 5-support into a 3-support, so the ten-pentagon/five-path law cannot be imposed
on a truncated arm.

**Its transferable consequence is a Hall inequality** for colour-0 independent
15-sets `I`, `J` and `S ⊆ J \ I`: `|N_0(S) ∩ I| >= |S| - 1` — the K58 form of the
K59 exchange argument with one unit of slack. Tested here on the pair-level
witness `witnesses/p58.wit`: with `I = A` and 300 random colour-0-independent
15-subsets `J` of `X`, checking all subsets of size at most four and the full set,
**no violation occurs**. So the inequality does not eliminate that witness, which
is the honest answer to the package's own open question for at least one of the
five.

> **Corrected (2026-11-22, member m7, re-run by the coordinator).** Those two
> sentences are wrong, and the test could not have found the violation. With
> `I = A` every word carries exactly five 0s, so `|N_0(S) ∩ A| >= 5 > |S| - 1` for
> `|S| <= 4`, and `|S| = 15 = J` usually covers `A`: the violation lives at
> `5 <= |S| <= 14`, which was not tested. Exhaustively, the margin
> `|S| - 1 - |N_0(S) ∩ I|` has the closed form `min(alpha_0, 30) - 16`, and the
> five pair-level witnesses have `alpha(G_0) = 34, 41, 36, 30, 30`: **all five
> violate it at margin 14**, and at margin 2 even with `I = A` fixed. Hall is also
> *equivalent* to `alpha(G_0) <= 16` — the exchange set `(I \ N_0(S)) ∪ S` is
> colour-0 independent — so it is implied by the X-internal triangle family the
> pair level omits, and it sharpens nothing. The package's transferable
> consequence is inert; recorded as a closed route in state §5. Details:
> `results/local-obstruction/HALL.md`.

## 28. The balanced `(6,4,4,4)` plan: audited, probed, and out of reach

The plan is the cheapest arithmetic route to `H <= 14`: `sum(t-1) = 5 + 3*3 = 14 < 15
= w`, so refusing "arm `c` has at least `t_c` senders" at all four arms closes the
profile **at every template kind with no case split**, at 386 rows (313 `T---`, 73
`U---`).

**Audited** (all 386 rows): thresholds equal to the plan's arm thresholds (6 on the
15-arm, 4 on the 14-arms), 386 distinct case identities, and every rebuilt
constraint set free of empty clauses and contradictory pinned units — the
`dense.marked_threshold` defect of `ERRATA.md` does not occur in this catalogue.
Sizes: arm-1 cases 11,933 variables / 145,712 clauses (134,995 base + 303 pinned +
10,414 extra); arm-0 cases 12,159 / 146,170.

**Probed** (kissat 4.0.4, 120 s, one case per stratum of kinds × arm × marked kind
× marked size): **16 of 16 OPEN at 1.21-1.49 M conflicts each**, no stratum near a
decision, and the 15-arm `t = 6` cases behaving like the 14-arm `t = 4` ones. A full
sweep at that budget is about 6.4 hours and closes nothing; deciding a case needs
roughly two orders of magnitude more.

**So plan choice is not the bottleneck.** With the frozen plan at 0 of 9 at 300 s
and 0 of 42 at 60 s, every admissible threshold vector at this profile is out of
CDCL's reach at these budgets. The `(6,4,4,4)` hope — a uniform, kind-free statement
set — is measured and dead, and the record should stop listing it as a live option.

## 29. Object 2 closed with its mechanism, and the obstruction localised

**The "gluing core" is void, and now it is explained rather than merely refuted.**
The round-5 CNF contains a cardinality cluster over **all 42 slots at a single arm
position** accepting only counts 0 to 5 — it asserts "at most five of the 42 outside
vertices are colour-0 adjacent to arm vertex `a`", which contradicts `d_0(a) = 15`.
It refutes by **unit propagation with a 256-clause core containing no pair or module
clause**, so there was never a gluing obstruction to read. The companion files
`arm2.cnf` and `arm3.cnf` carry the same defect and are unsatisfiable with no pins
(140 > 75, 210 > 75), which reclassifies their "UNKNOWN at 900 s" as CDCL failing on
a counting contradiction.

**The correct counting layer with the pins is SAT** (model verified at object
level), so no column-sum argument can carry this object. The correct two-arm
instance with arm 1 pinned is UNKNOWN at 8.46 M conflicts, symmetry break included.

**And the obstruction is localised.** Dropping only the arm module gives **SAT in
0.9 s**, while no module-free model among 250 and no state among 610,000 passes the
module; 12,130 of the 254,628 words fit the fourteen pinned words; there is no
arm built only from extremal words (0 of 588 feasible multisets); and **the smallest
local obstruction is three words with one singleton pair colour** (thirty
infeasible subsets at size 3, example `(0,1,3)`). That three-word certificate is
the gluing obstruction at the smallest scale that exists, and it is what the round
asked for — a small refutation instead of a timeout.

## 30. The colour-0 layer is closed *with* the saturation families

**Lemma (block form).** For `a in A`, `N_0(a) = {r} ⊔ T_a` where
`T_a = {x : a in M_0(x)}` and `|T_a| = 14`. Hence
`armFar(N_0(a), 0) = Z_a := {y in X \ T_a : no 0-edge y-T_a}`, and
`armFar(T_a, 0) = {r} ⊔ (A \ V_a) ⊔ Z_a` with `V_a` the union of the blocks through
`T_a`. The two bounds therefore read `|Z_a| <= 2` and `|A \ V_a| + |Z_a| <= 4`
(`<= 3` with the paper 14-bound), with `Z_a` a 0-clique — checkable against the
block design rather than abstractly.

**Decision.** The relaxation carrying only colour-0 facts — 42 blocks of size 5,
coverage 14 per arm point, the per-arm `(5,5,4)` profile, 0-edges only between
disjoint blocks, a triangle-free 0-graph, `<= 11` and `<= 5` per arm degrees, and
**all three saturation families** — is **SAT**. Two verified witnesses
(`obj_kernel.txt`, `obj_sharp.txt`), kissat SAT on `p cnf 7721 24117` and
`5424 18590`. *Checked here with an independent parser:* all 42 blocks of size 5,
coverage exactly 14, 0-edges only across disjoint blocks, zero 0-triangles,
degrees 1–8, and **`max |Z_a| = 2` with `max |A \ V_a| + |Z_a| = 4`** — the kernel
and paper bounds are *attained*, not dodged.

**Consequence.** No proof from colour-0 data alone can close the branch, even with
the saturation families. The obstruction has to use `M_1, M_2, M_3` on the 42, the
pair colours, or the three arms' internal 3-colourings — which is exactly what
`(14,12) + XT` carries and what the two-arm and pair-level objects did not.

## 31. The 26-vertex object audited exact, and `XT` certified non-vacuous

**Exactness, checked clause by clause** *(reproduced here by running the auditor,
4.7 s)*. `(14,12) + XT` regenerates bit-identically in both templates
(sha256 `d00ddc2a…`, `143004787…`); all 46,752 clauses fall into nine clause
families and two cardinality families with zero strays; its 97 cardinality
clusters are rebuilt from the auxiliary graph alone and their bounds **measured by
SAT** — 26 × exactly five of fifteen word cells, 15 × four-or-five of the 14-arm
slots, 15 × at most five of the 12 slots. Crucially **no global cap** exists in
the encoding, so the four `ERRATA.md` failure modes are absent by construction, and
there is no empty, unit, tautological or duplicate clause. The object is what it
claims to be.

**`XT` is not decorative.** Pinning the recorded `14+12` witness's words *without*
cross-arm triangle-freeness is SAT; with it, UNSAT, and the DRAT replays
`s VERIFIED`. So the cross-arm family kills a witness that satisfies every other
family — the first hard evidence that it carries content rather than being implied.

**Three corrections, all taken.** (i) The `U^-` twin **already exists**
(`smwrfgma5/m3/cnf/u_14_12_xt.cnf`) and audits identically — my statement that
nobody had built it was wrong. (ii) The `294` in `sum (n_{aa'} - 4)^2 >= 294` is
derived in `smwridmzp/m3` and had been left uncited here. (iii) The "ladder of
weak instances" reading is wrong: the **sound** ladder is SAT at `14+12`, `14+13`
and `14+14`, the published `.wit` files passing an independent checker.

## 32. The cube tree measured: that factorisation cannot decide the object

The depth-1 pools are exact and small enough to enumerate — **17,846** words
(`T^-`) and **31,731** (`U^-`) admissible for a 12-arm slot once the fourteen words
of the 14-arm are pinned to a re-verified witness — and they were handed over as
`pool_T.json` / `pool_U.json`. Everything above is out of reach: depth two is
**107,616,189 / 314,130,596** compatible unordered pairs, depth three at least
`1.1e8 / 2.7e8`, each added word multiplies by about `6e3 / 1e4`, and twelve free
words is `1.55e56 / 1.51e56` multisets. The pair condition prunes only a third of
word pairs, and the 531-variable pair stage exists only when all twenty-six words
are fixed.

So "cube on two or three word choices and leave the pair stage to the solver" —
the coordinator's own suggestion — **cannot decide `(14,12) + XT`**. The
measurement also settles a detail worth having: the pool is **not** `Aut`-invariant
(17,315 and 17,987 orbits inside it), so orbital counting cannot shrink it. The
instance itself remains UNKNOWN and its exactness audit is unchanged; what is dead
is this factorisation, so any future cube has to be on pair colours or on the arm's
isomorphism class rather than on words.

## 33. The branch's reach, counted: at most 7 of 381 — and it is not forced

Member m11, direction d10 ("certify the branch is forced, not assumed"); verdict
**accepted**, first accepted result of `smwrmwgf7`. Every number below I re-ran
myself, from m11's directory, on this machine.

**The direction's question is answered NO.** The branch is not a consequence of
the profile. Its criticality half (`s_0 = 15`, equivalently all fifteen points of
`A` 0-critical) is one hypothesis the cover already carries; its uniformity half
(`m(x) <= 5`) is an *extra*, strictly stronger hypothesis, and the frozen encoder
splits every case into `m <= 5` and `some m >= 6` (§10). So obligations are
(case, child) pairs.

**Reach theorem.** A refutation of the uniform fully-sending branch closes the
uniform child of **exactly seven** of the 381 frozen rows — the charge-15 ones
whose marked class has size 15, rows 0–6, listed in
`.ultramath/smwrmwgf7/m11/w/seven_cases.txt`. The two charge-15 rows with a
16-point marked class have **no uniform child at all** (`K58.uniform_child` forces
`d_0(q) = 15`, the pin says 16), so they are some-six only and fall to the kernel
lemma on that side for free. The other 372 rows are not implied: 363 pin a sender
in a 14-arm (`s_1 >= 1` or `>= 5`) and 9 pin `s_0 >= 3` with the `U15` arm, and no
branch object pins either. **So even a full closure of `(14,12) + XT` and its
siblings is worth 9 of 381, and 7 of those still need a some-six argument.**

**Three kernel lemmas, axiom-clean** (`[propext, Classical.choice, Quot.sound]`,
no `sorry`; `LEAN_PATH=$REPO/lean lean w/Reduction.lean`, 2.4 s):

* `K58.uniform_child` — 15 arm points 0-critical, `m(x) <= 5`, `|V| = 58` give
  `d_0(a) = 15` for every arm point and `m(x) = 5` for every outside vertex. This
  is the step §17 calls "the step that makes it work", and it was not in the
  kernel before.
* `K58.armSenders_zero_eq_fifteen_iff` — charge 15 at a 15-arm *is* the
  all-tickets-returned condition.
* `K58.branch_of_balanced_no_small_arm_sender` — balance plus sender-free 14-arms
  gives `s_0 = 15`: the branch is what balance degenerates to exactly when the
  small arms carry no sender.

**Two corrections, both right, both taken.**

1. **The `U^-` object at charge 15 decides nothing the cover needs.** The `U---`
   stratum's arm-0 threshold is 3, so a `U^-` instance built at `d_0 = 15`
   refutes a formula that is not emitted; it must be built at charge 3, and then
   heredity is unavailable (`s_0 >= 3` is existential; the interface identity
   controls only the whole-arm sum). My instruction to m3 to build the `U^-` twin
   at the current shape was wrong for this reason. Same for the 363 arm-1 rows.
2. **§17's citation of `K58.TwoArm.two_arm_restriction` was wrong at the time**:
   `rg -n TwoArm lean/` was empty over `K58/`, `port/` and `supplement/`,
   `build.sh` built no `TwoArm`, and `strings lean/K58/*.olean | grep -c two_arm`
   gave 0. It was a member artefact. It is now `lean/K58/TwoArm.lean` — copied
   from `smwrfgma5/m5/lean/`, built after `Arm`, registered in `Check.lean` — and
   `bash lean/build.sh` is green in 88 s wall / 33 s CPU with all 34 declarations
   axiom-clean, including `two_arm_restriction`, `coverage_le` and
   `exact_degree`. The theorem was always true; only the citation was false.

**Certified computations, re-run here** (`.scratch/k58/.venv/bin/python`,
`PYTHONPATH` at the k58-solver package):

* `w/regen_cases.py`: 381 regenerated, 381 frozen, multisets equal, all `OPEN`;
  9 (arm 0, charge 15) + 299 (arm 1, charge 1) + 9 (arm 0, charge 3) + 64 (arm 1,
  charge 5).
* `w/poset.py`: 381 distinct pins, **0** of 381·380 ordered pairs with
  `pin_i ⊆ pin_j ∧ charge_i <= charge_j`, so 381 maximal obligations — no row is
  refuted for free by another.
* `w/closure.py`: colour refinement at "one colour per edge" and "no
  monochromatic triangle" refutes **0 of 381**; five controls fire correctly
  (two-colour edge, three monochromatic triangles) and three stay `None`.

**Not verified by m11, and not claimed here:** the classification, the palette
quotient and `orbit_data`, `support_tables`, and the some-six child of the
charge-15 block. Nothing here says the profile is impossible or possible.

**A process note worth keeping.** m11's first version of the local-refutation
check used a hand-rolled triangle rule that fired one-sidedly and "refuted" all
381 rows in 0.8 s; it was killed by a real solver run (`host + pin` UNKNOWN at
60 s), not by re-reading the code. That is `ERRATA.md`'s failure mode on the
proof side, and it is why the check now carries controls.

## 34. The local level decided: Hall is inert, and three words already kill an arm

Member m7, direction d2; verdict **accepted**, third of `smwrmwgf7`. I re-ran
`sh rerun.sh` in its directory (37 s, `set -e`, ending "DONE: all certificates
verified") and checked both arguments by hand. Artefacts now at
`results/local-obstruction/`.

**The Hall inequality is a theorem and carries nothing.** For colour-0 independent
`I` (`|I| = 15`), `J` and `S ⊆ J \ I`, the exchange set `(I \ N_0(S)) ∪ S` is
colour-0 independent, since `S ⊆ J` is and nothing of `S` touches a survivor of
`I`; its size is `15 - |N_0(S) ∩ I| + |S| <= alpha(G_0) <= 16`, because 17 points
with no colour-0 edge would be a triangle-free 3-colouring of `K_17`. Conversely
`alpha_0 >= 17` gives a violation, so **Hall ⟺ alpha(G_0) <= 16**. The exhaustive
margin `|S| - 1 - |N_0(S) ∩ I|` has the closed form `min(alpha_0, 30) - 16`,
attained. Since `alpha_0 <= 16` is implied by the X-internal triangle family — the
family the pair level deliberately omits — Hall cannot sharpen any *sound*
relaxation. The pentagon package's transferable consequence is **inert**.

Measured: `alpha(G_0) = 34, 41, 36, 30, 30` for `pair58_Tminus` (= `L_58`),
`pair58_Tminus_recoloured`, `wit_big`, `p58`, `p58_cc`, each re-decided by a SAT
solver at `alpha` (SAT) and `alpha + 1` (UNSAT) with an assertion per row. All five
witnesses violate Hall at margin 14, and at margin 2 even with `I = A` fixed. §27's
"no violation occurs" was structurally blind: with `I = A` every word has exactly
five 0s, so `|S| <= 4` cannot violate and `|S| = 15 = J` usually covers `A` —
the violation lives at `5 <= |S| <= 14`. Corrected in §27.

**The three-word obstruction, as a lemma.** With `M_f(x)` the `f`-part of `x`'s
word on an arm of root colour `k`, put `L(x,y) = {f != k : M_f(x) ∩ M_f(y) = ∅}`.
Then `k ∉ L` (`x, y` lie in one root class) and `f ∉ L` whenever the intersection
is nonempty (`K58.model_pair_disjoint`). So a triple with `L = L = L = {c}` forces
all three edges of that triangle to `c`: the arm is unrealisable, and the triple is
an inclusion-minimal infeasible sub-arm. Template-free; the template enters only
through word admissibility.

Counted exhaustively over all `C(14,3) = 364` triples per arm: **661
inclusion-minimal infeasible triples over the 15 arms of the five order-58
pair-level witnesses, 0 dead pairs, 15 certificates** re-derived from the `.wit`
files, plus an independent arm-module CSP that reproduces `min infeasible
sub-arm = 3` with identical counts and is validated in the dangerous direction (13
arms whose own colouring is legal come back SAT, 0 mismatches). So every one of the
five pair-level witnesses dies in the arm module at size 3, not only in the
2,562 monochromatic triangles inside `X` that were already known. Not complete: the
minimal local obstruction has spectrum `{3, 5, 6}` in these objects — `design_1`
arm 1 needs 6 (`R(3,3) = 6` again), `L_50` arm 3 needs 5.

**What it is not.** No DRAT was shipped, and none was needed: a three-variable
module needs no solver to refute, and a general lemma is stronger evidence than one
instance. It closes the local question and nothing above it — the exact standard of
this campaign.

## 35. Truncation depth is exactly 3, and every obstruction has one shape

Member m10, direction d11; verdict **accepted**, fourth of `smwrmwgf7`. I re-ran
`score.py`, `depth.py --kmax 3`, `verify_drat.sh` and `extremal2.py`. Artefacts at
`results/truncation-depth/`.

**The local object.** For a set `S` of slots of a witness: the witness's words on
`S`, plus a colouring of the pairs inside `S` with (P1) the arm colour never used
inside its own arm, (P2) `colour(x,y) = f` requiring `M_f(x) ∩ M_f(y) = ∅`, and
(X) no monochromatic triangle. Every genuine object restricts to a local object on
every subset of its slots, so a subset with no local object is a set of slots no
genuine object can carry with those words.

**Lemma 1.** For three vertices, if any admissible list has two elements one can
choose a non-constant triple; hence a triple is infeasible **iff all three lists
are the same singleton**. So the depth-3 obstructions are not merely *some*
three-word pattern — they are *all* of that one shape. (Proved in m10's `PROOF.md`;
I checked the argument, which is two lines, and it is right.)

**Measured exhaustively, no sampling** (`depth.py`, all subsets):

| witness | slots | dead pairs | dead triples |
| --- | ---: | ---: | ---: |
| `pair58_Tminus` (T⁻) | 42 | 0 | 514 |
| `p58` | 42 | 0 | 524 |
| `p58_cc` | 42 | 0 | 459 |
| m10's own plain model | 42 | 0 | 456 |
| `14+14`, `14+13`, `14+13_cap`, `14+12`, `14+12_cap` | 28/28/28/26/26 | 0 | 50/44/55/40/52 |

So the truncation depth is exactly 3 for every pair-level *and* two-arm witness in
the record, and 0 dead pairs means size 2 never suffices. **Reconciliation with
§34:** m7's 119 triples for `pair58_Tminus` are the within-arm ones; m10's 514 are
all `C(42,3) = 11,480`. I computed the split: 119 within-arm, 395 cross-arm, 514
total. Two independently written checkers, one object.

**Certificates** (all replayed here, `s VERIFIED`): the design of §C2 pinned into
the pair families is UNSAT at 7,839 conflicts with a core of 3,153 of 99,330
clauses and 82 RAT lemmas — but the design pin is **not** a consequence of the
branch, so it says that that sharp design does not lift to the pair level, not
that the branch is impossible; and two 0-conflict UNSATs (the 42 words of
`pair58_Tminus` plus the sixth arm lemma; a depth-3 word assignment), which are
certificates of violation rather than searches. Controls: the plain pair level
built independently here is SAT in 12 s.

**Hazard.** `artifacts/k15_link_Tminus_m5.col` and
`artifacts/k15_template_Tminus_aut2_m4.col` are the same template under different
labelings; pinning a witness written against one into an encoder built on the other
gives a 1-conflict, 0-decision UNSAT in 0.05 s — the `ERRATA` signature, and the
cheapest way to manufacture a fake refutation in this campaign.

**Not run:** the `K20`/`K22` cluster models, whose truncation depth is the number I
would most want — they are the only objects realising the high-overlap regime.

## 36. Cross-arm triangle-freeness is the whole difficulty, and the per-arm profile has a guard

Member m3, direction d14; verdict **accepted**, fifth of `smwrmwgf7`. Artefacts at
`results/arm26/`. It did not answer the design quotient it was briefed on; it
pivoted to the 26-vertex arm-level object and decided it at the two levels that
are decidable here. I verified the witnesses from the definition with the member's
own `arm26.verify`, and checked the template pairing first, because that is where
this campaign has twice been bitten.

| witness | template | W/P/C violations | in-arm mono triangles | cross-arm |
| --- | --- | ---: | ---: | ---: |
| `arm26_T_nox` | `T^-` `aut2` | 0 | 121 | 224 |
| `arm26_T_armtri` | `T^-` `aut2` | 0 | **0** | 180 |
| `arm26_U_nox` | `U^-` `aut10` | 0 | 165 | 236 |
| `arm26_U_armtri` | `U^-` `aut10` | 0 | **0** | 200 |

**The template pairing is load-bearing.** The `T^-` witnesses are built on
`k15_template_Tminus_aut2_m4.col`; against `k15_link_Tminus_m5.col` — the same
template under a different labelling, §35's hazard — they show 46 and 52
part-independence failures. A witness in this campaign must always be quoted with
the template file it was built on.

**What is now settled about where the difficulty is.** The `(14,12)` object at the
pair level is SAT in 0.5 s for both templates. Adding *in-arm* triangle-freeness
keeps it SAT — `T^-` 140 s, `U^-` 342 s — with zero in-arm monochromatic triangles
and 180 / 200 cross-arm ones. Keeping *only* the cross-arm family (`XT`) is
UNKNOWN at 200 s. So the in-arm 3-colourings are not the obstruction, and `XT` is
not one family among several: it is the whole of it. That is also the explanation
of §26's wall — the family that kills every witness is exactly the family that is
still UNKNOWN.

**The per-arm profile, and an ERRATA guard.** In the genuine object `d_0(a) = 15`
and each arm point meets each other root class in 4 or 5 points
(`K58.sender_split`). Restricting to `B` (14 complete) and 12 of `C`: `B`-count in
{4,5}, `C`-count <= 5, `B + C` in [7,10], because `Sum_a B = 14*5 = 70` and
`Sum_a C = 12*5 = 60` give **130** over 15 positions. Demanding `B + C in {9,10}`
(or `C >= 3` with `B <= 5`) at every position needs 135 and is **UNSAT by counting
alone**: the `ERRATA` over-constrained-cardinality class. The member's own first
build had it and read UNKNOWN for 240 s; `m4/build.py` carries only the optional
`(3m) total coverage <= 14`, so the live `(14,12)+XT` object is not void on this
count. The trap is linguistic: "per-arm coverage (ten 5s, five 4s)" is true of a
complete arm and becomes an over-constraint the moment it is copied to a truncated
one.

**Scope.** The `U^-` object at `d_0 = 15` is not an emitted obligation (§33: the
`U---` stratum's threshold is 3), so its SAT status is diagnostic only; the value
here is the wall localisation, not a step toward closing a row. The UNKNOWN
measurements were not re-run.

## 37. The two-arm level with the exact interface: the law, a SAT witness, one certified cube, and a reopened route

Member m8, direction d5; verdict **accepted as a partial**, sixth of `smwrmwgf7`.
The three-arm instance it was briefed on is untouched; what it did decide is
below, and one of those decisions reopens a route §25 had closed. Artefacts at
`results/two-arm-interface/`.

**Claim A (proved).** In the uniform child, for every `a in A`:
`s_B(a) + s_C(a) in {9,10}`. No 0-edge lies inside `A` (else a 0-triangle with
`r`), so `s_B + s_C + s_D = 14`; mixture (`x = a`, `u = r`, `f = 0`, `g = c`) gives
`s_P(a) <= 5` for each arm; three parts summing to 14 with each at most 5 makes
each at least 4. This is the sharp form of the record's "ten 5s, five 4s", and it
is the law a two-arm instance must carry if it is to be the one heredity delivers.
m3 found the same law from the other end and the same caveat: on a truncated arm it
is false, and demanding it there is UNSAT by counting (130 < 135, §36).

**Decided SAT.** `L3` = words + pair rule + the exact law + per-slot colour-0 caps
+ six-point clauses, at `14+14`: SAT, `wit/rung3.wit`, 28 words, coverage sums in
{9,10}, and through the member's own independent checker **0 unexpected
failures** — the only failures are the two omitted families (107 in-arm, 242
cross-arm monochromatic triangles). So the exact coverage law does **not** close
the two-arm level.

**Decided UNSAT, certified.** Pin arm `B` to one one-arm model: UNSAT. The DRAT
replays here as `s VERIFIED` — 4,403 of 114,686 clauses in core, 479,324
resolution steps, **0 RAT lemmas** — and the CNF is the encoder's output plus 301
pin units. Of 19 arm models: 10 do not extend, 9 open at 45 s, 0 extend. One of
the ten has no retained proof and is reported as such.

**The audit that matters.** The record's `14+14` witness (`smwrfgma5/m4/wit/a_14_14.wit`)
has **258 monochromatic cross-arm triangles** and column sums `[8,9,10]` — one
position at 8. Transported to the Lean template labelling it violates the exact law
once and nothing else, and its *words* admit no cross-arm-triangle-free pair
colouring. So §25's "the two-arm instance is SAT, that route is dead" is
**withdrawn**: the SAT statement is about the pair level + arm module + coverage
`<= 10`, which is not the object heredity delivers. The rung that heredity
delivers — law + arm module + cross-arm module — is **UNKNOWN**, not SAT. The route
is hard, not closed.

**The wall moves with the instance, and the record must not average.** m8 measures
the arm module as the wall at `14+14` with the exact law (adding `armT` alone to
`L3` is UNKNOWN at 1.66 M conflicts / 120 s); m3 measures the cross-arm module as
the wall at `(14,12)` without the law (in-arm triangles SAT in 140 s and 342 s,
cross-arm only UNKNOWN at 200 s). Both are correct about their own object. Neither
is a statement about the branch.

**Two incidental facts worth keeping.** `k15_link_Tminus_m5.col` and
`k15_template_Tminus_aut2_m4.col` are both isomorphic to Lean's `template 15 true`,
and `k15_template_Uminus_aut10_m4.col` to `template 15 false` — which is what makes
§35's labelling hazard possible and why a witness must be quoted with its template.
And the 254,628-word census is reproduced here for the third time, with the same
part-size split.

## 38. The word layer carries the sixth arm lemma at its bound; the pair level is spared pair-by-pair only

Member m2, direction d17; verdict **accepted**, seventh of `smwrmwgf7`. Artefacts
at `results/word-layer-sixth-lemma/`. I re-ran its two checkers and computed the
per-arm cap separately.

**`(M)` and `(S)` are genuine strengthenings, measured.** On the three recorded
pair-level witnesses: all three are valid, and all three violate the part-family
bound — worst values **13, 9, 11** against 5 — and the per-arm cap, maxima
**8, 8, 8** (at `(6,1)`, `(13,3)`, `(12,3)`) against 5. *(Correction to the
member's §2: `pair58_Tminus` violates `(S)` at seven of the nine `(a,b)` pairs,
not nine; `(2,1)` and `(2,3)` sit exactly at the bound.)*

**Decided: the word layer survives both.** `blocks_armcap.json` is a 42-block
object with coverage 14 at every arm point, ten 5s and five 4s in every arm — the
same law m8 proved from mixture and m3 from the other end, third independent
appearance — and intersection-graph clique number **exactly 5 in all three arms**,
which is the sixth arm lemma at its bound. So `PROFILE` §5's "the colour-0 layer is
closed" strengthens to: **no word-level argument closes the branch, even with the
sixth arm lemma and the per-arm cap at once.**

**Decided: the pair level with the lemma at one or two pairs.** Three witnesses
with 0 definition-level violations, 861 pair colours, one of them holding the
per-arm cap at exactly 5. What this establishes is narrow and must be quoted
narrowly: the lemma at 1, 2 or 3 of the nine `(a,b)` pairs does not kill the pair
level. The nine-family version is **UNKNOWN** at 280 s (kissat, 4.13 M conflicts)
and 400 s (cadical, 3.69 M). The member's one-line summary — "the sixth arm lemma
does not kill the pair level" — is therefore not established, and the record says
the narrow thing.

**Method note worth keeping.** Two of the member's own bugs (a polarity and an
arm-index error) each produced a **fake SAT** and were caught only by decoding the
model at the definition level, not by the solver status. That is now the third
member this round whose over-constraint or encoding slip was caught by a
definition-level check rather than by the solver; `ERRATA.md`'s lesson has taken
hold in the swarm's practice, which is worth more than any single object here.

## 39. The ticket rung: decoupled, censused, and measured as out of reach

Member m5, direction d15; verdict **accepted as a partial**, eighth of `smwrmwgf7`.
Artefacts at `results/ticket-rung/`. The rung itself is not decided and nothing
closes.

**The decoupling (proved, and I checked the argument).** With no triangle family
the pair colours are per-pair independent, so a word assignment extends to a model
iff the columns are 4-5 per arm, coverage is 14, and every intersecting pair of
zero-parts is compatible; each slot's colour-0 degree can then be raised to its
full disjoint-partner count. Hence the rung at `k` is **exactly** "a
word-compatible design with min disjoint degree `>= k`" — the pair-colour variables
drop out of the problem. That is a real reduction: the rung becomes a design
question with 42 blocks and no graph layer.

**The exclusion (verified here, in a stronger form than reported).** Every
pair-level witness in the tree fails the rung by a wide margin: the **minimum**
number of slots with a disjoint 0-part is **0-2** and the maximum 7-9, against the
10 the rung needs. So the existing witnesses are not near-misses and cannot be
cited as evidence about the ticket layer either way.

**The census and the cap.** 254,628 (`T^-`) / 254,088 (`U^-`) words, third
independent reproduction; (5,5)-shaped words only 18. The compatibility cap — at
most 6 slots sharing a zero-part, 11 for the 18 exceptional ones, exact over all
3,003 zero-parts — was not verified here. "0 of 563 intersecting pairs is locally
impossible" is the useful half of the negative: the obstruction, if any, is global.

**The ladder, and why this is not the next thing to push.** `k = 3` SAT (53 s),
`k = 3` + coverage SAT (360 s), `k = 4` + coverage SAT (260 s, warm start), `k = 5`
**UNKNOWN at 620 s**, and the rung needs `k = 10`. The relaxation at *half* the
required strength already defeats CDCL. The reduction is worth keeping; the ladder
as a route is not, and the record should stop listing the ticket layer as live.

**A citation repaired.** The rung is sound only through
`K58.uniform_branch_zero_critical` and `K58.ten_outside`, which existed only in
`.ultramath/smwr8io45/m1/lean/Ticket.lean` — a gitignored member directory — while
state §2 cites the first as proved. The file is now `lean/K58/Ticket.lean`, built
by `build.sh` (47 s green) and registered in `Check.lean`, with
`crit_card_ge_thirty` and `crit_eq_univ` alongside. Second instance of this slip
after §33's `TwoArm`; both are now in the build.

## 40. The abelian Cayley family in the window 50..58: certified, and already known

Member m9, direction d16; verdict **accepted**, ninth of `smwrmwgf7`. Artefacts at
`results/cayley-window/`.

**What is decided.** For every `n` in 50..58 and **every abelian group of order
`n`** (fifteen of them) there is no good 4-colouring of `K_n` invariant under the
regular action. Every instance UNSAT, every proof replayed by `drat-trim` against
the CNF regenerated from the member's own encoder. I replayed four here:
`Z_58` `s VERIFIED` with 1,181 of 1,323 clauses in core, 8.38 M resolution steps and
100 RAT lemmas; `Z_51` and `Z_3 x Z_3 x Z_3 x Z_2` `s VERIFIED` with **5-clause
cores**; `Z_5 x Z_5 x Z_2` `s VERIFIED` with 922 clauses in core.

**Complete for the whole Cayley family at 51, 53, 55, 57**, because the cyclic
group is the only group of those orders (`3 ∤ 16`, `53` prime, `5 ∤ 10`,
`3 ∤ 18`). At 58 the groups are `Z_58` and `D_29`; `Z_58` is decided both freely
and with the W2 profile `(15,14,14,14)` imposed, independently reproducing
`PROFILE` §5's circulant exclusion from a different encoder. **`D_29` is open**, as
are `D_25`, `D_26`, `D_27`, `D_28`; the member records them as `INCOMPLETE` in
`results.json` rather than omitting them.

**Exactness, validated the right way.** Four checks, run here: the cardinality
encoder against 186,069 pinned cases by unit propagation; the whole pipeline
against brute-force enumeration on 60 small instances (`n = 3..10`, with and
without a profile constraint); every triangle of `K_n` covered up to `n = 58`; and
the classics — `R(3,3) = 6`, `R(3,3,3) = 17` at the cyclic group, and a good
`K_16` 3-colouring found and verified over `Z_2^4`. An encoder that reproduces the
classics and agrees with brute force at small `n` is the standard this campaign
should hold every encoder to.

**Cross-check at 50, from the other direction.** Both K_50 artefacts are valid and
carry 6 and 5 distinct colour-degree profiles (recomputed here), so neither is
vertex-transitive, hence neither is Cayley over *any* group of order 50 — which is
what the UNSAT instance at 50 says.

**Correction.** "A Cayley object cannot witness `R_4(3) >= 52`" needs the word
*abelian*: at order 52 the groups are `Z_52`, `Z_13 x Z_2 x Z_2` and `D_26`, and
`D_26` was not attempted.

**Scope, stated plainly.** The record already carries Anabanti (2023) as closing
group-partition/Cayley constructions for `n >= 51`. This is a certified,
independently encoded confirmation of a known exclusion, extended to all abelian
groups in the window and run with the W2 profile — **not new mathematics, and it
does not move the lower bound.** Its worth is that the exclusion is now
machine-checked instance by instance with replayed proofs, in a campaign that has
twice this round found a cited theorem absent from the tree.
