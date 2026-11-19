# K54 handoff: pilot verified, local-15 obstruction analysed, cuts certified

Session of 2026-11-18. Archive unpacked to `work/k54/` (152.1 MiB, 4,170 entries,
`sha256sum -c SHA256SUMS` clean on all 4,169 listed files). All work below is
reproducible from that directory; helper scripts are in `work/k54/ours/`.

## 1. Pilot verification (passed)

`sh tools/build_native.sh` builds CaDiCaL 3.0.1, Kissat 4.0.4 and drat-trim from the
vendored sources. `python3 tools/verify_pilot.py` then passes for all three boards:

```
live-07 count models, shared-crossing models, pair and full proofs verified
live-14 count models, shared-crossing models, pair and full proofs verified
local-15 count models, shared-crossing models, pair and full proofs verified
```

`checkpoints/counted/replay.sh` also passes: the live-17 arithmetic tree (29 nodes,
15 integer-checked leaves), both K34 controls, the three feasible histograms, the
fractional packing, and both native DRAT proofs.

## 2. The local-15 pair refutation is a three-vertex core

`drat-trim pilot/lifts/local-15-two.cnf.gz <trace> -c core.cnf` returns 67 of 63,668
clauses (2 lemmas, 89 resolution steps). The core mentions only right-side H42 vertices
14, 16, 18, 20, 24, 25, 26 and outsiders 37, 40, 49. Rebuilding just those three
pins from scratch gives a 4,608-variable, 73,186-clause instance that is UNSAT in
0.1 s with a 64-clause core, replayed `s VERIFIED`.

## 3. Two certified cuts

A cut is a clause over the outer unary count variables. `ours/verify_cut.py` rebuilds the
reduced instance from the cut description alone, checks that each rectangle has a unique
left column whose signature equals the pinned one (so `count(r,1,sigma) >= 1` forces a
vertex of exactly the pinned type), runs CaDiCaL, replays the DRAT, and emits the clause.

| cut | pinned rectangles (left support, right support) | marginals | clause | reduced CNF sha256 |
| --- | --- | --- | --- | --- |
| C1 | (3256,2128) (7416,2048) (11448,80), left sig 0, right sig 32 | 354, 323, 70 | -1670 -1482 -451 | `34b54d13abae0422190e0b638d1cdd1610fcceb72dfe30e5e47fcd3bc9a8d72e` |
| C2 | (51,393) (5875,128) (8507,8), left sig 0, right sig 8 | 187, 84, 14 | -1064 -543 -117 | `e50458a639d2c3ef03f229450271da0699be8e204ce8842fdbcffb9940289717` |

Each says: not all three of those marginal counts can be positive. Both proofs replay.

## 4. What the obstruction actually is

The 64-clause core is a two-outsider argument, not a three-outsider one. Write
`w` for an outsider, `H` for the H42 template on the right side. The core uses only

* `e(26,w)=0` and `e(16,w)=1` (the signature class with anchors `(0,12)`, `(1,2)`),
* `e(27,w) != 3`, which is the rectangle condition when 27 is outside the rectangle,

and the template colours `H(16,27)=1`, `H(18,26)=0`, `H(16,18)=1`, `H(18,27)=2`,
`H(26,27)=0`. Then for each such `w`:

* `e(27,w) != 3` (rectangle), `!= 0` (via 26), `!= 1` (via 16) so `e(27,w) = 2`;
* `e(18,w) != 0` (via 26), `!= 1` (via 16), `!= 2` (via 27) so `e(18,w) = 3`.

Two such outsiders `u,v` then have `e(u,v)` forbidden in colour 0 (via 26), 1 (via 16),
2 (via 27) and 3 (via 18). So **two outsiders of that cell type cannot coexist**; the
capacity of that signature class is 1, not the 5 that the two-anchor Ramsey bound gives.
The same reading was found independently by the swarm member working the structural
direction, with a 25-clause, 624-variable sub-CNF proof.

