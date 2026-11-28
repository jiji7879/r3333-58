# R_4(3): lower-bound construction review after the SAT/Lean wall campaign

**Direction:** mathematical lower bounds beyond Cayley/group partition (member m7).
**Repository inspected:** HEAD `211dd0b2b705efef7481d5cace379fea99a2a0ca` (the
required `211dd0b`).  I read all five required campaign documents before running
any checks.  This is a construction/literature review, not a wall closure and not a
new Ramsey bound.

## Bottom line

I found **no new candidate worth prioritising for the K58 wall, ChainReady, or the
11 small wall profiles**.  The lower-bound constructions examined here do not
supply sender criticality, the exact 112-support catalogue, coded/physical guard
equalities, or the parent/suffix semantic bridge.

There is nevertheless one useful, exact corrective result:

> **The repository's literal $j-i$ zebra/Toeplitz family is already impossible on
> $K_{46}$, hence on $K_{51}$.  Do not run the proposed four-leaf Toeplitz K51
> follow-up.**  This follows from the exact Schur number $S(4)=44$, not from a
> failed search.  The old 50,000-conflict UNKNOWN has no bearing on the truth of
> this exclusion.

A narrow Chung-shaped block-Cayley fit test remains undecided after its single
short cap.  It does **not** earn a larger budget on current evidence.  A direct
$\mathbb F_{49}$ residue-class analogue fails on the 49-vertex seed itself.

### Priority and disposition

| Priority | Item | Type and status | Disposition |
|---|---|---|---|
| 1 | Literal $j-i$ Toeplitz / Z-SC | **Exact family exclusion** | Cancel permanently as a K51 route.  This is not a global K51 UNSAT and changes no bound. |
| 2 | $\mathbb F_{49}$ quartic-residue seed | **Falsified construction template** | Do not try $49+2$: the seed has 1,960 monochromatic triangles. |
| 3 | Three blocks over $\mathbb Z_4^2$ plus three free exceptional vertices | **Model finding only; undecided** | One 60 s cap expired with no verdict.  Resume only with a new exact attachment reduction, never merely a larger cap. |
| 4 | Product/module, ordinary Cayley, direct Paley/cyclotomic transfer, and generic local repair | **No-go or no new candidate** | Do not resurrect.  Their precise scopes are separated below. |

No solver-throughput experiment for the K58 parent and no new certificate workflow
is recommended by this direction.

## 1. Exact exclusion: Toeplitz is a Schur partition problem

### 1.1 Primary sources and their exact hypotheses

1. **Xu Xiaodong, Xie Zheng, Geoffrey Exoo, Stanislaw P. Radziszowski,
   "Constructive Lower Bounds on Classical Multicolor Ramsey Numbers,"**
   *The Electronic Journal of Combinatorics* **11** (2004), #R35.
   DOI https://doi.org/10.37236/1788 ; official article and PDF:
   https://www.combinatorics.org/ojs/index.php/eljc/article/view/v11i1r35

   Section 2, PDF p. 3, defines a Schur partition of $[1,n]$ into sum-free sets
   and gives the construction: if the colour of the edge $\{u,v\}$ is determined
   by the class containing $|u-v|$, a Schur partition of $[1,n]$ gives a
   monochromatic-triangle-free colouring of $K_{n+1}$.  The same paragraph calls
   this a **linear colouring**.  It records the exact Schur numbers for one through
   four colours as $1,4,13,44$.  This is the key semantic bridge, not an analogy.

2. **Marijn J. H. Heule, "Schur Number Five,"** AAAI 2018; arXiv version
   https://arxiv.org/abs/1711.08076 (author's proof/data page:
   https://www.cs.utexas.edu/~marijn/Schur/).  PDF pp. 1--2 defines $S(k)$ as
   the largest $n$ admitting a $k$-colouring of $1,\dots,n$ with no monochromatic
   $a+b=c$, and explicitly recalls $S(4)=44$ from Golomb and Baumert (1965).
   The example uses $1+1=2$, so $a=b$ is included.  A footnote warns that the
   alternative "smallest forcing $n$" convention shifts the numbers by one.

3. **Fred Rowley, "Constructive lower bounds for Ramsey numbers from linear
   graphs,"** *Australasian Journal of Combinatorics* **68(3)** (2017), 385--395.
   Official record/PDF: https://ajc.maths.uq.edu.au/v68.p385

   Section 2 defines *linear* by dependence only on $|j-i|$ and *cyclic* by the
   additional identification of lengths $d$ and $m-d$.  Theorem 3.1 combines two
   **linear** Ramsey graphs with disjoint colour sets into another linear graph on
   $2mn-m-n+1$ vertices.  This confirms that dropping cyclic symmetry does not
   escape the Schur/Toeplitz semantics.  His tables report best available linear
   constructions; the impossibility at 46 comes from $S(4)=44$, not from a table
   of best attempts.

