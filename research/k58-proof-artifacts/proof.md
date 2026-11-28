**Status: PROVED. The ledger gate accepts #14, with independent `compute` and `model` checks. This is an audit of scoped clauses and certificates, not a new wall closure or a general solver-improvement theorem.**

# Audit of four K58 proof-artifact archives

## Outcome

The scoped mathematical and certificate audit is successful, but the supplied experiments do not establish a general or amortized solver improvement. They produce no new wall closure, no full-satisfying model and no change to the Ramsey bound.

The accepted conclusions are:

1. The general fixed-graph/list spoke rule is sound as a local 2-SAT obstruction. The four delivered ordinary-wall clauses are consequences of their respective original parents. Its performance panel remains OPEN and slower in total.
2. The two mined clauses in D are original-parent consequences. Each of the seven square transfers has a fresh two-step RUP certificate on its exact parent. Transfer requires semantic geometric rebinding; the same variable labels and proof bytes do not generally transfer. The ternary escape schema is specific to four colours, unlike the underlying square obstruction.
3. The five supplied projection refutations concern selectable subformulas, not new unrestricted searches. They also have parent-level proof certificates. The two projection SAT cases provide only local colorings, not full-parent models.
4. All eight supplied comparison streams independently check against the unrestricted original parent A, not just an augmented query. Their search statistics are limited to one historical row and two seeds and do not pay for mining, proof generation or checking.

This is an audit of existing historical cases; it does not imply that any unresolved K58 case is now closed.

## 1. Local spoke rules and wall-clause derivations

For a fixed graph, each site has a list of at most two colours permitted on its outside spoke. For each colour available at both endpoints of an identically coloured fixed edge, the combined choice is forbidden. The resulting 2-SAT instance has a solution exactly when its implication graph contains no complementary literals in the same strongly connected component. Every fixed edge must still be checked against the selected spoke colours. Missing fixed edges impose no extra constraint; the empty list is immediately impossible.

This gives a local minimum-deletion obstruction $\tau$: every spoke selection has at least $\tau$ out-of-list sites, where $\tau$ is the least number of sites that must be deleted to make the local problem feasible. Lifting such a statement to a parent still requires actual physical pins and colour exclusions at that parent.

The exhaustive implementation audit compared brute-force assignment enumeration with the SCC implementation on 186,624 four-site K4 missing-edge/list cases and 166,375 three-site four-colour cases, together with complete graphs through K6 and satisfiable controls. The independent coordinator then compared another 4,000 randomized constrained cases. No mismatch was found. Among the 18 legal two-colourings of K4, all six obstructions are exactly a square in one colour and a perfect matching in the other.

The result generalizes the earlier **local** square/matching obstruction. It does not syntactically subsume the separate guarded K15 square theorem: the four new wall clauses are unguarded positive palette-escape clauses rather than the earlier guarded clauses.

For each of four selected ordinary-wall rows, pin and colour-denial witnesses were reconstructed from original physical units and clauses. Each final five-literal clause was derived in two RUP steps. All eight obligations passed native `drat-trim` with `-i -f -W -U`, reading all 16 proof bytes, with no warnings or RAT lemmas. Eight no-helper controls correctly failed. These are derivation checks, not bare-parent UNSAT checks.

The supplied benchmark has 16 runs at about 40,000 conflicts, all OPEN, and cannot imply SAT or UNSAT. Summed child CPU is 21.502271 s stock versus 25.948904 s with the clauses, a **20.6798% increase**; only one of eight paired seeds improved. No discovery or certification overhead is included. Thus no wall speedup follows.

## 2. Mined clauses and literal-label transfer

The original parent A and augmented D have the same physical variables, and D is A plus exactly

```text
4687 3590 4034 4673 0
-5160 3282 4822 0
```

Call these $C_4$ and $C_3$. Every original-parent RUP step of their supplied proof slices passed. Fresh original-parent derivations were also checked: 14 additions/451 bytes for $C_4$ and two additions/42 bytes for $C_3$. Finite motif checks covered all 1,296 and 576 falsifying assignments, respectively, and showed that the tested premise covers are inclusion-minimal.

The general square fact allows arbitrary numbers of colours. The derived three-literal escape rule requires the additional four-colour hypotheses and explicit denials; dropping a premise or adding a fifth colour has a local counterexample. All seven transfers were certified by semantic role matching and fresh parent-relative RUP proofs. Raw variable-label replay at a neighbouring rank failed, as expected for a different fixed geometry.

