#!/usr/bin/env bash
# Build a release manifest over an evidence root and verify every certificate.
#   ./finalise.sh --bundle K58 --out evidence --release release-1
set -euo pipefail
cd "$(dirname "$0")"
BUNDLE=""; OUT=""; REL=""; CHECKER="$PWD/bin/drat-trim"
while [ $# -gt 0 ]; do case "$1" in
  --bundle) BUNDLE="$2"; shift 2;; --out) OUT="$2"; shift 2;;
  --release) REL="$2"; shift 2;; --checker) CHECKER="$2"; shift 2;;
  *) echo "unknown option $1" >&2; exit 2;; esac; done
[ -n "$BUNDLE" ] && [ -n "$OUT" ] && [ -n "$REL" ] || { echo "need --bundle --out --release" >&2; exit 2; }
python3 "$BUNDLE/cover_evidence.py" --ledger "$BUNDLE/case-ledger.jsonl.gz" --root "$OUT" manifest "$REL" | tee "$REL.manifest.json"
SHA=$(python3 -c "import json;print(json.load(open('$REL.manifest.json'))['manifest_sha256'])")
echo "manifest $SHA"
python3 "$BUNDLE/cover_evidence.py" --ledger "$BUNDLE/case-ledger.jsonl.gz" --root "$OUT" verify "$REL" --manifest-sha256 "$SHA" --checker "$CHECKER" | tee "$REL.verify.json"
echo "quote this together with the hash: $(cat "$REL.verify.json")"
