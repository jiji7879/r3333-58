# Modified solver validation

The tested artifact is a fresh copy of `dist/k58-solver.zip` with the added
optional modules, not an overwrite of the stock archive. The final archive is
`dist/k58-updated-solver.zip`.

## Clean-extraction environment

Tested in a separate extraction with no pre-existing virtual environment,
using this command only against the archived wheels:

```sh
PIP_NO_INDEX=1 ./k58.sh setup
```

Host interpreter: Python 3.12.14. This caused the expected fallback (no local
index), installed `python-sat==1.9.dev22` from `wheels/`, then printed
`Kissat ok 4.0.4`, `drat-trim ok`, and `example ... "replayed": 5`.

The external CaDiCaL-1.9.5 path is not required by the modified smoke test;
its false-cube certification uses the bundled Kissat.

## Deep modified smoke (`--deep`)

Passed all of the following in the clean extraction:

* exact K15 query/native proof, exhaustive normalization, both model checks,
  independent RUP with deletion records ignored, both rejecting controls;
* all fourteen ordinary-wall first-tier parents reconstructed and hash matched;
  9,287 emitted clauses with zero missing/extra rules, guard and geometry tests,
  4,807 original-propagation survivors across ten rows and four zero-gain rows;
* all six colour-pivot native derivations, 2,914 physical local words and the
  122-step omitted-target-derivation negative control;
* paired-arm short panel regeneration, exact historical `two5` encoding with
  8,533 added clauses/4,923 auxiliaries and SHA-256
  `fe9de879d99b320c57c7d90582842a532a045da9c3d90c8df5880d96498eb9af`;
* two bounded external-DIMACS leaves, retaining their exact augmented parent
  identity and budgets;
* false-cube certification on rank 8 using bundled Kissat, deletion-stripped
  strict RUP, the full normalized proof read, zero warnings/errors and zero RAT;
  a genuine halved proof was also rejected.

The modified smoke result was `MODIFIED SMOKE PASSED`. Its harness asserts all
of these receipts: earlier inert/failing smoke-output checks were corrected
before this test was counted as proof.

## Stock regression smoke

`./k58.sh smoke` also passed in the same clean extraction. It repeated all
five example certificates, closed and certified three sample cases, replayed
three of three with zero failures, rejected a deliberately truncated
certificate, and built the batch plan.

Additional source-control checks exercised separately include full rank-8
transversal generation/filtering (461,679 rules; 3,830 candidates of width at
most six; 3,829 surviving published-propagation) and joint-support discovery
at the explicit local one-conflict cap. The latter is not a cohort default or
an amortized-speedup test and is deliberately not repeated in the smoke test.
A stock CNF supplied for a different named rank is explicitly rejected.

## Deliberate limits

No production wall campaign was performed and no unresolved row, representative,
pivot branch or Ramsey bound was closed. The new commands are optional. Any
strengthened or aux-extended result is labelled accordingly; it is not
silently exported through the ordinary original-parent finalisation pipeline.
No stock ledger or measurement file is changed by the build.
