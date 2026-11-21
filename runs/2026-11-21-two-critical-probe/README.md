# The five two-critical profiles at the standard retry budget — 0 of 68

`review/WEAK_PROFILE_EXPERIMENT.md` measured the two *one-critical* profiles
(`(15,14,14,14)`, `(16,14,14,13)`: 469 cases) and concluded that the small
profiles are not a compute problem. That conclusion covered 12,054 cases, but
11,116 of them — all five *two-critical* profiles, and seven-eighths of the
wall — had never been run at any budget above 12 s. This is that measurement.

## Design

Stratified sample: two cases from each of the 34 `(profile, kinds, marked_size)`
groups the five profiles split into, drawn with a fixed seed (2026) from the
ledger's OPEN rows. 68 cases. `IDS.txt` lists them in draw order; `CASES.tsv`
gives each one's group and both results.

| profile | OPEN in ledger | sampled |
| --- | ---: | ---: |
| `(15,15,14,13)` | 7,732 | 12 |
| `(16,15,14,12)` | 2,058 | 16 |
| `(16,15,13,13)` | 1,046 | 16 |
| `(16,16,14,11)` | 140 | 12 |
| `(16,16,13,12)` | 140 | 12 |
| **total** | **11,116** | **68** |

Both tiers of the standard pipeline, in order, so the retry tier sees a real
first attempt: `run_cover.py --tier both`, 12 s / 400,000 conflicts then 70 s /
2,400,000 conflicts with `full_root` (the stronger encoding that asserts
`H(r) ≥ w(r)` itself), 3 workers, Kissat 4.0.4
(`b77de62fb1945d2ffab165b1f05e25c9e8ae7fc43de3a4fb8346fc2c9954097f`) and
drat-trim (`48891f3f9dfccbbebfc6a21fa9e6daa6b674900a3f65b16a0b0f7f21d8a03bce`),
the checker capped at 300 s by `tools/patch_run_cover_timeout.py`.

## Result

**0 of 68 closed, at either tier.** 136 receipts, every one `OPEN`.

The failure is not a fast tail that a better sample would miss: all 68 cases
consumed their entire budget. Retry-tier solver CPU is 70.0 s on all 68 (mean,
median and maximum are the same number), peak RSS 233 MiB; the tier spent
4,759 CPU-s — 32 minutes of wall time on 3 workers — without producing one
certificate.

With 0 successes in 68 the rule of three puts a 95 % upper bound of 3/68 = 4.4 %
on the closure rate, i.e. **at most ~490 of the 11,116** would close at this
budget even under that bound. The extra clause set is 55,241 to 68,078 clauses
on top of the host formula, so these are not near-trivial instances.

## What this settles

The wall is twelve thousand cases, not four hundred and seventy: the sample
spans every group of the five profiles that hold 7,732 + 2,058 + 1,046 + 140 +
140 open rows. Together with `runs/2026-11-16-small-probe/` (0/98 at the
first-pass budget, all seven profiles) and
`review/WEAK_PROFILE_EXPERIMENT.md` (0/51 on the one-critical pair at 60 s,
0/9 at 300 s), every one of the seven small profiles has now been measured at
or above the retry budget and closed nothing.

## Reproduce

```sh
cd .scratch/k58 && . .venv/bin/activate
mapfile -t ids < ../../runs/2026-11-21-two-critical-probe/IDS.txt
sel=(); for id in "${ids[@]}"; do sel+=(--case-id "$id"); done
python3 run_cover.py --ledger case-ledger.jsonl.gz --tier both \
  --kissat ../tools/kissat/build/kissat \
  --checker ../tools/drat-trim/drat-trim \
  --output ../probe2c --workers 3 "${sel[@]}"
```
