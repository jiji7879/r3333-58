import Mathlib

/-!
# The strict/balanced ticket dichotomy

`H v` and `w v` are arbitrary natural number functions.  Their sum equality is
an explicit hypothesis; in K58 it is the directed-ticket double count.  No
Ramsey theorem is used in this file.
-/
namespace K58
open scoped BigOperators
open Finset

variable {ι : Type*} [Fintype ι]

/-- If total incoming tickets equal total outgoing tickets, then either some
vertex is strict (hence has at least one surplus ticket) or every vertex is
exactly balanced. -/
theorem strict_or_balanced (H w : ι → ℕ)
    (h : ∑ v, H v = ∑ v, w v) :
    (∃ v, w v + 1 ≤ H v) ∨ (∀ v, H v = w v) := by
  classical
  by_cases hs : ∃ v, w v < H v
  · left
    obtain ⟨v, hv⟩ := hs
    exact ⟨v, by omega⟩
  · right
    push_neg at hs
    have heq : ∀ i ∈ (univ : Finset ι), H i = w i :=
      (Finset.sum_eq_sum_iff_of_le (f := H) (g := w)
        (fun i _ => hs i)).1 h
    intro v
    exact heq v (Finset.mem_univ v)

/-- In particular a finite nonempty ticket system has a root with no deficit. -/
theorem exists_ticket_root [Nonempty ι] (H w : ι → ℕ)
    (h : ∑ v, H v = ∑ v, w v) : ∃ v, w v ≤ H v := by
  rcases strict_or_balanced H w h with hs | hb
  · obtain ⟨v, hv⟩ := hs
    exact ⟨v, by omega⟩
  · exact ⟨Classical.choice inferInstance, by rw [hb]⟩

/-- Named strict branch of profile `(15,15,14,13)`: the two small arms have
combined capacity 27, so H >= 31 forces at least four senders in the big arms. -/
theorem canonical_strict_big_floor (H B : ℕ)
    (hH : 31 ≤ H) (hdecomp : H ≤ B + 27) : 4 ≤ B := by
  omega

/-- Its ordinary floor is exactly three. -/
theorem canonical_big_floor (H B : ℕ)
    (hH : 30 ≤ H) (hdecomp : H ≤ B + 27) : 3 ≤ B := by
  omega

/-- In the globally balanced alternative, a canonical root has H = 30. -/
theorem canonical_balanced_exact (H w : ℕ)
    (hw : w = 30) (hb : H = w) : H = 30 := by
  omega

#print axioms K58.strict_or_balanced
#print axioms K58.exists_ticket_root
#print axioms K58.canonical_strict_big_floor
#print axioms K58.canonical_big_floor
#print axioms K58.canonical_balanced_exact

end K58
