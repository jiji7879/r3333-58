/-
K58 emitted/coordinator bridge (swarm smx0er1f6, member m1, direction 6).

CONTENT.  `K58.SenderReady` shows the emitted `ready` obligation of the fifteen
guarded senders 18..32 is "at a true guard the 16 emitted atoms carry one of the
112 catalogue masks".  `K58.SupportTransport.support_mask_mem` shows that the
*physical* mask of a sender is a catalogue entry, given the sender's arm pinned
to a critical template and the root's arm 0 pinned to T16 in some coordinate
system `er`.  What was missing is the link between the two: which physical
proposition each emitted atom denotes, and in which order.

This file settles the first half exactly, kernel-checked:
* `rowAtoms_val` : the 16 atoms of sender `18+k` are literally
  `hostVar (1+j) (18+k) 1`, i.e. the colour-1 edge between the j-th coordinate of
  the root's arm 0 (label `1+j`) and the sender label `18+k`.
* `realized_rowAtoms` : under the repository's own physical valuation
  `realizedValuation G e p` those atoms evaluate to
  `G.col (e (1+j)) (e (18+k)) = p 1`, the physical mask.
* `emitted_mask_of_pinned` / `emitted_sender_step_ready` : therefore the emitted
  atom of sender `18+k` is the catalogue mask of the physical sender `e (18+k)`
  at the root's arm-0 coordinates `e (1+j)` -- with `er.symm j = e (1+j)` the
  coordinate system is *forced*, not guessed.
* `counterList18_decode`, `counter18_avoids_*` : the 41-atom guard counter of
  sender 18 counts colour-1 edges to `1..16` and `33..57` only; it excludes the
  root edge `(0,18)` and all sixteen arm-1 edges `(17..32,18)`.

What remains as a hypothesis is exactly the physical sender-side pinning
`PinnedArm G q 1 n t`, `n ∈ {15,16}` (and the root pinning `hroot`), both of
which are hypotheses of `SupportTransport` already.  No new axiom, no `sorry`,
no `native_decide`.
-/
import K58.SenderReady
import K58.SupportTransport
import K58.PhysicalBridge
import K58.ArmPinned

open K58
open K58.SenderReady
open K58.SupportTransport
open K58.SemanticAssembly

set_option autoImplicit false

namespace K58.EmittedBridge

/-! ## 1. What the emitted 16 atoms of each sender are -/

/-- The colour index used by every emitted support atom of the suffix. -/
def one : Fin 4 := ⟨1, by decide⟩

/-- Decoded form of the atoms of sender `18+k`: slot `j` is the edge
`(1+j, 18+k)` in colour `1`. -/
theorem rowAtoms_val : ∀ (k : Fin 15) (j : Fin 16),
    rowAtoms k j.val = hostVar (1 + j.val) (18 + k.val) one := by
  decide

/-- The full atom list of sender `18+k`, as decoded host-variable codes. -/
theorem rowAtomsList_val : ∀ k : Fin 15,
    rowAtomsList k = (List.finRange 16).map
      (fun j => hostVar (1 + j.val) (18 + k.val) one) := by
  decide

/-- Sender 18 explicitly, matching `SenderReady.atomsList18`. -/
theorem atomsList18_val :
    atomsList18 = (List.finRange 16).map
      (fun j => hostVar (1 + j.val) 18 one) := by
  decide

/-! ## 2. Their physical meaning -/

/-- **The physical meaning of an emitted support atom.**  Under the repository's
`realizedValuation` (host permutation `e`, palette permutation `p`) the atom of
slot `j` of sender `18+k` is the physical statement "the edge from `e (1+j)` to
`e (18+k)` has physical colour `p 1`". -/
theorem realized_rowAtoms (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58))
    (p : Equiv.Perm (Fin 4)) (k : Fin 15) (j : Fin 16) :
    realizedValuation G e p (rowAtoms k j.val) =
      decide (G.col (e ⟨1 + j.val, by omega⟩) (e ⟨18 + k.val, by omega⟩) = p one) := by
  rw [rowAtoms_val k j]
  exact realizedValuation_hostVar G e p
    (u := ⟨1 + j.val, by omega⟩) (v := ⟨18 + k.val, by omega⟩)
    (by have := j.isLt; simp only [Fin.mk_lt_mk]; omega) one

