# The Lean side of the K58 bridge

A kernel-checked formalisation of the part of the `R(3,3,3,3) ≤ 58` reduction
that does not depend on the case enumeration.  Lean 4.33.1 + Mathlib.

```sh
./build.sh          # compiles K58/*.lean in order, then prints the axioms
```

Every theorem below depends only on `[propext, Classical.choice, Quot.sound]`.
There is no `sorry`, no `native_decide`, and no new axiom anywhere in the tree.

## What is proved

| file | theorem | statement |
| --- | --- | --- |
| `K58/Basic.lean` | `sum_w_eq_sum_H` | total tickets sent equals total tickets received |
| | `exists_root` | some vertex receives at least as many tickets as it sends |
| `K58/TwoColour.lean` | `two_colour_six` | `R(3,3) ≤ 6` |
| | `deg_le_two_of_two_colour` | a triangle-free 2-colouring has colour degrees ≤ 2 |
| `K58/ThreeColour.lean` | `three_colour_seventeen` | `R(3,3,3) ≤ 17` |
| `K58/DegreeCap.lean` | `deg_le_sixteen` | in a triangle-free 4-colouring every colour degree is ≤ 16 |
| `K58/Reduction.lean` | `w_eq_sum_critical` | tickets sent = sum of the critical colour degrees |
| | `H_eq_sum_armSenders` | tickets received = sum over the four arms of their senders |
| | `threshold_pigeonhole` | `Σ (t a - 1) < W` implies some arm misses its threshold constraint |
| `K58/Main.lean` | `profile_sum` | at any vertex of a triangle-free 4-colouring of `K_58`: `Σ deg = 57`, each `deg ≤ 16` |
| | `exists_arm_reaches` | for any threshold plan obeying `Σ (t a - 1) < Σ critical degrees` at every profile, some arm of some root reaches its threshold |

`exists_arm_reaches` is the mathematical core of the cover: it is exactly the
step "a root with `H ≥ w` forces an arm to reach the threshold the plan chose
for it".  It does not use triangle-freeness — only the double counting — which
is why it is stated for an arbitrary colouring.

## What is not here

1. **The marking lemma.**  A sender in an arm that has reached its threshold
   must realise the units of one of the emitted cases.  This is where the U/T
   classification (every 15/16 critical neighbourhood is `U` or `T`), the
   palette quotient and the support embeddings live.  In the bundle this is
   `gluing.orbit_data` + `palette_quotient` + `support_tables`; the audit
   checked them, but nothing here formalises them.
2. **The eleven profiles and the 41 threshold plans.**  `profile_sum` gives the
   two numerical facts (`Σ deg = 57`, `deg ≤ 16`) from which the eleven
   partitions follow; the enumeration itself and the per-plan inequality
   `Σ (t a - 1) < W` are finite checks not yet written in Lean.
3. **The computation.**  All 113,179 case formulas unsatisfiable.  In the K60
   architecture this is one explicit premise (`ExactInputs.AllUnsat`); here it
   would be the analogous premise over the frozen K58 case list.

With (1)–(3) the argument closes: `exists_arm_reaches` produces a realised
case and (3) says no case is realised.  The formal bridge is therefore three
obligations away from the theorem, and (1) is much the largest.
