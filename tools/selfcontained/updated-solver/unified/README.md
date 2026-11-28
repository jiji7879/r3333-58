# Unified massive research frontend

Bounded variant selection, not a promise to solve the whole wall.

```sh
# Inspect a mixed plan without generating formulas or searching.
./k58.sh unified run --rows square:0 --variants original,square,square-color \
  --out results/cohort --depth 1 --seconds 1 --conflicts 1 \
  --max-total-conflicts 50 --wall-seconds 20 --check-seconds 8 \
  --workers 2 --dry-run

# Execute/resume the frozen plan, rechecking saved parent/proof artifacts.
./k58.sh unified run --out results/cohort
./k58.sh unified verify --out results/cohort
./k58.sh unified status --out results/cohort

# Byte-integrity checks, not proof/case classification.
./k58.sh store check --store results/cohort/store
./k58.sh store adopt --source results/cohort/store/blob.cnf \
  --store results/adopted --expected-sha256 REPLACE_WITH_REAL_HASH
```

`original`, `square`, `counter`, `escape`, and `color` are supported on frozen
first-tier rows; square variants additionally require one of the fourteen
audited ordinary rows. Combining square with colour never renumbers counter
variables. Other tiers, row families and derived-CNFs fail rather than fall
back to an ordinary parent.

Plan budgets are frozen. `--workers` permits 1–16 concurrent subprocesses
(one leaf solver each). A two-worker test on three row-0 variants stayed OPEN,
as intended at one conflict. A different budget requires a new cohort directory;
`--again` makes a fresh attempt rather than overwriting one. Reports and proof
refs live under `jobs/<attempt-id>/jobs/<job-id>/`.

`store` deduplicates actual bytes under a content hash. It does not deduplicate
logical K58 cases or reuse a closure because a filename mentions a row.
Decompressed proof digests are separate from raw compressed-carrier digests.
GC is not performed and adoption is never a proof.

For an external, tiny control file:

```sh
./k58.sh unified run --external unsat.cnf --variants external \
  --out results/toy-unsat --depth 1 --seconds 2 --conflicts 100 \
  --max-total-conflicts 1000 --wall-seconds 20 --check-seconds 5
```

This verifies a closure of the supplied toy, not of a K58 ledger case.
