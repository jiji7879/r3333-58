# Dynamic symmetry after the K58 wall campaign: prioritized next-step review

**Direction:** SMS/dynamic symmetry and graph-automorphism-based pruning
**Review date:** 2026-11-28
**Repository inspected:** HEAD `211dd0b2b705efef7481d5cace379fea99a2a0ca` (the initially checked-out HEAD `211dd0b`).

## Decision

| priority | category | proposal | why it is now concrete | first falsification / stop rule |
|---|---|---|---|---|
| **1** | **(b) solver-throughput experiment** | **Restricted one-colour SMS, export clauses, replay with the incumbent solver.** Fix colour names, permit only $H=S_9\times S_6$, and use colour 0 as the single SMS adjacency matrix. | The exact retained parent really has this nontrivial frozen-unit/cube stabilizer. All 51 transpositions preserve its abstract sender/support semantics. Current upstream SMS has block-restricted minimality and emits permutation witnesses. | Independent witness/unit/cube/lex checks first. Stop if a bounded generation run emits no valid nontrivial clause, or if a matched small parent+cube A/B has at least baseline propagations with no compensating reduction in searched space. Do not sweep. |
| **2** | **(c) certificate/proof engineering only** | Port the two-phase LeanSMS witness check to an **$H$-orbit, four-colour projected-model** theorem. | The 2026 paper and source expose precisely the missing trust boundary: isomorphism invariance, per-clause permutation verification, auxiliary completeness, then a separate LRAT run. | Implement only after priority 1 produces usable clauses. A proof that checks global lex decrease but not $q\in H$ or the cube is rejected. `native_decide` instance proofs cannot be imported under this campaign's standard-axioms discipline. |
| **3** | **(b), then (c)** | **Defer** symmetric explanation learning (SEL) until an explicit full auxiliary permutation is available. | SEL avoids a large static comparator and learns a symmetric explanation only when it is unit or conflicting. | No experiment until a generated Sinz-register map makes at least one concrete transposition a full-CNF automorphism in a toy and in the exact parent. No such aux-fixed symmetry exists in the actual parent today. Reject incompatible preprocessing. |

**No proposal here is a new mathematical Ramsey closure, a ChainReady proof, a wall/profile closure, or a bound change.** There is no worthwhile candidate of category (a) in this direction. Relabelling does not create the physical incidence facts still missing from `ChainReady`.

## Frozen status and scope

