# Structural literature review: critical attaching sets at $K_{58}$

**Verdict.** There is one genuinely new, bounded research probe in this direction:
a *same-degree critical attaching cover*, obtained by adapting the packing step in
Fettes–Kramer–Radziszowski (2004) rather than importing its $K_{62}$ case list.
It is a possible new **global reduction architecture**, not a proved wall reduction
and not a proposal to solve more frozen rows. The old recursive embedding
computation does **not** port verbatim. I found no defensible new solver-throughput
experiment and no stand-alone way to discharge `ChainReady` in this direction.

The recommendation is therefore **conditional and modest**: reproduce the early
2004 census exactly, generate the additional $K_{58}$ branches, and stop if the
valid low-criticality branches do not have a small exact cover. Do not start a wall
sweep or a reimplementation of the final 2004 computation first.

## 1. Fixed repository and bibliographic status

I inspected repository HEAD `211dd0b2b705efef7481d5cace379fea99a2a0ca` and read
all five requested files. The distinction used below is important:

* there are **11 root degree profiles** in the frozen cover;
* seven are the unresolved wall profiles in `WALL_STRUCTURAL_NOTE.md`, namely those
  with at most two critical colours;
* the ordinary parent is a relaxation with
  `tables=True,total_critical=True,full_root=False`;
* physical `deg`/`Sends`, exact 112-support membership, coded-plus-automatic guard
  equalities and `ChainReady` remain semantic obligations. A CNF refutation alone
  does not supply them.

The accepted bounds remain $51\le R_4(3)\le62$. The current primary arXiv page
<https://arxiv.org/abs/2610.36648> identifies the v2 author as **Milos Tatarevic**,
submitted 27 October 2026 and revised 6 November 2026. This supersedes the old local
`M. Stojanović` author attribution. The preprint still **claims** $R_4(3)\le60$; I
did not independently DRAT-check its formulas and do not call that bound
established. The current upstream README
<https://github.com/milostatarevic/r3333-upper-bound> still describes two-solver
UNSAT results, not independent DRAT checking by this project.

No package was installed, no wall solver was run, and no repository file outside
`.ultramath/smx04thj8/m5/` was changed.

## 2. Primary methods actually read

### 2.1 Fettes–Kramer–Radziszowski (2004): attachment and recursive pullbacks

Susan E. Fettes, Richard L. Kramer and Stanisław P. Radziszowski, *An Upper Bound
of 62 on the Classical Ramsey Number $R(3,3,3,3)$*, **Ars Combinatoria 72 (2004),
41–63**. Publisher record:
<https://combinatorialpress.com/ars-articles/volume-072-ars-articles/an-upper-bound-of-62-on-the-classical-ramsey-number-r3-3-3-3/>.
Journal PDF:
<https://combinatorialpress.com/article/ars/Volume%20072/volume-72-paper-5.pdf>,
fetched SHA-256 `8b890745152526c08a6a0657a7627b34c75439821bdb5a397f41a1b0451aac55`.

The method relevant here has two distinct layers.

1. **Theorem 3.2 (printed pp. 47–48 / PDF pp. 7–8).** At $K_{62}$ choose six
   16-point same-colour neighbourhoods. If every pairwise intersection has at most
   two points, the successive-new-parts lower bound is
   $16+14+12+10+8+6=66>62$. Thus there are $u,v$ and a colour $\delta$ with
   $d_\delta(u)=d_\delta(v)=16$ and attachment
   $A=N_\delta(u)\cap N_\delta(v)$ of size $k\ge3$. A separate partition of
   $N_\gamma(u)$, where $\gamma=uv$, gives $k\le14$. The upper-bound step uses the
   $K_{62}$ fact that every colour degree is at least 13.
2. **Section 5 (printed pp. 54–61).** This is not gray-edge generalisation. Starting
   from two exact $K_{16}$ templates overlapping in $A$, it successively pulls back
   compatible embeddings of *other colour neighbourhoods*. Reported stages include
   533 marked colourings (Proposition 5.1, p. 55), 724 overlaps (Proposition 5.2,
   p. 56), $724\to129\to124$ after the critical-embeddability filter (pp. 56–57),
   454/452 one-vertex extensions (Proposition 5.3, pp. 58–59), 512/5 two-colour
   sequences (Proposition 5.4, pp. 59–60), 8,191 nonattaching-vertex pullbacks
   (Proposition 5.5, p. 60), and zero outputs in the final phase (p. 61). At each
   attaching vertex the filter uses **two further critical neighbourhoods**. That
   criticality hypothesis is as important as the template hypothesis.

