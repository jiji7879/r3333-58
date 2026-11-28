# Duggan MCF and triangle constraints: applicability to `R_4(3)`

## Verdict

I read Duggan's PDF locally, especially Sections 5, 8, 9 and 11. I also inspected the current `host()`/`units()` encoder, regenerated an exact live wall parent, and ran only small controls. The current release remains 101,594 certified rows plus 11,585 open small-profile rows (`results/k58-release-2026-11-28/README.md`). **No row, profile, or Ramsey bound is changed here.**

| Target | Assessment |
|---|---|
| (i) Refuting the existing K58 small-wall rows | **No direct per-row transfer.** Duggan's maximal-clique-free (MCF) condition is non-exhaustive and its proof recolours edges, whereas these rows freeze root colours and arm matrices. An MCF-refuted row is not an UNSAT original row. On one exact live parent, full MCF substantially increased work at a small cap. |
| (i, global alternative) | There is a sound but much larger **colour-labelled frontier** construction below. It would require every colour label (or an equivalent disjunction) on every remaining row, plus the already certified rows and a separate proof of the MCF reduction. It has not been benchmarked beyond one row-control and is not a recommended production launch on this evidence. |
| (ii) Lemma L / profile reduction | **No useful reduction found.** The new star-degree inequality below gives only degree at least 4 for a fully maximal colour at `n=51,58`. Every K58 profile already has all degrees at least 9. It therefore cannot distinguish the 11 profiles or prove L. |
| (iii) Finding a K51 colouring | **The only plausible direct use.** For an otherwise unpinned global existence search, requiring one designated colour to be maximal is satisfiability-complete. It is a heuristic restriction for pinned model-finding searches; a returned model is easy to check, but failure is not evidence of absence. Full encoding size and performance remain material concerns. |
| (iv) Certificates | A solver proof of an augmented formula needs a separately checked **non-exhaustive reduction and colour-label coverage**; it is not a DRAT derivation of MCF from the parent. Strict warning-free proof checks remain necessary. |
| Duggan's triangle-count constraints | **Rule out for this encoder.** Every monochromatic triangle count on every edge in every colour is already fixed to zero by the host clauses. A further nonnegative cardinality bound is redundant, with counter overhead only. |

The new components relative to this repository, found by source search and inspection, are: an exact four-colour MCF specialization and implementation, a proof and finite check of a **star-degree inequality**, and a smaller **pinned-only MCF** relaxation. These are new here, not claims of priority in the wider literature.

## 1. What Duggan actually adds

Section 5 calls MCF **non-exhaustive**. For maximally blue `p`-clique-free, every red edge, if recoloured blue, must form a blue `p`-clique. The paper also cautions that the analogous red and blue maximal statements need not have a joint existential equivalence. In its SMS ablation (Section 9, Table 9.2), the times for `R(3,8;28)` are 28 h (SMS), 31 h (+degree), 24 h (+MCF), and 18 h (+degree+MCF). MathCheck's triangle constraints slowed its tests. Thus the paper supplies neither an unconditional row-strengthening theorem nor evidence for a four-colour frozen-arm speedup.

For the present problem every colour plays Duggan's `p=3` role. If `x^c_{uv}` says that edge `uv` has colour `c`, maximality of colour `c` is

\[
x^c_{uv}\ \lor\ \exists w\notin\{u,v\}:(x^c_{uw}\land x^c_{vw})
\qquad\text{for every edge }uv.
\]

For each `e=uv` and third vertex `w`, introduce `y^c_{e,w}` and the equivalence clauses

\[
(\neg y\lor x^c_{uw}),\quad
(\neg y\lor x^c_{vw}),\quad
(\neg x^c_{uw}\lor\neg x^c_{vw}\lor y),
\]

then add `x^c_{uv} OR OR_w y^c_{e,w}`. This is the `p=3` case of Duggan's alternate encoding. `mcf_pilot.py::mcf_cnf` implements it and `augment_mcf_dimacs.py` allocates its variables above the **actual parent maximum**, not merely above the 6,612 physical K58 variables.

### Closure theorem (one colour only)

