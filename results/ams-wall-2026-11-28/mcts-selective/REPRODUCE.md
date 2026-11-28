# Reproduction and verification

All paths and commands below start in `.ultramath/smwzzs8qs/m2/`. Inputs and results are already copied into this member directory. All intended generated artifacts are under this directory; the shared worker/checker binaries are executed read-only from their existing locations.

## Environment

```sh
BASE=/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/shared-learning-pilot/K58_shared_learning
PY="$BASE/.venv/bin/python"
export PYTHONPATH="$PWD/.scratch/ams_stubs:$(readlink -f "$BASE/.venv/lib/python3.12/site-packages")"
export TMPDIR="$PWD/.scratch/tmp"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$TMPDIR"
```

Use `python3` for AlphaMapleSAT (the system scientific interpreter supplies NumPy) and `$PY` for CaDiCaL/worker tasks (the existing virtualenv supplies python-sat 1.9.dev22). The initial failed attempt used `$PY` for AMS and stopped with `ModuleNotFoundError: numpy` before search. The two invocations above are the accepted adapter convention.

## Cheap verification of the retained run

```sh
"$PY" -m py_compile ams_tree.py audit_cubes.py run_leaves.py analyze_results.py cost_select.py
"$PY" analyze_results.py
sha256sum -c SHA256SUMS
```

Expected compact analyzer result:

```text
passed: true
control_final_conflicts: 284528
wall_raw_selected: 2744
wall_normalized_selected: 1426
wall_status: all four final children OPEN
final_queries_checked: 8
probe_queries_checked: 18
proof_files_hashed: 12
```

`analyze_results.py` reconstructs each query directly from its base DIMACS and cube, compares every query byte, verifies proof hashes and strict logs, checks the 1 GB per-file cap, re-runs the full-binary-cover logic, and recomputes raw/normalized rankings and timing/conflict totals. It does not ask a solver to reinterpret OPEN and does not prove physical-colouring semantics.

## Exact raw cubing commands

These commands would need fresh output paths if rerun because the harness deliberately refuses accidental result-directory reuse. The retained outputs are already present and are bound by the manifest.

```sh
python3 -u ams_tree.py --upstream .scratch/AlphaMapleSAT \
  --cnf inputs/wall-target/working.cnf --pool-json inputs/prior/arm-pool.json \
  --out results/wall-positive-recube/shallow-s10.cubes \
  --metadata results/wall-positive-recube/shallow-s10.json \
  --depth 1 --sims 10 --rollout-extra 0

timeout --signal=TERM --kill-after=10s 1200 \
python3 -u ams_tree.py --upstream .scratch/AlphaMapleSAT \
  --cnf inputs/wall-target/working.cnf --pool-json inputs/prior/arm-pool.json \
  --out results/wall-positive-recube/full20-s2.cubes \
  --metadata results/wall-positive-recube/full20-s2.json \
  --depth 1 --sims 2 --rollout-extra 20
```

The full setting emitted a cover in 21.071 s, so no timeout interpretation was needed. With two simulations the source-level MCTS expansion depth is at most one; `extra20` is a configuration name here, not a claim of a completed depth-20 rollout.

## Exact cost probes and final proof protocol

The source used in the actual raw runs is preserved as `inputs/cost-select-run.py` (SHA `88d6ff5112abbbe7f511ce2a4751eec26afe36e17fcd5fa6d5f4dbc2f427b0f3`). Current `cost_select.py` differs only in the post-run informational tie boolean and documents that reconciliation. Use the preserved file for byte-exact source reproduction.

Wall selector:

```sh
"$PY" -u inputs/cost-select-run.py --label wall-positive-cost20k \
  --upstream .scratch/AlphaMapleSAT --cnf inputs/wall-target/working.cnf \
  --parent inputs/source-plan/parent.cnf --pool-json inputs/prior/arm-pool.json \
  --worker "$BASE/cadical_leaf.py" --prefix=1413,-1417 --mcts-choice 1426 \
  --out results/wall-positive-recube/cost20k --conflicts 20000 --seconds 90
```

Control selectors differ only in formula/pool/output/prefix/choice: negative uses `inputs/control/{working,parent}.cnf`, `inputs/control/arm-pool.json`, prefix `-4141`, MCTS choice 4793; positive uses prefix `4141`, choice 4149.

Final command template (wall policy `cost20k` or `shallow`):

```sh
"$PY" -u run_leaves.py --label LABEL \
  --cubes CUBES --python "$PY" --worker "$BASE/cadical_leaf.py" \
  --run inputs/wall-target --checker "$BASE/tools/drat-trim" \
  --out FRESH_OUTPUT --conflicts 1000000 --seconds 300 --check-seconds 300
```

The control substitutes the four-leaf `results/control-cost20k-selected.cubes`, `--run inputs/control`, and `--conflicts 350000`. For each actual UNSAT, the runner concatenates the existing CAS/RUP prefix with the fresh binary leaf DRAT, removes every binary `d` record while preserving every `a` addition, and invokes:

```sh
"$BASE/tools/drat-trim" QUERY.cnf joined.additions-only.drat -i -U -t 300
```

Acceptance is return code 0, exactly one `s VERIFIED`, no `s NOT VERIFIED`, no `WARNING` or `ERROR`, and zero RAT lemmas in core. Raw, joined, and normalized proof hashes are separately retained. OPEN attempts retain their original-parent query/hashes but no incomplete proof as evidence.

## Main artifacts

* `REPORT.md` — complete result and scope argument.
* `results/summary.json` — exact measurements and derived ratios.
* `results/independent-byte-audit.json` — whole-byte query/proof audit details.
* `results/normalized-selection.json` — post-hoc cap-normalization diagnostic.
* `control-cost20k-final-leaves/` under `results/` — four strict control certificates.
* `results/wall-positive-recube/` — current-generic covers, probes, four final OPEN receipts, and six-leaf audits.
* `PREREGISTRATION.md` — pre-run policy and caps.
* `SHA256SUMS` — final manifest; regenerate only if intentionally changing artifacts, then rerun all checks.
