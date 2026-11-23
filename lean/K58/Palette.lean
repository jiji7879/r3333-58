import K58.Templates
import R4333Lean.CriticalTemplatePaletteSymmetry

namespace K58

theorem catalogue_col_15 : ∀ t i j,
    R4333.k15Template t i j = (template 15 t).col i j := by decide

theorem catalogue_col_16 : ∀ t i j,
    R4333.k16Template t i j = (template 16 t).col i j := by decide

/-- Realize the palette on K15 while allowing the marked position to move. -/
theorem palette_15 (t : Bool) (p : Equiv.Perm (Fin 3)) :
    ∃ e : Equiv.Perm (Fin 15), ∀ i j, i ≠ j →
      (template 15 t).col (e i) (e j) = p ((template 15 t).col i j) := by
  simpa only [catalogue_col_15] using R4333.k15Template_fullPaletteSymmetry t p

/-- On K16 the same realization can be chosen in the stabilizer of any vertex. -/
theorem palette_16_fixing (t : Bool) (p : Equiv.Perm (Fin 3)) (v : Fin 16) :
    ∃ e : Equiv.Perm (Fin 16), e v = v ∧ ∀ i j, i ≠ j →
      (template 16 t).col (e i) (e j) = p ((template 16 t).col i j) := by
  obtain ⟨f, hf⟩ := R4333.k16Template_fullPaletteSymmetry t p
  let A := R4333.k16TemplateToLastEquiv t
  have hlast (x : Fin 16) : A x x = Fin.last 15 := R4333.k16TemplateToLastMap_deleted t x
  have hA (x i j : Fin 16) (hij : i ≠ j) :
      R4333.k16Template t i j = R4333.k16Template t (A x i) (A x j) :=
    R4333.k16TemplateToLastMap_preserves t x i j hij
  let g := f.trans (A (f v))
  let e := g.trans (A v).symm
  refine ⟨e, ?_, ?_⟩
  · change (A v).symm (A (f v) (f v)) = v
    exact (A v).symm_apply_eq.mpr ((hlast _).trans (hlast v).symm)
  · intro i j hij
    simp only [← catalogue_col_16]
    calc
      R4333.k16Template t (e i) (e j) =
          R4333.k16Template t (A v (e i)) (A v (e j)) := hA v _ _ (e.injective.ne hij)
      _ = R4333.k16Template t (g i) (g j) := by simp [e]
      _ = R4333.k16Template t (f i) (f j) := (hA (f v) _ _ (f.injective.ne hij)).symm
      _ = _ := hf i j hij

end K58
