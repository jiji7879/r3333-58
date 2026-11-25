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
monochromatic triangle. Bounds, stated with their standing: the dynamic survey (Radziszowski,
DS1.18 rev. 18, Apr 2026) lists **51 <= R_4(3) <= 62**, the upper bound due to Fettes-Kramer-
Radziszowski (Ars Combin. 72, 2004). Tatarevic's preprint arXiv:2610.36648 improves it to **60**
("we improve the upper bound ... from 62 to 60") and is what this bundle is built on; it is a
preprint, checked by two solvers and not independently DRAT-verified. Cite both rather than one:
62 is the survey figure, 60 is the operative figure for the K60 campaign this bundle belongs to.

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
| live-07, live-14, local-15 | feasible | **0** | count model SAT — verified integral witnesses, so the board cannot be excluded by refuting its strengthened count model |
| live-16 | feasible | 287 of 289 | **undecided** — integer infeasibility would close the board |
| local-20 | feasible | 171 of 181 | **undecided** |
| local-22 | feasible | 236 of 238 | **undecided** |
| live-13, local-24 | timed out even as a relaxation | — | **undecided** |
| fresh-07, live-02, local-09, local-17 | OPEN | — | **undecided** |

So **nine of the twelve open covered boards are not known to be out of reach at all**, and any one
of them that proves integer-infeasible is a new board exclusion. Only the three pilots are settled
negatively, and that rests on actual integral count vectors, not on a relaxation: the archive's own
CaDiCaL model for each pilot was re-verified here clause by clause (0 violations out of 407,864 /
247,648 / 312,587 clauses, u[k,m] chains all genuine prefixes, mass 26 + 26), so each of those three
count CNFs is SAT. Note the precise scope of that: it rules out excluding a pilot board by refuting
*its strengthened count model*; it does not rule out the census route, which adds sound per-vector
cuts until the model becomes UNSAT and is merely expensive (section 6).

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
3. **Request the missing pieces from the bundle's author** — *corrected: there are none.* The
   bundle does contain all twelve seed formulas (`seeds/`, hashes verified here, all OPEN) and a
   written coverage argument (`checkpoints/structural/README.md`). An earlier version of this report
   said otherwise and was wrong. What the coverage argument does *not* do is finish: it covers
   1,881,012 of 2,136,206 rooted template-pair orbits by its matching/twins dichotomy, with seeds 2
   and 4 contributing zero, and the README says plainly that it "counts no completed seed
   refutations".
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
python3 ../../tools/k54/replay_marginal_cuts.py
# kernel-check one cut core through LRAT
python3 ../../tools/k54/kcheck_lrat.py kc/out cert-x INSTANCE.cnf PROOF.drat
# row-sum relaxation: feasible/infeasible per board
python3 ../../tools/k54/rowsum.py local-15 --timelimit 120
python3 ../../tools/k54/rowsum_bb.py live-17 --seconds 150
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

## 12. Independent audit of the crossing-cut handoff (added after review)

A second handoff, `R3333_K54_crossing_cut_handoff.zip` (4.0 MiB, 132 files, `sha256sum -c` clean),
reduces seed 12's dispatch by 40.8%: marked rectangles 59,925 -> **35,031**, marked rectangles with
all four crossing colours 2,809,638 -> **1,662,749**. It also supplies two mathematical results.
Both were checked here, and both hold.

### 12.1 The K5 lemma is correct

*Claim.* In a 3-colouring with no monochromatic triangle, take a K5 that uses only two colours, and
any three of its vertices S. At most two outside vertices can avoid the third colour on all three
edges to S; there are exactly five ways for such a vertex to meet the K5, and their compatibility
graph is a 4-cycle plus an isolated vertex.

*Check.* The only 2-colouring of K5 without a monochromatic triangle is a 5-cycle in one colour and
its complement 5-cycle in the other, unique up to relabelling. Enumerating all types and all
coexisting triples (searching over the mutual edge colours, since coexistence is not a pairwise
condition) gives, for **every** choice of S: exactly **5** legal types, and **no** three that can
coexist. The pairwise compatibility graph has degree sequence 2,2,2,2,0 with four edges - a 4-cycle
plus an isolated vertex, exactly as stated. Max clique 2. The lemma and its proof sketch are right.

### 12.2 The size-four capacity table is correct, and it is the crux

The theorem's engine is: for a 4-set P of template positions, at most four outsiders can have their
entire c-support inside P - except for 12 exceptional 4-sets where five can. Then 56 > 55 closes the
argument.

