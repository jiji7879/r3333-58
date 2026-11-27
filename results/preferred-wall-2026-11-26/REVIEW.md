# Representative-pair cover: is it useful?

Audit completed 2026-11-27 UTC. Repository base: `8e5a10eb58de4c4b50b128eadc9a36c4b105ee4f`.

## Decision

**Yes, narrowly: this is a useful exact local preprocessor and unrestricted-row-root decision cover. It is not a mathematical wall reduction or a demonstrated general SAT improvement.**

The supplied local artifacts support a verified cover of **3,604,436 preferred ten-spoke jobs** across the same 11,585 rows, versus 60,817,332 previously labeled cells. That is 94.0733408% fewer scheduled representative cells. It does **not** close any of those 11,585 rows.

Most importantly for utility, the existing data and one new bounded batch give no evidence for scaling a general preferred-job solver campaign. The supplied D wave is 10,000/10,000 OPEN at 128 conflicts; my matching next wave is 10,000/10,000 OPEN at 512 conflicts. **I stopped rather than increasing the cap again.**

## Certified scope

Four independent directions and coordinator replays established the following, with strict `drat-trim -i` checking and no warning suppression.

1. **Local sorted and preferred tables are complete in their stated encodings.**
   All **608** local RUP proofs replayed independently. I also supplied a malformed-prefix control which passes this checker with `-w` but fails with strict `-i`, explaining why the shipped helper's warning suppression was removed in our test copy.

2. **All 3,330 complete-arm witnesses validate.**
   Triangles, fixed pentagons, sorted outside words and declared first-two words all check. All **2,841** preferred catalog pairs have satisfying ownership witnesses.

3. **The preferred existence cover is complete locally.**
   One proof for every arm size and possible second sorted word shows that no sorted arm can avoid every preferred pair. This is an existence proof, not a trust assumption on the greedy catalog-generation search.

4. **The physical relabeling premises hold on all 11,585 rows.**
   Each outside vertex has only the positive root-color and negative marked-color signed stars prescribed. The nominated root arm is unnamed, size 11--14 and distinct from the marked arm. Cardinality/support predicates do not distinguish individual anonymous vertices. All 115,850 nominated pentagon edges match the local convention.

5. **The preferred ownership CNF has the intended semantics.**
   Independent semantic evaluation of the physical extension and owner gates succeeded on every supplied complete-arm coloring. The actual one-adjacent-pair sorting comparator was exhaustively tested over all **59,049** arbitrary word pairs and all 16 auxiliary assignments; it accepts exactly **29,646** nondecreasing pairs with zero mismatches.

6. **The physical full-parent injections supplied for sorting replay.**
   All **42** physical lifted RUP proofs passed after removing `-w`, against exact first-tier parents, cubes and sorting guards. These are 42 examples, not a per-job proof archive for millions of preferred jobs.

7. **Artifacts and counts reproduce.**
   ZIP integrity and all **2,124** listed SHA-256 entries passed. All 40,000 samples and 751 block receipts join to the roster and probe metadata. The weighted arm-size counts sum to 60,817,332 raw cells and 3,604,436 preferred jobs; contiguous job bounds cover all 11,585 rows exactly.

8. **Original parents and export/group semantics match the checked encoder.**
   All ten frozen encoder files and roster bytes are identical to tracked WallCC. Six independently regenerated FIRST parents plus all 512 cold parent/query hashes match. The grouped sender guard has the original guarded cardinality semantics, including the automatic-bypass boundary; no soundness defect was found. The continuation queue's full **3,594,436** positions are a bijection of the unused preferred jobs, with the original D set as its exact complement. Direct truth assignments validate every preferred extension and owner clause for all 3,330 local colorings.

## Exact mathematical boundary

Every sorted full arm has a preferred pair somewhere in its outside-word multiset. Choose the least such pair, rename an implementing vertex pair to the nominated positions (with unequal words ordered), and sort the remaining outside vertices by word. Outside permutations preserve first-tier parent satisfiability, including extension of the support/cardinality auxiliaries checked in the generator. Consequently:

> Strict refutations of every preferred class for a given row imply UNSAT of its unrestricted first-tier parent. A strict refutation of any one preferred query proves only that representative class, not the whole row.

This is a genuinely useful theorem, but three distinctions matter.

- **Uniqueness is per full coloring label, not per old raw cell.** The raw ten pins leave all other outside words free. A local n=11 witness explicitly gives raw pair `(00000,02100)` two different valid preferred labels, `(00000,02001)` and `(00000,02100)`. More generally, the witness audit found 15,251 raw keys with multiple preferred labels; that is a diagnostic on supplied witnesses, not a new census.
- **The cover is at unrestricted roots.** Under an arbitrary pre-existing cube, the selected permutation may not preserve that cube. Do not apply the preferred convention mechanically to every node of the older binary frontier.
- **Different conventions produce different restricted formulas.** A preferred job has owner and tail-sort constraints. Its result cannot be substituted for the corresponding raw cell's result without this semantic argument.

