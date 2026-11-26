#!/bin/bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
CAMPAIGN="${K58_ORIGINAL_CAMPAIGN:-$REPO/.scratch/campaign-1000/workspace/K58_wall_campaign}"
export K58_ORIGINAL_CAMPAIGN="$CAMPAIGN"
FRONTIER_SOURCE="${FRONTIER_SOURCE:-$CAMPAIGN/frontier.py}"
UNSPLIT_SOURCE="${UNSPLIT_SOURCE:-$REPO/tools/adaptive_wall/run_unsplit_ablation.py}"
CHECK="$HERE/.scratch/check-root"
rm -rf "$CHECK"
mkdir -p "$CHECK/campaign" "$CHECK/repo/tools/adaptive_wall" "$CHECK/tmp"
for file in frontier.py verify_campaign.py coverage.py arm_pairs.py; do
  source="$CAMPAIGN/$file"
  if [ "$file" = frontier.py ]; then source="$FRONTIER_SOURCE"; fi
  cp "$source" "$CHECK/campaign/$file"
done
cp "$UNSPLIT_SOURCE" "$CHECK/repo/tools/adaptive_wall/run_unsplit_ablation.py"
patch --directory="$CHECK/campaign" -p1 < "$HERE/campaign-integration.patch"
if rg -q 'stale receipt before launch' "$CHECK/repo/tools/adaptive_wall/run_unsplit_ablation.py"; then
  patch --directory="$CHECK/repo" -p1 < "$HERE/adaptive-wall-integration.patch"
else
  printf '%s\n' 'Unsplit guard already present in concurrent working-tree source; testing it without duplicate patch.'
fi
export INTEGRATION_CHECK_ROOT="$CHECK"
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$CHECK/tmp"
PY="$CAMPAIGN/.venv/bin/python"
"$PY" "$HERE/probe_original_tree.py"
"$PY" "$HERE/test_campaign_integration.py"
"$PY" "$HERE/test_unsplit_integration.py"
# The new native-audit security check is explicit rather than assert-based.
"$PY" -O "$HERE/test_campaign_integration.py" CampaignTreeIntegrationTests.test_forged_terminal_tree_without_receipt_is_invalid_open CampaignTreeIntegrationTests.test_hash_matching_malformed_prefix_is_revoked_by_strict_replay CampaignTreeIntegrationTests.test_partial_model_cannot_reopen_as_cached_sat
printf '%s\n' 'ALL INTEGRATION CHECKS PASSED; no SAT solver was executed.'
