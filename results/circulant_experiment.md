# Single-circulant case for R(3,3,3,3): scope and first results

Question: does a good (no monochromatic triangle) 4-colouring of K_52 exist in which
one colour class, say colour 3, is exactly a circulant graph on Z/52?

Setup. Vertices Z/52; xy has colour 3 iff the undirected cyclic distance of x-y lies in a
distance set D subset of {1,...,26}; the graph must be triangle-free; colours 0,1,2 are
free on every other edge. |D| = 8 gives degree 16, and the colour-degree lemma
(every colour-degree <= 16, machine-checked in Lean) forces degree <= 16.

## Verified setup (coordinator)

* The displayed mask D = {1,3,5,7,9,11,24,26} = {+-1,+-3,+-5,+-7,+-9,+-11,+-24,26} is
  triangle-free of degree 15, and is inclusion-maximal among triangle-free distance sets.
  N_3(0) = {1,3,5,7,9,11,24,26,28,41,43,45,47,49,51} induces K_15 none of whose edges is
  colour 3, so it must carry a good 3-colouring of K_15.
* Both verified K_16 templates (artifacts/k16_template_*_m4.col) are 5-regular in each
  colour, so in every good 3-colouring of K_15 (a deletion of one of them) every vertex
  has colour-degrees (4,5,5). This is also forced by R(3,3)=6 alone: a colour-c
  neighbourhood is 2-coloured so has <= 5 vertices, and the three counts sum to 14.

## Monotonicity (sound, and it is what makes the sweep finite)

If D works and D' superset of D is triangle-free, then D' works: recolour every D'-edge to
colour 3; colours 0,1,2 only lose edges, and colour 3 is triangle-free. Hence if any D
works then some inclusion-maximal D works, and if no maximal D works then none does.

## Census of triangle-free distance sets (independent computation, C)

| family | count | orbits under units of Z/52 (24 units) |
|---|---|---|
| all triangle-free D | 33,752 | 3,022 |
| inclusion-maximal D | 1,102 | 104 |
| triangle-free D with degree in {12,13,14,15} | 9,871 | 885 |
| maximal D with degree in {12,13,14,15} | 798 | 74 |

Degrees attained by maximal triangle-free sets: 10, 11, 12, 13, 14, 15, 16, 17, 18, 26
(counts 12, 204, 294, 209, 235, 60, 57, 24, 6, 1).

Two consequences for the handoff's numbers:
* "217 open distance sets up to multiplication by units" is not reproduced: the degree
  restricted families give 885 (all) and 74 (maximal).
* "71 inclusion-maximal ones" is close to the 74 computed here; the difference is
  probably the equivalence used (units only, versus also quotienting by isomorphism of
  the circulant graph). Should be re-derived before being quoted.
* The claim "a circulant colour class must have degree 12,13,14 or 15" is NOT a
  consequence of maximality: maximal sets occur at degrees 10, 11, 16, 17, 18 and 26.
  Degrees 17, 18, 26 are excluded by the colour-degree <= 16 lemma; degrees 10 and 11
  are not excluded by anything established so far.

## A counting constraint that bites

Fix u and a colour c in {0,1,2}. For each colour-3 neighbour v of u, the count
n_c(u,v) = |N_c(u) intersect N_3(v)| is at least 4 (that count is one of the (4,5,5)
entries inside the good K_15 on N_3(v)). Summing over the 15 colour-3 neighbours of u,
and writing mu(s) = |S intersect (S+s)| for the number of common colour-3 neighbours of
two vertices at difference s,

    Sum over w in N_c(u) of mu(u-w)  =  Sum over v in N_3(u) of n_c(u,v)  >=  15*4 = 60.

