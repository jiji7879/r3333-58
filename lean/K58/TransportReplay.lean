import K58.DecodePlacement
import Mathlib.Data.Nat.Pairing

namespace K58

/-- An address in the run-length encoded reference ledger. -/
structure Frozen.Address where
  plan : ℕ
  family : ℕ
  run : ℕ
  offset : ℕ

def Frozen.Address.read (a : Frozen.Address) : Option CaseKey := do
  let (p, fs) ← Frozen.planFamilies[a.plan]?
  let f ← fs[a.family]?
  let (start, len) ← f.runs[a.run]?
  if a.offset < len then return f.toKey p (start+a.offset)
  failure

theorem Frozen.Address.mem {a : Frozen.Address} {k : CaseKey} (h : a.read = some k) :
    k ∈ frozenKeys := by
  unfold Frozen.Address.read at h
  cases hp : Frozen.planFamilies[a.plan]? with
  | none => simp [hp] at h
  | some x =>
    obtain ⟨p,fs⟩ := x
    cases hf : fs[a.family]? with
    | none => simp [hp,hf] at h
    | some f =>
      cases hr : f.runs[a.run]? with
      | none => simp [hp,hf,hr] at h
      | some x =>
        obtain ⟨s,n⟩ := x
        by_cases ho : a.offset < n
        · simp [hp,hf,hr,ho] at h
          subst k
          exact List.mem_flatMap.mpr ⟨(p,fs),List.mem_of_getElem? hp,
            List.mem_flatMap.mpr ⟨f,List.mem_of_getElem? hf,List.mem_flatMap.mpr
              ⟨(s,n),List.mem_of_getElem? hr,List.mem_map.mpr ⟨_,List.mem_range.mpr ho,rfl⟩⟩⟩⟩
        · simp [hp,hf,hr,ho] at h

/-- Injective bit index for a signed, named edge, including both endpoints. -/
def ColourUnit.bitIndex (u : ColourUnit) : ℕ :=
  Nat.pair u.u u.v * 8 + u.colour.val * 2 + u.positive.toNat

theorem ColourUnit.bitIndex_injective : Function.Injective ColourUnit.bitIndex := by
  rintro ⟨a,b,c,p⟩ ⟨d,e,f,q⟩ h
  have hc := c.isLt
  have hf := f.isLt
  cases p <;> cases q <;> simp [ColourUnit.bitIndex, Bool.toNat] at h
  all_goals first | omega | (
    have huv : Nat.pair a b = Nat.pair d e := by omega
    have hcf : c = f := Fin.ext (by omega)
    obtain ⟨rfl,rfl⟩ := Nat.pair_eq_pair.mp huv
    subst f
    rfl)

def unitBits : List ColourUnit → ℕ
  | [] => 0
  | u :: us => (1 <<< u.bitIndex) ||| unitBits us

theorem unitBits_member (u : ColourUnit) (l : List ColourUnit) :
    (unitBits l).testBit u.bitIndex = true ↔ u ∈ l := by
  induction l with
  | nil => simp [unitBits]
  | cons v vs ih =>
    simp only [unitBits, Nat.testBit_or, Bool.or_eq_true, List.mem_cons, ← ih]
    rw [Nat.shiftLeft_eq, Nat.one_mul, Nat.testBit_two_pow, decide_eq_true_eq]
    rw [ColourUnit.bitIndex_injective.eq_iff, eq_comm (a := v)]

/-- Checking equality of bit masks proves equality of the entire signed unit sets. -/
theorem transport_of_bits {A B : ExpandedCase} {e : Equiv.Perm (Fin 58)}
    {p : Equiv.Perm (Fin 4)}
    (h : unitBits ((caseUnitList A).map (fun u => u.relabel e p)) = unitBits (caseUnitList B)) :
    UnitTransport A B e p := by
  ext u
  have hh := congrArg (fun n : ℕ => n.testBit u.bitIndex = true) h
  change _ ∈ Finset.image _ _ ↔ _
  simpa only [Finset.mem_image, caseUnits, List.mem_toFinset, List.mem_map, unitBits_member]
    using Iff.of_eq hh

def CoveredKey (k : CaseKey) : Prop := k ∈ frozenKeys ∨ ∀ A, expandKey k = some A →
  ∃ j ∈ frozenKeys, ∃ B, expandKey j = some B ∧ ∃ e p, UnitTransport A B e p

theorem rawTransportCover_of_families
    (h : ∀ f ∈ rawFamilies, ∀ k ∈ rawPlacements f, CoveredKey k) : RawTransportCover := by
  intro k hk
  obtain ⟨f,hf,hk⟩ := List.mem_flatMap.mp hk
  exact h f hf k hk