### 1.2 Proof of the exclusion

The local Duggan assessment's Z-SC encoding imposes
$x_{(i,j),c}\leftrightarrow z_{j-i,c}$ with $1\le i<j\le50$ and four colours.
Thus its $z_{d,c}$ are exactly a four-colouring of lengths $d=1,\dots,50$.

Already a putative good colouring on the first 46 vertices would colour lengths
$1,\dots,45$.  For any $a\le b$ with $a+b\le45$, consider the three **distinct**
vertices $0,a,a+b$.  Their edge lengths are
$$a,\qquad (a+b)-a=b,\qquad a+b.$$
Allowing $a=b$ is essential and valid: the vertices are $0,a,2a$.  A
monochromatic Schur triple is therefore exactly a monochromatic triangle.  By
$S(4)=44$, every four-colouring of $[1,45]$ has such a triple.  Consequently:

$$\boxed{\text{No good linear/Toeplitz colouring of $K_{46}$ exists, and hence
none exists on any larger $n$, including $K_{51}$.}}$$

Hereditary restriction of the first 46 vertices proves the larger-$n$ claim.
There is no implication in the reverse direction about non-Toeplitz colourings,
and there is no proof here that general K51 is unsatisfiable.

### 1.3 Independent bounded controls actually run

A direct encoder, [toeplitz_schur_control.py](toeplitz_schur_control.py), emits
one-hot colour variables, every $a\le b$ Schur clause (including $a=b$, with
syntactic duplicates removed), and the palette-symmetry-breaking pin
$\operatorname{colour}(1)=0$.  It does not build a Ramsey wall formula.

| Query | Result and independent check |
|---|---|
| $N=4$, 2 colours | SAT, as required by $S(2)=4$ |
| $N=5$, 2 colours | UNSAT, as required by the same boundary |
| $N=44$, 4 colours | SAT: 176 variables, 2,245 clauses, CaDiCaL process time 0.13 s.  A separate arithmetic parser verified all 2,245 clauses, exactly one colour per integer, the palette pin, and no Schur triple.  Class sizes were $12,13,10,9$. |
| $N=45$, 4 colours | UNSAT: 180 variables, 2,340 clauses, CaDiCaL 2.1.2 real time 11.81 s. |

For N45, an ASCII DRAT was independently replayed with the repository's
`tools/color-resolved-wallcc/bin/drat-trim` in default DRAT mode (not restricted
RUP mode).  It printed `s VERIFIED`: 1,924 of 2,340 clauses in core, 570,302 of
726,564 lemmas in core, 13,336,310 resolution steps, **0 RAT lemmas in core**,
verification time 16.965 s.  No warning appeared.

* CNF SHA-256: `33b572b0d94e1acaf016036977de87a3c58ad94f749c5041b242d170960aacb4`
* ASCII DRAT SHA-256: `9f0bfe060a0dfa43f7bcff8a2452ce9caa1a27f17344b45c4535cd2f7b31fee6`
* DRAT size: 77,510,575 bytes.
* Checker-log SHA-256: `58fe411dfc1eb964ca19694e1fbea5ec12ba7b949f332f7f418e8c91f2534069`

Reproduce from `.ultramath/smx04thj8/m7/` (CaDiCaL uses exit 10 for SAT and 20
for UNSAT, so do not treat either as a shell-level failure):

```sh
ROOT=$(git rev-parse --show-toplevel)
mkdir -p .scratch/schur-replay
python3 toeplitz_schur_control.py 44 4 .scratch/schur-replay/n44.cnf
python3 toeplitz_schur_control.py 45 4 .scratch/schur-replay/n45.cnf
/opt/lean/bin/cadical .scratch/schur-replay/n44.cnf > .scratch/schur-replay/n44.log 2>&1
/opt/lean/bin/cadical -q --no-binary .scratch/schur-replay/n45.cnf \
  .scratch/schur-replay/n45.drat > .scratch/schur-replay/n45.log 2>&1
"$ROOT/tools/color-resolved-wallcc/bin/drat-trim" \
  .scratch/schur-replay/n45.cnf .scratch/schur-replay/n45.drat -t 60
```

