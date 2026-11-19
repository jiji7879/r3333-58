# K54 (`R(3,3,3,3) <= 54`): what was verified, what was proved, what is closed

**Audience:** an LLM or researcher picking this up cold. Nothing below assumes prior context.
**Date:** 19 November 2026. **Author of this report:** the agent that audited the bundle.
**Bottom line up front:** the bundle's arithmetic is sound and its certificates replay, but its
central claim cannot be completed from this bundle as it stands. The 72 "boards" inside seed 12 are
a *sample*, not a cover, so closing them cannot close the seed. Counting is provably out of reach
for only three of the twelve open covered boards; the other nine have never had a serious solver run
and remain the live frontier.

---

## 1. The object and the bundle

`R(3,3,3,3)` is the least n such that every 4-colouring of the edges of `K_n` contains a
monochromatic triangle. Known bounds at the time of writing: `51 <= R_4(3) <= 62`. The bundle
attacked the upper bound at 54.

Bundle: `R3333_K54_CAS_SAT_LLM_handoff.zip`, 139.0 MiB, 4,170 entries, 152.1 MiB uncompressed,
zip sha256 `d55ddd0b1186829774203d6d7202c1f669a05df7c0d6c80da6aa7274e3d0406e`. Its own
`SHA256SUMS` verifies on all 4,169 listed files. Read `START_HERE.md` first; it is accurate about
what the bundle contains and honest about it being a sample.

The reduction, as stated by the bundle:

* A hypothetical colouring is reduced to 12 top-level "seeds". **All 12 are open.** The bundle
  contains no coverage argument that closes any of them.
* Inside seed 12 there are 24 rooted `H42`/`H42` placements, then a split into marked 2x2 crossing
  blocks (59,925 block orbits over 146,016 marked blocks) and then colourings of those four cells
  (7,300,917 colourings, **2,809,638 colour orbits** = the "leaves" of the split).
* Separately, there is a **sample** of 72 binary crossing "boards" inside seed 12: 58 excluded,
  14 open. `BOARD_STATUS.tsv` lists them.

A **board** is two 14-vertex copies of the 3-coloured template `H42`, in stated palettes, with a
14x14 binary mask: a zero pins that crossing to the fourth colour `c`, a one leaves it free. The
other 26 vertices of `K54` are "outsiders". A **count model** books each outsider into a maximal
free rectangle and a spoke signature, giving integer counts subject to per-rectangle balance,
population 26, per-class capacities (16/5/2/1) and price lower bounds.

---

## 2. What was verified to work

Everything in this section was rerun from the unpacked archive, not taken on trust.

| check | command | result |
| --- | --- | --- |
| bundle integrity | `sha256sum -c SHA256SUMS` | 4,169/4,169 |
| native solvers | `sh tools/build_native.sh` | CaDiCaL 3.0.1, Kissat 4.0.4, drat-trim build |
| pilot evidence | `python3 tools/verify_pilot.py` | passes for live-07, live-14, local-15: count models checked, one-outsider lifts reconstructed, pair and full DRAT proofs replayed |
| counted checkpoint | `checkpoints/counted/replay.sh` | passes: live-17 29-node arithmetic tree, 15 integer leaves, both K34 controls, both native proofs |

The archive's own generators are faithful: `pilot/make_pilot_cnf.py local-15` reproduces the
archived `pilot/cnfs/local-15.cnf.gz` **byte for byte** (uncompressed sha256
`c7e5a30c39977cdf87472cde292dcdf6c6626bc3fd85dcab686fb48b873bb252`), and its
`checkpoints/counted/src/board.py:graph()` at order 54 gives 4,608 variables / 73,108 clauses for
local-15, matching an independent re-encoder.

---

## 3. New results that stand

All of these are certified; none requires trusting this report.

### 3.1 Certified cuts over the outer count variables (three boards)

Notation: `u[k,m]` is the m-th literal of column k's unary chain in `pilot/cnfs/<board>.counts.json`,
so `u[k,m]` literally means `count[k] >= m`.