For any good multicolouring, fix one colour `c`. While a non-`c` edge `uv` has no common `c`-neighbour of `u,v`, recolour it `c`. This cannot make a `c` triangle, and cannot make a triangle in another colour because that colour only loses edges. Stop after finitely many steps. The result is good, and every remaining non-`c` edge has a `c`-coloured two-path. Consequently

\[
\exists\text{ good colouring}\quad\Longleftrightarrow\quad
\exists\text{ good colouring with prescribed colour }c\text{ maximal}.
\]

This proves global existential completeness, **not** that MCF follows from a frozen parent. Sequentially making a second colour maximal may recolour and unbalance the first; no two-colour version is used here.

The live `frozen/gluing.py::units` fixes the root colour of every arm vertex, complete U/T matrices, a marked template, and signed marked-vertex edges. The closure operation is not pin-preserving in general, which is the exact obstruction to treating MCF as a universal conditional clause family.

## 2. New star-degree consequence and its scope

Let `G_c` be maximal triangle-free on `n` vertices and let `d_c(v)=|N_c(v)|`. For every nonneighbour `u` of `v`, maximality supplies `w in N_c(v)` with `u in N_c(w)`. Assign each such `u` to one witness. A fixed `w` covers at most `d_c(w)-1` vertices. Therefore

\[
n-1-d_c(v)\leq \sum_{w\in N_c(v)}(d_c(w)-1),
\qquad\text{equivalently}\qquad
\boxed{\ \sum_{w\in N_c(v)}d_c(w)\geq n-1\ }.
\]

Under the established cap `d_c(w)<=16`, this gives `n-1<=16 d_c(v)`. Hence **every vertex has selected-colour degree at least 4 at both n=51 and n=58**. This goes beyond the current general `[2,16]` bound only for one colour in a fully maximal-MCF branch.

Checks: all 117,720 `(maximal graph, colour, vertex)` incidences in the exhaustive K5 control satisfy the inequality; all 12 K50 closure outputs satisfy the per-vertex incidence and degree checks. See `exhaustive/exhaustive.json` and `artifact_outputs/artifact_results.json`.

Limitations are essential:

* It does not remove any K58 root-degree profile and does not prove Lemma L.
* It needs **full** MCF. It is invalid for the pinned-only relaxation below.
* In a sorted profile representation, it applies to the tracked maximal colour, not automatically to colour 0 as the largest degree.

## 3. Independent small controls

All scripts are dependency-free Python except the exact frozen-parent regeneration, which uses the repository's existing read-only virtual environment. Commands are in `reproduce.sh`.

### 3.1 Exhaustive K5 semantics and a restricted UNSAT control

`mcf_pilot.py exhaustive` backtracks over all `4^10` edge colourings, pruning only already-created monochromatic triangles.

* 542,952 good colourings; exactly 5,886 are maximal in any single named colour (the count is the same for each colour).
* For every colour, the global existence equivalence agrees with the closure theorem.
* 5,430 periodically selected greedy closures had every step and final graph independently rechecked.
* Of the 35 root-degree profiles, 15 are lost if one requires MCF **and the identical profile**. All 15 have selected-colour degree zero. Of 256 literal root stars, 81 have no identical-star MCF completion; none uses all four colours at the root.
* The emitted chosen control has star `(1,1,2,3)`, with selected colour-0 degree zero. The baseline CNF is SAT and its model was checked against all 114 clauses. The same-star MCF CNF is UNSAT.

The last statement has a strict proof: CaDiCaL returned 20, and `drat-trim` returned `s VERIFIED` on the input with an empty addition stream because unit propagation already detects the contradiction. My first solver proof log contained a deletion warning and was **rejected**, not cleaned by passing `-w`. The accepted log `exhaustive/frozen_mcf_empty_drat.log` has no warning/error text and uses the complete input. This is only a proof of the restricted CNF, not of its original root-star problem.

This counterexample is deliberately not oversold: its selected root degree is zero. Complete small solver scans found no counterexample with colour 0 present on any of the 781 K6 root stars, or on all 1,560 K7 root stars using all four colours. Those SAT scans are negative search data, not a pin-preservation theorem.

