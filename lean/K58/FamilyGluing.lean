import K58.SupportPlacement
import K58.DecodePlacement

namespace K58

private theorem degree_positive : ∀ (i : Fin 41) (a : Fin 4), 0 < plannedDegree (indexedPlan i) a := by decide

set_option backward.isDefEq.respectTransparency false in
/-- Build all three ordered placements, then apply the three target automorphisms
on disjoint arms. The permutation on the sender's own arm is the identity. -/
theorem familyPlacementCover : FamilyPlacementCover := by
  classical
  intro G _ k _ hfamily
  obtain ⟨r,σ,L,hm,_,_,_,hrmem,e,href,hedge⟩ := hfamily
  let a := k.arm
  let d := plannedDegree k.plan
  let q := L.host (slotLabel k.planIndex (some ⟨a,⟨k.markPosition,hm⟩⟩))
  let b := fun c : Fin 3 => a.succAbove c
  let phys := fun x : Fin k.secondSize => (e.symm x).val
  have hinj : Function.Injective phys := Subtype.val_injective.comp e.symm.injective
  have hr : k.rootPosition < k.secondSize := href ▸ (e ⟨r,hrmem⟩).isLt
  let root : Fin k.secondSize := ⟨_, hr⟩
  have hroot : e ⟨r,hrmem⟩ = root := Fin.ext href
  have hphys : phys root = r := by
    change (e.symm root).val = r
    rw [← hroot, e.symm_apply_apply]
  have edge (x y : Fin k.secondSize) (h : x ≠ y) :
      G.col (phys x) (phys y) = σ (a.succAbove ((template _ k.secondTwisted).col x y)) := by
    simpa only [phys, Equiv.apply_symm_apply] using hedge (e.symm x) (e.symm y) (e.symm.injective.ne h)
  let src := fun c => supportAt k root (b c)
  have armMem (c) (x) (hx : x ∈ src c) : phys x ∈ arm G r (σ (b c)) := by
    obtain ⟨hxne, hcol⟩ := of_decide_eq_true (List.mem_filter.mp hx).2
    apply Finset.mem_filter.mpr
    refine ⟨Finset.mem_univ _,?_,?_⟩
    · rw [← hphys]
      exact hinj.ne hxne
    · rw [← hphys, edge root x hxne.symm]
      exact congrArg σ hcol
  let coord (c : Fin 3) (x : Fin k.secondSize) : Fin (d (b c)) :=
    if hx : x ∈ src c then (L.armEquiv (b c)).symm ⟨phys x, armMem c x hx⟩
    else ⟨0, degree_positive k.planIndex (b c)⟩
  have coordinate (c x) (hx : x ∈ src c) :
      L.host (slotLabel k.planIndex (some ⟨b c,coord c x⟩)) = phys x := by
    change ((L.armEquiv (b c)) (coord c x)).val = phys x
    simp [coord, hx]
  have cinj (c x y) (hx : x ∈ src c) (hy : y ∈ src c) (h : coord c x = coord c y) : x = y := by
    apply hinj
    rw [← coordinate c x hx, ← coordinate c y hy, h]
  have nodup (c) : (src c).Nodup := (List.nodup_finRange _).filter _
  have nmap (c) : ((src c).map (coord c)).Nodup :=
    (nodup c).map_on (fun x hx y hy => cinj c x y hx hy)
  have fits (c) (hc : 15 ≤ d (b c)) : (src c).Pairwise fun x y =>
      coord c x ≠ coord c y ∧ a.succAbove ((template _ k.secondTwisted).col x y) =
      (b c).succAbove ((template _ (planTwisted k.plan (b c))).col (coord c x) (coord c y)) := by
    apply (nodup c).imp_of_mem
    intro x y hx hy hxy
    have hne := fun h => hxy (cinj c x y hx hy h)
    refine ⟨hne,σ.injective ?_⟩
    have h := L.templates (b c) hc (coord c x) (coord c y) hne
    rw [coordinate c x hx, coordinate c y hy] at h
    exact (edge x y hxy).symm.trans h
  have select (c) := supportTable_cover k root c (coord c) (nmap c) (fits c)
  choose maps ws ix tables positions preserves using select
  let blocks : (z : Fin 4) → Equiv.Perm (Fin (d z)) :=
    a.succAboveCases (Equiv.refl _) maps
  have fixed : blocks a = Equiv.refl _ := by simp [blocks]
  have blocksAt (c : Fin 3) : blocks (b c) = maps c := by simp [blocks,b]
  let symm : RootSymmetry k.planIndex := {
    palette := Equiv.refl _
    blocks := blocks
    edges := by
      intro z hz x y hxy
      refine Fin.succAboveCases (α := fun z => ∀ (h : 15 ≤ d z) (x y : Fin (d z)), x ≠ y →
        z.succAbove ((template _ (planTwisted k.plan z)).col (blocks z x) (blocks z y)) =
          z.succAbove ((template _ (planTwisted k.plan z)).col x y)) a ?_ ?_ z hz x y hxy
      · intro _ x y _
        simp [fixed]
      · intro c hc x y hxy
        change (b c).succAbove ((template _ _).col (blocks (b c) x) (blocks (b c) y)) = _
        rw [blocksAt c, preserves c hc x y hxy] }
  let L' : RootLayout G r k.planIndex σ := {
    host := symm.host.symm.trans L.host
    root := (L.relabel symm).root
    arms := (L.relabel symm).arms
    templates := (L.relabel symm).templates }
  let F := fun x => L'.host.symm (phys x)
  have F0 : F root = 0 := L'.host.symm_apply_eq.mpr (hphys.trans L'.root.symm)
  have Finj : Function.Injective F := L'.host.symm.injective.comp hinj
  have FS (c x) (hx : x ∈ src c) : F x =
      slotLabel k.planIndex (some ⟨b c,maps c (coord c x)⟩) := by
    apply L'.host.injective
    change L'.host (L'.host.symm (phys x)) = L.host (symm.host.symm _)
    rw [L'.host.apply_symm_apply, ← coordinate c x hx]
    apply congrArg L.host
    symm
    apply (symm.host.symm_apply_eq).mpr
    exact (congrArg (fun f : Equiv.Perm (Fin (d (b c))) => slotLabel k.planIndex (some ⟨b c,f (coord c x)⟩)) (blocksAt c).symm).trans (symm.host_slot (b c) (coord c x)).symm
  let v := fun c => (ix c).val
  have good := mem_rawPlacements_of_indices k v hr ws tables (fun c => (ix c).isLt)
  have zipped (c) : (src c).zip (((ws c)[(ix c).val]).map (blockLabel k.plan (b c))) =
      (src c).map fun x => (x,(F x).val) := by
    rw [positions]
    simp only [List.map_map]
    have h := @List.zip_map' _ _ _ id (blockLabel k.plan (b c) ∘ fun x => (maps c (coord c x)).val) (src c)
    rw [List.map_id] at h
    rw [h]
    apply List.map_congr_left
    intro x hx
    have hval := (congrArg Fin.val (FS c x hx)).trans (slotLabel_val _ _ _)
    exact congrArg (fun n : ℕ => (x,n)) hval.symm
  let key := k.atPlacement v
  let C : ExpandedCase := ⟨key,F,Finj,hr,F0,hm⟩
  have expanded : expandKey key = some C := expandKey_of_labels k v hr hm F Finj F0 (by
    intro c
    exact ⟨ws c,_,tables c,List.getElem?_eq_getElem (ix c).isLt,zipped c⟩)
  have sender : L'.host (caseMark C) = q := by
    change L.host (symm.host.symm (slotLabel k.planIndex (some ⟨a,⟨k.markPosition,hm⟩⟩))) = _
    apply congrArg L.host
    apply symm.host.symm_apply_eq.mpr
    exact (congrArg (fun f : Equiv.Perm (Fin (d a)) => slotLabel k.planIndex (some ⟨a,f ⟨k.markPosition,hm⟩⟩)) fixed.symm).trans (symm.host_slot a ⟨k.markPosition,hm⟩).symm
  have D : AttachedBlock G C r σ L' := by
    have eqA : arm G (L'.host (caseMark C)) (σ C.key.arm) = arm G q (σ a) := by rw [sender]; rfl
    let E : ↥(arm G (L'.host (caseMark C)) (σ C.key.arm)) ≃ Fin C.key.secondSize :=
      (Equiv.subtypeEquivRight (fun x => show x ∈ arm G (L'.host (caseMark C)) (σ C.key.arm) ↔ x ∈ arm G q (σ a) by rw [eqA])).trans e
    refine ⟨E,?_,?_⟩
    · intro x
      change (e.symm x).val = L'.host (L'.host.symm (phys x))
      rw [L'.host.apply_symm_apply]
    · intro x y hxy
      let castArm : ↥(arm G (L'.host (caseMark C)) (σ C.key.arm)) ≃ ↥(arm G q (σ a)) :=
        Equiv.subtypeEquivRight (fun x => show x ∈ arm G (L'.host (caseMark C)) (σ C.key.arm) ↔ x ∈ arm G q (σ a) by rw [eqA])
      exact hedge (castArm x) (castArm y) (castArm.injective.ne hxy)
  exact ⟨key,good,C,expanded,attached_block_realizes G C r σ L' D⟩

theorem rawCover : RawCover := rawCover_of_family_placements familyPlacementCover

theorem frozenCover_of_transports (ht : RawTransportCover) : FrozenCover :=
  frozenCover_of_rawCover rawCover ht

end K58