Radziszowski, *Small Ramsey Numbers*, DS1 revision **18**, dated **24 April 2026**, [DOI 10.37236/21](https://doi.org/10.37236/21), section 6.2 (extracted page 56), states $51\le R_4(3)\le62$ (Chung 1973; Fettes–Kramer–Radziszowski 2004). The primary PDF was fetched and read; its SHA-256 is `9519a676ee381f02f03269c22e3f101162b2fdcc9d432e4103cb1192fdff91bc`. That remains the accepted status here.

The current [arXiv abstract page for 2610.36648](https://arxiv.org/abs/2610.36648) and [arXiv API record](https://export.arxiv.org/api/query?id_list=2610.36648) both say **Milos Tatarevic**, *An upper bound of 60 for the Ramsey number R(3,3,3,3)*, v1 27 October 2026, v2 6 November 2026. The official repository account is [`milostatarevic/r3333-upper-bound`](https://github.com/milostatarevic/r3333-upper-bound). These current primary records do **not** corroborate the older local “M. Stojanović” author field; they also do not establish whether the different names refer to the same person. Use the arXiv name when citing it and preserve the discrepancy rather than silently merging identities. The preprint only **claims** $R_4(3)\le60$ through global counting, classifications, Lean and two SAT solvers. This review did not independently DRAT-check its formulas and does not establish $\le60$, much less $\le58$.

The target remains row `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`, profile $(16,16,14,11)$, charge 7, ordinary recipe `tables=True,total_critical=True,full_root=False`, cube `[-1413,1014]`. No MCF suffix is used or proposed for the first experiment. Frozen units by themselves remain a relaxation, not a physical encoding.

## What the exact local compatibility gate found

Two solver-free scripts were run with the repository's existing `../../../.scratch/k58/.venv/bin/python`. Their complete outputs are in `symmetry_fit.json` and `counter_specs.json`.

### Parent identity and stabilizer

The regenerated ordinary parent is exactly:

```text
p cnf 19533 184335
SHA-256 90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae
```

Appending the two target cube clauses in the specified order gives SHA-256
`8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8`, matching the retained-leaf report. The parent has 438 explicit fixed signed units (396 positive, 42 negative); this is not the separate count of 1,813 parent/BCP-derived units in the residual audit.

There are two complete frozen-unit twin cells:

$$
C_2=\{38,39,40,41,42,43,44,45,46\},\qquad
C_3=\{52,53,54,55,56,57\}.
$$

Every one of the $\binom92+\binom62=51$ transpositions was applied to every fixed signed unit, including signs, and preserved the set. The adjacent transpositions therefore generate a verified candidate group

$$
H=\operatorname{Sym}(C_2)\times\operatorname{Sym}(C_3),
\qquad |H|=9!\,6!=261{,}273{,}600.
$$

All 51 transpositions also preserve the target cube set exactly. This is an **encoding-relabelling group**, not an achieved search reduction and not an automorphism group asserted for an unknown solution graph.

The cube literals decode to colour 0 on $(6,33)$, false, and colour 1 on $(4,36)$, true. Every future cube needs its own stabilizer check; parent stabilizers cannot be inherited by assertion.

### The suffix fit is semantic, not syntactic

All 51 transpositions leave the abstract counter specifications unchanged. The exact ordinary recipe makes:

- **31** physical sender `atleast` calls;
- **15** support-event calls, at selected-arm vertices $18,\ldots,32$;
- **2** final selector-guard bounds, for 33 `atleast` calls altogether.

For each transposition, sorting each counter's physical input literals and comparing the multiset of `(inputs,bound)` gives exact equality. All literals occurring in actual support clauses are fixed. This follows the code, not merely the unit signatures: support selectors on this row involve only selected arm 1 and arm 0, which are pointwise fixed by $H$; the ordinary recipe allocates no sender guards rooted in the two noncritical arms where $H$ acts.

Nevertheless, no transposition is an automorphism of the emitted full CNF when auxiliaries are left fixed. For $(38\,39)$ the first failure is clause **135464**:

```text
original: ( 373, -6613, -6642, 6644 )
image:    ( 377, -6613, -6642, 6644 )   # not a parent clause
```

Thus **naive BreakID/SEL input is falsified on this parent**. The finding does not rule out a separately proved permutation of Sinz registers, nor does it rule out a projected-model SMS cut. It does rule out skipping those issues.

## Distinguish the four things called “symmetry”

1. **Palette symmetry.** Global colour relabelling has already been used for cover normalization (`frozen/palette_quotient.py`). The candidate parent action here fixes all four colours. Moving colours would generally move root units, guards and the selected arm.
2. **Residual graph automorphisms.** A hypothetical $G_c$ may have few or no nontrivial automorphisms; that is irrelevant to the existence of $H$ as a relabelling group of labelled physical models. Conversely, $H$ says nothing structural about an unknown $G_c$.
3. **Root/frozen-unit/split stabilizers.** $H$ is genuine at the explicit-unit and abstract-suffix level. Its witnesses must be rechecked on every split/cube and every changed suffix. This is the only group proposed for the leaf SMS action.
4. **Case-cover symmetry.** Permutations among different family/template/cube cases belong to cover normalization. The $H$ above lives inside one parent and neither reduces the frozen 113179-case count nor discharges any uncovered case.

## Exact theorem template for priority 1

Let $\mathcal M$ be the set of **physical** four-colour assignments satisfying the intended ordinary-parent-and-cube predicate, not merely an assignment to frozen units. For fixed designated colour $c$, let $L_c(G)$ be the Boolean upper-triangular adjacency word of $G_c$ in SMS lex order. Suppose

1. $q(\mathcal M)=\mathcal M$ for every $q\in H$;
2. every $G\in\mathcal M$ admits an auxiliary extension satisfying the actual CNF $F$;
3. each exported clause $C$ comes with $q\in H$ and a checked strict indicator certificate showing that whenever $C$ is false, its partial assignment forces $L_c(q(G))<L_c(G)$ for every completion $G$.

If $\mathcal M\neq\varnothing$, choose $G^\star\in\mathcal M$ minimizing $L_c$ over the finite $H$-orbit of any model. Invariance gives $G^\star\in\mathcal M$, and every exported clause is true there. Hypothesis 2 then gives a model of $F\land S$. Consequently

$$
F\land S\ \mathrm{UNSAT}\quad\Longrightarrow\quad \mathcal M=\varnothing .
$$

The $H$-orbit lemma is straightforward finite-orbit reasoning, but each hypothesis is substantive. In particular, SMS clauses are symmetry cuts, generally **not logical consequences or DRAT/RAT consequences of $F$**. A second, ordinary CDCL refutation of $F\land S$ does not remove the need for this bridge.

For this exact leaf, the 51 local checks support hypothesis 1 at the exposed physical level via the code-level counter/support analysis. Hypothesis 2 and the original physical meaning of `Sends`, exact support membership and coded/automatic guard-set equalities are campaign obligations, not solved by symmetry. `PhysicalBridge` or its descendants would still have to be instantiated, and `ChainReady` remains open.

## Candidate 1 in detail: restricted one-colour SMS (throughput)

### Primary source and what it establishes

**Markus Kirchweger and Stefan Szeider**, [*SAT Modulo Symmetries for Graph Generation*](https://doi.org/10.4230/LIPIcs.CP.2021.34), CP 2021, LIPIcs 210, 34:1–34:16. Section 3 and Proposition 2 define partially defined graphs and strict indicator pairs; Theorem 5 concerns the completeness of `MinCheck` on constraining inputs; section 3.1 explains worst-case permutation search and learned clauses. A clause is valid for lex-minimal representatives because of its strict indicator property. Partial checks can omit pruning without making a correctly checked emitted clause stronger than intended.

The method's assumption is a graph property invariant under the vertex relabellings being used. Unrestricted graph isomorphism is not an exemption from that assumption. Minimality is worst-case exponential/NP-hard in the general setting, so propagation time must be measured, not inferred.

**Current official software:** [`markirch/sat-modulo-symmetries`, commit `63958bd09a871e484c59270a1d0f22d482dc5770`](https://github.com/markirch/sat-modulo-symmetries/tree/63958bd09a871e484c59270a1d0f22d482dc5770) and its [documentation](https://sat-modulo-symmetries.readthedocs.io/en/latest/).

- `src/options.cpp:31--33`: `--initial-partition` restricts minimality search to permutations preserving block membership; `--sym-break-clauses` selects witness output.
- `src/minimalityCheckCommon.cpp:51--78`: each emitted symmetry clause is written with its permutation.
- `src/graph.hpp`, `src/graph.cpp`: edge variables must be the first $\binom n2$ variables in row-wise upper-triangle order.
- Docs, “Requirements” and “Quick Start”: C++20, Boost 1.74+, CMake 3.12+, and a specially adapted CaDiCaL. A minimality cutoff can make symmetry breaking incomplete; that is acceptable for a search hint only when every emitted clause is independently checked, never for a completeness-by-assertion claim.

Crucially, **stock four-overlay SMS is unavailable**. `GraphHandler` has `overlayingGraphs = 1` and the other case calls `EXIT_UNWANTED_STATE`; `MultipleMinimalityChecker` exists, but its symmetry-witness file output is an unimplemented `EXIT_UNWANTED_STATE` path. Therefore “feed the four-colour K58 CNF to SMS” is not a compatible plan.

### Concrete fit construction

Use only one colour $c=0$ as SMS's graph. Reindex the entire exact CNF by a recorded bijection:

```text
old physical variable 4*r + 0 + 1  (r=0..1652)  ->  new r+1
other three physical colours       ->  new 1654..6612 (recorded bijection)
old auxiliaries 6613..19533        ->  unchanged
```

Map all host, fixed-unit, 31 guarded sender, 15 support-event, two final-bound and two cube clauses through this same bijection. Do not regenerate a weakened formula and do not add MCF. The initial SMS partition consists of singleton blocks for every vertex except cell $C_2$ of size 9 and cell $C_3$ of size 6. This matches the contiguous-block restriction available upstream.

Run SMS only as a **bounded clause generator**, not as a decision procedure. For each raw emitted `[clause,q]`:

1. Parse the entire receipt; reject truncation, duplicate/corrupt lines and non-bijections.
2. Test $q$ against the declared cells, every fixed signed unit and the exact cube. Do not trust `--initial-partition` as proof.
3. Independently verify the strict lex indicator with the same partial/undefined convention as the source. Check both possible permutation orientations in a rejecting control.
4. Map the clause back through the recorded variable bijection, deduplicate byte-exactly, and reject literals outside the designated physical tier.
5. Append only validated clauses to the original ordinary parent+cube. Solve that augmented formula with the incumbent engine and existing strict DRAT/model gates. An SMS `SAT` or `UNSAT` line, and an LRAT stream that simply assumes external SMS clauses, are not accepted results.

### Minimal reproducible A/B and abandonment rule

This is a proposed pilot, **not a run already performed here**.

1. **Toy controls first:** on a small pinned $K_4/K_5$ four-colouring, enumerate physical models before/after the exported clauses and show every $H$-orbit retains a representative. Reject a non-$H$ permutation, an inverted permutation, an altered cube, an altered undefined entry and an auxiliary remap. These controls differ from the old vacuous-comparator test: they check the actual clause/permutation pair and the $H$ orbit, not just SAT preservation.
2. **Generation gate:** bounded 60 CPU-s of SMS on the exact reindexed parent+cube, with a hard receipt/clause cap. If there is no valid non-unit, nontrivial clause, stop. If every emitted clause is made tautological by explicit units, recording that fact is more useful than increasing the budget.
3. **One matched A/B:** on the exact parent+cube, run baseline versus original-parent-plus-validated-clauses with the same incumbent CaDiCaL build, proof enabled, same seed, 200,000-conflict cap, jobs 1, and balanced run order. Record generation cost separately, added clauses/bytes, statuses, conflicts, decisions, restarts, propagations and solve CPU. Both OPEN is only a throughput result, never UNSAT evidence.
4. **Abandon rather than tune:** stop if validated generation is empty; if parsing/witness checks fail; or if augmented propagations are at least baseline propagations while decisions/conflicts give no reduction of at least 20% at the same cap. A closure with a checked proof overrides these heuristic stop numbers. Any further test must be earned by that single A/B, not by a wall sweep or a longer retry.

The rationale for trying once despite the old 4.75x static-lex propagation result is specific: this approach uses an actually validated nontrivial group, the unaffected support tier, and lazily generated clauses rather than the full initial one-hot comparator. The rationale for expecting failure is equally specific: minimality on 58 vertices can dominate CDCL, the group acts only on 15 vertices, and many emitted prefixes may be long. The proposed cap measures exactly that uncertainty.

## Candidate 2: LeanSMS witness checking (certificate engineering)

**Markus Kirchweger, Pablo Manrique Merchan and Stefan Szeider**, [*Formally Verified Graph Generation with SAT Modulo Symmetries and Lean*](https://doi.org/10.1007/978-3-032-32589-1_8), IJCAR 2026, LNAI 16688, pp. 117–135. Sections 3.2–3.8 require, separately: isomorphism invariance of the property; encoding completeness on physical variables; per-clause/permutation verification (`verifyDominationFull`); and a second solver's LRAT proof. Section 3.5 explicitly notes SMS clauses are not generally RAT-derivable and that an incremental LIDRUP checker was unavailable in Lean. Their framework does not waive any of these conditions.

Official implementation: [`leansolving/leansms`, commit `8fa708e4c8a00a8951dadc5c0f68863d057fcfab`](https://github.com/leansolving/leansms/tree/8fa708e4c8a00a8951dadc5c0f68863d057fcfab). `LeanSMS/Verify/TrustModel.lean` and `Verify/SymBreakSound.lean` contain the global-$S_n$ argument; `Parse/SymBreakJSON.lean` handles witness files. The pinned toolchain is `leanprover/lean4:v4.24.0-rc1`, not this VM's current Lean toolchain. Neither LeanSMS nor its examples was built or executed here.

Use its checker as a reference, not as a turnkey K58 theorem. Required changes are exactly:

- replace the global-$S_n$ lex-least lemma with the finite $H$-orbit lemma above;
- replace `SimpleGraph` with the four-colour physical realization and one designated adjacency word;
- include root units, split cube and counter/support semantics in the invariance proof;
- reuse or prove auxiliary completeness after permutation (physical `agreeOnEdges` alone is insufficient);
- feed only checked augmented CNF into the already accepted strict proof path.

The general theorem source does not make `ChainReady` disappear. The supplied instance files also use `native_decide` for certificate/LRAT booleans, whereas this campaign's new K58 modules require standard axioms without `native_decide`. Porting those concrete checks therefore needs theorem-level/kernel-checked replacements or the existing external strict verifiers; copying the instance idiom would violate the local evidence policy. Allow a few days for an isolated checker/invariance prototype, not for the whole wall semantic assembly.

**Abandon** this engineering branch if priority 1 has no usable clauses or if restricted invariance cannot be stated without assuming the very `Sends`/guard-set equalities still missing from the parent proof. Do not spend proof-engineering time merely to restate unrestricted graph invariance.

## Candidate 3: SEL only after explicit auxiliary lifting

**Jo Devriendt, Bart Bogaerts and Maurice Bruynooghe**, [*Symmetric Explanation Learning: Effective Dynamic Symmetry Handling for SAT*](https://www.bartbogaerts.eu/articles/2017/004-SAT-SEL/SAT-SEL.pdf), SAT 2017, LNCS 10491, pp. 83–100, [DOI 10.1007/978-3-319-66263-3_6](https://doi.org/10.1007/978-3-319-66263-3_6).

Section 2 requires a permutation on literals that commutes with negation and preserves formula satisfaction; clause-set preservation is the sufficient syntactic condition used by their implementation. Proposition 1 says $F\models C$ implies $F\models q(C)$ for a symmetry $q$. Section 3 learns a symmetric explanation only when it is unit or conflicting. Section 4.3, Theorem 1, permits preprocessing only when the preprocessed formula is a logical consequence of the original and equisatisfiable with it. The reported implementation uses Glucose 4.0 and BreakID's syntactic detection; it is not a compatibility proof for native CaDiCaL/K58.

The measured aux-fixed scan already rejects the simplest lift. A permissible continuation would be to inspect each guarded sender's generated Sinz inputs $x_1,\ldots,x_m$ and construct the induced permutation of its position-indexed registers, leaving guards and support selectors mapped appropriately. Require exact whole-parent clause-set preservation with all auxiliaries mapped, and reject a wrong register swap. Only then would an SEL A/B be meaningful. Any pre- or in-processing mode must separately satisfy SEL's Theorem 1; search-only is not a certificate by itself.

**Abandon immediately** if a complete aux permutation is not produced and checked on small counters and the exact parent. There is no sound fallback of applying $q$ to physical literals while leaving counter auxiliaries fixed, and symmetric learned clauses still need separate witness composition with strict DRAT replay.

## Explicit no-go / already-closed items

- **Unrestricted $S_{58}$ SMS or stock multi-overlay SMS:** unit/cube invariance fails in general, and current source does not support integrated four-graph witness output.
- **Trusting direct SMS verdicts or its external-clause LRAT:** generated clauses are not automatically RAT consequences; export, verify and independently replay.
- **Naive BreakID/SEL on physical variables with auxiliaries fixed:** all 51 proposed witnesses fail the full-CNF syntactic test.
- **Another full static lex or corrected one-hot comparator:** the prior exact pilot already paid 4.75x propagations and closed nothing. Priority 1 is conditional on being materially different and cheap, not a retry of static lex.
- **Co-certificate learning (CCL):** Kirchweger–Peitl–Szeider, [*Co-Certificate Learning with SAT Modulo Symmetries*](https://arxiv.org/abs/2306.10427), IJCAI 2023, targets an outer NP graph candidate with a co-NP property learned from counterexamples. The K58 parent is already existential CNF; CCL does not supply the missing `ChainReady` semantics or a new symmetry witness. No CCL experiment is proposed.
- **Cutoff as a completeness argument:** a minimality cutoff/frequency can skip pruning and invalidate exhaustive-isomorph-enumeration claims. It is only a bounded clause-sampling policy here.
- **Using $H$ to reduce the 11 profiles, close case-cover tails or infer physical UNSAT:** relabelling supplies neither the missing incidences nor a whole-parent bridge. Frozen-unit SAT/UNSAT alone does not speak about physical colourings.
- **Adding MCF or trying every profile:** explicitly outside this pilot. A changed suffix requires a new stabilizer and outside-dependence audit.

## Reproduction of the bounded checks actually run

From `.ultramath/smx04thj8/m2/` at the reviewed repository HEAD:

```bash
../../../.scratch/k58/.venv/bin/python symmetry_fit.py --full-cnf > symmetry_fit.json
../../../.scratch/k58/.venv/bin/python counter_specs.py > counter_specs.json
```

The first regenerates the exact parent and cube, applies every transposition to fixed units and the cube, tests full-CNF aux-fixed clause invariance, and records parent hashes and the first failure. Runtime was about 14 s, with no SAT solver. The second intercepts the existing recipe's `CardEnc.atleast` and support calls, records exact abstract counter inputs/bounds, and applies all 51 transpositions. It completed in under one second and reports `counter_calls=33`, `sender_counter_calls=31`, `support_calls=15`, `final_selector_counter_calls=2`, `passed=51`.

No SMS, CaDiCaL, Kissat or Glucose solve was run; no external binary/package was installed; no wall sweep, K51 campaign, profile campaign, MCT run, global lex/MCF experiment or long rejected computation was repeated. Public source clones under `sources/` are inspection inputs only. No repository production file, receipt root or other member's file was modified.

## Bottom line

The useful new information is not “dynamic symmetry might help” but a sharp fit gate: **a sizeable, exact restricted group exists on the retained parent, the support/candidate event semantics survive, and the emitted CNF's auxiliary layer breaks naive syntactic symmetry**. Spend one bounded experiment on restricted one-colour SMS/export if and only if all witness checks are kept. If generation or the matched A/B is unproductive, close this direction locally. The only continuing work would then be the independent $H$-orbit certification theorem; neither path addresses `ChainReady` or changes any Ramsey bound.
