/-
K58 supplement (swarm smwqx1yfw, member m5): corollaries of the arm-mixture bound.

`mixture` (in `Mixture.lean`) is L1: two colour classes of different colours meet
in at most five vertices.  Here are the two forms the wall actually uses:

* `mixture_subset` : the bound holds for any subset of the second class
  (the encoder-ready form: the cardinality is imposed on the literals of a
  sub-arm, not on the whole class);
* `arm_part_le_five` : at a vertex `r`, every vertex `a` of the arm `N_c(r)` has
  at most five colour-`f` neighbours inside that arm, for `f != c`.  This is the
  arithmetic behind the "4/5 split" of a critical neighbourhood.
-/
import K58.Mixture

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The mixture bound for a subset of the second colour class. -/
theorem mixture_subset (G : EdgeCol V 4) (h : TriangleFree G) (x u : V) (f g : Fin 4)
    (hfg : f ≠ g) {S : Finset V} (hS : S ⊆ nbr G u g) :
    ((nbr G x f) ∩ S).card ≤ 5 := by
  have hsub : (nbr G x f) ∩ S ⊆ (nbr G x f) ∩ (nbr G u g) := by
    intro y hy
    simp only [Finset.mem_inter] at hy ⊢
    exact ⟨hy.1, hS hy.2⟩
  exact le_trans (Finset.card_le_card hsub) (mixture G h x u f g hfg)

/-- Inside an arm, a vertex has at most five neighbours of any other colour. -/
theorem arm_part_le_five (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4)
    {a : V} (_ha : a ∈ nbr G r c) (f : Fin 4) (hf : f ≠ c) :
    ((nbr G a f) ∩ (nbr G r c)).card ≤ 5 := by
  have hsub : (nbr G a f) ∩ (nbr G r c) ⊆ (nbr G a f) ∩ (nbr G r c) := subset_rfl
  exact mixture_subset G h a r f c hf (S := nbr G r c) (subset_rfl)

end K58
