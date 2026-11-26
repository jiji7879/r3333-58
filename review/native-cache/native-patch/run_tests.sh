#!/bin/sh
# Tiny checker regressions only. Kissat command executions are intercepted by the harness.
set -eu
cd "$(dirname "$0")"
ROOT=$(CDPATH= cd -- ../../.. && pwd)
CAMPAIGN="${K58_ORIGINAL_CAMPAIGN:-$ROOT/.scratch/campaign-1000/workspace/K58_wall_campaign}"
export K58_ORIGINAL_CAMPAIGN="$CAMPAIGN"
mkdir -p .scratch
PYTHONDONTWRITEBYTECODE=1 "$CAMPAIGN/.venv/bin/python" test_cached_receipts.py
