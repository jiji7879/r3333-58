#!/usr/bin/env bash
# Run one shard of the frozen cover, resumably.
#   ./run_shard.sh --bundle K58 --out evidence --profile 16,15,15,11 --shards 4 --shard 0
set -euo pipefail
cd "$(dirname "$0")"
BUNDLE=""; OUT=""; PROFILE=""; SHARDS=1; SHARD=0; WORKERS=4; SECONDS=12; CONFLICTS=400000
TIER=first; KISSAT="$PWD/bin/kissat"; CHECKER="$PWD/bin/drat-trim"; LIMIT=""
while [ $# -gt 0 ]; do case "$1" in
  --bundle) BUNDLE="$2"; shift 2;; --out) OUT="$2"; shift 2;;
  --profile) PROFILE="$2"; shift 2;; --shards) SHARDS="$2"; shift 2;;
  --shard) SHARD="$2"; shift 2;; --workers) WORKERS="$2"; shift 2;;
  --seconds) SECONDS="$2"; shift 2;; --conflicts) CONFLICTS="$2"; shift 2;;
  --tier) TIER="$2"; shift 2;; --kissat) KISSAT="$2"; shift 2;; --limit) LIMIT="$2"; shift 2;;
  --checker) CHECKER="$2"; shift 2;;
  *) echo "unknown option $1" >&2; exit 2;;
esac; done
[ -n "$BUNDLE" ] && [ -n "$OUT" ] || { echo "need --bundle and --out" >&2; exit 2; }
mkdir -p "$OUT"
ARGS=(--ledger "$BUNDLE/case-ledger.jsonl.gz" --publication --tier "$TIER" --kissat "$KISSAT" --checker "$CHECKER"
      --output "$OUT" --workers "$WORKERS" --shards "$SHARDS" --shard "$SHARD")
if [ "$TIER" = first ]; then ARGS+=(--seconds "$SECONDS" --conflicts "$CONFLICTS"); fi
[ -n "$PROFILE" ] && ARGS+=(--profile "$PROFILE")
[ -n "$LIMIT" ] && ARGS+=(--limit "$LIMIT")
echo "running shard $SHARD/$SHARDS ${PROFILE:-(all profiles)} -> $OUT"
echo "rerun the identical command to resume; verified cases are skipped."
python3 "$BUNDLE/run_cover.py" "${ARGS[@]}" | tee -a "$OUT/run.log"
python3 "$BUNDLE/summarize_queue.py" "$OUT" | tee -a "$OUT/summary.txt"
