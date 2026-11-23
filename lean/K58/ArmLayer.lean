/-
  The arm layer of the K58 cross-arm template test, kernel-checked.

  Context.  In the campaign's K58 profile (15,14,14,14) an *ordinary arm* is a
  14-set of outside vertices whose internal pairs carry three colours: the arm's
  own colour 0 and the two other colours 2 and 3 (the catalogue's convention,
  see armtypes14.txt).  The *Z-classes* of an ordinary arm are the classes of
  vertices with equal Z(x); an arm without a singleton has six Z-classes, two
  triples and four doubles, and the six *kinds* of cross-arm sender are the six
  class-pairs whose union is a *site* (no colour-0 pair inside; and, for a union
  of size 4, colour-3 degrees 1,1,2,2).  The catalogue replay reports that in
  every one of the 4,236 admissible internal placements the site relation is a
  six-cycle on the six classes, that each class has five owners, and that
  consequently the number of senders of each kind alternates between t and 5−t
  for t in {1,2,3,4}; a two-arm case then pairs such a vector for each arm,
  giving 4 × 4 = 16 count-vector pairs.

  This file kernel-checks that layer.

  * Part 1 (no data): if six kinds are the vertices of a six-cycle and the
    five-owner bookkeeping gives w k + w (k+1) = 5 around the cycle, then the
    count vector is alternating with total 15, so it is determined by the single
    integer t = w 0, and positivity forces t in {1,2,3,4}: exactly four count
    vectors per arm.  On an odd cycle there is no integral solution at all, so
    the site relation of an arm with a count vector cannot be two triangles, and on six classes two-regular relations
    are a six-cycle or two triangles, so a site relation carrying a count vector
    is a six-cycle.
  * Part 2 (data): the arm colourings of catalogue types 16 and 36, the six
    Z-classes of the displayed type-16 placement and of the three type-36
    placements, and a kernel-checked verification that in each case the site
    pairs are exactly the pairs of a six-cycle on the six classes, that each
    class lies on exactly two sites and every vertex on two (the hypothesis
    "each class has five owners"), and what the class and site sizes are.  It
    also records the number of intra-class colour-3 pairs of each placement
    (2, 5, 3, 7), which separates them.
  * Part 3 (data): the displayed type-16 partition has four distinct images
    under exhibited colour-preserving automorphisms of the arm colouring, and
    each image is again a valid six-cycle placement — the scope of the
    package's theorem on the type-16 side.

  `PlacementsIneq.lean` (Mathlib, importing this file) turns the numbers 2, 5,
  3, 7 into the theorem that the four placements are pairwise inequivalent:
  `intra3` is an invariant of a placement under colour-preserving vertex
  permutations.  So the factor 3 in "3 placements of type 36" is not a repeat,
  and 3 × 4 × (4 × 4) = 192 counts distinct cases.

  Nothing here uses Mathlib: `import Init.Omega` only.  No `decide` outside the
  kernel, no `native_decide`, and `#print axioms` at the end of the file shows
  the axiom sets.
-/
import Init.Omega

namespace K58

/-! ## Part 1: the alternating count vector -/

/-- Successor on the six kinds of a site six-cycle. -/
def nxt6 (k : Fin 6) : Fin 6 := ⟨(k.val + 1) % 6, by omega⟩

/-- **The count vector alternates.**  If the six kinds are the vertices of a
six-cycle and the five-owner bookkeeping gives `w k + w (k+1) = 5` around it,
then the counts on opposite kinds are equal and adjacent counts add to five:
the vector is `(t, 5-t, t, 5-t, t, 5-t)` with `t = w 0`. -/
theorem count_alternates (w : Fin 6 → Int) (h : ∀ k : Fin 6, w k + w (nxt6 k) = 5) :
    w 0 = w 2 ∧ w 2 = w 4 ∧ w 1 = w 3 ∧ w 3 = w 5 ∧
      w 0 + w 1 = 5 ∧ w 0 = w 0 := by
  have h0 : w 0 + w 1 = 5 := by
    have := h 0; rwa [show nxt6 0 = 1 from by decide] at this
  have h1 : w 1 + w 2 = 5 := by
    have := h 1; rwa [show nxt6 1 = 2 from by decide] at this
  have h2 : w 2 + w 3 = 5 := by
    have := h 2; rwa [show nxt6 2 = 3 from by decide] at this
  have h3 : w 3 + w 4 = 5 := by
    have := h 3; rwa [show nxt6 3 = 4 from by decide] at this
  have h4 : w 4 + w 5 = 5 := by
    have := h 4; rwa [show nxt6 4 = 5 from by decide] at this
  have h5 : w 5 + w 0 = 5 := by
    have := h 5; rwa [show nxt6 5 = 0 from by decide] at this
  refine ⟨by omega, by omega, by omega, by omega, h0, rfl⟩

/-- The six counts are determined by `t = w 0` and add up to the fifteen
senders of the root arm. -/
theorem count_form (w : Fin 6 → Int) (h : ∀ k : Fin 6, w k + w (nxt6 k) = 5) :
    w 0 = w 0 ∧ w 1 = 5 - w 0 ∧ w 2 = w 0 ∧ w 3 = 5 - w 0 ∧ w 4 = w 0 ∧
      w 5 = 5 - w 0 ∧ w 0 + w 1 + w 2 + w 3 + w 4 + w 5 = 15 := by
  have h0 : w 0 + w 1 = 5 := by
    have := h 0; rwa [show nxt6 0 = 1 from by decide] at this
  have h1 : w 1 + w 2 = 5 := by
    have := h 1; rwa [show nxt6 1 = 2 from by decide] at this
  have h2 : w 2 + w 3 = 5 := by
    have := h 2; rwa [show nxt6 2 = 3 from by decide] at this
  have h3 : w 3 + w 4 = 5 := by
    have := h 3; rwa [show nxt6 3 = 4 from by decide] at this
  have h4 : w 4 + w 5 = 5 := by
    have := h 4; rwa [show nxt6 4 = 5 from by decide] at this
  refine ⟨rfl, by omega, by omega, by omega, by omega, by omega, by omega⟩

