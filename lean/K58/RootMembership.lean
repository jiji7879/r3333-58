import K58.StructuralTransport

namespace K58

def rootUnpack (w : ℕ) : ColourUnit := ⟨w >>> 8,(w >>> 2)%64,Fin.ofNat 4 w,true⟩

/-- Cached numerical description of the fixed units in one root layout. -/
structure RootCache (P : Plan) where
  words : List ℕ
  mask : ℕ
  words_ok : rootUnitList P = words.map rootUnpack
  mask_ok : unitBits (rootUnitList P) = mask
  bounded : words.all (fun w => decide ((rootUnpack w).u ≤ (rootUnpack w).v ∧ (rootUnpack w).v < 58)) = true

private theorem edge_relabel (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (x y : Fin 58) (c : Fin 4) (b : Bool) :
    (ColourUnit.ofEdge x.val y.val c b).relabel e p = ColourUnit.ofEdge (e x).val (e y).val (p c) b := by
  have hx (i : Fin 58) : Fin.ofNat 58 i.val = i := Fin.ext (Nat.mod_eq_of_lt i.isLt)
  rcases le_total x.val y.val with h | h
  · simp [ColourUnit.relabel,ColourUnit.ofEdge,min_eq_left h,max_eq_right h]
  · change ColourUnit.ofEdge (e (Fin.ofNat 58 (min x.val y.val))).val
      (e (Fin.ofNat 58 (max x.val y.val))).val (p c) b = _
    rw [min_eq_right h,max_eq_left h,hx,hx]
    simp only [ColourUnit.ofEdge,min_comm (e y).val,max_comm (e y).val]

private theorem undo_relabel (u : ColourUnit) (hu : u.u ≤ u.v ∧ u.v < 58)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) :
    (u.relabel e p).relabel e.symm p.symm = u := by
  let x : Fin 58 := ⟨u.u,lt_of_le_of_lt hu.1 hu.2⟩
  let y : Fin 58 := ⟨u.v,hu.2⟩
  have h : ColourUnit.ofEdge x.val y.val u.colour u.positive = u := by
    simp [x,y,ColourUnit.ofEdge,min_eq_left hu.1,max_eq_right hu.1]
  calc
    _ = ((ColourUnit.ofEdge x.val y.val u.colour u.positive).relabel e p).relabel e.symm p.symm := by rw [h]
    _ = _ := by simpa only [edge_relabel,Equiv.symm_apply_apply] using h

/-- On sorted valid edges a relabelling is injective. Inclusion in the same finite
root set therefore proves equality. Each table entry requires a single bit lookup. -/
theorem root_of_packed_test {P : Plan} (R : RootCache P) (e : Equiv.Perm (Fin 58))
    (p : Equiv.Perm (Fin 4)) (h : R.words.all (fun w => R.mask.testBit ((rootUnpack w).relabel e p).bitIndex) = true) :
    (rootUnitList P).toFinset.image (fun u => u.relabel e p) = (rootUnitList P).toFinset := by
  let S := (rootUnitList P).toFinset
  have repr (u : ColourUnit) (hu : u ∈ S) : ∃ w ∈ R.words, rootUnpack w = u := by
    have hmem := List.mem_toFinset.mp hu
    rw [R.words_ok] at hmem
    exact List.mem_map.mp hmem
  have inc : S.image (fun u => u.relabel e p) ⊆ S := by
    intro u hu
    obtain ⟨v,hv,rfl⟩ := Finset.mem_image.mp hu
    obtain ⟨w,hw,rfl⟩ := repr v hv
    have hit := List.all_eq_true.mp h w hw
    rw [← R.mask_ok] at hit
    exact List.mem_toFinset.mpr ((unitBits_member _ _).mp hit)
  have inv (u : ColourUnit) (hu : u ∈ S) : (u.relabel e p).relabel e.symm p.symm = u := by
    obtain ⟨w,hw,rfl⟩ := repr u hu
    exact undo_relabel _ (of_decide_eq_true (List.all_eq_true.mp R.bounded w hw)) e p
  apply Finset.eq_of_subset_of_card_le inc
  apply le_of_eq
  symm
  refine Finset.card_image_of_injOn ?_
  intro u hu v hv huv
  exact (inv u hu).symm.trans ((congrArg (fun t : ColourUnit => t.relabel e.symm p.symm) huv).trans (inv v hv))

end K58
