# After the SAT/Lean wall: alternative solver technology for the ordinary K58 parent

**Scope.** Repository HEAD `211dd0b2b705efef7481d5cace379fea99a2a0ca`.
This is a prioritized experiment memo, not a Ramsey bound, a wall closure, or an
endorsement of a new solver. I used the required five local reports, the actual
encoder, primary solver papers/documentation/source, and bounded non-wall toy
checks. No wall sweep, MCTS, K51 search, global MCF/lex run, or rejected long
computation was rerun.

## Recommendation at a glance

| priority | candidate | kind | expected information for a bounded pilot | implementation / blast radius | decision now |
|---|---|---|---|---|---|
| 1 | Replace **only the 31 guarded sender Sinz counters** by `kmtotalizer`; preserve naive guarding and all host/support/final **logical relations**, with an explicit auxiliary map | solver-throughput encoding | High for its cost: an exact shape calculation predicts **6,169 fewer auxiliary variables and 7,675 fewer clauses**; installed PySAT can already generate it | Small isolated encoder option; new allocation map and receipts. No change to production defaults | **Run one matched two-seed A/B after extension controls; abandon on the stated gate** |
| 2 | Deterministic proximity ordering of literals **within those same counters**, including preprocessing time | solver-throughput encoding | Conditional on (1), because ordering changes auxiliary meaning, not the formula size or logical constraint | Medium: a deterministic order generator plus end-to-end timings; do not launch a random-order portfolio | **Only if candidate 1 survives its first gate** |
| 3 | Native OPB reification of all 33 cardinality constraints, compared first against the *old OPB converter in the same PB engine* | solver-throughput diagnostic | Potentially distinguishes a real two-level PB benefit from the earlier host-only PB conversion; prior PB throughput makes success unlikely | Medium-to-large: OPB builder, pin binary, new VeriPB/CakePB path if it ever wins. Keep out of production | **Low-priority 2×60 s head-to-head only if the pinned engine is already available** |

There is **no new mathematical closure possibility** in this direction. None of
these items proves candidate criticality, the physical `deg`/`Sends` facts,
112-support membership, coded/automatic guard-set equalities, `ChainReady`, or
the whole-parent semantic bridge. They do not turn frozen units into a complete
physical theory or turn an OPEN/timeout result into UNSAT.

## 1. Exact local object being changed

For wall row
`06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`,
profile `(16,16,14,11)`, charge 7, the ordinary recipe is exactly
`tables=True,total_critical=True,full_root=False`. The frozen parent has
19,533 variables and 184,335 clauses and SHA-256
`90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae`.
The retained cube is `[-1413,1014]`.

Local instrumentation of `tools/color-resolved-wallcc/frozen/dense.py` gives:

| component | exact object in this parent | treatment in candidates 1/2 | native OPB treatment in candidate 3 |
|---|---|---|---|
| host | 134,995 clauses: per-edge exactly-one and 4 triangle clauses per triangle | unchanged | per-edge $\sum_{c=0}^3x_{e,c}=1$; each triangle clause becomes one linear inequality |
| frozen signed units | 438 in the serialized parent (BCP subsequently yields more) | unchanged | $\ell\ge1$ for every unit; never solve units alone |
| 31 guarded sender counters | **4** copies of $g\Rightarrow\operatorname{AtLeast}(30,10)$ and **27** copies of $g\Rightarrow\operatorname{AtLeast}(41,14)$ | replace these gadgets only | $\sum_i x_i+k(1-g)\ge k$ for each gadget |
| 15 support-event guards and other support selectors | `support_clauses` implications and guarded disjunctions; no cardinality re-encoding is licensed by their P4/C5 geometry | same logical relations; selectors may be renumbered and must be mapped by identity | each original clause independently becomes $\sum_{\ell\in C}\ell\ge1$; no nonlinear product is introduced |
| final guard totals | $\operatorname{AtLeast}(15,6)$ and $\operatorname{AtLeast}(31,6)$ | **retain existing Sinz** on the corresponding guard IDs as an ablation | direct PB sums |
| split points | retained physical cube above; generic physical variables have IDs $\le6612$ | same physical IDs; auxiliary-ID cubes are invalid after reallocation | append cube literals as units; old auxiliary cubes are invalid |
| optional 45-edge arm-3 MCF suffix | 2,520 fresh Tseitin witnesses, 7,605 clauses, 45 long clauses | **excluded from the pilots**; reallocate above the new maximum and rebind receipts before any later test | linearize each existing clause; OPB is linear, so do not replace witnesses by nonlinear monomials |