## 5. Why the marginal cut loop does not close the board by itself

The cut loop (`ours/run_cegar.py`) derives, for each count vector, the lift core, the
pinned types, a reduced UNSAT instance and the induced marginal clause. It produced C1
and C2 and then stalled: every later core either names several positions of one rectangle
that the lift's matching never realises together (so the induced clause is vacuous), or
names a cell whose marginal capacity the outer model already enforces.

That is structural, not an implementation accident. The outer model's unary chain for a
column is `min(26, min class capacity)`, and the class capacities are exactly the
two-anchor Ramsey bounds; the capacity-1 facts of section 4 come out at the same value.
So the marginal count model is closed under this cut family: it already knows the local
capacity of every signature class, and what it cannot see is the interaction between
outsiders (the mutual edges), which is exactly what the lift adds. Reproducing that with
marginal cuts needs pair-level information, not more single-column cuts.

## 6. Exhaustive alternative, running

Because the abstraction is closed under local cuts, the clean complete route for a board
is the case split: enumerate every count vector of the outer CNF and refute each lift.
The census is large but finite; `ours/exhaust.py` enumerates one vector per SAT call and
refutes each lift with a recorded DRAT proof (mean cost 0.43 s per vector, including
0.35 s of Python for the lift, 0.04 s to write the DIMACS and 0.04 s of CaDiCaL; every
lift so far is UNSAT within 20,000 conflicts).

Status at the time of writing: more than 23,600 count vectors enumerated and still
running, no vector yet whose lift is SAT. A completed pass gives a **board exclusion**
for local-15 (every graph induces one of the enumerated count vectors, and every one of
them is refuted), reported as an exhaustive case split rather than a single refutation.

## 7. What is not claimed

* No board is closed yet, and no seed. The 12 top-level seeds are untouched.
* C1 and C2 are certified but they do not close local-15; they are fixed-vector
  generalisations whose residual model is still large.
* The two-outsider lemma of section 4 is verified as a clause-core fact for the specific
  boards; its exact scope (which rectangles, which signature classes) is stated only for
  the instances that were replayed.

## 8. Update: certified cuts on live-07 and live-14

The bounds-conditioned lift generator (`liftb.py`, swarm member m5) produced one cut per open
board. Each is a clause over the outer unary variables; each certificate is the board graph plus
one-side witness pins on distinct outsiders, with everything else free. I rebuilt all three
independently (`work/k54/ours/check_oneside.py`, different code, no shared machinery) and got
byte-identical CNFs and replayed proofs:

| board | cut | witnesses | CNF sha256 | vars / clauses | core |
| --- | --- | --- | --- | ---: | ---: |
| local-15 | `-u[70,1] -u[323,1] -u[354,1]` | 1,1,1 | `945c876c6937dda9e9464237203ea4e18e0518f1414df25a8858ed958b3e8cd8` | 4608 / 73165 | 64 |
| live-07 | `-u[52,2] -u[83,1]` | 2,1 | `7f42587394364b52aaf82fa744da749c2551d656d7b9f700c64e10fbcbff5c38` | 4600 / 73004 | 80 |
| live-14 | `-u[1,1] -u[8,2]` | 1,2 | `921d3d1f97927a8b3fc5d5f50cf57325ccd3e3b2b057e3c129ec1e277d6228d0` | 4624 / 73601 | 71 |

All three `s VERIFIED` under the bundled drat-trim. The local-15 cut is the same column triple
(70/323/354) that section 3 derived from the archive core by a different route. The live-07 and
live-14 cuts are new: their two literals are a joint obstruction, not capacity bounds, and each
single literal alone is SAT.

The one-side encoding is the cleaner form of the argument: `count[k] >= m` is a booking count, so
it hands you `m` distinct outsiders satisfying the pins of column `k`; leaving the untested side
free makes the reduced instance a relaxation, so the refutation is stronger than the cut needs.
No uniqueness-of-the-other-side argument is required, unlike the two-sided instances in section 3.

