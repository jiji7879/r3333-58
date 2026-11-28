import K58.CounterNeighboursAudit2
import K58.ClassifiedBridge
import K58.SequentialCounter
import K58.PhysicalGuard

/-! Count-driven physical geometry at all fifteen retained senders.

`K58.R3Counter` decodes the exact counter inputs and constructs a genuine
physical neighbour finset.  `K58.EmittedBridge.hclass_classified` supplies the
literal-colour order-15/16 critical classification.  This module combines them:
no neighbour set `W`, its premises, or a separate `hclass` argument is needed.

The main results are the physical catalogue mask and its transport to any
valuation agreeing on the sixteen physical atoms.  Bare `ready` at
`realizedValuation` is retained below for continuity and is independently
shown in `PhysicalGuard` to be vacuous because the auxiliary counter guards
have the value `false` there.  None of this asserts `ChainReady`, a complete
exact-root/key bridge, a reverse guarded-counter soundness theorem, or a Ramsey
bound improvement. -/

open K58
open K58.SequentialCounter
open K58.SenderReady
open K58.SemanticAssembly
open K58.EmittedBridge

set_option autoImplicit false

namespace K58.R3Counter

/-- Every audited emitted 41-of-14 count makes the corresponding emitted
support step ready at the physical valuation, using the actual imported
order-15/16 classification.  The four `W` hypotheses and extra `hclass` of the
former bridge are removed; root and sender host-coordinate identifications
remain explicit. -/
theorem emitted_sender_step_ready_of_emitted_count_classified
    (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e (senderFin k) = q) (hzero : e zeroFin = r)
    (hcount : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (emittedCounterAtoms k i)) 41)
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val =
        (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val)
    (hb : VarsBelow (catalogueCNF (rowGuard k) (rowAtoms k) (rowSel k)) (rowNewTop k)) :
    (senderStep (rowOldTop k) (rowGuard k) (rowNewTop k) (rowAtoms k) (rowSel k)
      (by have := row_guard_le_old k; omega)
      (by have := row_old_le_new k; omega)
      (row_atoms_bound k) (row_sel_fresh k) (row_sel_injective k) hb).ready
      (realizedValuation G e p) := by
  rw [emittedCounterAtoms_eq k] at hcount
  exact emitted_sender_step_ready_of_counter_count G hG e p hp1 k q r hqr_ne hqr
    hq hzero hcount hclass_classified er hroot hcoord hb

/-- **Non-vacuous physical endpoint.** The actual emitted count determines a
catalogue mask, not merely the vacuous `ready` proposition at a guard-false
physical valuation.  The neighbour set comes from the audited input atoms and
the real classification is applied to its critical arm. -/
theorem exists_catalogue_mask_of_emitted_count_classified
    (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e (senderFin k) = q) (hzero : e zeroFin = r)
    (hcount : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (emittedCounterAtoms k i)) 41)
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val =
        (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val) :
    ∃ i : Fin 112, ∀ j : Fin 16,
      realizedValuation G e p (rowAtoms k j.val) = supportBit targetSupports i j.val := by
  rw [emittedCounterAtoms_eq k] at hcount
  obtain ⟨W, hW, hrW, hcard⟩ := exists_neighbour_finset_spec G e p hp1 k q r hq hzero hcount
  have hlo := deg_ge_fifteen_of_counter_count G e p hp1 k q r hqr_ne hqr hq hzero hcount
  obtain ⟨-, hhi, t, ht⟩ := sender_pinned_of_count_of_classification G hG q r hqr_ne hqr W hW hrW hcard
  have hdeg : deg G q 1 = 15 ∨ deg G q 1 = 16 := by omega
  exact emitted_mask_of_pinned G hG e p hp1 k q r hqr_ne hqr hq hdeg ht er hroot hcoord

/-- **Non-vacuous mask at an arbitrary valuation.** If `v` agrees with the
physical valuation on all sixteen genuine support atoms, then `v`'s support
vector is exactly one of the 112 emitted catalogue entries.  Unlike the bare
physical `.ready` proposition, this constrains genuine bits and is true even if
`v`'s auxiliary guard is true. -/
theorem catalogueVec_of_atom_agreement_classified
    (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e (senderFin k) = q) (hzero : e zeroFin = r)
    (hcount : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (emittedCounterAtoms k i)) 41)
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val =
        (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val)
    (v : Valuation)
    (hv : ∀ j < 16, v (rowAtoms k j) = realizedValuation G e p (rowAtoms k j)) :
    CatalogueVec (fun j => v (rowAtoms k j)) := by
  obtain ⟨i, hi⟩ := exists_catalogue_mask_of_emitted_count_classified G hG e p hp1 k q r
    hqr_ne hqr hq hzero hcount er hroot hcoord
  refine ⟨i, fun j hj => ?_⟩
  show v (rowAtoms k j) = catalogueBit i j
  rw [hv j hj]
  exact hi ⟨j, hj⟩

/-- **Non-vacuous emitted readiness.** Readiness is proved at every valuation
that agrees on the sixteen physical support atoms, not merely at the original
physical valuation whose auxiliary guard is false.  The physical count and
geometry remain hypotheses; sequential exactness of the emitted counter is not
silently inferred from agreement on those atoms. -/
theorem senderStep_ready_of_atom_agreement_classified
    (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e (senderFin k) = q) (hzero : e zeroFin = r)
    (hcount : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (emittedCounterAtoms k i)) 41)
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val =
        (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val)
    (hb : VarsBelow (catalogueCNF (rowGuard k) (rowAtoms k) (rowSel k)) (rowNewTop k))
    (v : Valuation)
    (hv : ∀ j < 16, v (rowAtoms k j) = realizedValuation G e p (rowAtoms k j)) :
    (senderStep (rowOldTop k) (rowGuard k) (rowNewTop k) (rowAtoms k) (rowSel k)
      (by have := row_guard_le_old k; omega)
      (by have := row_old_le_new k; omega)
      (row_atoms_bound k) (row_sel_fresh k) (row_sel_injective k) hb).ready v := by
  rw [sender_family_ready k hb]
  intro _
  exact catalogueVec_of_atom_agreement_classified G hG e p hp1 k q r hqr_ne hqr hq hzero
    hcount er hroot hcoord v hv

#print axioms K58.R3Counter.exists_catalogue_mask_of_emitted_count_classified
#print axioms K58.R3Counter.catalogueVec_of_atom_agreement_classified
#print axioms K58.R3Counter.senderStep_ready_of_atom_agreement_classified
#print axioms K58.R3Counter.emitted_sender_step_ready_of_emitted_count_classified

end K58.R3Counter
