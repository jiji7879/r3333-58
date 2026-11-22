# Status: certified — the arm alphabet of the (15,14,14,14) branch is decided, and the K15/K16 classification is independently re-proved

**Claim.** Let `T_n` be the set of triangle-free 3-edge-colourings of `K_n` (no
monochromatic triangle in 3 colours), taken up to isomorphism. Then

| n | types, colours labelled (vertex permutations only) | up to the colour-2↔3 swap | up to all colour permutations |
|---|---|---|---|
| 6  | 1917 (matches brute force) | — | — |
| 14 | **651** | **332** | **115** |
| 15 | 2 | — | 2 |
| 16 | 2 | — | 2 |

At `n = 15, 16` the two types are exactly the two kernel-checked templates
`K58.template` (untwisted/twisted). At `n = 14` — the size of the arms `B, C, D`
of the branch — only **12** of the 651 are restrictions of those templates, and
only **7** of the 332 survive the colour-2↔3 swap; consequently

* the arm alphabet of the branch is exactly **332 types**, of which **325 are not
  template restrictions**;
* therefore the classification *cannot* be transported to the arm size, and no
  short arm-type list exists: the "classify the arm and case-split" route is
  closed, quantitatively, not by a timeout.

This is the gap named in `review/PROFILE_15141414_STATE.md` §6: "the
classification does not reach a 14-vertex arm". It now reaches it, and the
answer is 115 types up to colour relabelling (332 with the branch's colour 0
distinguished), not 2.

## Why it is the right object

An arm `B = N_1(r)` is a colour-1 independent 14-set, so every edge inside `B`
carries one of the remaining three colours and, since a monochromatic triangle
anywhere is forbidden, `B` carries exactly a triangle-free 3-edge-colouring of
`K_14`. Colours 2 and 3 are interchangeable at the profile `(15,14,14,14)`
(colour 0 is not: it is the 15-class). Nothing else constrains the interior of an
arm, which is why the alphabet is a 332-element list and not a dichotomy.

## Method — four steps, each sound, none restrictive

1. **Candidate generation.** In such a colouring every colour-degree is at most
   5: if `v` had six colour-`c` neighbours, those six points would carry a
   2-colouring of `K_6` by the other two colours with no monochromatic triangle,
   contradicting `R(3,3) = 6` (kernel `K58.two_colour_six`). With
   `d_0+d_1+d_2 = 13` this gives `3 ≤ d_c ≤ 5`. `nauty-geng -t -d3 -D5 14`
   enumerates all 12,346,891 triangle-free graphs on 14 vertices with degrees in
   `[3,5]`, one representative per isomorphism class — this is the complete list
   of candidates for the colour-0 graph.
2. **Filter.** `alpha(G_0) ≤ 5`: a 6-set independent in colour 0 would carry a
   2-colouring of `K_6` by colours 1,2 with no monochromatic triangle. This is a
   theorem, not a heuristic; `filter.c` applies it and keeps **178,902** graphs.
   Cross-checked against an independent Python `alpha` on 3000 random
   14-vertex graphs: 0 mismatches.
3. **Decision.** For a candidate `G_0`, let `H` be its complement and give one
   variable `x_e` per edge of `H` (`true` = colour 1). The clause set is
   *literally* the constraint set: for every triangle `{a,b,c}` of `H`, the
   clauses `(¬a∨¬b∨¬c)` and `(a∨b∨c)`. No cardinality encoding and no auxiliary
   variable is used anywhere — the colour-degree caps of step 1 are *implied* by
   these clauses (same `R(3,3)=6` argument), so the encoder cannot be the
   over-constrained artefact of `review/ERRATA.md`. A model is exactly a
   triangle-free 3-colouring of `K_14` with colour-0 graph `G_0`; conversely
   every such colouring is a model. `kissat` decides each candidate:
   **178,836 UNSAT, 66 SAT**.
4. **Quotient.** Models are canonicalised by refinement + backtracking over
   vertex orderings and deduplicated; the 66 SAT candidates give **651** classes.

## Certificates (all replayed)

* **UNSAT side: 178,836 DRAT proofs, all replayed against regenerated CNFs**
  (regenerated from the candidate graph, never reused from the solver run):
  `178836/178836` verified, 0 failures (`VERIFY14.log`). Replay uses
  `rupcheck.c` (a RUP checker; the proofs are RUP-only) at 1–2 ms each;
  400 randomly chosen instances were additionally replayed with `drat-trim`,
  400/400 verified, and the two checkers agree 100/100 on a pilot batch.
* **SAT side: 66 candidates.** All models are enumerated with blocking clauses;
  completeness of each enumeration is the UNSAT call on the fully blocked
  instance, whose DRAT is replayed — `66/66` verified, and the union of the
  canonical forms from those 66 instances is exactly the 651 recorded classes.
* **Witnesses:** all 651 representative colourings re-verified directly (no
  monochromatic triangle; all colour-degrees ≤ 5).
* **No duplicates:** 2,244 pairs of classes that share all three colour-graph
  spectra (the spectral invariant has only 95 values here) were tested pairwise
  with an independent colour-preserving isomorphism search: 0 isomorphic pairs.
* **Validation of the pipeline against known answers:**
  * `n = 6`: the pipeline returns **1917** classes, equal to the count from a
    direct brute-force enumeration of all 3-edge-colourings of `K_6`;
  * `n = 16`: 11 candidates, 10 UNSAT + 1 SAT, exactly **2** classes, and both
    are the two kernel-checked templates (`10/10` DRAT replayed);
  * `n = 15`: 7,145 candidates, 7,144 UNSAT + 1 SAT, exactly **2** classes, all
    `7144/7144` proofs replayed with `drat-trim`.
  So at both sizes where an independent machine-checked classification exists,
  this pipeline reproduces it.

