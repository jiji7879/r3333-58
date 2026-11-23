/-
Arm senders under reciprocity, for the `(15,14,14,14)` profile at `n = 58`.

Everything here is stated against the campaign's own definitions (`K58.Basic`,
`K58.Ticket`, `K58.Reduction`), so the file registers in `lean/K58/Check.lean`
without restatement.

Main results (sorry-free, no `native_decide`, no extra axioms):

* `arm_sender_free_of_reciprocal` : under (R), a vertex `u` of the colour-`c`
  arm of a vertex `r` with `deg G r c <= 14` is not `c`-critical.  Equivalently:
  at a `(15,14,14,14)` root the three 14-arms carry no sender at all.
* `armSenders_eq_zero_of_reciprocal` : the same in the campaign's sender
  notation, `armSenders G r c = 0`.
* `arm0_reaches_of_reciprocal` : consequently balance `w r <= H r` at a
  `(15,14,14,14)` root forces `armSenders G r 0 = 15`, i.e. all fifteen points of
  the 15-arm are 0-critical -- the criticality half of the branch, which
  `review/PROFILE_15141414_STATE.md` §2 attributes to the missing theorem
  `K58.branch_of_balanced_no_small_arm_sender` (that theorem is nowhere in the
  tree; see REPORT.md).

The mathematical content is one line: under (R) criticality is symmetric along
every edge, and `r` is not `c`-critical for `c = 1,2,3` because `deg G r c = 14`.
-/
import K58.Ticket
import K58.Reduction

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- **(R) kills senders in a non-critical arm.**  If the colour-`c` degree of `r`
is at most 14, no colour-`c` neighbour of `r` is `c`-critical. -/
theorem arm_sender_free_of_reciprocal (G : EdgeCol V 4) (hR : Reciprocal G)
    {r : V} {c : Fin 4} (hr : deg G r c ≤ 14) {u : V} (hu : u ∈ nbrC G r c) :
    ¬ (15 ≤ deg G u c) := by
  intro hcrit
  rw [mem_nbrC] at hu
  obtain ⟨hur, hcol⟩ := hu
  have hedge : 15 ≤ deg G u (G.col u r) := by
    rw [G.symm u r, hcol]; exact hcrit
  have hback : 15 ≤ deg G r (G.col u r) := (hR u r hur).mp hedge
  rw [G.symm u r, hcol] at hback
  omega

/-- The sender count of a non-critical arm is zero under (R). -/
theorem armSenders_eq_zero_of_reciprocal (G : EdgeCol V 4) (hR : Reciprocal G)
    {r : V} {c : Fin 4} (hr : deg G r c ≤ 14) : armSenders G r c = 0 := by
  have h : ∀ u : V, ¬ (r ≠ u ∧ G.col r u = c ∧ 15 ≤ deg G u (G.col u r)) := by
    intro u hu
    obtain ⟨hru, hcol, hcrit⟩ := hu
    have h15 : 15 ≤ deg G u c := by
      simpa [G.symm u r, hcol] using hcrit
    exact arm_sender_free_of_reciprocal G hR hr (mem_nbrC.mpr ⟨hru.symm, hcol⟩) h15
  rw [armSenders, Finset.card_eq_zero, Finset.filter_eq_empty_iff]
  intro u _
  exact h u

/-- Senders in an arm never exceed the arm. -/
theorem armSenders_le_deg (G : EdgeCol V 4) (i : V) (a : Fin 4) :
    armSenders G i a ≤ deg G i a := by
  rw [armSenders, ← card_nbrC]
  unfold nbrC
  apply Finset.card_le_card
  intro j hj
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hj ⊢
  exact ⟨hj.1.symm, hj.2.1⟩

/-- **The missing theorem's content, sender-free form.**  At a root of profile
`(15,14,14,14)`, if the three 14-arms carry no sender and the root receives at
least as many tickets as it sends, then the 15-arm reaches fifteen senders.  This
is the statement `review/PROFILE_15141414_STATE.md` §2 and
`.ultramath/smwrmwgf7/m11/w/obligations.md` §3 cite as
`K58.branch_of_balanced_no_small_arm_sender`; no such theorem exists in the
tree (see REPORT.md), so it is proved here. -/
theorem arm0_reaches_of_arm_senders_zero (G : EdgeCol V 4) {r : V}
    (h0 : deg G r (0 : Fin 4) = 15) (h1 : deg G r (1 : Fin 4) = 14)
    (h2 : deg G r (2 : Fin 4) = 14) (h3 : deg G r (3 : Fin 4) = 14)
    (e1 : armSenders G r (1 : Fin 4) = 0) (e2 : armSenders G r (2 : Fin 4) = 0)
    (e3 : armSenders G r (3 : Fin 4) = 0)
    (hb : w G r ≤ H G r) : armSenders G r (0 : Fin 4) = 15 := by
  have hH : H G r = armSenders G r 0 + armSenders G r 1 + armSenders G r 2
      + armSenders G r 3 := by
    rw [H_eq_sum_armSenders, Fin.sum_univ_four]
  have hw : w G r = 15 := by
    rw [w_eq_sum_critical, Fin.sum_univ_four]
    rw [if_pos (by omega : 15 ≤ deg G r 0), if_neg (by omega : ¬ 15 ≤ deg G r 1),
      if_neg (by omega : ¬ 15 ≤ deg G r 2), if_neg (by omega : ¬ 15 ≤ deg G r 3)]
    omega
  have hle : armSenders G r (0 : Fin 4) ≤ 15 := by
    have := armSenders_le_deg G r 0
    omega
  rw [hw] at hb
  omega

