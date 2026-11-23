import K58.KindPlan

namespace K58

/-- Coordinates in the four blocks use one global map from plan colours to host colours. -/
def PlanPin (G : EdgeCol (Fin 58) 4) (r : Fin 58) (σ : Equiv.Perm (Fin 4))
    (a : Fin 4) (n : ℕ) (t : Bool) : Prop :=
  ∃ e : ↥(arm G r (σ a)) ≃ Fin n, ∀ x y, x ≠ y →
    G.col x.val y.val = σ (a.succAbove ((template n t).col (e x) (e y)))

theorem pin_in_global_palette (G : EdgeCol (Fin 58) 4) (r : Fin 58)
    (σ : Equiv.Perm (Fin 4)) (a : Fin 4) (n : ℕ) (t : Bool) (hn : n = 15 ∨ n = 16)
    (hp : PinnedArm G r (σ a) n t) : PlanPin G r σ a n t := by
  let res : {x : Fin 4 // x ≠ σ a} ≃ {x : Fin 4 // x ≠ a} :=
    σ.symm.subtypeEquiv (fun x => not_congr σ.symm_apply_eq.symm)
  let p := ((finSuccAboveEquiv (σ a)).trans res).trans (finSuccAboveEquiv a).symm
  have comm (c : Fin 3) : σ (a.succAbove (p c)) = (σ a).succAbove c := by
    have h := congrArg Subtype.val
      ((finSuccAboveEquiv a).apply_symm_apply (res (finSuccAboveEquiv (σ a) c)))
    change a.succAbove (p c) = σ.symm ((σ a).succAbove c) at h
    exact σ.eq_symm_apply.mp h
  have lift : ∃ g : Equiv.Perm (Fin n), ∀ i j, i ≠ j →
      (template n t).col (g i) (g j) = p ((template n t).col i j) := by
    rcases hn with rfl | rfl
    · exact palette_15 t p
    · obtain ⟨g, _, hg⟩ := palette_16_fixing t p 0
      exact ⟨g, hg⟩
  obtain ⟨g, hg⟩ := lift
  obtain ⟨e, he⟩ := hp
  refine ⟨e.trans g, ?_⟩
  intro x y hxy
  simpa only [Equiv.trans_apply, hg _ _ (e.injective.ne hxy), comm] using he x y hxy

/-- One balanced root, one globally named plan, and one reached threshold. The
pins on all critical arms interpret template colours through the same host palette. -/
theorem root_plan_in_global_palette (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G) :
    ∃ r, w G r ≤ H G r ∧ ∃ P ∈ plans, ∃ σ : Equiv.Perm (Fin 4),
      (∀ a, deg G r (σ a) = plannedDegree P a) ∧
      (∀ a, 15 ≤ plannedDegree P a → ∃ t : Bool,
        P.kinds.toList[a.val]? = some (if t then 'T' else 'U') ∧
        PlanPin G r σ a (plannedDegree P a) t) ∧
      ∃ a, plannedThreshold P a ≤ armSenders G r (σ a) := by
  obtain ⟨r, hr, P, hP, σ, hd, hp, ha⟩ := root_plan_with_kinds G hG
  refine ⟨r, hr, P, hP, σ, hd, ?_, ha⟩
  intro a hlo
  obtain ⟨t, hkind, hpin⟩ := hp a hlo
  have hhi := deg_le_sixteen G hG r (σ a)
  rw [hd] at hhi
  exact ⟨t, hkind, pin_in_global_palette G r σ a _ t (by omega) hpin⟩

end K58
