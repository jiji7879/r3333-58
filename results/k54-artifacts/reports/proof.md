# live-16: the integer count model is FEASIBLE

Member m6, swarm smwn8rsmo, direction d3. Job B, board **live-16**.

## Result

The integer count model of board `live-16` **is feasible**: an explicit integral vector
satisfying (C0) bounds, (C1) per-rectangle balance, (C2) left population 26, (C3) every
anchor-class capacity and (C4) every price lower bound exists and has been verified three
independent ways. Hence **live-16 cannot be excluded by the count-model route**; on that
route it must be dropped from the undecided list.

The whole certificate is: `work/witness-live-16.json` (52 columns, each count 1) plus
`work/replay.py`. No solver is needed to check it.

## What is and is not claimed

* (a) a fixed count vector is unrealizable — not claimed;
* (b) a board is excluded — **no; the opposite is proved**: the counting mechanism cannot
  close live-16. Nothing here says live-16 is realizable as a colouring;
* (c) a seed is excluded — nothing.

## The model (as re-derived from the archive, not from the handoff's ILP)

Sources (all match `work/k54/SHA256SUMS` and `checkpoints/counted/SHA256SUMS`):
`checkpoints/counted/data/{h42.json,boards.json,prices/live-16.json}` and
`pilot/{implied_spokes,price_cover,make_pilot_cnf}.py`.

* 12216 count columns `k = (maximal rectangle, side, spoke signature)`; column `k` appears
  at position `k` of `price_cover.instance('live-16')[0]`.
