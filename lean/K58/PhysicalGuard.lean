import K58.EmittedBridge

/-! Why bare emitted-step readiness at the physical valuation is vacuous.

The ordinary physical valuation has values only for genuine host edges. The
auxiliary sender guards lie above the physical tier. Consequently they are
false at `realizedValuation`, and a guarded-true implication is true whether
or not the geometric premises or emitted counts hold.  This does not invalidate
the neighbour finsets, degree bounds, or physical catalogue masks; it says that
those masks, or agreement of all sixteen support atoms with a non-vacuous
valuation, are the meaningful statements. -/

open K58
open K58.SenderReady
open K58.SemanticAssembly

set_option autoImplicit false

namespace K58.PhysicalGuard

/-- A variable strictly above the physical tier has no `HostVarRep`. -/
theorem realizedValuation_eq_false_of_gt
    (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    {a : Nat} (h : 6612 < a) : realizedValuation G e p a = false := by
  unfold realizedValuation
  split
  · rename_i hh
    obtain ⟨rep⟩ := hh
    have hne : (rep.u : Nat) ≠ (rep.v : Nat) := by
      simp only [ne_eq]
      exact ne_of_lt rep.sorted
    have hle := hostVar_le_of_host_edge rep.u.isLt rep.v.isLt hne rep.colour
    rw [rep.encode] at hle
    omega
  · rfl

/-- Every retained auxiliary counter guard lies above the physical tier. -/
theorem rowGuard_gt (k : Fin 15) : 6612 < rowGuard k := by
  fin_cases k <;> decide

/-- The guard of any emitted sender is false at the physical valuation. -/
theorem realizedValuation_rowGuard
    (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (k : Fin 15) : realizedValuation G e p (rowGuard k) = false :=
  realizedValuation_eq_false_of_gt G e p (rowGuard_gt k)

/-- Explicit vacuity check: bare readiness at the original physical valuation
holds with no triangle-freeness, root pinnings, classification, or count.
The useful results instead concern the mask or agree-on-atoms valuations. -/
theorem senderStep_ready_at_realized_valuation
    (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (k : Fin 15)
    (hb : VarsBelow (catalogueCNF (rowGuard k) (rowAtoms k) (rowSel k)) (rowNewTop k)) :
    (senderStep (rowOldTop k) (rowGuard k) (rowNewTop k) (rowAtoms k) (rowSel k)
      (by have := row_guard_le_old k; omega)
      (by have := row_old_le_new k; omega)
      (row_atoms_bound k) (row_sel_fresh k) (row_sel_injective k) hb).ready
      (realizedValuation G e p) := by
  rw [sender_family_ready k hb]
  intro hg
  rw [realizedValuation_rowGuard G e p k] at hg
  exact absurd hg Bool.false_ne_true

/-- The repaired, non-vacuous valuation premise is satisfiable even with a
true auxiliary guard.  The physical support atoms differ from the guard,
so changing that one auxiliary variable does not alter their physical bits. -/
theorem exists_guard_true_of_atom_agreement
    (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (k : Fin 15) :
    ∃ v : Valuation,
      (∀ j < 16, v (rowAtoms k j) = realizedValuation G e p (rowAtoms k j)) ∧
      v (rowGuard k) = true := by
  let v : Valuation := fun a =>
    if a = rowGuard k then true else realizedValuation G e p a
  refine ⟨v, ?_, ?_⟩
  · intro j hj
    have hne : rowAtoms k j ≠ rowGuard k := by
      have hle : rowAtoms k j ≤ 6612 := by
        rw [EmittedBridge.rowAtoms_val k ⟨j, hj⟩]
        simpa only [Fin.val_mk] using
          (hostVar_le_of_host_edge (u := 1 + j) (v := 18 + k.val)
            (by omega) (by have := k.isLt; omega) (by omega) EmittedBridge.one)
      have hgt := rowGuard_gt k
      omega
    simp [v, hne]
  · simp [v]

#print axioms K58.PhysicalGuard.exists_guard_true_of_atom_agreement
#print axioms K58.PhysicalGuard.realizedValuation_eq_false_of_gt
#print axioms K58.PhysicalGuard.rowGuard_gt
#print axioms K58.PhysicalGuard.realizedValuation_rowGuard
#print axioms K58.PhysicalGuard.senderStep_ready_at_realized_valuation

end K58.PhysicalGuard