/-- **Under (R) the branch is forced.**  At a root of profile `(15,14,14,14)`
with balance, reciprocity makes the 15-arm reach fifteen senders: every point of
`N_0(r)` is `0`-critical. -/
theorem arm0_reaches_of_reciprocal (G : EdgeCol V 4) (hR : Reciprocal G) {r : V}
    (h0 : deg G r (0 : Fin 4) = 15) (h1 : deg G r (1 : Fin 4) = 14)
    (h2 : deg G r (2 : Fin 4) = 14) (h3 : deg G r (3 : Fin 4) = 14)
    (hb : w G r ≤ H G r) : armSenders G r (0 : Fin 4) = 15 :=
  arm0_reaches_of_arm_senders_zero G h0 h1 h2 h3
    (armSenders_eq_zero_of_reciprocal G hR (by omega))
    (armSenders_eq_zero_of_reciprocal G hR (by omega))
    (armSenders_eq_zero_of_reciprocal G hR (by omega)) hb

/-- **The sharpest form.**  A profile root with a sender in a 14-arm is a
counterexample to (R): some edge of the colouring is critical at one end and not
at the other.  So every frozen row that demands a sender in a 14-arm lives
entirely outside the reciprocal world. -/
theorem not_reciprocal_of_arm_sender (G : EdgeCol V 4) {r u : V}
    (h1 : deg G r (1 : Fin 4) = 14) (hu : u ∈ nbrC G r (1 : Fin 4))
    (hcrit : 15 ≤ deg G u (1 : Fin 4)) : ¬ Reciprocal G := by
  intro hR
  exact arm_sender_free_of_reciprocal G hR (by omega) hu hcrit

/-- **The campaign's name for (R) is exact, one direction.**  Under (R) the
senders of an arm are all of it when the centre is critical in that colour and
none of it when it is not. -/
theorem armSenders_eq_of_reciprocal (G : EdgeCol V 4) (hR : Reciprocal G) (v : V)
    (c : Fin 4) : armSenders G v c = if 15 ≤ deg G v c then deg G v c else 0 := by
  by_cases h : 15 ≤ deg G v c
  · have key : Finset.univ.filter
        (fun j : V => v ≠ j ∧ G.col v j = c ∧ 15 ≤ deg G j (G.col j v)) = nbrC G v c := by
      apply Finset.Subset.antisymm
      · intro j hj
        simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hj
        exact mem_nbrC.mpr ⟨hj.1.symm, hj.2.1⟩
      · intro j hj
        rw [mem_nbrC] at hj
        obtain ⟨hjv, hcol⟩ := hj
        have hc : j ∈ Crit G c :=
          nbrC_subset_Crit G hR (mem_Crit.mpr h) (mem_nbrC.mpr ⟨hjv, hcol⟩)
        rw [mem_Crit] at hc
        simp only [Finset.mem_filter, Finset.mem_univ, true_and]
        exact ⟨hjv.symm, hcol, by simpa [G.symm j v, hcol] using hc⟩
    rw [if_pos h, armSenders, key, card_nbrC]
  · rw [if_neg h]
    exact armSenders_eq_zero_of_reciprocal G hR (by omega)

/-- **Under (R) every vertex returns every ticket it receives**: `H v = w v` at
every vertex, not merely at a root with balance.  So under (R) the whole board
satisfies the ticket-root condition, and `W2` degenerates to "no vertex of
profile `(15,14,14,14)` at all". -/
theorem H_eq_w_of_reciprocal (G : EdgeCol V 4) (hR : Reciprocal G) (v : V) :
    H G v = w G v := by
  rw [H_eq_sum_armSenders, w_eq_sum_critical]
  exact Finset.sum_congr rfl fun c _ => armSenders_eq_of_reciprocal G hR v c

end K58
