/-
  Placement inequivalence for the cross-arm test, kernel-checked.

  `ArmLayer.lean` computes, for each of the four placements of the type-16 /
  type-36 test, the number `intra3` of colour-3 pairs whose two ends lie in one
  Z-class: 2, 5, 3, 7.  Here that number is turned into a *theorem* of
  inequivalence: `T` is the same count in a form that is manifestly invariant
  under a colour-preserving permutation of the vertices, `T_invariant` proves the
  invariance, and the six pairwise inequivalence statements follow because the
  values 4, 10, 6, 14 are distinct.

  With this, the factor 3 of "3 placements of type 36" (and the factor 1 of the
  displayed type-16 placement, its four images being one orbit) is not a repeat:
  the case count of the cross-arm test is 3 * 4 * (4 * 4) = 192 distinct cases.
-/
import Mathlib
import K58.ArmLayer

open Finset

namespace K58

/-- `T m c` is the number of ordered pairs of distinct vertices that lie in one
class of `c` and are joined by colour 3.  `T` counts each unordered pair twice,
so `T = 2 * intra3`. -/
def T {V : Type} [Fintype V] [DecidableEq V] (m : V → V → Nat) (c : V → Nat) : Nat :=
  (univ.filter (fun p : V × V => p.1 ≠ p.2 ∧ c p.1 = c p.2 ∧ m p.1 p.2 = 3)).card

/-- **`T` is an invariant of a placement.**  A colour-preserving permutation of
the vertices that carries the class partition of `c₁` to that of `c₂` preserves
`T`; hence two placements with different `T` cannot be equivalent. -/
theorem T_invariant {V : Type} [Fintype V] [DecidableEq V]
    (m₁ m₂ : V → V → Nat) (c₁ c₂ : V → Nat) (e : Equiv.Perm V)
    (hm : ∀ x y, m₂ (e x) (e y) = m₁ x y)
    (hc : ∀ x y, c₂ (e x) = c₂ (e y) ↔ c₁ x = c₁ y) :
    T m₁ c₁ = T m₂ c₂ := by
  unfold T
  refine Finset.card_bij (fun p _ => (e p.1, e p.2)) ?_ ?_ ?_
  · intro p hp
    simp only [mem_filter, mem_univ, true_and] at hp ⊢
    exact ⟨fun h => hp.1 (e.injective h), (hc p.1 p.2).mpr hp.2.1,
      by rw [hm p.1 p.2]; exact hp.2.2⟩
  · intro p hp q hq hpq
    simp only [Prod.mk.injEq] at hpq
    exact Prod.ext (e.injective hpq.1) (e.injective hpq.2)
  · intro q hq
    simp only [mem_filter, mem_univ, true_and] at hq
    refine ⟨(e.symm q.1, e.symm q.2), ?_, by simp⟩
    simp only [mem_filter, mem_univ, true_and]
    refine ⟨fun h => hq.1 (by simpa using congrArg e h), ?_, ?_⟩
    · refine (hc (e.symm q.1) (e.symm q.2)).mp ?_
      simpa using hq.2.1
    · have h2 := hm (e.symm q.1) (e.symm q.2)
      simp only [Equiv.apply_symm_apply] at h2
      rw [← h2]; exact hq.2.2

/-- The arm colouring as a function of two vertices. -/
def colF (m : List Nat) : Fin 14 → Fin 14 → Nat := fun i j => m.getD (14 * i.val + j.val) 0

/-- The class map as a function of a vertex. -/
def clsFn (c : List Nat) : Fin 14 → Nat := fun i => c.getD i.val 999

/-- The values of `T` on the four placements: twice `intra3`, so 4, 10, 6, 14. -/
theorem T_values :
    T (colF m_display16) (clsFn cls_display16) = 4 ∧
    T (colF m_p36_0) (clsFn cls_p36_0) = 10 ∧
    T (colF m_p36_1) (clsFn cls_p36_1) = 6 ∧
    T (colF m_p36_2) (clsFn cls_p36_2) = 14 := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> decide

