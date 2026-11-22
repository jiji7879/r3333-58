/-
K58 supplement (swarm `smwrzh71x`, member m6, direction d4 = Target 5):
**the `2-(15,5,4)` design is not realisable at the `(15,14,14,14)` profile.**

Setting.  In the branch at a root `r` of profile `(15,14,14,14)`: `A = N_0(r)` with
`|A| = 15`, every `a in A` is `0`-critical (`d_0 a = 15`), and every outside vertex
`x` has `m x = |N_0 x cap A| = 5`.  Write `P_x = N_0 x cap A` and, for a pair
`{a,a'} ⊆ A`, `n (a,a') = #{x in X : a, a' in P_x}`.  Since `r` is a common
`0`-neighbour of every pair of arm points,

  `mu (a,a') = |N_0 a cap N_0 a'| = 1 + n (a,a')`.

So "the 42 blocks `P_x` are the blocks of a `2-(15,5,4)` design" (42 blocks of size
5, every point in 14, every pair in exactly 4) is *exactly* the statement

  `mu (a,a') = 5` for all `105` pairs `{a,a'} ⊆ A`.

What is proved here.

* `le_choose_two_add_one` : `k <= C(k,2) + 1`, the integrality refinement of the
  collision convexity `2k <= C(k,2) + 3`.
* `collision_engine_add_one` : the second engine,
  `sum_{z in R} |S cap N z| <= (pair count) + #R`.  Together with
  `K58.collision_engine` this gives the exact minimum of `sum_i C(k_i,2)` over
  integers `k_i` with a fixed sum.
* `rx_lower_refined` : at the pair `(r,x)`, `19 + d_0 x <= C_x`, against
  `3 d_0 x <= C_x + 8` (`K58.rx_lower`).
* `trace_codegree_six` : at every outside vertex with `12 <= d_0 x`, the trace
  `P_x` contains a pair of arm points whose codegree is at least `6`.
* `design_not_realisable` : the headline.  Under `(R)` no colouring in the branch
  has `mu = 5` on all `105` arm pairs; the trace system is never a `2-(15,5,4)`
  design.

Consequences.  `K58.arm_all_five` says `M = 6` forces `mu = 5` on all `105` arm
pairs, so `design_not_realisable` gives `M >= 7` (`K58.M_ge_seven`); the statement
above is the generalised final step, and it does not mention `M` at all.

Threshold (this is where the refinement bites).  The design case has
`C_x <= 10 * (5 - 2) = 30` at every `x` (`K58.rx_pair_bound` with `K = 5`); the
refined lower bound `19 + d_0 x <= C_x` then forces `d_0 x <= 11`, whereas the
unrefined `3 d_0 x - 8 <= C_x` only forces `d_0 x <= 12`.  Under `(R)`,
`d_0 x >= 15`, so the design case is four degrees below the profile's floor.

Paper version, the numbers, and the (independent, non-Lean) checks:
`.ultramath/smwrzh71x/m6/PROOF.md`;  `python3 -u .ultramath/smwrzh71x/m6/verify_design.py`.
-/
import K58.M7

set_option linter.unusedSectionVars false

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ## Part A: the second convexity engine -/

/-- `k <= C(k,2) + 1` for every `k`.  This is the integrality refinement of
`choose_two_add_three` (`2k <= C(k,2) + 3`): both hold termwise, and their maximum
`C(k,2) >= max (2k-3, k-1)` is the exact minimum of `sum C(k_i,2)` over integers
`k_i` with a fixed sum. -/
theorem le_choose_two_add_one (d : ℕ) : d ≤ d.choose 2 + 1 := by
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
        exact hh
      omega

/-- **The refined collision engine.**  The number of incidences between `R` and the
class of a vertex of `S` is at most the number of `(pair of S, vertex of R)`
incidences plus `#R`.  (The companion `collision_engine` has `3 * #R` on the right;
the two together are the exact convex minimum.) -/
theorem collision_engine_add_one (N : V → Finset V) (S R : Finset V) :
    ∑ z ∈ R, (S.filter (fun s => s ∈ N z)).card
      ≤ (∑ q ∈ S.powersetCard 2, (R.filter (fun z => ∀ s ∈ q, s ∈ N z)).card)
        + R.card := by
  have h1 : ∀ z ∈ R, (S.filter (fun s => s ∈ N z)).card
      ≤ (S.filter (fun s => s ∈ N z)).card.choose 2 + 1 :=
    fun z _ => le_choose_two_add_one _
  have h2 : ∑ z ∈ R, (S.filter (fun s => s ∈ N z)).card
      ≤ ∑ z ∈ R, ((S.filter (fun s => s ∈ N z)).card.choose 2 + 1) :=
    Finset.sum_le_sum h1
  have h3 : (∑ _z ∈ R, (1 : ℕ)) = R.card := by simp
  rw [Finset.sum_add_distrib, h3, sum_choose_two_comm N S R] at h2
  exact h2

/-! ## Part B: the refined lower bound at the pair `(r,x)` -/

