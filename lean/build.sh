#!/usr/bin/env bash
# Compile the K58 development in dependency order and print the axioms of every
# public theorem.  Requires lean + Mathlib on LEAN_PATH (see the repo's environment).
#
#   bash build.sh              the K58 library (order.txt)
#   bash build.sh --replay     ... and then the generated replay tree, which
#                              proves K58.Replay.frozenCover (needs replay/ReplayGen/;
#                              see replay/README.md for how it is generated)
#
# The upstream catalogue (pinned at 6c3f2fd0 with a 4.33.1 patch) is fetched on
# the first run into .catalogue/; .catalogue/ and replay/ReplayGen/ are build
# artefacts and are gitignored.
#
# A module is skipped when its .olean is newer than its source and than every
# .olean of the K58 modules it imports — the same rule lake uses, and the reason
# a re-run after a failure only builds what is missing.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .catalogue/lib/R4333Lean ]; then
  echo "== catalogue"
  bash replay/build-catalogue.sh
fi

export LEAN_PATH="$PWD:$PWD/.catalogue/lib:$LEAN_PATH"
while read -r f; do
  [ -z "$f" ] && continue
  src="K58/$f.lean"; obj="K58/$f.olean"
  if [ -f "$obj" ] && [ "$obj" -nt "$src" ]; then
    stale=""
    for d in $(sed -n 's/^import K58\.\([A-Za-z0-9_]*\)$/\1/p' "$src"); do
      [ -f "K58/$d.olean" ] || { stale=1; break; }
      [ "$obj" -nt "K58/$d.olean" ] || { stale=1; break; }
    done
    [ -z "$stale" ] && continue
  fi
  echo "== K58/$f.lean"
  lean -j1 -o "$obj" "$src"
done < order.txt

if [ "${1:-}" = "--replay" ]; then
  if [ ! -d replay/ReplayGen ]; then
    echo "replay/ReplayGen/ is missing: generate it with replay/generate_replay.py (see replay/README.md)" >&2
    exit 2
  fi
  python3 replay/run_replay.py . replay --jobs "${JOBS:-2}"
  echo "== ReplayCheck.lean"
  lean -j1 -o ReplayCheck.olean ReplayCheck.lean
fi