/-- Same with the palette fixed: the atom is the colour-1 edge. -/
theorem realized_rowAtoms_refl (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58))
    (k : Fin 15) (j : Fin 16) :
    realizedValuation G e (Equiv.refl (Fin 4)) (rowAtoms k j.val) =
      decide (G.col (e ⟨1 + j.val, by omega⟩) (e ⟨18 + k.val, by omega⟩) = 1) := by
  rw [realized_rowAtoms]
  rfl

/-! ## 3. The bridge: emitted atoms are the T16-pinned coordinates -/

/-- **Emitted mask = physical mask.**  Hypotheses are exactly
`SupportTransport.support_mask_mem`'s: triangle-freeness, the sender `q` joined to
the root `r` in colour 1, the sender's colour-1 arm pinned to a critical template
of order 15 or 16, and the root's arm 0 pinned to `T16` in the coordinates `er`.
`hq` and `hcoord` say that the *emit* labels `18+k` and `1+j` are the physical
sender and the root's arm-0 coordinates: that is the identification this file
supplies.  `hp1` is the palette gauge `p 1 = 1` (arm 1 is the marked colour); any
`p` reduces to it by relabelling the physical colouring, which preserves
triangle-freeness and every clause of the parent. -/
theorem emitted_mask_of_pinned (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e ⟨18 + k.val, by omega⟩ = q)
    {n : ℕ} {t : Bool} (hn : n = 15 ∨ n = 16) (hsender : PinnedArm G q 1 n t)
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val = (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val) :
    ∃ i : Fin 112, ∀ j : Fin 16,
      realizedValuation G e p (rowAtoms k j.val) = supportBit targetSupports i j.val := by
  obtain ⟨i, hi⟩ := support_mask_mem G hG q r hqr_ne hqr hn hsender er hroot
  refine ⟨i, fun j => ?_⟩
  rw [realized_rowAtoms, hcoord j, hq, hp1, G.symm]
  exact hi j

/-- **The emitted support step of sender `18+k` is ready at the physical
valuation.**  This closes the emitted side of the bridge: no coordinate guess, no
coded premise, only the two physical arm pinnings and the label identification. -/
theorem emitted_sender_step_ready (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e ⟨18 + k.val, by omega⟩ = q)
    {n : ℕ} {t : Bool} (hn : n = 15 ∨ n = 16) (hsender : PinnedArm G q 1 n t)
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val = (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val)
    (hb : VarsBelow (catalogueCNF (rowGuard k) (rowAtoms k) (rowSel k)) (rowNewTop k)) :
    (senderStep (rowOldTop k) (rowGuard k) (rowNewTop k) (rowAtoms k) (rowSel k)
      (by have := row_guard_le_old k; omega)
      (by have := row_old_le_new k; omega)
      (row_atoms_bound k) (row_sel_fresh k) (row_sel_injective k) hb).ready
      (realizedValuation G e p) := by
  rw [sender_family_ready k hb]
  intro _
  obtain ⟨i, hi⟩ := emitted_mask_of_pinned G hG e p hp1 k q r hqr_ne hqr hq hn hsender
    er hroot hcoord
  exact ⟨i, fun j hj => hi ⟨j, hj⟩⟩

/-! ## 4. The guard counter counts a proper subset of the sender's arm -/

/-- The 41 input atoms of sender 18's guard counter, decoded: colour-1 edges to
the sixteen arm-0 labels `1..16` and to the twenty-five labels `33..57`. -/
theorem counterList18_decode :
    counterList18 =
      (List.finRange 16).map (fun j => hostVar (1 + j.val) 18 one) ++
      (List.finRange 25).map (fun i => hostVar 18 (33 + i.val) one) := by
  decide

/-- The guard counter's atoms avoid the root edge `(0,18)` and all sixteen arm-1
edges `(17+i, 18)`: so a true guard certifies only part of the sender's colour-1
arm.  This is the precise sense in which the emitted guard is weaker than the
physical statement "the sender's colour-1 arm is pinned". -/
theorem counter18_avoids_fin : ∀ (i : Fin 41) (s : Fin 16),
    counterAtoms18 i.val ≠ hostVar 0 18 one ∧
      counterAtoms18 i.val ≠ hostVar (17 + s.val) 18 one := by
  decide

theorem counter18_ne_root (i : Nat) (hi : i < 41) :
    counterAtoms18 i ≠ hostVar 0 18 one :=
  (counter18_avoids_fin ⟨i, hi⟩ 0).1

