import K58.RootLayout
import K58.MarkBreadth

namespace K58

variable {G : EdgeCol (Fin 58) 4} {r : Fin 58} {i : Fin 41} {σ : Equiv.Perm (Fin 4)}

/-- The coordinates of a normalized arm enumerate exactly its vertices. -/
noncomputable def RootLayout.armEquiv (L : RootLayout G r i σ) (a : Fin 4) :
    Fin (plannedDegree (indexedPlan i) a) ≃ ↥(arm G r (σ a)) := by
  let f := fun x : Fin (plannedDegree (indexedPlan i) a) =>
    (⟨L.host (slotLabel i (some ⟨a,x⟩)), L.arms a x⟩ : ↥(arm G r (σ a)))
  apply Equiv.ofBijective f
  constructor
  · intro x y h
    have he := (slotLabel_bijective i).1 (L.host.injective (congrArg Subtype.val h))
    exact eq_of_heq (Sigma.mk.inj_iff.mp (Option.some.inj he)).2
  · intro y
    obtain ⟨v, hv⟩ := L.host.surjective y.val
    obtain ⟨s, rfl⟩ := (slotLabel_bijective i).2 v
    obtain ⟨hy, hc⟩ := (Finset.mem_filter.mp y.property).2
    cases s with
    | none => exact (hy (hv.symm.trans L.root)).elim
    | some z =>
      obtain ⟨b,x⟩ := z
      have he := (Finset.mem_filter.mp (L.arms b x)).2.2
      rw [hv] at he
      have hab := σ.injective (he.symm.trans hc)
      subst b
      exact ⟨x, Subtype.ext hv⟩

private theorem threshold_positive : ∀ (i : Fin 41) (a : Fin 4),
    0 < plannedThreshold (indexedPlan i) a := by decide

private theorem orbit_cast {n : ℕ} (hn : n = 15) (tag : Fin 3 → Option ℕ × Option Char)
    (t : Bool) (x y : Fin n) :
    PositionOrbit tag t ((finCongr hn) x) ((finCongr hn) y) → PositionOrbit tag t x y := by
  subst n
  exact id

/-- A sender in the coordinates of the single normalized root can be moved to
a retained mark by an allowed orbit action on a critical arm. On a free arm
the vertex labels can be permuted arbitrarily. -/
theorem reached_layout_sender (L : RootLayout G r i σ) (a : Fin 4)
    (ht : plannedThreshold (indexedPlan i) a ≤ armSenders G r (σ a)) :
    ∃ x y : Fin (plannedDegree (indexedPlan i) a), Sends G ((L.armEquiv a) x).val r ∧
      y.val ∈ ledgerMarks i a ∧ (15 ≤ plannedDegree (indexedPlan i) a →
        PositionOrbit (planTag (indexedPlan i) a) (planTwisted (indexedPlan i) a) x y) := by
  let P := indexedPlan i
  let d := plannedDegree P a
  let e := L.armEquiv a
  have hd : deg G r (σ a) = d :=
    (Fintype.card_coe (arm G r (σ a))).symm.trans ((Fintype.card_congr e.symm).trans (Fintype.card_fin _))
  have hfeas := ht.trans (arm_senders_le_deg G r (σ a))
  rw [hd] at hfeas
  by_cases h15 : d = 15
  · let f := e.symm.trans (finCongr h15)
    obtain ⟨q, hs, y, hym, hy⟩ := reached15_has_retained_mark i a G r (σ a) f P rfl h15 hd ht
    let x := e.symm q
    let z := (finCongr h15).symm y
    refine ⟨x, z, ?_, hym, fun _ => orbit_cast h15 _ _ x z ?_⟩
    · simpa only [x, e, Equiv.apply_symm_apply] using hs
    · simpa only [f, z, x, P, planTwisted, Equiv.trans_apply, Equiv.apply_symm_apply] using hy
  · have hmark : (0 : ℕ) ∈ ledgerMarks i a := by
      by_contra hz
      have h := ledger_mark_breadth i a hfeas
      change d - plannedThreshold P a + 1 ≤ markBreadth P a (ledgerMarks i a) at h
      simp only [markBreadth, show plannedDegree P a ≠ 15 from h15, if_false, hz] at h
      omega
    have hdpos : 0 < d := lt_of_lt_of_le (threshold_positive i a) hfeas
    have hp : 0 < plannedThreshold P a := threshold_positive i a
    have hpdeg : plannedThreshold P a ≤ deg G r (σ a) := ht.trans (arm_senders_le_deg G r (σ a))
    obtain ⟨q, hq, hs⟩ := marked_sender G r (σ a) (plannedThreshold P a) (arm G r (σ a))
      (by rfl) (by change deg G r (σ a) - plannedThreshold P a + 1 ≤ deg G r (σ a); omega) ht
    let x := e.symm ⟨q,hq⟩
    let y : Fin d := ⟨0,hdpos⟩
    refine ⟨x, y, ?_, hmark, ?_⟩
    · simpa only [x, e, Equiv.apply_symm_apply] using hs
    · intro hlo
      have of16 {n : ℕ} (hn : n = 16) (t : Bool) (u v : Fin n) :
          PositionOrbit (planTag P a) t u v := by
        subst n
        exact positionOrbit16_all _ _ _ _
      have hbound : d ≤ 16 := by
        change plannedDegree (indexedPlan i) a ≤ 16
        exact (by decide : ∀ (j : Fin 41) (b : Fin 4), plannedDegree (indexedPlan j) b ≤ 16) i a
      change 15 ≤ d at hlo
      have h16 : d = 16 := by omega
      exact of16 h16 _ x y