None of this closes a board: the outer count CNF plus each cut remains SAT. The cuts kill
>=22, >=8 and >=26 distinct count vectors per 30 s of enumeration, against exactly 1 for blocking
a single vector.

## 9. Coverage keystone for the count abstraction (13 boards)

The implication that any board exclusion silently uses — *every* triangle-free 4-colouring of K54
realizing the pins induces counts satisfying every clause of the outer CNF — is now discharged for
the 13 zero-pole-price boards (the three pilots among them). Ingredients I checked directly:

* `RectLocal15/07/14.lean` compile under Lean 4.33.1; `support_covered` depends on
  `[propext, Quot.sound]` only, and says: if `N0 x N1` lies in free cells then some listed
  rectangle has `N0` inside its left support and `N1` inside its right support. Non-vacuous.
* The Lean `rights` tables equal Python's `maximal_rectangles` exactly, as sets, for all three
  boards (141/80/120, zero difference either way) — so the Lean theorem is about the same
  rectangle family the count model uses.
* L1 (K6, 2 colours), L2 (K17, 3 colours, with sound symmetry breaking) and L3 (H42 plus one
  all-ordinary vertex) replay under the archive's drat-trim with `s VERIFIED`; the controls are
  SAT. These give `LIMIT = 16, 5, 2, 1` and the nonempty c-support on each side.
* Price arithmetic agrees with the archive: local-15 cost 280000 / scale 10000 / slack 20000;
  live-07 and live-14 270000 / 10000 / 10000; exactly 13 of the 15 price files have zero
  pole-pair prices.

Steps 4 to 6 of the argument (column retention, the charging identity, and the price lower bound
`C_j >= cap_j - slack/price_j`, which the generator encodes as `slack//w`) are prose bookkeeping
over those finite facts, not Lean. Nothing here closes a board; it is what licenses reading one off
the outer model when the census finishes.

## 10. Census

`local-15`'s count model had at least 58,975 vectors at the time of writing and was still
enumerating. With the measured 0.43 s per vector (lift build plus CaDiCaL plus write), exhaustive
refutation of that board is roughly 7 CPU-hours, about 40 minutes on twelve cores.

## 11. Forty-four cuts, independently rechecked

A second member ran the core-to-cut loop for 25 iterations per board, deriving 44 cuts
(`.ultramath/smwmq7hji/m3/cut/CUTS.tsv`). Its three primary cuts are the same three described
in sections 3 and 8, reached by a third route. I rebuilt **all 44** from their column and
multiplicity lists with my own builder, on the full 54-vertex graph and with every
monochromatic-triangle clause — a strictly stronger instance than the truncated 31-vertex one
they certify on — and all 44 are UNSAT with `drat-trim` `s VERIFIED`:

```
UNSAT verified 44 / 44
```

The unit cuts are genuine strengthenings, not restatements of the class capacities: live-07
column 89 has chain length 3 and the cut drives it to 1; column 269 has length 12 and its cut
drives it to 3; column 85 has length 26 and the loop-it03 cut drives it to 2. That is the
failure mode that killed the naive loop in section 5, and it is avoided here.

What remains open is minimality: "weaker sub-instances SAT, so the cuts cannot be shortened"
holds inside the truncated encoding only, and the corresponding two-witness instances on the
full graph are undecided at 200,000 conflicts. No minimality claim is made for the full graph.

## 12. Exhaustive pass on local-15, restarted

With the swarm winding down, `ours/exhaust.py local-15 3` is running again: three workers
enumerate the count model and refute each lift, one ledger row and one DRAT file per vector.
The census passed 66,600 vectors and was still growing, so the pass is projected at roughly
2.5 to 3 hours on three cores. Its completion is what would turn local-15 from "58 closed,
14 open" into a board exclusion backed by an exhaustive, replayable case split.

