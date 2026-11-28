import K58.TargetSuffix
import K58.CaseExpansion

open K58
open K58.SequentialCounter
open K58.EncoderExtensions
open K58.SemanticAssembly

/-- Lexicographic host-pair rank; the row before `u` has `57-i` entries. -/
def hostLexRank (u v : Nat) : Nat :=
  ((List.range u).map (fun i => 57 - i)).sum + (v - u - 1)

/-- DIMACS host variable, with four consecutive variables per unordered edge. -/
def hostVar (u v : Nat) (c : Fin 4) : Nat :=
  let a := min u v
  let b := max u v
  4 * hostLexRank a b + c.val + 1

def hostPairs : List (Nat × Nat) :=
  (List.range 58).flatMap fun u =>
    ((List.range 58).filter (fun v => u < v)).map (fun v => (u, v))

def hostTriplesExact : List (Nat × Nat × Nat) :=
  (List.range 58).flatMap fun u =>
    ((List.range 58).filter (fun v => u < v)).flatMap fun v =>
      ((List.range 58).filter (fun w => v < w)).map (fun w => (u, v, w))

def edgeExactlyOne (u v : Nat) : CNF :=
  [(List.range 4).map (fun c => (true, hostVar u v (Fin.ofNat 4 c)))] ++
    (List.range 4).flatMap fun c =>
      ((List.range 4).filter (fun d => c < d)).map fun d =>
        [(false, hostVar u v (Fin.ofNat 4 c)), (false, hostVar u v (Fin.ofNat 4 d))]

def triangleExclusions (u v w : Nat) : CNF :=
  (List.range 4).map fun c =>
    [(false, hostVar u v (Fin.ofNat 4 c)),
      (false, hostVar u w (Fin.ofNat 4 c)),
      (false, hostVar v w (Fin.ofNat 4 c))]

/-- Exactly `gluing.host(58)` in its original clause order. -/
def hostBaseCNF : CNF :=
  hostPairs.flatMap (fun p => edgeExactlyOne p.1 p.2) ++
    hostTriplesExact.flatMap (fun t => triangleExclusions t.1 t.2.1 t.2.2)

/-- Exact numeric key of the retained wall row. -/
def targetKey : CaseKey :=
  { planIndex := ⟨29, by decide⟩, arm := ⟨1, by decide⟩, markPosition := 0,
    secondSixteen := false, secondTwisted := true, rootPosition := 7,
    placement := fun _ => 0 }

def unitSigned (u : ColourUnit) : Int :=
  let a : Int := hostVar u.u u.v u.colour
  if u.positive then a else -a

/-- Sorted, duplicate-free signed unit clauses, exactly `gluing.units`. -/
def targetUnitCNF : CNF :=
  match expandKey targetKey with
  | none => []
  | some C =>
      ((K58.caseUnitList C).eraseDups.mergeSort fun u v => decide (unitSigned u ≤ unitSigned v)).map
        (fun u => [(u.positive, hostVar u.u u.v u.colour)])

/-- Exact complete clause list of parent 90d06e.... -/
def targetParentCNF : CNF := hostBaseCNF ++ targetUnitCNF ++ targetSuffixCNF

/-- Full-parent semantic assembly interface. The theorem hides none of its
remaining inputs: base/unit satisfaction, their physical-variable bound, and
all sequential support/total-counter readiness. -/
theorem targetParent_satisfiable_of_ready (v : Valuation)
    (hbase : FormulaSat v (hostBaseCNF ++ targetUnitCNF))
    (hvars : VarsBelow (hostBaseCNF ++ targetUnitCNF) 6612)
    (hready : ChainReady 6612 v targetSuffixSteps) :
    ∃ w : Valuation, (∀ a ≤ 6612, w a = v a) ∧ FormulaSat w targetParentCNF := by
  obtain ⟨w, hagree, hsuffix⟩ := targetSuffix_satisfiable_of_ready v hready
  refine ⟨w, hagree, ?_⟩
  change FormulaSat w ((hostBaseCNF ++ targetUnitCNF) ++ targetSuffixCNF)
  apply (formulaSat_append w (hostBaseCNF ++ targetUnitCNF) targetSuffixCNF).mpr
  exact ⟨formulaSat_preserved v w (hostBaseCNF ++ targetUnitCNF) 6612
    hvars hagree hbase, hsuffix⟩

#print axioms targetParent_satisfiable_of_ready

#eval do
  IO.println s!"p cnf 19533 {targetParentCNF.length}"
  for c in targetParentCNF do
    let fields := c.map (fun (l : Bool × Nat) => if l.1 then toString l.2 else "-" ++ toString l.2)
    IO.println ((String.intercalate " " fields) ++ " 0")
