# Does the four-set idea help find a counterexample at 52 or 53?

**No, and for two independent reasons.** One is logical, one is structural.

## 1. A `K_52` contains a `K_51`, so 52 and 53 are strictly harder targets

Deleting any vertex of a triangle-free 4-colouring of `K_52` gives one of `K_51`. So

> `K_52` exists ⟹ `K_51` exists, and the same for `K_53` ⟹ `K_51` by two deletions.

Finding a colouring at 52 or 53 therefore subsumes finding one at 51, which is the open case and the
one the community conjectures does **not** exist. If the conjecture is right, there is no `K_52`; if
it is wrong, the first counterexample is at 51 and would be found there first. Targeting 52 or 53 is
dominated.

The campaign's own evidence agrees: the eight known `K_50` colourings **do not extend to `K_51`**
(encoder verified, UNSAT), and Anabanti ruled out group-partition/Cayley constructions for `n ≥ 51`.

## 2. The structure the four-set idea exploits does not exist below 57

A colour is *critical* at a vertex when its degree is at least 15. Colour-degrees are at most 16
(`R(3,3,3) = 17`), so at `K_n` a vertex has degree `n-1` and

| n | degree | 4 × 14 | some colour forced critical? |
| ---: | ---: | ---: | :--- |
| 51–57 | 50–56 | 56 | **no** |
| **58** | 57 | 56 | **YES** |
| 59–62 | 58–61 | 56 | YES |

At `n ≥ 58` every vertex must have a critical colour, because `n-1 > 4·14`. **That forcing is what the
whole campaign rests on**: it is what makes a 15-arm exist, what makes each point of it a *sender*
whose colour-0 neighbourhood is a classified `K_15` template, and therefore what produces supports of
sizes 4 and 5, the cover census, the five 4-supports, and the four-set idea itself.

At 52 or 53 there is no forcing at all: a vertex can have all four colour-degrees at most 14. So
tickets, senders, supports, covers and the four-set structure have no definition there. The `K_57`
14-regular case is the tight boundary — all four degrees may equal 14 exactly.

## 3. What does transfer, and it is only pruning

Almost every arm profile at 52 or 53 contains a 14-arm:

| n | arm profiles (parts in [1,16], sum n−1) | with a 14-arm or larger |
| ---: | ---: | ---: |
| 52 | 39 | **38** |
| 53 | 34 | **33** |

So the campaign's `K_14` lemmas apply to at least one arm — two vertices share at most four
neighbours of any colour; the nine third-colour signatures are nonempty and distinct; the matching law;
the `8/8/4` and `10/10/5` component table. Those are entailed by triangle-freeness alone, so they are
**sound clauses to add to a search** at 52 or 53.

But they are pruning constraints, and pruning helps *refute*. For a construction they are the wrong
tool: the reason `K_58` is hard is that it is tightly constrained, and at 52 the constraint that
generates all the structure has switched off.

## Bottom line

The four-set idea is a refutation instrument for `n ≥ 57`. For a counterexample the target is **51**,
where it does not apply either, and the honest expectation — shared by the literature — is that no
such colouring exists.
