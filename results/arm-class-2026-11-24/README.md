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

## 4. The per-sender triple test prunes nothing (m5, verified here)

At a sender `a`, its colour-0 neighbourhood is a 3-coloured `K_15` — the root plus three supports of
sizes 5, 5, 4 across the three arms. The proposal was to test whether those three supports can occur
*together* around one vertex of the same template, and to use that as a joint condition.

**They always can, with no constraint beyond the three conditions separately.** The judge counted
completions of the 65 cross edges from `T.col`/`U.col` directly, with an independent encoder:

```
all 30 roots (15 in T.col, 15 in U.col):  exactly 600 completions
```

so the joint condition is *equivalent* to the three support conditions and **its pruning power is
exactly zero**. Any progress from gluing must come from shared cross edges, not from per-sender
compatibility.

Two further checks, both agreeing with the member:

- **the local law**, on cross edges only, at all 30 roots: the third present colour is a matching
  saturating the smaller side, and each of the two class colours spans both parts as a single path
  (sizes 4,5 — eight edges) or cycle (sizes 5,5 — ten edges). 90 pairs, 0 violations. This
  reproduces the campaign's matching law from the template data.
- **the 4-support is forced to be P4+P4**: of the 18 two-colourings of `K_4` with no monochromatic
  triangle (9 up to colour swap), exactly 3 are `C4`-plus-matching, so excluding those leaves only
  `P4+P4` — the campaign's standing statement, reached from the other direction.

The judge's own errors, recorded because they cost half an hour: a first encoder allowed four colours
on the cross edges when the templates are three-coloured (35 edges of each), which made the
enumeration run away; a second had a directed-edge lookup bug. With both fixed the count is
immediate.


## 5. The other three directions, all negative, all verified

**The nine-position matching test is vacuous** (m3). Across all 381 rows and both pentagon arms — 762
cases — there are **zero** pinned pairs among the nine arm vertices outside the pentagon, and all
nine always have identical pin-signatures (762 distinct signatures over 762 cases). Permuting them is
therefore an automorphism of the pinned constraints; the matching problem degenerates to `K_9,9` with
`9!` solutions for every embedding and the triangle conditions cannot bite. This was checked by the
judge directly, and it saves building the machinery at all.

**The core cannot supply the floor** (m6, m7). The 26-vertex board `r ∪ A ∪ C* ∪ D*` with the frozen
pins admits `U,V ∈ [5,25]`, `U+V ∈ [14,50]` — and with the uniform-child columns `U+V ∈ [15,49]` —
and it attains `U+V = 21` at `(9,12)` and `(10,11)`. So no argument confined to the pentagons, even
with uniformity, proves `U+V ≥ 21`; the 35-vertex certificates are not redundant. A useful sound
lemma from the same work: an outside vertex has at most two colour-f and two colour-g neighbours in a
two-coloured pentagon `P`, since three would close a monochromatic triangle.

**The deficient-sender gluing excludes nothing as posed** (m4, "Theorem V"). The placement conditions
live entirely inside one arm and never mention row labels, so the deficiency set `L ⊆ A` is a union of
orbits of the full symmetric group on `A` — empty or all of `A`. Hence compatible triples number
exactly `295³` of `332³`, every failure being a dead type. What survives is a **new joint condition
with real bite**: for every outside vertex `x`, at least `10 - g(x)` other-arm vertices must meet
`Z(x)`; random layers violate it 200 of 200 with median worst margin `-6`, yet it is satisfiable on a
verified witness, so it prunes without emptying.

**Two further negative facts** (m1): `m(x) = 5` is not template-forced — every `m` from 0 to 15
admits words — and since the average of `m` over the 42 outsiders is exactly 5, **every some-six
vertex carries a some-four companion**. Also confirmed independently: the `m = 5` word count is
exactly 254,628, pinning the encoder to the bundle's figure.

## 6. The census depends on the role, not the class (m8, verified here)

The cleanest statement of why the 115 alone is the wrong unit. Roles 24 and 155:

| | value |
| --- | --- |
| same `S_3` class | **yes** (checked by exact isomorphism) |
| independent-set pools in the special colour | **identical** — 10 five-sets, 67 four-sets |
| placements | **24 has 0, 155 has 42** |

So no local invariant decides: the degree sequences, pool sizes and edge counts all agree, and the two
roles differ only in whether a cover exists. The LP relaxation certifies 9 of the 37 deaths, which is
the same linear-blindness found elsewhere in this campaign.

Lift to the classes: 37 dead roles = **12 all-dead-class rows + 25 mixed**. And the operational
consequence, agreeing with Theorem V from the other side: every role is realisable in every arm slot,
so the admissible triples are the full product except for the five all-dead classes.

**Arithmetic reconciliation**: 651 labelled types = 102 orbits of size 6 + 13 of size 3; the 332 roles
are the same object after quotienting the non-special colour swap = 102 of size 3 + 13 of size 2. Both
`102*6 + 13*3 = 651` and `102*3 + 13*2 = 332`.
