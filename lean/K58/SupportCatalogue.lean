/-
K58: exact finite support-catalogue semantics for the retained profile.

This is a *local* port of the K60 pattern-completeness idea
(`UniformK60/BalancedAnchorSupport.lean`, upstream commit 6c3f2fd0:
`p4_complete`, `c5_table_complete`) to the K58 named T16 coordinates.
Nothing is imported from the K60 host package: the finite lemmas below are
re-proved against `K58.template`, and they are proved about the *production*
list `targetSupports` of `lean/K58/TargetSuffix.lean`
(112 entries = 96 four-element + 16 five-element).

Physical reading (proved in `K58SupportTransport.lean`, not here): at a true
guarded sender `x` of the retained parent, the mask of its colour-1 support over
the root's arm-0 coordinates is

* independent in the marked colour 1 (two colour-1 neighbours of `x` would close
  a monochromatic triangle at `x`), and
* a colour-2 path on four vertices or a colour-2 five-cycle
  (`K58.pinned_support_shape`),

and `p4_complete` + `c5_complete` say exactly that such a mask is one of the 112
emitted entries.  The controls at the end record that neither hypothesis alone
suffices, that the path colour cannot be swapped, and that the T16 template is
not interchangeable with U16.
-/
import K58.Support
import K58.TargetSuffix

set_option autoImplicit false
namespace K58.SupportCatalogue
open K58

/-- The named mask of emitted catalogue entry `i`: the set of the 16 positions
that `targetSupports` entry `i` lists (empty for out-of-range `i`). -/
def patternNat (i : Nat) : Finset (Fin 16) :=
  Finset.univ.filter fun j => (targetSupports.getD i []).contains j.val

/-- `S` is one of the 112 emitted masks. -/
def inCatalogue (S : Finset (Fin 16)) : Bool :=
  (List.finRange 112).any fun i => decide (patternNat i = S)

/-- No internal edge of local colour 0 (= physical colour 1, the marked colour):
two colour-1 neighbours of the sender would close a monochromatic triangle. -/
def indep0 (S : Finset (Fin 16)) : Prop :=
  ∀ a ∈ S, ∀ b ∈ S, a ≠ b → (template 16 true).col a b ≠ 0

instance (S : Finset (Fin 16)) : Decidable (indep0 S) := by unfold indep0; infer_instance

/-! ### Facts about the emitted list itself -/

theorem targetSupports_length : targetSupports.length = 112 := by decide

theorem targetSupports_four_count :
    (targetSupports.filter fun s => s.length = 4).length = 96 := by decide

theorem targetSupports_five_count :
    (targetSupports.filter fun s => s.length = 5).length = 16 := by decide

theorem targetSupports_nodup : targetSupports.Nodup := by decide

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 0 in
/-- **Soundness of the emitted list**: every one of the 112 entries is a
marked-colour independent set of exactly four or five positions. -/
theorem catalogue_sound :
    (List.finRange 112).all (fun i =>
      decide (indep0 (patternNat i)) &&
        (decide ((patternNat i).card = 4) || decide ((patternNat i).card = 5))) = true := by
  decide +kernel

theorem patternNat_indep (i : Fin 112) : indep0 (patternNat i.val) := by
  have h := List.all_eq_true.mp catalogue_sound i (List.mem_finRange _)
  rw [Bool.and_eq_true] at h
  exact of_decide_eq_true h.1

theorem patternNat_card (i : Fin 112) :
    (patternNat i.val).card = 4 ∨ (patternNat i.val).card = 5 := by
  have h := List.all_eq_true.mp catalogue_sound i (List.mem_finRange _)
  rw [Bool.and_eq_true] at h
  rcases Bool.or_eq_true .. ▸ h.2 with h4 | h5
  · exact Or.inl (of_decide_eq_true h4)
  · exact Or.inr (of_decide_eq_true h5)

/-! ### Exact completeness: the K60 `p4_complete` / `c5_complete` port -/

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 0 in
/-- **P4 completeness.**  Any four positions whose six mutual colours are those
of a colour-1 path `a-b-d-e` with the three diagonals in colour 2 form one of the
emitted 96 four-element masks.  (The six equations already force distinctness:
a diagonal pair of `template` has colour 0 and cannot equal 1 or 2.) -/
theorem p4_complete : ∀ (a b d e : Fin 16),
    (template 16 true).col a b = 1 → (template 16 true).col b d = 1 →
    (template 16 true).col d e = 1 → (template 16 true).col a d = 2 →
    (template 16 true).col a e = 2 → (template 16 true).col b e = 2 →
    inCatalogue {a, b, d, e} = true := by
  decide +kernel

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 0 in
/-- The 16-position check behind five-set completeness: every five-element
subset of the T16 coordinates that is independent in the marked colour is one of
the emitted entries (the `support_check` shape of the K60 port). -/
theorem c5_check :
    ((List.finRange 16).sublistsLen 5).all
      (fun l => !(decide (indep0 l.toFinset)) || inCatalogue l.toFinset) = true := by
  decide +kernel

