# Independent native-cache and tree-audit material

These files preserve the three accepted Ultramath `smwy6ntm1` directions as
review evidence. They are not a second production implementation and they do
not prove any K58 row.

- `native-patch/` — direction A's alternate drop-in `frontier.py`, unified
  patch, and 14 tiny fresh/cache tests. The deployed implementation is the
  coordinator's dependency-injected `tools/adaptive_wall/campaign_cache.py`
  integrated by `install_campaign_cache_fix.py`, with the same strict-proof and
  total-model requirements.
- `oracle/` — direction B's independent DIMACS/model/proof oracle, its
  deliberately prepatch 17-test contract suite, and the 29-case native matrix.
  The final postpatch reports are under `results/adaptive-wall-2026-11-26/`.
- `tree/` — direction C's persisted-tree/export patch and 10 campaign + 4
  freshness tests. `campaign-integration.patch` is the exact patch applied to
  the live campaign after `install_campaign_cache_fix.py`.

## Useful reruns

Use an **unmodified extraction** of the supplied campaign when running tests
that themselves apply a patch. Do not apply either patch twice. From this
repository root:

```sh
# Direction A's alternate patch tests (tiny fake solver calls only).
K58_ORIGINAL_CAMPAIGN=/path/to/unmodified/K58_wall_campaign \
  review/native-cache/native-patch/run_tests.sh

# Direction C's base tests on a fresh original campaign copy.
K58_ORIGINAL_CAMPAIGN=/path/to/unmodified/K58_wall_campaign \
  review/native-cache/tree/run_checks.sh
```

The matrix accepts a patched campaign through `K58_CAMPAIGN` and forbids every
Kissat invocation. Set an output parent that exists, and keep `TMPDIR` in
project scratch storage:

```sh
C="$PWD/.scratch/campaign-1000/workspace/K58_wall_campaign"
O="$PWD/review/native-cache/oracle"
mkdir -p "$O/.scratch"
K58_CAMPAIGN="$C" TMPDIR="$O/.scratch" PYTHONDONTWRITEBYTECODE=1 \
  "$C/.venv/bin/python" "$O/native_cache_matrix.py" \
  --require-contract --out "$O/.scratch/postpatch.json"
```

Expected final result: 29 cases, zero contract mismatches, zero false cached
terminals, zero lost valid terminals and zero Kissat executions. The three
`SearchAttempt` entries for missing/wrong-binding receipts are blocked fresh
solve attempts, not terminal acceptance.

`oracle/test_cached_terminal.py` contains baseline vulnerability assertions and
is intended for the unpatched original. Do not mistake its successful prepatch
bug demonstrations for postpatch tests. The final matrix is the postpatch gate.

## Limits retained

All clever negative controls use tiny synthetic CNFs/proofs/models. The separate
full campaign replay checks the supplied artifacts, not solver improvement.
There is no concurrency/TOCTOU guarantee, no claim about custom consumers that
bypass `checked_tree`, and no K58 search or Ramsey-number conclusion here.
