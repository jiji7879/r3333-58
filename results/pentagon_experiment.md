# Experiment 2 (six pentagon configurations): what it is worth

## The reduction is sound

R(5,5) <= 46 (Angeltveit-McKay) applied to any palette split {a,b}|{c,d} on the full
vertex set: with n >= 51 there are at least 46 vertices, so a 5-set A whose 10 edges use
only {a,b} exists. Being good, A is C_5 + C_5 (verified: exactly 12 two-colourings of K_5
with no monochromatic triangle, all with colour-0 degree sequence (2,2,2,2,2)). Removing A
leaves 46 vertices, exactly enough for the second split, and again for the third, giving
B and C both avoiding A.

Palette triples: one pair chosen from each of the three splits gives 8 transversals; under
the colour group S_4 these fall into exactly 2 classes - "star" {01},{02},{03} and
"triangle" {01},{02},{12}. |B cap C| >= 3 forces a monochromatic triangle (the three edges
of a 3-subset of B cap C lie in the intersection of the two palettes, a single colour), and
|B cap C| = 2 forces that one edge to the common colour. So six patterns, as handed down.

## But it is a relabelling, not a reduction

Fixing A, B and C to concrete vertex sets is *justified* by symmetry - S_51 acts on
vertices, and after fixing A the remaining S_46 moves B and C to canonical positions
consistent with the shared vertices. The six-pattern list is complete and the split is
sound. The problem is that it buys nothing:

* one triple pins at most 3 x 10 = 30 of the 1275 edges, i.e. 2.4% of the structure;
* there are very many such triples. Independently counted in the verified
  `artifacts/k50_z4z4_m6.col`: 5-sets whose edges use only a given colour pair number
  452, 283, 263, 465, 460, 313 for pairs 01, 02, 03, 12, 13, 23 - 2,236 in total. So a
  single instance of a case is one of ~2.2e7 choices in a K_50, worth about 25 bits out of
  the ~10^100 bits of a colouring.

Consequence measured by the swarm's m6 (24 instances, including six satisfiable by
construction): every one undecided at 60 s, and no case easier than the plain instance.
That matches what a 2.4%-of-edges pinning should do: nothing.

## Verdict on the experiment

Do not give Experiment 2 more compute as a reduction. It is a correct statement about the
structure of any good colouring and a legitimate way to generate *sample* sub-families,
but the residual instance is the original problem with 30 edges nailed down.

The correction to record: m6's report calls fixing (A,B,C) "an unjustified restriction
whose complete treatment needs about 1.9e12 triples". That is wrong on the logic - the
restriction is justified by vertex symmetry, one canonical triple per pattern suffices, and
the triple count only matters if you refuse to quotient. The conclusion is right for the
different reason above.

## Where the leverage actually is

A split is only worth running if fixing the canonical object pins a large fraction of the
edges. A colour-degree-16 link pins 120 edges and has only 2 isomorphism types; a link of
size 12 pins 66 edges and has 472,803 types. That is why the neighbourhood/link split is
the only family split on the board with real leverage - and why the open question is
whether a size-16 link is realisable at all.
