# A smaller exhaustive rectangle cover for the K54 Ramsey search

Every hypothetical counterexample assigned to seed 12 has a representative among **1,662,749 colored marked cases**, down from 2,809,638. With the four crossing colors left unspecified, the count falls from 59,925 to **35,031**. The reduction covers all 24 rooted H42 placements. The original 12 top-level seeds remain open, and the sample ledger remains 58 of 72 boards excluded.

Read the crossing-cut theorem below for the proof. The result is a covering argument. A coloring can contain several marks, so a branch omitted here could still be satisfiable in isolation. The count measures the number of cases available to dispatch; it does not measure wall-clock speedup.

## The crossing-cut theorem for seed 12

Let a good coloring mean a four-edge-coloring with no monochromatic triangle. In the project's normalized K54 case there are disjoint 14-vertex ordinary-color templates A and B, with poles a and b. Every edge from a to B and from b to A has the fourth color c. There are 26 outsiders. Seed 12 assigns H42, row 42 of the three-color K14 catalogue, to both templates. Vertex numbers here are zero-based, and catalogue row numbers start at one. For an outsider w, write S(w) and T(w) for its c-neighbors on A and B. Both sets are nonempty by ordinary nonextendibility of H42. Neither can include a pole, since w has a c-neighbor on the opposite side. Let D consist of the ordinary crossings between the two sets of 13 nonpoles. Every product S(w) × T(w) lies in D.

Call a subset P of a template tight when at most |P| outsiders can have their entire c-support contained in P. The term in this report refers to a verified upper bound. Equality need not be realized. A partition B1, B2 of the 13 nonpoles is eligible if every subset of each part is tight.

**Theorem.** For each eligible partition of B, some ordinary rectangle in D has one column in B1 and one in B2. The same assertion holds on A independently. The two assertions can use different rectangles.

**Proof.** Suppose there is no rectangle crossing the B partition. An outsider with neighbors in both parts of B must be a singleton on A, since two A-neighbors would give the missing rectangle. Let L be the set of A-singletons and M the set of outsiders with B-support contained in one part. The singleton capacities on A give |L| ≤ 13. Tightness of the parts gives |M| ≤ |B1|+|B2| = 13. Since L and M cover 26 outsiders, both have size 13 and they are disjoint. Each A position has its own singleton witness, whose B-support meets both parts.

Consider the 13 outsiders in M. If one had A-support of size k ≤ 3, it and the k singleton witnesses on those positions would contradict the k-point capacity on A. Thus all have at least four A-neighbors. For a specified four-set P, the four singleton witnesses already use four units of its capacity. Direct enumeration on H42 gives capacity four for 989 of its 1,001 four-sets and five for the other 12. Each exceptional set can consequently occur at most once as the exact support of an outsider in M. Every possible pole occurs in at least three of the 12 sets. Only sets avoiding the pole are available. At most nine members of M can have size four. Consequently

$$
\sum_{w\in M}|S(w)|\ \ge\ 9\cdot4+4\cdot5=56.
$$

Assign each member of M a distinct representative column from its B-support. Hall's marriage theorem applies within each part because a group of witnesses with union Q is confined to Q, which is tight. The parts are disjoint, so the assignments combine. Counting the ordinary edges from the representative column to S(w) gives |E(D)| ≥ 56.

On the other hand, each row meets both parts via its A-singleton witness. If its degrees into the parts are d1,d2, it accounts for d1 d2 ≥ d1+d2−1 cross-part column pairs. Each such pair has at most one common row, since two would make the forbidden rectangle. Summing over the 13 rows gives

$$
 |E(D)|\ \le\ 13+|B_1||B_2|\ \le\ 13+6\cdot7=55.
$$
This contradiction proves the theorem for the actual crossing graph. No crossing recoloring is needed.

### How the finite inputs are checked