| board | cut | reduced CNF (sha256) | vars/clauses | core |
| --- | --- | --- | --- | --- |
| local-15 | `-u[354,1] -u[323,1] -u[70,1]` | `945c876c...e8cd8` | 4608/73165 | 64 |
| local-15 | `-u[354,1] -u[323,1] -u[69,1]` | `d8c638f8...7df137` | 4608/73165 | 107 |
| live-07 | `-u[83,1] -u[52,2]` | `7f425873...bf5c38` | 4600/73004 | 80 |
| live-14 | `-u[1,1] -u[8,2]` | `921d3d1f...228d0` | 4624/73601 | 71 |

Each is a graph instance whose only pins are distinct witnesses of the cut's lower bounds,
everything else free; each is UNSAT with a DRAT that `drat-trim` accepts. The witnesses are
genuinely distinct because all columns of a cut lie on one side (one outsider carries at most one
type per side), and each cut's columns lie in pairwise distinct rectangles.

Two further families exist: 74 same-rectangle same-side pair cuts on live-07, and the **complete
single-column marginal frontier** - 235 cuts on local-15, 124 on live-07, 174 on live-14, 533 in
total, all replaying (`533 verified, 0 bad`).

### 3.2 A kernel-checked trust base

The capacity table 16/5/2/1 no longer rests on three SAT runs plus prose.
`K54Cap.anchor_capacity` (Lean 4.33.1) states: in a triangle-free 4-colouring, a set `W` of
vertices sharing `m >= 1` distinct anchor vertices with `m` distinct anchor colours, none of them in
`W`, has `|W| <= 16/5/2/1` for `m = 1..4`. Proof: a pair in `W` cannot take an anchor colour or it
forms a monochromatic triangle with that anchor, so `W` is a triangle-free `(4-m)`-colouring and
kernel-checked `R(3,3) <= 6`, `R(3,3,3) <= 17` apply. Six theorems, axioms
`[propext, Classical.choice, Quot.sound]`, no `sorry`, no `native_decide`. Board-independent.

94 cut cores are kernel-checked through LRAT: drat-trim extracts the core and emits LRAT against
it, every core clause is checked to occur verbatim in the instance, then Mathlib's
`lrat_proof` reconstructs the refutation in the kernel. Cores 11-480 clauses, LRAT <= 37 KB, zero
RAT lemmas, all with the same axioms. The load-bearing step is the subset check
(`clauses_outside_instance = 0`): kernel-refuting the core refutes the instance only because the
core is a subformula.

### 3.3 Coverage keystone for all 15 boards

For every board b that has a price file: **every** triangle-free 4-colouring of `K54` realizing b's
pins induces counts satisfying every clause of b's outer count CNF. Ingredients: Lean-checked
rectangle covers (`support_covered`, 86/120/141 rectangles for the three pilots, axioms
`propext`/`Quot.sound`), the general pole-pair indexing validated by reproducing
`columns_for` **identically element-for-element** on all 13 zero-mux boards, and DRAT-checked base
lemmas `R(3,3)=6`, `R(3,3,3)=17`, `R(3)=3`, and "H42 has no all-ordinary extension".

---

## 4. Finding A: the 72 boards are a sample, not a cover of seed 12

This is the most consequential structural fact, and it is a negative one.

A leaf of seed 12's split forces **four named cells to ordinary colours**. A board pins **66 to 96
named non-pole cells to `c`** (196 cells minus free cells minus 27 pole-star cells; local-15 70,
live-14 66, fresh-07 77). A board refutation therefore excludes colourings whose c-set contains the
board's pins, while a leaf lives where four named cells are guaranteed *not* `c`. Neither implies
the other, and a colouring with `c` only on the pole stars lies in **no** board's up-set at all.

Consequences:

* Closing all 14 open boards moves the sample ledger from 58/72 to 72/72 and discharges **zero of
  the 2,809,638 leaves** - i.e. zero claim-(c) steps.
* The honest seed-12 ledger is **"0 of 24 placements refuted, 0 of 2,809,638 leaves discharged"**.
* The count machinery has no leverage on a leaf either: a leaf's instance has **2 maximal
  rectangles and 4 count columns** against a population of 26, versus 68-167 rectangles and
  236-717 columns for a board.
* The pin-density frontier: boards with at most 72 non-pole c-pins are **all open** (11 of 11);
  boards with at least 78 are **all closed** (51 of 51); the band 73-77 holds 7 closed and 3 open.

