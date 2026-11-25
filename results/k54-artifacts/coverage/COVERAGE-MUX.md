# The count abstraction is sound for live-06 and live-20 (the pole-pair boards)

Claim (b) of the task — "a board is excluded" — is normally read off an unsatisfiable **outer
count CNF**.  That reading needs an implication: *every* triangle-free 4-colouring of K54 that
realizes the board's pins must induce a count vector satisfying the outer CNF.  The previous
run proved it for the thirteen boards whose price file has all-zero `mux`
(`.ultramath/smwmq7hji/m6/COVERAGE.md`) and left `live-06` and `live-20` out, because
`pilot/implied_spokes.columns_for` refuses those two:

```
ValueError: This indexing routine requires zero pole-pair prices.
```

This note supplies the general indexing and discharges the same obligation for those two
boards.  It produces no cut and closes no board.

## Setting

`B` is a board (`checkpoints/counted/data/boards.json`): two palettes (permutations of
`{0,1,2}`), two poles `poles = (a,b)`, and 14 row masks.  K54 has left core `L = {0..13}`,
right core `R = {14..27}`, outsiders `O = {28..53}`; `c := 3` is the fourth colour.  Cell
`(i,j)` of the crossing board is **free** when bit `j` of `rows[i]` is one.  A colouring
**realizes the pins** of `B` when

* `colour(14s+i, 14s+j) = palettes[s][H[i][j]]` for all `i<j<14`, `s in {0,1}` (`H` = `h42.json`);
* `colour(i, 14+j) = c` whenever `(i,j)` is not free.

`rects(B) = maximal_rectangles(rows)` is the table of maximal free rectangles; rectangle
`(left,right)` has `left = {i : right ⊆ row i}`.

An outsider `w` assigned rectangle `P` has `N_0(w), N_1(w) ⊆ P` where `N_s(w)` are its
`c`-neighbours in side `s`; its **word** on side `s` is the colour of its ordinary spokes to
the vertices of `P[s]`'s complement.  Its **signature** is the set of *priced classes*
`j = (side,{(h,q)})` of `prices/B.json` whose anchors all lie outside `P[s]` and are all met
in their prescribed colour `h`.

**Pole-pair (mux) class.**  An outsider's spoke to the pole `a` of side 0 and to the pole `b`
of side 1 are both ordinary: every edge from `a` to side 1 has colour `c`, so `w ∉ side 1`
forces `colour(a,w) != c`, and symmetrically.  The pair of colours `(x,y)` is charged
`mux[3x+y]`; the corresponding **pole-pair class** is the two-anchor class
`{(x,a),(y,b)}`, whose capacity is `16` when `x = y` and `5` otherwise (§5).

**Outer count CNF** of `B`: `outer/B.cnf`, built by `pilot/make_pilot_cnf.py` with
`price_cover.columns_for` rebound to `muxcol.columns_for_general` (`outer.py`, the only
change).  One unary chain `u[k,1..h_k]` per column `k = (rect,side,signature)`,
`h_k = min({26} ∪ {cap_j : j ∈ row(k)})`; per-rectangle equality of the two side totals;
population 26 on the left; one upper bound `cap_j` per implied class `j`; and one lower
bound per priced class with positive slack bound.  For both boards the last family is
**empty** (audit-mux.json: `positive_lower_bound_classes = 0`).

## Theorem

Let `B` be `live-06` or `live-20`, and let `col` be a colouring of K54 with **no
monochromatic triangle** that realizes the pins of `B`.  Then there is an integer
`cnt_k ≥ 0` for every column `k` of `columns_for_general(B)` such that `cnt` satisfies
**every clause** of `outer/B.cnf`.

Numerically (audit-mux.json):

| board | rectangles | columns | dropped rect / col | min charge | scale | capacity | slack | cutoff | max column price |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| live-06 | 86 | 11610 | 0 / 0 | 10004 | 10004 | 280459 | 20355 | 30359 | 18219 |
| live-20 | 75 | 8661 | 0 / 0 | 10004 | 10004 | 271752 | 11648 | 21652 | 16486 |

## Proof

Write `N_s(w) = {v in side s : colour(v,w) = c}`.

1. **Both c-supports are nonempty.**  If `N_s(w) = ∅`, all 14 spokes of `w` into side `s`
   are ordinary.  Lemma F4 (`lemmas/F4-H42-all-ordinary.cnf`, DRAT-verified) refutes that.
2. **`N_0(w) × N_1(w)` lies in free cells.**  A pinned `c` crossing `(i,j)` with `i ∈ N_0(w)`
   and `j ∈ N_1(w)` would make `{w,i,j}` a monochromatic `c` triangle.
