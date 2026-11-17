# The Lean side of the K58 bridge

The kernel-checked part of the `R(3,3,3,3) ≤ 58` reduction: everything that does
not depend on the case enumeration.  Lean 4.33.1 + Mathlib.

```sh
./build.sh          # compiles K58/*.lean in dependency order, then prints axioms
```

Builds in ~9 s.  Every theorem depends only on subsets of
`[propext, Classical.choice, Quot.sound]`; there is no `sorry`, no
`native_decide` and no new axiom.  `K58/Check.lean` prints all 27.

## The reduction

| file | theorem | statement |
| --- | --- | --- |
| `Basic` | `sum_w_eq_sum_H` | total tickets sent equals total received |
| | `exists_root` | some vertex receives at least as many tickets as it sends |
| `TwoColour` | `two_colour_six` | `R(3,3) ≤ 6` |
| `ThreeColour` | `three_colour_seventeen` | `R(3,3,3) ≤ 17` |
| `DegreeCap` | `deg_le_sixteen` | every colour degree of a triangle-free 4-colouring is ≤ 16 |
| `Reduction` | `w_eq_sum_critical` | tickets sent = Σ critical degrees |
| | `H_eq_sum_armSenders` | tickets received = Σ senders over the four arms |
| | `threshold_pigeonhole` | if every arm is below its threshold, `H` is below `w` |
| `Main` | `profile_sum` | at any vertex of a triangle-free `K_58`: Σ deg = 57, each ≤ 16 |
| `Plans` | `plans_ok`, `plans_feasible` | the 41 frozen plans satisfy the slack inequality and no threshold exceeds its arm |
| `Frontier` | `sorted_degree_profile_mem` | a descending degree vector of sum 57 with max 16 is one of eleven |
| | `root_degree_profile` | after a colour permutation every vertex has one of the eleven profiles |
| | `planned_degree_profiles` | the 41 plans mention exactly those eleven profiles (axiom-free) |
| | `balanced_root_arm_reaches` | a valid plan at a specified balanced root forces an arm to its threshold |
| | `normalized_plan_arm_reaches` | a listed plan matching the root's permuted degrees forces a reached threshold, no larger than the arm degree |

`root_degree_profile` closes the profile enumeration left open in the previous
checkpoint: the relation `Tuple.sort` puts the degrees in descending order and
`interval_cases` sweeps the resulting small box.

## A correction, kept visible

The first version of the threshold step was stated as

```
exists_arm_reaches (G) (t) (ht : ∀ p, Σ (t p a - 1) < Σ critical (p)) : ∃ r a, ...
```

That hypothesis is **unsatisfiable**: at the zero vector `p = 0` the right-hand
side is 0, so no `t` can satisfy it for every `p`.  The theorem was therefore
vacuous.  `Frontier.original_threshold_hypothesis_impossible` proves exactly
this, and `balanced_root_arm_reaches` replaces it with the inequality assumed
only at the root's actual profile (together with `w G r ≤ H G r`).
`exists_arm_reaches` is kept, with its hypothesis, only as the record of the
mistake.

## What is not here

1. **The marking lemma.**  A sender in an arm that reached its threshold must
   realise the units of one of the emitted cases.  This needs the U/T
   classification (every 15/16 critical neighbourhood is `U` or `T`), the root
   pinning, the palette quotient and the support embeddings.  The audit checked
   all of these computationally; none is formalised.
2. **The computation.**  All 113,179 case formulas unsatisfiable, as one
   explicit premise in the shape of `UniformK60.ExactInputs.AllUnsat`.

With (1) and (2) the argument closes.
