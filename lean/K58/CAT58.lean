/-
CAT58: the same-degree critical attaching theorem at `K_58`.

Statement (see `results/literature-next-2026-11-28/attachment-structure.md` §3):
in a triangle-free 4-colouring of the complete graph on 58 vertices there are
distinct vertices `u v`, a colour `c` and `s ∈ {15,16}` with

  `deg u c = s`, `deg v c = s`, `|N_c u ∩ N_c v| ≥ 3`,

where `N_c u` is the actual set of `c`-coloured neighbours of `u`
(`K58.nbrs`, definitionally the finset whose cardinality is `K58.deg`).

Hypotheses used: `TriangleFree G` and `Fintype.card V = 58` only.  The degree
cap `deg ≤ 16` is proved in `K58.DegreeCap` from `R(3,3,3) ≤ 17`; the degree sum
`Σ_c deg v c = 57` is `K58.sum_deg`.  No ticket/root/profile/balance/reciprocity
or FKR2004 attachment-perfection hypothesis is assumed.

This module adds no axiom, uses no `native_decide`, and should be placed after
`K58.DegreeCap` in `lean/order.txt`.
-/
import K58.DegreeCap

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V] {k : ℕ}

/-- The actual set of `a`-coloured neighbours of `i`.  Its cardinality is `deg`. -/
noncomputable def nbrs (G : EdgeCol V k) (i : V) (a : Fin k) : Finset V :=
  Finset.univ.filter (fun j : V => j ≠ i ∧ G.col i j = a)

theorem deg_eq_card_nbrs (G : EdgeCol V k) (i : V) (a : Fin k) :
    deg G i a = (nbrs G i a).card := rfl

theorem mem_nbrs {G : EdgeCol V k} {i j : V} {a : Fin k} :
    j ∈ nbrs G i a ↔ j ≠ i ∧ G.col i j = a := by
  simp [nbrs]

