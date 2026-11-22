/-
Transfer 1, kernel version: `M >= 7` for the `(15,14,14,14)` profile at `n = 58`.

Kernel form of the paper proof in
`.ultramath/smwridmzp/m3/REPORT.md` (Theorem 1 and its six lemmas).

The proof is 0-graph only.  Notation: `N_0 z = nbrC G z 0`, `A = N_0 r`,
`X = V \ (A u {r})`, `m x = |N_0 x cap A| = 5` for `x in X`, `d_0 = deg · 0`.

Branch hypotheses used (the problem's standing data, not re-derived here):
* `hA15 : |A| = 15`;
* `hAcrit : d_0 a = 15` for every `a in A` (every arm point is 0-critical);
* `hm5 : |N_0 x cap A| = 5` for every outside vertex `x`;
* `hR : Reciprocal G` (all tickets returned).

Results:

* `collision_engine` : the convexity device `C(d,2) >= 2d - 3` summed, once and
  for all, in the subtraction-free form
  `2 * (incidences) <= (pair count) + 3 * #R`.
* `pair_filter_le`  : a pair's `R`-class is its codegree minus a fixed set `B`
  of common neighbours lying outside `R`.
* `rx_bound`        : the collision count at the universal pair `(r,x)`:
  `3 d_0(x) + 12 <= 10 K` for any `K` bounding the codegrees inside
  `N_0(x) cap N_0(r)`.
* `M_ge_six`        : Corollary 3 (`M >= 6`), from `rx_bound` with `K = M`.
* `rigid_six`       : Lemma 4, the rigidity at a codegree-`6` pair.
* `arm_codeg_le_five` : Lemma 5 (`M <= 6` forbids an arm pair of codegree `6`).
* `arm_pair_total`  : Theorem 2(1), `sum_{a<a'} mu(a,a') = 525`.
* `arm_all_five`    : Lemma 6, `M <= 6` forces every arm pair to have codegree
  exactly `5`.
* `M_ge_seven`      : Theorem 1, `7 <= M`.

Note on the route: the paper's Lemma 2 gives `C_x >= 3 d_0(x) - 8` and
`C_x <= 10 (M-2)`; `rx_bound` states the two together, so the final step is one
linear inequality (`K = 5` gives `57 <= 50`) rather than two separate bounds.
Lemma 2's `C_x` is the `powersetCard` sum in `rx_pair_bound`; the identity
`sum_z C(|S cap N z|, 2) = sum_{q} |{z : q subset N z}|` is `sum_choose_two_comm`,
stated once and used at `(r,x)`, at a codegree-`6` pair, and in the `525` count.
-/
import Mathlib.Tactic
import K58.Basic
import K58.Mixture
import K58.DegreeCap
import K58.Ticket

set_option linter.unusedSectionVars false

namespace K58

/-! ## Part A: generic counting lemmas -/

section Generic

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Convexity, subtraction-free: `C(d,2) + 3 >= 2d` for every natural `d`. -/
theorem choose_two_add_three (d : ℕ) : 2 * d ≤ d.choose 2 + 3 := by
  induction d with
  | zero => simp
  | succ n ih =>
    match n with
    | 0 => simp
    | m + 1 =>
      have h : (m + 1 + 1).choose 2 = (m + 1) + (m + 1).choose 2 := by
        have hh := Nat.choose_succ_succ (m + 1) 1
        rw [Nat.choose_one_right] at hh
        rw [show (Nat.succ 1 : ℕ) = 2 from by norm_num] at hh
        show Nat.choose (Nat.succ (m + 1)) 2 = (m + 1) + Nat.choose (m + 1) 2
        exact hh
      omega

/-- **Linear double count.**  Summing a neighbourhood size over the vertices of
`R` equals summing the `R`-size over the vertices of `S`. -/
theorem sum_card_filter_comm (N : V → Finset V) (S R : Finset V) :
    ∑ s ∈ S, (R.filter (fun z => s ∈ N z)).card
      = ∑ z ∈ R, (S.filter (fun s => s ∈ N z)).card := by
  have h : ∀ s : V, (R.filter (fun z => s ∈ N z)).card
      = ∑ z ∈ R, if (s ∈ N z) then 1 else 0 := fun s => Finset.card_filter _ _
  have h' : ∀ z : V, (S.filter (fun s => s ∈ N z)).card
      = ∑ s ∈ S, if (s ∈ N z) then 1 else 0 := fun z => Finset.card_filter _ _
  calc ∑ s ∈ S, (R.filter (fun z => s ∈ N z)).card
      = ∑ s ∈ S, ∑ z ∈ R, if (s ∈ N z) then 1 else 0 :=
        Finset.sum_congr rfl (fun s _ => h s)
    _ = ∑ z ∈ R, ∑ s ∈ S, if (s ∈ N z) then 1 else 0 := Finset.sum_comm
    _ = ∑ z ∈ R, (S.filter (fun s => s ∈ N z)).card :=
        Finset.sum_congr rfl (fun z _ => (h' z).symm)

/-- **Triple double count.**  The number of (vertex of `R`, pair inside its
`S`-neighbourhood) is also the number of (pair inside `S`, vertex of `R`
containing it). -/
theorem sum_choose_two_comm (N : V → Finset V) (S R : Finset V) :
    ∑ z ∈ R, (S.filter (fun s => s ∈ N z)).card.choose 2
      = ∑ q ∈ S.powersetCard 2, (R.filter (fun z => ∀ s ∈ q, s ∈ N z)).card := by
  have subset_iff : ∀ (q : Finset V) (z : V), q ⊆ S →
      (q ⊆ S.filter (fun s => s ∈ N z) ↔ ∀ s ∈ q, s ∈ N z) := by
    intro q z hqS
    exact ⟨fun hh s hs => (Finset.mem_filter.mp (hh hs)).2,
      fun hh s hs => Finset.mem_filter.mpr ⟨hqS hs, hh s hs⟩⟩
  have step1 : ∀ z : V, (S.filter (fun s => s ∈ N z)).card.choose 2
      = ∑ q ∈ S.powersetCard 2, if (∀ s ∈ q, s ∈ N z) then 1 else 0 := by
    intro z
    rw [← Finset.card_powersetCard 2 (S.filter (fun s => s ∈ N z))]
    rw [← Finset.card_filter (fun q : Finset V => ∀ s ∈ q, s ∈ N z) (S.powersetCard 2)]
    congr 1
    ext q
    rw [Finset.mem_filter, Finset.mem_powersetCard, Finset.mem_powersetCard]
    constructor
    · rintro ⟨hq, hc⟩
      exact ⟨⟨subset_trans hq (Finset.filter_subset _ _), hc⟩,
        (subset_iff q z (subset_trans hq (Finset.filter_subset _ _))).mp hq⟩
    · rintro ⟨⟨hqS, hc⟩, hall⟩
      exact ⟨(subset_iff q z hqS).mpr hall, hc⟩
  calc ∑ z ∈ R, (S.filter (fun s => s ∈ N z)).card.choose 2
      = ∑ z ∈ R, ∑ q ∈ S.powersetCard 2, if (∀ s ∈ q, s ∈ N z) then 1 else 0 :=
        Finset.sum_congr rfl (fun z _ => step1 z)
    _ = ∑ q ∈ S.powersetCard 2, ∑ z ∈ R, if (∀ s ∈ q, s ∈ N z) then 1 else 0 :=
        Finset.sum_comm
    _ = ∑ q ∈ S.powersetCard 2, (R.filter (fun z => ∀ s ∈ q, s ∈ N z)).card :=
        Finset.sum_congr rfl (fun q _ => (Finset.card_filter _ _).symm)

/-- **The collision engine.**  If `d z` is the number of vertices of `S`
adjacent to `z`, then the total over pairs of `S` of the number of
`R`-vertices containing the pair is at least `2 * (incidences) - 3 * #R`. -/
theorem collision_engine (N : V → Finset V) (S R : Finset V) :
    2 * (∑ z ∈ R, (S.filter (fun s => s ∈ N z)).card)
      ≤ (∑ q ∈ S.powersetCard 2, (R.filter (fun z => ∀ s ∈ q, s ∈ N z)).card)
        + 3 * R.card := by
  have h1 : ∀ z ∈ R, 2 * (S.filter (fun s => s ∈ N z)).card
      ≤ (S.filter (fun s => s ∈ N z)).card.choose 2 + 3 :=
    fun z _ => choose_two_add_three _
  have h2 : ∑ z ∈ R, 2 * (S.filter (fun s => s ∈ N z)).card
      ≤ ∑ z ∈ R, ((S.filter (fun s => s ∈ N z)).card.choose 2 + 3) :=
    Finset.sum_le_sum h1
  have h3 : (∑ _z ∈ R, (3 : ℕ)) = 3 * R.card := by
    rw [Finset.sum_const, Finset.card_eq_sum_ones, Finset.mul_sum]
    simp
  rw [← Finset.mul_sum, Finset.sum_add_distrib, h3, sum_choose_two_comm N S R] at h2
  omega

/-- A filter over a two-element set is the corresponding conjunction. -/
theorem filter_pair_eq (R : Finset V) (N : V → Finset V) (s s' : V) :
    (R.filter (fun z => ∀ p ∈ ({s, s'} : Finset V), p ∈ N z))
      = R.filter (fun z => s ∈ N z ∧ s' ∈ N z) := by
  apply Finset.filter_congr
  intro z _
  constructor
  · intro h
    exact ⟨h s (by simp), h s' (by simp)⟩
  · rintro ⟨h1, h2⟩ p hp
    rcases Finset.mem_insert.mp hp with h | h
    · rw [h]; exact h1
    · rw [Finset.mem_singleton.mp h]; exact h2

/-- **A pair's `R`-class is its codegree minus `B`.**  If `B` is a set of common
`N`-neighbours of `s` and `s'` lying outside `R`, then the number of vertices of
`R` adjacent to both is at most `codegree - |B|`, and `codegree` is bounded. -/
theorem pair_filter_le (N : V → Finset V) (hN : ∀ z p : V, p ∈ N z ↔ z ∈ N p)
    (R B : Finset V) {s s' : V}
    (hBsub : B ⊆ N s ∩ N s') (hBdisj : Disjoint B R) (k : ℕ)
    (hcodeg : (N s ∩ N s').card ≤ k) :
    (R.filter (fun z => ∀ p ∈ ({s, s'} : Finset V), p ∈ N z)).card ≤ k - B.card := by
  rw [filter_pair_eq R N s s']
  have hsub : (R.filter (fun z => s ∈ N z ∧ s' ∈ N z))
      ⊆ (N s ∩ N s') \ B := by
    intro z hz
    obtain ⟨hzR, hz1, hz2⟩ := Finset.mem_filter.mp hz
    refine Finset.mem_sdiff.mpr ⟨Finset.mem_inter.mpr ⟨(hN z s).mp hz1, (hN z s').mp hz2⟩, ?_⟩
    intro hzB
    exact Finset.disjoint_left.mp hBdisj hzB hzR
  have hcard : ((N s ∩ N s') \ B).card = (N s ∩ N s').card - B.card :=
    Finset.card_sdiff_of_subset hBsub
  have := Finset.card_le_card hsub
  omega

/-- **All terms equal.**  A sum whose terms are each at most `k` and which equals
`#s * k` has every term equal to `k`. -/
theorem all_eq_of_sum_eq_card_mul {α : Type*} [DecidableEq α] {s : Finset α} {F : α → ℕ}
    {k : ℕ} (hle : ∀ a ∈ s, F a ≤ k) (hsum : ∑ a ∈ s, F a = s.card * k) :
    ∀ a ∈ s, F a = k := by
  intro a ha
  set E := ∑ b ∈ s.erase a, F b with hEdef
  have h1 : F a + E = s.card * k := by
    rw [hEdef, Finset.add_sum_erase s F ha, hsum]
  have h2 : E ≤ (s.card - 1) * k := by
    rw [hEdef]
    calc ∑ b ∈ s.erase a, F b ≤ ∑ _b ∈ s.erase a, k :=
          Finset.sum_le_sum (fun b hb => hle b (Finset.mem_erase.mp hb).2)
      _ = (s.erase a).card * k := Finset.sum_const_nat (fun b _ => rfl)
      _ = (s.card - 1) * k := by rw [Finset.card_erase_of_mem ha]
  have h4 : 1 ≤ s.card := Finset.card_pos.mpr ⟨a, ha⟩
  have h5 : (s.card - 1) * k = s.card * k - k := by
    rw [Nat.sub_mul, one_mul]
  have h6 : k ≤ s.card * k := by
    simpa using Nat.mul_le_mul_right k h4
  have hkey : k ≤ s.card * k - E := by
    have h7 : s.card * k - ((s.card - 1) * k) ≤ s.card * k - E :=
      Nat.sub_le_sub_left h2 _
    rw [h5, Nat.sub_sub_self h6] at h7
    exact h7
  have h8 : F a = s.card * k - E := Nat.eq_sub_of_add_eq h1
  have := hle a ha
  omega

/-- **All terms equal, from below.**  A sum whose terms are each at least `k` and
which equals `#s * k` has every term equal to `k`. -/
theorem all_eq_of_card_mul_eq_sum {α : Type*} [DecidableEq α] {s : Finset α} {F : α → ℕ}
    {k : ℕ} (hge : ∀ a ∈ s, k ≤ F a) (hsum : ∑ a ∈ s, F a = s.card * k) :
    ∀ a ∈ s, F a = k := by
  intro a ha
  set E := ∑ b ∈ s.erase a, F b with hEdef
  have h1 : F a + E = s.card * k := by
    rw [hEdef, Finset.add_sum_erase s F ha, hsum]
  have h2 : (s.card - 1) * k ≤ E := by
    rw [hEdef]
    calc (s.card - 1) * k = (s.erase a).card * k := by rw [Finset.card_erase_of_mem ha]
      _ = ∑ _b ∈ s.erase a, k := (Finset.sum_const_nat (fun b _ => rfl)).symm
      _ ≤ ∑ b ∈ s.erase a, F b :=
          Finset.sum_le_sum (fun b hb => hge b (Finset.mem_erase.mp hb).2)
  have h4 : 1 ≤ s.card := Finset.card_pos.mpr ⟨a, ha⟩
  have h5 : (s.card - 1) * k = s.card * k - k := by rw [Nat.sub_mul, one_mul]
  have h6 : k ≤ s.card * k := by simpa using Nat.mul_le_mul_right k h4
  have h7 : s.card * k - E ≤ s.card * k - (s.card - 1) * k := Nat.sub_le_sub_left h2 _
  rw [h5, Nat.sub_sub_self h6] at h7
  have h8 : F a = s.card * k - E := Nat.eq_sub_of_add_eq h1
  have := hge a ha
  omega

end Generic

/-! ## Part B: the colour-`0` graph at a root -/

section Graph

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The two neighbourhood spellings agree. -/
theorem nbrC_eq_nbr (G : EdgeCol V 4) (i : V) (a : Fin 4) : nbrC G i a = nbr G i a := rfl

/-- Membership in a colour class is symmetric. -/
theorem mem_nbrC_comm (G : EdgeCol V 4) (c : Fin 4) (p z : V) :
    p ∈ nbrC G z c ↔ z ∈ nbrC G p c := by
  rw [mem_nbrC, mem_nbrC]
  constructor
  · rintro ⟨hpz, hc⟩
    exact ⟨Ne.symm hpz, by rw [G.symm p z]; exact hc⟩
  · rintro ⟨hzp, hc⟩
    exact ⟨Ne.symm hzp, by rw [G.symm z p]; exact hc⟩

/-- A colour-`c` edge has no common colour-`c` neighbour at its ends. -/
theorem inter_nbrC_eq_empty_of_col (G : EdgeCol V 4) (hT : TriangleFree G) {u v : V}
    (huv : u ≠ v) (hc : G.col u v = 0) : nbrC G u 0 ∩ nbrC G v 0 = ∅ := by
  rw [Finset.eq_empty_iff_forall_notMem]
  rintro z hz
  obtain ⟨hz1, hz2⟩ := Finset.mem_inter.mp hz
  obtain ⟨hzu, hcu⟩ := mem_nbrC.mp hz1
  obtain ⟨hzv, hcv⟩ := mem_nbrC.mp hz2
  exact hT u v z huv (Ne.symm hzv) (Ne.symm hzu) ⟨by rw [hc, hcu], by rw [hcu, hcv]⟩

/-- Hence a positive codegree forces the connecting edge to avoid colour `0`. -/
theorem col_ne_zero_of_inter_pos (G : EdgeCol V 4) (hT : TriangleFree G) {u v : V}
    (huv : u ≠ v) (hpos : 0 < (nbrC G u 0 ∩ nbrC G v 0).card) : G.col u v ≠ 0 := by
  intro hc
  rw [inter_nbrC_eq_empty_of_col G hT huv hc] at hpos
  simp at hpos

/-- Membership in a colour class is symmetric, in the orientation "`p` in the
class of `z` iff `z` in the class of `p`". -/
theorem mem_nbrC_comm' (G : EdgeCol V 4) (c : Fin 4) (z p : V) :
    p ∈ nbrC G z c ↔ z ∈ nbrC G p c := (mem_nbrC_comm G c z p).symm

/-- A colour class misses its centre. -/
theorem notMem_nbrC_self (G : EdgeCol V 4) (i : V) (c : Fin 4) : i ∉ nbrC G i c :=
  fun h => (mem_nbrC.mp h).1 rfl

/-- A `0`-neighbour of an arm point is the root or lies outside the arm. -/
theorem arm_nbr_subset (G : EdgeCol V 4) (hT : TriangleFree G) {r a p : V}
    (ha : a ∈ nbrC G r 0) (hp : p ∈ nbrC G a 0) :
    p = r ∨ (p ≠ r ∧ p ∉ nbrC G r 0) := by
  by_cases hpr : p = r
  · exact Or.inl hpr
  refine Or.inr ⟨hpr, ?_⟩
  intro hpA
  have hpa : p ≠ a := (mem_nbrC.mp hp).1
  have hcol : G.col a p ≠ 0 := nbrC_indep G hT r 0 ha hpA (Ne.symm hpa)
  exact hcol (mem_nbrC.mp hp).2

/-- **Lemma 2's set inclusion.**  For an arm point `p` over the outside vertex
`x`, the class of `p` lies in `{r,x}` together with the residual set `R`. -/
theorem nbrC_subset_gap (G : EdgeCol V 4) (hT : TriangleFree G) {r x p : V}
    (hpA : p ∈ nbrC G r 0) (hpX : p ∈ nbrC G x 0) :
    nbrC G p 0 ⊆
      ({r, x} : Finset V) ∪ (Finset.univ \ (nbrC G r 0 ∪ nbrC G x 0 ∪ {r, x})) := by
  intro z hz
  have hzp : z ≠ p := (mem_nbrC.mp hz).1
  have hcol : G.col p z = 0 := (mem_nbrC.mp hz).2
  have hpx : p ≠ x := (mem_nbrC.mp hpX).1
  by_cases hzr : z = r
  · rw [hzr]; exact Finset.mem_union_left _ (by simp)
  by_cases hzx : z = x
  · rw [hzx]; exact Finset.mem_union_left _ (by simp)
  have hzX : G.col p x = 0 := by rw [G.symm p x]; exact (mem_nbrC.mp hpX).2
  have hznotA : z ∉ nbrC G r 0 := by
    intro hzA
    exact (nbrC_indep G hT r 0 hpA hzA (Ne.symm hzp)) hcol
  have hznotX : z ∉ nbrC G x 0 := by
    intro hzX'
    have hcz : G.col x z = 0 := (mem_nbrC.mp hzX').2
    exact hT p x z hpx (Ne.symm hzx) (Ne.symm hzp)
      ⟨by rw [hzX, hcol], by rw [hcol, hcz]⟩
  refine Finset.mem_union_right _ (Finset.mem_sdiff.mpr ⟨Finset.mem_univ _, ?_⟩)
  intro hmem
  rcases Finset.mem_union.mp hmem with h1 | h1
  · rcases Finset.mem_union.mp h1 with h2 | h2
    · exact hznotA h2
    · exact hznotX h2
  · rcases Finset.mem_insert.mp h1 with h | h
    · exact hzr h
    · exact hzx (Finset.mem_singleton.mp h)

/-- **The universal pair, lower bound.**  `3 d_0(x) <= C + 8` in the notation of
Lemma 2 (`C` is the number of (residual vertex, pair of `P`) incidences). -/
theorem rx_lower (G : EdgeCol V 4) (hT : TriangleFree G) (hV : Fintype.card V = 58)
    {r x : V} (hxr : x ≠ r) (hxA : x ∉ nbrC G r 0)
    (hA15 : (nbrC G r 0).card = 15)
    (hP5 : (nbrC G x 0 ∩ nbrC G r 0).card = 5)
    (hPdeg : ∀ p ∈ nbrC G x 0 ∩ nbrC G r 0, deg G p 0 = 15) :
    3 * deg G x 0
      ≤ (∑ q ∈ (nbrC G x 0 ∩ nbrC G r 0).powersetCard 2,
          ((Finset.univ \ (nbrC G r 0 ∪ nbrC G x 0 ∪ {r, x})).filter
            (fun z => ∀ p ∈ q, p ∈ nbrC G z 0)).card) + 8 := by
  classical
  set P : Finset V := nbrC G x 0 ∩ nbrC G r 0 with hPdef
  set R : Finset V := Finset.univ \ (nbrC G r 0 ∪ nbrC G x 0 ∪ {r, x}) with hRdef
  have hxr' : r ≠ x := Ne.symm hxr
  have hrA : r ∉ nbrC G r 0 := notMem_nbrC_self G r 0
  have hxNx : x ∉ nbrC G x 0 := notMem_nbrC_self G x 0
  have hrx0 : G.col r x ≠ 0 := by
    intro hc
    exact hxA (mem_nbrC.mpr ⟨hxr, hc⟩)
  have hrNx : r ∉ nbrC G x 0 := by
    intro h
    exact hrx0 (by rw [G.symm r x]; exact (mem_nbrC.mp h).2)
  -- sizes
  have hAx : (nbrC G r 0 ∪ nbrC G x 0).card = deg G x 0 + 10 := by
    have h1 := Finset.card_union_add_card_inter (nbrC G r 0) (nbrC G x 0)
    rw [hA15, card_nbrC] at h1
    have h2 : (nbrC G r 0 ∩ nbrC G x 0).card = 5 := by
      rw [Finset.inter_comm]; exact hP5
    omega
  have hdj : Disjoint (nbrC G r 0 ∪ nbrC G x 0) ({r, x} : Finset V) := by
    rw [Finset.disjoint_left]
    intro z hz hz2
    rcases Finset.mem_union.mp hz with hzA | hzX
    · rcases Finset.mem_insert.mp hz2 with h | h
      · rw [h] at hzA; exact hrA hzA
      · rw [Finset.mem_singleton] at h; rw [h] at hzA; exact hxA hzA
    · rcases Finset.mem_insert.mp hz2 with h | h
      · rw [h] at hzX; exact hrNx hzX
      · rw [Finset.mem_singleton] at h; rw [h] at hzX; exact hxNx hzX
  have hbig : (nbrC G r 0 ∪ nbrC G x 0 ∪ {r, x} : Finset V).card = deg G x 0 + 12 := by
    rw [Finset.card_union_of_disjoint hdj, hAx, Finset.card_pair hxr']
  have hdle : deg G x 0 + 12 ≤ 58 := by
    rw [← hbig]
    calc (nbrC G r 0 ∪ nbrC G x 0 ∪ {r, x} : Finset V).card
        ≤ Finset.univ.card := Finset.card_le_card (Finset.subset_univ _)
      _ = 58 := by rw [Finset.card_univ, hV]
  have hRcard : R.card + deg G x 0 = 46 := by
    have h1 : R.card = 58 - (nbrC G r 0 ∪ nbrC G x 0 ∪ {r, x} : Finset V).card := by
      rw [hRdef, Finset.card_sdiff, Finset.inter_univ, Finset.card_univ, hV]
    rw [h1, hbig]
    omega
  -- each `p in P` has 13 class points in `R`
  have hstep2 : ∀ p ∈ P, (R.filter (fun z => p ∈ nbrC G z 0)).card = 13 := by
    intro p hp
    obtain ⟨hpX, hpA⟩ := Finset.mem_inter.mp hp
    have hfil : (R.filter (fun z => p ∈ nbrC G z 0)) = nbrC G p 0 ∩ R := by
      ext z
      rw [Finset.mem_filter, Finset.mem_inter, mem_nbrC_comm]
      tauto
    rw [hfil]
    have hsub := nbrC_subset_gap G hT hpA hpX
    have hrp : r ∈ nbrC G p 0 := (mem_nbrC_comm G 0 r p).mpr hpA
    have hxp : x ∈ nbrC G p 0 := (mem_nbrC_comm G 0 x p).mpr hpX
    have hsub2 : ({r, x} : Finset V) ⊆ nbrC G p 0 := by
      intro z hz
      rcases Finset.mem_insert.mp hz with h | h
      · rw [h]; exact hrp
      · rw [Finset.mem_singleton.mp h]; exact hxp
    have hun : (nbrC G p 0 ∩ ({r, x} : Finset V)) ∪ (nbrC G p 0 ∩ R) = nbrC G p 0 := by
      rw [← Finset.inter_union_distrib_left]
      exact Finset.inter_eq_left.mpr hsub
    have hdj2 : Disjoint (nbrC G p 0 ∩ ({r, x} : Finset V)) (nbrC G p 0 ∩ R) := by
      rw [Finset.disjoint_left]
      intro z hz1 hz2
      have hzrx : z ∈ ({r, x} : Finset V) := (Finset.mem_inter.mp hz1).2
      have hzR : z ∈ R := (Finset.mem_inter.mp hz2).2
      have hnot : z ∉ (nbrC G r 0 ∪ nbrC G x 0 ∪ {r, x} : Finset V) :=
        (Finset.mem_sdiff.mp hzR).2
      exact hnot (Finset.mem_union_right _ hzrx)
    have hcard_rx : (nbrC G p 0 ∩ ({r, x} : Finset V)).card = 2 := by
      rw [Finset.inter_comm, Finset.inter_eq_left.mpr hsub2, Finset.card_pair hxr']
    have hsum := Finset.card_union_of_disjoint hdj2
    rw [hun, hcard_rx, card_nbrC, hPdeg p hp] at hsum
    omega
  -- the incidence total is 65
  have hT65 : ∑ z ∈ R, (P.filter (fun p => p ∈ nbrC G z 0)).card = 65 := by
    have h1 : ∑ z ∈ R, (P.filter (fun p => p ∈ nbrC G z 0)).card
        = ∑ p ∈ P, (R.filter (fun z => p ∈ nbrC G z 0)).card :=
      (sum_card_filter_comm (fun z => nbrC G z 0) P R).symm
    rw [h1]
    have h2 : ∑ p ∈ P, (R.filter (fun z => p ∈ nbrC G z 0)).card = ∑ _p ∈ P, 13 :=
      Finset.sum_congr rfl (fun p hp => hstep2 p hp)
    rw [h2, Finset.sum_const_nat (fun p _ => rfl), hP5]
  -- the engine
  have heng := collision_engine (fun z => nbrC G z (0 : Fin 4)) P R
  rw [hT65] at heng
  omega

end Graph

/-! ## Part C: splitting a set by `B u R` -/

section Split

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- **The `B u R` split.**  A set contained in `B u R`, with `B` inside it and
`B` disjoint from `R`, splits: its size is its `R`-part plus `|B|`. -/
theorem card_inter_union (T B R : Finset V) (hsub : T ⊆ B ∪ R) (hB : B ⊆ T)
    (hdisj : Disjoint B R) : (T ∩ R).card + B.card = T.card := by
  have hun : (T ∩ B) ∪ (T ∩ R) = T := by
    rw [← Finset.inter_union_distrib_left]
    exact Finset.inter_eq_left.mpr hsub
  have hdj : Disjoint (T ∩ B) (T ∩ R) := by
    rw [Finset.disjoint_left]
    intro z hz1 hz2
    exact Finset.disjoint_left.mp hdisj (Finset.mem_inter.mp hz1).2 (Finset.mem_inter.mp hz2).2
  have h1 := Finset.card_union_of_disjoint hdj
  rw [hun] at h1
  have h2 : T ∩ B = B := Finset.inter_eq_right.mpr hB
  rw [h2] at h1
  omega

/-- The `R`-filter of a single vertex is its class intersected with `R`. -/
theorem filter_single_eq_inter (R : Finset V) (N : V → Finset V)
    (hN : ∀ z p : V, p ∈ N z ↔ z ∈ N p) (s : V) :
    (R.filter (fun z => s ∈ N z)) = N s ∩ R := by
  ext z
  rw [Finset.mem_filter, Finset.mem_inter, hN z s]
  tauto

/-- The `R`-filter of a pair is the intersection of its two classes, met `R`. -/
theorem filter_pair_eq_inter (R : Finset V) (N : V → Finset V)
    (hN : ∀ z p : V, p ∈ N z ↔ z ∈ N p) (s s' : V) :
    (R.filter (fun z => ∀ p ∈ ({s, s'} : Finset V), p ∈ N z)) = (N s ∩ N s') ∩ R := by
  rw [filter_pair_eq]
  ext z
  rw [Finset.mem_filter, Finset.mem_inter, Finset.mem_inter]
  constructor
  · rintro ⟨hzR, h1, h2⟩
    exact ⟨⟨(hN z s).mp h1, (hN z s').mp h2⟩, hzR⟩
  · rintro ⟨⟨h1, h2⟩, hzR⟩
    exact ⟨hzR, (hN z s).mpr h1, (hN z s').mpr h2⟩

/-- **The pair bound at `(r,x)`.**  If every pair inside `P = N_0(x) cap N_0(r)`
has codegree at most `K`, then the collision count at `(r,x)` is at most
`10 (K-2)`. -/
theorem rx_pair_bound (G : EdgeCol V 4)
    {r x : V} (hxr : x ≠ r) (hxA : x ∉ nbrC G r 0)
    (hP5 : (nbrC G x 0 ∩ nbrC G r 0).card = 5) (K : ℕ)
    (hK : ∀ u ∈ nbrC G x 0 ∩ nbrC G r 0, ∀ v ∈ nbrC G x 0 ∩ nbrC G r 0, u ≠ v →
      (nbrC G u 0 ∩ nbrC G v 0).card ≤ K) :
    (∑ q ∈ (nbrC G x 0 ∩ nbrC G r 0).powersetCard 2,
        ((Finset.univ \ (nbrC G r 0 ∪ nbrC G x 0 ∪ {r, x})).filter
          (fun z => ∀ p ∈ q, p ∈ nbrC G z 0)).card) ≤ 10 * (K - 2) := by
  classical
  set P : Finset V := nbrC G x 0 ∩ nbrC G r 0 with hPdef
  set R : Finset V := Finset.univ \ (nbrC G r 0 ∪ nbrC G x 0 ∪ {r, x}) with hRdef
  have hxr' : r ≠ x := Ne.symm hxr
  have hrN : r ∉ nbrC G x 0 := by
    intro h
    have hcol : G.col r x = 0 := by rw [G.symm r x]; exact (mem_nbrC.mp h).2
    exact hxA (mem_nbrC.mpr ⟨hxr, hcol⟩)
  have hxN : x ∉ nbrC G r 0 := hxA
  have hdisj : Disjoint ({r, x} : Finset V) R := by
    rw [Finset.disjoint_left]
    intro z hz hzR
    exact (Finset.mem_sdiff.mp hzR).2 (Finset.mem_union_right _ hz)
  have hterm : ∀ q ∈ P.powersetCard 2,
      (R.filter (fun z => ∀ p ∈ q, p ∈ nbrC G z 0)).card ≤ K - 2 := by
    intro q hq
    obtain ⟨hqP, hq2⟩ := Finset.mem_powersetCard.mp hq
    obtain ⟨s, s', hss', hqeq⟩ := Finset.card_eq_two.mp hq2
    have hsP : s ∈ P := hqP (by rw [hqeq]; exact Finset.mem_insert_self _ _)
    have hs'P : s' ∈ P := hqP (by rw [hqeq]; exact Finset.mem_insert_of_mem (Finset.mem_singleton_self _))
    have hsX : s ∈ nbrC G x 0 := (Finset.mem_inter.mp (by rw [← hPdef]; exact hsP)).1
    have hsA : s ∈ nbrC G r 0 := (Finset.mem_inter.mp (by rw [← hPdef]; exact hsP)).2
    have hs'X : s' ∈ nbrC G x 0 := (Finset.mem_inter.mp (by rw [← hPdef]; exact hs'P)).1
    have hs'A : s' ∈ nbrC G r 0 := (Finset.mem_inter.mp (by rw [← hPdef]; exact hs'P)).2
    have hrS : r ∈ nbrC G s 0 ∩ nbrC G s' 0 :=
      Finset.mem_inter.mpr ⟨(mem_nbrC_comm G 0 r s).mpr hsA, (mem_nbrC_comm G 0 r s').mpr hs'A⟩
    have hxS : x ∈ nbrC G s 0 ∩ nbrC G s' 0 :=
      Finset.mem_inter.mpr ⟨(mem_nbrC_comm G 0 x s).mpr hsX, (mem_nbrC_comm G 0 x s').mpr hs'X⟩
    have hsub : ({r, x} : Finset V) ⊆ nbrC G s 0 ∩ nbrC G s' 0 := by
      intro z hz
      rcases Finset.mem_insert.mp hz with h | h
      · rw [h]; exact hrS
      · rw [Finset.mem_singleton.mp h]; exact hxS
    have hfil : R.filter (fun z => ∀ p ∈ q, p ∈ nbrC G z 0)
        = R.filter (fun z => ∀ p ∈ ({s, s'} : Finset V), p ∈ nbrC G z 0) := by
      apply Finset.filter_congr
      intro z _
      rw [hqeq]
    rw [hfil]
    have hmain := pair_filter_le (N := fun z => nbrC G z 0)
      (mem_nbrC_comm' G 0) R ({r, x} : Finset V) hsub hdisj K
      (hK s hsP s' hs'P hss')
    rwa [Finset.card_pair hxr'] at hmain
  calc ∑ q ∈ P.powersetCard 2, (R.filter (fun z => ∀ p ∈ q, p ∈ nbrC G z 0)).card
      ≤ ∑ q ∈ P.powersetCard 2, (K - 2) := Finset.sum_le_sum hterm
    _ = (P.powersetCard 2).card * (K - 2) := Finset.sum_const_nat (fun q _ => rfl)
    _ = 10 * (K - 2) := by
        have hc : Nat.choose 5 2 = 10 := by decide
        rw [show (P.powersetCard 2).card = Nat.choose 5 2 from by
          rw [Finset.card_powersetCard, hP5]]
        rw [hc]

/-- **The universal pair `(r,x)`.**  Under the branch data, `3 d_0(x) + 12 <= 10 K`
where `K` bounds the codegree of every pair inside `N_0(x) cap N_0(r)`. -/
theorem rx_bound (G : EdgeCol V 4) (hT : TriangleFree G) (hV : Fintype.card V = 58)
    {r x : V} (hxr : x ≠ r) (hxA : x ∉ nbrC G r 0)
    (hA15 : (nbrC G r 0).card = 15)
    (hP5 : (nbrC G x 0 ∩ nbrC G r 0).card = 5)
    (hPdeg : ∀ p ∈ nbrC G x 0 ∩ nbrC G r 0, deg G p 0 = 15)
    (K : ℕ) (hK2 : 2 ≤ K)
    (hK : ∀ u ∈ nbrC G x 0 ∩ nbrC G r 0, ∀ v ∈ nbrC G x 0 ∩ nbrC G r 0, u ≠ v →
      (nbrC G u 0 ∩ nbrC G v 0).card ≤ K) :
    3 * deg G x 0 + 12 ≤ 10 * K := by
  have h1 := rx_lower G hT hV hxr hxA hA15 hP5 hPdeg
  have h2 := rx_pair_bound G hxr hxA hP5 K hK
  omega

end Split

/-! ## Part D: rigidity at a codegree-`6` pair (Lemma 4) -/

section Rigid

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- **Lemma 4 (rigidity).**  If every colour-`0` degree is at least `15`, `u ≠ v`
have codegree exactly `6` and `6` bounds every codegree, then `d_0 u = d_0 v = 15`,
every common neighbour of `u,v` has `d_0 = 15`, and every pair of common
neighbours has codegree exactly `6`. -/
theorem rigid_six (G : EdgeCol V 4) (hT : TriangleFree G) (hV : Fintype.card V = 58)
    (hcrit : ∀ z : V, 15 ≤ deg G z 0)
    {u v : V} (huv : u ≠ v) (hS6 : (nbrC G u 0 ∩ nbrC G v 0).card = 6)
    (h6 : ∀ p q : V, p ≠ q → (nbrC G p 0 ∩ nbrC G q 0).card ≤ 6) :
    deg G u 0 = 15 ∧ deg G v 0 = 15 ∧
      (∀ s ∈ nbrC G u 0 ∩ nbrC G v 0, deg G s 0 = 15) ∧
      (∀ s ∈ nbrC G u 0 ∩ nbrC G v 0, ∀ s' ∈ nbrC G u 0 ∩ nbrC G v 0, s ≠ s' →
        (nbrC G s 0 ∩ nbrC G s' 0).card = 6) := by
  classical
  set S : Finset V := nbrC G u 0 ∩ nbrC G v 0 with hSdef
  set R : Finset V := Finset.univ \ (nbrC G u 0 ∪ nbrC G v 0 ∪ {u, v}) with hRdef
  have hScard : S.card = 6 := hS6
  -- the connecting edge is not of colour 0
  have hadj : G.col u v ≠ 0 := by
    intro hc
    have hE : nbrC G u 0 ∩ nbrC G v 0 = ∅ := inter_nbrC_eq_empty_of_col G hT huv hc
    rw [hSdef, hE] at hS6
    simp at hS6
  have huNv : u ∉ nbrC G v 0 := by
    intro h
    exact hadj (by rw [G.symm u v]; exact (mem_nbrC.mp h).2)
  have hvNu : v ∉ nbrC G u 0 := by
    intro h
    exact hadj (mem_nbrC.mp h).2
  have huNu : u ∉ nbrC G u 0 := notMem_nbrC_self G u 0
  have hvNv : v ∉ nbrC G v 0 := notMem_nbrC_self G v 0
  -- sizes
  have hU : (nbrC G u 0 ∪ nbrC G v 0).card + 6 = deg G u 0 + deg G v 0 := by
    have h1 := Finset.card_union_add_card_inter (nbrC G u 0) (nbrC G v 0)
    rw [card_nbrC, card_nbrC] at h1
    have h2 : (nbrC G u 0 ∩ nbrC G v 0).card = 6 := hS6
    omega
  have hdjuv : Disjoint (nbrC G u 0 ∪ nbrC G v 0) ({u, v} : Finset V) := by
    rw [Finset.disjoint_left]
    intro z hz hz2
    rcases Finset.mem_union.mp hz with h | h
    · rcases Finset.mem_insert.mp hz2 with h2 | h2
      · rw [h2] at h; exact huNu h
      · rw [Finset.mem_singleton.mp h2] at h; exact hvNu h
    · rcases Finset.mem_insert.mp hz2 with h2 | h2
      · rw [h2] at h; exact huNv h
      · rw [Finset.mem_singleton.mp h2] at h; exact hvNv h
  have hXle : (nbrC G u 0 ∪ nbrC G v 0 ∪ {u, v} : Finset V).card ≤ 58 := by
    have h := Finset.card_le_univ (nbrC G u 0 ∪ nbrC G v 0 ∪ {u, v} : Finset V)
    rwa [hV] at h
  have hbig : (nbrC G u 0 ∪ nbrC G v 0 ∪ {u, v} : Finset V).card + 4 = deg G u 0 + deg G v 0 := by
    rw [Finset.card_union_of_disjoint hdjuv, Finset.card_pair huv]
    omega
  have hRcard : R.card + deg G u 0 + deg G v 0 = 62 := by
    have h1 : R.card = 58 - (nbrC G u 0 ∪ nbrC G v 0 ∪ {u, v} : Finset V).card := by
      rw [hRdef, Finset.card_sdiff, Finset.inter_univ, Finset.card_univ, hV]
    have hdu := hcrit u
    have hdv := hcrit v
    omega
  have hRle : R.card ≤ 32 := by
    have hdu := hcrit u
    have hdv := hcrit v
    omega
  -- a common neighbour's class lies in `{u,v} u R`
  have hgap : ∀ s ∈ S, nbrC G s 0 ⊆ ({u, v} : Finset V) ∪ R := by
    intro s hs z hz
    rw [hSdef] at hs
    obtain ⟨hsu, hsv⟩ := Finset.mem_inter.mp hs
    have hsu' : G.col u s = 0 := (mem_nbrC.mp hsu).2
    have hsv' : G.col v s = 0 := (mem_nbrC.mp hsv).2
    have hsu_ne : s ≠ u := (mem_nbrC.mp hsu).1
    have hsv_ne : s ≠ v := (mem_nbrC.mp hsv).1
    have hzs : z ≠ s := (mem_nbrC.mp hz).1
    have hcz : G.col s z = 0 := (mem_nbrC.mp hz).2
    by_cases hzu : z = u
    · rw [hzu]; exact Finset.mem_union_left _ (by simp)
    by_cases hzv : z = v
    · rw [hzv]; exact Finset.mem_union_left _ (by simp)
    refine Finset.mem_union_right _ (Finset.mem_sdiff.mpr ⟨Finset.mem_univ _, ?_⟩)
    intro hmem
    rcases Finset.mem_union.mp hmem with h1 | h1
    · rcases Finset.mem_union.mp h1 with h2 | h2
      · have hczu : G.col u z = 0 := (mem_nbrC.mp h2).2
        exact hT u s z (Ne.symm hsu_ne) (Ne.symm hzs) (Ne.symm hzu)
          ⟨by rw [hsu', hczu], by rw [hczu, hcz]⟩
      · have hczv : G.col v z = 0 := (mem_nbrC.mp h2).2
        exact hT v s z (Ne.symm hsv_ne) (Ne.symm hzs) (Ne.symm hzv)
          ⟨by rw [hsv', hczv], by rw [hczv, hcz]⟩
    · rcases Finset.mem_insert.mp h1 with h2 | h2
      · exact hzu h2
      · exact hzv (Finset.mem_singleton.mp h2)
  have hdisjB : Disjoint ({u, v} : Finset V) R := by
    rw [Finset.disjoint_left]
    intro z hz hzR
    exact (Finset.mem_sdiff.mp hzR).2 (Finset.mem_union_right _ hz)
  -- each common neighbour has 13 class points in `R`
  have hstep : ∀ s ∈ S, (R.filter (fun z => s ∈ nbrC G z 0)).card = deg G s 0 - 2 := by
    intro s hs
    have hsub := hgap s hs
    rw [hSdef] at hs
    obtain ⟨hsu, hsv⟩ := Finset.mem_inter.mp hs
    have huS : u ∈ nbrC G s 0 := (mem_nbrC_comm' G 0 u s).mp hsu
    have hvS : v ∈ nbrC G s 0 := (mem_nbrC_comm' G 0 v s).mp hsv
    have hB : ({u, v} : Finset V) ⊆ nbrC G s 0 := by
      intro z hz
      rcases Finset.mem_insert.mp hz with h | h
      · rw [h]; exact huS
      · rw [Finset.mem_singleton.mp h]; exact hvS
    rw [filter_single_eq_inter R (fun z => nbrC G z 0) (mem_nbrC_comm' G 0) s]
    have h := card_inter_union (nbrC G s 0) ({u, v} : Finset V) R hsub hB hdisjB
    rw [Finset.card_pair huv, card_nbrC] at h
    omega
  -- T >= 78
  have hTge : 78 ≤ ∑ z ∈ R, (S.filter (fun s => s ∈ nbrC G z 0)).card := by
    have h13 : ∀ s ∈ S, 13 ≤ (R.filter (fun z => s ∈ nbrC G z 0)).card := by
      intro s hs
      rw [hstep s hs]
      have := hcrit s
      omega
    have h1 : S.card * 13 ≤ ∑ s ∈ S, (R.filter (fun z => s ∈ nbrC G z 0)).card := by
      calc S.card * 13 = ∑ _s ∈ S, 13 := (Finset.sum_const_nat (fun s _ => rfl)).symm
        _ ≤ _ := Finset.sum_le_sum h13
    rw [hScard] at h1
    rw [← sum_card_filter_comm (fun z => nbrC G z 0) S R]
    omega
  -- each pair of common neighbours contributes at most 4
  have hterm4 : ∀ q ∈ S.powersetCard 2,
      (R.filter (fun z => ∀ s ∈ q, s ∈ nbrC G z 0)).card ≤ 4 := by
    intro q hq
    obtain ⟨hqS, hq2⟩ := Finset.mem_powersetCard.mp hq
    obtain ⟨s1, s2, hs12, hqeq⟩ := Finset.card_eq_two.mp hq2
    have hs1S : s1 ∈ S := hqS (by rw [hqeq]; exact Finset.mem_insert_self _ _)
    have hs2S : s2 ∈ S := hqS (by rw [hqeq]; exact Finset.mem_insert_of_mem (Finset.mem_singleton_self _))
    have hsub : ({u, v} : Finset V) ⊆ nbrC G s1 0 ∩ nbrC G s2 0 := by
      have h1 : s1 ∈ nbrC G u 0 ∩ nbrC G v 0 := by rw [← hSdef]; exact hs1S
      have h2 : s2 ∈ nbrC G u 0 ∩ nbrC G v 0 := by rw [← hSdef]; exact hs2S
      have hu1 : u ∈ nbrC G s1 0 := (mem_nbrC_comm' G 0 u s1).mp (Finset.mem_inter.mp h1).1
      have hv1 : v ∈ nbrC G s1 0 := (mem_nbrC_comm' G 0 v s1).mp (Finset.mem_inter.mp h1).2
      have hu2 : u ∈ nbrC G s2 0 := (mem_nbrC_comm' G 0 u s2).mp (Finset.mem_inter.mp h2).1
      have hv2 : v ∈ nbrC G s2 0 := (mem_nbrC_comm' G 0 v s2).mp (Finset.mem_inter.mp h2).2
      intro z hz
      rcases Finset.mem_insert.mp hz with h | h
      · rw [h]; exact Finset.mem_inter.mpr ⟨hu1, hu2⟩
      · rw [Finset.mem_singleton.mp h]; exact Finset.mem_inter.mpr ⟨hv1, hv2⟩
    have hfil : R.filter (fun z => ∀ s ∈ q, s ∈ nbrC G z 0)
        = R.filter (fun z => ∀ s ∈ ({s1, s2} : Finset V), s ∈ nbrC G z 0) := by
      apply Finset.filter_congr
      intro z _
      rw [hqeq]
    rw [hfil]
    have hmain := pair_filter_le (N := fun z => nbrC G z 0) (mem_nbrC_comm' G 0) R
      ({u, v} : Finset V) hsub hdisjB 6 (h6 s1 s2 hs12)
    rwa [Finset.card_pair huv] at hmain
  have hCle : ∑ z ∈ R, (S.filter (fun s => s ∈ nbrC G z 0)).card.choose 2 ≤ 60 := by
    rw [sum_choose_two_comm (fun z => nbrC G z 0) S R]
    calc ∑ q ∈ S.powersetCard 2, (R.filter (fun z => ∀ s ∈ q, s ∈ nbrC G z 0)).card
        ≤ ∑ q ∈ S.powersetCard 2, 4 := Finset.sum_le_sum hterm4
      _ = (S.powersetCard 2).card * 4 := Finset.sum_const_nat (fun q _ => rfl)
      _ = 60 := by
          rw [show (S.powersetCard 2).card = Nat.choose 6 2 from by
            rw [Finset.card_powersetCard, hScard]]
          decide
  -- the engine
  have heng := collision_engine (fun z => nbrC G z 0) S R
  have hC2 : (∑ q ∈ S.powersetCard 2, (R.filter (fun z => ∀ s ∈ q, s ∈ nbrC G z 0)).card) ≤ 60 := by
    rw [← sum_choose_two_comm (fun z => nbrC G z 0) S R]
    exact hCle
  have hR32 : R.card = 32 := by omega
  have hduv : deg G u 0 = 15 ∧ deg G v 0 = 15 := by
    have hdu := hcrit u
    have hdv := hcrit v
    omega
  have hT78 : ∑ z ∈ R, (S.filter (fun s => s ∈ nbrC G z 0)).card = 78 := by omega
  -- every common neighbour has degree 15
  have hdeg15 : ∀ s ∈ S, deg G s 0 = 15 := by
    have hge13 : ∀ s ∈ S, 13 ≤ (R.filter (fun z => s ∈ nbrC G z 0)).card := by
      intro s hs
      rw [hstep s hs]
      have := hcrit s
      omega
    have hsum : ∑ s ∈ S, (R.filter (fun z => s ∈ nbrC G z 0)).card = 78 :=
      (sum_card_filter_comm (fun z => nbrC G z 0) S R).trans hT78
    have hkey : ∑ s ∈ S, (R.filter (fun z => s ∈ nbrC G z 0)).card = S.card * 13 := by
      rw [hsum, hScard]
    have hall := all_eq_of_card_mul_eq_sum (s := S)
      (F := fun s => (R.filter (fun z => s ∈ nbrC G z 0)).card) (k := 13) hge13 hkey
    intro s hs
    have h1 : (R.filter (fun z => s ∈ nbrC G z 0)).card = 13 := hall s hs
    rw [hstep s hs] at h1
    have := hcrit s
    omega
  have hC2eq : (∑ q ∈ S.powersetCard 2, (R.filter (fun z => ∀ s ∈ q, s ∈ nbrC G z 0)).card) = 60 := by
    omega
  have hC60 : ∑ z ∈ R, (S.filter (fun s => s ∈ nbrC G z 0)).card.choose 2 = 60 := by
    rw [sum_choose_two_comm (fun z => nbrC G z 0) S R]
    exact hC2eq
  refine ⟨hduv.1, hduv.2, hdeg15, ?_⟩
  intro s hs s' hs' hss'
  have hq : ({s, s'} : Finset V) ∈ S.powersetCard 2 := by
    rw [Finset.mem_powersetCard]
    exact ⟨by
      intro z hz
      rcases Finset.mem_insert.mp hz with h | h
      · rw [h]; exact hs
      · rw [Finset.mem_singleton.mp h]; exact hs', Finset.card_pair hss'⟩
  have hkey : ∑ q ∈ S.powersetCard 2,
      (R.filter (fun z => ∀ s ∈ q, s ∈ nbrC G z 0)).card = (S.powersetCard 2).card * 4 := by
    rw [← sum_choose_two_comm (fun z => nbrC G z 0) S R, hC60]
    rw [show (S.powersetCard 2).card = Nat.choose 6 2 from by
      rw [Finset.card_powersetCard, hScard]]
    decide
  have hall4 := all_eq_of_sum_eq_card_mul (s := S.powersetCard 2)
    (F := fun q => (R.filter (fun z => ∀ s ∈ q, s ∈ nbrC G z 0)).card) (k := 4) hterm4 hkey
  have h4 : (R.filter (fun z => ∀ p ∈ ({s, s'} : Finset V), p ∈ nbrC G z 0)).card = 4 := hall4 _ hq
  have hsub := hgap s hs
  have hBsub : ({u, v} : Finset V) ⊆ nbrC G s 0 ∩ nbrC G s' 0 := by
    have h1 : s ∈ nbrC G u 0 ∩ nbrC G v 0 := by rw [← hSdef]; exact hs
    have h2 : s' ∈ nbrC G u 0 ∩ nbrC G v 0 := by rw [← hSdef]; exact hs'
    have hu1 : u ∈ nbrC G s 0 := (mem_nbrC_comm' G 0 u s).mp (Finset.mem_inter.mp h1).1
    have hv1 : v ∈ nbrC G s 0 := (mem_nbrC_comm' G 0 v s).mp (Finset.mem_inter.mp h1).2
    have hu2 : u ∈ nbrC G s' 0 := (mem_nbrC_comm' G 0 u s').mp (Finset.mem_inter.mp h2).1
    have hv2 : v ∈ nbrC G s' 0 := (mem_nbrC_comm' G 0 v s').mp (Finset.mem_inter.mp h2).2
    intro z hz
    rcases Finset.mem_insert.mp hz with h | h
    · rw [h]; exact Finset.mem_inter.mpr ⟨hu1, hu2⟩
    · rw [Finset.mem_singleton.mp h]; exact Finset.mem_inter.mpr ⟨hv1, hv2⟩
  have hsplit := card_inter_union (nbrC G s 0 ∩ nbrC G s' 0) ({u, v} : Finset V) R
    (Finset.Subset.trans Finset.inter_subset_left hsub) hBsub hdisjB
  rw [Finset.card_pair huv] at hsplit
  rw [filter_pair_eq_inter R (fun z => nbrC G z 0) (mem_nbrC_comm' G 0) s s'] at h4
  omega

end Rigid

/-! ## Part E: the arm total and `M >= 7` -/

section Final

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The `42` outside vertices exist. -/
theorem exists_outside (G : EdgeCol V 4) (hV : Fintype.card V = 58)
    {r : V} (hA15 : (nbrC G r 0).card = 15) :
    ∃ x : V, x ≠ r ∧ x ∉ nbrC G r 0 := by
  have hrA : r ∉ nbrC G r 0 := notMem_nbrC_self G r 0
  have hdisj : Disjoint (nbrC G r 0) ({r} : Finset V) := by
    rw [Finset.disjoint_left]
    intro z hz hz2
    exact hrA (Finset.mem_singleton.mp hz2 ▸ hz)
  have hunion : (nbrC G r 0 ∪ {r} : Finset V).card = 16 := by
    rw [Finset.card_union_of_disjoint hdisj, hA15, Finset.card_singleton]
  have hcard : ((Finset.univ : Finset V) \ (nbrC G r 0 ∪ {r})).card = 42 := by
    rw [Finset.card_sdiff_of_subset (Finset.subset_univ _), Finset.card_univ, hV, hunion]
  have hne : ((Finset.univ : Finset V) \ (nbrC G r 0 ∪ {r})).Nonempty := by
    rw [Finset.nonempty_iff_ne_empty]
    intro h
    rw [h] at hcard
    simp at hcard
  obtain ⟨x, hx⟩ := hne
  rw [Finset.mem_sdiff] at hx
  obtain ⟨-, hx2⟩ := hx
  exact ⟨x, fun h => hx2 (Finset.mem_union_right _ (Finset.mem_singleton.mpr h)),
    fun h => hx2 (Finset.mem_union_left _ h)⟩

/-- **Theorem 2(1): the `525` identity.**  In the branch the codegrees of the
`C(15,2) = 105` arm pairs sum to `105 + 42 * C(5,2) = 525`. -/
theorem arm_pair_total (G : EdgeCol V 4) (hT : TriangleFree G) (hV : Fintype.card V = 58)
    {r : V} (hA15 : (nbrC G r 0).card = 15)
    (hm5 : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → (nbrC G x 0 ∩ nbrC G r 0).card = 5) :
    (∑ q ∈ (nbrC G r 0).powersetCard 2,
        ((Finset.univ : Finset V).filter (fun z => ∀ s ∈ q, s ∈ nbrC G z 0)).card) = 525 := by
  classical
  set A : Finset V := nbrC G r 0 with hAdef
  set X : Finset V := Finset.univ \ (nbrC G r 0 ∪ {r}) with hXdef
  set fx : V → ℕ := fun z => (A.filter (fun s => s ∈ nbrC G z 0)).card.choose 2 with hfxdef
  have hrA : r ∉ A := by rw [hAdef]; exact notMem_nbrC_self G r 0
  have hdisjAX : Disjoint A X := by
    rw [hXdef, Finset.disjoint_left]
    intro z hz hz2
    exact (Finset.mem_sdiff.mp hz2).2 (Finset.mem_union_left _ (by rw [← hAdef]; exact hz))
  have hcover : (Finset.univ : Finset V) = insert r (A ∪ X) := by
    ext z
    constructor
    · intro _
      by_cases hzr : z = r
      · exact Finset.mem_insert.mpr (Or.inl hzr)
      · refine Finset.mem_insert.mpr (Or.inr ?_)
        by_cases hzA : z ∈ A
        · exact Finset.mem_union_left _ hzA
        · refine Finset.mem_union_right _ (Finset.mem_sdiff.mpr ⟨Finset.mem_univ _, ?_⟩)
          intro h
          rcases Finset.mem_union.mp h with h1 | h1
          · exact hzA h1
          · exact hzr (Finset.mem_singleton.mp h1)
    · intro _; exact Finset.mem_univ _
  have hrnot : r ∉ A ∪ X := by
    intro h
    rcases Finset.mem_union.mp h with h1 | h1
    · exact hrA h1
    · exact (Finset.mem_sdiff.mp h1).2 (Finset.mem_union_right _ (Finset.mem_singleton_self r))
  have hXcard : X.card = 42 := by
    have hdisj : Disjoint (nbrC G r 0) ({r} : Finset V) := by
      rw [Finset.disjoint_left]
      intro z hz hz2
      exact hrA (Finset.mem_singleton.mp hz2 ▸ hz)
    have hunion : (nbrC G r 0 ∪ {r} : Finset V).card = 16 := by
      rw [Finset.card_union_of_disjoint hdisj, hA15, Finset.card_singleton]
    rw [hXdef, Finset.card_sdiff_of_subset (Finset.subset_univ _), Finset.card_univ, hV, hunion]
  -- the three values of the summand
  have hfr : fx r = 105 := by
    have h1 : A.filter (fun s => s ∈ nbrC G r 0) = A := by
      apply Finset.filter_true_of_mem
      intro s hs
      exact hAdef ▸ hs
    have h2 : A.card = 15 := by rw [hAdef]; exact hA15
    show (A.filter (fun s => s ∈ nbrC G r 0)).card.choose 2 = 105
    rw [h1, h2]
    decide
  have hfA : ∀ z ∈ A, fx z = 0 := by
    intro z hzA
    have hempty : A.filter (fun s => s ∈ nbrC G z 0) = ∅ := by
      rw [Finset.eq_empty_iff_forall_notMem]
      intro s hs
      obtain ⟨hsA, hsz⟩ := Finset.mem_filter.mp hs
      have hne : z ≠ s := by
        intro h
        rw [h] at hsz
        exact notMem_nbrC_self G s 0 hsz
      exact nbrC_indep G hT r 0 (hAdef ▸ hzA) (hAdef ▸ hsA) hne (mem_nbrC.mp hsz).2
    show (A.filter (fun s => s ∈ nbrC G z 0)).card.choose 2 = 0
    rw [hempty]
    simp
  have hfX : ∀ z ∈ X, fx z = 10 := by
    intro z hzX
    have hzX' := (hXdef ▸ hzX : z ∈ (Finset.univ : Finset V) \ (nbrC G r 0 ∪ {r}))
    have hzr : z ≠ r := by
      intro h
      exact (Finset.mem_sdiff.mp hzX').2 (Finset.mem_union_right _ (Finset.mem_singleton.mpr h))
    have hzout : z ∉ nbrC G r 0 := by
      intro h
      exact (Finset.mem_sdiff.mp hzX').2 (Finset.mem_union_left _ h)
    have h1 : A.filter (fun s => s ∈ nbrC G z 0) = nbrC G z 0 ∩ A := by
      ext s
      rw [Finset.mem_filter, Finset.mem_inter, and_comm]
    have h2 : (A.filter (fun s => s ∈ nbrC G z 0)).card = 5 := by
      rw [h1]
      exact hm5 z hzr hzout
    show (A.filter (fun s => s ∈ nbrC G z 0)).card.choose 2 = 10
    rw [h2]
    decide
  have hLHS : ∑ z ∈ (Finset.univ : Finset V), fx z = 525 := by
    rw [hcover, Finset.sum_insert hrnot, Finset.sum_union hdisjAX]
    have hA0 : ∑ z ∈ A, fx z = 0 := Finset.sum_eq_zero (fun z hz => hfA z hz)
    have hX10 : ∑ z ∈ X, fx z = X.card * 10 := by
      calc ∑ z ∈ X, fx z = ∑ _z ∈ X, 10 := Finset.sum_congr rfl (fun z hz => hfX z hz)
        _ = X.card * 10 := Finset.sum_const_nat (fun z _ => rfl)
    rw [hA0, hX10, hXcard, hfr]
    norm_num
  have hcomm := sum_choose_two_comm (fun z => nbrC G z (0 : Fin 4)) A (Finset.univ : Finset V)
  rw [hLHS] at hcomm
  exact hcomm.symm

/-- **The branch makes colour `0` critical everywhere** (under `(R)`). -/
theorem branch_crit (G : EdgeCol V 4) (hR : Reciprocal G) (r : V)
    (hA15 : (nbrC G r 0).card = 15)
    (hAcrit : ∀ a ∈ nbrC G r 0, deg G a 0 = 15)
    (hm5 : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → (nbrC G x 0 ∩ nbrC G r 0).card = 5) :
    ∀ z : V, 15 ≤ deg G z 0 := by
  refine uniform_branch_zero_critical G hR r ?_ ?_ ?_
  · rw [← card_nbrC, hA15]
  · intro a ha; rw [hAcrit a ha]
  · intro x hxr hxA
    refine Finset.card_pos.mp ?_
    rw [hm5 x hxr hxA]
    norm_num

/-- **The paper's `(∗)`.**  Under `(R)` every colour-`0` degree in the branch is
`15` or `16` (`branch_crit` from below, `deg_le_sixteen` from above). -/
theorem branch_deg_15_or_16 (G : EdgeCol V 4) (hT : TriangleFree G) (hR : Reciprocal G)
    (r : V) (hA15 : (nbrC G r 0).card = 15)
    (hAcrit : ∀ a ∈ nbrC G r 0, deg G a 0 = 15)
    (hm5 : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → (nbrC G x 0 ∩ nbrC G r 0).card = 5) :
    ∀ z : V, deg G z 0 = 15 ∨ deg G z 0 = 16 := by
  intro z
  have h1 := branch_crit G hR r hA15 hAcrit hm5 z
  have h2 := deg_le_sixteen G hT z 0
  omega

/-- The companion upper bound `M <= 16`: a codegree is at most one of the two
classes it sits in, and colour degrees are at most `16`. -/
theorem codeg_le_sixteen (G : EdgeCol V 4) (hT : TriangleFree G) :
    ∀ u v : V, u ≠ v → (nbrC G u 0 ∩ nbrC G v 0).card ≤ 16 := by
  intro u v _
  calc (nbrC G u 0 ∩ nbrC G v 0).card ≤ (nbrC G u 0).card :=
        Finset.card_le_card Finset.inter_subset_left
    _ = deg G u 0 := card_nbrC G u 0
    _ ≤ 16 := deg_le_sixteen G hT u 0

/-- **Corollary 3, kernel form.**  Under `(R)` the branch forces `M >= 6`; the
argument is the collision count at `(r,x)` alone, with no rigidity input. -/
theorem M_ge_six (G : EdgeCol V 4) (hT : TriangleFree G) (hV : Fintype.card V = 58)
    (hR : Reciprocal G) (r : V)
    (hA15 : (nbrC G r 0).card = 15)
    (hAcrit : ∀ a ∈ nbrC G r 0, deg G a 0 = 15)
    (hm5 : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → (nbrC G x 0 ∩ nbrC G r 0).card = 5)
    (M : ℕ) (hM : ∀ u v : V, u ≠ v → (nbrC G u 0 ∩ nbrC G v 0).card ≤ M) :
    6 ≤ M := by
  classical
  have hcrit := branch_crit G hR r hA15 hAcrit hm5
  obtain ⟨x, hxr, hxA⟩ := exists_outside G hV hA15
  have hP5 : (nbrC G x 0 ∩ nbrC G r 0).card = 5 := hm5 x hxr hxA
  have hPdeg : ∀ p ∈ nbrC G x 0 ∩ nbrC G r 0, deg G p 0 = 15 := by
    intro p hp
    exact hAcrit p (Finset.mem_inter.mp hp).2
  have hM5 : 5 ≤ M := by
    have h1 := hM r x (Ne.symm hxr)
    rw [Finset.inter_comm, hP5] at h1
    omega
  have hbound := rx_bound G hT hV hxr hxA hA15 hP5 hPdeg M (by omega)
    (fun u _ v _ huv => hM u v huv)
  have hx15 : 15 ≤ deg G x 0 := hcrit x
  omega

/-- **Lemma 5, kernel form.**  If `6` bounds every codegree then every arm pair
has codegree at most `5` (the codegree-`6` case is killed by `rigid_six`). -/
theorem arm_codeg_le_five (G : EdgeCol V 4) (hT : TriangleFree G) (hV : Fintype.card V = 58)
    (hcrit : ∀ z : V, 15 ≤ deg G z 0) (r : V)
    (hm5 : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → (nbrC G x 0 ∩ nbrC G r 0).card = 5)
    (h6 : ∀ p q : V, p ≠ q → (nbrC G p 0 ∩ nbrC G q 0).card ≤ 6) :
    ∀ a ∈ nbrC G r 0, ∀ a' ∈ nbrC G r 0, a ≠ a' →
      (nbrC G a 0 ∩ nbrC G a' 0).card ≤ 5 := by
  intro a ha a' ha' haa'
  by_contra hcon2
  push Not at hcon2
  have hcard6 : (nbrC G a 0 ∩ nbrC G a' 0).card = 6 := by
    have := h6 a a' haa'
    omega
  have hrS : r ∈ nbrC G a 0 ∩ nbrC G a' 0 :=
    Finset.mem_inter.mpr ⟨(mem_nbrC_comm G 0 r a).mpr ha, (mem_nbrC_comm G 0 r a').mpr ha'⟩
  obtain ⟨-, -, -, hkey⟩ := rigid_six G hT hV hcrit (u := a) (v := a') haa' hcard6 h6
  have herase : ((nbrC G a 0 ∩ nbrC G a' 0).erase r).card = 5 := by
    rw [Finset.card_erase_of_mem hrS, hcard6]
  obtain ⟨t, ht⟩ := Finset.card_pos.mp (by omega :
    0 < ((nbrC G a 0 ∩ nbrC G a' 0).erase r).card)
  rw [Finset.mem_erase] at ht
  obtain ⟨htr, htS⟩ := ht
  have h61 : (nbrC G r 0 ∩ nbrC G t 0).card = 6 := hkey r hrS t htS (Ne.symm htr)
  have hta : t ∈ nbrC G a 0 := (Finset.mem_inter.mp htS).1
  have htX : t ≠ r ∧ t ∉ nbrC G r 0 := by
    rcases arm_nbr_subset G hT ha hta with h | h
    · exact absurd h htr
    · exact h
  have h62 : (nbrC G t 0 ∩ nbrC G r 0).card = 5 := hm5 t htX.1 htX.2
  rw [Finset.inter_comm] at h61
  omega

/-- **Lemma 6, kernel form.**  If `6` bounds every codegree then every one of the
`105` arm pairs has codegree exactly `5` — the `525` identity forces the last
unit, so the `42` blocks `N_0(x) cap A` are *not* the blocks of a
`2-(15,5,4)` design. -/
theorem arm_all_five (G : EdgeCol V 4) (hT : TriangleFree G) (hV : Fintype.card V = 58)
    (hcrit : ∀ z : V, 15 ≤ deg G z 0) (r : V)
    (hA15 : (nbrC G r 0).card = 15)
    (hm5 : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → (nbrC G x 0 ∩ nbrC G r 0).card = 5)
    (h6 : ∀ p q : V, p ≠ q → (nbrC G p 0 ∩ nbrC G q 0).card ≤ 6) :
    ∀ a ∈ nbrC G r 0, ∀ a' ∈ nbrC G r 0, a ≠ a' →
      (nbrC G a 0 ∩ nbrC G a' 0).card = 5 := by
  classical
  have hle5 := arm_codeg_le_five G hT hV hcrit r hm5 h6
  have hle : ∀ q ∈ (nbrC G r 0).powersetCard 2,
      ((Finset.univ : Finset V).filter (fun z => ∀ s ∈ q, s ∈ nbrC G z 0)).card ≤ 5 := by
    intro q hq
    obtain ⟨hqA, hq2⟩ := Finset.mem_powersetCard.mp hq
    obtain ⟨a, a', haa', hqeq⟩ := Finset.card_eq_two.mp hq2
    have haA : a ∈ nbrC G r 0 := hqA (by rw [hqeq]; exact Finset.mem_insert_self _ _)
    have ha'A : a' ∈ nbrC G r 0 := hqA (by rw [hqeq]; exact Finset.mem_insert_of_mem (Finset.mem_singleton_self _))
    have hfil : (Finset.univ : Finset V).filter (fun z => ∀ s ∈ q, s ∈ nbrC G z 0)
        = (Finset.univ : Finset V).filter
            (fun z => ∀ s ∈ ({a, a'} : Finset V), s ∈ nbrC G z 0) := by
      apply Finset.filter_congr
      intro z _
      rw [hqeq]
    rw [hfil, filter_pair_eq_inter (Finset.univ : Finset V) (fun z => nbrC G z 0)
      (mem_nbrC_comm' G 0) a a', Finset.inter_univ]
    exact hle5 a haA a' ha'A haa'
  have htot := arm_pair_total G hT hV hA15 hm5
  have hsum : (∑ q ∈ (nbrC G r 0).powersetCard 2,
      ((Finset.univ : Finset V).filter (fun z => ∀ s ∈ q, s ∈ nbrC G z 0)).card)
      = ((nbrC G r 0).powersetCard 2).card * 5 := by
    rw [htot]
    rw [show ((nbrC G r 0).powersetCard 2).card = Nat.choose 15 2 from by
      rw [Finset.card_powersetCard, hA15]]
    decide
  have hall := all_eq_of_sum_eq_card_mul (s := (nbrC G r 0).powersetCard 2)
    (F := fun q => ((Finset.univ : Finset V).filter (fun z => ∀ s ∈ q, s ∈ nbrC G z 0)).card)
    (k := 5) hle hsum
  intro a ha a' ha' haa'
  have hq : ({a, a'} : Finset V) ∈ (nbrC G r 0).powersetCard 2 := by
    rw [Finset.mem_powersetCard]
    exact ⟨by
      intro z hz
      rcases Finset.mem_insert.mp hz with h | h
      · rw [h]; exact ha
      · rw [Finset.mem_singleton.mp h]; exact ha', Finset.card_pair haa'⟩
  have h4 := hall _ hq
  rw [filter_pair_eq_inter (Finset.univ : Finset V) (fun z => nbrC G z 0)
    (mem_nbrC_comm' G 0) a a', Finset.inter_univ] at h4
  exact h4

/-- **Theorem 1, kernel form.**  In the branch at a `(15,14,14,14)` root, with all
tickets returned, every upper bound `M` on the colour-`0` codegrees satisfies
`7 <= M`. -/
theorem M_ge_seven (G : EdgeCol V 4) (hT : TriangleFree G) (hV : Fintype.card V = 58)
    (hR : Reciprocal G) (r : V)
    (hA15 : (nbrC G r 0).card = 15)
    (hAcrit : ∀ a ∈ nbrC G r 0, deg G a 0 = 15)
    (hm5 : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → (nbrC G x 0 ∩ nbrC G r 0).card = 5)
    (M : ℕ) (hM : ∀ u v : V, u ≠ v → (nbrC G u 0 ∩ nbrC G v 0).card ≤ M) :
    7 ≤ M := by
  classical
  have hcrit := branch_crit G hR r hA15 hAcrit hm5
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

end Final

end K58
