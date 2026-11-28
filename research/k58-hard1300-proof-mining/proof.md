**Status: PROVED, for the bounded two-case execution and finite core analysis. The ledger gate accepts #4 with `self` and `compute` checks. Two hard1300 cases were freshly refuted and independently replayed; no new general reusable physical lemma is asserted. The earlier historical-example and H=8 selections do not answer this task.**

# Fresh K58 hard1300 refutations and the core-mining boundary

The correct cohort is the one identified explicitly by the user: slow, historically UNSAT full-root cases, locally listed as the 1,300 rows in [hard1300.tsv](../../results/hard-tail-2026-11-27/hard1300.tsv). These are not the ordinary wall rows, and the bounded two-case panel does not close an entire profile or cohort.

No Ultramath was used, following the explicit user instruction. Native CaDiCaL 2.1.2 and `drat-trim` provide the proof checks; no SAT model is inferred from a timeout or solver-cap outcome.

# Clean claim: two checked hard1300 case refutations, with a bounded mining obstruction

## Scope and exact inputs

The target cohort is the locally defined `hard1300.tsv` population of **full-root retry-tier K58 cases already proved UNSAT but slow for the solver**. These are not the ordinary wall rows. The bounded selections are:

| rank | case | input SHA-256 | historical role |
|---|---|---|---|
| 1297 | `29fa65a26d50c595ef314f1ba16884756ced217aa9a70c74a7e8ad14653f1e4e` | `d75196e6a5445f2035b84777720e99a0c10482fe591f4bb17139b12f744c61a6` | bounded fresh source/core comparison |
| 1300 | `e52b5bdaef139b32a0778abac2b39470076bd55b225de3840bafc83e9110556b` | `56ad3dc529f1b855e65fa3f3f5363e8275930a7cb6ea5b04dc01a112535b0837` | bounded independent comparison |

Both parents have profile `(15,15,15,12)`, `TTT-`, marked size 15, charge 11, the recipe `tables=true,total_critical=true,full_root=true`, 29,942 variables and 211,564 clauses. Both were regenerated from the frozen ledger and hash-checked against `hard1300.tsv`. Rank 1300's bytes also equal the previously independent checked parent at `.scratch/k58-candidate-verification/proof/rank1300/rank1300.cnf`. No production ledger was modified.

## Case results

Each case received a fresh, bounded native CaDiCaL 2.1.2 default process from the K58 solver frontend (seed 0, 2,600,000 conflicts and 360 solver seconds). The actual results were:

| rank | conflicts used | solver CPU-s | whole-parent DRAT bytes / SHA-256 | fresh validation |
|---|---:|---:|---|---|
| 1297 | 771,786 | 36.94 | 39,514,788 / `f17ffa5093858f59ffa56b2d43ca9e082bfe106c50a07cde95e5896af4ca78b4` | `VERIFIED_UNSAT`, followed by successful compact proof export |
| 1300 | 875,852 | 42.46 | 45,245,027 / `676d59d759fb7d1cb63c881c561e0bcc87590565d4d8373b03f07d2ec1020043` | same |

Each returned solver exit 20, native raw proof `s VERIFIED`, frontend `VERIFIED_UNSAT`, and a compact whole-parent DRAT that also replayed. Raw warnings were never hidden using `-w`. These are two genuine fresh refutations of exact, certified full-root K58 case parents, not merely replayed historical assertions. Their local runtimes are observations under this engine, not a new difficulty, speedup or wall difficulty theorem. Rank 1297's raw native proof was 78,825,635 bytes and rank 1300's was 90,382,454 bytes; each differs from its independently compacted proof and from the historical cohort evidence.

No ordinary wall row, profile, the 1,300-case cohort, the Ramsey bound, or the physical semantics of the full root is claimed proved by these two CNF refutations.

## Independently checked cores

Raw warning-visible DRAT extraction read the complete 78,825,635/90,382,454-byte proofs and gave 5,219 and 5,250 clause cores. Text deletion normalisation then removed only `d … 0` records, retained every addition byte, accounted for all 99,634,032 and 121,695,451 input bytes, and required one terminal empty addition. Forced-ASCII `-I -W -U` replay of both reduced core/lemma pairs returned exit 0 and `s VERIFIED`, zero warnings/errors and zero RAT. The second-stage reduced cores retained 5,186 and 5,204 clauses respectively.

