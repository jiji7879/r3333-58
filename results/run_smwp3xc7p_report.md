# R(3,3,3,3), run smwp3xc7p: what the two handed-down experiments gave

Question: does a good 4-colouring of K_51 (or K_52) exist? Bounds unchanged:
51 <= R_4(3) <= 60. **No witness was found and no family containing one was excluded.**
Two things were accepted: an exact symmetry classification (m7) and 1,018 certified
closures in the K58 cover (m3).

## Experiment 1: single circulant colour class on Z/52

Colour 3 is exactly the circulant with distance set D; the other three colours are free.

* Verified setup: D = {1,3,5,7,9,11,24,26} is triangle-free, degree 15, inclusion-maximal;
  N_3(0) is a 15-set with no colour-3 edge, so it carries a good 3-colouring of K_15.
* Monotonicity (so the sweep is finite): if D works and D' superset of D is triangle-free
  then D' works, so only inclusion-maximal D need deciding.
* Census (computed three times independently): 33,752 triangle-free D, 1,102 maximal,
  104 orbits under the 24 units. **The handoff's 217 / 71 does not reproduce.**
* 6 of the 104 orbits are excluded with no search: four by colour-degree > 16
  (degrees 17, 17, 18, 26); two by alpha(C(D)) > 16, since a 17-set with no colour-3 edge
  would 3-colour K_17 with no monochromatic triangle. Alpha values 20 and 26 re-checked
  with igraph. 98 orbits remain open.
* The fully circulant subfamily is decided: no good circulant colouring of K_n exists for
  n = 45, 46, 50, 51, 52, 53 (SAT at n = 40, 43, 44 with verified models), consistent with
  the closure of the Cayley subfamily for all 104 masks.
* Local structure closes nothing: pairwise neighbourhood gluing is SAT for every one of the
  1,237 constrained distances across all 98 open orbits, for the three-neighbourhood version
  (112 instances), and for unions of up to 11 roots.
* The full instances do not yield: cadical and kissat undecided at up to 50 min per mask in
  four configurations built here plus three configurations built by a member; tabu search
  over the 936 free edges plateaus at 302-334 of 8,060 monochromatic triangles.
* **Status: 98 orbits open. Exact reason: every sound relaxation tested is satisfiable, and
  no solver available here decides the full instances.**

## Experiment 2: the six pentagon configurations

The reduction is sound - R(5,5) <= 46 gives a 5-set A on one colour pair (necessarily
C_5 + C_5), 46 vertices remain for the other two palette splits, the palette triples fall
into 2 classes under S_4, and |B cap C| >= 3 forces a monochromatic triangle - so six cases,
complete.

It is also inert. Fixing A, B, C is justified by symmetry but pins at most 30 of 1,275
edges (2.4%), and one verified K_50 contains 2,236 such 5-sets, so a case instance is one of
~2.2e7. All 24 instances tested were undecided at 60 s, **including the six that are
satisfiable by construction**. Do not give this split more compute.

## The leverage criterion (the run's portable result)

A split is usable only if it is exhaustive, few-typed, and leaves a decidable instance.
Measured at n = 51 (edges pinned / total, types):

| split | pinned | types | exhaustive | free |
|---|---|---|---|---|
| six pentagons | <= 30 (2.4%) | ~2.2e7 | yes | >= 1245 |
| link 16 / 15 / 14 / 13 | 136/120/105/91 | 2/2/115/>=6807 | yes | 1139/1155/1170/1184 |
| edge link | 1 | 1 | yes | 1274 |
| circulant Z/52 | 390 of 1326 | 100 orbits | no | 936 |
| folded involution (f=1 / f=0) | 650 of 1275 / 676 of 1326 | 26/27 | no | 650/676 |
| pinned good K_50 + lift | 1225 (96.1%) | unclassified | no | 50 |

**Every exhaustive row leaves >= 1139 free variables; every row that pins heavily is
non-exhaustive.** At n = 51 exhaustive and tight cannot both be had with any structure on
this board. That is a measured explanation of why the bound is stuck, and it agrees with all
three splits failing independently.

## Accepted results

1. **m7, cyclic two-orbit actions.** For 2 <= m <= 26, good 4-colourings of K_{2m}
   invariant under a cyclic action with two orbits of size m exist exactly for
   m in {2,4,5,7,8,10,11,13,14,16,17,19,20,22} and not for m in {3,6,9,...,21,23,24,25,26};
   the 11 empty cases have DRAT proofs (two replayed by the judge) and the 14 non-empty
   cases are verified matrices. So no good K_46, K_48, K_50 or K_52 has an automorphism of
   cycle type two m-cycles with m >= 23. The multiples of 3 are exactly what the
   machine-checked order-3 theorem forces, so the computation independently corroborates it.
2. **m3, K58 cover.** 1,018 previously OPEN cases of the frozen 113,179-case cover are now
   CERTIFIED, each with a DRAT proof replayed against a CNF regenerated from the frozen
   ledger row; 64 replayed by the judge with the repository's own verifier, 0 failures, and
   a truncated certificate is correctly rejected (negative control). OPEN 111,035 -> 110,017.
   **Quote 1,018, not 1,050**: 32 of the 1,050 certificates were re-derivations for cases
   already certified. This is upper-bound work; it says nothing about the lower bound, and
   the cover's reduction remains unaudited, so R_4(3) <= 58 is still unproved.

## Corrections to the handoff (all verified independently, some by three members)

* The circulant census is 33,752 / 1,102 / 104 orbits, not 217 / 71.
* "A circulant colour class must have degree 12, 13, 14 or 15" is not a theorem. Maximal
  triangle-free masks exist at degrees 10, 11, 16, 17, 18 and 26; 17, 18 and 26 die by the
  colour-degree lemma and 10, 11 do not. The provable window is [3,16].
* "Every colour degree <= 15" is false: the bound is 16, attained in all three verified
  K_50s and in the 1-defect K_51 record, so a split over sizes 13/14/15 omits exactly the
  cases that Chung-type colourings realise. Size 16 needs both K_16 templates.
* Template gluing must be done at the LABELLED level. The classification of good K_15
  colourings is up to vertex relabelling, so instantiating one representative per class
  manufactures false inconsistencies (a member's labelled version called 11 of 13 orbits
  inconsistent; the unconditional instances are all satisfiable).

## Open

* 98 circulant orbits; the degree-16 cell (locally realisable for all 24 profiles at n=51
  and both templates, so not excludable by counting or propagation); general involutions;
  Z/17 actions at n=51; Z/13 actions at n=52.
* The lower bound itself: no good K_51, no proof that none exists.
* One judge error, caught by a member: an outside vertex has at least m_j - 15 >= 1 edges of
  the LINK colour into N_3(v), not "at least 6 colour-0 edges". The colour absent inside
  N_3(v) is the link colour.
