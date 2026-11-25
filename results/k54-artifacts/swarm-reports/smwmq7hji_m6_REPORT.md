# m6 / direction d9 — coverage of the count abstraction

What follows is everything I verified, what it is worth, and what is still open.  Nothing here
produces a cut or closes a board; it supplies the implication that any *board-level* use of
the outer count model needs.

## Verified

1. **Rectangle coverage, Lean-checked, 13 boards.**  `RectFresh07.lean`, `RectLive02.lean`,
   `RectLive07.lean`, `RectLive13.lean`, `RectLive14.lean`, `RectLive16.lean`,
   `RectLive17.lean`, `RectLocal09.lean`, `RectLocal15.lean`, `RectLocal17.lean`,
   `RectLocal20.lean`, `RectLocal22.lean`, `RectLocal24.lean`.  Each proves
   `support_covered`: for any two nonempty products of free crossing cells, some recorded
   right support `r` contains the right support and every left vertex of the product contains
   all of `r`.  Lean 4.33.1; `#print axioms` gives `propext, Quot.sound` only.
   Generators: `rects.py`, `genlean.py`.  Run: `lean RectLocal15.lean` (31 s; the table checks
   are `by decide`).
2. **The finite Lemmas the counting needs, DRAT-checked.**  `verify_lemmas.py` writes
   `lemmas/report.json`:
   * `L1` K6 with 2 colours, no monochromatic triangle — UNSAT, `drat-trim` verified, 21
     conflicts, sha256 `a60bc7ef…` ⇒ `R(3,3)=6` ⇒ `LIMIT[2]=5`.
   * `L2` K17 with 3 colours — UNSAT, verified, 1888 conflicts (Kissat), sha256 `9e11bf34…`
     ⇒ `R(3,3,3)=17` ⇒ `LIMIT[1]=16`.  Without symmetry breaking the same formula is open
     after >3M conflicts; the breaking used is sound: apply a colour permutation, then a
     vertex permutation fixing vertex 0, so the colours of the edges at vertex 0 are monotone
     and the first is colour 0.
   * `L3` H42 plus one vertex joined by all-ordinary spokes — UNSAT, verified, 16 conflicts,
     sha256 `719e32ae…` ⇒ every outsider has a c-spoke on each side.
   * Controls: K5 and K16 SAT; H42 plus one vertex with a single c-spoke at `p` is SAT for
     every `p` in 0..13 (`lemmas/single-c-support.json`), so `L3` is tight.
3. **Board data sanity** (`audit_pins.py`): `h42.json` is a symmetric triangle-free
   3-colouring of K14; every palette is a permutation of `{0,1,2}`; every table rectangle is
   free and its left side is exactly the set of rows containing its right side.
4. **Price/charge side conditions, 13 boards** (`audit_model.py`, `audit-model.json`): every
   outsider's minimum charge over all signatures of its rectangle equals the price file's
   `scale` (10000–10005); the recomputed capacity `sum_j price_j (LIMIT-inside)` equals the
   file's `cost`; the slack `cost - 26*scale` is nonnegative (1121 for live-17, 24178 for
   live-13); and **every** dropped rectangle and dropped column satisfies the strict
   inequality `cost + cheapest other side + 25*scale > capacity` that makes it unusable.
   live-17 drops 4 rectangles, 3842 columns and has 65 positive lower-bound classes; the
   pilot boards drop at most 3 columns.
5. **The coverage theorem** (`COVERAGE.md`, proof included): for these thirteen boards, every
   triangle-free 4-colouring of K54 that realizes the pins induces an integer count for every
   column of `columns_for(B)` that satisfies **every clause** of the outer CNF built by
   `pilot/make_pilot_cnf.py`.  The only ingredients are (1), (2), (4) plus short graph
   arguments (c-supports nonempty; their product lands in free cells because a pinned c
   crossing with two c-spokes would be a c-triangle; the assignment keeps both signatures of
   one outsider at the same rectangle, which is exactly what the per-rectangle balance and the
   population-26 constraint read).
6. **The cut-side coverage obligation** (`CUTS.md`, `cut_witness.py`): a reduced instance that
   pins one distinct outsider per column proves a cut over the count variables only if no two
   columns of the cut share a rectangle on opposite sides; otherwise one outsider can witness
   two literals and the pinned instance is a stronger hypothesis.  `cut_witness.py` decides
   this and, when it fails, prints the case split that has to be refuted instead (for three
   columns: at most four instances).
7. **The signature-bit / implied-class equivalence** (`audit_rows.py`, 0 mismatches over
   4302 / 3833 / 5131 / 301170 column-class pairs on local-15, live-07, live-14, live-17):
   for a priced class `j`, a column's signature has bit `j` set exactly when that column's
   implied-class row contains `j`.  This is what turns the archive's price lower bound into the
   charge bound `C_j >= cap_j - slack/price_j` and keeps step 6 of the coverage proof honest.
8. **Independent replay of m3's three certificates** (f7, f11): `build/drat-trim` exits 0 on
   `red-local-15.cnf` (sha256 `375d21e3…`), `red-live-14.cnf` (`7d8e6c09…`) and
   `red-live-07.cnf` (`6a58a50f…`); their column sets are side-injective (all columns of a cut
   on one side), and the unary literals they claim are exactly the chain heads I read from
   `pilot/cnfs/*.counts.json`: 1670/1482/451, 110/27, 423/337.

## Not verified, and open

* The glue in steps 1, 2, 4, 6 of the proof is human mathematics.  Every *finite* ingredient
  is machine-checked, but the composition is not in Lean.
* The price files are read as given; they are not derived or checked against the counted
  checkpoint's derivation.
* The counted checkpoint's richer generator `checkpoints/counted/src/unary.py`
  (`pure-<board>.cnf`) is **not** covered.  Its defect, per-rectangle `S//delta`,
  per-column `S//over` and rounded-budget constraints are sound by the same charge argument,
  but its rectangle population bound `table[m.bit_count()]` is not justified by anything here.
* No board closes.  m3 reports the outer model plus each certified cut still SAT, and my
  attempt to refute live-17 with the covered generator alone (`counted-live17/live-17.cnf`,
  618578 vars, 1337381 clauses, sha256 `dc67b5da…`) was a budget stop: OPEN after 254935
  conflicts / 400 s.  That is a budget stop, not evidence.
* Claim (c), seed exclusions, is untouched.
* Dead end recorded: a direct whole-board CNF (`mkdirect.py`: 5283 vars, 80008 clauses,
  sha256 `5d8092e9…` for local-15) is not refutable in minutes — 300004 conflicts on live-17
  in 10 s and open, matching `checkpoints/counted/README.md`.

## Reproduce

```sh
cd .ultramath/smwmq7hji/m6
python3 rects.py                       # rectangle tables are closures
python3 genlean.py && lean RectLocal15.lean   # (or any Rect*.lean)
python3 verify_lemmas.py               # L1, L2, L3, controls, DRAT replay
python3 audit_pins.py                  # board data sanity, all 15 boards
python3 audit_model.py local-15 live-07 live-14   # side conditions (add boards as wanted)
python3 audit_rows.py                  # signature bit <=> implied-class row
python3 cut_witness.py local-15 354 323 70        # witness injectivity of a cut
```