The sender counters dominate the avoidable counter encoding. Their present
Sinz totals are 11,006 auxiliary variables, 21,621 clauses and 53,830 literal
occurrences before adding `-g` to each clause. `kmtotalizer` needs 4,837, 13,946
and 41,445 respectively. The resulting whole-parent prediction is therefore:

| formula | variables | clauses | change |
|---|---:|---:|---|
| existing ordinary parent | 19,533 | 184,335 | pinned baseline |
| sender-only `kmtotalizer` parent | **13,364** | **176,660** | −6,169 variables, −7,675 clauses, −12,385 counter literal occurrences |

These are exact generation-size calculations, not measured solver speedups and
not hashes of a CNF I have emitted. Host/fixed-unit bytes and physical IDs stay
fixed, but a smaller counter changes the following `highest` allocation. Thus
sender guards and support selectors after that point need **semantic identity
maps** (sender $x$, support family $P_i$); “unchanged support” never means that
their renamed DIMACS literals can be copied blindly. Final counters use the
corresponding mapped guard IDs.

## 2. Priority 1 — sender-only `kmtotalizer`

### Source and what it actually establishes

* **Official implementation/API:** PySAT, `pysat.card`, documentation
  <https://pysathq.github.io/docs/html/api/card.html> and source
  <https://github.com/pysathq/pysat/blob/master/pysat/card.py>.
  `CardEnc.atleast` defines $\sum x_i\ge k$ and exposes
  `EncType.kmtotalizer`; the local pinned Python environment is
  `python-sat==1.9.dev22`, and `dense.py` currently relies on its default
  sequential counter. The source names the modulo-k-totalizer reference:
  António Morgado, Alexey Ignatiev, Joao Marques-Silva, *MSCG: Robust
  Core-Guided MaxSAT Solving*, JSAT 9 (2015), 129–134. This establishes an
  available encoding and its intended relation—not a K58 speed result.
* Reeves, Filipe, Hsu, Martins and Heule, *The Impact of Literal Sorting on
  Cardinality Constraint Encodings*, AAAI 2025, pp. 11327–11334, primary PDF
  <https://www.cs.cmu.edu/~jereeves/research/AAAI25-paper.pdf>. The background
  section explains how sequential, totalizer, and network encodings create
  different auxiliary abstractions; tables 1–2 (pp. 11331–11332) report that
  natural-order `kmtotalizer` solved 635 generated MaxSAT-derived instances
  versus 597 for Sinz. Their instances come from **one large bound in MaxSAT
  2023**, use 1,800 s timeouts and StarExec, and are not four-colour Ramsey
  formulas or conditional sender counters. I infer only that this particular
  alternative deserves a controlled A/B, not that 635/597 transfers here.
* The repository search found **no existing `kmtotalizer` use** in tracked
  tools/results. Conversely, conditional-boundary Sinz is not new and already
  failed its exact-parent gate: geometric-mean CPU ratio 1.33344 with all 12
  calls OPEN (`results/ams-wall-2026-11-28/conditional-sinz/ASSESSMENT.md`).

### Exact method and semantic boundary

For each sender, with physical/candidate literals $X=(x_1,\ldots,x_n)$,
replace only the auxiliary implementation of
$$R_g(X)\quad\Longleftrightarrow\quad g\Rightarrow(\textstyle\sum x_i\ge k).$$
Use the same naive policy as production: prepend `-g` to every emitted
`kmtotalizer` clause. Do **not** mix the experiment with the already rejected
conditional-boundary policy. Keep final-counter Sinz, support logic, host,
units, and physical/candidate order fixed, while recording the induced logical
IDs by sender/support identity.

Projection equivalence is the only semantic statement licensed here. Under the
physical-ID and logical guard/selector identity map, a satisfying assignment in
either encoding projects to values satisfying the other relation; fresh counter
auxiliaries are existentially projected away. This is neither physical-graph criticality nor a
proof of the guarded ticket theorem. A KMT-parent UNSAT transfers to the
original CNF only after this projection relation and the exact input map have
been independently checked. A model must be extended back to the original
auxiliary variables and checked against the full original formula before use.

