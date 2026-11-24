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
all five `t`, twice over (strength 1 and strength 3): 40 instances, every one
UNSAT with a DRAT proof replayed to `s VERIFIED` by `drat-trim` against the same
CNF, median 27 s, max 102 s. `tools/pb/sweep_all16.py` regenerates the whole
table; the ledger is `.scratch/pb/all16/ledger.tsv`.

Stronger than that: this half already follows from the **degree laws alone**. The
instance with (L2) triangles and (L4) codegree dropped is still UNSAT (0.9 s,
1514-clause core). So the content is arithmetic, not combinatorial — which is why
it is cheap. It is also why it says nothing about the other half.

## What is open

The complement — **some shared site has red degree 15** — and the mixed cases.
`tools/pb/encode.py --strength 3 --fp15` is the complete child (all nine
footprints wired in, no case split), and it is undecided: Kissat 4.0.4 at 900 s
and then 3000 s, and CaDiCaL in parallel. Sanity ladder for that encoding:
`--strength 0 --fp15` SAT, `--strength 1 --fp15` SAT (1.7 s), full undecided.

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
