/-
K58 (15,14,14,14): the some-six companion of `K58.uniform_child`.

`K58.uniform_child` says: at a root whose 15-point colour class sends
everywhere, if every outside vertex meets the class in at most five points then
the interface is tight -- every class point has exactly fifteen colour-`c`
partners and every outside vertex meets the class in exactly five.  The frozen
encoder splits every charge-15 case into that child (`m(x) <= 5` everywhere) and
its complement, the *some-six* child (`some x has m(x) >= 6`).  This file
supplies the some-six side of the same count.

The interface identity (`K58.interface_count`, restated below without `deg`) is

    sum_{x outside} m(x)  =  sum_{a in A} (d_c(a) - 1).

In the branch every `a in A` is `c`-critical (`15 <= d_c(a)`) and the degree cap
gives `d_c(a) <= 16`, so the right side is `15 * 14 = 210` plus one for each
class point of degree 16.  Hence

    sum_{x outside} m(x)  =  210 + #{a in A : d_c(a) = 16},                   (1)
    sum_{x outside} (m(x) - 5)  =  #{a in A : d_c(a) = 16}  (all m(x) >= 5).  (2)

(1) is the some-six conservation law: the outside mass is the tight value 210
plus one for each 16-armed class point.  Consequence `some_six_or_deficit`: if
some outside vertex sees six class points then either some class point is
16-armed or some outside vertex sees at most four.  So a some-six object with no
16-class carries a deficit vertex, and one with no deficit vertex carries a
16-class -- the exact sense in which the uniformity half of the branch is not a
counting consequence, and why the two charge-15 rows whose pin forces
`d_0(q) = 16` are not closed by any interface counter.

Pure double counting plus the two degree bounds; no classification is used.
-/
import K58.Frontier
import K58.Arm

namespace K58

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The interface identity in the form used below, with the colour degree
written as the cardinality of the colour neighbourhood. -/
theorem interface_count' (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4) :
    ∑ a ∈ nbr G r c, ((nbr G a c).card - 1)
      = ∑ y ∈ (univ \ nbr G r c) \ {r}, ((nbr G y c) ∩ (nbr G r c)).card := by
  rw [← interface_count G h r c]
  exact sum_congr rfl (fun a _ => by rw [nbr_card])