/-- **Positivity gives exactly four count vectors.**  A count of senders is at
least one, so `t = w 0` lies in {1,2,3,4} and the vector is one of the four
alternating vectors. -/
theorem four_count_vectors (w : Fin 6 → Int) (h : ∀ k : Fin 6, w k + w (nxt6 k) = 5)
    (hpos : ∀ k : Fin 6, 1 ≤ w k) :
    1 ≤ w 0 ∧ w 0 ≤ 4 ∧ w 1 = 5 - w 0 ∧ w 2 = w 0 ∧ w 3 = 5 - w 0 ∧
      w 4 = w 0 ∧ w 5 = 5 - w 0 := by
  have h0 : w 0 + w 1 = 5 := by
    have := h 0; rwa [show nxt6 0 = 1 from by decide] at this
  have h1 : w 1 + w 2 = 5 := by
    have := h 1; rwa [show nxt6 1 = 2 from by decide] at this
  have h2 : w 2 + w 3 = 5 := by
    have := h 2; rwa [show nxt6 2 = 3 from by decide] at this
  have h3 : w 3 + w 4 = 5 := by
    have := h 3; rwa [show nxt6 3 = 4 from by decide] at this
  have h4 : w 4 + w 5 = 5 := by
    have := h 4; rwa [show nxt6 4 = 5 from by decide] at this
  have p0 := hpos 0
  have p1 := hpos 1
  refine ⟨p0, by omega, by omega, by omega, by omega, by omega, by omega⟩

/-- Each of the four alternating vectors really is a count vector: the five-owner
equations hold and every entry lies in [1,4]. -/
theorem alternating_solutions (t : Int) (h1 : 1 ≤ t) (h4 : t ≤ 4) :
    (∀ k : Fin 6, (fun j : Fin 6 => if j.val % 2 = 0 then t else 5 - t) k +
        (fun j : Fin 6 => if j.val % 2 = 0 then t else 5 - t) (nxt6 k) = 5)
      ∧ (∀ k : Fin 6, 1 ≤ (fun j : Fin 6 => if j.val % 2 = 0 then t else 5 - t) k
          ∧ (fun j : Fin 6 => if j.val % 2 = 0 then t else 5 - t) k ≤ 4) := by
  refine ⟨?_, ?_⟩
  · intro k
    rcases (show k = 0 ∨ k = 1 ∨ k = 2 ∨ k = 3 ∨ k = 4 ∨ k = 5 from by
      revert k; decide) with rfl | rfl | rfl | rfl | rfl | rfl <;>
      simp [nxt6] <;> omega
  · intro k
    rcases (show k = 0 ∨ k = 1 ∨ k = 2 ∨ k = 3 ∨ k = 4 ∨ k = 5 from by
      revert k; decide) with rfl | rfl | rfl | rfl | rfl | rfl <;>
      simp <;> omega

/-- **No integral count vector on an odd cycle.**  Two triangles cannot carry a
count vector: adding the three five-owner equations of a triangle forces
`2 (w 0 + w 1 + w 2) = 15`.  Since the site relation of a count-carrying arm is
2-regular on the six classes and six edges on six vertices are either a
six-cycle or two triangles, an arm with a count vector has a six-cycle site
relation. -/
theorem no_triangle_weights (w : Fin 3 → Int)
    (h01 : w 0 + w 1 = 5) (h12 : w 1 + w 2 = 5) (h20 : w 2 + w 0 = 5) : False := by
  omega

/-- Two arms: the pair of count vectors is determined by `(t, s)`, the number of
senders of the first kind in each arm, and `(t,s)` ranges over 4 × 4 = 16 pairs:
the factor 16 of the cross-arm case count. -/
theorem count_vector_pairs :
    (∀ t s t' s' : Int, 1 ≤ t → t ≤ 4 → 1 ≤ s → s ≤ 4 → 1 ≤ t' → t' ≤ 4 →
      1 ≤ s' → s' ≤ 4 →
      (t = t' ∧ s = s' ↔
        ((fun k : Fin 6 => if k.val % 2 = 0 then t else 5 - t) =
          (fun k : Fin 6 => if k.val % 2 = 0 then t' else 5 - t')) ∧
        ((fun k : Fin 6 => if k.val % 2 = 0 then s else 5 - s) =
          (fun k : Fin 6 => if k.val % 2 = 0 then s' else 5 - s')))) ∧
    (4 : Nat) * 4 = 16 := by
  refine ⟨?_, by decide⟩
  intro t s t' s' ht1 ht4 hs1 hs4 ht1' ht4' hs1' hs4'
  constructor
  · rintro ⟨rfl, rfl⟩; exact ⟨rfl, rfl⟩
  · rintro ⟨hf, hg⟩
    have h1 : t = t' := by have := congrFun hf 0; simpa using this
    have h2 : s = s' := by have := congrFun hg 0; simpa using this
    exact ⟨h1, h2⟩




/-! ## Part 2: the four placements and their site systems -/

/-- `l₁ × l₂`, in lexicographic order. -/
def prod : List α → List α → List (α × α)
  | [], _ => []
  | a :: as, l => l.map (fun b => (a, b)) ++ prod as l

/-- Entry `14 * i + j` of the arm colouring. -/
def col (m : List Nat) (i j : Nat) : Nat := m.getD (14 * i + j) 0

/-- The class of a vertex. -/
def clsOf (cls : List Nat) (x : Nat) : Nat := cls.getD x 999

/-- The vertices of class `k`. -/
def cv (cls : List Nat) (k : Nat) : List Nat := (List.range 14).filter (fun x => clsOf cls x == k)

/-- The number of vertices of class `k`. -/
def csize (cls : List Nat) (k : Nat) : Nat := (cv cls k).length

/-- Colour-3 degree of `x` inside `S`. -/
def deg3 (m : List Nat) (S : List Nat) (x : Nat) : Nat :=
  (S.filter (fun y => y != x && col m x y == 3)).length

