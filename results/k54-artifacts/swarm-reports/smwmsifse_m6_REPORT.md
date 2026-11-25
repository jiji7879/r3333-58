# m6 / d4 — the coverage keystone reaches the pole-pair boards

What is verified, what it is worth, and what is still open.  Nothing here produces a cut or
closes a board: it supplies the implication that any *board-level* use of the outer count
model needs.

## The gap this closes

The previous run proved (`.ultramath/smwmq7hji/m6/COVERAGE.md`) that for the thirteen boards
whose price file has all-zero `mux`, every triangle-free 4-colouring of K54 realizing the
board's pins induces counts satisfying every clause of the outer count CNF.  Two of the
fourteen open boards were left out, because the archive's column routine refuses them:

```
pilot/implied_spokes.py:76:  raise ValueError("This indexing routine requires zero pole-pair prices.")
```

`live-06` (price `mux[6] = 73`) and `live-20` (`mux[2] = 56`) were the two, so for those boards
nothing tied the graph to the count model at all.

## Verified

1. **The general (pole-pair) indexing.**  `muxcol.columns_for_general` is the archive routine
   with one change: a word's retention price adds `mux[3c+d]`, where `c` and `d` are the
   ordinary colours of the outsider's spokes to side 0's and side 1's pole, and the cheapest
   pairing over `d` is taken.  A rectangle is kept iff its cheapest full charge is at most
   `cost - 25*scale`; a column likewise.  `validate.py`: on **all thirteen** zero-mux boards
   the output is **identical to `implied_spokes.columns_for`**, element for element and in
   order (495, 672, 717, 2473, 8619, 10917, 12110, 12216, 18475, 14050, 8539, 10800, 12911
   columns).  On the two mux boards it produces 11610 and 8661 columns, so their outer CNFs
   now exist (`outer/live-06.cnf` 3 501 416/7 603 287, `outer/live-20.cnf` 2 465 649/5 316 320,
   with `counts.json` variable maps ready for cuts).

2. **The coverage theorem for live-06 and live-20** (`COVERAGE-MUX.md`, proof included): every
   triangle-free 4-colouring of K54 realizing the board's pins induces an integer count for
   every column that satisfies **every clause** of the outer CNF.  The pole-pair class is
   handled as a two-anchor class with anchors in *different* sides — the same lemma as the
   one-sided classes, giving capacity `16` when the two pole colours agree and `5` when they
   differ — and it is used only in the charge/slack test, which on these two boards is vacuous
   (no rectangle, no column and no price lower bound is dropped or emitted).

3. **All fifteen priced boards.**  `audit_mux.py` recomputes every side condition for the other
   thirteen boards **independently of the previous run** and reproduces its numbers exactly
   (`audit-mux.json`).  `lean-all.log` re-checks all fifteen Lean rectangle tables in this
   session: `support_covered` ×15 with axioms `propext, Quot.sound` only, `count_rights` ×15
   with no axioms, no errors.  So the 14 open boards of the sample all carry the implication.

4. **The finite lemmas, DRAT-verified here** (`verify_lemmas.py`, `lemmas/report.json`):
   * `F1` K6 / 2 colours UNSAT — 21 conflicts, `s VERIFIED`, sha256 `a60bc7ef…` ⇒ `R(3,3)=6`;
   * `F2` K17 / 3 colours UNSAT — 1888 conflicts, `s VERIFIED`, sha256 `9e11bf34…`
     ⇒ `R(3,3,3)=17` (symmetry breaking: sort the colours at vertex 0, then set the first to 0;
     both steps are automorphisms, so a sorted representative always exists);
   * `F3` K3 / 1 colour UNSAT ⇒ `R(3)=3`, and `K2` with no colour ⇒ `LIMIT[4]=1` needs nothing;
   * `F4` H42 + one all-ordinary vertex UNSAT — 16 conflicts ⇒ every outsider meets `c` on each
     side;
   * 17 SAT controls (`K5`, `K16` sorted, `K2`, and one `c`-spoke at each of the 14 positions).

5. **The numeric side conditions** (`audit-mux.json`): recomputed capacity total equals the
   price file's `cost` including the pole terms (280459 = 280094 + 365; 271752 = 271472 + 280);
   the minimum charge of one outsider over every signature of every rectangle equals `scale`
   (10004) on both boards; slack `20355` and `11648`; **zero** rectangles dropped, **zero**
   columns dropped, **zero** positive price lower bounds.  The largest column price is 18219
   against a cutoff of 30359 (and 29994 even with the pole terms deleted), so the retention of
   these two boards does not depend on the mux convention at all.

6. **Bookkeeping** (`audit_rows_mux.py`): over 3 061 064 column–class pairs, a column's
   signature bit is set exactly when its CNF-side implied-class row carries that class; all
   capacities nonnegative.

## Not verified, and open

* The composition in `COVERAGE-MUX.md` steps 2, 4, 6, 7 is prose, not Lean.  Every *finite*
  ingredient is machine-checked; the glue is not.
* The price files, row masks, palettes and poles are **read** from the archive, not derived.
* **No board closes.**  Both count models and both counted-form models are OPEN (budget
  stops, not evidence): 25081 conflicts / 118 s on the live-06 pilot form, 1128 / 116 s on the
  live-20 pilot form, ~200 / 112 s and ~116 / 111 s on the counted forms.  The rates are
  contention artefacts: the machine carried load average 13.2 on 4 cores during those runs (90 s
  of CaDiCaL bought 24 s of CPU), so they say nothing about how hard the formulas are.  The two
  counted-form CNFs (223k and 286k variables) are the same generators that refuted live-17 in
  10 982 conflicts and are worth another attempt by whoever gets CPU.
* A randomised repair search (`probe_greedy.py`, 400 restarts) never placed 26 outsiders
  within the class capacities on either board (best residual violation 85 classes on both).  A
  lead that the two marginal models are tight, nothing more.
* Refuted conjecture, recorded so nobody repeats it: "H42 minus a single vertex has no ordinary
  response" is **false** — `lemmas/F5-refuted-*.cnf` are SAT at all 14 positions.  So an
  outsider can have exactly one `c`-neighbour on a side; `N_s(w) ≠ ∅` is the strongest support
  statement available, and a "≥2 c-spokes" strengthening must not be assumed.
* The counted checkpoint's `src/unary.py` generator is still uncovered (unchanged).

## Reproduce

```sh
cd .ultramath/smwmsifse/m6
python3 validate.py
python3 audit_mux.py live-06 live-20
python3 audit_rows_mux.py
python3 genlean.py && lean RectLive06.lean && lean RectLive20.lean
python3 verify_lemmas.py
python3 outer.py live-06 outer && python3 outer.py live-20 outer
python3 outer_counted.py live-06 outer && python3 outer_counted.py live-20 outer
```