**Decision:** abandon this construction family and cancel the four proposed
$z_2$ leaves.  A DRAT for the small control is not a DRAT lifting of the old
whole-parent Z-SC formula; none is needed for the direct Schur exclusion.  I did
not formalise $S(4)=44$ in Lean.

## 2. Chung-shaped block Cayley with free exceptional vertices

### 2.1 What the source actually supplies

**William J. Wesley, "New bounds for some small multicolor Ramsey numbers,"**
arXiv:2509.03784v1 (2025).  Metadata/full text:
https://arxiv.org/abs/2509.03784 and https://arxiv.org/html/2509.03784v1

Section 2.1 defines a block-Cayley adjacency matrix whose block $C_{ij}$ is a
directed Cayley graph for each ordered block pair.  Dependencies can therefore
vary by block pair; this is not ordinary Cayley on the 48 core vertices.
Section 2.2 says that to extend by $c$ vertices one uses the full exactly-one
and forbidden-subgraph CNF on all $bn+c$ vertices, adding block-Cayley clauses
only on the induced first $bn$ vertices.  A model of this restricted formula is
a model of the unrestricted formula; an UNSAT result would exclude only the
restricted family.  Section 2.2 also recalls Chung's 3-blocks-of-16 plus two
vertices over $\mathbb Z_4\times\mathbb Z_4$.

The existing generator `.ultramath/smwiiyj7u/m4/blockcayley.py` implements that
extension: the first 48 vertices are three order-16 blocks; every edge incident
to an exceptional vertex is free (apart from the global palette symmetry pin).
I ran only the $\mathbb Z_4^2$ group and the next exceptional-vertex count,
not a group or budget sweep.

### 2.2 Measured fit test

| Exceptions | Exact formula | Outcome |
|---|---|---|
| 2 ($K_{50}$) | 88 classes, 19,600 triangles, 79,016 clauses | SAT in 2.26 s; `tools/verify_coloring.py` said `VALID: 50 vertices, 4 colours, no monochromatic triangle`.  Certificate SHA-256 `67d0435c883311ea0c91201fd586d84c3009ba9ea20a0f137ba94ac044b8c252`. |
| 3 ($K_{51}$) | 90 classes, 20,825 triangles, 83,930 clauses | External 60 s cap expired, 59.80 s user CPU, 78,252 KiB peak RSS.  No solver verdict, model, or DRAT. |

**Interpretation:** only that the encoder has a positive control and that the
next case did not fall in one minute.  It is not evidence of absence, and it is
not a solver-throughput gain for any wall formula.  The 60 s run is deliberately
not repeated at a larger cap.

**Abandon/resume criterion:** abandon production compute unless someone first
supplies a new exact reduction of the residual attachment system (with a small
known-SAT and known-UNSAT calibration).  A future SAT model must pass the original
K51 physical checker; a future UNSAT would need an independently replayed proof
and would concern only this block-restricted family.  Neither result would
advance ChainReady or refute any of the 11 wall profiles.

## 3. Direct residue-class / Paley-like check

The same Xu et al. paper (Section 2, PDF pp. 2--3) describes a good three-colouring
of $K_{16}$ on $\mathrm{GF}(2^4)$: $\{u,v\}$ receives colour $i$ when $u-v$ lies
in the $i$th cubic-residue class.  This is an exact algebraic template, not an
invocation of an unread association-scheme theorem.

I tested its direct four-colour analogue on $\mathbb F_{49}$ using
$\mathbb F_7[i]/(i^2+1)$.  The script
[cyclotomic_f49_control.py](cyclotomic_f49_control.py) verifies the field
operations, finds primitive $g=1+2i$, forms the four cosets of $\langle g^4
\rangle$, checks $-1\in\langle g^4\rangle$ so colours are undirected, and colours
every edge by the coset of its additive difference.  Each class has 12 elements,
well below the degree ceiling 16.

The direct exhaustive result is

| colour | monochromatic triangles |
|---|---:|
| 0 | 490 |
| 1 | 490 |
| 2 | 490 |
| 3 | 490 |

Thus the K49 seed itself has 1,960 bad triangles, including one explicitly
reported by the checker.  Adding two vertices cannot remove them, so **no $49+2$
extension of this template exists**.  Recolouring/deleting parts of the seed
would be a different unstructured perturbation, not a remaining application of
this residue mechanism.  This test used only 28 ms of CPU and no SAT solver.

Ordinary regular-group cyclotomic/Cayley constructions on exactly 51 vertices
are separately excluded.  C. S. Anabanti, **"A counterexample on a group
partitioning problem,"** Birkbeck Pure Mathematics Preprint Series #37 (2017),
https://eprints.bbk.ac.uk/id/eprint/26765/ , proves that the group of order 51
cannot be 4-partitioned into symmetric product-free sets (see the C51 argument
concluding at PDF p. 6).  That hypothesis does not cover Wesley's block-pair
formula with free exceptions, which is why the preceding section is not a repeat.

