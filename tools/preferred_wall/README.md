# Preferred-cover audit tools

- `strict-cover_proofs.patch` and `strict-arm_pairs.patch` remove `drat-trim -w`
  from the extracted proof-checking helpers. In this checker version `-w` can
  also bypass the malformed-binary-prefix break, so these are correctness
  changes, not logging preferences.
- `bounded-cheap.patch` makes the native full-parent fallback use the probe's
  actual cap, replays it strictly, and records each fallback's query, native
  conflicts, result and proof digest. The stock fallback default is a much
  larger hidden allowance and must not be mistaken for the group cap.
- `audit_next.py` independently reconstructs the first 10,000 next preferred
  jobs, their K58 row groups and physical ownership assumptions. It strictly
  replays any reported full preferred-query refutation and checks total models.
  Open/pending/model statuses never promote an original row to UNSAT.

The completed next-batch command and source audit are described in
`../../results/preferred-wall-2026-11-26/REVIEW.md`.

## Audit this exact next batch

```sh
C=/absolute/path/to/bounded-next/K58_wall_10k_batches
"$C/.venv/bin/python" tools/preferred_wall/audit_next.py "$C" \
  --out .scratch/preferred-next-audit.json
```

The audit assumes the same first 10,000-next-job source and cap-512 result names
(`next-0-10000.tsv.gz` and `next-0-10000-cap512.{tsv.gz,json}`). It does not
launch a SAT search. Proof checking can use the strict helper in the extracted
package. All OPEN and PENDING_BASE outcomes remain unresolved.

## Do not infer a speedup

The local 608 certificates and their physical semantics justify preprocessing
and a root decision cover only. A preferred job's result cannot be substituted
for a differently labeled raw cell, and arbitrary under-cube transport needs its
own invariance argument. Current preferred measurements are all OPEN, including
the new capped 10,000-job wave, so no further batch is justified on solver-speed
grounds.
