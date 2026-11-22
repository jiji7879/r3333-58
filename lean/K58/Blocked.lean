/-
K58 supplement (swarm smwrfgma5, member m4): the sixth arm lemma.

* `blocked_set_le_five` : in a triangle-free 4-colouring, at a vertex `r` and for
  colours `a ≠ b`, at most five vertices of the colour-`b` class `N_b(r)` are
  pairwise `a`-blocked, i.e. every pair shares a common colour-`a` neighbour
  (a vertex distinct from both, joined to both in colour `a`).
* `blocked_in_set_le_five` : the stated form, where the common `a`-neighbour is
  additionally required to lie in `N_a(r)`.
* `part_family_le_five` : the word form used by the encoders.  Writing
  `M_a(x) = N_a(x) ∩ N_a(r)` for the `a`-part of the word of `x`, a set of
  vertices of one arm whose `a`-parts are pairwise intersecting has at most five
  elements.  Equivalently: no six vertices of an arm have pairwise intersecting
  `a`-parts, so the intersection graph of the `a`-parts of one arm has clique
  number at most five.

The proof is the one in `review/WALL_15141414_SWARM.md` section 15.  Six
pairwise blocked vertices have every mutual edge avoiding `a` (else a
monochromatic triangle with the common `a`-neighbour) and `b` (else a
monochromatic triangle with `r`, both endpoints being colour-`b` neighbours of
`r`), so their induced colouring is a triangle-free 2-colouring of `K_6`,
contradicted by `K58.two_colour_six`.  Note that the bound holds for the
*unrestricted* notion of blocking too, where the common `a`-neighbour need not
lie in `N_a(r)`; the restricted form is a corollary.
-/
import K58.Arm

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- `x` and `y` share a common colour-`a` neighbour distinct from both. -/
def ABlocked (G : EdgeCol V 4) (a : Fin 4) (x y : V) : Prop :=
  ∃ z, z ≠ x ∧ z ≠ y ∧ G.col z x = a ∧ G.col z y = a

/-- `x` and `y` share a common colour-`a` neighbour inside `N_a(r)`. -/
def ABlockedIn (G : EdgeCol V 4) (r : V) (a : Fin 4) (x y : V) : Prop :=
  ∃ z, z ∈ nbr G r a ∧ z ≠ x ∧ z ≠ y ∧ G.col z x = a ∧ G.col z y = a

theorem ABlockedIn.toBlocked (G : EdgeCol V 4) {r : V} {a : Fin 4} {x y : V}
    (h : ABlockedIn G r a x y) : ABlocked G a x y := by
  obtain ⟨z, -, h1, h2, h3, h4⟩ := h
  exact ⟨z, h1, h2, h3, h4⟩

/-- **The sixth arm lemma.**  At most five vertices of a colour class `N_b(r)`
are pairwise `a`-blocked. -/
theorem blocked_set_le_five (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (a b : Fin 4)
    (hab : a ≠ b) {S : Finset V} (hS : S ⊆ nbr G r b)
    (hbl : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → ABlocked G a x y) : S.card ≤ 5 := by
  by_contra hle
  simp only [not_le] at hle
  obtain ⟨T, hTS, hTcard⟩ := Finset.exists_subset_card_eq (show 6 ≤ S.card by omega)
  have hT6 : T.card = 6 := hTcard
  have hmem : ∀ p ∈ T, p ∈ nbr G r b := fun p hp => hS (hTS hp)
  -- every edge inside `T` avoids both colours
  have hne : ∀ p ∈ T, ∀ q ∈ T, p ≠ q → G.col p q ≠ a ∧ G.col p q ≠ b := by
    intro p hp q hq hpq
    constructor
    · intro hc
      obtain ⟨z, hzp, hzq, hzx, hzy⟩ := hbl p (hTS hp) q (hTS hq) hpq
      exact h z p q hzp hpq hzq ⟨by rw [hzx, hzy], by rw [hzy, hc]⟩
    · intro hc
      have hrp : r ≠ p := ((mem_nbr.mp (hmem p hp)).1).symm
      have hrq : r ≠ q := ((mem_nbr.mp (hmem q hq)).1).symm
      have h1 : G.col r p = b := (mem_nbr.mp (hmem p hp)).2
      have h2 : G.col r q = b := (mem_nbr.mp (hmem q hq)).2
      exact h r p q hrp hpq hrq ⟨by rw [h1, h2], by rw [h2, hc]⟩
  -- the induced 2-colouring of `T`
  let φ : {c : Fin 4 // c ≠ a ∧ c ≠ b} ≃ Fin 2 := Fintype.equivFinOfCardEq (card_ne_ne hab)
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
    intro p q w hpq hqw hpw hmono
    have hpq' : ¬ (p = q) := hpq
    have hqw' : ¬ (q = w) := hqw
    have hpw' : ¬ (p = w) := hpw
    simp only [G2, dif_neg hpq', dif_neg hqw', dif_neg hpw'] at hmono
    have e1 : G.col p.1 q.1 = G.col p.1 w.1 := by
      have hh := congrArg Subtype.val (φ.injective hmono.1)
      simpa using hh
    have e2 : G.col p.1 w.1 = G.col q.1 w.1 := by
      have hh := congrArg Subtype.val (φ.injective hmono.2)
      simpa using hh
    have hpq2 : p.1 ≠ q.1 := fun hh => hpq (Subtype.ext hh)
    have hqw2 : q.1 ≠ w.1 := fun hh => hqw (Subtype.ext hh)
    have hpw2 : p.1 ≠ w.1 := fun hh => hpw (Subtype.ext hh)
    exact h p.1 q.1 w.1 hpq2 hqw2 hpw2 ⟨e1, e2⟩
  exact two_colour_six G2 (by simp [Fintype.card_coe, hT6]) h2

/-- The stated form: the common `a`-neighbour is required to lie in `N_a(r)`. -/
theorem blocked_in_set_le_five (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (a b : Fin 4)
    (hab : a ≠ b) {S : Finset V} (hS : S ⊆ nbr G r b)
    (hbl : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → ABlockedIn G r a x y) : S.card ≤ 5 :=
  blocked_set_le_five G h r a b hab hS fun x hx y hy hxy =>
    ABlockedIn.toBlocked G (hbl x hx y hy hxy)

/-- **The word form.**  If the `a`-parts `M_a(x) = N_a(x) ∩ N_a(r)` of the
vertices of a subset `S` of one arm `N_b(r)` are pairwise intersecting, then
`S` has at most five elements. -/
theorem part_family_le_five (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (a b : Fin 4)
    (hab : a ≠ b) {S : Finset V} (hS : S ⊆ nbr G r b)
    (hint : ∀ x ∈ S, ∀ y ∈ S, x ≠ y →
      ((nbr G x a) ∩ (nbr G y a) ∩ (nbr G r a)).Nonempty) : S.card ≤ 5 := by
  refine blocked_in_set_le_five G h r a b hab hS ?_
  intro x hx y hy hxy
  obtain ⟨z, hz⟩ := hint x hx y hy hxy
  simp only [Finset.mem_inter] at hz
  obtain ⟨⟨hzx, hzy⟩, hzr⟩ := hz
  have hzx' : G.col z x = a := by rw [G.symm z x]; exact (mem_nbr.mp hzx).2
  have hzy' : G.col z y = a := by rw [G.symm z y]; exact (mem_nbr.mp hzy).2
  exact ⟨z, hzr, (mem_nbr.mp hzx).1, (mem_nbr.mp hzy).1, hzx', hzy'⟩

end K58
