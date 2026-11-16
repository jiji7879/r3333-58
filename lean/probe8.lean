import Mathlib
#check Finset.eq_empty_iff_forall_not_mem
#check Finset.notMem_empty
#check Finset.mem_empty
#check Finset.card_eq_zero
example (s : Finset ℕ) (h : ∀ x, x ∉ s) : s = ∅ := by
  ext x; simp [h x]
