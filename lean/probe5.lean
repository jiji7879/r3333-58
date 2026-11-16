import Mathlib
example (a : Fin 3) : Function.Injective (fun c : {c : Fin 3 // c ≠ a} => if c.1 = a + 1 then (0 : Fin 2) else 1) := by
  rintro ⟨c, hc⟩ ⟨d, hd⟩ hcd
  simp only at hcd ⊢
  fin_cases a <;> fin_cases c <;> fin_cases d <;> simp_all
  all_goals first | exact absurd rfl hc | exact absurd rfl hd
