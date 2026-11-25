# What closing a board buys for seed 12, and which strengthenings actually transfer

Member m2, direction d6 (seed-level dependency).  Everything below was computed here from
the archive read-only; every UNSAT is a DRAT file that `build/drat-trim` accepts.

Two claims are separated throughout:
* **claim (b)** = one board excluded (a fixed 14x14 crossing pattern cannot be realized);
* **claim (c)** = a seed excluded (no counterexample in that seed).

## 1. The 72-board sample is not a cover of seed 12 (verified)

Reproduced independently of `checkpoints/counted/src/orbits.py` by direct enumeration of
the group orbits on coloured blocks (`orbit_check.py`, 108 s):

| object | count |
| --- | ---: |
| rooted H42/H42 placements of seed 12 (`data/placements.json`) | 24 |
| marked non-pole 2x2 crossing blocks, 24 x 6084 | 146,016 |
| blocks up to the placement stabiliser | 59,925 |
| triangle-free colourings of those blocks | 7,300,917 |
| colour orbits (seed-12 leaves of the archive's split) | 2,809,638 |

This matches `results/orbits.json` and the counted checkpoint exactly, placement by
placement, and each orbit family was checked to partition its raw set (`orbit_check.json`).

**A leaf fixes four non-pole crossings.**  A board pins far more: over the 72 boards the
*binary* pattern already fixes 27 pole-star cells and **66 to 96** further cells to c
(`census.py`; the sparsest is live-14 at 66, the densest fresh-18 at 96).  A board
refutation is a statement about the up-set {colourings whose c-set contains pins(b)}; a
leaf forces 4 cells to *ordinary* colours and leaves the other 165 free.  Hence

* no leaf of the split implies any board's pin set, so **0 of the 2,809,638 leaves are
  covered by any of the 72 boards**, closed or open;
* the all-but-pole-stars-ordinary colourings (c-set empty on non-pole cells) lie in no
  board's up-set at all, so no family of board refutations, however large, can discharge
  that branch.

**The count machinery has no leverage on a leaf either.**  Maximal free rectangles (exact,
price-independent, `leafmodel.py`):

| instance | maximal rectangles | count-model columns |
| --- | ---: | ---: |
| pin-free (pole stars only) | 1 | 2 |
| a seed-12 leaf (4 ordinary cells) | 2 | 4 |
| the 58 closed boards | 31-136 | 104-448 |
| the 14 open boards | 68-167 | 236-717 |

So a board's count model is 60-180 times larger than a leaf's, and the leaf's is vacuous
(4 unary columns against a population of 26).

**Answer to the direction's question.**  Which of the 72 boards are load-bearing for seed
12: **none**.  Closing the 14 open boards would change the sample's ledger from 58/72 to
72/72 and would not remove one leaf of seed 12's coverage, i.e. not one claim-(c) step.
That is a statement about proof architecture, not about the value of the work: an open
board is the cheapest place to *develop* an argument, because it carries the most pins.

Frontier, exact (`pinmap.py`): the 14 open boards are the sparsest-pinned ones.  Boards
with at most 72 non-pole c-pins are open (11 of 11); boards with at least 78 are closed
(51 of 51); the band 73-77 contains 7 closed and 3 open (local-17 at 73, live-20 at 75,
fresh-07 at 77).  Pin density, not size, tracks
solvability.

## 2. Statements that do transfer: pin-free cell capacities

A pinned board is the same two H42 copies with extra cells forced to c.  Every colouring
of the pinned graph is a colouring of the pin-free graph, so

> **Monotonicity.**  An UNSAT proof for the pin-free placement (two H42 copies, poles 2 and
> 2, pole stars c, all other crossings free) is an UNSAT proof for *every* board of that
> placement and for *every* leaf of the seed-12 split.

A cell is (side, spoke colours at named vertices).  The tables here are for the placement
with poles (2,2) and *identity ordinary palettes on both sides*, which is exactly local-15's
placement; a board with a non-identity side palette (live-07 has (1 2) on the right, live-14
(0 2)) needs its own scan, because a palette relabelling of one side's internal colours is
not an automorphism of the H42/H42 pair with free crossings.  The archive's cell bounds are
the two-colour Ramsey numbers 16/5/2/1.  Their exact
pin-free values (`scan_caps.py`, `scan_cells.py`; every bound certified):

* **two-spoke cells, 936 of them:** capacities 1, 2, 3, 4, 5 for 88, 24, 488, 280, 56
  cells.  Total 3000 against the Ramsey total 4680, a **36% overcount**.
* **three-spoke cells, 3432 of them:** 160 cells hold **no** outsider, 1920 hold at most
  one, 1352 hold two.  Total <= 4624 against 6864, a **33% overcount**.
* **one-spoke cells, 78 of them:** 10 have capacity 6, not >= 7; the rest reach 7.

All of these hold with the pole stars only, so they are valid clauses for every board and
every leaf.  A single concrete case, certified as a DRAT-verified lemma rather than a
capacity scan:

> **Lemma.**  With poles 2 (left) and 4 (right), no two distinct outside vertices can both
> have colour 0 at right vertex 26 and colour 1 at right vertex 16.
> CNF `lemma-poles24-c26-0-c16-1.cnf` sha256 `ab56a67b8a4b6d8f7a56c62cf13eb0b3699e43bd1a14088a937df5ec9ae50901`,
> DRAT `lemma-poles24-c26-0-c16-1.drat` sha256 `ea015bbd1d14efb5a08f2142cef74634b6c862af420344b84fcc785664f17134`,
> `drat-trim` prints `s VERIFIED`, exit 0.  The archive's bound for that cell is 3.

## 3. Measured negative: capacities are not the missing joint constraint

The archive's cell bounds already subtract occupants inside the side, which absorbs most of
the slack.  For local-15's outer CNF (4758 classes, `need-local-15.json`) the exact
capacities sum to 9406 against the archive's 9642, a **2.4% reduction**; applied as
at-most clauses over the unary chains (`apply_needed.py`) they sharpen 87 classes and leave
the model **SAT** (`need-applied-local-15.cnf`, sha256 `b7f300f3c574e1a7...`).  Sharpening
every two- and three-spoke cell of that placement alone is therefore not enough to close
local-15, and the two-anchor Ramsey bounds are not the weakness the marginal model suffers
from.  The joint obstruction has to come from the interaction of distinct columns with
distinct witnesses, not from a tighter per-cell count.

## 4. What this says the swarm should do

* A cut whose validity proof survives removing all non-pole pins is worth 24 placements and
  all 2.8M leaves; a pinned cut is worth one board.  The cheap test is: rebuild the same
  two-witness instance with only the pole stars fixed (`pinfree_test.py`,
  `locate.py` do this in a second).
* Everything closed through pins should be reported as claim (b) for that board, never as
  seed progress, and the seed-12 ledger should stay "0 of 24 placements refuted, 0 of
  2,809,638 leaves discharged".

## Files

`census.py`, `pinmap.py`, `leafmodel.py`, `orbit_check.py`, `scan_caps.py`,
`scan_cells.py`, `scan_needed.py`, `apply_needed.py`, `pin_free` tests `pinfree_test.py`
and `locate.py`, lemma `lemma_pair.py` with `lemma-poles24-*`.  Data: `boards_census.json`,
`pinmap.json`, `leafmodel.json`, `orbit_check.json`, `caps-22.json`, `caps1-22.json`,
`caps3-22.json`, `need-local-15.json`, `need-applied-local-15.json`, `lemma_pair.json`.
