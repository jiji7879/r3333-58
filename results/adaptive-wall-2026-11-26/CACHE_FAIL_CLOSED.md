# Fail-closed native cache and persisted-tree validation

Date: 2026-11-26. Repository base: `279a9a0f3923e2b8b6a0ed9a1ca89f51ffae9919`.

## Outcome

The unattended cache-acceptance gaps identified in the preceding handoff have
been fixed in the working campaign and tested in combination. This is an
**evidence-integrity change**, not a solver improvement and not a wall closure.
The live frontier remains **11,585/11,585 original roots OPEN**, with zero
closed nodes and the same 105 OPEN native receipts. No K58 solver search was
launched for this work.

The supplied campaign ZIP was not modified. Its SHA-256 is
`1e22e33461b5325285932d2909f4f7735ce4edc7be050f6b40b641169fb2bd37`.

## Defects reproduced

Before the change, tiny synthetic controls demonstrated all of the following:

- a cached receipt with a missing proof returned `UNSAT_BASE`;
- a cached receipt with a missing model returned `SAT_BASE`;
- an under-cap OPEN receipt was reused without solver execution;
- a partial but satisfying model passed the original campaign model check;
- a persisted tree could claim `UNSAT_BASE` with no receipt or proof and return
  from `run_row` without a solver call;
- a malformed binary proof could print `s VERIFIED` under `drat-trim -i -w`
  but be rejected under strict `drat-trim -i`.

The malformed-prefix control is meaningful because this checker's
wrong-binary-prefix `break` is guarded by its warning setting. Hashing the
malformed bytes and updating the receipt digest does not repair them; semantic
replay is required.

## Changes installed

### Native `run_native` cache

`tools/adaptive_wall/campaign_cache.py` requires, before a cached result can be
reused:

- the exact original parent/plain/query/case identities;
- receipt-local regular gzip artifacts, with checked decompressed hashes;
- strict binary DRAT replay using `-i`, never `-w` or `-W`;
- replay against **plain = original parent + cube** for `UNSAT_BASE`;
- replay against the augmented **query** for
  `AUGMENTED_UNSAT_PENDING_BASE`, which remains nonterminal;
- a total one-literal-per-declared-variable satisfying model for `SAT_BASE`.

A malformed or invalid cache returns explicit nonterminal `CACHE_INVALID`. Its
old files are retained for diagnosis, no terminal artifact fields are returned,
and no implicit re-solve is started by the cache loader. Timing/conflict fields
are validated when present but are not treated as proof evidence; older valid
terminal receipts may omit them. An OPEN receipt carrying an explicit
under-cap conflict count is rejected.

Fresh native proofs use the same strict checker, and fresh models must be total.
The same `-w` removal was applied to the tracked `CaseQueue`, `cubelearn` and
`strengthened_probe` replay paths.

### Persisted trees and export

`review/native-cache/tree/campaign-integration.patch` adds `checked_tree` before
resume, scheduling and export:

- re-evaluate a persisted root/closed tree through `verify_native` on the same
  in-memory object;
- require matching node/cube identities, receipt-local artifacts, strict proof
  replay and total models;
- revoke invalid root/closed claims to a nonterminal `INVALID_CACHE` view
  without deleting the suspect evidence;
- export unvalidated raw terminal strings only as `UNVERIFIED_*`, while keeping
  the unprivileged observation in `reported_status`.

A valid checked tree is not itself a newly composed original-parent DRAT proof.
Any original-row promotion still requires the separately stated exact-root or
exhaustive-cover-plus-composition gate.

### Fresh ablation observations

`run_unsplit_ablation.py` now requires a real empty case directory, rejecting
canonical, query-suffixed and unrelated preexisting files. It refuses to write
fresh-execution provenance unless at least one actual Kissat invocation was
observed. This does not alter the completed all-OPEN ablation outcome.

### Source authentication

After the source patch, the campaign manifest was rebuilt with the new
`campaign_cache.py` entry. All **1,000/1,000** entries verify. The ablation
source preflight passes against the updated manifest.

