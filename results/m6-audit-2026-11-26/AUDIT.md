# m6 / d8 — independent audit

Accepted only as three augmented original-tree leaf refutations, four
marked-free equal-kind parents, and exact counting delimitations. There is no
full row/profile closure and no completed end-to-end encoder bridge.

## Checks run here

For precision, the m6 verdict said 22 manifest hashes; the actual manifest has **21** entries, and all 21 passed.

- `sha256sum -c MANIFEST.sha256`: **all 21** listed inputs and three proof files
  matched (`manifest-check.log`).
- Fresh reruns of `validate_genkind.py` for `gen-TT.cnf`, `gen-UU.cnf`, and
  their reciprocal variants: **four/four passed**, with zero leftovers and zero
  failures (`parent-validation.log`). The mixed clone cap is not used for equal
  kinds. These are marked-free reciprocal/inactive parents, not ordinary
  marked-row parents and not strict/mixed/balanced-active closures.
- `validate_dcap.py` passed on both n017 and n022: **310,184** new cap clauses
  each (`validate-dcaps.log`). Literal degree caps follow from
  `three_colour_seventeen`, not the weaker familyA caps (which need $c\ne q$).
- `audit_leaf_metadata.py` rebuilt the exact root+cube formulas and checked
  bare/augmented input and proof SHA-256 values, manifest receipts and the
  three retained successful verification logs. The fresh theorem is n024; its
  raw DRAT was independently replayed here against its hash-matched 1,474,596
  clause CNF: **`s VERIFIED` in 264.330 seconds** (`replay-n024.log`). The n017
  and n022 retained verified receipts were checked without another redundant
  long replay. The original frontier has only `n025` left after these three;
  m7's separate later three-cube refinement is described in the final handoff.
- Both count-model witnesses (`counting-witnesses.json`) are nonnegative and
  satisfy every listed inequality in exact `Fraction` arithmetic: **1,324**
  inactive and **1,495** reciprocal inequalities with **912** variables. No
  floating-point optimality claim is needed to establish the delimitation.
- Exactly 12 profiles arise from $d_0,d_1\in\{15,16\}$, $d_2,d_3\le14$ and
  total 57 (`coverage.json`). The support/C4 statements were read with their
  actual critical-source hypotheses; the $c=q$ cross-arm cap is not asserted.

The four parents and n025 remain unrefuted. No solver timeout or countermodel
was promoted to a proof.
