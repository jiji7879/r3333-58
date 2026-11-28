import K58.CaseExpansion

open K58

/-- Exact numeric key of retained wall row 06861a3d..., before any CNF claim. -/
def targetRowKey : K58.CaseKey :=
  { planIndex := ⟨29, by decide⟩
    arm := ⟨1, by decide⟩
    markPosition := 0
    secondSixteen := false
    secondTwisted := true
    rootPosition := 7
    placement := fun _ => 0 }

#eval do
  let some C := K58.expandKey targetRowKey
    | throw (IO.userError "target key does not expand")
  IO.println s!"UNITS {(K58.caseUnitList C).length}"
  for u in K58.caseUnitList C do
    IO.println s!"{u.u} {u.v} {u.colour.val} {if u.positive then 1 else 0}"
