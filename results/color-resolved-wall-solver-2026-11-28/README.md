# Color-resolved wall solver attempt

## Outcome

A working clone of `wallcc` with the audited color-resolved pivot clauses is
installed at [`tools/color-resolved-wallcc`](../../tools/color-resolved-wallcc/COLOR.md).
The underlying fork was initially committed as `f083279`. All four implementation,
proof-safety, real-wall and supplied-engine directions were independently accepted.

**No full ordinary-wall row was closed.** The useful established effect is local
pruning with actual DRAT replay, not a completed wall search or a Ramsey-bound
claim.

## What was tested

| Group | What ran | Outcome |
|---|---|---|
| Clone implementation | `wallcc`, `color_pivot.py`, `color-export`, frozen `--pivot-color` workflow | Working; original and augmented parent/receipt scopes explicitly separate |
| Regression and semantic tests | K5/K6, four exact variants on six benchmark rows, counter assignments and 2,914 local words | PASS, including native miters and damaged-proof rejection |
| Real-wall controlled panel | Deterministic gap-up/gap-down, unique-minimum and missing-pivot rows | All full rows OPEN; 6/6 paired 1M runs OPEN; 24 terminal local/coverage proofs replayed |
| Engine comparison | Native CaDiCaL 2.1.2, stock/reducer CaDiCaL 1.9.5 and Kissat 4.0.4 on exact original/color row 0 and gap2 | 16 trials at 200k and 8 at 2M were all OPEN |
| Coordinator pivot and threshold splits | three physical color cubes, exact-minimum and above-minimum variants | All six runs at 200k stayed OPEN; a direct exact-minimum CaDiCaL 2.1.2 run stayed OPEN |
| Engine setup controls | SAT/UNSAT inputs on copied CaDiCaL 2.1.2 and Kissat 4.0.4 | Direct checked SAT models and deletion-free, warnings-fatal RUP verification passed |

The ordinary fork's K5/K6/regression selftest and color selftest were rerun after
installation. The engine asset matches the already audited binary. The copied
proof normalizer does not copy or hide a malformed proof: it drops only deletion
commands, then requires warning-fatal RUP checking.

## Measured pruning versus wall hardness

The strongest local result is not just a timing percentage. Nine predetermined
local pairs produced independently verified child refutations. `escape`
required 2--11 conflicts per cube, **41 in total**; every color child was already
UNSAT by unit propagation. A separate fresh row-0 cube `[511,-18464]` (pivot 2
plus fewer than the minimum three escapes) took **6 conflicts with escape and 0
with color**, again independently replayed. Its color proof correctly fails on
the escape sibling formula.

All **18/18** of those local controls and **6/6** split-coverage queries passed
independent checking. Coverage queries prove that branches exhaust the pivot
model space, not that the parent is UNSAT. Parent bad paths and partial DRATs are
not terminal certificates.

The complete runs tell a different story: 16 full variants at 100k, 36 ordinary
threshold leaves at 40k, six baseline/color pairs at 1M, and all four engines on
both variants of gap2 at 2M remain **OPEN**. The controlled 1M pairs spent
305.676073 CPU-s. The matched engine panel spent 1100.237231 CPU-s and generated
no completed wall proof.

On the descriptive 1M escape-versus-color pairs, three rows had CPU ratios
0.81194, 0.83585 and 0.96364. On the 2M gap2 panel, the original+color CPU totals
were 227.892 (CaDiCaL 2.1.2), 313.430 (stock 1.9.5), 280.449 (Glucose policy)
and 166.380 (Kissat 4.0.4). These effects are input-specific and capped; they
are not closure rates, universal speedups or guarantees that a larger cap will
pay off.

## How to use the current solver

Read [COLOR.md](../../tools/color-resolved-wallcc/COLOR.md) for exact commands:

```sh
.scratch/k58/.venv/bin/python tools/color-resolved-wallcc/wallcc.py \
  color-export --row 00032f347903 --out .scratch/row0-export \
  --checker "$PWD/tools/color-resolved-wallcc/bin/drat-trim"
```

The augmented color parent contains the original parent plus 270 counter
definitions, 15 positive escape clauses and 21 guarded pivot rules, with fresh
auxiliary IDs 18388--18477. Its SHA-256 is
`66cde0ddb0556a76a73244981976aff09d9928788a9dbf59f1a56779049efa50`.
The ordinary parent and off path remain unchanged.

The direct native backends available are the audited CaDiCaL 2.1.2 in
`bin/cadical-2.1.2` and Kissat 4.0.4. Use CaDiCaL for the certifying lead and
Kissat as a cross-check, not `--reduceglucose` as a default. This is a provenance
and operational choice, not a declaration that the fastest timing sample is a
stable engine ranking.

Any completed wall-style result requires a complete, independently replayed
leaf/cover proof. For an augmented parent, the explicit scope is the auxiliary
counter-extended parent together with the native original-plus-counter
derivation; a monolithic proof against the original-only formula is not silently
substituted.

## Evidence files

- `implementation-summary.json`: actual installed candidate and regression
  receipts.
- `controlled-summary.json`: real-wall controlled experiment totals and
  selection.
- `engine-summary.json`: exact per-engine and cap results.
- `coordinator-three-color-probe.json`: three 40k ordinary-color leaves.
- `coordinator-minimum-probe.json`: exact-minimum/above-minimum results at 200k.
- `native-engine-controls.json`: independent SAT model and warnings-fatal RUP
  controls after deletion normalization.

Additional complete calculations, sources and native receipts are under
`.ultramath/smwzopt3q/{m1,m2,m3,m4}` and `.scratch/wall-color-eval/`. The large
CNFs and raw partial proof streams are deliberately not copied into the Git
repository.

## Next useful gate

The evidence supports trying a structured pivot/threshold cube-and-conquer
branch with the native lead engine, not declaring the wall solved or spending
unbounded effort on an isolated easy child. A defensible next gate is an
exhaustive pivot-color/minimum split with every terminal leaf checked and the
composed parent proof replayed. If that does not close, the result is still
OPEN; it is not a proof of impossibility and not a reason to relax proof checks.
