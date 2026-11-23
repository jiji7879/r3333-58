# Judging m1 of `smwsyh6tk` (cross-arm layer, direction B — the rectangle layer)

Submitted 2026-11-23 ~10:15. Claim: the two-arm package's finite chain is re-derived and verified
without the missing proof archive, and a smaller irredundant certificate set is supplied.

This file records what the judge checked **independently**, with the command that produced it.
Provisional until the replay row below is filled.

## What the submission claims

192 theorem cases (3 type-36 placements × 4 colour orientations × 16 count-vector pairs) are
UNSAT with an irredundant set of **2,541 cores** (package: 4,869), every core certified three ways
(kissat+DRAT against a regenerated CNF, the package's own encoder, HiGHS for the tables), plus the
package's shipped data verified against the definitions.

## Checks made by the judge

| check | command | result |
|---|---|---|
| certificate structure | read `cert_irr.json` | 12 groups, 2,541 cores, sizes `{2:134, 3:892, 4:1271, 5:235, 6:9}` — matches the report exactly |
| `cert_min` vs `cert_irr` | set comparison | identical core sets; the files differ only in metadata |
| manifest size | read `manifest.json` | 2,740 = 2,541 cores + 192 tables + 7 missing-neighbour |
| the transportation layer works | `table_sat` with 0 / 186 cores | 0 of 16 decided with no cores, **16 of 16** with the full certificate (positive control) |
| two-entry layer is empty | `cores_pairs.json` replayed through `table_sat` | **453** two-entry cores, 0 singles, **0 of 16 decided in every one of the 12 groups** |
| irredundancy | drop one core at a time, 6 sampled cores in each of groups `0-0`, `1-2`, `2-3` | every sampled core essential, 18 of 18; full set decides 16/16 in each |
| cores are UNSAT, non-cores SAT (both encoders) | judge's own probe, kissat on written DIMACS | 3 declared cores UNSAT in m1's encoder **and** the package's; 3 single entries SAT; 4 pairs outside the census SAT — `PROBE PASS` |
| the MILP check is not vacuous | same formulation, cores removed | full 186 cores → HiGHS status 2 (infeasible); **no cores → status 0 (feasible)**; only 2-entry cores → status 0 |
| shipped-data arithmetic | read `.scratch/tac/cases.json` | 18 groups × 16 results = 288; **12 theorem groups are 16 UNSAT / 0 SAT each = 192**; controls 16 UNSAT + 32 UNSAT + 48 SAT = 240/48 overall; control cores 272+0+297+267+272+296 = **1,404**, theorem 4,869, total **6,273** |

Two things the judge checked because they *looked* wrong and were not:

- 32 SAT results appear inside the "theorem groups" if the group filter matches `105` anywhere in
  the tag. The tags `p105-105-*` and `p105-338-*` are the (36,36) and (36,77) control families, not
  theorem groups. On the correct split the 12 theorem groups are 16 UNSAT / 0 SAT each.
- the judge's first probe drew "non-cores" from entries occurring in some core, so UNSAT was the
  expected answer there; the probe was redesigned to use the single-entry and census-complete
  two-entry layers, where SAT is the prediction. The submission was not at fault.

## The decisive check: replay of all 2,733 proofs

m1's own `replay.py` skips any tag already present in `manifest.json`, so a naive re-run verifies
nothing. The judge rebuilt the archive from `cert_min.json` and `cert.json` alone in a fresh
directory, with a parallel driver (`parareplay.py`) that regenerates each CNF, runs kissat, checks
the proof with `drat-trim`, and requires the regenerated CNF **and proof** SHA-256 to equal the
manifest's.

RESULT: **2,733 of 2,733 OK, 0 mismatches.** Every CNF regenerated, every proof accepted by
`drat-trim`, and both the CNF and the proof SHA-256 equal to the manifest's. The archive is
bit-reproducible from `cert_min.json` and `cert.json` alone, in about 10 minutes on four cores.

The submission is accepted. Not verified by the judge, and therefore not counted: `hashcheck.py`
(all 6,520 package CNFs regenerate from the package's encoder) — started, killed for time; and
`verify_package.py` (the 6,273 shipped cores, 240 shipped results, 48 local models) — never run.
Those remain the submission's own claims.

## m3, the same swarm, direction C

m3 submitted a pair census plus an independent re-decision of all 288 shipped cases. Judged
**rejected on evidence, not on mathematics**:

- reproduced: `census.py` prints `labelled placements 4236 in 219 types / type16 21 type36 3`,
  agreeing with m1's enumerator and with the package's own `catalogue.py` — three implementations;
- reproduced: copying m3's scripts to a scratch directory and running `mono_all.py 0` gives
  **16 of 16 CNF SHA-256 identical** to its ledger and 16 of 16 verdicts, all UNSAT with
  `drat_ok`;
- not accepted: the headline "288 of 288, every one DRAT-verified". The member disclosed that
  `.scratch/smwsyh6tk/` was deleted mid-run by something outside its control, leaving only records
  0 and 1 live. A disclosed deletion is honest but it is not evidence, and this campaign has
  already recorded five claims that turned out to have nothing behind them. The member was sent
  back to re-run `mono_all.py` over all 18 records and ship the ledger; the census, cost table and
  probes were explicitly excluded from the redo.

### m3 after the rejection: the ledger is now complete

m3 re-ran the whole sweep. `ledger.jsonl` (111,942 bytes) now holds **288 records covering all 18
cases**: 240 UNSAT each with `drat_ok` and a CNF SHA-256, 48 SAT each with `witness_ok`, **288 of
288 agreeing with the package's verdicts, 0 disagreements**. `REPORT.md` was updated in the same
pass.

The judge re-ran two whole records through m3's own pipeline in a scratch copy — record 0 and
record 12 — and got **16 of 16 CNF SHA-256, verdicts, `drat_ok` and `witness_ok` identical to the
shipped ledger in both**. The ledger is reproducible, not merely written.

Two of m3's structural findings corroborate m1 independently: exactly 4 of the 36 cells carry no
rectangle, and the entry and two-cell layers decide nothing, so the content is in joint refutations
of three or more cells.

One claim the judge could not confirm, and did not credit: m3 explains the four dead cells as "the
ones whose two sites both have 4 vertices". The cells are indexed by classes of size 2 and 3, and m1
describes the same four cells differently, as two size-4 rows against named columns depending on
the placement. Only the count (32 of 36) was checked. m3 was asked to restate the explanation from
its own data or drop it.