/-- **The universal pair, refined.**  `19 + d_0(x) <= C_x`, where `C_x` is the
number of `(vertex of the residual set, pair of the trace)` incidences, i.e.
`C_x = sum_{z in R_x} C(|N_0 z cap P_x|, 2)`.  Compare `K58.rx_lower`, which gives
`3 d_0 x <= C_x + 8`. -/
theorem rx_lower_refined (G : EdgeCol V 4) (hT : TriangleFree G)
    (hV : Fintype.card V = 58)
    {r x : V} (hxr : x ≠ r) (hxA : x ∉ nbrC G r 0)
    (hA15 : (nbrC G r 0).card = 15)
    (hP5 : (nbrC G x 0 ∩ nbrC G r 0).card = 5)
    (hPdeg : ∀ p ∈ nbrC G x 0 ∩ nbrC G r 0, deg G p 0 = 15) :
    19 + deg G x 0
      ≤ (∑ q ∈ (nbrC G x 0 ∩ nbrC G r 0).powersetCard 2,
          ((Finset.univ \ (nbrC G r 0 ∪ nbrC G x 0 ∪ {r, x})).filter
            (fun z => ∀ p ∈ q, p ∈ nbrC G z 0)).card) := by
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
  -- the refined engine
  have heng := collision_engine_add_one (fun z => nbrC G z (0 : Fin 4)) P R
  rw [hT65] at heng
  omega

/-! ## Part C: the threshold and the local law -/

/-- **The threshold.**  If every pair inside the trace `P_x` has codegree at most
`5` (the design case at `x`), then `d_0 x <= 11`.  The design upper bound is
`K58.rx_pair_bound` at `K = 5` (`C_x <= 10 * 3 = 30`); the refined lower bound is
`K58.rx_lower_refined` (`19 + d_0 x <= C_x`). -/
theorem design_forces_light (G : EdgeCol V 4) (hT : TriangleFree G)
    (hV : Fintype.card V = 58)
    {r x : V} (hxr : x ≠ r) (hxA : x ∉ nbrC G r 0)
    (hA15 : (nbrC G r 0).card = 15)
    (hP5 : (nbrC G x 0 ∩ nbrC G r 0).card = 5)
    (hPdeg : ∀ p ∈ nbrC G x 0 ∩ nbrC G r 0, deg G p 0 = 15)
    (hdes : ∀ u ∈ nbrC G x 0 ∩ nbrC G r 0, ∀ v ∈ nbrC G x 0 ∩ nbrC G r 0, u ≠ v →
      (nbrC G u 0 ∩ nbrC G v 0).card ≤ 5) :
    deg G x 0 ≤ 11 := by
  have hup := rx_pair_bound G hxr hxA hP5 5 hdes
  have hlow := rx_lower_refined G hT hV hxr hxA hA15 hP5 hPdeg
  omega

/-- **The local law.**  If `x` is an outside vertex with `12 <= d_0 x` and a
five-point trace `P_x`, then some pair of `P_x` has codegree at least `6`.
Contrapositive of `design_forces_light`. -/
theorem trace_codegree_six (G : EdgeCol V 4) (hT : TriangleFree G)
    (hV : Fintype.card V = 58)
    {r x : V} (hxr : x ≠ r) (hxA : x ∉ nbrC G r 0)
    (hA15 : (nbrC G r 0).card = 15)
    (hP5 : (nbrC G x 0 ∩ nbrC G r 0).card = 5)
    (hPdeg : ∀ p ∈ nbrC G x 0 ∩ nbrC G r 0, deg G p 0 = 15)
    (hcritx : 12 ≤ deg G x 0) :
    ∃ u ∈ nbrC G x 0 ∩ nbrC G r 0, ∃ v ∈ nbrC G x 0 ∩ nbrC G r 0, u ≠ v ∧
      6 ≤ (nbrC G u 0 ∩ nbrC G v 0).card := by
  classical
  by_contra hcon
  have hle : ∀ u ∈ nbrC G x 0 ∩ nbrC G r 0, ∀ v ∈ nbrC G x 0 ∩ nbrC G r 0,
      u ≠ v → (nbrC G u 0 ∩ nbrC G v 0).card ≤ 5 := by
    intro u hu v hv huv
    by_contra hgt
    exact hcon ⟨u, hu, v, hv, huv, by omega⟩
  have := design_forces_light G hT hV hxr hxA hA15 hP5 hPdeg hle
  omega

/-! ## Part D: the design is not realisable -/

/-- **Target 5, kernel form.**  In the branch at a `(15,14,14,14)` root, with all
tickets returned, the `105` arm codegrees are never all `5`: the 42 five-point
traces `P_x = N_0 x cap A` are never the blocks of a `2-(15,5,4)` design. -/
theorem design_not_realisable (G : EdgeCol V 4) (hT : TriangleFree G)
    (hV : Fintype.card V = 58) (hR : Reciprocal G) (r : V)
    (hA15 : (nbrC G r 0).card = 15)
    (hAcrit : ∀ a ∈ nbrC G r 0, deg G a 0 = 15)
    (hm5 : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → (nbrC G x 0 ∩ nbrC G r 0).card = 5) :
    ¬ (∀ a ∈ nbrC G r 0, ∀ b ∈ nbrC G r 0, a ≠ b →
        (nbrC G a 0 ∩ nbrC G b 0).card = 5) := by
  classical
  intro hdes
  have hcrit := branch_crit G hR r hA15 hAcrit hm5
  obtain ⟨x, hxr, hxA⟩ := exists_outside G hV hA15
  have hP5 := hm5 x hxr hxA
  have hcx : 12 ≤ deg G x 0 := by have := hcrit x; omega
  obtain ⟨u, hu, v, hv, huv, h6⟩ :=
    trace_codegree_six G hT hV hxr hxA hA15 hP5
      (fun p hp => hAcrit p (Finset.mem_inter.mp hp).2) hcx
  have huA : u ∈ nbrC G r 0 := (Finset.mem_inter.mp hu).2
  have hvA : v ∈ nbrC G r 0 := (Finset.mem_inter.mp hv).2
  rw [hdes u huA v hvA huv] at h6
  omega

end K58
