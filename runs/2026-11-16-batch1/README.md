# 2026-11-16 batch 1 — 96 cases from the K58 cover

First run of the handoff's fixed batch (`FIRST_BATCH_IDS.txt`: 48 fresh OPEN
cases from each of the two largest profiles), on this VM, with the pinned
toolchain.

| | |
| --- | --- |
| requested | 96 (`48 x (15,15,15,12)`, `48 x (16,15,15,11)`) |
| certified UNSAT and replayed | **81** (34 / 47) |
| cut off at budget | 15 |
| of those, closed by the retry tier | 14 — but on a **stronger formula**, see `RETRY.md` |
| budget | 12 s, 400,000 conflicts, Kissat 4.0.4 |
| solver CPU, all attempts | 397.3 s |
| checker CPU (trim + replay) | 236.5 s |
| retained certificates | 83.8 MB compressed (1.03 MB per closed case) |
| median solve | 3.0 s |

Release manifest over this evidence root:

```
{"counts": {"CERTIFIED": 81, "LEGACY_EVIDENCE_NEEDED": 2144, "OPEN": 110954},
 "manifest_sha256": "6a0fc4f8090e786710f5c52d56dcb080050418277f8756587db0e41d8a646bae"}
```

`LEGACY_EVIDENCE_NEEDED = 2144` is the 1,743 historical closures plus the 401
profile/template exclusions of the handoff ledger, for which the bundle
contains no proof bytes (it ships five example certificates only).

## Contents

* `evidence/<xx>/<case_id>/` — one directory per requested case:
  `certificate.drat.gz` (trimmed proof), `verified.json` (formula hash, proof
  hash, solver identity and timing) for the 81 certified cases; `first/*.jsonl`
  attempt receipts for all 96, including the cut-offs.
* `retry-stronger-formula/<xx>/<case_id>/` — the 14 retry-tier certificates,
  which refute a formula with the extra `full_root` assumption. `RETRY.md`
  explains why they are not closures of their cases.
* `manifest-with-retry.json` — the manifest that counts those 14 as CERTIFIED
  (95 in total). It is kept as the demonstration that the pipeline cannot
  distinguish them.
* `CASES.tsv` — id, profile, kinds, arm, branch, status, solver CPU, bytes.
* `manifest.json`, `cases.jsonl.gz` — the release manifest built by
  `cover_evidence.py manifest` and the per-case index it covers.
* `manifest-result.json` — the printed manifest hash above.

## Replay

With the handoff bundle unpacked at `K58` and drat-trim built:

```sh
python3 "$K58/cover_evidence.py" --root evidence verify . \
  --manifest-sha256 6a0fc4f8090e786710f5c52d56dcb080050418277f8756587db0e41d8a646bae \
  --checker /path/to/drat-trim
```

This regenerates every one of the 113,179 case formulas from the bundle's
generators, checks the case ids against the ledger, and replays all 81
certificates against the exact regenerated CNFs. It must print
`"replayed": 81` before the certificate files here mean anything.
