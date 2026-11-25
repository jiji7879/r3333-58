# The count abstraction is sound for local-15, live-07 and live-14

Claim (c) of the task — "a board is excluded" — is normally read off an unsatisfiable
**outer count CNF**.  That reading needs a missing implication: *every* triangle-free
4-colouring of K54 realizing the board's pins must induce a count vector that satisfies the
outer CNF.  This note states that implication exactly, proves it, and records which of its
ingredients are machine-checked here and which are not.

Nothing below produces a cut or a refutation.  It is the coverage obligation that any
board-level use of the outer model has to discharge, and it is discharged for the three
pilot boards under the price files of `checkpoints/counted/data/prices/`.

## Setting

`B` is a board: two palettes (permutations of `{0,1,2}`), poles, and 14 row masks.
K54 has left core `L = {0..13}`, right core `R = {14..27}`, outsiders `O = {28..53}`;
`c := 3` is the fourth colour.  A colouring realizes the pins of `B` when

* `colour(14s+i, 14s+j) = palettes[s][H[i][j]]` for all `i<j<14`, `s in {0,1}`, where `H`
  is `h42.json`, and
* `colour(i, 14+j) = c` whenever bit `j` of `rows[i]` is zero ("pinned to c").

Call a cell `(i,j)` **free** when that bit is one.  `rects(B) = maximal_rectangles(rows)`
is the table of maximal free rectangles used by `columns_for`.

The **outer count CNF** of `B` is `pilot/cnfs/B.cnf.gz` (built by `pilot/make_pilot_cnf.py`,
variables named by `pilot/cnfs/B.counts.json`): one unary chain per column
`(rect, side, signature)` of `columns_for(B)`, per-rectangle balance of the two side totals,
population 26 on the left, class capacities `LIMIT[|anchors|] - inside`, and price lower
bounds.

**Theorem.**  Let `B` be one of the thirteen boards listed under "Scope" and let `col` be a colouring of K54
with **no monochromatic triangle** that realizes the pins of `B`.  Then there is an integer
count for every column of `columns_for(B)` that satisfies **every clause** of the outer
count CNF of `B`.

## Proof

Write `N_s(w) = {v in side s : colour(v,w) = c}` for an outsider `w`.

1. **Both c-supports are nonempty** (`N_0(w) != 0 != N_1(w)`).  If `N_s(w)` were empty,
   all 14 spokes of `w` into side `s` would be ordinary.  No 3-colouring of the 14 spokes
   avoids a monochromatic triangle with `H`, refuted as lemma L3
   (`lemmas/L3-H42-ordinary.cnf`, 16 conflicts, DRAT verified).  Controls:
   `lemmas/L3p-H42-cspoke-p0.cnf` and `lemmas/single-c-support.json` show the statement is
   tight — one single c-spoke at any of the 14 positions makes it satisfiable.
2. **`N_0(w) x N_1(w)` is inside the free cells.**  If `i in N_0(w)`, `j in N_1(w)` and cell
   `(i,j)` is pinned to `c`, then `{w,i,j}` is a monochromatic `c` triangle.
3. **A table rectangle contains both supports.**  By the Lean-checked `support_covered`
   (`RectLocal15.lean`, `RectLive07.lean`, `RectLive14.lean`, Lean 4.33.1, axioms
   `propext`/`Quot.sound` only) the canonical `r = intersect (row a) as` over `N_0(w)` is a
   recorded right support with `N_0(w) ⊆ leftMember r` and `N_1(w) ⊆ r`.  So `w` can be
   **assigned** a rectangle `R` of the table with `N_0(w) ⊆ R.left`, `N_1(w) ⊆ R.right`.
   That is exactly the pin the lift imposes (`lift_counts.pin` forbids any c-spoke outside
   `R`), so the assignment is a choice the lift's formula permits.
4. **The assigned column exists.**  Outside `R` the spokes of `w` are ordinary, and `G` has
   no triangle, so `w`'s ordinary pattern is one of the words `projected_words` enumerates
   for `(side, R[side])`.  Its signature — bit `j` set iff the priced class `j` has all its
   anchors outside `R[side]` and `w` meets all of them — is therefore a key of the `masks`
   table, i.e. `(R, side, signature)` is a pair produced by `columns_for`.  Column *retention*
   also holds: a column is dropped only when `cost(sig) + cheapest other side > cutoff`, and
   the strict inequalities for every dropped column and rectangle are re-checked in
   `audit_model.py` (live-14 drops 3 columns and 0 rectangles; local-15 and live-07 drop
   nothing).
