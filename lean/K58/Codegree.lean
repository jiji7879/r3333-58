/-
# The counting step behind "a packing of seven gives one pair of codegree nine"

This file kernel-checks the arithmetic step of the repeated-pentagon codegree
argument (`K58_repeated_pentagon_codegree`), isolated from all geometry.

Setting.  `X` is the vertex set of the ambient colouring.  `N₁ N₂ N₃` are the
three colour-0 neighbourhoods `N₀(o₁)`, `N₀(o₂)`, `N₀(o₃)` of three vertices,
and `S` is the six-point set `{r} ∪ F` they share.  `K` indexes the triples of a
packing: `u k`, `v k`, `w k` are one slot in each chart, so `u k ∈ N₁ \ S`,
`v k ∈ N₂ \ S`, `w k ∈ N₃ \ S`, and a packing uses distinct slots inside each
chart, so `u`, `v`, `w` are injective on `K`.

Two hypotheses are geometric and are *assumed*, not proved, here:

* `htri : ∀ k ∈ K, u k = v k ∨ u k = w k ∨ v k = w k`.  A triple of slots one
  from each chart whose three pairs are all conflicting cannot consist of three
  distinct vertices: each conflicting pair is joined in colour 0, so three
  distinct vertices would be a monochromatic colour-0 triangle, which the
  colouring does not have.  Hence two of the three slots are the same vertex.
* nothing else.  In particular no bound on any codegree is assumed.

Conclusion: the three pair codegrees sum to at least `#K + 3 * 6`.  With `#K = 7`
that is 25, and `3 * 8 = 24 < 25`, so some pair has codegree at least nine.

The proof is the pigeonhole argument: each slot triple of the packing charges one
common zero-neighbour to one of the three owner pairs, and *distinct* triples
charge *distinct* vertices to the same pair, because `u` (say) is injective on
`K` and the slots of one chart are distinct vertices.
-/
import Mathlib

open Finset

namespace K58

variable {X ι : Type*} [DecidableEq X] [DecidableEq ι]

omit [DecidableEq ι] in
/-- One chart's worth of the charging map: the triples whose two slots in the
first chart coincide inject into the common zero-neighbours of that pair. -/
lemma card_filter_le_codegree (N M S : Finset X) (K : Finset ι) (u v : ι → X)
    (hu : ∀ k ∈ K, u k ∈ N \ S) (hv : ∀ k ∈ K, v k ∈ M \ S)
    (hinj : ∀ k₁ ∈ K, ∀ k₂ ∈ K, u k₁ = u k₂ → k₁ = k₂) :
    (K.filter fun k => u k = v k).card ≤ ((N ∩ M) \ S).card := by
  refine card_le_card_of_injOn u ?_ ?_
  · intro k hk
    obtain ⟨hkK, hkeq⟩ := mem_filter.mp hk
    obtain ⟨hN, hS⟩ := mem_sdiff.mp (hu k hkK)
    obtain ⟨hM, -⟩ := mem_sdiff.mp (hv k hkK)
    rw [← hkeq] at hM
    exact mem_sdiff.mpr ⟨mem_inter.mpr ⟨hN, hM⟩, hS⟩
  · intro k₁ hk₁ k₂ hk₂ heq
    exact hinj k₁ (mem_filter.mp hk₁).1 k₂ (mem_filter.mp hk₂).1 heq