## 13. The 72 boards are a sample, not a cover - and what that means for the bound

This is the most consequential finding of the session and it is a negative one about the shape of
the whole exercise, not about any individual proof.

The archive's seed-12 split decomposes into 24 rooted H42/H42 placements, then marked 2x2 crossing
blocks (59,925 block orbits), then colourings of those blocks' four cells (2,809,638 colour orbits).
A leaf of that split forces **four named cells to ordinary colours**. A board pins **66 to 96 named
non-pole cells to c** (recomputed here: 196 cells minus free cells minus 27 pole-star cells;
local-15 70, live-14 66, fresh-07 77, the range 66-96 over the 72).

So a board refutation excludes colourings whose c-set contains the board's pins, while a leaf lives
where four named cells are guaranteed *not* c. Neither implies the other, and a colouring with c
only on the pole stars lies in no board's up-set at all. Consequences:

* closing the 14 open boards moves the sample ledger from 58/72 to 72/72 and discharges **zero** of
  the 2,809,638 leaves, i.e. zero claim-(c) steps;
* the honest seed-12 ledger is "0 of 24 placements refuted, 0 of 2,809,638 leaves discharged";
* the count machinery has no leverage on a leaf either: a leaf's instance has 2 maximal rectangles
  and 4 count columns against a population of 26, versus 68-167 rectangles and 236-717 columns for
  a board.