5. **Charging.**  Charge `w` the price of the priced classes its two signatures meet.  Every
   outsider is charged at least `scale` (`audit_model.py` recomputes the minimum over all
   signatures of all rectangles: 10000 = `scale` on all three boards) and the total capacity
   `sum_j price_j * (LIMIT[k_j] - inside_j)` equals the price file's `cost`
   (280000 / 270000 / 270000).  Both `LIMIT` constants come from refuted formulas: `L1`
   (K6, 2 colours) and `L2` (K17, 3 colours, sound symmetry breaking) with `R(3)=3` and
   `K2` trivial; the glue is: vertices meeting the same `k` anchors pairwise avoid those `k`
   colours, so at most `R(3,...,3) - 1` of them fit.  Hence
   `sum_j price_j m_j >= 26*scale` and, for each class, `m_j >= cap_j - slack/price_j`,
   `slack = cost - 26*scale >= 0` (20000 / 10000 / 10000).
6. **Counts.**  Let `cnt(R, side, sig)` be the number of outsiders assigned `R` with that
   signature.  Each outsider contributes one to each side of its own rectangle, so the left
   population is 26 and the two side totals agree on every rectangle.  Class capacities hold
   because every outsider in a column whose implied classes contain `j` meets the anchors of
   `j`, and `m_j <= cap_j` (step 5 with the `LIMIT` lemmas).  The price lower bounds hold by
   `m_j >= cap_j - slack/price_j`, using only columns whose signature bit `j` is set, which
   is *exactly* the sum `C_j` that the capacity constraint of `j` bounds, because for a priced
   class `j` a column's signature has bit `j` set iff its implied-class row contains `j`
   (`audit_rows.py`, checked on local-15, live-07, live-14, live-17 with 0 mismatches over
   4302/3833/5131/301170 column-class pairs).  Charging gives
   `sum_w charge(w) = sum_j price_j C_j >= 26*scale`, so
   `sum_j price_j (cap_j - C_j) <= slack`, hence `C_j >= cap_j - slack/price_j` for every priced
   class — the price lower bound, and for a class that no column implies, `C_j = 0` contradicts
   it, which is exactly the empty clause `bound([], lower)` emits.  Unary chain lengths are
   `min(26, caps)`, implied by the same capacities.  Every clause of the outer CNF is
   satisfied.  ∎

## Scope

The thirteen boards whose price file has all-zero `mux` — `fresh-07, live-02, live-07, live-13,
live-14, live-16, live-17, local-09, local-15, local-17, local-20, local-22, local-24` — all
pass every side condition (`audit-model.json`).  `live-06` and `live-20` have a nonzero
pole-pair price; `implied_spokes.columns_for` refuses them outright, so neither the lift nor
the outer CNF exists for them here and no claim is made.

All thirteen boards have a Lean-checked rectangle table (`Rect<Board>.lean`, one module each,
Lean 4.33.1, axioms `propext`/`Quot.sound` only); `rects.py` additionally checks for the same
boards that the recorded right supports are closed under intersection with every row and that
the table is exactly the set of maximal free rectangles.

Per-board side conditions, from `audit_model.py` and stored in `audit-model.json`:

| board | rectangles (kept) | columns | dropped columns | min charge = scale | capacity | slack | positive lower bounds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fresh-07 | 95 (95) | 8619 | 169 | 10003 = 10003 | 266712 | 6634 | 1 |
| live-02 | 116 (116) | 10917 | 691 | 10003 = 10003 | 265817 | 5739 | 12 |
| live-07 | 80 (80) | 495 | 0 | 10000 = 10000 | 270000 | 10000 | 6 |
| live-13 | 132 (132) | 12110 | 0 | 10004 = 10004 | 284282 | 24178 | 1 |
| live-14 | 120 (120) | 672 | 3 | 10000 = 10000 | 270000 | 10000 | 6 |
| live-16 | 90 (90) | 12216 | 0 | 10003 = 10003 | 295655 | 35577 | 0 |
| live-17 | 63 (59) | 2473 | 3842 | 10003 = 10003 | 261199 | 1121 | 65 |
| local-09 | 167 (167) | 18475 | 0 | 10005 = 10005 | 297122 | 36992 | 0 |
| local-15 | 141 (141) | 717 | 0 | 10000 = 10000 | 280000 | 20000 | 7 |
| local-17 | 141 (141) | 14050 | 0 | 10004 = 10004 | 282058 | 21954 | 0 |
| local-20 | 68 (68) | 8539 | 1 | 10001 = 10001 | 269798 | 9772 | 5 |
| local-22 | 98 (98) | 10800 | 0 | 10004 = 10004 | 273623 | 13519 | 1 |
| local-24 | 140 (140) | 12911 | 0 | 10003 = 10003 | 293389 | 33311 | 0 |

