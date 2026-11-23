# The 19-spoke bound, replayed here from the solver archive alone

Bundle: `attachments/let-s-try-and-wcbj/K58_solver_and_proof_notes.zip` (46.7 MiB), unpacked at
`.scratch/pg/k58-solver-pair-glue/`. **The two DRAT archives the notes ask for
(`K58_DRAT_1_foundations_and_endpoints.zip`, `K58_DRAT_2_interior_splits.zip`) are not present**,
so every stage was run in *regenerating* mode (no `--stored-only`): the verifier rebuilds each CNF
from the row and re-derives each refutation with the bundled Kissat.

## Result: all four stages pass, in 18 min 18 s

```
signatures   Verified the signature and incidence bounds, four K13 witnesses, and 8469 catalogue
             pentagons.  Verified 562 marked 14-arm pentagons on 381 parents.  Verified every
             sector split below 18 on both rows.
endpoints    (7,11) and (10,8): unresolved branches 0, on both rows.
interior     Verified 121 certificates.  U<=8 and V<=10 jointly impossible on both rows;
             (8,10) excluded on both.
balanced     (9,9) excluded on both; 96 local certificates and both parent gluing certificates
             replayed.  "Together with the preceding exclusions, both rows require at least 19
             spokes."
```

Environment: `python3 -m venv .venv` plus the vendored `wheels/` (python-sat 1.9.dev22), no network.
Four workers. So the claim `U+V >= 19` on rows `076eafbfe47e` and `4629be2de806` is reproducible
**without any of the shipped certificates**, at 18 minutes for both rows.

## What the census says about generalising it

Computed here with the bundle's own `pentagons(case)` and `row_info(case)` over all 381 rows of the
profile:

| quantity | value |
| --- | ---: |
| rows with a marked pentagon in arm 2 **and** one in arm 3 | 169 |
| of those, rows where the construction applies (`family.arm = 1`) | **159** |
| core pin counts among the 159 | **215 (134 rows), 225 (25 rows)** |
| rows needing their own board argument after pin containment | **134** |
| difference between the two published rows | 10 |

**Correction (m1 of swarm `smwtqk6ku`, verified here).** The first version of this file counted 169
rows and 185 core pins throughout. Both were contaminated by **ten rows with `family.arm = 0`**,
where the marked colour is the pentagon's own colour and `U,V` would count the wrong thing; those
ten are the only ones with 185 pins. On the 159 that carry the argument the counts are 215 and 225.
The 165 distinct pin sets and median difference 84 were computed over all 169 and stand as stated.

All 169 share the same shape — pentagons at exactly `{30..34}` and `{44..48}`, a 26-vertex core
(`{0} + A + both pentagons`), 185 pinned core edges — but the pin patterns differ substantially. The
two published rows are the **closest pair in the family** (10 edges apart), which is why the pilot
looked tractable.

Consequences:

- certificates **do not transfer** between rows; generalisation is per-row certification;
- **isomorphism does not help**: all 159 relevant rows are pairwise non-isomorphic. Verified here by
  9,211 VF2 tests on the coloured 26-vertex cores (vertex types plus negative pins), 0 isomorphic
  pairs — a fourth program agreeing with m1's three. Classes: 163 over the 169, i.e. a 3.6 % saving
  and none on a relevant row;
- the one real saving is **pin containment**: 25 of the 159 sit on a 215-pin board, so 134 board
  arguments cover all 159 (15.7 %). Verified here, difference exactly 10 literals in every pair;
- measured cost: 18 min 18 s for two rows, so **about 20 h wall for the 134 boards** at the same
  parallelism (the earlier ~60 CPU-hour and ~26 h figures are superseded);
- the driver is hard-wired (`CASES = (ps.SOURCE, ps.SECOND)` in `tools/nine_spokes.py`, and
  `validate()` refuses any other case), so extending it is a code change, not a rerun.

## Where the bound actually lives (m8, verified here)

