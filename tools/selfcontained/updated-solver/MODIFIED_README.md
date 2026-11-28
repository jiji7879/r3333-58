# K58 solver — modified, opt-in research build

This is a copy of `dist/k58-solver.zip`; the original archive is not replaced.
All original commands, including `setup`, `run`, `wallcc`, `finalise` and
`replay`, retain their existing production paths. The new commands are
**explicit variants**, not global settings:

```sh
./k58.sh square rows
./k58.sh square verify --out results/square/checks
./k58.sh square run --index 0 --conflicts 40000 --out results/square/row0
./k58.sh square export --index 0 --out results/square/row0.cnf \
  --receipt-dir results/square/export-checks

./k58.sh color-wallcc rows --profile 15,15,14,13 --limit 5
./k58.sh color-wallcc prepare --row 00032f347903 --tier first \
  --pivot-color color --depth 1 --out results/color/row0 \
  --checker "$PWD/bin/drat-trim"
./k58.sh color-smoke --out results/color-selftest

./k58.sh armcap build --family short --rank 1288 --out results/armcap/panel
./k58.sh armcap build --family two5 --rank 1300 --out results/armcap/two5
./k58.sh armcap build --family transversal --rank 1300 --out results/armcap/transversal
./k58.sh armcap run --cnf results/armcap/two5/1300-two5.cnf \
  --out results/armcap/run --depth 1 --seconds 60 --conflicts 200000
./k58.sh armcap finite-check
./k58.sh armcap export-stock --rank 8 --out results/armcap/rank8-stock.cnf
./k58.sh armcap certify --rank 8 --clause=-24663,1056,2428,6024   --stock results/armcap/rank8-stock.cnf --out results/armcap/certify-r8   --checker "$PWD/bin/drat-trim"  # uses bundled Kissat by default

./k58.sh unified run --rows square:0,square:25557   --variants original,color,square,square-color   --out results/unified-cohort --depth 1 --seconds 10 --conflicts 1000   --workers 2 --dry-run
./k58.sh unified run --out results/unified-cohort --seconds 10 --conflicts 1000
./k58.sh unified verify --out results/unified-cohort
./k58.sh unified status --out results/unified-cohort

./k58.sh modified-smoke --out results/modified-smoke
```

## What is actually included

* **Square spokes** (`square_spoke/`): exact `next/`, `hard-study/` and
  `hard-more/` sources from the supplied square archive, all fourteen batches,
  witness data and models. The strict driver reconstructs the parent with
  `tables=True,total_critical=True,full_root=False`; it does not rely on the
  original bundle's blind `verify.py` or its `-w` proof checks. It independently
  pinpoints guard sender/colour/candidates, tests both directions of the
  cardinality block, compares the complete generated set with the stored set,
  and runs strict native K15 replay and exhaustive normalization/model checks.
* **Colour-resolved wall** (`color-resolved-wallcc/`): the separate certified
  physical-pivot layer and its audited 240-configuration cache. This is
  available only with `--row --tier first`. Its CLI takes `wallcc`'s usual
  subcommands and the new `--pivot-color counter|escape|color` setting.
* **Historical paired arms** (`paired_arm/`): source/code for short, wide-delta,
  four-only, transversal, lower-bound and `two5` variants. These apply only to
  the 1,300 historical **full-root** inputs. The scripts do not use missing
  historic proof bytes and do not select unresolved wall profiles by accident.
  `armcap run` is a bounded, ordinary external-DIMACS `wallcc` invocation, not
  a shortcut to an original-row certificate.

## Unified bounded cohorts

`unified run --rows ...` creates an immutable list of `(row,variant)` job IDs
before any search. `--rows` accepts full/unique wall-row prefixes and
`square:INDEX`. `--profiles 15,14,14,14` is a deliberately explicit large
selection; it is never the default. `--limit`, `--shards`/--`shard`,
`--workers`, and positive `--seconds`/`--conflicts` control the actual bounded
search. Without an explicit selector the command will refuse an unknown new
output directory. Plan budgets are frozen: resume with only `--out`, optionally
adjusting `--workers` or raising `--min-free-gb`. **Raising a budget requires a
new cohort directory**, and `--again` deliberately makes a fresh attempt instead
of overwriting one. `--wall-seconds` bounds the whole child process group,
`--check-seconds` bounds drat-trim, and `--max-total-conflicts` caps the
conservative total conflict reservation for the invocation (including a
search-plus-trace estimate); native leaf caching may re-use fewer actual conflicts.
`--limit 0` is rejected, never interpreted as an unbounded cohort.

