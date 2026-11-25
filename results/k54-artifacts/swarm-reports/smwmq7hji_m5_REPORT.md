# Certified cuts on the three open seed-12 boards, and the generator that makes them checkable

Member m5 (swarm smwmq7hji), direction "bounds-conditioned lift generator".
Everything below was produced in this directory; the archive at
`/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/work/k54`
was read only.

## Result in one paragraph

Each of the three boards that are SAT for the outer integer count model but UNSAT
for a fixed-vector graph lift has a **certified cut over the outer count
variables**. The certificate is a reduced graph CNF whose only pins are the
witnesses of the cut's lower bounds -- every other vertex, rectangle and spoke is
free -- together with a DRAT refutation that `build/drat-trim` accepts
(`s VERIFIED`). The cut is the clause `OR_k not u[k,m_k]`, where `u[k,m]` is the
m-th variable of column k's unary chain in `pilot/cnfs/<board>.counts.json`
(so `u[k,m]` is literally "count[k] >= m").

| board | certified cut | K=2 reduced CNF (sha256) | vars / clauses | CaDiCaL conflicts | drat-trim |
| --- | --- | --- | --- | ---: | --- |
| local-15 | `not u[70,1] or not u[323,1] or not u[354,1]` | `8d11483c372a1766c3e0565c8f71fbd2545daa6dac245b4ea5875055a3b8a3e6` | 4608 / 62765 | 2 | VERIFIED |
| live-07 | `not u[52,2] or not u[83,1]` | `dcb560d6c0bd3cf0ae5623a33f4503ac86de533c84442c970ee7ea96792a7746` | 4600 / 62604 | 266 | VERIFIED |
| live-14 | `not u[1,1] or not u[8,2]` | `ab32f947aa7b40642d51991c8211f24cb55be49bc38a4a36650df140e9d45e9a` | 4624 / 63201 | 4 | VERIFIED |

The same three cuts are also refuted with **every** triangle of the 54 vertices
(K=3, no truncation):

| board | K=3 reduced CNF (sha256) | vars / clauses | conflicts | drat-trim |
| --- | --- | --- | ---: | --- |
| local-15 | `945c876c6937dda9e9464237203ea4e18e0518f1414df25a8858ed958b3e8cd8` | 4608 / 73165 | 126 | VERIFIED |
| live-07 | `7f42587394364b52aaf82fa744da749c2551d656d7b9f700c64e10fbcbff5c38` | 4600 / 73004 | 164 | VERIFIED |
| live-14 | `921d3d1f97927a8b3fc5d5f50cf57325ccd3e3b2b057e3c129ec1e277d6228d0` | 4624 / 73601 | 131 | VERIFIED |

Reduced cores are tiny: 64, 73, 70 clauses (K=2) and 64, 80, 71 (K=3).

## What a certificate asserts, exactly

Notation follows the archive. A **column** is `(rect, side, sig)` from
`pilot/implied_spokes.columns_for(board)` -- a maximal rectangle of free
crossings, one side, and the priced-anchor signature of the ordinary spokes
outside the rectangle. `count[k]` is the number of outsiders booked into column
k. The cut says: *not all of `count[k] >= m_k` hold simultaneously*.

The reduced CNF for `witness = [[k_1,m_1],...]` contains

1. the board's free-edge colour choices (exactly one colour per free edge) and
   the monochromatic-triangle clauses;
2. for every named column k, `m_k` pins on a **distinct** outsider of side(k),
   where "outsider w is in column (rect,side,sig)" means: on side(k), every
   spoke from w to a vertex outside `rect[side]` is ordinary (not colour c), the
   anchors of every class j with sig bit 1 have the class colours, and for every
   class j with sig bit 0 at least one anchor misses its class colour.

Nothing else is pinned. In particular every vertex that is not a named witness is
completely free, the witnesses' *other* side is free, and the witnesses may
choose any rectangle content inside `rect`. Points worth stating because they are
the usual ways a cut certificate goes wrong:

