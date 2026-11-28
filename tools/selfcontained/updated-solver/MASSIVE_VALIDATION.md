# Massive unified solver: tested evidence and boundaries

## Final clean extraction

The fresh zip at `dist/k58-massive-solver-final.zip` was unpacked into a new
workspace with no pre-existing environment. `PIP_NO_INDEX=1 ./k58.sh setup`
fell back to the packaged wheels, installing `python-sat==1.9.dev22` under
Python 3.12.14. Kissat 4.0.4 and drat-trim both passed the bundled doctor, as did
all five bundled stock certificates.

`./k58.sh modified-smoke --deep --out <new-directory>` passed:

- strict K15/native replay, normalization and both models;
- all fourteen first-tier original-parent/emitting-guard/clause recomputations;
- colour native derivation, local word and tamper controls;
- the new mixed stock/square/square-colour cohort, including exact composite
  parent validation and content-addressed store checks;
- historical paired-arm/two5 generation and bounded external-DIMACS solving;
- original-parent false-cube certification with bundled Kissat, retained
  deletion-stripped strict RUP, zero warnings/errors and zero RAT conclusions,
  and truncated-proof rejection.

Its final line was `MODIFIED SMOKE PASSED`. The input archive and stock run,
finalise and production-ledger paths were not changed.

## Specific unified checks

- One worker and two workers both prepared/verified `original`, `square`, and
  `square-color` on row 0. Their bounded reports stayed **OPEN**. Two-worker
  reservation accounting was 12 conservative conflict slots, within a cap of 50.
- A deliberately insufficient total-conflict reservation stopped before a leaf
  search and returned `OPEN_BUDGET_EXHAUSTED`. Re-specifying the budget on resume
  is refused; `--again` creates another attempt instead.
- A four-clause UNSAT toy reached `VERIFIED_UNSAT` with an exported and then
  replayed composed DRAT. Repeated export replays the stored artifact rather
  than overwriting it. A compatibly satisfiable toy reached `VERIFIED_SAT` after
  checking its complete model against the supplied CNF.
- A deliberately weakened different parent was rejected. An empty attempt set
  is not a closed cohort. The tiny earlier truncation test wasn't sufficient on
  its own (unit propagation in the prefix can make a truncated trace can retain a valid derivation prefix).
- Storage self-tests show exact-byte deduplication, correct distinct
  decompressed/raw-carrier digests, empty payload refusal and modified-blob
  rejection. A timeout control kills the entire child process group; the test
  verifies no remaining active child rather than claiming a timeout outcome is
  SAT or UNSAT.

This frontend schedules
bounded exact encodings and verifies their artifacts. A cohort counter is not a
case-cover proof and an `OPEN` result never licences a SAT or UNSAT statement.

## Deliberate limits

No production wall cohort was launched and no whole-cover runtime or speedup is
measured. A square-strengthened or aux-extended parent is ineligible for stock
original-parent finalise merely because its augmented search finished. Complete
closure of a supplied external toy is not a closure of a K58 case. An augmented
SAT model must be projected and rechecked with the original parent; external
models never masquerade as a stock-case certificate.

The archive leaves `dist/k58-solver.zip` and `dist/k58-updated-solver.zip`
untouched. Source build and validation scripts are in this directory; the
handover zip stays under gitignored `dist/`, not in a repository commit.
