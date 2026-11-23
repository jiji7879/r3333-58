import K58.RootSender

namespace K58

/-- Extend a permutation of the other three colours by fixing the distinguished arm. -/
private def extendPalette (a : Fin 4) (p : Equiv.Perm (Fin 3)) : Equiv.Perm (Fin 4) :=
  ((finSuccEquiv' a).trans p.optionCongr).trans (finSuccEquiv' a).symm

private theorem extendPalette_at (a : Fin 4) (p : Equiv.Perm (Fin 3)) :
    extendPalette a p a = a := by
  apply (finSuccEquiv' a).injective
  simp [extendPalette, Equiv.optionCongr_apply]

private theorem extendPalette_other (a : Fin 4) (p : Equiv.Perm (Fin 3)) (j : Fin 3) :
    extendPalette a p (a.succAbove j) = a.succAbove (p j) := by
  apply (finSuccEquiv' a).injective
  simp [extendPalette, Equiv.optionCongr_apply]

private theorem inducedPalette (π : Equiv.Perm (Fin 4)) (b : Fin 4) :
    ∃ p : Equiv.Perm (Fin 3), ∀ c, (π b).succAbove (p c) = π (b.succAbove c) := by
  let z : {x : Fin 4 // x ≠ b} ≃ {x : Fin 4 // x ≠ π b} :=
    π.subtypeEquiv (fun x => not_congr π.injective.eq_iff.symm)
  let p := ((finSuccAboveEquiv b).trans z).trans (finSuccAboveEquiv (π b)).symm
  exact ⟨p, fun c => congrArg Subtype.val
    ((finSuccAboveEquiv (π b)).apply_symm_apply (z (finSuccAboveEquiv b c)))⟩

/-- A change of coordinates in each arm, with one common host palette and one
permutation of the 58 labels. Template coherence is required on every critical arm. -/
structure RootSymmetry (i : Fin 41) where
  palette : Equiv.Perm (Fin 4)
  blocks : ∀ b : Fin 4, Fin (plannedDegree (indexedPlan i) b) ≃
    Fin (plannedDegree (indexedPlan i) (palette b))
  edges : ∀ b, 15 ≤ plannedDegree (indexedPlan i) b → ∀ u v, u ≠ v →
    (palette b).succAbove ((template _ (planTwisted (indexedPlan i) (palette b))).col
      (blocks b u) (blocks b v)) =
    palette (b.succAbove ((template _ (planTwisted (indexedPlan i) b)).col u v))

noncomputable def RootSymmetry.host {i : Fin 41} (S : RootSymmetry i) : Equiv.Perm (Fin 58) :=
  let slots := Equiv.ofBijective (slotLabel i) (slotLabel_bijective i)
  (slots.symm.trans (Equiv.sigmaCongr S.palette S.blocks).optionCongr).trans slots

theorem RootSymmetry.host_root {i : Fin 41} (S : RootSymmetry i) : S.host 0 = 0 := by
  let slots := Equiv.ofBijective (slotLabel i) (slotLabel_bijective i)
  change slots ((Equiv.sigmaCongr S.palette S.blocks).optionCongr (slots.symm (slots none))) = 0
  rw [slots.symm_apply_apply]
  rfl

theorem RootSymmetry.host_slot {i : Fin 41} (S : RootSymmetry i) (b : Fin 4) (u) :
    S.host (slotLabel i (some ⟨b,u⟩)) = slotLabel i (some ⟨S.palette b,S.blocks b u⟩) := by
  let slots := Equiv.ofBijective (slotLabel i) (slotLabel_bijective i)
  change slots ((Equiv.sigmaCongr S.palette S.blocks).optionCongr
    (slots.symm (slots (some ⟨b,u⟩)))) = _
  rw [slots.symm_apply_apply]
  rfl

private theorem castColour {m n : ℕ} (h : m = n) {t k : Bool} (ht : t = k) (x y : Fin m) :
    (template n k).col (finCongr h x) (finCongr h y) = (template m t).col x y := by
  subst n
  subst k
  rfl

private def planTag4 (P : Plan) (b : Fin 4) := (P.prof[b.val]?, P.kinds.toList[b.val]?)

private theorem liftUnmarkedBlock (i : Fin 41) (π : Equiv.Perm (Fin 4)) (b : Fin 4)
    (tag : planTag4 (indexedPlan i) (π b) = planTag4 (indexedPlan i) b) :
    ∃ f : Fin (plannedDegree (indexedPlan i) b) ≃ Fin (plannedDegree (indexedPlan i) (π b)),
      15 ≤ plannedDegree (indexedPlan i) b → ∀ u v, u ≠ v → (π b).succAbove
        ((template _ (planTwisted (indexedPlan i) (π b))).col (f u) (f v)) =
        π (b.succAbove ((template _ (planTwisted (indexedPlan i) b)).col u v)) := by
  let P := indexedPlan i
  let d := plannedDegree P
  have hd : d b = d (π b) := congrArg (fun z : Option ℕ × Option Char => z.1.getD 0) tag.symm
  have hk : planTwisted P b = planTwisted P (π b) :=
    congrArg (fun z : Option ℕ × Option Char => z.2 == some 'T') tag.symm
  obtain ⟨q, hq⟩ := inducedPalette π b
  by_cases crit : 15 ≤ d b
  · have cap : d b ≤ 16 := (by decide : ∀ (j : Fin 41) (c : Fin 4),
        plannedDegree (indexedPlan j) c ≤ 16) i b
    have realise {n : ℕ} (hn : n = 15 ∨ n = 16) (t : Bool) :
        ∃ h : Equiv.Perm (Fin n), ∀ u v, u ≠ v →
          (template n t).col (h u) (h v) = q ((template n t).col u v) := by
      rcases hn with rfl | rfl
      · exact palette_15 t q
      · obtain ⟨h, _, hh⟩ := palette_16_fixing t q 0
        exact ⟨h, hh⟩
    obtain ⟨h, hh⟩ := realise (n := d b) (by omega) (planTwisted P b)
    refine ⟨h.trans (finCongr hd), ?_⟩
    intro _ u v hne
    change (π b).succAbove ((template (d (π b)) (planTwisted P (π b))).col
      (finCongr hd (h u)) (finCongr hd (h v))) =
      π (b.succAbove ((template (d b) (planTwisted P b)).col u v))
    rw [castColour hd hk, hh _ _ hne, hq]
  · exact ⟨finCongr hd, fun h => (crit h).elim⟩

/-- A palette-augmented mark action extends across every other root block.
The resulting single host permutation sends the marked coordinate to y. -/
theorem marked_orbit_lifts (i : Fin 41) (a : Fin 4)
    (x y : Fin (plannedDegree (indexedPlan i) a))
    (orb : PositionOrbit (planTag (indexedPlan i) a) (planTwisted (indexedPlan i) a) x y) :
    ∃ S : RootSymmetry i, S.palette a = a ∧
      S.host (slotLabel i (some ⟨a,x⟩)) = slotLabel i (some ⟨a,y⟩) := by
  classical
  let P := indexedPlan i
  let d := plannedDegree P
  obtain ⟨p, htag, g, hxy, hg⟩ := orb
  let π := extendPalette a p
  have fix : π a = a := extendPalette_at _ _
  have tags (b : Fin 4) : (P.prof[(π b).val]?, P.kinds.toList[(π b).val]?) =
      (P.prof[b.val]?, P.kinds.toList[b.val]?) := by
    refine Fin.succAboveCases a ?_ (fun j => ?_) b
    · rw [fix]
    · rw [show π (a.succAbove j) = a.succAbove (p j) from extendPalette_other _ _ _]
      exact htag j
  have arms (b : Fin 4) : ∃ f : Fin (d b) ≃ Fin (d (π b)),
      (∀ z, b = a → z.val = x.val → (f z).val = y.val) ∧
      (15 ≤ d b → ∀ u v, u ≠ v → (π b).succAbove
        ((template _ (planTwisted P (π b))).col (f u) (f v)) =
        π (b.succAbove ((template _ (planTwisted P b)).col u v))) := by
    by_cases hb : b = a
    · subst b
      rw [fix]
      refine ⟨g, ?_, ?_⟩
      · intro z _ h
        exact congrArg Fin.val ((congrArg g (Fin.ext h)).trans hxy)
      · intro _ u v hne
        rw [hg _ _ hne]
        exact (extendPalette_other a p _).symm
    · obtain ⟨f, hf⟩ := liftUnmarkedBlock i π b (tags b)
      exact ⟨f, fun _ h' => (hb h').elim, hf⟩
  choose blocks hmark hedge using arms
  let S : RootSymmetry i := ⟨π, blocks, hedge⟩
  refine ⟨S, fix, ?_⟩
  rw [S.host_slot]
  apply congrArg (fun s : (b : Fin 4) × Fin (d b) => slotLabel i (some s))
  apply Sigma.ext fix
  have same {n m : ℕ} (h : n = m) (u : Fin n) (v : Fin m) (huv : u.val = v.val) : HEq u v := by
    subst m
    exact heq_of_eq (Fin.ext huv)
  exact same (congrArg d fix) _ _ (hmark a x rfl rfl)

/-- Change all four blocks together. An old slot carried to a new slot by S
continues to denote the same physical vertex in the new labelling. -/
noncomputable def RootLayout.relabel {G : EdgeCol (Fin 58) 4} {r : Fin 58} {i : Fin 41}
    {σ : Equiv.Perm (Fin 4)} (L : RootLayout G r i σ) (S : RootSymmetry i) :
    RootLayout G r i (S.palette.symm.trans σ) where
  host := S.host.symm.trans L.host
  root := by
    change L.host (S.host.symm 0) = r
    rw [S.host.symm_apply_eq.mpr S.host_root.symm, L.root]
  arms := by
    intro b x
    obtain ⟨c,rfl⟩ := S.palette.surjective b
    obtain ⟨z,rfl⟩ := (S.blocks c).surjective x
    rw [← S.host_slot]
    simpa only [Equiv.trans_apply, Equiv.symm_apply_apply] using L.arms c z
  templates := by
    intro b hc x y hxy
    obtain ⟨c,rfl⟩ := S.palette.surjective b
    obtain ⟨z,rfl⟩ := (S.blocks c).surjective x
    obtain ⟨w,rfl⟩ := (S.blocks c).surjective y
    have hz : z ≠ w := fun h => hxy (congrArg _ h)
    have hd : plannedDegree (indexedPlan i) c = plannedDegree (indexedPlan i) (S.palette c) := by
      simpa only [Fintype.card_fin] using Fintype.card_congr (S.blocks c)
    rw [← hd] at hc
    rw [← S.host_slot, ← S.host_slot, S.edges c hc z w hz]
    simpa only [Equiv.trans_apply, Equiv.symm_apply_apply] using L.templates c hc z w hz

private theorem free_mark_lifts (i : Fin 41) (a : Fin 4)
    (x y : Fin (plannedDegree (indexedPlan i) a)) (hfree : plannedDegree (indexedPlan i) a < 15) :
    ∃ S : RootSymmetry i, S.palette a = a ∧
      S.host (slotLabel i (some ⟨a,x⟩)) = slotLabel i (some ⟨a,y⟩) := by
  let block (b : Fin 4) : Equiv.Perm (Fin (plannedDegree (indexedPlan i) b)) :=
    if h : b = a then h ▸ Equiv.swap x y else Equiv.refl _
  let S : RootSymmetry i := {
    palette := Equiv.refl _
    blocks := block
    edges := by
      intro b hb u v huv
      have hba : b ≠ a := fun h => (Nat.not_le_of_gt hfree) (h ▸ hb)
      change b.succAbove ((template _ _).col (block b u) (block b v)) = _
      simp only [block, dif_neg hba, Equiv.refl_apply] }
  refine ⟨S, rfl, ?_⟩
  rw [S.host_slot]
  change slotLabel i (some ⟨a,block a x⟩) = _
  simp [block]

/-- The first arm of the same size and kind is the arm stored in the ledger. -/
def canonicalArm (i : Fin 41) (a : Fin 4) : Fin 4 :=
  ((List.finRange 4).find? fun b => planTag4 (indexedPlan i) b == planTag4 (indexedPlan i) a).getD a

theorem canonicalArm_ok : ∀ (i : Fin 41) (a : Fin 4),
    let b := canonicalArm i a
    canonicalArm i b = b ∧ plannedThreshold (indexedPlan i) b = plannedThreshold (indexedPlan i) a ∧
    ∀ c, planTag4 (indexedPlan i) (Equiv.swap a b c) = planTag4 (indexedPlan i) c := by decide

private theorem canonical_reached_layout (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G) :
    ∃ r, w G r ≤ H G r ∧ ∃ (i : Fin 41) (σ : Equiv.Perm (Fin 4)) (_ : RootLayout G r i σ)
      (b : Fin 4), canonicalArm i b = b ∧ plannedThreshold (indexedPlan i) b ≤ armSenders G r (σ b) := by
  obtain ⟨r, hr, i, σ, ⟨L⟩, a, ha⟩ := exists_root_layout G hG
  let b := canonicalArm i a
  let π := Equiv.swap a b
  obtain ⟨hb, hth, htags⟩ := canonicalArm_ok i a
  have lifts (c : Fin 4) := liftUnmarkedBlock i π c (htags c)
  choose blocks hedge using lifts
  let S : RootSymmetry i := ⟨π, blocks, hedge⟩
  refine ⟨r, hr, i, S.palette.symm.trans σ, L.relabel S, b, hb, ?_⟩
  change plannedThreshold (indexedPlan i) b ≤ armSenders G r (σ ((Equiv.swap a b).symm b))
  change plannedThreshold (indexedPlan i) b = plannedThreshold (indexedPlan i) a at hth
  simpa only [hth, Equiv.symm_swap, Equiv.swap_apply_right] using ha

/-- The selected sender actually occupies a retained coordinate in a single
global root layout and still has a second pinned block in that palette. -/
theorem root_layout_at_retained_mark (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G) :
    ∃ r, w G r ≤ H G r ∧ ∃ (i : Fin 41) (σ : Equiv.Perm (Fin 4))
      (L : RootLayout G r i σ) (a : Fin 4) (y : Fin (plannedDegree (indexedPlan i) a)),
      let q := L.host (slotLabel i (some ⟨a,y⟩))
      canonicalArm i a = a ∧ plannedThreshold (indexedPlan i) a ≤ armSenders G r (σ a) ∧
        y.val ∈ ledgerMarks i a ∧ Sends G q r ∧ r ∈ arm G q (σ a) ∧
        (deg G q (σ a) = 15 ∨ deg G q (σ a) = 16) ∧ ∃ t, PlanPin G q σ a (deg G q (σ a)) t := by
  obtain ⟨r, hr, i, σ, L, a, hcanonical, ht⟩ := canonical_reached_layout G hG
  obtain ⟨x, y, hs, hym, horb⟩ := reached_layout_sender L a ht
  let q₀ := ((L.armEquiv a) x).val
  obtain ⟨hne₀, hcol₀⟩ := (Finset.mem_filter.mp ((L.armEquiv a) x).property).2
  have hrev : G.col q₀ r = σ a := (G.symm q₀ r).trans hcol₀
  have hmem : r ∈ arm G q₀ (σ a) :=
    Finset.mem_filter.mpr ⟨Finset.mem_univ _, hne₀.symm, hrev⟩
  have hlo : 15 ≤ deg G q₀ (σ a) := hrev ▸ hs.2
  have hhi := deg_le_sixteen G hG q₀ (σ a)
  have hd : deg G q₀ (σ a) = 15 ∨ deg G q₀ (σ a) = 16 := by omega
  have lifted : ∃ S : RootSymmetry i, S.palette a = a ∧
      S.host (slotLabel i (some ⟨a,x⟩)) = slotLabel i (some ⟨a,y⟩) := by
    by_cases h : 15 ≤ plannedDegree (indexedPlan i) a
    · exact marked_orbit_lifts i a x y (horb h)
    · exact free_mark_lifts i a x y (by omega)
  obtain ⟨S, hfix, hxy⟩ := lifted
  let τ := S.palette.symm.trans σ
  let M := L.relabel S
  have hA : τ a = σ a := congrArg σ (S.palette.symm_apply_eq.mpr hfix.symm)
  let q := M.host (slotLabel i (some ⟨a,y⟩))
  have hq : q = ((L.armEquiv a) x).val := by
    change L.host (S.host.symm (slotLabel i (some ⟨a,y⟩))) = L.host (slotLabel i (some ⟨a,x⟩))
    rw [← hxy, S.host.symm_apply_apply]
  have hd' : deg G q (τ a) = 15 ∨ deg G q (τ a) = 16 := by simpa only [hq, hA] using hd
  obtain ⟨t, hp⟩ := critical_arm_pinned G hG q (τ a) hd'
  refine ⟨r, hr, i, τ, M, a, y, hcanonical, ?_, hym, ?_, ?_, hd', t, pin_in_global_palette G q τ a _ t hd' hp⟩
  · simpa only [hA] using ht
  · change Sends G q r
    simpa only [hq] using hs
  · change r ∈ arm G q (τ a)
    simpa only [hq, hA] using hmem

end K58
