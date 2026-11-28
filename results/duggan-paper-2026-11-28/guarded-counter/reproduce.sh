#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
PY=.scratch/k58/.venv/bin/python
M=.ultramath/smwzxq4fl/m3
"$PY" -B "$M/guarded_counter.py" > "$M/guarded-counter-run.out"
"$PY" -B "$M/propagation_conformance.py" > "$M/propagation-conformance.out"
"$PY" -B "$M/two5_boundary_encoder.py" 1300 --mode two5 \
  --conditionalization naive --out "$M/actual/r1300-naive.cnf" \
  > "$M/actual/naive-build.out"
"$PY" -B "$M/two5_boundary_encoder.py" 1300 --mode two5 \
  --conditionalization boundary --out "$M/actual/r1300-boundary.cnf" \
  > "$M/actual/boundary-build.out"
"$PY" -B "$M/audit_actual.py" > "$M/actual/audit-run.out"
"$PY" -B "$M/bounded_ab.py" > "$M/actual/bounded-ab.out"
sha256sum "$M/actual/r1300-naive.cnf" "$M/actual/r1300-boundary.cnf"
printf 'PASS: generic, propagation-conformance, actual-gadget, and capped OPEN controls\n'
printf 'No DRAT or row-closure check is part of this reproduction.\n'
