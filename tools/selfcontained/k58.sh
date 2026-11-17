#!/usr/bin/env bash
# K58 cover — one entry point.
#   ./k58.sh setup      install the pinned Python environment
#   ./k58.sh doctor     check the machine and replay the bundled example
#   ./k58.sh test       close 5 cases end to end (a few minutes)
#   ./k58.sh run ...    run shards
#   ./k58.sh finalise   build a manifest and replay every certificate
#   ./k58.sh status     how far along, how much disk
#   ./k58.sh smoke      end-to-end self test incl. rejecting a bad certificate
#   ./k58.sh pin        pin the encoding (recipe + encoder revision + CNF hashes)
set -uo pipefail
cd "$(dirname "$0")"
ROOT=$PWD
BUNDLE=$ROOT/k58
export PATH="$ROOT/bin:$PATH"
PY=$ROOT/.venv/bin/python
PYTHON_SAT=1.9.dev22
EV=${EV:-$ROOT/evidence}

die() { echo "error: $*" >&2; exit 1; }
need_venv() { [ -x "$PY" ] || die "run ./k58.sh setup first"; }

cmd_setup() {
  command -v python3 >/dev/null || die "python3 not found (need 3.10 or newer)"
  local v; v=$(python3 -c 'import sys;print("%d.%d"%sys.version_info[:2])')
  python3 -c 'import sys;raise SystemExit(0 if sys.version_info>=(3,10) else 1)' \
    || die "python3 is $v; need 3.10 or newer"
  [ -d .venv ] || python3 -m venv .venv || die "could not create .venv (install python3-venv)"
  echo "installing python-sat $PYTHON_SAT (python $v)"
  if .venv/bin/pip -q install "python-sat==$PYTHON_SAT" 2>/dev/null; then
    echo "installed from the network"
  else
    echo "network install failed; trying the bundled wheels"
    .venv/bin/pip -q install --no-index --find-links "$ROOT/wheels" "python-sat==$PYTHON_SAT" \
      || die "no wheel for python $v here; connect to the network and rerun, or install python 3.10-3.13"
    echo "installed from wheels/"
  fi
  .venv/bin/python -c "import pysat;print('python-sat', pysat.__version__)"
  "$ROOT/k58.sh" doctor || true
}

cmd_doctor() {
  need_venv
  local fail=0
  say() { printf '%-22s %s\n' "$1" "$2"; }
  say python "$($PY -V 2>&1)"
  local pv; pv=$($PY -c 'import pysat;print(pysat.__version__)' 2>/dev/null || echo missing)
  if [ "$pv" = "$PYTHON_SAT" ]; then say python-sat "ok $pv"; else say python-sat "WRONG $pv (need $PYTHON_SAT)"; fail=1; fi
  if bin/kissat --version 2>/dev/null | grep -q '^4\.0\.4$'; then say kissat "ok 4.0.4"; else say kissat "BAD"; fail=1; fi
  bin/drat-trim >/dev/null 2>&1 || { say drat-trim BAD; fail=1; }
  [ -x bin/drat-trim ] && say drat-trim "ok"
  local gb; gb=$(df -Pk "$ROOT" | awk 'NR==2{print int($4/1048576)}')
  say disk "$gb GB free here (plan on 150-350 GB for the whole cover)"
  echo "replaying the bundled example (5 certificates, ~25 s)..."
  if out=$($PY "$BUNDLE/cover_evidence.py" --ledger "$BUNDLE/case-ledger.jsonl.gz" \
        --root "$BUNDLE/example/evidence" verify "$BUNDLE/example/release" \
        --manifest-sha256 ea32a0abc368677b74ee12118dbeacfd2ded817dc3a90e0e1c4ea2a8e3320150 \
        --checker "$ROOT/bin/drat-trim" 2>&1 | tail -1); then
    echo "$out" | grep -q '"replayed": 5' && say example "ok $out" || { say example "UNEXPECTED $out"; fail=1; }
  else say example "FAILED"; fail=1; fi
  return $fail
}

