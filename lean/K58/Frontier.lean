import K58.Plans
import Mathlib.Data.Fin.Tuple.Sort
import Mathlib.Tactic.IntervalCases

namespace K58

/-- The original universal hypothesis fails on the zero degree vector. -/
theorem original_threshold_hypothesis_impossible
    (t : (Fin 4 → ℕ) → Fin 4 → ℕ) :
    ¬ (∀ p : Fin 4 → ℕ, (∑ a : Fin 4, (t p a - 1)) <
      ∑ a : Fin 4, if 15 ≤ p a then p a else 0) := by
  intro h
  simpa using h (fun _ => 0)

/-- A threshold plan for this balanced root forces one of its arms. -/
theorem balanced_root_arm_reaches (G : EdgeCol (Fin 58) 4) (r : Fin 58)
    (hr : w G r ≤ H G r) (t : Fin 4 → ℕ)
    (ht : (∑ a : Fin 4, (t a - 1)) <
      ∑ a : Fin 4, if 15 ≤ deg G r a then deg G r a else 0) :
    ∃ a : Fin 4, t a ≤ armSenders G r a := by
  by_contra h
  simp only [not_exists, not_le] at h
  have hs : (fun a => armSenders G r a) ≤ t - 1 := fun a => by
    change armSenders G r a ≤ t a - 1
    have ha := h a
    omega
  have hlt := threshold_pigeonhole (p := deg G r) ht hs
  rw [← H_eq_sum_armSenders, ← w_eq_sum_critical] at hlt
  exact (not_lt_of_ge hr) hlt

/-- Only balanced roots need a plan. The witness retains the balance condition. -/
theorem exists_balanced_root_arm_reaches (G : EdgeCol (Fin 58) 4)
    (t : Fin 58 → Fin 4 → ℕ)
    (ht : ∀ r, w G r ≤ H G r →
      (∑ a : Fin 4, (t r a - 1)) <
        ∑ a : Fin 4, if 15 ≤ deg G r a then deg G r a else 0) :
    ∃ r : Fin 58, w G r ≤ H G r ∧ ∃ a : Fin 4, t r a ≤ armSenders G r a := by
  obtain ⟨r, hr⟩ := exists_root G
  exact ⟨r, hr, balanced_root_arm_reaches G r hr (t r) (ht r hr)⟩

/-- All degree profiles are listed in descending degree order. -/
def degreeProfiles58 : List (List ℕ) := [
  [15, 14, 14, 14], [15, 15, 14, 13], [15, 15, 15, 12],
  [16, 14, 14, 13], [16, 15, 13, 13], [16, 15, 14, 12],
  [16, 15, 15, 11], [16, 16, 13, 12], [16, 16, 14, 11],
  [16, 16, 15, 10], [16, 16, 16, 9]
]

/-- A decreasing degree vector of sum 57 with maximum 16 is listed. -/
theorem sorted_degree_profile_mem (a b c d : ℕ)
    (hab : b ≤ a) (hbc : c ≤ b) (hcd : d ≤ c)
    (ha : a ≤ 16) (hs : a + b + c + d = 57) :
    [a, b, c, d] ∈ degreeProfiles58 := by
  have h₁ : 15 ≤ a := by omega
  have h₂ : 14 ≤ b ∧ b ≤ 16 := by omega
  have h₃ : 13 ≤ c ∧ c ≤ 16 := by omega
  have h₄ : 9 ≤ d ∧ d ≤ 16 := by omega
  obtain ⟨hb₁, hb₂⟩ := h₂
  obtain ⟨hc₁, hc₂⟩ := h₃
  obtain ⟨hd₁, hd₂⟩ := h₄
  interval_cases a <;> interval_cases b <;> interval_cases c <;>
    interval_cases d <;> first | omega | decide

/-- Every vertex has one of the eleven profiles after reordering its colours. -/
theorem root_degree_profile (G : EdgeCol (Fin 58) 4) (h : TriangleFree G)
    (r : Fin 58) :
    ∃ σ : Equiv.Perm (Fin 4),
      [deg G r (σ 0), deg G r (σ 1), deg G r (σ 2), deg G r (σ 3)] ∈ degreeProfiles58 := by
  let p : Fin 4 → ℕ := deg G r
  obtain ⟨hs, hc⟩ := profile_sum G h r
  let σ := Tuple.sort (fun a : Fin 4 => 16 - p a)
  refine ⟨σ, ?_⟩
  have hm := Tuple.monotone_sort (fun a : Fin 4 => 16 - p a)
  have hdesc {i j : Fin 4} (hij : i ≤ j) : p (σ j) ≤ p (σ i) := by
    have hd := hm hij
    change 16 - p (σ i) ≤ 16 - p (σ j) at hd
    have hi : p (σ i) ≤ 16 := hc (σ i)
    have hj : p (σ j) ≤ 16 := hc (σ j)
    omega
  have hsum : (∑ a : Fin 4, p (σ a)) = 57 := (Equiv.sum_comp σ p).trans hs
  simp only [Fin.sum_univ_succ] at hsum
  apply sorted_degree_profile_mem
  · exact hdesc (by decide : (0 : Fin 4) ≤ 1)
  · exact hdesc (by decide : (1 : Fin 4) ≤ 2)
  · exact hdesc (by decide : (2 : Fin 4) ≤ 3)
  · exact hc (σ 0)
  · change p (σ 0) + p (σ 1) + p (σ 2) + p (σ 3) = 57
    change p (σ 0) + (p (σ 1) + (p (σ 2) + p (σ 3))) = 57 at hsum
    omega

