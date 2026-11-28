/-
K58: what the retained target's own units freeze (swarm smx0er1f6, m1, direction 6).

`K58.SupportTransport.support_mask_mem` needs two physical pinnings: the sender's
colour-1 arm and "the root's arm 0 pinned to T16 in the emitted coordinates `er`".
This file shows the second one is not an extra physical assumption for the
retained key `targetKey` (plan 29, profile `(16,16,14,11)`, kinds `TU--`): the
key's own frozen units are exactly the T16 template on arm 0 in emitted label
order, and exactly the colour-1 root edges to arm 1 -- the latter being the
`hqr : G.col q r = 1` hypothesis of `SupportTransport` for every sender
`e (18+k)`.

Kernel-checked here: the unit lists of `rootUnitList targetPlan` themselves
(`by decide`), the plan data, and the transfer from `caseUnitList` to the emitted
`targetUnitCNF`, then to the physical colouring.  The single bookkeeping step not
proved here is `C.key.plan = targetPlan` from `expandKey targetKey = some C`,
which is carried as the hypothesis `hplan`.
-/
import K58.SenderReady
import K58.SupportTransport
import K58.PhysicalBridge
import K58.ArmPinned

open K58
open K58.SemanticAssembly

set_option autoImplicit false
set_option maxRecDepth 1000000
set_option maxHeartbeats 4000000

namespace K58.TargetUnits

/-- The plan of the retained key: ledger row 29. -/
def targetPlan : Plan := plans.get ⟨29, by decide⟩

theorem targetPlan_prof : targetPlan.prof = [16, 16, 14, 11] := by decide
theorem targetPlan_kinds : targetPlan.kinds = "TU--" := by decide
theorem targetPlan_deg0 : plannedDegree targetPlan 0 = 16 := by decide
theorem targetPlan_deg1 : plannedDegree targetPlan 1 = 16 := by decide
theorem targetPlan_deg2 : plannedDegree targetPlan 2 = 14 := by decide
theorem targetPlan_deg3 : plannedDegree targetPlan 3 = 11 := by decide

/-- Arm 0 has sixteen vertices, labelled `1 … 16`. -/
theorem targetPlan_blockLabel0 (i : Nat) (_hi : i < 16) :
    blockLabel targetPlan 0 i = 1 + i := by
  unfold blockLabel
  rw [targetPlan_prof]
  simp

/-- Arm 1 has sixteen vertices, labelled `17 … 32`. -/
theorem targetPlan_blockLabel1 (i : Nat) (_hi : i < 16) :
    blockLabel targetPlan 1 i = 17 + i := by
  unfold blockLabel
  rw [targetPlan_prof]
  simp

/-- **Arm 0's inside-block units are the T16 template**, in emitted label order:
the pair `(1+i, 1+j)` carries colour `0.succAbove (template 16 true).col i j`.
This is exactly the `hroot` hypothesis of `SupportTransport.support_mask_mem`. -/
theorem arm0_block_units : ∀ (i j : Fin 16), i < j →
    ColourUnit.ofEdge (1 + i.val) (1 + j.val)
        ((0 : Fin 4).succAbove ((template 16 true).col i j)) ∈ rootUnitList targetPlan := by
  decide

/-- The root edges into arm 0 are colour 0. -/
theorem arm0_root_units : ∀ i : Fin 16,
    ColourUnit.ofEdge 0 (1 + i.val) (0 : Fin 4) ∈ rootUnitList targetPlan := by
  decide

/-- **The root edges into arm 1 are colour 1**, for all sixteen arm-1 vertices
`17 … 32`.  So every sender `e (18+k)` of the emitted suffix satisfies
`G.col q r = 1`, the `hqr` hypothesis of `SupportTransport`. -/
theorem arm1_root_units : ∀ i : Fin 16,
    ColourUnit.ofEdge 0 (17 + i.val) (1 : Fin 4) ∈ rootUnitList targetPlan := by
  decide

/-- `rootUnitList` is part of the key's unit list. -/
theorem root_units_subset (C : ExpandedCase) (hplan : C.key.plan = targetPlan)
    {u : ColourUnit} (hu : u ∈ rootUnitList targetPlan) : u ∈ caseUnitList C := by
  unfold caseUnitList
  rw [hplan]
  exact List.mem_append_left _ (List.mem_append_left _ hu)