*Check.* Rebuilt independently in this session with my own CNF (H42 plus k outsiders, c-spokes
confined to P, all monochromatic-triangle clauses, including outsider-outsider triangles) and
Cadical: of the 1001 four-sets, **989 have capacity 4 and 12 have capacity 5**, and the twelve sets
are exactly `results/saturated4.json` in the handoff. Each pole position lies in 3 or 4 of them, so
at most 9 exceptional sets avoid a given pole - the step that yields 9*4 + 4*5 = 56.

*The arithmetic.* If no rectangle crosses the partition, the singleton sets L and the part-confined
sets M cover 26 outsiders with |L| <= 13 and |M| <= 13, so both are 13 and disjoint; Hall gives 13
distinct representative columns; hence |E(D)| >= sum over M of |S(w)| >= 9*4 + 4*5 = **56**. From the
other side each of the 13 rows meets both parts with degrees d1,d2, contributing d1*d2 >= d1+d2-1
cross-part column pairs, and each pair has at most one common row (two would be the forbidden
rectangle), so |E(D)| <= 13 + |B1||B2| <= 13 + 6*7 = **55**. Contradiction. The inequality chain is
correct as written.

### 12.3 The Lean core and the cover arithmetic

`formal/CrossCut.lean` compiles here and `forcedRectangle` depends on
`[propext, Classical.choice, Quot.sound]` only. It states the counting step: 13 rows, each meeting
both parts, with >= 56 ordinary edges, cannot be pairwise disjoint in their cross-part pairs. The
premises (that the edge count is >= 56) are *not* derived in Lean - the handoff says so, and that is
the honest boundary.

`src/cut_cover.py` re-derives the whole orbit cover from the placement data and the certified
partitions, rebuilding the group action per placement, checking that the 6,084 raw rectangles are
partitioned, recomputing the number of inequivalent colourings per representative, and asserting
equality with the saved `results/cover.json` and the omitted-orbit list. It reproduces
`{'old_marks': 59925, 'kept_marks': 35031, 'old_colored': 2809638, 'kept_colored': 1662749}`.
Dropping an orbit requires **every** image (including side-interchanged images) to miss the cut, so
coverage survives - and since a colouring may carry several marks, an omitted branch can still be
satisfiable in isolation, which the handoff states.

### 12.4 What this does and does not do