**Text-access qualification.** The publisher PDF is an image-only 23-page scan;
`pdftotext -layout` produced zero text. I checked the exact page-mapped statements
against the retained, independently reviewed reconstruction at
<https://erdosproblems.ai/wiki/library/ramsey_theory/fettes_kramer_radziszowski_2004_upper_bound_62/theorem_3_2>
and the detailed documentary map at
<https://erdosproblems.ai/wiki/library/ramsey_theory/fettes_kramer_radziszowski_2004_upper_bound_62/section_5_pipeline>,
then rechecked the deductions above myself. I did not visually OCR the scan, rerun
the 2004 enumerations, or obtain the original 2004 programs. Those limitations are
part of the proposed falsification test, not hidden provenance. An attempted
ordinary author-upload check at ResearchGate was stopped by a CAPTCHA and was not
repeated.

### 2.2 Tatarevic (v2): reciprocity needs perfect balance

Milos Tatarevic, *An upper bound of 60 for the Ramsey number $R(3,3,3,3)$*,
arXiv:2610.36648v2. I fetched the actual TeX source from
<https://arxiv.org/src/2610.36648v2>, SHA-256
`753738e6f1f483366a313da6290c454a34fba41c202aedb4075caed807da6d81`.

Sections 2.3 and 6.1 derive ticket reciprocity only **after** excluding entrances
and using perfect balance. Connectivity and homogeneity then force a common critical
pair. Sections 6.2–6.4 use that pair to derive guards and visible opposite
neighbourhoods. None of those steps justifies assuming reciprocity, a common pair,
or exact visible neighbourhoods in the ordinary $K_{58}$ parent. This is a reason
not to relabel the proposed attachment route as another disguised balanced case.

### 2.3 Eliahou (2020): no local structural mechanism to transfer

Shalom Eliahou, *An adaptive upper bound on the Ramsey numbers $R(3,\ldots,3)$*,
**Integers 20 (2020), #A54**; arXiv:1912.05353,
<https://arxiv.org/abs/1912.05353> (v1 PDF fetched SHA-256
`a32b8cdab42f5f555731d890dd834dec86b35a7c3e67a28e1f371dfda3e5723e`).
Sections 2.1–2.4 optimise the standard recursion
$R_n(3)\le n(R_{n-1}(3)-1)+2$ using an assumed numerical value/bound for $R_4(3)$.
This is valuable after a new upper bound exists, but supplies no new attachment,
incidence or neighbourhood-packing premise for $K_{58}$. It is not a candidate.

### 2.4 Sánchez-Flores: bibliographic record checked, method not used

Adolfo Sánchez-Flores, *An improved upper bound for Ramsey number
$N(3,3,3,3;2)$*, **Discrete Mathematics 140 (1995), 281–286**, DOI
<https://doi.org/10.1016/0012-365X(93)E0187-9>. Crossref confirms this record and
its six references. ScienceDirect presented a human check, so I did not fetch the
article body and claim none of its internal lemmas as evidence. Semantic Scholar
also returned 429 during a metadata check and was not retried.

## 3. A new deduction: the same-degree critical attaching theorem

The following statement is **mine**, not a quotation from the 2004 paper.

> **CAT58.** Every triangle-free four-colouring of $K_{58}$ contains distinct
> vertices $u,v$, a colour $c$, and $s\in\{15,16\}$ such that
> $$d_c(u)=d_c(v)=s,\qquad k:=|N_c(u)\cap N_c(v)|\ge3.$$

### Proof

At every vertex the four degrees sum to 57. If all were at most 14 their sum would
be at most 56, so every vertex has a critical colour. Let
$C_c=\{x:d_c(x)\ge15\}$. Then $\sum_c|C_c|\ge58$, so some colour $c$ has
$|C_c|\ge15$. Among these vertices there are either at least five with $d_c=16$ or
at least six with $d_c=15$: otherwise there would be at most $4+5=9$ in total.

Take five 16-point neighbourhoods in the first case, or six 15-point
neighbourhoods in the second, and suppose all pairwise intersections had size at
most two. Their successive-new-parts lower bounds are respectively
$$16+14+12+10+8=60,\qquad 15+13+11+9+7+5=60.$$
Both exceed the 58 available vertices, a contradiction. Hence some pair has
intersection at least three; both degrees have the same exact value by
construction. $\square$

### The upper attachment bound at $K_{58}$