/-- Number of occurrences of `v` in `l`. -/
def cntv (l : List Nat) (v : Nat) : Nat := (l.filter (fun z => z == v)).length

/-- No arm-colour pair inside `S`. -/
def noZero (m : List Nat) (S : List Nat) : Bool :=
  S.all (fun x => S.all (fun y => (x == y) || (col m x y != 0)))

/-- The package's site condition on the union of classes `k` and `l`: size 4 or 5,
no arm-colour pair inside, and, for a union of size 4, colour-3 degrees 1,1,2,2. -/
def isSite (m cls : List Nat) (k l : Nat) : Bool :=
  let S := cv cls k ++ cv cls l
  if S.length == 4 then
    noZero m S && cntv (S.map (fun x => deg3 m S x)) 1 == 2 &&
      cntv (S.map (fun x => deg3 m S x)) 2 == 2
  else if S.length == 5 then noZero m S
  else false

/-- The kinds of sender: the class pairs whose union is a site. -/
def sitePairs (m cls : List Nat) : List (Nat × Nat) :=
  (prod (List.range 6) (List.range 6)).filter (fun p => p.1 < p.2 && isSite m cls p.1 p.2)

/-- How many sites the class `k` lies on: the number of kinds a vertex of that
class can be sent with.  The campaign's "each class has five owners" says the
senders using these kinds add up to five. -/
def siteDeg (sl : List (Nat × Nat)) (k : Nat) : Nat :=
  (sl.filter (fun p => p.1 == k || p.2 == k)).length

/-- The number of kinds whose site holds the vertex `x`, i.e. of kinds the class
of `x` is joined with.  The package's `weights` propagates the five-owner
equations along exactly this incidence, and asserts that every vertex lies on
two sites. -/
def vertexKinds (cls : List Nat) (sl : List (Nat × Nat)) (x : Nat) : Nat :=
  (sl.filter (fun p => p.1 == clsOf cls x || p.2 == clsOf cls x)).length

/-- The positions in the kind list of the two kinds that the class `j` lies on. -/
def kindsOf (sl : List (Nat × Nat)) (j : Nat) : List Nat :=
  (List.range 6).filter (fun k => (sl.getD k (0, 0)).1 == j || (sl.getD k (0, 0)).2 == j)

/-- The number of colour-3 pairs with both ends in one Z-class: an invariant of a
placement under colour-preserving permutations of the fourteen vertices. -/
def intra3 (m cls : List Nat) : Nat :=
  ((prod (List.range 14) (List.range 14)).filter
    (fun p => p.1 < p.2 && clsOf cls p.1 == clsOf cls p.2 && col m p.1 p.2 == 3)).length

/-- Arm colouring of the `display16` placement (data from `armtypes14.txt`, row-major). -/
def m_display16 : List Nat :=
  [0, 2, 3, 3, 2, 0, 0, 2, 0, 0, 2, 2, 3, 3, 2, 0, 2, 3, 3, 2, 0, 0, 2, 0, 3, 0, 3, 2, 3, 2, 0, 2, 3, 3, 2, 0, 0, 0, 3, 0, 2, 0, 3, 3, 2, 0, 2, 3, 3, 2, 0, 0, 2, 0, 0, 0, 2, 3, 3, 2, 0, 2, 3, 3, 2, 0, 0, 0, 0, 0, 0, 2, 3, 3, 2, 0, 2, 3, 3, 2, 0, 0, 0, 0, 0, 0, 2, 3, 3, 2, 0, 2, 3, 3, 0, 2, 0, 0, 2, 0, 0, 2, 3, 3, 2, 0, 2, 3, 0, 3, 0, 2, 0, 2, 0, 0, 2, 3, 3, 2, 0, 2, 0, 3, 2, 3, 0, 0, 0, 0, 0, 2, 3, 3, 2, 0, 2, 2, 3, 3, 2, 3, 3, 2, 0, 0, 0, 0, 0, 2, 0, 3, 2, 3, 2, 0, 0, 0, 0, 0, 2, 3, 3, 2, 3, 0, 3, 2, 3, 3, 2, 0, 0, 0, 0, 0, 2, 3, 2, 3, 0, 2, 3, 2, 0, 0, 0, 0, 0, 2, 3, 3, 3, 2, 2, 0]

/-- Z-class of each vertex, for the `display16` placement (data from `cases.json`). -/
def cls_display16 : List Nat :=
  [0, 0, 0, 1, 1, 2, 2, 2, 3, 3, 4, 5, 4, 5]

/-- The six kinds of the `display16` placement, in the cyclic order of its site system:
ikind `k` joins the classes at positions `k` and `k+1` and the last joins position 5 to 0. -/
def sites_display16 : List (Nat × Nat) :=
  [(0, 1), (1, 2), (2, 3), (3, 5), (5, 4), (4, 0)]

/-- Arm colouring of the `p36_0` placement (data from `armtypes14.txt`, row-major). -/
def m_p36_0 : List Nat :=
  [0, 2, 3, 3, 2, 0, 2, 0, 3, 2, 3, 2, 0, 3, 2, 0, 3, 2, 3, 2, 0, 3, 0, 3, 2, 0, 2, 3, 3, 3, 0, 2, 2, 3, 3, 0, 0, 2, 2, 0, 0, 0, 3, 2, 2, 0, 3, 3, 2, 0, 2, 3, 0, 0, 0, 0, 2, 3, 2, 3, 0, 2, 3, 2, 0, 0, 3, 0, 0, 0, 0, 2, 3, 3, 2, 0, 2, 3, 2, 0, 0, 0, 3, 0, 2, 0, 3, 2, 3, 2, 0, 2, 3, 0, 0, 3, 0, 0, 0, 3, 0, 0, 2, 3, 2, 0, 3, 0, 3, 3, 2, 2, 3, 0, 0, 2, 0, 2, 3, 3, 0, 3, 0, 2, 3, 2, 2, 3, 2, 3, 0, 0, 0, 0, 3, 0, 3, 3, 2, 2, 3, 2, 2, 0, 3, 0, 0, 3, 0, 3, 0, 2, 3, 2, 2, 0, 0, 0, 0, 0, 3, 3, 2, 3, 2, 0, 2, 3, 0, 2, 0, 0, 0, 3, 0, 2, 3, 2, 3, 2, 0, 3, 3, 3, 0, 0, 0, 0, 0, 2, 2, 2, 2, 3, 3, 0]

