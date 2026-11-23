#!/usr/bin/env bash
# Build exactly the upstream source closure imported by K58.Classification.
set -euo pipefail
cd "$(dirname "$0")"
rev=6c3f2fd0386335321801fa4079397d4a4c1962f3
cache="$PWD/.catalogue"
objects="$cache/objects.git"
mkdir -p "$cache"
if [[ -n ${K58_CATALOGUE_GIT_DIR:-} ]]; then
  objects="$K58_CATALOGUE_GIT_DIR"
else
  if [[ ! -d "$objects" ]]; then
    git init -q --bare "$objects"
  fi
  if ! git --git-dir="$objects" cat-file -e "$rev^{commit}" 2>/dev/null; then
    git --git-dir="$objects" fetch -q --depth=1 \
      https://github.com/milostatarevic/r3333-upper-bound.git "$rev"
  fi
fi
git --git-dir="$objects" archive "$rev" formal/src/R4333Lean formal/src/r4333_upper |
  tar -x -C "$cache"
cd "$cache/formal/src"
patch --silent --batch --fuzz=0 -p1 < "$cache/../catalogue-4.33.1.patch"
mkdir -p "$cache/lib/R4333Lean"
export LEAN_PATH="$cache/lib:${LEAN_PATH:?Set LEAN_PATH to the Lean 4.33.1 Mathlib build}"
python3 - <<'PY'
from pathlib import Path
import subprocess

compiled = set()

def compile_module(module):
    if module in compiled:
        return
    source = Path(*module.split(".")).with_suffix(".lean")
    for line in source.read_text().splitlines():
        if line.startswith("import R4333Lean."):
            compile_module(line.split()[1])
    output = Path("../../lib") / source.with_suffix(".olean")
    print(f"== {module}", flush=True)
    subprocess.run(["lean", "-j1", "-o", output, source], check=True)
    compiled.add(module)

compile_module("R4333Lean.CriticalCatalogues")
compile_module("R4333Lean.CriticalTemplatePaletteSymmetry")
PY