For D = {1,3,5,7,9,11,24,26} the mu values are distributed as
{0:15, 1:2, 2:4, 3:2, 4:4, 5:2, 6:12, 7:2, 8:2, 9:2, 11:2, 13:2} (over the 51 nonzero
differences), so the sum for d_c = |N_c(u)| vertices is at most 48 for d_c = 4 and 57 for
d_c = 5. Hence d_c(u) >= 6 for each of the three ordinary colours, at every vertex.

## CNF instances built and running (timeouts kept open)

All use one-hot 3-valued variables on the 936 free edges (2808 variables), the 8060
all-free triangles, one symmetry-breaking unit clause (see below), and are solved by
cadical 2.1.2 writing a DRAT proof.

| instance | extra constraints | size | status |
|---|---|---|---|
| D15.cnf | none | 2,808 vars / 27,925 clauses | running |
| D15aug.cnf | colour-degree <= 16; per-neighbourhood (4,5,5) counts | 251,628 / 521,509 | running |
| D15full.cnf | above + colour-degree >= 6 | 279,708 / 573,925 | running |

Symmetry breaking (sound): translations of Z/52 and permutations of colours 0,1,2 both
map solutions to solutions while preserving the colour-3 circulant. Among the 26 edges
{x,x+2} (distance 2 is not in D) some colour occurs at least 9 times, so after a
translation and a colour permutation one solution has colour({0,2}) = 0. The unit clause
imposes exactly that. An UNSAT therefore means "no solution at all", not merely "none
with this normalisation" - but the final report must state this reduction explicitly.

## Encoder validation

The generator was checked end to end on a small case (n=6, D={1}, colour 3 = a 6-cycle):
brute force over the 9 free edges finds 15552 good colourings, cadical answers SAT, the
model decodes to a colouring accepted by tools/verify_coloring.py, and its colour-3 class
is exactly the 6-cycle. Triangle-freeness testing was cross-checked against explicit
triangle enumeration on 300 random distance sets (0 mismatches).

## Fully circulant case (a strict sub-case, decided)

A fully circulant colouring (colour of {x,y} depends only on x-y mod n) is a special case
of the single-circulant family. It is a tiny SAT instance (one 4-valued variable per
difference class 1..26). Results, with every SAT model decoded and checked by
`tools/verify_coloring.py`:

| n | 40 | 42 | 43 | 44 | 45 | 46 | 50 | 51 | 52 | 53 |
|---|---|---|---|---|---|---|---|---|---|---|
| fully circulant good colouring | SAT | UNSAT | SAT | SAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |

The three SAT models (`cyc_40_4.col`, `cyc_43_4.col`, `cyc_44_4.col`) are verified valid,
so the encoder is sound as well as complete. Consequence: a fully circulant colouring
cannot reach 52 at all, so the single-circulant relaxation (one circulant colour, three
free) is the right generalisation and the only one that can produce an improvement.
Note the family is not monotone in n (a circulant colouring of K_n does not induce one of
K_{n-1}), so the pattern above is not contradictory.

## Pairwise neighbourhood consistency: SAT for every shift (no local obstruction)

