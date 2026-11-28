# Duggan symmetry methods: exact transfer, corrected encoder, and a negative K58 pilot

## Bottom line

The repository's previous `results/hailmary-lex` experiment did **not** add a
lexicographic symmetry break. Its comparator is existentially vacuous, so the
reported 3% conflict difference is only a solver-trajectory difference. That
experiment cannot support its conclusion that orbit redundancy is unimportant.

There is a genuine Duggan/Codish method applicable to frozen multicolour rows:
partition-preserving improved lex constraints $sb^*_\preceq(A,P)$. I give the
exact stabilizer theorem and a corrected one-hot CNF encoding below, validate
it exhaustively on small instances, and verify a tiny UNSAT refutation with
strict DRAT. On an exact historical K58 row, however, the corrected full rule
was about **3.01 times slower per 200,000-conflict tranche** and performed
**4.75 times as many propagations** as the bare formula. Nothing closed. The
present evidence therefore does **not** support a production deployment.

No K58 row or profile was closed here, no K51 model was found, and the
published bounds remain $51\le R_4(3)\le 62$. This is an encoding audit and a
small validated pilot, not a Ramsey result.

Sources read directly: Duggan, sections 4, 5, 7, 8 and 11 of the supplied PDF
(SHA-256 `58665d3b71e1e5452a6afdd6d8087bfb7df99daf6566263addfc2f1a905109e8`),
and Codish--Miller--Prosser--Stuckey, *Constraints for symmetry breaking in
graph representation* (2019), especially Theorems 4 and 6 and the multicolour
discussion. The primary paper is at
<https://eprints.gla.ac.uk/165865/> (DOI `10.1007/s10601-018-9294-5`).
Duggan credits that paper for the static constraints. His SMS canonicity order
is different from MathCheck's, so their witnesses and verifier implementations
must not be interchanged.

## 1. The historical lex comparator is vacuous

`results/hailmary-lex/hm.py:71-102` creates three families of fresh variables:
`lt`, `peq`, and `p`. Every generated clause contains a positive fresh
variable:

* each less-than implication ends in `lt`;
* each prefix implication ends in `peq`;
* each disjunct production contains positive `p` (even when it contains
  negative `lt` or `peq`);
* the final big clause contains positive `p` and `peq` literals.

Consequently, **setting every fresh variable to TRUE satisfies every added
clause, for every assignment of the physical edge variables**. The added CNF
therefore has exactly the same physical satisfying assignments as the input;
it does not enforce either strict or non-strict lex order.

This is not an inference from a SAT timeout. The direct checker
`work/check_historical_vacuity.py` imports the repository's actual `hm.py`, and
checks this structural property on its 23 clauses for a two-witness comparator.
It also checks all 7,404 added clauses in the regenerated exact case-7 formula.
The independent exhaustive semantic control found every one of the 256 pairs
of two-witness one-hot rows accepted, including 120 with left row greater than
right row. The first counterexample to the claimed comparator is
$(0,1)\not\preceq(0,0)$.

The satisfiable `probe3.py` control could not detect this: retaining SAT is only
one half of comparator correctness. A comparator must also reject non-lex
physical rows. This defect is different from the earlier strict-lex,
over-constraining bug recorded in `review/WALL_15141414_SWARM.md`; the two must
not be conflated. The present `hm.py` addition is vacuous, not unsoundly strong.
Thus an UNSAT proof of its augmented formula would still imply UNSAT of the
unaugmented formula, but there was no symmetry-breaking benefit to measure.

The old twin-pair calculation itself was checked independently against the
full action on **signed**, not merely positive, units. For case 7 all 100
reported transpositions, and all 12 used in the matching, preserve the 338
signed units exactly. The defect is the comparator, not that twin inventory.

## 2. The exact static transfer that *is* valid

Let $P=(P_1,\ldots,P_r)$ be an **ordered partition** of the vertices, with a
singleton part for every non-twin vertex, and let
$G=\prod_k\operatorname{Sym}(P_k)$. Assume every permutation in $G$ preserves
the host clauses and all frozen signed units (and, for an extended parent,
that all other constraints are invariant after suitable reassignment of their
auxiliaries). Let $A$ be the symmetric integer adjacency matrix whose entries
are the physical colour numbers.

Codish et al.'s partitioned predicate requires, for every $i<j$ in one part,
$$
A[i]\setminus\{i,j\}\;\preceq\;A[j]\setminus\{i,j\},
$$
where $\preceq$ is ordinary non-strict lex order in increasing column order.
Let $S(P)$ be the conjunction of these constraints.

**Stabilizer-lex lemma.** $F\land S(P)$ is satisfiable if and only if $F$ is
satisfiable. Indeed, any model can be replaced by the lex-least member of its
$G$-orbit; $G$-invariance preserves $F$. If some compared row pair were out of
order, swapping its two vertices would give a strictly smaller matrix in that
orbit, contradicting minimality (Codish et al., Theorem 6). This argument uses
no automorphism of the hypothetical colouring: it chooses an isomorphic
representation of an assignment.

