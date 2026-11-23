import K58.RootPalette
import K58.Cases

namespace K58

def indexedPlan (i : Fin 41) : Plan := plans[i.val]'(by exact i.isLt)

/-- Source coordinates for a vertex, with a separate coordinate for the root. -/
abbrev RootSlot (i : Fin 41) := Option ((a : Fin 4) × Fin (plannedDegree (indexedPlan i) a))

def slotLabel (i : Fin 41) : RootSlot i → Fin 58
  | none => 0
  | some ⟨a,x⟩ => Fin.ofNat 58 (blockLabel (indexedPlan i) a x.val)

private def rootSlots (i : Fin 41) : List (RootSlot i) :=
  none :: (List.finRange 4).flatMap fun a =>
    (List.finRange (plannedDegree (indexedPlan i) a)).map fun x => some ⟨a,x⟩

private theorem mem_rootSlots (i : Fin 41) (x : RootSlot i) : x ∈ rootSlots i := by
  cases x with
  | none => exact List.mem_cons_self
  | some x =>
    obtain ⟨a,x⟩ := x
    exact List.mem_cons_of_mem _ (List.mem_flatMap.mpr
      ⟨a,List.mem_finRange _,List.mem_map.mpr ⟨x,List.mem_finRange _,rfl⟩⟩)

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
private theorem slotLabels_ordered : ∀ i : Fin 41,
    (rootSlots i).map (slotLabel i) = List.finRange 58 := by decide +kernel

theorem slotLabel_bijective : ∀ i : Fin 41, Function.Bijective (slotLabel i) := by
  intro i
  have nodup : ((rootSlots i).map (slotLabel i)).Nodup :=
    (slotLabels_ordered i) ▸ List.nodup_finRange 58
  constructor
  · intro x y h
    exact List.inj_on_of_nodup_map nodup (mem_rootSlots i x) (mem_rootSlots i y) h
  · intro y
    have hy : y ∈ (rootSlots i).map (slotLabel i) := (slotLabels_ordered i) ▸ List.mem_finRange y
    obtain ⟨x,_,hx⟩ := List.mem_map.mp hy
    exact ⟨x,hx⟩

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem slotLabel_val : ∀ (i : Fin 41) (a : Fin 4) (x : Fin (plannedDegree (indexedPlan i) a)),
    (slotLabel i (some ⟨a,x⟩)).val = blockLabel (indexedPlan i) a x.val := by decide +kernel

def planTwisted (P : Plan) (a : Fin 4) := P.kinds.toList[a.val]? == some 'T'

/-- A single permutation of all 58 vertices puts the root, its four blocks,
and the edges of every critical arm into the frozen plan's coordinate system. -/
structure RootLayout (G : EdgeCol (Fin 58) 4) (r : Fin 58) (i : Fin 41)
    (σ : Equiv.Perm (Fin 4)) where
  host : Equiv.Perm (Fin 58)
  root : host 0 = r
  arms : ∀ (a : Fin 4) (x : Fin (plannedDegree (indexedPlan i) a)),
    host (slotLabel i (some ⟨a,x⟩)) ∈ arm G r (σ a)
  templates : ∀ (a : Fin 4), 15 ≤ plannedDegree (indexedPlan i) a →
    ∀ x y : Fin (plannedDegree (indexedPlan i) a), x ≠ y →
    G.col (host (slotLabel i (some ⟨a,x⟩))) (host (slotLabel i (some ⟨a,y⟩))) =
      σ (a.succAbove ((template _ (planTwisted (indexedPlan i) a)).col x y))

/-- Normalize the entire root at once, retaining the threshold for the same arm. -/
theorem exists_root_layout (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G) :
    ∃ r, w G r ≤ H G r ∧ ∃ (i : Fin 41) (σ : Equiv.Perm (Fin 4)),
      Nonempty (RootLayout G r i σ) ∧
      ∃ a, plannedThreshold (indexedPlan i) a ≤ armSenders G r (σ a) := by
  classical
  obtain ⟨r, hr, P, hP, σ, hd, hp, ha⟩ := root_plan_in_global_palette G hG
  obtain ⟨i, hi⟩ := List.mem_iff_get.mp hP
  let k : Fin 41 := i
  change indexedPlan k = P at hi
  subst P
  have localMaps (a : Fin 4) : ∃ e : ↥(arm G r (σ a)) ≃ Fin (plannedDegree (indexedPlan k) a),
      15 ≤ plannedDegree (indexedPlan k) a → ∀ x y, x ≠ y →
        G.col x.val y.val = σ (a.succAbove
          ((template _ (planTwisted (indexedPlan k) a)).col (e x) (e y))) := by
    by_cases h : 15 ≤ plannedDegree (indexedPlan k) a
    · obtain ⟨t, hk, e, he⟩ := hp a h
      have ht : planTwisted (indexedPlan k) a = t := by cases t <;> simp [planTwisted, hk]
      exact ⟨e, fun _ => ht ▸ he⟩
    · exact ⟨Fintype.equivFinOfCardEq ((Fintype.card_coe _).trans (hd a)),
        fun h' => (h h').elim⟩
  choose labels hlabel using localMaps
  let vertex : RootSlot k → Fin 58
    | none => r
    | some ⟨a,x⟩ => ((labels a).symm x).val
  have prop (a : Fin 4) (x) := (Finset.mem_filter.mp ((labels a).symm x).property).2
  have inj : Function.Injective vertex := by
    intro s t h
    cases s with
    | none =>
      cases t with
      | none => rfl
      | some z => exact ((prop z.1 z.2).1 h.symm).elim
    | some z =>
      cases t with
      | none => exact ((prop z.1 z.2).1 h).elim
      | some w =>
        obtain ⟨a,x⟩ := z
        obtain ⟨b,y⟩ := w
        change ((labels a).symm x).val = ((labels b).symm y).val at h
        have hab := σ.injective (((prop a x).2).symm.trans
          ((congrArg (G.col r) h).trans (prop b y).2))
        subst b
        have hxy := (labels a).symm.injective (Subtype.ext h)
        subst y
        rfl
  let pack := Equiv.ofBijective (slotLabel k) (slotLabel_bijective k)
  have bv : Function.Bijective vertex := by
    apply (Fintype.bijective_iff_injective_and_card _).mpr
    exact ⟨inj, Fintype.card_congr pack⟩
  let host := pack.symm.trans (Equiv.ofBijective vertex bv)
  have eval (s : RootSlot k) : host (slotLabel k s) = vertex s := by
    change vertex (pack.symm (pack s)) = vertex s
    rw [pack.symm_apply_apply]
  refine ⟨r, hr, k, σ, ⟨⟨host, eval none, ?_, ?_⟩⟩, ha⟩
  · intro a x
    rw [eval]
    exact ((labels a).symm x).property
  · intro a h x y hxy
    rw [eval, eval]
    simpa only [vertex, Equiv.apply_symm_apply] using hlabel a h
      ((labels a).symm x) ((labels a).symm y) ((labels a).symm.injective.ne hxy)

end K58
