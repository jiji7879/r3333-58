# Exploratory variants (superseded; kept as evidence)

These scripts are the working history of the 533/724 calibration. They are kept
because two of them document *wrong* reductions, and that is part of the
evidence for the final semantics.

* `census533.py` — Burnside + explicit-orbit count of the FKR Table 5 census
  (533 marked colourings). Correct; its Burnside routine was folded into
  `../run_census.py` as an independent cross-check.
* `overlaps724_old.py` — first (buggy) attempt: a bit-table variable shadowed
  the colour permutation inside `classes()`, so the residual group was wrong.
  Kept only to show that the bug was found and fixed, not to be reused.
* `overlaps724.py` — "fixed-slice" reduction: an overlap class was assumed to
  be (unordered pair of marked-colouring classes, orbit of the linking under
  matching-colour-permutation stabilisers). Gives 609 instead of 724; it is
  *wrong* because a marked-colouring class does not always meet the chosen
  representative slice in a named-colour-preserving way (at k = 2 it gives 4
  where the truth is 7). Kept as the counterexample to that reduction.
* `honest_k2.py` — explicit union-find over labelled triples (A, B, theta) under
  the matching weak groupoid, with no slice reduction. Gives 3 at k = 1 and 8 at
  k = 2. The 8 over-counts by one because the copy swap of the two K16 copies is
  a genuine isomorphism of the glued object and the groupoid of seed
  automorphisms does not generate it for the same-seed family. Kept as the
  counterexample to that model.
* `overlaps_strong_v1.py`, `overlaps_strong.py` — the two-layer split (strong
  colour-preserving classes, then the S_3 colour quotient). `overlaps_strong.py`
  reproduces 724 with per-order profile equal to FKR Table 6, but its canonical
  key minimised over a conjugated group (`c_2 H_2 c_2^-1`), which is not a
  complete invariant; the key collision it can produce is what forced the
  rewrite in `../census_generic.py`. Kept as the record of that failure and of
  the 3900 strong classes that quotient to 724.
* `census_k58.py` — the first K58 driver (16/16 and 15/15). Superseded by
  `../run_census.py`, which additionally carries the brute-force cross-check, the
  Burnside cross-check of the 15-vertex marked census, and the controls. Its
  output `k58_out.json` is the first independent sight of the 15/15 numbers
  (3402 marked, 31283 overlaps) and agrees with the final run.

Nothing here should be imported by new work; the supported entry point is
`../run_census.py`.