/-- Union bound for a finset of sets with pairwise intersections of size at most
two.  Written with binomials: `2 * choose m 2 = m * (m - 1)`. -/
theorem card_biUnion_ge_union_bound :
    ∀ T : Finset (Finset V), ∀ s : ℕ, (∀ A ∈ T, A.card = s) →
      (∀ A ∈ T, ∀ B ∈ T, A ≠ B → (A ∩ B).card ≤ 2) →
      T.card * s ≤ (T.biUnion id).card + 2 * T.card.choose 2 := by
  classical
  intro T
  induction T using Finset.induction_on with
  | empty => intro s _ _; simp
  | insert a T ha ih =>
      intro s hcard hpair
      have hcardT : ∀ A ∈ T, A.card = s := fun A hA => hcard A (Finset.mem_insert_of_mem hA)
      have hpairT : ∀ A ∈ T, ∀ B ∈ T, A ≠ B → (A ∩ B).card ≤ 2 :=
        fun A hA B hB hAB =>
          hpair A (Finset.mem_insert_of_mem hA) B (Finset.mem_insert_of_mem hB) hAB
      have ih' := ih s hcardT hpairT
      have has : a.card = s := hcard a (Finset.mem_insert_self a T)
      have hcard_insert : (insert a T).card = T.card + 1 := Finset.card_insert_of_notMem ha
      have hbiU : (insert a T).biUnion id = a ∪ T.biUnion id := by
        rw [Finset.biUnion_insert]; rfl
      have hinter_eq : a ∩ (T.biUnion id) = T.biUnion (fun B => a ∩ B) := by
        ext x
        simp only [Finset.mem_inter, Finset.mem_biUnion, id]
        constructor
        · rintro ⟨h1, B, hB, h2⟩; exact ⟨B, hB, h1, h2⟩
        · rintro ⟨B, hB, h1, h2⟩; exact ⟨h1, B, hB, h2⟩
      have hinter_le : (a ∩ (T.biUnion id)).card ≤ 2 * T.card := by
        rw [hinter_eq]
        refine (Finset.card_biUnion_le).trans ?_
        have hterm : ∀ B ∈ T, (a ∩ B).card ≤ 2 := by
          intro B hB
          have hne : a ≠ B := fun h => ha (h ▸ hB)
          exact hpair a (Finset.mem_insert_self a T) B (Finset.mem_insert_of_mem hB) hne
        calc ∑ B ∈ T, (a ∩ B).card ≤ ∑ _B ∈ T, 2 := Finset.sum_le_sum hterm
          _ = 2 * T.card := by
              rw [Finset.sum_const, smul_eq_mul, Nat.mul_comm]
      have hunion := Finset.card_union_add_card_inter a (T.biUnion id)
      rw [has] at hunion
      have hchoose : 2 * (T.card + 1).choose 2 = 2 * T.card.choose 2 + 2 * T.card := by
        rw [Nat.choose_succ_succ', Nat.choose_one_right, Nat.mul_add, Nat.add_comm]
      have hstep : (T.card + 1) * s = T.card * s + s := Nat.succ_mul T.card s
      rw [hbiU, hcard_insert, hstep, hchoose]
      omega

/-- Core counting step: a set `S` whose `c`-neighbourhoods all have size `s`,
with `58 + 2 * choose |S| 2 < |S| * s`, contains two vertices whose
neighbourhoods meet in at least three points. -/
theorem exists_pair_large_inter (G : EdgeCol V 4) (hV : Fintype.card V = 58)
    (c : Fin 4) (S : Finset V) (s : ℕ) (hs : 3 ≤ s)
    (hdeg : ∀ v ∈ S, deg G v c = s)
    (hineq : 58 + 2 * S.card.choose 2 < S.card * s) :
    ∃ u ∈ S, ∃ v ∈ S, u ≠ v ∧ 3 ≤ (nbrs G u c ∩ nbrs G v c).card := by
  classical
  by_contra hcon
  simp only [not_exists, not_and, not_le] at hcon
  have hinj : Set.InjOn (fun v => nbrs G v c) ↑S := by
    intro u hu v hv heq
    by_contra hne
    have heq' : nbrs G u c = nbrs G v c := heq
    have hle := hcon u hu v hv hne
    rw [heq', Finset.inter_self, ← deg_eq_card_nbrs, hdeg v hv] at hle
    omega
  set T : Finset (Finset V) := S.image (fun v => nbrs G v c) with hT
  have hTcard : T.card = S.card := Finset.card_image_of_injOn hinj
  have hcardT : ∀ A ∈ T, A.card = s := by
    intro A hA
    obtain ⟨v, hv, rfl⟩ := Finset.mem_image.mp hA
    rw [← deg_eq_card_nbrs]
    exact hdeg v hv
  have hpairT : ∀ A ∈ T, ∀ B ∈ T, A ≠ B → (A ∩ B).card ≤ 2 := by
    intro A hA B hB hAB
    obtain ⟨u, hu, rfl⟩ := Finset.mem_image.mp hA
    obtain ⟨v, hv, rfl⟩ := Finset.mem_image.mp hB
    have huv : u ≠ v := by
      intro h; exact hAB (by rw [h])
    have := hcon u hu v hv huv
    omega
  have hb := card_biUnion_ge_union_bound T s hcardT hpairT
  have hunion : (T.biUnion id).card ≤ 58 := by
    have := Finset.card_le_univ (T.biUnion id)
    simpa [hV] using this
  rw [hTcard] at hb
  omega

/-- **CAT58.**  In a triangle-free 4-colouring of `K_58` there are distinct
vertices `u v`, a colour `c` and `s ∈ {15,16}` such that both `c`-degrees equal
`s` and the two `c`-neighbourhoods share at least three vertices. -/
theorem cat58 (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G) :
    ∃ u v : Fin 58, u ≠ v ∧ ∃ c : Fin 4, ∃ s ∈ ({15, 16} : Finset ℕ),
      deg G u c = s ∧ deg G v c = s ∧ 3 ≤ (nbrs G u c ∩ nbrs G v c).card := by
  classical
  -- (1) every vertex has a critical colour: the four degrees sum to 57 and 4*14 < 57
  have hcrit : ∀ v : Fin 58, ∃ a : Fin 4, 15 ≤ deg G v a := by
    intro v
    by_contra h
    simp only [not_exists, not_le] at h
    have hsum := sum_deg G v
    have hV : Fintype.card (Fin 58) = 58 := by simp
    rw [hV] at hsum
    have hle : ∑ a : Fin 4, deg G v a ≤ ∑ _a : Fin 4, (14 : ℕ) :=
      Finset.sum_le_sum (fun a _ => by have := h a; omega)
    have h4 : (∑ _a : Fin 4, (14 : ℕ)) = 56 := by decide
    omega
  -- (2) some colour is critical at at least 15 vertices
  have hcount : 58 ≤
      ∑ a : Fin 4, (Finset.univ.filter (fun v : Fin 58 => 15 ≤ deg G v a)).card := by
    have hpt : ∀ v : Fin 58, 1 ≤ ∑ a : Fin 4, (if 15 ≤ deg G v a then 1 else 0) := by
      intro v
      obtain ⟨a, ha⟩ := hcrit v
      have hnn : ∀ b : Fin 4, (0 : ℕ) ≤ (if 15 ≤ deg G v b then 1 else 0) := by
        intro b; split <;> omega
      have hsingle := Finset.single_le_sum
        (f := fun b : Fin 4 => if 15 ≤ deg G v b then 1 else 0)
        (fun b _ => hnn b) (Finset.mem_univ a)
      have haz : (if 15 ≤ deg G v a then 1 else 0) = 1 := by simp [ha]
      omega
    have hcard : ∀ a : Fin 4,
        (Finset.univ.filter (fun v : Fin 58 => 15 ≤ deg G v a)).card
          = ∑ v : Fin 58, (if 15 ≤ deg G v a then 1 else 0) := by
      intro a
      rw [Finset.card_eq_sum_ones, ← Finset.sum_filter]
    calc 58 = ∑ _v : Fin 58, 1 := by simp
      _ ≤ ∑ v : Fin 58, ∑ a : Fin 4, (if 15 ≤ deg G v a then 1 else 0) :=
            Finset.sum_le_sum (fun v _ => hpt v)
      _ = ∑ a : Fin 4, ∑ v : Fin 58, (if 15 ≤ deg G v a then 1 else 0) :=
            Finset.sum_comm
      _ = ∑ a : Fin 4, (Finset.univ.filter (fun v : Fin 58 => 15 ≤ deg G v a)).card :=
            Finset.sum_congr rfl (fun a _ => (hcard a).symm)
  obtain ⟨c, hc⟩ : ∃ c : Fin 4,
      15 ≤ (Finset.univ.filter (fun v : Fin 58 => 15 ≤ deg G v c)).card := by
    by_contra h
    simp only [not_exists, not_le] at h
    have hle : ∑ a : Fin 4, (Finset.univ.filter (fun v : Fin 58 => 15 ≤ deg G v a)).card
        ≤ ∑ _a : Fin 4, (14 : ℕ) :=
      Finset.sum_le_sum (fun a _ => by have := h a; omega)
    have h4 : (∑ _a : Fin 4, (14 : ℕ)) = 56 := by decide
    omega
  -- (3) split the critical vertices of colour `c` by exact degree 15 or 16
  set C : Finset (Fin 58) := Finset.univ.filter (fun v => 15 ≤ deg G v c) with hC
  have hCc : 15 ≤ C.card := by rw [hC]; exact hc
  have hCdich : ∀ v ∈ C, deg G v c = 15 ∨ deg G v c = 16 := by
    intro v hv
    have hge : 15 ≤ deg G v c := by simpa [hC] using hv
    have hcap := deg_le_sixteen G hG v c
    omega
  have hsplit : C.card = (C.filter (fun v => deg G v c = 15)).card
      + (C.filter (fun v => deg G v c = 16)).card := by
    have hsum := Finset.card_filter_add_card_filter_not (s := C)
      (p := fun v => deg G v c = 16)
    have hcongr : C.filter (fun v => ¬ (deg G v c = 16)) = C.filter (fun v => deg G v c = 15) := by
      apply Finset.filter_congr
      intro v hv
      have := hCdich v hv
      constructor <;> intro h <;> omega
    rw [hcongr] at hsum
    omega
  -- (4) five vertices of degree 16, or six of degree 15
  rcases Nat.lt_or_ge (C.filter (fun v => deg G v c = 16)).card 5 with hlt | hge16
  · have hge15 : 6 ≤ (C.filter (fun v => deg G v c = 15)).card := by omega
    obtain ⟨S, hSC, hScard⟩ := Finset.exists_subset_card_eq hge15
    have hdeg : ∀ v ∈ S, deg G v c = 15 := fun v hv =>
      (Finset.mem_filter.mp (hSC hv)).2
    have hineq : 58 + 2 * S.card.choose 2 < S.card * 15 := by
      rw [hScard]; decide
    obtain ⟨u, huS, v, hvS, huv, hk⟩ :=
      exists_pair_large_inter G (by simp) c S 15 (by decide) hdeg hineq
    exact ⟨u, v, huv, c, 15, by decide, hdeg u huS, hdeg v hvS, hk⟩
  · obtain ⟨S, hSC, hScard⟩ := Finset.exists_subset_card_eq hge16
    have hdeg : ∀ v ∈ S, deg G v c = 16 := fun v hv =>
      (Finset.mem_filter.mp (hSC hv)).2
    have hineq : 58 + 2 * S.card.choose 2 < S.card * 16 := by
      rw [hScard]; decide
    obtain ⟨u, huS, v, hvS, huv, hk⟩ :=
      exists_pair_large_inter G (by simp) c S 16 (by decide) hdeg hineq
    exact ⟨u, v, huv, c, 16, by decide, hdeg u huS, hdeg v hvS, hk⟩

end K58