/-- **C5 completeness.**  Every five-element marked-independent subset of the
T16 coordinates is one of the emitted 16 five-element masks. -/
theorem c5_complete (S : Finset (Fin 16)) (hcard : S.card = 5) (hind : indep0 S) :
    inCatalogue S = true := by
  let l := (List.finRange 16).filter fun v => decide (v ∈ S)
  have hnd : l.Nodup := (List.nodup_finRange 16).filter _
  have htof : l.toFinset = S := by
    ext v
    simp [l]
  have hlen : l.length = 5 := by
    rw [← List.toFinset_card_of_nodup hnd, htof, hcard]
  have hmem : l ∈ (List.finRange 16).sublistsLen 5 :=
    List.mem_sublistsLen.mpr ⟨List.filter_sublist, hlen⟩
  have hh := List.all_eq_true.mp c5_check l hmem
  have hcond : (decide (indep0 l.toFinset)) = true := by
    rw [htof]; simp [hind]
  rw [hcond] at hh
  simp only [Bool.not_true, Bool.false_or] at hh
  rwa [htof] at hh

/-! ### Negative controls (all kernel-checked, none asserted by hand) -/

/-- Independence in the marked colour alone does not put a four-set in the
catalogue: `{0,2,9,11}` is marked-independent but its four colour-1 edges form a
four-cycle, not a path. -/
theorem control_indep_not_member :
    indep0 {0, 2, 9, 11} ∧ inCatalogue {0, 2, 9, 11} = false ∧
      ((template 16 true).col 0 2 = 1 ∧ (template 16 true).col 0 11 = 1 ∧
        (template 16 true).col 2 9 = 1 ∧ (template 16 true).col 9 11 = 1) := by
  decide

/-- The colour-1 path shape alone does not suffice: `{0,1,2,5}` carries a
colour-1 path `0-2-1-5` but contains a marked colour-0 edge `0-1`. -/
theorem control_path_with_marked_edge :
    ¬ indep0 {0, 1, 2, 5} ∧ inCatalogue {0, 1, 2, 5} = false ∧
      ((template 16 true).col 0 2 = 1 ∧ (template 16 true).col 2 1 = 1 ∧
        (template 16 true).col 1 5 = 1 ∧ (template 16 true).col 0 1 = 0) := by
  decide

/-- The path colour cannot be replaced by the other remaining colour:
`{0,1,4,8}` is a colour-2 path with no colour-1 edge, and is not an entry. -/
theorem control_wrong_path_colour :
    inCatalogue {0, 1, 4, 8} = false ∧
      ((template 16 true).col 0 1 = 0 ∧ (template 16 true).col 0 4 = 2 ∧
        (template 16 true).col 0 8 = 0 ∧ (template 16 true).col 1 4 = 2 ∧
        (template 16 true).col 1 8 = 2 ∧ (template 16 true).col 4 8 = 0) := by
  decide

/-- A one-bit change of a listed mask leaves the catalogue: the two 4-element
entries `{0,2,4,6}` and `{0,2,4,7}`, and a non-member `{0,2,4,8}`. -/
theorem control_single_bit :
    inCatalogue {0, 2, 4, 6} = true ∧ inCatalogue {0, 2, 4, 7} = true ∧
      inCatalogue {0, 2, 4, 8} = false := by decide

/-- The five-element branch needs the marked-independence hypothesis:
`{0,1,4,8,12}` is not an entry (and is not marked-independent). -/
theorem control_five_needs_indep :
    inCatalogue {0, 1, 4, 8, 12} = false ∧ ¬ indep0 {0, 1, 4, 8, 12} := by decide

/-- The template is not interchangeable: `{0,2,4,6}` *is* a T16 colour-1 path
(colour-1 edges `02, 26, 46`) but under the U16 template its colour-1 edges are
only `02, 46`, a matching rather than a path.  So the emitted list is not the
U16 pattern list. -/
theorem control_t16_not_u16 :
    inCatalogue {0, 2, 4, 6} = true ∧
      ((template 16 true).col 0 2 = 1 ∧ (template 16 true).col 2 6 = 1 ∧
        (template 16 true).col 4 6 = 1 ∧ (template 16 true).col 0 4 = 2 ∧
        (template 16 true).col 0 6 = 2 ∧ (template 16 true).col 2 4 = 2) ∧
      ((template 16 false).col 0 2 = 1 ∧ (template 16 false).col 4 6 = 1 ∧
        (template 16 false).col 2 6 = 2 ∧ (template 16 false).col 0 4 = 2 ∧
        (template 16 false).col 0 6 = 2 ∧ (template 16 false).col 2 4 = 2) := by
  decide

