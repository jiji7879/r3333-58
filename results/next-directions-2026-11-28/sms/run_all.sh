#!/bin/sh
# Full reproduction of the restricted one-colour SMS experiment.
# Writes only inside this directory.  No network, no package installation.
set -e
cd "$(dirname "$0")"
PY=../../../.scratch/k58/.venv/bin/python

echo "== 1. regenerate the exact retained parent and cube (hash-checked)"
$PY regen.py

echo "== 2. generate bounded one-colour lex-leader clauses (NOT stock SMS)"
$PY gen.py

echo "== 3. independent verification, and build augmented.cnf"
$PY verify_clauses.py

echo "== 4. record the SMS-shaped whole-formula bijection and round-trip check"
$PY reindex.py

echo "== 5. toy controls (complete rule check, orbit survival, negative controls)"
$PY toy_control.py

echo "== 6. matched A/B, both run orders (200000 conflicts, jobs=1)"
rm -f ab_runs.jsonl
for order in "baseline sms" "sms baseline"; do
  for arm in $order; do $PY ab_bench.py --arm "$arm" --conflicts 200000 >> ab_runs.jsonl; done
done

echo "== 7. corrupted same-size control (trajectory control, not a sound instance)"
$PY make_corrupted.py
$PY ab_bench.py --arm corrupted --conflicts 200000 >> ab_runs.jsonl
$PY ab_bench.py --arm corrupted --conflicts 200000 >> ab_runs.jsonl

echo "== 8. summary"
$PY summarise.py
