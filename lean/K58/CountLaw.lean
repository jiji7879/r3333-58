/-
Kernel-checked colour-count law for the two classified 3-coloured K15 templates of the
twisted uniform child (T.col and U.col of the K58_twisted_partition_screen package).

For a zero-neighbourhood of a sender a whose root's colour-1 class has k vertices, an
added vertex x of root colour h occupies some vertex v with colour h to the root, so its
colour multiset on that B part is the multiset of T[v][-] over the root's colour-1 class.
The theorems below say: the attainable multisets are exactly the listed ones, for both
templates.  Every proof is `by decide`, i.e. the statement is evaluated by the kernel;
no native_decide, no axiom beyond the kernel's own.
-/
namespace K58

/-- The T template, 15 x 15, colours 1..3 off the diagonal. -/
def Tm : List (List Nat) :=
  [[0, 1, 2, 2, 3, 3, 3, 2, 1, 3, 1, 2, 1, 2, 3],
      [1, 0, 2, 2, 3, 2, 3, 3, 3, 1, 2, 1, 3, 1, 1],
      [2, 2, 0, 1, 3, 3, 2, 3, 1, 2, 1, 3, 2, 1, 1],
      [2, 2, 1, 0, 2, 3, 3, 3, 2, 1, 3, 1, 1, 3, 2],
      [3, 3, 3, 2, 0, 1, 2, 2, 1, 2, 3, 1, 1, 3, 1],
      [3, 2, 3, 3, 1, 0, 2, 2, 3, 1, 1, 2, 3, 1, 2],
      [3, 3, 2, 3, 2, 2, 0, 1, 2, 1, 1, 3, 1, 2, 1],
      [2, 3, 3, 3, 2, 2, 1, 0, 1, 3, 2, 1, 2, 1, 3],
      [1, 3, 1, 2, 1, 3, 2, 1, 0, 1, 2, 2, 2, 3, 3],
      [3, 1, 2, 1, 2, 1, 1, 3, 1, 0, 2, 2, 3, 3, 2],
      [1, 2, 1, 3, 3, 1, 1, 2, 2, 2, 0, 1, 3, 2, 3],
      [2, 1, 3, 1, 1, 2, 3, 1, 2, 2, 1, 0, 3, 3, 3],
      [1, 3, 2, 1, 1, 3, 1, 2, 2, 3, 3, 3, 0, 1, 2],
      [2, 1, 1, 3, 3, 1, 2, 1, 3, 3, 2, 3, 1, 0, 2],
      [3, 1, 1, 2, 1, 2, 1, 3, 3, 2, 3, 3, 2, 2, 0]]

/-- The U template, 15 x 15. -/
def Um : List (List Nat) :=
  [[0, 1, 2, 2, 3, 3, 3, 2, 1, 3, 1, 2, 1, 2, 3],
      [1, 0, 2, 2, 3, 3, 2, 3, 3, 1, 2, 1, 2, 1, 1],
      [2, 2, 0, 1, 3, 2, 3, 3, 1, 2, 1, 3, 3, 1, 1],
      [2, 2, 1, 0, 2, 3, 3, 3, 2, 1, 3, 1, 1, 3, 2],
      [3, 3, 3, 2, 0, 1, 2, 2, 1, 2, 3, 1, 1, 3, 1],
      [3, 3, 2, 3, 1, 0, 2, 2, 2, 1, 1, 3, 3, 1, 2],
      [3, 2, 3, 3, 2, 2, 0, 1, 3, 1, 1, 2, 1, 2, 1],
      [2, 3, 3, 3, 2, 2, 1, 0, 1, 3, 2, 1, 2, 1, 3],
      [1, 3, 1, 2, 1, 2, 3, 1, 0, 1, 2, 2, 3, 3, 3],
      [3, 1, 2, 1, 2, 1, 1, 3, 1, 0, 2, 2, 3, 3, 2],
      [1, 2, 1, 3, 3, 1, 1, 2, 2, 2, 0, 1, 3, 2, 3],
      [2, 1, 3, 1, 1, 3, 2, 1, 2, 2, 1, 0, 2, 3, 3],
      [1, 2, 3, 1, 1, 3, 1, 2, 3, 3, 3, 2, 0, 1, 2],
      [2, 1, 1, 3, 3, 1, 2, 1, 3, 3, 2, 3, 1, 0, 2],
      [3, 1, 1, 2, 1, 2, 1, 3, 3, 2, 3, 3, 2, 2, 0]]