Necessary condition for the mask: for two colour-3 neighbourhoods N_3(v), N_3(v') the two
good K_15 colourings must agree on the colours of the edges among shared vertices.
Checked for all 51 nonzero shifts (instances of 136-435 free edges, sharing up to 13
vertices at shift 50): **SAT in every case**. So there is no pairwise obstruction; any
exclusion has to be genuinely global, and any witness has to satisfy these local gluings.

## Status of the global instances

| instance | extra constraints | size | result |
|---|---|---|---|
| D15.cnf | none | 2,808 vars / 27,925 clauses | **no answer in 50 min** (cadical 2.1.2) |
| D15aug.cnf | degree <= 16; per-neighbourhood (4,5,5) | 251,628 / 521,509 | **no answer in 50 min** |
| D15full.cnf | above + degree >= 6 | 279,708 / 573,925 | running |
| D15.cnf with --sat, seed 7 | none | 2,808 / 27,925 | running |

Lesson recorded for the next attempt: the sequential-counter encodings inflate the
instance ~100x and did not pay for themselves; the useful direction is stronger implied
constraints in compact form (e.g. the mu-weighted sum >= 60 as a weighted cardinality
constraint), or a bespoke search that branches on the neighbourhood templates.

## Local-search landscape (tabu over the 936 free edges)

With colour 3 fixed to the circulant, a monochromatic triangle can only use three
free edges, so the objective is over 8,060 triangles (not C(52,3) = 22,100). Tabu search
over single-edge recolourings, incremental deltas, tabu tenure 5-14, optional penalty
lambda on the implied (4,5,5) local structure:

| configuration | iterations | best (min mono) |
|---|---|---|
| lambda = 0, seeds 1-4 | 30M each | 309, 334, 308, 302 |
| lambda = 5, seeds 1-4 | 30M each | same minima (405,425,428,359 were the final states, not the minima) |
| lambda = 0, seed 1, 40M | 40M | 309 |
| lambda = 2, seed 1, 40M | 40M | 309 |

A random colouring has ~895 monochromatic triangles (mean 8060/9), so the search descends
fast to ~300 and then **plateaus: about 3.7% of the all-free triangles stay monochromatic,
and neither longer runs nor the local-structure penalty moves the floor.** That is
landscape information, not evidence: only a DRAT-verified UNSAT closes the mask, and
min-conflicts failure on Ramsey-type instances is notoriously non-probative.

Implementation note, recorded because it produced a misleading number once: an earlier
version printed the monochromatic count of the *current* state rather than the saved
best, which made the lambda runs look as if they had reached identical minima. After the
fix, "min mono over run" agrees exactly with a recomputation from the saved colouring.

## Final attack log on D = {1,3,5,7,9,11,24,26} (all attempts, nothing omitted)

| attempt | instance | budget | outcome |
|---|---|---|---|
| cadical 2.1.2, default | 2,808 vars / 27,925 clauses | 3,000 s | timeout |
| cadical, + degree<=16 + per-neighbourhood (4,5,5) | 251,628 / 521,509 | 3,000 s | timeout |
| cadical, + degree>=6 as well | 279,708 / 573,925 | 3,000 s | timeout |
| cadical --sat --seed=7 | 2,808 / 27,925 | 2,700 s | timeout |
| tabu local search, 936 edges, 12 configurations | - | 30-40M iters each | plateau at 302-334 mono of 8,060 |
| pairwise neighbourhood gluing, all 51 shifts | 136-435 free edges | ms each | SAT everywhere |
| mu-counting bound (d_c >= 6), applied to all 1,102 maximal masks | - | seconds | excludes nothing |

Independent corroboration (swarm member m4, separate code): cadical and kissat 240 s plain, 840 s
with a validated lex-leader over translations x colour permutations, 880 s with rigorous link
cardinalities - all undecided; and all 104 maximal-mask orbits undecided at 10 s each.

Verdict on this case: **undecided, and not decidable by the methods available here.** There is
no local obstruction (pairwise gluing is satisfiable for every shift), no counting obstruction
(the mu bound gives d_c >= 6 and nothing more, even in the sharpened profile test across all
maximal masks), and neither CDCL nor local search makes progress. A proof either way needs a
structural argument, not more solver time.

## Cheap exclusions actually obtained for the family (from m4, verified by the coordinator)

* 6 of the 104 maximal-mask orbits are excluded with no search: four by colour-degree > 16
  (degrees 17, 17, 18, 26), two by alpha(C(D)) > 16, which is necessary because a 17-set with
  no colour-3 edge would 3-colour K_17 with no monochromatic triangle. I recomputed both alpha
  values with igraph: 20 and 26.
* The translation-invariant (fully Cayley) subfamily is closed for all 104 masks, consistent
  with the n=52 circulant UNSAT above and with Anabanti 2023.
* 98 orbits remain open.
