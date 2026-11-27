# Square/matching spokes on the ordinary K58 wall

## Status and ceiling

The shared K15 formula is proved and its normalization is now checked
exhaustively against literal CNF clauses. Four accepted Ultramath reviews
(`smwziqvco`, DeepSeek v4.1 Flash) cover the local mathematics, ordinary-wall
reconstruction, historical controls and claim limits. This audit narrows the
package to what was independently checked.

It certifies conditional clauses on their exact encoder parents, not a
representative, wall-row or Ramsey closure. No full-parent DRAT was produced
for the ten nominated ordinary-wall cubes. OPEN is neither SAT nor UNSAT.

## 1. Exact local theorem and normalization

Let $x$ be in the root's colour-$c$ arm. Partition its colour-$c$ neighbours by
root-edge colour. The root arm itself is excluded, as is $r$. In each remaining
group, mutual edges can use neither that group's root colour (triangle with
$r$) nor $c$ (triangle with $x$). Therefore a group is a triangle-free
2-coloured complete graph and has at most five vertices because $R(3,3)=6$.
The exhaustive checks here count 18, 12 and 0 valid labelled colourings of
$K_4,K_5,K_6$ respectively.

In a valid colouring of $K_5$, each colour class is a $C_5$. Every induced
four-set is $P_4+P_4$, so it cannot contain a $C_4+M_2$. Hence a four-site set
$S$ carrying one square and a perfect matching in the other two colours has a
root group of exactly four vertices. If the guard supplies at least 14
colour-$c$ neighbours other than $r$, choose 14 partitioned among the three
groups. The other two groups therefore have five vertices each.

The symmetry step is explicit, not merely “two templates look alike”:

* Each five-group's palette is respectively $(0,2)$ and $(0,1)$. In both cases
  palette-first is actual colour 0, which forms a $C_5$. Order the group's
  vertices along that actual $C_5$. This maps every one of its ten edge pins
  to the supplied formula, preserves its root colour, and changes no palette
  or cross-group edge. All 12 possible labelled colourings can be used in each
  group independently. The checker compares all 144 pairs as complete 1,825-
  clause multisets. Trying to relabel the *other* palette colour to
  palette-first would require an unsupported colour swap; that is not the
  argument used here.
* On $S$, walking the square in cyclic order maps its four edges to the
  canonical square and its two remaining diagonals to the unique matching.
  All six labelled square/matching choices are tested. If matching and square
  colours are exchanged, globally exchange those two colours and their two
  root groups. The complete clause multiset again equals the canonical one.

`checks/normalization.py` constructs base and pinned clauses separately and
permutes colour/vertex indices at the DIMACS-variable level; it does not rely on
an isomorphism of merely the four- and five-vertex graphs. The resulting query
has 315 variables / 1,825 clauses and SHA-256
`9fb32091685b9e3adf1e7e670c3d4333f35b0d12ed6990e968a44b83fb180b01`.
It is UNSAT. The earlier “eight flavours require further graph proofs” report
was withdrawn: its alternative generator accidentally pinned both pentagons
to a single colour.

The proof certificate `next/matching.drat.gz` decompresses to **470,852
bytes**, SHA-256
`4ca7a5d302ceadc4afb5d8d54e4f9c3d5613f48cf08681fe0461a05acb6085d7`
(gzip-file SHA-256 `63db62ec43ac015e53a7013b5da59a705c3432136b0946da21d414ea2cf1c4e3`).
A fresh drat-trim binary used no `-w`, returned exit 0 with one exact
`s VERIFIED`, read all 470,852 bytes, emitted no warnings/errors and reported
zero RAT lemmas. The stronger `-p -U -W` run also passes. Deletion records are
not needed for that RUP proof. A second implementation ignoring all deletion
records verifies **11,868/11,868 additions** and reaches the empty clause;
this run reproduced those counts.

The K15 path variant is satisfiable and the shipped model satisfies its exact
formula. It has root groups 4/5/5. A 91-edge K14 model is also satisfiable,
has root groups 4/4/5 and a square/matching on its four sites. These are
*boundary models only*, not embeddings in a K58 colouring. They prevent a
purely local strengthening from 14 to 15 neighbours by this same template.
Model validation evaluates a negative CNF literal $-l$ by requiring $l$ to be
absent from the positive edge model rather than using a set intersection.

## 2. Conditional clause and physical guard

The rule is

$$\neg g_{x,c}\ \lor\ \bigvee_{v\in S}\neg E(x,v,c). $$

On actual guarded blocks, m2 reran both directions of the cardinality test:
forcing enough candidates false to exceed the remaining threshold bound is
UNSAT; a tight meeting of that bound is SAT; and $g=false$ with every
candidate false is SAT. This checks physical guard meaning, rather than
guessing its sender from a variable number above 6612.

The encoder starts with `needed = 14`, takes candidates $E(x,y,c)$ with
$y\ne0$ and $y$ in another root arm, excludes negative/otherwise-determined
spokes and lowers the residual threshold for positive colour-$c$ units. Its
leading `[-guard, ... clauses ...]` therefore make $g$ imply at least 14
eligible colour-$c$ spokes outside $x$'s arm, excluding $xr$. Four matching
spokes leave at most ten such neighbours in the other two groups, hence at
most 13 outside the root arm — opposed to the guard. Equivalently
$\deg_c(x)\le14$ including $xr$. Guard activation is not asserted.

m2 also recovered geometry solely from original unit pins and reconciled the
complete generated clause sets, not just their counts. Only already-positive
spokes are omitted from a negative-spoke list; the 377 omitted candidates
have different-colour unit explanations.

