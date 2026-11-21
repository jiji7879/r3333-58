# r3333-58

Working repository for the project on `R(3,3,3,3)`, the four-colour Ramsey
number for triangles. Two efforts live here.

## 1. Upper bound: the K58 campaign (current)

A handoff bundle proposes a computer-assisted proof of `R(3,3,3,3) <= 58` by a
frozen cover of 113,179 SAT cases, each refuted by Kissat with a DRAT proof
replayed by drat-trim. The bundle's ledger is frozen at 111,035 OPEN; the
campaign's own state is the release checkpoint below.

| status | rows |
| --- | ---: |
| `CERTIFIED` (replayed against regenerated CNFs) | 79,264 |
| `LEGACY_EVIDENCE_NEEDED` (1,743 historical + 401 scoped exclusions) | 2,144 |
| `OPEN` | 31,771 |

* [HANDOFF_NEXT_CHAT.md](HANDOFF_NEXT_CHAT.md) — **start here**: the state at
  the end of the last session, what is open in priority order, the traps that
  cost time, and how to work in this repository.
* [release/2026-11-21-checkpoint/](release/2026-11-21-checkpoint/) — the
  checkpoint: 113,179-row case index, manifest
  `ce90ee33d7df566fe69f32405d693d7fe06942a4c6108e18d630b8f62226fc1d`, and a
  replay transcript of `{"checked": 79264, "replayed": 79264, "failed": 0}`.
* [review/K58_CAMPAIGN_REVIEW.md](review/K58_CAMPAIGN_REVIEW.md) — what the
  bundle claims, what is checked here, the reduction read back in precise form,
  measured cost, and what is missing.
* [HANDOFF.md](HANDOFF.md) — the campaign written for a cold reader (LLM
  session or person): what is verified, what is blocked, the obligations in
  order. Its status table predates the checkpoint.
* [review/WEAK_PROFILE_EXPERIMENT.md](review/WEAK_PROFILE_EXPERIMENT.md) — why
  the remaining small profiles are not a compute problem.
* [lean/README.md](lean/README.md) — the kernel-checked formal core of the
  reduction: the degree cap, `R(3,3) ≤ 6` and `R(3,3,3) ≤ 17`, the ticket
  double counting, and the threshold step.  Build with `lean/build.sh`.

Where the 31,771 open rows are, and what each needs:

* **20,166** in `(15,15,15,12)` — throughput, not thought: that profile's retry
  tier closed 14/15 and 8/10 in samples. One retry-only pass is 20,166 × 70 s =
  ~390 CPU-h (≈33 h wall on 12 cores). Its certificates are large — the 2,297
  retry-tier certificates in the index average 28.6 MB, against 5.6 MB for the
  76,967 first-tier ones — so the pass emits ~480 GB of DRAT. `--publication`
  deletes each certificate after hashing it, so peak disk is a few hundred MB;
  keeping them needs a disk that size.
* **20** in `(16,15,15,11)` — the hard tail of a profile whose other 16,070
  rows are certified (the bulk run). The 20 are refuted from the 458 MB LFS
  archive (`runs/2026-11-21-hard-tail-16-15-15-11/`) as *split* certificates
  that the one-DRAT-per-case pipeline cannot carry, so they sit OPEN in the
  index; 83 further rows are historical evidence.
* **11,585** in the seven small profiles — **the wall**
  ([review/WALL_STRUCTURAL_NOTE.md](review/WALL_STRUCTURAL_NOTE.md) puts it in
  structural terms: these are exactly the profiles whose vertices have two or
  one colour-degrees `<= 14`, and the ticket argument's budget there is 15 to
  32 against 45 to 48 on the four reachable profiles). All seven have now
  been measured at or above the retry budget and closed nothing: 0/98 at 12 s
  ([runs/2026-11-16-small-probe/](runs/2026-11-16-small-probe/)), 0/68 at 70 s
  over the five two-critical profiles
  ([runs/2026-11-21-two-critical-probe/](runs/2026-11-21-two-critical-probe/)),
  0/51 at 60 s and 0/9 at 300 s on the one-critical pair. A case here pins one
  or two rigid blocks and leaves 42 or 27 of 57 vertices free; refuting one is
  close to the original problem.

Status in one line: 70 % of the cover is certified and replayed, but the
reduction at n = 58 is unformalised, 2,144 rows have no proof bytes here, and
a tenth of the cover does not fall to any budget tried. No bound moves yet.

## 2. Lower bound: previous work

`results/`, `artifacts/` and `tools/` hold the earlier work on the lower bound
side: three verified non-isomorphic 4-colourings of K_50 (so `R >= 51`), a
kernel-checked Lean certificate, the primitivity theorem for triangle-free
4-colourings of `K_n` with `n >= 51`, and the analysis of the 1-defect K_51
near-miss. Start at [results/summary.md](results/summary.md).

## Reproducing

The K58 runner needs the handoff bundle (not redistributed here), python-sat
1.9.dev22, Kissat 4.0.4 and drat-trim. The bundle pins the python-sat version
string in its manifest, so the venv must be exact. The certificates under
`runs/` replay against formulas regenerated from that bundle; their case ids
are content hashes, so a replay either matches or fails loudly.
