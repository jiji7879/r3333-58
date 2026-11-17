/-
K58: from a balanced root to a plan entry and a reached threshold.

`Frontier.root_degree_profile` says every vertex has one of the eleven profiles;
`Frontier.planned_degree_profiles` says the 41 table entries mention exactly
those.  Here they are composed, so the threshold argument no longer needs a
matching hypothesis: at every balanced root of a triangle-free colouring some
frozen plan forces one of its arms to its threshold.
-/
import K58.Frontier

namespace K58

/-- Every triangle-free colouring has, at every vertex, a table entry whose
planned degrees match the actual degrees after a colour permutation. -/
theorem exists_plan_matching (G : EdgeCol (Fin 58) 4) (h : TriangleFree G) (r : Fin 58) :
    ∃ x ∈ plans, ∃ σ : Equiv.Perm (Fin 4), ∀ a, deg G r (σ a) = plannedDegree x a := by
  obtain ⟨σ, hσ⟩ := root_degree_profile G h r
  have hmem : [deg G r (σ 0), deg G r (σ 1), deg G r (σ 2), deg G r (σ 3)]
      ∈ plans.map Plan.prof := by
    rw [← List.mem_eraseDups, planned_degree_profiles]
    exact hσ
  obtain ⟨x, hx, hxprof⟩ := List.mem_map.mp hmem
  refine ⟨x, hx, σ, fun a => ?_⟩
  fin_cases a <;> simp [plannedDegree, hxprof]

/-- At every balanced root of a triangle-free colouring of `K_58`, some entry of
the frozen table forces one of its arms to reach the planned threshold, and that
threshold is no larger than the arm. -/
theorem exists_plan_arm_reaches (G : EdgeCol (Fin 58) 4) (h : TriangleFree G)
    (r : Fin 58) (hr : w G r ≤ H G r) :
    ∃ x ∈ plans, ∃ σ : Equiv.Perm (Fin 4), ∃ a : Fin 4,
      plannedThreshold x a ≤ armSenders G r (σ a) ∧
      plannedThreshold x a ≤ plannedDegree x a := by
  obtain ⟨x, hx, σ, hprof⟩ := exists_plan_matching G h r
  obtain ⟨a, ha, hb⟩ := normalized_plan_arm_reaches G r hr σ x hx hprof
  exact ⟨x, hx, σ, a, ha, hb⟩

/-- Unconditionally: a triangle-free colouring of `K_58` has a root which
receives at least as many tickets as it sends, a table entry matching its
degrees, and an arm of that root at the planned threshold. -/
theorem root_plan_arm (G : EdgeCol (Fin 58) 4) (h : TriangleFree G) :
    ∃ r : Fin 58, w G r ≤ H G r ∧ ∃ x ∈ plans, ∃ σ : Equiv.Perm (Fin 4), ∃ a : Fin 4,
      plannedThreshold x a ≤ armSenders G r (σ a) := by
  obtain ⟨r, hr⟩ := exists_root G
  obtain ⟨x, hx, σ, a, ha, _⟩ := exists_plan_arm_reaches G h r hr
  exact ⟨r, hr, x, hx, σ, a, ha⟩

end K58
