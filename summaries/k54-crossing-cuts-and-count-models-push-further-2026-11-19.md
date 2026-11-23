# K54 (R(3,3,3,3) <= 54): the crossing-cut reduction verified, the count-model frontier narrowed

Session of 19 Nov 2026, continuing the K54 bundle work. Four swarms (`smwmq7hji`, `smwmsifse`,
`smwn8gya1`, `smwn8rsmo`, model deepseek-v4.1-flash, 8/8/8/6 members). Deliverables live in the
repo: `results/K54_REPORT_FOR_LLM.md` (the handoff report, 746 lines), `results/k54-local-15-notes.md`
(session log, 25+ sections), `work/k54/` (unpacked bundle + `ours/` tooling), `work/k54cut/`
(unpacked crossing-cut handoff).

## The bound

Unchanged: **51 <= R_4(3) <= 60**. 62 is the survey figure (Radziszowski DS1.18 rev.18, Apr 2026,
Fettes-Kramer-Radziszowski); 60 is Tatarevic arXiv:2610.36648("we improve the upper bound from 62 to
60"), a preprint. Cite both with standing. Nothing in this session moves either end, and the reason
is structural - see "the sample fact" below.

## The sample fact (the most consequential thing found)

The 72 seed-12 "boards" are a **sample, not a cover**. A leaf of the seed-12 split forces four named
cells to *ordinary* colours; a board pins 66-96 named non-pole cells to c (196 minus free minus 27
pole-star; local-15 70, live-14 66, fresh-07 77). Neither implies the other. Consequences:
closing all 14 open boards moves the ledger 58/72 -> 72/72 and discharges **zero of 2,809,638
leaves**; the honest seed-12 ledger is "0 of 24 placements refuted, 0 of 2,809,638 leaves
discharged". START_HERE.md says boards are "a sample" but never quantified it. Pin-density frontier:
boards with <=72 non-pole c-pins are all open (11/11), >=78 all closed (51/51), band 73-77 has 7
closed + 3 open. **Any board-level result is sample-ledger progress, never seed progress.**

## The crossing-cut handoff (`R3333_K54_crossing_cut_handoff.zip`) - all three links verified

Reduces seed 12 dispatch: 59,925 -> 35,031 marked rectangles, 2,809,638 -> **1,662,749** coloured
cases (40.8%). Verified here with independent code, none of theirs:

1. **Cuts valid.** The K5 lemma is true: in a 3-colouring of K5 with no mono triangle there are
   exactly **5** legal types for any chosen triple, and no three coexist; compatibility graph is
   C4 + isolated vertex (degrees 2,2,2,2,0). The size-four table is right: **989** four-sets have
   capacity 4, **12** have capacity 5, the twelve matching `results/saturated4.json` exactly. The
   56 > 55 arithmetic holds (|E(D)| >= sum|S(w)| >= 9*4+4*5; <= 13+|B1||B2| <= 55).
2. **Eligibility.** Only **6** of the 161 stored partitions are load-bearing (key placements by the
   pole of the cut side, not by side index): pole 0 mask 1776; pole 2 masks 2032, 5521; pole 4 masks
   3813, 5761, 6158. All 161 are fully eligible; all subsets of size 4-8 tight (5980 masks); the
   domain restriction is sound because every part has size 5-8. Sharpness: capacity(P) = |P| exactly
   for all 8872 masks. Pole exclusion is load-bearing (allowing c-spokes to the pole makes every
   instance SAT).
3. **Ledger exact.** Two independent implementations reproduce 59,925/35,031/2,809,638/1,662,749
   with 0 discrepancies.
4. The sharper **4/4/3** packing bound is verified and attained: pole 0, k=5 -> 0 SAT of 56; pole 0,
   k=4 -> 1 SAT of 70; pole 4, k=4 -> 0 SAT of 126. Lifts the edge bound to 61/61/62. Stronger
   theorem, **not** a smaller case count.

What it does not do: refute any of the 1,662,749 surviving cases.

## The count-model frontier

Nine boards had undecided integer count models. **Five are now settled, all negatively** (integral
witnesses, re-verified against C0-C4 with 0 violations, mass 52, population 26/26, stored in
`work/k54/witnesses/`): live-16 (12216 cols, incumbent under time limit 280 s), local-20 (8539,
OPTIMAL 521 s), local-22 (10800, OPTIMAL 990 s), local-24 (12911, incumbent 1001 s), live-13 (12110,
incumbent 2501 s). **Four remain**: fresh-07, live-02, local-09, local-17 - each returns *no
incumbent at all* in 1000-2500 s, which is what an infeasible model looks like; still not a proof.

Method lesson (cost three false negatives): **a feasible LP/fractional relaxation says nothing about
the integer model in either direction** - integer points are a subset of the relaxation, and a
relaxation that *times out* says even less. live-13's relaxation was undecidable at 300 s yet the
integer model has a solution found in 2501 s. Also: read the **incumbent**, not the status - HiGHS
"time limit" with an integral point is a complete answer.

Size does not explain the split: feasible boards span 8539-12911 columns, open ones 8619-18475;
fresh-07 (8619) is the smallest of the nine and the hardest (five methods, 10^6 conflicts in its CNF,
B&B 219 nodes, elastic MIP bound 0 / violation 2911, local search best 10 of 7203 rows violated).

## Other results that stand

* **Kernel-checked capacity table** 16/5/2/1 as a board-independent theorem (`K54Cap.anchor_capacity`,
  Lean 4.33.1, axioms [propext, Classical.choice, Quot.sound], no sorry, no native_decide).
* **94 cut cores kernel-checked through LRAT** (drat-trim -c core, -L lrat against the core, subset
  check that every core clause occurs verbatim in the instance, then Mathlib `lrat_proof`). All four
  published cuts kernel-backed. Wall: full counted CNFs are too big (live-17 LRAT 53 MB / 7.5M steps
  OOMs at 617 s) - the kernel route is for cut-sized cores only.
* **Coverage keystone for all 15 priced boards**: any triangle-free 4-colouring realizing a board's
  pins induces counts satisfying every clause of its outer CNF, so UNSAT outer model => board
  excluded. General pole-pair indexing reproduces `columns_for` identically on all 13 zero-mux boards;
  Lean rectangle covers for live-06/live-20 too.
* Certified cuts: local-15 `-u[354,1] -u[323,1] -u[70,1]` and `-u[354,1] -u[323,1] -u[69,1]`,
  live-07 `-u[83,1] -u[52,2]`, live-14 `-u[1,1] -u[8,2]`, all UNSAT with replayed DRAT and cores
  64/107/80/71. Plus a complete single-column marginal frontier: **533 cuts** (235/124/174), all
  replaying, CNFs regenerated and hashes matched.
* **fresh-07 certified rectangle bounds**: every maximal rectangle holds n_r <= 3 outsiders, so with
  sum n_r = 26 at least nine rectangles are used; capping chains at 3 shrinks the CNF from 2,396,462
  vars / 5,239,842 clauses to 1,208,606 / 3,151,262.

## Dead ends, measured (do not re-spend)

| route | measurement |
| --- | --- |
| direct whole-board CNF, no count decomposition | open after 250k conflicts (local-15), 300k elsewhere |
| truncation to fewer outsiders | SAT at orders 30-40; **OPEN at 41,42 and every order 43-53** (33 instances, 45 s) on fresh-07/live-17/local-15 |
| symmetry quotient of the census | colour-preserving Aut(H42) has order **4** (Klein four, not 2); pin-preserving pair is identity for all 14 open boards; no palette permutation preserves the priced class structure; census genuinely ~10^5 |
| pairwise two-witness cuts | 484 of 558 undecided at 30k conflicts, 3.3 CPU-s each; same-rectangle cuts kill 0.3% of a census sample |
| tighter per-cell capacities | exact pin-free values 36%/33% below Ramsey, but applying them to local-15 sharpens 87 classes (9642->9406) and leaves it SAT |
| count-model transfer from live-17 | fresh-07, live-02 UNKNOWN at 10^6 conflicts / 600 s |
| cut transfer between boards | over 72x72 pairs, 144 have a structure isomorphism, **0** have pins(src) subset pins(dst); local-15 (poles 2,2) reaches no other open board |
| exact static column aggregation | **vacuous by construction**: 8539 -> 8539 groups. A column=(rect,side,sig) fixes a unique balance row and population row, and distinct sigs differ in a class row, so no two columns share a row support |
| census | local-15 >= 90,775 vectors (23/s, still growing); with the 235 marginal cuts >= 44,000 (45/s) - about 2x faster, **not** the "97% killed" a biased sample suggested. ~10 CPU-hours for one board |

## Retracted this session (do not revive)

* **"Counting provably cannot close 8 of the 12 open covered boards"** - WRONG. It inferred integer
  infeasibility from a feasible but fractional relaxation. Corrected: five boards have integral
  witnesses (closed negatively), four are undecided.
* **"The bundle lacks the seed formulas and the coverage argument"** - WRONG. All 12 seed formulas
  are in `seeds/` with matching hashes (all OPEN); the coverage argument is in
  `checkpoints/structural/README.md` (covers 1,881,012 of 2,136,206 rooted template-pair orbits;
  seeds 2 and 4 contribute zero; "counts no completed seed refutations"). The gap is real but
  differently shaped.
* **|Aut(H42)| = 2** (an earlier session's claim) - it is 4.
* A member's **"97.27% of the local-15 census killed"** - sampling artefact; direct enumeration gave
  >= 44,000 surviving vectors.
* `core/l15-cut3.cnf` and the cut `-u[351,1] -u[322,1] -u[67,1]` - unsound: the archived core pins
  *both* signatures and the left signature is not a count variable. Deleted.

## Defects to hand back to the bundle's author

1. **live-14 has 675 columns, not 672** - the cost cutoff `total - 25*scale` drops 3 real columns and
   is only valid at population 26; do not reuse live-14 column indices at another population.
2. **live-07's stored cut certificate is not the instance its cut regenerates** - differs by two
   clauses (one rectangle, one class); UNSAT either way, but unreproducible from the stated cut.
3. **The two-sided cell test needs a uniqueness condition**: deriving `count_k <= 1` from a
   two-witness refutation is valid only when the rectangle has a unique column on the far side.
   All four published unit cuts pass; `count_269 <= 1` and `count_89 <= 1` are sound and stronger
   than the archived `count_269 <= 3`.

## Swarm-process lesson

`smwn8gya1` burned 2 hours with **zero findings and 15+ duplicate refusals**: all eight members
converged on "solve the integer program" and the dedup guard refused every proposal after the first.
Restarting with **job-and-board-disjoint** assignments (`smwn8rsmo`) produced 5 acceptances. Brief a
swarm by *object ownership*, not by *method*, when the object is a list you can partition.
