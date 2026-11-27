# K58 adaptive-wall audit handover

Read `results/wall-983774-2026-11-27/REPORT.md` and `summary.json` first.

This is a scoped audit, not a proof that remaining representatives or ordinary
wall rows are UNSAT. It establishes the revised-cover and symmetry reductions,
all 3,066 full-owner closures, propagation/local certificates, historical
receipt/formula bindings, and a synthetic cache fail-open defect. Historical
OPEN executions and external archive provenance remain unverified.

The archive preserves each member's reports, audit programs, raw JSONL/TSV
receipts and failure controls under `.ultramath/smwyfnpf0/`. Coordinator logs,
statistics and the live-0 run are in `results/wall-983774-2026-11-27/`.

## Prerequisites

The supplied `K58_wall_campaign` solver and sweep-evidence bundles are still
required to regenerate formulas and replay proofs. This archive does not
reduplicate them. Set `B` to a correctly extracted directory with its bundled
offline wheels and compiled tools. Before using any contents, run its supplied
`sha256sum -c SHA256-solver` and `sha256sum -c SHA256-evidence` checks from the
corresponding root. Also run `sha256sum -c SHA256SUMS` in this archive.

For member-origin commands with a workspace-relative source path, retain this
repository layout. If the archive is extracted anywhere else, create this
layout explicitly **inside that extracted root**, using `B` for the actual
initialized source-bundle directory:

```sh
mkdir -p .scratch/wall983774/base
ln -s "$B" .scratch/wall983774/base/K58_wall_campaign
```

Do not replace an existing healthy link with `ln -s` by default; run the link
command only when that destination does not yet exist. Setting `B` alone does
not change m3's hardcoded relative default. m7's revised harness is
cwd-independent and also honors `K58_BASE`. The primary report is intended to
be self-contained for interpretation even without executing anything.

## Main verification programs

- m8: `audit_packages.py`, `audit_queue.py`, `compare_prior_sources.py`
- m1: `audit_b.py` with owner/cover/symmetry/queue/physical suites
- m2: `audit/integration_audit.py` with static/all-except-static
- m3: `audit_ledger.py`, `replay_closed.py`, `audit_controls.py`,
  `summarize_results.py`
- m4: propagation/local/physical/geometry programs listed in `D_REPORT.md`
- m5: `audit/audit_live0.py`, `audit/audit_cache_controls.py` (the latter creates
  negative-control outputs that are NOT campaign evidence)
- m6: `audit_receipts.py`, `audit_formula_bindings.py`,
  `replay_positive_proofs.py`, plus the complete cap128 call map
- m7: `run_all.sh` and `check_results.py`, with every intermediate/final
  symmetry check and all encoder/permutation checks

Exact interpreter/install commands are preserved in each member report. The
judge reruns used fresh destination directories; m4 concurrency was reduced
from six to two workers without changing formulas or proofs. `strict_local.py`,
`strict_physical_all.py` and `audit_propagation.py` in the archive are the
member's versions. A member-local virtual environment can be created from the
bundle's offline wheels as documented in the reports.

## Coordinator sampler

The coordinator's separate sampler is included at
`tools/wall983774/replay_closed_sample.py`. With an initialized source bundle:

```sh
B=/absolute/path/to/K58_wall_campaign
cc -std=c99 -D_GNU_SOURCE -O2 "$B/tools/drat-trim.c" -o .scratch/audit-drat-trim
"$B/.venv/bin/python" tools/wall983774/replay_closed_sample.py "$B" \
  --checker .scratch/audit-drat-trim --out .scratch/sample16-new
```

It passes 16 stratified full-parent proofs, independently reports a malformed
proof rejection, and uses the independently compiled checker with `-i -U`, never
`-w`. It is intentionally not a substitute for m3's exhaustive replay of all
3,066 parents.

## Lightweight consistency checks after extraction

The following checks need no SAT search:

```sh
# Recompute m7's final internal evidence gate without changing its contents.
cd .ultramath/smwyfnpf0/m7
python3 work/check_results.py

# Recompute m3's consolidated raw-result summary; requires binary files from
# the original member or independently rebuilt replacements.
cd ../m3
python3 summarize_results.py
```

Full physical replays and all-row formula regeneration take minutes to tens of
minutes and require the source bundles. The central report does not pretend
those checks are instantaneous, nor that unavailable historical engine
executions were rerun.
