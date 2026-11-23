#!/usr/bin/env bash
# Rebuild dist/k58-solver.zip from this repository plus the handoff bundle.
#   build_package.sh /path/to/R3333_K58_LLM_handoff.zip /path/to/kissat /path/to/drat-trim
set -euo pipefail
HANDOFF=${1:?handoff zip}; KISSAT=${2:?kissat binary}; DRAT=${3:?drat-trim binary}
HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$HERE/../.." && pwd)
WORK=$(mktemp -d); PKG=$WORK/k58-solver
mkdir -p "$PKG"/{bin,wheels,tools}
unzip -q "$HANDOFF" -d "$PKG/k58"
# The bundle's drat-trim call has no time limit (40000 s default), so one hard
# certificate can look like a stall for hours and then kill the shard. The patch
# caps the checker, records failures instead of raising, and reads the cap from
# K58_CHECK_SECONDS at runtime.
python3 "$REPO/tools/patch_run_cover_timeout.py" "$PKG/k58/run_cover.py" --seconds "${CHECK_SECONDS:-300}"
# The bundled example manifest pins the digest of every generator, run_cover.py
# among them, so the patch above invalidates it. Re-pin that single entry — the
# files that decide the CNF bytes (dense, gluing, joint_plan, charge_plan,
# matched_anchor, palette_quotient) are untouched — and record the new manifest
# hash where doctor reads it. The example's certificates predate the patched
# runner; what is re-pinned is the code that regenerates their inputs.
python3 - "$PKG/k58" <<'PIN'
import hashlib, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
manifest = root / "example/release/manifest.json"
data = json.loads(manifest.read_text())
data["generators"]["run_cover.py"] = hashlib.sha256((root / "run_cover.py").read_bytes()).hexdigest()
manifest.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
(root / "example/release/MANIFEST.sha256").write_text(
    hashlib.sha256(manifest.read_bytes()).hexdigest() + "\n")
print("re-pinned the example manifest to the patched runner")
PIN
cp "$KISSAT" "$PKG/bin/kissat"; cp "$DRAT" "$PKG/bin/drat-trim"; chmod +x "$PKG/bin"/*
cp "$REPO"/tools/{pin_manifest.py,lean_certify.py,import_historical.py,verify_parallel.py,retry_status.py,find_unpublished.py,manifest_parallel.py,cover_evidence_full_root.patch} "$PKG/tools/"
cp "$HERE/k58.sh" "$HERE/k58-batch.sh" "$HERE/patch_batch_only_small.py" "$HERE/README.md" "$PKG/"
# The compat package's additions: the compact/fast search (profile_fast.py and its
# two kernels), the seven uniform children (uniform.py, uniform_kernel.py and the
# arm-type table), the bundled uniform proofs, and its run_cover.py, which replaces
# the patched one -- it carries the same K58_CHECK_SECONDS behaviour and records the
# formula and proof sizes in a failure line.  Vendored under tools/selfcontained/k58new.
cp -a "$HERE"/k58new/. "$PKG/k58/"
for v in 3.10 3.11 3.12 3.13; do
  python3 -m pip download python-sat==1.9.dev22 -d "$PKG/wheels" --no-deps -q \
    --only-binary=:all: --python-version $v --implementation cp --abi cp${v/./} \
    --platform manylinux_2_24_x86_64 || echo "warning: no wheel for python $v"
done
python3 -m pip download six -d "$PKG/wheels" --no-deps -q --only-binary=:all: || true
( cd "$WORK" && zip -q -X -r "$REPO/dist/k58-solver.zip" k58-solver )
rm -rf "$WORK"
sha256sum "$REPO/dist/k58-solver.zip"