`live-17` is the one board where the charge argument actually bites: 4 of its 63 rectangles
and 3842 columns are dropped as unaffordable, 65 classes get a positive lower bound, and the
slack is only 1121.  That is consistent with its outer model being the only unsatisfiable one
in the archived fifteen.

## Composition: from the outer model to a board exclusion

1. **Fixed vector unrealizable** (claim a).  A DRAT-checked refutation of one lift
   `pilot/lifts/B-<stage>` refutes that vector only.
2. **Board excluded** (claim b).  Given (i) the theorem above, (ii) a certificate for each cut
   added to the outer CNF (`CUTS.md` states when the reduced-instance refutation really is
   one), and (iii) a DRAT-checked refutation of `outer(B) + cuts`, no triangle-free colouring
   realizes the pins of `B`.
3. **Seed excluded** (claim c) needs the seed's own coverage of all its boards and placements.
   Nothing here touches it.

## What this buys, and what it does not

* It is **not** claim (a) (one fixed vector unrealizable) and **not** a cut.  It says that a
  board is excluded as soon as *the outer CNF together with justified cuts* is unsatisfiable:
  the census route (every vector refuted) and the cut route (outer + cuts UNSAT) both become
  board exclusions, because every allowed graph induces one of the vectors under discussion.
* The **glue** in steps 2, 4 and 6 is short human mathematics, not Lean.  Machine-checked
  ingredients: `Rect*.lean` (step 3, whole rectangle table), `lemmas/report.json` (L1, L2,
  L3 and their controls), `audit-model.json` (all per-board arithmetic: minima, capacity
  totals, cutoffs, dropped-column inequalities, nonnegative capacities).
* **Unverified**: that the *price file* of a board is the price file the archive intends (it
  is read, not derived), and the exact clause-level correspondence between the lift's `pin`
  and the outer CNF columns, which is checked only through shared code
  (`implied_spokes.columns_for` is used by both `lift_counts.py` and `make_pilot_cnf.py`).
* **Not covered**: the *counted checkpoint's* richer generator `checkpoints/counted/src/unary.py`
  (`pure-<board>.cnf`).  Its defect variables, per-rectangle population bounds `S // delta`,
  per-column bounds `S // over` and rounded budgets `sum (w*level)//S <= level` are all sound
  by the same charge argument, but it also bounds a rectangle's population by
  `table[m.bit_count()]` (and, in `standalone` mode, by a greedy `cover_cap`), and I have not
  justified that table.  Anything built with `pilot/make_pilot_cnf.py` is covered; anything
  built with `src/unary.py` is not.
* My own attempt to refute `live-17` with the covered generator (`pilot/make_pilot_cnf.py`,
  618578 vars, 1337381 clauses, sha256 dc67b5da...) was still OPEN after 254935 conflicts /
  400 s, so the covered generator alone is not strong enough to close even live-17; the
  counted checkpoint needed its extra constraints.  This is a budget stop, not evidence.
* Seed-level claims are untouched: 12 seeds remain open, and a board exclusion is not a seed
  exclusion.

## Reproduce

```sh
cd .ultramath/smwmq7hji/m6
python3 rects.py local-15 live-07 live-14 live-17   # rectangle tables are closures
lean RectLocal15.lean && lean RectLive07.lean && lean RectLive14.lean
python3 verify_lemmas.py                            # L1, L2, L3, controls, DRAT replay
python3 audit_model.py                              # every numeric side condition
```

Hashes of the refuted inputs are in `lemmas/report.json`; the Lean tables print their
rectangle counts, 141 / 80 / 120, and `count_rights` proves them duplicate-free.
