# Reproduction and receipts

The input archive SHA-256 is
`08a1e2e9513ade7dffab4d8ff89fb5f2f5dc04e68d8928ff8cf54cded9093873`.
All writes were made to disposable copies. No supplied measurement was
silently overwritten and no production CNF/queue was touched.

## 1. Finite enumeration and literal normalisation

```sh
.scratch/k58/.venv/bin/python \
  research/k58-square-spoke-wall-test/checks/normalization.py \
  .scratch/k58-square-spoke-wall-test-v1/src \
  research/k58-square-spoke-wall-test/checks/normalization.json
```

Exit 0. The script exhaustively computes exact CNF isomorphism under explicit
maps: 144 labelled pairs of valid group colourings and six square/matching
assignments. Its output is `normalization.json`. Member m1's independent four
explicit variant maps are in `flavours.log`/`flavours.json`; these are cheap
redundancy, not substitutes for the finite case proof.

Intermittent failures in writing this checker (incidental clause-order
comparison, a symmetric adjacency error, and an unnecessary additional local
palette swap) were corrected before recording results. There was no SAT
search hidden behind this checker. It does not itself establish UNSAT; the
native/RUP certificates do that.

## 2. Models, native strict proof and independent RUP

```sh
.scratch/k58/.venv/bin/python research/k58-square-spoke-wall-test/checks/local_models.py SOURCE local-models.json
.scratch/k58/.venv/bin/python research/k58-square-spoke-wall-test/checks/rup_check.py SOURCE > rup_check.log
.scratch/k58/.venv/bin/python research/k58-square-spoke-wall-test/checks/rup_negative.py SOURCE > rup_negative.log
cc -std=c99 -D_GNU_SOURCE -O2 SOURCE/hard-study/tools/drat-trim.c -o AUDIT/bin/drat-trim
.scratch/k58/.venv/bin/python research/k58-square-spoke-wall-test/checks/strict_replay.py SOURCE AUDIT/bin/drat-trim AUDIT/out
```

Here `SOURCE` is the extracted archive root (containing `next/`) and `AUDIT`
is a new disposable output root. `strict_replay.out` is the fresh receipt
from the newly compiled checker used for this audit; it is not an arm of the
solver benchmark.

The receipt `local-models.json` and log `local_models.log` validate both exact
formulas and combinatorial structures. `direct-receipts.json` records native
proof replay. `strict_original.log`, `strict_deletions_ignored.log` and
`negative_path.log` contain complete drat-trim outputs and exit codes.

`rup_check.log` says 315 variables, 1825 clauses, 24,384 records, 11,868
additions, 12,516 deletions ignored and zero non-RUP additions. The algorithm
assumes a clause counts each literal at most once; this is not merely assumed
on this input: `direct-receipts.json` checks zero duplicate literals and zero
complementary literal pairs in base/proof clauses.

m3's original diagnostic log `rup_negative-member.log` has one print-label error: for base
`[[1,2],[-1,2],[1,-2]]`, RUP([1]) is True and should be so (taking x1 false
forces x2 then conflicting units), while RUP([-1]) is False. Its line says
“expect False” after a True result. This is a logging expectation typo, not
an accepted false proof: the engine returned the mathematically correct
answer and the coordinator separately checked the case by hand. The path and
K14 full-trace controls fail respectively at additions 27 and 1. The native
path control produces no VERIFIED line. `rup_negative.py` adapts the same
tests with the corrected True expectation as an assertion and fresh receipts
in `rup_negative.log`; the original diagnostic log is retained separately.

Member claim-ceiling notes are in `claim-ceiling-member.md`, including their
own disclaimer that normalization/parent regeneration lie outside d4. The
query digest was newly pinned above; the archive does not itself do so.

## 3. Ordinary-wall reconstruction and bounded controls

Fresh previous-run working directory:
`.scratch/k58-square-spoke-wall-test-v1/review-m2/` (scripts `stage2.py` to
`stage4.py`; `inp` uses the independent m2 input copy and captured absolute
`ROOT`). `stage2.out` contains zero missing/extra rules per row. `stage3.json`
and `stage3.out` record exact hashes, guards, geometry and omissions.
`stage4-cubes.json`/`.out` are ten original-parent OPEN calls;
`stage4-bench.json`/`.out` are eight bounded comparisons.

The original first-tier encoder call is explicitly
`dict(tables=True,total_critical=True,full_root=False)` in stage2. Guard
semantics are tested by a solver on each actual physical block: exceeding the
remaining cap is UNSAT, whereas a tight assignment and negated guard permit
models. No guard-activation inference is made.

## 4. Historical controls

`hist2.json` is the corrected 13-row run from
`.scratch/k58-square-spoke-wall-test-v1/review-m4-v2/`. It reproduces parent
hashes, seed/neighbour counts, propagation gains and square lengths.
`guardscope.json` and `s5.out` check sender/colour/non-arm scope: 0 of 269,150
edge-literal occurrences fall outside it. These receipts concern the 13
`full_root=True` inputs, not the ordinary 14. Only these corrected reports
are retained. No stored status is promoted to a minimality or final-row
result.

## 5. Checks not performed and final scope

No new large SAT/SLS run, publication export, or production search started.
No LRAT/Lean or semantic marking-lemma certificate exists for this package.
Native DRAT/RUP checks certify the K15 formula and/or an explicitly identified
query; they are not kernel-checked semantic proofs of the whole K58 cover.
No whole-parent DRAT exists locally for the ten nominated ordinary-wall
OPEN cubes.

Regenerations must retain the supplied inputs intact and use source/parent
hashes rather than filenames alone. The detailed mathematical statement and
limits are [../audit.md](../audit.md).
