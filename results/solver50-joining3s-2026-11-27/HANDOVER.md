# K58 joining-colour proof handover

Outcome: two fresh positive controls produced independently replayed UNSAT
proofs; all eight new parent/child candidate calls remained OPEN at three
seconds. No representative, whole wall row, or Ramsey bound closed.

See `results/solver50-joining3s-2026-11-27/RESULTS.md` for measurements and
exact scope.

## Contents

- `primary-run-v1/`: complete generated CNFs, raw and compressed DRAT proofs,
  checker logs, watchdog markers, receipts and summary.
- `.ultramath/smwyejhdn/m1/`: exact candidate source artifacts and split audit.
- `.ultramath/smwyejhdn/m3/execution-ready/`: frozen primary design.
- `.ultramath/smwyejhdn/m2/ROUND50_REPLAY.md`: accepted transport audit report.
- `tools/solver50/`: coordinator and independent read-only verifier.
- `results/solver50-joining3s-2026-11-27/`: compact report and machine records.
- `SHA256SUMS`: hash of every packaged artifact other than the checksum file.

The supplied `K58_wall_50k` source bundle is still required. It is not
reduplicated in this archive. Set `ROOT` to its extracted directory, which
must include `.venv`, `tools/drat-trim`, and the frozen inputs.

From this archive's extracted root:

```sh
ROOT=/absolute/path/to/K58_wall_50k
sha256sum -c SHA256SUMS
"$ROOT/.venv/bin/python" tools/solver50/verify_joining3s.py "$ROOT" \
  --prepared primary-run-v1
```

To repeat the bounded preparation without solving:

```sh
"$ROOT/.venv/bin/python" tools/solver50/joining3s.py "$ROOT" \
  --design .ultramath/smwyejhdn/m3/execution-ready \
  --out .scratch/reproduction-prep --prepare-only
```

Removing `--prepare-only` runs two controls followed by eight candidate calls
using fresh solver processes. Use a new output directory every time. The
small report's full reproduction command repeats all ten calls.

Absolute paths in historical log lines are provenance, not dependencies for
replay. The read-only verifier reconstructs and hashes the actual packaged
queries and proofs and regenerates their representative identities from ROOT.