/-- Z-class of each vertex, for the `p36_0` placement (data from `cases.json`). -/
def cls_p36_0 : List Nat :=
  [0, 0, 1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5]

/-- The six kinds of the `p36_0` placement, in the cyclic order of its site system:
ikind `k` joins the classes at positions `k` and `k+1` and the last joins position 5 to 0. -/
def sites_p36_0 : List (Nat × Nat) :=
  [(0, 1), (1, 2), (2, 3), (3, 5), (5, 4), (4, 0)]

/-- Arm colouring of the `p36_1` placement (data from `armtypes14.txt`, row-major). -/
def m_p36_1 : List Nat :=
  [0, 2, 3, 3, 2, 0, 2, 0, 3, 2, 3, 2, 0, 3, 2, 0, 3, 2, 3, 2, 0, 3, 0, 3, 2, 0, 2, 3, 3, 3, 0, 2, 2, 3, 3, 0, 0, 2, 2, 0, 0, 0, 3, 2, 2, 0, 3, 3, 2, 0, 2, 3, 0, 0, 0, 0, 2, 3, 2, 3, 0, 2, 3, 2, 0, 0, 3, 0, 0, 0, 0, 2, 3, 3, 2, 0, 2, 3, 2, 0, 0, 0, 3, 0, 2, 0, 3, 2, 3, 2, 0, 2, 3, 0, 0, 3, 0, 0, 0, 3, 0, 0, 2, 3, 2, 0, 3, 0, 3, 3, 2, 2, 3, 0, 0, 2, 0, 2, 3, 3, 0, 3, 0, 2, 3, 2, 2, 3, 2, 3, 0, 0, 0, 0, 3, 0, 3, 3, 2, 2, 3, 2, 2, 0, 3, 0, 0, 3, 0, 3, 0, 2, 3, 2, 2, 0, 0, 0, 0, 0, 3, 3, 2, 3, 2, 0, 2, 3, 0, 2, 0, 0, 0, 3, 0, 2, 3, 2, 3, 2, 0, 3, 3, 3, 0, 0, 0, 0, 0, 2, 2, 2, 2, 3, 3, 0]

/-- Z-class of each vertex, for the `p36_1` placement (data from `cases.json`). -/
def cls_p36_1 : List Nat :=
  [0, 0, 1, 1, 1, 2, 2, 3, 3, 5, 5, 4, 4, 5]

/-- The six kinds of the `p36_1` placement, in the cyclic order of its site system:
ikind `k` joins the classes at positions `k` and `k+1` and the last joins position 5 to 0. -/
def sites_p36_1 : List (Nat × Nat) :=
  [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]

/-- Arm colouring of the `p36_2` placement (data from `armtypes14.txt`, row-major). -/
def m_p36_2 : List Nat :=
  [0, 2, 3, 3, 2, 0, 2, 0, 3, 2, 3, 2, 0, 3, 2, 0, 3, 2, 3, 2, 0, 3, 0, 3, 2, 0, 2, 3, 3, 3, 0, 2, 2, 3, 3, 0, 0, 2, 2, 0, 0, 0, 3, 2, 2, 0, 3, 3, 2, 0, 2, 3, 0, 0, 0, 0, 2, 3, 2, 3, 0, 2, 3, 2, 0, 0, 3, 0, 0, 0, 0, 2, 3, 3, 2, 0, 2, 3, 2, 0, 0, 0, 3, 0, 2, 0, 3, 2, 3, 2, 0, 2, 3, 0, 0, 3, 0, 0, 0, 3, 0, 0, 2, 3, 2, 0, 3, 0, 3, 3, 2, 2, 3, 0, 0, 2, 0, 2, 3, 3, 0, 3, 0, 2, 3, 2, 2, 3, 2, 3, 0, 0, 0, 0, 3, 0, 3, 3, 2, 2, 3, 2, 2, 0, 3, 0, 0, 3, 0, 3, 0, 2, 3, 2, 2, 0, 0, 0, 0, 0, 3, 3, 2, 3, 2, 0, 2, 3, 0, 2, 0, 0, 0, 3, 0, 2, 3, 2, 3, 2, 0, 3, 3, 3, 0, 0, 0, 0, 0, 2, 2, 2, 2, 3, 3, 0]

/-- Z-class of each vertex, for the `p36_2` placement (data from `cases.json`). -/
def cls_p36_2 : List Nat :=
  [0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5]

/-- The six kinds of the `p36_2` placement, in the cyclic order of its site system:
ikind `k` joins the classes at positions `k` and `k+1` and the last joins position 5 to 0. -/
def sites_p36_2 : List (Nat × Nat) :=
  [(0, 1), (1, 2), (2, 3), (3, 5), (5, 4), (4, 0)]

