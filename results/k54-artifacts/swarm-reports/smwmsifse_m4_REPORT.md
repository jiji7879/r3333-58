# d8 — mining the live-17 exclusion mechanism, and where it does *not* fire

Member m4, swarm smwmsifse. All work in this directory. Archive read-only at
`/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/work/k54`.

## What was mined

Of the 58 closed boards, 57 were closed by nonnegative *class weights* (capacity
counting). The 58th, `live-17`, was closed by *integrality*: the archive's
`checkpoints/counted` gives a 29-node arithmetic tree over integral counts or
integral rectangle row sums, plus two DRAT refutations of a 124,959-variable CNF.
That integrality mechanism is the only part of the closed corpus that is not
already proved exhausted for the open boards by the archive's fractional packings
(`checkpoints/twins/run/dual-*.json`, mass 26.02–27.08 > 26, weak duality).

So the question I asked: **is the live-17 mechanism reusable — does "class caps +
balance + population 26 + integral rectangle row sums" already exclude any of the
13 zero-pole-pair-price boards?**

## Method

1. `pilot/make_pilot_cnf.py` encodes the strengthened count model as a CNF. I
   re-encode its *integer core* (`ilp.py`): x_k >= 0 integer per column
   (rectangle, side, signature), with
   (C0) x_k <= min(26, caps of the classes of k),
   (C1) per rectangle  sum_{left} x_k = sum_{right} x_k,
   (C2) sum_{left} x_k = 26,
   (C3) per class sum <= cap (identical index sets merged, minimum cap),
   (C4) the price lower bounds LIMIT[#anchors] - inside - slack//w.
2. `rowsum.py` relaxes x to continuous and keeps only the per-rectangle totals
   n_r integral (this is exactly the branching the archive used for live-17).
   **Infeasible here => the count model has no integer solution => the board is
   excluded by counting alone** (given the archive's Lean coverage keystone).
3. `bb.py` is an independent depth-first branch and bound on the n_r, pruning by
   LP infeasibility, so live-17's exclusion can be re-derived without DRAT and
   without the 124,959-variable encoding.
4. `witness.py` builds integral count witnesses (exact integer verification).

## Faithfulness checks (these are the load-bearing ones)

* `python3 arc/pilot/make_pilot_cnf.py local-15 out` reproduces the archived
  `pilot/cnfs/local-15.cnf.gz` **bit for bit**
  (`gzip -dc | sha256sum` = `c7e5a30c39977cdf87472cde292dcdf6c6626bc3fd85dcab686fb48b873bb252`,
  identical `counts.json`). So my copy of the generator and the data is the
  archive's.
* Decoding the CaDiCaL model of `out/live-07.cnf.gz` into counts x_k
  (`proof/live-07.sol`, `out/live-07.counts.json`) gives a vector that satisfies
  **every** constraint of my integer system: balance 80/80 rectangles, 0 class
  cap violations, population 26 + 26, 0 price violations. The integer encoding is
  therefore a faithful image of the CNF's constraints (I also checked the
  chain-length/balance coding: `bound(a + [-v for v in b], len(b))` is exactly
  `sum_a x = sum_b x` because `len(b)` counts the *literals* of side b).
* The three pilots come out feasible, as the archive says, and `live-17` comes out
  infeasible by two independent methods. Controls behave.

## Results (13 covered boards: the zero-pole-pair-price ones)

| board | columns | classes | caps | price rows | row-sum relaxation | archive |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| live-07 | 495 | 3178 | 410 | 6 | FEASIBLE (16 nonzero rows) | open |
| live-14 | 672 | 3328 | 480 | 6 | FEASIBLE (18) | open |
| local-15 | 717 | 4758 | 698 | 7 | FEASIBLE (15) | open |
| live-17 | 2473 | 5256 | 3291 | 65 | **INFEASIBLE** | excluded |
| live-13 | 12110 | 6313 | 3943 | 1 | FEASIBLE (25) | open |
| live-16 | 12216 | 5239 | 3782 | 0 | FEASIBLE (25) | open |
| local-20 | 8539 | 4613 | 2800 | 5 | FEASIBLE (23) | open |
| live-22 (=local-22) | 10800 | 5781 | 3261 | 1 | FEASIBLE (24) | open |
| local-24 | 12911 | 7172 | 4272 | 0 | FEASIBLE (26) | open |
| fresh-07 | 8619 | 7203 | 4344 | 1 | OPEN at 280 s (`--indicators`) | open |
| live-02 | 10917 | 5869 | 3333 | 12 | OPEN at 280 s (`--indicators`) | open |
| local-09 | 18475 | 8096 | 4782 | 0 | OPEN at 150 s | open |
| local-17 | 14050 | 8070 | 4707 | 0 | OPEN at 150 s | open |

`--indicators` adds the valid inequalities n_r <= 26 z_r, sum z_r <= 26,
sum_r n_r = 26 (at most 26 rectangles can be non-empty); it decided local-20,
which was OPEN without them. Same `SUMMARY.tsv` table, machine readable.

Also relevant: the LP maximum population with (C2) removed is 27.0 / 27.0 / 28.0
for live-07 / live-14 / local-15, 26.10 for live-17, 26.65 for fresh-07, 26.56 for
live-02, 29.54 for live-16 — i.e. the LP relaxation is never the obstruction; only
integrality can be, and for the open boards tested it is not.

## Claims, separated

1. **A fixed count vector is unrealizable** — not claimed here; nothing new.
2. **A board is excluded** — no new board is excluded. The row-sum relaxation is
   feasible for the 8 decided open boards, so this mechanism provably cannot
   close them; for the 5 OPEN ones nothing is claimed (OPEN, not refuted).
3. **live-17 is excluded** — reproduced independently (HiGHS: infeasible; my own
   B&B: INFEASIBLE, 41 nodes, 21 infeasible leaves, 59 rectangles). This rests on
   the archive's own board data and its Lean coverage keystone, which I did not
   re-run.
4. **A seed is excluded** — nothing claimed.

## Reproduction

```sh
# count-model CNFs for any zero-price board (reproduces the archived CNF for the three pilots)
python3 arc/pilot/make_pilot_cnf.py local-15 out          # 201049 vars / 407864 clauses
gzip -dc out/local-15.cnf.gz | sha256sum                  # c7e5a30c...873bb252

# integer core, row-sum relaxation, B&B
python3 ilp.py   live-17 --timelimit 240                  # INFEASIBLE
python3 rowsum.py live-16 --timelimit 120                 # FEASIBLE, prints row sums
python3 rowsum.py local-20 --timelimit 330 --indicators    # FEASIBLE (valid ineqs)
python3 bb.py    live-17 --seconds 150                    # INFEASIBLE, 41 nodes
python3 bb.py    live-07 --seconds 150                    # FEASIBLE, 1 node
python3 witness.py local-15 --out out/w-local-15.json     # integral witness

# faithfulness: decode a solver model of the count CNF
bin/cadical -q -w proof/live-07.sol out/live-07.cnf.gz    # SAT, rc 10
python3 check_model.py                                    # balance/caps/population/price = 0 violations
```

`bin/cadical` and `bin/drat-trim` are copies of `build/cadical/build/cadical` and
`build/drat-trim`. `arc/` holds copies of `pilot/{make_pilot_cnf,price_cover,
implied_spokes}.py` and `checkpoints/counted/data/{boards,h42,placements}.json`
plus `data/prices/*.json` (15 files), unmodified.

## Dead ends recorded

* A first version of the row-sum relaxation put all columns of a rectangle in one
  row (`sum_L + sum_R - |cols| n_r = 0`), which spuriously made all nine untested
  boards infeasible. With one row per side (`sum_L = n_r`, `sum_R = n_r`) seven of
  them are feasible and live-17 stays infeasible. Anyone reusing this: check the
  row layout against the `n_r` semantics before believing an INFEASIBLE.
* HiGHS MIPs on the full integer system (8k–18k integer columns) do not decide
  within 300 s; the row-sum-only relaxation is the tractable projection.
* My own B&B is much slower than HiGHS per node on the 12k-column boards (20 s per
  LP), so it is only used as an independent check on the two small boards.