3. **A table rectangle contains both supports.**  `RectLive06.lean` / `RectLive20.lean`
   prove `support_covered`: for any two nonempty vertex lists whose product is free there is
   a recorded right support `r` with the right list inside `r` and every left vertex of the
   product containing all of `r`.  So `w` can be **assigned** the rectangle `P = (left,right)`
   with `N_0(w) ⊆ left`, `N_1(w) ⊆ right`.  One such `P` is chosen for each outsider.
4. **The assigned column exists.**  Outside `P[s]` the spokes of `w` are ordinary and `col`
   has no triangle, so `w`'s pattern on side `s` is one of the words the table enumerates for
   `(s, P[s])`; its signature is therefore a key, i.e. `(P,s,σ)` is a column.  It is
   *retained*: audit-mux.json checks that no rectangle is dropped (`rectprice ≤ cutoff` for
   all 86 / all 75) and no column is dropped (`max column price 18219 ≤ 30359`, resp.
   `16486 ≤ 21652`).  Even with the pole-pair terms deleted from the cutoff the maximum is
   below it (29994 and 21372), so the two boards' retention does not depend on the mux
   convention at all.  The column's forced masks are the intersection over all words of the
   signature, hence contained in `w`'s own masks: every class implied by `row(k)` is really
   met by `w`.
5. **Class capacities.**  Let `j = (s,{(h_1,q_1),…,(h_m,q_m)})` be an anchor class with
   distinct colours `h_1..h_m`.  For any two vertices `v,v'` of the class and any anchor
   `q_l`, the triangle `v,v',q_l` has colours `colour(v,v')`, `h_l`, `h_l`, so
   `colour(v,v') ≠ h_l`.  The class therefore induces a `(4-m)`-colouring of a complete graph
   with no monochromatic triangle, so `|class| ≤ R_{4-m}(3) - 1`.  Lemmas F1 (`K6`, 2
   colours), F2 (`K17`, 3 colours), F3 (`K3`, 1 colour) give `R(3,3)=6`, `R(3,3,3)=17`,
   `R(3)=3`, so the bounds are `16, 5, 2`, and `1` for `m = 4`; these are the archive's
   `LIMIT`.  The `inside_j` vertices of side `s` that already meet all anchors are class
   members (their edges to the counted outsiders avoid the `h_l` too), hence
   `cnt`-sum over the columns of `j` `≤ LIMIT[m] - inside_j = cap_j`.  **The pole-pair class
   is the same lemma with `m ∈ {1,2}` applied to the two-anchor set `{(x,a),(y,b)}`:** its
   two anchors lie in different sides and edges to a pole are ordinary, so the bound
   `16 / 5` applies verbatim.  No vertex is *forced* into it (`forced_left = forced_right = 0`
   in audit-mux.json, because a pinned crossing is colour `c`, never an ordinary colour);
   free crossings could add members, which only lowers the true capacity — the direction that
   keeps the argument sound.  `muxcol` therefore charges `16/5` and the capacity total
   `280459 / 271752` is an upper bound on the real one.
6. **Balance and population.**  `cnt_k` = number of outsiders assigned column `k`.  Each
   outsider is assigned exactly one rectangle and contributes exactly one to a left column
   and one to a right column of that rectangle, so the two side totals agree on every
   rectangle and the left population is 26.
7. **Unary chains and lower bounds.**  `cnt_k ≤ h_k` by step 5 and `cnt_k ≤ 26`.  There are
   no positive lower bounds on these two boards, so no further clause.  ∎

Steps 1, 4 (retention), 5 (the `inside` counts, the pole-pair bookkeeping, the capacity
totals, the minima) are recomputed by `audit_mux.py`; the finite Lemmas by
`verify_lemmas.py`; step 3 by Lean.  The composition is prose, as in the thirteen-board note.

## What the general indexing is

`muxcol.columns_for_general` is `implied_spokes.columns_for` with one change: the retention
price of a word is

```
price = cost(word) + min over d of ( cheapest word of the other side with pole colour d + mux[3c+d] )
```

with `c` the word's pole colour.  A rectangle is kept iff
`min over (c,d) of (mins_0[c] + mins_1[d] + mux[3c+d]) ≤ cutoff`; a column iff its `price ≤
cutoff`.  Both are lower bounds on the true charge of an outsider of that type, so retention
is sound.  For `mux = 0` the two formulas collapse to the archive's
`cost(sig) + cheapest other side` and `mins_0 + mins_1`.

`validate.py` checks the collapse exactly: on **all thirteen** zero-mux boards the general
indexing returns a list **identical** to `implied_spokes.columns_for`, element for element, in
order — 495, 672, 717, 2473, 8619, 10917, 12110, 12216, 18475, 14050, 8539, 10800 and 12911
columns.  On the two mux boards it returns 11610 and 8661 columns.

## Machine-checked ingredients

