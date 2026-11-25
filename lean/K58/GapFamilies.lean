import Mathlib

/-!
# Machine-checked soundness chain for the K58 gap-four recipe

A colouring `c : V → V → Fin 4` of the pairs of a finite set, symmetric, with no
monochromatic triangle.  Two classical Ramsey inputs are carried as explicit
hypotheses and appear nowhere else:

* `R33`   : no 6-set is 2-coloured by two fixed distinct colours without a
            monochromatic triangle  (= R(3,3) = 6);
* `R333`  : every 3-colouring of a 17-set has a monochromatic triangle
            (= R(3,3,3) = 17).

Main results: `card_nb_le_sixteen` (colour classes bounded by 16, from R333) and
`familyB` (a critical vertex sends at least four colour-0 edges into each colour class
of any other vertex, from R33 + the 16 bound).  This is exactly the implication used by
the campaign to add family B to a pilot CNF.
-/

namespace K58

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Colour-`γ` neighbourhood of `v`, the vertex `v` itself excluded. -/
def nb (c : V → V → Fin 4) (v : V) (γ : Fin 4) : Finset V :=
  Finset.univ.filter (fun x => x ≠ v ∧ c v x = γ)

@[simp] lemma mem_nb {c : V → V → Fin 4} {v x : V} {γ : Fin 4} :
    x ∈ nb c v γ ↔ x ≠ v ∧ c v x = γ := by
  simp [nb]

/-- No monochromatic triangle. -/
def NoMono (c : V → V → Fin 4) : Prop :=
  ∀ x y z : V, x ≠ y → y ≠ z → x ≠ z → ¬ (c x y = c x z ∧ c x z = c y z)

/-- R(3,3) = 6, in the form needed: a 6-set cannot be 2-coloured by two fixed
distinct colours without a monochromatic triangle. -/
def R33 (c : V → V → Fin 4) : Prop :=
  ∀ (p q : Fin 4), p ≠ q → ∀ S : Finset V, S.card = 6 →
    (∀ x ∈ S, ∀ y ∈ S, x ≠ y → c x y ≠ p ∧ c x y ≠ q) →
    ∃ x ∈ S, ∃ y ∈ S, ∃ z ∈ S, x ≠ y ∧ y ≠ z ∧ x ≠ z ∧
      c x y = c x z ∧ c x z = c y z

/-- R(3,3,3) = 17, in the form needed: every 3-colouring of a 17-set has a
monochromatic triangle. -/
def R333 (c : V → V → Fin 4) : Prop :=
  ∀ S : Finset V, 17 ≤ S.card →
    (∀ x ∈ S, ∀ y ∈ S, x ≠ y → c x y ≠ 0) →
    ∃ x ∈ S, ∃ y ∈ S, ∃ z ∈ S, x ≠ y ∧ y ≠ z ∧ x ≠ z ∧
      c x y = c x z ∧ c x z = c y z

