# The full-cover run of 2026-11-25, audited from the bundle alone

The person ran `k58-batch.sh` over the frozen cover on their own machine and sent the release
bundle: `manifest.json`, `cases.jsonl.gz` (18,727,180 bytes), `release.verify.json`,
`release.coverage.json`, `release.manifest.log`, `RUN_SUMMARY.md`. No evidence was sent (350 GB
stayed on their disk). This file records what was checked here, on 2026-11-25, and what was not.

## The claim in the bundle

    98,142 certificates, 0 without a ledger row, 24 workers
    {"checked": 98142, "replayed": 98142, "failed": 0, "unknown": 0}

with manifest `98d82268ff4c277820f00cbed3405c625dbb53d3603610e45eacc73b562b19f9` and counts
CERTIFIED 98,142 / OPEN 12,893 / LEGACY_EVIDENCE_NEEDED 2,144.

## What reproduces exactly

| check | result |
| --- | --- |
| `cases.jsonl.gz` bytes and sha256 against the manifest | 18,727,180 and `1da95e15…` both match |
| `ledger_sha256` against the frozen ledger | `d34e8b27689d…` — identical file |
| row count and identity | 113,179 lines, 113,179 unique ids, 0 absent from the frozen ledger |
| counts | 98,142 + 12,893 + 2,144 = 113,179 |
| the 11 `generators` hashes | all resolve; 10 are the pristine bundle, `run_cover.py` is the delivered package's copy (`1f4e67ae…`), whose only diff from the pristine runner is the configurable 300 s checker cap - no change to the CNF path |
| **instance reproduction** | 12 random certified rows rebuilt from the frozen ledger row + the recorded `recipe` give the recorded `input.sha256` and byte count, 12 of 12 |

So the objects refuted are the rows of the frozen cover, not lookalikes, and the manifest pins the
encoders the campaign audited.

## What the 12,893 open rows are

| profile | CERTIFIED | OPEN | LEGACY |
| --- | ---: | ---: | ---: |
| 15,15,15,12 | 82,072 | 1,288 | 80 |
| 16,15,15,11 | 16,070 | 20 | 83 |
| 15,15,14,13 | 0 | 7,732 | 0 |
| 16,15,14,12 | 0 | 2,058 | 0 |
| 16,15,13,13 | 0 | 1,046 | 0 |
| 15,14,14,14 | 0 | 381 | 0 |
| 16,16,14,11 | 0 | 140 | 0 |
| 16,16,13,12 | 0 | 140 | 0 |
| 16,14,14,13 | 0 | 88 | 0 |
| 16,16,15,10 | 0 | 0 | 1,767 |
| 16,16,16,9 | 0 | 0 | 214 |

Both big profiles are all but closed (1,308 rows left, the retry tail); every one of the seven
small profiles is untouched (11,585 rows); the 2,144 legacy rows are the 1,743 historical ones
(the 11.4 GB store that is not here) and the 401 scoped exclusions.

**Recipes.** 76,967 closures used `full_root=false`, 21,175 used `full_root=true` (the retry
tier). `full_root` is the `H(r) >= w(r)` strengthening, which the campaign verified is implied by
the row's charge pin, so both are sound - but a write-up should say that 21,175 of the 98,142 rest
on the stronger recipe rather than leave it implicit.

## What was not checked

The 98,142 proofs. The replay line is theirs: `verify_parallel.py` rebuilds each CNF, checks it
against the recorded input hash, decompresses the certificate and requires `s VERIFIED` from
drat-trim, and it reports 0 failures - but that ran on their machine with their checker. Nothing
in this bundle can confirm it, because the certificates were not sent.

The cheapest way to close that: send three case directories from `evidence/` -
`<xx>/<id>/verified.json` and `certificate.drat.gz` - one `full_root=false`, one `full_root=true`,
one from `16,15,15,11`. Each is a few MB; rebuilding and replaying them here takes seconds.

## What it is not

`R_4(3) <= 58` needs all 113,179 rows decided plus the cover-completeness theorem
(`K58.Replay.frozenCover`). This run decides 98,142. The bound has not moved.
