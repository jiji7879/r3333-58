# tools/pb — the singleton-perfect-balance codegree-14 instances

State as of the session that started swarm `smwu1nsf3`. Everything below is
reproducible from this directory; nothing here is a proof of `R_4(3) <= 58`.

## The instance

`encode.py` builds the exact CNF for one child `(row, t)`: the 20 pinned vertices
of the handoff `attachments/see-what-you-can-yel5/K58_PB_parallel_handoff.md`,
the 38 outside sites in cells with pinned sizes, and the four laws

    (L1) one colour per edge          (L2) no monochromatic triangle
    (L3) red degree in {15,16}, other colours <= 14
    (L4) every pair has <= 14 common red neighbours

Vertex layout: 0..13 shared sites, 14/15 the two p's, 16/17 the two q's,
18 = u, 19 = v, 20..57 outside in the order `encode.CELLORDER`.

    python3 tools/pb/encode.py TT_d02 3 out.cnf --strength N

`--strength 0` is exactly "(L1)-(L4) plus the pins". Higher levels add only
consequences of the laws, so an UNSAT at any level is an UNSAT of the child:

* `1` every ordinary colour-degree is at least 13.  From (L3): 57 = red + b + g + y
  with red in {15,16} and b,g,y <= 14 forces b+g+y in {41,42}.
* `2` (with `--all16`/`--some15`) the red-degree-16 split variable, and with
  `footprint` on, the exact per-cell footprint of a degree-16 shared site
  (see below).
* `3` each of the four 5-cells is a red 5-cycle: a vertex with three red
  neighbours inside such a cell would force a monochromatic triangle, so at most
  two, and for a cell of size 5 the totals give exactly two.

`--all16` restricts to "every one of the 14 shared sites has red degree 16";
`--some15` to its complement; `--z15 i` to "shared site i has red degree 15".

## Verified so far

| statement | evidence |
| --- | --- |
| every blue edge of T and of U has the same footprint: 0 in (B,B), 2 in each of (B,G),(B,Y),(G,B),(Y,B),(G,G),(Y,Y), 1 in each of (G,Y),(Y,G). So a degree-16 shared site has exactly two red neighbours in each of the four 5-cells | `python3 tools/pb/footprint.py` |
| ~~the all-16 sub-case is UNSAT~~ **RETRACTED** | the `h <-> (red and d16)` guard was inverted, so `--all16` was unsatisfiable by construction. With a gadget-free `at-least-16` the same sub-case is **SAT in 2.4 s** under the degree laws and undecided at 600 s with all four. See `results/pb-codegree-2026-11-24/README.md`. |
| the nine footprints | two independent routes, see below |

The `--all16` sweep over all four rows and all five `t` is `sweep_all16.py`;
its ledger is the table to read, not this paragraph.

## The nine footprints (the lever)

A shared site's red chart is a triangle-free 3-coloured K15 or K16 containing the
blue edge uv. Two independent routes give the same nine possibilities:

* literature: Kalbfleisch-Stanton 1968 p.19 (two K16 colourings) plus Heinrich
  1977 Theorem 2, J. Austral. Math. Soc. Ser. A 24, 465-495, DOI
  10.1017/S1446788700020838 (two K15 colourings, each a K16 colouring with one
  vertex deleted); with `footprint.py` this gives the full table, and the full
  table with one unit removed from one positive cell;
* swarm `smwu1nsf3` members m6 and m8, classification-free: enumerate the 60
  (order 16) and 432 (order 15) count matrices obeying the total and the
  per-vertex colour degrees {5,5,5} / {4,5,5}, eliminate 449 arithmetically, and
  refute 34 by replayed DRAT; nine survive. `check_footprints.py` in
  `.ultramath/smwu1nsf3/m6` - replayed here, passes.

`--fp15` is that theorem in the CNF: for each shared site exactly one of
"red degree 16 and the full table" or "red degree 15 and the table minus one in
the chosen positive cell" holds. It is the complete child, not a sub-case.

## Open

Nothing in this line is closed. `--strength 3 --fp15` on TT_d02 t=3 is **undecided** (Kissat 4.0.4, 900 s, and
the run above it). Sanity ladder for that encoding: pins+fp15 SAT, degree+fp15
SAT (1.7 s), full undecided - so the nine-footprint block is not itself
contradictory, unlike two earlier versions of it. The four rows are therefore
still open, and the all-16 half above is only a sub-case.

## Traps already hit

Second trap: the `--fp15` block first passed cell *vertices* where edge literals
belong, so every footprint clause was over raw vertex ids and the instance was
UNSAT in 0.03 s even with only (L1) and the pins. A CNF that is UNSAT at
`--strength 0 --fp15` is broken: that combination must be SAT.

## Trap already hit once

`encode.py` early in the session allocated auxiliary variables from
`4*C(58,2)+4` while the edge variables run to `(56*58+57)*4+4 = 13224`, so every
cardinality encoding overwrote edge variables and everything came back "UNSAT"
in 0.2 s. Any CNF built before 02:05 on 2026-11-24 is void; the header must
declare more than 13224 variables. Check `p cnf` before trusting a verdict.
