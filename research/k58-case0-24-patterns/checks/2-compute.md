# Compute check for the 24-pattern conditional clause

All commands ran from the project root. No SAT/SLS search was launched and no
production queue or ledger was changed.

## 1. Input and source audit

```sh
sha256sum attachments/let-s-try-and-rbdv/K58_case0_24_patterns.zip
```

Result:
`22d87d5245ea80b8459d3ce40698a745aea9cf6f1c611606cc490cba9a19706e`.

The archive has 245 files / 295.2 MiB uncompressed, approximately 93.1 MiB
compressed. ZIP CRC validation succeeds; duplicate/unsafe paths are rejected
before extraction into a new directory `.scratch/case0-24-patterns-v1/src/`.
The independent program hashes all 244 `SHA256SUMS` entries with zero errors.

The source `replay.py` was read before execution. Its actual verifier uses
`-i -w -U` plus substring acceptance. That warning-suppressed rule was not
relied on. A locally compiled drat-trim from the shipped C source was invoked
by a strict proxy that removes `-w`, requires one exact `s VERIFIED`, return
code 0, and zero warnings. Hashes from the previous package provide a useful
cross-check only after comparing formulas and proof bytes, never as a
substitute for replay.

## 2. Complete official run under the strict proxy

```sh
ROOT="$PWD"
P="$ROOT/.scratch/case0-24-patterns-v1/src/K58_case0_24_patterns"
D="$ROOT/.scratch/case0-24-patterns-v1/strict-verifier"
mkdir -p "$D/bin" "$D/tools" "$D/strict-logs" "$D/tmp"
cc -std=c99 -D_GNU_SOURCE -O2 "$P/tools/drat-trim.c" -o "$D/bin/drat-trim"
cp "$ROOT/.scratch/two-site-consequences-v1/tools/strict-drat-wrap.py" "$D/tools/strict-drat-wrap.py"
chmod +x "$D/tools/strict-drat-wrap.py"
export AUDIT_ROOT="$D" AUDIT_REAL_DRAT_TRIM="$D/bin/drat-trim" TMPDIR="$D/tmp"
export PYTHONDONTWRITEBYTECODE=1 K58_VERIFY_WORKERS=4
cd "$P"
python3 -B "$P/replay.py" "$D/tools/strict-drat-wrap.py" > "$D/verify.out"
```

This background job `jmwzfr9mg` completed successfully. Its stdout is:

```text
Checked source coverage, all 24 patterns and all 217 arm alternatives.
Remaining patterns and open arm counts []
Verified conditional clauses [[-2721, -2766]]

calls 236 accepted 236 seconds 115.72383641055785
```

The expected receipt count is independently checked, not inferred from that
line: 2 old pivot eliminations + 2 word covers + 1 unsplit frontier + 24 arm
covers + 4 direct word refutations + 203 arm refutations = **236**.

Every raw output was parsed separately. For each call it has one exact
`s VERIFIED`, no `WARNING` or `ERROR`, `0 RAT lemmas in core`, and its reported
proof-byte read equals the actual decompressed proof length. All 236 whole
proof files were consumed. The packaged default `-w` verifier alone would be
insufficient because warning-bearing acceptance is possible; there are no
such accepted warnings in this run.

## 3. Independent DAG and identity reconstruction

[independent_audit.py](independent_audit.py) is separate code. It constructs
the requested CNFs directly from the parent, validates all predecessor case
boundaries and compares all expected query/proof pairs with the strict logs.
Reproduce with:

```sh
python3 -B research/k58-case0-24-patterns/checks/independent_audit.py \
  .scratch/case0-24-patterns-v1/src/K58_case0_24_patterns \
  .scratch/two-site-consequences-v1/src/K58_two_site_consequences \
  .scratch/case0-24-patterns-v1/strict-verifier/strict-receipts.jsonl \
  research/k58-case0-24-patterns/checks/2-compute.json
```

Result: **2,113 assertions pass**, with no SAT solver call. In particular:

- The parent hash is exactly the previous one, dimensions 19218/178823, with
  all 1653/9918/123424 graph-constraint clauses present.
- `[(31,13),0] -> 2721`, `[(42,13),1] -> 2766`, and the pivot map is correct;
  the parent has all pivot at-least/at-most clauses.
- Only pivots 1 and 2 are eliminated in prior event evidence.
- New words are exactly the seven plus seventeen prior OPEN words. Previous
  branch proofs have same word lists, query hashes and raw proof bytes.
- All 217 arm assignments are 91-colour strings on the 14-vertex complete arm;
  they are distinct within each word's list.
- Every one of the 24 arm-cover and 207 terminal proof queries matches its
  record and every reference proof digest.
- Every arm is a direct CLOSED terminal; there are no active forced groups
  or deeper colour splits. `open_patterns` and the open-leaves data rows are
  empty by independent enumeration, not taking a status label at face value.
- All 236 proof files are used once; none is orphaned.
- Strict receipts, as a multiset of `(query SHA, proof SHA, accepted, rc=0)`,
  equal the expected list from the newly written DAG reconstruction.

Receipt: [2-compute.json](2-compute.json), including every query/proof digest.

## 4. Negative controls

```sh
python3 -B research/k58-case0-24-patterns/checks/negative_controls.py \
  .scratch/case0-24-patterns-v1/src/K58_case0_24_patterns \
  .scratch/case0-24-patterns-v1/strict-verifier/bin/drat-trim \
  .scratch/case0-24-patterns-v1/negative-controls \
  research/k58-case0-24-patterns/checks/negative-controls.json
```

Both finished normally as negative controls:

```text
satisfiable_units_query rejected rc 1 verified_lines 0 warnings 15129 errors 0
genuine_proof_half_truncated rejected rc 1 verified_lines 0 warnings 0 errors 1
```

The first control uses only the pin units. It is SAT by construction since
there are no no-monochromatic-triangle or AMO clauses in this control formula.
Duplicates caused by the full 14-vertex arm already containing the pivot and
word edges are harmless positive units. The second uses the genuine complete
query but only the first half of its proof. The accepted proof on its actual
query was already independently replayed; neither rejected control can be
used as additional evidence for a new closure.

## 5. Skipped or unverified checks

No Lean or semantic kernel check exists for this source package: it gives
CNF/proof objects, not a Lean statement. No new Lean proof or direct root-CNF
SAT search was attempted within this audit. The advertised binary clause is
proved by replayed finite case analysis, not by making a standalone DRAT
proof for `P + 2721 + 2766`.

The old event's pivot 0/3 records remain `OPEN_UNKNOWN`; that is not a SAT
claim. Nothing here closes representative 0, an unconditional branch, the
production wall, or `R(3,3,3,3)`. The title's local-to-representative wording
is essential.
