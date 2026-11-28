# Literature-driven next steps for $R_4(3)$

## Status and decision

The accepted interval remains $51\le R_4(3)\le 62$ (Chung 1973;
Fettes–Kramer–Radziszowski 2004), as recorded by Radziszowski's
[Dynamic Survey DS1.18](https://doi.org/10.37236/21). Tatarevic's
[arXiv:2610.36648v2](https://arxiv.org/abs/2610.36648v2) **claims** an upper
bound of 60 with a global incidence count, classifications, Lean and 296,081
SAT refutations from each of two solvers. It is a preprint claim, not a bound
independently established here. Current arXiv and GitHub metadata name Milos
Tatarevic, correcting the old local `M. Stojanović` attribution.
No wall profile, whole parent, `ChainReady`, or Ramsey bound has been changed by
this literature review.

Ultramath `smx04thj8` had **seven accepted bounded directions**; the independent
prioritization member finished without a final report. The coordinator checked
the calculations and the key primary sources. These are candidate experiments,
not already-established improvements. The seven detailed accepted memos are:

| topic | detailed memo |
|---|---|
| exact support transport and the K60 comparison | [k60-source-audit.md](k60-source-audit.md) |
| same-degree critical attachment | [attachment-structure.md](attachment-structure.md) |
| sender counters and alternative solvers | [alternative-sat.md](alternative-sat.md) |
| restricted dynamic symmetry | [dynamic-symmetry.md](dynamic-symmetry.md) |
| support relations and GAC | [support-encodings.md](support-encodings.md) |
| proof/cube workflows | [proof-workflows.md](proof-workflows.md) |
| lower-bound families | [lower-bound-families.md](lower-bound-families.md) |

## The recommended order

### 1. Port the exact K60 support-pattern transport into K58

**Type:** physical-semantic/certificate work, not a new solver search.

K60's `BalancedHostGuard.actual_guard_pattern` proves that each physical
critical-neighbourhood guard is a named P4/C5 catalogue entry. The separate
finite lemmas supply explicit P4 and C5 completeness by ordinary `by decide
+kernel` (not `native_decide`). The important contribution is an exact physical
coordinate argument, not another generic independent-set argument:
[P4 transport source](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/formal/src/UniformK60/BalancedHostGuard.lean),
[finite completeness](https://github.com/milostatarevic/r3333-upper-bound/blob/6c3f2fd0386335321801fa4079397d4a4c1962f3/formal/src/UniformK60/BalancedAnchorSupport.lean).

A local regeneration verified **ordered equality** of these three lists:

```text
K58 targetSupports == allowed_supports(16, "T", arm=0, marked=1)
                     == K60 full-T masks
                     == 96 P4 patterns + 16 C5 patterns = 112 entries
```

Four palette choices also have K60's exact masks; the other eight do not match
even as sets. Internal marked colour 1 must be excluded and path/cycle colour 2
is required. No "either remaining colour" shortcut is valid. See
[`checks/catalogue-check.json`](checks/catalogue-check.json), independently
recomputed with [`check_catalogues.py`](checks/check_catalogues.py).

The K58 theorem to instantiate already has its physical shape result,
`pinned_support_shape` in `lean/K58/Support.lean`. At a true guarded sender, its
candidate count plus the root must first establish $15\le d\le16$. The proof
then needs explicit `PinnedArm` coordinates for both sender and root, no invented
physical vertices, the physical P4/C5 relation, and the mask/name bridge.

**Minimal step:** write one generic K58 lemma for sender 18, with triangle-freeness,
mutual root membership, degree bounds and both pinned arms explicit. Check its
axioms, then instantiate guards at vertices 18–32 and plug it into
`emittedSupportStep.ready`. Reject a U palette, path colour 3, a wrong mask, and
a wrong coordinate order. Failure to meet those conditions stops the port.

This addresses a named open semantic obligation, but it does not show that every
coded guard equals a physical `Sends` event, that vertex 17 plus the coded sets
exhaust the guards, or the final `ChainReady`. K60's visible-neighbourhood theorem
is not a replacement for all of that, and its balanced/common-critical-pair
assumptions must not be silently added to K58.

A separate K60 **all-five** mechanism uses 32 simultaneous visible-neighbourhood
embeddings (without its large degree-counter block). It is relevant only after a
new K58 branch proof actually supplies $d_0(v)=d_1(v)=16$ for every $v$ and an
exhaustive normalized cover. No such branch has been proved here. Do not generate
its roughly 700,000-clause formulas merely because a ticket-root $w\le H$ exists;
that would change the theorem rather than import it.

### 2. Formalize CAT58 and measure its new attachment cover

**Type:** a genuinely new global structural possibility, currently not a wall
reduction.

The following is a direct deduction checked during this review:

> **CAT58.** In a triangle-free four-colouring of $K_{58}$, there are distinct
> vertices $u,v$ and a critical colour $c$ such that $d_c(u)=d_c(v)=s\in\{15,16\}$
> and $|N_c(u)\cap N_c(v)|\ge3$.

Each vertex has some degree at least 15: all degrees sum to 57 and are at most
16. So $\sum_c|C_c|\ge58$, giving a colour with at least 15 critical vertices.
At least five have degree 16, or at least six have degree 15. Pairwise
intersections of at most two would give the lower bounds
$16+14+12+10+8=60$ or $15+13+11+9+7+5=60$, both already larger than 58.

For the edge colour $\gamma=uv$, the analogous partition bound is
$k\le s-\max(0,d_\gamma(u)-11)$ (and with $u,v$ reversed). Its two other
parts are bounded by $R(3,3)=6$. This does **not** imply the old K62 bound
$k\le14$ at K58. The 2004 method is Fettes–Kramer–Radziszowski,
[Ars Combinatoria 72](https://combinatorialpress.com/article/ars/Volume%20072/volume-72-paper-5.pdf),
but its successive attachment theorem and its further-critical-neighbourhood
filter cannot be imported verbatim.

The independent physical controls find high-overlap examples ($k=15,16$) and no
pair with two further critical colours at both endpoints. Reproduction:
[`fit_checks.py`](checks/fit_checks.py), [`fit_checks.json`](checks/fit_checks.json).
This proves that the old criticality assumption is not an automatic simplification.

**Minimal step:** formalize only CAT58 first. Reproduce the reported 533 marked
and 724 overlap reference classes exactly; any mismatch stops the experiment.
Generate 15/15 and high-overlap branches afresh, with explicit cover/permutation
witnesses. Continue only if the normalized early census is below $10^4$ and a
non-copying pullback relation remains. Do not add an existential attachment as
units to one existing parent: the witnessing pair need not be its root/sender.
The original 2004 programs were not recovered here, so its reported counts are
calibration targets, not imported proof bytes. Its scanned PDF was not OCRed;
that source limitation is explicit.

### 3. A/B the 31 guarded sender counters with `kmtotalizer`

**Type:** solver-throughput encoding experiment.

The exact parent has 4 copies of guarded AtLeast(30,10), 27 of AtLeast(41,14),
and two final shapes AtLeast(15,6) and AtLeast(31,6). Replacing only those 31
Sinz implementations (not the final counters, support logic, host or cube)
gives this exact size calculation:

| encoding | auxiliaries | clauses |
|---|---:|---:|
| Sinz | 11,006 | 21,621 |
| `kmtotalizer` | 4,837 | 13,946 |
| **change** | **−6,169** | **−7,675** |

So the predicted parent is **13,364 variables and 176,660 clauses**, rather
than 19,533/184,335. It is smaller, not yet faster. `audit_candidates.py`
recomputed the actual 31-shape inventory and ran **6,152** exhaustive
projected guarded/input assignments correctly. See
[`checks/audit_results.json`](checks/audit_results.json), which was byte-equal
on coordinator replay.

Use the existing naive guard relation in a private generator copy, keeping all
subsequent guard/support identities explicit. A smaller counter changes the
allocation of later auxiliaries; their DIMACS IDs cannot be copied blindly.
Satisfying models must transfer in both directions through that identity map.
A subsequent UNSAT still needs a projection proof plus strict replay on the
true transformed input. K60/literature gains in different MaxSAT families do not
provide a K58 timing guarantee:
[PySAT counter implementation](https://github.com/pysathq/pysat/blob/master/pysat/card.py),
[Reeves et al., AAAI 2025](https://www.cs.cmu.edu/~jereeves/research/AAAI25-paper.pdf).

**Bounded A/B:** parent+cube `[-1413,1014]`, seeds 0 and 1, 100,000 conflicts
per arm/seed with alternating order, fresh CaDiCaL 1.9.5 through PySAT 1.9.dev22.
Include preprocessing and record memory and all statuses. Abandon on semantic
failure or no meaningful improvement. Literal-order experiments are a separate
follow-up only if KMT wins; proximity sorting is not guaranteed to help, and its
preprocessing is part of its cost.

### 4. One restricted, one-colour SMS/export experiment

**Type:** solver-throughput experiment, only with separately checked witnesses.

The exact root units and cube give two frozen twin cells on vertices
`{38..46}` and `{52..57}`. All 51 transpositions within them preserve the 438
signed units and cube and the abstract counter/support specifications. Thus a
candidate restricted group is

$$H=S_9\times S_6,\qquad |H|=9!\,6!=261{,}273{,}600.$$

The coordinator reproduced this and the counter-specification interception
with [`symmetry_fit.py`](checks/symmetry_fit.py),
[`counter_specs.py`](checks/counter_specs.py), and identical receipts
[`symmetry_fit.json`](checks/symmetry_fit.json),
[`counter_specs.json`](checks/counter_specs.json). **No tested transposition is a
full-CNF automorphism with auxiliaries fixed**, so naive BreakID/SEL input is
excluded on this parent.

The proposal is one-colour SMS restricted to $H$, with a recorded variable
bijection and the same root/cube semantics. Current upstream SMS supports block
partitions and single-graph witness output, but not stock four-overlay witness
output. Relevant primary methods:
[Kirchweger–Szeider, CP 2021](https://doi.org/10.4230/LIPIcs.CP.2021.34),
[LeanSMS](https://doi.org/10.1007/978-3-032-32589-1_8),
[SEL, SAT 2017](https://doi.org/10.1007/978-3-319-66263-3_6).

**Gate:** bounded 60 CPU-s of generation. Every emitted clause must carry a
permutation that belongs to $H$, preserves units/cube and has a checked strict
lex indicator. Reindex back through the recorded bijection. Solve the augmented
formula with the incumbent engine and strict DRAT/model controls. Do not trust
an SMS verdict or an LRAT stream that merely assumes SMS clauses. Stop on no
valid nontrivial clause, a failed witness check, or a matched capped regression
without reduced searched work. Any useful result then earns the separate
$H$-orbit/four-colour projected-model certificate port; LeanSMS's concrete
`native_decide` examples cannot simply be imported under this project's axiom rules.

### 5. Compare full LRAT and two-level cube certificates on closed cases

**Type:** certificate engineering only.

Use [native CaDiCaL LRAT + Lrat-Trim](https://doi.org/10.4230/LIPIcs.SAT.2023.21)
on already closed, heterogeneous cases. The published SAT-2022 averages support
trying it, not extrapolating a speedup here. Native LRAT eliminates the expensive
DRAT elaboration step in principle, but one local H=8 run showed a cost, not a
win: 1.58 vs 1.83 CPU-s and 9,529,642 vs 14,594,230 proof bytes for incumbent
DRAT vs direct LRAT. The deterministic counters were unchanged, and **no
independent LRAT replay was installed or run**. See
[`checks/native-lrat-h8.json`](checks/native-lrat-h8.json). My read of the PDF
confirms its reported 30%/180%/125% certification overheads are benchmark-specific.

The next option is
[Tan–Heule–Myreen, Compositional UNSAT Checking in CakeML](https://doi.org/10.1007/s10009-022-00690-y).
For exhaustive cubes $G_i$, top-level blockers $\neg G_i$ are justified by
independently checked subproofs against earlier blockers. A failed-core subset
$H_i\subseteq G_i$ must itself be proved, never just minimized in text. The final
coverage derivation is also checked. Compare per-cover composition with the
existing monolithic DRAT export rather than creating a second permanent archive.

ICNF/LIDRUP is a later throughput experiment:
[Certifying Incremental SAT Solving](https://kfazekas.github.io/papers/FazekasPollittFleuryBiere-LPAR24.pdf).
Check **both** the ICNF interaction and proof file; assumption cores and SAT/UNKNOWN
statuses are not ordinary parent DRAT. Without a checked complete cover and
parent-level composition, incremental learning is just a solver claim.

No checker was installed for this review. Any build/use of new native checkers
requires its own approval and a separate pinned, isolated test. These options
cannot discharge the physical bridge.

## Narrow exclusions found: stop spending on these routes

### Literal Toeplitz/Z-SC is impossible already at K46

The existing encoding is $x_{(i,j),c}\leftrightarrow z_{j-i,c}$, for
$1\le i<j\le50$. For $a\le b$ with $a+b\le45$, vertices $0,a,a+b$ have edge
lengths $a,b,a+b$. That is a monochromatic triangle exactly when $a,b,a+b$ are a
monochromatic Schur triple; $a=b$ is valid. Schur's exact value $S(4)=44$
therefore excludes every such graph on K46 and larger, while saying nothing
about unrestricted K51. This is a theorem, not an interpretation of a timeout.

Sources:
[Xu–Xie–Exoo–Radziszowski, EJC 11 #R35](https://doi.org/10.37236/1788),
§2 (linear colourings and $S(4)=44$), and
[Heule, Schur Number Five](https://arxiv.org/abs/1711.08076), whose definition
includes $a=b$ and gives $S(k)\le R_k(3)-2$.

The coordinator independently checked the N44 witness for all 2,245 clauses
(class sizes 12,13,10,9) and replayed the exact N45 proof with
`s VERIFIED`: 1,924 core clauses, 570,302 core lemmas, **0 RAT lemmas**, final
empty addition, no warning in that default mode. A separate normalized `-U -W`
run hit its 60-second TIMEOUT and is **not claimed as verification**. The old
raw/default proof and its exact CNF hashes are not evidence for the whole old
wall family; the structural proof is the reason for the exclusion.

### Direct quartic-residue classes on $\mathbb F_{49}$

$\mathbb F_7[i]/(i^2+1)$, with primitive $g=1+2i$, gives four undirected
difference cosets of size 12. Direct enumeration finds **490 monochromatic
triangles in each class**, 1,960 in total. So $49+2$ cannot extend that seed.
Source check: [`cyclotomic_f49_control.py`](checks/cyclotomic_f49_control.py).

The positive block-Cayley K50 control remains distinct from ordinary group 51
Cayley/group-partition exclusions (Anabanti 2023). Its one exceptional-vertex
increment stayed UNKNOWN at a small cap. There is no case for enlarging that
cap without a new exact attachment reduction.

### Do not revive already rejected mechanisms

Global/pinned MCF is not generally row-preserving; exact arm-3 and its BCP
residual stayed OPEN at all tested cubes. Corrected static lex was much more
expensive. Conditional-boundary Sinz had a negative CPU measurement. Duggan's
full-vertex and critical-gray-edge compression do not transfer to K58. AlphaMaple
and the current MCTS gave no end-to-end advantage. Degree/profile-only counting
admits models, so it does not settle ChainReady. The guarded CCDCL candidate has
specific upstream unsoundness reports awaiting reproduction and is not safe for
a wall A/B. XOR has no useful cross-edge parity component here; its BNN output is
an equivalence, incompatible with the one-sided sender guards. Direct OPB has
very poor prior throughput, not just a missing solver installation. None of these
deserve a broader sweep as a follow-up to this literature review.

## Additional bounded negative controls

* All **12,544** pairs of exact 112-support choices for senders 18 and 19 were
  locally SAT in the induced local host model. A deliberately overlarge support
  was UNSAT, showing the control was nontrivial. This is not global SAT and does
  not justify sweeping the other sender pairs: [`pair_support_check.py`](checks/pair_support_check.py),
  [`pair_support_check.json`](checks/pair_support_check.json).
* A lazy GAC support relation is a legitimate possible optimization only if each
  explanation is independently derived. An IPASIR-UP callback's external clause
  is not automatically RUP or a DRAT consequence. Start with exhaustive relation
  checks and two independent derivations before any timing claim:
  [Fazekas et al., SAT 2023](https://doi.org/10.4230/LIPIcs.SAT.2023.8).
* The old K$_{62}$ further-critical-neighbourhood filter is not validated by the
  small physical controls, and order-15/16 attachments really occur. Any new
  attachment cover must include those branches or prove why K58 excludes them.

## What actually supports the recommendations

- Explicit input/query/file identities, not receipts with no checker.
- Parent/cube/regenerated clause identity, and actual suffix disjointness.
- Projected semantics and auxiliary-extension obligations rather than an
  equisatisfiability/implication swap.
- Exact physical senders and support sets; no inference from degree profiles alone.
- Confirmed SAT witness clauses model-by-model, not just a `SAT` status.
- `s VERIFIED` plus proper query/proof/hash handling, not a warning, a DERIVATION,
  an UNKNOWN, a budget stop, or a hash alone.
- Preserved standard-axiom Lean goals; no packaging of `native_decide` into the
  K58 standard-axiom core.

The seven accepted reports contain their original source links, exact formulas,
implementation estimates and abandonment rules. This directory adds the checked
small scripts and receipts; **no archives, full proofs, CNFs or solver binaries
are committed**. Large retained LRAT/DRAT artifacts remain in their original
ignored work directories. No wall sweep, new K51 campaign, or production solver
was run for this review.
