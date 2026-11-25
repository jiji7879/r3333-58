# Independent audit of the K54 count decomposition (member m7)

Direction d7: *trust-base audit, not search*.  Nothing here is a new cut and no
board is claimed closed.  What follows is a second, independent implementation
of the ground-truth statement and of the count decomposition, used to check the
load-bearing links of the archive.  Everything below was run in this VM with
`build/cadical/build/cadical` (3.0.1) and `build/drat-trim`.

Replay: `sh replay.sh` from this directory (about 2 minutes, plus the order scan).

## What is established (all re-runnable, all hashed)

### A1. The ground-truth encoder is reproduced exactly
`enc.py` builds "a triangle-free 4-colouring of K_order with the board's pins"
from the prose statement only: variable per (free edge, colour), exactly-one per
edge, one clause per (triangle, colour), the two H42 side templates read through
each side's palette, and the crossing pins (bit 0 of `rows[i]` at `j` forces
colour c on `(i,14+j)`).

For all **15** boards in `checkpoints/counted/data/boards.json` and orders
34, 42, 54, the pair (number of variables, number of clauses) equals the pair
produced by the archive's own `checkpoints/counted/src/board.py:graph(k,n,sort=False)`.
Example: local-15 at 54 is 4608 variables / 73108 clauses in both.
Ledger: `work/encoder_crosscheck.json`.

Semantic check on models: every SAT model below was decoded to raw edge colours
and re-checked from scratch (every pin respected, every one of the
$\binom{n}{3}$ triangles non-monochromatic).  Counts of triangles checked:
local-15 at orders 30/34/38/40 = 4060/5984/8436/9880; live-20 at 34/38 =
5984/8436; fresh-07 at 36/38 = 7140/8436.

### A2. The column semantics is reproduced exactly
`semantics.py` re-derives maximal rectangles, the legal ordinary spoke words on
the complement of a rectangle, the class signatures and the column list, without
importing `implied_spokes.py`.  For local-15 it returns **717** columns and for
live-07 **495**, as the *identical list in the identical order* to
`implied_spokes.columns_for`.  For live-14 it returns 675 against the archive's
672: the three extra columns are exactly the ones the archive's cost cutoff
(`total - 25*scale`) discards, and that cutoff is only valid at population 26.
This is a population-dependent filter, not a discrepancy; but column indices of
live-14 must not be reused at smaller populations.

The capacity arithmetic is re-derived independently: with
`LIMIT = {1:16, 2:5, 3:2, 4:1}` and `inside` = number of template vertices
already meeting a class, `sum_class weight*(LIMIT[k]-inside)` equals the stored
`prices['cost']` for all three pilots: **280000** (local-15), **270000**
(live-07), **270000** (live-14), with `scale = 10000`.  With minimum outsider
cost `scale`, population 26 consumes 260000, so live-07 and live-14 have only
**10000** units of slack and local-15 **20000**.

### A3. The witness-pinning clauses are satisfied by real colourings
`audit_relax.py`: for six real colourings (local-15 at 30/34/38/40, fresh-07 at
36/38) and every outsider, every side and every maximal rectangle containing
that outsider's c-support, I compute the column with my own code and then
evaluate **every clause the archive's `ours/cut.py:Instance.pin` and rectangle
generator produce** for it.  1873 instances, **0 violations**.  So the
archive's witness clauses are a genuine relaxation of the graph statement (they
are implied whenever the outsider really realises that column), at least on all
sampled witnesses.  live-06 and live-20 are excluded here: `columns_for` refuses
them (nonzero pole-pair price).

### A4. The four published cuts have no shared-witness gap
A single outsider occupies one rectangle but *both* sides of it, so two cut
literals with the same rectangle and different sides are satisfiable by one
vertex.  The columns of every published cut have **pairwise distinct
rectangles**:

| board | columns | rectangles distinct |
| --- | --- | --- |
| local-15 | 354, 323, 70 | yes |
| local-15 | 354, 323, 69 | yes |
| live-07 | 83, 52 | yes |
| live-14 | 1, 8 | yes |

Hence for these four cuts the witnesses are distinct outsiders in any colouring
and no case split is needed.  (This had to be checked; it is not automatic.)

### A5. Independent rebuilds of the published cuts
`cutcheck.py` rebuilds each instance from `enc.py` plus its own pin clauses:
same variable count, same clause count, own DRAT, all `s VERIFIED`.

| board | cut | vars/clauses | sha256 (first 16) | core | archive |
| --- | --- | --- | --- | --- | --- |
| local-15 | 354,323,70 | 4608 / 73165 | 67aa9b9212033516 | 64 | = `ours/cert-local-15-b.cnf` |
| local-15 | 354,323,69 | 4608 / 73165 | d8c638f8aa67beaa | 64 | not stored |
| live-07 | 83,52(x2) | 4600 / 73004 | b72881d20c0cb4a5 | 80 | stored `7f425873...` differs in 2 clauses |
| live-14 | 1,8(x2) | 4624 / 73601 | 921d3d1f97927a8b | 71 | **byte-identical** to `ours/cert-live-14-a.cnf` |

The live-07 difference is two clauses out of 73004 (literals 420/428 and
817/817+8): one rectangle clause and one class clause, i.e. the stored file
encodes a cell that differs by one anchor vertex from the stated cut
(83,1),(52,2).  Both files are UNSAT with an 80-clause core, so the stated cut
holds either way; the stored file simply is not the instance the stated cut
regenerates.  Worth knowing, not a soundness problem.

