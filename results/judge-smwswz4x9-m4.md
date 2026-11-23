# Judging m4 of `smwswz4x9`, and what that swarm settled

The swarm ended **solved**, 8 directions accepted (d8 abandoned). This file records the judge's
check of m4 and the one cross-member issue the board cannot see.

## m4, direction d4 — accepted

Claim: 37 of the 332 arm types admit no zero-set layer at all; for the remaining 295 the exact set
of realisable multiplicity profiles is computed per type; and the 219/113 no-singleton split is
reproduced independently.

What the judge checked, with its own code:

- **An independent enumerator.** The judge wrote its own graph6 decoder for `armtypes14.txt` and its
  own placement search from the definition — fifteen rows, ten 5-supports and five 4-supports, no
  colour-0 edge inside a row, colour-1/2 degrees `1,1,2,2` on a 4-set and `2,2,2,2,2` on a 5-set,
  every vertex in exactly five rows. It reproduces the submission's numbers exactly: type 2 → **2
  placements, 1 profile** `(2,1^12)`; type 9 → **352 placements, 7 profiles**, the profile sets
  identical to the submission's.
- **R6 confirmed on its sharpest cases.** That same enumeration finds `(5,4,4,1)` and `(5,5,4)`
  realised, on type 9, with placements the judge constructed and checked. So those two exclusions
  genuinely cannot be obtained inside one arm.
- **R1 confirmed by an argument the submission did not have.** The campaign's own support-incidence
  computation (`.scratch/cac/excluded14.txt`, produced independently by `verify.py` in job
  `jmwsj2030`) lists 37 types, and they are **identical to the submission's 37, entry for entry**.
  Two different arguments, same list.
- **Witnesses.** The submission's checker passes 5,180 witnesses on 295 types, 0 failures; before
  running it the judge had already checked four witnesses with its own code, 0 failures.
- **Data consistency.** 332 types, 332 searches marked COMPLETE, 37 with zero placements, 219
  realising `(3,3,2,2,2,2)`, 48 allowed profiles with 33 realised and 15 never, and of the 9 allowed
  profiles containing a 5 exactly one `(5,2,2,2,2,1)` is realised. All recomputed from the TSV and
  `allowed.txt`.

Not verified: the exhaustive searches themselves (the judge re-ran 2 of 332 types), so the 15
never-realised profiles and the other 330 completeness claims rest on the submission's enumerator.
No DRAT exists for the 37, as the submission's §6 states.

Correction sent to the member: the report calls the 48 "profiles that survive the established
theorems", but the 48 is the **candidate** list and contains the four the campaign's theorems
exclude — all four appear among its own 15 never-realised. The surviving set is 44, not 48.

## The cross-member issue: 44 is not the end of the layer

m5 (direction d2) reports "44 profiles survive ... **The arm-local multiplicity layer is
exhausted: it cannot exclude any of the 44.**" m4 reports that only **33** of the 48 candidates are
realised. On the surface those contradict.

They do not. They decide **different layers**:

- **m5's model** is the incidence layer: classes are distinct 5-subsets of `A`, with
  `d(a) = Σ multiplicity over classes meeting a ∈ {4,5}` for each of the 15 points `a`. Its
  witnesses (`survivors.md`) are support families on the 15-point set `A`; nothing there requires
  the pattern to come from an actual triangle-free 3-colouring of the 14-arm.
- **m4's model** adds exactly that: its rows must be *admissible* in the arm's own colouring
  (no colour-0 edge inside a row, the induced 4-path-pair or 5-cycle-pair structure), which is what
  the template classification forces on every `F_a`.

m4's filter is therefore strictly stronger, and the combined statement is:

> 48 arithmetic candidates → 4 excluded by the packages → **44 survive the incidence layer (m5)**
> → of those, only **33 are realised by some arm type** (m4); 11 more die at the arm-realisation
> layer.

The 11 are `(4,2,1^8) (4,3,1^7) (4,4,1^6) (5,1^9) (5,2,1^7) (5,2,2,1^5) (5,2,2,2,1,1,1)
(5,3,1^6) (5,3,2,1,1,1,1) (5,3,2,2,1,1) (5,3,3,1,1,1)`.

This supersedes the standing line in the campaign record — "44 profiles survive and no multiplicity
argument removes a survivor" — which was true of the incidence layer only. The multiplicity layer is
**not** exhausted; it leaves 33, and the arm-realisation census is what removes the other 11.

## What the swarm settled, direction by direction

| dir | member | verdict |
|---|---|---|
| d1 | m2 | six-distinct verified as far as the join layer; residual reduced to 3 internal signatures; **join layer not replayed** |
| d2 | m5 | 48 candidates, 44 survive the incidence layer, 4 excluded with DRAT and short proofs; layer exhausted *at that level* |
| d3 | m1 | repeated-pentagon codegree: finite core correct, chain checks out |
| d4 | m4 | per-type zero-set census: 37 types dead, 33 profiles realised, 219/113 reproduced |
| d5 | m8 | no-singleton case is **compatible** with the whole layer; two new kernel lemmas; 219 census reproduced |
| d6 | m7 | cross-arm transfer partial: decided instances + kernel lemmas, general statement **not** proved |
| d7 | m6 | design filter decided for all 135 partitions (53 with a design, 82 without) |
| d9 | m3 | forced-pentagon parent rule kernel-checked |

Net effect on the campaign: the zero-set multiplicity layer is now charted to its arm-level bottom
(33 profiles), the no-singleton case is confirmed compatible rather than contradictory, and the one
route still open inside this layer is cross-arm transfer, where m7 leaves the general statement
unproved.
