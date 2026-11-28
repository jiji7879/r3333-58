/-
Attachment structure at `K_58`: the two-colour part bound (`R(3,3) = 6`) and the
upper attachment bound `k + (d_γ u - 11) ≤ d_c v`.

This follows `results/literature-next-2026-11-28/attachment-structure.md` §3:
for distinct `u v` and `γ = χ(u,v)`, `c ≠ γ`, the set `A = N_c u ∩ N_c v` and
`D = N_γ u ∩ N_c v` are disjoint subsets of `N_c v`, and
`N_γ u ⊆ {v} ∪ D ∪ B_α ∪ B_β` where `B_α = N_γ u ∩ N_α v` for the two colours
`α β ∉ {γ, c}`; each `B` is internally two-coloured (it avoids `γ` and its own
`α`), hence has at most 5 points.  This gives
`|A| ≤ |N_c v| - max 0 (|N_γ u| - 11)`, i.e. `|A| + (d_γ u - 11) ≤ d_c v`.

No `k ≤ 14` claim: that needs `d_γ ≥ 13`, which is false in general here.
-/
import K58.CAT58

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- A part of a triangle-free 4-colouring in which every internal edge avoids two
distinct colours `p q` has at most five points (`R(3,3) ≤ 6`). -/
theorem card_le_five_of_two_colours (G : EdgeCol V 4) (hG : TriangleFree G)
    (B : Finset V) (p q : Fin 4) (hpq : p ≠ q)
    (havoid : ∀ x ∈ B, ∀ y ∈ B, x ≠ y → G.col x y ≠ p ∧ G.col x y ≠ q) :
    B.card ≤ 5 := by
  classical
  by_contra hle
  simp only [not_le] at hle
  obtain ⟨B', hB'B, hB'card⟩ := Finset.exists_subset_card_eq (show 6 ≤ B.card by omega)
  -- the two colours different from `p` and `q`
  set U : Finset (Fin 4) := (Finset.univ.erase p).erase q with hU
  have hUcard : U.card = 2 := by
    have hq_mem : q ∈ Finset.univ.erase p := by simp [Ne.symm hpq]
    have hp_mem : p ∈ Finset.univ := Finset.mem_univ p
    rw [hU, Finset.card_erase_of_mem hq_mem, Finset.card_erase_of_mem hp_mem,
      Finset.card_univ, Fintype.card_fin]
  obtain ⟨r, s, hrs, hUrs⟩ := Finset.card_eq_two.mp hUcard
  have hmemU : ∀ c : Fin 4, c ≠ p → c ≠ q → c ∈ U := by
    intro c h1 h2
    simp [hU, h1, h2]
  have hUelim : ∀ c : Fin 4, c ∈ U → c = r ∨ c = s := by
    intro c hc
    rw [hUrs] at hc
    simpa using hc
  -- the indicator that separates the two surviving colours
  have hbad : ∀ a b : Fin 4, a ∈ U → b ∈ U →
      (if a = r then (0 : Fin 2) else 1) = (if b = r then 0 else 1) → a = b := by
    intro a b ha hb heq
    by_cases h0 : (if a = r then (0 : Fin 2) else 1) = 0
    · have har : a = r := by
        by_contra h
        rw [if_neg h] at h0
        exact absurd h0 (by decide)
      have hbr : b = r := by
        by_contra h
        rw [har, if_pos rfl, if_neg h] at heq
        exact absurd heq (by decide)
      rw [har, hbr]
    · have har : a ≠ r := by
        intro h
        exact h0 (by rw [h]; simp)
      have hbr : b ≠ r := by
        intro h
        have hb0 : (if b = r then (0 : Fin 2) else 1) = 0 := by rw [if_pos h]
        exact h0 (heq.trans hb0)
      have ha' : a = s := by
        rcases hUelim a ha with h | h
        · exact absurd h har
        · exact h
      have hb' : b = s := by
        rcases hUelim b hb with h | h
        · exact absurd h hbr
        · exact h
      rw [ha', hb']
  have havoid' : ∀ x ∈ B', ∀ y ∈ B', x ≠ y → G.col x y ≠ p ∧ G.col x y ≠ q :=
    fun x hx y hy hxy => havoid x (hB'B hx) y (hB'B hy) hxy
  -- the induced two-colouring of `B'`
  let G2 : EdgeCol ↥B' 2 :=
    { col := fun x y =>
        if hxy : x = y then 0
        else (if G.col x.1 y.1 = r then (0 : Fin 2) else 1)
      symm := by
        intro x y
        by_cases hxy : x = y
        · subst hxy; simp
        · have hyx : y ≠ x := Ne.symm hxy
          rw [dif_neg hxy, dif_neg hyx, G.symm x.1 y.1] }
  have h2 : TriangleFree G2 := by
    intro x y z hxy hyz hxz hmono
    simp only [G2, dif_neg hxy, dif_neg hyz, dif_neg hxz] at hmono
    have hmem1 : G.col x.1 y.1 ∈ U :=
      hmemU _ (havoid' x.1 x.2 y.1 y.2 (fun h => hxy (Subtype.ext h))).1
        (havoid' x.1 x.2 y.1 y.2 (fun h => hxy (Subtype.ext h))).2
    have hmem2 : G.col x.1 z.1 ∈ U :=
      hmemU _ (havoid' x.1 x.2 z.1 z.2 (fun h => hxz (Subtype.ext h))).1
        (havoid' x.1 x.2 z.1 z.2 (fun h => hxz (Subtype.ext h))).2
    have hmem3 : G.col y.1 z.1 ∈ U :=
      hmemU _ (havoid' y.1 y.2 z.1 z.2 (fun h => hyz (Subtype.ext h))).1
        (havoid' y.1 y.2 z.1 z.2 (fun h => hyz (Subtype.ext h))).2
    have e1 : G.col x.1 y.1 = G.col x.1 z.1 := hbad _ _ hmem1 hmem2 hmono.1
    have e2 : G.col x.1 z.1 = G.col y.1 z.1 := hbad _ _ hmem2 hmem3 hmono.2
    have hxy' : x.1 ≠ y.1 := fun h => hxy (Subtype.ext h)
    have hyz' : y.1 ≠ z.1 := fun h => hyz (Subtype.ext h)
    have hxz' : x.1 ≠ z.1 := fun h => hxz (Subtype.ext h)
    exact hG x.1 y.1 z.1 hxy' hyz' hxz' ⟨e1, e2⟩
  exact two_colour_six G2 (by simp [Fintype.card_coe, hB'card]) h2



/-- **Upper attachment bound at `K_n`.**  For distinct `u v`, `γ = χ(u,v)` and a
colour `c ≠ γ`, the common `c`-neighbourhood of `u` and `v` satisfies
`|N_c u ∩ N_c v| + (d_γ u - 11) ≤ d_c v`.  (Equivalently
`k ≤ d_c v - max 0 (d_γ u - 11)`.) -/
theorem attachment_bound (G : EdgeCol V 4) (hG : TriangleFree G)
    {u v : V} (huv : u ≠ v) (c : Fin 4) (hc : c ≠ G.col u v) :
    (nbrs G u c ∩ nbrs G v c).card + (deg G u (G.col u v) - 11) ≤ deg G v c := by
  classical
  set γ : Fin 4 := G.col u v with hγ
  have hγc : γ ≠ c := fun h => hc h.symm
  set A : Finset V := nbrs G u c ∩ nbrs G v c with hA
  set D : Finset V := nbrs G u γ ∩ nbrs G v c with hD
  set S : Finset V := nbrs G u γ with hS
  -- `A` and `D` are disjoint subsets of `N_c v`
  have hAsub : A ⊆ nbrs G v c := by rw [hA]; exact Finset.inter_subset_right
  have hDsub : D ⊆ nbrs G v c := by rw [hD]; exact Finset.inter_subset_right
  have hAD : Disjoint A D := by
    rw [Finset.disjoint_left]
    intro x hxA hxD
    have h1 : G.col u x = c := (mem_nbrs.mp (Finset.mem_inter.mp hxA).1).2
    have h2 : G.col u x = γ := (mem_nbrs.mp (Finset.mem_inter.mp hxD).1).2
    exact hγc (by rw [← h2, h1])
  have hADcard : A.card + D.card ≤ deg G v c := by
    have h1 : (A ∪ D).card = A.card + D.card := Finset.card_union_of_disjoint hAD
    have h2 : (A ∪ D).card ≤ (nbrs G v c).card :=
      Finset.card_le_card (Finset.union_subset hAsub hDsub)
    have h3 : deg G v c = (nbrs G v c).card := deg_eq_card_nbrs G v c
    omega
  -- the two colours different from `γ` and `c`
  set Uc : Finset (Fin 4) := (Finset.univ.erase γ).erase c with hUc
  have hUccard : Uc.card = 2 := by
    have hq_mem : c ∈ Finset.univ.erase γ := by simp [Ne.symm hγc]
    have hp_mem : γ ∈ Finset.univ := Finset.mem_univ γ
    rw [hUc, Finset.card_erase_of_mem hq_mem, Finset.card_erase_of_mem hp_mem,
      Finset.card_univ, Fintype.card_fin]
  obtain ⟨α, β, hαβ, hUcαβ⟩ := Finset.card_eq_two.mp hUccard
  have hmemUc : ∀ a : Fin 4, a ≠ γ → a ≠ c → a ∈ Uc := by
    intro a h1 h2
    simp [hUc, h1, h2]
  have hUcelim : ∀ a : Fin 4, a ∈ Uc → a = α ∨ a = β := by
    intro a ha
    rw [hUcαβ] at ha
    simpa using ha
  have hαγ : γ ≠ α := by
    have hαmem : α ∈ Uc := by rw [hUcαβ]; simp
    have h1 : α ≠ γ := by
      have h2 := hαmem
      simp only [hUc, Finset.mem_erase, Finset.mem_univ, and_true] at h2
      exact h2.2
    exact fun h => h1 h.symm
  have hβγ : γ ≠ β := by
    have hβmem : β ∈ Uc := by rw [hUcαβ]; simp
    have h1 : β ≠ γ := by
      have h2 := hβmem
      simp only [hUc, Finset.mem_erase, Finset.mem_univ, and_true] at h2
      exact h2.2
    exact fun h => h1 h.symm
  -- the cover of `N_γ u`
  have hcover : S ⊆ {v} ∪ D ∪ (S ∩ nbrs G v α) ∪ (S ∩ nbrs G v β) := by
    intro x hx
    have hxu : x ≠ u := (mem_nbrs.mp hx).1
    have hcol : G.col u x = γ := (mem_nbrs.mp hx).2
    have hxS : x ∈ S := hx
    rw [Finset.mem_union, Finset.mem_union, Finset.mem_union]
    by_cases hxv : x = v
    · exact Or.inl (Or.inl (Or.inl (by simp [hxv])))
    · have hne : G.col v x ≠ γ := by
        intro h
        have h1 : G.col u v = G.col u x := hγ.symm.trans hcol.symm
        have h2 : G.col u x = G.col v x := by rw [hcol, h]
        exact hG u v x huv (Ne.symm hxv) (Ne.symm hxu) ⟨h1, h2⟩
      by_cases hvc : G.col v x = c
      · have hxD : x ∈ D := by
          rw [hD]
          exact Finset.mem_inter.mpr ⟨hxS, by rw [mem_nbrs]; exact ⟨hxv, hvc⟩⟩
        exact Or.inl (Or.inl (Or.inr hxD))
      · have hmem : G.col v x ∈ Uc := hmemUc _ hne hvc
        rcases hUcelim _ hmem with h | h
        · have hxI : x ∈ S ∩ nbrs G v α := by
            refine Finset.mem_inter.mpr ⟨hxS, ?_⟩
            rw [mem_nbrs]; exact ⟨hxv, h⟩
          exact Or.inl (Or.inr hxI)
        · have hxI : x ∈ S ∩ nbrs G v β := by
            refine Finset.mem_inter.mpr ⟨hxS, ?_⟩
            rw [mem_nbrs]; exact ⟨hxv, h⟩
          exact Or.inr hxI
  -- each of the two extra parts has at most five points
  have hpart : ∀ a : Fin 4, a ∈ Uc → (S ∩ nbrs G v a).card ≤ 5 := by
    intro a ha
    have haγ : a ≠ γ := by
      have h2 := ha
      simp only [hUc, Finset.mem_erase, Finset.mem_univ, and_true] at h2
      exact h2.2
    have haα : γ ≠ a := fun h => haγ h.symm
    refine card_le_five_of_two_colours G hG _ γ a haα ?_
    rintro x hx y hy hxy
    have hxS : x ∈ S := (Finset.mem_inter.mp hx).1
    have hxa : x ∈ nbrs G v a := (Finset.mem_inter.mp hx).2
    have hyS : y ∈ S := (Finset.mem_inter.mp hy).1
    have hya : y ∈ nbrs G v a := (Finset.mem_inter.mp hy).2
    have hxu : x ≠ u := (mem_nbrs.mp hxS).1
    have hxcol : G.col u x = γ := (mem_nbrs.mp hxS).2
    have hyu : y ≠ u := (mem_nbrs.mp hyS).1
    have hycol : G.col u y = γ := (mem_nbrs.mp hyS).2
    have hxv : x ≠ v := (mem_nbrs.mp hxa).1
    have hxacol : G.col v x = a := (mem_nbrs.mp hxa).2
    have hyv : y ≠ v := (mem_nbrs.mp hya).1
    have hyacol : G.col v y = a := (mem_nbrs.mp hya).2
    constructor
    · intro h
      exact hG u x y (Ne.symm hxu) hxy (Ne.symm hyu) ⟨by rw [hxcol, hycol], by rw [hycol, h]⟩
    · intro h
      exact hG v x y (Ne.symm hxv) hxy (Ne.symm hyv) ⟨by rw [hxacol, hyacol], by rw [hyacol, h]⟩
  have hScard : S.card ≤ 1 + D.card + 5 + 5 := by
    have h1 : S.card ≤ ({v} ∪ D ∪ (S ∩ nbrs G v α) ∪ (S ∩ nbrs G v β)).card :=
      Finset.card_le_card hcover
    have h2 : ({v} ∪ D ∪ (S ∩ nbrs G v α) ∪ (S ∩ nbrs G v β)).card
        ≤ 1 + D.card + (S ∩ nbrs G v α).card + (S ∩ nbrs G v β).card := by
      have h3 := Finset.card_union_le ({v} ∪ D ∪ (S ∩ nbrs G v α)) (S ∩ nbrs G v β)
      have h4 := Finset.card_union_le ({v} ∪ D) (S ∩ nbrs G v α)
      have h5 := Finset.card_union_le ({v} : Finset V) D
      simp only [Finset.card_singleton] at h3 h4 h5
      omega
    have h6 : (S ∩ nbrs G v α).card ≤ 5 := hpart α (by rw [hUcαβ]; simp)
    have h7 : (S ∩ nbrs G v β).card ≤ 5 := hpart β (by rw [hUcαβ]; simp)
    omega
  have hSdeg : S.card = deg G u γ := (deg_eq_card_nbrs G u γ).symm
  have hDcard : deg G u γ - 11 ≤ D.card := by omega
  omega


/-- At a CAT58 attachment point the attachment colour is not the edge colour:
if `χ(u,v) = c` then a common `c`-neighbour would close a `c`-triangle.  Hence
`attachment_bound` applies to every CAT58 pair with `k ≥ 1` without a further
hypothesis. -/
theorem attachment_colour_ne (G : EdgeCol V 4) (hG : TriangleFree G) {u v : V}
    (huv : u ≠ v) (c : Fin 4) (hk : 1 ≤ (nbrs G u c ∩ nbrs G v c).card) :
    c ≠ G.col u v := by
  intro h
  have hempty : nbrs G u c ∩ nbrs G v c = ∅ := by
    rw [Finset.eq_empty_iff_forall_notMem]
    intro x hx
    have h1 := Finset.mem_inter.mp hx
    have hxu : x ≠ u := (mem_nbrs.mp h1.1).1
    have hux : G.col u x = c := (mem_nbrs.mp h1.1).2
    have hxv : x ≠ v := (mem_nbrs.mp h1.2).1
    have hvx : G.col v x = c := (mem_nbrs.mp h1.2).2
    exact hG u v x huv (Ne.symm hxv) (Ne.symm hxu) ⟨by rw [← h, hux], by rw [hux, hvx]⟩
  rw [hempty] at hk
  simp at hk

end K58