/-- The counting step.  Each packed triple charges a common zero-neighbour to one
of the three owner pairs, injectively per pair, so the triple count plus the
`3 * 6` shared points is a lower bound for the sum of the three codegrees. -/
theorem codegree_count (N₁ N₂ N₃ S : Finset X) (K : Finset ι) (u v w : ι → X)
    (hS : S.card = 6) (hS₁ : S ⊆ N₁) (hS₂ : S ⊆ N₂) (hS₃ : S ⊆ N₃)
    (hu : ∀ k ∈ K, u k ∈ N₁ \ S) (hv : ∀ k ∈ K, v k ∈ N₂ \ S)
    (hw : ∀ k ∈ K, w k ∈ N₃ \ S)
    (hu' : ∀ k₁ ∈ K, ∀ k₂ ∈ K, u k₁ = u k₂ → k₁ = k₂)
    (hv' : ∀ k₁ ∈ K, ∀ k₂ ∈ K, v k₁ = v k₂ → k₁ = k₂)
    (htri : ∀ k ∈ K, u k = v k ∨ u k = w k ∨ v k = w k) :
    K.card + 18 ≤ (N₁ ∩ N₂).card + (N₁ ∩ N₃).card + (N₂ ∩ N₃).card := by
  have hA₁₂ : (K.filter fun k => u k = v k).card ≤ ((N₁ ∩ N₂) \ S).card :=
    card_filter_le_codegree N₁ N₂ S K u v hu hv hu'
  have hA₁₃ : (K.filter fun k => u k = w k).card ≤ ((N₁ ∩ N₃) \ S).card :=
    card_filter_le_codegree N₁ N₃ S K u w hu hw hu'
  have hA₂₃ : (K.filter fun k => v k = w k).card ≤ ((N₂ ∩ N₃) \ S).card :=
    card_filter_le_codegree N₂ N₃ S K v w hv hw hv'
  have hcover : K ⊆ (K.filter fun k => u k = v k)
      ∪ (K.filter fun k => u k = w k) ∪ (K.filter fun k => v k = w k) := by
    intro k hk
    rcases htri k hk with h | h | h
    · exact mem_union_left _ (mem_union_left _ (mem_filter.mpr ⟨hk, h⟩))
    · exact mem_union_left _ (mem_union_right _ (mem_filter.mpr ⟨hk, h⟩))
    · exact mem_union_right _ (mem_filter.mpr ⟨hk, h⟩)
  have hsplit : K.card ≤ (K.filter fun k => u k = v k).card
      + (K.filter fun k => u k = w k).card + (K.filter fun k => v k = w k).card := by
    calc K.card ≤ ((K.filter fun k => u k = v k)
            ∪ (K.filter fun k => u k = w k)
            ∪ (K.filter fun k => v k = w k)).card := card_le_card hcover
      _ ≤ ((K.filter fun k => u k = v k)
            ∪ (K.filter fun k => u k = w k)).card
            + (K.filter fun k => v k = w k).card := card_union_le _ _
      _ ≤ ((K.filter fun k => u k = v k).card
            + (K.filter fun k => u k = w k).card)
            + (K.filter fun k => v k = w k).card := by
            have := card_union_le (K.filter fun k => u k = v k)
              (K.filter fun k => u k = w k)
            omega
      _ = _ := by omega
  -- the shared points sit in all three pairwise intersections
  have e₁₂ : ((N₁ ∩ N₂) \ S).card = (N₁ ∩ N₂).card - 6 := by
    rw [card_sdiff, inter_eq_left.mpr (subset_inter hS₁ hS₂), hS]
  have e₁₃ : ((N₁ ∩ N₃) \ S).card = (N₁ ∩ N₃).card - 6 := by
    rw [card_sdiff, inter_eq_left.mpr (subset_inter hS₁ hS₃), hS]
  have e₂₃ : ((N₂ ∩ N₃) \ S).card = (N₂ ∩ N₃).card - 6 := by
    rw [card_sdiff, inter_eq_left.mpr (subset_inter hS₂ hS₃), hS]
  have c₁₂ : 6 ≤ (N₁ ∩ N₂).card := by
    have := card_le_card (subset_inter hS₁ hS₂); omega
  have c₁₃ : 6 ≤ (N₁ ∩ N₃).card := by
    have := card_le_card (subset_inter hS₁ hS₃); omega
  have c₂₃ : 6 ≤ (N₂ ∩ N₃).card := by
    have := card_le_card (subset_inter hS₂ hS₃); omega
  omega

/-- Seven packed triples: some owner pair has at least nine common
zero-neighbours. -/
theorem nine_le_codegree (N₁ N₂ N₃ S : Finset X) (K : Finset ι) (u v w : ι → X)
    (hS : S.card = 6) (hS₁ : S ⊆ N₁) (hS₂ : S ⊆ N₂) (hS₃ : S ⊆ N₃)
    (hu : ∀ k ∈ K, u k ∈ N₁ \ S) (hv : ∀ k ∈ K, v k ∈ N₂ \ S)
    (hw : ∀ k ∈ K, w k ∈ N₃ \ S)
    (hu' : ∀ k₁ ∈ K, ∀ k₂ ∈ K, u k₁ = u k₂ → k₁ = k₂)
    (hv' : ∀ k₁ ∈ K, ∀ k₂ ∈ K, v k₁ = v k₂ → k₁ = k₂)
    (htri : ∀ k ∈ K, u k = v k ∨ u k = w k ∨ v k = w k)
    (hK : K.card = 7) :
    9 ≤ (N₁ ∩ N₂).card ∨ 9 ≤ (N₁ ∩ N₃).card ∨ 9 ≤ (N₂ ∩ N₃).card := by
  have h := codegree_count N₁ N₂ N₃ S K u v w hS hS₁ hS₂ hS₃ hu hv hw
    hu' hv' htri
  omega

/-- The arithmetic the argument actually uses: `25 > 3 * 8`. -/
example : ¬ (25 ≤ 3 * 8) := by decide

end K58

#print axioms K58.card_filter_le_codegree
#print axioms K58.codegree_count
#print axioms K58.nine_le_codegree
