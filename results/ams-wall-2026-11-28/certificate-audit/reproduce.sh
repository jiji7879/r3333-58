#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
sha256sum -c SHA256SUMS
python3 scripts/audit_cubes.py inputs/frontier.cubes inputs/arm-pool.json \
  --out checks/frontier-audit.json > checks/frontier-audit.log 2>&1
python3 scripts/audit_prefix.py > checks/audit-prefix.log
python3 scripts/independent_rup.py > checks/independent-rup.log
python3 scripts/replay_derivation.py > checks/derivation-replay-driver.log
python3 scripts/checker_controls.py > checks/controls/driver.log
python3 scripts/audit_run.py > checks/run-reaudit.log
python3 scripts/make_summary.py
printf 'PASS: exact cover, retained query/status audit, parent/working derivation, controls\n'