## 3. Fourteen ordinary-wall parents

These are fourteen selected ordinary, unsplit first-tier parents, distinct
from the thirteen full-root historical parents and from the earlier 1,300-
row cohort. They regenerate with

```python
dict(tables=True, total_critical=True, full_root=False)
```

Every parent hash matches the recorded value; every compressed batch hash and
row id matches, and all batch tiers say `first`. The exact reconstruction has
zero missing/extra rules and no bad guard, arm, root-unit, square/matching or
spoke-set bindings. Independent witness-geometry checks bind all 9,287 sets.
The K15 theorem supplies their soundness **on those checked parents**.

| wall indices with new unit-propagation exclusions | rules | surviving falsifying cubes |
|---|---:|---:|
| 0, 47 | 667, 498 | 415, 246 |
| 370 | 606 | 336 |
| 762, 945 | 820, 820 | 550, 550 |
| 1086 | 830 | 560 |
| 15533 | 950 | 590 |
| 24541 | 720 | 360 |
| 25557, 30056 | 960, 960 | 600, 600 |
| **total (ten rows)** | **7,831** | **4,807** |
| 1039, 4234, 5300, 6476 (zero) | 390, 234, 312, 520 | 0 |

There are 9,287 per-row distinct clauses across all fourteen parents;
globally there are **7,247 distinct** literal sets because 2,040 repeat across
rows. The zero-gain panel is **four rows**, two each under profiles
$(15,14,14,14)$ and $(16,14,14,13)$.

“Survives propagation” means the cube stays consistent under original-parent
unit propagation. It is a measured pruning opportunity, not a count of
previously refuted cubes. Adding the clauses refutes each negated cube by
propagation tautologically, since its own cube negates that clause; this must
not be reported as a separate strength result.

The nominated shortest original-parent cube in each of ten gain rows remains
OPEN at 12,000–12,003 conflicts. The local clause proves that configuration
unsatisfiable on the matched parent, but those calls supplied no full-parent
DRAT certificate. This distinction is kept deliberately.

The two ordinary case-0 parent hash
`160f9fb6c60638443c50d79e4fcaa64e6cdb6460db32fc61406d269a938bec00`
and the earlier signed parent hash
`ae90931dc6cd482105153dd720209e602bbfc7cc0915e18c6e87023ee2659931`
name different objects. Neither implies a result on the other or all 11,585
wall rows.

## 4. Original bounded runs

m2 repeated the eight OPEN test calls cold at a nominal 40,000-conflict cap.
Their conflict counts are 40,000–40,003, not exact budgets. CPU times are
local-clock measurements, not a general speed comparison:

| index | original parent CPU s | with square clauses CPU s |
|---:|---:|---:|
| 0 | 1.954 | 2.066 |
| 370 | 2.012 | 1.994 |
| 762 | 1.949 | 1.997 |
| 15533 | 1.911 | 2.204 |

These fresh numbers differ from the shipped archived CPU numbers; neither
set is a speedup/slowdown theorem because each comparison is single-seed and
bounded. The archive's older 10.435-second makespan, 0.0344-second matching
cost and 122,156-KiB peak RSS were also reconciled. The latter is **119.3 MiB**,
not 122 MiB. No whole-row search was run.

## 5. Thirteen separate full-root historical controls

Fresh corrected historical reruns reproduce 13/13 full-root hashes and their
mismatches when constructed with `full_root=False`. Across those controls:

* 939 seed cubes give 2,817 distinct one-spoke-flip neighbours, three per
  seed;
* 1,918 neighbours have at least one additional propagated literal after
  adding the wide-family rules, against the direct-plus-ternary baseline;
* square-scan counts are 353 / 151 / 18,528 for lengths 3 / 4 / 5;
* all controls at the tested 3,000-conflict caps remain OPEN, and proper
  subcube timeouts do **not** establish clause minimality.

All 728 tested guards lead their blocks. The corrected scope analysis finds no
off-leading negative guard occurrence, and 269,150 edge-literal occurrences
lie inside their proper sender, colour and non-arm candidate scope. The first
report's guard failures were a bug comparing literals to sender map keys
rather than guard-variable values. Its receipt was rejected; only the rerun
report and the compact receipts preserved here are used.

## 6. Provenance warnings worth retaining

1. The batch headers pin the *decompressed* local theorem proof, but
   `batches.json` pins compressed batch JSON bytes. These are different hash
   conventions. Before this audit, none pinned the shipped K15 query;
   `9fb32091…80b01` above should be persisted alongside it.
2. A batch records only `tier: "first"`, not the three encoder booleans.
   Fresh hash reconstruction binds the intended tier, but future bundle
   headers should persist all three.
3. The stock `next/verify.py` checks clause shape/propagation and clause
   counts; it does not independently derive the complete `pathcuts` set.
   m2's zero missing/extra comparison supplies that missing completeness
   check. Without it, a substituted well-formed set of the same size could
   pass.
4. `Pysat`'s `propagate` status is True if *no conflict arises*. Here 4,807
   counts surviving original-parent falsifying cubes. It should not be read
   with inverted conflict/survival semantics.
5. The archive contains 13 full-root historical and 14 first-tier ordinary
   parents. These are different panels; their premise strength and statuses
   cannot be interchanged.

Evidence is indexed in `checks/reproduction.md`. There is no Lean statement
for this package and no Lean check was done. No production ledger, cover,
queue or input was changed. Nothing here changes the public Ramsey bounds.
