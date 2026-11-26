# Independent cached-terminal adversarial audit (direction B)

## Scope and outcome

Audited repository HEAD `279a9a0f3923e2b8b6a0ed9a1ca89f51ffae9919` and the
unmodified campaign runtime. `frontier.py` still matches its distributed
`SHA256SUMS` entry (`d6d49c41eea5d865c90e0aa41d97f1aca19f659beedcadd667075088e35c36cd`),
as do `arm_pairs.py` and `vendor/problem.py`. No production or shared runtime
file was edited.

The executable artifacts are:

- `cached_terminal_oracle.py`: independent fail-closed **test oracle**, not a
  proposed production patch. It has its own DIMACS reader and JSON/artifact
  checks and invokes only `drat-trim`.
- `test_cached_terminal.py`: contract, adversarial, fresh-compatibility, and
  explicit current-vulnerability tests. Fixtures derive `plain` and `query`
  independently rather than calling campaign `append`.
- `native_cache_matrix.py`: drives the actual `frontier.run_native` on both the
  primary and query-suffixed cached-receipt paths. It compares native outcomes
  with the oracle and records exact JSON evidence.
- `test-output.txt`, `native-baseline.txt`, and `native-findings.json`: executed
  outputs, not expected results copied from another audit.

**Result:** 17/17 unittest methods pass. The 29-case native matrix reproduces
15 invalid cached-terminal returns on the current runtime. Valid cached
SAT/UNSAT and a valid query-suffixed UNSAT receipt retain their exact states;
OPEN, pending, UNKNOWN, TIMEOUT, and raw solver states do not enter `DEAD`.
The strict baseline exits 1, as it must before the production fix.

## Root causes independently confirmed

1. `frontier.py:113-116` returns a primary cached receipt solely when metadata
   fields match. `frontier.py:117-121` does the same for the compatibility
   filename. Neither return inspects status, opens a proof/model, checks its
   digest, replays DRAT, or validates an assignment. `DEAD` at line 28 and
   `run_row` at lines 193-196 give returned `UNSAT_BASE`/`SAT_BASE` closure
   meaning.
2. `vendor/problem.py:125-132` validates literals, contradiction, cube, and
   clause satisfaction, but never requires a complete assignment. On a
   three-variable formula with clauses `1` and `2 OR 3`, the satisfying partial
   model `[1, 2]` is accepted. This is also a fresh-model gap at
   `frontier.py:136`, not merely a cache issue.
3. `arm_pairs.py:98-102` calls `drat-trim -i -w`. The supplied checker has a
   concrete malformed-prefix differential, so `s VERIFIED` under warning
   suppression is not sufficient for the new cache validator.

## Adversarial semantics tested

| Receipt claim | Required independent test oracle behavior |
|---|---|
| `UNSAT_BASE` | Load sibling gzip; bound/decompress; check decompressed SHA-256; replay against **`plain = parent + cube`**; only then terminal. |
| `SAT_BASE` | Load/check model gzip and SHA-256; require exactly one literal for every declared `plain` variable; check cube and every physical clause; only then terminal. |
| `AUGMENTED_UNSAT_PENDING_BASE` | Reload/hash/replay against **`query`**, never silently against `plain`; retain exact pending status and remain nonterminal even if the proof also checks on `plain`. |
| `OPEN` | Valid nonterminal cache state; no closure or certificate inference. |
| `UNKNOWN`, `TIMEOUT`, raw `UNSAT`/`SAT`, unknown/missing status | `INVALID_CACHE`, nonterminal; never promote to native closure. |
| Missing/corrupt JSON, duplicate keys, wrong parent/plain/query/case, missing/unsafe artifact, bad hash, corrupt/truncated gzip/proof/model, failed/inconclusive checker | `INVALID_CACHE`, nonterminal; hashes alone never confer terminal meaning. |

Artifact names must be nonempty basenames of regular, non-symlink siblings.
Receipt metadata comparison is type-sensitive (so `true` cannot equal `1`).
Proof replay accepts only return code zero and a whole output line exactly
`s VERIFIED`. The oracle checker command uses `-i -t 10`, never `-w` or `-W`.

