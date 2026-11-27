#!/usr/bin/env bash
# Drive the whole remaining cover, unattended and resumable.
#
#   ./k58-batch.sh plan                 show what would run
#   ./k58-batch.sh run                  first pass over both large profiles
#   ./k58-batch.sh retry                retry tier over whatever stayed OPEN
#   ./k58-batch.sh finish               manifest + replay + summary
#   ./k58-batch.sh all                  run, retry, finish
#
# Options: --shards N --workers W --min-free-gb G --include-small --limit N --dry-run
set -uo pipefail
cd "$(dirname "$0")"
ROOT=$PWD
export PATH="$ROOT/bin:$PATH"
PY=$ROOT/.venv/bin/python
EV=${EV:-$ROOT/evidence}
STATE=${STATE:-$ROOT/batch-state}

BIG=("16,15,15,11" "15,15,15,12")
SMALL=("15,15,14,13" "16,15,14,12" "16,15,13,13" "15,14,14,14" "16,16,14,11" "16,16,13,12" "16,14,14,13")
SHARDS=4; WORKERS=4; MIN_FREE=20; INCLUDE_SMALL=0; LIMIT=""; DRY=0
CMD=${1:-}; [ $# -gt 0 ] && shift

while [ $# -gt 0 ]; do case "$1" in
  --shards) SHARDS=$2; shift 2;; --workers) WORKERS=$2; shift 2;;
  --min-free-gb) MIN_FREE=$2; shift 2;; --include-small) INCLUDE_SMALL=1; shift;;
  --limit) LIMIT=$2; shift 2;; --dry-run) DRY=1; shift;;
  *) echo "unknown option: $1" >&2; exit 2;;
esac; done

[ -x "$PY" ] || { echo "error: run ./k58.sh setup first" >&2; exit 1; }
[ -x bin/kissat ] && [ -x bin/drat-trim ] || { echo "error: bin/ is incomplete" >&2; exit 1; }

mkdir -p "$STATE" "$EV"
free_gb() { df -Pk "$ROOT" | awk 'NR==2{print int($4/1048576)}'; }
stamp() { date -Is; }

profiles() { printf '%s\n' "${BIG[@]}"; [ "$INCLUDE_SMALL" = 1 ] && printf '%s\n' "${SMALL[@]}"; true; }

# one (profile, shard, tier) job; returns 99 if the disk guard trips
job() {
  local profile=$1 shard=$2 tier=$3 free
  free=$(free_gb)
  if [ "$free" -lt "$MIN_FREE" ]; then
    echo "$(stamp) STOP disk guard: ${free} GB free < ${MIN_FREE} GB" | tee -a "$STATE/batch.log"
    return 99
  fi
  echo "$(stamp) START $profile shard $shard/$SHARDS tier=$tier free=${free}GB" | tee -a "$STATE/batch.log"
  [ "$DRY" = 1 ] && { echo "   (dry run)"; return 0; }
  local args=(--profile "$profile" --shards "$SHARDS" --shard "$shard"
              --workers "$WORKERS" --tier "$tier" --out "$EV")
  [ -n "$LIMIT" ] && args+=(--limit "$LIMIT")
  ./k58.sh run "${args[@]}" >> "$STATE/batch.log" 2>&1
  local rc=$?
  echo "$(stamp) END   $profile shard $shard tier=$tier rc=$rc" | tee -a "$STATE/batch.log"
  return $rc
}

cmd_plan() {
  echo "evidence: $EV   shards: $SHARDS   workers: $WORKERS   disk guard: ${MIN_FREE} GB"
  echo
  for p in $(profiles); do
    for ((s=0; s<SHARDS; s++)); do echo "first  $p shard $s/$SHARDS"; done
  done
  for p in $(profiles); do
    for ((s=0; s<SHARDS; s++)); do echo "retry  $p shard $s/$SHARDS"; done
  done
  [ "$INCLUDE_SMALL" = 0 ] && echo && echo "(seven small profiles excluded; add --include-small to include them)"
}

cmd_run() {
  for p in $(profiles); do
    for ((s=0; s<SHARDS; s++)); do
      job "$p" "$s" first || { [ $? = 99 ] && exit 99; }
    done
  done
}

cmd_retry() {
  for p in $(profiles); do
    for ((s=0; s<SHARDS; s++)); do
      job "$p" "$s" retry || { [ $? = 99 ] && exit 99; }
    done
  done
}

cmd_finish() {
  echo "$(stamp) finalising $EV" | tee -a "$STATE/batch.log"
  if ! ./k58.sh finalise --release "$ROOT/release" 2>&1 | tee -a "$STATE/batch.log"; then
    echo "$(stamp) finalise FAILED; RUN_SUMMARY.md not written" | tee -a "$STATE/batch.log"
    return 1
  fi
  local rel=$ROOT/release n size
  n=$(find "$EV" -name verified.json | wc -l)
  size=$(du -sh "$EV" | cut -f1)
  {
    echo "# K58 cover — run summary"
    echo
    echo "- date: $(stamp)"
    echo "- cases closed and verified: $n"
    echo "- evidence size: $size"
    echo "- disk free at finish: $(free_gb) GB"
    echo
    echo "## Release"
    echo
    echo '```'
    cat "$rel/manifest.json"
    echo '```'
    echo
    echo "Manifest: \`$(tail -1 "$rel.manifest.log" | python3 -c 'import json,sys;print(json.load(sys.stdin)["manifest_sha256"])')\`"
    echo
    echo "## Verification"
    echo
    echo '```'
    cat "$rel.verify.json"
    echo '```'
    echo
    echo "Upload the three files in \`release/\` and this summary. The certificates"
    echo "(\`evidence/\`, $size) stay on disk; they are bit-reproducible from the"
    echo "pinned toolchain, so the manifest hash plus the replay line is the claim."
  } > "$ROOT/RUN_SUMMARY.md"
  echo
  echo "wrote $ROOT/RUN_SUMMARY.md"
  cat "$ROOT/RUN_SUMMARY.md" | sed -n '1,8p'
}

case "$CMD" in
  plan) cmd_plan ;;
  run) cmd_run ;;
  retry) cmd_retry ;;
  finish) cmd_finish ;;
  all) cmd_run && cmd_retry && cmd_finish ;;
  *) sed -n '2,11p' "$0" | sed 's/^# //'; exit 2 ;;
esac
