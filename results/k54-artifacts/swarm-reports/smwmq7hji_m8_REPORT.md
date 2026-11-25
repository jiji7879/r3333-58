# Certified cuts over the outer count variables for local-15, live-07, live-14

Member m8, swarm smwmq7hji, direction d3 (structural lemma for the local obstruction).

Everything below was produced in this directory from the read-only archive
`/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/work/k54`
(hereafter `$K`). Nothing in the archive was modified. All paths below are relative to
this directory, `.ultramath/smwmq7hji/m8/`.

## 0. The three claims, kept separate

| claim | status here |
| --- | --- |
| (a) one fixed count vector is unrealizable | **certified for the three archived vectors**, by pairwise/one-column certificates, independently of the archive's 26-outsider lift |
| (b) a board (all count vectors satisfying its pins) is excluded | **not achieved.** For each of the three boards, the count CNF plus *every* certified cut I could derive is still SAT |
| (c) a seed is excluded | not attempted |

## 1. The reduction (the one construction everything rests on)

A column `k` of a board's outer count model is a triple `(rect, side, sig)`:
`rect = (left_mask, right_mask)` a maximal rectangle of free crossings, `side ∈ {0,1}`
(0 = left H42 copy, core vertices 0..13; 1 = right, 14..27), `sig` the priced
anchor-signature mask. `count_k >= 1` says at least one of the 26 outsiders has that
marginal type.

`reduced(board, [k_1..k_t])` (`reduced.py`, `lib.reduced`) builds the CNF

* `graph(board, 28+t, sort=False)` — the board's own fixed crossings plus **all** edge
  and triangle clauses on the 28 core vertices and `t` fresh outsiders `28..28+t-1`;
* the pin block of column `k_i` applied to outsider `28+i` on `k_i`'s own side
  (`lib.pin_block`, identical to `pin()` plus the outside-rectangle loop of
  `$K/pilot/lift_counts.py`; my re-implementation reproduces the archived
  `lift-local-15-two` formula byte for byte, sha256
  `e499e127a1ec5a07bd0c2070539fafbbed3be95003ff3c963c8a8dc36ec1e36f`).

**Nothing else is imposed**: no population 26, no left/right rectangle-total balance, no
labelled-matching clauses, no other outsider, no symmetry breaking. So UNSAT of the
reduced instance says: *no graph satisfying the board's pins has one outsider of each of
these marginal types at once.*

**Inclusion lemma, machine-checked.** `lib.inclusion_check` verifies that every clause of
the reduced CNF occurs *literally* (same variable numbers) in
`graph(board,54, sort=False)` or in one of the pin blocks of the same columns. The result
is recorded as `inclusion_check_clauses_missing` in each certificate and is `0`
everywhere. Because the 54-vertex formula's clause set contains the reduced clause set,
UNSAT of the reduced instance implies UNSAT of the full formula with those pins — no
relabelling or symmetry argument is needed.

**What the encoding allows (witness distinctness).** Every cut reported here uses columns
of a *single* side. An outsider has exactly one side-`s` marginal column (its
c-neighbourhood on that side lies in exactly one maximal rectangle, and its price
signature is determined), so `t` distinct columns on one side are automatically `t`
distinct outsiders, and a repeated column with chain literal `u_{k,m}` is exactly "at
least `m` outsiders of column `k`" (the reduced instance uses `m` distinct vertices
`28..27+m`). The `start_of_stream` hazard the task warns about — one outsider witnessing
two literals for the same rectangle on different sides — cannot arise, because no cut
mixes sides.

## 2. The structural lemma (why these cuts are necessary at all)

