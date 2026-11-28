#!/usr/bin/env bash
# K58 cover — one entry point.
#   ./k58.sh setup      install the pinned Python environment
#   ./k58.sh doctor     check the machine and replay the bundled example
#   ./k58.sh test       close 5 cases end to end (a few minutes)
#   ./k58.sh run ...    run shards
#   ./k58.sh wallcc ...        single-row cube-and-conquer with fresh per-leaf DRAT
#   ./k58.sh wallcc-smoke      run the wall toolkit's ordinary proof controls
#   ./k58.sh uniform ...         search the seven fully sending uniform children
#   ./k58.sh profile-fast ...    run the optimized (15,14,14,14) search
#   ./k58.sh finalise   build a manifest and replay every certificate
#   ./k58.sh replay     replay certificates against an existing release
#                       (--only IDS.txt replays just those, --out FILE names the log)
#   ./k58.sh status     how far along, how much disk
#   ./k58.sh watch      is the run alive? per-worker elapsed times and counters
#   ./k58.sh smoke      end-to-end self test incl. rejecting a bad certificate
#   ./k58.sh retrystatus  is the retry pass actually closing cases?
#   ./k58.sh unpublished  closed-but-unpublished vs still-open cases
#   ./k58.sh version    print the package version
#   ./k58.sh pin        pin the encoding (recipe + encoder revision + CNF hashes)
#   ./k58.sh square ... strict K15 spoke verification/export/bounded search
#   ./k58.sh color-wallcc ... optional color-pivot wall engine
#   ./k58.sh color-smoke ... color-interface native controls
#   ./k58.sh armcap ... optional historical paired-arm/transversal/two5 tools
#   ./k58.sh modified-smoke --out DIR combined modified-build controls
#   ./k58.sh unified ...    bounded/resumable stock+colour+square cohorts
#   ./k58.sh store adopt/check        read-only byte adoption and integrity checks
set -uo pipefail
cd "$(dirname "$0")"
K58_VERSION="2026-11-28-massive-unified"
ROOT=$PWD
BUNDLE=$ROOT/k58
export PATH="$ROOT/bin:$PATH"
PY=$ROOT/.venv/bin/python
PYTHON_SAT=1.9.dev22
EV=${EV:-$ROOT/evidence}

die() { echo "error: $*" >&2; exit 1; }
usage() {
  awk 'NR>1 && /^#/ { sub(/^# ?/, ""); print; next } NR>1 { exit }' "$0"
  echo
  echo "version $K58_VERSION"
}
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
  say checker-cap "${K58_CHECK_SECONDS:-300}s per certificate (K58_CHECK_SECONDS); a certificate that does not check in that time leaves its case OPEN"
  local gb; gb=$(df -Pk "$ROOT" | awk 'NR==2{print int($4/1048576)}')
  say disk "$gb GB free here (plan on 150-350 GB for the whole cover)"
  echo "replaying the bundled example (5 certificates, ~25 s)..."
  # The build re-pins the example manifest to the patched runner and records its
  # hash next to it; fall back to the handoff's own manifest if that file is gone.
  local example_manifest_sha
  example_manifest_sha=$(cat "$BUNDLE/example/release/MANIFEST.sha256" 2>/dev/null \
    || echo ea32a0abc368677b74ee12118dbeacfd2ded817dc3a90e0e1c4ea2a8e3320150)
  if out=$($PY "$BUNDLE/cover_evidence.py" --ledger "$BUNDLE/case-ledger.jsonl.gz" \
        --root "$BUNDLE/example/evidence" verify "$BUNDLE/example/release" \
        --manifest-sha256 "$example_manifest_sha" \
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
  local opt fast=0
  local forwarded=()
  for opt in "$@"; do
    if [ "$opt" = "--fast" ]; then fast=1; else forwarded+=("$opt"); fi
  done
  if [ "$fast" -eq 1 ]; then
    "$PY" "$BUNDLE/profile_fast.py" "${forwarded[@]}"
    return $?
  fi
  local profile="" shards=1 shard=0 workers=4 tier=first seconds=12 conflicts=400000 limit="" status=""
  local retry_seconds=70 retry_conflicts=2400000 ids_file=""
  local check_seconds=${K58_CHECK_SECONDS:-300}
  while [ $# -gt 0 ]; do case "$1" in
    --profile) profile=$2; shift 2;; --shards) shards=$2; shift 2;;
    --shard) shard=$2; shift 2;; --workers) workers=$2; shift 2;;
    --tier) tier=$2; shift 2;; --limit) limit=$2; shift 2;;
    --seconds) seconds=$2; shift 2;; --conflicts) conflicts=$2; shift 2;;
    --out) EV=$2; shift 2;; --check-seconds) check_seconds=$2; shift 2;;
    --status) status=$2; shift 2;;
    --retry-seconds) retry_seconds=$2; shift 2;;
    --retry-conflicts) retry_conflicts=$2; shift 2;;
    --case-ids-file) ids_file=$2; shift 2;;
    *) die "unknown option $1";;
  esac; done
  mkdir -p "$EV"
  local args=(--ledger "$BUNDLE/case-ledger.jsonl.gz" --publication --tier "$tier"
              --kissat "$ROOT/bin/kissat" --checker "$ROOT/bin/drat-trim"
              --output "$EV" --workers "$workers" --shards "$shards" --shard "$shard")
  [ "$tier" = first ] && args+=(--seconds "$seconds" --conflicts "$conflicts")
  [ "$tier" = retry ] && args+=(--retry-seconds "$retry_seconds" --retry-conflicts "$retry_conflicts")
  [ -n "$profile" ] && args+=(--profile "$profile")
  [ -n "$limit" ] && args+=(--limit "$limit")
  [ -n "$status" ] && args+=(--status "$status")
  [ -n "$ids_file" ] && args+=(--case-ids-file "$ids_file")
  export K58_CHECK_SECONDS=$check_seconds
  echo "shard $shard/$shards ${profile:-all profiles}, tier $tier, $workers workers, checker cap ${check_seconds}s"
  echo "rerun the identical command to resume."
  $PY "$BUNDLE/run_cover.py" "${args[@]}" | tee -a "$EV/run.log"
  $PY "$BUNDLE/summarize_queue.py" "$EV" | tee -a "$EV/summary.txt"
}

