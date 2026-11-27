# Notes

## 1. Two universal counting bounds and their exact scope

For any sender $x$ of colour $c$ and a different root arm $B$ of colour $b$, let $N=\{v\in B:E(x,v,c)\}$. Edges within $N$ can use neither $b$ (root triangle) nor $c$ (sender triangle). Two colours remain, so $|N|\le5$ by $R(3,3)=6$. The bound needs no arm classification and no active sender guard. With fixed positive and unavailable spokes removed, the residual bound is $5-m$, where $m$ fixed spokes are already true.

Consequently, an active guard requiring at least 14 such neighbours over three other arms forces the three counts to be $(5,5,4)$ or $(5,5,5)$: every arm has at least four, every pair at least nine, and at least two arms have five. Auxiliary encodings must preserve the original models. In particular a selector $q_B$ may imply that arm $B$ has at least five receivers, with pair clauses $\neg g\lor q_B\lor q_D$; an original model can extend by setting $q_B$ on two actually full arms.

Independently, $R_3(3)=17$ bounds every monochromatic degree by 16. For $x$ in its own root arm $c$, the root supplies one colour-$c$ neighbour and same-arm colour-$c$ edges are impossible, so the other three arms supply at most 15. For other colours the general degree bound remains 16. Again this is unconditional; the parent encoder contains triangle and root constraints but no explicit global degree counters.

## 2. Local benchmark implementation and data

The generators and fresh matched-run scripts are in `work/arm_caps.py`, `work/distribution_bench.py`, `work/degree_bench.py`, `work/targeted_bench.py`, and `work/cadical212_panel.py`. Original inputs are regenerated through the pinned `hard-study/probe.py`; every original SHA-256 matched `hard1300.tsv`. Exploratory runs use CaDiCaL 1.9.5 unless explicitly labelled 2.1.2. No production ledger or queue was changed.

At 60,000 conflicts, unconditional arm caps reduced decisions on three rows but gave no consistent CPU win; guarded caps were nearly inert. Adding per-arm lower-four or pair-nine counters added many clauses without solving any panel row. On rank 1300 at 800,000 conflicts all of stock, five-cap, lower-four, pair-nine and five-cap-plus-direct stayed OPEN; stock was 40.45 CPU-s and five-cap 40.25 CPU-s.

Universal root-colour degree caps were also neutral at 60,000 conflicts. The all-colour degree version was slower. A compact $k$-totalizer for the 57 root-colour counters used about 22,600 clauses and 8,100 fresh variables per row; the modified totalizer used about 26,400 clauses and 8,800 fresh variables; sequential counters used about 42,000 clauses and 20,700 fresh variables.

## 3. Completed original-parent comparisons on rank 1300

Rank 1300 is `e52b5bdaef139b32a0778abac2b39470076bd55b225de3840bafc83e9110556b`, original SHA-256 `56ad3dc529f1b855e65fa3f3f5363e8275930a7cb6ea5b04dc01a112535b0837`. Standalone CaDiCaL 2.1.2 with proof logging first returned UNSAT in 48.17 user CPU-s and wrote 87 MiB. Its exact conflict count from a fresh no-proof run was 875,852, with 52.42 user CPU-s; wall timings were affected by concurrent swarm work and are not used as the principal measure.

The sequential no-proof 2.1.2 panel completed four records before the overall 600-second harness limit stopped the fifth (extended):

| policy | conflicts | decisions | propagations | user CPU-s | outcome |
|---|---:|---:|---:|---:|---|
| stock | 875,852 | 1,402,059 | 107,430,138 | 52.421 | UNSAT |
| five-cap | 888,836 | 1,392,311 | 122,803,884 | 56.597 | UNSAT |
| root-colour degree cap, $k$-totalizer | 828,729 | 1,336,157 | 106,925,035 | 51.554 | UNSAT |
| previous direct paired-arm bank | 968,863 | 1,516,569 | 116,918,485 | 61.316 | UNSAT |

Thus the degree-cap candidate reduced conflicts by 5.38%, decisions by 4.70%, propagations by 0.47%, and process CPU by 1.65% on this one row/seed. That is a measurable improvement but too small and too narrow to recommend without replication. The five-cap and old direct policies were worse here. The uncompleted extended run supplies no result.

Proof replay initially hit warning-fatal pseudo-unit-deletion warnings. A deletion-only normalization over the entire 90,064,584-byte proof reached the 300-second checker limit and was not accepted. A raw `drat-trim -i -U` pass then verified the complete 90,064,584-byte proof and emitted a core proof, with warnings explicitly recorded. Stripping only deletion records from that core and checking with `-i -U -W -t 600` passed: all 24,356,572 normalized proof bytes were read, one `s VERIFIED`, zero warnings/errors, and 0 RAT lemmas in core. This verifies the baseline without hiding the warnings or the first timeout.