For one-hot physical literals $X_{w,c},Y_{w,c}$ at witness $w$, the corrected
encoding uses
$$
L_w\Longleftrightarrow X_w<Y_w,\qquad
E_w\Longleftrightarrow E_{w-1}\land(X_w=Y_w),\qquad E_{-1}=\top.
$$
The less-than equivalence is encoded by
$$
(c<d):\;\neg X_{w,c}\lor\neg Y_{w,d}\lor L_w,\qquad
(c\ge d):\;\neg L_w\lor\neg X_{w,c}\lor\neg Y_{w,d}.
$$
The host's exactly-one colour per edge makes these 16 clauses sufficient in
both directions. Prefix equality is made fully bidirectional, including
$E_w\to E_{w-1}$. Finally, with $P_0\leftrightarrow L_0$ and
$P_w\leftrightarrow E_{w-1}\land L_w$ encoded in both directions, assert
$$E_{m-1}\lor\bigvee_{w=0}^{m-1}P_w.$$
These are the clauses in `work/symmetry_pilot.py::lex_clauses`. The missing
reverse directions, especially $P\to E_{w-1}$ and $P\to L_w$, are precisely
what made the historical version vacuous.

For exact case 7 of profile $(16,14,14,13)$, kinds `T---`, arm 0, charge 1,
placements `(0,0,0)`, the signed-unit stabilizer contains three complete twin
cells:
$$[22,30],\qquad[36,44],\qquad[50,57].$$
They generate $S_9\times S_9\times S_8$, of order
$5{,}309{,}413{,}982{,}208{,}000$. The old matching used only 12
transpositions. The full corrected experiment uses all 100 within-cell pairs.
Neither number is an achieved pruning ratio: $sb^*_\preceq$ is an incomplete
static symmetry break, and its actual accepted fraction is instance-dependent.

## 3. Validation actually performed

### Semantic and orbit controls

`work/validation.json` records:

* all 256 two-witness pairs of four-colour one-hot rows: exact agreement of
  the corrected CNF with non-strict integer lex order, after exhaustively
  enumerating every auxiliary assignment;
* the historical comparator accepted all 120 non-lex pairs in that set;
* every one of $4^6=4096$ integer colourings of $K_4$, separately for full
  $S_4$, the ordered partition $S_2\times S_2$, and $S_3\times S_1$:
  the explicitly computed lex-least orbit member satisfies $sb^*_\preceq$;
* equal rows survive, excluding the earlier strict-order failure mode.

The numbers of $K_4$ partition orbits were 276, 1,216 and 816 respectively.
The accepted matrix counts were 331, 1,376 and 816; this also demonstrates
that the static predicate need not select exactly one member per orbit.

### Strict refutation control

`work/symmetry_pilot.py certificate` encodes $R(3,3)=6$ as a four-colour host
on $K_6$ with colours 2 and 3 forbidden, then adds all 15 corrected $S_6$
constraints. Kissat returned UNSAT. Independently running `drat-trim` without
`-w` consumed the entire 31,120-byte proof and returned exactly `s VERIFIED`,
with exit 0 and no warning or error. The formula had 240 variables and 2,360
clauses; zero RAT lemmas occurred in core. This is only an encoder/certificate
control, not a K58 result.

For a wall row, a DRAT proof of $F\land S(P)$ would still need the independent
stabilizer-lex lemma above to infer UNSAT of $F$. The cut is SAT-preserving,
not logically entailed by $F$. A SAT model of the augmented formula can simply
be projected back to the physical variables and re-evaluated on $F$.

## 4. Exact K58 pilot: corrected symmetry costs more than it saves here

The case was regenerated from the same frozen engine used by the historical
experiment. Bare dimensions match exactly: 6,612 variables and 135,333
clauses. Case 7 has 338 signed units, 41 negative. All runs used the same
Kissat binary, a 200,000-conflict cap, and seeds 0 and 1. Every result below
is **OPEN at the cap**, not SAT or UNSAT.

| case-7 arm | lex pairs | variables | clauses | median wall seconds | median propagations |
|---|---:|---:|---:|---:|---:|
| bare | 0 | 6,612 | 135,333 | 4.285 | 24.367M |
| historical vacuous matching | 12 | 8,628 | 142,737 | 4.373 | 23.976M |
| corrected matching | 12 | 8,628 | 159,513 | 6.215 | 35.315M |
| corrected full partition $sb^*$ | 100 | 23,412 | 336,833 | 12.896 | 115.809M |

Raw wall seconds for bare were 4.239/4.330, historical 4.239/4.506, corrected
matching 6.074/6.356, and corrected full 12.489/13.303. Full $sb^*$ therefore
had time ratio 3.010 and propagation ratio 4.753 relative to bare. Even the
corrected matching had time ratio 1.450. Full decisions were not notably lower
(median 2.062M versus 1.995M bare). Input hashes and every raw measurement
are in `work/built.json` and `work/timings.jsonl`.

This rules out the old experiment as evidence about orbit redundancy. It also
shows that the straightforward corrected static encoding has a substantial
propagation-cost barrier on this row. It does **not** prove that a more compact
encoding, dynamic SMS, a longer run, or another profile cannot help.

