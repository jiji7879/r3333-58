#!/usr/bin/env bash
# Create a separate copied package with the opt-in raw-arm3 entry point.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
STOCK=
OUT=
while [ $# -gt 0 ]; do
  case "$1" in
    --stock) STOCK=$2; shift 2 ;;
    --out) OUT=$2; shift 2 ;;
    *) echo "usage: $0 --stock UNPACKED-K58-MASSIVE --out NEW-DIRECTORY" >&2; exit 2 ;;
  esac
done
[ -n "$STOCK" ] && [ -n "$OUT" ] || { echo "both --stock and --out are required" >&2; exit 2; }
[ ! -e "$OUT" ] || { echo "refusing to overwrite existing output: $OUT" >&2; exit 2; }
EXPECTED=43f20cd7100775efcd16834934de9ceaeda82c0c43861cd04c217e54d7d844ad
ACTUAL=$(sha256sum "$STOCK/k58.sh" | cut -d' ' -f1)
[ "$ACTUAL" = "$EXPECTED" ] || { echo "unexpected stock k58.sh: $ACTUAL" >&2; exit 2; }
[ -f "$STOCK/color-resolved-wallcc/problem.py" ] || { echo "missing frozen wall encoder" >&2; exit 2; }
mkdir -p "$OUT/mcf" "$(dirname "$OUT")"
# A reflink when supported makes this cheap; it is still a separate directory.
cp -a --reflink=auto "$STOCK"/. "$OUT"/
cp "$HERE/k58-mcf.sh" "$HERE/MCF_README.md" "$OUT/"
for name in driver.py normal_form.py cadical_worker.py proof.py strict_rup.py test_controls.py package_controls.py audit_queries.py; do
  cp "$HERE/$name" "$OUT/mcf/$name"
done
chmod +x "$OUT/k58-mcf.sh"
[ "$(sha256sum "$OUT/k58.sh" | cut -d' ' -f1)" = "$EXPECTED" ]
python3 - "$OUT" <<'PY'
import hashlib, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
files = [root / 'k58-mcf.sh', root / 'MCF_README.md', *sorted((root / 'mcf').glob('*.py'))]
receipt = {
    'schema': 'k58-mcf-overlay-install/v1',
    'variant': 'mcf-arm3',
    'explicit_opt_in_only': True,
    'scope': 'raw arm3, colour0, exact retained cube; no stock-finalise admission or physical-row claim',
    'stock_k58_sha256': hashlib.sha256((root / 'k58.sh').read_bytes()).hexdigest(),
    'files': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
}
(root / 'mcf-overlay-install.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
print(json.dumps(receipt, indent=2, sort_keys=True))
PY
