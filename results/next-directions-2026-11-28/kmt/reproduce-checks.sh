#!/usr/bin/env bash
# Reproduce only the bounded KMT generation and semantic controls (no benchmark).
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(cd -- "$HERE/../../.." && pwd)
PY=${KMT_PY:-"$ROOT/.scratch/k58/.venv/bin/python"}
if [ ! -x "$PY" ]; then
  printf 'Pinned interpreter is missing: %s\n' "$PY" >&2
  exit 1
fi
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$ROOT/.scratch"
cd "$HERE"
"$PY" -B kmt_stage1.py > coordinator-stage1.log
"$PY" -B kmt_semantics.py > coordinator-stage2.log
"$PY" -B kmt_bcp.py > coordinator-bcp.log