cmd_wallcc() {
  need_venv
  local pdir="$ROOT/wallcc"
  export PYTHONPATH="$pdir/frozen${PYTHONPATH:+:$PYTHONPATH}"
  export TMPDIR="${TMPDIR:-$ROOT/.scratch/wallcc}"
  mkdir -p "$TMPDIR"
  "$PY" "$pdir/wallcc.py" "$@"
}

cmd_wallcc_smoke() {
  need_venv
  local pdir="$ROOT/wallcc"
  export PYTHONPATH="$pdir/frozen${PYTHONPATH:+:$PYTHONPATH}"
  export TMPDIR="$ROOT/.scratch/wallcc-smoke"
  mkdir -p "$TMPDIR"
  "$PY" "$pdir/selftest.py"
  "$PY" "$pdir/leafcert_selftest.py"
  [ -f "$pdir/smoke-results.json" ] || echo "optional merged wall-row fixture smoke-results.json is absent; it was not run or replaced"
}

cmd_square() {
  need_venv
  export PYTHONPATH="$ROOT/square_spoke/work:$ROOT/square_spoke/source/next:$ROOT/square_spoke/source/hard-more:$ROOT/square_spoke/source/hard-study:$ROOT/square_spoke/source/hard-study/encoder"
  export TMPDIR="${TMPDIR:-$ROOT/.scratch/square-spoke}"
  mkdir -p "$TMPDIR"
  "$PY" "$ROOT/square_spoke/driver.py" "$@"
}

cmd_color_wallcc() {
  need_venv
  local pdir="$ROOT/color-resolved-wallcc"
  export PYTHONPATH="$pdir/frozen"
  export TMPDIR="${TMPDIR:-$ROOT/.scratch/color-wallcc}"
  mkdir -p "$TMPDIR"
  "$PY" "$pdir/wallcc.py" "$@"
}

cmd_color_smoke() {
  need_venv
  local out="$ROOT/color-selftest" checker="$ROOT/bin/drat-trim"
  while [ $# -gt 0 ]; do case "$1" in
    --out) out=$2; shift 2;; --checker) checker=$2; shift 2;;
    *) die "unknown option $1";;
  esac; done
  "$PY" "$ROOT/color-resolved-wallcc/color_selftest.py"     --checker "$checker" --out "$out"
}

cmd_armcap() {
  need_venv
  [ "${1:-}" = "--cadical" ] && { CADICAL=$2; shift 2; }
  export PYTHONPATH="$ROOT/paired_arm/work"
  export K58_HARD_STUDY="$ROOT/paired_arm/source/hard-study"
  export TMPDIR="${TMPDIR:-$ROOT/.scratch/armcap}"
  mkdir -p "$TMPDIR"
  "$PY" "$ROOT/paired_arm/driver.py" "$@"
}

