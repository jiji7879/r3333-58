import K58.M7
import K58.Arm

set_option linter.unusedSectionVars false

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Membership in a colour class, read in the other direction. -/
theorem mem_nbrC_swap (G : EdgeCol V 4) (c : Fin 4) (p z : V) :
    p ∈ nbrC G z c ↔ z ∈ nbrC G p c := by
  rw [mem_nbrC, mem_nbrC]
  constructor
  · rintro ⟨hpz, hc⟩
    exact ⟨hpz.symm, by rw [G.symm p z]; exact hc⟩
  · rintro ⟨hzp, hc⟩
    exact ⟨hzp.symm, by rw [G.symm z p]; exact hc⟩

/-- **The double count.** -/
theorem sum_inter_nbrC_comm (G : EdgeCol V 4) (c : Fin 4) (S T : Finset V) :
    ∑ a ∈ S, ((nbrC G a c) ∩ T).card = ∑ x ∈ T, ((nbrC G x c) ∩ S).card := by
  have key : ∀ (a : V) (U : Finset V),
      ((nbrC G a c) ∩ U).card = ∑ x ∈ U, (if a ∈ nbrC G x c then 1 else 0) := by
    intro a U
    have h1 : (nbrC G a c) ∩ U = U.filter (fun x => a ∈ nbrC G x c) := by
      ext x
      rw [Finset.mem_inter, Finset.mem_filter, mem_nbrC_swap]
      exact and_comm
    rw [h1, Finset.card_eq_sum_ones, Finset.sum_filter]
  calc ∑ a ∈ S, ((nbrC G a c) ∩ T).card
      = ∑ a ∈ S, ∑ x ∈ T, (if a ∈ nbrC G x c then 1 else 0) :=
        Finset.sum_congr rfl (fun a _ => key a T)
    _ = ∑ x ∈ T, ∑ a ∈ S, (if a ∈ nbrC G x c then 1 else 0) := Finset.sum_comm
    _ = ∑ x ∈ T, ((nbrC G x c) ∩ S).card := by
        refine Finset.sum_congr rfl (fun x _ => ?_)
        have h2 : ∑ a ∈ S, (if a ∈ nbrC G x c then 1 else 0)
            = ∑ a ∈ S, (if x ∈ nbrC G a c then 1 else 0) :=
          Finset.sum_congr rfl (fun a _ => by simp only [mem_nbrC_swap G c a x])
        exact h2.trans (key x S).symm

/-- A word of an `f`-arm (`f ≠ 0`) has five `0`-neighbours in `A`. -/
theorem word_support_eq_five (G : EdgeCol V 4) (r : V) {f : Fin 4} (hf : f ≠ 0)
    (hm : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → ((nbrC G x 0) ∩ (nbrC G r 0)).card = 5)
    {x : V} (hx : x ∈ nbrC G r f) :
    ((nbrC G x 0) ∩ (nbrC G r 0)).card = 5 := by
  obtain ⟨hxr, hxf⟩ := mem_nbrC.mp hx
  refine hm x hxr ?_
  intro h0
  have hcol0 : G.col r x = 0 := (mem_nbrC.mp h0).2
  rw [hxf] at hcol0
  exact hf hcol0

/-- **`Sum_a |N_0(a) ∩ B| = |B| * 5`.** -/
theorem sum_support_arm (G : EdgeCol V 4) (r : V) {f : Fin 4} (hf : f ≠ 0)
    (hm : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → ((nbrC G x 0) ∩ (nbrC G r 0)).card = 5) :
    ∑ a ∈ nbrC G r 0, ((nbrC G a 0) ∩ (nbrC G r f)).card
      = (nbrC G r f).card * 5 := by
  rw [sum_inter_nbrC_comm G 0 (nbrC G r 0) (nbrC G r f)]
  calc ∑ x ∈ nbrC G r f, ((nbrC G x 0) ∩ (nbrC G r 0)).card
      = ∑ _x ∈ nbrC G r f, 5 :=
        Finset.sum_congr rfl (fun x hx => word_support_eq_five G r hf hm hx)
    _ = (nbrC G r f).card * 5 := Finset.sum_const_nat (fun x _ => rfl)

