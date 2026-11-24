# Separate spoke caps on row 4629: U ≤ 24 and V ≤ 24

Bundle: `K58_spoke_caps24_solver_and_replay.zip` (46.9 KiB), unpacked at `.scratch/sc24/spokes/`.
The proof volumes are **not** shipped, but the package has a regeneration path
(`replay.py --kissat`), so the 116 refutations are being regenerated rather than replayed.

## What it claims

On row `4629be2de806` — one of the two original published rows, and **not** one of the five rows the
19-spoke work covers — every completion satisfies **`U ≤ 24` and `V ≤ 24` separately**, each allowing
the opposite pentagon any count. This is strictly stronger than the earlier sum bound `U + V ≤ 48`:
of the 51 ordered pairs with a `25` coordinate, the sum bound removed 3 and the separate caps remove
all 51, leaving `(24,24)` as the only survivor at total 48.

## The argument's shape

A pentagon position is **saturated** when all five `F(p) = N_1(p) ∩ A` have size 5, giving 25 spokes.
The five `F(p)` can only be the three sets the judge verified earlier on this row for the high-branch
bundle — `(2,3,6,8,13)`, `(6,9,12,13,15)`, `(8,10,11,13,15)` — so a saturated pentagon is a
five-digit word, 243 words, 126 reflection representatives. Completing the arm gives a 36-vertex
board and **every representative dies on it**: 0 of 8 surviving for `C*`, 0 of 27 for `D*`. The
remaining obstruction uses the third arm (the 13 edges from the mark into `B`, split `3+3+3` by
colour), giving a 45-vertex board on which all 27 `D` representatives and 7 of 8 `C` representatives
have direct refutations; the last `C` word `10120` is reflection-invariant and is closed by 21
refutations of star pairs.

## Verified here so far

```
python3 replay.py                     # witnesses, reflection cover, numerical conclusions
  C 15 local patterns; surviving representatives at opposite floors 0 and 23: [[], []]
  D 51 local patterns; surviving representatives at opposite floors 0 and 23: [[], []]
  Balanced core and larger-board exclusions: {'30': [72, 22], '31': [60, 20], '33': [31, 9]}

python3 replay.py --hash-only          # reconstructs every CNF, 116 manifest entries, no mismatch
```

So the witness audit, the reflection cover, the numerical conclusions and every CNF reconstruction
pass. The 116 DRAT traces are being regenerated with the bundled Kissat and checked with `drat-trim`;
that result is recorded when it lands.

## The balanced case remains open

At `(24,24)` each pentagon has one four-set and four five-sets. Of 207 core words, 163 are realised
on the core and 51 are excluded, leaving **112 representatives**, of which one (`020x2`) was refuted
at 110,000 conflicts and **112 returned OPEN**. So the top of the row's range is not closed: the
package is explicit that a listed word can still fail as more arms are joined, and the four bounded
integrated runs (1M and 750k conflicts) all returned OPEN with no measured speedup.
