# Singleton perfect balance: the codegree-14 cases on K58

Session of 2026-11-24, from the incoming handoff
`attachments/see-what-you-can-yel5/K58_PB_parallel_handoff.md` (David Lai's
project), plus swarm `smwu1nsf3`.

> **`R_4(3) in [51,62]` has not moved.** Closing all four cases below gives
> "max red codegree <= 13" only inside the singleton-perfect-balance branch, and
> that branch still has the 25 overlap-13 alignments and the lower strata behind
> it. Three of the four cases are still open anyway.

## The claim and the reduction

Call a colour *critical* at a vertex of a 4-colouring of `K58` if its degree there
is 15 or 16. "Singleton perfect balance" = red is the unique critical colour at
every vertex: red degree in {15,16}, blue/green/yellow at most 14. The claim is
that the maximum red codegree is at most 13.

If a pair `u,v` attains 14 common red neighbours with `uv` blue, the handoff
reduces the case to four pinned 20-vertex structures (two private labels each
side, 14 shared sites, two roots) times `t in {1,...,5}` for the 38 outside
sites: 20 children. Instance specification and the encoder are `tools/pb/`.

**Audited** (`smwu1nsf3/m5`, accepted): both roots are forced to degree table
(16,13,14,14) by an equality-case argument that needs only `R(3,3)=6` — inside
`v`'s 13-site blue arm, `u` has at most 5 green and 5 yellow neighbours, red *is*
allowed there, so `b_v - 1 <= (r_u - 14) + 5 + 5 <= 12` while `b_v >= 13`. All
four opposite spokes are then blue. The cell table, `0 <= t <= 5` and the
impossibility of `t = 0` are confirmed. Unmatched private edges have exactly the
two advertised colours in all four rows. What the audit **cannot** check here is
the handoff's own census — "exactly four surviving 14-overlap alignments" — since
the companion archive and `check_common.py` were not supplied. That remains an
explicit premise.

## The lever: nine footprints

A shared site `z` has its only fixed red neighbours at `u,v`, so its red chart is
a triangle-free 3-coloured `K15` or `K16` containing the blue edge `uv`. Two
independent routes give the same answer:

* Kalbfleisch-Stanton 1968 p.19 (two `K16` colourings) and Heinrich 1977
  Theorem 2, J. Austral. Math. Soc. Ser. A 24, 465-495, DOI
  10.1017/S1446788700020838 (exactly two `K15` colourings, each a `K16`
  colouring with one vertex deleted); with the verified fact that every blue edge
  of either `K16` template has the same footprint (`tools/pb/footprint.py`), the
  footprints are the full table and the full table minus one unit in one of the
  8 positive cells.
* `smwu1nsf3/m6` and `m8`, classification-free: enumerate the 60 (order 16) and
  432 (order 15) count matrices obeying the total and Heinrich's per-vertex
  degrees {5,5,5} / {4,5,5}; 449 die arithmetically, 34 fall to replayed DRAT,
  9 survive charts. `m6/check_footprints.py` replays in this repository.

    FULL = [[0,2,2],
            [2,2,1],
            [2,1,2]]      (rows: colour to u, columns: colour to v)

so a shared site has two red neighbours in each of the four mixed 5-cells and in
`GG`, `YY`, one in `GY`, `YG`, and none in `BB` — or that with one unit removed.

## What is closed

**The half where all 14 shared sites have red degree 16**, for all four rows and
all five `t`, twice over (strength 1 and strength 3): **40 of 40 instances UNSAT,
every DRAT proof replayed to `s VERIFIED` against the same CNF** - median 29 s,
max 102 s, whole sweep 45 min on a loaded 4-core VM. `tools/pb/sweep_all16.py`
regenerates it. Ledger: [all16-ledger.tsv](all16-ledger.tsv)
(sha256 `c5d08af238435fffa5db506d73fc22535734af27dbf2f33c9d154938b60c1bfd`),
columns `row, t, strength, status, cnf_sha256, proof_bytes, proof_sha256,
checker, seconds`.

Stronger than that: this half already follows from the **degree laws alone**. The
instance with (L2) triangles and (L4) codegree dropped is still UNSAT (0.9 s,
1514-clause core). So the content is arithmetic, not combinatorial — which is why
it is cheap. It is also why it says nothing about the other half.

## What is open

The complement — **some shared site has red degree 15** — and the mixed cases.
`tools/pb/encode.py --strength 3 --fp15` is the complete child (all nine
footprints wired in, no case split), and it is undecided: Kissat 4.0.4 at 900 s
and then 3000 s, CaDiCaL 195 in parallel. Sanity ladder for that encoding:
`--strength 0 --fp15` SAT, `--strength 1 --fp15` SAT (1.7 s), full undecided.

Two things learned about the search, both measured. (a) The footprint clauses are
*expensive*: `--all16 --fp15` did not finish in 600 s while `--all16` without
them closes in 20 s, so the nine-footprint block buys pruning at a large cost in
auxiliary variables. (b) The degree-15 sites cannot be isolated by counting:
under the degree laws plus the footprints, every one of the 14 shared sites can
individually be the degree-15 one (14/14 SAT, 4-7 s each), and so can every
sampled pair (6/6 pairs SAT). So there is no cheap "at most one" split; a host
with several degree-15 shared sites is not excluded at the degree level.