/-- **The some-six conservation law.**  At a vertex `r` of a triangle-free
4-colouring of `K_58` whose colour-`c` class has 15 points, all `c`-critical,
the outside vertices meet the class in `210` points' worth, plus one for each
class point of colour-`c` degree 16. -/
theorem some_six_count (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4)
    (hV : Fintype.card V = 58) (h15 : (nbr G r c).card = 15)
    (hlo : ∀ a ∈ nbr G r c, 15 ≤ (nbr G a c).card)
    (hhi : ∀ a ∈ nbr G r c, (nbr G a c).card ≤ 16) :
    ∑ x ∈ (univ \ nbr G r c) \ {r}, ((nbr G x c) ∩ (nbr G r c)).card
      = 210 + ((nbr G r c).filter (fun a => (nbr G a c).card = 16)).card := by
  classical
  rw [← interface_count' G h r c]
  -- every class point contributes 14, plus one exactly when it is 16-armed
  have hterm : ∀ a ∈ nbr G r c,
      ((nbr G a c).card - 1)
        = 14 + (if (nbr G a c).card = 16 then 1 else 0) := by
    intro a ha
    have h1 := hlo a ha
    have h2 := hhi a ha
    split_ifs with hh
    · omega
    · omega
  calc ∑ a ∈ nbr G r c, ((nbr G a c).card - 1)
      = ∑ a ∈ nbr G r c, (14 + (if (nbr G a c).card = 16 then 1 else 0)) :=
        sum_congr rfl hterm
    _ = ∑ _a ∈ nbr G r c, 14
          + ∑ a ∈ nbr G r c, (if (nbr G a c).card = 16 then 1 else 0) :=
        sum_add_distrib
    _ = 210 + ((nbr G r c).filter (fun a => (nbr G a c).card = 16)).card := by
        rw [sum_const_nat (fun _ _ => rfl), h15, ← card_filter]

/-- **The some-six companion of `K58.uniform_child`.**  In the branch, if some
outside vertex meets the 15-point class in six or more points, then either some
class point is 16-armed (`d_c = 16`) or some outside vertex meets the class in
at most four points. -/
theorem some_six_or_deficit (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (c : Fin 4) (hV : Fintype.card V = 58) (h15 : (nbr G r c).card = 15)
    (hlo : ∀ a ∈ nbr G r c, 15 ≤ (nbr G a c).card)
    (hhi : ∀ a ∈ nbr G r c, (nbr G a c).card ≤ 16)
    (hsix : ∃ x ∈ (univ \ nbr G r c) \ {r},
      6 ≤ ((nbr G x c) ∩ (nbr G r c)).card) :
    (∃ a ∈ nbr G r c, (nbr G a c).card = 16)
      ∨ ∃ x ∈ (univ \ nbr G r c) \ {r},
          ((nbr G x c) ∩ (nbr G r c)).card ≤ 4 := by
  classical
  set X := (univ \ nbr G r c) \ {r} with hXdef
  set f : V → ℕ := fun x => ((nbr G x c) ∩ (nbr G r c)).card with hfdef
  by_contra hcon
  rw [not_or] at hcon
  have hno16 : ∀ a ∈ nbr G r c, (nbr G a c).card ≠ 16 := by
    intro a ha hh
    exact hcon.1 ⟨a, ha, hh⟩
  have hge5 : ∀ x ∈ X, 5 ≤ f x := by
    intro x hx
    have h2 : ¬ (f x ≤ 4) := fun hh => hcon.2 ⟨x, hx, hh⟩
    omega
  -- the arm side is exactly 210 when no class point is 16-armed
  have harm : ∑ a ∈ nbr G r c, ((nbr G a c).card - 1) = 210 := by
    have hterm : ∀ a ∈ nbr G r c, ((nbr G a c).card - 1) = 14 := by
      intro a ha
      have h1 := hlo a ha
      have h2 := hhi a ha
      have h3 := hno16 a ha
      omega
    rw [sum_congr rfl hterm, sum_const_nat (fun _ _ => rfl), h15]
  have hsum : ∑ x ∈ X, f x = 210 := by
    rw [hfdef, hXdef, ← interface_count' G h r c, harm]
  have hXcard : X.card = 42 := by
    rw [hXdef]; exact interface_outside_card G r c hV h15
  -- 42 terms, each at least 5, summing to 210: all exactly 5
  have hfive : ∀ x ∈ X, f x = 5 := by
    intro x hx
    by_contra hne
    have hgt : 5 < f x := by
      have := hge5 x hx
      omega
    have hbig : 210 < ∑ y ∈ X, f y := by
      calc 210 = 42 * 5 := by norm_num
        _ = ∑ _y ∈ X, (5 : ℕ) := by
            rw [sum_const_nat (fun _ _ => rfl), hXcard]
        _ < ∑ y ∈ X, f y :=
            sum_lt_sum (fun y hy => hge5 y hy) ⟨x, hx, hgt⟩
    omega
  obtain ⟨x, hx, hsix'⟩ := hsix
  have h5 := hfive x hx
  have hfx : f x = ((nbr G x c) ∩ (nbr G r c)).card := by rw [hfdef]
  omega

/-- The excess form (2): if additionally every outside vertex meets the class in
at least five points, the outside excess over five is exactly the number of
16-class points. -/
theorem some_six_excess (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4)
    (hV : Fintype.card V = 58) (h15 : (nbr G r c).card = 15)
    (hlo : ∀ a ∈ nbr G r c, 15 ≤ (nbr G a c).card)
    (hhi : ∀ a ∈ nbr G r c, (nbr G a c).card ≤ 16)
    (hdef : ∀ x ∈ (univ \ nbr G r c) \ {r},
      5 ≤ ((nbr G x c) ∩ (nbr G r c)).card) :
    ∑ x ∈ (univ \ nbr G r c) \ {r},
        (((nbr G x c) ∩ (nbr G r c)).card - 5)
      = ((nbr G r c).filter (fun a => (nbr G a c).card = 16)).card := by
  classical
  set X := (univ \ nbr G r c) \ {r} with hXdef
  set f : V → ℕ := fun x => ((nbr G x c) ∩ (nbr G r c)).card with hfdef
  have hcount : ∑ x ∈ X, f x
      = 210 + ((nbr G r c).filter (fun a => (nbr G a c).card = 16)).card := by
    rw [hfdef, hXdef]
    exact some_six_count G h r c hV h15 hlo hhi
  have hXcard : X.card = 42 := by
    rw [hXdef]; exact interface_outside_card G r c hV h15
  have hcongr : ∑ x ∈ X, ((nbr G x c) ∩ (nbr G r c)).card
      = ∑ x ∈ X, ((((nbr G x c) ∩ (nbr G r c)).card - 5) + 5) := by
    exact (sum_congr rfl (fun x hx => by
      have hh := hdef x (hXdef ▸ hx)
      omega)).symm
  rw [hcongr, sum_add_distrib, sum_const_nat (fun _ _ => rfl), hXcard] at hcount
  omega

end K58

#print axioms K58.interface_count'
#print axioms K58.some_six_count
#print axioms K58.some_six_or_deficit
#print axioms K58.some_six_excess
