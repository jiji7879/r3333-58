# Working notes

## 1. Baseline proof identity vs 5,245 vs 5,250

Initial inspection of `A0.json` found the exact coordinator-generated native CaDiCaL 2.1.2 baseline: parent SHA-256 `56ad3dc529f1b855e65fa3f3f5363e8275930a7cb6ea5b04dc01a112535b0837` and raw DRAT SHA-256 `9798683a7f8b3e5ee7c77b86c005bd64aa4357490be350bafd71ea0e76ee9e89`. The supplied `A0.core` has 5,250 clauses. The earlier coordinator original core from a rebuilt stock 1.9.5 DRAT with SHA-256 `91be7183…` had 5,245 clauses.

Rerunning `drat-trim` on the raw native 2.1.2 proof with `-i -U -t 600 -c` produced **5,250 clauses, byte-for-byte identical to the packaged A0 core**, hash `5f4d62aa81757098093d988c9914ae35642d7aa9f77df4c7fef49b41043cf8e0`. The checker C source hashes all match `d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee`. The discrepancy is the different proof stream, not a checker bug or random nondeterminism. The full `recheck.py A0` independent LRAT replay then returned `A0 VERIFIED against 56ad…0837`.

## 2. Local 2-SAT/spoke checks already rerun

The supplied exhaustive small analysis was rerun: two-colour complete graphs through $K_5$, 600 varying-list cases, all deletions of the two-odd-cycle obstruction, and its explicit triangle-free 4-colouring of $K_{10}$. An additional 4,000 random list-constrained instances on up to ten sites and four colours were compared with independent brute-force assignment enumeration: 3,293 satisfiable and 707 unsatisfiable, with no mismatches.

`verify.py` rebuilt and warning-fatally checked both RUP steps of each of the four ordinary-wall five-literal clauses against the exact original parent, included fixed palette exclusions, and passed all four. Their local satisfiability or OPEN performance status is not altered by that semantic validity; all 16 supplied comparison runs at 40,000 conflicts remain OPEN.

## 3. Native original-parent checks already completed

With independently compiled `drat-trim`, the C `lrat-check`, and the binary-to-text converter:

* `recheck.py A0`: PASS against the unrestricted original parent.
* `recheck.py P13000`: PASS against the unrestricted original parent, after putting the supplied optional proof stream beside the verifier as it requires. The earlier missing-path failure was not a failed proof or a package defect.
* `recheck.py D0`: PASS against the unrestricted original parent.
* `recheck.py squares`: PASS on all seven square-transfer clauses at ranks 1294–1300, including each checked derivation step.
* `drat-trim A.cnf 502176.rup -I -f -U`: the checker reports `s DERIVATION` and “all lemmas preserve satisfiability”; expected `rc=1` because the slice is a derived-clause proof, **not a refutation**. `-W` correctly rejects the expected “no empty clause” warning rather than enabling a false refutation claim.
* `drat-trim A.cnf 577233.rup -I -f -U`: the same explicit derivation result, with the same non-refutation status.

DIMACS identity checks show D is the unchanged baseline body plus exactly `4687 3590 4034 4673 0` and `-5160 3282 4822 0`; the D0 whole-parent proof therefore is not simply accepting those lines as assumptions. B/C have their documented one/two additional clauses and matching hashes.

## 4. Projection semantics

All seven projections (`P1294`–`P1300`) are strict ordered subsequences of their own original parents, with only the header's clause count changed, every variable on an edge within the selected vertices, and no auxiliary clause. Bound hashes and all 30,630/33,270-clause counts reproduce exactly. The two classified other arms and the marked sender's known support account for the 35 vertices on most projections, 36 on rank 1299.

On the supplied full-model logs, the rank-1298 model satisfies all 30,630 projected clauses and the rank-1299 model all 33,270. Evaluation with the exact sign per absolute variable ID shows the same models falsify 1,318 and 1,287 full-parent clauses, respectively. These are explicitly local models on selectable 35/36-vertex subgraphs, **not $K_{58}$ colourings**. An UNSAT projection implies unrestricted parent UNSAT via subset; a projection model says nothing about full admissibility.

