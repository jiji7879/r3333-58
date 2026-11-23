# A 42-row sample of the wall, first-pass budget, 2026-11-23

Package: `dist/k58-solver.zip` (2026-11-23, sha256 `b09058a3…`), unpacked and
smoke-tested at `.scratch/pkgchk2/k58-solver`.

Command, run once per profile:

    ./k58.sh run --profile <P> --shards 7 --shard 0 --limit 6 --workers 3 \
        --out evidence-wall

for the seven small profiles `15,15,14,13`, `16,15,14,12`, `16,15,13,13`,
`15,14,14,14`, `16,16,14,11`, `16,16,13,12`, `16,14,14,13`.

**Result: 42 cases, all OPEN.** Six per profile, first-pass budgets (12 s /
400,000 conflicts), **284 solver CPU seconds** total, median 6.6 s per case,
**0 formulas retained** — no case closed, so nothing was certified.

That is the expected outcome and it agrees with every earlier measurement of this
layer: 0/98 closed at 12 s, 0/68 at 70 s, 0/51 at 60 s, 0/9 at 300 s in the
2026-11-22 record. The seven small profiles are the wall, and the first-pass
budget does not touch them.

Sizing for a full pass at this budget: 11,585 rows × 6.6 s ≈ **21 CPU-hours**,
which is affordable — but on this evidence it would produce 11,585 OPEN verdicts.
The wall profiles are worth running for *release coverage* (a complete ledger of
attempts at a stated budget), not in the expectation of closures.

Evidence: `.scratch/pkgchk2/k58-solver/evidence-wall/<xx>/<case-id>/first/*.jsonl`,
one line per case with the profile, branch, charge, budgets, CPU seconds and status.
