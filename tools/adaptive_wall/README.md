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
- `strengthened_probe.py` — construct a derived parent from the 384 audited
  square/six clauses, freshly replay their implication, then compare one direct
  attempt against an exact depth-one pair on that same derived parent.
- `replay_941.py` — one bounded supplied-artifact replay driver; it starts no
  SAT search and uses the already checked local encoder environment.
- `import_six.py` — real queue integration for all six direct cases: frozen
  FIRST-parent regeneration, exact registration and full root replay.
- `split_policy.py` — conservative same-query conflict accounting and bounded
  one-level split/stop decisions.
- `benchmark_audit.py`, `projection_bindings.py`, `probe_audit.py` —
  independent receipt, signed-projection and exact matched-run accounting for
  the copy-map experiment and this strengthened-parent probe.
- A separate `probe_audit.py compare` check reports matched allocation while
  retaining CaDiCaL's actual conflict counters, including cap overshoot.

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
python3 -m unittest -v test_case_queue test_cubelearn test_benchmark test_strengthened_probe test_probe_audit
```

Expected scope: **69 tests** (25 queue, 10 learner, 12 benchmark/policy,
10 strengthened-probe and 12 exact-match accounting tests).
The `drat-trim` and Kissat binaries used by tests are the already checked
executables in `../selfcontained/wallcc/bin/`. The benchmark integration test
uses the supplied ZIP but never unpacks or modifies it and launches no solver.
Only the learner's tiny synthetic minimization test starts a solver.

## Matched direct versus one-level split

`strengthened_probe.py` is the updated runnable controller for the requested
experiment. It uses `wallcc` directly on the same strengthened CNF. Direct uses
60,000 conflicts at depth 0; the two depth-1 children receive 30,000 each. It
uses one worker and eager proof generation and separately records run/verify
wall time. The 384-goal implication and an empty-proof negative control are
replayed before any search. Plan, parent, child, proof and checker hashes are
retained.

From this directory, with a checked `python-sat==1.9.dev22` interpreter:

```sh
python3 strengthened_probe.py \
  --square /path/to/K58_square_six \
  --wallcc ../selfcontained/wallcc/wallcc.py \
  --checker ../selfcontained/wallcc/bin/drat-trim \
  --python /path/to/python-sat-1.9.dev22/bin/python \
  --out ../../.scratch/adaptive-wall/matched-new \
  --conflicts 60000 --seconds 60
```

The square directory must contain `evidence/parent.cnf.gz`,
`evidence/study.json` and `evidence/implication.drat`. `--prepare-only`
performs the RUP and materialization checks without solving. Output directories
must be new.

The actual probe used derived parent SHA-256
`17cd9b8bf8ee597782feb426145f7f926a076171e818635a270b4d662e0afe0b`.
Both attempts returned OPEN: direct used 60,000 conflicts, and the children
used 30,002 and 30,000. CaDiCaL's two-conflict overshoot is preserved, so the
strict work-equality outcome is `INVALID_SPLIT_WORK`; it is not a tie and not
evidence for splitting. Independently, `probe_audit.py compare` confirms the
matching parent/source and 60,000 allocated conflicts per arm and reports the
actual 60,002 split total without masking the overshoot. Cap equality and
actual-work equality are distinct checks. The original row remains OPEN. Wall
time was 2.929977 seconds for direct run and 3.067169 seconds for split run
(cubing and solving), with separate verification timings recorded. These are
observations on one parent, not a speedup estimate.

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

## Model-supported physical word probes

`pattern_wave_probe.py` runs a bounded batch of physical third-word patterns
from the new campaign. It selects the 61 full-arm model-supported words on the
largest size-14 pentagon of distinct rows, rather than the 73 earlier
pair-live candidates, and can exclude the previously sampled 61-word row.
Every case uses the original first-tier parent plus fifteen physical spoke
units and `run_native`'s exact query/proof pipeline. It is not a local
three-color approximation and cannot close a whole row by itself.

From this directory:

```sh
/path/to/campaign/.venv/bin/python pattern_wave_probe.py \
  /path/to/K58_wall_campaign \
  --limit 1000 --cap 5000 --jobs 2 \
  --out ../../results/adaptive-wall-2026-11-26/pattern-wave-new.json
```

The result keeps every (row, arm, word), native receipt, cap, actual conflict
count and parent/query hash. OPEN is retained. UNSAT_BASE is replayed against
the exact physical parent; SAT_BASE means only a physical model under that
cube. A known locally refuted example was separately used as a 430,058-byte
original-parent RUP control, not included in the model-supported batch.
Current result: all 1,000 selected cases OPEN.
See `../../results/adaptive-wall-2026-11-26/PATTERN_WAVE_1000.md` and its two
JSON report/audit files for the exact authorization and scope.

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