**Dead route, so it is not retried.** The repeated-pentagon triple cannot give a
codegree contradiction: for a yellow pair `a,b` in a mixed cell and three shared
sites using it, the three charts share `{u,v,a,b}` with fixed colours, and
enumerating all 35 triples of full-chart word families gives a maximum of 7
disjoint forced-red slot triangles (`smwu1nsf3/m6` f6). That yields only
`max codeg(z_i,z_j) >= 7` against the 15 needed. The prior
`.scratch/K58_repeated_pentagon_codegree` argument is a different profile and
does not transfer.

`smwu1nsf3/m6` additionally emits a sound covering split: 1,128 branch graphs,
5,640 strengthened branches over the 20 children, audited independently
(`check_cover.py`: every one of the 29,120 raw block/triple choices mapped,
multiplicities `2*(triple orbit size)`, symmetries checked against the pins).
No branch is decided. That is the remaining obligation.

## Traps hit while building this (both produced a false 0.2 s UNSAT)

1. Auxiliary variables allocated from `4*C(58,2)+4` while the edge variables run
   to 13224: every cardinality encoding overwrote edge variables.
2. In the footprint block, cell *vertices* passed where edge literals belong, so
   the instance was UNSAT with only (L1) and the pins.

Any CNF from this line must have its header above 13224 and must be SAT at
`--strength 0 --fp15`. Both are now asserted in `tools/pb/NOTES.md`.

## Handover: how to finish this

Reproduce everything from the repo root:

```bash
python3 tools/pb/footprint.py                      # the footprint of one blue edge, both templates
python3 tools/pb/encode.py TT_d02 3 x.cnf --strength 3 --fp15   # the complete open child
python3 tools/pb/encode.py TT_d02 3 y.cnf --strength 1 --all16 --no-footprint  # the closed half
python3 tools/pb/sweep_all16.py .scratch/pb/all16  # 40 instances, ~36 min on 4 cores
python3 tools/pb/check_matrix.py ROW T MATRIX.txt  # any claimed host, from the definition
```

Sizes, so the next person does not have to measure them again: 58 vertices, 1387
free 4-way edge variables, 2,406,235 clauses and 1,092,138 variables at
`--strength 3 --fp15`. Kissat 4.0.4: undecided at 900 s, at 3000 s (530 MB of DRAT emitted before the
cap, so no closure was near), and with `--sat --seed=2` and `--sat --seed=7` at
1500 s each; CaDiCaL 195: undecided at 45 min. The incomplete proof traces were
deleted - a timed-out DRAT is not evidence of anything. The machine was
shared with six other solver processes throughout, so those are lower bounds on
wall time, not measurements of difficulty.

Four concrete routes, in the order I would take them.

1. ~~**Cut (L4) out of the search** and put it back by CEGAR.~~ **Tried, and it
   does not work: the hardness is in (L2), not (L4).** `tools/pb/cegar.py` solves
   the child with (L1)-(L3) only, reads the red neighbourhoods out of the model
   and adds blocking clauses for the pairs that actually exceed 14. Its very
   first solve - 627,935 clauses, 257,556 variables, no codegree constraints at
   all - did not finish in 900 s. Measured ladder on the same child:

   | laws kept | result |
   | --- | --- |
   | (L1),(L3): degree laws + footprints | SAT, 1.7 s |
   | (L1),(L2),(L3): + triangle-freeness | **undecided at 900 s** |
   | (L1)-(L4) | undecided at 3000 s |

   So the mixed case is hard because it asks for a triangle-free 4-colouring of
   the 38 free vertices under near-regular degrees - the original problem in
   miniature - and not because of the codegree constraints. Any future attempt
   should attack (L2) directly, or find a structural reason why (L2) cannot hold
   with a degree-15 shared site.
2. **Cube on the five-cells.** At the start the only couplings between the 14
   shared sites are the outside vertices themselves, so the 8 cells' reduced-cell
   selectors interact weakly. A cube over the four mixed cells' choices is
   9^4 = 6561 nodes, each pinning four sites exactly; a portfolio on those nodes
   is the natural parallelisation and is what a machine larger than this one
   should run.
3. **Try to prove that no shared site has red degree 15.** That would close all
   four rows at once, since the other half is done. It cannot be arithmetic: the
   degree laws plus the nine footprints admit every single shared site at degree
   15 (14 of 14 SAT) and every sampled pair (6 of 6 SAT), so any such proof must
   use (L2) or (L4) essentially.
4. **Look at the `GG` and `YY` cells first.** They are the largest (9 - t, up to
   8 vertices) and the least constrained: internally 3-coloured, so no cell
   size is forced the way it is for the four mixed cells. If any sound rigidity
   is available in this instance it is most likely there.

## What is external and stays external

* The two `K16`/`K15` classifications (Kalbfleisch-Stanton 1968 p.19, Heinrich
  1977 Theorem 2) - or, in place of them, the classification-free enumeration
  that `smwu1nsf3/m6` and `m8` both carried out and that replays in this repo.
* The handoff's own alignment census: exactly four surviving 14-overlap
  alignments out of its 69,523-row catalogue. The companion archive and
  `check_common.py` were **not** supplied, so nothing here can check it, and the
  four-row reduction is conditional on it.
* That `max codegree <= 13` is what the branch actually needs, and that the
  branch closes R(3,3,3,3) <= 58 - neither is touched by this work.