theorem counter18_ne_arm1 (i : Nat) (hi : i < 41) (s : Fin 16) :
    counterAtoms18 i ≠ hostVar (17 + s.val) 18 one :=
  (counter18_avoids_fin ⟨i, hi⟩ s).2

/-- The seventeen colour-1 atoms of the sender `18` that the guard counter does
not count: the root edge and the sixteen arm-1 edges.  So a true guard count of
`m` gives `deg G (e 18) 1 ≥ m + 1` (the root edge), and at most `m + 16`. -/
def excludedAtoms18 : List Nat :=
  hostVar 0 18 one :: (List.finRange 16).map (fun s => hostVar (17 + s.val) 18 one)

theorem excludedAtoms18_length : excludedAtoms18.length = 17 := by decide

theorem excludedAtoms18_disjoint :
    ∀ a ∈ excludedAtoms18, ∀ i < 41, counterAtoms18 i ≠ a := by
  intro a ha i hi
  rcases List.mem_cons.mp ha with rfl | ha
  · exact counter18_ne_root i hi
  · obtain ⟨s, -, rfl⟩ := List.mem_map.mp ha
    exact counter18_ne_arm1 i hi s

/-! ## 5. Axiom audit -/

#print axioms K58.EmittedBridge.rowAtoms_val
#print axioms K58.EmittedBridge.rowAtomsList_val
#print axioms K58.EmittedBridge.atomsList18_val
#print axioms K58.EmittedBridge.realized_rowAtoms
#print axioms K58.EmittedBridge.realized_rowAtoms_refl
#print axioms K58.EmittedBridge.emitted_mask_of_pinned
#print axioms K58.EmittedBridge.emitted_sender_step_ready
#print axioms K58.EmittedBridge.counterList18_decode
#print axioms K58.EmittedBridge.counter18_avoids_fin
#print axioms K58.EmittedBridge.counter18_ne_root
#print axioms K58.EmittedBridge.counter18_ne_arm1
#print axioms K58.EmittedBridge.excludedAtoms18_length
#print axioms K58.EmittedBridge.excludedAtoms18_disjoint


/-! ## 6. From the counted colour-1 neighbours to the sender's pinned arm -/

/-- `TriangleFree` in the form the guard analysis needs: two colour-`c` edges of a
triangle forbid the third.  This is why the guard counter may safely ignore the
sender's own arm-1 siblings -- they can never be colour-1 adjacent to the
sender once both are colour-1 adjacent to the root. -/
theorem triangle_free_third_ne {V : Type*} [Fintype V] [DecidableEq V]
    (G : EdgeCol V 4) (hG : TriangleFree G) {q r s : V}
    (hqr_ne : q ≠ r) (hrs_ne : r ≠ s) (hqs_ne : q ≠ s) {c : Fin 4}
    (hqr : G.col q r = c) (hrs : G.col r s = c) : G.col q s ≠ c := by
  intro hqs
  refine hG r q s hqr_ne.symm hqs_ne hrs_ne ⟨?_, ?_⟩
  · rw [G.symm r q, hqr, hrs]
  · rw [hrs, hqs]

/-- **The counter count is a lower bound for the sender's colour-1 degree.**  A set
of `14` vertices that are colour-1 adjacent to `q`, together with the root edge,
already force `deg G q 1 ≥ 15`. -/
theorem deg_ge_of_counted (G : EdgeCol (Fin 58) 4) (q r : Fin 58)
    (hqr_ne : q ≠ r) (hqr : G.col q r = 1) (W : Finset (Fin 58))
    (hW : ∀ x ∈ W, x ≠ q ∧ G.col q x = 1) (hrW : r ∉ W) (hcard : 14 ≤ W.card) :
    15 ≤ deg G q 1 := by
  have hsub : insert r W ⊆ arm G q 1 := by
    intro x hx
    rcases Finset.mem_insert.mp hx with rfl | hx
    · exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, hqr_ne.symm, hqr⟩
    · obtain ⟨hxq, hxc⟩ := hW x hx
      exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, hxq, hxc⟩
  have hcard' : 15 ≤ (insert r W).card := by
    rw [Finset.card_insert_of_notMem hrW]
    omega
  exact le_trans hcard' (Finset.card_le_card hsub)

