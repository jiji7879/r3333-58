# K58 cached-terminal integration audit (direction C)

## Outcome

Direction A fixes native receipts, but was not sufficient for persisted `tree.json`
closures. This directory supplies a tested, orthogonal integration patch for the
resume/export layer, plus a tiny unsplit-driver regression harness. No shared
campaign or tracked repository file was edited by m1, and no SAT/K58 solver was
executed.

Primary artifacts:

- `campaign-integration.patch` — apply relative to the campaign root, after or
  before direction A's `frontier.py` patch. It does **not** implement another
  native cache validator.
- `adaptive-wall-integration.patch` — HEAD-based optional unsplit guard. An
  equivalent guard subsequently appeared in the coordinator's working tree;
  do not apply it twice.
- `test_campaign_integration.py`, `test_unsplit_integration.py`,
  `probe_original_tree.py`, and `run_checks.sh` — solver-free executable checks.
- `check-results.log` — final original + C run.
- `combined-check-results.log` — final direction-A + C composition run.
- `original-tree-control.json` — machine-readable original bypass control.

## Findings and exact control flow

### 1. Persisted tree claims bypass fixed native receipts

Original `frontier.py`:

1. `run_row` returns immediately on any truthy `root_verdict` (old line 179).
2. It skips every node in `tree['closed']` without calling `run_native`
   (old line 188).
3. It composes a root UNSAT verdict directly from `tree['closed']` (old line 205).
4. `index` and the `deepen` selector reread these claims. `coverage.py` exports
   `root_status` from the same unverified object. A fixed `run_native` is never
   entered on these paths.

`probe_original_tree.py` installed a synthetic tree claiming `UNSAT_BASE` with
**no native receipt and no proof file**. Original `run_row` returned with
`root_verdict_after_run_row = UNSAT_BASE`, `solver_calls = 0`, and both artifact
counts zero. See `original-tree-control.json`.

### 2. Freshness provenance in the unsplit driver

`run_unsplit_ablation.py` checked only the canonical receipt name. A native
query-suffixed cache could therefore be missed, while the observation
unconditionally asserted `fresh_directory_created=true` and
`preexisting_receipt=false`. The prior independent ablation auditor already
rejects an empty invocation list and independently replays terminal evidence,
so this is primarily a contaminated fresh-performance measurement / late audit
failure, not a demonstrated additional mathematical closure bypass.

The optional adaptive patch requires a real empty case directory and at least
one observed native invocation before writing fresh provenance. Equivalent
changes appeared concurrently in the coordinator's working tree; m1 did not
make or overwrite those edits.

### 3. CaseQueue and replay boundaries

`CaseQueue.close_parent` reads the exact stored parent, reloads proof bytes from
CAS, and invokes its verifier before inserting a closure. `record_attempt`
leaves UNKNOWN/TIMEOUT/OPEN and raw solver statuses nonterminal. There is no
generic “trust a native receipt” queue importer to patch; such an importer must
use `close_parent`, never `record_attempt`, for a claimed closure.

The queue/cubelearn replayers and campaign `arm_pairs.check_drat` originally
passed `-w`. This is unsuitable for malformed binary proofs. m1 independently
reproduced the failure with a tiny CNF and five-byte proof: changing the first
addition tag from `0x61` to `0x58` gives `s VERIFIED` under `-i -w`, but strict
`-i` reports `WARNING: wrong binary prefix` and rejects. The valid proof passes
both. Results are in `.scratch/checker-controls/results.json`; every final test
run repeats the meaningful differential. Campaign replay in the patch now uses
strict `-i`. Equivalent adaptive-tool changes appeared concurrently elsewhere
and are not claimed as m1 edits.

### 4. Replay/export model and status gaps

The old native audit used `problem.check_model`, which accepts a satisfying
partial assignment even when declared variables are missing. The patch requires
one nonzero integer literal for every variable in both `verify_native` and
word-wave SAT auditing, in addition to the original exact-clause/cube check.

`coverage.py` also copied raw receipt strings into `full-row-runs.tsv` regardless
of whether their tree had been validated. After the patch, only a receipt whose
node/status belongs to the successfully validated tree retains `UNSAT_BASE` or
`SAT_BASE`. Other such raw claims are exported as `UNVERIFIED_<reported-status>`;
`OPEN` remains `OPEN`. The original string is separately preserved as
`reported_status` and must not be consumed as certification.

## Patched behavior

`checked_tree(rid)` is now used by `run_row`, `index`, `deepen`, and `coverage`:

1. No `root_verdict` and an empty `closed` map returns immediately, preserving
   the ordinary all-OPEN path.
2. Otherwise the same in-memory tree object is passed to
   `verify_native(rid, tree=tree)`. No solver is called. This avoids validating
   one disk tree and returning another after replacement.
