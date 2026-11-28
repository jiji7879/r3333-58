#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$(cd ../../.. && pwd)
PY="$ROOT/.scratch/shared-learning-pilot/K58_shared_learning/.venv/bin/python"
export LEAN_PATH="$PWD/lean:$ROOT/lean:${LEAN_PATH:-}"

"$PY" generated/trace_parent.py > logs/trace.out
"$PY" generated/semantic_map.py > logs/semantic-map.out

lean lean/TargetRowUnits.lean > generated/lean-units.txt 2> logs/lean-units.err
"$PY" generated/check_units.py > logs/unit-binding.out

lean -o lean/SemanticAssembly.olean lean/SemanticAssembly.lean > logs/semantic-assembly.out 2>&1
python3 generated/emit_target_lean.py > logs/emit-target.out
lean -o lean/TargetSuffix.olean lean/TargetSuffix.lean > generated/lean-suffix.txt 2> logs/target-suffix.err
python3 generated/check_suffix.py > logs/suffix-binding.out

lean lean/TargetParent.lean > generated/lean-parent.txt 2> logs/target-parent.err
python3 generated/check_parent.py > logs/parent-binding.out
lean lean/TicketPremises.lean > logs/ticket-premises.out 2>&1

# A hard fail if any checked Lean theorem acquired a sorry axiom.
! rg -n 'sorryAx|error:' logs/semantic-assembly.out generated/lean-suffix.txt \
  generated/lean-parent.txt logs/ticket-premises.out
cat generated/parent-binding.json
