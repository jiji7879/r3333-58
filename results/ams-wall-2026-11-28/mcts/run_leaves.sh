#!/usr/bin/env bash
set -euo pipefail
M=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$M/../../.." && pwd)
BASE="$ROOT/.scratch/shared-learning-pilot/K58_shared_learning"
PYSITE=$(readlink -f "$BASE/.venv/lib/python3.12/site-packages")
export PYTHONPATH="$M/.scratch/ams_stubs:$PYSITE"
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$M/.scratch/tmp"
# Bash's -f limit is KiB here: fail closed before any proof exceeds 1 GiB.
ulimit -f 1048576
cd "$M"
/usr/bin/time -v timeout --signal=TERM --kill-after=10s 1300s \
  python3 -u scripts/run_leaves.py \
  --label wall-full20-s2 \
  --cubes results/wall-full20-s2.cubes \
  --python "$BASE/.venv/bin/python" \
  --worker "$BASE/cadical_leaf.py" \
  --run inputs/run \
  --checker "$BASE/tools/drat-trim" \
  --out results/wall-full20-s2-leaves \
  --conflicts 1000000 --seconds 180 --check-seconds 120 \
  > results/wall-full20-s2-leaves.log 2>&1
