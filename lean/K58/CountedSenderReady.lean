import K58.CounterNeighboursAudit2
import K58.ClassifiedBridge
import K58.SequentialCounter

/-! Count-driven physical support readiness at all fifteen retained senders.

`K58.R3Counter` decodes the exact counter inputs and constructs a genuine
physical neighbour finset.  `K58.EmittedBridge.hclass_classified` supplies the
literal-colour order-15/16 critical classification.  This module combines them:
no neighbour set `W`, its premises, or a separate `hclass` argument is needed.

The conclusion is at the ordinary physical valuation.  It is NOT yet uniformity
at every valuation satisfying a sequentially emitted counter, nor is it a
`ChainReady` theorem, an exact-root/key bookkeeping completion, or a Ramsey
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

#print axioms K58.R3Counter.emitted_sender_step_ready_of_emitted_count_classified

end K58.R3Counter
