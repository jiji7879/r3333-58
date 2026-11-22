/-
K58 supplement (swarm smwr0lr3q, member m8, run 2): certifying the hypothesis
list of the type-level Family-A model.

* `sum_inter_nbr_even` : the in-class colour degrees of a finite set sum to twice
  the number of colour-`i` edges inside it  (finishes the evenness step of the
  parity argument);
* `model_pair_disjoint` : the pair condition `M_f(x) cap M_f(x') = empty` for
  `x, x'` joined in colour `f`, in the general-colour form;
* `model_pair_rigidity` : the per-`(u,y)` rigidity, in the correct form, for every
  sender `u` and every `y` in its colour class;
* `light_count_parity` : the 15-arm colour-class edge count as a function of the
  light counts, `2 e_i = 75 - n_i`, and `n_i` odd.
-/
import K58.Arm

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- **Evenness.** For a finite set `A` and a colour `i`, the sum of the in-class
colour-`i` degrees is twice the number of colour-`i` edges inside `A`. -/
theorem sum_inter_nbr_even (G : EdgeCol V 4) (A : Finset V) (i : Fin 4) :
    ∃ e, ∑ a ∈ A, ((nbr G a i) ∩ A).card = 2 * e := by
  classical
  set en : V ≃ Fin (Fintype.card V) := Fintype.equivFin V with hen
  set lt : V → V → Prop := fun a b => (en a).val < (en b).val with hlt
  have htri : ∀ a b : V, a ≠ b → (lt b a ∧ ¬ lt a b) ∨ (lt a b ∧ ¬ lt b a) := by
    intro a b hab
    have h := Nat.lt_trichotomy (en a).val (en b).val
    rcases h with h | h | h
    · exact Or.inr ⟨h, by omega⟩
    · exact absurd (en.injective (Fin.ext h)) hab
    · exact Or.inl ⟨h, by omega⟩
  -- each in-class degree is a sum of indicators
  have h1 : ∑ a ∈ A, ((nbr G a i) ∩ A).card
      = ∑ a ∈ A, ∑ b ∈ A, (if b ≠ a ∧ G.col a b = i then (1:ℕ) else 0) := by
    refine Finset.sum_congr rfl ?_
    intro a _
    rw [show ((nbr G a i) ∩ A) = A.filter (fun b => b ≠ a ∧ G.col a b = i) from by
      ext b
      simp only [Finset.mem_inter, Finset.mem_filter, mem_nbr]
      tauto]
    rw [card_filter_eq_sum_ite]
  -- split by the order
  have hpoint : ∀ a b : V, (if b ≠ a ∧ G.col a b = i then (1:ℕ) else 0)
      = (if lt b a ∧ G.col a b = i then 1 else 0) + (if lt a b ∧ G.col a b = i then 1 else 0) := by
    intro a b
    by_cases hba : b = a
    · rw [hba]
      have h0 : ¬ lt a a := by
        rw [hlt]
        omega
      have e1 : ¬ (lt a a ∧ G.col a a = i) := fun h => h0 h.1
      rw [if_neg (fun h : a ≠ a ∧ G.col a a = i => h.1 rfl), if_neg e1]
    · by_cases hc : G.col a b = i
      · rw [if_pos ⟨hba, hc⟩]
        rcases htri a b (Ne.symm hba) with ⟨h1, h2⟩ | ⟨h1, h2⟩
        · rw [if_pos ⟨h1, hc⟩, if_neg (fun h => h2 h.1), add_zero]
        · rw [if_neg (fun h => h2 h.1), if_pos ⟨h1, hc⟩, zero_add]
      · rw [if_neg (fun h => hc h.2), if_neg (fun h => hc h.2),
          if_neg (fun h => hc h.2), add_zero]
  have h2 : ∑ a ∈ A, ∑ b ∈ A, (if b ≠ a ∧ G.col a b = i then (1:ℕ) else 0)
      = ∑ a ∈ A, ∑ b ∈ A, ((if lt b a ∧ G.col a b = i then 1 else 0)
          + (if lt a b ∧ G.col a b = i then 1 else 0)) := by
    refine Finset.sum_congr rfl ?_
    intro a _
    exact Finset.sum_congr rfl (fun b _ => hpoint a b)
  have h3 : ∑ a ∈ A, ∑ b ∈ A, ((if lt b a ∧ G.col a b = i then 1 else 0)
        + (if lt a b ∧ G.col a b = i then 1 else 0))
      = (∑ a ∈ A, ∑ b ∈ A, (if lt b a ∧ G.col a b = i then 1 else 0))
        + (∑ a ∈ A, ∑ b ∈ A, (if lt a b ∧ G.col a b = i then 1 else 0)) := by
    rw [← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl (fun a _ => Finset.sum_add_distrib)
  have h4 : (∑ a ∈ A, ∑ b ∈ A, (if lt a b ∧ G.col a b = i then 1 else 0))
      = (∑ a ∈ A, ∑ b ∈ A, (if lt b a ∧ G.col a b = i then 1 else 0)) := by
    rw [Finset.sum_comm (s := A) (t := A)]
    refine Finset.sum_congr rfl (fun y _ => Finset.sum_congr rfl (fun x _ => ?_))
    rw [G.symm x y]
  refine ⟨∑ a ∈ A, ∑ b ∈ A, (if lt b a ∧ G.col a b = i then 1 else 0), ?_⟩
  rw [h1, h2, h3, h4]
  omega

end K58

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- **The pair condition of the model**, general colour: two distinct vertices
joined in colour `f` have disjoint colour-`f` classes.  (Intersecting with the
pinned arm gives `M_f(x) cap M_f(x') = empty`.) -/
theorem model_pair_disjoint (G : EdgeCol V 4) (h : TriangleFree G) (x x' : V) (f : Fin 4)
    (hne : x ≠ x') (hcol : G.col x x' = f) : (nbr G x f) ∩ (nbr G x' f) = ∅ := by
  rw [Finset.eq_empty_iff_forall_notMem]
  intro y hy
  obtain ⟨h1, h2⟩ := Finset.mem_inter.mp hy
  rw [mem_nbr] at h1 h2
  exact h x x' y hne h2.1.symm h1.1.symm ⟨by rw [hcol, h1.2], by rw [h1.2, h2.2]⟩

/-- **The per-`(u,y)` rigidity of the model.** For a sender `u` and any `y` in its
colour-`c` class, the colour-`f` counts inside that class are 4 or 5, and 5 when the
class has 16 points; with the sum being `|class| - 1` they are a permutation of
(5,5,4) (15 points) or of (5,5,5) (16 points). -/
theorem model_pair_rigidity (G : EdgeCol V 4) (h : TriangleFree G) (u : V) (c : Fin 4)
    (hs : 15 ≤ (nbr G u c).card) (y : V) (hy : y ∈ nbr G u c) (f : Fin 4) (hf : f ≠ c) :
    4 ≤ ((nbr G y f) ∩ (nbr G u c)).card ∧ ((nbr G y f) ∩ (nbr G u c)).card ≤ 5 ∧
      ((nbr G u c).card = 16 → ((nbr G y f) ∩ (nbr G u c)).card = 5) := by
  have hcap := deg_le_sixteen G h u c
  rw [← nbr_card] at hcap
  rcases Nat.eq_or_lt_of_le hs with h15 | h16
  · exact ⟨(arm_degree_partition G h u y c hy h15.symm f hf).1,
      (arm_degree_partition G h u y c hy h15.symm f hf).2, by omega⟩
  · have hp := arm_degree_sixteen G h u y c hy (by omega) f hf
    exact ⟨by omega, by omega, fun _ => hp⟩

/-- **The arm's colour-class edge count as a function of the light counts.**
For a 15-arm, `2 e_i + n_i = 75` where `e_i` is the number of colour-`i` edges
inside the arm and `n_i` the number of its points that are light in colour `i`;
in particular `n_i` is odd. -/
theorem light_count_parity (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c i : Fin 4)
    (hi : i ≠ c) (h15 : (nbr G r c).card = 15) :
    (∃ e, 2 * e
        + ((nbr G r c).filter (fun a => ((nbr G a i) ∩ (nbr G r c)).card = 4)).card = 75)
      ∧ Odd ((nbr G r c).filter
          (fun a => ((nbr G a i) ∩ (nbr G r c)).card = 4)).card := by
  classical
  obtain ⟨e, he⟩ := sum_inter_nbr_even G (nbr G r c) i
  have hpoint : ∀ a ∈ nbr G r c, ((nbr G a i) ∩ (nbr G r c)).card
      + (if ((nbr G a i) ∩ (nbr G r c)).card = 4 then 1 else 0) = 5 := by
    intro a ha
    have hp := arm_degree_partition G h r a c ha h15 i hi
    by_cases h4 : ((nbr G a i) ∩ (nbr G r c)).card = 4
    · rw [if_pos h4]; omega
    · rw [if_neg h4]; omega
  have hsum : ∑ a ∈ nbr G r c, (((nbr G a i) ∩ (nbr G r c)).card
      + (if ((nbr G a i) ∩ (nbr G r c)).card = 4 then 1 else 0)) = 75 := by
    rw [Finset.sum_congr rfl hpoint]
    rw [Finset.sum_const_nat (fun a _ => rfl), h15]
  have hsplit : ∑ a ∈ nbr G r c, (((nbr G a i) ∩ (nbr G r c)).card
        + (if ((nbr G a i) ∩ (nbr G r c)).card = 4 then 1 else 0))
      = (∑ a ∈ nbr G r c, ((nbr G a i) ∩ (nbr G r c)).card)
        + ∑ a ∈ nbr G r c, (if ((nbr G a i) ∩ (nbr G r c)).card = 4 then 1 else 0) :=
    Finset.sum_add_distrib
  have hcount : ∑ a ∈ nbr G r c, (if ((nbr G a i) ∩ (nbr G r c)).card = 4 then 1 else 0)
      = ((nbr G r c).filter (fun a => ((nbr G a i) ∩ (nbr G r c)).card = 4)).card :=
    (card_filter_eq_sum_ite _ _).symm
  have hkey : 2 * e
      + ((nbr G r c).filter (fun a => ((nbr G a i) ∩ (nbr G r c)).card = 4)).card = 75 := by
    rw [← he, ← hcount, ← hsplit, hsum]
  refine ⟨⟨e, hkey⟩, ?_⟩
  exact ⟨37 - e, by omega⟩

end K58