/-- No colour-preserving vertex permutation carries the displayed type-16
partition to a type-36 placement (with its own arm colouring). -/
theorem no_iso_display_p36_0 :
    ¬ ∃ e : Equiv.Perm (Fin 14),
        (∀ x y, colF m_p36_0 (e x) (e y) = colF m_display16 x y) ∧
        (∀ x y, clsFn cls_p36_0 (e x) = clsFn cls_p36_0 (e y) ↔
          clsFn cls_display16 x = clsFn cls_display16 y) := by
  rintro ⟨e, hm, hc⟩
  have h := T_invariant (colF m_display16) (colF m_p36_0) (clsFn cls_display16)
    (clsFn cls_p36_0) e hm hc
  rw [T_values.1, T_values.2.1] at h
  exact absurd h (by decide)

theorem no_iso_display_p36_1 :
    ¬ ∃ e : Equiv.Perm (Fin 14),
        (∀ x y, colF m_p36_1 (e x) (e y) = colF m_display16 x y) ∧
        (∀ x y, clsFn cls_p36_1 (e x) = clsFn cls_p36_1 (e y) ↔
          clsFn cls_display16 x = clsFn cls_display16 y) := by
  rintro ⟨e, hm, hc⟩
  have h := T_invariant (colF m_display16) (colF m_p36_1) (clsFn cls_display16)
    (clsFn cls_p36_1) e hm hc
  rw [T_values.1, T_values.2.2.1] at h
  exact absurd h (by decide)

theorem no_iso_display_p36_2 :
    ¬ ∃ e : Equiv.Perm (Fin 14),
        (∀ x y, colF m_p36_2 (e x) (e y) = colF m_display16 x y) ∧
        (∀ x y, clsFn cls_p36_2 (e x) = clsFn cls_p36_2 (e y) ↔
          clsFn cls_display16 x = clsFn cls_display16 y) := by
  rintro ⟨e, hm, hc⟩
  have h := T_invariant (colF m_display16) (colF m_p36_2) (clsFn cls_display16)
    (clsFn cls_p36_2) e hm hc
  rw [T_values.1, T_values.2.2.2] at h
  exact absurd h (by decide)

/-- **The three type-36 placements are pairwise inequivalent**: no
colour-preserving vertex permutation of the type-36 arm carries one placement's
class partition to another's. -/
theorem p36_pairwise_inequivalent :
    (¬ ∃ e : Equiv.Perm (Fin 14),
        (∀ x y, colF m_p36_1 (e x) (e y) = colF m_p36_0 x y) ∧
        (∀ x y, clsFn cls_p36_1 (e x) = clsFn cls_p36_1 (e y) ↔
          clsFn cls_p36_0 x = clsFn cls_p36_0 y)) ∧
    (¬ ∃ e : Equiv.Perm (Fin 14),
        (∀ x y, colF m_p36_2 (e x) (e y) = colF m_p36_0 x y) ∧
        (∀ x y, clsFn cls_p36_2 (e x) = clsFn cls_p36_2 (e y) ↔
          clsFn cls_p36_0 x = clsFn cls_p36_0 y)) ∧
    (¬ ∃ e : Equiv.Perm (Fin 14),
        (∀ x y, colF m_p36_2 (e x) (e y) = colF m_p36_1 x y) ∧
        (∀ x y, clsFn cls_p36_2 (e x) = clsFn cls_p36_2 (e y) ↔
          clsFn cls_p36_1 x = clsFn cls_p36_1 y)) := by
  refine ⟨?_, ?_, ?_⟩
  · rintro ⟨e, hm, hc⟩
    have h := T_invariant (colF m_p36_0) (colF m_p36_1) (clsFn cls_p36_0)
      (clsFn cls_p36_1) e hm hc
    rw [T_values.2.1, T_values.2.2.1] at h
    exact absurd h (by decide)
  · rintro ⟨e, hm, hc⟩
    have h := T_invariant (colF m_p36_0) (colF m_p36_2) (clsFn cls_p36_0)
      (clsFn cls_p36_2) e hm hc
    rw [T_values.2.1, T_values.2.2.2] at h
    exact absurd h (by decide)
  · rintro ⟨e, hm, hc⟩
    have h := T_invariant (colF m_p36_1) (colF m_p36_2) (clsFn cls_p36_1)
      (clsFn cls_p36_2) e hm hc
    rw [T_values.2.2.1, T_values.2.2.2] at h
    exact absurd h (by decide)

#print axioms K58.T_invariant
#print axioms K58.T_values
#print axioms K58.no_iso_display_p36_0
#print axioms K58.no_iso_display_p36_1
#print axioms K58.no_iso_display_p36_2
#print axioms K58.p36_pairwise_inequivalent

end K58