The `color` family has the native original-plus-counter derivation. `square`
adds the audited K15 rules, and `square-color` appends exactly those rules to
the colour-extended parent without renumbering its auxiliaries. Counter, escape
and full colour can also be combined this way, but only for the fourteen named
square rows on tier `first`. Recipe/tier mismatches and unsupported rows fail.
The composite has a separately checked parent hash and separate derivation/
K15 evidence, not a monolithic original-parent certificate.

Use `--dry-run` to print the plan without generating formulas or searching.
`status` summarizes saved jobs. `verify` re-runs the ordinary model/leaf/parent
checks and exits 2 if subtrees remain OPEN. Each job's `unified-result.json`,
child `plan.json`, colour/square receipts and leaf artifacts are retained. Any
hash, receipt or executable failure disqualifies promotion. The cohort is not a
Ramsey-cover tautology checker: an `OPEN` status is unknown, not SAT or UNSAT;
only `original` can be individually eligible for an eventual original-row
finalisation even when all its leaves are VERIFIED_UNSAT. All new layers keep
`finalise` incompatible with strengthened and auxiliary-extended searches.

External DIMACS is supported with `--external FILE --variants external`.
Its normalized source hash is rebound on resume, and model/leaf verification
remains a statement about that supplied file, not a K58 parent classification.
The paired/historical toolkit continues to use `armcap`, with its separate
full-root/historical contract; it is not relabelled as this first-tier cohort.
`--min-free-gb 10` is the default free-disk guard. Workers each run one solver.

## Verification and proof ceilings

* `square verify --deep` additionally reruns the independent strict-RUP trace
  with deletion records ignored and actual rejecting controls. Without
  `--deep`, native original replay and `-p -U -W` are both enforced, the path
  formula is rejected, all K15 normalization and model checks run, and every
  selected parent/emitting-guard/clause binding is re-derived.
* Square strengthened CNFs keep the original body and change the header/clause
  count only when emitting. `STRENGTHENED_UNSAT` does **not** imply UNSAT of
  the original parent, a wall closure, or a Ramsey result. No square result is
  eligible for `finalise`'s stock-release promotion.
* Paired-selector and colour augmentations may introduce auxiliaries. A proof
  of that formula has aux-extended-parent scope and is not silently relabelled
  as a monolithic original-parent proof. The color native derivation, run plan,
  leaf checks and paths remain available in their own run directories.
* Paired/transversal benchmark gains on historical closed inputs are not a
  campaign-wide result. `armcap finite-check` verifies abstract selector and
  $R(3,3)=6$ conditions but does not provide a per-case augmented-to-original
  proof lift. `verify-selection` expects a panel with both rank 1288 and 1162
  generated by `generate_selection.py`.
* `certify` defaults to the bundled Kissat; `--engine cadical --cadical /path/to/cadical`
  explicitly selects an external native CaDiCaL. Truncation is tested on every
  accepted proof. `certify` is the strict one-clause path: supply the exact stock parent and
  the clause to its helper; it attempts a native refutation of the false cube
  and then checks with `-i -U -W`, no `-w`.

All write tests use caller-selected new output paths. Existing production
ledgers, shared package inputs, supplied measurements and stock receipts are
never rewritten by the new preprocessing commands.

## Discovery cost warning

`armcap build --family joint-support ...` may issue thousands of SAT calls.
`--query-conflicts` caps each query, not the whole wall-clock search or its
amortization cost. It is intentionally excluded from the smoke test.

## Attempts, models and storage

Each attempt gets its own `jobs/<attempt-id>/jobs/<job-id>/` directory. A reopen
of an existing attempt still rechecks its saved artifacts; `--again` yields a
new attempt with a suffix rather than exposing a different search as the same
evidence. A complete cover needs both native leaf verification and an exported,
replayed DRAT. Cohort verification checks the same composed proof again and
rejects an empty attempt set or a wrong/weakened parent.

SAT leaf results are projected onto the original variables and rechecked with
the exact original first-tier CNF. Counts of `verified_case_models` include only
that original-parent validation; an external DIMACS model is subject to its
exact supplied parent and remains external. A model can be proved without a
whole-column cover; it is not rewritten as a leaf-closed subproblem.

The cohort-level `store/` hashes CNFs, proof carriers and models, and deduplicates
them by raw bytes using immutable blob paths. Metadata distinguishes raw carrier
hash, decompressed proof hash and regenerated/formula digests. `store adopt`
indexes bytes as `stored-untyped`, not as trusted evidence or a K58 parent;
`store check` verifies blob integrity, not semantic sufficiency. There is no GC,
no 64-hex row-ID lookup, and no claim that scanning an old directory certifies
its artifacts or preserves historical cases.

Small fixtures are under `unified/test_store.py` and `unified/test_controls.py`.
They exercise duplicate compression payload hashes, empty/tampered rejection,
and a complete child process-group timeout. They do not start a solver campaign.
