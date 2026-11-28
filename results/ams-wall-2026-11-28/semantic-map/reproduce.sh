#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
BASE=$(realpath ../../../.scratch/shared-learning-pilot/K58_shared_learning)
PY="$BASE/.venv/bin/python"
[[ -x "$PY" ]]
(cd inputs && sha256sum -c SHA256SUMS)
"$PY" -B audit_parent.py > results/run.log 2>&1
python3 -B verify_map.py | tee results/verify.log
cmp inputs/parent.cnf results/reconstructed-parent.cnf
sha256sum \
  audit_parent.py verify_map.py reproduce.sh REPORT.md \
  results/summary.json results/verification.json \
  results/frozen-units.json results/allocations.json results/counters.json \
  results/support-selectors.json results/clause-blocks.json results/senders.json \
  results/skipped-senders.json results/support-catalogue.json results/mcf-config.json \
  results/reconstructed-parent.cnf results/run.log results/verify.log \
  > SHA256SUMS
printf 'PASS: exact-parent regeneration and independent map verification\n'
