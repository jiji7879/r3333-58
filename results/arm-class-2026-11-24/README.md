# The 115 arm classes and the one-arm cover census

The person proposed using the classification of triangle-free three-colourings of `K_14` — **115** up
to vertex relabelling and all colour permutations — as the working alphabet, and asked how many
survive a one-arm cover test. Both parts are now settled, and one of them was already done.

## 1. 115 is the same object as the campaign's 332, and this is now verified

The campaign's alphabet (`armtypes14.txt`) holds **332** types, quotiented by vertex permutation and
the single colour swap `2<->3`. Computing the full `S_3` colour orbits of those 332 by exact
isomorphism (VF2 with edge-colour matching, binned by the colour-degree multiset):

```
S3-colour orbits: 115
orbit size distribution: {3: 102, 2: 13}      102*3 + 13*2 = 332
```

So the literature's 115 and the campaign's 332 are the same set, and the 13 short orbits are exactly
the types with a colour symmetry. No download is needed; the classification is already in the tree.

## 2. The cover test was already run, and it is the campaign's "placement" census

The proposed test — ten 5-sets and five 4-sets with multiplicity, every vertex covered exactly five
times, each set carrying the two-colour pentagon structure — is exactly what swarm `smwswz4x9`'s m4
computed for all 332 types. Its results, independently checked at the time (the 37-type list matches
the campaign's own `excluded14.txt` entry for entry):

```
332 types:  37 admit NO placement  ->  excluded as arms
           295 admit a placement    ->  survive this layer
```

## 3. New: the answer is not well defined on the 115 alone

Whether a type admits a placement depends on **which internal colour is the one the set avoids** —
i.e. on the role assignment, exactly as the proposal anticipated by saying "and each choice of which
internal color is 0". Lifting m4's per-type verdicts to the 115 classes:

| class behaviour under colour permutation | classes |
| --- | ---: |
| survives for every role assignment | **88** |
| dies for every role assignment | **5** |
| status depends on the role | **22** |

So "how many of the 115 survive the cover test" has no single answer: 88 always survive, 5 never do,
and 22 are mixed. The honest unit is the pair (class, role assignment), of which there are 332 and of
which 295 survive.

The 22 mixed classes are the interesting ones for the next step, because their survival is a
statement about how the arm's colouring is embedded in the root, not merely about its isomorphism
class.