* For the capacities through size four, enumerate every possible word of colors from an outsider to the 14 template vertices. Two words can coexist only if their joint color masks leave a color for their mutual edge. The search enumerates compatible word multisets, including repetitions, and colors their mutual edges subject to all outsider triangles. The order-four run goes through the test for six outsiders so the upper bound of five is certified. The table of 12 exceptional masks is supplied.
* For larger subsets, the supplied integer weights certify an occupancy bound using ordinary spoke words on the complement. A class fixes spokes to one, two or three distinct anchors in distinct ordinary colors. Its total population is at most 16, 5 or 2 respectively, by the elementary Ramsey bounds for monochromatic triangles in three, two or one remaining colors. Subtract the already counted template occupants. If every admissible word receives weighted coverage at least L and the remaining weighted capacities total C, the integer upper bound is floor(C/L). The checker enumerates the words and verifies the weights for every subset needed by the reported cuts and verifies each palette/vertex symmetry used in that step.
* In the fixed H42 numbering the three representative poles are 0, 2 and 4. The verified searches produce 63, 48 and 50 eligible unordered partitions respectively. These are the partitions found from the available certificates. The marks generator works with these lists directly.
* For each placement, select the verified cut and orientation that remove the largest total colored weight from the old list of orbits among the tested choices. Drop an orbit only when **every image** misses the cut. This includes images that interchange the sides. The verifier rebuilds the group action, checks the partition of all 6,084 raw rectangles, and recalculates the number of inequivalent ordinary colorings of each representative.

## A sharper bound on four-point supports

With all 13 singleton slots occupied on H42, the largest number of additional outsiders having exactly four c-neighbors is **at most 4, 4 and 3** for pole 0, 2 and 4 respectively. This strengthens the 56-edge lower bound in the argument to 61, 61 and 62. The weaker bound already proves the crossing-cut theorem.

For each pole, start with the exceptional masks avoiding it. For each tested set of masks, use a graph containing H42, an outsider with each selected exact support, and all 13 prescribed singleton outsiders. Every edge involving outsiders is a color variable subject to the stated support and triangle constraints. CaDiCaL's 39 small refutations, replayed with drat-trim, suffice to prove the three bounds by enumerating subsets of the mask list. Stored and independently checked models attain 4, 4 and 3 on the respective local induced graphs. They do not construct a full K54 coloring.

## A restriction across eight full seed families

The small-set enumeration also verifies 48,880 bounds on 104 catalogue rows: every subset of at most three points is tight, including the empty subset. For each such row, enumerate its four-point deletions whose complementary K10 can appear in one of the two ordinary K15 templates. The union of all admissible deletion sets has at most eight vertices, and for H42 it is empty. The code verifies completeness of the two K15 templates by testing all ordinary one-vertex extensions of the 115 K14 rows and finding an explicit isomorphism to a K15 class for every completion. The input assertion that the 115 K14 rows are exhaustive and the original seed assignments are the audited results in the preceding project handoff.

For any pair of these 104 templates, fix a partition of the A nonpoles into four triples and a singleton, and any 6+7 bipartition of the B nonpoles. It is impossible for every ordinary rectangle to have its A pair in the same block **and** its B pair on opposite sides of the bipartition.

To see this, let d count outsiders nonsingleton on both sides, t the outsiders singleton on both, and hA,hB the numbers of missing singleton slots. Singleton capacities and inclusion-exclusion give d = hA+hB+t. Under the stated rectangle restriction a doubly nonsingleton outsider lies within one A-block, and has exactly two B-neighbors since all pairs of its B-neighbors would have to cross the bipartition. Subtract the occupied A-singletons from the capacities of the A-blocks to get d ≤ hA. It follows that hB=t=0. If d were positive, the double outsider and the two occupied B-singletons on its B-pair would violate the two-point bound. Hence all singleton slots are filled on both sides, with no overlap. Each of the 26 witnesses has at least four non-singleton-side neighbors by the three-point bounds. Every vertex of D then has degree at least four.