/-- Combined root and sender selection before the three placements are aligned.
The sender's second pinned block uses the same global palette as the root. -/
theorem root_layout_marked_block (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G) :
    ∃ r, w G r ≤ H G r ∧ ∃ (i : Fin 41) (σ : Equiv.Perm (Fin 4))
      (L : RootLayout G r i σ) (a : Fin 4),
      plannedThreshold (indexedPlan i) a ≤ armSenders G r (σ a) ∧
      ∃ x y : Fin (plannedDegree (indexedPlan i) a),
        let q := ((L.armEquiv a) x).val
        Sends G q r ∧ y.val ∈ ledgerMarks i a ∧
          (15 ≤ plannedDegree (indexedPlan i) a →
            PositionOrbit (planTag (indexedPlan i) a) (planTwisted (indexedPlan i) a) x y) ∧
          r ∈ arm G q (σ a) ∧ (deg G q (σ a) = 15 ∨ deg G q (σ a) = 16) ∧
          ∃ t, PlanPin G q σ a (deg G q (σ a)) t := by
  obtain ⟨r, hr, i, σ, ⟨L⟩, a, ht⟩ := exists_root_layout G hG
  obtain ⟨x, y, hs, hm, horbit⟩ := reached_layout_sender L a ht
  let q := ((L.armEquiv a) x).val
  have hmem := ((L.armEquiv a) x).property
  obtain ⟨hqr, hcol⟩ := (Finset.mem_filter.mp hmem).2
  have hrev : G.col q r = σ a := (G.symm q r).trans hcol
  have hlo : 15 ≤ deg G q (σ a) := hrev ▸ hs.2
  have cap := deg_le_sixteen G hG q (σ a)
  have hd : deg G q (σ a) = 15 ∨ deg G q (σ a) = 16 := by omega
  obtain ⟨t, hpin⟩ := critical_arm_pinned G hG q (σ a) hd
  exact ⟨r, hr, i, σ, L, a, ht, x, y, hs, hm, horbit,
    Finset.mem_filter.mpr ⟨Finset.mem_univ _, hqr.symm, hrev⟩, hd, t,
    pin_in_global_palette G q σ a _ t hd hpin⟩

end K58