/-- **The truncated version.** -/
theorem sum_support_subset (G : EdgeCol V 4) (r : V) {f : Fin 4} (hf : f ≠ 0)
    (hm : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → ((nbrC G x 0) ∩ (nbrC G r 0)).card = 5)
    (C' : Finset V) (hC' : C' ⊆ nbrC G r f) :
    ∑ a ∈ nbrC G r 0, ((nbrC G a 0) ∩ C').card = C'.card * 5 := by
  rw [sum_inter_nbrC_comm G 0 (nbrC G r 0) C']
  calc ∑ x ∈ C', ((nbrC G x 0) ∩ (nbrC G r 0)).card
      = ∑ _x ∈ C', 5 :=
        Finset.sum_congr rfl (fun x hx => word_support_eq_five G r hf hm (hC' hx))
    _ = C'.card * 5 := Finset.sum_const_nat (fun x _ => rfl)

/-! ## Part C: the guard -/

/-- **The `ERRATA` guard.**  `A = N_0(r)`, `B = N_f(r)` a complete arm of 14, and
`C' ⊆ N_g(r)` a 12-subset: in the uniform child the 15 positions of `A` carry
`70 + 60 = 130` incidences, so they cannot all carry nine (`15 * 9 = 135 > 130`).
An encoder that demands `B + C ∈ {9,10}` at every position is therefore UNSAT by
arithmetic alone — this is the campaign's first `ERRATA` failure class. -/
theorem rung_guard (G : EdgeCol V 4) (r : V)
    (hA : (nbrC G r 0).card = 15)
    (hm : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → ((nbrC G x 0) ∩ (nbrC G r 0)).card = 5)
    {f g : Fin 4} (hf : f ≠ 0) (hg : g ≠ 0)
    (hB : (nbrC G r f).card = 14)
    (C' : Finset V) (hC' : C' ⊆ nbrC G r g) (hCc : C'.card = 12) :
    ¬ ∀ a ∈ nbrC G r 0,
      9 ≤ ((nbrC G a 0) ∩ (nbrC G r f)).card + ((nbrC G a 0) ∩ C').card := by
  intro hall
  have h1 := sum_support_arm G r hf hm
  have h2 := sum_support_subset G r hg hm C' hC'
  rw [hB] at h1
  rw [hCc] at h2
  have hsum : ∑ a ∈ nbrC G r 0,
      (((nbrC G a 0) ∩ (nbrC G r f)).card + ((nbrC G a 0) ∩ C').card) = 130 := by
    rw [Finset.sum_add_distrib, h1, h2]
  have h9 : (∑ _a ∈ nbrC G r 0, 9) = 135 := by
    rw [Finset.sum_const_nat (fun x _ => rfl), hA]
  have hge : 135 ≤ ∑ a ∈ nbrC G r 0,
      (((nbrC G a 0) ∩ (nbrC G r f)).card + ((nbrC G a 0) ∩ C').card) := by
    calc 135 = ∑ _a ∈ nbrC G r 0, 9 := h9.symm
      _ ≤ ∑ a ∈ nbrC G r 0,
            (((nbrC G a 0) ∩ (nbrC G r f)).card + ((nbrC G a 0) ∩ C').card) :=
          Finset.sum_le_sum (fun a ha => hall a ha)
  omega

/-- **One position is at most eight.**  The constructive form of `rung_guard`: the
`(14,12)` rung's per-position profile has slack at some arm point. -/
theorem rung_exists_le_eight (G : EdgeCol V 4) (r : V)
    (hA : (nbrC G r 0).card = 15)
    (hm : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → ((nbrC G x 0) ∩ (nbrC G r 0)).card = 5)
    {f g : Fin 4} (hf : f ≠ 0) (hg : g ≠ 0)
    (hB : (nbrC G r f).card = 14)
    (C' : Finset V) (hC' : C' ⊆ nbrC G r g) (hCc : C'.card = 12) :
    ∃ a ∈ nbrC G r 0,
      ((nbrC G a 0) ∩ (nbrC G r f)).card + ((nbrC G a 0) ∩ C').card ≤ 8 := by
  by_contra hcon
  refine rung_guard G r hA hm hf hg hB C' hC' hCc ?_
  intro a ha
  by_contra hlt
  exact hcon ⟨a, ha, by omega⟩

/-! ## Part D: the guard is sharp, and the per-position cap -/

/-- The witness vector: `b = (0,5,5,...,5)`, `c = (4,4,...,4)` on `Fin 15`.  It
meets every constraint the double count leaves — `b, c <= 5`, `Sum b = 70`,
`Sum c = 60` — and attains `9 <= b + c` at fourteen of the fifteen positions.  So
`rung_exists_le_eight` is the best possible statement of its kind: fifteen
positions at nine is excluded by `130 < 135` and by nothing else. -/
def guardWitnessB : Fin 15 → ℕ := fun i => if (i : ℕ) = 0 then 0 else 5

/-- The second coordinate of the witness. -/
def guardWitnessC : Fin 15 → ℕ := fun _ => 4

theorem guard_sharp :
    (∀ i, guardWitnessB i ≤ 5 ∧ guardWitnessC i ≤ 5) ∧
    (∑ i, guardWitnessB i = 70) ∧ (∑ i, guardWitnessC i = 60) ∧
    (∀ i : Fin 15, (i : ℕ) ≠ 0 → 9 ≤ guardWitnessB i + guardWitnessC i) ∧
    (guardWitnessB 0 + guardWitnessC 0 = 4) := by
  refine ⟨?_, ?_, ?_, ?_, ?_⟩ <;> decide

/-- **The `mixture` cap.**  An arm point meets any other class of the root in at
most five points. -/
theorem block_le_five (G : EdgeCol V 4) (h : TriangleFree G) (r a : V)
    {f : Fin 4} (hf : f ≠ 0) : ((nbrC G a 0) ∩ (nbrC G r f)).card ≤ 5 :=
  mixture G h a r 0 f (Ne.symm hf)

/-- The truncated version: a subset of an arm meets a word in at most five too. -/
theorem block_le_five_subset (G : EdgeCol V 4) (h : TriangleFree G) (r a : V)
    {f : Fin 4} (hf : f ≠ 0) (C' : Finset V) (hC' : C' ⊆ nbrC G r f) :
    ((nbrC G a 0) ∩ C').card ≤ 5 := by
  refine le_trans (Finset.card_le_card ?_) (block_le_five G h r a hf)
  intro z hz
  exact Finset.mem_inter.mpr ⟨(Finset.mem_inter.mp hz).1, hC' (Finset.mem_inter.mp hz).2⟩

/-- **The upper half of the box.**  `B + C <= 10` at every position. -/
theorem block_le_ten (G : EdgeCol V 4) (h : TriangleFree G) (r a : V)
    {f g : Fin 4} (hf : f ≠ 0) (C' : Finset V) (hC' : C' ⊆ nbrC G r g)
    (hg : g ≠ 0) :
    ((nbrC G a 0) ∩ (nbrC G r f)).card + ((nbrC G a 0) ∩ C').card ≤ 10 := by
  have h1 := block_le_five G h r a hf
  have h2 := block_le_five_subset G h r a hg C' hC'
  omega

/-! ## Part E: the root classes cover everything but the root -/

/-- **The four colour classes of `r` cover `V \ {r}`.**  From `|V| = 58` and the
class sizes (their sum is `57`): the classes are pairwise disjoint and miss `r`, so
their union has `57` elements and sits inside `V \ {r}`, of which there are `57`. -/
theorem exists_class_of_ne (G : EdgeCol V 4) (r : V) (hV : Fintype.card V = 58)
    (hcard : ∑ c : Fin 4, (nbrC G r c).card = 57) :
    ∀ z : V, z ≠ r → ∃ c : Fin 4, z ∈ nbrC G r c := by
  classical
  have hdisj : ∀ c ∈ (Finset.univ : Finset (Fin 4)), ∀ d ∈ (Finset.univ : Finset (Fin 4)),
      c ≠ d → Disjoint (nbrC G r c) (nbrC G r d) := by
    intro c _ d _ hcd
    rw [Finset.disjoint_left]
    intro y hy hy'
    have h1 : G.col r y = c := (mem_nbrC.mp hy).2
    have h2 : G.col r y = d := (mem_nbrC.mp hy').2
    exact hcd (h1 ▸ h2)
  have hU : (Finset.univ.biUnion (fun c : Fin 4 => nbrC G r c)).card = 57 := by
    rw [Finset.card_biUnion hdisj]
    simpa using hcard
  have hr : r ∉ Finset.univ.biUnion (fun c : Fin 4 => nbrC G r c) := by
    intro hmem
    rw [Finset.mem_biUnion] at hmem
    obtain ⟨c, -, hc⟩ := hmem
    exact notMem_nbrC_self G r c hc
  have hsub : Finset.univ.biUnion (fun c : Fin 4 => nbrC G r c) ⊆
      (Finset.univ.erase r : Finset V) := by
    intro y hy
    rw [Finset.mem_erase]
    exact ⟨fun hyr => hr (hyr ▸ hy), Finset.mem_univ y⟩
  have h57 : (Finset.univ.erase r : Finset V).card = 57 := by
    rw [Finset.card_erase_of_mem (Finset.mem_univ r), Finset.card_univ, hV]
  have heq : Finset.univ.biUnion (fun c : Fin 4 => nbrC G r c) = Finset.univ.erase r :=
    Finset.eq_of_subset_of_card_le hsub (le_of_eq (by rw [hU, h57]))
  intro z hzr
  have hz : z ∈ Finset.univ.biUnion (fun c : Fin 4 => nbrC G r c) := by
    rw [heq, Finset.mem_erase]
    exact ⟨hzr, Finset.mem_univ z⟩
  rw [Finset.mem_biUnion] at hz
  obtain ⟨c, -, hc⟩ := hz
  exact ⟨c, hc⟩

/-- A word's colour-`0` class meets `A` only in `r` and in classes of `r` of
non-zero colour. -/
theorem nbrC_zero_cover (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hV : Fintype.card V = 58) (hcard : ∑ c : Fin 4, (nbrC G r c).card = 57)
    {a z : V} (ha : a ∈ nbrC G r 0) (hz : z ∈ nbrC G a 0) :
    z = r ∨ ∃ f : Fin 4, f ≠ 0 ∧ z ∈ nbrC G r f := by
  rcases arm_nbr_subset G h ha hz with h' | ⟨hzr, hzA⟩
  · exact Or.inl h'
  · obtain ⟨f, hf⟩ := exists_class_of_ne G r hV hcard z hzr
    exact Or.inr ⟨f, fun hf0 => hzA (hf0 ▸ hf), hf⟩

/-- **The class split at a word.**  With `S` containing every non-zero colour, the
class of a word over the root is `{r}` together with its intersections with the
classes `N_c(r)`, `c ∈ S`. -/
theorem nbrC_zero_card_split (G : EdgeCol V 4) (h : TriangleFree G) (r a : V)
    (hV : Fintype.card V = 58) (hcard : ∑ c : Fin 4, (nbrC G r c).card = 57)
    (ha : a ∈ nbrC G r 0) (S : Finset (Fin 4)) (hS : ∀ c : Fin 4, c ≠ 0 → c ∈ S) :
    (nbrC G a 0).card
      = 1 + ∑ c ∈ S, ((nbrC G a 0) ∩ (nbrC G r c)).card := by
  classical
  have hcover : nbrC G a 0
      = insert r (S.biUnion (fun c => (nbrC G a 0) ∩ (nbrC G r c))) := by
    ext z
    constructor
    · intro hz
      rcases nbrC_zero_cover G h r hV hcard ha hz with hzr | ⟨f, hf0, hzf⟩
      · rw [hzr]; exact Finset.mem_insert_self _ _
      · refine Finset.mem_insert.mpr (Or.inr ?_)
        rw [Finset.mem_biUnion]
        exact ⟨f, hS f hf0, Finset.mem_inter.mpr ⟨hz, hzf⟩⟩
    · intro hz
      rcases Finset.mem_insert.mp hz with hzr | hz
      · rw [hzr]; exact (mem_nbrC_swap G 0 r a).mpr ha
      · rw [Finset.mem_biUnion] at hz
        obtain ⟨c, -, hc⟩ := hz
        exact (Finset.mem_inter.mp hc).1
  have hdisj : ∀ c ∈ S, ∀ d ∈ S, c ≠ d →
      Disjoint ((nbrC G a 0) ∩ (nbrC G r c)) ((nbrC G a 0) ∩ (nbrC G r d)) := by
    intro c _ d _ hcd
    rw [Finset.disjoint_left]
    intro y hy hy'
    have h1 : G.col r y = c := (mem_nbrC.mp (Finset.mem_inter.mp hy).2).2
    have h2 : G.col r y = d := (mem_nbrC.mp (Finset.mem_inter.mp hy').2).2
    exact hcd (h1 ▸ h2)
  have hnotin : r ∉ S.biUnion (fun c => (nbrC G a 0) ∩ (nbrC G r c)) := by
    intro hmem
    rw [Finset.mem_biUnion] at hmem
    obtain ⟨c, -, hc⟩ := hmem
    exact notMem_nbrC_self G r c (Finset.mem_inter.mp hc).2
  conv_lhs => rw [hcover]
  rw [Finset.card_insert_of_notMem hnotin, Finset.card_biUnion hdisj]
  omega

/-! ## Part F: the box, and three positions of slack -/

/-- **The sound per-position box of the `(14,12)` rung.**  For a word `a` of `A`
with `d_0(a) = 15`: `7 <= B + C <= 10`, where `B = N_1(r)` is the complete arm and
`C' ⊆ N_2(r)` the 12-subset.  The upper bound is `mixture` twice; the lower bound is
the class split plus the truncation: the third arm can hold at most five of the
word's fourteen outside `0`-neighbours, and the two dropped words of the truncated
arm at most two more. -/
theorem rung_box (G : EdgeCol V 4) (h : TriangleFree G) (r a : V)
    (hV : Fintype.card V = 58)
    (hA15 : (nbrC G r 0).card = 15)
    (hB14 : (nbrC G r 1).card = 14)
    (hC14 : (nbrC G r 2).card = 14)
    (hD14 : (nbrC G r 3).card = 14)
    (ha : a ∈ nbrC G r 0) (hda : (nbrC G a 0).card = 15)
    (C' : Finset V) (hC' : C' ⊆ nbrC G r 2) (hCc : C'.card = 12) :
    7 ≤ ((nbrC G a 0) ∩ (nbrC G r 1)).card + ((nbrC G a 0) ∩ C').card ∧
      ((nbrC G a 0) ∩ (nbrC G r 1)).card + ((nbrC G a 0) ∩ C').card ≤ 10 := by
  classical
  set S : Finset (Fin 4) := {1, 2, 3} with hSdef
  have hS : ∀ c : Fin 4, c ≠ 0 → c ∈ S := by
    intro c hc
    rw [hSdef]
    fin_cases c
    · exact absurd rfl hc
    · simp
    · simp
    · simp
  have hcard : ∑ c : Fin 4, (nbrC G r c).card = 57 := by
    rw [Fin.sum_univ_four, hA15, hB14, hC14, hD14]
  have hsplit := nbrC_zero_card_split G h r a hV hcard ha S hS
  have hSsum : ∑ c ∈ S, ((nbrC G a 0) ∩ (nbrC G r c)).card
      = ((nbrC G a 0) ∩ (nbrC G r 1)).card + ((nbrC G a 0) ∩ (nbrC G r 2)).card
        + ((nbrC G a 0) ∩ (nbrC G r 3)).card := by
    rw [hSdef]
    simp [Finset.sum_insert, add_assoc]
  rw [hSsum] at hsplit
  -- the third arm holds at most five
  have hd5 : ((nbrC G a 0) ∩ (nbrC G r 3)).card ≤ 5 :=
    block_le_five G h r a (by decide : (3 : Fin 4) ≠ 0)
  -- the dropped pair costs at most two
  have hdrop : ((nbrC G a 0) ∩ (nbrC G r 2)).card
      ≤ ((nbrC G a 0) ∩ C').card + 2 := by
    have hdiff : ((nbrC G r 2) \ C').card = 2 := by
      rw [Finset.card_sdiff_of_subset hC', hC14, hCc]
    have hd : ((nbrC G a 0) ∩ (nbrC G r 2)) \ ((nbrC G a 0) ∩ C')
        ⊆ (nbrC G r 2) \ C' := by
      intro z hz
      rw [Finset.mem_sdiff] at hz ⊢
      exact ⟨(Finset.mem_inter.mp hz.1).2,
        fun hzc => hz.2 (Finset.mem_inter.mpr ⟨(Finset.mem_inter.mp hz.1).1, hzc⟩)⟩
    have h1 : (nbrC G a 0) ∩ (nbrC G r 2)
        = ((nbrC G a 0) ∩ C')
          ∪ (((nbrC G a 0) ∩ (nbrC G r 2)) \ ((nbrC G a 0) ∩ C')) := by
      ext z
      simp only [Finset.mem_union, Finset.mem_sdiff, Finset.mem_inter]
      constructor
      · rintro ⟨hz1, hz2⟩
        by_cases hzc : z ∈ C'
        · exact Or.inl ⟨hz1, hzc⟩
        · exact Or.inr ⟨⟨hz1, hz2⟩, fun hcon => hzc hcon.2⟩
      · rintro (⟨hz1, hz2⟩ | ⟨⟨hz1, hz2⟩, -⟩)
        · exact ⟨hz1, hC' hz2⟩
        · exact ⟨hz1, hz2⟩
    have hdj : Disjoint ((nbrC G a 0) ∩ C')
        (((nbrC G a 0) ∩ (nbrC G r 2)) \ ((nbrC G a 0) ∩ C')) := by
      rw [Finset.disjoint_left]
      intro z hz hz'
      exact (Finset.mem_sdiff.mp hz').2 hz
    rw [h1, Finset.card_union_of_disjoint hdj]
    have hle := Finset.card_le_card hd
    omega
  have hb5 : ((nbrC G a 0) ∩ (nbrC G r 1)).card ≤ 5 :=
    block_le_five G h r a (by decide : (1 : Fin 4) ≠ 0)
  have hc5 : ((nbrC G a 0) ∩ C').card ≤ 5 :=
    block_le_five_subset G h r a (by decide : (2 : Fin 4) ≠ 0) C' hC'
  constructor <;> omega

/-! ## Part G: three positions of slack, and sharpness -/

/-- **At least three of the fifteen positions carry `B + C <= 8`.**  Every position
lies in `[7,10]` (`rung_box`) and the fifteen positions sum to `130`
(`sum_support_arm`, `sum_support_subset`).  So if `k` positions carried `9` or
more, the sum would be at least `9k + 7(15-k) = 105 + 2k`, forcing `k <= 12`.  This
is a sound cardinality constraint on the `(14,12)` rung that the frozen instance
does not carry as a cardinality cluster. -/
theorem rung_three_slack (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hV : Fintype.card V = 58)
    (hA15 : (nbrC G r 0).card = 15)
    (hm : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → ((nbrC G x 0) ∩ (nbrC G r 0)).card = 5)
    (hB14 : (nbrC G r 1).card = 14)
    (hC14 : (nbrC G r 2).card = 14)
    (hD14 : (nbrC G r 3).card = 14)
    (hAcrit : ∀ a ∈ nbrC G r 0, (nbrC G a 0).card = 15)
    (C' : Finset V) (hC' : C' ⊆ nbrC G r 2) (hCc : C'.card = 12) :
    3 ≤ ((nbrC G r 0).filter
      (fun a => ((nbrC G a 0) ∩ (nbrC G r 1)).card + ((nbrC G a 0) ∩ C').card ≤ 8)).card := by
  classical
  set A : Finset V := nbrC G r 0 with hAdef
  set phi : V → ℕ :=
    fun a => ((nbrC G a 0) ∩ (nbrC G r 1)).card + ((nbrC G a 0) ∩ C').card with hphidef
  have hbox : ∀ a ∈ A, 7 ≤ phi a ∧ phi a ≤ 10 := by
    intro a ha'
    have ha : a ∈ nbrC G r 0 := hAdef ▸ ha'
    exact rung_box G h r a hV hA15 hB14 hC14 hD14 ha (hAcrit a ha) C' hC' hCc
  have hsum : ∑ a ∈ A, phi a = 130 := by
    have h1 := sum_support_arm G r (f := 1) (by decide : (1 : Fin 4) ≠ 0) hm
    have h2 := sum_support_subset G r (f := 2) (by decide : (2 : Fin 4) ≠ 0) hm C' hC'
    rw [hB14] at h1
    rw [hCc] at h2
    have : ∑ a ∈ A, phi a = ∑ a ∈ nbrC G r 0, ((nbrC G a 0) ∩ (nbrC G r 1)).card
        + ∑ a ∈ nbrC G r 0, ((nbrC G a 0) ∩ C').card := by
      rw [hphidef, hAdef, Finset.sum_add_distrib]
    rw [this, h1, h2]
  set T : Finset V := A.filter (fun a => 9 ≤ phi a) with hTdef
  have hTsub : T ⊆ A := Finset.filter_subset _ _
  have hTcard : T.card ≤ 15 := by
    refine le_trans (Finset.card_le_card hTsub) ?_
    rw [hAdef, hA15]
  have hgeT : 9 * T.card ≤ ∑ a ∈ T, phi a := by
    calc 9 * T.card = ∑ _a ∈ T, 9 := by
          rw [Finset.sum_const_nat (fun x _ => rfl), Nat.mul_comm]
      _ ≤ ∑ a ∈ T, phi a :=
          Finset.sum_le_sum (fun a ha' => (Finset.mem_filter.mp ha').2)
  have hgeC : 7 * (A \ T).card ≤ ∑ a ∈ A \ T, phi a := by
    calc 7 * (A \ T).card = ∑ _a ∈ A \ T, 7 := by
          rw [Finset.sum_const_nat (fun x _ => rfl), Nat.mul_comm]
      _ ≤ ∑ a ∈ A \ T, phi a :=
          Finset.sum_le_sum (fun a ha' => (hbox a (Finset.mem_sdiff.mp ha').1).1)
  have hsplit : ∑ a ∈ A, phi a = ∑ a ∈ A \ T, phi a + ∑ a ∈ T, phi a :=
    (Finset.sum_sdiff hTsub).symm
  have hk : T.card ≤ 12 := by
    have hAcard : A.card = 15 := by rw [hAdef, hA15]
    have hAcardT : (A \ T).card = 15 - T.card := by
      rw [Finset.card_sdiff_of_subset hTsub, hAcard]
    omega
  have hnot : (A.filter (fun a => ¬ 9 ≤ phi a)).card = A.card - T.card := by
    have h1 := Finset.card_filter_add_card_filter_not (s := A) (p := fun a => 9 ≤ phi a)
    have h2 : T.card = (A.filter (fun a => 9 ≤ phi a)).card := rfl
    omega
  have hfilters : (A.filter
      (fun a => ((nbrC G a 0) ∩ (nbrC G r 1)).card + ((nbrC G a 0) ∩ C').card ≤ 8))
      = A.filter (fun a => phi a ≤ 8) := by
    apply Finset.filter_congr
    intro a _
    rw [hphidef]
  have hnot2 : (A.filter (fun a => phi a ≤ 8)).card = A.card - T.card := by
    rw [← hnot]
    exact congrArg Finset.card (Finset.filter_congr (fun a _ => by omega))
  rw [hfilters, hnot2]
  have hAcard : A.card = 15 := by rw [hAdef, hA15]
  omega

/-- The witness vector for sharpness: `b = (4,4,4,4,4,5,...,5)`,
`c = (3,3,4,5,5,4,...,4)` on `Fin 15`. -/
def slackB : Fin 15 → ℕ := fun i => if (i : ℕ) < 5 then 4 else 5

/-- The second coordinate of the sharpness witness. -/
def slackC : Fin 15 → ℕ := fun i =>
  if (i : ℕ) = 0 then 3 else if (i : ℕ) = 1 then 3 else if (i : ℕ) = 2 then 4
    else if (i : ℕ) = 3 then 5 else if (i : ℕ) = 4 then 5 else 4

/-- **Sharpness.**  A vector meeting every constraint used above — `b, c <= 5`,
`7 <= b + c <= 10` positionwise, `Sum b = 70`, `Sum c = 60` — carries `9 <= b + c`
at exactly twelve of the fifteen positions.  So `rung_three_slack` is the best
statement the double count can give: thirteen positions at nine is out of reach,
twelve is not. -/
theorem slack_sharp :
    (∀ i : Fin 15, slackB i ≤ 5 ∧ slackC i ≤ 5) ∧
    (∀ i : Fin 15, 7 ≤ slackB i + slackC i ∧ slackB i + slackC i ≤ 10) ∧
    (∑ i, slackB i = 70) ∧ (∑ i, slackC i = 60) ∧
    ((Finset.univ.filter (fun i : Fin 15 => 9 ≤ slackB i + slackC i)).card = 12) := by
  refine ⟨?_, ?_, ?_, ?_, ?_⟩ <;> decide

/-- **Exactly five of the fifteen positions are deficient.**  `Sum_a B = 70 = 15 * 5
- 5` with `B <= 5` at every position, so the deficiencies `5 - B` sum to five.  This
is the arm-level form of the campaign's "five senders are deficient per arm"; as a
cardinality constraint it says exactly five arm points meet `N_1(r)` in at most
four points. -/
theorem rung_deficiency (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hA15 : (nbrC G r 0).card = 15)
    (hm : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → ((nbrC G x 0) ∩ (nbrC G r 0)).card = 5)
    {f : Fin 4} (hf : f ≠ 0) (hB14 : (nbrC G r f).card = 14) :
    ∑ a ∈ nbrC G r 0, (5 - ((nbrC G a 0) ∩ (nbrC G r f)).card) = 5 := by
  have h1 := sum_support_arm G r hf hm
  rw [hB14] at h1
  have hle : ∀ a ∈ nbrC G r 0, ((nbrC G a 0) ∩ (nbrC G r f)).card ≤ 5 :=
    fun a _ => block_le_five G h r a hf
  have hterm : ∀ a ∈ nbrC G r 0,
      (5 - ((nbrC G a 0) ∩ (nbrC G r f)).card) + ((nbrC G a 0) ∩ (nbrC G r f)).card
        = 5 := by
    intro a ha'
    have := hle a ha'
    omega
  have hsum5 : ∑ a ∈ nbrC G r 0,
      ((5 - ((nbrC G a 0) ∩ (nbrC G r f)).card) + ((nbrC G a 0) ∩ (nbrC G r f)).card)
      = 75 := by
    rw [Finset.sum_congr rfl hterm, Finset.sum_const_nat (fun x _ => rfl), hA15]
  rw [Finset.sum_add_distrib] at hsum5
  omega

/-- **Every arm point is deficient in exactly one ordinary arm.**  Its class is
`{r}` plus its intersections with the three `14`-arms (`nbrC_zero_card_split`), so
the three counts sum to `14`; each is at most `5` (`mixture`).  The only triples of
three integers at most `5` summing to `14` are the permutations of `(4,5,5)`.  This
is the kernel form of the campaign's "the deficient colour is unique at each
sender". -/
theorem arm_triple (G : EdgeCol V 4) (h : TriangleFree G) (r a : V)
    (hV : Fintype.card V = 58)
    (hA15 : (nbrC G r 0).card = 15)
    (hB14 : (nbrC G r 1).card = 14)
    (hC14 : (nbrC G r 2).card = 14)
    (hD14 : (nbrC G r 3).card = 14)
    (ha : a ∈ nbrC G r 0) (hda : (nbrC G a 0).card = 15) :
    ((nbrC G a 0) ∩ (nbrC G r 1)).card + ((nbrC G a 0) ∩ (nbrC G r 2)).card
        + ((nbrC G a 0) ∩ (nbrC G r 3)).card = 14 ∧
      ((nbrC G a 0) ∩ (nbrC G r 1)).card ≤ 5 ∧
      ((nbrC G a 0) ∩ (nbrC G r 2)).card ≤ 5 ∧
      ((nbrC G a 0) ∩ (nbrC G r 3)).card ≤ 5 := by
  classical
  set S : Finset (Fin 4) := {1, 2, 3} with hSdef
  have hS : ∀ c : Fin 4, c ≠ 0 → c ∈ S := by
    intro c hc
    rw [hSdef]
    fin_cases c
    · exact absurd rfl hc
    · simp
    · simp
    · simp
  have hcard : ∑ c : Fin 4, (nbrC G r c).card = 57 := by
    rw [Fin.sum_univ_four, hA15, hB14, hC14, hD14]
  have hsplit := nbrC_zero_card_split G h r a hV hcard ha S hS
  have hSsum : ∑ c ∈ S, ((nbrC G a 0) ∩ (nbrC G r c)).card
      = ((nbrC G a 0) ∩ (nbrC G r 1)).card + ((nbrC G a 0) ∩ (nbrC G r 2)).card
        + ((nbrC G a 0) ∩ (nbrC G r 3)).card := by
    rw [hSdef]
    simp [Finset.sum_insert, add_assoc]
  rw [hSsum] at hsplit
  refine ⟨by omega, ?_, ?_, ?_⟩
  · exact block_le_five G h r a (by decide : (1 : Fin 4) ≠ 0)
  · exact block_le_five G h r a (by decide : (2 : Fin 4) ≠ 0)
  · exact block_le_five G h r a (by decide : (3 : Fin 4) ≠ 0)

/-- **The two-arm exact law.**  For a word `a` of `A`, the counts into two complete
`14`-arms sum to `9` or `10` (`arm_triple` with the third arm holding `4` or `5`).
This is the law the state file records as satisfied by every branch object and
violated by the recorded two-arm witness (`s_B + s_C` was `[8,9,10]` there), which
had made an earlier "the two-arm level is SAT" claim void. -/
theorem two_arm_law (G : EdgeCol V 4) (h : TriangleFree G) (r a : V)
    (hV : Fintype.card V = 58)
    (hA15 : (nbrC G r 0).card = 15)
    (hB14 : (nbrC G r 1).card = 14)
    (hC14 : (nbrC G r 2).card = 14)
    (hD14 : (nbrC G r 3).card = 14)
    (ha : a ∈ nbrC G r 0) (hda : (nbrC G a 0).card = 15) :
    9 ≤ ((nbrC G a 0) ∩ (nbrC G r 1)).card + ((nbrC G a 0) ∩ (nbrC G r 2)).card ∧
      ((nbrC G a 0) ∩ (nbrC G r 1)).card + ((nbrC G a 0) ∩ (nbrC G r 2)).card ≤ 10 := by
  obtain ⟨hsum, h1, h2, h3⟩ := arm_triple G h r a hV hA15 hB14 hC14 hD14 ha hda
  omega

/-! ## Part H: Law 6 without reciprocity -/

/-- **`M >= 7` without `(R)`.**  `K58.M_ge_seven` derives "colour `0` is critical
everywhere" from reciprocity plus the uniform branch (`K58.branch_crit`), and uses
nothing else from `(R)`.  Taking that conclusion as the hypothesis therefore gives
a strictly stronger statement, applicable to objects that do not return all
tickets.  The proof is `M_ge_seven`'s with the `branch_crit` line replaced. -/
theorem M_ge_seven_of_crit (G : EdgeCol V 4) (hT : TriangleFree G)
    (hV : Fintype.card V = 58)
    (hcrit : ∀ z : V, 15 ≤ deg G z 0) (r : V)
    (hA15 : (nbrC G r 0).card = 15)
    (hAcrit : ∀ a ∈ nbrC G r 0, deg G a 0 = 15)
    (hm5 : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → (nbrC G x 0 ∩ nbrC G r 0).card = 5)
    (M : ℕ) (hM : ∀ u v : V, u ≠ v → (nbrC G u 0 ∩ nbrC G v 0).card ≤ M) :
    7 ≤ M := by
  classical
  by_contra hcon
  push Not at hcon
  have hM6 : M ≤ 6 := by omega
  have h6 : ∀ p q : V, p ≠ q → (nbrC G p 0 ∩ nbrC G q 0).card ≤ 6 := by
    intro p q hpq
    have := hM p q hpq
    omega
  have harm5 := arm_codeg_le_five G hT hV hcrit r hm5 h6
  obtain ⟨x, hxr, hxA⟩ := exists_outside G hV hA15
  have hP5 : (nbrC G x 0 ∩ nbrC G r 0).card = 5 := hm5 x hxr hxA
  have hPdeg : ∀ p ∈ nbrC G x 0 ∩ nbrC G r 0, deg G p 0 = 15 := by
    intro p hp
    exact hAcrit p (Finset.mem_inter.mp hp).2
  have hbound := rx_bound G hT hV hxr hxA hA15 hP5 hPdeg 5 (by norm_num)
    (fun u hu v hv huv =>
      harm5 u (Finset.mem_inter.mp hu).2 v (Finset.mem_inter.mp hv).2 huv)
  have hx15 : 15 ≤ deg G x 0 := hcrit x
  omega

end K58

#print axioms K58.mem_nbrC_swap
#print axioms K58.sum_inter_nbrC_comm
#print axioms K58.word_support_eq_five
#print axioms K58.sum_support_arm
#print axioms K58.sum_support_subset
#print axioms K58.rung_guard
#print axioms K58.rung_exists_le_eight
#print axioms K58.guard_sharp
#print axioms K58.block_le_five
#print axioms K58.block_le_five_subset
#print axioms K58.block_le_ten
#print axioms K58.exists_class_of_ne
#print axioms K58.nbrC_zero_cover
#print axioms K58.nbrC_zero_card_split
#print axioms K58.rung_box
#print axioms K58.rung_three_slack
#print axioms K58.slack_sharp
#print axioms K58.rung_deficiency
#print axioms K58.arm_triple
#print axioms K58.two_arm_law
#print axioms K58.M_ge_seven_of_crit