The old $k\le14$ conclusion is not automatic. Let $\gamma=uv$. Since $k\ge1$,
$\gamma\ne c$. Put $A=N_c(u)\cap N_c(v)$ and
$D=N_\gamma(u)\cap N_c(v)$. Then $A$ and $D$ are disjoint subsets of $N_c(v)$.
Partition $N_\gamma(u)$ into $\{v\}$, two sets $B_\alpha,B_\beta$ according to the
other two colours at $v$, and $D$. Each $B$ has at most five points because its
internal edges avoid two colours and $R(3,3)=6$. Therefore
$$|D|\ge d_\gamma(u)-1-5-5=d_\gamma(u)-11,$$
and consequently, with $d_c(v)=s$,
$$k\le s-\max(0,d_\gamma(u)-11).$$
Reversing $u$ and $v$ gives the same bound using $d_\gamma(v)$. The $K_{62}$ proof
has $s=16$ and $d_\gamma\ge13$, hence $k\le14$. At $K_{58}$, order 15 or 16
attachments must be retained unless a separate argument removes them.

The two template classifications apply to each $N_c(u)$ and $N_c(v)$ because both
are critical: $U/T$ for order 16 and a deletion $U^-/T^-$ for order 15. Their common
induced colouring on $A$ is genuine shared structure, not mere degree counting.

## 4. Prioritized next steps

### Priority 1 — bounded attachment-cover feasibility probe

**Class: (a) new mathematical closure possibility, currently unproved.**

**Purpose.** Determine whether CAT58 yields a useful global cover, before spending
solver time. If a complete attachment case cover were eventually refuted and its
coverage independently checked, it could replace the ticket-root/profile split. It
would eliminate the 11-profile partition **as a proof architecture**, not prove any
individual profile impossible. It would not by itself close a wall profile.

**Exact structural object.** Normalize $c,s,u,v,A$ as above; place the two critical
templates consistently on their shared induced colouring. Split at least into
15/15, 16/16, ordinary $3\le k\le14$, and high-overlap $k=15,16$ cases. Only then
apply whatever additional *critical* embeddings actually exist at the particular
attaching vertices.

**What is not allowed.** Do not import $\Upsilon_3,\ldots,\Upsilon_6$ or the old
counts 124/452/5/8191 as a $K_{58}$ cover. They depend on exact 16-neighbourhoods
and further criticality. Do not call a general $\le14$-vertex neighbourhood
embeddable in a critical template: the completeness statement concerns orders 15
and 16. Do not add an existential attachment as units to one existing frozen row;
the witnessing pair need not lie in that row's root/brace or satisfy its sender
semantics. A new case split must cover the **whole host colouring** and carry its
own semantic and proof obligations.

**Minimal reproducible programme.**

1. Formalize CAT58 and the displayed upper bound in a small standalone module.
   Test the existential selector against the physical controls in §5. Stop if the
   selected theorem requires ticket balance, a root profile, or reciprocity; those
   are not hypotheses.
2. From the pinned $U/T$ matrices, independently reproduce the old **marked/overlap
   census only**, seeking 533 and 724 weak-isomorphism classes. This calibrates
   canonicalisation and weak colour permutation before any $K_{58}$ case is built.
   Failure to match these counts is an immediate stop, not a discrepancy to explain
   away by asserting the old paper wrong.
3. Generate the $K_{58}$ marked/overlap families afresh, retaining 15/15 and high
   overlap. Record canonical representatives, the actual permutations, and an
   independent check that every labelled pair maps to a retained case. Do not run a
   wall solver during this phase.
4. At the first recursive-pullback stage, branch on the actual number of other
   critical colours at each attaching vertex. Emit one bounded, necessary-condition
   test only if its complete cover and auxiliary-extension semantics are explicit.

**Go criterion.** Continue only if (i) the reference 533/724 controls match,
(ii) every new orbit has a machine-checked covering witness, (iii) the complete
ordinary/high/low-criticality branch description stays below $10^4$ normalized
configurations in the early census (a declared engineering cut-off, not a
mathematical threshold), and (iv) at least one valid new pullback relation remains
that is not merely the current support tables or the already-rejected gray-edge
closure.

**Abandon criteria.** Stop if the reference census cannot be reproduced; if a
15/15 or high-overlap branch is omitted to preserve the old argument; if the early
census exceeds the declared cut-off; or if useful reductions require unclassified
noncritical $\le14$ neighbourhoods they do not justify. A SAT/OPEN/UNKNOWN result
on a relaxed fragment settles nothing either way. A physical countermodel to the
claimed *complete* cover would falsify the reduction, not prove $K_{58}$ exists.

**Cost/destructiveness.** The first test is enumerator/proof work, not CPU
saturation. The subsequent cover would be a new, independent and potentially large
artifact family: high implementation cost and high semantic risk. In particular,
existing frozen DRATs and `ChainReady` cannot simply be reused. This is why the
recommendation stops at the early feasibility census.

### Priority 2 — formalize only the reusable packing lemma

**Class: (c) certificate/proof engineering only.**

