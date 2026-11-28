# R(3,3,3,3): combinatorial-CSP next-step memo (member m8)

**Direction:** graph-colouring CSP encodings/enumeration and recoverable projections. Repository inspected at `211dd0b2b705efef7481d5cace379fea99a2a0ca` (exact requested HEAD). Web/API checks below were made on 2026-11-28. This memo proposes two bounded tests and otherwise records negative results. It asserts no wall, profile, or Ramsey closure.

## 0. Frozen status and actual object

Accepted bounds remain $51\le R_4(3)\le62$ (Chung 1973; Fettes–Kramer–Radziszowski 2004; DS1 rev.18, 24 Apr 2026). The frozen K58 cover has 113,179 cases. Its 11-profile, 11,585-case tail/wall and physical whole-parent bridge are not closed.

Current primary metadata gives **Milos Tatarevic**, *An upper bound of 60 for the Ramsey number $R(3,3,3,3)$*, arXiv:2610.36648v2, submitted 27 Oct 2026 and revised 6 Nov 2026. The abstract says global incidence counts, classifications, exhaustive SAT, Lean, and two SAT solvers. It is still a **claimed** $R_4(3)\le60$, not established here: there is no independent DRAT/LRAT check of its 296,081 formulas in this repository. The current upstream README reports the same count and the theorem's external `AllUnsat` premise. `<https://arxiv.org/abs/2610.36648>`, `<https://github.com/milostatarevic/r3333-upper-bound>`, commit `6c3f2fd0386335321801fa4079397d4a4c1962f3`.

The old local `M. Stojanović` attribution is not supported by current primary records: arXiv's Atom API and abstract page, GitHub's user record (`name: Milos Tatarevic`), repository owner, and latest commit author all say Milos Tatarevic / `milostatarevic`. Correct the stale note; do not make an identity claim beyond those records. zbMATH record `903229195` could not be rechecked because zbMATH returned a Cloudflare human check; automated access was stopped, not worked around.

The retained ordinary parent has SHA-256 `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae`, recipe `tables=True,total_critical=True,full_root=False`: host clauses + 438 unique frozen units + **31** guarded sender counters + **15** support events (112 selectors each) + two final bound-6 counters. It is a relaxation of the physical row. The Lean `PhysicalBridge` closes only base/unit assembly conditional on expanded-row realization; `ChainReady`, candidate criticality/degree/sender equality, exact 112-support membership and floor selection remain. SAT/timeout on frozen units or a projection says nothing physical.

## 1. Prioritized candidates

### Priority 1 — (c) certificate/proof engineering: one exact support-normal-form lemma, then its 15 uniform instances

**Source and relevant existing code.** `tools/color-resolved-wallcc/frozen/support_tables.py::allowed_supports` excludes marked colour, tests degree sequences on four/five points and emits P4/C5 sets. `results/ams-wall-2026-11-28/semantic-map/support-catalogue.json` is the exact 112-set ($96P4+16C5$) catalogue for target `arm0=16,T`, marked colour 1, palette `[2,3]`, with P4/C5 tested in colour 2. `lean/K58/Support.lean` already has `SupportShape` and `pinned_support_shape`; it does **not** by itself prove membership in the coded 112-set. `lean/K58/SemanticAssembly.lean::emittedSupportStep` makes that missing membership an explicit `ready` premise.

**Proposed theorem template.** For every physical realization of the retained case and every $x\in\{18,\ldots,32\}$ for which the selected guard is true, prove that the colour-1 neighbourhood of $x$ in arm 0 is exactly one member of the emitted 112-list. The proof must expose all used premises:
1. criticality supplies degree at least 15, hence at least 14 off-root neighbours in the other three arms;
2. each such support has at most five vertices, so the named target support has size four or five;
3. its internal marked/root colours are forbidden;
4. **the candidate's own critical-link classification and support placement** gives the P4/C5 exclusion needed to recover the exact coded set, not just an abstract shape.