/-- The units of the key reach the emitted `targetUnitCNF` through the
sort/deduplicate step. -/
theorem targetUnitCNF_mem (C : ExpandedCase) (hC : expandKey targetKey = some C)
    {u : ColourUnit} (hu : u ∈ caseUnitList C) :
    [(u.positive, hostVar u.u u.v u.colour)] ∈ targetUnitCNF := by
  unfold targetUnitCNF
  rw [hC]
  exact List.mem_map.mpr
    ⟨u, List.mem_mergeSort.mpr (List.mem_eraseDups.mpr hu), rfl⟩

/-- A `ClauseSat` of a unit clause is that unit's literal being true. -/
theorem eval_of_unit_mem {w : Valuation} {F : CNF} {l : Bool × Nat} (h : [l] ∈ F)
    (hs : FormulaSat w F) : w l.2 = l.1 := by
  obtain ⟨l', hl', hw⟩ := hs _ h
  rw [List.mem_singleton] at hl'
  rw [← hl']
  exact hw

/-- **The root's arm-0 pinning is in the key's units, in the emitted
coordinates.**  Given the arm-0 template unit of the key (supplied by
`arm0_block_units` via `root_units_subset` and `targetUnitCNF_mem`) and that the
emitted units are satisfied, the physical colouring of the root's arm 0 is the
`T16` template along `e`, i.e. `hroot` with `er.symm i = e (1+i)`. -/
theorem hroot_of_unit_mem (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58))
    (i j : Fin 16) (hij : i < j)
    (hu : [(true, hostVar (1 + i.val) (1 + j.val)
      ((0 : Fin 4).succAbove ((template 16 true).col i j)))] ∈ targetUnitCNF)
    (hs : FormulaSat (realizedValuation G e (Equiv.refl (Fin 4))) targetUnitCNF) :
    G.col (e ⟨1 + i.val, by omega⟩) (e ⟨1 + j.val, by omega⟩) =
      (0 : Fin 4).succAbove ((template 16 true).col i j) := by
  have hsat : realizedValuation G e (Equiv.refl (Fin 4))
      (hostVar (1 + i.val) (1 + j.val)
        ((0 : Fin 4).succAbove ((template 16 true).col i j))) = true :=
    eval_of_unit_mem hu hs
  have hne : (⟨1 + i.val, by omega⟩ : Fin 58) ≠ ⟨1 + j.val, by omega⟩ := by
    intro h
    have hv : (1 + i.val : Nat) = 1 + j.val := congrArg Fin.val h
    have hlt : i.val < j.val := hij
    omega
  rw [realizedValuation_hostVar_unsorted G e (Equiv.refl (Fin 4)) hne] at hsat
  exact of_decide_eq_true hsat

/-- **The `hqr` premise of `SupportTransport` is frozen by the key too**, for
every arm-1 vertex `e (17+i)`, hence for every sender `e (18+k)`. -/
theorem root_edge_colour_of_unit_mem (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58))
    (i : Fin 16)
    (hu : [(true, hostVar 0 (17 + i.val) (1 : Fin 4))] ∈ targetUnitCNF)
    (hs : FormulaSat (realizedValuation G e (Equiv.refl (Fin 4))) targetUnitCNF) :
    G.col (e ⟨0, by omega⟩) (e ⟨17 + i.val, by omega⟩) = 1 := by
  have hsat : realizedValuation G e (Equiv.refl (Fin 4)) (hostVar 0 (17 + i.val) (1 : Fin 4)) = true :=
    eval_of_unit_mem hu hs
  have hne : (⟨0, by omega⟩ : Fin 58) ≠ ⟨17 + i.val, by omega⟩ := by
    intro h
    have hv : (0 : Nat) = 17 + i.val := congrArg Fin.val h
    omega
  rw [realizedValuation_hostVar_unsorted G e (Equiv.refl (Fin 4)) hne] at hsat
  exact of_decide_eq_true hsat

#print axioms K58.TargetUnits.targetPlan_prof
#print axioms K58.TargetUnits.targetPlan_blockLabel0
#print axioms K58.TargetUnits.targetPlan_blockLabel1
#print axioms K58.TargetUnits.eval_of_unit_mem
#print axioms K58.TargetUnits.arm0_block_units
#print axioms K58.TargetUnits.arm0_root_units
#print axioms K58.TargetUnits.arm1_root_units
#print axioms K58.TargetUnits.root_units_subset
#print axioms K58.TargetUnits.targetUnitCNF_mem
#print axioms K58.TargetUnits.hroot_of_unit_mem
#print axioms K58.TargetUnits.root_edge_colour_of_unit_mem

end K58.TargetUnits