cmd_test() {
  need_venv
  echo "closing 5 cases from profile 16,15,15,11 into $EV"
  "$0" run --profile 16,15,15,11 --limit 5 --workers 2 || return 1
  echo "building a manifest and replaying every certificate"
  "$0" finalise --release "$ROOT/release-test" || return 1
}

cmd_run() {
  need_venv
  local profile="" shards=1 shard=0 workers=4 tier=first seconds=12 conflicts=400000 limit=""
  while [ $# -gt 0 ]; do case "$1" in
    --profile) profile=$2; shift 2;; --shards) shards=$2; shift 2;;
    --shard) shard=$2; shift 2;; --workers) workers=$2; shift 2;;
    --tier) tier=$2; shift 2;; --limit) limit=$2; shift 2;;
    --seconds) seconds=$2; shift 2;; --conflicts) conflicts=$2; shift 2;;
    --out) EV=$2; shift 2;;
    *) die "unknown option $1";;
  esac; done
  mkdir -p "$EV"
  local args=(--ledger "$BUNDLE/case-ledger.jsonl.gz" --publication --tier "$tier"
              --kissat "$ROOT/bin/kissat" --checker "$ROOT/bin/drat-trim"
              --output "$EV" --workers "$workers" --shards "$shards" --shard "$shard")
  [ "$tier" = first ] && args+=(--seconds "$seconds" --conflicts "$conflicts")
  [ -n "$profile" ] && args+=(--profile "$profile")
  [ -n "$limit" ] && args+=(--limit "$limit")
  echo "shard $shard/$shards ${profile:-all profiles}, tier $tier, $workers workers"
  echo "rerun the identical command to resume."
  $PY "$BUNDLE/run_cover.py" "${args[@]}" | tee -a "$EV/run.log"
  $PY "$BUNDLE/summarize_queue.py" "$EV" | tee -a "$EV/summary.txt"
}

cmd_finalise() {
  need_venv
  local rel="$ROOT/release" workers=${WORKERS:-$(nproc 2>/dev/null || echo 4)}
  while [ $# -gt 0 ]; do case "$1" in
    --release) rel=$2; shift 2;; --workers) workers=$2; shift 2;;
    *) die "unknown option $1";;
  esac; done
  [ -d "$EV" ] || die "no evidence at $EV; run ./k58.sh run first"
  echo "1/2 building the manifest"
  $PY "$BUNDLE/cover_evidence.py" --ledger "$BUNDLE/case-ledger.jsonl.gz" \
     --root "$EV" manifest "$rel" | tee "$rel.manifest.json"
  local sha
  sha=$($PY -c "import json;print(json.load(open('$rel.manifest.json'))['manifest_sha256'])")
  echo "manifest $sha"
  echo "checking coverage and manifest consistency (no replay, fast)"
  $PY "$BUNDLE/cover_evidence.py" --ledger "$BUNDLE/case-ledger.jsonl.gz" \
     --root "$EV" verify "$rel" --manifest-sha256 "$sha" > "$rel.coverage.json" \
     || die "manifest/coverage check failed: see $rel.coverage.json"
  echo "2/2 replaying certificates with $workers workers"
  $PY "$ROOT/tools/verify_parallel.py" --bundle "$BUNDLE" --evidence "$EV" \
     --checker "$ROOT/bin/drat-trim" --workers "$workers" | tee "$rel.verify.json"
  echo
  echo "quote the manifest hash together with this line:"
  cat "$rel.verify.json"
}

cmd_status() {
  local n tc
  n=$(find "$EV" -name verified.json 2>/dev/null | wc -l)
  tc=$(du -sh "$EV" 2>/dev/null | cut -f1)
  echo "closed and verified: $n"
  echo "evidence size:       ${tc:-0}"
  echo "disk free:           $(df -Pk "$ROOT" | awk 'NR==2{print int($4/1048576)}') GB"
  [ -f "$EV/run.log" ] && { echo "last run lines:"; tail -3 "$EV/run.log"; }
}

