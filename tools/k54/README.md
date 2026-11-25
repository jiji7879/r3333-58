# K54 count-model tools

Extracted from the swarm directories of 19 Nov 2026 so that they survive pruning of
`repo/.ultramath/` (which is gitignored and large). Each is self-contained: it reads the archive
at `repo/work/k54/` and needs nothing else.

Run them from the archive root (`repo/work/k54/`):

```sh
python3 ../../tools/k54/rowsum.py live-17 --timelimit 120          # rectangle-row-sum relaxation
python3 ../../tools/k54/rowsum_bb.py live-17 --seconds 200         # branch and bound on row sums
python3 ../../tools/k54/replay_marginal_cuts.py                    # replay the 533 marginal cuts
python3 ../../tools/k54/kcheck_lrat.py OUTDIR NAME INSTANCE PROOF  # kernel-check a cut core via LRAT
```

`rowsum.py` and `rowsum_bb.py` were verified after extraction: both report **live-17 INFEASIBLE**
(HiGHS status 8; and 41 nodes / 21 infeasible leaves), matching the accepted result.

`ilp.py` and `witness.py` are the shared integer model and witness checker used by the two rowsum
scripts; they are not meant to be run directly.

`kcheck_lrat.py` still expects the Lean project layout it was written for (it emits a `Cert.lean`
that imports Mathlib's `lrat_proof`); the four published cut cores were already kernel-checked with
it and the transcripts are recorded in `results/K54_REPORT_FOR_LLM.md` §20.