The degree screen's color-0 capacity 5 is conservative rather than tight (4 would be tighter in the full signature); this does not affect the proved cover.

## What the solver measurements actually show

### Supplied waves A--D

Across all four waves there are **zero whole-row closures** and all 11,585 rows remain OPEN. Partial-graph SAT witnesses are not unrestricted row certificates.

| Wave | Relevant outcome | Work meaning |
|---|---|---|
| A/B, 20,000 | raw: all OPEN | 2,576,473 recorded conflicts at cap 128 |
| C raw, 10,000 | raw: all OPEN | 1,288,377 conflicts, 128 cap |
| C sorted, 10,000 | 2,418 `UNSAT_SORTED_ARM`, 7,582 OPEN | 1,011,952 conflicts, 128 cap |
| D preferred, 10,000 | all OPEN | 1,289,283 conflicts, 128 cap |

The C breakdown is decisive:

- **3,359 exact local exclusions = 2,418 sorted UNSAT outcomes + 941 cap-OPEN outcomes.** These figures are not additive.
- On the **6,641 locally realizable cases**, raw and sorted produced zero UNSAT and used **855,611 versus 856,193 conflicts** respectively. Sorted used 582 more (about 0.068%).
- The sorted table was consulted only after `solve_limited()` returned false, not as a prefilter. Thus even these runs spent 155,759 sorted conflicts on the 3,359 already-excluded classes.
- Workers, grouping and shared learning histories differ. C's block seconds sum to 105.8953 raw versus 281.4424 sorted. This is not a controlled causal runtime comparison.

### New bounded E wave

After verifying the cover and exact export identities, I ran the deterministic next disjoint batch:

```sh
.venv/bin/python campaign_queue.py next --start 0 --count 10000 --run --cap 512 --jobs 2
```

The shipped full-parent fallback had a hidden 1,000,000-conflict cap. I explicitly capped it at 512 as well, removed `-w`, and added separate native attempt/proof receipts. A small contradictory-unit control exercised that capped proof path and replayed successfully.

Results:

- **10,000/10,000 OPEN**, with **5,129,608 group conflicts** and a 512 cap per group call.
- **Zero full-parent fallback calls**, zero full-row models, and zero refutations.
- **271 block receipts**; all seven wall profiles are represented, and all remain OPEN.
- Reported coordinator wall time: **147.655 seconds** with two workers.

An independent auditor (`tools/preferred_wall/audit_next.py`) rebuilt every source ranking, group hash and physical/ownership assumption for all 10,000 records and confirmed the same result. No per-job proof claim was manufactured. This is an OPEN stop, not evidence that the jobs are unsatisfiable or that representative labels make them harder.

## Recommendation

Use the exact local tables **before spending conflicts**: discard ORDER/COLUMN/local-arm contradictions immediately and avoid rerunning old labels under another naming convention. The preferred catalogue also provides an exact root-level job decision cover: a complete mathematical proof follows if every one of its constituent class refutations is verified.

Do **not** launch another broad batch based on the current evidence. The compact queue is worth using if the wall is attacked anyway, but these data do not show improved solving of locally realizable or preferred jobs. A subsequent performance experiment must use the **same locally realizable identities** and the **same solver setup**, with raw, sorted and preferred variants independently proof-checked, rather than comparing different samples or worker/group histories.

No broad matched performance experiment is claimed here. The new E wave was a single bounded availability test, not a speed benchmark, and it closed neither a representative class nor a whole row. The Ramsey bound is unchanged.

## Evidence map

- `strict-verify.log`: one-worker bundle verifier after removing warning suppression.
- `trial-audit.json`: direct full-TSV census and stage/status arithmetic.
- `representative-export-audit.json`: raw/sorted/preferred query identities for the second D example, matching the original parent in the previous campaign.
- `next512-summary.json`, `next512-run.log`, `next512-audit.json`: completed capped batch and independent audit.
- `certify-control.json`: small strict proof-path control.
- `tools/preferred_wall/bounded-cheap.patch`: explicit fallback cap and independent attempt receipts.
- `tools/preferred_wall/strict-*.patch`: strict DRAT checker changes used in the extracted verification copy.
- `review/preferred-cover/`: scope and reproduction notes, plus the independent
  `mathematics.md`, `artifacts.md`, `trials.md`, `original-export.md` reports
  and their executable audit sources.