3. The audit rebuilds original/plain/query identities and cube structure,
   requires exact cut counts/hashes, reloads regular receipt-local artifacts
   named from the receipt stem (no symlinks or borrowed paths), checks digests,
   strictly replays UNSAT evidence against **plain** and pending evidence
   against **query**, and checks total SAT models against **plain + cube**.
   Security decisions in the rewritten `verify_native` use explicit
   `require_native`, not `assert`.
4. On any exception, the returned tree has no `root_verdict`, `closed={}`,
   `cache_status=INVALID_CACHE`, and a bounded diagnostic. Bad evidence is not
   deleted or overwritten. Export reads sanitize in memory; a subsequent
   `run_row` may save the revoked state. A valid tree retains its original schema
   and early-return behavior.
5. `read_tree` remains the raw diagnostic/mutation interface. New code that
   makes a public closure decision must use `checked_tree`.

Direction A's native receipt validator remains responsible for ordinary receipt
loads and fresh solving. This patch only governs previously persisted tree
claims and exports. Applying C to m2's accepted `frontier.py` succeeded with
line offsets and passed the complete regression set. It also passed against the
coordinator's actual `NativeCacheValidator` installer output; see
`coordinator-combined-check-results.log` (10+4+3 PASS).

## Executed checks

From this member directory:

```sh
./run_checks.sh 2>&1 | tee check-results.log
FRONTIER_SOURCE="$PWD/../m2/frontier.py" ./run_checks.sh \
  2>&1 | tee combined-check-results.log
# Independently test the optional adaptive patch against exact HEAD:
git -C ../../.. show HEAD:tools/adaptive_wall/run_unsplit_ablation.py \
  > .scratch/head-source/run_unsplit_ablation.py
UNSPLIT_SOURCE="$PWD/.scratch/head-source/run_unsplit_ablation.py" \
  ./run_checks.sh 2>&1 | tee head-adaptive-check-results.log
```

All three final runs report:

- 10 campaign integration tests PASS: corrupt tree JSON; forged terminal tree
  without a receipt; valid cached UNSAT retained; malformed hash-matching proof
  revoked despite `-w` accepting it; borrowed artifact name rejected; partial
  model rejected; valid total SAT retained; revoked node re-enters native
  handling without solving; valid ordinary early return retained; raw export
  terminal status downgraded unless tree-validated.
- 4 unsplit tests PASS: ordinary fresh OPEN receipts still work; canonical and
  query-suffixed/stale files are rejected before native execution; no-invocation
  returns cannot attest freshness; symlink/nonempty guards work. Kissat is a
  fake Python callable and is never executed.
- Three key negative tests also PASS under `python -O`.

Runtime inventory was read only: 35 tree files with zero closed entries/root
verdicts and 105 native receipts, all OPEN. Thus the current live cache contains
no terminal tree claim that this gate would revoke or need to preserve.

Final artifact hashes:

```text
f284d75399317403c84dee923a1999f4045ffebe5de3550bba29f904d89cb66d  campaign-integration.patch
2f8f7690d4548e1acb0ef239a1ed3cc033442ebe0ede3a9eb0def7ea0675ca32  adaptive-wall-integration.patch
b4ded79f72271d7b9d2287003a9b20236a26724b44e0e935dd77166f400586e2  check-results.log
20627e17e8dee4a365c6c605b76ecc651ce7be6237bda99812227446fe8ab3d3  combined-check-results.log
```

## Limitations and integration notes

- Tests use tiny synthetic CNFs/proofs/models only. They do not replay a large
  K58 proof or validate campaign geometry. Direction B independently covers the
  general native artifact matrix; neither direction ran a K58 search.
- Validating a claimed tree currently audits every native JSON receipt in that
  row folder. One unrelated corrupt/stale receipt conservatively revokes the
  whole tree to INVALID_CACHE, possibly losing reuse of otherwise valid sibling
  claims; this is fail-closed but can be expensive. No performance benchmark was
  run.
- The same tree object is checked and returned, but filesystem artifacts are
  not snapshotted or locked against mutation **after** successful validation.
  No concurrency/TOCTOU proof is claimed. Run/export under the campaign's normal
  single-writer discipline.
- Existing gzip/path/resource limits and checker resource limits are unchanged.
  Standard campaign JSON parsing is retained; canonical duplicate-key detection
  is not added here. These are not substitutes for direction A/B validation.
- `read_tree` remains intentionally raw for diagnostics and is public within
  the campaign. Unlisted/custom consumers must not reinterpret its raw terminal
  fields as certified. Separate `arm_pairs`/`third_star` cache architecture is
  outside this run_native/tree integration patch.
- The `UNVERIFIED_*`/`reported_status` export change requires downstream parsers
  to distinguish observations from certificates. No commit/push or shared-file
  installation was performed.
