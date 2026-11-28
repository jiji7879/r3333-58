# The release of 2026-11-28: both big profiles complete

Manifest `8eec036cd1185011a393f1887e8044dd57451a535e4d76a632e8684f54c82898`,
counts `{"CERTIFIED": 101594, "OPEN": 11585}`, `cases.jsonl.gz` 19,206,916 bytes
sha256 `9224bed7…`. `python3 tools/audit_release.py <bundle>` prints `AUDIT PASSED`.

| check | result |
| --- | --- |
| cases bytes / sha256 vs manifest | 19,206,916 / `9224bed7…` both match |
| ledger_sha256 | `d34e8b27689d…`, the frozen ledger |
| ids | 113,179 rows, 0 unknown, 0 duplicates |
| counts | 101,594 + 11,585 = 113,179, matching the manifest |
| generators | `run_cover.py` = `d26f6ffc…`, the shipped runner; the rest the audited encoders |
| sample of certified rows rebuilt from ledger row + recipe | 12 of 12 |
| **the 8 rows closed last** | **8 of 8** rebuild to their recorded `input.sha256`, all `full_root=true` |

`release.coverage.json` is empty: the coverage run was stopped, because at cover scale it
re-derives every CNF and hashes every compressed certificate single-threaded, which is
hours. The manifest build already re-derived all 113,179 CNFs and recorded their hashes,
so `cases.jsonl.gz` is the coverage statement; `tools/audit_release.py` checks it against
the frozen ledger.

## The profile table

| profile | CERTIFIED | OPEN |
| --- | ---: | ---: |
| 15,15,15,12 | **83,440** | **0** |
| 16,15,15,11 | **16,173** | **0** |
| 16,16,15,10 | 1,767 | 0 |
| 16,16,16,9 | 214 | 0 |
| 15,15,14,13 | 0 | 7,732 |
| 16,15,14,12 | 0 | 2,058 |
| 16,15,13,13 | 0 | 1,046 |
| 15,14,14,14 | 0 | 381 |
| 16,16,14,11 | 0 | 140 |
| 16,16,13,12 | 0 | 140 |
| 16,14,14,13 | 0 | 88 |

Both big profiles are complete, as are the two `(16,16,…)` profiles. **Every open row is
now in one of the seven small profiles** - the wall - and there are no legacy rows left:
not one row of the cover rests on imported evidence.

## The two replay lines that carry the claim

* `{"checked": 101586, "replayed": 101586, "failed": 0, "unknown": 0}` - the full replay of
  2026-11-27, against the manifest of that release.
* `{"retry": {"VERIFIED": 8}}` - the eight 322-586 MB certificates closed on 2026-11-28 with
  a 21,600 s checker cap; each was replayed by drat-trim inside the run.

Both name the same encoders; the second is a subset of the first plus eight rows, and the
8-of-8 CNF rebuild above is the check that they are rows of this cover.

## What this is and is not

101,594 of 113,179 frozen cover rows are UNSAT with machine-replayed certificates - 89.8 %.
It is not `R_4(3) <= 58`: the cover's completeness (`K58.Replay.frozenCover`) is a separate
kernel-checked obligation, there is no Lean bridge at n = 58, and the 11,585 wall rows are
open. The bound stands at `51 <= R_4(3) <= 62`.