* **distinctness.** Each named column gets its own outsider, and two columns on
  the same side can never share one (an outsider owns exactly one column per
  side). The witness mode enforces this by construction, so a multiplicity-2
  literal `u[52,2]` really needs two different outsiders.
* **free vertices.** No vertex outside the named witnesses occurs in any clause
  except the board's own graph clauses, so "vertices not pinned stay free" holds
  literally.
* **relaxation.** The count model books one rectangle per outsider for *both*
  sides; the certificate pins only the side of the named column. That is strictly
  weaker, hence a refutation is stronger.
* **truncation.** The K=2 clauses omit triangles with three outsiders, so its
  model set contains all true extensions: UNSAT at K=2 implies the cut. K=3
  removes even that caveat.

## The one reduction step that is not vacuous: fixing the witnesses

For every board, all columns of a cut lie on a single side, so the witnesses of
that side are interchangeable. Claim: if a graph on the board's pins has m_k
distinct outsiders in each named column k of side s, then some relabelling of the
26 outsiders has those witnesses exactly `28,29,...`. This holds because the
board constrains no outsider individually: every edge between two outsiders and
every edge from an outsider to either H42 side is free, and the pins are attached
to whichever vertex takes the witness role.

`symcheck.py` checks the premise mechanically: for each board and K in {1,2,3} it
maps every graph clause through five random permutations of `28..53` and compares
clause sets; all nine combinations are invariant (e.g. local-15 K=3: 73108
clauses, invariant). Without the fixing the same three cuts are refutable but the
witness CNF is much harder (local-15: 4686 vars, open after 300000 conflicts);
with it, 2 conflicts.

## How a cut was mined from a refuted vector

`mine_cut.py BOARD`:
1. rebuilds the archived fixed-vector lift verbatim, but tagged: every clause
   records the (outsider, side, column) pin it came from;
2. refutes it with CaDiCaL and extracts the used core with `drat-trim -c`;
3. reads off which pins the core actually uses -> a multiset of columns (the
   multiplicity being the number of distinct outsiders those pins attach to);
4. re-refutes the relaxation above, at K = 2 and 3, and prints the cut.

The refutation counts of step 2 reproduce the archive's own numbers exactly --
local-15 3 conflicts, live-07 1008, live-14 42 -- which is a check that the
rebuilt instance is the archive's instance. The mined pin sets are local-15:
columns 70/323/354 one outsider each (outsiders 49/40/37 in the archive's
labelling; all side 1, sig `0b100000`, three different rectangles); live-07:
column 52 twice and 83 once (outsiders 30,31 and 29; side 0); live-14: column 1
once and 8 twice (outsiders 39 and 30,31; side 1).

## Validation of the generator itself

* `liftb.py --spec specs/local-15-fixed.json --max-outsiders 2` (exact bounds
  lo=hi= the archived vector, per-column booking): UNSAT, DRAT verified
  (`cnfs/local-15-fixed-two.cnf`, sha256
  `86f520d31235c612c99a7e6bc89ab3cab3fbea9a30d1cba3f463c01426f66af3`, 333344
  conflicts). With `--max-outsiders 1` the same instance is SAT
  (`94b2c8b380cade39b126e0b5070b00d7f7bdb9f6089e352699ad1de228cb0b01`), matching
  the archive's SAT/UNSAT pair on that vector. With no bounds at all it is SAT.
* Witness mode naming **all 40 booked columns with their multiplicities** is SAT
  at K=1 (`cnfs/local-15-vecwit-K1.cnf`, sha256
  `aeb5b13cda514cfbd13caba0a942cd18b05345a162341a20b087318c5d2e000d`), so the
  pin encoding admits the true graph instead of only excluding things.
* Non-vacuity of each cut: the outer count CNF plus the cut's lower bounds is
  SAT, and the model decodes to a concrete count vector that the cut kills
  (`runs/<board>-killed-vector.json`, e.g. local-15 has counts 1,1,1 on columns
  70,323,354 and 40 nonzero columns summing to 52).
* Each cut instance is SAT at K=1 on all three boards, so the pins themselves are
  consistent and the obstruction genuinely needs the two-outsider triangles.
