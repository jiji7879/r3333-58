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
