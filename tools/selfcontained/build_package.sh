#!/usr/bin/env bash
# Rebuild dist/k58-solver.zip from this repository plus the handoff bundle.
#   build_package.sh /path/to/R3333_K58_LLM_handoff.zip /path/to/kissat /path/to/drat-trim
set -euo pipefail
HANDOFF=${1:?handoff zip}; KISSAT=${2:?kissat binary}; DRAT=${3:?drat-trim binary}
HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$HERE/../.." && pwd)
WORK=$(mktemp -d); PKG=$WORK/k58-solver
mkdir -p "$PKG"/{bin,wheels,tools}
unzip -q "$HANDOFF" -d "$PKG/k58"
cp "$KISSAT" "$PKG/bin/kissat"; cp "$DRAT" "$PKG/bin/drat-trim"; chmod +x "$PKG/bin"/*
cp "$REPO"/tools/{pin_manifest.py,lean_certify.py,import_historical.py,verify_parallel.py,retry_status.py,find_unpublished.py,cover_evidence_full_root.patch} "$PKG/tools/"
cp "$HERE/k58.sh" "$HERE/k58-batch.sh" "$HERE/README.md" "$PKG/"
for v in 3.10 3.11 3.12 3.13; do
  python3 -m pip download python-sat==1.9.dev22 -d "$PKG/wheels" --no-deps -q \
    --only-binary=:all: --python-version $v --implementation cp --abi cp${v/./} \
    --platform manylinux_2_24_x86_64 || echo "warning: no wheel for python $v"
done
python3 -m pip download six -d "$PKG/wheels" --no-deps -q --only-binary=:all: || true
( cd "$WORK" && zip -q -X -r "$REPO/dist/k58-solver.zip" k58-solver )
rm -rf "$WORK"
sha256sum "$REPO/dist/k58-solver.zip"
