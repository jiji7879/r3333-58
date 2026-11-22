#!/usr/bin/env bash
# Replay the three DRAT certificates against the CNFs that make_all.sh rebuilds.
# Verification succeeds when every drat-trim log ends with "s VERIFIED".
set -uo pipefail
cd "$(dirname "$0")"
K=../../../.scratch/satcheck/bin/kissat
D=../../../.scratch/satcheck/bin/drat-trim
for f in design_plain sixth_pin t3v2_pin; do
  echo "== $f"
  rm -f "log/$f.drat"
  timeout 300 "$K" --time=240 "cnf/$f.cnf" "log/$f.drat" > "log/$f.kissat" 2>&1
  echo "  kissat exit $? (10 = SAT, 20 = UNSAT)"
  grep -E '^s ' "log/$f.kissat" | sed 's/^/  /'
  grep -E '^c conflicts:' "log/$f.kissat" | sed 's/^/  /'
  timeout 300 "$D" "cnf/$f.cnf" "log/$f.drat" > "log/$f.dratcheck" 2>&1
  tr -d '\r' < "log/$f.dratcheck" | grep -E '^(s |c [0-9]+ of)' | sed 's/^/  /'
done