The most useful structural result on the bundle, and it is negative for the cheapest hope:

- **The 26-vertex core carries none of the bound.** For all 159 shape-P rows the core board
  (pins both signs, triangle-free, plus the Ramsey degree bounds — *stronger* than the bundle's own
  core board) admits `U+V <= 18`, and each of the four splits is satisfiable on it too. Judge's
  check: five witnesses re-verified from the definition, 0 failures. So no certificate that only
  sees the 26 vertices can give 19, and canonicalising cores cannot work — not because there are
  many classes, but because the core has no content to certify.
- **The load-bearing boards are the arms.** On a 35-vertex `(14,5)` board the same query is
  unanswered in 270 s, against ~1 s at the core. That is why the bundle needs 663 certificates.
- **A is rigid**: all 105 pairs inside `A` are pinned in every row, with exactly two templates
  (`T` 308 rows, `U` 73), and **no spoke pair is ever pinned**. The bound is a consequence of arm
  structure, never of the pins.
- **Nine more rows decided.** For 9 of the 18 shape-Q rows (marked vertex inside `A`, spoke colour
  0) the core already forces `U+V >= 19`. Judge's check: all nine CNFs return `s VERIFIED` under an
  independent `drat-trim` invocation, and the same CNF without the bound returns SAT. Four of the
  nine are outside the 169 entirely; the other nine Q rows admit `<= 18` at the core.