theorem rawTransportCover_of_plans (h : ∀ i : Fin 41,
    ∀ f ∈ rawFamilies.filter (fun f => f.planIndex.val == i.val),
    ∀ k ∈ rawPlacements f, CoveredKey k) : RawTransportCover := by
  apply rawTransportCover_of_families
  intro f hf
  exact h f.planIndex f (List.mem_filter.mpr ⟨hf,by simp⟩)

/-- A contiguous interval of mixed-radix placements with proved coverage. -/
def GridCover (f : CaseKey) (ny nz start len : ℕ) : Prop :=
  ∀ i < len, CoveredKey (f.atPlacement
    ![(start+i) / nz / ny, (start+i) / nz % ny, (start+i) % nz])

theorem grid_single {f : CaseKey} {ny nz start : ℕ}
    (h : CoveredKey (f.atPlacement ![start / nz / ny,start / nz % ny,start % nz])) :
    GridCover f ny nz start 1 := by
  intro i hi
  have : i = 0 := by omega
  simpa [this] using h

theorem grid_append {f : CaseKey} {ny nz start len more : ℕ}
    (hl : GridCover f ny nz start len) (hr : GridCover f ny nz (start+len) more) :
    GridCover f ny nz start (len+more) := by
  intro i hi
  by_cases h : i < len
  · exact hl i h
  · have hn : i-len < more := by omega
    simpa only [show start+len+(i-len) = start+i by omega] using hr (i-len) hn

theorem cover_family_of_grid {f : CaseKey} {nx ny nz : ℕ}
    (hs : placementShape f = some (nx,ny,nz)) (h : GridCover f ny nz 0 (nx*ny*nz)) :
    ∀ k ∈ rawPlacements f, CoveredKey k := by
  intro k hk
  simp only [rawPlacements,hs, Id.run,pure,Pure.pure,List.mem_flatMap,List.mem_map,List.mem_range] at hk
  obtain ⟨a,ha,b,hb,c,hc,rfl⟩ := hk
  have hab : a*ny+b < nx*ny := calc
    _ < a*ny+ny := Nat.add_lt_add_left hb _
    _ = (a+1)*ny := (Nat.succ_mul _ _).symm
    _ ≤ nx*ny := Nat.mul_le_mul_right _ ha
  have hrank : (a*ny+b)*nz+c < nx*ny*nz := calc
    _ < (a*ny+b)*nz+nz := Nat.add_lt_add_left hc _
    _ = (a*ny+b+1)*nz := (Nat.succ_mul _ _).symm
    _ ≤ nx*ny*nz := Nat.mul_le_mul_right _ hab
  have divc : ((a*ny+b)*nz+c)/nz = a*ny+b := by
    rw [Nat.mul_comm (a*ny+b) nz,Nat.mul_add_div (Nat.zero_lt_of_lt hc),Nat.div_eq_of_lt hc,Nat.add_zero]
  have divb : (a*ny+b)/ny = a := by
    rw [Nat.mul_comm a ny,Nat.mul_add_div (Nat.zero_lt_of_lt hb),Nat.div_eq_of_lt hb,Nat.add_zero]
  simpa [divc,divb,
    Nat.div_eq_of_lt hb,Nat.div_eq_of_lt hc,Nat.mod_eq_of_lt hb,Nat.mod_eq_of_lt hc,
    CaseKey.atPlacement] using h _ hrank

theorem family_nil : ∀ f ∈ ([] : List CaseKey), ∀ k ∈ rawPlacements f, CoveredKey k := by simp

theorem family_cons {f : CaseKey} {fs : List CaseKey}
    (h : ∀ k ∈ rawPlacements f, CoveredKey k)
    (hs : ∀ g ∈ fs, ∀ k ∈ rawPlacements g, CoveredKey k) :
    ∀ g ∈ f :: fs, ∀ k ∈ rawPlacements g, CoveredKey k := by
  intro g hg
  rcases List.mem_cons.mp hg with rfl | ht
  · exact h
  · exact hs g ht

def transportCheck (k j : CaseKey) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) : Bool :=
  match expandKey k, expandKey j with
  | some A, some B => decide (unitBits ((caseUnitList A).map (fun u => u.relabel e p)) = unitBits (caseUnitList B))
  | _, _ => false

theorem covered_of_transportCheck {k j : CaseKey} {e : Equiv.Perm (Fin 58)}
    {p : Equiv.Perm (Fin 4)} (hj : j ∈ frozenKeys) (h : transportCheck k j e p = true) :
    CoveredKey k := by
  right
  intro A hA
  cases hB : expandKey j with
  | none => simp [transportCheck,hA,hB] at h
  | some B =>
    simp only [transportCheck,hA,hB,decide_eq_true_eq] at h
    exact ⟨j,hj,B,hB,e,p,transport_of_bits h⟩

end K58
