# Where the K58 campaign can go from here

State on 2026-11-16: pipeline reproduced, 81 cases certified and pushed,
audit of the reduction in progress. The frozen ledger is 111,035 OPEN. Below,
each option with its measured cost and the exact command.

The bundle lives outside this repository (it is the author's handoff). Paths
below assume it is unpacked at `$K58`, with `$KISSAT` and `$DRAT` built from
the pinned commits and a venv holding python-sat 1.9.dev22.

## Option A — close a large share of one big profile (~10 h, ~14 GB)

`(16,15,15,11)` has 16,090 OPEN cases and closed 47/48 in the first batch.
A full pass at the first-pass budget should close ~13,000 of them.

```sh
python3 "$K58/run_cover.py" --publication --tier first \
  --kissat "$KISSAT" --checker "$DRAT" --output work/evidence \
  --workers 4 --seconds 12 --conflicts 400000 --profile 16,15,15,11
python3 "$K58/summarize_queue.py" work/evidence
python3 "$K58/cover_evidence.py" --root work/evidence manifest work/release
```

Do it in shards (`--shards 4 --shard i`) if the run has to be interruptible
across sessions; the evidence root is shared and locked per case, so a plain
rerun resumes. Budget 1.03 MB of certificate per closure, and check the
retained total against `df` every few thousand cases.

## Option B — the small profiles are the wall (unknown cost)

11,585 OPEN cases in the seven profiles below `(16,15,15,11)` closed **0 of
98** at 12 s and **0 of 306** in the pilot. Nothing is known about their
closure rate at the retry budget except for `(15,15,15,12)`, where 8/10
closed. Before committing to them, measure:

```sh
python3 "$K58/run_cover.py" --publication --tier retry \
  --kissat "$KISSAT" --checker "$DRAT" --output work/evidence \
  --workers 2 --retry-seconds 70 --retry-conflicts 2400000 \
  --profile 15,15,14,13 --limit 40
```

If that closes under ~20%, the campaign's cost is dominated by ~11,000 cases
of unknown difficulty and the handoff's projection is not usable.

## Option C — the actual bottleneck: a Lean bridge for n = 58

The pinned repository has `UniformK60` and `UniformK61`, one development per
order, and nothing for n = 58. This is the step that turns a finished
computational cover into a theorem, and it is months of work at the K60 scale.
It is also the step where the n = 58 cover's *completeness* argument has to be
written down and checked, which is exactly what the current audit is probing
without a formal language.

If the aim is a publishable `R(3,3,3,3) <= 58`, start here, not with more
Kissat runs: a completed cover with no bridge is not a result, and the bridge
will dictate which parts of the cover are even in the right shape.

## What would falsify the current plan

* A genuine K_58 colouring that the cover does not reach — i.e. a root with
  `H >= w` whose (profile, kinds, arm, mark, template, embedding) tuple is not
  one of the 113,179. This is the completeness question; the audit's d1/d3/d7
  directions are on it.
* An added clause family not implied by the root hypothesis, which would make
  cases UNSAT for the wrong reason (d5/d7).
* A case whose UNSAT depends on `support_tables` excluding a realizable
  support. m4's audit argues the 4-point exclusion is harmless because a
  sender's 4-class is always P4; that argument is conditional on the U/T
  classification, which m4 re-derived independently.

## Resume notes

* The evidence root is keyed by content hash; a rerun skips verified cases and
  reuses OPEN receipts. Never edit a `verified.json` or a certificate.
* `cover_evidence.py verify` pins the python-sat version string. A different
  version fails before it checks anything; use the venv.
* `drat-trim` needs `gcc -std=c99 -D_GNU_SOURCE -O2` to build; the Makefile
  does not.