These stage-specific counts must not be conflated. Earlier standalone core-only attempts with different propagation/settings hit `s TIMEOUT`; that is a failed mining check, not SAT, UNSAT or an ordinary-wall result. The already verified case refutations stand independently of that mining timeout.

The two output streams have 519,764 and 585,676 nonempty additions. Their additions all use physical edge variables at most 6612. That does **not** eliminate auxiliary premises in the original full-root parents or parent cores. Width-finding and literal decoding therefore do not supply a free guard theorem.

For checked short physical additions (width at most four, omitting unwound empty clauses), the bounded inventory retains 13,608 rank-1297 additions and 11,778 rank-1300 additions not explicitly repeated in/subsumed by a parent under the implemented literal-set test. There are 2,346 exact shared non-subsumed short physical candidates between them. Earlier independent rank-1300 cores with 5,245 and 5,250 clauses share 5,094 clauses when each clause's literals are sorted. This compares valid solver-search-specific cores; it is not a claim that hard-case proof cores are unique.

## Bounded transfer checks and exact obstruction

Four diverse shared clauses were checked on each exact full-root parent using a separate query consisting of the parent and the negated cube, with no candidate assumed as an axiom. All eight forced-ASCII RUP checks returned `s VERIFIED`, no warnings, and no auxiliary literals in their native cores. Decoding the cores gives only elementary relations:

* `-3225 -3385` and `-3237 -3397`: the common fixed positive edge unit `3169` ($E(16,17,0)$), plus the corresponding monochromatic-triangle clause;
* `3849 3850 3852` and `5641 5642 5643`: a positive two-pin residual $\bigvee_{d\ne c}E(u,v,d)$, which is the previously established pinned palette/triangle family.

Thus these are true repeated instances, not a newly identified nontrivial reusable schema. A third-edge pin plus its triangle is an immediate property of the existing host encoding; the other two are already in the accepted bank. Neither is repackaged as a new guard, attachment, degree or critical-support theorem.

The complete collection of 2,346 exact shared short candidates was also screened with PySAT CaDiCaL's `conf_budget(0)` under each candidate's negated cube at each exact parent. Both ranks refuted 2,346/2,346, leaving no solver-cap-zero-unresolved shared candidate. A satisfiable-unit and a conflicting-unit control establish the solver interface's basic positive/negative behaviour. This is a **candidate filter**, not a new independent proof of 2,346 clauses, and no full-parent SAT model follows from a conflict cap, an unresolved result or a timeout.

The bounded generalisation obstruction is now specific: cheap common short clauses are either already accessible through elementary physical propagation or return the prior pinned residual family, while the genuinely hard-case refutations require hundreds of thousands of derived additions and tens of millions of resolution steps. Deriving a nontrivial reusable lemma needs a further mechanism with explicit role, guard and destination premises. None has been found or certified in this panel.

This is **not** an absence theorem for all clauses in rank 1297 or 1300, all 1,300 hard cases, other physical placements or the ordinary wall rows. It is an honest bounded negative mining result: no new general reusable physical clause is asserted from these two case-local proofs, but both fresh hard-cohort refutations themselves are established.

# Reproduction and retained evidence

The report gate is [gate.txt](gate.txt), and the clean proof and checks are in `checks/`. The machine-indexed execution receipts are [work/native-receipts.json](work/native-receipts.json). Core comparisons and bounded candidate evidence are [work/core-comparison.json](work/core-comparison.json), [work/common-probe.json](work/common-probe.json), [work/common-filter.json](work/common-filter.json), and [work/core-verification.json](work/core-verification.json).

Large native proofs and regenerated inputs remain in `.scratch/hard1300-proof-mining/`, not in Git. Their parent and proof hashes, sizes and warning-visible logs are bound in those compact receipts. To regenerate the exact parent identity from the authoritative unpack, run:

```sh
.scratch/massive-clean-install/k58-solver/.venv/bin/python \
  research/k58-hard1300-proof-mining/work/prepare.py
```

No archive was committed, no production ledger or queue was changed, and other sessions' untracked/modified files were not included in this work. A nontrivial reusable clause for another parent, explicit guard/role premises included, remains future work.
