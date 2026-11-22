/-
K58 supplement (swarm smwr0lr3q, member m4), part III: the 16-arm forcing theorem.

For a vertex `r` whose colour-`0` class `A = N_0(r)` has 16 points, all of them
`0`-critical (`15 <= d_0(a)`), the interface count cannot be spread at five per
outside vertex: `16*14 = 224` exceeds `5*41 = 205`.  So some outside vertex has at
least six colour-`0` neighbours in `A`, and - using the degree cap twice - at
least two of them do.

The interface identity is `K58.interface` and the degree cap `K58.deg_le_sixteen`,
both kernel-checked in `Interface.lean`.
-/
import Interface

namespace K58

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The outside of a 16-point colour class has 41 points (`58 - 16 - 1`). -/
theorem outside_card (G : EdgeCol V 4) (hV : Fintype.card V = 58) (r : V)
    (hAcard : (nbr G r 0).card = 16) :
    (Finset.univ \ (nbr G r 0 ∪ {r})).card = 41 := by
  have hrA : r ∉ nbr G r 0 := by simp [nbr]
  have hdisj : Disjoint (nbr G r 0) ({r} : Finset V) := by
    rw [Finset.disjoint_singleton_right]
    exact hrA
  have hcard : (nbr G r 0 ∪ {r}).card = 17 := by
    rw [Finset.card_union_of_disjoint hdisj, hAcard]
    simp
  have hcover : (nbr G r 0 ∪ {r}) ∪ (Finset.univ \ (nbr G r 0 ∪ {r}))
      = (Finset.univ : Finset V) :=
    Finset.union_sdiff_of_subset (Finset.subset_univ _)
  have hdj : Disjoint (nbr G r 0 ∪ {r}) (Finset.univ \ (nbr G r 0 ∪ {r})) :=
    Finset.disjoint_sdiff
  have hunion := Finset.card_union_of_disjoint hdj
  rw [hcover, Finset.card_univ, hV] at hunion
  omega

/-- A saturated 16-arm sends at least `224` colour-`0` edges to the outside. -/
theorem outside_sum_ge (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hAcard : (nbr G r 0).card = 16)
    (hcrit : ∀ a ∈ nbr G r 0, 15 ≤ deg G a 0) :
    224 ≤ ∑ x ∈ (Finset.univ \ (nbr G r 0 ∪ {r})),
      ((nbr G x 0) ∩ (nbr G r 0)).card := by
  have hmain := interface_sum G h r 0
  have hge : 16 * 15 ≤ ∑ a ∈ nbr G r 0, deg G a 0 := by
    have hle := Finset.sum_le_sum (s := nbr G r 0) (f := fun _ => 15)
      (g := fun a => deg G a 0) (fun a ha => hcrit a ha)
    rwa [Finset.sum_const, hAcard, smul_eq_mul] at hle
  omega

/-- **Theorem A.** A saturated 16-arm forces an outside vertex with at least six
colour-`0` neighbours in it. -/
theorem forced_six (G : EdgeCol V 4) (h : TriangleFree G) (hV : Fintype.card V = 58)
    (r : V) (hAcard : (nbr G r 0).card = 16)
    (hcrit : ∀ a ∈ nbr G r 0, 15 ≤ deg G a 0) :
    ∃ x ∈ (Finset.univ \ (nbr G r 0 ∪ {r})), 6 ≤ ((nbr G x 0) ∩ (nbr G r 0)).card := by
  by_contra hcon
  have h1 : ∀ x ∈ (Finset.univ \ (nbr G r 0 ∪ {r})),
      ((nbr G x 0) ∩ (nbr G r 0)).card ≤ 5 := by
    intro x hx
    by_contra hbig
    exact hcon ⟨x, hx, by omega⟩
  have h2 : ∑ x ∈ (Finset.univ \ (nbr G r 0 ∪ {r})),
      ((nbr G x 0) ∩ (nbr G r 0)).card ≤ 41 * 5 := by
    have h3 : ∑ x ∈ (Finset.univ \ (nbr G r 0 ∪ {r})),
        ((nbr G x 0) ∩ (nbr G r 0)).card
        ≤ ∑ _x ∈ (Finset.univ \ (nbr G r 0 ∪ {r})), 5 :=
      Finset.sum_le_sum (fun x hx => h1 x hx)
    rwa [Finset.sum_const, outside_card G hV r hAcard, smul_eq_mul] at h3
  have h4 := outside_sum_ge G h r hAcard hcrit
  omega

/-- **Theorem A'.** At least two outside vertices have six or more: after removing
one witness, `224 - 16 = 208` still exceeds `40 * 5 = 200`. -/
theorem forced_six_two (G : EdgeCol V 4) (h : TriangleFree G) (hV : Fintype.card V = 58)
    (r : V) (hAcard : (nbr G r 0).card = 16)
    (hcrit : ∀ a ∈ nbr G r 0, 15 ≤ deg G a 0) :
    ∃ x ∈ (Finset.univ \ (nbr G r 0 ∪ {r})), ∃ y ∈ (Finset.univ \ (nbr G r 0 ∪ {r})),
      x ≠ y ∧ 6 ≤ ((nbr G x 0) ∩ (nbr G r 0)).card ∧
        6 ≤ ((nbr G y 0) ∩ (nbr G r 0)).card := by
  set X := Finset.univ \ (nbr G r 0 ∪ {r}) with hX
  obtain ⟨x0, hx0, hbig⟩ := forced_six G h hV r hAcard hcrit
  by_contra hcon
  have hsmall : ∀ y ∈ X.erase x0, ((nbr G y 0) ∩ (nbr G r 0)).card ≤ 5 := by
    intro y hy
    have hyX : y ∈ X := Finset.mem_of_mem_erase hy
    have hyx : y ≠ x0 := (Finset.mem_erase.mp hy).1
    by_contra hb
    exact hcon ⟨x0, hx0, y, hyX, Ne.symm hyx, hbig, by omega⟩
  have hcap : ((nbr G x0 0) ∩ (nbr G r 0)).card ≤ 16 := by
    have h1 : ((nbr G x0 0) ∩ (nbr G r 0)).card ≤ (nbr G x0 0).card :=
      Finset.card_le_card Finset.inter_subset_left
    have h2 := deg_le_sixteen G h x0 0
    rw [nbr_card] at h1
    omega
  have hsplit := Finset.sum_erase_add (s := X)
    (f := fun x => ((nbr G x 0) ∩ (nbr G r 0)).card) hx0
  have hrest : ∑ x ∈ X.erase x0, ((nbr G x 0) ∩ (nbr G r 0)).card ≤ 40 * 5 := by
    have h3 : ∑ x ∈ X.erase x0, ((nbr G x 0) ∩ (nbr G r 0)).card
        ≤ ∑ _x ∈ X.erase x0, 5 := Finset.sum_le_sum (fun y hy => hsmall y hy)
    rwa [Finset.sum_const, Finset.card_erase_of_mem hx0, hX,
      outside_card G hV r hAcard, smul_eq_mul] at h3
  have h4 := outside_sum_ge G h r hAcard hcrit
  rw [← hX, ← hsplit] at h4
  omega

#print axioms K58.outside_card
#print axioms K58.outside_sum_ge
#print axioms K58.forced_six
#print axioms K58.forced_six_two

end K58
