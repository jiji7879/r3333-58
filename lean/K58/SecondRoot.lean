import K58.RawCover
import K58.RootRelabel

namespace K58

private theorem secondRootMap (s t : Bool) (x : Fin (if s then 16 else 15)) :
    ∃ g : Equiv.Perm (Fin (if s then 16 else 15)),
      (g x).val ∈ (if s then [0] else secondRoots15 t) ∧ ∀ i j, i ≠ j →
        (template _ t).col (g i) (g j) = (template _ t).col i j := by
  cases s with
  | false =>
    have table : ∀ (t : Bool) (x : Fin 15), ∃ g ∈ named15 t, (g x).val ∈ secondRoots15 t := by decide
    obtain ⟨g, hg, hx⟩ := table t x
    rw [named15_exact] at hg
    obtain ⟨hb, he⟩ := (PositionSearch.mem_automorphisms_iff _ _).mp hg
    exact ⟨Equiv.ofBijective g hb, hx, he⟩
  | true =>
    obtain ⟨p, hp, g, hx, he⟩ := positionOrbit16_all (id : Fin 3 → Fin 3) t x 0
    refine ⟨g, by simp [hx], ?_⟩
    intro i j hij
    exact (he i j hij).trans (hp _)

private theorem first_has_no_predecessor : ∀ (i : Fin 41) (a : Fin 4), canonicalArm i a = a →
    ((List.finRange 4).any (fun b => decide (b < a ∧
      plannedDegree (indexedPlan i) a = plannedDegree (indexedPlan i) b ∧
      (indexedPlan i).kinds.toList[a.val]? = (indexedPlan i).kinds.toList[b.val]?))) = false := by decide

private theorem family_mem (i : Fin 41) (a : Fin 4) (m : ℕ) (s t : Bool) (r : ℕ)
    (ha : canonicalArm i a = a) (hm : m ∈ ledgerMarks i a)
    (hr : r ∈ (if s then [0] else secondRoots15 t)) :
    (⟨i,a,m,s,t,r,fun _ => 0⟩ : CaseKey) ∈ rawFamilies := by
  apply List.mem_flatMap.mpr
  refine ⟨i, List.mem_finRange _, List.mem_flatMap.mpr ⟨a, List.mem_finRange _, ?_⟩⟩
  rw [first_has_no_predecessor i a ha]
  apply List.mem_flatMap.mpr
  refine ⟨m, hm, List.mem_flatMap.mpr ⟨s, by cases s <;> simp, ?_⟩⟩
  exact List.mem_flatMap.mpr ⟨t, by cases t <;> simp, List.mem_map.mpr ⟨r, hr, rfl⟩⟩

/-- The root and the second block realize the named family, before choosing
the three embeddings into the other root arms. -/
def RealizesFamily (G : EdgeCol (Fin 58) 4) (k : CaseKey) : Prop :=
  ∃ (r : Fin 58) (σ : Equiv.Perm (Fin 4)) (L : RootLayout G r k.planIndex σ)
    (hy : k.markPosition < plannedDegree k.plan k.arm),
    let q := L.host (slotLabel k.planIndex (some ⟨k.arm,⟨k.markPosition,hy⟩⟩))
    w G r ≤ H G r ∧ plannedThreshold k.plan k.arm ≤ armSenders G r (σ k.arm) ∧
    Sends G q r ∧ ∃ (hr : r ∈ arm G q (σ k.arm)) (e : ↥(arm G q (σ k.arm)) ≃ Fin k.secondSize),
      (e ⟨r,hr⟩).val = k.rootPosition ∧ ∀ u v, u ≠ v →
        G.col u.val v.val = σ (k.arm.succAbove ((template _ k.secondTwisted).col (e u) (e v)))

/-- Every hypothetical counterexample realizes one of the 1,764 raw families,
with a single global host labelling and the reference position already normalized. -/
theorem exists_realized_raw_family (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G) :
    ∃ k ∈ rawFamilies, RealizesFamily G k := by
  obtain ⟨r, hr, i, σ, L, a, y, hcan, ht, hym, hs, hmem, hd, t, hp⟩ :=
    root_layout_at_retained_mark G hG
  let q := L.host (slotLabel i (some ⟨a,y⟩))
  obtain ⟨s, hn⟩ : ∃ s : Bool, deg G q (σ a) = if s then 16 else 15 := by
    rcases hd with h | h
    · exact ⟨false,h⟩
    · exact ⟨true,h⟩
  change PlanPin G q σ a (deg G q (σ a)) t at hp
  rw [hn] at hp
  obtain ⟨e, hedge⟩ := hp
  let x := e ⟨r,hmem⟩
  obtain ⟨g, hpos, hg⟩ := secondRootMap s t x
  let k : CaseKey := ⟨i,a,y.val,s,t,(g x).val,fun _ => 0⟩
  refine ⟨k, family_mem i a y.val s t _ hcan hym hpos, r, σ, L, y.isLt,
    hr, ht, hs, hmem, e.trans g, rfl, ?_⟩
  intro u v huv
  change G.col u.val v.val = σ (a.succAbove ((template _ t).col (g (e u)) (g (e v))))
  rw [hg _ _ (e.injective.ne huv)]
  exact hedge u v huv

/-- Remaining geometric gluing step for a realized family. Each of the three
placement coordinates must refer to the canonical support table used by expandKey. -/
def FamilyPlacementCover : Prop :=
  ∀ (G : EdgeCol (Fin 58) 4), TriangleFree G → ∀ f ∈ rawFamilies, RealizesFamily G f →
    ∃ k ∈ rawPlacements f, RealizesKey G k

theorem rawCover_of_family_placements (placements : FamilyPlacementCover) : RawCover := by
  intro G hG
  obtain ⟨f, hf, hGf⟩ := exists_realized_raw_family G hG
  obtain ⟨k, hk, hGk⟩ := placements G hG f hf hGf
  exact ⟨k, List.mem_flatMap.mpr ⟨f,hf,hk⟩, hGk⟩

theorem frozenCover_of_family_placements (placements : FamilyPlacementCover)
    (transports : RawTransportCover) : FrozenCover :=
  frozenCover_of_rawCover (rawCover_of_family_placements placements) transports

end K58