cmd_smoke() {
  need_venv
  local keep=0; [ "${1:-}" = "--keep" ] && keep=1
  local dir=$ROOT/smoke; local fails=0
  step() { printf '\n[%d/5] %s\n' "$1" "$2"; }
  ok()   { printf '   PASS  %s\n' "$1"; }
  no()   { printf '   FAIL  %s\n' "$1"; fails=$((fails+1)); }

  step 1 "toolchain and the bundled example (5 certificates)"
  if "$0" doctor >"$dir.log" 2>&1; then ok "versions pinned, example replayed"; else no "doctor failed; see $dir.log"; cat "$dir.log"; return 1; fi

  step 2 "close real cases end to end"
  rm -rf "$dir"; mkdir -p "$dir"
  if "$0" run --profile 16,15,15,11 --limit 3 --workers 2 --out "$dir/evidence" >"$dir/run.log" 2>&1; then
    local n; n=$(find "$dir/evidence" -name verified.json | wc -l)
    [ "$n" -ge 1 ] && ok "$n case(s) closed and certified" || no "no case closed"
  else no "run failed; see $dir/run.log"; tail -5 "$dir/run.log"; fi

  step 3 "manifest and parallel replay"
  if EV="$dir/evidence" "$0" finalise --release "$dir/release" --workers 4 >"$dir/finalise.log" 2>&1; then
    grep -q '"failed": 0' "$dir/release.verify.json" 2>/dev/null \
      && ok "every certificate replayed: $(cat "$dir/release.verify.json" 2>/dev/null | tail -1)" \
      || no "replay reported failures"
  else no "finalise failed; see $dir/finalise.log"; tail -5 "$dir/finalise.log"; fi

  step 4 "rejecting a corrupted certificate"
  local cert
  cert=$(find "$dir/evidence" -name certificate.drat.gz | head -1)
  if [ -n "$cert" ]; then
    cp "$cert" "$dir/original.gz"
    $PY - "$cert" <<'PYEOF'
import gzip, sys
p = sys.argv[1]
data = gzip.open(p, "rb").read()
open(p, "wb").write(gzip.compress(data[: len(data) // 2]))
PYEOF
    if $PY "$ROOT/tools/verify_parallel.py" --bundle "$BUNDLE" --evidence "$dir/evidence" \
         --checker "$ROOT/bin/drat-trim" --workers 2 >"$dir/negative.log" 2>&1; then
      no "a truncated certificate was accepted -- do not trust this build"
    else ok "truncated certificate rejected"; fi
    cp "$dir/original.gz" "$cert"; rm -f "$dir/original.gz"
  else no "no certificate to corrupt"; fi

  step 5 "batch driver"
  if ./k58-batch.sh plan >/dev/null 2>&1; then ok "plan builds"; else no "k58-batch.sh broken"; fi

  echo
  if [ "$fails" -eq 0 ]; then
    echo "SMOKE TEST PASSED -- this machine is ready."
    echo "start the real run with:  ./k58-batch.sh all --shards 4 --workers $(nproc 2>/dev/null || echo 4)"
    [ "$keep" = 1 ] && echo "(left the worked example in $dir)" || rm -rf "$dir"
    return 0
  else
    echo "SMOKE TEST FAILED ($fails problem(s)). Logs in $dir"
    return 1
  fi
}

cmd_pin() {
  need_venv
  $PY "$ROOT/tools/pin_manifest.py" make --bundle "$BUNDLE" --out "$ROOT/encodings-v1.json"
  $PY "$ROOT/tools/pin_manifest.py" verify --bundle "$BUNDLE" --manifest "$ROOT/encodings-v1.json"
}

case "${1:-}" in
  setup) cmd_setup ;;
  doctor) cmd_doctor ;;
  test) cmd_test ;;
  run) shift; cmd_run "$@" ;;
  finalise) shift; cmd_finalise "$@" ;;
  status) cmd_status ;;
  smoke) shift; cmd_smoke "$@" ;;
  pin) cmd_pin ;;
  *) sed -n '2,11p' "$0" | sed 's/^# //'; exit 2 ;;
esac
