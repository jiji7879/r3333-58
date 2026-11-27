# K58 adaptive-wall batch audit

Read `results/wall-983774-2026-11-27/REPORT.md` first. This directory contains only the coordinator's independent 16-case full-parent checker sampler; the complete exhaustive auditors live in swarm `smwyfnpf0` and in the handover archive.

## Independent stratified sample

Requirements: the supplied `K58_wall_campaign` bundle with its venv and compiled tools. The sample reconstructs four beginning/third/two-thirds/end receipts per affected profile, checks every full parent/query hash against its receipt, then replays using an independently built checker with `-i -U` and no warning suppression.

```sh
B=/absolute/path/to/K58_wall_campaign
CHECK=.scratch/wall983774/bin/drat-trim
mkdir -p "$(dirname "$CHECK")"
cc -std=c99 -D_GNU_SOURCE -O2 "$B/tools/drat-trim.c" -o "$CHECK"
"$B/.venv/bin/python" tools/wall983774/replay_closed_sample.py "$B" \
  --checker "$CHECK" --out .scratch/wall983774/sample16-new
```

The sampler substitutes only the producer's checker callback: it still uses the supplied physical map/formula constructors. This is an independent checker/build and fresh identity/replay check, not a separate proof of the entire encoder.

Measured result: all 16 across all four affected profiles, one malformed-proof rejection. Completion requires initialized bundle tools. The first attempt against an uninitialized source ZIP correctly stopped because `relabel` was not executable; it was not a certificate failure.

The complete 3,066-parent run and all positive-control backend replays are in the batch audit archive and member `m3`; the sampler does not substitute for them.

## Findings kept in the main report

- Historical OPEN execution cannot be established from statistics-only receipts.
- Official helper `rup()` uses `-w`; independent positive checks do not.
- An unrecognized cached status can be reused without proof/model and promoted to an answer. This was confirmed with synthetic negative input, not discovered as a forged normal campaign receipt.
- Local rules plus selected physical applications must not be reported as a full physical replay of all 983,774 current parents.