### Bounded verification already done here

`audit_candidates.py`, run with the existing pinned interpreter (0.507 s total),
regenerated the original parent bytes and checked the hash above. It then:

* independently counted every `CardEnc.atleast` call and asserted the exact
  4/27 sender shape split and the two final shapes;
* compared encoder sizes at those actual $(n,k)$ values;
* exhaustively tested both naive-guarded encoders at $n=1..7$, every
  $1\le k\le n$, and every guard/input assignment: **6,152 projected SAT
  checks**, with zero mismatches;
* rejected an unguarded below-threshold assignment as a separate negative
  control.

No wall formula was solved. Toy SAT equivalence is not a Lean proof, an actual
parent semantic assembly, or evidence of hardness.

### Minimal A/B and abandonment criterion

1. Add an experimental `sender_encoding` argument in a private generator copy.
   Require stock output byte-equality with the pinned baseline before enabling
   KMT. Recompute all subsequent top-IDs automatically; never relabel old aux
   IDs. Assert the predicted 13,364/176,660 dimensions and preserve every
   physical and support relation **after applying the recorded identity map**.
   Validate the direct projected relation on all 31 actual gadgets with positive,
   negative, guard-false and wrong-bound controls. Produce an explicit
   old-logical-object/new-logical-object/auxiliary allocation receipt.
2. On **parent+cube only**, run fresh default CaDiCaL 1.9.5 through the same
   pinned PySAT binding, seed 0 and seed 1, 100,000 conflicts per arm per seed,
   no proof logging in the timing stage, alternating baseline/variant order.
   Record preprocessing separately, as well as solve CPU, propagations,
   decisions, restarts, peak RSS and statuses. Use the same host and cube
   through the campaign receipt root; never compare against an old timing with
   a different engine, proof mode or concurrency context.
3. **Stop** if a semantic control fails, if either KMT call errors, or if its
   geometric-mean solve-CPU ratio is $>0.90$ with no reduction in peak memory.
   Only if it passes, repeat the pair at one million conflicts/seed (still only
   this one row), then require a $\le0.80$ CPU ratio and no propagation/memory
   regression before considering a second wall row. A completed SAT/UNSAT
   interrupts the benchmark and invokes the full model/proof protocol; an OPEN
   result is used only for the stated capped performance comparison.

The thresholds are a resource-allocation rule, not a claim that a larger cap is
more informative by default. If there is no clear bounded win, this direction
ends without another encoding sweep.

## 3. Priority 2 — literal-order follow-up, only after a KMT signal

The AAAI source's ordering hypothesis is precise: placing structurally related
literals nearby changes which subsets the auxiliary counters summarize, while
leaving the constraint relation and encoding size fixed (background,
pp. 11328–11330). Its Proximity method uses co-occurrence scoring and short
clauses; the paper reports mixed outcomes. In particular, cheap occurrence-only
ordering **underperformed Natural**, random best-of-five is an oracle-like
portfolio, Proximity preprocessing can exceed 100 s above 100,000 clauses,
and PAR-2 includes preprocessing (pp. 11331–11333). Our parent has 184,335
clauses, so preprocessing is part of the honest cost.

**Fit.** Candidate lists in `dense.py` already follow arm/vertex enumeration,
which is meaningful structure. Thus “sort them arbitrarily” has no rationale.
The only worthwhile variant is one deterministic proximity ordering computed
from the exact original host/support clauses and applied identically to the KMT
input lists for both at-least and its at-most translation. Keep final Sinz order
fixed.

**Test and stop rule.** Emit natural and proximity KMT parents from the same
constraint list; certify that each is a permutation before encoding and that
auxiliary allocation remains 13,364 variables/176,660 clauses. Run the same
seed-0/seed-1 100,000-conflict pair. Include ordering and serialization time in
end-to-end CPU. Abandon if ordering takes over 120 CPU-s, if projected semantics
or permutation controls fail, or if end-to-end geometric-mean CPU is not at
least 20% below natural KMT. Do not run occurrence-only, five random orders, or
an MCTS/order-selection layer.

## 4. Priority 3 — direct reified OPB, a narrow diagnostic

### What is genuinely untested, and the earlier negative evidence

