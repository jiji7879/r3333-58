/- Kernel-checked literal-colour critical-template classification.

Adapted from m4 / swarm smx0gue0b / direction d5.

The `hclass` hypothesis of `sender_pinned_of_count` and of
`emitted_sender_step_ready_of_count` is *proved*, not assumed, from
`K58.classified_15` / `K58.classified_16` (the pinned R4333Lean catalogue
completeness results) plus the two template palette-symmetry theorems.
It remains intentionally separate from the physical count-to-neighbour step.
-/
import K58.EmittedBridge
import K58.Classification
import K58.Palette

set_option autoImplicit false

namespace K58.EmittedBridge

open K58
open K58.SenderReady
open K58.SemanticAssembly

/-- Colour-permutation elimination: `Classified n` (template up to vertex *and
colour* relabelling) plus colour symmetry of the template gives the template up
to vertex relabelling alone.  `K58.Marking.named_of_palette` is the private
version of this argument; this one is public and stated for reuse. -/
theorem named_of_classified {n : ℕ} (hc : Classified n)
    (hp : ∀ t (p : Equiv.Perm (Fin 3)), ∃ e : Equiv.Perm (Fin n),
      ∀ i j, i ≠ j → (template n t).col (e i) (e j) = p ((template n t).col i j)) :
    ∀ C : EdgeCol (Fin n) 3, TriangleFree C →
      ∃ t : Bool, ∃ e : Equiv.Perm (Fin n), ∀ i j, i ≠ j →
        C.col i j = (template n t).col (e i) (e j) := by
  intro C hC
  obtain ⟨t, v, p, hv⟩ := hc C hC
  obtain ⟨e, he⟩ := hp t p
  exact ⟨t, v.trans e, fun i j hij => (hv i j hij).trans (he _ _ (v.injective.ne hij)).symm⟩

/-- Order 15 in literal host colours. -/
theorem named_15 :
    ∀ C : EdgeCol (Fin 15) 3, TriangleFree C →
      ∃ t : Bool, ∃ e : Equiv.Perm (Fin 15), ∀ i j, i ≠ j →
        C.col i j = (template 15 t).col (e i) (e j) :=
  named_of_classified classified_15 palette_15

/-- Order 16 in literal host colours. -/
theorem named_16 :
    ∀ C : EdgeCol (Fin 16) 3, TriangleFree C →
      ∃ t : Bool, ∃ e : Equiv.Perm (Fin 16), ∀ i j, i ≠ j →
        C.col i j = (template 16 t).col (e i) (e j) :=
  named_of_classified classified_16 (fun t p => by
    obtain ⟨e, -, he⟩ := palette_16_fixing t p 0
    exact ⟨e, he⟩)

/-- **The `hclass` hypothesis of the bridge, discharged.**  Type copied verbatim
from the source of `sender_pinned_of_count`. -/
theorem hclass_classified :
    ∀ n : ℕ, n = 15 ∨ n = 16 → ∀ C : EdgeCol (Fin n) 3, TriangleFree C →
      ∃ t : Bool, ∃ e : Equiv.Perm (Fin n), ∀ i j, i ≠ j →
        C.col i j = (template n t).col (e i) (e j) := by
  intro n hn
  rcases hn with rfl | rfl
  · exact named_15
  · exact named_16

/-- `sender_pinned_of_count` without the classification hypothesis. -/
theorem sender_pinned_of_count_of_classification (G : EdgeCol (Fin 58) 4)
    (hG : TriangleFree G) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (W : Finset (Fin 58)) (hW : ∀ x ∈ W, x ≠ q ∧ G.col q x = 1) (hrW : r ∉ W)
    (hcard : 14 ≤ W.card) :
    Sends G q r ∧ deg G q 1 ≤ 16 ∧ ∃ t : Bool, PinnedArm G q 1 (deg G q 1) t :=
  sender_pinned_of_count G hG q r hqr_ne hqr W hW hrW hcard hclass_classified

/-- `emitted_sender_step_ready_of_count` without the classification hypothesis:
same statement, one argument fewer. -/
theorem emitted_sender_step_ready_of_count_of_classification
    (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e ⟨18 + k.val, by omega⟩ = q)
    (W : Finset (Fin 58)) (hW : ∀ x ∈ W, x ≠ q ∧ G.col q x = 1) (hrW : r ∉ W)
    (hcard : 14 ≤ W.card)
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val = (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val)
    (hb : VarsBelow (catalogueCNF (rowGuard k) (rowAtoms k) (rowSel k)) (rowNewTop k)) :
    (senderStep (rowOldTop k) (rowGuard k) (rowNewTop k) (rowAtoms k) (rowSel k)
      (by have := row_guard_le_old k; omega)
      (by have := row_old_le_new k; omega)
      (row_atoms_bound k) (row_sel_fresh k) (row_sel_injective k) hb).ready
      (realizedValuation G e p) :=
  emitted_sender_step_ready_of_count G hG e p hp1 k q r hqr_ne hqr hq
    W hW hrW hcard hclass_classified er hroot hcoord hb

#print axioms K58.EmittedBridge.named_of_classified
#print axioms K58.EmittedBridge.named_15
#print axioms K58.EmittedBridge.named_16
#print axioms K58.EmittedBridge.hclass_classified
#print axioms K58.EmittedBridge.sender_pinned_of_count_of_classification
#print axioms K58.EmittedBridge.emitted_sender_step_ready_of_count_of_classification

end K58.EmittedBridge
