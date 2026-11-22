# Hail mary (their item 2): SBVA preprocessing — no reduction, no speedup

Their hypothesis: SBVA compresses the repeated triangle and at-most-one structure
the case formulas are made of, and stays proof-checkable.

**Setup.** `github.com/hgarrereyn/SBVA` (the SAT'23 SBVA-CaDiCaL preprocessor),
built here with g++ against Eigen 3.4 from conda-forge. Input: `16,14,14,13`
case 7, the bare host-plus-pin formula (`p cnf 6612 135333`, 2.58 MB).

**Result: it changes nothing.**

| file | variables | clauses | bytes |
| --- | ---: | ---: | ---: |
| input | 6,612 | 135,333 | 2,579,508 |
| SBVA output | 6,612 | 135,333 | 2,579,508 |

The verbose trace shows it *tries* exactly the structures one would hope for —
`s Trying 4608 (1) / Iteration, Mlit: 4608 / Clause 8057 (0): 4605 4606 4607 4608`
is the four-literal at-most-one clause of one edge — and applies no replacement.
The output file differs from the input only in ordering.

And the solve rate is unchanged: kissat on the SBVA output gives 5,192,204
conflicts in 120 s (~43 k/s), against 2,972,946 in 60 s (~49 k/s) on the input —
the same regime, no gain, status UNKNOWN in both.

**Why.** SBVA wins on formulas where many clauses share literal *pairs* and the
added variable eliminates a large set of them. Here every edge's six clauses are
already the compact formulation of one four-valued variable, and the triangle
clauses share literals in triples that no single auxiliary variable covers: the
formula is already as compressed as BVA can make it. So there is nothing for the
preprocessor to find, which is consistent with the fact that the case CNFs are
2.58 MB for 6,612 variables — dense but not redundant.

**Verdict.** Item 2 is closed: not applicable rather than harmful. Unlike the
degree-cap experiment (which made things 3x worse), SBVA is neutral, so it can be
left in a pipeline without cost — but it buys nothing.
