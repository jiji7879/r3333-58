# Four one-hour records against the wall, 2026-11-23

One case per small profile, at the **release** budget rather than the first-pass budget: 3600 s
and 200,000,000 conflicts per case, one worker per case, four cases in parallel.

```
cd .scratch/pkgchk2/k58-solver
./k58.sh run --profile <P> --shards 7 --shard 0 --limit 1 --workers 1 \
    --seconds 3600 --conflicts 200000000 --out evidence-hour
```

for `P` = `15,15,14,13`, `16,15,14,12`, `16,15,13,13`, `15,14,14,14`. Package:
`dist/k58-solver.zip` (2026-11-23, sha256 `b09058a3…`), smoke-tested 5/5 first.

## Why this run exists

Every earlier measurement of these rows used a first-pass budget (12 s / 400k conflicts) and closed
nothing. The question here is not "is the row satisfiable" but **"does an hour at the release
budget change the verdict"** — because if it does, the wall is a sizing problem; if it does not, it
is a depth problem, and no wall-clock per case will close 11,585 rows.

## Result: 0 of 4 closed

Per-case records are the JSONL files under `evidence-hour/<xx>/<id>/first/`; the table is parsed
from them, not typed.

| profile | case | branch | charge | wall s | CPU s | CPU/wall | status |
|---|---|---|---|---|---|---|---|
| `15,15,14,13` | `TT--_0_4` | 4 | 2 | 3600.0 | 1496.9 | 41.6 % | **OPEN** |
| `16,15,14,12` | `TT--_0_6` | 6 | 1 | 3600.0 | 1497.8 | 41.6 % | **OPEN** |
| `16,15,13,13` | `TT--_0_4` | 4 | 1 | 3600.0 | 1499.7 | 41.7 % | **OPEN** |
| `15,14,14,14` | `T---_0_4` | 4 | 15 | 3600.0 | 1499.5 | 41.7 % | **OPEN** |

Totals: 14,400 s wall, **5,993.9 solver CPU-seconds**, 0 verified identities, 0 proofs retained.
Every row is exactly as OPEN as it was at 12 s.

## Reading

**1. An hour of wall clock bought 25 minutes of search.** Each case used 1,497–1,500 CPU-s of a
3,600 s run: 41.6 % of one core. Four cases plus two Ultramath swarms plus a short Lean build were
sharing four cores, so the machine was oversubscribed by a factor of ~2.4. The numbers below are
therefore a *lower* bound on what an hour buys; on a quiet 4-core VM the same four cases would get
~1 core each.

**2. Scaling to the 12-core box does not rescue it.** With one worker per case on 12 cores, each
case would get ~3,600 CPU-s — 2.4× what is measured here. The certificate stream is the reason to
doubt that this changes any verdict: it was still growing linearly at 45 minutes.

**3. The checker cap, not the solver, is the binding constraint on a closure.** At 45 minutes the
four DRAT streams were 3.0, 3.4, 3.1 and 5.6 GB and still growing, so a full hour emits roughly
4–7 GB per case. The harness runs `drat-trim` under a **300 s cap** (`run_cover.py`, "checker limit
300s, failures skip the case"). The campaign's own replay measurement gives the scale to compare
against: `finalise` replays 95 certificates in 233 CPU-s including CNF regeneration, ~2.5 CPU-s
each, at a **5.58 MB** mean certificate size. A 5 GB proof is ~900× that, i.e. **~2,000–2,500
CPU-s ≈ 30–40 minutes of checking per closure** — an extrapolation from the mean, not a measured
`drat-trim` run on a 5 GB file, but far enough past 300 s that the conclusion is safe: had one of
these rows closed, the harness would have recorded a failed check and skipped it. **Any hour-scale
sweep must raise the checker cap or it will discard the very closures it is looking for.**

**4. What was deleted.** The harness discarded all four proof streams (they were UNKNOWN, not
certificates) and kept the JSONL records; `evidence-hour/` is 92 KB. Formula hashes are in the
records (`formula_sha256`), e.g. `26a6a89a71f8…` for `T---_0_4`.

## Two instrument defects found

- **No conflict count is ever recorded.** The harness hard-codes `--quiet` into every Kissat call
  (`k58/run_cover.py`, `k58/cover_evidence.py:226`, `k58/profile_fast.py:65`,
  `k58/matched_anchor.py:84`). The JSONL has `elapsed`, `cpu_seconds`, `proof_bytes`,
  `formula_bytes` and the solver's name/version/hash — but no `conflicts`. The "200 M conflicts"
  budget
  is therefore a **setting, not a measurement**, and cannot be audited after the fact. Fix: drop
  `--quiet` and parse Kissat's statistics block.
- **`proof_bytes` records what was retained, not what was emitted.** All four records say
  `proof_bytes: 0` while the files on disk were already several GB. The emitted size — the only
  quantity that tells you whether a closure could be checked — is nowhere in the evidence. Fix:
  record the size and hash before deleting.
