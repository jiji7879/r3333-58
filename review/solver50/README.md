# Accepted three-second review material

The main result and bundle description are
[THREE_SECOND_RESULTS.md](../../results/solver50-3s-2026-11-27/THREE_SECOND_RESULTS.md).

Four accepted independent directions checked this result:

- [cover.md](cover.md): 678 cover/edge checks, 885 labels and queue scope.
- [solver.md](solver.md): all nine original full-representative control proofs,
  strict wrong-prefix/wrong-query controls, solver/cache and timer boundaries.
- [data.md](data.md): all 150,000 representatives, block receipt consistency,
  sampled/timed outcomes and the fixed local-survivor candidate set.
- [two-arm.md](two-arm.md): target-row provenance: two exact representatives,
  unsupported quoted split counts, and the fully witnessed joint-support projection.

`artifacts/` preserves their final summary reports. `audit.py`, `audit.json` and
`candidates.tsv` preserve the experiment's frozen inputs. The candidate rows
are raw `(convention,row_id,w,z)` identifiers only; full CNF identities must be
regenerated before use.

The main distinction is that full DRAT closure of a locally excluded class is
not advancement beyond the local exclusion. Locally surviving jobs remained
OPEN here, so no speedup was demonstrated.
