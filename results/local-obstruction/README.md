# The local level: the Hall inequality is inert, and three words already kill an arm

Member m7 of swarm `smwrmwgf7`, accepted 2026-11-22. Two results, both re-run by
the coordinator (`sh rerun.sh`, 37 s, `set -e`, ends "DONE: all certificates
verified") before acceptance.

## 1. The Hall inequality is a theorem, and it carries nothing

For colour-0 independent `I` (`|I| = 15`), `J`, and `S ⊆ J \ I`:

    |N_0(S) ∩ I| >= |S| - 1.

`(I \ N_0(S)) ∪ S` is colour-0 independent (`S ⊆ J` is, `I` is, and nothing of
`S` touches a survivor of `I`), so its size is at most `alpha(G_0) <= 16`, because
17 points with no colour-0 edge would be a triangle-free 3-colouring of `K_17`.
Conversely `alpha_0 >= 17` gives a violation. So **Hall <=> alpha(G_0) <= 16**, and
the exhaustive maximum of the margin `|S| - 1 - |N_0(S) ∩ I|` has the closed form
`min(alpha_0, 30) - 16`, attained.

Consequence: **it is inert.** It is implied by the X-internal triangle family that
the pair level deliberately omits, so it cannot sharpen any sound relaxation. The
pentagon package's transferable consequence adds nothing to this campaign.

The five order-58 pair-level witnesses have `alpha(G_0) = 34, 41, 36, 30, 30` — each
re-decided here by SAT at `alpha` (SAT) and `alpha + 1` (UNSAT) — so all five
violate Hall at margin 14. With `I = A` alone the exact maximum is 2.

**Record correction.** `WALL` §27 reported "no violation occurs ... so the
inequality does not eliminate that witness". That test checked `|S| <= 4` and the
full set only. Since every word has exactly five 0s, `|N_0(S) ∩ A| >= 5 > |S| - 1`
for `|S| <= 4`, and the full set usually covers `A`: the tested range could not
contain the violation, which lives at `5 <= |S| <= 14`. Corrected in `WALL` §27.

## 2. The three-word obstruction

With `M_f(x) = {a in A : word of x has colour f}` and `k` the arm's root colour,
put `L(x,y) = {f != k : M_f(x) ∩ M_f(y) = empty}`. Then `k ∉ L` (same root class)
and `f ∉ L` when the intersection is nonempty (`K58.model_pair_disjoint`). So a
triple of words with `L = L = L = {c}` forces the three internal edges to `c`: a
monochromatic triangle, and the arm is unrealisable.

Exhaustive over all `C(14,3) = 364` triples per arm: **661 inclusion-minimal
infeasible triples over the 15 arms of the five order-58 pair-level witnesses, 0
dead pairs, 15 certificates** re-derived from the `.wit` files by an independent
script. Cross-checked by an exact arm-module CSP that reproduces
`min infeasible sub-arm = 3` with identical counts, and validated in the dangerous
direction: the 13 arms whose own colouring is legal come back SAT, 0 mismatches.

Not complete: the minimal local obstruction has spectrum `{3, 5, 6}` in these
objects — `design_1` arm 1 needs 6 (`R(3,3) = 6` again) and `L_50` arm 3 needs 5.

**What this is and is not.** It is a proof, not a DRAT: a three-variable module
needs no solver to refute, and the lemma is stronger than any single instance. It
closes the local question. It closes nothing above it.
