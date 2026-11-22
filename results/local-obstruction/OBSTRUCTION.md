# The three-word gluing obstruction

## Lemma

Let `r` be a vertex of a triangle-free 4-colouring of `K_58` in which every outside
vertex is uniform (`m(x) = 5`), so each outside vertex `x` carries a word
`w_x : A → {0,1,2,3}` with exactly five 0s, `M_f(x) = {a ∈ A : w_x(a) = f}`. Let
`k` be the root colour of an arm, so every vertex of that arm lies in `N_k(r)`.
For `x, y` in that arm put

    L(x,y) = { f ≠ k : M_f(x) ∩ M_f(y) = ∅ }.

* `k ∉ L(x,y)`: `x, y ∈ N_k(r)`, so a `k`-edge `xy` would make the `k`-triangle `rxy`.
* `f ∉ L(x,y)` when `M_f(x) ∩ M_f(y) ≠ ∅`: the common point `a` is `f`-adjacent to
  both, and `{a,x,y}` is an `f`-triangle. (This is the kernel-checked
  `K58.model_pair_disjoint`.)

**If three words `x, y, z` of one arm satisfy `L(x,y) = L(x,z) = L(y,z) = {c}`, the
arm has no admissible colouring**: every internal edge of that triangle is forced to
`c`, so the arm carries a monochromatic triangle. The triple is an
inclusion-minimal infeasible sub-arm (its three pairs are each feasible), and no
triangle-free 4-colouring of `K_58` restricts to this arm.

The argument is template-free; the template enters only through word admissibility.

## Certificates

`out/three_word_certificates.json` — fifteen certificates, one per arm of the five
distinct order-58 pair-level witnesses. Each names three vertices of one arm, its
root colour, its three words, and the singleton colour. `scripts/verify_obstruction.py`
re-derives everything from the witness file and reports:

| witness | arm 1 | arm 2 | arm 3 | triples |
| --- | --- | --- | --- | ---: |
| `pair58_Tminus` | `[0,1,8] → 2` | `[14,17,19] → 3` | `[28,29,39] → 1` | 119 |
| `pair58_Tminus_recoloured` | `[0,1,3] → 2` | `[14,15,17] → 3` | `[28,29,36] → 1` | 160 |
| `wit_big` | `[0,1,3] → 3` | `[14,15,22] → 1` | `[28,29,33] → 1` | 131 |
| `p58` | `[0,5,6] → 3` | `[14,16,18] → 1` | `[28,29,41] → 1` | 149 |
| `p58_cc` | `[0,2,12] → 3` | `[14,16,18] → 1` | `[28,31,34] → 1` | 102 |

`661` mono-forced triples over the fifteen arms, `0` dead pairs, so size 3 is the
smallest refutation present in these objects. Exhaustive over all `C(14,3) = 364`
triples per arm. `L_58.wit` is byte-identical to `pair58_Tminus.wit`.

The counts are unchanged (only larger) under the alternative reading in which
colour 0 is banned inside an arm as well: 42–69 triples per arm in that reading,
plus 0–4 dead pairs.

## Cross-check by an exact CSP, and what is *not* size 3

`scripts/arm_sat.py` decides the arm module directly: variables per
`(pair, colour)`, one colour per pair from `L`, and a clause per triple and colour.
It reproduces, for all fifteen arms, **minimal infeasible sub-arm = 3 with exactly
the same counts**. It is validated in the dangerous direction by
`scripts/arm_validate.py`: for the eleven arms whose own pair colours already form a
legal arm colouring, the CSP returns SAT — 11 of 11, no mismatches.

The test does not over-fire: the ten arms of the five two-arm witnesses
(`a_14_12`, `a_14_13`, `a_14_14`, and the two `_cap` variants) have `0` triples and
the CSP is SAT, so `14+14` SAT is untouched.

It is **not complete**. The ten `smwr8io45/m4/design_*.wit` arms 1 are infeasible
with no infeasible subset of size ≤ 5; `design_1` arm 1 has minimum size **6** with
exactly 14 such 6-sets, and `L_50` arm 3 has minimum size **5**. So the spectrum of
minimal local obstructions in these objects is {3, 5, 6}: size 3 is the smallest
that occurs, not the only one. (That 6 appears is the `R(3,3) = 6` boundary again.)

The minimum-size search (run from this directory; ~90 s for the `design_1` line):

```sh
../../../.scratch/k58/.venv/bin/python -c '
import sys, itertools; sys.path.insert(0,"scripts")
from wit import Wit
from arm_sat import feasible
R = "../../../"
for path, k in [(".ultramath/smwr8io45/m4/design_1.wit", 1),
                (".ultramath/smwr8io45/m6/wit/L_50.wit", 3)]:
    w = Wit(R + path); vs = sorted(w.arms[k])
    for sz in range(2, len(vs) + 1):
        n = sum(1 for s in itertools.combinations(vs, sz) if not feasible(w, list(s), k))
        print(path, "arm", k, "size", sz, "infeasible subsets", n)
        if n: break
'
```

## What this settles

The wall's §15/§29 question — "which constraints kill the extension: a column sum, a
cross-arm pair condition, or a blocked set?" — has the answer: none of the three.
The counting layer is SAT with the pins (round-five `m7`), the pair level is SAT with
the pins (`abs2_nomod.cnf`), and the failure is the second arm's own list-colouring.
Its smallest witness is three words and one singleton pair colour, and it is now a
standalone checkable certificate for every 58-vertex pair-level witness the campaign
has.
