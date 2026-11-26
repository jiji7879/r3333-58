# K58 native cached-terminal fail-closed patch (direction A)

Scope: repository HEAD `279a9a0f3923e2b8b6a0ed9a1ca89f51ffae9919`, campaign
`.scratch/campaign-1000/workspace/K58_wall_campaign`. This directory contains the only writes made by
m2. No shared runtime or tracked repository file was changed, and no K58 solver search was launched.

## Root cause

The original `frontier.run_native` has two cached early returns, original lines 116 and 121. Both use
only `id/node/mode/cap/cube`, parent/plain/query hashes, and cut counts as the cache key. They return
the cached JSON object without checking its status, reading its proof/model, checking the artifact
digest, replaying a proof, or validating a model. The second return additionally uses an `assert`,
which is not input validation. Consequently a matching receipt saying `UNSAT_BASE` or `SAT_BASE` is
terminal even when its artifact is absent or malformed.

There are two independent problems in the original evidence checks:

* `vendor/problem.check_model` checks a satisfying partial assignment, not a complete model. The
  patch therefore requires exactly `nv` signed integer literals and
  `{abs(x) for x in model} == {1, ..., nv}` before calling the original clause/cube checker.
* `arm_pairs.check_drat` runs `drat-trim -i -w`. In this exact `tools/drat-trim.c` (lines 1111-1114),
  the wrong-binary-prefix `break` is inside `if (warning != NOWARNING)`. Thus `-w` can change parser
  semantics, not just logging. The tiny test replaces the first addition tag with `0x58`: the old
  helper verifies it with `-i -w`, while `-i` rejects it. This agrees with, but does not depend on,
  the large historical control reported by prior run smwy50l9u.

A read-only snapshot of the current campaign found 105 native receipts, all `OPEN`, and 35
`tree.json` files with no `root_verdict` or closed nodes. This is not evidence that future or other
cached trees are safe.

## Patched control flow

`frontier.py` is the complete drop-in candidate; `native-cache-fail-closed.patch` is its unified diff.

1. Reconstruct `plain` and `query` from the supplied original parent, cube, cuts, and pair cuts. Their
   hashes remain cache keys, never substitutes for evidence.
2. Load the receipt as a JSON object and require every original expected field to match. A mismatch is
   a cache miss and preserves the legacy query-suffixed alternate-cache lookup.
3. Accept cached `OPEN` only as nonterminal. Whitelist `OPEN`, `UNSAT_BASE`,
   `AUGMENTED_UNSAT_PENDING_BASE`, and `SAT_BASE`; raw `UNSAT`, `SAT`, `UNKNOWN`, `TIMEOUT`, missing,
   or other statuses become annotated `OPEN`, never closure.
4. For a terminal/pending receipt, require the exact fresh-path artifact name next to the receipt
   (`<receipt-stem>.drat.gz` or `.model.json.gz`), gunzip it, and compare the SHA-256 of its plaintext
   to the receipt. Path aliases/traversal are rejected.
5. Replay `UNSAT_BASE` against `plain` (the original parent plus its cube). Replay
   `AUGMENTED_UNSAT_PENDING_BASE` only against `query` and preserve that nonterminal status. An
   augmented proof mislabeled `UNSAT_BASE` fails replay against `plain`.
6. Use a native checker invocation `drat-trim CNF PROOF -i`, without `-w` or `-W`. Require return code
   zero and an exact stripped `s VERIFIED` output line. The same function is used for fresh UNSAT
   receipts, so fresh malformed proofs cannot enter the cache either.
7. For SAT, parse the model JSON and require the complete assignment above, then check the cube and
   every parent clause. Fresh return-code-10 models receive the same completeness check before a
   receipt is written.
8. Any receipt parse/read/gzip/digest/model/replay/schema error on a matching cached entry returns
   `status='OPEN'`, `cache_status='INVALID_CACHE'`, and a bounded diagnostic. It does not invoke a
   solver and does not overwrite or delete the suspect receipt. A valid query-suffixed alternate can
   still be used after a bad primary entry. If there are no cache errors, a genuine metadata mismatch
   retains the original fresh-query behavior.

No other `run_native` solver status logic is changed: raw return-code-zero `UNKNOWN` remains `OPEN`;
only return code 10 with a checked full model becomes `SAT_BASE`; return code 20 needs proof replay;
and `AUGMENTED_UNSAT_PENDING_BASE` remains outside `DEAD`.

## Compatibility

* Fresh valid output names, proof/model bytes, receipt fields, and existing call signatures are
  unchanged. Valid cached SAT/UNSAT/OPEN and the query-suffixed fallback have executed positive tests.
* Complete models now include all declared variables, including unconstrained/unused ones. This is the
  requested complete-model contract. Normal complete solver output is accepted; a partial satisfying
  assignment is rejected before receipt creation.
* Every cached terminal/pending resume now pays for artifact loading and replay. That is deliberate;
  a hash match alone is not proof validation.
* An invalid matching cache returns `OPEN` instead of silently re-solving. Repair/remove the invalid
  cache deliberately before requesting another search. A wrong-parent/query metadata mismatch is a
  cache miss, as before; its old terminal is never returned.
* Requiring the fresh-path artifact basename is compatible with artifacts generated by this
  `run_native`. Hand-authored receipts using aliases or other paths are intentionally invalid.

## Executed checks

Run from this member directory:

```sh
./run_tests.sh
```

Executed with the campaign's Python 3.12 virtual environment. Final result: **14 tests, all passing**
(see `test-results.json` and `test-output.txt`). The harness uses the real campaign `drat-trim` on
formulas with at most two variables. Every executable named `kissat` is intercepted by a Python fake;
invalid-cache tests make any such invocation an assertion failure. Fresh-path tests use synthetic
return codes/output and binary DRAT bytes, not searches.

Coverage includes the original missing-artifact SAT/UNSAT acceptance and its patched rejection;
missing/corrupt/wrong-hash/aliased/truncated/wrong-formula proofs; incomplete, contradictory,
duplicate, extra-variable, wrong, corrupt, missing, and wrong-hash models; corrupt receipt JSON;
wrong parent/plain/query metadata; raw solver and unknown statuses; valid and mislabeled augmented
proofs; strict malformed-tag replay; valid fresh and cached SAT/UNSAT/OPEN; and valid fallback cache.
The valid-cache proof test also asserts checker command flags `-i` and absence of `-w`/`-W`.

## Required integration and limits

* **Existing `tree.json` closure is outside this run_native patch and must be revoked/revalidated by
  the coordinator.** Original `run_row` line 179 returns on `root_verdict`, line 188 skips every node
  in `tree['closed']`, and line 205 composes root UNSAT from those cached statuses without entering
  `run_native`. Direction C is handling this separate bypass. Do not publish an old closed tree merely
  because this run_native patch is installed.
* This patch does not rewrite a bad cached receipt to `OPEN`; its annotated `OPEN` is the return value
  for the current call. Direct raw-receipt/tree consumers need the integration guard. All other uses
  of `arm_pairs.check_drat` remain unchanged and still use `-w`; this patch secures native fresh/cache
  proof acceptance only.
* Tests are small synthetic controls, not a full K58 campaign replay. No real large cached terminal
  was modified or accepted, no campaign solver was run, and no nested Ultramath run was started.
* Replay inherits the campaign checker's lack of per-call resource limits and adds repeated resume
  cost. Artifact decompression/proof resource caps and checker timeouts are separate hardening work.
