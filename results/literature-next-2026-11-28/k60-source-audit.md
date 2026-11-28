# K60 source/Lean audit and prioritized K58 next steps

**Scope:** literature and experiment design only. Repository inspected at HEAD `211dd0b2b705efef7481d5cace379fea99a2a0ca`. The accepted interval remains **51 ≤ R₄(3) ≤ 62**. Nothing below establishes `R₄(3) ≤ 60`, `R₄(3) ≤ 58`, a wall-row closure, or a physical-colouring exclusion. No solver was run and no external package was installed for this review.

## Executive recommendation

| priority | proposal and category | why it is worth a small next step | first falsification/abandonment test |
|---|---|---|---|
| **1** | **Port K60's exact P4/C5 guard-pattern transport into the 15 K58 support-readiness proofs. (c) certificate/physical-semantics engineering; no new mathematical closure by itself.** | It addresses a named open obligation directly rather than changing the CNF. The required K60 finite completeness lemmas and the K58 physical support-shape lemma already exist separately, and their T16 catalogues are ordered-identical here. | If the root/sender `PinnedArm` coordinates cannot be related with marked colour 1 excluded and path/cycle colour 2, stop; do not alter the catalogue to make the theorem fit. Success still leaves criticality, adjusted guard totals and final `ChainReady` open. |
| **2** | **Only after producing a new global branch proof, test a K58 analogue of K60's 32-owner all-five compatibility formulas. (a) potential mathematical branch closure; (b) solver only after (a) and exact input semantics are complete.** | This is the genuinely structural mechanism not present in the K58 parent: 32 simultaneous visible-neighbourhood embeddings, rather than degree counts or independent local guards. Three K60 formulas are small enough for a bounded, independently checked experiment after regeneration. | The K60 soundness theorem requires normalized root/templates, high degrees for embeddings, and `AllOwnSixteen`. If the K58 reduction cannot derive and cover that global hypothesis, there is no K58 wall improvement to test. Do not import K60 UNSAT results or treat `w(r) ≤ H(r)` as supplying it. |
| — | Reuse the four K60 C2 compatibility formulas, their 130k-variable degree-counter architecture, or their K60 UNSAT conclusions directly. | **No-go.** Their canonical root has 15+16 critical cells, whereas the retained K58 root has 16+16; their host is K60, not K58. | Any proposed reused clause/proof must first map the K60 host onto K58. No such automatic map exists in the sources read. |

The first recommendation is unusually concrete: K58's existing readiness premise is

```lean
v g = true → ∃ i, ∀ j < n, v (x j) = allowed i j
```

for the exact emitted support gadget (`lean/K58/SemanticAssembly.lean`). K60 proves the corresponding physical catalogue-membership theorem, rather than merely an auxiliary extension theorem. That is the reusable part.

## 1. Current primary metadata and verification status

### 1.1 arXiv and author records