/-! ### The exact membership characterisation (both directions) -/

/-- Number of local-colour-`c` neighbours of `v` inside `S`. -/
def localDeg (S : Finset (Fin 16)) (c : Fin 3) (v : Fin 16) : Nat :=
  (S.filter fun w => decide (w ≠ v ∧ (template 16 true).col v w = c)).card

/-- Four positions whose colour-1 degrees are `1,1,2,2`, i.e. a path. -/
def pathDegrees (S : Finset (Fin 16)) : Bool :=
  decide (S.card = 4) && decide (∀ v ∈ S, localDeg S 1 v = 1 ∨ localDeg S 1 v = 2) &&
    decide ((S.filter fun v => decide (localDeg S 1 v = 1)).card = 2)

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 0 in
/-- The four-position check: marked independence plus colour-1 path degrees is
exactly catalogue membership on four-element sets. -/
theorem four_check :
    ((List.finRange 16).sublistsLen 4).all
      (fun l => !(decide (indep0 l.toFinset) && pathDegrees l.toFinset) ||
        inCatalogue l.toFinset) = true := by
  decide +kernel

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 0 in
/-- Soundness of the shape predicate on the emitted four-element entries. -/
theorem catalogue_pathDegrees :
    (List.finRange 112).all (fun i =>
      !(decide ((patternNat i).card = 4)) || pathDegrees (patternNat i)) = true := by
  decide +kernel

theorem patternNat_pathDegrees (i : Fin 112) (h4 : (patternNat i.val).card = 4) :
    pathDegrees (patternNat i.val) = true := by
  have h := List.all_eq_true.mp catalogue_pathDegrees i (List.mem_finRange i)
  have hc : (decide ((patternNat i.val).card = 4)) = true := by
    simp [h4]
  simpa [hc] using h

/-- **Completeness in set form.**  A marked-independent subset of the T16
coordinates with four path-shaped or five elements is an emitted mask. -/
theorem catalogue_complete (S : Finset (Fin 16)) (hind : indep0 S)
    (hcard : S.card = 4 ∨ S.card = 5) (h4 : S.card = 4 → pathDegrees S = true) :
    inCatalogue S = true := by
  rcases hcard with hc | hc
  · -- four elements: transfer through the four-sublist check
    let l := (List.finRange 16).filter fun v => decide (v ∈ S)
    have hnd : l.Nodup := (List.nodup_finRange 16).filter _
    have htof : l.toFinset = S := by
      ext v; simp [l]
    have hlen : l.length = 4 := by
      rw [← List.toFinset_card_of_nodup hnd, htof, hc]
    have hmem : l ∈ (List.finRange 16).sublistsLen 4 :=
      List.mem_sublistsLen.mpr ⟨List.filter_sublist, hlen⟩
    have hh := List.all_eq_true.mp four_check l hmem
    have hcond : (decide (indep0 l.toFinset) && pathDegrees l.toFinset) = true := by
      rw [htof]
      have hi : (decide (indep0 S)) = true := by simp [hind]
      have hp : pathDegrees S = true := h4 hc
      simp [hi, hp]
    rw [hcond] at hh
    simp only [Bool.not_true, Bool.false_or] at hh
    rwa [htof] at hh
  · exact c5_complete S hc hind

/-- **The exact finite semantics.**  On subsets of the T16 coordinates of size
four or five, being an emitted mask is *equivalent* to marked-colour
independence together with the colour-1 path condition (four) resp. nothing
further (five). -/
theorem catalogue_iff (S : Finset (Fin 16)) (hcard : S.card = 4 ∨ S.card = 5) :
    inCatalogue S = true ↔ indep0 S ∧ (S.card = 4 → pathDegrees S = true) := by
  constructor
  · intro hcat
    obtain ⟨i, -, hi⟩ := List.any_eq_true.mp hcat
    have hpat : patternNat i.val = S := of_decide_eq_true hi
    refine ⟨?_, ?_⟩
    · rw [← hpat]; exact patternNat_indep i
    · intro h4
      have h4' : (patternNat i.val).card = 4 := hpat.symm ▸ h4
      rw [← hpat]
      exact patternNat_pathDegrees i h4'
  · rintro ⟨hind, h4⟩
    exact catalogue_complete S hind hcard h4

end K58.SupportCatalogue
