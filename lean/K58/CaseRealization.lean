import K58.RootLayout
import K58.Ledger

namespace K58

def caseMark (C : ExpandedCase) : Fin 58 :=
  slotLabel C.key.planIndex (some ⟨C.key.arm, ⟨C.key.markPosition, C.mark_in_range⟩⟩)

/-- The pinned sender neighbourhood in the *same* coordinates as the normalized
root. The equivalence records every neighbour and all internal template edges. -/
structure AttachedBlock (G : EdgeCol (Fin 58) 4) (C : ExpandedCase)
    (r : Fin 58) (σ : Equiv.Perm (Fin 4)) (L : RootLayout G r C.key.planIndex σ) where
  localEquiv : ↥(arm G (L.host (caseMark C)) (σ C.key.arm)) ≃ Fin C.key.secondSize
  labels : ∀ x, (localEquiv.symm x).val = L.host (C.marked x)
  edges : ∀ x y, x ≠ y → G.col x.val y.val = σ (C.key.arm.succAbove
    ((template _ C.key.secondTwisted).col (localEquiv x) (localEquiv y)))

private def UnitHolds (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58))
    (σ : Equiv.Perm (Fin 4)) (u : ColourUnit) : Prop :=
  ∃ i j : Fin 58, i.val = u.u ∧ j.val = u.v ∧ i ≠ j ∧
    (G.col (e i) (e j) = σ u.colour ↔ u.positive = true)

private theorem edge_holds (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58))
    (σ : Equiv.Perm (Fin 4)) (x y : Fin 58) (hxy : x ≠ y) (c : Fin 4) (pos : Bool)
    (h : G.col (e x) (e y) = σ c ↔ pos = true) :
    UnitHolds G e σ (ColourUnit.ofEdge x.val y.val c pos) := by
  rcases le_total x.val y.val with hle | hle
  · exact ⟨x, y, (min_eq_left hle).symm, (max_eq_right hle).symm, hxy, h⟩
  · refine ⟨y, x, (min_eq_right hle).symm, (max_eq_left hle).symm, hxy.symm, ?_⟩
    simpa only [ColourUnit.ofEdge, G.symm (e y) (e x)] using h

private theorem block_holds (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58))
    (σ : Equiv.Perm (Fin 4)) {n : ℕ} (f : Fin n → Fin 58) (hf : Function.Injective f)
    (t : Bool) (a : Fin 4)
    (he : ∀ x y, x ≠ y → G.col (e (f x)) (e (f y)) = σ (a.succAbove ((template n t).col x y))) :
    ∀ u ∈ blockUnits (fun x => (f x).val) t a, UnitHolds G e σ u := by
  intro u hu
  obtain ⟨x, _, hx⟩ := List.mem_flatMap.mp hu
  obtain ⟨y, hy, rfl⟩ := List.mem_map.mp hx
  have hxy := of_decide_eq_true (List.mem_filter.mp hy).2
  exact edge_holds G e σ _ _ (hf.ne hxy.ne) _ true (by simp [he x y hxy.ne])

set_option maxRecDepth 20000 in
private theorem kinds_critical : ∀ (i : Fin 41) (a : Fin 4),
    (indexedPlan i).kinds.toList[a.val]? = some 'T' ∨
    (indexedPlan i).kinds.toList[a.val]? = some 'U' → 15 ≤ plannedDegree (indexedPlan i) a := by
  decide

