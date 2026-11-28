# Three engines on one wall row: stock, square-spoke, colour-resolved

Row `06861a3df60c…` of `(16,16,14,11)`, charge 7 — the top of the wall ranking
(`results/wall-ranking-2026-11-28`). Same row, same machine, one core each.

| engine | instance | budget | verdict |
| --- | --- | --- | --- |
| stock package `run` | the row CNF (134,995 base clauses + units + threshold) | 180 s | **OPEN**, 180 CPU-s |
| updated `square run` | + 960 validated K15 square/matching clauses (32 senders, 31 guarded, 1,000 pairs) | 2,000,000 conflicts | **OPEN_AT_CONFLICT_CAP**, 152 s, 5.95M decisions |
| updated `square run --baseline` | the same CNF without those clauses | 2,000,000 conflicts | **OPEN_AT_CONFLICT_CAP**, 159 s, 5.46M decisions |
| colour-resolved `color-wallcc` | parent augmented to 19,665 vars / 184,779 clauses, 315 cuts, 15 tables, depth 1 → 2 leaves | 60 s and 200k conflicts per leaf | **OPEN (2 of 2 leaves)** |

Both supplied engines are honest about what they do: `square` records
`"certificate_ceiling": "no original-parent UNSAT certificate is produced or inferred"`
and `verify` on the colour run returns `PASS_RUP_DERIVATION` for the augmentation only —
the two leaves stay open, and the run reports `{"counts": {"OPEN": 2}}`.

## What the numbers say

* The square-spoke cut set is real (960 clauses, fingerprinted
  `fa1e8778…`, original parent `90d06e32…`) but at one seed and 2M conflicts it buys
  ~4 % of wall clock (152 s vs 159 s) and closes nothing.
* The colour engine is the only one that produces a *checkable decomposition* of the
  row: a RUP-verified parent plus depth-1 cubes. Its value is not a speedup on the whole
  row but two smaller instances, each of which is still open at 60 s / 200k conflicts.
* Throughput on this row is ~13k conflicts/s, against 22k/s measured on a big-profile
  row — the wall rows are slower per conflict as well as harder.

## What follows

The natural continuation is the colour engine at larger leaf budgets (600 s / 5M
conflicts per leaf, 2 leaves), and the square panel of fourteen rows at 2M conflicts
each — both launched, results appended here when they land.

None of this changes the position: the row is one of 11,585, one of them closing would be
a single row, and the structural statement that would close all of them (no vertex with
two colour-degrees <= 14) remains unwritten.

## The continuations came back negative

**Square-spoke panel, all 14 rows, 2M conflicts each: 0 of 14 closed.** Every row returned
`OPEN_AT_CONFLICT_CAP`, at 114-227 s CPU per row (median 191 s) and a median of 10,468
conflicts/s. That is the complete panel the updated solver ships - two rows per wall
profile, the audited ordinary first-tier walls - and none of them is decided at 2M
conflicts, with the square cuts in place.

**Colour engine, same row, leaves at 600 s / 5M conflicts each: 2 of 2 still OPEN.** The
parent derivation still verifies (`PASS_RUP_DERIVATION`), the split is still into two
depth-1 cubes, and both cubes survive 10x the leaf budget of the first run.

So on this evidence the wall is not a budget problem and not an encoding problem at the
level these two engines operate: the square-spoke cuts shave ~4 %, the colour engine
decomposes correctly but its parts are as hard as the whole, and the panel - which was
chosen by the people who built the square engine as the rows most likely to fall - is
14 for 14 open.

The honest reading: a per-row search is not going to cover 11,585 rows, and the next thing
worth doing is the structural statement, not a bigger cap.
