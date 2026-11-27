# Preferred-pair cover review and audit context

The final assessment is in
[results/preferred-wall-2026-11-26/REVIEW.md](../../results/preferred-wall-2026-11-26/REVIEW.md).

Only the mathematical/usefulness scope is recorded here; no solver speedup is
claimed.

## What is established

- 304 complete sorted-arm RUP certificates and 304 preferred-pair existence
  certificates: **608/608 strict replays**.
- 3,330 complete local arm models checked directly, and 2,841 preferred catalog
  jobs have checked ownership witnesses.
- Exact signed-unit, anonymous-arm, cardinality and support conditions on all
  11,585 physical rows.
- A root decision-cover argument: strict refutations of all preferred classes
  for a row imply UNSAT of the unrestricted parent.
- Important limits: raw cells do not have unique canonical labels, preferred
  queries are not raw queries, and arbitrary under-cube permutation transport
  is not justified.
- All 42 supplied physical sorted-guard lifts replay strictly.
- The supplied D wave has 10,000 OPEN at 128 conflicts; the next disjoint
  capped batch has 10,000 OPEN at 512 conflicts. No whole-row closure.

## Independent directions

Ultramath `smwy7kg2n` used four accepted directions and coordinator replays:

1. **Mathematical/symmetry cover** — root premises, semantics, witness and comparator
   checks, and a counterexample to bijective raw-to-preferred labeling.
2. **Artifact/proof completeness** — independent reconstruction of all 608 local
   CNFs and proofs, plus complete model/ownership/roster checks.
3. **Data/usefulness** — all 40,000 trials, all 751 receipt blocks, exact sampling
   frames, conflicts and non-comparability of the timing results.
4. **Original-parent/export/group encoding** — original query identities, queue
   permutation, physical owner semantics and guarded precomputation.

The four accepted reports are [mathematics.md](mathematics.md),
[artifacts.md](artifacts.md), [trials.md](trials.md), and
[original-export.md](original-export.md). Their independent scripts and final
outputs are under [audits/](audits/).

The independently checked result is that the cover is useful as an exact local
preprocessor and root partition, not as evidence of easier full-row solving.
Coarse timing summaries do not form a matched A/B benchmark.

## Strict reproduction

Start from a fresh extraction of the supplied bundle. Its checker helpers use
`-w`; remove that flag before relying on proof results:

```sh
unzip -q attachments/let-s-try-and-rbdv/K58_wall_10k_batches.zip -d .scratch/preferred-cover
patch -d .scratch/preferred-cover/K58_wall_10k_batches -p1 \
  < tools/preferred_wall/strict-cover_proofs.patch
patch -d .scratch/preferred-cover/K58_wall_10k_batches -p1 \
  < tools/preferred_wall/strict-arm_pairs.patch
cd .scratch/preferred-cover/K58_wall_10k_batches
mkdir -p ../../tmp
sh setup.sh
TMPDIR="$PWD/../../tmp" .venv/bin/python verify.py --jobs 1
```

This runs finite witness checks and proof replay, not a new K58 search. A 42-proof
physical lift check and the exact original-parent hash comparison are also
recorded in the final report and `representative-export-audit.json`.

The final handover ZIP includes the independent mathematical/data/proof sources
used in the review and all next-batch receipts. It is in `dist/`, never staged in
the repository.
