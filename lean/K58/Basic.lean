/-
K58: the combinatorial core of the `R(3,3,3,3) ≤ 58` reduction.

Edge colourings of a complete graph on an arbitrary finite vertex type, colour
degrees, the campaign's "ticket" bookkeeping, and the double-counting identity
that gives a root with at least as many tickets received as sent.
-/
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Fintype.EquivFin
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Set
import Mathlib.Tactic.Tauto

namespace K58

/-- A colouring of the edges of the complete graph on `V` with `k` colours.
The diagonal is a dummy value; `TriangleFree` never looks at it. -/
structure EdgeCol (V : Type*) (k : ℕ) where
  col : V → V → Fin k
  symm : ∀ i j, col i j = col j i

/-- No monochromatic triangle. -/
def TriangleFree {V : Type*} {k : ℕ} (G : EdgeCol V k) : Prop :=
  ∀ i j l : V, i ≠ j → j ≠ l → i ≠ l →
    ¬ (G.col i j = G.col i l ∧ G.col i l = G.col j l)

variable {V : Type*} [Fintype V] [DecidableEq V] {k : ℕ}

/-- The number of neighbours of `i` joined to `i` in colour `a`. -/
noncomputable def deg (G : EdgeCol V k) (i : V) (a : Fin k) : ℕ :=
  (Finset.univ.filter (fun j : V => j ≠ i ∧ G.col i j = a)).card

/-- `i` sends a ticket along the edge `ij` when its colour-degree in that colour
is critical, i.e. at least 15.  (The degree cap `≤ 16` is proved separately.) -/
def Sends (G : EdgeCol V k) (i j : V) : Prop :=
  j ≠ i ∧ 15 ≤ deg G i (G.col i j)

noncomputable instance (G : EdgeCol V k) (i j : V) : Decidable (Sends G i j) := by
  unfold Sends; infer_instance

/-- Tickets sent by `i`. -/
noncomputable def w (G : EdgeCol V k) (i : V) : ℕ :=
  (Finset.univ.filter (fun j : V => Sends G i j)).card

/-- Tickets received by `i`. -/
noncomputable def H (G : EdgeCol V k) (i : V) : ℕ :=
  (Finset.univ.filter (fun j : V => Sends G j i)).card

/-- The double-counting identity: total tickets sent equals total received. -/
theorem sum_w_eq_sum_H (G : EdgeCol V k) :
    ∑ i, w G i = ∑ i, H G i := by
  have h1 : ∀ i, w G i = ∑ j, if Sends G i j then 1 else 0 := by
    intro i; rw [w, Finset.card_eq_sum_ones, Finset.sum_filter]
  have h2 : ∀ i, H G i = ∑ j, if Sends G j i then 1 else 0 := by
    intro i; rw [H, Finset.card_eq_sum_ones, Finset.sum_filter]
  calc ∑ i, w G i = ∑ i, ∑ j, (if Sends G i j then 1 else 0) :=
        Finset.sum_congr rfl fun i _ => h1 i
    _ = ∑ j, ∑ i, (if Sends G i j then 1 else 0) := Finset.sum_comm
    _ = ∑ i, ∑ j, (if Sends G j i then 1 else 0) := rfl
    _ = ∑ i, H G i :=
        (Finset.sum_congr rfl fun i _ => (h2 i).symm)

/-- Some vertex receives at least as many tickets as it sends. -/
theorem exists_root [Nonempty V] (G : EdgeCol V k) : ∃ i, w G i ≤ H G i := by
  by_contra h
  simp only [not_exists, not_le] at h
  have hlt : ∑ i, H G i < ∑ i, w G i :=
    Finset.sum_lt_sum (fun i _ => le_of_lt (h i))
      ⟨Classical.arbitrary V, Finset.mem_univ _, h (Classical.arbitrary V)⟩
  rw [sum_w_eq_sum_H] at hlt
  exact lt_irrefl _ hlt

end K58
