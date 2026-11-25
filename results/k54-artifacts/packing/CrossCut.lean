import Std

namespace R3333.CrossCut

/-- The enumeration has one occurrence for each pair of entries in the two lists. -/
def cross (xs : List α) (ys : List β) : List (α × β) :=
  xs.flatMap (fun x => ys.map (fun y => (x,y)))

private theorem cross_length (xs : List α) (ys : List β) :
    (cross xs ys).length = xs.length * ys.length := by
  induction xs with
  | nil => simp [cross]
  | cons x xs ih => simpa [cross, Nat.succ_mul, Nat.add_comm] using ih

private theorem size_of_distinct [DecidableEq α] (xs ys : List α) (nd : xs.Nodup)
    (included : ∀ x ∈ xs, x ∈ ys) : xs.length ≤ ys.length := by
  induction xs generalizing ys with
  | nil => simp
  | cons x xs ih =>
    obtain ⟨fresh, tail⟩ := List.nodup_cons.mp nd
    have present : x ∈ ys := included x (by simp)
    have smaller := ih (ys.erase x) tail (by
      intro v hv
      have ne : v ≠ x := by intro e; subst v; exact fresh hv
      exact (List.mem_erase_of_ne ne).mpr (included v (by simp [hv])))
    have len := List.length_erase_of_mem present
    have pos : 0 < ys.length := List.length_pos_iff.mpr (by intro h; simp [h] at present)
    simp only [List.length_cons]; omega

abbrev Row := List Nat × List Nat

def edges : List Row → Nat
  | [] => 0
  | (xs,ys) :: tail => xs.length + ys.length + edges tail

def pairOccurrences (rows : List Row) : List (Nat × Nat) :=
  rows.flatMap (fun r => cross r.1 r.2)

private theorem row_bound (a b : Nat) (ha : 0 < a) (hb : 0 < b) : a+b ≤ a*b+1 := by
  cases a <;> cases b <;> simp_all [Nat.succ_mul, Nat.mul_succ] <;> omega

private theorem incidence_bound (rows : List Row)
    (meet : ∀ r ∈ rows, 0 < r.1.length ∧ 0 < r.2.length) :
    edges rows ≤ rows.length + (pairOccurrences rows).length := by
  induction rows with
  | nil => simp [edges,pairOccurrences]
  | cons r rs ih =>
    obtain ⟨x,y⟩ := r
    obtain ⟨hx,hy⟩ := meet (x,y) (by simp)
    have z := row_bound x.length y.length hx hy
    have rest := ih (fun r hr => meet r (by simp [hr]))
    simp only [edges, List.length_cons, pairOccurrences, List.flatMap_cons,
      List.length_append, cross_length] at *
    omega

private theorem split_max :
    ∀ p q : Fin 14, p.val+q.val=13 → p.val*q.val≤42 := by decide

/-- With genuine neighbor lists, a repeated pair of columns identifies two
    distinct common rows. This theorem provides the counting part of the cut. -/
theorem forcedRepeat (rows : List Row) (left right : List Nat)
    (nrows : rows.length = 13) (ncols : left.length + right.length = 13)
    (meet : ∀ r ∈ rows, 0 < r.1.length ∧ 0 < r.2.length)
    (within : ∀ t ∈ pairOccurrences rows, t ∈ cross left right)
    (many : 56 ≤ edges rows) : ¬ (pairOccurrences rows).Nodup := by
  intro nd
  have prod := split_max ⟨left.length,by omega⟩ ⟨right.length,by omega⟩ ncols
  have upper := size_of_distinct _ _ nd within
  rw [cross_length] at upper
  have counted := incidence_bound rows meet
  change left.length * right.length ≤ 42 at prod
  omega

private theorem cross_mem (p : Nat × Nat) (xs ys : List Nat) :
    p ∈ cross xs ys ↔ p.1 ∈ xs ∧ p.2 ∈ ys := by
  rcases p with ⟨u,v⟩
  simp [cross]

private theorem cross_nodup (xs ys : List Nat) (hx : xs.Nodup) (hy : ys.Nodup) :
    (cross xs ys).Nodup := by
  apply List.pairwise_flatMap.mpr
  constructor
  · intro x _
    exact List.pairwise_map.mpr (hy.imp (fun h e => h (congrArg Prod.snd e)))
  · apply hx.imp
    intro x x' ne u hu v hv e
    rcases List.mem_map.mp hu with ⟨i,_,rfl⟩
    rcases List.mem_map.mp hv with ⟨j,_,rfl⟩
    exact ne (congrArg Prod.fst e)

/-- A 13-by-13 ordinary crossing graph with at least 56 edges, whose rows
    all meet the two parts, has a rectangle crossing that column cut. -/
theorem forcedRectangle (rows : List Row) (left right : List Nat)
    (nrows : rows.length = 13) (ncols : left.length + right.length = 13)
    (meet : ∀ r ∈ rows, 0 < r.1.length ∧ 0 < r.2.length)
    (simple : ∀ r ∈ rows, r.1.Nodup ∧ r.2.Nodup)
    (inside : ∀ r ∈ rows, (∀ x ∈ r.1, x ∈ left) ∧ (∀ y ∈ r.2, y ∈ right))
    (many : 56 ≤ edges rows) :
    ¬ rows.Pairwise (fun r s => ∀ p ∈ cross r.1 r.2, p ∉ cross s.1 s.2) := by
  intro disjoint
  apply forcedRepeat rows left right nrows ncols meet _ many
  · apply List.pairwise_flatMap.mpr
    constructor
    · intro r hr
      exact cross_nodup _ _ (simple r hr).1 (simple r hr).2
    · apply disjoint.imp
      intro a b h x hx y hy e
      exact h x hx (e ▸ hy)
  · intro t ht
    rcases List.mem_flatMap.mp ht with ⟨r,hr,hw⟩
    have h := (cross_mem t r.1 r.2).mp hw
    exact (cross_mem t left right).mpr ⟨(inside r hr).1 _ h.1, (inside r hr).2 _ h.2⟩

#print axioms forcedRectangle
end R3333.CrossCut
