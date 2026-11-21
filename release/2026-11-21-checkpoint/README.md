# Release checkpoint — 21 November 2026

79,264 of the 113,179 frozen cases refuted, with every certificate replayed
against its exact regenerated CNF.

```
manifest SHA-256  ce90ee33d7df566fe69f32405d693d7fe06942a4c6108e18d630b8f62226fc1d
```

| status | rows |
| --- | ---: |
| `CERTIFIED` | 79,264 |
| `LEGACY_EVIDENCE_NEEDED` | 2,144 |
| `OPEN` | 31,771 |
| total | 113,179 |

## Contents

* `manifest.json` — pins the ledger hash, the SHA-256 of each generator source,
  the python-sat version, and the digest of `cases.jsonl.gz`.
* `cases.jsonl.gz` — one line per cover case: status, and for a certified row the
  regenerated input hash, the proof hash, its size, the encoding recipe and the
  receipt that produced it. 113,179 rows, 16,031,141 bytes.
* `verify.json` — the independent replay transcript: **79,264 certificates, 0
  without a ledger row, `{"checked": 79264, "replayed": 79264, "failed": 0,
  "unknown": 0}`**.
* `coverage.json` — the manifest/coverage consistency check, which regenerates
  every cover case and compares it against the index with no replay.

Both file digests were checked here against the values the manifest claims:
`cases.jsonl.gz` hashes to `8c8b4e00…f7267` and `manifest.json` to
`ce90ee33…6fc1d`, as recorded.

## What this does and does not establish

**Established.** 79,264 of the 113,179 cases are unsatisfiable, each with a DRAT
certificate replayed against the CNF regenerated from its ledger row and recipe.
That is 70% of the cover.

**Not established.** The cover is not closed. Of the remaining 33,915 rows:

* 2,144 are cases where evidence is missing rather than work — 1,743 historical
  refutations whose proof bytes are in an archive not held here, and 401 profile
  and template exclusions that rest on arguments rather than per-case
  certificates.
* 31,771 are open: about 20,150 in profile `(15,15,15,12)`, and 11,585 in seven
  profiles never attempted, which closed at zero rate at the first-pass budget.

No claim about `R(3,3,3,3)` follows from this checkpoint alone.

## Independent replay

The certificates are bit-reproducible: re-running the pinned Kissat uncapped on
the regenerated CNF and trimming with the same drat-trim reproduces the stored
certificate byte for byte (verified 10/10 across both tiers). A reviewer with
the bundle and the pinned toolchain can therefore regenerate any case from its
ledger row and recipe in `cases.jsonl.gz` and compare hashes, rather than
transferring ~117 GB of certificates.

Pinned: Kissat 4.0.4 at `8af8e56`, drat-trim at `2e3b2dc`, python-sat
`1.9.dev22` — the last is load-bearing, since the CNF is regenerated through
`pysat.card.CardEnc` and a different version emits different clauses.