### 3.2 Unpinned K10 SAT control

Both the unpinned base and colour-0 MCF CNFs were SAT. Every returned literal was independently checked against all 795 base clauses / 1,920 augmented clauses. The recovered colourings are monochromatic-triangle-free; the MCF model has zero missing colour-0 two-paths. See `unpinned/` and the `verify-solution` output in `checks.log`. No timing conclusion is drawn from this easy instance.

### 3.3 Actual K50 and K40 artifacts

For each of the three valid K50 artifacts and each colour, the closure was run and all steps checked: 12/12 outputs are good and maximal in the selected colour, and all passed the repository's independent `tools/verify_coloring.py`. Closures took 1 to 11 recolourings. Two of 12 changed the root profile:

* `k50_z4z4_m6`, colour 3: `(11,16,11,11) -> (11,15,11,12)`;
* `k50_sanity_f2`, colour 0: `(11,16,11,11) -> (12,15,11,11)`.

The labelled K51 one-defect artifact was independently rejected for its colour-1 triangle `(48,49,50)` and was not used as a valid input.

On the actual K40 two-16-arm coloring, root star plus all internal edges of both arms gives 279 pins (`k40_control.py`):

* colour 0: 4 recolourings, all 279 pins preserved, maximal good witness emitted;
* colour 1: 6 recolourings, all 279 pins preserved, maximal good witness emitted;
* colour 2: 8 recolourings, two root pins changed, root profile `(16,16,7,0)->(14,16,9,0)`;
* colour 3: 17 recolourings, 11 root pins changed.

The first two outputs passed the repository colouring checker. Thus pin-compatible closures exist, but the generic proof does not supply them; neither result is a theorem for the K58 wall.

## 4. Exact current-wall control

I regenerated row `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`, tier `first`, with the live tool. Its SHA-256 is exactly the independently recorded

`90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae`.

It has 19,533 variables and 184,335 clauses. Full colour-0 MCF adds 92,568 variables and 279,357 clauses. Under conservative physical one-hot/triangle propagation only (no claim of whole-parent BCP), 1,813 physical literals are assigned. Of 309 pinned non-colour-0 MCF obligations:

* 264 already have a forced two-path witness;
* 45 remain unresolved;
* 0 have all possible witnesses refuted.

This suggests avoiding the 264 satisfied and 1,257 not-currently-pinned edge conditions. **Pinned-only MCF** retains just the 45 unresolved pinned obligations and all of their Tseitin definitions. It uses 2,520 fresh variables and 7,605 clauses. Full MCF implies every emitted pinned-only condition, so this weaker restriction retains the global existential reduction. It does *not* imply full maximality or the star-degree inequality.

### Matched 10,000-conflict CaDiCaL control

All three jobs returned 0 at the conflict cap and are **OPEN**, not UNSAT. The complete logs are in `wall_control/`.

| Formula | conflicts | decisions | propagations | wall CPU / wall s | max RSS |
|---|---:|---:|---:|---:|---:|
| exact parent | 10,000 | 122,355 | 3,375,033 | 0.50 / 0.52 | 41.5 MB |
| + full MCF c0 | 10,003 | 72,446 | 22,448,916 | 1.52 / 1.55 | 90.3 MB |
| + pinned-only MCF c0 | 10,000 | 55,692 | 2,892,597 | 0.50 / 0.51 | 41.2 MB |

Full MCF is unattractive here: about three times the time and 6.6 times the propagations at this cap. Pinned-only avoids that observed overhead, but a 0.01 s difference is noise, not an improvement. Decision counts on different formulas are not a proof of search quality. This is one row, one colour, one seed and one cap; no material speedup has been established.

For scale, `size_estimates.json` independently counts the standalone basic encodings:

| order | base vars / clauses | MCF auxiliary vars | MCF added clauses | total vars / clauses | long-clause length |
|---|---:|---:|---:|---:|---:|
| 51 | 5,100 / 92,225 | 62,475 | 188,700 | 67,575 / 280,925 | 50 |
| 58 | 6,612 / 134,995 | 92,568 | 279,357 | 99,180 / 414,352 | 57 |