## 4. Glucose-style learned-clause reduction attachment

Archive SHA-256 is `59642cc74e576005e54f64bfc1f344ca3a33f45a7c2b4b5235528f8b711dade0`. The archive supplies upstream CaDiCaL 1.9.5, a five-file source patch, separate stock/hybrid binaries, and bounded results. The patch defaults off. Rebuilding from the supplied source succeeded; the new binary hashes differ from the binaries in the archive, as expected for a new compiler/build identity.

The package's own reported unsplit panel closes no additional rows and has 52.35 stock versus 54.09 hybrid CPU-s; hybrid also deletes more clauses and uses more memory. Completed signed/local examples go both ways: one 4,790-to-2,952 conflict improvement and another 2,756-to-5,131 regression. These are mixed bounded results, not a general win.

Our fresh, matched, rebuilt-binary run on original rank 1300, seed 0, both with proof logging:

| policy | conflicts | propagations | user CPU-s | DRAT bytes | peak RSS KiB |
|---|---:|---:|---:|---:|---:|
| stock 1.9.5 | 883,977 | 108,305,135 | 50.530 | 90,064,584 | 68,172 |
| Glucose hybrid | 941,707 | 114,713,782 | 54.901 | 110,327,620 | 106,912 |

On this completed hard row the hybrid is worse by 6.53% in conflicts, 8.64% in user CPU, 22.50% in proof bytes and 56.83% in peak RSS. This is one row/seed and not a universal condemnation, but it gives no support to deploying the reducer on these inputs. Its proof is retained and has not yet received the same clean core replay as stock.

## 5. Ultramath leads awaiting independent verdict

Swarm `smwziyz3b` is still active. Member-reported, not yet coordinator-accepted results include:

* A compact `two5` selector encoding: on rank 1300 seed 0, stock 883,977 conflicts versus 796,760, with 44.351 versus 39.015 CPU-s and only 8,533 added clauses. This directly exploits the valid at-least-two-full-arms consequence and is smaller than the pair-nine counter encoding.
* All-false initial phases on the unchanged original formulas: repeated conflict reductions on ranks 1200, 1299 and 1300. This is solver guidance, not a clause family, and requires independent reruns and proof receipts.
* New two-star and joint-support clauses have strict representative local proofs but no measured whole-parent improvement so far.

These are leads only until their files, generators, negative controls, fresh proof checks and matched runs are read and reproduced.

## 6. Independently reproduced `two5` and phase results

The coordinator regenerated the member's rank-1300 `two5` formula and checked it byte-for-byte. The portable source is now `work/two5_encoder.py`; its regeneration is byte-identical as well (`work/portable-two5.out`). The member source hash used during review was `76e5db2adc5f53c95623594eccc45ce8dac82cdd6a366e7f69e711ef4532e115`. The output is byte-identical to the member's augmented CNF, SHA-256 `fe9de879d99b320c57c7d90582842a532a045da9c3d90c8df5880d96498eb9af`: 8,533 added clauses and 4,923 fresh variables. A fresh coordinator solve reproduced **796,760 conflicts, 1,296,311 decisions and 98,781,013 propagations**, versus the independently confirmed original-parent 883,977, 1,404,609 and 108,305,135. The member's nearby matched CPU measurements were 39.015 versus 44.351 seconds (12.03% lower); coordinator CPU was higher under concurrent load, so the exact conflict count is the hard comparison.

`checks/verify_two5.py` independently checked all 32,768 two-colour $K_6$ assignments, twelve $K_5$ witnesses, all 216 count triples, all 220 active/inactive abstract selector extensions, exact original-body preservation, and the 168 pair-selector clauses. Its representative original-parent arm-lower-bound replay accepted all 16,652 proof bytes with `-i -U -W`, one `s VERIFIED`, no warnings and 0 RAT lemmas. This validates the model extension and representative geometric content; it is not an end-to-end proof-lifting implementation for the auxiliary `two5` formula.

Scope matters. The same `two5` policy on rank 1299 was worse (1,081,870 versus the stock 1,000,820 conflicts), and on rank 1300 seeds 1 and 2 it was also worse than stock. Critical/marked subsets have different behaviour again. Thus this is a general sound constraint schema with a measured useful instance, not a universal speedup or a completed 1,300-row evaluation.

The coordinator also independently reran all-false phases on the unchanged rank-1300 parent and reproduced **745,335 conflicts and 93,044,313 propagations**, versus stock 883,977 and 108,305,135. The member's cross-row measurements have material gains on several rows but regressions on rank 1298 and on rank 1300 seed 1 as well. All-false changes no clauses or logical constraints. Its SAT controls and wrong-hash rejection passed in the member package.

