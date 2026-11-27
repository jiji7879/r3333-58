# Direction A — local witnesses versus the advertised “full cover”

## Outcome

The archive contains **real, explicitly checkable local certificates**, not just solver status labels. In a bounded independent audit I regenerated case 0’s physical projection and signed row constraints and directly checked its two saved assignments, the six current initial/robust assignments for the same normalized owner, and both 26-vertex repairs. All ten passed the applicable local edge, sign, triangle, degree, pentagon, word, owner-order and pivot checks.

This establishes local satisfiability for those concrete projections. It does **not** produce a coloring of $K_{58}$, close a wall row, or prove any Ramsey upper bound. “Full cover” is exhaustive **roster/branch bookkeeping with one local model per normalized key**, not a global extension theorem.

## 1. What case 0 actually is

`case0.json` has two records for row
`00032f347903758c89e2187f30f0e1c07aecb21bd27c149fb43aef0ccdb60f0d`, arm size 14, owner pair $p=(00000,01022)$, branch palette indices 1 and 2. The first record in `maps.jsonl.gz` supplies 25 physical vertices and palette `[1,0,3,2]`.

I regenerated that map from the frozen row, placement and nominated-arm binding, rather than accepting the JSON. The raw wall data have the SHA-256 expected by the inspected helper source,
`d5641e1ba875bc4ec5fbe156d48585f610e877f5232de7181eb464d4ad4fa2bc`, and the row-ID hash also recomputes correctly. The regenerated list is exactly:

- nominated arm, in local positions 0–13:
  `[31,32,35,33,34,36,37,38,39,40,41,42,43,44]`;
- full projection: the arm followed by
  `[17,1,0,45,46,47,48,15,14,12,10]`.

The vertices outside this projection are listed explicitly in `case0_audit.json`; there are 33, including vertex 5. This implements the construction in `scale.py:23-40`: `T+O`, then the marked vertex `q=17`, then the remaining marked/root vertices. The row has 404 signed unit literals, 138 of which lie wholly in this projection (129 positive and 9 negative).

Stored coloring characters are **palette positions**, not physical color names. The revised pivot, independently read from the case’s propagated rule record, is local arm edge $(0,11)$, hence physical edge $(31,42)$. Therefore:

| case-0 record | stored branch $c$ | physical pivot color `PAL[c]` |
|---|---:|---:|
| 0 | 1 | 0 |
| 1 | 2 | 3 |

The use of the **revised** pivot for these two retained examples is also explicit in `repair.py:16-18`. They should not be confused with the original-convention branch-0 record for this owner. In my normalized owner tables, $p$ has original rank 1 and revised rank 0.

### Local memberships checked

For each 300-character, 25-vertex assignment, the checker verifies all of the following, using only explicit assignments (no SAT status trusted):

1. **Complete edge assignment and domains.** Exactly one character in `0..3` per local edge; edges internal to the 14-vertex arm use only colors `0..2`, as required by `support_helpers.py:10-30`.
2. **Signed row units.** Every one of the 138 projected signed literals agrees after applying `[1,0,3,2]`.
3. **All local triangles.** All $\binom{25}{3}=2300$ triples are non-monochromatic.
4. **Local degree caps.** At every selected vertex and in each palette class, at most 16 incident selected edges have that color. Both case-0 examples have maximum local monochromatic degree **15**, attained at physical vertex 17.
5. **Nominated pentagon/glyph, words and order.** The first five arm vertices have the required two-colored pentagon. The first two outside-star words are exactly `00000` and `01022`; the other seven outside-star words are lexicographically sorted. The minimum owner pair present under each supplied original/revised owner bank is exactly $p$. These are the conditions in `helper_reference/adaptive/arm_pairs.py:66-78,89-96` and `helper_reference/adaptive/edge_domains.py:38-44`.
6. **Selected edge.** The extracted 91-edge arm coloring has the claimed branch color at the original or revised pivot, as appropriate.

The full outside-word lists, assignment hashes and every numerical result are in `case0_audit.json`. `audit_case0.py` is the standard-library-only checker; it imports none of the supplied scripts.

### Bounded results

| records checked independently | vertices | edges each | triangles each | projected signed literals each | max local degree | result |
|---|---:|---:|---:|---:|---:|---|
| 2 retained `case0.json` witnesses | 25 | 300 | 2300 | 138 | 15 | all applicable checks pass |
| 3 initial + 3 robust current records for the same owner/key | 25 | 300 | 2300 | 138 | 15 | all pass |
| 2 `repairs.json` records | 26 | 325 | 2600 | 145 | 15 | all pass, including arm/pivot/word/order |

These are model checks, so they justify **SAT for the specified finite projected formulas**. They do not turn unchecked constraints into SAT and do not involve UNKNOWN.

## 2. Exact local-versus-global scope

A 25-vertex case-0 witness assigns

$$\binom{25}{2}=300 \quad\text{of}\quad \binom{58}{2}=1653$$

edges: **18.1488%**. It leaves **1353** edge colors unspecified: $25\cdot33=825$ projection/exterior edges and $\binom{33}{2}=528$ exterior/exterior edges. Likewise it checks 2300 of the 30856 triples in $K_{58}$, leaving 28556 triples outside the all-local triangle test. A local degree of at most 16 does not constrain the 33 still-uncolored edges at that vertex to admit any particular global completion.

For a branch $b$, a saved record proves a statement of the form

$$\exists y_b\; \operatorname{Local}_b(y_b).$$

Full-cover inventory aims to establish this for every enumerated branch $b$. A global counterexample would instead require **one** branch with **one** full assignment $X$ on all 58 vertices satisfying every global constraint; its restriction would then be a local model. Thus