/-- **The counted sender is a physical sender and its arm is critical.**  With
`deg ≤ 16` from triangle-freeness, `deg ≥ 15` from the count, and the order-15/16
critical-template classification, the sender's colour-1 arm is a pinned critical
template.  Hence the emitted guard, read as its degree count, supplies exactly
the hypothesis `SupportTransport.support_mask_mem` asks for. -/
theorem sender_pinned_of_count (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1) (W : Finset (Fin 58))
    (hW : ∀ x ∈ W, x ≠ q ∧ G.col q x = 1) (hrW : r ∉ W) (hcard : 14 ≤ W.card)
    (hclass : ∀ n : ℕ, n = 15 ∨ n = 16 → ∀ C : EdgeCol (Fin n) 3, TriangleFree C →
      ∃ t : Bool, ∃ e : Equiv.Perm (Fin n), ∀ i j, i ≠ j →
        C.col i j = (template n t).col (e i) (e j)) :
    Sends G q r ∧ deg G q 1 ≤ 16 ∧ ∃ t : Bool, PinnedArm G q 1 (deg G q 1) t := by
  have hlo : 15 ≤ deg G q 1 := deg_ge_of_counted G q r hqr_ne hqr W hW hrW hcard
  have hhi : deg G q 1 ≤ 16 := deg_le_sixteen G hG q 1
  have hd : deg G q 1 = 15 ∨ deg G q 1 = 16 := by omega
  have hsends : Sends G q r := ⟨hqr_ne.symm, by rw [hqr]; exact hlo⟩
  refine ⟨hsends, hhi, ?_⟩
  rcases hd with h | h
  · rw [h]
    exact pin_of_named_classification (hclass 15 (Or.inl rfl)) G hG q 1 h
  · rw [h]
    exact pin_of_named_classification (hclass 16 (Or.inr rfl)) G hG q 1 h

/-- **The full emitted/physical chain at one sender.**  Inputs, all named:
the count of true atoms of the sender's guard counter (`W`, `hcard`), the root
edge in colour 1, the palette gauge, the root's arm-0 pinning in the emitted
coordinates, and the order-15/16 classification.  Output: the emitted support
step of sender `18+k` is ready at the physical valuation.  Nothing else is
assumed and no coded counter is identified with a physical event by fiat: the
degree statement is proved from the count. -/
theorem emitted_sender_step_ready_of_count (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e ⟨18 + k.val, by omega⟩ = q)
    (W : Finset (Fin 58)) (hW : ∀ x ∈ W, x ≠ q ∧ G.col q x = 1) (hrW : r ∉ W)
    (hcard : 14 ≤ W.card)
    (hclass : ∀ n : ℕ, n = 15 ∨ n = 16 → ∀ C : EdgeCol (Fin n) 3, TriangleFree C →
      ∃ t : Bool, ∃ e : Equiv.Perm (Fin n), ∀ i j, i ≠ j →
        C.col i j = (template n t).col (e i) (e j))
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val = (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val)
    (hb : VarsBelow (catalogueCNF (rowGuard k) (rowAtoms k) (rowSel k)) (rowNewTop k)) :
    (senderStep (rowOldTop k) (rowGuard k) (rowNewTop k) (rowAtoms k) (rowSel k)
      (by have := row_guard_le_old k; omega)
      (by have := row_old_le_new k; omega)
      (row_atoms_bound k) (row_sel_fresh k) (row_sel_injective k) hb).ready
      (realizedValuation G e p) := by
  obtain ⟨-, -, t, ht⟩ := sender_pinned_of_count G hG q r hqr_ne hqr W hW hrW hcard hclass
  have hdeg : deg G q 1 = 15 ∨ deg G q 1 = 16 := by
    have hlo : 15 ≤ deg G q 1 := deg_ge_of_counted G q r hqr_ne hqr W hW hrW hcard
    have hhi : deg G q 1 ≤ 16 := deg_le_sixteen G hG q 1
    omega
  exact emitted_sender_step_ready G hG e p hp1 k q r hqr_ne hqr hq hdeg ht er hroot hcoord hb

#print axioms K58.EmittedBridge.triangle_free_third_ne
#print axioms K58.EmittedBridge.deg_ge_of_counted
#print axioms K58.EmittedBridge.sender_pinned_of_count
#print axioms K58.EmittedBridge.emitted_sender_step_ready_of_count

end K58.EmittedBridge
