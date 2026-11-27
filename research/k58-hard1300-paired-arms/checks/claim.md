# Paired five-neighbor clauses on the 1,300 hard K58 inputs

All 1,300 row identifiers were recovered using the original family and placement enumeration. Each regenerated full-root DIMACS matched its uploaded SHA-256. The TSV identifies 191,031,232,170 historical proof bytes. It contains no solver times or proof traces. The original completion statuses are taken from the supplied history. The stored small proofs in this package were generated afresh.

## Derivation

Let x be in root arm c. Its encoder guard g asserts that x sends color c to at least 14 vertices outside its own arm, excluding the root. For another root arm B of color b, the vertices of B receiving c from x have neither b nor c on any mutual edge. Six such vertices would give a two-color triangle-free K6. Hence each of the three other arms supplies at most five, and at most one of these arms can supply only four or fewer.

In a fixed arm enumerate all five-subsets having no internal c edge. Each is a two-color pentagon. Keep subsets consistent with the row's positive and negative physical pins on x. For two classified arms B and D, an active sender must realize at least one compatible five-set in their union. If H_B and H_D each intersect every compatible five-set in their respective arms, the resulting clause consists of the negated sender guard and the positive color-c spoke literals from x to H_B and H_D. A row-specific hitting set and the DIMACS guard always have to be rebound on the target. The bound also holds if the third arm has no classified template.

The ternary version uses a single unfixed vertex common to all feasible five-sets in each of the two arms. The census requires nonempty lists in both arms and excludes spokes already set by signed pins. It found 16,530 row-specific ternary clauses in 1,236 of 1,300 inputs. These are preprocessing opportunities. Clause counts do not measure savings in complete search.

## Replays and searches

For sender 48 and target vertices 19 and 35, the same physical implication matched 14 inputs. If the sender guard is true, edge (48,19) or (48,35) must have color 3. On rank 1 the clause is `-25165 3764 5652 0`. All 14 falsifying cubes passed plain unit propagation and then required 21–81 native search conflicts on the original inputs, totaling 840. The added clause rejects each cube by unit propagation. Each original input plus its three signed assumptions has an independently replayed DRAT certificate here. The 14 traces total 32,972 uncompressed bytes. Ranks, guard IDs and hashes are in physical-replays.json. The 14 proofs test one physical pattern across placements. The generic proof above supports the wider census.

Six complete parents, ranks 1, 6, 325, 650, 975 and 1300, were compared at 60,000 conflicts with cold seed-zero CaDiCaL 1.9.5. Stock, a direct encoding with up to three minimum hitting sets per arm, and an extended encoding with auxiliary pentagon selectors all reached the limit. The extended encoding introduces implications from a pentagon selector to its five required spokes and forces at least one alternative from each pair of classified arms when g is active. The auxiliary variables admit an extension for every original model by choosing its realized supports.

At 800,000 conflicts, ranks 1200 and 1300 also hit the limit for all three policies with proof logging. Stock/direct/extended search CPU seconds were 98.94/91.16/99.65 and 88.76/73.85/95.73 respectively. These measure a fixed amount of search with a single seed. Time to finish remains undetermined. Results from the separate four-row test of the ternary-only encoding are in short-panel.json.

## Running the package

Use x86-64 Linux, Python 3.12 and a C compiler. From this directory:

```sh
sh setup.sh
.venv/bin/python verify.py tools/drat-trim
.venv/bin/python check.py
.venv/bin/python export.py 1 ternary rank1-ternary.cnf
```

The verifier reads the retained artifacts, recomputes their hashes, binds each guard and cube to the archived parent, and replays the proof. The separate check regenerates all 1,300 input hashes and verifies the finite coloring and template facts. To repeat the search comparisons use probe.py with a comma-separated rank list and conflict budget, completion.py with a conflict budget and checker path, or short_panel.py for the ternary-only panel. Scripts producing JSON results can overwrite those results on a rerun. Use a copy when preserving the original measurements.
