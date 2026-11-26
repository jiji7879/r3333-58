# Four-row unsplit A/B/C ablation

Date: 2026-11-26.

## Bottom line

**All 12 independently verified cases remain OPEN.** No parent closed, no
satisfying full-parent assignment was found, and there is no measured basis for
claiming that pair or third-word rules improve search. Validity of a reusable
conditional refutation is not the same thing as a faster solver.

This was a deliberately small ablation of **four third-active parents**, with
one worker and **40,000 conflicts per variant**, not a campaign-wide solution or
a 12-independent-row benchmark.

## What separated the variables

The script `tools/adaptive_wall/run_unsplit_ablation.py` composed and recorded
independent implementations, retaining native calls and observations:

| Variant | Same original FIRST parent? | Change introduced |
| --- | --- | --- |
| A | Yes | No additional clauses or splits; empty RUP prefix |
| B | Yes | Pentagon + generalized-spoke + pair batch; unsplit |
| C | Exactly B | Adds the validated third-word table; unsplit |

Both B and C used the checked `compile_cas`, `produce`, and `pair_clauses`
functions with the ordinary root pins. None imported the excluded
minimum-conditioned off-star table. There was no word cube and no binary split,
so the A/B comparison concerns the combined batch, while C/B isolates the third
increment only.

All four original rows resolve uniquely on the checked roster and are
third-active. B's extra effective clause count was 374/355/391/390 plus
1,001/1,001/1,001/1,172 pair clauses. C adds a further **12, 12, 12, and 24**
clauses respectively. The last value is 24 because that row has two size-14
pentagons; this is expected rather than duplicate materialization.

The reference constructor independently rebuilt all twelve exact parent/query
hashes before running. The wrapper and both audits verified those hashes again,
along with original tier (`FIRST`, not retry), no cube, cap, status-dependent
keys and all process settings.

## Measured work

- **480,007** actual recorded conflicts, all of them observed native solver
  work. No additional 160,000-conflict base fallback was invoked.
- All cap values were 40,000, not actual work targets. There were **5** small
  cap overshoots, with a maximum of **2** conflicts. These are retained, not
  normalized into a tie or treated as a split winner.
- Native first-solver-call seconds total: **19.164**.
- End-to-end native-call seconds total: **19.319029**.
- Independent receipt/model/proof audit time: **2.231559 seconds**.
- All 12 observations are present, with fresh per-case directories, native
  stdout, return codes, matching conflict lines and solver/checker hashes.
- A second constructor/receipt audit also passed independently.

All cases have `status == OPEN` with at least the declared cap. No `SAT_BASE`,
`UNSAT_BASE`, or `AUGMENTED_UNSAT_PENDING_BASE` receipt occurred. Consequently,
there was nothing to export or promote to original-parent closure.

Independent checks preserved the actual per-parent variable totals, rather than
assuming 19,425 or 6,612 variables. A future satisfying model would require a
separate full-model check on that exact parent; a local arm SAT witness would be
irrelevant here. Likewise, any future base proof must be replayed against the
plain original parent, not a strengthened query.

## The actual decision

The predeclared stopping rule applies: **STOP when all 12 valid receipts are
OPEN at cap.** Do not rank variants by overshoot and do not claim that deeper
search or larger batches help. This experiment gives no evidence that the new
rules either help or hurt the eventual wall.

It narrows the next useful investigation:

1. do not repeat this batch at a larger cap without a specific hypothesis;
2. separate individual rule families or placements before adding yet more
   clauses;
3. compare one unsplit rule batch at a time, with matched budgets and complete
   generation/proof timing;
4. test a matched split only if a reproducible unsplit benefit exists.

## Independent replay and audit controls

- `abc_audit.py self-test` passed stale-root, parent-tamper, retry, minimum,
  cube and third-difference controls with zero solver calls.
- The measurement validator's positive synthetic receipt fixtures, native
  stdout-tamper control and total-model rejection tests passed.
- The independent DRAT replay gate passed its real positive control: the known
  conditional word **00210** (explicitly not this new A/B/C batch), with
  `proof_sha256` `944e7cc76ecab1287ac3c3157b770bf15986ee417e4781bbb63db9f1c4a8f13c`,
  and rejected the corresponding tampered proof. Empty/truncated/corrupt-proof
  controls were also rejected. Malformed-artifact checking should not use
  warning suppression merely to permit them.

The bare cached receipt path can still skip terminal-artifact validation on
resumption. Observation/freshness is necessary but not sufficient: final
terminal claims require actual artifact hash and independent replay. These are
enforced in this workflow.

## Files

- `unsplit-ablation-4x3-v2.json` — complete measurement/observation audit with
  exact parent/query hashes, native and observed work, launch sidecars and scope.
- `unsplit-ablation-4x3-constructor-audit.json` — the independent constructor's
  final receipt/schema audit.
- `unsplit-construction-plan.json` — immutable construction manifest including
  exact row, query, clause-delta and RUP-prefix hashes.
- `tools/adaptive_wall/run_unsplit_ablation.py` — observation-recording driver.

Raw scratch case folders are not committed. A small hand-over archive,
`dist/unsplit-ablation-v2.zip`, includes the native receipts and observations
without the large historical evidence stores. Its SHA-256 is recorded in
`dist/SHA256SUMS`.

The inherited 179+326 contact evidence is not reopened by this experiment;
neither are any cohort-wide H bounds altered. All original wall parents remain
OPEN and this is not a Ramsey-number result.
