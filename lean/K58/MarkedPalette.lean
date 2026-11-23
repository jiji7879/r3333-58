import K58.Templates

namespace K58

/-- The ordered vector at the reference vertex of both deleted templates. -/
theorem template15_zero_degrees (t : Bool) :
    [deg (template 15 t) 0 0, deg (template 15 t) 0 1, deg (template 15 t) 0 2] = [4,5,5] := by
  cases t <;> decide

/-- A marked vertex of either 15-vertex template obstructs the palette swap
of 0 and 1. Its colour-0 and colour-1 neighbourhoods have different sizes. -/
theorem no_marked_swap_15 (t : Bool) :
    ¬ ∃ e : Equiv.Perm (Fin 15), e 0 = 0 ∧
      ∀ i j, i ≠ j → (template 15 t).col (e i) (e j) =
        Equiv.swap (0 : Fin 3) 1 ((template 15 t).col i j) := by
  rintro ⟨e, hfix, hmap⟩
  let N (c : Fin 3) := Finset.univ.filter fun j : Fin 15 =>
    j ≠ 0 ∧ (template 15 t).col 0 j = c
  have hdeg : (N 0).card = 4 ∧ (N 1).card = 5 := by
    cases t <;> decide
  have hcard : (N 0).card = (N 1).card := by
    apply Finset.card_bijective e e.bijective
    intro j
    simp only [N, Finset.mem_filter, Finset.mem_univ, true_and]
    by_cases hj : j = 0
    · simp [hj, hfix]
    · have hej : e j ≠ 0 := hfix ▸ e.injective.ne hj
      have h := hmap 0 j (Ne.symm hj)
      rw [hfix] at h
      rw [h]
      have hswap (c : Fin 3) : c = 0 ↔ Equiv.swap (0 : Fin 3) 1 c = 1 := by
        fin_cases c <;> decide
      simp [hj, hej, ← hswap]
  omega

end K58