For a fixed row, at most two other rows can have more than one common column with it, and neither can have more than two since all pairs of those columns must cross the bipartition. The sum of its codegrees with the other 12 rows is at most 14. Its adjacent columns each contribute at least three to this sum. Its degree must therefore be four. There are 52 edges, so every column also has degree four. Every singleton witness uses the entire opposite neighborhood of its position. The c-neighborhood of a row contains ten opposite template vertices, its own singleton witness, and the four singleton witnesses of its adjacent columns. These 15 vertices use only the three ordinary colors internally. Thus each row neighborhood is an admissible four-point deletion of the opposite template. Together these neighborhoods cover all 13 opposite nonpoles, contradicting the verified union bound of eight.

The count of rooted pairs to which this result applies is **1,881,012**. This includes all pairs assigned to seeds 5 through 12 and some pairs assigned to seeds 1 and 3. The stronger individual crossing-cut theorem and the 1,662,749-job count above were verified for seed 12 only.

## New solver runs

All six count assignments that survived the earlier five-cycle inequalities fail on **both** individual H42 sides. The 12 new small refutations use between three and ten marked outsiders, without crossing pins or the opposite core. The package contains each CNF and its verified DRAT proof. Adding the four count clauses per board rules out the six inputs. Both CaDiCaL and Kissat found replacement assignments for local-15, live-07 and live-14. All six replacements satisfy every clause of the corresponding strengthened count CNF.

The full-graph CNF generator enforces every certified cut on both sides. It uses an indicator per potential ordinary rectangle and flags for a row or column pair participating in such a rectangle. A selected indicator implies four ordinary crossings, and each cut requires a witnessing pair. In a good coloring satisfying the theorem the indicators can be chosen for actual rectangles. All 24 unmarked placements and the 14 open sampled boards were run through CaDiCaL with these clauses, at 5,000 conflicts each. All 38 reached the budget. This experiment establishes neither a runtime improvement nor a new full-order refutation.

## Reproduce and continue

Use Python 3.10 or later with SymPy, a C compiler and a C++20 compiler, with Python assertions enabled. The original project handoff contains the underlying seed assignment, root normalization, longer K14 catalogue proofs and Lean work. This archive contains the proof and code for the present reduction. Lean 4.19 checks the graph-theoretic upper bound in formal/CrossCut.lean. Its theorem forcedRectangle starts from genuine row neighbor lists, the assumption that each row meets both parts, and at least 56 ordinary edges. Its conclusion forces two distinct row positions to share a cross-part neighbor pair. Deriving these premises from the H42 occupancy certificates and Hall’s marriage theorem remains outside Lean.

```sh
sha256sum -c SHA256SUMS
python src/global_scope.py
python src/template.py
python src/saturated.py
python src/four_bounds.py
python src/cut_cover.py
python src/replay_records.py
```

Run `lean formal/CrossCut.lean` with Lean 4.19.0 to check the structural counting lemma.

For a complete rebuild of the orbit selection, run `python src/cut_cover.py --build` before the ordinary verification command. The cover and omitted IDs are in results/cover.json and results/omitted_orbit_ids.json.gz. Old orbit representatives with their weights are in data/rect_reps.json.gz. Placements start at 1; mark and color indices start at 0. Each marked color word is in row-major order and uses the global ordinary palette.

```sh
python src/jobs.py list 23 --limit 3
python src/jobs.py cnf 23 0 0 placement-23-mark-0-color-0.cnf
python src/cut_cnf.py placement-23 placement-23-all-cuts.cnf.gz
```

The second command emits the first retained colored case of placement 23. The third emits the full rooted placement with no marked rectangle fixed. Distributing one job per retained colored case is optional. The compact root CNF already enforces all the cuts. A full proof still needs certified coverage and refutations for the remaining cases in all 12 seeds.
