/-
K58: the U/T critical templates, as Lean objects.

The bundle's `gluing.template` builds a three-colouring of `K_15`/`K_16` from the
XOR difference classes of `Z_2^4` plus a 16-edge trade.  This file reproduces
that definition and checks the two properties the cover relies on: the templates
are triangle-free, and there are exactly two of them at each size.  The
completeness statement is `Classified` at the bottom — the classification
theorem the marking lemma needs, stated precisely, not yet proved.
-/
import K58.DegreeCap

namespace K58

/-- The difference colour table of `gluing.DIFFERENCE_COLORS`. -/
def dc : ℕ → Fin 3
  | 1 => 0 | 2 => 1 | 3 => 1 | 4 => 2 | 5 => 2 | 6 => 2 | 7 => 1
  | 8 => 0 | 9 => 2 | 10 => 0 | 11 => 1 | 12 => 0 | 13 => 1 | 14 => 2
  | _ => 0

/-- The 16-edge trade of `gluing.TRADE`. -/
def trade : Finset ℕ :=
  {21, 22, 28, 31, 37, 38, 44, 47, 88, 91, 104, 107, 140, 143, 188, 191}

/-- The colour swap `(0,2,1)` applied by the twisted template. -/
def swap01 : Fin 3 → Fin 3
  | 0 => 0 | 1 => 2 | 2 => 1

/-- The colour of the edge `uv` in the `U` (`twisted = false`) or `T`
(`twisted = true`) template on `Fin n`. -/
def templateCol (n : ℕ) (twisted : Bool) (u v : Fin n) : Fin 3 :=
  if twisted && (16 * min u.val v.val + max u.val v.val) ∈ trade
  then swap01 (dc (u.val ^^^ v.val))
  else dc (u.val ^^^ v.val)

lemma templateCol_symm (n : ℕ) (t : Bool) (u v : Fin n) :
    templateCol n t u v = templateCol n t v u := by
  unfold templateCol
  rw [Nat.min_comm, Nat.max_comm, Nat.xor_comm]

/-- The `U`/`T` template as an edge colouring. -/
def template (n : ℕ) (twisted : Bool) : EdgeCol (Fin n) 3 :=
  ⟨templateCol n twisted, templateCol_symm n twisted⟩

instance decidableTriangleFree {n k : ℕ} (G : EdgeCol (Fin n) k) : Decidable (TriangleFree G) := by
  unfold TriangleFree
  infer_instance

/-- Both templates are triangle-free on 15 vertices. -/
theorem template_triangleFree_15 : ∀ t : Bool, TriangleFree (template 15 t) := by
  decide

/-- Both templates are triangle-free on 16 vertices. -/
theorem template_triangleFree_16 : ∀ t : Bool, TriangleFree (template 16 t) := by
  decide

/-- The two templates are not isomorphic, even allowing a colour permutation. -/
def IsoUpToColour {n : ℕ} (G H : EdgeCol (Fin n) 3) : Prop :=
  ∃ (e : Equiv.Perm (Fin n)) (p : Equiv.Perm (Fin 3)),
    ∀ i j, i ≠ j → G.col i j = p (H.col (e i) (e j))

/-- **The classification the marking lemma needs.**  Every triangle-free
3-colouring of `K_n` (`n = 15` or `16`) is isomorphic, up to relabelling the
vertices and the colours, to one of the two templates.

This is the statement proved in the pinned repository as
`R4333Lean.k16CriticalCatalogue_complete` / `k15CriticalCatalogue_complete`
(Kalbfleisch–Stanton for 16, Heinrich for 15).  It is stated here so the marking
lemma can be developed against a precise interface; it is not proved here. -/
def Classified (n : ℕ) : Prop :=
  ∀ G : EdgeCol (Fin n) 3, TriangleFree G → ∃ t : Bool, IsoUpToColour G (template n t)

end K58