## 4. Graph decomposition, perturbation, and local repair

### Product/module constructions

Xu et al.'s Section 4 construction theorem builds colourings on Cartesian products
with constant between-block colour rules.  Such a decomposition cannot manufacture
the needed K51 object.  Here is the self-contained fit argument behind the
repository's primitivity warning.

Let $P$ be a nontrivial module of size $s=|P|\ge2$: every outside vertex sees
all of $P$ in one colour.  Let $j$ be the number of colours on the cut.  Inside
$P$ none of those $j$ colours can occur, or an internal edge of that colour plus
an outside vertex makes a monochromatic triangle.  Hence
$$s\le R_{4-j}(3)-1.$$
A vertex inside $P$ partitions its $n-s$ external neighbours into at most $j$
colour classes, each of size at most 16 (its colour neighbourhood otherwise
requires a good 3-colouring of $K_{17}$), giving $n-s\le16j$.  For $j=1,2,3,4$
these bounds cap $n$ respectively by $32,37,50,65$, and $j=4$ forces $s=1$.
So no target colouring with $n\ge51$ has a nontrivial module.  Substitution,
blow-ups, and the Abbott/Song-type product rule all create precisely such
modules.  This is a structural exclusion, not a solver failure.

### Existing near-miss and soft-pin repairs

The repository already has an exact Hamming-sphere exclusion through five changes
around the one-defect K51 record, extensive conditional extension exclusions, and
UNKNOWN soft-constraint pilots.  Nonminimal cores released 65 edges at once in
the 20% run.  Fresh-vs-incremental comparison and small/minimised-core scoring
were already recommended by the Duggan assessment; they are not new candidates
from this review.  No local-search stagnation is treated as UNSAT.

### Anti-Ramsey/general nonlinear suggestions

The target is a partition of the edges of $K_n$ into four triangle-free graphs.
Anti-Ramsey constraints concern rainbow rather than monochromatic copies; no
primary theorem consulted here supplies a correspondence that would construct
such a partition at 51 vertices.  I therefore make no recommendation from an
anti-Ramsey title or from unstructured random colouring.  (For scale only, a
uniform random four-colouring has $\binom{51}{3}/16=1301.5625$ expected
monochromatic triangles, not a near-miss-like landscape.)

## 5. Classification against the campaign's requested categories

**(a) New mathematical closure possibility.**  The Toeplitz Schur exclusion is a
real family closure, and the module argument excludes product constructions.
Neither is a new Ramsey bound.  No new mathematical route to general K51, to a
K58 wall profile, or to ChainReady was found.

**(b) Solver-throughput experiment.**  None is proposed.  The block-Cayley runs
were model-finding controls, not a wall A/B.  There is no evidence that porting
them to host clauses, fixed units, guarded senders, support events, bounds, split
points, or optional MCF would improve a wall solve.

**(c) Certificate/proof engineering only.**  The verified small Schur CNF/DRAT is
a reproducible control for this exact family exclusion.  It supplies no whole
parent assembly, support criticality, guard-set equality, ChainReady fact, or
large-proof compression technique.  No new proof-engineering direction is claimed.

## 6. Frozen status and source limitations

* The accepted/frozen bounds remain $51\le R_4(3)\le62$ as required.  The current
  arXiv abstract page for https://arxiv.org/abs/2610.36648 was read in this run:
  it lists **Milos Tatarevic**, v1 27 Oct 2026 and v2 6 Nov 2026, and claims an
  upper bound of 60.  That remains a preprint claim, not an established bound or
  an independently DRAT-checked result here.  I make no identity inference about
  the older local author-name discrepancy.
* Crossref verified the original Chung metadata, DOI
  `10.1016/0012-365X(73)90125-8`, but ScienceDirect returned a human-check
  challenge.  Crossref also verified Golomb--Baumert, *Backtrack Programming*,
  JACM 12(4) (1965), DOI `10.1145/321296.321300`; the ACM full text returned a
  human-check challenge.  I do not quote either unread full text.  The needed
  Schur relation/value was read in Xu et al. and Heule, and independently
  controlled above.
* The RIT mirror of Xu et al. returned HTTP 403; the official EJC DOI page and PDF
  were accessible.  No external packages were installed.  No wall sweep, K51
  general search, group sweep, or rejected long computation was launched.
