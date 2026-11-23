import K58.Templates
import K58.Reduction
import Mathlib.Logic.Equiv.Fin.Basic

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

def arm (G : EdgeCol V 4) (r : V) (a : Fin 4) : Finset V :=
  Finset.univ.filter fun q => q ≠ r ∧ G.col r q = a

/-- A sufficiently large set of positions in an arm contains a sender to the root. -/
theorem marked_sender (G : EdgeCol V 4) (r : V) (a : Fin 4) (t : ℕ) (M : Finset V)
    (hM : M ⊆ arm G r a) (hm : deg G r a - t + 1 ≤ M.card)
    (ht : t ≤ armSenders G r a) : ∃ q ∈ M, Sends G q r := by
  let S := Finset.univ.filter fun q => r ≠ q ∧ G.col r q = a ∧ 15 ≤ deg G q (G.col q r)
  have hsub : S ⊆ arm G r a := by
    intro q hq
    obtain ⟨hrq, hcol, _⟩ := (Finset.mem_filter.mp hq).2
    exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, hrq.symm, hcol⟩
  change t ≤ S.card at ht
  change (arm G r a).card - t + 1 ≤ M.card at hm
  obtain ⟨q, hq⟩ := Finset.inter_nonempty_of_card_lt_card_add_card hM hsub (by omega)
  obtain ⟨hqm, hqs⟩ := Finset.mem_inter.mp hq
  obtain ⟨hrq, _, hcrit⟩ := (Finset.mem_filter.mp hqs).2
  exact ⟨q, hqm, hrq, hcrit⟩

/-- A named copy uses the three remaining host colours in increasing order. -/
def PinnedArm (G : EdgeCol V 4) (r : V) (a : Fin 4) (n : ℕ) (t : Bool) : Prop :=
  ∃ e : ↥(arm G r a) ≃ Fin n, ∀ x y, x ≠ y →
    G.col x.val y.val = a.succAbove ((template n t).col (e x) (e y))

/-- Restrict to a critical neighbourhood, given a classification with literal colours. -/
theorem pin_of_named_classification {n : ℕ}
    (hclass : ∀ C : EdgeCol (Fin n) 3, TriangleFree C →
      ∃ t : Bool, ∃ e : Equiv.Perm (Fin n), ∀ i j, i ≠ j →
        C.col i j = (template n t).col (e i) (e j))
    (G : EdgeCol V 4) (hG : TriangleFree G) (r : V) (a : Fin 4) (hd : deg G r a = n) :
    ∃ t, PinnedArm G r a n t := by
  let B := arm G r a
  let v : ↥B ≃ Fin n := Fintype.equivFinOfCardEq ((Fintype.card_coe B).trans hd)
  have avoid (x y : ↥B) (hxy : x ≠ y) : G.col x.val y.val ≠ a := by
    obtain ⟨hxr, hx⟩ := (Finset.mem_filter.mp x.property).2
    obtain ⟨hyr, hy⟩ := (Finset.mem_filter.mp y.property).2
    intro h
    exact hG r x.val y.val hxr.symm (fun q => hxy (Subtype.ext q)) hyr.symm
      ⟨hx.trans hy.symm, hy.trans h.symm⟩
  let C : EdgeCol (Fin n) 3 := {
    col := fun i j => if h : i = j then 0 else
      (finSuccAboveEquiv a).symm ⟨G.col (v.symm i).val (v.symm j).val,
        avoid _ _ (v.symm.injective.ne h)⟩
    symm := by
      intro i j
      by_cases h : i = j
      · subst j; rfl
      · simp only [dif_neg h, dif_neg (Ne.symm h)]
        apply congrArg (finSuccAboveEquiv a).symm
        exact Subtype.ext (G.symm _ _) }
  have edge (i j : Fin n) (h : i ≠ j) :
      a.succAbove (C.col i j) = G.col (v.symm i).val (v.symm j).val := by
    simp only [C, dif_neg h]
    exact congrArg Subtype.val ((finSuccAboveEquiv a).apply_symm_apply _)
  have hC : TriangleFree C := by
    intro i j k hij hjk hik hmono
    apply hG _ _ _ (fun h => hij (v.symm.injective (Subtype.ext h)))
      (fun h => hjk (v.symm.injective (Subtype.ext h)))
      (fun h => hik (v.symm.injective (Subtype.ext h)))
    rw [← edge i j hij, ← edge i k hik, ← edge j k hjk]
    exact ⟨congrArg _ hmono.1, congrArg _ hmono.2⟩
  obtain ⟨t, e, he⟩ := hclass C hC
  refine ⟨t, v.trans e, ?_⟩
  intro x y hxy
  have hz := edge (v x) (v y) (v.injective.ne hxy)
  rw [he _ _ (v.injective.ne hxy)] at hz
  simpa only [Equiv.symm_apply_apply, Equiv.trans_apply] using hz.symm

end K58
