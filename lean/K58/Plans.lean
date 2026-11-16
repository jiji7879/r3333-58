/-
K58: the 41 threshold plans of the frozen cover, and the arithmetic each one
has to satisfy.

The data is transcribed from `case-ledger.jsonl.gz` (one threshold per group of
equal `(size, kind)` arms, copied across the group).  The theorem says every
plan's slack condition `Σ (t a - 1) < Σ critical degrees` holds; that is the
hypothesis `exists_arm_reaches` consumes.
-/
import K58.Main

namespace K58

/-- One `(profile, kinds)` stratum of the cover with its per-arm thresholds. -/
structure Plan where
  prof : List ℕ
  kinds : String
  t : List ℕ
  deriving DecidableEq, Repr

/-- The 41 strata of the frozen ledger. -/
def plans : List Plan := [
  { prof := [15, 14, 14, 14], kinds := "T---", t := [15, 1, 1, 1] },
  { prof := [15, 14, 14, 14], kinds := "U---", t := [3, 5, 5, 5] },
  { prof := [15, 15, 14, 13], kinds := "TT--", t := [2, 2, 15, 14] },
  { prof := [15, 15, 14, 13], kinds := "TU--", t := [3, 1, 15, 14] },
  { prof := [15, 15, 14, 13], kinds := "UU--", t := [2, 2, 15, 14] },
  { prof := [15, 15, 15, 12], kinds := "TTT-", t := [11, 11, 11, 13] },
  { prof := [15, 15, 15, 12], kinds := "TTU-", t := [9, 9, 16, 13] },
  { prof := [15, 15, 15, 12], kinds := "TUU-", t := [3, 16, 16, 13] },
  { prof := [15, 15, 15, 12], kinds := "UUU-", t := [11, 11, 11, 13] },
  { prof := [16, 14, 14, 13], kinds := "T---", t := [1, 2, 2, 14] },
  { prof := [16, 14, 14, 13], kinds := "U---", t := [1, 2, 2, 14] },
  { prof := [16, 15, 13, 13], kinds := "TT--", t := [1, 5, 14, 14] },
  { prof := [16, 15, 13, 13], kinds := "TU--", t := [1, 5, 14, 14] },
  { prof := [16, 15, 13, 13], kinds := "UT--", t := [1, 5, 14, 14] },
  { prof := [16, 15, 13, 13], kinds := "UU--", t := [1, 5, 14, 14] },
  { prof := [16, 15, 14, 12], kinds := "TT--", t := [1, 5, 15, 13] },
  { prof := [16, 15, 14, 12], kinds := "TU--", t := [1, 5, 15, 13] },
  { prof := [16, 15, 14, 12], kinds := "UT--", t := [1, 5, 15, 13] },
  { prof := [16, 15, 14, 12], kinds := "UU--", t := [1, 5, 15, 13] },
  { prof := [16, 15, 15, 11], kinds := "TTT-", t := [17, 10, 10, 12] },
  { prof := [16, 15, 15, 11], kinds := "TTU-", t := [17, 4, 16, 12] },
  { prof := [16, 15, 15, 11], kinds := "TUU-", t := [5, 16, 16, 12] },
  { prof := [16, 15, 15, 11], kinds := "UTT-", t := [17, 10, 10, 12] },
  { prof := [16, 15, 15, 11], kinds := "UTU-", t := [17, 4, 16, 12] },
  { prof := [16, 15, 15, 11], kinds := "UUU-", t := [17, 10, 10, 12] },
  { prof := [16, 16, 13, 12], kinds := "TT--", t := [4, 4, 14, 13] },
  { prof := [16, 16, 13, 12], kinds := "TU--", t := [1, 7, 14, 13] },
  { prof := [16, 16, 13, 12], kinds := "UU--", t := [4, 4, 14, 13] },
  { prof := [16, 16, 14, 11], kinds := "TT--", t := [4, 4, 15, 12] },
  { prof := [16, 16, 14, 11], kinds := "TU--", t := [1, 7, 15, 12] },
  { prof := [16, 16, 14, 11], kinds := "UU--", t := [4, 4, 15, 12] },
  { prof := [16, 16, 15, 10], kinds := "TTT-", t := [17, 17, 5, 11] },
  { prof := [16, 16, 15, 10], kinds := "TTU-", t := [17, 17, 5, 11] },
  { prof := [16, 16, 15, 10], kinds := "TUT-", t := [17, 17, 5, 11] },
  { prof := [16, 16, 15, 10], kinds := "TUU-", t := [6, 17, 16, 11] },
  { prof := [16, 16, 15, 10], kinds := "UUT-", t := [17, 17, 5, 11] },
  { prof := [16, 16, 15, 10], kinds := "UUU-", t := [17, 17, 5, 11] },
  { prof := [16, 16, 16, 9], kinds := "TTT-", t := [13, 13, 13, 10] },
  { prof := [16, 16, 16, 9], kinds := "TTU-", t := [12, 12, 17, 10] },
  { prof := [16, 16, 16, 9], kinds := "TUU-", t := [7, 17, 17, 10] },
  { prof := [16, 16, 16, 9], kinds := "UUU-", t := [13, 13, 13, 10] },
]

/-- The slack condition: the sum of `t - 1` is below the critical mass. -/
def planOk (x : Plan) : Prop :=
  (x.t.map (fun t => t - 1)).sum < (x.prof.map (fun d => if 15 ≤ d then d else 0)).sum

instance (x : Plan) : Decidable (planOk x) := by unfold planOk; infer_instance

/-- Every one of the 41 plans satisfies the slack condition. -/
theorem plans_ok_bool : plans.all (fun x => decide (planOk x)) = true := by decide

/-- Every plan in the frozen list satisfies the slack condition. -/
theorem plans_ok {x : Plan} (hx : x ∈ plans) : planOk x :=
  of_decide_eq_true ((List.all_eq_true.mp plans_ok_bool) x hx)

/-- No threshold exceeds its arm, so no case is vacuous by asking for more
senders than the arm has. -/
def planFeasible (x : Plan) : Prop :=
  (x.t.zip x.prof).all (fun p => decide (p.1 ≤ p.2 + 1)) = true

instance (x : Plan) : Decidable (planFeasible x) := by unfold planFeasible; infer_instance

theorem plans_feasible_bool : plans.all (fun x => decide (planFeasible x)) = true := by decide

/-- No threshold in the frozen list exceeds its arm. -/
theorem plans_feasible {x : Plan} (hx : x ∈ plans) : planFeasible x :=
  of_decide_eq_true ((List.all_eq_true.mp plans_feasible_bool) x hx)

end K58