The separate rank-1300 square transfer `-3900 3282 3598` is **not** D's `-5160 3282 4822`. It cannot inherit D's timing measurement. The B/C additions' original-parent certificates establish the refutations in this audit, not a general model-preservation theorem on other inputs.

## 3. Projection scope and models

For a selected vertex set, take exactly the parent clauses whose variables all lie on edges induced by that set, preserving variable numbering. Call the result $P\subseteq F$. Therefore $P$ UNSAT implies $F$ UNSAT, while $P$ SAT alone says nothing about whether $F$ has a satisfying extension. The selected 35/36 vertices use the earlier-known arm and marked-neighbour units, not a retrospective proof core.

The independent rebuilding covered all seven projections. Every one is a strict ordered subsequence of its original parent, with only the header clause count changed. Parent hashes match `hard1300.tsv`, all row IDs and projection hashes match the bindings, and there are no auxiliary projection variables. Six projections have 30,630 clauses; rank 1299 has 33,270.

The rank-1298 model, on 35 selected vertices, satisfies all 30,630 projected clauses but falsifies 1,318 clauses of its complete parent under the same assignment. Rank 1299 similarly satisfies all 33,270 projected clauses but falsifies 1,287 parent clauses. Neither is a model of K58 or of an unrestricted parent.

Raw source hashes for the five projection proof streams and their distinct projection-query versus full-parent certificate bindings were independently recomputed in `checks/remaining-recomputation.json`. The two checks must not be conflated: the solver refuted a projection, while the final proof was checked on the complete original parent.

All five refutations received native parent-level replay. To avoid warning-bearing deletion bookkeeping, a byte-exact parser dropped only deletion commands and retained every addition, accounting for every source byte and exactly one empty addition. Ranks 1294, 1295, 1296 and 1300 then passed `drat-trim` with warnings fatal and RAT disabled, followed by an independent C LRAT check on their unrestricted parents. I independently did the same for rank 1297; its receipt is checked independently in `checks/P12970-parent-replay.json`.

| rank | raw proof bytes | native DRAT-stage user CPU-s | final classification |
|---:|---:|---:|---|
| 1294 | 155,381,768 | 486.62 | verified original-parent UNSAT |
| 1295 | 140,972,662 | 314.22 | verified original-parent UNSAT |
| 1296 | 162,346,866 | 466.84 | verified original-parent UNSAT |
| 1297 | 82,519,178 | 139.388 (coordinator) | verified original-parent UNSAT |
| 1300 | 128,638,536 | 245.39 | verified original-parent UNSAT |

Together these are 669,859,010 proof-source bytes, normalized to 336,193,354 addition bytes and 1,375,316,158 newly checked LRAT bytes. The CPU figures are only the reported native DRAT-stage costs, not projection generation, conversion/checking totals, or a comparison with the original full-row searches. The certificate-LRAT files themselves were not supplied; these fresh LRAT identities do not purport to reproduce the absent certificate bytes. Exact hashes and replay scopes are consolidated in `checks/projection-replay-reconciliation.json`.

On the only directly comparable original/projection run—original A0 versus P13000, seed 0 and cap 2,000,000—the smaller projection had 1,449,682 versus 875,852 conflicts (+65.5168%), took 217.800171 versus 108.300309 solver CPU-s (+101.1076%), and wrote 128,638,536 versus 90,382,454 native proof bytes (+42.3269%). This one case does not establish universal slowdown, but it cannot be cited as a projection speedup. Neighboring projections have no matched full-parent timing controls, and local SAT times on ranks 1298/1299 are not parent-solving times.

One replay-transparency defect remains: the supplied `recheck.py` uses `-w`, concealing deletion-bookkeeping warnings. Those warnings are not counterexamples to the independently checked parent refutations, but a publication/replay harness should not suppress them. The accepted path instead normalizes away deletion commands and exposes all subsequent checker behavior. A missing-empty proof and a wrong-parent formula are properly rejected; exploratory timeouts are not counted as proof results. The final projection report initially mislabeled three kind strings as `TTU-` where the actual cohort values are `TTT-`; that version was rejected and the corrected table was accepted.

## 4. Comparison-proof and core audit

