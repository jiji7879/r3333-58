# Duggan SAT+CAS methods for $R(3,3,3,3)$

**Status.** All eight independent directions were accepted after reproduction; the swarm has ended. **No Ramsey bound, wall row or profile closed.** Everything below uses `dist/k58-massive-solver.zip` as the baseline, not the older stock solver alone.

## Baseline and sources

* `k58-massive-solver.zip` SHA-256 `cc78f1d9f6f7901615b264c9ceaa3319bd152cd4caccc381a74ed742538bdb6a`, including unified stock/colour/square backends, bounded C&C, strict proof export and content-addressed artifacts.
* Conor Duggan, [A SAT + Computer Algebra System Verification of the Ramsey Problems R(3,8) and R(3,9)](https://uwaterloo.ca/computational-mathematics/sites/default/files/uploads/documents/research_paper_conor_duggan.pdf), 2024. PDF SHA-256 `58665d3b71e1e5452a6afdd6d8087bfb7df99daf6566263addfc2f1a905109e8`.
* Accepted reviews: all eight directions of `smwzxq4fl`. Evidence is collected in `results/duggan-paper-2026-11-28/`.

## Outcome at a glance

| paper method | what the massive baseline already has | result here |
| --- | --- | --- |
| Sinz/totalizer counters and arc consistency | conditional Sinz/totalizer degree and support counters | **Real encoding improvement:** guard only overflow clauses, not the recurrence. Exactly equivalent physical projection and much stronger back-propagation, but the actual capped A/B was slightly slower. |
| preferred-full-vertex/minimum-edge gluing | root arms, templates and support gluing | **Negative proof:** at $K_{58}$, the full-vertex deficit bound guarantees no full vertex at any colour. Do not build a minimum-edge catalogue for this route. |
| Gauthier–Brown exact gray-edge generalisation (surveyed in §10) | fixed critical link templates and exact orbit quotients | **No compression possible:** every such generalisation of the $K_{15}/K_{16}$ critical link sets is a singleton. Transverse and smaller-link generalisations are not covered by that negative result. |
| static lex / SAT+CAS / SMS | exact template/stabilizer quotients, plus separate preferred/sorted experiments | The old `hailmary-lex` comparator was vacuous. A corrected stabilizer-lex encoding was much slower on its pilot. Dynamic SMS remains untested and needs frozen-stabilizer permutation witnesses. |
| unit/zebra soft constraints | local/model searches and verified $K_{50}$ witnesses | Implementable for $K_{51}$ model finding. One corrupted $K_{50}$ guide was repaired, but both informative $K_{51}$ pilots returned UNKNOWN. Nonminimal cores drive bad deletion scales. |
| certificate separation | strict DRAT replay, parent/model checks and content hashes | **Directly useful:** new pure-kernel native-counter and support-selector extension theorems. The old abstract at-least formula was only auxiliary-sign-equivalent, not syntactically native PySAT. Full-parent assembly remains open. |
| AlphaMapleSAT / selective re-cubing | bounded greedy C&C and independently checked leaves | Duggan's pinned 2024 code is incompatible with the four-colour action layout. Current generic MCTS produced an exact five-leaf wall frontier, all OPEN, and lost end-to-end to greedy on the solvable control. |
| maximal clique-free constraints | many implied local clauses, but no WLS normal form | A new configurable-edge normal form is sound and passed exhaustive small controls; its million-conflict wall pilot was neutral. Global/pinned MCF is different and generally does not preserve a frozen row. |

## 1. Guard only the boundary of a conditioned counter

For $g\Rightarrow(\sum_i x_i\ge k)$, the baseline prepends $\neg g$ to every Sinz clause. Split the counter into recurrence clauses $E$ and overflow clauses $O$, and replace it by

$$E\land\bigwedge_{C\in O}(\neg g\lor C).$$

Every physical input has a canonical prefix-threshold extension satisfying $E$. If $g$ is false the overflow clauses are vacuous; if $g$ is true the usual hard overflow clauses enforce the bound. Thus this has exactly the same projected models as all-clause guarding. Unlike all-clause guarding, it builds prefix counts before $g$ is decided and can derive $\neg g$ from a bound violation.

The reproduction regenerated the pinned naive and boundary `two5` formulas and passed 9,212 SAT projection cases, 9,828 independent BCP comparisons and all 168 actual counter gadgets. Boundary removed 7,913 literal occurrences and propagated 736/736 sampled actual violations, versus 24 for naive. The one actual 20,000-conflict A/B nevertheless had 21.66% more propagations and slightly more CPU. Treat this as a better encoding to test on one ordinary wall parent, not as a measured speedup.

See [guarded-counter assessment](../results/duggan-paper-2026-11-28/guarded-counter/assessment.md).

## 2. Full vertices do not supply the missing structure

For colour $c$, let $G_c$ be its graph and $d=d_c(v)$. Then $G_c$ is a $(3,17;58)$ graph and its anti-neighbourhood $H_{2,c}(v)$ is $(3,16;57-d)$. For this triangle-free setting the exact identity is

$$58|E_c|=\sum_v e(H_{2,c}(v))+\sum_v d_c(v)^2.$$

Consequently Duggan's deficit is

$$\phi_c=\sum_v\left(29d_c(v)-d_c(v)^2-e(3,16;57-d_c(v))\right).$$

Three disjoint copies of a checked 16-vertex Clebsch colour graph give a triangle-free graph on 48 vertices with independence at most 15 and 120 edges. Induced subgraphs therefore give $e(3,16;m)\le120$ on every relevant order $41\le m\le48$. Also $9\le d\le16$, so $29d-d^2\ge180$ and

$$\phi_c\ge58(180-120)=3480.$$

The proposed count of at least $58-\phi_c$ full roots is negative: it guarantees none. This is a proof not to spend time on the preferred-full-vertex catalogue/gluing route at $K_{58}$.

The same review corrected a literal defect in the paper's generic Lemma 2: for a general graph one needs $E=e(H_2)+Z-e(H_1)$. The omitted $e(H_1)$ vanishes in the paper's actual $p=3$ applications, so its $R(3,9)$ argument is unaffected.

See [full-vertex assessment](../results/duggan-paper-2026-11-28/full-vertex/ASSESSMENT.md).

## 3. Exact gray-edge generalisation cannot compress critical links

Every one of the 1,800 edge/alternative-colour obligations in the stored $K_{15}/K_{16}$ representatives has a common-neighbour witness. Hence changing any one edge to either alternative colour creates a triangle. Under the existing two-class classification, a Gauthier–Brown generalisation cannot retain a gray edge: changing only that edge while keeping every other gray edge fixed gives a bad labelled completion. Every exact generalisation of these sets is a singleton. No further compression of critical internal templates or their placements is available by this mechanism.

This was verified independently with three rejecting negative controls. `K58.template_alternativeClosed_15/16` compile with only the standard axioms. The classification itself is an explicit dependency; transverse interfaces and unrestricted catalogues of smaller links are not ruled out.

See [link saturation](../results/duggan-paper-2026-11-28/LINK_SATURATION.md).

## 4. Symmetry: old experiment invalid; corrected pilot negative

`results/hailmary-lex/hm.py::lex_leader` has a positive fresh auxiliary in every clause, so all auxiliary variables true satisfies it for any physical colouring. Its old 3%/4% result did not measure symmetry breaking and its orbit-redundancy conclusion was unsupported. The old report now carries a withdrawal notice.

A corrected bidirectional comparator passed all 256 two-witness pairs, $3\times4096$ small-matrix partition controls and a strict DRAT refutation. Replaying all eight timing calls reproduced exactly the decisions and propagations: the corrected full rule used 4.75× the propagations and 2.69× our median wall time, always OPEN. This does not rule out dynamic SMS or a more compact encoding. A frozen-row CAS/SMS clause additionally needs a permutation in the stabilizer of the physical pins *and* suitable auxiliary semantics.

See [symmetry assessment](../results/duggan-paper-2026-11-28/symmetry/work/duggan-symmetry-assessment.md).

## 5. Soft constraints for $K_{51}$

The implemented hard/soft split is sound for model finding: deleting guide pins only enlarges the permitted set, so any returned model satisfies the original hard formula. A corrupted $K_{50}$ guide was repaired after one deletion and independently accepted by `verify_coloring.py`. The actual $K_{51}$ core-scored trajectory stopped UNKNOWN at 50,003 conflicts after 21 assumption-UNSAT rounds with 485 active pins. The literal $j-i$ zebra/Toeplitz instance was also UNKNOWN at 50,000 conflicts. No $K_{51}$ witness or family exclusion followed.

The first failed core had 321 pins, so the 20% deletion rule released 65 at once even though the local-repair discussion concerned at most five changes. Small/minimised cores are therefore the informative next experiment, not simply a bigger conflict cap. A separately regenerated 1,195-pin branch has strict DRAT verification and a rejecting wrong-parent control; it is only a conditional exclusion.

See [soft-constraint assessment](../results/duggan-paper-2026-11-28/soft-constraints/ASSESSMENT.md).

## 6. Certificate semantics for the actual emitted formulas

The new `K58.EncoderExtensions` theorems establish existential auxiliary extension for the native PySAT at-least encoding, its guarded form, and guarded P4/C5 support selectors. They compile with only `[propext, Classical.choice, Quot.sound]`. A real contiguous 2,536-clause counter/support suffix regenerated exactly and passed its joint-extension and wrong-selector controls.

This exposed a documentation/binding defect in `AtLeast.lean`: `flipCNF(counter)` flips counter cells as well as inputs, while native PySAT negates only inputs. This is not a wrong CNF or DRAT; auxiliary sign renaming relates the formulas. The native theorem now avoids relying on that unstated renaming. The full-parent Lean/DIMACS assembly, support-classification binding and actual UNSAT obligations remain open.

See [encoder-extension assessment](../results/duggan-paper-2026-11-28/encoder-extensions/REPORT.md).

## 7. A configurable-edge maximal-colour normal form

Duggan's global maximal-clique-free closure does not preserve a frozen row. The following row-safe generalisation does. Let $F$ be a set of physical edges and $S$ the non-host part of the formula, and require that no variable associated with an edge of $F$ occurs in $S$. Choose target colour $c$. Repeatedly recolour a non-$c$ edge $uv\in F$ to $c$ when no third vertex $w$ has $uw$ and $vw$ colour $c$. Each step creates no monochromatic triangle, preserves exactly-one-colour, and leaves every edge outside $F$ unchanged. Existing $c$-paths are never deleted. With the old auxiliary assignment retained, $S$ stays true throughout. At termination every non-$c$ $uv\in F$ has such a witness $w$.

Adding that witness condition is therefore an **equisatisfiability normal form**, not a DRAT consequence of the original parent. For a fresh variable $y_{uv,w}$ equivalent to the conjunction of the two path literals, it is encoded by

$$y\to x_{uw,c},\quad y\to x_{vw,c},\quad (x_{uw,c}\land x_{vw,c})\to y,$$
$$x_{uv,c}\lor\bigvee_{w\notin\{u,v\}}y_{uv,w}\qquad(uv\in F).$$

On wall row `06861a3df60c`, $F$ comprises the 126 unfixed internal edges of small arms 2 and 3 and $c=0$. The builder mechanically proves $F$ disjoint from the fixed unit, threshold and support clauses and preserves the exact ordinary CNF body. An exhaustive $K_4$ control over every good 4-colouring, all 64 fixed-edge subsets and every colour passed 807,936 normalisation runs.

At one million conflicts, original and augmented versions were both OPEN:

| formula | decisions | propagations | solve CPU s |
| --- | ---: | ---: | ---: |
| original | 2,322,342 | 371,735,517 | 63.300 |
| normal form | 2,253,100 | 446,260,223 | 63.666 |

This is a sound new encoding but not a demonstrated solver benefit. An augmented UNSAT proof would still need the independent normal-form argument and strict DRAT replay; it is not eligible for stock finalisation as written.

Reproduce with [maximal_normal_form.py](../tools/duggan/maximal_normal_form.py); see [controls](../results/duggan-paper-2026-11-28/maximal-selftest.json) and [comparison](../results/duggan-paper-2026-11-28/maximal-comparison.jsonl).

The independent full/pinned-MCF review passed 542,952 small colourings, 117,720 star-incidence checks and the actual $K_{50}/K_{40}$ closure witnesses. Full MCF used 6.6× the propagations and about 3× the time at a 10,000-conflict cap; pinned-only was neutral. See [maximality assessment](../results/duggan-paper-2026-11-28/maximality/assessment.md).

Globally normalising one colour also gives

$$n-1-d_c(v)\le\sum_{u\in N_c(v)}(d_c(u)-1)\le15d_c(v),$$

hence $d_c(v)\ge4$ at $n=51$ or $58$ for that **one normalised colour only**. It does not show all four colour degrees are at least four simultaneously and does not constrain the wall profiles, whose small degrees already exceed four.

## 8. AlphaMapleSAT and selective re-cubing

Duggan's pinned 2024 cuber has an interface incompatibility, not just a tuning issue. Its prior array has $58\times57+1=3{,}307$ slots, while K58 needs $2\times6612+1=13{,}225$ signed physical-colour actions. Restricting its pool hit the expected `IndexError`; unrestricted prefix cubing emitted no depth-two cover in 420 seconds. Do not run that binary on this input.

The current generic implementation generated a valid depth-2 wall cover in 66.96 s. All four leaves stayed OPEN at one million conflicts each; selective re-cubing produced two more, also OPEN. The exact remaining frontier has five leaves, not a closure. A completed control then compared identical depth-2 covers: full-rollout MCTS used 284,528 conflicts, 11.282 CPU-s of search and 306.456 s of cubing, versus greedy's 226,881 conflicts, 8.835 CPU-s and 0.720 s preparation. All eleven retained positive replays passed the second checker and the negative controls worked. This is useful proof protocol, but no end-to-end improvement and no support for deployment.

See [MCTS assessment](../results/duggan-paper-2026-11-28/mcts/ASSESSMENT.md), [artifact index](../results/duggan-paper-2026-11-28/mcts/ARTIFACTS.md) and [measured summary](../results/duggan-paper-2026-11-28/mcts/summary.json).

## Recommended next steps

1. **Certificate first:** complete one exact parent semantic assembly using `EncoderExtensions.lean`, then hash-bind it to DIMACS. This is concrete, useful and independent of solving performance.
2. **One small counter A/B:** use the conditional-boundary encoding on one exact ordinary wall parent with equal caps, parent hashes and proof controls. Do not sweep from the historical-row result.
3. **Do not invest** in preferred-full-vertex catalogues, gray-edge compression of critical links, the corrected full static-lex formula, or a larger MCTS pass on this row.
4. **For $K_{51}$:** prioritise small/minimised-core soft deletion and the one-colour maximal normal form over literal Toeplitz search, but only after a matched fresh-versus-incremental control at the same budget.
5. The configurable maximal normal form remains a research encoding, not a recommendation for production until it wins a matched control or closes an independently checked instance.
