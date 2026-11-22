# A certified partial-word exclusion for the uniform K58 branch

The Hail Mary in the attached README fixes all fourteen words on arm B and refutes the resulting 42-slot instance. **116 specified cells on ten of those words already suffice.** Two independently replayable SAT proofs establish the exclusion. A second experiment gives a sharp local separation between full words and their zero positions.

## The forbidden pattern

Let the root be r, its color-0 arm A have size 15, and B, C, D have size 14 and root colors 1, 2, 3 respectively. Use the twisted 15-point template on A. In the fully sending uniform branch, every a in A has color-0 degree 15, and every outside word from B, C or D into A has five zeros. A dot in the table denotes an unrestricted entry. The column order is 0 through 14 in the Lean labeling. The row IDs refer to the transported upstream witness. The ten rows can occupy **any ten distinct positions** in B.

| Row ID | Letters on A |
| ---: | --- |
| 1 | `121.21102.010..` |
| 2 | `1.02.2303021.11` |
| 3 | `2131123.0310000` |
| 6 | `2.03.2.01213211` |
| 7 | `.1121.1.0.00200` |
| 8 | `3302.1201..10..` |
| 9 | `312121101.0202.` |
| 11 | `0203.00.311.121` |
| 12 | `..00.....231131` |
| 13 | `1321.31.0002030` |

**Theorem.** No coloring in the stated uniform branch realizes this table.

**Proof.** Use point a = 7 of A. Write s_P for its number of color-0 neighbors in P. No color-0 edge lies inside A, and ra has color 0, so s_B + s_C + s_D = 14. Inside each of these three neighbor sets, the color 0 and the root color of P are both forbidden. The remaining two colors can cover at most five vertices without a monochromatic triangle, by R(3,3) = 6. Consequently the three counts are 5, 5, 4 in some order. At least one of C and D contributes five vertices.

On these five vertices the two remaining colors each induce a pentagon. Indeed, three neighbors of the same color at one vertex would have to form a triangle of the other color. Each color therefore has degree at most two at each vertex and hence exactly two. A simple 2-regular graph on five vertices is a 5-cycle. Relabel the five positions along the cycle of the smaller of the two available colors. This only permutes the five new positions. It preserves the labels of A and the ten B rows.

For each of the two possible arms, consider just the ten displayed B positions and this five-vertex pentagon. Assign the five new words their unknown colors on A, give each five zeros including column 7, and forbid same-color pairs on the corresponding template edges. Give the edges between the fifteen positions colors, excluding 1 inside B and prescribing the two colors around the pentagon as above. Forbid a monochromatic triangle among the fifteen, and forbid a monochromatic triangle through a point of A whenever its two attachment colors are specified. Unspecified letters of B are ignored. Every full realization gives an assignment to this relaxation, whatever its other words or edge colors.

`pattern-2.cnf` and `pattern-3.cnf` implement these two cases. Each has 1,261 variables and 4,641 clauses. Both certificates replay to `s VERIFIED`. The two cases exhaust the possible source of the forced pentagon, proving the theorem. The statement applies to this particular partial pattern. No optimum for the number of specified cells or rows is claimed.

**Solver consequence.** For a fixed placement of the ten rows, the disjunction of the negations of the 116 specified color literals is an implied clause. To recognize every placement without enumerating row permutations, join each pattern row to each B position whose already assigned letters agree on all its specified entries. If a matching covers the ten pattern rows, the search branch can be rejected. `matches_pattern` in `check_witnesses.py` implements this test. A production solver would need to translate its template labels and guard the cut by the stated branch hypotheses. The package does not measure the end-to-end runtime effect of learning this cut.

## Why the column counts lose information

Pin the original fourteen complete B words. Allow k distinct color-2 vertices, each with five zeros on A. All their mutual edge colors other than 2 are free, as are all compatible edges to B and all compatible edges inside B. Keep the template, the fixed words, and the prohibition on monochromatic triangles. This is a hereditary projection of the uniform branch.

| Fixed information on B | Further color-2 vertices | Result |
| --- | ---: | --- |
| All fourteen words | 5 | SAT. `five.col` gives a good K35. |
| All fourteen words | 6 | UNSAT. `local6.drat` certifies the 7,166-clause formula. |
| The exact zero positions of all fourteen words | 6 | SAT. `same_zeros_six.col` gives a good K36. |

These results give a sharp maximum of five for the full words in this projection. The K36 witness has the same 70 zero cells in the same rows and columns as the original. It changes 51 of the 140 ordinary letters. The direct checker verifies all 6,545 and 7,140 triangles in the two colorings, the root arms, the labeled template, all zero supports, and all fourteen complete B words in the five-vertex witness. Thus even the full zero-incidence matrix cannot imply the same six-vertex contradiction. Neither of these smaller colorings resolves extendibility to K58.

## What the 3,003-way split proves

For each a, the preceding degree argument gives one arm with four hits and two with five. A complete B arm contributes 14 × 5 = 70 incidences. If t of the fifteen columns have four hits, then 4t + 5(15 − t) = 70, giving t = 5. The five deficient positions therefore define a unique 5-subset of A. Fixing this set partitions the labeled models on a fixed template into at most binom(15,5) = 3,003 cases. Every completion is covered exactly once. Nonemptiness and solve time are separate questions. The deficient sets for B, C and D themselves partition A.

The witness has deficient set {0,1,3,8,10}. I rebuilt the mathematical 42-slot model in this labeling, using fresh variable numbers and cardinality constraints. The following runs used Kissat 4.0.4. Time is solver CPU seconds. The original README reports 10.5 seconds on its own encoding.

| Information fixed at 42 slots | Outcome | Seconds |
| --- | --- | ---: |
| None | UNKNOWN | 90 |
| Matching coverage profile | UNKNOWN | 90 |
| Coverage profile {0,1,2,3,4} | UNKNOWN | 90 |
| All original B zero positions | UNKNOWN | 90 |
| All original B words | UNSAT, DRAT verified | 17.73 |

`pilot/` contains the five benchmark inputs and the measured conflict counts. To reproduce an individual run, invoke `kissat --time=90 input.cnf proof.drat`. The shorter local6 certificate already proves the full-word exclusion by restriction. The archive retains that certificate and both certificates for the ten-row pattern. The two tested profile cases remain open. The experiment certifies no complete coverage profile, no original ledger row and no change in the Ramsey bound.

## Replay and provenance

Run `bash replay.sh` from the unpacked directory. It checks hashes, checks both graph matrices, compiles the included DRAT checker, and replays all three certificates. The default replay needs Python 3, a C compiler, and standard Unix utilities. `python3 regenerate.py` optionally regenerates the three CNFs and compares them byte for byte. Formula regeneration uses `python-sat==1.9.dev24`. The independent checker and certificate replay use no Python packages outside the standard library.

The source witness is the repository's transported `a_14_14_lean.wit`, stored here as `source.wit`. Its first fourteen rows are the B pin. The file-to-campaign color conversion adds one to each template edge color. The color-preserving permutation from our Lean point order to the supplied `.col` point order is `[3,11,1,9,2,8,0,10,14,4,12,6,13,5,7]`. The witness checker uses the `.col` matrix directly to audit the template correspondence. [Upstream witness and transport record](https://github.com/jiji7879/r3333-58/tree/830e256ede58f7b9ea10adbff5bbf5d27906727f/results/two-arm-interface) · [Original Hail Mary](https://github.com/jiji7879/r3333-58/tree/830e256ede58f7b9ea10adbff5bbf5d27906727f/results/hailmary-2)
