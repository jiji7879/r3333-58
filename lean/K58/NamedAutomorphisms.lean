import K58.PositionSearch
import Mathlib.Data.Fin.Tuple.Reflection

namespace K58

/-- The named K15 automorphisms, in lexicographic order of their images.
The table is checked against the complete partial-map search below. -/
def named15 (t : Bool) : List (Fin 15 → Fin 15) :=
  if t then [
    ![0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    ![3, 11, 8, 0, 13, 5, 6, 14, 2, 10, 9, 1, 12, 4, 7]
  ]
  else [
    ![0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    ![0, 10, 13, 7, 4, 14, 9, 3, 12, 6, 1, 11, 8, 2, 5],
    ![3, 9, 4, 14, 13, 7, 10, 0, 12, 6, 11, 1, 2, 8, 5],
    ![3, 11, 8, 0, 13, 5, 6, 14, 2, 10, 9, 1, 12, 4, 7],
    ![5, 9, 2, 14, 12, 0, 11, 7, 13, 1, 10, 6, 4, 8, 3],
    ![5, 10, 8, 7, 12, 3, 1, 14, 4, 11, 9, 6, 13, 2, 0],
    ![7, 6, 4, 5, 2, 3, 1, 0, 8, 9, 11, 10, 13, 12, 14],
    ![7, 11, 12, 0, 2, 14, 9, 5, 13, 1, 6, 10, 8, 4, 3],
    ![14, 1, 12, 3, 8, 7, 10, 5, 4, 11, 6, 9, 2, 13, 0],
    ![14, 6, 13, 5, 8, 0, 11, 3, 2, 10, 1, 9, 4, 12, 7]
  ]

set_option maxRecDepth 200000 in
set_option maxHeartbeats 0 in
theorem named15_exact : ∀ t, named15 t = PositionSearch.automorphisms (template 15 t) := by
  decide +kernel

end K58