## 5. The colour-label issue in a hypothetical global wall use

A tempting argument is: close an arbitrary colour globally, then use the existing full cover. This needs an additional accounting step because the frozen profiles are sorted by degree.

A sound formulation is the following. For each open row `R` and each **physical colour label** `c`, independently refute `F_R AND M_c` (or refute `F_R` plus the disjunction over all four `M_c`). Start with any hypothetical good colouring, greedily make one colour maximal, choose the ticket root and relabel according to the existing cover. The transformed colouring still has its maximal class, now assigned some label `c`; it either lies in an already certified row (impossible) or in one of the open-row/label cases just refuted. This, together with the semantic encoder bridge and all required strict proofs, would rule out the original colouring.

Consequences:

* One selected row's MCF UNSAT still closes only a restricted branch, never the original row.
* Current evidence covers neither the fourfold frontier nor a four-colour disjunction, and there is no basis for launching it as a production sweep.
* Augmenting only the largest-degree arm of each sorted profile is not complete without a separate argument that the maximal colour can be placed there.
* Pinned-only obligations are compatible with this global argument because full MCF implies them; the degree-4 consequence is not available when only a subset is imposed.

## 6. Exact next experiments / stop conditions

1. **K51 model finding, the only direct recommended experiment.** In a genuinely unpinned global CNF, compare (A) basic encoder plus the already validated degree constraints, (B) A with full colour-0 MCF, and (C) B with the `d_0(v)>=4` consequence at every vertex. Keep physical colour 0 designated; do not insert U/T matrices or a fixed root star in this complete-semantics control. Use one matched seed/cap and independently check every model on the original clauses. Include encoding time and memory, not just conflicts. If only overly constrained/pinned heuristic searches are available, advertise them solely as model-finding heuristics. Stop if B or C merely reproduces the full encoding overhead; no K51 absence conclusion follows from a timeout.
2. **One follow-up wall control at most.** If a 100k-conflict test is desired, use the already emitted baseline and pinned-only CNF with matched settings, then stop unless a verified structural reduction emerges. Do not read an OPEN result as evidence either way, and do not mark the parent closed even if the restricted formula obtains a DRAT refutation. Record any such result solely in the colour-labelled MCF namespace.
3. **Do not run the fourfold frontier now.** First show on a small set that a pinned-only condition produces a verified reduction or materially improves propagation at equal work. The current 10k result does not.
4. **Do not implement Duggan's edge-triangle counters here.** They are definitionally zero under the present four-colour triangle-free host.

## 7. Certificate boundary

For an unpinned K51 SAT result, the physical model check is sufficient for the heuristic's result. For any UNSAT use, one needs: exact original-parent binding, fresh auxiliary ranges, strict full-byte DRAT checking with no warning suppression, an independently checked one-colour closure argument, and (for the sorted wall) the label/disjunction coverage argument. A DRAT proof of `F_R AND M_c` does not show `F_R` UNSAT because `M_c` is not entailed by `F_R`.

The K50/K40 step traces provide independently checkable transformations of those particular SAT witnesses; the same does not turn a non-exhaustive UNSAT restriction into a row proof. Existing handoff tooling's warning-related defects were not reused. The accepted micro-proof was checked without `-w`, with zero warnings/errors and `s VERIFIED`.

## Reproduction and principal artifacts

Run from `.ultramath/smwzxq4fl/m8/`:

```sh
sh reproduce.sh > checks.log 2>&1
```

Principal files: `mcf_pilot.py`, `k40_control.py`, `augment_mcf_dimacs.py`, `prepare_wall_parent.py`, `exhaustive/exhaustive.json`, `unpinned/encoding.json`, `artifact_outputs/artifact_results.json`, `k40_outputs/k40_results.json`, `wall_control/parent.json`, `wall_control/parent_mcf_c0.json`, `wall_control/parent_mcf_c0_pinned.json`, and `wall_control/*10k.*`. `checks.log` records the complete commands' outputs, including the strict proof and model checks.
