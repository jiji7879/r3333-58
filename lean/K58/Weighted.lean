/-
The arithmetic of the corrected weighted statistic, kernel-checked.

Context (the campaign's record): for a vertex `y` of the 14-arm, the weighted
statistic `t y` counts the zero senders of `y` at which `y` is matched to its
fixed partner arm.  Two facts are input to the correction:

  * each zero sender contributes at most one match, and a vertex has five zero
    senders, so `t y ≤ 5`;
  * the fourteen vertex totals sum to 65.

The correction's content is then pure arithmetic: fourteen integers, each at
most five, summing to 65, must have at least nine equal to five; in particular
"eight totals of five and six of at most four", which would give at most 64, is
impossible.  This file proves both, and the general pigeonhole they come from,
with no `sorry`, no `native_decide` and no axiom beyond the standard three.

Nothing here re-derives the two inputs; they are hypotheses, and this file makes
the step from them to the stated conclusion a theorem.
-/
import Mathlib

open Finset
open scoped BigOperators

namespace K58

theorem sum_le_of_card_eq {k m S : ℕ} (t : Fin k → ℕ)
    (ht : ∀ i, t i ≤ m) (hS : ∑ i, t i = S) :
    S ≤ k * (m - 1) + (univ.filter (fun i => t i = m)).card := by
  classical
  set F := univ.filter (fun i : Fin k => t i = m) with hF
  have hmem : ∀ i, i ∈ F ↔ t i = m := by
    intro i; rw [hF, mem_filter]; exact ⟨fun h => h.2, fun h => ⟨mem_univ i, h⟩⟩
  have hk : F.card ≤ k := by simpa using Finset.card_le_univ F
  have hFsum : ∑ i ∈ F, t i = F.card * m := by
    have hc : ∀ i ∈ F, t i = m := fun i hi => (hmem i).1 hi
    rw [Finset.sum_congr rfl hc, Finset.sum_const, smul_eq_mul]
  have hCsum : ∑ i ∈ Fᶜ, t i ≤ Fᶜ.card * (m - 1) := by
    have hstep : ∀ i ∈ Fᶜ, t i ≤ m - 1 := by
      intro i hi
      have hne : t i ≠ m := fun h => (Finset.mem_compl.1 hi) ((hmem i).2 h)
      have := ht i
      omega
    calc ∑ i ∈ Fᶜ, t i ≤ ∑ _i ∈ Fᶜ, (m - 1) := Finset.sum_le_sum hstep
      _ = Fᶜ.card * (m - 1) := by rw [Finset.sum_const, smul_eq_mul]
  have hc : Fᶜ.card = k - F.card := by rw [Finset.card_compl, Fintype.card_fin]
  have hC' : ∑ i ∈ Fᶜ, t i ≤ (k - F.card) * (m - 1) := by rw [← hc]; exact hCsum
  have hsplit : S = ∑ i ∈ F, t i + ∑ i ∈ Fᶜ, t i := by
    rw [← hS, Finset.sum_add_sum_compl]
  rw [hsplit, hFsum]
  rcases Nat.eq_zero_or_pos m with hm | hm
  · have hz : ∑ i ∈ Fᶜ, t i = 0 := by
      apply Finset.sum_eq_zero
      intro i _
      have := ht i
      omega
    rw [hm, hz]
    simp
  · have hid1 : F.card * m = F.card * (m - 1) + F.card := by
      obtain ⟨n, rfl⟩ : ∃ n, m = n + 1 := ⟨m - 1, by omega⟩
      rw [Nat.mul_succ, Nat.add_sub_cancel]
    have hid2 : (k - F.card) * (m - 1) + F.card * (m - 1) = k * (m - 1) := by
      rw [Nat.sub_mul, Nat.sub_add_cancel (Nat.mul_le_mul_right _ hk)]
    omega

/-- **At least nine of the fourteen attain five.**  The correction's conclusion,
with the two inputs as hypotheses. -/
theorem nine_of_fourteen (t : Fin 14 → ℕ) (h5 : ∀ i, t i ≤ 5) (hsum : ∑ i, t i = 65) :
    9 ≤ (univ.filter (fun i => t i = 5)).card := by
  have h := sum_le_of_card_eq t h5 hsum
  rw [show (14 : ℕ) * (5 - 1) = 56 by norm_num] at h
  omega

/-- **"Eight fives and six fours" is impossible.**  If every one of the fourteen
totals is 4 or 5 and the total is 65, the number of fives is not 8: eight fives
with six values at most four give at most 64. -/
theorem not_eight_fives (t : Fin 14 → ℕ) (h4 : ∀ i, 4 ≤ t i) (h5 : ∀ i, t i ≤ 5)
    (hsum : ∑ i, t i = 65) :
    (univ.filter (fun i => t i = 5)).card ≠ 8 := by
  intro h8
  classical
  set F := univ.filter (fun i : Fin 14 => t i = 5) with hF
  have hmem : ∀ i, i ∈ F ↔ t i = 5 := by
    intro i; rw [hF, mem_filter]; exact ⟨fun h => h.2, fun h => ⟨mem_univ i, h⟩⟩
  have hFsum : ∑ i ∈ F, t i = F.card * 5 := by
    have hc : ∀ i ∈ F, t i = 5 := fun i hi => (hmem i).1 hi
    rw [Finset.sum_congr rfl hc, Finset.sum_const, smul_eq_mul]
  have hCsum : ∑ i ∈ Fᶜ, t i ≤ Fᶜ.card * 4 := by
    have h4' : ∀ i ∈ Fᶜ, t i = 4 := by
      intro i hi
      have hne : t i ≠ 5 := fun h => (Finset.mem_compl.1 hi) ((hmem i).2 h)
      have := h4 i; have := h5 i
      omega
    rw [Finset.sum_congr rfl h4']
    simp [Finset.sum_const, smul_eq_mul]
  have hc : Fᶜ.card = 14 - F.card := by rw [Finset.card_compl, Fintype.card_fin]
  have hsplit : (65 : ℕ) = ∑ i ∈ F, t i + ∑ i ∈ Fᶜ, t i := by
    rw [← hsum, Finset.sum_add_sum_compl]
  have h65 : (65 : ℕ) = F.card * 5 + ∑ i ∈ Fᶜ, t i := by rw [hsplit, hFsum]
  rw [h8] at h65
  rw [hc, h8] at hCsum
  omega

/-- **A vertex total is at most five.**  The matched senders of a vertex are a
subset of its five zero senders. -/
theorem total_le_five {V : Type*} [DecidableEq V] (Z M : Finset V)
    (hsub : M ⊆ Z) (hZ : Z.card = 5) : M.card ≤ 5 := by
  have := Finset.card_le_card hsub
  omega

end K58

#print axioms K58.sum_le_of_card_eq
#print axioms K58.nine_of_fourteen
#print axioms K58.not_eight_fives
#print axioms K58.total_le_five