$$\forall b\,\exists y_b\,\operatorname{Local}_b(y_b)
\;\not\Rightarrow\;
\exists b\,\exists X\,\operatorname{Global}_b(X).$$

Different owners/branches are alternatives, not pieces that all must be glued simultaneously. The missing step is not “make all the displayed local strings mutually agree”; it is to extend **at least one** branch fully, or, for the opposite whole-row closure, refute global extension of **every** required branch. Consequently no fixed-row or whole-row upper bound follows from the local branch counts.

### The three different units being counted

The code distinguishes these, but a casual reader can easily conflate them:

- **19,048 saved normalized records.** My scan counts 8,174 original-convention and 10,874 revised-convention records, aligned across 41 geometries.
- **11,585 physical rows.** `maps.jsonl.gz` reuses a normalized geometry on many rows.
- **1,967,548 revised branch incidences.** Independently summing `live_count` in the separately supplied live roster gives 983,774 representatives; `scale.py:44-53,111-124,132-135` counts two allowed pivot colors per representative. This matches the summary arithmetic, but is not a regeneration of every saved model.

A concrete normalization example: geometry 0 occurs on **545 rows**. For $p=(00000,01022)$, the current original branch-0 record has recomputed multiplicity 545, and each current revised branch-1/branch-2 record has multiplicity 545. One normalized string is therefore reused on hundreds of row incidences; it is not hundreds of independent global models. My multiplicity computation uses the saved maps and live ranks; I did not independently re-check all those 545 physical sign placements.

Case 0 itself has 47 revised representatives, hence 94 revised branch incidences on its row. The two retained examples therefore concern one owner/two branches on one of 11,585 rows, versus 1,967,548 revised incidences in the advertised full inventory. Their two-witness fraction of that inventory is $2/1967548\approx1.0165\times10^{-6}$ (about 0.00010165%).

Also, `case0.json` retains the earlier examples promised by `README.md:11`; its strings are not the current full-cover strings. Relative to the current initial revised records, they differ in 61 (branch 1) and 45 (branch 2) edges; relative to robust records, in 51 and 45 edges. All 91 arm edges agree. The first difference is full-text edge position 119, local vertices $(5,15)$, physical vertices $(36,1)$. Therefore a defect in a retained case-0 string cannot be silently attributed to a different current record.

## 3. Why the first two local witnesses can still be non-extendable

I independently regenerated the row signs for exterior vertex 5. Toward anchors $(1,10,12)$ it has physical colors $(3,2,1)$. In **both** retained case-0 assignments, each of vertices 43 and 44 has stored palette-index triple $(2,3,0)$ toward those anchors, which maps to the same physical triple $(3,2,1)$.

For any pair $x,y\in\{5,43,44\}$, edge $xy$ cannot have physical color 3 (the triangle with anchor 1 would be monochromatic), nor 2 (anchor 10), nor 1 (anchor 12). It must therefore have the fourth physical color 0. All three mutual edges are then 0, making a monochromatic triangle on $\{5,43,44\}$.

This is a complete finite contradiction: **neither exact 25-vertex assignment can extend even to the 26-vertex set consisting of the projection plus vertex 5.** It does not refute its owner branch, all local colorings, or the whole row. In particular, the obstruction uses the two older `case0.json` strings and does not automatically apply to the different current records above.

The repairs illustrate the correct quantifier. `repair.py:9-15` fixes only the 14-vertex arm, allowing other projected edges to change. I checked both new 26-vertex assignments directly; they pass their local constraints. This resolves that particular obstruction for those replacement assignments while retaining the arm, but 32 vertices and $1653-325=1328$ edges remain unassigned. A successful replacement is still not a full $K_{58}$ model.

## 4. Replay boundary and acceptance criteria

The main ZIP is **not standalone**. `scale.py:11-18` imports helper modules and PySAT, and `replay.py:37-48` requires a separately supplied `K58_three_seconds` tree, its runner, frozen reference inputs and native tools. That complete tree is not included in this ZIP. I did not run `replay.py`, an archive solver, or any RUP proof, and I make no complete-replay claim.

For the bounded reconstruction only, I used raw inputs and rule/label records from the adjacent `K58_wall_campaign.zip` and `K58_adaptive_wall_solver.zip`, copied under `helper_reference/` in this member directory. Relevant helper code was inspected before use. The final checker itself is independent and executes no supplied code. Running `python3 audit_case0.py` under CPython 3.12.14 regenerated `case0_audit.json`; it does no broad search.

An audit of claims at these levels should require:

1. **Verified local witness:** regenerate the exact key, physical vertex order, palette, domains and signed units; check complete edge values, every local triangle, local caps, pentagon/words/order and selected pivot against an explicit model. State exactly which projection was checked.
2. **Refuted obstruction:** regenerate the exterior sign pattern and prove the contradiction with the disputed assignment fixed. A small explicit argument suffices; otherwise require an independently regenerated CNF and strict proof check (`-i -U`, exit 0, exactly one `s VERIFIED`, zero warnings, no `-w`). One failed assignment is not branch UNSAT.
3. **Validated replacement:** apply all local checks to the new string, verify exactly what was held fixed (here only the arm), and independently check every applicable exterior placement claimed by the repair stage. Non-null and SAT are not interchangeable with global extension.
4. **Global or whole-row result:** require either a full 58-vertex model satisfying all constraints, or a rigorous global refutation for every member of an independently regenerated exhaustive roster, with valid composition. A timeout/UNKNOWN never discharges either side; local coverage, later partial SAT records and degree/support certificates do not compose into such a result by themselves.

The useful progress here is therefore finite necessary-condition screening, concrete local models, and precise assignment-level counterexamples/replacements. The hard bottleneck remains full extension or global refutation. Nothing in this direction supports a new $R\le58$ theorem or the claim that most unexplored local choices are global models.
