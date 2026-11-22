/-
K58 supplement (swarm smwr0lr3q, member m4), part II: the "all four colours inside X"
constraint on a Family-A root.

Setting: `A = N_c(r)` and `X` the 42 vertices outside `A ∪ {r}`.  Two facts that the
record's extremal-type scheme (m5's `J4`/12.4: "colour every pair of `X` by a free
colour of one of its types") ignores:

* if `x, y` are joined in colour `c` then their colour-`c` neighbourhoods are disjoint
  (otherwise the common neighbour completes a monochromatic triangle);
* a set of at least 17 points has an internal edge of *every* colour, because a
  colour missing inside `X` leaves a triangle-free 3-colouring of `X`, and
  `R(3,3,3) ≤ 17`.

Consequently, in a Family-A object (`|X| = 42`) there are two outside vertices joined
in the arm colour, hence **two outside vertices whose arm parts `M_0` are disjoint**.
In particular colouring all of `X` by free colours only - a 3-colouring of `K_42` -
is impossible, so the extremal-type scheme of the record can never produce a witness
whatever the multiplicities.
-/
import Interface

namespace K58

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Two distinct points joined in colour `c` have disjoint colour-`c`
neighbourhoods: a common colour-`c` neighbour would complete a monochromatic
triangle. -/
theorem nbr_disjoint_of_col (G : EdgeCol V 4) (h : TriangleFree G) {x y : V} {c : Fin 4}
    (hxy : x ≠ y) (hcol : G.col x y = c) : nbr G x c ∩ nbr G y c = ∅ := by
  refine Finset.eq_empty_iff_forall_notMem.mpr ?_
  intro a ha
  rw [Finset.mem_inter] at ha
  obtain ⟨hx, hy⟩ := ha
  simp only [nbr, Finset.mem_filter, Finset.mem_univ, true_and] at hx hy
  exact h x y a hxy (Ne.symm hy.1) (Ne.symm hx.1)
    ⟨by rw [hcol, hx.2], by rw [hx.2, hy.2]⟩

/-- **All four colours occur inside a 17-point set.**  If colour `c` were missing on
the edges inside `X`, the induced colouring of `X` would be a triangle-free
3-colouring, so `X` would have at most 16 points. -/
theorem colour_occurs_inside (G : EdgeCol V 4) (h : TriangleFree G) (X : Finset V)
    (hX : 17 ≤ X.card) (c : Fin 4) :
    ∃ x ∈ X, ∃ y ∈ X, x ≠ y ∧ G.col x y = c := by
  by_contra hcon
  simp only [not_exists, not_and, not_ne_iff] at hcon
  -- every edge inside `X` avoids colour `c`
  have hmiss : ∀ x ∈ X, ∀ y ∈ X, x ≠ y → G.col x y ≠ c := by
    intro x hx y hy hxy
    intro hc
    exact hcon x hx y hy hxy hc
  obtain ⟨U, hUX, hUcard⟩ := Finset.exists_subset_card_eq (s := X) hX
  have hU17 : U.card = 17 := hUcard
  have hne : ∀ x ∈ U, ∀ y ∈ U, x ≠ y → G.col x y ≠ c := fun x hx y hy =>
    hmiss x (hUX hx) y (hUX hy)
  have hcard : Fintype.card {d : Fin 4 // d ≠ c} = 3 := by
    have h1 : Fintype.card {d : Fin 4 // d = c} = 1 := Fintype.card_subtype_eq c
    have h2 := Fintype.card_subtype_compl (fun d : Fin 4 => d = c)
    rw [h1, Fintype.card_fin] at h2
    simp only [h2]
  let φ : {d : Fin 4 // d ≠ c} ≃ Fin 3 := Fintype.equivFinOfCardEq hcard
  let G3 : EdgeCol ↥U 3 :=
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
  exact three_colour_seventeen G3 (by simp [Fintype.card_coe, hU17]) h3

/-- **The arm-part disjointness corollary.**  In a 4-colouring with no monochromatic
triangle, any 17-point set `X` contains two points joined in colour `c`, and their
colour-`c` neighbourhoods are disjoint.  With `X` the 42 vertices outside `A ∪ {r}`
and `c` the root colour this says: *two outside vertices have disjoint colour-`c`
parts into the arm* - a constraint on Family A that no counting argument in the
record uses. -/
theorem exists_disjoint_arm_parts (G : EdgeCol V 4) (h : TriangleFree G) (X : Finset V)
    (hX : 17 ≤ X.card) (c : Fin 4) :
    ∃ x ∈ X, ∃ y ∈ X, x ≠ y ∧ G.col x y = c ∧ nbr G x c ∩ nbr G y c = ∅ := by
  obtain ⟨x, hx, y, hy, hxy, hcol⟩ := colour_occurs_inside G h X hX c
  exact ⟨x, hx, y, hy, hxy, hcol, nbr_disjoint_of_col G h hxy hcol⟩

#print axioms K58.nbr_disjoint_of_col
#print axioms K58.colour_occurs_inside
#print axioms K58.exists_disjoint_arm_parts

end K58
