# Anchor-class capacity table 16/5/2/1, kernel-checked (member m8, direction d9)

## Theorem (Lean 4.33.1, `lean/lean/Capacity.lean`, namespace `K54Cap`)

`anchor_capacity` — Let `G` be a triangle-free 4-colouring of a complete graph on a finite
vertex type `V`. Let `m ≥ 1`, let `p : Fin m → V` be injective (distinct anchor vertices),
`hs : Fin m → Fin 4` injective (distinct anchor colours), and `W` a set of vertices with
`p i ∉ W` for all `i` and `G.col (p i) w = hs i` for all `w ∈ W`, `i`.
Then `W.card ≤ cap m`, where `cap 1 = 16`, `cap 2 = 5`, `cap 3 = 2`, `cap 4 = 1`.

`card_le_cap` — the general form: if all pairwise edge colours on `S` avoid a nonempty
colour set `C`, then `S.card ≤ cap |C|`.

Proof: a pair `x,y ∈ W` has `G.col x y ≠ hs i` for every `i` (else `p i, x, y` is a
monochromatic triangle), so `W` is a triangle-free colouring with the `4-m` colours outside
`C`; apply `two_colour_six` / `three_colour_seveneen`-style bounds from the repository's
`K58` development, which are themselves kernel-checked.

## Why this matters

The count decomposition for `R(3,3,3,3) ≤ 54` uses exactly these four numbers as the
per-anchor-class capacities ("the familiar one-, two- and three-spoke upper bounds are 16,
5 and 2, using the three-color triangle Ramsey number 17, the two-color number 6 and the
one-color number 3"). In the archive that table rests on three separate SAT runs plus prose.
Here it is one board-independent theorem, kernel-checked, axioms `[propext, Classical.choice,
Quot.sound]`, no `sorry`, no `native_decide`.

## Definitive negative result on symmetry (direction d2, abandoned)

Measured, SAT permutation search over all vertex permutations:
* colour-preserving `Aut(H42)` has order **4** (a Klein four-group), not 2; the hue-relabelling
  automorphism group has order 8 = 4 × 2.
* for **all 14 open boards**, the group `{(π₀,π₁) ∈ Aut(H42)² : π preserves the 14×14 pin mask}`
  is the **identity**, and the side-swap coset is **empty**.
* per-side palette relabelling is **not** a symmetry of realizability: it recolours one side's
  fixed edges only, while crossing and outsider edges keep their colours, so a triangle with
  one side edge and two crossing edges is not mapped to a colour-relabelled triangle.
Consequence: the ≥90,775-vector census of local-15 admits **no** symmetry quotient. Anything
that shrinks it must be a constraint, as m5/m3 are doing.
