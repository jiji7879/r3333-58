#!/usr/bin/env bash
set -euo pipefail
M=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$M/../../.." && pwd)
BASE="$ROOT/.scratch/shared-learning-pilot/K58_shared_learning"
PYSITE=$(readlink -f "$BASE/.venv/lib/python3.12/site-packages")
export PYTHONPATH="$M/.scratch/ams_stubs:$PYSITE"
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$M/.scratch/tmp"
cd "$M"
/usr/bin/time -v timeout --signal=TERM --kill-after=10s 1200s \
  python3 -u scripts/ams_tree.py \
  --upstream .scratch/AlphaMapleSAT \
  --cnf inputs/run/working.cnf \
  --pool-json inputs/arm-pool.json \
  --out results/wall-full20-s2.cubes \
  --metadata results/wall-full20-s2.json \
  --depth 2 --sims 2 --rollout-extra 20 \
  > results/wall-full20-s2.log 2>&1
