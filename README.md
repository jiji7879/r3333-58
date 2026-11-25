# r3333-58

Working repository for the project on `R(3,3,3,3)`, the four-colour Ramsey
number for triangles. Two efforts live here.

## Manuscript

The working paper is [paper/main.pdf](paper/main.pdf), with source in
[paper/main.tex](paper/main.tex). It presents the certified common-critical
obstruction, the reciprocal-profile restriction, and an audit of the unfinished
K58 computation. It does **not** claim `R(3,3,3,3) <= 58`. Build and numerical
checks are documented in [paper/README.md](paper/README.md); exact verification
scope is recorded in [paper/VERIFICATION.md](paper/VERIFICATION.md).

## 1. Upper bound: the K58 campaign (current)

A handoff bundle proposes a computer-assisted proof of `R(3,3,3,3) <= 58` by a
frozen cover of 113,179 SAT cases, each refuted by Kissat with a DRAT proof
replayed by drat-trim. The bundle's ledger is frozen at 111,035 OPEN; the latest
run against it is the 2026-11-25 one below.

| status | rows |
| --- | ---: |
| `CERTIFIED` (replayed against regenerated CNFs) | 98,142 |
| `LEGACY_EVIDENCE_NEEDED` (1,743 historical + 401 scoped exclusions) | 2,144 |
| `OPEN` | 12,893 |

The 2026-11-25 run on the owner's machine closed **18,858** rows in one pass:
manifest `98d82268ff4c277820f00cbed3405c625dbb53d3603610e45eacc73b562b19f9`,
replay `{"checked": 98142, "replayed": 98142, "failed": 0}`.
[results/k58-full-cover-run-2026-11-25/](results/k58-full-cover-run-2026-11-25/)
records the audit of that bundle: the case index and the frozen ledger match it
byte for byte, and twelve sampled rows rebuild to their recorded CNF hashes.
The proofs themselves were never sent here, so the replay line is the owner's
report, not an independently confirmed fact.

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

Where the 12,893 open rows are, and what each needs:

* **1,308** in the two big profiles — 1,288 in `(15,15,15,12)` and 20 in
  `(16,15,15,11)`. The 20 are refuted from the 458 MB LFS archive
  (`runs/2026-11-21-hard-tail-16-15-15-11/`) as *split* certificates that the
  one-DRAT-per-case pipeline cannot carry, so they sit OPEN in the index; the
  1,288 are the retry tail, throughput rather than thought. A retry pass over
  them is ~25 CPU-h and emits large certificates — the index's retry-tier
  entries average 28.6 MB against 5.6 MB first-tier, and `--publication`
  deletes each proof after hashing it.
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

Status in one line: 87 % of the cover (98,142 of 113,179) is certified and
replayed; the 12,893 that remain are 11,585 small-profile rows no budget has
touched plus a 1,308-row tail; 2,144 rows have no proof bytes here; and the
reduction at n = 58 is still unformalised. No bound moves yet.

Two side results from the same period, both certified and both explicitly
non-progress on the bound:

* [results/k58-full-cover-run-2026-11-25/](results/k58-full-cover-run-2026-11-25/)
  — the audit of the 98,142-row run.
* [results/pb-balance-2026-11-24/](results/pb-balance-2026-11-24/) — the
  perfect-balance sub-case: 29 of the 381 `(15,14,14,14)` rows die on a ticket
  pin with a replayed proof, the other 352 stay UNKNOWN at every budget and
  encoding tried, and no isomorphism reduction exists.

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