* 90 maximal rectangles -> 90 balance rows; 5239 anchor classes, which collapse to **3782
  distinct row index sets** (exactly `ilp.py`'s `ncaps`); 0 price rows have a positive
  lower bound, so (C4) is vacuous for this board (as the handoff's table says).
* (C0): `x_k <= min(26, caps of the classes of k)` — the unary-chain length of
  `make_pilot_cnf.py`.
* The search (not the proof) solved: 12216 nonnegative integer columns, 3872 rows
  (90 balance + 3782 caps), 648118 nonzeros, maximising the left population. (C2) was *not*
  imposed: the incumbent reaches left total 26 on its own, and balance then forces right
  total 26.

## The witness

`work/witness-live-16.json`: 52 columns with count 1 each, 26 on the left and 26 on the
right, spread over 23 rectangles (20 rectangles with 2 pairs, 3 with 4 pairs), no
empty-signature ("free") column used.

Support (column indices): 877 983 1459 1637 2039 2149 2593 2683 2731 2800 2914 2922 3602
3790 4251 4282 4489 4678 5335 5556 5844 5975 6089 6112 7240 7314 7886 8018 8108 8184 8607
8651 9122 9217 9276 9288 9885 9984 10019 10051 10095 10239 10726 10736 11216 11275 11285
11288 11496 11603 11742 11782.

## Verification

1. **Exact integer arithmetic** (`work/verify_exact.py`, also inside `replay.py`): rebuilds
   the columns, per-column class terms, the 3782 distinct class rows and their caps from the
   archive data and checks C0, C1 (all 90 rectangles), C2, C3, C4 with Python integers.
   Result: 0 violations, population left/right `[26, 26]`, support 52, max count 1.
2. **Definition level** (`work/verify_defs.py`): does not use `price_cover.instance` at all.
   It regenerates every implied anchor class from `implied_classes(forced_spoke_masks)` and
   the capacity `LIMIT[len(anchors)] - #{template vertices realising all anchors}` from
   `h42.json`. Result: 2092 occupied classes, 0 capacity violations, 0 unbalanced
   rectangles, left total 26.
3. **The archive's own count CNF**: `pilot/make_pilot_cnf.py live-16` gives
   3,816,422 variables / 8,237,447 clauses — exactly the instance quoted in the handoff.
   Fixing the 13015 unary chain variables to the witness satisfies 3,817,740 clauses
   outright, falsifies **0**, and leaves 4,419,707 binary clauses over the cardinality
   auxiliaries; CaDiCaL (archive `build/cadical/build/cadical`) returns **rc 10, SAT** on
   that residual, so the full CNF is satisfiable under the witness.
4. **Negative controls (sensitivity of check 3)**: the same procedure with (i) one extra unit
   on a left column of a used rectangle (breaks a balance) and (ii) one extra unit on a
   column of a class that is exactly saturated plus its rectangle partner (breaks a class
   cap) both return CaDiCaL **rc 20, UNSAT**. The frozen-CNF check therefore does detect
   violations.

## How it was found (not part of the proof)

`scipy.optimize.milp` (scipy 1.18.1, HiGHS) on the 12216-column integer system above,
presolve on, `mip_heuristic_effort=0.5` (passed through to HiGHS verbatim, since scipy does
not know the name). The run that produced the witness had time limit 280 s and finished with
status `1` (time limit reached) and an **integral incumbent**, left total 26. Incumbent
quality over time: 45 s -> left 17, 90 s -> left 25, 280 s -> left 26 (the witness). Without
the heuristic option a 10 s and a 30 s run had no incumbent yet. Peak RSS of model+search:
348 MB (measured on a 20 s run: 348456 kB). Two heuristics were tried first — a randomised
pair-greedy and a min-conflicts local search over 26 (left, right) pairs — and stalled at 18
and 20 pairs; recorded because they show that a heuristic stall here means nothing, and that
an OPEN would not have been evidence.

## Reproduction

```sh
cd .ultramath/smwn8rsmo/m6
python3 work/replay.py --cnf work/cnf/live-16.cnf.gz     # exact + definition + CNF checks
python3 work/replay.py --solve                            # optional: re-run the HiGHS search
```

`work/cnf/live-16.cnf.gz` is rebuilt (outside the archive) with

```sh
cd <archive>   # work/k54
PYTHONDONTWRITEBYTECODE=1 python3 pilot/make_pilot_cnf.py live-16 <this dir>/work/cnf
```

## Hashes

| file | sha256 |
| --- | --- |
| `work/witness-live-16.json` | `0a8b2809b9726361f48bc9432bae5f0b3707f7984b99754d7af7963985dcb1fc` |
| `work/ilp_solution.json` | `8bdff75ab08a9ea2ff420be5d5fe79b0808d3bc9ef5eb1ccea91c8c68f0e1882` |
| `work/cnf/live-16.cnf.gz` | `780ff537d73ba2701a4844b5f1e9af382c9900deb8a850cb1b2e8b678c2380e8` |
| … uncompressed | `967fb55ec45b05153e636fe841734dc11bfd78e3bedbcf33cf7837671d8519e4` |
| `work/cnf/live-16.counts.json` | `b8ae6dea753de067c7862d9c088943a5bcb31918f30c0f84c90ab3972f1fd411` |
| `work/verify_exact.py` | `12e1741c123291adf823ebf2258aa57fffab43400fc6973d1995631c890b6773` |
| `work/verify_defs.py` | `c48326da7f41d3fba5a4dcdd96ce2c4a6d59d947160c35cebdc052a830e3c981` |
| `work/replay.py` | `7f72de5a4ad447d94fe0c87cf1093d90e4a28d46e36f56fe06b83c03c2e1a272` |
| `data/h42.json` | `eb9c7864946230b0ddbcdf72b0dd68666f9e45725e5d547e7c5acc9ac9445136` |
| `data/boards.json` | `ec0694f4a351ad2c8c95ffb48d4ab8cf9b0994f7f0f412f9d85a13685f74a48b` |
| `data/prices/live-16.json` | `9050500274ecf0f79a2478d2cadfa91cccb8cee7cb58c323ead91f38e4a283fe` |

## Limitations

* The model is the archive's; I re-derived its constraints from the definitions and matched
  the archive's own CNF, but I did not re-verify the "every triangle-free 4-colouring
  induces such counts" implication. If that implication were wrong, a count-model
  infeasibility would carry no exclusion power either — the implication is not my claim.
* Feasibility of the count model says only that this refutation route fails on live-16; it
  says nothing about whether live-16 is realizable.
