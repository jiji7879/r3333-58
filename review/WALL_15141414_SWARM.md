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

### 2.4 The extremal 6-blocks — and a correction (m5, corrected here)
In the extremal configuration (`t = 0`, all `m_0 = 5`) the types with an empty
part come in exactly **6** configurations per (empty part, ordered colour pair)
in both templates. They do **not** form a `2-(15,5,2)` design: 6 blocks is
impossible for any `lambda` (`b = 105 lambda/10`), the point degrees are 1, 2
and 3 (five points each), and the pair multiplicities are 1 for 40 pairs and 2
for 10. For `T^-`, empty part 0, `g = 1`, `h = 2` the blocks are
`(0,6,7,10,11) (1,5,6,9,10) (2,3,7,11,14) (2,3,8,12,13) (2,5,6,11,13) (4,5,8,9,13)`.
m5's §12.4 infeasibility for the natural extremal schemes must be recomputed
from these lists, not from a uniformity assumption.

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

## 5. Honest status

No family refuted, no case closed, no DRAT certificate produced, `R_4(3)` not
moved. The three closed routes and the `n = 48` calibration object are the parts
that should survive; the rest is bookkeeping.