The original unrestricted rank-1300 parent A has SHA-256 `56ad3dc529f1b855e65fa3f3f5363e8275930a7cb6ea5b04dc01a112535b0837`, 29,942 variables and 211,564 clauses. The comparison formulas preserve A's body and append the recorded geometric clauses; D's query hash is `e51ef50cc4a7a6234118be0cf14063681929dfa509e0e5ac95e3ff006aa4dc75`.

Each requested A1, B0, B1, C0, C1, D0, D1 and K0 source was decompressed and hashed, converted by native `drat-trim -i -C -U` **without `-w`**, scanned completely as binary LRAT and then checked by the independent C `lrat-check` against A. All eight passed, with one terminal empty clause, no later additions, zero RAT hints and zero final warnings/timeouts. Their source and LRAT identities agree with the attached certificates. The totals are 419,793,932 source bytes and 1,084,173,458 LRAT bytes.

Thus these are genuinely original-parent refutations. The added B/C/D clauses are not accepted as axioms by the final proof. The C checker itself passed a valid toy proof and rejected a wrong parent, an empty proof and a truncated proof. Only A0 and K0 raw solver streams are available. The other seven attachments are trimmed streams: absent raw hashes cannot be re-derived, though their actual trimmed-source hashes and independent original-parent certificates were checked.

The two A0 cores are associated with different valid searches:

| core | source solver / proof | clauses |
|---|---|---:|
| old | CaDiCaL 1.9.5, raw SHA-256 `91be718315926c5f0348a5d98a211b70e3dec2c4345ccea05d275fc58b3bbac5` | 5,245 |
| new | CaDiCaL 2.1.2, raw SHA-256 `9798683a7f8b3e5ee7c77b86c005bd64aa4357490be350bafd71ea0e76ee9e89` | 5,250 |

The cores share 4,359 clauses as exact literal lines, or 5,094 after sorting each clause's literals. These are different comparison conventions, not inconsistent set sizes. K is byte-identical to the new 5,250-clause core and does not certify the older core. Its direct K replay also succeeded and confirms K is UNSAT. A subsequent retrospective trim of K is not an earlier-selectable algorithm.

A0's first-pass LRAT was regenerated from its raw proof; a second pass on A0.trim gives another valid, non-identical LRAT. The supplied fallback `recheck.py` uses `-w` and does not compare that second-pass LRAT hash with the stored certificate. This is a provenance defect, not a failed refutation. Strict `-W` conversion runs rejected deletion bookkeeping and were recorded separately, not suppressed or counted as successful replays.

## 5. Measured search versus end-to-end benefit

The comparison tables use proof-writing solver runs on a shared machine. Over only seeds 0 and 1 of rank 1300:

| variant | conflicts | proof-writing CPU-s | native proof bytes |
|---|---:|---:|---:|
| A | 1,845,186 | 218.032950 | 190,090,051 |
| D | 1,680,786 (−8.910%) | 200.611902 (−7.990%) | 167,306,123 (−11.986%) |

This is a useful descriptive search reduction when the clauses are already available. It is not an amortized speedup: baseline solve plus native trim plus selection is about 196.492 **mixed CPU/wall** seconds versus 17.421 CPU seconds saved on the two D solves. Candidate extraction is unpriced, and full proof conversion/checking is extra. The reported total adding unit-unlike stages is a bound on any cold claim, not a cold wall-time measurement.

A0 metadata also places the native 85.221-second trim under `convert_to_lrat_wall_s` while its certificate records no conversion time. Stage timings must not be summed as though their labels were uniform.

No cohort estimate, default solver setting or full-cover campaign follows. The 40,000-conflict ordinary-wall tests separately remain OPEN and have negative aggregate timing.

## Evidence and limitations

Independent reports and native receipts are in `.ultramath/smwzmjadv/m1`, `m2`, `m3` and `m4`. Coordinator recomputations are `checks/remaining-recomputation.json` and `checks/P12970-parent-replay.json`; `checks/recompute_remaining.py` regenerates the source/binding/statistical audit. Earlier native A0, C0, D0, K0 and P13000 checks are summarized in `checks/original-proof-receipts.json`.

Checks used native DRAT/RUP and independent C LRAT checking, not a pure Lean-kernel proof. No new production search, solver timing run, historical raw-proof recovery, wall-parent model or wall-parent closure was attempted. No earlier solver-policy result outside these four archives is overruled by this scoped audit.