`START_HERE.md` says "the 72 reference crossing patterns are a sample" and "the 14 open sampled
boards cannot substitute for this coverage argument", but nowhere quantifies the gap. The
quantification is Finding A.

**Therefore:** board work is *development on the densest-pinned instances* - the cheapest place to
build and validate an argument - and it is not progress toward the bound. Any report that presents
a board exclusion as a step toward `R(3,3,3,3) <= 54` is wrong.

---

## 5. Finding B: counting is only ruled out for the three pilots — the other nine are open

The count model can be strengthened into an integer program: `x_k >= 0` **integer** per column,
per-class caps, per-rectangle balance, population 26, price bounds. Relaxing `x` to continuous while
keeping the per-rectangle totals integral gives a system whose **infeasibility implies the board is
excluded**, since integer points are a subset of the relaxation.

What that relaxation did, by HiGHS and by branch and bound:

* `live-17` is **INFEASIBLE**: 41 nodes, 21 infeasible leaves, 59 rectangles. This reproduces the
  archive's only integrality exclusion without DRAT and without its 124,959-variable CNF.
* The relaxation is **FEASIBLE** for live-07, live-14, local-15, live-13, live-16, local-20,
  local-22, local-24; fresh-07, live-02, local-09, local-17 remain OPEN at 150-280 s.
* The LP maximum with population removed is 27.0 / 27.0 / 28.0 (pilots) and 26.10 (live-17), so the
  LP is never the obstruction by itself.

**A feasible relaxation does not mean the integer model is infeasible, and the converse reading is
the single most tempting error here.** Integer solutions are a subset of the relaxation, so
feasibility of the relaxation tells you nothing about them. The decisive test is integrality of the
solution found. Checked per board:

| board | relaxation | count vars fractional | status of the **integer** model |
| --- | --- | --- | --- |
| live-07, live-14, local-15 | feasible | **0** | count model SAT — integral witnesses exist, so counting provably cannot close these three |
| live-16 | feasible | 287 of 289 | **undecided** — integer infeasibility would close the board |
| local-20 | feasible | 171 of 181 | **undecided** |
| local-22 | feasible | 236 of 238 | **undecided** |
| live-13, local-24 | timed out even as a relaxation | — | **undecided** |
| fresh-07, live-02, local-09, local-17 | OPEN | — | **undecided** |

So **nine of the twelve open covered boards are not known to be out of reach of counting at all**,
and any one of them that proves integer-infeasible is a new board exclusion. Only the three pilots
are settled negatively, and that rests on actual integral count vectors, not on a relaxation.

An earlier version of this report claimed "counting provably cannot close 8 of the 12 open covered
boards" on the strength of the feasible relaxation alone. That claim was wrong: it confused
feasibility of the relaxation with feasibility of the integer model. The corrected statement is the
table above. Anyone continuing this work should treat the nine undecided boards as the live
frontier — and note that none of them has had a serious solver run: the best previous effort was
600 s / 10^6 conflicts on fresh-07 and live-02, and 170 s / 2·10^5 on the pure encodings of live-02,
local-17 and local-24.

One prior signal is worth acting on: fresh-07's strengthened count CNF ran to **10^6 conflicts
without producing a model**, which is what an unsatisfiable instance looks like, whereas the pilots'
count CNFs are answered in seconds. fresh-07 is the best single candidate in the set.

---

## 6. Measured dead ends

Do not spend compute on these; each was run and measured.

