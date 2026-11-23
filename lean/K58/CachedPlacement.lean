import K58.TransportReplay

namespace K58

/-- The first image partitions a critical-arm support search into independent branches. -/
theorem words15_first {n : ℕ} (C : EdgeCol (Fin n) 3) (a b : Fin 4) (t : Bool)
    (x : Fin n) (xs : List (Fin n)) (chunks : Fin 15 → List (List ℕ))
    (h : ∀ y, supportEmbeddings C a (template 15 t) b (named15 t) xs [(x,y)] = chunks y) :
    targetWords C a b 15 (if t then 'T' else 'U') (x::xs) =
      some ((List.finRange 15).flatMap chunks) := by
  rw [← funext h]
  cases t <;> rfl

theorem words16_first {n : ℕ} (C : EdgeCol (Fin n) 3) (a b : Fin 4) (t : Bool)
    (x : Fin n) (xs : List (Fin n)) (chunks : Fin 16 → List (List ℕ))
    (h : ∀ y, supportEmbeddings C a (template 16 t) b (named16 t) xs [(x,y)] = chunks y) :
    targetWords C a b 16 (if t then 'T' else 'U') (x::xs) =
      some ((List.finRange 16).flatMap chunks) := by
  rw [← funext h]
  cases t <;> rfl

/-- The three support tables for one family, checked once for all its placements. -/
structure PlacementTables (f : CaseKey) where
  rootBound : f.rootPosition < f.secondSize
  table : Fin 3 → List (Fin f.secondSize) × List (List ℕ)
  exactTable : ∀ c, supportTable f ⟨_,rootBound⟩ c = some (table c)

def expandUsing (k : CaseKey)
    (tables : Fin k.secondSize → Fin 3 → Option (List (Fin k.secondSize) × List (List ℕ))) :
    Option ExpandedCase := do
  if hr : k.rootPosition < k.secondSize then
    let r : Fin k.secondSize := ⟨_, hr⟩
    let parts ← (List.finRange 3).mapM fun c => do
      let b := k.arm.succAbove c
      let (s, choices) ← tables r c
      let positions ← choices[k.placement c]?
      return s.zip (positions.map (blockLabel k.plan b))
    let pairs := (r, 0) :: parts.flatten
    let label := fun i => (pairs.lookup i).getD 58
    if hv : ∀ i, label i < 58 then
      let f : Fin k.secondSize → Fin 58 := fun i => ⟨_, hv i⟩
      if hi : Function.Injective f then
        if hz : f r = 0 then
          if hq : k.markPosition < plannedDegree k.plan k.arm then
            return ⟨k, f, hi, hr, hz, hq⟩
    failure
  else failure

def PlacementTables.expand {f : CaseKey} (T : PlacementTables f) (v : Fin 3 → ℕ) :
    Option ExpandedCase := expandUsing (f.atPlacement v) (fun _ c => some (T.table c))

theorem PlacementTables.expand_exact {f : CaseKey} (T : PlacementTables f) (v : Fin 3 → ℕ) :
    expandKey (f.atPlacement v) = T.expand v := by
  change expandUsing (f.atPlacement v) (supportTable (f.atPlacement v)) = _
  unfold PlacementTables.expand expandUsing
  have hr : (f.atPlacement v).rootPosition < (f.atPlacement v).secondSize := T.rootBound
  simp only [hr, ↓reduceDIte]
  have ht : supportTable (f.atPlacement v) ⟨_,hr⟩ = (fun c => some (T.table c)) :=
    funext T.exactTable
  rw [ht]
  rfl

theorem PlacementTables.shape {f : CaseKey} (T : PlacementTables f) :
    placementShape f = some ((T.table 0).2.length,(T.table 1).2.length,(T.table 2).2.length) := by
  simp [placementShape,T.rootBound,T.exactTable]

def checkExpanded (A B : Option ExpandedCase) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) : Bool :=
  match A,B with
  | some C, some D => decide (unitBits ((caseUnitList C).map (fun u => u.relabel e p)) = unitBits (caseUnitList D))
  | _,_ => false

theorem covered_of_cached {f g : CaseKey} {v w : Fin 3 → ℕ} (T : PlacementTables f) (U : PlacementTables g)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (hj : g.atPlacement w ∈ frozenKeys)
    (h : checkExpanded (T.expand v) (U.expand w) e p = true) : CoveredKey (f.atPlacement v) := by
  apply covered_of_transportCheck (e := e) (p := p) hj
  change checkExpanded (expandKey _) (expandKey _) e p = true
  rwa [T.expand_exact, U.expand_exact]

end K58