* live-07: each single literal alone is SAT at K=2 (columns 52 and 83 in
  isolation), so the 2-literal cut is a joint obstruction, not a capacity bound
  on one column. local-15: the pairs and singletons are OPEN after 100000
  conflicts, so no minimality claim is made there.

## What is closed and what is not

* (a) *one fixed count vector is unrealizable*: reproduced for local-15 with the
  archive's vector (`86f520d3...`, verified), and mechanised for any vector that
  `mine_cut.py --counts FILE` refutes.
* (b) *a board is excluded*: **not** claimed. The outer count CNF plus each cut is
  still SAT (`runs/<board>-outer-pluscut.cnf`), so every board needs further
  vectors, further cuts, or the census. Killed-set sizes found by 30 s of exact
  enumeration with blocking (not exhausted, so lower bounds only): >=22
  (local-15), >=8 (live-07), >=26 (live-14) distinct count vectors, against
  exactly 1 for blocking a single vector. Exact totals belong to the census
  direction (m1/d4).
* (c) *a seed is excluded*: not claimed, and nothing here bears on the 11 other
  seeds.
* Not verified by me: that the outer count CNF is a sound necessary condition for
  a graph (rectangle booking, capacity pricing) -- I take it as given, as the
  archive does and as d9 is checking; the transfer of these cuts to other boards
  or placements (d8); any exact model count.

## Reproduction

```sh
cd .ultramath/smwmq7hji/m5
A=/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/work/k54

# cut mining, end to end (rebuild, refute, core, re-refute, replay): all three
python3 mine_cut.py local-15 ; python3 mine_cut.py live-07 ; python3 mine_cut.py live-14

# or straight from the saved specs:
python3 liftb.py local-15 --spec specs/local-15-cut-canonical.json --max-outsiders 2 \
        --out cnfs/local-15-cut-canon-K2.cnf --map cnfs/local-15-cut-canon-K2.map.json \
        --outer $A/pilot/cnfs/local-15.counts.json
$A/build/cadical/build/cadical -c 400000 cnfs/local-15-cut-canon-K2.cnf runs/local-15-canon-K2.drat
$A/build/drat-trim cnfs/local-15-cut-canon-K2.cnf runs/local-15-canon-K2.drat   # s VERIFIED

# generator validation, symmetry check, non-vacuity
python3 liftb.py local-15 --spec specs/local-15-fixed.json --max-outsiders 2 --out cnfs/local-15-fixed-two.cnf
python3 symcheck.py
```

`liftb.py` needs the copied `src/` and `data/` (hashes in `COPIES.sha256`) and, for
non-trivial cardinality bounds only, `pysat`. `mine_cut.py` and `symcheck.py` also
read the read-only archive for the board data and the archived vectors.

## Files

| file | what |
| --- | --- |
| `liftb.py` | the bounds-conditioned lift generator (modes `counts`, `witness`, canonical fixing, model decoder) |
| `mine_cut.py` | refute vector -> core -> column multiset -> certified cut, end to end |
| `cut_from_core.py` | same pipeline driven by the archived DRAT trace (first version, kept for the record) |
| `symcheck.py` | outsider-permutation invariance of the graph part |
| `specs/*.json` | every spec used: the three cuts (canonical), the fixed vector, the all-column witness instance |
| `cnfs/*.cnf` | every reduced CNF, with `*.map.json` column/variable maps |
| `runs/*.drat`, `runs/*.check.log` | proofs and drat-trim transcripts |
| `runs/<board>-certificate.json` | machine-readable certificate: cut, hashes, conflicts, replay verdict, outer clause |
| `runs/<board>-killed-vector.json`, `runs/killed-enumeration.json`, `runs/subcuts.json` | non-vacuity, killed-set lower bounds, sub-cut status |
| `COPIES.sha256` | hashes of everything copied out of the archive |

Large intermediate proofs and the decompressed archive traces are stored gzipped
(`runs/*.gz`); the six cut certificates `runs/<board>-canon-K{2,3}.drat` are kept
uncompressed because `verify.sh` replays them directly. Everything compressed can
be regenerated by the commands above.
