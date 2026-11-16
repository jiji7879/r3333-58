# r3333-58

Working repository for the project on `R(3,3,3,3)`, the four-colour Ramsey
number for triangles. Two efforts live here.

## 1. Upper bound: the K58 campaign (current)

A handoff bundle proposes a computer-assisted proof of `R(3,3,3,3) <= 58` by a
frozen cover of 113,179 SAT cases, each refuted by Kissat with a DRAT proof
replayed by drat-trim. The bundle's ledger currently has 111,035 cases OPEN.

* [review/K58_CAMPAIGN_REVIEW.md](review/K58_CAMPAIGN_REVIEW.md) — what the
  bundle claims, what is checked here, the reduction read back in precise form,
  measured cost, and what is missing.
* [runs/2026-11-16-batch1/](runs/2026-11-16-batch1/) — the first batch run
  here: 96 requested cases, **81 certified and replayed**, 15 cut off at the
  12 s budget, with the release manifest and the compressed certificates.

Status in one line: the pipeline works and its arithmetic is consistent, but
the retry tier refutes a stronger formula than the cases it files under, the
reduction at n = 58 is unformalised, and 2,144 rows of the frozen ledger have
no proof bytes in the handoff. No bound moves yet.

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