/-- Compatible root and sender coordinates suffice for every signed unit,
including the negative sender-star units. -/
theorem attached_block_realizes (G : EdgeCol (Fin 58) 4) (C : ExpandedCase) (r : Fin 58)
    (σ : Equiv.Perm (Fin 4)) (L : RootLayout G r C.key.planIndex σ)
    (D : AttachedBlock G C r σ L) : RealizesCase G C := by
  let k := C.key
  let v (a : Fin 4) (x : Fin (plannedDegree k.plan a)) := slotLabel k.planIndex (some ⟨a,x⟩)
  have val (a x) : (v a x).val = blockLabel k.plan a x.val := slotLabel_val _ _ _
  have qval : (caseMark C).val = blockLabel k.plan k.arm k.markPosition := slotLabel_val _ _ _
  have blockinj (a) : Function.Injective (v a) := by
    intro x y h
    have he := (slotLabel_bijective k.planIndex).1 h
    exact (Sigma.mk.inj_iff.mp (Option.some.inj he)).2 |> eq_of_heq
  have star (w : Fin 58) (hw : w ≠ caseMark C) :
      G.col (L.host (caseMark C)) (L.host w) = σ k.arm ↔ ∃ i, C.marked i = w := by
    constructor
    · intro h
      let z : ↥(arm G (L.host (caseMark C)) (σ k.arm)) :=
        ⟨L.host w, Finset.mem_filter.mpr ⟨Finset.mem_univ _, L.host.injective.ne hw, h⟩⟩
      refine ⟨D.localEquiv z, L.host.injective ?_⟩
      rw [← D.labels, D.localEquiv.symm_apply_apply]
    · rintro ⟨i, rfl⟩
      have h := (Finset.mem_filter.mp (D.localEquiv.symm i).property).2.2
      rwa [D.labels] at h
  refine ⟨L.host, σ, ?_⟩
  intro u hu
  change UnitHolds G L.host σ u
  simp only [caseUnits, caseUnitList, rootUnitList, starUnitList, List.mem_toFinset, List.mem_append] at hu
  rcases hu with ((h | h) | h) | h
  · obtain ⟨a, _, h⟩ := List.mem_flatMap.mp h
    obtain ⟨j, hj, rfl⟩ := List.mem_map.mp h
    let x : Fin (plannedDegree k.plan a) := ⟨j, List.mem_range.mp hj⟩
    have hv := L.arms a x
    obtain ⟨hne, hedge⟩ := (Finset.mem_filter.mp hv).2
    have hn : (0 : Fin 58) ≠ v a x := fun h => hne ((congrArg L.host h).symm.trans L.root)
    have hcol : G.col (L.host 0) (L.host (v a x)) = σ a := by rw [L.root]; exact hedge
    have hh := edge_holds G L.host σ 0 (v a x) hn a true (by simp [hcol])
    simpa only [val, Fin.val_zero, x, k] using hh
  · obtain ⟨a, _, h⟩ := List.mem_flatMap.mp h
    have go (t : Bool) (htag : k.plan.kinds.toList[a.val]? = some (if t then 'T' else 'U'))
        (hh : u ∈ blockUnits (fun x : Fin (plannedDegree k.plan a) => blockLabel k.plan a x.val) t a) :
        UnitHolds G L.host σ u := by
      have hc : 15 ≤ plannedDegree k.plan a := by
        apply kinds_critical k.planIndex a
        cases t
        · exact Or.inr htag
        · exact Or.inl htag
      have ht : planTwisted k.plan a = t := by cases t <;> simp [planTwisted, htag]
      have hem := L.templates a hc
      change ∀ x y, x ≠ y → G.col (L.host (v a x)) (L.host (v a y)) =
        σ (a.succAbove ((template _ (planTwisted k.plan a)).col x y)) at hem
      rw [ht] at hem
      exact block_holds G L.host σ (v a) (blockinj a) t a hem u (by simpa only [val] using hh)
    split at h
    next htag => exact go false htag h
    next htag => exact go true htag h
    next => simp at h
  · apply block_holds G L.host σ C.marked C.marked_injective k.secondTwisted k.arm _ u h
    intro x y hxy
    simpa only [D.labels, D.localEquiv.apply_symm_apply] using D.edges
      (D.localEquiv.symm x) (D.localEquiv.symm y) (D.localEquiv.symm.injective.ne hxy)
  · obtain ⟨j, hj, rfl⟩ := List.mem_map.mp h
    obtain ⟨hj, hne⟩ := List.mem_filter.mp hj
    let w : Fin 58 := ⟨j, List.mem_range.mp hj⟩
    have hn : w ≠ caseMark C := by
      intro h
      have h' := (congrArg Fin.val h).trans qval
      simp [w] at h'
      have both : j ≠ 0 ∧ j ≠ blockLabel k.plan k.arm k.markPosition := by
        simpa using hne
      exact both.2 h'
    have hh := edge_holds G L.host σ (caseMark C) w hn.symm k.arm
      ((List.finRange k.secondSize).any fun i => (C.marked i).val == j) (by
        rw [star w hn]
        simp only [List.any_eq_true, List.mem_finRange, true_and, beq_iff_eq]
        exact exists_congr fun i => Fin.ext_iff)
    simpa only [qval] using hh

/-- Apply the same host permutation and the same palette permutation to a signed
unit. Endpoint sorting uses the convention of the frozen case generator. -/
def ColourUnit.relabel (u : ColourUnit) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) :
    ColourUnit :=
  ColourUnit.ofEdge (e (Fin.ofNat 58 u.u)).val (e (Fin.ofNat 58 u.v)).val
    (p u.colour) u.positive

/-- A finite certificate can verify a placement quotient by comparing unit sets
under explicit permutations of 58 labels and four colour names. -/
def UnitTransport (A B : ExpandedCase) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) : Prop :=
  (caseUnits A).image (fun u => u.relabel e p) = caseUnits B

theorem realizes_of_unitTransport {G : EdgeCol (Fin 58) 4} {A B : ExpandedCase}
    {e : Equiv.Perm (Fin 58)} {p : Equiv.Perm (Fin 4)}
    (h : UnitTransport A B e p) (hA : RealizesCase G A) : RealizesCase G B := by
  obtain ⟨l, σ, hs⟩ := hA
  refine ⟨e.symm.trans l, p.symm.trans σ, ?_⟩
  intro u hu
  rw [← h] at hu
  obtain ⟨v, hv, rfl⟩ := Finset.mem_image.mp hu
  obtain ⟨x, y, hx, hy, hxy, he⟩ := hs v hv
  have fval (z : Fin 58) : Fin.ofNat 58 z.val = z := Fin.ext (Nat.mod_eq_of_lt z.isLt)
  change UnitHolds G (e.symm.trans l) (p.symm.trans σ) (v.relabel e p)
  unfold ColourUnit.relabel
  rw [← hx, ← hy, fval, fval]
  apply edge_holds G _ _ _ _ (e.injective.ne hxy)
  simpa only [Equiv.trans_apply, Equiv.symm_apply_apply] using he

/-- The remaining global choice of compatible coordinates for a retained key. -/
def LedgerAttachmentCover : Prop :=
  ∀ G : EdgeCol (Fin 58) 4, TriangleFree G →
    ∃ k ∈ frozenKeys, ∃ C, expandKey k = some C ∧
      ∃ (r : Fin 58) (σ : Equiv.Perm (Fin 4)) (L : RootLayout G r C.key.planIndex σ),
        Nonempty (AttachedBlock G C r σ L)

theorem frozenCover_of_attachments (h : LedgerAttachmentCover) : FrozenCover := by
  intro G hG
  obtain ⟨k, hk, C, hC, r, σ, L, ⟨D⟩⟩ := h G hG
  exact ⟨k, hk, C, hC, attached_block_realizes G C r σ L D⟩

end K58
