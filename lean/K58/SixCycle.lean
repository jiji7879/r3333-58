/-
  Why the site relation is a six-cycle.

  `ArmLayer.no_triangle_weights` shows that three kinds whose sites pairwise share
  a class cannot all carry counts: the three five-owner equations of a triangle
  force `2 (w0 + w1 + w2) = 15`.  The sharing graph of the six kinds is
  two-regular (each kind has two classes, and each of them is shared with exactly
  one other kind).  Here: a triangle-free two-regular graph on six vertices is
  connected.  Putting the two together: whenever a placement's site relation
  carries an integral count vector, that relation is a six-cycle — the
  package's catalogue observation "all six-cycles" is then a consequence of the
  count vector and not an extra input.
-/
import Mathlib

open Finset

namespace K58

/-- **A triangle-free two-regular graph on six vertices is connected.** -/
theorem connected_of_two_regular_of_triangle_free (G : SimpleGraph (Fin 6))
    [DecidableRel G.Adj]
    (hdeg : ∀ v, G.degree v = 2)
    (htri : ∀ a b c : Fin 6, ¬ (G.Adj a b ∧ G.Adj b c ∧ G.Adj c a)) :
    ∀ u v : Fin 6, G.Reachable u v := by
  classical
  -- the component of `0`
  set S : Finset (Fin 6) := univ.filter (fun v => G.Reachable 0 v) with hSdef
  have hS : ∀ v, v ∈ S ↔ G.Reachable 0 v := by
    intro v; simp [hSdef]
  have h0 : (0 : Fin 6) ∈ S := (hS 0).mpr (SimpleGraph.Reachable.refl 0)
  -- `S` is closed under neighbours
  have hcl : ∀ v ∈ S, ∀ w : Fin 6, G.Adj v w → w ∈ S := by
    intro v hv w hvw
    exact (hS w).mpr (((hS v).mp hv).trans hvw.reachable)
  -- every vertex of `S` has both its neighbours in `S`
  have hdegS : ∀ v ∈ S, (S.filter (fun w => G.Adj v w)).card = 2 := by
    intro v hv
    have hEq : S.filter (fun w => G.Adj v w) = G.neighborFinset v := by
      ext w
      simp only [mem_filter, SimpleGraph.mem_neighborFinset]
      exact ⟨fun h => h.2, fun h => ⟨hcl v hv w h, h⟩⟩
    rw [hEq, SimpleGraph.card_neighborFinset_eq_degree, hdeg v]
  -- a vertex outside `S` has both its neighbours outside `S`
  have hout : ∀ v ∉ S, G.neighborFinset v ⊆ univ \ S := by
    intro v hv w hw
    simp only [SimpleGraph.mem_neighborFinset] at hw
    simp only [mem_sdiff, mem_univ, true_and]
    intro hwS
    exact hv ((hS v).mpr (((hS w).mp hwS).trans hw.symm.reachable))
  -- `3 ≤ |S|`
  have hSge : 3 ≤ S.card := by
    have hnb : (G.neighborFinset (0 : Fin 6)).card = 2 := by
      rw [SimpleGraph.card_neighborFinset_eq_degree, hdeg 0]
    have hsub : G.neighborFinset (0 : Fin 6) ⊆ S.erase 0 := by
      intro w hw
      rw [SimpleGraph.mem_neighborFinset] at hw
      exact mem_erase.mpr ⟨fun h => G.irrefl (h ▸ hw), hcl 0 h0 w hw⟩
    have hc : (G.neighborFinset (0 : Fin 6)).card ≤ (S.erase 0).card := card_le_card hsub
    have h2 : (S.erase 0).card = S.card - 1 := card_erase_of_mem h0
    omega
  -- either `S` is everything, or the complement has at least three vertices
  by_cases hall : S = univ
  · -- connected
    intro u v
    have hu : u ∈ S := by rw [hall]; exact mem_univ u
    have hv : v ∈ S := by rw [hall]; exact mem_univ v
    exact ((hS u).mp hu).symm.trans ((hS v).mp hv)
  · -- some vertex outside `S`; its two neighbours are outside `S`
    obtain ⟨v, hv⟩ : ∃ v, v ∉ S := by
      by_contra h
      exact hall (eq_univ_of_forall (by simpa using h))
    have hnb : (G.neighborFinset v).card = 2 := by
      rw [SimpleGraph.card_neighborFinset_eq_degree, hdeg v]
    -- the complement holds `v` and its two neighbours, so it has at least three
    have hvins : v ∈ univ \ S := by simp [hv]
    have hsub2 : insert v (G.neighborFinset v) ⊆ univ \ S := by
      intro w hw
      rcases mem_insert.mp hw with rfl | hw'
      · exact hvins
      · exact hout v hv hw'
    have hcard3 : (insert v (G.neighborFinset v)).card = 3 := by
      rw [card_insert_of_notMem (by simp [SimpleGraph.mem_neighborFinset]), hnb]
    have hcomp3 : 3 ≤ (univ \ S).card := by
      rw [← hcard3]; exact card_le_card hsub2
    have hcomp : (univ \ S).card = 6 - S.card := by
      rw [card_sdiff, card_univ, Fintype.card_fin, Finset.inter_univ]
    have hSle : S.card ≤ 6 := by
      simpa using card_le_card (subset_univ S)
    -- so `|S| = 3`, and three vertices each with two neighbours inside `S`
    -- adjacent to one another make a triangle
    have h3 : S.card = 3 := by omega
    -- inside `S` every vertex is adjacent to every other one
    have hadj : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → G.Adj x y := by
      intro x hx y hy hxy
      have hsub : S.filter (fun w => G.Adj x w) ⊆ S.erase x := by
        intro w hw
        rw [mem_filter] at hw
        exact mem_erase.mpr ⟨fun h => G.irrefl (h ▸ hw.2), hw.1⟩
      have hcard : (S.erase x).card = 2 := by
        rw [card_erase_of_mem hx, h3]
      have heq : S.filter (fun w => G.Adj x w) = S.erase x := by
        refine eq_of_subset_of_card_le hsub ?_
        rw [hcard, hdegS x hx]
      have hy' : y ∈ S.erase x := mem_erase.mpr ⟨Ne.symm hxy, hy⟩
      rw [← heq] at hy'
      exact (mem_filter.mp hy').2
    -- three vertices, so a triangle
    have hcard2 : (S.erase 0).card = 2 := by rw [card_erase_of_mem h0, h3]
    obtain ⟨a, b, hab, hSe⟩ := Finset.card_eq_two.mp hcard2
    have ha : a ∈ S := by
      have : a ∈ S.erase 0 := by rw [hSe]; exact mem_insert_self a {b}
      exact mem_of_mem_erase this
    have hb : b ∈ S := by
      have : b ∈ S.erase 0 := by rw [hSe]; exact mem_insert_of_mem (mem_singleton_self b)
      exact mem_of_mem_erase this
    have ha0 : a ≠ 0 := by
      rintro rfl
      exact Finset.notMem_erase 0 S (by rw [hSe]; exact mem_insert_self 0 {b})
    have hb0 : b ≠ 0 := by
      rintro rfl
      exact Finset.notMem_erase 0 S (by rw [hSe]; exact mem_insert_of_mem (mem_singleton_self 0))
    exact absurd ⟨hadj 0 h0 a ha ha0.symm, hadj a ha b hb hab, hadj b hb 0 h0 hb0⟩
      (htri 0 a b)

/-- **A site relation that carries a count vector is a six-cycle.**  The sharing
graph of the six kinds is two-regular (each kind has two classes and each class
is shared with exactly one other kind), and an integral count vector `w` with
`w a + w b = 5` on every shared class rules out a triangle: the three five-owner
equations of a triangle force `2 (wa + wb + wc) = 15`.  By the theorem above the
sharing graph is then connected, and a connected two-regular graph on six
vertices is a six-cycle.  So the package's catalogue observation that every one
of the 4,236 admissible placements puts the six classes on a cycle is a
consequence of the count vector, not an extra input. -/
theorem connected_of_weights (G : SimpleGraph (Fin 6)) [DecidableRel G.Adj]
    (hdeg : ∀ v, G.degree v = 2) (w : Fin 6 → ℤ)
    (hedge : ∀ a b : Fin 6, G.Adj a b → w a + w b = 5) :
    ∀ u v : Fin 6, G.Reachable u v := by
  refine connected_of_two_regular_of_triangle_free G hdeg ?_
  intro a b c h
  obtain ⟨hab, hbc, hca⟩ := h
  have h1 := hedge a b hab
  have h2 := hedge b c hbc
  have h3 := hedge c a hca
  omega

#print axioms K58.connected_of_two_regular_of_triangle_free
#print axioms K58.connected_of_weights

end K58