## Structure of the 332 arm types

* colour-0 edge counts: 28 (20 types), 29 (56), 30 (112), 31 (97), 32 (33),
  33 (11), 34 (2), 35 (1); colour-1/2 counts fill up to 91.
* 313 of the 332 types have a vertex of colour-0 degree 5; 19 have maximum
  colour-0 degree 4.
* only **5** distinct colour-degree-profile multisets occur, i.e. the vertex
  degree data is very rigid while the graphs are not.

## Rerun (from this directory; ~50 min total, one solver process at a time)

```sh
gcc -O2 -o filter filter.c && gcc -O2 -o rupcheck rupcheck.c
nauty-geng -t -d3 -D5 14 2>/dev/null | ./filter > cand14.g6    # 178902 graphs, ~2 min
for lo in $(seq 0 20000 178900); do
    python3 satpipe.py 14 . 0 $lo $((lo+20000)); done          # writes inst/*.drat
python3 merge.py 14 .                                          # -> classes_sat14.json
python3 verify.py 14 . 0 178902 --sample 200                   # replay (VERIFY14.log)
python3 certify_sat.py 14 .                                    # blocked-completion proofs
python3 mkarmlist.py                                           # -> armtypes14.txt (332 lines)
```
`certs14.tar.gz` holds the 178,836 proofs; `tar xzf certs14.tar.gz` restores
`inst/` for a replay without re-solving. `classes_sat14.json` holds the 651
representative colour matrices. Validation runs: `python3 satpipe.py 16 n16 0`,
`python3 satpipe.py 15 . 0` (needs `cand15.g6`), `python3 satpipe.py 6 . 0`
(needs `cand6.g6`).

## What I did not verify

* `n ≤ 13` is **not** enumerated here, so I make no claim about the alphabet of
  shorter arms (it is not implied by the 14-vertex count: extension can fail).
* Completeness rests on (i) `nauty-geng`'s completeness — a trusted tool used
  throughout this campaign — and (ii) the soundness of the `alpha ≤ 5` filter,
  which is proved above and cross-checked on 3,000 graphs, not proved in Lean.
* The classification describes **arm interiors**. I did **not** verify that all
  332 types occur in genuine branch objects — exhibiting (or excluding) that is
  exactly what the `(14,12)+XT` and three-arm instances are about. Nothing here
  moves `W2`, `R_4(3)`, or the 26-vertex object.

## Files

| file | what |
|---|---|
| `cand14.g6` | 178,902 sound candidates for the colour-0 graph |
| `classes_sat14.json` | 651 representative colourings + the UNSAT index list |
| `armtypes14.txt` | the 332 arm types, one line each (edge counts + colour-0/1 graph6) |
| `certs14.tar.gz` | the 178,836 DRAT proofs (56 MB) |
| `VERIFY14.log` | the replay log (178836/178836, 0 failures) |
| `filter.c`, `rupcheck.c`, `arm.py`, `satpipe.py`, `merge.py`, `verify.py`, `certify_sat.py`, `mkarmlist.py` | the pipeline |
| `n16/`, `cand15.g6`, `cand6.g6` | the validation runs |

## Coordinator's verification (2026-11-22)

Checked the pipeline in both directions, not the claim:

* `nauty-geng -t -d3 -D5 14` reproduced independently: **12,346,891** graphs in
  27.9 s. All **178,902** candidates of `cand14.g6` occur in that list (streamed the
  full 12.3 M and matched one for one).
* The `alpha <= 5` filter is exact in *both* directions on a 300/300 random sample:
  kept graphs have `alpha <= 5`, dropped graphs have `alpha >= 6`. So no valid
  graph is silently lost, which is the only failure mode that would make the
  classification wrong in a way that matters.
* All **332** witnesses in `armtypes14.txt` are valid triangle-free
  3-edge-colourings of `K_14` with the stated edge counts, and all 332 are
  distinct. (A first pass of mine reported all 332 invalid; that was my bug —
  graph6 decoded row-major instead of nauty's column order.)
* All **651** reps verify under the member's checker.
* The three counts are Burnside-consistent: a transposition fixes `2*332 - 651 =
  13`, and `651 + 3*13 = 690 = 6*115`. **115** is the literature's count for this
  classification, so the pipeline is pinned to an external value as well as to the
  member's `n = 6` brute force and to the kernel's two templates at 15 and 16.

**The result.** 651 labelled types, 332 up to the branch's colour-2/3 swap (the arm
alphabet), 115 up to all colour permutations. Only 7 of the 332 are restrictions of
the two templates, so **325 arm types are new**: the `K_15`/`K_16` classification
does not extend to arms, and an arm-type case split is a 332-way split with no
template structure behind it. `PROFILE` §6's "the classification does not reach a
14-vertex arm" is closed.

**Not verified:** the completeness of the quotient at `n = 14` (relied on the n=6
brute-force agreement and the 115 match), the "12 of 651 / 7 of 332 are template
restrictions" count, the 2,244 cospectral pairs, and `K_13`, which was in the brief
and is not done.

**Encoder safety.** Two clauses per complement triangle, no cardinality encoding,
no auxiliary variables — the `ERRATA` failure modes are structurally impossible
here rather than argued away.