/-- **The site system of the `display16` placement.**  The six kinds of sender are the
six class pairs of one six-cycle on the six Z-classes; every class lies on exactly
two kinds; the class sizes are two triples and four doubles; the classes are the
vertex sets listed; each of the six pairs listed in cyclic order really is a site;
and the placement has 2 intra-class colour-3 pairs. -/
theorem facts_display16 :
    sitePairs m_display16 cls_display16 = [(0, 1), (0, 4), (1, 2), (2, 3), (3, 5), (4, 5)] ∧
    sites_display16 = [(0, 1), (1, 2), (2, 3), (3, 5), (5, 4), (4, 0)] ∧
    (List.range 6).map (fun k => siteDeg (sitePairs m_display16 cls_display16) k) = [2, 2, 2, 2, 2, 2] ∧
    (List.range 6).map (fun j => kindsOf sites_display16 j) = [[0, 5], [0, 1], [1, 2], [2, 3], [4, 5], [3, 4]] ∧
    (List.range 14).map (fun x => vertexKinds cls_display16 sites_display16 x) = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2] ∧
    (List.range 6).map (fun k => csize cls_display16 k) = [3, 2, 3, 2, 2, 2] ∧
    (List.range 6).map (fun k => cv cls_display16 k) = [[0, 1, 2], [3, 4], [5, 6, 7], [8, 9], [10, 12], [11, 13]] ∧
    sites_display16.map (fun p => isSite m_display16 cls_display16 p.1 p.2) = [true, true, true, true, true, true] ∧
    sites_display16.map (fun p => csize cls_display16 p.1 + csize cls_display16 p.2) = [5, 5, 5, 4, 4, 5] ∧
    intra3 m_display16 cls_display16 = 2 := by
  decide

/-- **The site system of the `p36_0` placement.**  The six kinds of sender are the
six class pairs of one six-cycle on the six Z-classes; every class lies on exactly
two kinds; the class sizes are two triples and four doubles; the classes are the
vertex sets listed; each of the six pairs listed in cyclic order really is a site;
and the placement has 5 intra-class colour-3 pairs. -/
theorem facts_p36_0 :
    sitePairs m_p36_0 cls_p36_0 = [(0, 1), (0, 4), (1, 2), (2, 3), (3, 5), (4, 5)] ∧
    sites_p36_0 = [(0, 1), (1, 2), (2, 3), (3, 5), (5, 4), (4, 0)] ∧
    (List.range 6).map (fun k => siteDeg (sitePairs m_p36_0 cls_p36_0) k) = [2, 2, 2, 2, 2, 2] ∧
    (List.range 6).map (fun j => kindsOf sites_p36_0 j) = [[0, 5], [0, 1], [1, 2], [2, 3], [4, 5], [3, 4]] ∧
    (List.range 14).map (fun x => vertexKinds cls_p36_0 sites_p36_0 x) = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2] ∧
    (List.range 6).map (fun k => csize cls_p36_0 k) = [2, 3, 2, 2, 2, 3] ∧
    (List.range 6).map (fun k => cv cls_p36_0 k) = [[0, 1], [2, 3, 4], [5, 6], [7, 8], [9, 10], [11, 12, 13]] ∧
    sites_p36_0.map (fun p => isSite m_p36_0 cls_p36_0 p.1 p.2) = [true, true, true, true, true, true] ∧
    sites_p36_0.map (fun p => csize cls_p36_0 p.1 + csize cls_p36_0 p.2) = [5, 5, 4, 5, 5, 4] ∧
    intra3 m_p36_0 cls_p36_0 = 5 := by
  decide

/-- **The site system of the `p36_1` placement.**  The six kinds of sender are the
six class pairs of one six-cycle on the six Z-classes; every class lies on exactly
two kinds; the class sizes are two triples and four doubles; the classes are the
vertex sets listed; each of the six pairs listed in cyclic order really is a site;
and the placement has 3 intra-class colour-3 pairs. -/
theorem facts_p36_1 :
    sitePairs m_p36_1 cls_p36_1 = [(0, 1), (0, 5), (1, 2), (2, 3), (3, 4), (4, 5)] ∧
    sites_p36_1 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)] ∧
    (List.range 6).map (fun k => siteDeg (sitePairs m_p36_1 cls_p36_1) k) = [2, 2, 2, 2, 2, 2] ∧
    (List.range 6).map (fun j => kindsOf sites_p36_1 j) = [[0, 5], [0, 1], [1, 2], [2, 3], [3, 4], [4, 5]] ∧
    (List.range 14).map (fun x => vertexKinds cls_p36_1 sites_p36_1 x) = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2] ∧
    (List.range 6).map (fun k => csize cls_p36_1 k) = [2, 3, 2, 2, 2, 3] ∧
    (List.range 6).map (fun k => cv cls_p36_1 k) = [[0, 1], [2, 3, 4], [5, 6], [7, 8], [11, 12], [9, 10, 13]] ∧
    sites_p36_1.map (fun p => isSite m_p36_1 cls_p36_1 p.1 p.2) = [true, true, true, true, true, true] ∧
    sites_p36_1.map (fun p => csize cls_p36_1 p.1 + csize cls_p36_1 p.2) = [5, 5, 4, 4, 5, 5] ∧
    intra3 m_p36_1 cls_p36_1 = 3 := by
  decide

/-- **The site system of the `p36_2` placement.**  The six kinds of sender are the
six class pairs of one six-cycle on the six Z-classes; every class lies on exactly
two kinds; the class sizes are two triples and four doubles; the classes are the
vertex sets listed; each of the six pairs listed in cyclic order really is a site;
and the placement has 7 intra-class colour-3 pairs. -/
theorem facts_p36_2 :
    sitePairs m_p36_2 cls_p36_2 = [(0, 1), (0, 4), (1, 2), (2, 3), (3, 5), (4, 5)] ∧
    sites_p36_2 = [(0, 1), (1, 2), (2, 3), (3, 5), (5, 4), (4, 0)] ∧
    (List.range 6).map (fun k => siteDeg (sitePairs m_p36_2 cls_p36_2) k) = [2, 2, 2, 2, 2, 2] ∧
    (List.range 6).map (fun j => kindsOf sites_p36_2 j) = [[0, 5], [0, 1], [1, 2], [2, 3], [4, 5], [3, 4]] ∧
    (List.range 14).map (fun x => vertexKinds cls_p36_2 sites_p36_2 x) = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2] ∧
    (List.range 6).map (fun k => csize cls_p36_2 k) = [3, 2, 2, 2, 2, 3] ∧
    (List.range 6).map (fun k => cv cls_p36_2 k) = [[0, 1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12, 13]] ∧
    sites_p36_2.map (fun p => isSite m_p36_2 cls_p36_2 p.1 p.2) = [true, true, true, true, true, true] ∧
    sites_p36_2.map (fun p => csize cls_p36_2 p.1 + csize cls_p36_2 p.2) = [5, 4, 4, 5, 5, 5] ∧
    intra3 m_p36_2 cls_p36_2 = 7 := by
  decide