## 5. Applicability by target

### (i) Proving small-wall rows UNSAT

The static theorem transfers exactly, but the naive static implementation is
not presently a material improvement. More importantly, stock MathCheck/PySMS
**cannot simply be run on a frozen row as though every vertex permutation were
allowed**. Duggan section 7 makes exactly this point for graph gluing: his CAS
permutations affect the entire immutable matrix, and he says this would have
to be resolved by restricting permutations to the stabilizer. Pinned arms,
marked senders, and physically coloured pivots are precisely such immutable
data here.

Before applying any symmetry to a current augmented parent, signed-unit
invariance alone is insufficient. Candidate sets, selector guards, degree
counters, and support tables must either be invariant literally or possess an
explicit auxiliary reassignment. My wall timing used only bare `host+units`;
it did not validate those current auxiliary families.

### (ii) Lemma L or profile reduction

No help follows. Relabelling preserves every colour-degree profile and
creates no incidence relation. It cannot prove that a vertex has three critical
degrees at least 15, cannot remove any of the 11 degree profiles, and supplies
no substitute for the required incidence/global counting argument.

### (iii) Finding a K51 colouring

The same SAT-preservation theorem applies to unrestricted and pinned K51
searches, using only the stabilizer of the pins actually imposed. An encoding
has relabelling symmetry even if no good colouring has a nontrivial geometric
automorphism; these are different statements. In particular, impossibility of
an order-3 colouring automorphism is not a reason to ban quotienting labelled
SAT assignments.

There is no positive K51 experiment here. Corrected static comparators made
the K58 control slower, so a generic K51 rollout is not justified. Symmetry
also does not address the measured exhaustive-split/gluing obstruction (at
least 1,139 free variables); it would have to earn its keep on a small matched
model-finding control rather than be assumed beneficial.

### (iv) Proof-certificate tooling

Correct static constraints require no CAS callback, but their independent
stabilizer soundness theorem is part of the proof, in addition to DRAT replay
of the augmented formula. Dynamic SMS/CAS adds a second obligation for every
trusted symmetry clause:

1. retain its explicit vertex permutation $q$ and the exact canonicity order;
2. prove $q$ lies in the stabilizer of all frozen physical data and all
   auxiliary semantics, not merely that $q\in S_{58}$;
3. independently apply $q$ to the blocked partial matrix and verify strict lex
   decrease, including the paper's rule for unassigned entries;
4. retain and strictly check the ordinary DRAT stream, with no suppressed
   warnings and no inference from `OPEN` or `s DERIVATION`.

A permutation that merely establishes canonicity up to unrestricted graph
isomorphism is not a valid witness on a frozen arm/pivot row.

## 6. Concrete next experiments (small controls only)

1. **Correct the historical record first.** Mark the 3% `hailmary-lex` result
   as a vacuous-encoding measurement and withdraw its “hardness is not orbit
   redundancy” conclusion. Use the direct `vacuity.json` check as a regression
   test. Do not resurrect the separate strict-lex encoder.
2. **Measure pruning independently of CDCL speed.** On a small satisfiable
   pinned instance, enumerate physical models before/after the corrected
   comparator and verify every original orbit retains a representative. Only
   then compare a more compact order-coded comparator with the current
   one-hot comparator on case 7 at the same 200,000-conflict cap. My data do
   not justify simply increasing the budget of the 336,833-clause full form.
3. **Use one current exact parent, not a sweep.** Recompute its stabilizer on
   all physical and auxiliary semantics, record parent/cut hashes and fresh
   variable bounds, and run bare versus the cheapest corrected matching at one
   fixed conflict cap and seed. If it closes, retain the proof and independently
   check the stabilizer-lex bridge; if it times out, report only OPEN.
4. **Defer restricted-SMS integration until it can beat that control.** A
   first SMS prototype should operate only in the known twin-cell stabilizer
   and emit independent $q$-witness receipts as above. Developing unrestricted
   MathCheck graph generation for frozen rows would be unsound; Duggan himself
   did not implement the required glued-submatrix version.

## 7. Reproduction

From this member directory (`.ultramath/smwzxq4fl/m4`):

```sh
../../../.scratch/k58/.venv/bin/python work/check_historical_vacuity.py
../../../.scratch/k58/.venv/bin/python work/symmetry_pilot.py validate
../../../.scratch/k58/.venv/bin/python work/symmetry_pilot.py build 7
../../../.scratch/k58/.venv/bin/python work/symmetry_pilot.py certificate
rm -f work/timings.jsonl
../../../.scratch/k58/.venv/bin/python work/symmetry_pilot.py run \
  work/case7-bare.cnf work/case7-historical.cnf \
  work/case7-matching.cnf work/case7-full.cnf \
  --conflicts 200000 --seeds 0 1
```

The run command deliberately asserts the recorded OPEN outcome rather than
silently treating an unexpected SAT/UNSAT exit as certified. No production
queue, tracked repository file, or file outside this member directory was
modified. No stock SMS solver was run; no current full auxiliary parent was
benchmarked; no general speedup, wall closure, or new Ramsey bound is claimed.
