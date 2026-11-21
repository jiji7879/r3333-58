/-
K58 supplement (swarm smwqx1yfw, member m5): the arm-mixture bound and the interface identity.

`mixture` is the swarm's L1: two colour classes of *different* colours meet in at
most five vertices, because the intersection is 2-coloured with no monochromatic
triangle and `R(3,3) ≤ 6` (`K58.two_colour_six`).

`interface` is the double count used in addendum II of the report: for a vertex
`r` and a colour `c`, the number of colour-`c` edges between the arm `N_c(r)` and
its complement equals `sum_{a in N_c(r)} (deg_c(a) - 1)`.
-/
import K58.DegreeCap

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The colour-`a` neighbourhood of `i`, as a finite set. -/
noncomputable def nbr (G : EdgeCol V 4) (i : V) (a : Fin 4) : Finset V :=
  Finset.univ.filter (fun j => j ≠ i ∧ G.col i j = a)

/-- Its cardinality is the colour degree. -/
theorem nbr_card (G : EdgeCol V 4) (i : V) (a : Fin 4) :
    (nbr G i a).card = deg G i a := rfl

/-- A colour class is independent in its own colour. -/
theorem nbr_indep (G : EdgeCol V 4) (h : TriangleFree G) (i : V) (a : Fin 4) :
    ∀ x ∈ nbr G i a, ∀ y ∈ nbr G i a, x ≠ y → G.col x y ≠ a := by
  intro x hx y hy hxy hc
  simp only [nbr, Finset.mem_filter, Finset.mem_univ, true_and] at hx hy
  exact h i x y (Ne.symm hx.1) hxy (Ne.symm hy.1)
    ⟨by rw [hx.2, hy.2], by rw [hy.2, hc]⟩

/-- The complement of two distinct colours in `Fin 4` has two elements. -/
theorem card_ne_ne {f g : Fin 4} (hfg : f ≠ g) :
    Fintype.card {c : Fin 4 // c ≠ f ∧ c ≠ g} = 2 := by
  have hset : (Finset.univ.filter (fun c : Fin 4 => c ≠ f ∧ c ≠ g)) = Finset.univ \ {f, g} := by
    ext c
    simp only [Finset.mem_filter, Finset.mem_univ, true_and, Finset.mem_sdiff, Finset.mem_insert,
      Finset.mem_singleton, not_or]
  rw [Fintype.card_subtype, hset, Finset.card_sdiff]
  have hdis : ({f, g} : Finset (Fin 4)) ∩ Finset.univ = {f, g} := Finset.inter_univ _
  rw [hdis]
  simp [hfg]

/-- **L1 / the mixture bound.** In a triangle-free 4-colouring, a colour-`f`
neighbourhood of `x` and a colour-`g` neighbourhood of `u`, with `f ≠ g`, have at
most five common vertices. -/
theorem mixture (G : EdgeCol V 4) (h : TriangleFree G) (x u : V) (f g : Fin 4) (hfg : f ≠ g) :
    ((nbr G x f) ∩ (nbr G u g)).card ≤ 5 := by
  by_contra hle
  simp only [not_le] at hle
  obtain ⟨T, hTS, hTcard⟩ := Finset.exists_subset_card_eq (show 6 ≤ ((nbr G x f) ∩ (nbr G u g)).card by omega)
  have hT6 : T.card = 6 := hTcard
  -- membership
  have hmem : ∀ p ∈ T, p ∈ nbr G x f ∧ p ∈ nbr G u g := by
    intro p hp
    have hp' : p ∈ (nbr G x f) ∩ (nbr G u g) := hTS hp
    simpa only [Finset.mem_inter] using hp'
  -- every edge of T avoids both colours
  have hne : ∀ p ∈ T, ∀ q ∈ T, p ≠ q → G.col p q ≠ f ∧ G.col p q ≠ g := by
    intro p hp q hq hpq
    exact ⟨nbr_indep G h x f p (hmem p hp).1 q (hmem q hq).1 hpq,
           nbr_indep G h u g p (hmem p hp).2 q (hmem q hq).2 hpq⟩
  -- the induced 2-colouring of T
  let φ : {c : Fin 4 // c ≠ f ∧ c ≠ g} ≃ Fin 2 := Fintype.equivFinOfCardEq (card_ne_ne hfg)
  let G2 : EdgeCol ↥T 2 :=
    { col := fun p q =>
        if hpq : p = q then 0
        else φ ⟨G.col p.1 q.1, (hne p.1 p.2 q.1 q.2 (fun hh => hpq (Subtype.ext hh))).1,
                                  (hne p.1 p.2 q.1 q.2 (fun hh => hpq (Subtype.ext hh))).2⟩
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
      have hh := congrArg Subtype.val (φ.injective hmono.1)
      simpa using hh
    have e2 : G.col p.1 r.1 = G.col q.1 r.1 := by
      have hh := congrArg Subtype.val (φ.injective hmono.2)
      simpa using hh
    have hpq2 : p.1 ≠ q.1 := fun hh => hpq (Subtype.ext hh)
    have hqr2 : q.1 ≠ r.1 := fun hh => hqr (Subtype.ext hh)
    have hpr2 : p.1 ≠ r.1 := fun hh => hpr (Subtype.ext hh)
    exact h p.1 q.1 r.1 hpq2 hqr2 hpr2 ⟨e1, e2⟩
  exact two_colour_six G2 (by simp [Fintype.card_coe, hT6]) h2

end K58
