# Independent audit sources

These preserve the substantive checks used to support the review. They are not a
new campaign controller and they do not launch a broad K58 search.

- `mathematics/` has the root-pin, full-witness, raw-label and exhaustive comparator
  checks, and a strict 608-proof replayer.
- `artifacts/` independently regenerates all 608 local CNFs, replays their proofs,
  validates all 3,330 models and 2,841 owner witnesses, and recomputes the roster
  totals without a SAT solver.
- `trials/` reconstructs all 40,000 trials and all 751 corresponding receipt
  blocks, including exact conditional sampling and matched conflict audits.
- `export/` checks original parents, parent-vs-export identities, preferred
  ownership assignments, group guard conditions and all 42 physical lifts.

The `.md` files one level above are the corresponding accepted audit reports.

## Replay prerequisites

Scripts use an extracted bundle located next to themselves:

- `mathematics/`, `artifacts/`, `trials/`: unzip the supplied batch ZIP into that
  directory's `extracted/` subdirectory. For `artifacts/` and `trials/`, also put
  the supplied external `K58_40000_pattern_trials.tsv` in its `inputs/`.
- `export/`: unzip the supplied batch ZIP into its `bundle/` subdirectory.

For proof replay, apply the two strict checker patches in
`tools/preferred_wall/` to the extracted bundle, run its offline `setup.sh`, and
use its `.venv` interpreter. The standard-library trial/root/cover audits do not
need a new install. All path arguments are fixed by conventional bundle names;
no K58 generation is needed by the audits.

The full original/export audit is comparatively expensive (about five minutes in
this workspace), so it belongs in a bounded background computation if repeated.
Its last successful machine-readable outputs are preserved here. One interrupted
foreground coordinator attempt was not counted as a completed check.

`trials/work/audit_results.json` is reproduced by `trials/audit.py` and should
match the preserved copy's SHA-256. `artifacts/independent-results.json` matches
608 proof checks, 3,330 models and zero solver calls, with zero checker warnings.
