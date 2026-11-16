/-
K58: `R(3,3,3) ≤ 17`, hence every colour-degree in a triangle-free
4-colouring is at most 16.
-/
import K58.TwoColour

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- `R(3,3,3) ≤ 17`: no triangle-free 3-colouring of a seventeen-point set. -/
theorem three_colour_seventeen (G : EdgeCol V 3) (hV : Fintype.card V = 17)
    (h : TriangleFree G) : False := by
  have : Nonempty V := Fintype.card_pos_iff.mp (by omega)
  set v : V := Classical.arbitrary V with hv
  -- some colour class at `v` has at least six points
  have hsum := sum_deg G v
  rw [Fin.sum_univ_three, hV] at hsum
  have hex : ∃ a : Fin 3, 6 ≤ deg G v a := by
    by_contra hc
    simp only [not_exists, not_le] at hc
    have h0 := hc 0
    have h1 := hc 1
    have h2 := hc 2
    omega
  obtain ⟨a, ha⟩ := hex
  set S : Finset V := Finset.univ.filter (fun j : V => j ≠ v ∧ G.col v j = a) with hS
  have hScard : S.card = deg G v a := by
    rw [hS, deg]
  obtain ⟨T, hTS, hTcard⟩ := Finset.exists_subset_card_eq (show 6 ≤ S.card by omega)
  have hT6 : T.card = 6 := hTcard
  -- the points of `T` are `a`-neighbours of `v`, so edges inside `T` avoid `a`
  have hmem : ∀ x ∈ T, x ≠ v ∧ G.col v x = a := by
    intro x hx
    have hx' : x ∈ S := hTS hx
    simpa [hS] using hx'
  have hne : ∀ x ∈ T, ∀ y ∈ T, x ≠ y → G.col x y ≠ a := by
    intro x hx y hy hxy hc
    have hx' := hmem x hx
    have hy' := hmem y hy
    exact h v x y (Ne.symm hx'.1) hxy (Ne.symm hy'.1)
      ⟨by rw [hx'.2, hy'.2], by rw [hy'.2, hc]⟩
  -- the two colours other than `a`, indexed by `Fin 2`
  let φ : {c : Fin 3 // c ≠ a} → Fin 2 := fun c => if c.1 = a + 1 then 0 else 1
  have hφ : Function.Injective φ := by
    rintro ⟨c, hc⟩ ⟨d, hd⟩ hcd
    simp only [φ] at hcd ⊢
    fin_cases a <;> fin_cases c <;> fin_cases d <;> simp_all
    all_goals first | exact absurd rfl hc | exact absurd rfl hd
  -- the induced two-colouring on `T`
  let G2 : EdgeCol ↥T 2 :=
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
  have h2 : TriangleFree G2 := by
    intro p q r hpq hqr hpr hmono
    have hpq' : ¬ (p = q) := hpq
    have hqr' : ¬ (q = r) := hqr
    have hpr' : ¬ (p = r) := hpr
    simp only [G2, dif_neg hpq', dif_neg hqr', dif_neg hpr'] at hmono
    have e1 : G.col p.1 q.1 = G.col p.1 r.1 := by
      have hh := congrArg Subtype.val (hφ hmono.1)
      simpa using hh
    have e2 : G.col p.1 r.1 = G.col q.1 r.1 := by
      have hh := congrArg Subtype.val (hφ hmono.2)
      simpa using hh
    have hpq2 : p.1 ≠ q.1 := fun hh => hpq (Subtype.ext hh)
    have hqr2 : q.1 ≠ r.1 := fun hh => hqr (Subtype.ext hh)
    have hpr2 : p.1 ≠ r.1 := fun hh => hpr (Subtype.ext hh)
    exact h p.1 q.1 r.1 hpq2 hqr2 hpr2 ⟨e1, e2⟩
  exact two_colour_six G2 (by simp [Fintype.card_coe, hT6]) h2

end K58