cmd_unified() {
  need_venv
  export K58_SQUARE_ROOT="$ROOT/square_spoke"
  export TMPDIR="${TMPDIR:-$ROOT/.scratch/unified}"
  mkdir -p "$TMPDIR"
  "$PY" "$ROOT/unified/driver.py" "$@"
}

cmd_store() {
  need_venv
  export PYTHONPATH="$ROOT/unified"
  "$PY" "$ROOT/unified/store.py" "$@"
}

cmd_modified_smoke() {
  need_venv
  local out="" deep=0
  while [ $# -gt 0 ]; do case "$1" in
    --out) out=$2; shift 2;; --deep) deep=1; shift;;
    --keep) shift;; *) die "unknown option $1";;
  esac; done
  [ -n "$out" ] || die "modified-smoke requires a new --out directory"
  [ ! -e "$out" ] || die "modified-smoke output already exists: $out"
  mkdir -p "$out"
  # rm does not occur here: every receipt is retained, and an existing known
  # subdirectory is a failure rather than a license to overwrite its evidence.
  local extra=()
  [ "$deep" = 1 ] && extra=(--deep)
  "$0" square verify --out "$out/square" "${extra[@]}"     >"$out/square-summary.log" || return 1
  echo "PASS: strict K15/native/model and all 14 ordinary-parent/clause checks"
  "$0" square run --index 0 --conflicts 1 --out "$out/square-interface"     >"$out/square-interface.log" || return 1
  echo "PASS: bounded square solver interface (not a row closure)"
  cmd_color_smoke --out "$out/color" --checker "$ROOT/bin/drat-trim"     >"$out/color.log" || return 1
  echo "PASS: color native derivations, local words, rejecting control"
  "$0" color-wallcc run --row 00032f347903 --tier first --cas pentagon     --pivot-color color --depth 1 --out "$out/color-interface" --jobs 1     --seconds 3 --conflicts 10 --checker "$ROOT/bin/drat-trim"     >"$out/color-interface.log" || return 1
  echo "PASS: bounded color interface; OPEN/augmented scope remains explicit"
  "$0" unified run --rows square:0 --variants original,square,square-color     --out "$out/unified" --depth 1 --seconds 1 --conflicts 1     --max-total-conflicts 50 --wall-seconds 20 --check-seconds 8 --workers 1     >"$out/unified.log" || rc=$?
  if [ "${rc:-0}" != 2 ]; then cat "$out/unified.log"; return 1; fi
  "$PY" - "$out/unified/cohort-summary.json" <<'PYUNIFIED' || return 1
import json, pathlib, sys
s = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert s['status'] == 'OPEN' and s['reports'].get('OPEN') == 3, s
assert s['allocated_conflicts_ceiling'] <= 50, s
print('PASS: unified stock/square/colour composition, bounded receipts and blob store')
PYUNIFIED
  "$0" store check --store "$out/unified/store" >"$out/unified-store.json" || return 1

  "$0" armcap finite-check >"$out/armcap-finite.json" || return 1
  "$0" armcap build --family short --rank 1288 --out "$out/armcap-panel"     >"$out/armcap-panel.log" || return 1
  "$0" armcap build --family two5 --rank 1300 --out "$out/armcap-two5"     >"$out/armcap-two5.log" || return 1
  "$0" armcap run --cnf "$out/armcap-panel/1288/short.cnf"     --out "$out/armcap-interface" --depth 1 --seconds 1 --conflicts 10     >"$out/armcap-interface.log" || return 1
  echo "PASS: bounded external-DIMACS paired-parent route"
  "$0" armcap export-stock --rank 8 --out "$out/rank8-stock.cnf"     >"$out/rank8-stock.log" || return 1
  "$0" armcap certify --rank 8 --clause=-24663,1056,2428,6024     --stock "$out/rank8-stock.cnf" --out "$out/armcap-certificate"     --checker "$ROOT/bin/drat-trim" --conflicts 1000 --seconds 5     >"$out/armcap-certificate.log" || return 1
  echo "PASS: bundled-Kissat false-cube proof, strict RUP and truncated rejection"
  "$PY" - "$out" <<'PYEND' || return 1
import json, pathlib, sys
out = pathlib.Path(sys.argv[1])
finite = json.loads((out / 'armcap-finite.json').read_text())
assert finite['status'] == 'PASS' and finite['K6_binary_colourings_checked'] == 32768
m = json.loads((out / 'armcap-panel' / '1288' / 'manifest.json').read_text())
assert m['input_sha256'] and m['files']['wide_delta']['added_clauses'] > 0
info = json.loads((out / 'armcap-two5' / '1300-two5.json').read_text())
assert info['mode'] == 'two5' and info['added_clauses'] > 0 and info['added_variables'] > 0
assert info['original_sha256'] == '56ad3dc529f1b855e65fa3f3f5363e8275930a7cb6ea5b04dc01a112535b0837'
receipt = json.loads((out / 'square-interface' / 'receipt.json').read_text())
assert receipt['square']['status'] in ('STRENGTHENED_UNSAT_NOT_ORIGINAL_CLOSURE',
                                        'STRENGTHENED_MODEL', 'OPEN_AT_CONFLICT_CAP')
