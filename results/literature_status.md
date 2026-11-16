# R(3,3,3,3) = R_4(3): verified state of the art

Primary source: S. Radziszowski, *Small Ramsey Numbers*, Electronic Journal of
Combinatorics, Dynamic Survey DS1.18 (version dated April 24, 2026),
DOI 10.37236/21. Quotations below are from that version; nothing here is from memory.

## The bound

    DS1.18, Sec. 6.2:  "The most studied and intriguing open case is
                        51 <= R_4(3) = R(3,3,3,3) <= 62"     [Chu1] / [FeKR]

* Lower bound 51: F. R. K. Chung, *On the Ramsey numbers N(3,3,...,3;2)*,
  Discrete Math. 5 (1973) 317-321 — a 4-colouring of K_50 with no monochromatic
  triangle (a block-Cayley colouring, three blocks of size 16, extended by two
  vertices; see also arXiv:2509.03784, Sec. 1).
* **Warning, DS1.18 verbatim**: "The construction for 51 <= R_4(3) as described
  in [Chu1] is correct, but be warned of a typo found by Christopher Frederick in
  2003 (there is a triangle (31, 7, 28) in color 1 in the displayed matrix)."
  Anyone transcribing the published matrix gets a colouring with a defect at
  {7,28,31}; it must be reconstructed or repaired, not copied.
* Upper bound: 62 — S. Fettes, R. L. Kramer, S. P. Radziszowski, *An upper bound
  of 62 on the classical Ramsey number R(3,3,3,3)*, Ars Combin. 72 (2004) 41-63.
  History in DS1.18: the elementary inequality gives 66 (implicit), Folkman 1974
  gave 65, Sanchez-Flores 1995 gave 64, Fettes-Kramer-Radziszowski gave 62.

## Constructions that provably cannot improve 51 (important for search design)

DS1.18, Sec. 6.2, immediately after the bound:

> "It was shown that the bound 51 cannot be improved by using group partitioning
> into disjoint union of symmetric product-free sets [Ana1], neither by some other
> group partition means [Ana2]."

* [Ana1] C. S. Anabanti, *A counterexample on a group partitioning problem*,
  Birkbeck Mathematics Preprint Series #37, 2017.
* [Ana2] C. S. Anabanti, *The Ramsey number R_4(3) is not solvable by group
  partition means*, Quasigroups and Related Systems 31 (2023) 165-174.

Consequence: **no Cayley/group-partition colouring of any group of order 51 can
give R_4(3) >= 52.** Cayley-type search (colour of (x,y) determined by y-x^{-1} or
by y-x in a partition of G minus identity) is a closed chapter. Structures that
are only *group-adjacent* (e.g. a colouring of Z_3 x Z_17 whose colour depends on
the block pair as well as the difference, or a colouring merely *invariant* under
a group action) are not covered by [Ana2] and remain legitimate targets, but any
result there should say explicitly how it escapes Anabanti's hypothesis.

## The recursion that produces 51

DS1.18, Sec. 6.2(b):  R_r(3) >= 3 R_{r-1}(3) + R_{r-3}(3) - 3   [Chu1].

With R_3(3) = 17 and R_1(3) = 3 this is 3*17 + 3 - 3 = 51. So Chung's colouring is
exactly the r = 4 instance of this recursion; a 4-colouring of K_51 would beat the
recursion by one vertex. Any product-type construction is therefore fighting the
same recursion, and the natural question is whether a *non-uniform* twist of it
(perturbing the two extra vertices, or one block) can buy the 51st vertex.

## Conditional consequences (why the value matters beyond itself)

* DS1.18: if R_4(3) = 51 then R_4(3,3,3,3 with K_3+e) = 52, and if R_4(3) > 51
  then the two numbers agree.
* S. Eliahou, *An adaptive upper bound on the Ramsey numbers R(3,...,3)*,
  Integers 20 (2020) #A54: assuming R_4(3) = 51, R_r(3) <= r!(e - 5/8) + 1 for all
  r >= 4, i.e. asymptotically ~2.09 r!, against the unconditional ~2.55 r!.

## Post-survey development (2026): the upper bound has moved

DS1.18 (April 2026) records 62. A preprint posted after it claims a better bound:

* M. Stojanović (repository owner `milostatarevic`), *An upper bound of 60 for the
  Ramsey number R(3,3,3,3)*, arXiv:2610.36648 (v1 27 Oct 2026, v2 6 Nov 2026).
  Abstract: "We improve the upper bound on the classical Ramsey number R(3,3,3,3)
  from 62 to 60. The proof is based on a global incidence count, classifications of
  small neighborhoods and exhaustive SAT computations. We formalize the mathematical
  reductions in Lean and refute every resulting formula with two SAT solvers."
  Code, formula set (296,081 formulas) and Lean formalisation at
  github.com/milostatarevic/r3333-upper-bound.

Status: preprint, not (yet) reflected in DS1; the SAT refutations are verified by two
solvers (Kissat and CaDiCaL) rather than by an independent DRAT/LRAT checker, so the
computational premise is a trust assumption. Treat "R_4(3) <= 60" as a claimed bound.

Relevance to the lower-bound question: none directly (a K_51 colouring would be
consistent with R <= 60, giving 52 <= R <= 60). But the *method* is the one that works
on this problem: split on the colour-degree profile of a vertex (the 47 profiles
summing to 50 with entries <= 16 for n = 51; six surviving profiles for n = 60), use
classifications of the mono-triangle-free 3-colourings of K_15 and K_16, then kill each
case by SAT. Any serious attempt on the lower bound should read it for encodings.