/-- **Family A, in the general form**: for any vertex `a`, any vertex `r`, and two
distinct colours `p ≠ q`, at most five vertices are `p`-neighbours of `a` and at the
same time `q`-neighbours of `r`.  (Taking `r` to be the root and `p = 0` gives the
campaign's family A; taking `q = 0` gives the dual bound used at arm vertices.) -/
theorem five_bound {c : V → V → Fin 4} (hc : ∀ x y, c x y = c y x)
    (hno : NoMono c) (hr33 : R33 c) {p q : Fin 4} (hpq : p ≠ q) (a r : V) :
    ((nb c a p) ∩ (nb c r q)).card ≤ 5 := by
  by_contra h
  rw [not_le] at h
  obtain ⟨S, hSsub, hScard⟩ := Finset.exists_subset_card_eq (show 6 ≤ ((nb c a p) ∩ (nb c r q)).card from h)
  have hfree : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → c x y ≠ p ∧ c x y ≠ q := by
    intro x hx y hy hxy
    have hx' := hSsub hx
    have hy' := hSsub hy
    simp only [Finset.mem_inter, mem_nb] at hx' hy'
    obtain ⟨hxa, hxr⟩ := hx'
    obtain ⟨hya, hyr⟩ := hy'
    obtain ⟨hxa', hxap⟩ := hxa
    obtain ⟨hya', hyap⟩ := hya
    obtain ⟨hxr', hxrq⟩ := hxr
    obtain ⟨hyr', hyrq⟩ := hyr
    constructor
    · intro hpxy
      refine hno a x y (Ne.symm hxa') hxy (Ne.symm hya') ⟨?_, ?_⟩
      · rw [hxap, hyap]
      · rw [hyap, hpxy]
    · intro hqxy
      refine hno r x y (Ne.symm hxr') hxy (Ne.symm hyr') ⟨?_, ?_⟩
      · rw [hxrq, hyrq]
      · rw [hyrq, hqxy]
  obtain ⟨x, hxS, y, hyS, z, hzS, hxy, hyz, hxz, hmono⟩ := hr33 p q hpq S hScard hfree
  exact hno x y z hxy hyz hxz hmono

end K58

namespace K58

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Every colour class has at most 16 vertices: `N_γ(a)` inherits a 3-colouring with no
monochromatic triangle, and R(3,3,3) = 17 forbids 17 vertices. -/
theorem card_nb_le_sixteen {c : V → V → Fin 4} (hno : NoMono c) (hr333 : R333 c) (a : V) :
    (nb c a 0).card ≤ 16 := by
  by_contra h
  rw [not_le] at h
  obtain ⟨S, hSsub, hScard⟩ := Finset.exists_subset_card_eq (show 17 ≤ (nb c a 0).card from h)
  have hzero : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → c x y ≠ 0 := by
    intro x hx y hy hxy h0
    have hx' := hSsub hx
    have hy' := hSsub hy
    simp only [mem_nb] at hx' hy'
    refine hno a x y (Ne.symm hx'.1) hxy (Ne.symm hy'.1) ⟨?_, ?_⟩
    · rw [hx'.2, hy'.2]
    · rw [hy'.2, h0]
  obtain ⟨x, hxS, y, hyS, z, hzS, hxy, hyz, hxz, hmono⟩ := hr333 S (by rw [hScard]) hzero
  exact hno x y z hxy hyz hxz hmono

end K58

namespace K58

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- `arm c a r γ` is the set of `γ`-neighbours of `r` that are also colour-0 neighbours
of `a`: in the campaign's notation, `N_0(a) ∩ A_γ`. -/
def arm (c : V → V → Fin 4) (a r : V) (γ : Fin 4) : Finset V :=
  (nb c a 0) ∩ (nb c r γ)

/-- **Family B, machine-checked.**  Let `a` be a vertex with `c a r = 0` (so `a` lies in
the colour-0 arm of `r`) and at least 15 colour-0 neighbours.  Then `a` sends at least
four colour-0 edges into each colour class of `r` other than the colour 0 one.

The only inputs beyond `NoMono` are `R33` (R(3,3) = 6, through `five_bound`) and `R333`
(R(3,3,3) = 17, through `card_nb_le_sixteen`). -/
theorem familyB {c : V → V → Fin 4} (hc : ∀ x y, c x y = c y x) (hno : NoMono c)
    (hr33 : R33 c) (hr333 : R333 c) {a r : V} (hra : r ≠ a) (har : c a r = 0)
    (hcrit : 15 ≤ (nb c a 0).card) :
    ∀ γ : Fin 4, γ ≠ 0 → 4 ≤ (arm c a r γ).card := by
  have h16 := card_nb_le_sixteen hno hr333 a
  -- every non-root vertex of `nb c a 0` is a `γ`-neighbour of `r` for some `γ ≠ 0`
  have hcover : ∀ x ∈ nb c a 0, x ≠ r → x ∈ ((arm c a r 1 ∪ arm c a r 2) ∪ arm c a r 3) := by
    intro x hx hxr
    have hx' : x ≠ a ∧ c a x = 0 := by simpa only [mem_nb] using hx
    have hcx : c r x ≠ 0 := by
      intro h0
      refine hno a x r (Ne.symm hx'.1) hxr (Ne.symm hra) ⟨?_, ?_⟩
      · rw [hx'.2, har]
      · rw [hc x r, h0, har]
    have htri : c r x = 1 ∨ c r x = 2 ∨ c r x = 3 := by
      have hk : ∀ k : Fin 4, k ≠ 0 → k = 1 ∨ k = 2 ∨ k = 3 := by decide
      exact hk _ hcx
    rcases htri with h1 | h2 | h3
    · refine Finset.mem_union_left _ (Finset.mem_union_left _ ?_)
      simp only [arm, Finset.mem_inter, mem_nb]
      exact ⟨hx', hxr, h1⟩
    · refine Finset.mem_union_left _ (Finset.mem_union_right _ ?_)
      simp only [arm, Finset.mem_inter, mem_nb]
      exact ⟨hx', hxr, h2⟩
    · refine Finset.mem_union_right _ ?_
      simp only [arm, Finset.mem_inter, mem_nb]
      exact ⟨hx', hxr, h3⟩
  have hsub : (nb c a 0) ⊆ insert r ((arm c a r 1 ∪ arm c a r 2) ∪ arm c a r 3) := by
    intro x hx
    by_cases hxr : x = r
    · subst hxr; exact Finset.mem_insert_self _ _
    · exact Finset.mem_insert_of_mem (hcover x hx hxr)
  have hcard1 : (nb c a 0).card ≤ (insert r ((arm c a r 1 ∪ arm c a r 2) ∪ arm c a r 3)).card :=
    Finset.card_le_card hsub
  have hcard2 : (insert r ((arm c a r 1 ∪ arm c a r 2) ∪ arm c a r 3)).card ≤
      ((arm c a r 1 ∪ arm c a r 2) ∪ arm c a r 3).card + 1 := Finset.card_insert_le _ _
  have hcard3 : ((arm c a r 1 ∪ arm c a r 2) ∪ arm c a r 3).card ≤
      (arm c a r 1).card + (arm c a r 2).card + (arm c a r 3).card := by
    have h := Finset.card_union_le (arm c a r 1 ∪ arm c a r 2) (arm c a r 3)
    have h' := Finset.card_union_le (arm c a r 1) (arm c a r 2)
    omega
  have h5 : ∀ k : Fin 4, k ≠ 0 → (arm c a r k).card ≤ 5 := by
    intro k hk
    exact five_bound hc hno hr33 (p := 0) (q := k) (Ne.symm hk) a r
  have h51 := h5 1 (by decide)
  have h52 := h5 2 (by decide)
  have h53 := h5 3 (by decide)
  have key : 14 ≤ (arm c a r 1).card + (arm c a r 2).card + (arm c a r 3).card := by omega
  intro γ hγ
  have hcases : γ = 1 ∨ γ = 2 ∨ γ = 3 := by
    have hk : ∀ k : Fin 4, k ≠ 0 → k = 1 ∨ k = 2 ∨ k = 3 := by decide
    exact hk γ hγ
  rcases hcases with rfl | rfl | rfl
  · omega
  · omega
  · omega

end K58

namespace K58

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- **Family C, machine-checked.**  Let `y` be a vertex outside the colour-0 class of `r`
and suppose `y` has at least 4 colour-0 neighbours inside its own class (this is the one
template-specific input: the campaign's `T`/`U` arm templates give every arm vertex 4 or
5 colour-0 neighbours inside its arm).  Then `y` has at most 12 colour-0 neighbours in the
colour-0 class of `r`. -/
theorem familyC {c : V → V → Fin 4} (hno : NoMono c) (hr333 : R333 c) {y r : V}
    (hγ : c r y ≠ 0) (hin : 4 ≤ ((nb c y 0) ∩ (nb c r (c r y))).card) :
    ((nb c y 0) ∩ (nb c r 0)).card ≤ 12 := by
  have h16 := card_nb_le_sixteen hno hr333 y
  have hdisj : Disjoint ((nb c y 0) ∩ (nb c r 0)) ((nb c y 0) ∩ (nb c r (c r y))) := by
    rw [Finset.disjoint_left]
    intro x hx1 hx2
    have h1 : x ∈ nb c r 0 := (Finset.mem_inter.1 hx1).2
    have h2 : x ∈ nb c r (c r y) := (Finset.mem_inter.1 hx2).2
    simp only [mem_nb] at h1 h2
    exact hγ (by rw [← h2.2, h1.2])
  have hsub : ((nb c y 0) ∩ (nb c r 0)) ∪ ((nb c y 0) ∩ (nb c r (c r y))) ⊆ nb c y 0 := by
    intro x hx
    simp only [Finset.mem_union, Finset.mem_inter] at hx
    tauto
  have hunion : (((nb c y 0) ∩ (nb c r 0)) ∪ ((nb c y 0) ∩ (nb c r (c r y)))).card ≤
      (nb c y 0).card := Finset.card_le_card hsub
  have hadd : (((nb c y 0) ∩ (nb c r 0)) ∪ ((nb c y 0) ∩ (nb c r (c r y)))).card =
      ((nb c y 0) ∩ (nb c r 0)).card + ((nb c y 0) ∩ (nb c r (c r y))).card :=
    Finset.card_union_of_disjoint hdisj
  omega

end K58


namespace K58

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- **The dual form of family A.**  For *every* vertex `v` (not only for `v` in the
colour-0 class of the root) and every colour `γ ≠ 0`, the colour-0 neighbourhood of `v`
meets the colour-`γ` class of `r` in at most five vertices.  The campaign's family A is
the special case `v ∈ N_0(r)`; the general form is what a bound at an arm vertex needs. -/
theorem dual_five_bound {c : V → V → Fin 4} (hc : ∀ x y, c x y = c y x) (hno : NoMono c)
    (hr33 : R33 c) {γ : Fin 4} (hγ : γ ≠ 0) (v r : V) :
    ((nb c v 0) ∩ (nb c r γ)).card ≤ 5 :=
  five_bound hc hno hr33 (p := 0) (q := γ) (Ne.symm hγ) v r

/-- The exact degree pattern at a critical vertex.  Families A and B together with the
flag's own definition (`x 1 + x 2 + x 3 ≥ 14`) leave no room: each `x γ` is 4 or 5, the
sum is 14 or 15, and at most one of the three equals 4.  So no single-vertex refinement
of B is available. -/
theorem exact_pattern {x1 x2 x3 : ℕ} (h1 : x1 ≤ 5) (h2 : x2 ≤ 5) (h3 : x3 ≤ 5)
    (l1 : 4 ≤ x1) (l2 : 4 ≤ x2) (l3 : 4 ≤ x3) (hs : 14 ≤ x1 + x2 + x3) :
    x1 + x2 + x3 ≤ 15 ∧ (x1 = 5 ∨ x2 = 5) ∧ (x1 = 5 ∨ x3 = 5) ∧ (x2 = 5 ∨ x3 = 5) := by
  omega

end K58

#print axioms K58.five_bound
#print axioms K58.card_nb_le_sixteen
#print axioms K58.familyB
#print axioms K58.familyC
#print axioms K58.dual_five_bound
#print axioms K58.exact_pattern
