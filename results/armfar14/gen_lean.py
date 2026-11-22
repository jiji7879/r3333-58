#!/usr/bin/env python3
"""Emit the Lean file with the 18-vertex sharpness witness (|X| = 14 c-free,
4 far points) from far18.col."""
import sys

ROWS = open('far18.col').read().split('\n')[1:]
ROWS = [r for r in ROWS if r.strip()]
n = len(ROWS)
assert n == 18


def main():
    lines = []
    for r in ROWS:
        vals = r.split()
        assert len(vals) == 18
        lines.append('  ![' + ', '.join(vals) + ']')
    body = ',\n'.join(lines)
    lean = f"""/-
K58 supplement (swarm smwrmwgf7, member m6): the sharpness witness for the
improved independent-14 bound.

`armFar_le_five` (lean/supplement/m4/Interface.lean, kernel-checked) says that a
14-point set `X` with no colour-`c` edge inside has at most five points with no
colour-`c` edge into it.  The bound is **4**, not 5, and this file records the
sharpness half: an explicit triangle-free 4-colouring of `K_18` with such an `X`
of 14 points and **four** far points.  So `4` cannot be replaced by `3`.

The other half (`≤ 4`) is not a hand argument: it is a finite exhaustion over the
two classified 15-point templates (see the member's REPORT.md).  This file is the
kernel-checked half of the pair; it is `decide`-checked, no `native_decide`, no
`sorry`.

The definition of `armFar` below is copied verbatim from
`lean/supplement/m4/Interface.lean` so that this file is self-contained (that
file is not on `lean/build.sh`'s import path); the declaration is definitionally
identical.
-/
import K58.Corollaries

namespace K58

variable {{V : Type*}} [Fintype V] [DecidableEq V]

/-- The points outside `X` with no colour-`c` edge into `X`.
(copied from `lean/supplement/m4/Interface.lean`) -/
def armFar (G : EdgeCol V 4) (X : Finset V) (c : Fin 4) : Finset V :=
  Finset.univ.filter (fun y => y ∉ X ∧ ∀ x ∈ X, G.col y x ≠ c)

/-- The colour matrix of the 18-point witness, from `far18.col` (re-verified by
`tools/verify_coloring.py`). -/
def far18v : Fin 18 → Fin 18 → Fin 4 := ![
{body}]

def far18G : EdgeCol (Fin 18) 4 where
  col := far18v
  symm := by decide

theorem far18_triangleFree : TriangleFree far18G := by
  unfold TriangleFree
  decide

/-- The 14-point set `X` (vertices 0 to 13). -/
def far18X : Finset (Fin 18) :=
  Finset.univ.filter (fun i => (i : ℕ) < 14)

theorem far18X_card : far18X.card = 14 := by decide

theorem far18_X_free : ∀ x ∈ far18X, ∀ y ∈ far18X, x ≠ y → far18v x y ≠ 0 := by
  decide

theorem far18_armFar_card : (armFar far18G far18X 0).card = 4 := by
  decide

/-- **Sharpness.** Some triangle-free 4-colouring has a 14-point colour-0-free set
`X` with four points that carry no colour-0 edge into `X`.  So the exhaustive
bound `(armFar G X c).card ≤ 4` is attained, and `armFar_le_five`'s 5 is not the
sharp value at 14 points. -/
theorem armFar_four_attained :
    ∃ (G : EdgeCol (Fin 18) 4) (X : Finset (Fin 18)),
      TriangleFree G ∧ (∀ x ∈ X, ∀ y ∈ X, x ≠ y → G.col x y ≠ 0) ∧
        X.card = 14 ∧ (armFar G X 0).card = 4 :=
  ⟨far18G, far18X, far18_triangleFree, far18_X_free, far18X_card, far18_armFar_card⟩

end K58

#print axioms K58.far18_triangleFree
#print axioms K58.far18X_card
#print axioms K58.far18_X_free
#print axioms K58.far18_armFar_card
#print axioms K58.armFar_four_attained
"""
    open('ArmFarFour.lean', 'w').write(lean)
    print("wrote ArmFarFour.lean", len(lean), "bytes")


if __name__ == '__main__':
    main()
