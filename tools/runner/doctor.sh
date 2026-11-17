#!/usr/bin/env bash
# Check that this machine can run the K58 cover.
#   ./doctor.sh /path/to/unpacked/K58
set -uo pipefail
BUNDLE="${1:-}"
fail=0
say() { printf '%-32s %s\n' "$1" "$2"; }
ok()  { say "$1" "ok: $2"; }
bad() { say "$1" "MISSING: $2"; fail=1; }

command -v python3 >/dev/null && ok python3 "$(python3 -V 2>&1)" || bad python3 "install Python 3.10+"
python3 - <<'PY' || fail=1
import sys
try:
    import pysat
except Exception:
    print("%-32s %s" % ("python-sat", "MISSING: pip install python-sat==1.9.dev22")); sys.exit(1)
v = getattr(pysat, "__version__", "?")
if v == "1.9.dev22":
    print("%-32s %s" % ("python-sat", "ok: " + v))
else:
    print("%-32s %s" % ("python-sat", "WRONG: " + v + " (the verifier pins 1.9.dev22)")); sys.exit(1)
PY
if command -v kissat >/dev/null; then
  v=$(kissat --version 2>/dev/null | head -1)
  [ "$v" = "4.0.4" ] && ok kissat "$v" || bad kissat "found '$v', need 4.0.4"
else bad kissat "build it with ./build_tools.sh"; fi
if command -v drat-trim >/dev/null; then ok drat-trim "$(command -v drat-trim)"; else bad drat-trim "build it with ./build_tools.sh"; fi
if [ -n "$BUNDLE" ] && [ -f "$BUNDLE/case-ledger.jsonl.gz" ]; then
  ok bundle "$BUNDLE"
else bad bundle "pass the unpacked K58 bundle as the first argument"; fi
avail=$(df -Pk . | awk 'NR==2{print int($4/1048576)}')
say disk "${avail} GB free here (a full cover needs ~200 GB of certificates, or ~1.9 TB as LRAT)"
if [ -n "$BUNDLE" ] && [ -f "$BUNDLE/case-ledger.jsonl.gz" ] && command -v drat-trim >/dev/null; then
  if out=$(python3 "$BUNDLE/cover_evidence.py" --ledger "$BUNDLE/case-ledger.jsonl.gz" \
        --root "$BUNDLE/example/evidence" verify "$BUNDLE/example/release" \
        --manifest-sha256 ea32a0abc368677b74ee12118dbeacfd2ded817dc3a90e0e1c4ea2a8e3320150 \
        --checker "$(command -v drat-trim)" 2>&1 | tail -1); then
    ok "bundled example" "$out"
  else bad "bundled example" "$out"; fi
else say "bundled example" "skipped (needs the bundle and drat-trim)"; fi
exit $fail
