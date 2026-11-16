# 2026-11-16 batch 1 — 96 cases from the K58 cover

First run of the handoff's fixed batch (`FIRST_BATCH_IDS.txt`: 48 fresh OPEN
cases from each of the two largest profiles), on this VM, with the pinned
toolchain.

| | |
| --- | --- |
| requested | 96 (`48 x (15,15,15,12)`, `48 x (16,15,15,11)`) |
| certified UNSAT and replayed | **95** (81 first pass, 14 retry) |
| still OPEN | 1 |
| first-pass closures | 34 / 48 and 47 / 48 |
| budget | 12 s, 400,000 conflicts, Kissat 4.0.4 |
| solver CPU | 397.3 s first pass + 314.1 s retry |
| checker CPU (trim + replay) | 236.5 s first pass (retry replays in `verification.json`) |
| retained certificates | 187.2 MB compressed (1.03 MB first pass, 7.4 MB retry) |
| median solve | 3.0 s |

Release manifest over this evidence root:

```
{"counts": {"CERTIFIED": 95, "LEGACY_EVIDENCE_NEEDED": 2144, "OPEN": 110940},
 "manifest_sha256": "cd112445d53eeb1f50af360b13321d0cd04bbab26cfa04dadb74c8981b4cd1fd"}
```

`LEGACY_EVIDENCE_NEEDED = 2144` is the 1,743 historical closures plus the 401
profile/template exclusions of the handoff ledger, for which the bundle
contains no proof bytes (it ships five example certificates only).

## Contents

* `evidence/<xx>/<case_id>/` — one directory per requested case:
  `certificate.drat.gz` (trimmed proof), `verified.json` (formula hash, proof
  hash, solver identity and timing) for the 81 certified cases; `first/*.jsonl`
  attempt receipts for all 96, including the cut-offs.
* `RETRY_TIER.md` — the two encodings used, and why both refute their case.
* `verification.json` — the independent replay of all 95 certificates through
  `cover_evidence.py verify` (`"replayed": 95`).
* `CASES.tsv` — id, profile, kinds, arm, branch, status, solver CPU, bytes.
* `manifest.json`, `cases.jsonl.gz` — the release manifest built by
  `cover_evidence.py manifest` and the per-case index it covers.
* `manifest-result.json` — the printed manifest hash above.

## Replay

With the handoff bundle unpacked at `K58` and drat-trim built:

```sh
python3 "$K58/cover_evidence.py" --root evidence verify . \
  --manifest-sha256 cd112445d53eeb1f50af360b13321d0cd04bbab26cfa04dadb74c8981b4cd1fd \
  --checker /path/to/drat-trim
```

This regenerates every one of the 113,179 case formulas from the bundle's
generators, checks the case ids against the ledger, and replays all 81
certificates against the exact regenerated CNFs. It must print
`"replayed": 95` before the certificate files here mean anything.
