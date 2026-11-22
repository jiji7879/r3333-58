#!/usr/bin/env bash
# Compile the K58 Lean development in dependency order and print the axioms of
# every public theorem.  Requires lean + Mathlib on LEAN_PATH (see the repo's
# environment) and nothing else.
set -euo pipefail
cd "$(dirname "$0")"
export LEAN_PATH="$PWD:$LEAN_PATH"
for f in CNF SequentialCounter AtLeast Basic TwoColour ThreeColour DegreeCap Mixture Corollaries Arm TwoArm Link14 Model Templates Reduction Main Plans Frontier Selection Check; do
  echo "== K58/$f.lean"
  lean -o "K58/$f.olean" "K58/$f.lean"
done