| item | file | check | result |
| --- | --- | --- | --- |
| rectangle coverage, live-06 | `RectLive06.lean` | `lean RectLive06.lean` | `support_covered` axioms `propext, Quot.sound`; `count_rights` no axioms; 86 rectangles |
| rectangle coverage, live-20 | `RectLive20.lean` | `lean RectLive20.lean` | same; 75 rectangles |
| `R(3,3)=6` | `lemmas/F1-K6-2col.cnf` | `build/drat-trim …` | UNSAT, 21 conflicts, `s VERIFIED`, sha256 `a60bc7ef…` |
| `R(3,3,3)=17` | `lemmas/F2-K17-3col-sorted.cnf` | `build/drat-trim …` | UNSAT, 1888 conflicts, `s VERIFIED`, sha256 `9e11bf34…` |
| `R(3)=3` | `lemmas/F3-K3-1col.cnf` | `build/drat-trim …` | UNSAT, `s VERIFIED`, sha256 `b0723feb…` |
| H42 has no all-ordinary extension | `lemmas/F4-H42-all-ordinary.cnf` | `build/drat-trim …` | UNSAT, 16 conflicts, `s VERIFIED`, sha256 `719e32ae…` |
| sharpness controls | `lemmas/F1p`, `F2p`, `F3p`, `F4p-p00..p13` | models decoded | SAT, all 17 |
| generalisation of the indexing | `validate.py` | list equality vs `columns_for` | 13/13 boards identical |
| side conditions, live-06/20 | `audit_mux.py` → `audit-mux.json` | `python3 audit_mux.py` | all hold (table above) |
| CNF bookkeeping = charge bookkeeping | `audit_rows_mux.py` | 3.06M column-class pairs | 0 mismatches, all caps ≥ 0 |
| the two CNFs | `outer/live-06.cnf`, `outer/live-20.cnf` | sha256 | `f8a6e2d9…` (3 501 416 vars / 7 603 287 clauses), `37317a1d…` (2 465 649 / 5 316 320) |

`#print axioms` output, verbatim:

```
'R3333.Live06.support_covered' depends on axioms: [propext, Quot.sound]
'R3333.Live06.count_rights' does not depend on any axioms
'R3333.Live20.support_covered' depends on axioms: [propext, Quot.sound]
'R3333.Live20.count_rights' does not depend on any axioms
```

## Not verified, and open

* The glue (steps 2, 4, 5's "class members avoid the anchor colours", 6, 7) is prose, not
  Lean.  Every *finite* ingredient is machine-checked; the composition is not.
* The price file, the row masks, the palettes and the poles are **read** from the archive,
  not derived here.
* **No board closes.**  Both count models and both counted-form models were attacked and are
  OPEN; the exact budgets, proof sizes and conflict counts are in "Probes that did not decide
  anything" below.  Those are budget stops, not evidence.
* Claim (a) (one fixed vector unrealizable) and claim (c) (a seed) are untouched.
* Refuted conjecture, recorded so nobody repeats it: "H42 minus any single vertex has no
  ordinary response" is **false** (`lemmas/F5-refuted-H42-one-c-spoke-p*.cnf` are SAT for all
  14 positions).  Consequently an outsider may have exactly one `c`-neighbour on a side; only
  the all-ordinary statement F4 is available, and `N_s(w) ≠ ∅` is the strongest support
  statement in this file.
* The counted checkpoint's `src/unary.py` generator remains uncovered (unchanged from the
  thirteen-board note).

## All fifteen priced boards

With the general indexing in place, the same obligation is discharged for every board that has
a price file, i.e. for **all fourteen open boards** of the 72-board sample.  The thirteen
zero-mux boards are the previous run's scope; `audit_mux.py` recomputes every side condition
for them **independently of that run** and reproduces its numbers exactly, and `validate.py`
shows the general indexing returns its column table unchanged.  `lean-all.log` re-checks all
fifteen Lean tables in this session (`support_covered` ×15 with axioms `propext, Quot.sound`,
`count_rights` ×15 with none, no errors).

