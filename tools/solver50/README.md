# Bounded CaDiCaL representative experiments

`direct3s.py` emits strict full-representative proofs for newly selected
cap-128-OPEN sorted cases. `shared3s.py` repeats the same jobs with reusable
incremental CaDiCaL within each group. `survivors3s.py` runs the fixed
ARM_WITNESS comparison described in `results/solver50-3s-2026-11-27/`.

These experiments accept only `VERIFIED_UNSAT` after exact full-query DRAT
replay. A local `UNSAT_SORTED_ARM` label, timeout, raw UNSAT line, timeout
budget hit or missing/malformed proof is not closure. A hash-matched malformed
binary prefix must be rejected. All ordinary rows remain OPEN.

## Commands actually used

```sh
ROOT=/absolute/path/to/extracted/K58_wall_50k
mkdir -p .scratch/solver50/direct3s-tmp .scratch/solver50/results
TMPDIR="$PWD/.scratch/solver50/direct3s-tmp" \
  "$ROOT/.venv/bin/python" tools/solver50/direct3s.py "$ROOT" \
  --count 24 --out .scratch/solver50/results/direct-next-3s.json

TMPDIR="$PWD/.scratch/solver50/shared3s-tmp" \
  "$ROOT/.venv/bin/python" tools/solver50/shared3s.py "$ROOT" \
  --direct-root "$ROOT/round50/timed-sorted-next3s" \
  --out .scratch/solver50/results/shared-next-3s.json

TMPDIR="$PWD/.scratch/solver50/survivors3s-tmp" \
  "$ROOT/.venv/bin/python" tools/solver50/survivors3s.py "$ROOT" \
  --candidates review/solver50/candidates.tsv \
  --out .scratch/solver50/results/survivors-3s.json
```

The validation copy of the source also has
`tools/solver50/runtime-changes.patch`, containing only fresh output-directory
selection and strict `-i` proof-checker changes.

Timers are per call after encoding and block initialization, not total process
wall time. The first direct 24-job cohort may take at most 72 seconds of search;
the frozen 12-job fresh/shared comparison plus its two fast controls per arm may
take at most 84 seconds of search. Use one worker and a new output directory.
Do not infer a solver winner from a selected cohort.

`--reuse-direct-validated` exists solely for continuing a completed cohort after
a bookkeeping failure. It verifies every direct receipt again before using it
and is not an implicit skip of fresh solving. A partial/partly written shared
run remains a failure, not a reusable closure.

Current measured result: four exact representative closures, all already
excluded by the local table; zero closure on the fixed 12 locally surviving
jobs. Stop after the matched cohort.