Combining the two mechanisms is not an improvement over either alone: on rank 1300 seed 0, `two5 + all-false` returned UNSAT after **847,047 conflicts and 103,501,199 propagations**, versus 796,760 for `two5` alone and 745,335 for all-false alone. There is no evidence for a synergistic policy.

**Native phase flags are not the same policy.** Fresh native 1.9.5 runs on the same parent gave 928,042 conflicts for `--no-phase` alone and 831,681 for `--no-phase --forcephase`, versus stock 883,977 and explicit per-variable all-false 745,335. In this CaDiCaL source, `set_phases` fills `phases.forced` one variable at a time, whereas `--phase` changes only the initial/saved default; they interact differently with target phases and rephasing. The explicit API result therefore must not be advertised as a simple `--no-phase` speedup.

## 7. Signed-pair submission and verdict

The m4 signed size-two support-certificate family is mathematically valid: its clause is $\neg g\lor L_B\lor L_D$ where each signed $L$ hits every original-scope compatible five-support in its arm. The coordinator independently reran every support check on all 3,709 rank-1200 and 2,995 rank-1300 retained clauses, including the guard-broken and removed-scope controls. The original-parent representative strict replay read all 16,652 bytes, returned one `s VERIFIED`, no warnings and 0 RAT lemmas.

The submission was nevertheless **rejected as a solver improvement**. Its six completed pairs reduce conflicts by 1.80% but increase post-parse CPU by 6.45% and summed wall time by 5.83%; rank 1200/seed 2 has a 61.65% CPU regression and the smaller one-negative policy is worse still. The family is retained as a verified negative/structural result, not as evidence that adding more short clauses is useful.

## 8. Fresh full-proof core observations, not transfer theorems

The fresh stock proof's first core has 5,245 of 211,564 parent clauses. Every one maps back to a physical host clause or frozen physical unit; no original threshold-auxiliary clause is present in that output. The induced support is 35 vertices: two full 15-vertex arms plus five vertices of the small arm. This does not yield an easy standalone refutation—the core-only solve was OPEN after 60 seconds and 1,233,403 conflicts.

From the verified core, 15 final physical units alone turn the identical source-row stock solve into a 0.04-second, 207-conflict refutation. The 5,212 deduplicated new physical learnt clauses of width at most three reduce it to six conflicts. These are dramatic **proof-derived checkpoints on their source input**, not general clauses or evidence of transfer to another row. All 15 units lie on the arm-1/arm-2 interface. No claim of cohort-wide validity, automatic relabelling, or a reusable local theorem has been made.

## 9. Production status

No production ledger, queue, or 1,300-row campaign was changed. `two5`, the arm caps, and the degree-cap experiments use fresh auxiliary variables and have no implemented original-parent DRAT derivation prefix in this work. The mathematical model-extension argument is distinct from a production certificate pipeline. The direct physical signed pairs and lower bounds have representative proofs, not a complete per-row bank of refutations. The Glucose patch was rebuilt and benchmarked but not installed into the cohort tooling.

## 10. Compact paired-arm selection and signed-kernel follow-up

The strongest clause-based result is a compact selection on two representatives. The coordinator regenerated the exact formulas and complete audit, independently repeated one primary comparison, copied the source into `work/`, and verified the portable copy byte-identically. No logical novelty is claimed over the paired-arm clauses themselves.

| selection | added clauses | three-seed conflicts stock → selected | native search CPU stock → selected |
|---|---:|---:|---:|
| TUU 1288 `wide_delta = F \ (D ∪ T)` | 112 width 4 | 4,018,246 → 3,363,248 (−16.30%) | 263.15 → 160.67 s (−38.94%) |
| UUU 1162 `short = {C in D ∪ T ∪ F: card(C) ≤ 4}` | 24 width 3 + 193 width 4 | 3,219,778 → 3,054,950 (−5.12%) | 192.37 → 141.27 s (−26.56%) |

The independent TUU seed-2 rerun reproduced exactly 1,041,030 versus 1,149,949 conflicts, with coordinator CPU 47.28 versus 53.96 seconds. All 112 and 217 emitted clauses and their guards were independently checked; the representative 16,954-byte wide proof passed warning-free original-parent replay with 0 RAT. All primary timing calls returned UNSAT but did not generate full proofs. One seed on each profile has a small conflict regression, and every tested paired-arm policy on rank 1300 was worse. Scope is still these two rows and their seeds.

The m4 signed-pair follow-up explicitly withdraws every speedup claim. I regenerated the reverse kernels' exact hashes and independently verified their final-UP coverage: 438/445 clauses remain after eliminating 88.19%/85.14% while every original false cube remains closed. Fresh forward, reverse and combined policies still leave rank-1200 regressions, so the accepted disposition is mathematical/negative evidence, not a solver improvement. It does not change the positive m6 selection result above.