It reduces the *number of cases a search must dispatch* in seed 12 by 40.8%, with a sound covering
argument. It does not close a case: 1,662,749 coloured orbits remain, all 12 seeds are open, and the
sample ledger is still 58/72. The handoff says this itself ("it does not measure wall-clock
speedup"). Beyond the size-four table, the tightness certificates for subsets of sizes 1, 2, 3 and
5-13 come from its own data files and were **not** audited here.

## 13. How far the crossing-cut verification was pushed

The load-bearing finite input of the crossing-cut theorem is tightness: a position set `P` is tight
when at most `|P|` outsiders can have their whole c-support inside `P`, and every certified partition
must have all its parts, and all their subsets, tight. Verified here with an independent CNF (H42 plus
k outsiders, c-spokes confined to `P`, every triangle clause including outsider-outsider):

| subsets | count | result |
| --- | ---: | --- |
| size 1 | 14 | all tight |
| size 2 | 91 | all tight |
| size 3 | 364 | all tight |
| size 4 | 1001 | 989 tight, 12 with capacity 5 (the exceptional list, matching theirs exactly) |
| whole parts of 8 sampled certified partitions (sizes 5-8) | 8 | all tight |

So every subset of size <= 4 on H42 is tight, which is what the counting half of the proof uses
(`k`-point capacities for `k <= 3`, and the size-four table for the 56-edge bound). Eight of the
partitions' actual parts were spot-checked at their true sizes and all are tight.

**Not verified:** the weighted certificates covering subset sizes 5-13 in general. Partitions whose
parts have size 6 or 7 lean on those, and only sampled instances were re-derived here. Any consumer
of the cover should treat that family of certificates as the remaining unaudited input.

## 14. Two measured dead ends on the undecided boards

**Exact static aggregation is vacuous by construction.** The obvious way to shrink the count model is
to merge columns that have identical incidence in every row. Implemented exactly (a merged variable
z = sum of a group with added bounds is a faithful encoding, since any integer in range splits within
the individual bounds), it produces **8539 groups from 8539 columns** on local-20 - no merging at
all. The reason is structural, not an accident of implementation: a column is a triple
(rectangle, side, signature), its rectangle/side membership fixes a unique balance row and a unique
population row, and two distinct signatures differ in at least one class row. So no two columns ever
share a row support, and no aggregation can help. Anyone who proposes column merging for this model
can be told this once.

**The full MIP is slow.** HiGHS on the complete integer model of local-20 (8539 integer variables,
847 rows) reaches the 600 s time limit without status: OPEN, not infeasible. That is a legitimate
outcome, not a refutation - but it removes "just hand it to a MIP solver" as a shortcut for the nine
undecided boards, and it is consistent with the row-sum relaxation timing out at 300 s on the same
board.

What remains for the nine boards is either a long CDCL run on the strengthened CNF, a smarter
decomposition of the integer model, or a heuristic hunt for an integral witness. A swarm is running
on exactly those three routes.

## 15. live-16 is off the undecided list: its count model is feasible

Of the nine boards whose integer count model was undecided, the first is now settled - negatively.

**live-16 has an integral solution of its count model.** The witness is 52 columns, each with count
1, giving mass 52 (26 left, 26 right). Verified here independently, rebuilding C0-C4 from the
archive's own `instance()`/`LIMIT` and evaluating the vector:

| constraint | rows | violations |
| --- | ---: | ---: |
| C0 per-column bounds | 12216 | 0 |
| C1 per-rectangle balance | 90 | 0 |
| C2 population | left 26 / right 26 | 0 |
| C3 anchor-class capacities | 3782 distinct | 0 |
| C4 price lower bounds | 0 (none active) | 0 |

A third, strongest check fixes the 13015 unary chain variables in the archive's regenerated
count CNF (3,816,422 vars / 8,237,447 clauses, matching the handoff's figures exactly) and lets
CaDiCaL decide the residual, which returns SAT. Negative controls behave: bumping one left column
breaks C1, and adding a column of a saturated class breaks C3.

**Consequence.** live-16 cannot be excluded by the count-model route and is removed from the
undecided list. The undecided set is now eight: fresh-07, live-02, local-20, local-22, live-13,
local-24, local-09, local-17.

**Method note worth keeping.** HiGHS returned status *time limit*, not optimal or infeasible, but it
had an integral incumbent with the correct left mass by 280 s. On these models the incumbent, not the
status, is the answer - which is exactly why my own local-20 run looked like a failure at 600 s.

## 16. The 4/4/3 packing bound is verified, and it strengthens the crossing-cut theorem

The crossing-cut theorem proves 56 > 55 ordinary edges. The handoff claims a sharper bound
(4, 4, 3 outsiders with exactly four c-neighbours at poles 0, 2, 4), lifting 56 to 61, 61, 62.
Verified here from scratch:

* **Capacity table, sizes 1-4.** 14 one-sets all tight; 91 two-sets all tight; 364 three-sets all
  tight; of the 1001 four-sets, 989 have capacity 4 and 12 have capacity 5, the twelve being
  277, 550, 1162, 2121, 4388, 4417, 5154, 5192, 8724, 8834, 10257, 10376. Two independent
  computations agree on this, mine and the swarm member's, from separate encoders.
* **Packing bound.** With all 13 singleton slots occupied on H42 and k extra outsiders whose
  c-support is exactly a chosen four-set: pole 0 gives **0 SAT of 56** at k = 5 and **1 SAT of 70**
  at k = 4, so the bound is 4 and is attained; pole 4 gives **0 SAT of 126** at k = 4, so the bound
  is 3.
* **Arithmetic.** |M| = 13, every |S(w)| >= 4 by the three-point capacities, at most 4 (or 3) have
  |S(w)| = 4, hence sum |S(w)| >= 4*4 + 9*5 = 61 for poles 0 and 2 and 3*4 + 10*5 = 62 for pole 4,
  against the upper bound 13 + 6*7 = 55.
* The implicit multiplicity step ("each exceptional four-set occurs at most once") is a real gap in
  the handoff's prose and is closed by 25 duplicate-support refutations.

**What this changes and does not.** It makes the theorem stronger, not the reduction smaller: the
cover was already sound at 56 > 55. The case count stays 1,662,749.

## 17. Two more measured dead ends on fresh-07

* **Branch and bound on the rectangle totals**: OPEN after 2,100 s and 219 nodes (103 infeasible
  leaves). The live-17 precedent (41 nodes) does not repeat here.
* **Full MIP on fresh-07 / local-20**: local-20 reached the 600 s limit with no integral incumbent,
  in contrast to live-16 where an incumbent with the correct mass appeared at 280 s.

So of the eight remaining undecided boards, the cheap routes have been tried on two and neither
decided them. That is why live-16's feasible witness matters: it was found by inspecting a
time-limited MIP's incumbent rather than by any solver reaching a terminal status.

## 18. Eligibility of the certified partitions: fully verified

The 40.8% reduction rests on six partitions actually being *eligible*, meaning every subset of each
part is tight (at most |P| outsiders have their whole c-support inside P). This was the last
unaudited input. It is now closed for the partitions the cover actually uses.

First, only six matter. Keying each placement by the pole of the side the cut is taken on and the
partition mask, the 24 placements use exactly six distinct certified partitions:

| pole | mask | part size | complement size |
| ---: | ---: | ---: | ---: |
| 0 | 1776 | 6 | 7 |
| 2 | 2032 | 7 | 6 |
| 2 | 5521 | 6 | 7 |
| 4 | 3813 | 8 | 5 |
| 4 | 5761 | 5 | 8 |
| 4 | 6158 | 5 | 8 |

Then, checked here with an independent CNF (H42 plus |P|+1 outsiders, c-spokes confined to P, every
triangle clause):

| subsets | count | result |
| --- | ---: | --- |
| all sizes 1-4, everywhere on the template | 1470 | tight (with the 12 four-set exceptions) |
| size >= 5 within the twelve parts | **390** | **all tight, 0 failures** |
| four-subsets of the twelve parts that are exceptional | 375 checked | **0 exceptional** |

So every subset of every part of every partition the cover uses is tight, and no part contains one of
the twelve capacity-5 four-sets. Combined with the previous section this leaves the reduction's
chain verified end to end except for the hand counting argument (checked by hand and by hand again,
not machine-checked) and the exhaustiveness of the 115-row K14 catalogue, which is taken from the
archive.

**The reduction's three separate claims, kept apart:**

1. the cuts are *valid* - crossing-cut theorem, counting half in Lean, finite inputs verified here;
2. the stored partitions are *eligible* - now verified (this section);
3. the case accounting from cuts to 1,662,749 is *exact* - re-derived by two independent
   implementations, 0 discrepancies.

All three hold. What still does not exist is a refutation of any of the 1,662,749 cases.

## 19. local-20 is off the undecided list as well

The integer MIP on local-20 (8539 integer columns, 847 rows) returned **OPTIMAL** at 521 s with an
integral solution, and my independent checker confirms it:

| constraint | rows | violations |
| --- | ---: | ---: |
| C0 per-column bounds | 8539 | 0 |
| C1 per-rectangle balance | 68 | 0 |
| C2 population | 26 / 26 | 0 |
| C3 anchor-class capacities | 2800 distinct | 0 |
| C4 price lower bounds | none active | 0 |

mass 52, support 51, maximum count 2. Witness kept at `work/k54/witnesses/w-local-20.json`.

So **local-20's count model is feasible** and the undecided list is down to seven: fresh-07, live-02,
local-22, live-13, local-24, local-09, local-17.

Two of the three boards whose relaxation was feasible-but-fractional have now been settled in the
negative, by the same method: a MIP that was never asked for an optimal objective, only for integral
feasibility, and whose answer had to be read off the incumbent or the terminal status depending on
how the solver behaved. live-16 gave an incumbent under a time limit at 280 s; local-20 went all the
way to OPTIMAL at 521 s. local-22, which was the third such board, is running now.

**Methodological point.** For three of these boards the previous session had concluded only that
"the relaxation is feasible but fractional", which says nothing about the integer model - it does not
show the model is satisfiable, and it does not show it is not. Actually solving the integer model
takes minutes, not hours, and should have been the first thing tried rather than the last.

## 20. Eligibility: complete, not just the six load-bearing partitions (supersedes §18)

An exhaustive independent run closes the eligibility question for **all 161 stored partitions**, not
only the six the cover uses:

* 161/161 partitions fully eligible, 0 non-tight subsets.
* Every set the certificate table calls tight at size 4-8, for all three poles (5980 masks), is
  tight; 18,595 UNSAT instances over 7,087 distinct position sets, each with a DRAT accepted by
  drat-trim **and** Kissat agreeing, 93.7M conflicts total, median 0.031 s.
* **Sharpness**: capacity(P) = |P| exactly for all 8,872 masks, so the certificates are exact bounds
  and no eligibility was lost by using them.
* The domain restriction is sound, not a gap: all 161 stored partitions have both parts of size 5-8,
  so subsets of size <= 8 are the only ones that can matter (a part of size k has bound ~35 > k).
* Calibration against the archived `cap.cpp`: capacity 0/1/2/3 for empty/single/2/3-sets, and
  exactly 8 of the 715 pole-0 four-sets admit five outsiders - the two orbits of the twelve
  saturated exceptions.
* The pole exclusion is load-bearing: allowing c-spokes to the pole makes every instance SAT, so
  forgetting it would have made the whole table vacuous.

Checked here independently and consistently: all 161 partitions have part sizes in {5,6,7,8}; my
own 390-subset run over the six load-bearing partitions found 0 failures; and a fresh sample of
twelve size-6 and size-7 part-subset instances gave capacity exactly |P| (SAT) with tightness at
|P|+1 (UNSAT), 12 of 12.

**The crossing-cut reduction now has all three links independently verified, none using the
handoff's own code**: the cuts are valid (crossing-cut theorem, counting half in Lean, finite inputs
checked), the certified partitions are eligible (this section), and the case accounting is exact
(two independent implementations, 0 discrepancies). The reduction is therefore sound as a
reduction. It still refutes none of its 1,662,749 surviving cases.

## 21. Four of the nine undecided boards are feasible; five remain

Integral count vectors have now been found and independently verified for **four** of the nine
boards that were undecided:

| board | columns | how it was decided | violations on re-check |
| --- | ---: | --- | --- |
| live-16 | 12216 | HiGHS incumbent under a time limit, 280 s | 0 |
| local-20 | 8539 | HiGHS OPTIMAL, 521 s | 0 |
| local-22 | 10800 | HiGHS OPTIMAL, 990 s | 0 |
| local-24 | 12911 | HiGHS incumbent under a time limit, 1001 s | 0 |

Each was re-verified here against C0-C4 from the archive's own `instance()`/`LIMIT`: 0 bound
violations, 0 unbalanced rectangles, population exactly 26/26, 0 class-cap violations, 0 price
violations, mass 52.

**Five remain undecided**: fresh-07, live-02, live-13, local-09, local-17. What distinguishes them
is that the MIP returns *no incumbent at all* within 1,000-2,500 s (as opposed to returning a
fractional or infeasible one), which is the behaviour one expects when the model is infeasible or
nearly so - fresh-07 additionally ran 10^6 conflicts in its CNF encoding without producing a model.
That is a signal, not a proof: no board has been excluded, and a limiter stop is not evidence.

**What this changes.** The list of boards that the count-model route could still close has shrunk
from nine to five. It does not change the bound - the boards are a sample of seed 12 - but it means
that any further counting effort should be spent on those five and nowhere else.

## 22. fresh-07: certified rectangle bounds, and still OPEN

The last undecided board with a serious attempt records an OPEN, but with a genuine reduction
attached that applies to all of them.

**Certified rectangle bounds.** For each maximal rectangle r, let n_r be the number of outsiders
booked into it on one side. The LP maximum of that total over C1-C4 and the column bounds is a valid
upper bound on n_r in any integer solution, since integer solutions are LP-feasible. Recomputed here
independently for fresh-07: every rectangle has **n_r <= 3**, and since sum of n_r = 26 at least
**nine** rectangles are used. Capping each unary chain at 3 shrinks the instance from 2,396,462 vars
/ 5,239,842 clauses to **1,208,606 / 3,151,262** - about 40% fewer clauses, and it is a sound
restriction, not a relaxation.

A caveat recorded because it matters for reproducibility: the exact distribution of U_r across
rectangles differs between my computation (55 rectangles at U=1, 35 at U=2, 4 at U=3, 1 at U=0) and
the member's (58 / 33 / 4 / 0). Both agree on the bound of 3, so the reduction is safe, but the
per-rectangle values sit on an LP boundary and a documented floor tolerance is needed before the
table itself can be treated as a certificate.

**Three negatives that close cheap hopes for fresh-07:**

* with the population equality relaxed the LP reaches only 26.65, with 319 of 320 support columns
  fractional - the LP sees nothing;
* the tight-rows-only relaxation (cap <= 2) is SATISFIABLE, its model violating 47 class rows
  (39 cap-3, 7 cap-4, 1 cap-12) - so no tight-class argument can exclude fresh-07;
* with the per-rectangle balance rows dropped, the two sides pack 26 + 26 at zero violation - so the
  per-rectangle coupling is the entire difficulty.

**Open record.** Full-model CNF: CaDiCaL 600 s / 2.36M conflicts / 843 MB peak, CaDiCaL seed 17
980 s, Kissat 980 s, all UNKNOWN. Tight+47-rows CNF: CaDiCaL 1200 s, Kissat 1100 s, UNKNOWN. Elastic
MIP: bound 0 with 2911 violation. Local search on the 26-unit form: best 10 violated rows of 7203
over 15M+ moves.

So fresh-07 remains undecided, and the convergence of five independent methods on "hard" is the
strongest evidence available that its count model is infeasible - evidence, not proof, and it closes
no board.

## 23. Five of the nine boards are feasible, all independently verified

The standing after the sweeps:

| board | columns | status | violations on re-check |
| --- | ---: | --- | --- |
| live-16 | 12216 | **feasible**, HiGHS incumbent under a time limit | 0 |
| local-20 | 8539 | **feasible**, HiGHS OPTIMAL | 0 |
| local-22 | 10800 | **feasible**, HiGHS OPTIMAL | 0 |
| local-24 | 12911 | **feasible**, HiGHS incumbent under a time limit | 0 |
| live-13 | 12110 | **feasible**, HiGHS incumbent under a time limit, 2501 s | 0 |
| fresh-07 | 8619 | OPEN after five independent methods | - |
| live-02 | 10917 | OPEN, 1001 s, no incumbent | - |
| local-09 | 18475 | running | - |
| local-17 | 14050 | pending | - |

Each feasible witness was re-verified here against C0-C4 from the archive's own `instance()` and
`LIMIT`: 0 bound violations, 0 unbalanced rectangles, population exactly 26/26, 0 anchor-class
violations, 0 price violations, mass 52. Witnesses kept in `work/k54/witnesses/`.

live-13 is the notable one: its row-sum relaxation could not even be decided in 300 s in the
previous session, and the integer model still had a solution that a MIP found within 2,501 s. A
relaxation timing out says nothing about the integer model in either direction.

**What this means.** Of the nine boards that were undecided at the start of this stretch, five now
have integral count witnesses. The count-model route can still close at most four of them:
fresh-07, live-02, local-09 and local-17. That is a substantial narrowing of the only route this
session found that could produce a new board exclusion - and it is a narrowing, not a result. No
board has been excluded and the bound is untouched.

## 24. Final standing on the nine boards, and why size is not the variable

| board | columns | status | how | no incumbent? |
| --- | ---: | --- | --- | --- |
| live-16 | 12216 | **feasible** | HiGHS incumbent under a time limit, 280 s | - |
| local-20 | 8539 | **feasible** | HiGHS OPTIMAL, 521 s | - |
| local-22 | 10800 | **feasible** | HiGHS OPTIMAL, 990 s | - |
| local-24 | 12911 | **feasible** | HiGHS incumbent under a time limit, 1001 s | - |
| live-13 | 12110 | **feasible** | HiGHS incumbent under a time limit, 2501 s | - |
| fresh-07 | 8619 | OPEN | five methods, incl. CDCL 600-980 s and B&B 219 nodes | yes |
| live-02 | 10917 | OPEN | HiGHS, 1001 s and 2501 s | yes |
| local-09 | 18475 | OPEN | HiGHS, 2502 s | yes |
| local-17 | 14050 | OPEN | HiGHS, 2501 s | yes |

All five witnesses were re-verified here against C0-C4: 0 violations, mass 52, population 26/26.
They are stored in `work/k54/witnesses/`.

**Size does not explain the split.** The five feasible boards run from 8,539 to 12,911 columns; the
four open ones from 8,619 to 18,475. fresh-07 at 8,619 is the smallest of the nine and the hardest -
five independent methods found nothing - while local-24 at 12,911 was solved. Whatever separates them
is structural in the pin pattern, not computational scale, and more cores would not change fresh-07.

**The only remaining question** is whether any of the four open boards is integer-infeasible, which
would be a new board exclusion. All four return *no incumbent at all* - not a fractional point, not an
infeasibility certificate, nothing - which is what a model with no integer point looks like, and
fresh-07 additionally ran 10^6 conflicts in its CNF encoding without a model. That is a signal
accumulated across five methods and it is still not a proof. Closing one needs either a long CDCL run
with DRAT on a 3-5M clause instance or an infeasibility argument for the integer model itself.

Even if all four fell, the ledger would move from 58/72 to 62/72 and seed 12 would not be one case
closer to closed, because the boards are a sample.