/-- **The count vector of the `display16` placement.**  Index the counts by its six
kinds in the cyclic order `sites_display16`.  Each class lies on two consecutive kinds
(`facts_display16`), and every sender of the root arm owns exactly two classes, so the
five senders that own a class fall into the two kinds meeting there and the
counts satisfy the six cyclic equations.  Hence the count vector is alternating,
with `t = w 0` in `{1,2,3,4}`: four count vectors for this placement. -/
theorem count_vector_display16 (w : Fin 6 → Int)
    (h : ∀ k : Fin 6, w k + w (nxt6 k) = 5) (hpos : ∀ k : Fin 6, 1 ≤ w k) :
    1 ≤ w 0 ∧ w 0 ≤ 4 ∧ w 1 = 5 - w 0 ∧ w 2 = w 0 ∧ w 3 = 5 - w 0 ∧ w 4 = w 0 ∧
      w 5 = 5 - w 0 :=
  four_count_vectors w h hpos

/-- **The count vector of the `p36_0` placement.**  Index the counts by its six
kinds in the cyclic order `sites_p36_0`.  Each class lies on two consecutive kinds
(`facts_p36_0`), and every sender of the root arm owns exactly two classes, so the
five senders that own a class fall into the two kinds meeting there and the
counts satisfy the six cyclic equations.  Hence the count vector is alternating,
with `t = w 0` in `{1,2,3,4}`: four count vectors for this placement. -/
theorem count_vector_p36_0 (w : Fin 6 → Int)
    (h : ∀ k : Fin 6, w k + w (nxt6 k) = 5) (hpos : ∀ k : Fin 6, 1 ≤ w k) :
    1 ≤ w 0 ∧ w 0 ≤ 4 ∧ w 1 = 5 - w 0 ∧ w 2 = w 0 ∧ w 3 = 5 - w 0 ∧ w 4 = w 0 ∧
      w 5 = 5 - w 0 :=
  four_count_vectors w h hpos

/-- **The count vector of the `p36_1` placement.**  Index the counts by its six
kinds in the cyclic order `sites_p36_1`.  Each class lies on two consecutive kinds
(`facts_p36_1`), and every sender of the root arm owns exactly two classes, so the
five senders that own a class fall into the two kinds meeting there and the
counts satisfy the six cyclic equations.  Hence the count vector is alternating,
with `t = w 0` in `{1,2,3,4}`: four count vectors for this placement. -/
theorem count_vector_p36_1 (w : Fin 6 → Int)
    (h : ∀ k : Fin 6, w k + w (nxt6 k) = 5) (hpos : ∀ k : Fin 6, 1 ≤ w k) :
    1 ≤ w 0 ∧ w 0 ≤ 4 ∧ w 1 = 5 - w 0 ∧ w 2 = w 0 ∧ w 3 = 5 - w 0 ∧ w 4 = w 0 ∧
      w 5 = 5 - w 0 :=
  four_count_vectors w h hpos

/-- **The count vector of the `p36_2` placement.**  Index the counts by its six
kinds in the cyclic order `sites_p36_2`.  Each class lies on two consecutive kinds
(`facts_p36_2`), and every sender of the root arm owns exactly two classes, so the
five senders that own a class fall into the two kinds meeting there and the
counts satisfy the six cyclic equations.  Hence the count vector is alternating,
with `t = w 0` in `{1,2,3,4}`: four count vectors for this placement. -/
theorem count_vector_p36_2 (w : Fin 6 → Int)
    (h : ∀ k : Fin 6, w k + w (nxt6 k) = 5) (hpos : ∀ k : Fin 6, 1 ≤ w k) :
    1 ≤ w 0 ∧ w 0 ≤ 4 ∧ w 1 = 5 - w 0 ∧ w 2 = w 0 ∧ w 3 = 5 - w 0 ∧ w 4 = w 0 ∧
      w 5 = 5 - w 0 :=
  four_count_vectors w h hpos

/-! ### The four placements are pairwise inequivalent

`intra3` counts the colour-3 pairs whose two ends lie in one Z-class.  A
colour-preserving permutation of the fourteen vertices carries Z-classes to
Z-classes and preserves every colour, so it preserves this number; two
placements with different values therefore cannot be equivalent.  The values are
`2` (displayed type 16), `5`, `3`, `7` (the three
type-36 placements), all distinct.  So the "3 placements" of type 36 are three
distinct placements, and with four pairs of colour orientations and the sixteen
count-vector pairs of Part 1 the case count of the cross-arm test is
`3 * 4 * (4 * 4) = 192`. -/

theorem intra3_distinct :
    intra3 m_display16 cls_display16 = 2 ∧ intra3 m_p36_0 cls_p36_0 = 5 ∧
      intra3 m_p36_1 cls_p36_1 = 3 ∧ intra3 m_p36_2 cls_p36_2 = 7 ∧
      2 ≠ 5 ∧ 5 ≠ 3 ∧ 3 ≠ 7 ∧
      2 ≠ 3 ∧ 2 ≠ 7 ∧ 5 ≠ 7 := by
  decide

/-- The case count of the cross-arm test: three placements of type 36, four pairs
of colour orientations, and the sixteen count-vector pairs derived in Part 1. -/
theorem case_count : 3 * 4 * (4 * 4) = 192 := by decide

/-! ## Part 3: the four images of the displayed type-16 partition

The package's theorem is stated for the displayed equal-Z partition and its four
images under colour-preserving automorphisms of the type-16 arm.  Below, for each
of the four images: the vertex permutation that produces it, a kernel check that
the permutation is a bijection of `{0..13}` preserving every colour of the arm,
a check that it carries the displayed partition to the image partition, and the
same site-system facts as in Part 2.

