# Square clauses for active senders on the K58 wall

## The rule and its boundary

Fix the root r. Let x belong to its color-c arm, and let g be the first-tier encoder's positive selector requiring at least 14 color-c spokes from x in addition to xr. Fix another root arm B of color b. Within B choose four sites S whose six mutual edges use only the two colors other than b and c. If one of those colors forms a square and the other a matching, insert

    ¬g ∨ ⋁_{v∈S} ¬E(x,v,c).

Delete a negative spoke literal only when the original row pins the corresponding positive spoke. If extra child assumptions establish any of the geometry, retain their negations on export to the parent. The witness geometry used in these batches consists entirely of units in the original wall parent. All four color-c spokes together imply that the color-c degree of x is at most 14, irrespective of which selectors the encoder sets.

To prove the rule, suppose the four spokes hold and the degree is at least 15. In the three-colored triangle-free neighborhood N_c(x), keep r, the four sites and any other ten vertices. At r the three color groups have size at most five, since six same-color neighbors would contain a two-colored triangle. The group for b includes the four specified sites. If its size is five, each color of its two-color K5 is a pentagon, and deleting any vertex gives a path. If its size is four, the other two groups have five each. Normalize their pentagons independently by permuting vertices. The two ways to assign the matching color on the four sites are equivalent under exchange of the other two colors and their groups. The resulting three-color K15 formula with a square/matching on the four sites is UNSAT. The archive includes the formula generator and trimmed DRAT. With a path in that position K15 is feasible, as the saved model demonstrates.

At order 14, a triangle-free three-coloring with the square/matching and root group sizes 4,4,5 exists. The 91-edge model is directly validated. This establishes the sharp threshold for this neighborhood argument. It makes no extension claim to K58. The path condition already occurred in the project's support tables for the marked sender arm. This experiment applies it directly to every available sender selector, which also covers senders outside the marked arm.

## Results on ordinary wall rows

The panel is the 14 previously selected physical wall rows, two per profile. We regenerated their original unsplit first-tier formulas with tables and total critical enabled and full root disabled. Indices in wall-rows.json are borrowed from each row's selected representative for identification. The experiment adds no representative, pivot or spoke assumptions to the parent benchmark.

The independent batch check bound every guard to the original encoder, tested the six internal edges and root spokes against the regenerated parent's unit clauses, replayed the common DRAT and checked both models. Of 9,287 distinct row-specific clauses, 4,807 across ten rows had falsifying cubes that survived original unit propagation. Adding the clauses refutes those cubes by unit propagation. These cubes can overlap. The two rows each of (15,14,14,14) and (16,14,14,13) had zero new propagation exclusions. In each of the ten rows with a gain, the first shortest new cube remained OPEN under plain original CaDiCaL at a nominal 12,000 conflicts. The shared geometric certificate validates its exclusion. No direct full-parent DRAT was produced for those ten cubes.

On the first applicable row of each of four different profiles, cold CaDiCaL 1.9.5 ran with seed zero and proof logging in both arms of an unsplit comparison. Results at a 40,000 conflict cap:

| Wall index | Profile | Added clauses | Base search and load CPU s | With square clauses CPU s |
|---:|---|---:|---:|---:|
| 0 | 15,15,14,13 | 667 | 2.70 | 4.44 |
| 370 | 16,15,13,13 | 606 | 2.85 | 3.88 |
| 762 | 16,15,14,12 | 820 | 2.77 | 2.77 |
| 15533 | 16,16,13,12 | 950 | 2.84 | 3.11 |

All eight runs reached the cap OPEN. Matching took about 0.034 additional CPU seconds for the four square batches combined. Comparison makespan was 10.43 seconds with up to four workers. Peak fresh worker RSS was about 122 MiB. No whole-row proof was retained. Wall-bench.json lists per-run conflicts and times. A single seed and a bounded run determine neither time to completion nor whether the augmented search is generally slower.

## Historical controls

For 939 previously propagation-surviving falsifying cubes on the 13 historical rows, flip exactly one physical spoke at a time and hold the guard true. Of 2,817 distinct neighbors, adding the previous positive four-literal rules to the older direct and ternary baseline propagated additional literals on 1,918. Both policies left all 2,817 OPEN by propagation. On one neighbor per row both cold CaDiCaL variants reached 3,000 conflicts. All 28 nonempty proper subcubes of the two earlier certified examples at ranks 8 and 340 also reached 3,000 conflicts on their original parents. Those timeouts do not prove minimality.

On those same 13 historical inputs, the square-rule scan found 353 three-literal, 151 four-literal, and 18,528 five-literal instances whose falsifying cubes survived all three older clause batches. This is a separate panel from the 14 ordinary wall rows. The historical rows were already solved.

## Replay or export

On x86-64 Linux with Python 3.12 and a C compiler, run from the extracted top directory:

    sh hard-study/setup.sh
    hard-study/.venv/bin/python next/verify.py verify hard-study/tools/drat-trim
    hard-study/.venv/bin/python next/verify.py export hard-study/tools/drat-trim 0 wall0-squares.cnf

Export writes a new file and contains the whole first-tier parent plus its checked square clauses. Each batch is bound to its row, parent hash, formula tier, empty cube, physical palette and shared theorem-proof hash. Every clause carries its sender, both arm colors and witness sites. The batch index binds the compressed bytes. If a file is missing or verification fails, abort. Accept a terminal wall closure only after the full original-input proof or full model passes the publication verifier.

Use wall.py screen and wall.py bench with the checker path to repeat the ordinary wall tests. The neighbors.py, shorten.py and pathcuts.py scripts reproduce the historical controls. Run these in a disposable copy to preserve the measurements.
