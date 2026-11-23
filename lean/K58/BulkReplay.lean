import K58.StructuralTransport

namespace K58

/-- Compare exactly the six family fields and all three placement coordinates. -/
def CaseKey.same (a b : CaseKey) : Bool :=
  a.planIndex == b.planIndex && a.arm == b.arm && a.markPosition == b.markPosition &&
  a.secondSixteen == b.secondSixteen && a.secondTwisted == b.secondTwisted &&
  a.rootPosition == b.rootPosition && a.placement 0 == b.placement 0 &&
  a.placement 1 == b.placement 1 && a.placement 2 == b.placement 2

theorem CaseKey.eq_of_same {a b : CaseKey} (h : a.same b = true) : a = b := by
  obtain ⟨i,c,m,s,t,r,v⟩ := a
  obtain ⟨j,d,n,u,z,k,w⟩ := b
  simp only [same,Bool.and_eq_true,beq_iff_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨rfl,rfl⟩,rfl⟩,rfl⟩,rfl⟩,rfl⟩,ha⟩,hb⟩,hc⟩ := h
  have : v = w := funext fun x => by fin_cases x <;> assumption
  cases this
  rfl

def Frozen.Address.matches (a : Frozen.Address) (k : CaseKey) : Bool :=
  match a.read with
  | some j => k.same j
  | none => false

theorem Frozen.Address.mem_of_matches {a : Frozen.Address} {k : CaseKey} (h : a.matches k = true) :
    k ∈ frozenKeys := by
  cases hr : a.read with
  | none => simp [Frozen.Address.matches,hr] at h
  | some j =>
    have he : k = j := CaseKey.eq_of_same (by simpa [Frozen.Address.matches,hr] using h)
    exact he ▸ a.mem hr

/-- The inverse image digits supply a linear-time check of injectivity. -/
structure PackedMarkData where
  word : ℕ
  inverse : ℕ

def PackedMarkData.read {f : CaseKey} (m : PackedMarkData) (T : PlacementTables f)
    (hm : f.markPosition < plannedDegree f.plan f.arm) : Option (Marking f) :=
  if hi : ∀ i : Fin f.secondSize, packedValue m.inverse 4 (packedLabels m.word i).val = i.val then
    if hz : packedLabels m.word (⟨_,T.rootBound⟩ : Fin f.secondSize) = 0 then
      some (packedMarking f m.word m.inverse T.rootBound hm hi hz)
    else none
  else none

structure MoveTarget (f : CaseKey) where
  key : CaseKey
  tables : PlacementTables key
  bound : key.markPosition < plannedDegree key.plan key.arm
  relabelling : Alignment f key

structure MoveInput where
  x : ℕ
  y : ℕ
  z : ℕ
  address : Frozen.Address
  sourceLabels : PackedMarkData
  targetLabels : PackedMarkData

def MoveInput.indices (d : MoveInput) : Fin 3 → ℕ := ![d.x,d.y,d.z]

def MoveTarget.check {f : CaseKey} (dst : MoveTarget f) (T : PlacementTables f)
    (hm : f.markPosition < plannedDegree f.plan f.arm) (v : Fin 3 → ℕ) (d : MoveInput) : Bool :=
  match d.sourceLabels.read T hm, d.targetLabels.read dst.tables dst.bound with
  | some M, some N =>
    d.address.matches (dst.key.atPlacement d.indices) && T.matches v M &&
    dst.tables.matches d.indices N && decide (∀ i, dst.relabelling.host (M.labels i) =
      N.labels (dst.relabelling.localMap i))
  | _,_ => false

theorem MoveTarget.sound {f : CaseKey} {dst : MoveTarget f} {T : PlacementTables f}
    {hm : f.markPosition < plannedDegree f.plan f.arm} {v : Fin 3 → ℕ} {d : MoveInput}
    (h : dst.check T hm v d = true) : CoveredKey (f.atPlacement v) := by
  cases hM : d.sourceLabels.read T hm with
  | none => simp [check,hM] at h
  | some M =>
    cases hN : d.targetLabels.read dst.tables dst.bound with
    | none => simp [check,hM,hN] at h
    | some N =>
      simp only [check,hM,hN,Bool.and_eq_true,decide_eq_true_eq] at h
      exact covered_aligned T dst.tables M N dst.relabelling
        (Frozen.Address.mem_of_matches h.1.1.1) h.1.1.2 h.1.2 h.2

inductive ReplayEntry where
  | retained (address : Frozen.Address)
  | moved (action : ℕ) (input : MoveInput)

def ReplayEntry.check {f : CaseKey} (entry : ReplayEntry) (T : PlacementTables f)
    (hm : f.markPosition < plannedDegree f.plan f.arm) (actions : Array (MoveTarget f))
    (v : Fin 3 → ℕ) : Bool :=
  match entry with
  | .retained a => a.matches (f.atPlacement v)
  | .moved j d => match actions[j]? with
    | some a => a.check T hm v d
    | none => false

theorem ReplayEntry.sound {f : CaseKey} {d : ReplayEntry} {T : PlacementTables f}
    {hm : f.markPosition < plannedDegree f.plan f.arm} {actions : Array (MoveTarget f)}
    {v : Fin 3 → ℕ} (h : d.check T hm actions v = true) : CoveredKey (f.atPlacement v) := by
  cases d with
  | retained a => exact Or.inl (Frozen.Address.mem_of_matches h)
  | moved j d =>
    cases ha : actions[j]? with
    | none => simp [check,ha] at h
    | some a => exact MoveTarget.sound (dst := a) (T := T) (hm := hm) (d := d) (by simpa [check,ha] using h)

def checkRows {f : CaseKey} (T : PlacementTables f)
    (hm : f.markPosition < plannedDegree f.plan f.arm) (actions : Array (MoveTarget f))
    (ny nz : ℕ) : ℕ → List ReplayEntry → Bool
  | _,[] => true
  | r,x::xs => x.check T hm actions ![r/nz/ny,r/nz%ny,r%nz] && checkRows T hm actions ny nz (r+1) xs

theorem grid_of_checked_rows {f : CaseKey} (T : PlacementTables f)
    (hm : f.markPosition < plannedDegree f.plan f.arm) (actions : Array (MoveTarget f))
    (ny nz start : ℕ) (rows : List ReplayEntry) (h : checkRows T hm actions ny nz start rows = true) :
    GridCover f ny nz start rows.length := by
  induction rows generalizing start with
  | nil => intro i hi; simp at hi
  | cons x xs ih =>
    have both : x.check T hm actions ![start/nz/ny,start/nz%ny,start%nz] = true ∧
        checkRows T hm actions ny nz (start+1) xs = true := by
      simpa only [checkRows,Bool.and_eq_true] using h
    have one := grid_single (ny := ny) (nz := nz) (start := start) (ReplayEntry.sound both.1)
    simpa [Nat.add_comm 1] using grid_append one (ih (start+1) both.2)

end K58
