#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd ../../.. && pwd)
PY="$ROOT/.scratch/shared-learning-pilot/K58_shared_learning/.venv/bin/python"
PKG="$ROOT/.scratch/massive-clean-install/k58-solver"
mkdir -p inputs results logs scripts
# Re-copy, never edit, the retained source artifacts.
RUN="$ROOT/.scratch/shared-learning-pilot/K58_shared_learning/runs/06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06/first-depth2-arm-auto-both"
cp "$RUN/parent.cnf" inputs/parent.cnf
cp "$RUN/working.cnf" inputs/working.cnf
cp "$RUN/plan.json" inputs/plan.json
printf '%s  %s\n' \
 '90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae' inputs/parent.cnf \
 '39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38' inputs/working.cnf \
 'dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3' "$RUN/cas.drat" \
 'cc78f1d9f6f7901615b264c9ceaa3319bd152cd4caccc381a74ed742538bdb6a' "$ROOT/dist/k58-massive-solver.zip" | sha256sum -c -
for spec in 2 3 2,3; do
 tag=${spec//,/_}
 "$PY" scripts/maximal_normal_form.py --package "$PKG" --row 06861a3df60c \
  --arms "$spec" --colour 0 --output "results/mcf-arm${tag}.cnf" \
  --metadata "results/mcf-arm${tag}.json" > "logs/build-arm${tag}.log"
 python3 scripts/audit_mcf.py --cnf "results/mcf-arm${tag}.cnf" \
  --metadata "results/mcf-arm${tag}.json" --report "results/audit-arm${tag}.json" \
  > "logs/audit-arm${tag}.log"
done
for tag in 3 2_3; do
 python3 scripts/bcp_simplify.py --parent inputs/parent.cnf \
  --augmented "results/mcf-arm${tag}.cnf" --output "results/mcf-arm${tag}-bcp.cnf" \
  --metadata "results/mcf-arm${tag}-bcp.json" > "logs/bcp-arm${tag}.log"
 python3 scripts/verify_bcp.py --augmented "results/mcf-arm${tag}.cnf" \
  --simplified "results/mcf-arm${tag}-bcp.cnf" --metadata "results/mcf-arm${tag}-bcp.json" \
  --report "results/verify-bcp-arm${tag}.json" > "logs/verify-bcp-arm${tag}.log"
done
python3 scripts/maximal_normal_form.py --selftest > results/maximal-selftest.json
sha256sum -c results/query-sha256.txt
python3 scripts/check_receipts.py
if [[ ${1:-} == --solve ]]; then
 "$PY" scripts/compare_cadical.py --conflicts 1000000 --output results/cadical-1m.jsonl \
  parent=inputs/parent.cnf arm2=results/mcf-arm2.cnf arm3=results/mcf-arm3.cnf \
  union=results/mcf-arm2_3.cnf union-bcp=results/mcf-arm2_3-bcp.cnf | tee logs/cadical-1m.log
 "$PY" scripts/compare_cadical.py --conflicts 2000000 --output results/cadical-2m.jsonl \
  arm3=results/mcf-arm3.cnf parent=inputs/parent.cnf | tee logs/cadical-2m.log
 "$PY" scripts/compare_cadical.py --conflicts 1000000 --output results/cadical-arm3-bcp-1m.jsonl \
  arm3-bcp=results/mcf-arm3-bcp.cnf | tee logs/cadical-arm3-bcp-1m.log
 "$PY" scripts/compare_cadical.py --conflicts 1000000 --output results/cadical-repeat-1m.jsonl \
  arm3-bcp=results/mcf-arm3-bcp.cnf parent=inputs/parent.cnf | tee logs/cadical-repeat-1m.log
fi