`START_HERE.md` says as much ("the 72 reference crossing patterns are a sample"; "the 14 open
sampled boards cannot substitute for this coverage argument"), but nowhere quantifies it. The
session's board work therefore has to be described as *development on the densest-pinned instances*
- the cheapest place to build and validate an argument - and not as progress toward R(3,3,3,3) <= 54.
The pin-density frontier is worth recording: 11 of 11 boards with at most 72 non-pole c-pins are
open, 51 of 51 with at least 78 are closed, and the band 73-77 holds 7 closed and 3 open.

Because of this, the exhaustive per-vector pass on local-15 was stopped at 2,641 refuted vectors
rather than run for days: it would close one dense board and buy nothing at seed level.

## 14. Pin-free cell capacities: a real strengthening, and a measured dead end

The archive's per-cell capacities are the two-anchor Ramsey numbers 16/5/2/1. On a placement where
only the pole stars are pinned these are not tight. Exact values, each certified:

| cells | archive bound | exact pin-free | total saved |
| --- | --- | --- | --- |
| 936 two-spoke | 5 each (4680 total) | 1,2,3,4,5 for 88/24/488/280/56 cells (3000) | 36% |
| 3432 three-spoke | 2 each (6864) | 160 hold none, 1920 hold one, 1352 hold two (4624) | 33% |
| 78 one-spoke | 16 | 10 hold only 6, the rest 7 | - |

These are valid for every board of that placement and for every leaf, so they are worth far more
than a pinned cut. But they are not enough: applied to local-15's outer CNF they sharpen 87 classes
(9452 capacities down to 9406, a 2.4% reduction) and leave the model **SAT**. So per-cell capacity
tightening, even at its exact value, is not the missing constraint. That closes a direction that
looked promising from the outside.

## 15. The capacity table is now kernel-checked

The 16/5/2/1 table itself no longer rests on three SAT runs and prose. `K54Cap.anchor_capacity`
(Lean 4.33.1, compiled here) states: in a triangle-free 4-colouring, a set W of vertices sharing
`m >= 1` distinct anchor vertices with `m` distinct anchor colours, none of them in W, has
`|W| <= 16/5/2/1` for `m = 1,2,3,4`. Proof: a pair in W cannot take an anchor colour or it forms a
monochromatic triangle with that anchor, so W is a triangle-free `(4-m)`-colouring and the repo's
kernel-checked `R(3,3) <= 6` and `R(3,3,3) <= 17` apply. All six theorems depend on
`[propext, Classical.choice, Quot.sound]` only; no `sorry`, no `native_decide`. Board-independent.

## 16. No symmetry quotient exists

The census cannot be reduced by symmetry. Colour-preserving `Aut(H42)` has order **4** (a Klein
four-group), not 2 as an earlier note claimed; but for all 14 open boards the only pair in
`Aut(H42)^2` preserving the 14x14 pin mask is the identity, and the side-swap coset is empty
(checked over all 16 pairs per board). A global colour permutation fixing c would be a symmetry of
realizability, but none of the six preserves the priced class structure of local-15, live-07 or
live-14 - only the identity does. So the case count is genuinely in the 10^5 range.

## 17. Coverage is complete for all 15 boards with a price file

The keystone of §9 covered the 13 zero-pole-pair-price boards. The general indexing now covers
`live-06` and `live-20` as well, so for **every** board that has a price file: any triangle-free
4-colouring of K54 realizing the board's pins induces counts satisfying every clause of its outer
count CNF. An UNSAT outer model is therefore a board exclusion, and cuts certified on
distinct-witness instances can be added soundly.

What I checked: the general indexing reproduces `columns_for` **identically, element for element**,
on all 13 zero-mux boards (8619, 10917, 495, 12110, 672, 12216, 2473, 18475, 717, 14050, 8539,
10800, 12911 columns) and returns 11610 / 8661 for live-06 / live-20; the two new Lean rectangle
covers compile with `support_covered` depending on `[propext, Quot.sound]` only. The pole-pair
class is a real two-anchor class - members share colour x at the side-0 pole and y at the side-1
pole, so their mutual edges avoid both, giving capacity 5 for x != y and 16 for x = y - and it is
charged with no forced occupants (`forced_left = forced_right = 0`), which over-counts capacity and
is therefore the safe direction. Retention does not depend on the mux arithmetic: even with the
pole terms deleted from the cutoff, the most expensive kept column (29994 and 21372) stays below it
(30359 and 21652).

## 18. The audit found two things worth carrying back to the archive's author

* **live-14 has 675 columns, not 672.** The archive's cost cutoff `total - 25*scale` discards three
  columns that exist. That filter is only valid at population 26, so live-14's column indices must
  not be reused at any other population. local-15 (717) and live-07 (495) are unaffected.
* **live-07's stored cut certificate is not the instance its stated cut regenerates.** It differs by
  two clauses (one rectangle clause, one class clause) - the stored file encodes a cell that differs
  by one anchor vertex. Both are UNSAT with an 80-clause core, so nothing is unsound, but the
  stored certificate is unreproducible from the stated cut.

Also confirmed: the two-sided cell test that yields `count_k <= 1` from a two-witness refutation is
only valid when the rectangle has a **unique column on the far side**, since only then does booking
into column k force the outsider's other-side signature. All four published unit cuts pass that
test, so `count_269 <= 1` (live-07, chain length 12) and `count_89 <= 1` are sound and strictly
stronger than the archived `count_269 <= 3`.

## 19. Where the truncation route actually stands

Pinned instances of the open boards are SAT up to order 40 and undecided at 41, 42 and 54. Orders
43-53 were untested in the audit; a single UNSAT there would close a board with a strictly smaller
certificate than K54. Sweep in progress at 45 s per instance over the three densest-pinned open
boards. First results: fresh-07 OPEN at orders 43, 44, 45, 46, 47. The frontier is where the
satisfiability threshold sits, not where the problem gets easier.

## 20. The cuts now rest on the Lean kernel, not on drat-trim

`Mathlib`'s `lrat_proof` command checks an LRAT refutation at elaboration time, so a cut can be
verified by the kernel instead of by an external checker. The pipeline is: drat-trim on the instance
to get the UNSAT core and the core lemmas, drat-trim again on core + lemmas with `-L` so the LRAT
ids are numbered against the core, a check that **every core clause occurs verbatim in the
instance**, then `lrat_proof (include_str "core.cnf") (include_str "core.lrat")`. The subset check is
the load-bearing step - kernel-proving the core UNSAT proves the instance UNSAT only because the
core is a subformula - and it is done mechanically (`clauses_outside_instance = 0`).

94 instances are kernel-checked this way (50 from the fixed-vector loops, 44 from the cut loop),
cores 11-480 clauses, LRAT at most 37 KB, zero RAT lemmas, every one depending on
`[propext, Classical.choice, Quot.sound]` only. I compiled one myself to confirm, and I added the
`-u[354,1] -u[323,1] -u[69,1]` cut to the set: `cert-local-15-b`, 64-clause core, 348-byte LRAT,
kernel-checked in 37 s. So all four published cuts (local-15 70-triple, local-15 69-triple, live-07,
live-14) are kernel-backed, not merely drat-trim-backed.

The wall is measured and worth recording: the full counted CNF of live-17 yields a 53 MB,
7.5M-step LRAT that is OOM-killed by Lean at 617 s. The kernel route is viable exactly where it is
needed - for cut-sized cores - and not for whole counted instances.

## 21. Housekeeping

The audit also flagged eight unusable traces in `work/k54/ours/`; all eight were mine, not the
archive's - truncated DRAT files from runs I killed on a timer, and 85 stale proof files whose CNFs
had been deleted. They are now removed (1.8 GB), which also disposes of the one unsound artifact
among them: `core/l15-cut3.cnf`, the early left-side cut that never corresponded to a count
variable.

## 22. Which open board is cheapest, and why the cut programme stalls

A survey of all 14 open boards by the size of the count model, plus three measured negatives:

| board | types (columns) | note |
| --- | ---: | --- |
| live-07 | 495 | price cover prunes nothing; the pin pattern is what makes it small |
| live-14 | 675 | full universe (the archive's 672 drops 3 by its cost filter) |
| local-15 | 717 | price cover prunes nothing |
| the other 11 | 8 540 - 18 475 | 12-25x larger; nothing else is cheap |

So there is no cheaper open board than the three pilots, and the reason is structural, not the
price certificate: for the pilots the number of retained columns equals the full type universe.

Three negatives, each measured rather than asserted:

* **Census rate does not decay.** live-07 3 189 vectors in 150 s (21.3/s), live-14 2 344 (15.6/s),
  local-15 90 775 in 65 min (23/s). A per-vector closure costs (census size) x ~0.4 s and the
  census is not in the thousands.
* **live-17's route does not transfer.** Its count model was UNSAT in 10 982 conflicts; fresh-07
  and live-02 are UNKNOWN at 1e6 conflicts / 600 s, and the pure encodings of live-02, local-17 and
  local-24 are UNKNOWN at 2e5 conflicts. OPEN, not refuted.
* **Same-rectangle same-side pair cuts are nearly vacuous.** 74 new cuts were certified on live-07
  (all DRAT-replayed, all 74 rebuilding cleanly) and they kill 2 of 800 sampled census vectors,
  0.3%. The undecided pair tests cost 3.3 CPU-s each - 484 of 558 were undecided at 30 000
  conflicts - because the non-pinned spokes are entirely free, so the two-witness instance is far
  harder than the per-vector lift (0.05 s). Any systematic pair scan must spend its budget on
  cross-rectangle pairs.

The soundness of the pair family is clean: one vertex carries at most one type per side, so two
same-side columns always have distinct witnesses and no case split is needed. Opposite-side pairs
are excluded for exactly that reason.

One reproducibility defect: the 74-cut ledger records only the indices `i`, `j` and the rectangle,
not the generator call, and an independent rebuild gives 72 982 clauses against the recorded 73 008,
with none of the first five hashes matching. The indices do resolve to real columns of
`columns_for('live-07')`, so the cuts are presumably what they claim, but the ledger must record the
full `(rect, side, sig)` triples and the exact generator parameters to be checkable by anyone else.
