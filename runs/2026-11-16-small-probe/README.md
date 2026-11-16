# 2026-11-16 probe — the seven small profiles at the first-pass budget

The handoff's pilot reported **0 closures in 306 sampled cases** from the seven
smaller profiles and flagged that its weighted projection is weakest exactly
there. This probe tests that on fresh cases: 14 random OPEN ids from each
profile, 12 s / 400,000 conflicts, Kissat 4.0.4, 3 workers.

Result: **0 certified, 98 of 98 cut off**, 573 s of solver CPU.

| profile | OPEN cases in ledger | sampled | closed |
| --- | ---: | ---: | ---: |
| (15,15,14,13) | 7,732 | 14 | 0 |
| (16,15,14,12) | 2,058 | 14 | 0 |
| (16,15,13,13) | 1,046 | 14 | 0 |
| (15,14,14,14) | 381 | 14 | 0 |
| (16,16,14,11) | 140 | 14 | 0 |
| (16,16,13,12) | 140 | 14 | 0 |
| (16,14,14,13) | 88 | 14 | 0 |

The pilot's observation is not a sampling artefact. These 11,585 cases are the
campaign's wall: at the first-pass budget they yield nothing, and at the retry
budget (70 s / 2.4M conflicts) the whole profile has to be re-attempted with no
measured closure rate for six of the seven profiles.

Files: `IDS.txt` (the 98 ids), `CASES.tsv`, `receipts/` (the OPEN attempt
receipts, including solver CPU and peak RSS).