`P13000` refutation has independently replayed on the true original parent. The other four projection refutations (ranks 1294–1297) were left to the independent projection-direction audit rather than claimed replayed locally.

## 5. Remaining review and overheads

A related independent swarm, `smwzmjadv`, covered local 2-SAT/spoke audits, projection refutations, all eight comparison LRAT streams, and mined-clause transfer semantics. This preliminary paragraph is superseded by the checked results below, which incorporate their verdicts, defects, replayed-stream scope and amortized solver-cost assessment. Do not describe all new files as before verification or as a general solver win merely because a receipt claims it. Proof generation/checking itself is expensive and must be included in any end-to-end claim.

## 6. Independent direction results so far

The ordinary-wall 2-SAT audit passed all eight native RUP obligations at four rows and 353,038 independent exhaustive implementation comparisons. The six $K_4$ obstructions are exactly square+complementary-matching patterns. That is a genuine generalization of the local square spoke obstruction, not of the separately guarded K15 theorem. All 16 supplied benchmark runs remain OPEN and stock/added CPU sums are 21.502271/25.948904 seconds, so adding those clauses is slower by 20.68%; no wall performance result follows.

The mined-transfer audit passed 148 retained logs, including 137 accepted native checks and 11 intended failures. Every supplied addition was individually checked as a RUP consequence on the current original parent. Fresh shorter original-parent prefixes were produced and verified. The only D mined clauses are $C_4$ and $C_3$, not the subsequent `-3900 3282 3598` square transfer. That subsequent transfer therefore cannot inherit D's search measurement. The clause-escape construction is specifically a four-colour rule, though the earlier arbitrary-colour square lemma needs no threshold.

The comparison-direction replay has now passed all eight streams by no-warning conversion to binary LRAT, a full independent structural scan for a terminal empty clause and no RAT hints, and the bundled independent C `lrat-check` on the unrestricted parent. Replaying the original A0 trimmed output again gives a different but valid 134,966,705-byte LRAT (`f88737…`) than the recorded 137,648,366-byte certificate (`c0ad3d…`). The fallback `recheck.py` does not compare that newly computed LRAT hash with `A0.cert.json`. This is an acceptable new trimmed refutation, not identical certificate provenance.

The same direction independently resolved the core histories: rebuilt native A0 is byte-identical to its 5,250-clause package core; A1 and the earlier 5,245 core have equal size only coincidentally. Earlier A0 and the new A0 share 4,359 clauses with the original literal ordering, or 5,094 after sorting each clause's literals. Different valid searches generate different valid backward cores.

One metadata-stage issue is retained: `summary.tsv` puts A0's 85.221-second native trim under `convert_to_lrat_wall_s`, `REPORT.md` describes it as native trim, and `A0.cert.json` records `conversion_wall_s: null`. These stages must not be summed as though their labels were uniform. Timing, discovery and checking are not a controlled cold pipeline amortization measurement anyway.

## 7. Accepted comparison-direction submission

Member m4's report was accepted after independently reading all nine compressed source streams, recomputing their byte hashes and checking all formula/query/certificate bindings. Every requested A1, B0, B1, C0, C1, D0, D1 and K0 source produces a full binary LRAT that independently checks against unrestricted A. The structural scan requires one terminal empty clause, no later addition, backward references and no RAT hint IDs; the bundled C `lrat-check` succeeds on each. The original A hashes match the cohort ledger, and B/C/D query prefixes differ only by their recorded added clauses. K is byte-identical to A0's 5,250-clause 2.1.2 core and is not a certifier of the older 5,245-clause 1.9.5 core.

The two core-overlap numbers are not a discrepancy: 4,359 is the exact literal-line intersection, whereas 5,094 is the intersection after sorting each clause's literals. The canonical core sets have 156 new-only and 151 old-only clauses. See `checks/remaining-recomputation.json`.

