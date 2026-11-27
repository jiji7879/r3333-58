# The release of 2026-11-27: 101,586 of 113,179 rows certified

Bundle: `manifest.json`, `cases.jsonl.gz` (19,205,914 bytes, sha256 `9390bf50…`),
`release.coverage.json`, `release.manifest.log`, `RUN_SUMMARY.md`. Manifest
`f18136daa9db26e6b6941ce3dea3298fe3e95d99f090e65cd7f8646643718ad9`; replay line
`{"checked": 101586, "replayed": 101586, "failed": 0, "unknown": 0}`.

`python3 tools/audit_release.py <bundle>` prints `AUDIT PASSED`:

| check | result |
| --- | --- |
| cases bytes / sha256 vs manifest | 19,205,914 / `9390bf50…` both match |
| ledger_sha256 vs the frozen ledger | `d34e8b27689d…`, identical |
| ids | 113,179 rows, 0 unknown, 0 duplicates |
| counts | 101,586 + 11,593 = 113,179 |
| generators | `run_cover.py` = `d26f6ffc…`, byte-identical to `tools/selfcontained/k58new/run_cover.py`; the other ten are the audited encoders |
| sampled rows rebuilt from ledger row + recipe | 12 of 12 |

## Where the 11,593 open rows are

| profile | CERTIFIED | OPEN |
| --- | ---: | ---: |
| 15,15,15,12 | 83,432 | **8** |
| 16,15,15,11 | 16,173 | **0** |
| 16,16,15,10 | 1,767 | 0 |
| 16,16,16,9 | 214 | 0 |
| 15,15,14,13 | 0 | 7,732 |
| 16,15,14,12 | 0 | 2,058 |
| 16,15,13,13 | 0 | 1,046 |
| 15,14,14,14 | 0 | 381 |
| 16,16,14,11 | 0 | 140 |
| 16,16,13,12 | 0 | 140 |
| 16,14,14,13 | 0 | 88 |

`(16,15,15,11)` is complete, and `(15,15,15,12)` is 8 rows from complete. The
remaining 11,585 are the seven small profiles, every row still open.

## Recipes

79,111 closures used `full_root=false`, 22,475 used `full_root=true` (the retry
tier and the re-solve of the legacy rows). `full_root` is the `H(r) >= w(r)`
strengthening, implied by the row's charge pin, so both are sound; the split is
recorded so a reader can see which recipe each certificate used.

## What this does and does not establish

It establishes that 101,586 of the 113,179 frozen cover rows are UNSAT, with
certificates replayed against CNFs regenerated from their ledger rows and recipes.
It does not move `R_4(3)`: the cover's completeness is the kernel-checked
`K58.Replay.frozenCover` (a separate obligation), the Lean bridge at `n = 58` is
not written, and 11,585 wall rows stand open.
