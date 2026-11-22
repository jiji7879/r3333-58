/-
A kernel-verified witness that a 14-point link need not have all colour degrees
in (4, 5): the 3-coloured K_14 below is triangle-free and its point 5 has colour
degrees (5,5,3).  It is the T-template of `artifacts/k16_template_T_aut32_m4.col`
with the two points 0 and 1 deleted (both colour-2 adjacent to the point that
becomes 5 here), so it also shows that the (5,5,3) pattern is not exotic.
-/
import K58.Basic
import K58.DegreeCap

namespace K58

/-- The colour matrix of the 14-point link. -/
def k14v : Fin 14 → Fin 14 → Fin 3 :=
  ![![0, 1, 2, 2, 0, 1, 0, 0, 1, 0, 2, 1, 0, 2],
  ![1, 0, 1, 2, 2, 0, 0, 0, 0, 1, 2, 2, 1, 0],
  ![2, 1, 0, 1, 2, 1, 0, 1, 2, 2, 1, 0, 0, 0],
  ![2, 2, 1, 0, 1, 2, 2, 0, 1, 2, 0, 1, 0, 0],
  ![0, 2, 2, 1, 0, 1, 2, 2, 0, 1, 0, 0, 1, 0],
  ![1, 0, 1, 2, 1, 0, 1, 2, 2, 0, 0, 0, 0, 1],
  ![0, 0, 0, 2, 2, 1, 0, 1, 2, 1, 0, 1, 2, 2],
  ![0, 0, 1, 0, 2, 2, 1, 0, 1, 2, 2, 0, 1, 2],
  ![1, 0, 2, 1, 0, 2, 2, 1, 0, 1, 2, 2, 0, 1],
  ![0, 1, 2, 2, 1, 0, 1, 2, 1, 0, 1, 2, 2, 0],
  ![2, 2, 1, 0, 0, 0, 0, 2, 2, 1, 0, 1, 2, 1],
  ![1, 2, 0, 1, 0, 0, 1, 0, 2, 2, 1, 0, 1, 2],
  ![0, 1, 0, 0, 1, 0, 2, 1, 0, 2, 2, 1, 0, 1],
  ![2, 0, 0, 0, 0, 1, 2, 2, 1, 0, 1, 2, 1, 0]]

def k14G : EdgeCol (Fin 14) 3 where
  col := k14v
  symm := by decide

theorem k14_triangleFree : TriangleFree k14G := by
  unfold TriangleFree
  decide

theorem k14_degree_zero : (Finset.univ.filter (fun j : Fin 14 => j ≠ 5 ∧ k14v 5 j = 0)).card = 5 := by
  decide

theorem k14_degree_one : (Finset.univ.filter (fun j : Fin 14 => j ≠ 5 ∧ k14v 5 j = 1)).card = 5 := by
  decide

theorem k14_degree_two : (Finset.univ.filter (fun j : Fin 14 => j ≠ 5 ∧ k14v 5 j = 2)).card = 3 := by
  decide

end K58