cert = json.loads((out / 'armcap-certificate' / 'receipt.json').read_text())
assert cert['verified'] and cert['strict_replay']['strict_accepted']
assert cert['strict_replay']['zero_warning_or_error_output'] and cert['strict_replay']['zero_RAT_in_core']
assert cert['negative_control']['rejected'] and not cert['negative_control']['warning_suppression']
assert receipt['certificate_ceiling']
with (out / 'armcap-interface' / 'plan.json').open() as stream:
    plan = json.load(stream)
assert plan['parent_sha256'] == m['files']['short']['sha256']
leaves=[json.loads(p.read_text()) for p in (out / 'armcap-interface').glob('leaves/*/receipt.json')]
assert leaves and all(p['budget']['conflicts']==10 for p in leaves)
print('PASS: paired/two5 historical generation and bounded receipt ceilings')
PYEND
  echo "MODIFIED SMOKE PASSED: outputs in $out; stock run/finalise paths were not changed"
}


cmd_finalise() {
  need_venv
  local rel="$ROOT/release" workers=${WORKERS:-$(nproc 2>/dev/null || echo 4)}
  local only="" skip_verify=0
  while [ $# -gt 0 ]; do case "$1" in
    --release) rel=$2; shift 2;; --workers) workers=$2; shift 2;;
    --only) only=$2; shift 2;;
    --skip-verify) skip_verify=1; shift;;
    *) die "unknown option $1";;
  esac; done
  [ -d "$EV" ] || die "no evidence at $EV; run ./k58.sh run first"
  # manifest_parallel.py creates its output directory and refuses an existing one, so a
  # second finalise (the normal case after another run) died on FileExistsError.  Move the
  # previous release aside instead: it is superseded, and its files stay for comparison.
  if [ -e "$rel" ]; then
    local aside="$rel.superseded-$(date -u +%Y%m%dT%H%M%SZ)"
    mv "$rel" "$aside"
    echo "previous release moved to $aside"
  fi
  echo "1/2 building the manifest with $workers processes (this re-derives every CNF)"
  $PY "$ROOT/tools/manifest_parallel.py" --bundle "$BUNDLE" --root "$EV" \
     --out "$rel" --workers "$workers" | tee "$rel.manifest.log" | tail -1
  local sha
  # manifest_parallel prints its hash as the last line of its log
  sha=$(tail -1 "$rel.manifest.log" | $PY -c "import json,sys;print(json.load(sys.stdin)['manifest_sha256'])")
  [ -n "$sha" ] || die "could not read the manifest hash from $rel.manifest.log"
  echo "manifest $sha"
  echo "checking coverage and manifest consistency (no replay, fast)"
  $PY "$BUNDLE/cover_evidence.py" --ledger "$BUNDLE/case-ledger.jsonl.gz" \
     --root "$EV" verify "$rel" --manifest-sha256 "$sha" > "$rel.coverage.json" \
     || die "manifest/coverage check failed: see $rel.coverage.json"
  if [ "$skip_verify" = 1 ]; then
    echo "2/2 replay SKIPPED (--skip-verify): the manifest and coverage only"
    echo "replay the whole evidence later with: ./k58.sh replay --release $rel"
    return 0
  fi
  echo "2/2 replaying certificates with $workers workers"
  local extra=()
  [ -n "$only" ] && extra=(--only "$only")
  $PY "$ROOT/tools/verify_parallel.py" --bundle "$BUNDLE" --evidence "$EV" \
     --checker "$ROOT/bin/drat-trim" --workers "$workers" "${extra[@]}" | tee "$rel.verify.json"
  echo
  echo "quote the manifest hash together with this line:"
  cat "$rel.verify.json"
}

