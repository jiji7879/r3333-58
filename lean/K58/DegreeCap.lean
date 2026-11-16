/-
K58: the colour-degree cap.  A triangle-free 4-colouring has every colour
degree at most 16, because a colour class is a triangle-free 3-colouring.
-/
import K58.ThreeColour

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- In a triangle-free 4-colouring, `deg i a ≤ 16`. -/
theorem deg_le_sixteen (G : EdgeCol V 4) (h : TriangleFree G) (i : V) (a : Fin 4) :
    deg G i a ≤ 16 := by
  by_contra hle
  simp only [not_le] at hle
  set S : Finset V := Finset.univ.filter (fun j : V => j ≠ i ∧ G.col i j = a) with hS
  have hScard : S.card = deg G i a := by rw [hS, deg]
  obtain ⟨T, hTS, hTcard⟩ := Finset.exists_subset_card_eq (show 17 ≤ S.card by omega)
  have hT17 : T.card = 17 := hTcard
  have hmem : ∀ x ∈ T, x ≠ i ∧ G.col i x = a := by
    intro x hx
    have hx' : x ∈ S := hTS hx
    simpa [hS] using hx'
  have hne : ∀ x ∈ T, ∀ y ∈ T, x ≠ y → G.col x y ≠ a := by
    intro x hx y hy hxy hc
    have hx' := hmem x hx
    have hy' := hmem y hy
    exact h i x y (Ne.symm hx'.1) hxy (Ne.symm hy'.1)
      ⟨by rw [hx'.2, hy'.2], by rw [hy'.2, hc]⟩
  -- the three colours other than `a`, indexed by `Fin 3`
  have hcard : Fintype.card {c : Fin 4 // c ≠ a} = 3 := by
    have h1 : Fintype.card {c : Fin 4 // c = a} = 1 := Fintype.card_subtype_eq a
    have h2 := Fintype.card_subtype_compl (fun c : Fin 4 => c = a)
    rw [h1, Fintype.card_fin] at h2
    simp only [h2]
  let φ : {c : Fin 4 // c ≠ a} ≃ Fin 3 := Fintype.equivFinOfCardEq hcard
  let G3 : EdgeCol ↥T 3 :=
    { col := fun p q =>
        if hpq : p = q then 0
        else φ ⟨G.col p.1 q.1, hne p.1 p.2 q.1 q.2 (fun hh => hpq (Subtype.ext hh))⟩
      symm := by
        intro p q
        by_cases hpq : p = q
        · subst hpq; simp
        · have hqp : q ≠ p := Ne.symm hpq
          rw [dif_neg hpq, dif_neg hqp]
          congr 1
          exact Subtype.ext (G.symm p.1 q.1) }
  have h3 : TriangleFree G3 := by
    intro p q r hpq hqr hpr hmono
    have hpq' : ¬ (p = q) := hpq
    have hqr' : ¬ (q = r) := hqr
    have hpr' : ¬ (p = r) := hpr
    simp only [G3, dif_neg hpq', dif_neg hqr', dif_neg hpr'] at hmono
    have e1 : G.col p.1 q.1 = G.col p.1 r.1 := by
      have hh := congrArg Subtype.val (φ.injective hmono.1)
      simpa using hh
    have e2 : G.col p.1 r.1 = G.col q.1 r.1 := by
      have hh := congrArg Subtype.val (φ.injective hmono.2)
      simpa using hh
    have hpq2 : p.1 ≠ q.1 := fun hh => hpq (Subtype.ext hh)
    have hqr2 : q.1 ≠ r.1 := fun hh => hqr (Subtype.ext hh)
    have hpr2 : p.1 ≠ r.1 := fun hh => hpr (Subtype.ext hh)
    exact h p.1 q.1 r.1 hpq2 hqr2 hpr2 ⟨e1, e2⟩
  exact three_colour_seventeen G3 (by simp [Fintype.card_coe, hT17]) h3

end K58
