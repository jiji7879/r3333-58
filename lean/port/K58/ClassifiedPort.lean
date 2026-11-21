/-
K58: port of the kernel-checked critical-template classification.

`K58.Templates.Classified n` ("every good 3-colouring of `K_n` is, up to a
vertex relabelling and a colour permutation, one of the two templates") is the
one unproved structural premise the `n = 58` cover rests on.  It is proved in
the pinned `n = 60` development (Tatarevic, arXiv:2610.36648v2, source at
`.scratch/k60ref/formal`) as

  `R4333.k16CriticalCatalogue_complete`
  `R4333.k15CriticalCatalogue_complete`

both with axioms `[propext, Classical.choice, Quot.sound]`.  This file derives
`K58.Classified 16` and `K58.Classified 15` from them.  It contains no
`native_decide` and no `sorry`.

Build requirement: `R4333Lean.CriticalCatalogues` (and the pinned Mathlib it was
compiled against) must be on `LEAN_PATH`, and the toolchain must match the
pinned one (`leanprover/lean4:v4.32.1`), because the upstream oleans are used.
-/
import K58.Templates
import R4333Lean.CriticalCatalogues

namespace K58

open R4333

/-- The same edge colouring, seen as an `R4333.EdgeColoring` (`ThreeColor` is
`Fin 3` by definition, so this is a pure change of structure). -/
def toR4333 {n : ℕ} (G : EdgeCol (Fin n) 3) : R4333.EdgeColoring (Fin n) R4333.ThreeColor where
  color := G.col
  color_symm := G.symm

theorem r4333_noMono {n : ℕ} (G : EdgeCol (Fin n) 3) (hG : TriangleFree G) :
    R4333.NoMonochromaticTriangle (toR4333 G) := by
  intro x y z hd htri
  exact hG x y z hd.1 hd.2.2 hd.2.1 ⟨htri.1, htri.2⟩

/-! ### The templates are the repository's templates

Both sides are explicit: the upstream ones are built from the XOR difference
table of `Z_2^4` plus the sixteen-edge trade, and so are `templateCol`'s via
`dc` and `trade`.  The identifications are finite and are checked by the
kernel (`decide`, as in `template_triangleFree_16`). -/

theorem k16Untwisted_eq :
    ∀ i j : Fin 16, R4333.k16Untwisted.color i j = templateCol 16 false i j := by
  decide

theorem k16Twisted_eq :
    ∀ i j : Fin 16, R4333.k16Twisted.color i j = templateCol 16 true i j := by
  decide

theorem k15Untwisted_eq :
    ∀ i j : Fin 15, R4333.k15Untwisted.color i j = templateCol 15 false i j := by
  decide

theorem k15Twisted_eq :
    ∀ i j : Fin 15, R4333.k15Twisted.color i j = templateCol 15 true i j := by
  decide

/-- A catalogue whose entries are the repository's two templates classifies. -/
theorem classified_of_catalogue {n : ℕ}
    (catalogue : List (R4333.EdgeColoring (Fin n) R4333.ThreeColor))
    (hcomplete : R4333.ThreeColorCatalogueComplete n catalogue)
    (hmap : ∀ t ∈ catalogue, (∀ i j : Fin n, t.color i j = templateCol n false i j) ∨
                            (∀ i j : Fin n, t.color i j = templateCol n true i j)) :
    Classified n := by
  intro G hG
  obtain ⟨-, hcomp⟩ := hcomplete
  obtain ⟨t, ht, ⟨e⟩⟩ := hcomp (toR4333 G) (r4333_noMono G hG)
  rcases hmap t ht with h | h
  · refine ⟨false, e.vertex, e.colors.symm, ?_⟩
    intro i j hij
    have h1 : e.colors (G.col i j) = templateCol n false (e.vertex i) (e.vertex j) := by
      have hm := e.map_color i j hij
      simp only [toR4333] at hm
      rw [hm]; exact h _ _
    calc G.col i j = e.colors.symm (e.colors (G.col i j)) := (e.colors.symm_apply_apply _).symm
      _ = e.colors.symm (templateCol n false (e.vertex i) (e.vertex j)) := by rw [h1]
  · refine ⟨true, e.vertex, e.colors.symm, ?_⟩
    intro i j hij
    have h1 : e.colors (G.col i j) = templateCol n true (e.vertex i) (e.vertex j) := by
      have hm := e.map_color i j hij
      simp only [toR4333] at hm
      rw [hm]; exact h _ _
    calc G.col i j = e.colors.symm (e.colors (G.col i j)) := (e.colors.symm_apply_apply _).symm
      _ = e.colors.symm (templateCol n true (e.vertex i) (e.vertex j)) := by rw [h1]

theorem k16_catalogue_map :
    ∀ t ∈ R4333.k16CriticalCatalogue,
      (∀ i j : Fin 16, t.color i j = templateCol 16 false i j) ∨
      (∀ i j : Fin 16, t.color i j = templateCol 16 true i j) := by
  intro t ht
  simp only [R4333.k16CriticalCatalogue, List.mem_cons, List.not_mem_nil,
    or_false] at ht
  rcases ht with rfl | rfl
  · exact Or.inl k16Untwisted_eq
  · exact Or.inr k16Twisted_eq

theorem k15_catalogue_map :
    ∀ t ∈ R4333.k15CriticalCatalogue,
      (∀ i j : Fin 15, t.color i j = templateCol 15 false i j) ∨
      (∀ i j : Fin 15, t.color i j = templateCol 15 true i j) := by
  intro t ht
  simp only [R4333.k15CriticalCatalogue, List.mem_cons, List.not_mem_nil,
    or_false] at ht
  rcases ht with rfl | rfl
  · exact Or.inl k15Untwisted_eq
  · exact Or.inr k15Twisted_eq

/-- **The classification at 16 vertices**, from the pinned development. -/
theorem classified_16 : Classified 16 :=
  classified_of_catalogue R4333.k16CriticalCatalogue
    R4333.k16CriticalCatalogue_complete k16_catalogue_map

/-- **The classification at 15 vertices**, from the pinned development. -/
theorem classified_15 : Classified 15 :=
  classified_of_catalogue R4333.k15CriticalCatalogue
    R4333.k15CriticalCatalogue_complete k15_catalogue_map

#print axioms K58.classified_16
#print axioms K58.classified_15

end K58
