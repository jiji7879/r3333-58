# Artifact and reproduction index

All paths below are inside `.ultramath/smwzxq4fl/m2/`; no repository file outside this member directory was modified.

## Source code written for the assessment

* `ams_tree.py` — upstream-current/Duggan-era loader with an explicit candidate pool, depth/rollout controls, metadata, and no clause or branch deletion.
* `audit_cubes.py` — independent full-binary-cover parser/checker, including ragged refinements.
* `run_leaves.py` — capped fresh CaDiCaL leaves, exact original-parent query reconstruction, additions-only DRAT normalization, strict checker acceptance.
* `summarize.py` — combines per-leaf receipts and computes the reported totals.
* `second_replay.py` — independent second-checker replay.
* `selftest.py` — executable negative/encoding controls.

The two small offline import stubs are `.scratch/ams_stubs/{wandb,coloredlogs}.py`; the cuber is run with wandb disabled and no network logging. Pinned upstream source is under `.scratch/AlphaMapleSAT` and `.scratch/AlphaCube2024`, with commits named in `ASSESSMENT.md`.

## Primary compact results

* `results/summary.json` — wall/control search and cubing totals.
* `results/wall-refined-frontier.cubes` and `results/wall-refined-frontier-audit.json` — exact five-OPEN-leaf tree.
* `results/mcts-s10-cover-audit.json` — four-leaf wall cover before refinement.
* `results/mcts-s10-leaves/receipts.json` — four fresh wall MCTS OPEN receipts.
* `results/recube-leaves/receipts.json` — two fresh depth-three OPEN receipts.
* `results/control-full20-combined-receipts.json` — four full-rollout control `CHECKED_UNSAT` receipts.
* `results/second-checker-summary.json` and `results/second-replay/` — all eleven second-checker results/raw logs.
* `results/k5-negative-fixed.log` — expected rejection of the K6 proof against K5.
* `results/duggan2024-direct-receipt.json` — explicit non-SAT receipt for the 2024 cap and multicolour interface control.
* `results/control-duggan2024-full20-s2.log` — startup of the unmodified 2024 run that reached its 420 s cubing cap without a cover.
* `results/control-duggan2024-restricted-full20-s2.log` — 2024 multicolour action-layout `IndexError` control.

Per-leaf `query.cnf`, raw and normalized proofs, receipts and strict replay logs live below `results/control-{greedy,mcts,mcts-full20-new}-leaves/` and `results/k6-control-leaves-fixed/`. No OPEN proof stream is used as evidence.

## Exact environment

Commands start in `.ultramath/smwzxq4fl/m2/`.

```sh
M=$PWD
BASE=$(readlink -f "$M/../../../.scratch/shared-learning-pilot/K58_shared_learning")
PY="$BASE/.venv/bin/python"
CHECK="$BASE/tools/drat-trim"
PYSITE=$(readlink -f "$BASE/.venv/lib/python3.12/site-packages")
export PYTHONPATH="$M/.scratch/ams_stubs:$PYSITE"
```

The wall input was the retained plan under:

```text
$BASE/runs/06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06/
  first-depth2-arm-auto-both/{parent.cnf,working.cnf,cas.drat,plan.json}
```

Rebuild the solvable control parent/working/RUP-prefix with:

```sh
"$PY" "$BASE/wallcc.py" prepare \
  --case "$BASE/cases/0f9ba81047f4/row.json" --tier retry \
  --arm-pair auto --arm-mode both --depth 2 \
  --out results/control-greedy-plan
```

## Core cube-generation commands

Current generic implementation, real wall, shallow:

```sh
python3 -u ams_tree.py --upstream .scratch/AlphaMapleSAT \
  --cnf "$BASE/runs/06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06/first-depth2-arm-auto-both/working.cnf" \
  --pool-json arm-pool.json --out results/mcts-s10.cubes \
  --metadata results/mcts-s10.json --depth 2 --sims 10 --rollout-extra 0
```

Selective wall re-cube uses `results/recube-working.cnf` (working CNF plus units `-1413 1014`), `--depth 1 --sims 10 --rollout-extra 0`, and produced split 1421.

Current generic implementation, control, shallow and full rollout:

```sh
python3 -u ams_tree.py --upstream .scratch/AlphaMapleSAT \
  --cnf results/control-greedy-plan/working.cnf --pool-json results/control-arm-pool.json \
  --out results/control-mcts-s10.cubes --metadata results/control-mcts-s10.json \
  --depth 2 --sims 10 --rollout-extra 0

python3 -u ams_tree.py --upstream .scratch/AlphaMapleSAT \
  --cnf results/control-greedy-plan/working.cnf --pool-json results/control-arm-pool.json \
  --out results/control-mcts-full20-s10.cubes --metadata results/control-mcts-full20-s10.json \
  --depth 2 --sims 10 --rollout-extra 20
```

The final adapter regression reruns are `results/{wall,control}-finalreg-*.cubes`; Python assertions in the reproduction run checked that their cube sets match the reported originals.

## Strict checking commands

Cover audits (use the appropriate pool JSON):

```sh
python3 audit_cubes.py results/mcts-s10.cubes arm-pool.json \
  --out results/mcts-s10-cover-audit.json
python3 audit_cubes.py results/wall-refined-frontier.cubes arm-pool.json \
  --out results/wall-refined-frontier-audit.json
```

Wall MCTS leaf calls (all OPEN):

```sh
python3 run_leaves.py --label mcts-s10 --cubes results/mcts-s10.cubes \
  --python "$PY" --worker "$BASE/cadical_leaf.py" \
  --run "$BASE/runs/06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06/first-depth2-arm-auto-both" \
  --checker "$CHECK" --out results/mcts-s10-leaves \
  --conflicts 1000000 --seconds 300 --check-seconds 300
```

For control A/B runs, substitute `results/control-greedy.cubes` or the MCTS cube file, use `--run results/control-greedy-plan`, and `--conflicts 350000`. The selective re-cube uses `results/recube-extended.cubes` and the wall run directory.

Every retained positive proof was replayed again with a second binary:

```sh
python3 second_replay.py
python3 selftest.py
```

The individual checker form is:

```sh
drat-trim QUERY.cnf PROOF.additions-only.drat -i -U -t 300
```

Acceptance requires return code 0, exactly one `s VERIFIED`, no `WARNING`, no `ERROR`, and no `s NOT VERIFIED`. No `-w`/`-W` is used.

## Integrity snapshot

Upstream Duggan PDF SHA-256:
`58665d3b71e1e5452a6afdd6d8087bfb7df99daf6566263addfc2f1a905109e8`.

The second checker binary SHA-256 is recorded in `results/second-checker-summary.json`. Formula/query/proof SHA-256 values are inside each receipt rather than inferred from status text.