A small, independently checked CAT58 theorem and an executable witness extractor
are useful even if Priority 1 fails: they supply a second global object against
which later structural proposals can be tested. They are **not** themselves wall
progress and should not be presented as a new encoding. The expected implementation
cost is low compared with the census. The no-go test is simple: if the formal
statement quietly becomes $K_{62}$-only, assumes $H=w$, or asserts $k\le14$
uniformly, it is the wrong theorem.

### No solver-throughput candidate from this direction

There is no honest (b) item here. The attachment lemma changes the mathematical
case structure; testing it by giving a solver more time on an existing frozen row
would test the wrong object.

## 5. Bounded physical calibration actually run

`fit_checks.py` reads the five existing physical colourings, independently checks
symmetry and absence of monochromatic triangles, enumerates same-colour/same-degree
pairs with $k\ge3$, and counts those with at least two *other* critical colours at
both endpoints. It uses no SAT solver. `fit_checks.json` is its exact output.


| artifact | eligible pairs | $3\le k\le14$ | maximum $k$ | pairs with two other critical colours at both endpoints |
|---|---:|---:|---:|---:|
| `n48_z4z4_f0.col` | 768 | 720 | 15 | 0 |
| `k49_from_n48_m5.col` | 516 | 468 | 16 | 0 |
| `k50_z4z4_m6.col` | 480 | 448 | 16 | 0 |
| `k50_blockcayley_Z4xZ4_m4.col` | 464 | 428 | 16 | 0 |
| `k50_sanity_f2.col` | 424 | 380 | 16 | 0 |

Two conclusions are warranted, and only two:

* high-overlap attachments cannot be discarded by a generic local-degeneracy
  assertion; order-16 identical neighbourhoods occur in actual physical controls;
* the old two-further-critical-colours filter has no direct validation in these
  controls. A $K_{58}$ implementation must measure and cover low-criticality
  branches, not silently assume the $K_{62}$ profile arithmetic.

These small orders are semantic controls, **not** evidence about existence or
nonexistence at $K_{58}$. They also already contain ordinary $k\le14$
alternatives, so retaining such a case split is not vacuous.

Reproduce from the actual paths (shell, no external packages):

```sh
REPO=/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo
WORK="$REPO/.ultramath/smx04thj8/m5"
cd "$WORK"
python3 fit_checks.py > .scratch/fit_checks.stdout
sha256sum fit_checks.py fit_checks.json
```

The resulting script/result hashes at this submission are
`68bc424cc2369f311d9835fddf266d2615db163ed987f39f6130da35610ae0f0` and
`52c66878c45384b1a9f1ce35ca4a43f3c2bc2c7d2cc66346c38f76d508285029`,
respectively.

## 6. Labelled no-go items

1. **Direct $K_{62}$ attachment transplant.** False parameter transfer: order-15/16
   overlaps occur, and the $k\le14$ proof uses minimum degree 13.
2. **“Two further critical neighbourhoods at every attachment.”** Not a $K_{58}$
   theorem. This invalidates direct use of the old 124 and later-stage counts, not
   just an encoding detail.
3. **Colour-filtered tickets imply one full-return critical arm.** Unsupported. The
   identity $\sum_vH_c(v)=\sum_{v:d_c(v)\ge15}d_c(v)$ is valid, but its vertex with
   $H_c\ge w_c$ can have $d_c\le14$. Additional noncritical-receiver accounting is
   indispensable; no full arm follows as stated.
4. **Degree/profile-only contradiction.** Excluded by the campaign's SAT models of
   degree-level count systems. CAT58 is relevant only because it forces two exact
   overlapping template embeddings, not because it supplies another degree average.
5. **Generic local exclusion of identical/near-identical attachments.** The controls
   realize $k=15$ and $k=16$. Any new exclusion must use the order-58 global
   hypotheses explicitly; a local counterexample cannot be declared impossible.
6. **Assert `ChainReady`, exact 112-support membership, or guard equalities from
   CAT58.** These are unrelated per-parent semantic obligations. A new global cover
   might bypass them only by taking on its own complete physical realization proof;
   it does not discharge them.
7. **Old FKR computations as a ready-made proof or archive.** No original code or
   independently replayed enumeration was obtained here. The reported 533/724/etc.
   are methods to calibrate, not evidence to import on trust.

## Bottom line

CAT58 is a new, elementary structural fact with a clean physical fit and no
reciprocity hypothesis. It justifies a **small exact enumeration experiment**, not a
bound claim. If the extra 15/15, high-overlap and low-criticality branches remain
compact and admit valid recursive pullbacks, it opens a genuinely different cover
of all 11 profiles. If they do not, the early test closes this direction cheaply.
Everything stronger would currently be assertion rather than evidence.