The accepted conversions had zero warnings and did not use `-w`; the separate `-W` runs all failed early with rc 80 and were not counted. The full raw A0 conversion retains 236 visible pseudo-unit-deletion warnings; its final independently checked LRAT carries no warning. A0's second conversion yields a valid but non-identical LRAT, and `recheck.py` omits comparing this fallback to the stored certificate. Those are provenance/stage caveats, not failed original-parent refutations.

D versus A over just two seeds of rank 1300 gives 1,680,786 versus 1,845,186 conflicts (−8.910%), 200.611902 versus 218.032950 proof-logging process CPU-s (−7.990%) and 167,306,123 versus 190,090,051 native proof bytes (−11.986%). Baseline solve+trim+selection is 196.492 mixed CPU/wall seconds, not a complete cold wall measurement, against 17.421 measured CPU-s saved on two D solves. Candidate extraction and full checking are not fully priced, so no amortized or cohort speedup follows. All 16 ordinary-wall bounded runs also remain OPEN; no wall result is inferred from them.

## 8. Coordinator rank-1297 projection-parent replay

The independent P12970 source transformation preserves the 41,393,868 addition bytes and discards only deletion commands, with one terminal empty addition. Its original-parent input SHA-256 is `d75196e6a5445f2035b84777720e99a0c10482fe591f4bb17139b12f744c61a6`. Running the previously compiled native checker with `-i -W -U -C -L` (no `-w`) read all additions and returned `s VERIFIED`, zero RAT lemmas. The 184,004,360-byte independently regenerated LRAT (`f816b6de…`) passed the separate C `lrat-check`, with zero warnings/errors in either stage. The retained receipt is `checks/P12970-parent-replay.json`; large replay files were deleted afterward.

## 9. Complete projection-native reconciliation

The five supplied original-parent projection proofs P12940, P12950, P12960, P12970 and P13000 now all have fresh native RUP and independent LRAT checks. The project coordinator separately verified rank 1297; the other parent receipts have complete source-byte normalization, warnings-fatal RUP gates and separate LRAT terminal checks. Their combined raw source size is 669,859,010 bytes. Reported user times of the native DRAT conversion/checking stage alone are 486.62, 314.22, 466.84, 139.388 (coordinator P12970) and 245.39 seconds. Those are audit costs, not previous search-completion times or a speed result.

The independent reconstruction establishes 35/36-vertex locally selectable subformulas without auxiliary projections. Rank 1298's model satisfies its projection but falsifies 1,318 unrestricted parent clauses, and rank 1299's model satisfies its projection but falsifies 1,287 parent clauses. These local models do not settle any parent. Five verified historical original-parent refutations yield no new wall closure or bound change. Exact per-proof hash/size/cost receipts are in `checks/projection-replay-reconciliation.json`.

## 10. Accepted final projection audit and metadata correction

The final projection submission originally labeled ranks 1294, 1295 and 1297 as `TTU-`. The coordinator rejected that version because `hard1300.tsv` and the reconstruction's `projection_audit.json` both show `TTT-` on those three rows; only 1298 is `TTU-` among the affected entries. The member corrected the profile table and checked all seven entries against both sources. No proof rerun was needed. The corrected report is now accepted, completing all four requested direction verdicts.

The normalized five-proof totals are 669,859,010 raw bytes completely parsed, 336,193,354 addition-only bytes accepted and 1,375,316,158 fresh binary LRAT bytes independently checked. The certificate-LRAT files themselves were not supplied; these are newly regenerated and checked LRAT identities, not purported reproductions of absent certificate bytes. Wrong-parent and missing-empty LRAT controls reject as required, and one exploratory malformed/timeout path is retained as unverified rather than counted positive.

Performance scope remains negative. On the directly comparable original A0 versus projection P13000 (seed 0, cap 2,000,000), the projection has 1,449,682 versus 875,852 conflicts (+65.5168%), 217.800171 versus 108.300309 solver CPU-s (+101.1076%), and 128,638,536 versus 90,382,454 native proof bytes (+42.3269%). This single comparison does not prove universal slowdown, but it affirmatively cannot support a projection speedup. Neighboring rows lack matched full-parent timing controls; local rank-1298/1299 SAT times are not full-row searches.
