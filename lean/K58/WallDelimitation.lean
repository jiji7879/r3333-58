import K58.Basic

/-!
# Delimiting the proposed `two small arms` lemma at order 58

Nothing here disproves the assertion for a good four-colouring of K58.
We prove (1) the exact profile arithmetic showing why it would kill every
WALL profile and (2) a genuine smaller full countermodel.  The latter shows
that triangle-freeness and R(3,3)>5 do not by themselves create critical
colour degrees.  The order 58 and the further global hypotheses are essential
to any proof of the proposed assertion.
-/

namespace K58
open Finset

/-- If the sorted colour degrees at a K58 vertex have at most one entry below
15, they have exactly one of the four non-WALL profiles. -/
theorem at_most_one_small_sorted {d0 d1 d2 d3 : ℕ}
    (hsum : d0 + d1 + d2 + d3 = 57)
    (h0 : d0 ≤ 16) (h1 : d1 ≤ 16) (h2 : d2 ≤ 16) (h3 : d3 ≤ 16)
    (h01 : d1 ≤ d0) (h12 : d2 ≤ d1) (h23 : d3 ≤ d2)
    (hthird : 15 ≤ d2) :
    (d0 = 15 ∧ d1 = 15 ∧ d2 = 15 ∧ d3 = 12) ∨
    (d0 = 16 ∧ d1 = 15 ∧ d2 = 15 ∧ d3 = 11) ∨
    (d0 = 16 ∧ d1 = 16 ∧ d2 = 15 ∧ d3 = 10) ∨
    (d0 = 16 ∧ d1 = 16 ∧ d2 = 16 ∧ d3 = 9) := by
  omega

/-- For sorted degrees, no pair of entries below 15 is equivalent to the
third largest entry being at least 15. -/
theorem no_two_small_iff_third_critical {d0 d1 d2 d3 : ℕ}
    (h01 : d1 ≤ d0) (h12 : d2 ≤ d1) (h23 : d3 ≤ d2) :
    ¬ ((d0 ≤ 14 ∧ d1 ≤ 14) ∨ (d0 ≤ 14 ∧ d2 ≤ 14) ∨
       (d0 ≤ 14 ∧ d3 ≤ 14) ∨ (d1 ≤ 14 ∧ d2 ≤ 14) ∨
       (d1 ≤ 14 ∧ d3 ≤ 14) ∨ (d2 ≤ 14 ∧ d3 ≤ 14)) ↔ 15 ≤ d2 := by
  omega

/-- Cyclic coordinate difference on the natural-number coordinates mod 5. -/
def diff5 (x y : ℕ) : ℕ := (x + 5 - y) % 5

/-- The substitution/square construction on 5×5 vertices.  Inside a block,
±1 differences have colour 0 and ±2 differences colour 1.  Between blocks,
the same good two-colouring of K5 is used with colours 2 and 3. -/
def squareCol (i j : Fin 25) : Fin 4 :=
  let a := i.val / 5
  let x := i.val % 5
  let b := j.val / 5
  let y := j.val % 5
  if a = b then
    if diff5 x y = 1 ∨ diff5 x y = 4 then 0 else 1
  else
    if diff5 a b = 1 ∨ diff5 a b = 4 then 2 else 3

/-- A full symmetric four-colouring of K25. -/
def squareG : EdgeCol (Fin 25) 4 where
  col := squareCol
  symm := by decide

/-- Exhaustive kernel check of all 2300 triangles. -/
theorem squareG_triangleFree : TriangleFree squareG := by
  unfold TriangleFree
  decide

/-- Every vertex has colour degrees (2,2,10,10) in this genuine full model. -/
theorem squareG_degrees (i : Fin 25) :
    deg squareG i 0 = 2 ∧ deg squareG i 1 = 2 ∧
    deg squareG i 2 = 10 ∧ deg squareG i 3 = 10 := by
  revert i
  decide

/-- In particular, the implication from goodness to two critical colours is
false if the order-58 hypothesis is omitted. -/
theorem squareG_has_no_critical_degree (i : Fin 25) (c : Fin 4) :
    deg squareG i c ≤ 14 := by
  have h := squareG_degrees i
  fin_cases c <;> simp_all

#print axioms K58.at_most_one_small_sorted
#print axioms K58.no_two_small_iff_third_critical
#print axioms K58.squareG_triangleFree
#print axioms K58.squareG_degrees
#print axioms K58.squareG_has_no_critical_degree

end K58
