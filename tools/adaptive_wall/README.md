# Adaptive K58 wall queue and proof-learning prototypes

This directory consolidates the accepted components of Ultramath run
`smwy2754s`. It is a tested **prototype**, not a running whole-wall campaign
and not a claim that any complete profile is closed.

## Components

- `case_queue.py` — SQLite open-case/task queue with content-addressed
  formulas and proofs, immutable parent/context identities, rule flushing,
  exact binary splits, ancestor pruning, independent refutation replay,
  RUP-entailed cut materialization and worker leases.
- `cubelearn.py` — exact parent-plus-cube child binding, DRAT core extraction,
  assumption-deletion reproof and signed-map proof transport.
- `replay_941.py` — one bounded supplied-artifact replay driver; it starts no
  SAT search and uses the already checked local encoder environment.
- `import_six.py` — real queue integration for all six direct cases: frozen
  FIRST-parent regeneration, exact registration and full root replay.
- `split_policy.py` — conservative same-query conflict accounting and bounded
  one-level split/stop decisions.
- `benchmark_audit.py` and `projection_bindings.py` — independent receipt and
  signed-projection accounting for the supplied copy-map experiment.

The source files were copied unchanged from the accepted member artifacts,
except for repository-relative fixture/checker paths in the tests. Tests and
examples use small fixtures; they do not search the K58 wall.

## Closure rules

- `OPEN`, `UNKNOWN`, `TIMEOUT`, `RAW_UNSAT` and `RAW_SAT` are attempts, not
  independently replayed closure.
- A refutation closes only the exact parent against which it replays.
- A checked complementary child cover yields `COMPOSE`; it is not a root
  certificate by itself.
- A strengthened residual can close without closing its original parent.
- Root status is `VERIFIED_UNSAT` only after replay against its original
  registered formula.
- RUP establishes entailment. Generic DRAT/RAT can preserve satisfiability
  without making every intermediate lemma parent-entailed. A complete DRAT
  refutation of the exact input remains valid whole-formula evidence.
- Assumption deletion is accepted only after replay against the exact reduced
  query. A checked SAT model after deletion is necessity evidence; an
  unresolved deletion remains `UNKNOWN`.
- Signed transport requires exact source-clause inclusion/context matching and
  a fresh target replay. Missing signed pins or a changed parent is not an
  alternative proof of closure.

## Run tests

From the repository root:

```sh
cd tools/adaptive_wall
export PYTHONDONTWRITEBYTECODE=1
export K58_937_ZIP="../../attachments/let-s-try-and-rbdv/K58_wall_937_copy_map_solver.zip"
python3 -m unittest -v test_case_queue test_cubelearn test_benchmark
```

Expected scope: **47 tests** (25 queue, 10 learner, 12 benchmark/policy).
The `drat-trim` and Kissat binaries used by tests are the already checked
executables in `../selfcontained/wallcc/bin/`. The benchmark integration test
uses the supplied ZIP but never unpacks or modifies it and launches no solver.
Only the learner's tiny synthetic minimization test starts a solver.

## Replay the demonstrated supplied full case

Choose a new output directory. No fresh SAT search is performed:

```sh
python3 replay_941.py \
  --archive ../../attachments/let-s-try-and-rbdv/K58_six_whole_rows.zip \
  --shared ../../.scratch/shared-learning-pilot/K58_shared_learning \
  --checker ../../tools/selfcontained/wallcc/bin/drat-trim \
  --out ../../.scratch/adaptive-wall/fresh-941 \
  --seconds 90
```

This binds the exact `941d51630693…` FIRST parent and transports its proof to
the exact RETRY formula, with a missing-signed-unit negative control. It does
not generalize the result to any other row.

## Real CaseQueue integration check

`import_six.py` supplies and runs a real frozen-formula validator, not only the
fixture validator used by unit tests. It regenerated all six exact FIRST
parents, checked their published hashes, replayed root proofs and returned six
`VERIFIED_UNSAT` cases with zero open tasks. Its summary is
`../../results/adaptive-wall-2026-11-26/queue-import-summary.json`.
The SQLite database and artifacts remain ignored in `.scratch`. This does not
populate or close a larger wall cohort.

## Integration gaps before a live campaign

1. Generalize the frozen-encoder `original_formula_validator` already
   demonstrated by `import_six.py`; a plan hash alone is only provenance.
2. Supply a checked exhaustive K58 matcher and transformed proofs for every
   declared transport class. The bundled identity matcher is not enough for
   broad learning.
3. Connect WallCC's split-proof exporter/composer; `COMPOSE` must stay pending
   until the root replay succeeds.
4. Connect measured direct/split estimators to the queue's `SplitEvidence`.
5. Supply missing proof/core bytes and their signed premises. Receipt hashes
   or reported `VERIFIED_UNSAT` text alone stay `OPEN` on import.

No branch in this package silently treats a cutoff, projection, relaxation,
one-sided cover, conflict cap, or cohort-wide reported bound as an original-row
refutation.