| route | measurement | verdict |
| --- | --- | --- |
| Direct whole-board CNF (no count decomposition) | open after 250,000 conflicts on local-15; 300k elsewhere | dead |
| Truncation to fewer outsiders | SAT at orders 30-40; **OPEN at 41,42 and at every order 43-53** (33 instances, 45 s) on fresh-07, live-17, local-15 | dead; no certificate smaller than K54 |
| Symmetry quotient of the census | colour-preserving `Aut(H42)` has order **4** (Klein four, not 2 as one note claimed); for all 14 open boards the only `(pi0,pi1) in Aut^2` preserving the pin mask is the identity; no side swap; no global colour permutation fixing `c` preserves the priced class structure | no quotient exists; the census is genuinely ~10^5 |
| Single-column marginal cuts | complete frontier, 533 cuts, all verified | real but weak: they roughly double census enumeration speed |
| Pairwise two-witness cuts | 484 of 558 undecided at 30,000 conflicts, 3.3 CPU-s each; same-rectangle cuts kill 0.3% of a census sample | not the missing constraint |
| Tighter per-cell capacities | exact pin-free values are 36% (two-spoke) and 33% (three-spoke) below the Ramsey bounds - a genuine transferable strengthening - but applying them to local-15 sharpens 87 classes (9,642 -> 9,406) and leaves the model **SAT** | not the missing constraint |
| Transfer of count-model UNSAT from live-17 | fresh-07 and live-02 UNKNOWN at 10^6 conflicts / 600 s | does not transfer |
| Transfer of cuts between boards | over all 72x72 board pairs, 144 have a structure isomorphism and **zero** have pins(src) subset pins(dst) | impossible by pin inclusion |

**The census, measured.** local-15's count model has **at least 90,775** distinct count vectors
(23/s, 3,879 s, still growing). With the 235 marginal cuts installed it reaches **at least 44,000**
in 969 s (45/s) and is still growing - so the reduction is a factor of about two, not the "97%"
that one measurement on a solver-biased sample suggested. Per-vector lift refutation costs 0.43 s
(0.35 s Python to build the lift, 0.04 s to write DIMACS, 0.03 s of CaDiCaL); 3,636 such vectors were
refuted with all DRAT verified, mean proof 2.7 KB, cores 67-479 clauses. An exhaustive closure of
local-15 alone is therefore roughly **10 CPU-hours** - a guaranteed certificate for one board of a
sample that cannot close the seed.

---

## 7. Defects in the archive, to hand back to its author

1. **`live-14` has 675 columns, not 672.** The cost cutoff `total - 25*scale` discards three real
   columns. That filter is valid only at population 26, so live-14's column indices must not be
   reused at any other population. local-15 (717) and live-07 (495) are unaffected.
2. **`live-07`'s stored cut certificate is not the instance its stated cut regenerates.** It differs
   by two clauses (one rectangle clause, one class clause) - the stored file encodes a cell off by
   one anchor vertex. Both are UNSAT with an 80-clause core, so nothing is unsound, but the stored
   certificate is unreproducible from the stated cut.
3. **The two-sided cell test needs a uniqueness condition.** Deriving `count_k <= 1` from a
   two-witness refutation is valid only when the rectangle has a **unique column on the far side**,
   since only then does booking into column k force the outsider's other-side signature. All four
   published unit cuts pass, so `count_269 <= 1` (live-07, chain length 12) and `count_89 <= 1` are
   sound and strictly stronger than the archive's `count_269 <= 3`. State the condition; without it
   the same test is unsound for a column whose rectangle has several far-side columns.
4. **A cut over left-side columns is not certified by the archived core.** The archive's
   three-outsider refutation pins *both* signatures; the left signature is not a count variable. An
   earlier cut loop in this project emitted `-u[351,1] -u[322,1] -u[67,1]` on that mistaken reading
   and had to be discarded.

---

## 8. What a next step would have to do

Nothing in this bundle, completed, closes the bound — but one line of work is still live and cheap.

1. **Decide the integer count model for the nine undecided boards (live section).** This is a pure
   SAT problem on an existing encoding, it needs no new mathematics, and either answer is a result:
   infeasible ⇒ a new board exclusion with a DRAT certificate; feasible ⇒ an integral count vector
   proving counting cannot close that board. fresh-07 is the best candidate (10^6 conflicts with no
   model found). The nine have never had a serious run.
2. **Attack the seed-12 leaf structure directly.** The real object is the ordinary-rectangle split:
   2,809,638 colour orbits, each forcing four cells to ordinary colours. Board refutations do not
   touch it. This needs the archive's structural reduction (seeds 5-12: "an ordinary crossing
   rectangle is necessary") to be made explicit and formalised, and it is a different computation
   from anything in the bundle.
3. **Request the missing pieces from the bundle's author**: the actual seed formulas and the
   coverage argument for the 12 seeds, not just the seed-12 sample. Without them nothing can be
   completed.