The native matrix includes both early returns, valid and corrupt proof/model
controls, missing/corrupt/wrong-hash/wrong-parent/wrong-query/truncated inputs,
an augmented-only proof mislabeled `UNSAT_BASE`, incomplete/wrong/duplicate and
cube-violating models, pending corruption, raw solver statuses, and OPEN.

## Concrete warning-suppression control

For the hand-written two-variable CNF containing all four assignments to
variables 1 and 2, the valid binary DRAT proof is `61 04 00 61 00` (add unit 2,
then add the empty clause). The malformed proof tested is:

```text
58 00 61 04 00 61 00
```

That is `b"X\0" + valid_proof`, with its receipt hash updated to match the
malformed bytes. The existing `frontier.check_drat` (`drat-trim -i -w`) accepts
it. Strict `drat-trim -i` rejects it with `WARNING: wrong binary prefix` and
`ERROR: no conflict`. In `drat-trim.c:1112-1114`, the wrong-prefix `break` is
inside `warning != NOWARNING`; `-w` therefore skips the invalid prefix and
continues through the NUL and remaining proof. A cached replay that reuses the
warning-suppressing helper will fail this regression even if it adds hashing.

## Fresh compatibility evidence

No solver was run. Only tiny fake `CompletedProcess` objects stood in for
Kissat; actual `drat-trim` checked the tiny proofs. The real fresh
`run_native` path successfully produced and the oracle accepted:

- `SAT_BASE` with complete model `[1, 2, 3]`;
- nontrivial `UNSAT_BASE` with the two-step binary DRAT proof above;
- `OPEN` from UNKNOWN;
- `AUGMENTED_UNSAT_PENDING_BASE` after a query-only proof and fake fallback
  UNKNOWN, which remained nonterminal under independent replay.

The valid fresh controls demonstrate compatibility independently of cache
validation. They do not make an invalid fresh proof or partial model sound.

## Commands actually run

Set `$C` to the campaign and `$M3` to this member directory:

```bash
TMPDIR="$M3/.scratch" PYTHONDONTWRITEBYTECODE=1 \
  "$C/.venv/bin/python" "$M3/test_cached_terminal.py"

TMPDIR="$M3/.scratch" PYTHONDONTWRITEBYTECODE=1 \
  "$C/.venv/bin/python" "$M3/native_cache_matrix.py" \
  --out "$M3/native-findings.json"

# Negative pre-patch gate: observed exit 1.
TMPDIR="$M3/.scratch" PYTHONDONTWRITEBYTECODE=1 \
  "$C/.venv/bin/python" "$M3/native_cache_matrix.py" --require-contract \
  --out "$M3/.scratch/native-strict-baseline.json"
```

All actual Kissat invocations in native probes raise `SearchAttempt`; no
fallback solver execution is possible. Oracle child commands are checker only.
The checker binary hash is
`a9571deb08430a3d7f7a72074440f53e2ad48196dced50b146835052a18e9066`.

## Coordinator integration

Rerun `native_cache_matrix.py --require-contract` against the patched isolated
campaign. It now requires exact preservation of every oracle-valid cached
status, not merely equal terminal booleans; invalid receipts must be
nonterminal. The strict baseline contains 15 contract mismatches. A correct
patch should have none. `test_cached_terminal.py::CurrentVulnerabilityTests`
are baseline probes and should stop passing after the fix; use the strict
matrix, not those bug-assertions, as the post-patch gate.

The production implementation may catch invalid cache conditions and return
OPEN or a distinct nonterminal invalid-cache result. It must not write such a
result into `tree['closed']` or a root verdict. Fixing already persisted tree
closures is outside this direction's matrix and requires the integration work.

## Limitations

- No production patch is supplied here and no patched implementation has yet
  been tested. The strict post-patch execution remains required.
- These are small synthetic DIMACS/DRAT/model fixtures, not a replay of full
  K58 parents, roster identities, or large historical proofs. No mathematical
  K58 result is claimed or changed.
- Resource bounds, malformed JSON, traversal, and CLI failures receive basic
  checks; concurrency, TOCTOU races, checker exploits, and full campaign
  performance are not stress-tested.
- The strict native matrix enforces sound terminal semantics and preservation
  of valid states. For invalid receipts it permits an exception/non-return as
  nonterminal evidence; the matrix separately records these outcomes. A
  production-friendly OPEN/INVALID_CACHE return policy still needs review.