* **Milos Tatarevic**, *An upper bound of 60 for the Ramsey number R(3,3,3,3)*, arXiv:2610.36648v2 [math.CO], revised 6 November 2026; 15 pages, 3 figures. Primary records: [abstract/version history](https://arxiv.org/abs/2610.36648), [v2 PDF](https://arxiv.org/pdf/2610.36648). v1 was submitted 27 October 2026 and claimed 61; [v1 metadata](https://arxiv.org/abs/2610.36648v1). The PDF read here has SHA-256 `1e8d390eddcda7a8208353c374c2e4b969f8264ba2a55bf0737acc13bf54fe70`.
* Both arXiv versions name **Milos Tatarevic**. The current [GitHub user API record](https://api.github.com/users/milostatarevic) also gives `name: Milos Tatarevic`, and the repository HEAD commit has author `Milos Tatarevic <milos.tatarevic@gmail.com>`. Thus the old local `M. Stojanović` attribution is unsupported by these primary records and should be corrected for this citation. This statement is about the bibliographic records checked, not about anyone's legal identity.
* The preprint claims 296,081 UNSAT results from each of two solvers. It does not turn the claim into an accepted bound here. No independent DRAT/LRAT replay of its large formula set was performed for this review.

### 1.2 Upstream revision actually inspected

Official repository: [milostatarevic/r3333-upper-bound](https://github.com/milostatarevic/r3333-upper-bound), HEAD/commit inspected:

```text
6c3f2fd0386335321801fa4079397d4a4c1962f3  Update README.md
2026-11-09T11:03:21-08:00
author Milos Tatarevic <milos.tatarevic@gmail.com>
```

Use the [commit permalink](https://github.com/milostatarevic/r3333-upper-bound/tree/6c3f2fd0386335321801fa4079397d4a4c1962f3). The release index says `status: READY_FOR_HUMAN_REVIEW`, `selected_formulas: 296081`, `kissat_complete: true`, `cadical_complete: true`, but also explicitly says that large UNSAT refutations are not replayed in Lean ([release index](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/publication/checks/K60_RELEASE.json)).

The formal package pins Lean **4.32.1**, whereas the local toolchain is 4.33.1 and `elan` is not on PATH. I therefore did not claim a local upstream compilation and did not download a toolchain or Mathlib cache. The upstream [build guide](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/formal/BUILD.md) itself distinguishes a conditional mathematical build from native SAT evidence. I inspected public source and release metadata, not the large native logs/proofs; the evidence archives were not pulled or replayed.

### 1.3 Exact theorem boundary

The final theorem is [`UniformK60.ramsey60_of_exact_unsat`](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/formal/src/UniformK60/FiniteBoundary.lean), with premise `ExactInputs.AllUnsat`. [`ExactInputs.lean`](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/formal/src/UniformK60/ExactInputs.lean) defines this as unsatisfiability of all formulas in an explicit finite sum type. It is not an axiom-free proof of UNSAT. Section 6 of the paper says the mathematical reductions and classification certificates are checked in Lean, while the SAT exclusions are checked by two solver runs and exact-input comparisons.

**Section-number correction:** in current v2, guards and visible opposite neighbourhoods are in **§5.2**, anchored tables in **§5.3**, compatibility formulas in **§5.4**, verification in **§6**, and **§7 is “Data and AI assistance”**, not the guard section.

## 2. What the K60 source actually proves

### 2.1 Exact guard membership, not just P4/C5 existence

For each owner/center, `guardSet` is the actual set of other-cell vertices joined in the owner's own colour. K60's [`BalancedHostGuard.lean`](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/formal/src/UniformK60/BalancedHostGuard.lean) has the theorem

```lean
actual_guard_pattern :
  ∃ i : BalancedAnchor.PatternIndex (guardMinor s) (otherKind o s),
    BalancedAnchor.pattern ... i = castSet c s
```

Its hypotheses are triangle-freeness and a normalized host/root/template layout. The proof uses the **actual critical neighbourhood of the center**. In the four-element case it obtains a physical ordered P4 and transports its six edge relations into the other root template. This is much stronger than observing that some arbitrary independent four-set exists.

[`BalancedAnchorSupport.lean`](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/formal/src/UniformK60/BalancedAnchorSupport.lean) supplies kernel-checked finite completeness statements:

```lean
p4_complete : ∀ ... valid positions and explicit P4 edge relations ...,
  ∃ i, pattern minor kind i = {a,b,d,e}

c5_complete : ∀ s, s.card = 5 → Independent kind s →
  (∀ v ∈ s, validPosition minor v) → ∃ i, pattern minor kind i = s
```

The same file proves the catalogue counts, in (full U, full T, minor U, minor T) order: **96, 112, 71, 83**. The arrays explicitly store the masks, so a port can be checked rather than accepted by name.

K58 already has `template_support_shape` and `pinned_support_shape` in [`lean/K58/Support.lean`](../../../lean/K58/Support.lean). These prove physical P4/C5 shape for an attaching support, but HEAD contains no use of `pinned_support_shape` beyond its definition and no transport to `targetSupports`. K60's extra contribution is precisely the named-coordinate, exact-list completeness argument.

### 2.2 Simultaneous visible-neighbourhood embeddings

K60's second mechanism is different from the P4/C5 selector alone:

* §5.2 defines visible opposite neighbourhoods on `X ∪ Y`. Each relevant opposite neighbourhood has order 15 or 16 and therefore a classified U/T embedding. The guard count 4 or 5 uses only the own-colour degree and the at-most-five capacity of the other root cells.
* §5.3's Computation 5.6 enumerates 320 ordered anchors, two templates × 16 supports × ten anchor orders. Six anchored tables cover them. Proposition 5.7 is an if-and-only-if statement for colour-preserving embeddings with an ordered anchor.
* [`BalancedVisible.actual_chart`](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/formal/src/UniformK60/BalancedVisible.lean) starts with the actual critical neighbourhood, invokes fixed-palette classification, and composes the chart with an anchor-coverage bijection. `chart_local_witness` assigns roles only to observed physical members; unused reference positions are not fictitious host vertices.
* [`BalancedEncodingDefs.lean`](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/formal/src/UniformK60/BalancedEncodingDefs.lean) encodes one-of-six state selection, optional member roles, role injectivity, anchor colours and member-member colours. The constraints share physical edge variables across owners.
* [`BalancedEncodingSoundness.normalized_satisfiable`](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/formal/src/UniformK60/BalancedEncodingSoundness.lean) constructs **all** degree, guard and embedding auxiliary assignments after one host normalization, proving physical variables remain equal to the given colouring.

This simultaneous construction matters. Independent per-neighbourhood encodings with freshly invented physical vertices would not establish compatibility on overlaps and would not be a valid port.

### 2.3 All-five is a special theorem with strong hypotheses

[`BalancedEncodingAllFiveSoundness.normalized_satisfiable`](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/formal/src/UniformK60/BalancedEncodingAllFiveSoundness.lean) takes:

```lean
(hc : NoMonochromaticTriangle c)
(hn : Normalized true c o)
(hall : AllOwnSixteen c)
```

`AllOwnSixteen` means every vertex has colour degree 16 in **both** named colours. [`BalancedHostAllFive.lean`](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/formal/src/UniformK60/BalancedHostAllFive.lean) proves that this alone makes each relevant guard have five elements. It is not inferred from catalogue shape, and the K60 derivation of that situation comes from the separate perfect-balance/common-critical-pair argument.

The three all-five formulas have no global degree-counter block. They contain K60 base/root/template clauses, 32 guard gadgets, 32 embedding gadgets, and negative units prohibiting every four-element guard. Their public input dimensions are:

| owner | variables | clauses |
|---|---:|---:|
| UU | 15,976 | 696,929 |
| UT | 16,232 | 727,777 |
| TT | 16,488 | 758,625 |

Dimensions are from the [readiness result](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/publication/checks/readiness/RESULT.json). The upstream [cost report](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/publication/MEASURED_COSTS.md) reports 0.03 successful-run CPU hours for each solver over all three formulas combined, on an Apple M4 Max. This is not a timing prediction for the VM or for any K58 formula.

## 3. Exact fit with the retained K58 parent

The target remains row `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`, profile `(16,16,14,11)`, arm 1, charge 7, root kinds `T,U,-,-`, marked template `15,T`, with ordinary parent hash `90d06e...` and recipe `tables=True,total_critical=True,full_root=False`.

The local semantic inventory establishes:

* 31 guarded native counters for vertices 1–16 (arm 0) and 18–32 (arm 1), plus automatic sender vertex 17;
* 15 support events after the arm-1 counters, each targeting arm 0/T16;
* all 112 selectors and all 16 positions active in every event, hence `112×16+1=1,793` clauses per event;
* final adjusted counters 6-of-15 and 6-of-31 after the automatic sender.

A guarded counter's true branch supplies at least 14 same-colour neighbours outside the sender's root arm. Adding the root gives degree at least 15. A physical degree cap then gives order 15 or 16 and a critical template for the sender. This forward direction is required before the K60 support theorem can be used; the SAT counter alone does not supply it.

### Bounded non-solving catalogue check

I compared the actual source-generated lists, without invoking a solver. Reproduction files are [`check_catalogues.py`](check_catalogues.py) and [`catalogue-check.json`](catalogue-check.json).

```sh
python3 check_catalogues.py > catalogue-check.out
```

Results:

```text
K58 TargetSuffix.targetSupports
  == allowed_supports(16, "T", target_arm=0, marked_color=1)
  == K60 BalancedAnchor.supportMasks[full][T]
  (ordered equality in both cases)

96 four-element patterns + 16 five-element patterns = 112.
```

For each U/T and full/minor family, four `(arm, marked)` palettes have exactly K60's ordered colour-2 masks. The other eight palettes produce different sets and require an explicit colour-transport argument. The retained `(arm 0, marked colour 1)` palette is one of the exact matches. This negative palette control is important: a generic “P4/C5 in either remaining colour” theorem does **not** prove membership in the emitted list.

No conclusion about physical guard-set equality, parent UNSAT, or ChainReady follows from this byte/catalogue check.

## 4. Priority 1 — discharge the 15 exact support-membership obligations

**Category: (c), certificate and physical-semantic engineering only.** This changes no CNF and suggests no solver-throughput experiment.

### Theorem template

For a marked-arm sender `x = 18`, first write the target statement in normalized physical coordinates; then repeat uniformly through `x = 32`.

> Assume a good physical colouring realizes the target's common vertex and colour permutations. Let `r` be its root, suppose `x` is a true guarded sender in root arm 1, and let the root's arm-0 vertices be enumerated by its named T16 coordinates. Let
> $$S_x = \{j<16: G(x,y_j)=1\}.$$
> Then there is an index `i < targetSupports.length` whose listed set equals `S_x`.

A proof should expose the following hypotheses rather than hide them in a Boolean guard:

1. `TriangleFree G`;
2. `x ∈ arm G r 1` and `r ∈ arm G x 1`;
3. `15 ≤ deg G x 1` (from the guard candidate count plus root edge) and `deg G x 1 ≤ 16`;
4. a sender template `PinnedArm G x 1 n t`, with `n=15∨n=16`, obtained by `critical_arm_pinned`;
5. the normalized root template `PinnedArm G r 0 16 true` and its exact correspondence with the frozen coordinate labels.

Now apply `pinned_support_shape` in the **colour-1 sender neighbourhood**. In the local palette used by that theorem, choose root-arm selector `b=0` and path selector `c=1`; for own colour 1 these denote physical root arm 0 and physical path colour 2. The b≠c side condition holds.

The remaining steps are the K60 transport, not another enumeration:

* use the P4 or C5 physical support shape;
* use the root T16 chart to read its coordinates;
* internal marked-colour-1 edges are impossible because both support vertices are already colour-1 neighbours of `x` (triangle-freeness);
* for P4, port K60's `guard_path_pattern` argument with its six physical edge relations, then `p4_complete`;
* for C5, use independence from marked colour 1, exact cardinality and valid positions, then `c5_complete`;
* identify the resulting K60 full-T mask with `targetSupports` using the ordered equality above.

This closes only the `ready` premise of each `emittedSupportStep`. It does not prove that all 31 true guards represent `Sends`, that vertex 17 plus the coded guard sets exhaust the physical sender sets, or the two final floor-counter premises. It therefore does not discharge whole `ChainReady` by itself.

### Minimal implementation and controls

1. Write one generic K58 lemma with the five explicit hypotheses above. Compile it with the repository's existing Lean environment and print axioms. Do not import the K60 package globally: port the two small finite lemmas/proof pattern into the K58 namespace and preserve the pinned source revision in the comment.
2. Instantiate guard 11965/vertex 18 first. Verify the `x j`, `allowed`, and all-true active mask against `lean/K58/TargetSuffix.lean`. The desired conclusion is exactly its `ready` proposition, not a new semantic predicate.
3. Reuse the same construction for the other 14 events. Only then instantiate the support part of `ChainReady`; leave all remaining premises visibly unsolved.
4. Include rejecting controls: U instead of T; path colour 3 instead of 2; a changed mask bit; and one nonmatching palette. A theorem that accepts these as the same emitted catalogue is not testing the required statement.

**CPU budget:** no SAT calls; only Lean elaboration/kernel checks. **Implementation cost:** moderate and local (one generic physical transport + instantiations), non-destructive to the frozen parent. **Abandon if:** the common physical realization does not provide both required `PinnedArm` structures at the same coordinates, or if exact colour-2 transport cannot be established. Do not “repair” this by broadening the support list or calling candidate lists physical degrees without proof.

## 5. Priority 2 — a separate all-five compatibility branch, not a parent patch

**Category: (a) possible new mathematical branch closure; (b) solver only after its branch and semantics are proved.** This is lower priority because the principal missing item is global mathematics, not encoding or CPU.

### What would have to be proved

Find a K58 reduction branch with two palette colours 0,1 such that, for **every** vertex `v`,

$$d_0(v)=d_1(v)=16,$$

together with a complete normalization of roots into UU, UT, TT (using colour exchange to remove TU). At such a root with 16+16 critical cells:

* both opposite neighbourhoods are critical at each of the 32 owners;
* own degree 16 forces every cross guard to have five elements, using the same at-most-five capacities as K60;
* the six-table library supplies all visible embeddings simultaneously;
* a K58 host analogue of `normalized_satisfiable` produces a satisfying assignment of the corresponding all-five formula.

An independently checked UNSAT result for all three K58 formulas would exclude precisely this branch. It would say nothing about vertices outside it until the branch-generating theorem is supplied.

The arithmetic `(16,16,14,11)` is compatible with `16+16+14+11=57`, so this is not immediately ruled out by a degree sum. That is not evidence that the existing K58 ticket reduction reaches the branch. K60 reaches its common pair through perfect balance, reciprocity, internal connectivity and a global critical-neighbourhood argument with K60-specific numerical assumptions. Those assumptions cannot be silently transplanted to K58 or to a single `w(r)≤H(r)` wall root.

The current K58 structural record locates this hypothetical branch more precisely. `paper/main.tex`, “Reciprocal profiles at 58,” says a reciprocal good colouring has one **sole** common critical colour and sorted profile `(15,14,14,14)` or `(16,14,14,13)`. Consequently an `AllOwnSixteen` colouring, having two critical colours everywhere, must be nonreciprocal. That result does not exclude the nonreciprocal branch. Its “Ticket gap” corollary rules out only certain small numbers of unreciprocated tickets (at least 15 if two colours are critical somewhere, and at least 30 under global incoming/outgoing equality), not 16-versus-15 high-degree equality. The required new branch proof therefore belongs in the nonreciprocal analysis, not in a rerun of the already-proved reciprocal profile restriction.

### Minimal go/no-go test before any solver run

1. State the global branch lemma in K58 terms and attempt to derive it from the actual existing global hypotheses. If the only way to state it is as a fresh assumption, keep this out of the wall campaign. In that case stop here: generating seven-hundred-thousand-clause formulas tests no relevant implication.
2. If a complete branch is available, generate only UU first on the K58 host (6,612 physical variables and 134,995 base clauses). Bind the exact formula bytes and separately prove the physical-to-CNF assignment theorem. Do not reuse the K60 CNF hash or verdict.
3. Compare its root/template unit prefix with the retained target's normalized coordinates. Append frozen units or `[-1413,1014]` only after proving those literals hold throughout the intended branch. A conflict with a pinned literal is a mapping failure, not a wall closure.
4. With all semantics complete, run one bounded UU solve, capped well below five minutes for a first measurement, with DRAT retained and independently replayed on the exact regenerated query. If the solver returns SAT, use the model to falsify the intended mathematical exclusion. OPEN is only OPEN. Do not run UT/TT unless UU passes certificate and cost controls.

The source's 697k–759k-clause sizes and its M4 Max cost data make an initially bounded experiment plausible, not a promise of improvement over the 184,335-clause K58 parent. The four C2 compatibility formulas (roughly 800k clauses and 130k variables each) are not the appropriate first experiment here.

**Abandon if:** no exhaustive K58 branch proof exists; unit/template normalization does not align; the regeneration requires inventing unobserved host vertices; or a correctly bound model exposes a false semantic premise. Do not classify failed search as evidence for the branch exclusion.

## 6. Explicit no-go and named-limit items

* **No direct K60 theorem/proof reuse.** K60 has 7,080 physical edge-colour variables and 149,270 base clauses on 60 vertices; K58 has 6,612 and 134,995 on 58. K60's final `AllUnsat` premise and its 296,081 logs cannot be renamed into a K58 DRAT certificate.
* **No “either colour” support shortcut.** The retained support catalogue is colour-2 P4/C5 with internal marked colour 1 excluded. This was verified in both generator and Lean source and is also stated in the existing K58 semantic audit.
* **No independent visible-neighbourhood completion vertices.** K60's `LocalWitness` assigns roles only to actual observed members. Inventing missing physical vertices breaks exact outside-dependence and shared-edge semantics.
* **No claim that K60's simultaneous-extension theorem replaces K58 `ChainReady`.** K58 already has a general sequential extension theorem and exact fresh allocations. Its hard part is physical readiness. Port the support-membership lemma, not the whole architecture.
* **No claim from support transport to final floor counts.** Candidate criticality, exact `Sends`, automatic vertex 17, selected/total coded-set equalities and final `ChainReady` are separate obligations.
* **No promotion of upstream dual-solver evidence.** Two UNSAT exits and hash-identical inputs are not independent DRAT/LRAT replay. The upstream 55 small K15/K16 classification CNF/LRAT pairs have a different, narrower verification scope from the 296,081 large exclusions.
* **No local upstream build claim.** Only source inspection, primary metadata retrieval and non-solving list comparisons were performed here. The upstream pinned Lean version was not installed, the large native archives were not fetched or checked, and no wall sweep was run.

## 7. Sources consulted

Primary upstream sources read directly:

1. Milos Tatarevic, [arXiv abstract/version metadata](https://arxiv.org/abs/2610.36648) and [v2 paper](https://arxiv.org/pdf/2610.36648): §§1, 2, 5.1–5.4, 6–7; especially Lemma 5.5, Computation 5.6, Proposition 5.7, Lemma 5.8, Computations 5.9–5.11.
2. Official repository at commit `6c3f2fd...`: `RESEARCH.md`; `formal/BUILD.md`; and the source modules linked above, including `BalancedHostGuard`, `BalancedAnchorSupport`, `BalancedVisible`, `BalancedEncodingDefs`, `BalancedEncodingSoundness`, `BalancedEncodingAllFiveSoundness`, `BalancedHostAllFive`, `ExactInputs`, and `FiniteBoundary`.
3. Official release/readiness/cost records linked above for exact formula counts, dimensions, reported solver scope and costs. These substantiate what the upstream evidence claims, not an independent verification here.
4. [GitHub repository](https://github.com/milostatarevic/r3333-upper-bound), [HEAD commit API](https://api.github.com/repos/milostatarevic/r3333-upper-bound/commits/6c3f2fd0386335321801fa4079397d4a4c1962f3), and [user API](https://api.github.com/users/milostatarevic) for revision and author metadata.

Local sources read before and during the fit analysis:

* `results/literature_status.md`;
* `results/literature-r3333-2026-11-23.md`;
* `review/DUGGAN_PAPER_ASSESSMENT.md`;
* `results/ams-wall-2026-11-28/arm3/retained-leaf/REPORT.md`;
* `tools/color-resolved-wallcc/NATIVE.md`;
* `lean/K58/{Support,SemanticAssembly,TargetSuffix,TargetParent,PhysicalBridge,TicketPremises,Basic,Marking,ArmPinned}.lean`;
* `tools/color-resolved-wallcc/frozen/{support_tables,dense}.py`;
* `results/ams-wall-2026-11-28/semantic-assembly/SEMANTIC_ASSEMBLY.md`;
* `results/ams-wall-2026-11-28/SEMANTIC_READINESS.md`;
* `research/ams-wall-followup/checks/5-proof.md`;
* `paper/main.tex`, “Consequences for reciprocal colourings,” and `paper/lean/ReciprocityBoundary.lean`, to separate the reciprocal profiles already excluded from the nonreciprocal all-five hypothesis.

The K58 semantic assembly source already identifies the missing support transport explicitly; this memo's new information is the exact upstream mechanism that fills it, the ordered catalogue match and palette countercontrol, and the separate precise all-five hypotheses required before any solver experiment.