/-- The colour-1 class of vertex `rt`. -/
def class1 (M : List (List Nat)) (rt : Nat) : List Nat :=
  (List.range 15).filter (fun y => y != rt && (M.getD rt []).getD y 0 == 1)

/-- The colour-count vector `(n1,n2,n3)` of `v` on the colour-1 class of `rt`. -/
def vec (M : List (List Nat)) (rt v : Nat) : Nat × Nat × Nat :=
  let c := (class1 M rt).map (fun y => (M.getD v []).getD y 0)
  ((c.filter (fun x => x == 1)).length, (c.filter (fun x => x == 2)).length,
   (c.filter (fun x => x == 3)).length)

/-- All count vectors attained over all roots whose colour-1 class has size `k`,
and all `v` of root colour `h` to that root. -/
def realised (M : List (List Nat)) (h k : Nat) : List (Nat × Nat × Nat) :=
  ((List.range 15).filter (fun rt => (class1 M rt).length == k)).flatMap fun rt =>
    ((List.range 15).filter (fun v => v != rt && (M.getD rt []).getD v 0 == h)).map
      (fun v => vec M rt v)

/-- The attained set of count vectors is exactly `allowed`. -/
def ok (M : List (List Nat)) (h k : Nat) (allowed : List (Nat × Nat × Nat)) : Bool :=
  let got := (realised M h k).eraseDups
  got.all (fun c => allowed.contains c) && allowed.all (fun c => got.contains c)

theorem law_T_h2_k5 : ok Tm 2 5 [(2,2,1)] = true := by decide
theorem law_U_h2_k5 : ok Um 2 5 [(2,2,1)] = true := by decide
theorem law_T_h3_k5 : ok Tm 3 5 [(2,1,2)] = true := by decide
theorem law_U_h3_k5 : ok Um 3 5 [(2,1,2)] = true := by decide
theorem law_T_h2_k4 : ok Tm 2 4 [(1,2,1),(2,1,1),(2,2,0)] = true := by decide
theorem law_U_h2_k4 : ok Um 2 4 [(1,2,1),(2,1,1),(2,2,0)] = true := by decide
theorem law_T_h3_k4 : ok Tm 3 4 [(1,1,2),(2,0,2),(2,1,1)] = true := by decide
theorem law_U_h3_k4 : ok Um 3 4 [(1,1,2),(2,0,2),(2,1,1)] = true := by decide

/-- Both templates agree at every (h,k) that occurs (k in {4,5}, h in {2,3}). -/
theorem templates_agree :
    ((List.range 2).all fun h => (List.range 2).all fun k =>
      (realised Tm (h+2) (k+4)).eraseDups.all
        (fun c => ((realised Um (h+2) (k+4)).eraseDups).contains c) &&
      (realised Um (h+2) (k+4)).eraseDups.all
        (fun c => ((realised Tm (h+2) (k+4)).eraseDups).contains c)) = true := by
  decide

/-- The colour-1 class sizes of both templates are 4 or 5, ten of size 5 and five of size 4. -/
theorem class_sizes_T :
    ((List.range 15).map fun rt => (class1 Tm rt).length) = [4,5,5,4,5,4,5,4,5,5,5,5,5,5,4] := by
  decide
theorem class_sizes_U :
    ((List.range 15).map fun rt => (class1 Um rt).length) = [4,5,5,4,5,4,5,4,5,5,5,5,5,5,4] := by
  decide

/-- Ten roots of class size 5 and five of class size 4, in both templates: the shape of
the fifteen senders on every board. -/
theorem class_size_profile :
    ((List.range 15).filter fun rt => (class1 Tm rt).length == 5).length = 10 ∧
    ((List.range 15).filter fun rt => (class1 Tm rt).length == 4).length = 5 := by
  decide

end K58