`results/hailmary-4/README.md` reports RoundingSat 2 at roughly 69 conflicts/s
on a first-tier case and 137/s on a retry case, versus about 24,800/s for
Kissat on that first-tier case. Both PB attempts were UNKNOWN. The converter in
`results/hailmary-4/opb.py` made per-edge equalities native but translated
**every ticket/counter CNF clause** merely to an OPB clause. The remaining
untested change is to represent the two cardinality levels natively, not to
repeat that conversion.

The old note states zero core-guided counters; do not overread that as a formal
proof that no PB conflict reasoning occurred. The robust prior observation is
its very low search throughput.

For every sender in the new converter use
$$\sum_i x_i+k(1-g)\ge k.$$
If $g=0$ this is vacuous; if $g=1$ it is exactly $\sum x_i\ge k$. This keeps the
existing **one-sided** guards. Do not strengthen them to two-sided
criticality/equivalence. Add native $\operatorname{AtLeast}(15,6)$ and
$\operatorname{AtLeast}(31,6)$, while mapping host, support selectors and units
as listed in §1. The calculation predicts 8,323 retained physical/guard/support
variables and 152,443 OPB constraints, with all 11,210 counter auxiliaries gone.

### Primary source and fit

* Jan Elffers and Jakob Nordström, *Divide and Conquer: Towards Faster
  Pseudo-Boolean Solving*, IJCAI 2018, pp. 1291–1299, DOI
  [10.24963/ijcai.2018/180](https://doi.org/10.24963/ijcai.2018/180), primary
  PDF <https://ijcai.org/proceedings/2018/0180.pdf>. Section 1 (pp. 1291–1292)
  explicitly says stronger PB constraints can make storing/manipulation much
  costlier than clauses and multi-precision arithmetic costly; §2 defines
  conflict-driven PB propagation. This supports a possible stronger conflict
  analysis, but also predicts the main measured risk on our 134,995-clause
  resolution-heavy host.
* Official RoundingSat README and format documentation:
  <https://gitlab.com/MIAOresearch/software/roundingsat/-/raw/master/README.md>
  and `InputFormats.md`. RoundingSat handles linear 0–1 constraints with native
  conflict analysis and certified UNSAT; OPB supports positive/negative integer
  coefficients and `~x=1-x`. Our reification is within exactly that fragment.
  VeriPB/CakePB is a different certificate pipeline, not DRAT:
  <https://veripb.org/> and Koops et al., *Practically Feasible Proof Logging
  for Pseudo-Boolean Optimization*, CP 2025, DOI
  [10.4230/LIPIcs.CP.2025.21](https://doi.org/10.4230/LIPIcs.CP.2025.21).

The interesting possible interaction is between the 31 reified constraints and
final guard sums during PB conflict analysis. Native propagation alone is not a
reason to expect a win, and the host remains mostly ternary resolution work.

### Falsifying A/B and stop rule

Regenerate **both** of the following against the same ordinary parent/cube:

* **old-style OPB:** native per-edge equalities, but every original sender and
  final-counter CNF clause translated independently to OPB;
* **direct-reified OPB:** the native sums above.

Run each for 60 CPU-s once with the same binary hash, version, options and seed
on one core—no parallel portfolio. Do not compare these runs with the old #7
profile/tier or with a different engine. Record parsing time separately and all
native search counters. Abandon immediately if direct reification is slower,
does not reduce the native search work substantially (at least a 5× normalized
conflict/decision rate improvement, because the prior deficit is two orders of
magnitude), or produces a result whose model/proof cannot be checked. Only a
clear win earns one matched query against CaDiCaL and any VeriPB development.

A PB UNSAT would require independently checked VeriPB/CakePB evidence, plus a
proof that satisfaction of the original parent projects to satisfaction of the
OPB formula. VeriPB's richer `red/dom` rules are proofs of redundancy, not a
license to assert arbitrary equisatisfability. Cube exhaustiveness and the
physical `ChainReady`/support bridge remain separate obligations. Do not spend
on this certificate port before the small same-engine performance gate.

## 5. Clearly labelled no-go items

### 5.1 Current guarded Cardinality-CDCL: **do not run on K58**

The otherwise attractive paper is Reeves, Heule and Bryant, *From Clauses to
Klauses*, CAV 2024, DOI
[10.1007/978-3-031-65627-9_6](https://doi.org/10.1007/978-3-031-65627-9_6),
primary PDF <https://www.cs.cmu.edu/~jereeves/research/cav24-paper.pdf>.
Sections 5–6 (preprint pp. 11–14) give native cardinality propagation and its
DRAT conditions. However:

* Its larger-cardinality general benchmark table (table 3, p. 17) has worse
  UNSAT PAR-2 for CCDCL (3315.55) and Hybrid (3104.27) than CaDiCaL
  (2824.08); ReEncode (2297.03) was better. The evaluated extraction primarily
  finds AMO constraints, not our 31 conditional $\ge10/\ge14$ senders.
* Native guarded propagation was added later (commit `8ff1661`,
  2024-12-06), after the CAV24 solver commit. Its logic is therefore not covered
  by the reviewed CAV24 evaluation/argument merely because it lives in the same
  repository.
* **Current upstream has a specific reported unsoundness witness, not locally
  reproduced here.** Issue
  <https://github.com/jreeves3/Cardinality-CDCL/issues/2> (opened 2026-09-14,
  still open against current HEAD `75b47e4`) gives
  `p knf 3 4; g 1 -1 2 3 0; 1 0; 2 0; -3 0`. Hand evaluation confirms that
  `1,2,-3` satisfies the documented guard semantics; the reporter says the
  solver returns UNSAT. Issue
  <https://github.com/jreeves3/Cardinality-CDCL/issues/3> separately reports an
  invalid returned model. These reports alone are not my solver measurement,
  but they are precise open upstream counterexamples requiring resolution.
* My source reading at commit
  `75b47e4454d89c61005c48c273c2d274adc82c6e` independently identifies a source
  condition that needs the same controls: `propagate.cpp:547` tests a guard
  value as a Boolean, admitting the unassigned value 0, while line 549's
  assertion requires a false guard. `Tools/check-sat/check-sat.hpp:110` instead
  treats a true guard as sufficient. This condition/assertion disagreement is
  not covered by the published CCDCL proof argument. It is not a substitute for
  reproducing issue #2, but it is enough to forbid calibration on a
  million-conflict wall.

The direct `g k -g candidates` mapping would otherwise have fit perfectly, but
it is disqualified now. Even a future fix needs issue #2's accepting control,
an active-guard UNSAT control with replay, and an independent reason/proof
review. The README's duplicate-literal-to-equivalent-variable workaround
(`README.md:55–63`) should not be used to smuggle the same untrusted semantics.
No external build or wall A/B was attempted here.

### 5.2 CryptoMiniSat XOR/BNN: no new useful structure, and an unsafe card shortcut

Official CMS documentation <https://github.com/msoos/cryptominisat> supports
incremental solving, XOR input and XLRUP proofs checked by `cake_xlrup`. The
primary format source <https://github.com/meelgroup/frat-xor/blob/master/format.md>
is more restrictive: no RAT support, only XOR steps in current `cake_xlrup`,
and it explicitly says CMS does **not properly handle BNN without an output
literal**.

Replacing each four-colour at-least-one clause by
$x_0\oplus x_1\oplus x_2\oplus x_3=1$ while retaining pairwise AMO is logically
valid. But XOR hyperedges would be 1,653 disjoint four-variable blocks: every
colour variable belongs to exactly one such edge. There is no nontrivial
Gaussian-elimination chain joining graph triangles. Native XOR therefore adds
machinery without new cross-edge parity content. A BNN output literal is an
**equivalence**, whereas these relaxed sender guards are one-sided; changing to
equivalence would require a separate physical proof. Omitting the output is
explicitly unsupported. The new proof backend would also complicate RAT-heavy
cube proof composition. Reject this rather than launching a different-engine
timing.

### 5.3 No additional encoding/engine survey justified now

* At the exact shapes, full totalizer, sorting/cardinality networks are larger
  than KMT; `mtotalizer` is a close size-matched alternative, useful only as a
  diagnostic if KMT behaves unexpectedly, not as another candidate queue.
  BDD/Pindakaas encodings were not installed and no package installation is
  approved. The source supplies no independent mechanism that overrides the
  negative tradeoff measured for conditional Sinz.
* MiniCard 1.2 accepts CNF+ and repeated literals for implication
  (<https://github.com/liffiton/minicard>), but it is based on MiniSAT 2.2 and
  does not supply the modern DRAT/inprocessing workflow required here. CAV24
  explicitly identifies this gap.
* Existing CaDiCaL 1.9.5/2.1.2, Kissat, default/search-only/reducer and
  incremental/shared-learning comparisons are already matched and mostly OPEN
  or neutral (`tools/color-resolved-wallcc/NATIVE.md`,
  `results/color-resolved-wall-solver-2026-11-28/README.md`,
  `results/solver50-3s-2026-11-27/THREE_SECOND_RESULTS.md`). A generic version
  portfolio or parallel CPU expansion is not a new candidate.
* Full/pinned/global MCF, static lex, larger solver budgets, MCTS and global
  caps are deliberately outside this memo. The rejected arm-3 MCF trajectory
  and conditional-Sinz CPU penalty are not evidence of UNSAT.

## 6. Three-way classification and certificate obligations

**(a) New mathematical closure possibility: none.** No proposal eliminates one
of the 11 wall profiles, reduces the 113,179-case cover, or discharges
`ChainReady`. Throughput improvements cannot substitute for the exact physical
112-support/guard equalities and expanded-row realization.

**(b) Solver-throughput experiments:** priorities 1–3 only, with all timings
confined to one exact ordinary parent/cube and the stated abort rules. SAT,
UNSAT and OPEN have different meanings. Timeout/conflict cap exhaustion is not
UNSAT evidence. SAT of the relaxed parent is not a physical K58 colouring.

**(c) Certificate/proof engineering only, if a candidate ever finishes:**

1. Preserve stock bytes and emit a semantic/input map and complete allocation
   receipt. Freeze parent, cube, generator, solver binary and option hashes.
2. Independently prove the projected relation and the direction needed for
   UNSAT transfer. Existential extension (equisatisfiability) is not syntactic
   CNF identity and not automatically a DRAT-prefix proof.
3. On SAT, extend/reconstruct original auxiliaries and check every original
   clause, frozen unit and cube literal. On UNSAT, strictly replay the entire
   produced proof against the actual transformed input, with a wrong-parent
   rejecting control. Do not splice an incremental prefix or accept a solver's
   UNSAT line alone.
4. KMT/ordering use ordinary DRAT/LRAT on the transformed CNF plus the checked
   projection proof. OPB instead needs VeriPB/CakePB and cannot be renamed DRAT.
   Every completed cube still needs cover correctness and whole-parent replay.
5. Only then revisit `ChainReady` and the physical facts. These semantic tasks
   are pre-existing obligations, not solved by choosing a tighter encoding.

## 7. Metadata housekeeping (checked, but not a review result)

The accepted local status remains **$51\le R_4(3)\le62$** (Chung 1973;
Fettes–Kramer–Radziszowski 2004, per DS1 rev18, 2026-04-24). ArXiv
<https://arxiv.org/abs/2610.36648> currently shows *An upper bound of 60 for the
Ramsey number R(3,3,3,3)*, **Milos Tatarevic**, v1 2026-10-27 and v2 revised
2026-11-06. It still claims, rather than independently establishes here,
$R_4(3)\le60$ through global counts, classifications, Lean and two SAT solvers.
Its approximately $3\times10^5$ refutations have not been independently
DRAT/LRAT-checked in this repository.

The current GitHub API profile <https://api.github.com/users/milostatarevic>
also gives **Milos Tatarevic**, and the repository README
<https://github.com/milostatarevic/r3333-upper-bound> uses the same arXiv link.
Neither current primary record supports the old local note's “M. Stojanović”
attribution. Correct that author field to Tatarevic while retaining the explicit
preprint claim warning; do not infer anything further about the discrepancy
without a primary explanation.

## 8. Reproduction and checks not run

From this member directory, with the repository root three levels above:

```sh
PYTHONDONTWRITEBYTECODE=1 \
  ../../../.scratch/k58/.venv/bin/python -B audit_candidates.py \
  > audit_results.json
```

The output is retained in `audit_results.json`. It took 0.507 s and produced no
CNF/DRAT file. Official source was fetched/cloned read-only into this member's
`.scratch/`; no package or external solver was installed or compiled. In
particular, **no candidate wall A/B, PB run, CCDCL run, full semantic Lean
assembly, independent DRAT check of arXiv:2610.36648, or proof of a new bound
was run here.**