Final patched identities:

| File | SHA-256 |
|---|---|
| `frontier.py` | `567b770fd55fb2e31144da94aeb857239ca6a48569d26761de33c3ed765b42b6` |
| `arm_pairs.py` | `c57adafd0a7cfcd93c455e8c849e869928c8344a2a52620bd1c5c9a46be3ec74` |
| `coverage.py` | `a454d266253b4e90eb03627262bec210a41ddc09d6aaf311c0f45f001636fa4f` |
| `verify_campaign.py` | `19070a38ef1519080c2c150126188b3fe0259996aba44d1eab24722c5b830260` |
| `campaign_cache.py` | `a06a2c63364c547a29893da60ebb528ab181fa75ad621a3809a5147db2f2ad52` |
| `SHA256SUMS` | `1659fdb554896de24379407fb6e6ad58369299da93bc22f4b0ebb45275232761` |

The original manifest SHA-256 remains recorded in
`campaign-cache-finalise.json`; these hashes authenticate bytes, not proofs.

## Checks actually run

| Gate | Result |
|---|---|
| Tracked adaptive suite | **92/92 tests PASS** |
| Alternate native patch direction | **14/14 tests PASS** |
| Independent adversarial oracle | **17/17 prepatch tests PASS** |
| Independent native matrix on combined/live code | **29 cases, zero mismatches/false terminals/lost valid states** |
| Coordinator native integration | **22 checks PASS**, including a hash-matched malformed binary proof |
| Combined tree/export tests | **10 campaign + 4 freshness tests PASS** |
| Security checks under `python -O` | **3/3 PASS** |
| Full campaign verifier on live combined source | **PASS** — 11,585 identities/bindings, all local tables, 61 survivor queries, 105 native inputs on 35 parents |
| Updated manifest | **1,000/1,000 hashes PASS**, before and after full verification |
| Final live status | **11,585 OPEN roots, 0 closed nodes, 105 OPEN receipts** |

The 22-check native integration used only **three tiny synthetic Kissat calls**
to test fresh SAT/UNSAT compatibility. The independent 29-case matrix forbade
every Kissat call. Full campaign verification replays existing evidence; it is
not a new solver search or a solver-speed measurement.

An earlier combined test copy failed the newly added borrowed-artifact-name
control, was identified as stale, and was discarded. The hashes above are from
the rebuilt final copy and the byte-identical live installation, which passed
that control and all subsequent gates.

## Important limits

- No direct-versus-guided or split-speed comparison was run. The preceding
  all-OPEN A/B/C and 1,000-pattern outcomes are unchanged, and they provide no
  basis for a larger cap or deeper split.
- Production decompression/proof resource caps and per-call checker timeouts
  were not added. Concurrent filesystem mutation and TOCTOU are not solved;
  retain the normal single-writer campaign discipline.
- `read_tree` remains a raw diagnostic/mutation interface. Custom consumers
  must use `checked_tree`, not reinterpret raw terminal fields as certified.
- One unrelated corrupted receipt in a row folder conservatively revokes the
  entire tree view. This is fail-closed but can discard useful reuse.
- Separate `third_star` cache architecture is outside this patch. Auxiliary
  legacy invocations in `lift.py` and `make_portable.py` were not rewritten;
  the strictness claim here covers native replay, `verify_native`/`word_wave`,
  campaign `arm_pairs`, and the listed `tools/adaptive_wall` paths.
- Synthetic controls do not establish K58 geometry. Full campaign replay checks
  the supplied artifacts and exact formulas, not the open mathematical wall.

## Relevant files

- `cache-unit-tests.log`, `cache-tree-tests.log`
- `cache-native-validation.json`, `native-cache-matrix.json`
- `campaign-verify-live.log`, `campaign-cache-finalise.json`
- `live-frontier-state.json`
- `review/native-cache/` for the independent patches, oracles and test sources
- `tools/adaptive_wall/{campaign_cache.py,install_campaign_cache_fix.py,finalise_campaign_cache_fix.py,audit_campaign_cache.py}`