`autOK p` is the whole certificate for one permutation: a bijection of the
fourteen vertices that preserves the arm colouring. -/

/-- The six class masks of a class map. -/
def masksOf (cls : List Nat) : List Nat :=
  (List.range 6).map (fun j =>
    (List.range 14).foldl (fun acc x => if clsOf cls x == j then acc + 2 ^ x else acc) 0)

/-- `p` is a bijection of `{0,...,13}`. -/
def isBijection14 (p : List Nat) : Bool :=
  (List.range 14).all (fun y => ((List.range 14).filter (fun x => p.getD x 999 == y)).length == 1)

/-- `p` preserves every colour of the arm `m` (including the diagonal). -/
def preservesColours (m : List Nat) (p : List Nat) : Bool :=
  (List.range 14).all (fun x => (List.range 14).all (fun y =>
    col m (p.getD x 999) (p.getD y 999) == col m x y))

/-- `p` carries the partition `cls₁` to the partition `cls₂`. -/
def carriesPartition (cls₁ cls₂ p : List Nat) : Bool :=
  (List.range 14).all (fun x => (List.range 14).all (fun y =>
    (clsOf cls₂ (p.getD x 999) == clsOf cls₂ (p.getD y 999)) ==
      (clsOf cls₁ x == clsOf cls₁ y)))

/-- Vertex permutation giving image `0` of the displayed type-16 partition. -/
def perm_img0 : List Nat := [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

/-- The Z-classes of image `0`, as a class map on the fourteen vertices. -/
def cls_img0 : List Nat := [0, 0, 0, 1, 1, 2, 2, 2, 3, 3, 4, 5, 4, 5]

/-- The six class masks of image `0`. -/
def masks_img0 : List Nat := [7, 24, 224, 768, 5120, 10240]

/-- The six kinds of image `0`, in the cyclic order of its site system. -/
def sites_img0 : List (Nat × Nat) := [(0, 1), (1, 2), (2, 3), (3, 5), (5, 4), (4, 0)]

/-- **Image `0` of the displayed type-16 partition.**  The permutation is a
colour-preserving bijection, it carries the displayed partition to this one, and
the resulting placement has the same six-cycle site structure. -/
theorem image0_facts :
    isBijection14 perm_img0 = true ∧
    preservesColours m_display16 perm_img0 = true ∧
    carriesPartition cls_display16 cls_img0 perm_img0 = true ∧
    sitePairs m_display16 cls_img0 = [(0, 1), (0, 4), (1, 2), (2, 3), (3, 5), (4, 5)] ∧
    sites_img0 = [(0, 1), (1, 2), (2, 3), (3, 5), (5, 4), (4, 0)] ∧
    (List.range 6).map (fun j => siteDeg (sitePairs m_display16 cls_img0) j) = [2, 2, 2, 2, 2, 2] ∧
    (List.range 6).map (fun j => kindsOf sites_img0 j) = [[0, 5], [0, 1], [1, 2], [2, 3], [4, 5], [3, 4]] ∧
    (List.range 14).map (fun x => vertexKinds cls_img0 sites_img0 x) = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2] ∧
    masksOf cls_img0 = masks_img0 ∧
    (List.range 6).map (fun j => csize cls_img0 j) = [3, 2, 3, 2, 2, 2] ∧
    (List.range 6).map (fun j => cv cls_img0 j) = [[0, 1, 2], [3, 4], [5, 6, 7], [8, 9], [10, 12], [11, 13]] ∧
    sites_img0.map (fun p => isSite m_display16 cls_img0 p.1 p.2) = [true, true, true, true, true, true] ∧
    intra3 m_display16 cls_img0 = 2 := by
  decide

/-- Vertex permutation giving image `1` of the displayed type-16 partition. -/
def perm_img1 : List Nat := [7, 8, 9, 11, 13, 12, 10, 0, 1, 2, 6, 3, 5, 4]

/-- The Z-classes of image `1`, as a class map on the fourteen vertices. -/
def cls_img1 : List Nat := [0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 0, 5, 0, 5]

/-- The six class masks of image `1`. -/
def masks_img1 : List Nat := [5121, 6, 24, 96, 896, 10240]

/-- The six kinds of image `1`, in the cyclic order of its site system. -/
def sites_img1 : List (Nat × Nat) := [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]

/-- **Image `1` of the displayed type-16 partition.**  The permutation is a
colour-preserving bijection, it carries the displayed partition to this one, and
the resulting placement has the same six-cycle site structure. -/
theorem image1_facts :
    isBijection14 perm_img1 = true ∧
    preservesColours m_display16 perm_img1 = true ∧
    carriesPartition cls_display16 cls_img1 perm_img1 = true ∧
    sitePairs m_display16 cls_img1 = [(0, 1), (0, 5), (1, 2), (2, 3), (3, 4), (4, 5)] ∧
    sites_img1 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)] ∧
    (List.range 6).map (fun j => siteDeg (sitePairs m_display16 cls_img1) j) = [2, 2, 2, 2, 2, 2] ∧
    (List.range 6).map (fun j => kindsOf sites_img1 j) = [[0, 5], [0, 1], [1, 2], [2, 3], [3, 4], [4, 5]] ∧
    (List.range 14).map (fun x => vertexKinds cls_img1 sites_img1 x) = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2] ∧
    masksOf cls_img1 = masks_img1 ∧
    (List.range 6).map (fun j => csize cls_img1 j) = [3, 2, 2, 2, 3, 2] ∧
    (List.range 6).map (fun j => cv cls_img1 j) = [[0, 10, 12], [1, 2], [3, 4], [5, 6], [7, 8, 9], [11, 13]] ∧
    sites_img1.map (fun p => isSite m_display16 cls_img1 p.1 p.2) = [true, true, true, true, true, true] ∧
    intra3 m_display16 cls_img1 = 2 := by
  decide

/-- Vertex permutation giving image `2` of the displayed type-16 partition. -/
def perm_img2 : List Nat := [1, 0, 10, 12, 13, 11, 9, 8, 7, 6, 2, 5, 3, 4]

