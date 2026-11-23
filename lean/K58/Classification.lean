import K58.Templates
import R4333Lean.CriticalCatalogues

namespace K58

private def asCatalogueColouring {n : ℕ} (G : EdgeCol (Fin n) 3) :
    R4333.EdgeColoring (Fin n) R4333.ThreeColor :=
  ⟨G.col, G.symm⟩

private theorem catalogueTriangleFree {n : ℕ} {G : EdgeCol (Fin n) 3}
    (h : TriangleFree G) : R4333.NoMonochromaticTriangle (asCatalogueColouring G) :=
  fun x y z hxyz => h x y z hxyz.1 hxyz.2.2 hxyz.2.1

private theorem classifiedOfCatalogue {n : ℕ}
    (cat : List (R4333.EdgeColoring (Fin n) R4333.ThreeColor))
    (hc : R4333.ThreeColorCatalogueComplete n cat)
    (hmatch : ∀ C ∈ cat, ∃ t : Bool, ∀ x y, C x y = (template n t).col x y) :
    Classified n := by
  intro G hG
  obtain ⟨C, hC, ⟨e⟩⟩ := hc.2 (asCatalogueColouring G) (catalogueTriangleFree hG)
  obtain ⟨t, ht⟩ := hmatch C hC
  refine ⟨t, e.vertex, e.colors.symm, ?_⟩
  intro x y hxy
  apply e.colors.injective
  rw [Equiv.apply_symm_apply]
  exact (e.map_color x y hxy).trans (ht _ _)

theorem classified_15 : Classified 15 := by
  apply classifiedOfCatalogue _ R4333.k15CriticalCatalogue_complete
  intro C hC
  simp only [R4333.k15CriticalCatalogue, List.mem_cons, List.not_mem_nil,
    or_false] at hC
  rcases hC with rfl | rfl
  · exact ⟨false, by decide⟩
  · exact ⟨true, by decide⟩

theorem classified_16 : Classified 16 := by
  apply classifiedOfCatalogue _ R4333.k16CriticalCatalogue_complete
  intro C hC
  simp only [R4333.k16CriticalCatalogue, List.mem_cons, List.not_mem_nil,
    or_false] at hC
  rcases hC with rfl | rfl
  · exact ⟨false, by decide⟩
  · exact ⟨true, by decide⟩

end K58
