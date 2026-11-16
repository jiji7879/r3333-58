/-
K58: the mathematical core of the `R(3,3,3,3) ≤ 58` reduction, assembled.

Proved here, with no `sorry` and no extra axioms:

* every colour degree of a triangle-free 4-colouring is at most 16
  (`deg_le_sixteen`, via `R(3,3,3) ≤ 17` and `R(3,3) ≤ 6`);
* the colour degrees at a vertex sum to 57 (`profile_sum`);
* tickets sent equal tickets received (`sum_w_eq_sum_H`), so some root has
  `H ≥ w` (`exists_root`);
* `w` is the sum of the critical degrees and `H` is the sum of the senders in
  the four arms (`w_eq_sum_critical`, `H_eq_sum_armSenders`);
* hence, for any threshold assignment obeying the plan's inequality
  `Σ (t a - 1) < Σ critical degrees`, some arm at some root reaches its
  threshold (`exists_arm_reaches`).

Not here, and what a full bridge to the 113,179 cases still needs:

1. the marking lemma: a sender in an arm that has reached its threshold
   realises the units of one of the emitted cases (this is where the U/T
   classification, the palette quotient and the support embeddings live);
2. the enumeration of the eleven degree profiles and of the 41 threshold plans;
3. the computational premise: all 113,179 case formulas are unsatisfiable.

With (1)-(3) the argument closes: `exists_arm_reaches` produces a realised
case, and (3) says no case is realised.
-/
import K58.Reduction

namespace K58

/-- In a triangle-free 4-colouring of `K_58`, the colour degrees at any vertex
sum to 57 and each is at most 16. -/
theorem profile_sum (G : EdgeCol (Fin 58) 4) (h : TriangleFree G) (r : Fin 58) :
    (∑ a : Fin 4, deg G r a = 57) ∧ (∀ a : Fin 4, deg G r a ≤ 16) := by
  refine ⟨?_, fun a => deg_le_sixteen G h r a⟩
  have hsum := sum_deg G r
  simpa using hsum

/-- The cover's pigeonhole step, at the level of a colouring: for any threshold
assignment obeying the plan's inequality at every profile, some arm of some
root reaches its threshold. -/
theorem exists_arm_reaches (G : EdgeCol (Fin 58) 4)
    (t : (Fin 4 → ℕ) → Fin 4 → ℕ)
    (ht : ∀ p : Fin 4 → ℕ, (∑ a : Fin 4, (t p a - 1))
      < ∑ a : Fin 4, if 15 ≤ p a then p a else 0) :
    ∃ r : Fin 58, ∃ a : Fin 4, t (fun b => deg G r b) a ≤ armSenders G r a := by
  obtain ⟨r, hr⟩ := exists_root G
  have hH := H_eq_sum_armSenders G r
  have hw := w_eq_sum_critical G r
  by_contra hc
  simp only [not_exists, not_le] at hc
  have hle : ∑ a : Fin 4, armSenders G r a
      ≤ ∑ a : Fin 4, (t (fun b => deg G r b) a - 1) :=
    Finset.sum_le_sum fun a _ => by
      have hca := hc r a
      omega
  have hlt := ht (fun b => deg G r b)
  omega

end K58