/-- The Z-classes of image `2`, as a class map on the fourteen vertices. -/
def cls_img2 : List Nat := [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 0, 4, 5, 5]

/-- The six class masks of image `2`. -/
def masks_img2 : List Nat := [1027, 12, 48, 192, 2816, 12288]

/-- The six kinds of image `2`, in the cyclic order of its site system. -/
def sites_img2 : List (Nat × Nat) := [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]

/-- **Image `2` of the displayed type-16 partition.**  The permutation is a
colour-preserving bijection, it carries the displayed partition to this one, and
the resulting placement has the same six-cycle site structure. -/
theorem image2_facts :
    isBijection14 perm_img2 = true ∧
    preservesColours m_display16 perm_img2 = true ∧
    carriesPartition cls_display16 cls_img2 perm_img2 = true ∧
    sitePairs m_display16 cls_img2 = [(0, 1), (0, 5), (1, 2), (2, 3), (3, 4), (4, 5)] ∧
    sites_img2 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)] ∧
    (List.range 6).map (fun j => siteDeg (sitePairs m_display16 cls_img2) j) = [2, 2, 2, 2, 2, 2] ∧
    (List.range 6).map (fun j => kindsOf sites_img2 j) = [[0, 5], [0, 1], [1, 2], [2, 3], [3, 4], [4, 5]] ∧
    (List.range 14).map (fun x => vertexKinds cls_img2 sites_img2 x) = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2] ∧
    masksOf cls_img2 = masks_img2 ∧
    (List.range 6).map (fun j => csize cls_img2 j) = [3, 2, 2, 2, 3, 2] ∧
    (List.range 6).map (fun j => cv cls_img2 j) = [[0, 1, 10], [2, 3], [4, 5], [6, 7], [8, 9, 11], [12, 13]] ∧
    sites_img2.map (fun p => isSite m_display16 cls_img2 p.1 p.2) = [true, true, true, true, true, true] ∧
    intra3 m_display16 cls_img2 = 2 := by
  decide

/-- Vertex permutation giving image `3` of the displayed type-16 partition. -/
def perm_img3 : List Nat := [8, 7, 6, 5, 4, 3, 2, 1, 0, 10, 9, 12, 11, 13]

/-- The Z-classes of image `3`, as a class map on the fourteen vertices. -/
def cls_img3 : List Nat := [0, 1, 1, 1, 2, 2, 3, 3, 3, 4, 0, 4, 5, 5]

/-- The six class masks of image `3`. -/
def masks_img3 : List Nat := [1025, 14, 48, 448, 2560, 12288]

/-- The six kinds of image `3`, in the cyclic order of its site system. -/
def sites_img3 : List (Nat × Nat) := [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]

/-- **Image `3` of the displayed type-16 partition.**  The permutation is a
colour-preserving bijection, it carries the displayed partition to this one, and
the resulting placement has the same six-cycle site structure. -/
theorem image3_facts :
    isBijection14 perm_img3 = true ∧
    preservesColours m_display16 perm_img3 = true ∧
    carriesPartition cls_display16 cls_img3 perm_img3 = true ∧
    sitePairs m_display16 cls_img3 = [(0, 1), (0, 5), (1, 2), (2, 3), (3, 4), (4, 5)] ∧
    sites_img3 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)] ∧
    (List.range 6).map (fun j => siteDeg (sitePairs m_display16 cls_img3) j) = [2, 2, 2, 2, 2, 2] ∧
    (List.range 6).map (fun j => kindsOf sites_img3 j) = [[0, 5], [0, 1], [1, 2], [2, 3], [3, 4], [4, 5]] ∧
    (List.range 14).map (fun x => vertexKinds cls_img3 sites_img3 x) = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2] ∧
    masksOf cls_img3 = masks_img3 ∧
    (List.range 6).map (fun j => csize cls_img3 j) = [2, 3, 2, 3, 2, 2] ∧
    (List.range 6).map (fun j => cv cls_img3 j) = [[0, 10], [1, 2, 3], [4, 5], [6, 7, 8], [9, 11], [12, 13]] ∧
    sites_img3.map (fun p => isSite m_display16 cls_img3 p.1 p.2) = [true, true, true, true, true, true] ∧
    intra3 m_display16 cls_img3 = 2 := by
  decide

/-- The four images are four distinct partitions of the fourteen vertices,
separated by their class masks, and the displayed partition itself is image 0. -/
theorem image_partitions_distinct :
    masks_img0 ≠ masks_img1 ∧ masks_img0 ≠ masks_img2 ∧ masks_img0 ≠ masks_img3 ∧
      masks_img1 ≠ masks_img2 ∧ masks_img1 ≠ masks_img3 ∧ masks_img2 ≠ masks_img3 ∧
      masks_img0 = [7, 24, 224, 768, 5120, 10240] := by
  decide


/-- The displayed partition is image 0: the identity permutation produces it. -/
theorem image0_is_display :
    perm_img0 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] ∧
      cls_img0 = cls_display16 := by
  decide

/-! ## Axiom audit -/

#print axioms K58.count_alternates
#print axioms K58.count_form
#print axioms K58.four_count_vectors
#print axioms K58.alternating_solutions
#print axioms K58.no_triangle_weights
#print axioms K58.count_vector_pairs
#print axioms K58.facts_display16
#print axioms K58.facts_p36_0
#print axioms K58.facts_p36_1
#print axioms K58.facts_p36_2
#print axioms K58.count_vector_display16
#print axioms K58.count_vector_p36_0
#print axioms K58.count_vector_p36_1
#print axioms K58.count_vector_p36_2
#print axioms K58.intra3_distinct
#print axioms K58.case_count
#print axioms K58.image0_facts
#print axioms K58.image1_facts
#print axioms K58.image2_facts
#print axioms K58.image3_facts
#print axioms K58.image_partitions_distinct
#print axioms K58.image0_is_display

end K58
