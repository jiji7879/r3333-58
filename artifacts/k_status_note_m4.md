# Status of R_4(3) = R(3,3,3,3) — checked note (member m4, swarm smwiiyj7u)

All statements below were read in the cited source during this run (Nov 2026).

## Bounds: the problem statement's upper bound is OUT OF DATE

* Lower bound: R_4(3) >= 51, i.e. a 4-colouring of K_50 with no monochromatic
  triangle. F. R. K. Chung, "On the Ramsey numbers N(3,3,...,3;2)",
  Discrete Math. 5 (1973) 317-321.
* Upper bound: **R_4(3) <= 60**, not 62.
  M. Tatarevic, "An upper bound of 60 for the Ramsey number R(3,3,3,3)",
  arXiv:2610.36648 (v1 27 Oct 2026, v2 6 Nov 2026). Abstract: "We improve the
  upper bound ... from 62 to 60. The proof is based on a global incidence count,
  classifications of small neighborhoods and exhaustive SAT computations. We
  formalize the mathematical reductions in Lean and refute every resulting
  formula with two SAT solvers." The comments field records that v1 gave 61 and
  v2 improves it to 60. The earlier bound 62 is Fettes, Kramer, Radziszowski,
  "An upper bound of 62 on the classical Ramsey number R(3,3,3,3)",
  Ars Combin. 72 (2004) 41-63.
* Radziszowski's dynamic survey (Electron. J. Combin. DS1, ver. 17, 2024) is
  cited by Tatarevic as listing 51 <= R(3,3,3,3) <= 62, i.e. the survey predates
  the 60 bound.

The swarm's target (a K_51 colouring, giving R_4(3) >= 52) is unaffected, but any
*upper* bound quoted in a write-up should now say 60.

## Shape of Chung's colouring

W. J. Wesley, "New bounds for some small multicolor Ramsey numbers",
arXiv:2509.03784 (4 Sep 2025), Section 1: "A famous coloring of Chung gives the
best known lower bound of 51 for R(3,3,3,3): this comes from a block Cayley
4-coloring with 3 blocks of size 16 that is extended by two additional
vertices." The paper does not print the colouring.

This swarm now has a verified K_50 of exactly that shape:
artifacts/k50_blockcayley_Z4xZ4_m4.col (blocks 16+16+16+2 over Z_4 x Z_4).

## What is NOT established (do not assume)

* No classification of the (3,3,3,3;50)-colourings is known to me; nothing read
  in this run states one exists.
* I found no source reporting a SAT refutation of K_51. A full UNSAT for n=51
  would settle R_4(3)=51 and is not claimed anywhere I read.
