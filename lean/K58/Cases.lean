import K58.Frontier
import K58.Templates

namespace K58

/-- A raw key in the frozen ledger, with the profile and root kinds looked up
together by plan index. Placement indices are ordered by the three host colours
other than the sender arm, in increasing order. -/
structure CaseKey where
  planIndex : Fin 41
  arm : Fin 4
  markPosition : ℕ
  secondSixteen : Bool
  secondTwisted : Bool
  rootPosition : ℕ
  placement : Fin 3 → ℕ

def CaseKey.plan (k : CaseKey) := plans[k.planIndex.val]'(by exact k.planIndex.isLt)
def CaseKey.secondSize (k : CaseKey) : ℕ := if k.secondSixteen then 16 else 15

/-- The host label of local position i in a canonical root block. -/
def blockLabel (P : Plan) (a : Fin 4) (i : ℕ) : ℕ := 1 + (P.prof.take a.val).sum + i

structure ColourUnit where
  u : ℕ
  v : ℕ
  colour : Fin 4
  positive : Bool
  deriving DecidableEq

def ColourUnit.ofEdge (u v : ℕ) (c : Fin 4) (pos := true) : ColourUnit :=
  ⟨min u v, max u v, c, pos⟩

def blockUnits {n : ℕ} (vertices : Fin n → ℕ) (t : Bool) (a : Fin 4) :
    List ColourUnit :=
  (List.finRange n).flatMap fun i =>
    ((List.finRange n).filter (fun j => i < j)).map fun j =>
      ColourUnit.ofEdge (vertices i) (vertices j) (a.succAbove ((template n t).col i j))

/-- The ordered second block is the result of expanding the three support
placement indices. Its root position maps to host label zero. -/
structure ExpandedCase where
  key : CaseKey
  marked : Fin key.secondSize → Fin 58
  marked_injective : Function.Injective marked
  root_in_range : key.rootPosition < key.secondSize
  root_at : marked ⟨key.rootPosition, root_in_range⟩ = 0
  mark_in_range : key.markPosition < plannedDegree key.plan key.arm

/-- Signed assertions fixed by the root layout of a plan. -/
def rootUnitList (P : Plan) : List ColourUnit :=
  let first := (List.finRange 4).flatMap fun a =>
    (List.range (plannedDegree P a)).map fun i => ColourUnit.ofEdge 0 (blockLabel P a i) a
  let inside := (List.finRange 4).flatMap fun a =>
    let block : Fin (plannedDegree P a) → ℕ := fun i => blockLabel P a i.val
    match P.kinds.toList[a.val]? with
    | some 'U' => blockUnits block false a
    | some 'T' => blockUnits block true a
    | _ => []
  first ++ inside

/-- Positive and negative assertions at the marked sender. -/
def starUnitList {n : ℕ} (q : ℕ) (a : Fin 4) (labels : Fin n → Fin 58) : List ColourUnit :=
  ((List.range 58).filter (fun v => v != 0 && v != q)).map fun v =>
    ColourUnit.ofEdge q v a ((List.finRange n).any (fun i => (labels i).val == v))

/-- Signed edge-colour assertions of the original marked-root gluing. -/
def caseUnitList (C : ExpandedCase) : List ColourUnit :=
  rootUnitList C.key.plan ++ blockUnits (fun i => (C.marked i).val) C.key.secondTwisted C.key.arm ++
    starUnitList (blockLabel C.key.plan C.key.arm C.key.markPosition) C.key.arm C.marked

def caseUnits (C : ExpandedCase) : Finset ColourUnit := (caseUnitList C).toFinset

/-- A unit is interpreted on two distinct valid labels in the concrete host.
Both vertex and global colour permutations are shared by every unit of the case. -/
def RealizesCase (G : EdgeCol (Fin 58) 4) (C : ExpandedCase) : Prop :=
  ∃ (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)), ∀ u ∈ caseUnits C,
    ∃ i j : Fin 58, i.val = u.u ∧ j.val = u.v ∧ i ≠ j ∧
      (G.col (e i) (e j) = p u.colour ↔ u.positive = true)

end K58