Shape census: **P** 159 (the bundle's configuration), **Q** 18 (marked vertex inside `A`),
**R** 204 (one pentagon only — the two-spoke statement cannot be posed). 159 + 10 + 204 = 373, plus
the 8 Q rows outside the 169 = 381.

## The bound has no linear content (m5, verified here)

A third "no shortcut" result, independent of the other two. Write the row's constraint system as
totalness (one colour per edge), the triangle constraints (`x[e1]+x[e2]+x[e3] <= 2` per colour), and
the row's pins; drop integrality. A feasible fractional point with `U+V = v` is a Farkas witness
that **no** nonnegative combination of those constraints bounds `U+V` above `v`.

m5 exhibits such a point for every row: `U+V <= 89/12` uniformly, with `19/4` on the first published
row and `11/2` on the second, and exactly `0` once the pins are dropped. Judge's check: four rows
re-verified here in exact integer arithmetic — totalness, all 123,424 triangle constraints in all
four colours (colour 3 is the implicit slack), every pin, and the objective — zero violations,
values matching `lp_values.csv`.

So on that relaxation the gap to 19 is at least `139/12` on **every** row, and no dual, weighting or
counting certificate can replace the per-row integral work. Caveat, stated by the author and adopted
here: Turán K5/K6 cuts are not implied by the triangle constraints and these witnesses violate them
off-core, so what is refuted is the linear route over (T),(R),(P) — not the strongest possible linear
relaxation.

## The four rectangles do not transfer (m3, verified here)

The generalisation programme assumed the bundle's four split exclusions could be re-certified row by
row on the same boards. **They cannot.** Sweeping the `(14,5)` board with `U <= 6` over all 159 rows
(15 s each) gives 95 UNSAT with DRAT verified against the regenerated CNF, **2 SAT**, 62 undecided.
The two satisfiable rows are real counters to the obligation as stated:

| row | U | V | board | witness |
| --- | ---: | ---: | --- | --- |
| `12819910` | **6** | 18 | (14,5), 35 vertices | 0 monochromatic triangles, 224/224 pins |
| `f9d26ea9` | **6** | 19 | (14,5), 35 vertices | same |

Judge's check: both witnesses decoded and verified here from the definition with the bundle's own
pin numbering — 595 pairs per witness, 0 monochromatic triangles, 224 pins with 0 mismatches, U=6 in
both. So at least two of the 134 board obligations are false as stated.

Correct scope, as the author states it: this does **not** make `U >= 7` false for the full 58-vertex
rows, and it does not touch the bundle's theorem on its own two rows. It says the obligation on
those rows needs more vertices or a different cut.

## Does the bound bite? No, at 50k conflicts

Paired pilot with and without `U+V >= 19` on four rows: search-effort ratios **0.93, 1.58, 1.13,
0.94**, every run at the conflict limit. At that budget the bound buys nothing, which is a negative
answer to the question that decides whether the 134-board programme is worth buying.

## Where the row-dependence actually sits: the spokes (m7, verified here)

Splitting the 26-vertex core into the **150 A-spoke pairs** and the other **175 pairs**:

| quantity | 159 shape-P rows | all 381 rows |
| --- | ---: | ---: |
| distinct skeleton patterns (the 175) | **6** | 28 |
| distinct spoke patterns (the 150) | **145** | 335 |
| distinct (skeleton, spoke) pairs | 159 | 377 |
| spoke edges pinned to colour 1 | **0** | **0** |

So the skeleton is nearly shared and the spokes carry the row. The practical consequence is
negative: sharing skeletons saves about one and a half percent of the certificate count, so the
~54,000 figure is not an artefact of counting.

The pins are also what closes the branches: on the `(7,11)`, `(10,8)`, `(8,10)` stages, deleting
every spoke pin turns 152 of 204 (cover, skeleton) pairs SAT, and a terminal runs in 0.05 s UNSAT
with its pins against undecided at 300 s without. That half is reported, not re-derived here.

## The 34/35 boundary, and the cheaper route (m4, verified here)

- **34 vertices are not enough.** On the `(13,5)` board — 26-vertex core plus one arm at 13 and the
  other at 5, 34 vertices — `U+V = 18` is attained on **88 of 169 rows** (the other 81 timed out).
  Judge's check: three witnesses decoded and verified from the definition, 0 monochromatic
  triangles, every pin matched, `U+V = 18` in all three. So 35 is the first board size that could
  force the bound.
- All 169 rows also admit `U+V <= 18` on the core *and* on the 27-vertex board (core plus the marked
  vertex with its pins), so no core-shaped certificate can give 19 — this extends m8's statement
  from 159 to 169.
- **The cheaper route, and it is open.** If a 35-vertex `(14,5)` board forces `U+V >= 19` for a row,
  the bound follows from **one instance per row** — at most 134 with containment — instead of
  ~54,000 certificates. Nobody has decided whether that board forces 19: `k=18` and `k=19` on
  `(14,5)` and `k=19` on `(14,14)` resisted nine sat solvers at 45–300 s. m3's counterexample does
  not bear on it, since its witness has `U+V = 24`, which satisfies 19.

## Two stages, not one, fail on the shared relaxation (m6, verified here)

m3 showed the `U <= 6` stage fails on two rows. m6 shows the same mechanism for `(8,10)` in a
sharper form: there is a triangle-free colouring of the 35-vertex `(14,5)` board with **U = 8,
V = 10** — inside the forbidden rectangle — satisfying **every pin that all 159 mark-in-arm-1 rows
share**. Judge's check: model decoded against the global K58 numbering, 0 monochromatic triangles,
the shared-pin set recomputed here as the intersection of the 159 rows restricted to the board
(exactly **146**, equal to the witness's own pin set both ways), 0 violations, U=8 and V=10 counted
from the definition.

So the stage exclusions consume **row-specific** pins; they are not liftable to what the rows have in
common. The author's own batch totals are withdrawn in the report after one receipt contradicted its
ledger entry, and are not counted here.

## What is not established here

- Nothing about whether `U+V >= 19` actually shrinks a row's search. The bundle evidences a 60.4 %
  CPU saving only on the *pilot branches* with the signature ordering, not on a full row.
- Nothing about `U+V = 19` being unattainable; the notes say that is open, and if it fails the bound
  becomes 20 rather than 19.
- The claim is on two rows of 381 in this profile, which is 381 of the 11,585 wall rows. Neither row
  is closed, and `R_4(3)` remains in `[51,62]`.
