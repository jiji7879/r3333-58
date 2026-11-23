# Two hours on one wall row: UNKNOWN at 170 M conflicts

Following the four one-hour records (`results/wall-hour-2026-11-23/`), the question was whether the
wall rows are a *sizing* problem — "give it enough time and it will answer" — or a *depth* problem.
This run answers it for one row with instrumentation the earlier runs did not have.

## Setup

- Case: `T---_0_4`, profile `(15,14,14,14)`, branch 4 — the same instance as the hour run.
  CNF regenerated from the frozen ledger row by the package's own encoder, 2,821,167 bytes,
  `sha256 26a6a89a71f8b3c9f4a0b246ceca862b…` — **identical to the hour-run CNF**, so this is a
  pure time extension, not a different case.
- Solver: `kissat` 4.0.4, `--verbose=1 --time=7700 --conflicts=2000000000`, one dedicated core,
  proof written to disk and kept.
- The earlier hour runs were CPU-starved (41.6 % of a core, ~25 CPU-minutes each). This one had a
  full core for 2 h 8 m — about **5× the search**.

## Result

```
c conflicts:      170,229,433        22,114 per second
c decisions:      959,507,634         5.64 per conflict
c propagations:    17,967,384,857
c restarts:       4,560,251           interval 37
c process-time:   2h 8m 18s
exit 0            (UNKNOWN — no verdict)
```

Proof stream: **44,972,455,119 bytes = 45.0 GB in 2 h 8 m = 21.0 GB per hour**, 264 bytes per
conflict. Hashed no, deleted yes: a DRAT stream with no empty clause is not a certificate.

## The trajectory

| time | conflicts | rate |
| ---: | ---: | ---: |
| 213 s | 7.47 M | 34,948/s |
| 1,394 s | 38.75 M | 27,791/s |
| 3,580 s | 83.36 M | 23,287/s |
| 6,038 s | 138.07 M | 22,869/s |
| 7,696 s | 170.21 M | 22,116/s |

The rate decays from ~35 k/s to ~22 k/s over the first hour and then **flattens**: 22.9 k/s at
6,038 s, 22.1 k/s at 7,696 s. The search is in a steady state, not collapsing and not accelerating
towards a refutation. 170 M conflicts is 425× the first-pass budget of 400 k, which closes nothing.

## What this settles, and what it does not

- **Settles**: 2 h 8 m and 170 M conflicts do not decide this row. "Give it more time" is false at
  this scale, measured rather than inferred.
- **Does not settle**: that no budget decides it. 170 M is not obviously near the threshold for a
  combinatorial UNSAT proof; 10⁹ is plausible.
- **The binding constraint is now storage, not time.** At 21 GB of certificate per hour of search,
  a 24 h run on this row needs **~500 GB** of proof — five times the free disk on this VM. The
  campaign's design (retain the proof, check it afterwards) cannot support multi-hour runs on the
  wall rows at all: it hits the disk long before it hits an answer.
- The earlier hour run's proofs were being written at ~18 GB per CPU-hour (measured at 41.6 % of a
  core); at full core the rate is 21 GB/h. Either way the same conclusion.

## Correction to an earlier figure

In a first reading of the progress lines the judge reported "167,201 conflicts at 1,634/s" at 102 s.
That was a misread: the column taken for conflicts was restarts. The true figure at 102 s was
3.67 M conflicts at ~36 k/s, and the final count is 170.2 M, not 167 k. The trajectory table above
is parsed from the correct column (field 9 of the progress line) and cross-checked against the
final statistics block, which agree to within one progress interval.
