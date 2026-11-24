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
| row TT_d02, t=3, **sub-case "all 14 shared sites have red degree 16"**: UNSAT | `--strength 1 --all16 --no-footprint`, Kissat 4.0.4, DRAT replay `s VERIFIED` (`sweep_all16.py` regenerates) |
| the same sub-case is already UNSAT from the degree laws alone: laws (1,3) only, no triangles and no codegree | 0.9 s, 1514-clause core |
| both verify with drat-trim | yes |

The `--all16` sweep over all four rows and all five `t` is `sweep_all16.py`;
its ledger is the table to read, not this paragraph.

## Open

The complement — **some shared site has red degree 15** — is not decided. That is
the whole remaining gap for the four rows: `--some15` times out. A degree-15
site's red chart is a 3-coloured K15 instead of a K16, so the footprint theorem
does not apply to it, and only "at most two red neighbours per 5-cell" survives.

## Trap already hit once

`encode.py` early in the session allocated auxiliary variables from
`4*C(58,2)+4` while the edge variables run to `(56*58+57)*4+4 = 13224`, so every
cardinality encoding overwrote edge variables and everything came back "UNSAT"
in 0.2 s. Any CNF built before 02:05 on 2026-11-24 is void; the header must
declare more than 13224 variables. Check `p cnf` before trusting a verdict.