cmd_replay() {
  need_venv
  local rel="$ROOT/release" workers=${WORKERS:-$(nproc 2>/dev/null || echo 4)} only="" out=""
  while [ $# -gt 0 ]; do case "$1" in
    --release) rel=$2; shift 2;; --workers) workers=$2; shift 2;;
    --only) only=$2; shift 2;; --out) out=$2; shift 2;;
    *) die "unknown option $1";;
  esac; done
  [ -d "$EV" ] || die "no evidence at $EV; run ./k58.sh run first"
  [ -n "$out" ] || { if [ -n "$only" ]; then out="$rel.verify-$(basename "$only" .txt).json"; else out="$rel.verify.json"; fi; }
  local extra=()
  [ -n "$only" ] && extra=(--only "$only")
  if [ -n "$only" ]; then echo "replaying the ids in $only with $workers workers"
  else echo "replaying the whole evidence with $workers workers"; fi
  $PY "$ROOT/tools/verify_parallel.py" --bundle "$BUNDLE" --evidence "$EV" \
     --checker "$ROOT/bin/drat-trim" --workers "$workers" "${extra[@]}" | tee "$out"
  echo
  echo "quote this line with the manifest hash:"
  tail -1 "$out"
}

cmd_watch() {
  local ev=${1:-$EV}
  local receipts verified failed
  receipts=$(find "$ev" -name "*.jsonl" -type f 2>/dev/null | wc -l)
  verified=$(find "$ev" -name verified.json -type f 2>/dev/null | wc -l)
  failed=$(find "$ev" -name CHECK_FAILED.json -type f 2>/dev/null | wc -l)
  echo "evidence: $ev"
  printf '%-22s %s\n' "attempt receipts" "$receipts"
  printf '%-22s %s\n' "verified cases" "$verified"
  printf '%-22s %s\n' "checker failures" "$failed"
  printf '%-22s %s\n' "disk free" "$(df -Pk "$ROOT" | awk 'NR==2{print int($4/1048576)" GB"}')"
  echo "processes (elapsed seconds):"
  local seen=0 line etime name
  while read -r etime name; do
    [ -z "$name" ] && continue
    seen=1
    printf '  %-46s %6ss\n' "$name" "$etime"
    if [ "$name" = "drat-trim" ] && [ "$etime" -gt $(( ${K58_CHECK_SECONDS:-300} + 30 )) ]; then
      echo "    ^ older than the checker cap: started without the cap, or the cap is above ${K58_CHECK_SECONDS:-300}s"
    fi
    if [ "$name" = "kissat" ] && [ "$etime" -gt 900 ]; then
      echo "    ^ one case older than 15 min: the instance is hard, not the run"
    fi
  done < <(ps -eo etimes=,comm= 2>/dev/null | awk '$2=="drat-trim" || $2=="kissat"')
  [ "$seen" = 0 ] && echo "  none running"
  local newest
  newest=$(find "$ev" -type f -newermt "-10 minutes" 2>/dev/null | wc -l)
  printf '%-22s %s\n' "files written in 10 min" "$newest"
  if [ "$newest" = 0 ] && [ "$seen" = 0 ]; then echo "nothing has moved in ten minutes: the run is stopped, not slow."; fi
  return 0
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

cmd_unpublished() {
  need_venv
  local args=(--evidence "$EV")
  [ $# -gt 0 ] && args+=("$@")
  $PY "$ROOT/tools/find_unpublished.py" "${args[@]}"
}

cmd_retrystatus() {
  need_venv
  local args=(--evidence "$EV" --batch-log "$ROOT/batch-state/batch.log")
  [ $# -gt 0 ] && args+=("$@")
  $PY "$ROOT/tools/retry_status.py" "${args[@]}"
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
  uniform) shift; need_venv; exec "$PY" "$BUNDLE/uniform.py" "$@" ;;
  profile-fast) shift; need_venv; exec "$PY" "$BUNDLE/profile_fast.py" "$@" ;;
  wallcc) shift; cmd_wallcc "$@" ;;
  wallcc-smoke) shift; cmd_wallcc_smoke "$@" ;;
  square) shift; cmd_square "$@" ;;
  color-wallcc) shift; cmd_color_wallcc "$@" ;;
  color-smoke) shift; cmd_color_smoke "$@" ;;
  armcap) shift; cmd_armcap "$@" ;;
  unified) shift; cmd_unified "$@" ;;
  store) shift; cmd_store "$@" ;;
  modified-smoke) shift; cmd_modified_smoke "$@" ;;
  finalise) shift; cmd_finalise "$@" ;;
  status) cmd_status ;;
  watch) shift; cmd_watch "$@" ;;
  smoke) shift; cmd_smoke "$@" ;;
  replay) shift; cmd_replay "$@" ;;
  version) echo "$K58_VERSION" ;;
  retrystatus) shift; cmd_retrystatus "$@" ;;
  unpublished) shift; cmd_unpublished "$@" ;;
  pin) cmd_pin ;;
  *) usage; exit 2 ;;
esac