/-- The 41 plans collectively mention exactly the eleven degree profiles. -/
theorem planned_degree_profiles : (plans.map Plan.prof).eraseDups = degreeProfiles58 := by decide


/-- The planned degree at a normalized colour index. -/
def plannedDegree (x : Plan) (a : Fin 4) : ℕ := x.prof[a.val]?.getD 0

/-- The planned threshold at a normalized colour index. -/
def plannedThreshold (x : Plan) (a : Fin 4) : ℕ := x.t[a.val]?.getD 0

/-- The slack condition in the exact indexing used by balanced roots. -/
def indexedPlanOk (x : Plan) : Prop :=
  (∑ a : Fin 4, (plannedThreshold x a - 1)) <
    ∑ a : Fin 4, if 15 ≤ plannedDegree x a then plannedDegree x a else 0

instance (x : Plan) : Decidable (indexedPlanOk x) := by
  unfold indexedPlanOk
  infer_instance

theorem indexed_plans_ok {x : Plan} (hx : x ∈ plans) : indexedPlanOk x := by
  have h : plans.all (fun y => decide (indexedPlanOk y)) = true := by decide
  exact of_decide_eq_true ((List.all_eq_true.mp h) x hx)

/-- The incoming senders in an arm are a subset of that arm. -/
theorem arm_senders_le_deg (G : EdgeCol (Fin 58) 4) (r : Fin 58) (a : Fin 4) :
    armSenders G r a ≤ deg G r a := by
  unfold armSenders deg
  apply Finset.card_le_card
  intro v hv
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hv ⊢
  exact ⟨Ne.symm hv.1, hv.2.1⟩

/-- A member of the frozen table forces an active arm at a matching balanced root. -/
theorem normalized_plan_arm_reaches (G : EdgeCol (Fin 58) 4) (r : Fin 58)
    (hr : w G r ≤ H G r) (σ : Equiv.Perm (Fin 4)) (x : Plan)
    (hx : x ∈ plans) (hprof : ∀ a, deg G r (σ a) = plannedDegree x a) :
    ∃ a : Fin 4, plannedThreshold x a ≤ armSenders G r (σ a) ∧
      plannedThreshold x a ≤ plannedDegree x a := by
  have hslack := indexed_plans_ok hx
  unfold indexedPlanOk at hslack
  let t : Fin 4 → ℕ := fun a => plannedThreshold x (σ.symm a)
  have hcrit : (∑ a : Fin 4, if 15 ≤ plannedDegree x a then plannedDegree x a else 0) =
      ∑ a : Fin 4, if 15 ≤ deg G r a then deg G r a else 0 := by
    calc
      _ = ∑ a : Fin 4, if 15 ≤ deg G r (σ a) then deg G r (σ a) else 0 :=
        Finset.sum_congr rfl (fun a _ => by rw [hprof a])
      _ = _ := Equiv.sum_comp σ (fun a => if 15 ≤ deg G r a then deg G r a else 0)
  have hsum : (∑ a : Fin 4, (t a - 1)) =
      ∑ a : Fin 4, (plannedThreshold x a - 1) :=
    Equiv.sum_comp σ.symm (fun a => plannedThreshold x a - 1)
  have ht : (∑ a : Fin 4, (t a - 1)) <
      ∑ a : Fin 4, if 15 ≤ deg G r a then deg G r a else 0 := by
    rwa [hsum, ← hcrit]
  obtain ⟨a, ha⟩ := balanced_root_arm_reaches G r hr t ht
  change plannedThreshold x (σ.symm a) ≤ armSenders G r a at ha
  refine ⟨σ.symm a, ?_, ?_⟩
  · simpa only [Equiv.apply_symm_apply] using ha
  · rw [← hprof (σ.symm a), Equiv.apply_symm_apply]
    exact ha.trans (arm_senders_le_deg G r a)

end K58