Write `H` for the H42 template (`$K/checkpoints/counted/data/h42.json`, symmetric, `-1`
on the diagonal, `H(p,q) ∈ {0,1,2}` for `p≠q`) and let `s_x(p)` be the colour of the edge
from outsider `x` to core vertex `p` on one side (colours via that side's palette).

*Board-formula clause shape.* The generator emits a triangle clause for a triangle and a
colour `c` only when **every fixed edge of that triangle already has colour `c`**, and
then the clause contains only the free edges' negations
(`$K/checkpoints/counted/src/board.py`, the `for … else` in the triangle loop). For a
triangle `(p, q, x)` with `p,q` core, the core edge is fixed, so

> **Rule P.** `s_x(p) = c` and `H(p,q) = c` imply `s_x(q) ≠ c`.
> There is no rule for colour 3: `H` never takes the value 3, so no clause forbids two
> c-spokes. (A c-neighbour set of an outsider is a rectangle, not a single vertex.)

> **Lemma 1 (pair ban).** Let `x ≠ y` be outsiders and suppose colours `c_0,c_1,c_2,c_3`
> and core vertices `p_0,…,p_3` satisfy `s_x(p_c) = s_y(p_c) = c`. Then no graph exists.
>
> *Proof.* The triangle `(p_c, x, y)` for colour `c` has all three edges free, so its
> clause is `¬e(p_c,x)=c ∨ ¬e(p_c,y)=c ∨ ¬e(x,y)=c`, which forces `e(x,y) ≠ c`. For the
> four colours this forbids every colour for `e(x,y)`. ∎

> **Corollary 1 (capacity).** If the four colours of Lemma 1 are forced for a column `k`
> already by the pin block of `k` (via Rule P plus `s_x(p) ≠ 3` for `p ∉ rect`), then
> `count_k <= 1`; more generally, the largest `m` for which `m` outsiders of column `k`
> can coexist is a finite "capacity" `t_k`, and `count_k <= t_k` is a cut.

Lemma 1 and Corollary 1 are what `certs/*-capacity-all.json` records, one certificate per
UNSAT `m`. Rule P is sound as a derivation but **not complete**: a column pair can be
impossible through a case split that unit propagation does not see, so the propagation
criterion in `prop.py`/`pairgraph.py` is only used to *find* candidates; every claim below
is confirmed by an actual refutation.

**The concrete mechanism, hand-checked on local-15.** Take two outsiders `x,y` with
`s_x(24)=s_y(24)=1`, `s_x(16)=s_y(16)=2`, `s_x(20)=s_y(20) ≠ 3`. Using Rule P and
`H(16,24)=2`, `H(16,20)=2`, `H(20,24)=1`, `H(25,16)=2`, `H(25,24)=1`, `H(25,20)=2`:
`s(20) ∉ {1,2}` and `≠3` so `s(20)=0`; then `s(25) ∉ {1,2,0}` so `s(25)=3`. Now
`s(24)=1`, `s(16)=2`, `s(20)=0`, `s(25)=3` exhaust the four colours on positions
`24,16,20,25`, so Lemma 1 applies. This is exactly the 25-clause drat-trim core of
`certs/local-15-cap-…`; see also the `t=2` certificate in §3.1. The same shape explains
every capacity bound found.

## 3. Certificates

`certs/` holds every CNF, DRAT and core referred to below plus the JSON records with
hashes. `verify_cuts.py` re-derives each CNF from its recorded columns and checks the
sha256, replays the DRAT, and re-runs the inclusion check.

### 3.1 Headline cuts that bite the archived count vectors

Archived count models: `$K/pilot/runs/<board>-cadical/counts.json`.

| board | columns (in order) | cut clause over the outer model | recorded model | reduced CNF sha256 | verdict |
| --- | --- | --- | --- | --- | --- |
| local-15 | 354, 323, 70 (all side 1) | `¬u_{354,1} ∨ ¬u_{323,1} ∨ ¬u_{70,1}` (unary lits 1670, 1482, 451) | c₃₅₄=c₃₂₃=c₇₀=1 → **violated** | `914322f1067128183d98f90a4d228477cf6c3863e4f45a9400da41752aa099ae` | UNSAT, DRAT VERIFIED, 64-clause core, core itself refuted (`cff1381341047d80…`), inclusion 0 missing |
| live-14 | 1, 8, 8 (all side 1) | `¬u_{1,1} ∨ ¬u_{8,2}` (chains: col 1 = `[27]`, col 8 = `[109,110,111]`, so `u_{8,2}=110`) | c₁=1, c₈=2 → **violated** | `ed2e4da0e168731d90bd1340d1a56bb951f42ca2df87c21b2f16fadfe56a0830` | UNSAT, DRAT VERIFIED, core refuted, inclusion 0 missing |
| live-07 | 83, 52, 52 (all side 0) | `¬u_{83,1} ∨ ¬u_{52,2}` (chains: 83 = `[423,424,425]`, 52 = `[336,337,338]`) | c₈₃=1, c₅₂=2 → **violated** | `3fc394efce9b13ed69d9b38ceff13fa7247d9cbf2bdecc177bede9cf65b73f70` | UNSAT, DRAT VERIFIED, core refuted, inclusion 0 missing |
| live-07 | 55, 55, 55 (side 1) | `count_55 <= 2`, i.e. add `¬u_{55,3}` (chain `[343,344,345]`) | c₅₅=3 → **violated** | `61a9f32dd2ac8beaac151336e6fe7e52fd5f7e60b310a60985358cee096b8ea7` (DRAT `c08f54b76675e849…`) | UNSAT, DRAT VERIFIED, 288-clause core, inclusion 0 missing |

Reproduce any of them with

```sh
python3 certify.py <board> <comma-separated columns> certs     # 3-literal / multiplicity cuts
python3 allcaps.py <board>                                    # whole capacity table + counts CNF
python3 verify_cuts.py                                        # re-verify everything
```

The three earlier `*-cut-*` rows are exactly the shapes the task's key observation
predicted, with one correction worth recording: on **local-15 the archived obstruction is
not three-way-essential in the pins** — the two-outsider pattern
`{colour 1 at vertex 24, colour 2 at vertex 16, not colour 3 at vertex 20}` is already
UNSAT for **two** outsiders (`red2.build('local-15',[{'c3neq':[6],'col':{10:1,2:2}}]*2)`,
624 vars, 3254 clauses, sha256
`98493ace11fc94095de85d6d31c96cecc375d3d1bf7aef7d07a62e18570dee82`, DRAT VERIFIED,
25-clause core), while `t=1` is SAT. That is Corollary 1 with `t_k = 1`.

### 3.2 Full capacity tables

For every column of each board, the largest `m` with `m` copies of that column's pin block
SAT. `m` runs 2,3,4 (and stops at the first UNSAT).

| board | columns | finite capacities | of which `t_k = 1` | nonextendible by 4 | UNSAT instances certified | nontrivial cuts (`t_k < len(chain)`) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| local-15 | 717 | 639 | 452 | 78 | 639 | 122 |
| live-07 | 495 | 429 | 347 | 66 | 429 | 38 |
| live-14 | 672 | 579 | 468 | 93 | 579 | 54 |

Records: `certs/{local-15,live-07,live-14}-capacity-all.json`. Each UNSAT entry carries
`cnf`, `drat`, both sha256 values, `drat_trim_verified` and the drat-trim core size.

**The archived count vectors violate certified capacities**, so claim (a) is re-derived
without the archive's lift at all:

* local-15: `c₅₅=3 > t₅₅=2`, `c₃₇₃=3 > 2`, `c₃₇₆=3 > 2`
* live-07: `c₅₅=3 > 2`, `c₄₅₀=10 > 3`, `c₄₅₁=3 > 2`
* live-14: `c₁₀₀=6 > 3`, `c₁₀₇=7 > 3`

(`certs/<board>-capacity.json` is the first, used-columns-only version of the same table,
also fully verified: 81 checks, 0 failures when run with
`python3 verify_cuts.py '*-capacity.json'`.)

### 3.3 Strength of the certified 3-literal local-15 cut

The capped enumerations in `killcount.py` (Cadical195, blocking on the unary projection,
3000 models / 240 s per run) gave

* models satisfying `c₃₅₄>=1 ∧ c₃₂₃>=1 ∧ c₇₀>=1`: **3000**, budget exhausted at 17 models/s;
* models of the count CNF in total: **3000**, budget exhausted at 19 models/s.

So the cut kills at least 3000 distinct count vectors while blocking a single vector kills
exactly one. Neither enumeration exhausted, so no exact total is claimed.

## 4. Feeding the cuts back: the loop runs, the boards stay open

`cegar2.py` / `allcaps.py` add `¬u_{k,t_k+1}` for every column with `t_k < len(chain)` to
`$K/pilot/cnfs/<board>.cnf.gz` and re-solve:

| board | capacity cuts added | augmented CNF sha256 | result |
| --- | ---: | --- | --- |
| local-15 | 122 | `edc6af2eb547defdae276aff4ced4ad5d7b5eb39c53695afcccd9409b9838d70` | **SAT** (new vector, 44 used columns) |
| live-07 | 38 | `ba3e388b56977a62fd98febdfda0304450e80f2ba9a50819a1aaf87528bf32dc` | **SAT** |
| live-14 | 54 | `f95674c30955f0a22cc23e8805fd032718d361ffb62e45e07ca349d365488249` | **SAT** |

Then, for local-15, one full pair round on the surviving vector (`round1.py`,
`certs/local-15-paircuts-round1.json`): all 946 pairs of its 44 used columns were tested
exactly and **none** was UNSAT, so the pair round adds zero cuts and the formula is
unchanged (`edc6af2e…`, still SAT).

An earlier, more aggressive experiment used the *stronger-but-uncertified* propagation
pair graph of `pairgraph.py` (6318 pairs on local-15): adding all of them gave an
**OPEN** result at 120 s of CaDiCaL, and since those pairs are not individually
certified, nothing is claimed about that formula. File:
`.scratch/cegar/local-15-cut1.cnf`.

**Conclusion.** No board is excluded. Capacities and pairwise bans are exhausted for
local-15; closing it needs genuine three-outsider (or higher) conditions, and the one
three-way condition known to bite (`354,323,70`) is a single cut, not a family.

## 5. Negative and transferable findings for the rest of the swarm

1. **Do not expect pairwise reasoning to close local-15.** All 820 pairs (including
   self-pairs) among the 40 columns of its archived vector were tested exactly
   (`exact_pairs.py`, `certs/local-15-exact-pairs.json`): 16 self-pairs are UNSAT (those
   give `count_k <= 1`, all satisfied by the archived vector, which has count 1 there),
   **zero cross-pairs are UNSAT**. So the archived vector is killed only by a condition on
   ≥3 columns at once.
2. **Structural type-level content that does transfer.** Rule P, Lemma 1 and Corollary 1
   are board-independent: they need only that a board's core sides are 3-coloured
   templates. Any column whose pin block forces all four colours on four spokes gives a
   capacity bound with no search. live-07's column 55 has `sig = 0` — a pure rectangle
   type with no priced anchors — and still has capacity 2, so capacities are not only a
   price-signature phenomenon.
3. **A cut must live on one side.** live-07's three drat-trim core witnesses (29, 30, 31)
   have columns (83, 85), (52, 55), (52, 55); restricting those three pins to side 1 alone
   is **SAT** (`certs/live-07-cut-85-55-55.json`), so the core's own shape does not give a
   marginal cut. The valid live-07 cuts come from one side only: `count_55 <= 2` (side 1)
   and `¬(c₈₃>=1 ∧ c₅₂>=2)` (side 0). The marginal count model cannot express a joint
   condition on an outsider's two sides.
4. Cuts of the form "one side-0 column and one side-1 column are incompatible" cannot be
   derived from marginals at all; any cut mixing sides must be checked for the
   one-outsider-two-literals hazard.

## 6. What is verified and what is not

Verified, with a checked transcript:

* every UNSAT instance above re-derives from its column list, its sha256 matches the
  recorded one, `build/drat-trim <cnf> <drat>` exits 0 with `s VERIFIED`, and the
  inclusion check against `graph(board,54)` + pin blocks reports 0 missing clauses;
* the archived `lift-<board>-two` formulas are reproduced byte for byte from the archive's
  own generator and count models (sha256 `e499e127…`, `c1d17a0c…`, `4ba6cd35…`), and
  `drat-trim -c` on the archived traces gives 67 / 72 / 78-clause cores;
* `python3 verify_cuts.py` over **every** record in `certs/`: **1728 checks, 0 failures**,
  exit 0. Full transcript in `verify_transcript.txt`. Each check rebuilds the CNF from the
  recorded column list, compares its sha256 with the recorded one, replays the DRAT through
  `build/drat-trim` (exit 0 and `s VERIFIED`), and re-runs the inclusion check.

Not verified / not claimed:

* no board exclusion and no seed exclusion; every augmented count CNF was SAT;
* no exact census: both enumerations were capped at 3000 models, so the true number of
  count vectors (hence the exact kill count of any cut) is **not** known here. The rate is
  17–19 vectors/s, so the archive's `ours/count_models.py` needs hours for a total;
* the `t=2` local-15 certificate in §3.1 is a *hand-chosen* pin pattern that is not the
  pin block of any single column; it is a statement about the board, not a cut over the
  count model (the columns that satisfy it are only those with `6 ∉ rect[1]`, e.g. 323);
* `prop.py`'s propagation is a sufficient criterion only; `pairgraph.py`'s counts are
  candidate counts, not certified claims.

## 7. File map

| file | role |
| --- | --- |
| `lib.py` | column data, `pin_block`, `reduced`, `inclusion_check`, `unit_sets` |
| `reduced.py` | reduced-instance builder + DIMACS writer + pin description |
| `certify.py` | one certificate per column list: CNF, DRAT, core, DRAT of the core, inclusion check, unary mapping |
| `allcaps.py` | whole capacity table per board + the augmented count CNF solve |
| `capacity.py` | first used-columns-only capacity table |
| `verify_cuts.py` | independent re-derivation + DRAT replay + inclusion check for every record |
| `pairgraph.py`, `prop.py` | Rule P propagation; candidate pair bans (sufficient, not complete) |
| `exact_pairs.py` | exact pairwise scan of the archived vectors' columns (§5.1) |
| `round1.py`, `cegar2.py`, `cegar.py`, `killcount.py` | CEGAR rounds and capped enumerations |
| `instr.py` | instrumented copy of `lift_counts.build` that records each outsider's column; reproduces the archived sha256 |
| `anacore.py`, `mincore.py`, `red2.py`, `dec.py`, `test_variants.py`, `sweep.py` | core decoding and the minimal-instance searches |
| `certs/` | every certificate, its DRAT and core, plus the JSON records |