4. **Publish the method rather than the bound.** What is genuinely new and defensible here: the
   kernel-checked capacity table, the LRAT kernel-checking of cut cores, the coverage keystone
   (Lean rectangle covers + validated general indexing), the complete marginal cut frontier, and
   Findings A and B as structural results about this reduction. None of it moves `R_4(3)`.

**What would change the answer:** a sound way to reduce the leaf space of seed 12 (or of any seed)
to something countable. Absent that, any board-level work - however well certified - is a
sandbox.

---

## 9. Reproduction

Unpack, then from the archive root (Python 3.11+, gcc, gzip; numpy/pysat only for regeneration):

```sh
sha256sum --quiet -c SHA256SUMS
sh tools/build_native.sh
python3 tools/verify_pilot.py
(cd checkpoints/counted && sh replay.sh)
python3 tools/run_native.py lift-local-15-two cadical 12000 runs/l15-two
```

The new work lives beside the archive. Two layouts are referenced below: the archive unpacks to
`work/k54/` inside the project repository, and the session's own scripts are in `work/k54/ours/`;
the swarm members' directories `.ultramath/<swarm>/m<n>/` sit at the repository root, one level
*above* the archive, which is what the `../.ultramath/...` paths below mean.

```sh
# certified cut instances, rebuilt from a cut description alone
python3 ours/check_oneside.py local-15 '[[354,1],[323,1],[70,1]]' a
# complete marginal cut frontier replay (533 cuts)
python3 ../.ultramath/smwmsifse/m5/src/ours/replay_cuts.py
# kernel-check one cut core through LRAT
python3 ../.ultramath/smwmsifse/m3/kcheck.py kc/out cert-x INSTANCE.cnf PROOF.drat
# row-sum relaxation: feasible/infeasible per board
python3 ../.ultramath/smwmsifse/m4/rowsum.py local-15 --timelimit 120
python3 ../.ultramath/smwmsifse/m4/bb.py live-17 --seconds 150
```

Solvers: CaDiCaL 3.0.1 and Kissat 4.0.4 built from the bundle's vendor tarballs, drat-trim
compiled as `cc -O2 -std=gnu11 vendor/drat-trim.c -lm`. Lean 4.33.1 with Mathlib for the kernel
checks (`LEAN_PATH` must include the project's `lean/` directory for the K58 Ramsey lemmas).

---

## 10. Claim ladder - keep these apart

* **(a) One fixed count vector is unrealizable.** Established, repeatedly, with DRAT.
* **(b) A board is excluded.** Established for the 58 sampled boards by the bundle; **not**
  established for any of the 14 open ones.
* **(c) A seed is excluded.** Not established for any of the 12. **Not reachable** from board
  exclusions at all (Finding A).
* **A certified cut** ("these lower bounds cannot hold simultaneously") is strictly between (a) and
  (b): it is true of every graph realizing the board's pins, but it does not exclude the board.
* **A board exclusion** is now *licensed* by the coverage keystone: an UNSAT outer count CNF
  (possibly plus certified cuts) does exclude the board. That is the one piece of scaffolding this
  session added.

---

## 11. What each result rests on

| result | rests on |
| --- | --- |
| capacity table 16/5/2/1 | Lean kernel, `[propext, Classical.choice, Quot.sound]` |
| coverage keystone (15 boards) | Lean kernel (rectangle covers) + DRAT (base lemmas) + prose composition over finite checks |
| cuts in §3.1 | DRAT replay + a distinct-witness argument, all four now also kernel-checked via LRAT |
| 533 marginal cuts | DRAT replay, CNF regenerated and sha matched |
| Finding B (counting closed) | HiGHS/branch-and-bound feasibility certificates; constraint matrix cross-validated against the archive's own CNF |
| Finding A (sample not cover) | recomputation of the orbit counts (24 / 59,925 / 2,809,638, matching the archive) + pin counts + the leaf/board rectangle counts |
| census sizes | direct enumeration with blocking, timed |

**Not verified by anyone:** that the bundle's 12-seed reduction itself is sound. Every result above
is conditional on it. The bundle asserts the reduction; this session did not audit it, and Finding A
suggests the seed-12 side of it is a sample rather than a cover.
