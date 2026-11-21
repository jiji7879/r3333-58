#!/usr/bin/env bash
# Rebuild the campaign's K58 Lean tree together with the ported classification,
# in this member's own directory, and print the axioms of the ported theorems.
#
# The port needs the pinned n=60 development's classification closure and the
# Mathlib it was compiled against.  Both are present in the repository's cache:
#   $REPO/.scratch/k60ref/formal/src            (R4333Lean sources + oleans)
#   $REPO/.scratch/k60ref/formal/.lake/packages (pinned Mathlib, 7.4 GB, prebuilt)
# and the pinned toolchain is leanprover/lean4:v4.32.1 (installed by elan here).
#
# Nothing outside $HERE is written: sources are copied in, oleans land here.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)            # .../repo
PINNED="$REPO/.scratch/k60ref/formal"
BUILD="$HERE/build"

[ -d "$PINNED/src/R4333Lean" ] || { echo "missing $PINNED/src/R4333Lean" >&2; exit 1; }
[ -d "$PINNED/.lake/packages/mathlib/.lake/build/lib/lean" ] || {
  echo "missing the pinned Mathlib build under $PINNED/.lake/packages" >&2; exit 1; }

LP="$PINNED/src"
for p in mathlib batteries Qq aesop proofwidgets importGraph LeanSearchClient plausible Cli; do
  d="$PINNED/.lake/packages/$p/.lake/build/lib/lean"
  [ -d "$d" ] && LP="$LP:$d"
done

rm -rf "$BUILD"; mkdir -p "$BUILD/K58"
cp "$REPO"/lean/K58/*.lean "$BUILD/K58/"
cp "$HERE/K58/ClassifiedPort.lean" "$BUILD/K58/"
echo "leanprover/lean4:v4.32.1" > "$BUILD/lean-toolchain"
cd "$BUILD"
export LEAN_PATH=".:$LP"
start=$(date +%s)
for f in CNF SequentialCounter AtLeast Basic TwoColour ThreeColour DegreeCap Mixture \
         Corollaries Templates Reduction Main Plans Frontier Selection Check ClassifiedPort; do
  lean -o "K58/$f.olean" "K58/$f.lean"
done
echo "== built 17 modules in $(( $(date +%s) - start ))s; axioms of the ported theorems:"
echo "   (printed by K58/ClassifiedPort.lean above)"
