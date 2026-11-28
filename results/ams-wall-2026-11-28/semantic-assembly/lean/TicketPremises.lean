import K58.ArmSender

/-!
Physical ticket inequality used by the retained `(16,16,14,11)` parent.
This does not by itself identify the coded guard set or prove `ChainReady`.
-/
set_option autoImplicit false
namespace K58.SemanticAssembly

open K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- At a balanced root of profile `(16,16,14,11)`, at least seven senders lie
in the two critical arms. The two small arms contribute at most `14+11`. -/
theorem seven_critical_senders_of_16_16_14_11
    (G : EdgeCol V 4) (r : V)
    (h0 : deg G r 0 = 16) (h1 : deg G r 1 = 16)
    (h2 : deg G r 2 = 14) (h3 : deg G r 3 = 11)
    (hb : w G r ≤ H G r) :
    7 ≤ armSenders G r 0 + armSenders G r 1 := by
  have hw : w G r = 32 := by
    rw [w_eq_sum_critical, Fin.sum_univ_four, h0, h1, h2, h3]
    decide
  have hH : H G r = armSenders G r 0 + armSenders G r 1 +
      armSenders G r 2 + armSenders G r 3 := by
    rw [H_eq_sum_armSenders, Fin.sum_univ_four]
  have hb2 := armSenders_le_deg G r 2
  have hb3 := armSenders_le_deg G r 3
  rw [hw, hH] at hb
  omega

/-- Once one already-forced sender is omitted by the encoder, the two exact
`6` counter bounds follow. The equalities are the required guard-set map:
`coded0,coded1` must enumerate the remaining physical senders exactly. -/
theorem six_of_adjusted_guard_count (critical arm codedCritical codedArm : Nat)
    (hcritical : 7 ≤ critical) (harm : 7 ≤ arm)
    (hcodedCritical : codedCritical + 1 = critical)
    (hcodedArm : codedArm + 1 = arm) :
    6 ≤ codedCritical ∧ 6 ≤ codedArm := by omega

#print axioms K58.SemanticAssembly.seven_critical_senders_of_16_16_14_11
#print axioms K58.SemanticAssembly.six_of_adjusted_guard_count

end K58.SemanticAssembly