Point 4 is load-bearing. A Ramsey-only two-colour $K_4$ argument is insufficient: `C4 + 2K2` is triangle-free in both colours but is exactly the excluded support shape (the campaign review's 1,344 omitted local supports). The existing `template_support_shape` should be used only where its root/neighbourhood hypotheses actually match; it must not be quoted as already proving target membership.

**Minimal test (no SAT budget).** In a new isolated Lean file, first produce a `by decide` equivalence between the executable catalogue-building predicate and the exact 112-member list, with reject witnesses for `C4 + 2K2`, wrong size, and wrong colour. Then instantiate the physical theorem for sender 18, printing axioms. Only after that compiles, abstract it over senders 18–32 and use it in the corresponding `emittedSupportStep.ready`. Cross-check the generated sets against `support-catalogue.json` and the current parent hash. Keep this a new proof file, not a changed production bridge.

**Information/implementation/abandonment.** Cost is near-zero solver CPU and moderate focused Lean work; expected information is high because either one recurring `ChainReady` premise is discharged or a missing semantic premise is exposed. Abandon this lemma route if the proof needs an unjustified universal P4/C5 assertion or if its generated catalogue differs from the 112 sets. A successful lemma discharges only support readiness for this row: it does not prove criticality, floor selection, `ChainReady`, or any wall closure.

### Priority 2 — (b) solver-throughput only: lazy generalized-arc-consistency for the 15 support relations

**Primary sources.**
- K. Fazekas, A. Niemetz, M. Preiner, M. Kirchweger, S. Szeider, A. Biere, *IPASIR-UP: User Propagators for CDCL*, SAT 2023, pp. 8:1–8:13, DOI `10.4230/LIPIcs.SAT.2023.8`, §§2.1–2.4, 5. The API observes/freeze-marks variables, supports delayed reasons and external additions; external clauses use observed variables and are recorded as irredundant original input, with proof support described as experimental.
- Official CaDiCaL 2.1.2 source, tag `3ff42f04384489916f017acd6d5e7cbfa7257be7`, `src/cadical.hpp` (`ExternalPropagator`): external clauses are expected over observed/frozen variables and added to incremental proofs in real time. `<https://github.com/arminbiere/cadical/blob/3ff42f04384489916f017acd6d5e7cbfa7257be7/src/cadical.hpp>`.
- Z. Li, C. Duggan, C. Bright, V. Ganesh, *Verified Certificates via SAT and Computer Algebra Systems for the Ramsey $R(3,8)$ and $R(3,9)$ Problems*, IJCAI 2025, DOI `10.24963/ijcai.2025/292`; arXiv:2502.06055v2 §5 and §8.4. Their orderly-generation CAS supplies permutation witnesses for trusted clauses, which a separate script checks. It does not show that arbitrary callbacks are DRAT consequences or provide the missing formal encoding proof.

**Fit.** Start from a *variant* without the 26,895 support-table clauses/1,680 selectors, never from an assumed-valid shortcut of production. For one guard $g$ and its 16 physical colour-1 spokes $x_0,\ldots,x_{15}$, maintain the currently forced `must` and `cannot` sets. If no one of the 112 supports contains `must` and avoids `cannot`, return the explanation
$$\neg g\;\lor\;\bigvee_{j\in\mathrm{must}}\neg x_j\;\lor\;\bigvee_{j\in\mathrm{cannot}}x_j.$$
This is generalized arc consistency of the same finite relation, not maximal-clique-free normalization, graph automorphism/SMS, or another transversal bank. Observe only these 240 spoke variables and 15 guards; no eliminated/unobserved variable may enter an explanation.

**Measured risks.** The current PySAT CaDiCaL-1.9.5 interface does not expose this propagator; a native IPASIR-UP driver is new implementation, not a flag. Every explanation is valid by catalogue enumeration, but **logical consequence is not RUP**. CaDiCaL's trusted external-input lines and self-written hashes are not acceptable final evidence. A proof needs an independent derivation for every emitted explanation (and exact backtracking/reason semantics), followed by replay against the support-free original and the derivation prefix. Preprocessing of unobserved auxiliaries can also change the search substantially.

**Minimal reproducible test.** (i) Exhaustively compare the lazy predicate with the eager relation on all $2^{16}$ support words for one guard, including partial must/cannot pruning and four rejecting controls. (ii) Emit an independent derivation for the first two nontrivial conflict explanations; if only SAT/OPEN or no valid derivation exists within the bounded pre declared cap, stop. (iii) On one small *completed historical control* (not the hard retained leaf), compare eager baseline with fresh proof-enabled lazy run at equal conflict cap, including preprocessing, callback time and external-derivation/checking time. Reject any SAT model unless all 112-support relations hold on the original physical projection. If this reaches a matched ordinary-parent comparison, cap total solver CPU at 30 minutes and run only one seed/budget pair.

**Abandon if** external clauses cannot be independently derived, if any callback misses a physical model, or if end-to-end CPU is no better than the eager baseline. Never report an OPEN run, number of callback conflicts, or removal of eager clauses as evidence of a faster or closed wall.

## 2. (a) New mathematical closure possibility: none survives the inspected local tests

The proposed two-sender/shared-support cut was cheap enough to execute rather than speculate about. For senders 18 and 19, build the induced physical host/frozen-unit CNF on $\{0,18,19\}\cup\{1,\ldots,16\}$ (5,212 clauses), leaving out all other arms, counters, cubes and final floors. Enumerate every one of the exact $112^2=12,544$ support pairs.

**Result:** all 12,544 were locally SAT in 1.943 CPU-s (0 conflicts). Pinning all 16 colour-1 spokes was UNSAT, a rejecting control that shows the formula was not vacuous. This rejects only that raw two-sender local cut; it is not evidence of global satisfiability and does not justify sweeping the other 104 sender pairs without a new mechanism.

Reproduce with explicit roots:

```sh
R=/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo
cd "$R/.ultramath/smx04thj8/m8"
"$R/.scratch/k58/.venv/bin/python" pair_support_check.py
# parent SHA-256 is asserted in the script; result: pair_support_check.json
```

The broader three-arm per-sender joint test is also not a new opening: `results/arm-class-2026-11-24/README.md` reports exactly 600 completions at every one of 30 template roots, hence zero pruning beyond separate support conditions. Any new joint condition must involve shared cross-edges, not a renamed $(4,5,5)$ profile constraint.

## 3. Sources read and precise no-go/transfer decisions

### Degree matrices and first-star embedding — no new proof route

M. Codish, M. Frank, A. Itzhakov, A. Miller, *Solving Graph Coloring Problems with Abstraction and Symmetry*, arXiv:1409.5189v2–v3 (latest v3, 26 Mar 2015), especially §3 and §4 Definitions 3–5. The abstraction is the $n\times k$ matrix of per-vertex colour degrees; a (possibly over-approximated) set of matrices is refined into concrete searches, optionally after embedding the smaller colour-neighbourhoods of one vertex. The source itself leaves $R(4,3,3)=30$ as a conjecture. It does not offer a semantic recovery theorem for a frozen four-colour guarded suffix. Here the star/template embedding is already present, and degree/profile-only abstractions manufacture SAT models. **No-go:** another degree-matrix/profile partitioning pass merely discards the 31 guards, 15 support relations and final floors.

### Canonizing sets / interchangeable matrices — not invariant under this parent

A. Itzhakov, M. Codish, *Breaking Symmetries in Graph Search with Canonizing Sets*, arXiv:1511.08205v2, 4 Feb 2016, Definitions 1–3, Lemma 1, Algorithms 1–2, §5. A complete break is canonizing only relative to a stated graph predicate; Algorithm 1 repeatedly searches for a smaller permutation in that predicate's solution set. Instance-independent examples are at most 10 vertices; instance-dependent computation remains potentially expensive. Fully interchangeable matrix symmetry additionally requires row/column actions to preserve the whole predicate. Ordinary frozen units and cubes invalidate general vertex actions. The preferred-pair cover works only because its unnamed-arm stabilizer was proved to preserve counter semantics and because the arm produces no support-table events; that proof is not reusable for arbitrary rows/cells. **No-go:** do not feed the raw 19,533-variable parent or an under-cube frontier to these algorithms.

M. Codish, M. Janota, *Breaking Symmetries with Involutions*, CP 2025, DOI `10.4230/LIPIcs.CP.2025.8`, §§1 and 5. Its graph patterns cover noncanonical simple graphs, with CEGAR experiments for $R(4,4;n)$ and $R(3,6;n)$ up to $n=18$ (and complete-break computations on small orders). It gives no four-colour auxiliary-suffix invariance theorem and no large-UNSAT speed guarantee. **No-go here:** do not transfer the published coverage percentages into a static constraint on this parent. Any local residual-group experiment belongs to the separate dynamic-symmetry review and needs explicit stabilizer witnesses.

### Orderly graph generation — its principal symmetry premise is missing

Li–Duggan–Bright–Ganesh (source above), §5, uses lex-least adjacency matrices and the hereditary fact that a canonical matrix's upper-left parent is canonical. Its certificate checker applies the supplied witness permutation to each trusted CAS clause; it does not make those clauses ordinary DRAT additions. Root/frozen-unit/cube stabilizers here do not supply the global vertex-permutation group or the required canonical-parent property for the whole guarded formula. **No-go as a K58 enumeration method.** This is distinct from the narrow non-symmetry support propagator above.

### Paired-arm transversals and joint-support clauses — already measured, not new

The local campaign already enumerates all inclusion-minimal pair transversals: 462,094 clauses on historical rank 1300, filtered to 3,961 new short clauses. Its accepted report gives gains on that row but a rank-1200 regression of +20.59% conflicts and +50.90% CPU. The direct joint-support bank needed 458.97 CPU-s cold discovery plus 23.02 CPU-s rechecking, exceeding its measured search saving. The `two5` selector relation already captures “at least two 5-support arms.” **No-go:** do not resell these as unused CSP methods or run the full transversal product on a hard wall. A proposed triple relation adds nothing merely by saying $(4,5,5)$ again.

## 4. Bottom line

1. Do the exact support-normal-form lemma first (category c); it addresses a named bridge obligation at zero solver cost and has a crisp failure detector.
2. Only if a native IPASIR-UP experiment is genuinely affordable, gate the lazy support propagator on independent explanation derivations before any timing claim (category b).
3. No new mathematical closure method survived this direction. The bounded shared-support test is negative; degree matrices, global canonization, exact transversal re-encoding and orderly graph generation either discard required suffix semantics or have already been measured adversely here.
