/-
K58: from "some root receives at least as many tickets as it sends" to the
per-arm thresholds of the cover.
-/
import K58.DegreeCap

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Splitting a count by the colour of the edge to `i`, when the remaining
condition depends only on that colour. -/
theorem card_filter_colour {k : ℕ} (G : EdgeCol V k) (i : V)
    (q : Fin k → Prop) [DecidablePred q] :
    (Finset.univ.filter (fun j : V => j ≠ i ∧ q (G.col i j))).card
      = ∑ a : Fin k, if q a
          then (Finset.univ.filter (fun j : V => j ≠ i ∧ G.col i j = a)).card else 0 := by
  have hmaps : Set.MapsTo (fun j : V => G.col i j)
      ↑(Finset.univ.filter (fun j : V => j ≠ i ∧ q (G.col i j)))
      ↑(Finset.univ : Finset (Fin k)) := fun x _ => Finset.mem_univ _
  have h := Finset.card_eq_sum_card_fiberwise
    (s := Finset.univ.filter (fun j : V => j ≠ i ∧ q (G.col i j)))
    (t := (Finset.univ : Finset (Fin k))) (f := fun j : V => G.col i j) hmaps
  rw [h]
  refine Finset.sum_congr rfl fun a _ => ?_
  by_cases hq : q a
  · rw [if_pos hq]
    congr 1
    ext j
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    constructor
    · rintro ⟨⟨hji, hqj⟩, hcol⟩
      exact ⟨hji, hcol⟩
    · rintro ⟨hji, hcol⟩
      exact ⟨⟨hji, hcol ▸ hq⟩, hcol⟩
  · rw [if_neg hq, Finset.card_eq_zero]
    ext j
    simp only [Finset.mem_filter, Finset.mem_univ, true_and, Finset.notMem_empty,
      iff_false, not_and]
    intro hji hqj
    exact hq (hqj ▸ hji.2)

/-- Splitting a count by the colour of the edge to `i`, for a condition on the
vertex `j` itself. -/
theorem card_filter_colour' {k : ℕ} (G : EdgeCol V k) (i : V)
    (Q : V → Prop) [DecidablePred Q] :
    (Finset.univ.filter (fun j : V => i ≠ j ∧ Q j)).card
      = ∑ a : Fin k,
          (Finset.univ.filter (fun j : V => i ≠ j ∧ G.col i j = a ∧ Q j)).card := by
  have hmaps : Set.MapsTo (fun j : V => G.col i j)
      ↑(Finset.univ.filter (fun j : V => i ≠ j ∧ Q j))
      ↑(Finset.univ : Finset (Fin k)) := fun x _ => Finset.mem_univ _
  have h := Finset.card_eq_sum_card_fiberwise
    (s := Finset.univ.filter (fun j : V => i ≠ j ∧ Q j))
    (t := (Finset.univ : Finset (Fin k))) (f := fun j : V => G.col i j) hmaps
  rw [h]
  refine Finset.sum_congr rfl fun a _ => ?_
  congr 1
  ext j
  simp only [Finset.mem_filter, Finset.mem_univ, true_and]
  tauto

/-- Tickets sent are the sum of the critical colour degrees. -/
theorem w_eq_sum_critical (G : EdgeCol V 4) (i : V) :
    w G i = ∑ a : Fin 4, if 15 ≤ deg G i a then deg G i a else 0 := by
  have h := card_filter_colour (k := 4) G i (q := fun a => 15 ≤ deg G i a)
  rw [w]
  simp only [Sends]
  rw [h]
  refine Finset.sum_congr rfl fun a _ => ?_
  by_cases hc : 15 ≤ deg G i a
  · rw [if_pos hc, if_pos hc, deg]
  · rw [if_neg hc, if_neg hc]

/-- Senders in a fixed colour arm of `i`. -/
noncomputable def armSenders (G : EdgeCol V 4) (i : V) (a : Fin 4) : ℕ :=
  (Finset.univ.filter (fun j : V => i ≠ j ∧ G.col i j = a ∧
    15 ≤ deg G j (G.col j i))).card

/-- Tickets received are the sum of the senders in the four arms. -/
theorem H_eq_sum_armSenders (G : EdgeCol V 4) (i : V) :
    H G i = ∑ a : Fin 4, armSenders G i a := by
  have h := card_filter_colour' (k := 4) G i (Q := fun j => 15 ≤ deg G j (G.col j i))
  rw [H]
  simp only [Sends]
  rw [h]
  rfl

/-- The cover's pigeonhole step: if no arm reaches its threshold, the total
number of senders is below the critical mass. -/
theorem threshold_pigeonhole {p t s : Fin 4 → ℕ}
    (h : ∑ a : Fin 4, (t a - 1) < ∑ a : Fin 4, if 15 ≤ p a then p a else 0)
    (hs : s ≤ t - 1) : ∑ a : Fin 4, s a < ∑ a : Fin 4, if 15 ≤ p a then p a else 0 := by
  have : ∑ a : Fin 4, s a ≤ ∑ a : Fin 4, (t a - 1) := Finset.sum_le_sum fun a _ => hs a
  omega

end K58