| board | mux | rectangles (kept) | columns | dropped rect/col | min charge = scale | capacity | slack | positive lower bounds |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fresh-07 | 0 | 95 (95) | 8619 | 0 / 169 | 10003 | 266712 | 6634 | 1 |
| live-02 | 0 | 116 (116) | 10917 | 0 / 691 | 10003 | 265817 | 5739 | 12 |
| live-06 | **73 at (2,0)** | 86 (86) | 11610 | 0 / 0 | 10004 | 280459 | 20355 | 0 |
| live-07 | 0 | 80 (80) | 495 | 0 / 0 | 10000 | 270000 | 10000 | 6 |
| live-13 | 0 | 132 (132) | 12110 | 0 / 0 | 10004 | 284282 | 24178 | 1 |
| live-14 | 0 | 120 (120) | 672 | 0 / 3 | 10000 | 270000 | 10000 | 6 |
| live-16 | 0 | 90 (90) | 12216 | 0 / 0 | 10003 | 295655 | 35577 | 0 |
| live-17 | 0 | 63 (59) | 2473 | 4 / 3842 | 10003 | 261199 | 1121 | 65 |
| live-20 | **56 at (0,2)** | 75 (75) | 8661 | 0 / 0 | 10004 | 271752 | 11648 | 0 |
| local-09 | 0 | 167 (167) | 18475 | 0 / 0 | 10005 | 297122 | 36992 | 0 |
| local-15 | 0 | 141 (141) | 717 | 0 / 0 | 10000 | 280000 | 20000 | 7 |
| local-17 | 0 | 141 (141) | 14050 | 0 / 0 | 10004 | 282058 | 21954 | 0 |
| local-20 | 0 | 68 (68) | 8539 | 0 / 1 | 10001 | 269798 | 9772 | 5 |
| local-22 | 0 | 98 (98) | 10800 | 0 / 0 | 10004 | 273623 | 13519 | 1 |
| local-24 | 0 | 140 (140) | 12911 | 0 / 0 | 10003 | 293389 | 33311 | 0 |

(`live-17` is closed; the other fourteen are the open sample.)

Consequence, stated to keep the claim levels apart: for each of the 14 open boards, a
DRAT-checked refutation of its outer count CNF — or of that CNF plus cuts each certified on a
*distinct-outsider* reduced instance — yields a **board exclusion** (claim b).  Nothing here
excludes a board or a seed.

## Probes that did not decide anything

Recorded so that nobody repeats them.  None of these is evidence, **and their rates are not
evidence either**: the machine carried load average 13.2 on 4 cores while they ran (eight
swarm members plus the owner's job), so a 90 s CaDiCaL run consumed only 24 s of CPU.  The
"one conflict per second" figures below measure contention, not the difficulty of the formula.

* `outer/live-06.cnf` (pilot form, 3 501 416 vars / 7 603 287 clauses, sha256 `f8a6e2d9…`):
  budget stop after 25 081 conflicts / 118 s, `s UNKNOWN`.
* `outer/live-20.cnf` (pilot form, 2 465 649 / 5 316 320, sha256 `37317a1d…`): budget stop
  after 1 128 conflicts / 116 s, `s UNKNOWN`.
* `outer/counted-live-06.cnf` (counted-checkpoint form, 285 807 / 766 203, sha256 `f2a6cbfc…`):
  budget stop after ~200 conflicts / 112 s.
* `outer/counted-live-20.cnf` (223 513 / 594 338, sha256 `dda700a9…`): budget stop after
  ~116 conflicts / 111 s; the same formula without any DRAT output still did not terminate in
  90 s (`c UNKNOWN`, 24 s of CPU).
* `probe_mip.py`: the count model as an integer program (6741 constraints / 8661 columns for
  live-20, the same constraint set the CNF encodes) — HiGHS produced no primal point inside
  140 s, so not even the LP relaxation finished under this load; abandoned.
* `probe_greedy.py`: randomised repair search for a count vector, 400 restarts per board.  No
  vector found; the best placements leave 85 class-capacity violations on **both** boards.
  That is a lead — the marginal models of these two boards look tightly constrained — but a
  failed search is not infeasibility.

Both counted-form CNFs are small enough (223k and 286k variables) to be worth another attempt
by whoever gets CPU: they are the same generators that refuted live-17 in 10 982 conflicts.
The two `.cnf.gz` files are in `outer/` for exactly that.

## Reproduce

```sh
cd .ultramath/smwmsifse/m6
python3 validate.py                     # general indexing == columns_for on 13 boards; mux boards build
python3 audit_mux.py                    # every side condition, live-06 and live-20 (append board names for the rest)
python3 audit_mux.py fresh-07 live-02 live-13 live-16 live-17 local-09 local-17 local-20 local-22 local-24 live-07 live-14 local-15
python3 audit_rows_mux.py               # CNF bookkeeping == charge bookkeeping, 3.06M pairs
python3 genlean.py && lean RectLive06.lean && lean RectLive20.lean
python3 verify_lemmas.py                # F1..F4, 17 controls, 14 refuted-conjecture instances
python3 outer.py live-06 outer && python3 outer.py live-20 outer
python3 outer_counted.py live-06 outer && python3 outer_counted.py live-20 outer
python3 probe_greedy.py live-20 live-06 # a failed search; not evidence
python3 cut_vars.py live-20 0 1           # u[k,m] mapping and the side-injectivity check
```

`lean-all.log` was produced by running `lean Rect<Board>.lean` on the thirteen modules of
`.ultramath/smwmq7hji/m6/` (read-only, run from that directory) and on `RectLive06.lean` /
`RectLive20.lean` here.

Everything is written under this directory; nothing in the archive or the repository is
modified.