### A6. Independent rebuilds of the cell (single-column) bounds
`units.py` uses the *two-sided* cell test (two distinct outsiders confined to
one rectangle on both sides, left signature fixed to the rectangle's unique left
column): a two-witness UNSAT gives `count_k <= 1`.  All UNSAT, all verified:

| board | column | claim | vars/clauses | sha256 (first 16) | core |
| --- | --- | --- | --- | --- | --- |
| local-15 | 319 | count <= 1 | 4608 / 73160 | a63f4fd1ed7a15a5 | 25 |
| local-15 | 321 | count <= 1 | 4608 / 73162 | 2bcb4f7391339306 | 27 |
| live-07 | 89 | count <= 1 (stated) | 4600 / 73010 | 1a7ed678fdfd7858 | 131 |
| live-07 | 269 | count <= 1 (**stated only <= 3**) | 4600 / 73006 | 6ce6570231f540df | 27 |
| local-15 | r=11835,sig=1 | scan row | 4608 / 73158 | 12ef307972786900 | 25 |
| local-15 | r=8507,sig=8 | scan row | 4608 / 73162 | 0315ae62761e6491 | 25 |
| local-15 | r=11769,sig=2 | scan row | 4608 / 73156 | 4b0f3f17f8fb6c70 | 25 |

`count_269 <= 1` is strictly stronger than the archived `count_269 <= 3` (chain
length 12); the outer model may safely take the stronger bound.

## The measured obstruction to direct truncation (negative result, with numbers)

A colouring of K54 with the pins restricts to one of K_n for every n <= 54, so
UNSAT at any order <= 54 closes the board, and *nothing at order 54 can be
easier than at its threshold order*.  Measured frontier (cadical unless stated,
seconds in brackets; full CNFs kept in `work/`):

| board | 30 | 34 | 36 | 38 | 40 | 41 | 42 | 54 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| local-15 | SAT | SAT | | SAT (0.5) | SAT (45) | OPEN (90) | OPEN (100) | OPEN (archive, 250k conflicts) |
| live-20 | | SAT | | SAT (0.1) | OPEN (25) | | OPEN (25) | |
| fresh-07 | | | SAT | SAT (1) | OPEN (25) | | OPEN (25; 300 s kissat; 90 s with outsider-lex) | |
| other 11 open boards | | | | | | | OPEN (25-30) | |

So the satisfiability threshold of these pinned instances sits at **13-14
outsiders (orders 41-42)**, and every one of the 14 open boards is already at or
past it at order 42.  Consequences:

* the "just use fewer outsiders" route to a board closure is dead: the easy
  orders are SAT (verified witnesses at 38-40) and the UNSAT orders are the hard
  ones, 42 being already at the wall;
* any board closure must either settle order 41/42 (still OPEN: 100 s cadical,
  300 s kissat, both fail) or go through the 26-outsider count decomposition.

The CNFs at every order used here are in `work/`, so another member can attack
order 41/42 with a different solver without rebuilding.

## What is NOT done

* **No board is closed, and no new cut is claimed.**  The frontier at order 41
  and 42 is OPEN, not refuted.  Budget exhaustion is not evidence.
* The relaxation lemma of A3 is *sampled*, not proved.  The general statement
  ("every real colouring satisfies the clauses of every column it realises") is
  a clause-by-clause reading of `Instance.pin`, and I checked 1873 real
  instances of it; I did not machine-check it for all witnesses of all columns.
* The coverage keystone beyond A3 is **not** re-verified: nothing here checks
  that induced counts satisfy the outer CNF's capacity clauses, weight bounds,
  population or rectangle balances, nor the class-capacity Ramsey bounds
  themselves.
* 75 of the 256 rows of `ours/capacity-local-15.json` are UNKNOWN at the
  archive's 30000-conflict budget, so those cells remain uncertified.
* The 44 loop cuts of the previous swarm were not rebuilt here.
* The two boards with nonzero pole-pair price (live-06, live-20) are outside the
  reach of the column semantics audited here.

## Addendum: the whole capacity base of local-15, and a cube split at the frontier

### A7. All 181 certified cells of local-15 rebuilt independently
`capacity_all.py` rebuilds every row of `ours/capacity-local-15.json` whose
archive verdict is UNSAT (181 of 256; the other 75 are UNKNOWN at the archive's
30000-conflict budget).  Each is the two-sided cell instance of A6, built from
`enc.py` + `semantics.py` only.  Result: **181/181 UNSAT, 181/181 DRAT
`s VERIFIED`, 181 distinct CNF hashes** (recorded in
`ours/capacity_all.json`, proofs `ours/cap-<rect>-<sig>.drat`).  The CNFs are
deleted because they are a deterministic function of `(board, rect, left_sig,
right_sig)` through `cellcheck.build`; the hashes pin them.

### A8. Cube split at order 42 (negative, reported as OPEN)
`cube.py` splits on the colours of three outsider-outsider edges
(28,29), (30,31), (32,33): 4^3 = 64 exhaustive cubes.  fresh-07, order 42,
10 s per cube, 3 workers: **64/64 OPEN**, nothing settled
(`ours/cubes-fresh-07-42.json`).  Combined with the order scan this says the
difficulty at the frontier is not an artefact of one search trajectory.
No claim either way about fresh-07 at order 42.
