import K58.RawCover

namespace K58

/-- Change the three indices without changing the family or the support tables. -/
def CaseKey.atPlacement (k : CaseKey) (v : Fin 3 → ℕ) : CaseKey := {k with placement := v}

theorem mem_rawPlacements_of_indices (k : CaseKey) (v : Fin 3 → ℕ)
    (hr : k.rootPosition < k.secondSize) (ws : Fin 3 → List (List ℕ))
    (tables : ∀ c, supportTable k ⟨_,hr⟩ c = some (supportAt k ⟨_,hr⟩ (k.arm.succAbove c),ws c))
    (bounds : ∀ c, v c < (ws c).length) : k.atPlacement v ∈ rawPlacements k := by
  have hv : ![v 0,v 1,v 2] = v := by funext c; fin_cases c <;> rfl
  simp only [rawPlacements, placementShape, bind, Option.bind, hr, ↓reduceDIte, tables, Id.run, pure, Pure.pure, List.mem_flatMap, List.mem_map, List.mem_range]
  exact ⟨v 0,bounds 0,v 1,bounds 1,v 2,bounds 2,by rw [hv]; rfl⟩

private theorem lookup_graph {α β : Type*} [DecidableEq α] (f : α → β) (l : List α) (x : α)
    (hx : x ∈ l) : (l.map (fun i => (i,f i))).lookup x = some (f x) := by
  induction l with
  | nil => simp at hx
  | cons y ys ih =>
    by_cases h : y = x
    · simp [h]
    · simp [List.lookup, beq_eq_false_iff_ne.mpr (Ne.symm h), ih ((List.mem_cons.mp hx).resolve_left (Ne.symm h))]

/-- If every support index reads the prescribed global labels, expandKey
returns precisely those labels on the entire second block. -/
theorem expandKey_of_labels (k : CaseKey) (v : Fin 3 → ℕ) (hr : k.rootPosition < k.secondSize)
    (hm : k.markPosition < plannedDegree k.plan k.arm) (F : Fin k.secondSize → Fin 58)
    (hF : Function.Injective F) (hroot : F ⟨_,hr⟩ = 0)
    (words : ∀ c, ∃ ws ps, supportTable k ⟨_,hr⟩ c =
      some (supportAt k ⟨_,hr⟩ (k.arm.succAbove c),ws) ∧ ws[v c]? = some ps ∧
      (supportAt k ⟨_,hr⟩ (k.arm.succAbove c)).zip (ps.map (blockLabel k.plan (k.arm.succAbove c))) =
      (supportAt k ⟨_,hr⟩ (k.arm.succAbove c)).map (fun x => (x,(F x).val))) :
    expandKey (k.atPlacement v) = some ⟨k.atPlacement v,F,hF,hr,hroot,hm⟩ := by
  let r : Fin k.secondSize := ⟨_,hr⟩
  let src := fun c => supportAt k r (k.arm.succAbove c)
  let graph := fun x : Fin k.secondSize => (x,(F x).val)
  let part (c : Fin 3) : Option (List (Fin k.secondSize × ℕ)) := do
    let (s,choices) ← supportTable (k.atPlacement v) r c
    let ps ← choices[v c]?
    return s.zip (ps.map (blockLabel k.plan (k.arm.succAbove c)))
  have hp (c) : part c = some ((src c).map graph) := by
    obtain ⟨ws,ps,ht,hj,h⟩ := words c
    change supportTable (k.atPlacement v) r c = some (src c,ws) at ht
    unfold part
    rw [ht]
    change (ws[v c]?.bind fun q => some ((src c).zip (q.map (blockLabel k.plan (k.arm.succAbove c))))) = _
    rw [hj]
    exact congrArg some h
  let domain := r :: ((List.finRange 3).flatMap src)
  have hall (x : Fin k.secondSize) : x ∈ domain := by
    by_cases h : x = r
    · exact List.mem_cons.mpr (Or.inl h)
    · refine List.mem_cons.mpr (Or.inr (List.mem_flatMap.mpr
        ⟨(template _ k.secondTwisted).col r x,List.mem_finRange _,?_⟩))
      simp [src,supportAt,h]
  let parts := (List.finRange 3).map (fun c => (src c).map graph)
  have hparts : (List.finRange 3).mapM part = some parts := by
    rw [show part = (fun c => pure ((src c).map graph)) from funext hp, List.mapM_pure]
    rfl
  have hgraph : (r,0) :: parts.flatten = domain.map graph := by
    have hzero : F r = 0 := hroot
    simp only [domain, List.map_cons, graph, hzero, Fin.val_zero, parts,
      List.map_flatten, List.flatMap_def, List.map_map, Function.comp_def]
  have hl (x : Fin k.secondSize) :
      (((r,0) :: parts.flatten).lookup x).getD 58 = (F x).val := by
    rw [hgraph, lookup_graph (fun j => (F j).val) _ _ (hall x)]
    rfl
  unfold expandKey
  rw [dif_pos (show (k.atPlacement v).rootPosition < (k.atPlacement v).secondSize from hr)]
  change (do
    let parts' ← (List.finRange 3).mapM part
    let label := fun j => (((r,0) :: parts'.flatten).lookup j).getD 58
    if hv : ∀ j, label j < 58 then
      let g : Fin k.secondSize → Fin 58 := fun j => ⟨label j, hv j⟩
      if hi : Function.Injective g then
        if hz : g r = 0 then
          if hq : k.markPosition < plannedDegree k.plan k.arm then
            return (⟨k.atPlacement v,g,hi,hr,hz,hq⟩ : ExpandedCase)
    failure) = _
  rw [hparts]
  simp only [bind, Option.bind]
  have hv (j : Fin k.secondSize) : (((r,0) :: parts.flatten).lookup j).getD 58 < 58 :=
    (hl j).symm ▸ (F j).isLt
  rw [dif_pos hv]
  have hf : (fun j => (⟨_,hv j⟩ : Fin 58)) = F := funext fun j => Fin.ext (hl j)
  have hz := (congrFun hf r).trans hroot
  simp only [hf, hF, hz, hm, ↓reduceDIte, pure, Pure.pure]

end K58
