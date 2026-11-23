import Mathlib

open Finset

namespace K58

variable {A : Type*} [Fintype A] [DecidableEq A]

/-- Weighted total of a point: the number of arm vertices that see it in
colour 0. -/
def tot (F : Finset (Finset A)) (m : Finset A → ℕ) (a : A) : ℕ :=
  ∑ S ∈ F, if a ∈ S then m S else 0

/-- Double counting: the sum of the weighted totals is the total multiplicity
weighted by support size. -/
theorem sum_tot (F : Finset (Finset A)) (m : Finset A → ℕ) :
    ∑ a, tot F m a = ∑ S ∈ F, m S * S.card := by
  simp only [tot]
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl ?_
  intro S _
  rw [Finset.sum_ite_mem]
  simp [Finset.sum_const, smul_eq_mul, Nat.mul_comm]

/-- **The disjointness rule.**  Two distinct classes whose multiplicities sum to
more than five have disjoint supports, because a common point would already be
seen more than five times. -/
theorem disjoint_of_add_gt (F : Finset (Finset A)) (m : Finset A → ℕ)
    (h5 : ∀ a, tot F m a ≤ 5) {S T : Finset A} (hS : S ∈ F) (hT : T ∈ F)
    (hne : S ≠ T) (hgt : 5 < m S + m T) : Disjoint S T := by
  refine Finset.disjoint_left.2 ?_
  intro a haS haT
  have hnonneg : ∀ U ∈ F, 0 ≤ (if a ∈ U then m U else 0) := by
    intro U _; split <;> omega
  have hsub : ({S, T} : Finset (Finset A)) ⊆ F := by
    intro U hU
    simp only [Finset.mem_insert, Finset.mem_singleton] at hU
    rcases hU with rfl | rfl <;> assumption
  have hle : ∑ U ∈ ({S, T} : Finset (Finset A)), (if a ∈ U then m U else 0)
      ≤ tot F m a := Finset.sum_le_sum_of_subset_of_nonneg hsub (fun U hU _ => hnonneg U hU)
  have hpair : ∑ U ∈ ({S, T} : Finset (Finset A)), (if a ∈ U then m U else 0)
      = m S + m T := by
    rw [Finset.sum_insert (by simp [hne]), Finset.sum_singleton]
    simp [haS, haT]
  have := h5 a
  omega

/-- **At most three pairwise disjoint 5-subsets of a 15-point set.** -/
theorem inc_card_le_three (F : Finset (Finset A)) (hA : Fintype.card A = 15)
    (hcard : ∀ S ∈ F, S.card = 5)
    (hdisj : ∀ S ∈ F, ∀ T ∈ F, S ≠ T → Disjoint S T) : F.card ≤ 3 := by
  have hb : (F.biUnion id).card = ∑ S ∈ F, (id S).card :=
    Finset.card_biUnion (fun S hS T hT hne => hdisj S hS T hT hne)
  have hsub : F.biUnion id ⊆ (Finset.univ : Finset A) := by
    intro a ha; exact Finset.mem_univ a
  have hcard' : (F.biUnion id).card = 5 * F.card := by
    rw [hb, Finset.sum_congr rfl (fun S hS => by simpa using hcard S hS), Finset.sum_const,
      smul_eq_mul, Nat.mul_comm]
  have := Finset.card_le_card hsub
  rw [hcard', Finset.card_univ, hA] at this
  omega

/-- **No four classes of multiplicity at least three.** -/
theorem no_four_heavy (F : Finset (Finset A)) (m : Finset A → ℕ)
    (hA : Fintype.card A = 15) (hcard : ∀ S ∈ F, S.card = 5)
    (h5 : ∀ a, tot F m a ≤ 5) (H : Finset (Finset A)) (hHF : H ⊆ F)
    (hheavy : ∀ S ∈ H, 3 ≤ m S) : H.card ≤ 3 := by
  refine inc_card_le_three H hA (fun S hS => hcard S (hHF hS)) ?_
  intro S hS T hT hne
  exact disjoint_of_add_gt F m h5 (hHF hS) (hHF hT) hne (by have := hheavy S hS; have := hheavy T hT; omega)

/-- If every multiplicity is even, every weighted total is even. -/
theorem tot_even (F : Finset (Finset A)) (m : Finset A → ℕ)
    (heven : ∀ S ∈ F, 2 ∣ m S) (a : A) : 2 ∣ tot F m a := by
  refine Finset.dvd_sum ?_
  intro S hS
  split
  · exact heven S hS
  · exact dvd_zero 2

/-- **All multiplicities even is impossible.**  Every point would have an even
total, hence total 4 (totals are 4 or 5); double counting then gives `4 * 15`
against `5 * sum of the multiplicities`. -/
theorem excl_all_even (F : Finset (Finset A)) (m : Finset A → ℕ)
    (hA : Fintype.card A = 15) (hcard : ∀ S ∈ F, S.card = 5)
    (h45 : ∀ a, tot F m a = 4 ∨ tot F m a = 5)
    (heven : ∀ S ∈ F, 2 ∣ m S) (hsum : ∑ S ∈ F, m S = 14) : False := by
  have h4 : ∀ a, tot F m a = 4 := by
    intro a
    rcases h45 a with h | h
    · exact h
    · have := tot_even F m heven a
      omega
  have h1 : ∑ a, tot F m a = 4 * 15 := by
    rw [Finset.sum_congr rfl (fun a _ => h4 a), Finset.sum_const, Finset.card_univ, hA,
      smul_eq_mul]
  have hstep : ∑ S ∈ F, m S * 5 = 5 * ∑ S ∈ F, m S := by
    rw [Finset.mul_sum]
    exact Finset.sum_congr rfl (fun S _ => Nat.mul_comm _ _)
  have h2 : ∑ a, tot F m a = 5 * 14 := by
    rw [sum_tot, Finset.sum_congr rfl (fun S hS => by rw [hcard S hS]), hstep, hsum]
  omega


/-! ## The four excluded profiles -/

/-- **No arm has all multiplicities even.**  `(2,2,2,2,2,2,2)` and
`(4,2,2,2,2,2)` are therefore impossible. -/
theorem no_all_even (F : Finset (Finset A)) (m : Finset A → ℕ)
    (hA : Fintype.card A = 15) (hcard : ∀ S ∈ F, S.card = 5)
    (h45 : ∀ a, tot F m a = 4 ∨ tot F m a = 5)
    (heven : ∀ S ∈ F, 2 ∣ m S) (hsum : ∑ S ∈ F, m S = 14) : False :=
  excl_all_even F m hA hcard h45 heven hsum

/-- **No four classes of multiplicity at least three**, concretely: the profile
`(3,3,3,3,1,1)` is impossible. -/
theorem excl_3333 (F : Finset (Finset A)) (m : Finset A → ℕ)
    (hA : Fintype.card A = 15) (hcard : ∀ S ∈ F, S.card = 5)
    (h5 : ∀ a, tot F m a ≤ 5)
    {S1 S2 S3 S4 : Finset A} (h1 : S1 ∈ F) (h2 : S2 ∈ F) (h3 : S3 ∈ F) (h4 : S4 ∈ F)
    (h12 : S1 ≠ S2) (h13 : S1 ≠ S3) (h14 : S1 ≠ S4) (h23 : S2 ≠ S3)
    (h24 : S2 ≠ S4) (h34 : S3 ≠ S4)
    (hm1 : 3 ≤ m S1) (hm2 : 3 ≤ m S2) (hm3 : 3 ≤ m S3) (hm4 : 3 ≤ m S4) : False := by
  have hsub : ({S1, S2, S3, S4} : Finset (Finset A)) ⊆ F := by
    intro U hU
    simp only [Finset.mem_insert, Finset.mem_singleton] at hU
    rcases hU with rfl | rfl | rfl | rfl <;> assumption
  have hheavy : ∀ S ∈ ({S1, S2, S3, S4} : Finset (Finset A)), 3 ≤ m S := by
    intro S hS
    simp only [Finset.mem_insert, Finset.mem_singleton] at hS
    rcases hS with rfl | rfl | rfl | rfl <;> assumption
  have hc4 : ({S1, S2, S3, S4} : Finset (Finset A)).card = 4 := by
    have h1' : S1 ∉ ({S2, S3, S4} : Finset (Finset A)) := by
      simp only [Finset.mem_insert, Finset.mem_singleton, not_or]
      exact ⟨h12, h13, h14⟩
    have h2' : S2 ∉ ({S3, S4} : Finset (Finset A)) := by
      simp only [Finset.mem_insert, Finset.mem_singleton, not_or]
      exact ⟨h23, h24⟩
    have h3' : S3 ∉ ({S4} : Finset (Finset A)) := by
      simp only [Finset.mem_singleton]
      exact h34
    rw [Finset.card_insert_of_notMem h1', Finset.card_insert_of_notMem h2',
      Finset.card_insert_of_notMem h3', Finset.card_singleton]
  have := no_four_heavy F m hA hcard h5 ({S1, S2, S3, S4} : Finset (Finset A)) hsub hheavy
  omega

/-- **The profile `(4,4,2,2,1,1)` is impossible.**  Distinctness of the supports
is essential here: without it the incidence `T1 = S1`, `T2 = S2` exists.  Both
2-classes are disjoint from both 4-classes, so both sit in the five points left
over and coincide. -/
theorem excl_442211 (F : Finset (Finset A)) (m : Finset A → ℕ)
    (hA : Fintype.card A = 15) (hcard : ∀ S ∈ F, S.card = 5)
    (h5 : ∀ a, tot F m a ≤ 5)
    {S1 S2 T1 T2 : Finset A} (hS1 : S1 ∈ F) (hS2 : S2 ∈ F) (hT1 : T1 ∈ F) (hT2 : T2 ∈ F)
    (hS : S1 ≠ S2) (hT : T1 ≠ T2) (hT1S1 : T1 ≠ S1) (hT1S2 : T1 ≠ S2)
    (hT2S1 : T2 ≠ S1) (hT2S2 : T2 ≠ S2)
    (hmS1 : m S1 = 4) (hmS2 : m S2 = 4) (hmT1 : m T1 = 2) (hmT2 : m T2 = 2) : False := by
  have hcard_univ : (Finset.univ : Finset A).card = 15 := by
    rw [Finset.card_univ]; exact hA
  have hdSS : Disjoint S1 S2 :=
    disjoint_of_add_gt F m h5 hS1 hS2 hS (by rw [hmS1, hmS2]; omega)
  have hd1 : Disjoint T1 S1 :=
    disjoint_of_add_gt F m h5 hT1 hS1 hT1S1 (by rw [hmT1, hmS1]; omega)
  have hd2 : Disjoint T1 S2 :=
    disjoint_of_add_gt F m h5 hT1 hS2 hT1S2 (by rw [hmT1, hmS2]; omega)
  have hd3 : Disjoint T2 S1 :=
    disjoint_of_add_gt F m h5 hT2 hS1 hT2S1 (by rw [hmT2, hmS1]; omega)
  have hd4 : Disjoint T2 S2 :=
    disjoint_of_add_gt F m h5 hT2 hS2 hT2S2 (by rw [hmT2, hmS2]; omega)
  have hsub1 : T1 ⊆ (S1 ∪ S2)ᶜ := by
    intro a ha
    simp only [Finset.mem_compl, Finset.mem_union, not_or]
    exact ⟨Finset.disjoint_left.1 hd1 ha, Finset.disjoint_left.1 hd2 ha⟩
  have hsub2 : T2 ⊆ (S1 ∪ S2)ᶜ := by
    intro a ha
    simp only [Finset.mem_compl, Finset.mem_union, not_or]
    exact ⟨Finset.disjoint_left.1 hd3 ha, Finset.disjoint_left.1 hd4 ha⟩
  have hcardU : (S1 ∪ S2).card = 10 := by
    rw [Finset.card_union_of_disjoint hdSS, hcard S1 hS1, hcard S2 hS2]
  have hcompl : ((S1 ∪ S2)ᶜ).card = 5 := by
    rw [Finset.card_compl, hcardU, hA]
  have e1 : T1 = (S1 ∪ S2)ᶜ :=
    Finset.eq_of_subset_of_card_le hsub1 (by rw [hcard T1 hT1, hcompl])
  have e2 : T2 = (S1 ∪ S2)ᶜ :=
    Finset.eq_of_subset_of_card_le hsub2 (by rw [hcard T2 hT2, hcompl])
  exact hT (e1.trans e2.symm)

/-- **No class has multiplicity above five.**  Every point of a support has
weighted total at least the multiplicity, and totals are at most five.  So the
fivefold package's bound `X1` is a consequence of the incidence layer. -/
theorem inc_mult_le_five (F : Finset (Finset A)) (m : Finset A → ℕ)
    (h5 : ∀ a, tot F m a ≤ 5) {S : Finset A} (hS : S ∈ F) (hcard : S.card = 5) :
    m S ≤ 5 := by
  have hpos : 0 < S.card := by rw [hcard]; norm_num
  obtain ⟨a, ha⟩ := Finset.card_pos.mp hpos
  have hsingle : (if a ∈ S then m S else 0) ≤ tot F m a :=
    Finset.single_le_sum (f := fun U => if a ∈ U then m U else 0)
      (fun U _ => by split <;> omega) hS
  rw [if_pos ha] at hsingle
  have := h5 a
  omega

/-- The profile `(2,2,2,2,2,2,2)` is impossible. -/
theorem excl_2_7 (F : Finset (Finset A)) (m : Finset A → ℕ)
    (hA : Fintype.card A = 15) (hcard : ∀ S ∈ F, S.card = 5)
    (h45 : ∀ a, tot F m a = 4 ∨ tot F m a = 5)
    (hsum : ∑ S ∈ F, m S = 14) (hm : ∀ S ∈ F, m S = 2) : False :=
  no_all_even F m hA hcard h45
    (fun S hS => by rw [hm S hS]) hsum

/-- The profile `(4,2,2,2,2,2)` is impossible. -/
theorem excl_4_2_2_2_2_2 (F : Finset (Finset A)) (m : Finset A → ℕ)
    (hA : Fintype.card A = 15) (hcard : ∀ S ∈ F, S.card = 5)
    (h45 : ∀ a, tot F m a = 4 ∨ tot F m a = 5)
    (hsum : ∑ S ∈ F, m S = 14) (hm : ∀ S ∈ F, m S = 4 ∨ m S = 2) : False :=
  no_all_even F m hA hcard h45
    (fun S hS => by rcases hm S hS with h | h <;> rw [h] <;> norm_num) hsum

/-- An arm whose profile is `(3,3,3,3,1,1)`: four classes of multiplicity three
are already impossible. -/
theorem excl_3_3_3_3_1_1 (F : Finset (Finset A)) (m : Finset A → ℕ)
    (hA : Fintype.card A = 15) (hcard : ∀ S ∈ F, S.card = 5)
    (h5 : ∀ a, tot F m a ≤ 5)
    {S1 S2 S3 S4 : Finset A} (h1 : S1 ∈ F) (h2 : S2 ∈ F) (h3 : S3 ∈ F) (h4 : S4 ∈ F)
    (h12 : S1 ≠ S2) (h13 : S1 ≠ S3) (h14 : S1 ≠ S4) (h23 : S2 ≠ S3)
    (h24 : S2 ≠ S4) (h34 : S3 ≠ S4) (hm : ∀ S ∈ F, 3 ≤ m S) : False :=
  excl_3333 F m hA hcard h5 h1 h2 h3 h4 h12 h13 h14 h23 h24 h34
    (hm S1 h1) (hm S2 h2) (hm S3 h3) (hm S4 h4)

/-- An arm whose profile is `(4,4,2,2,1,1)`. -/
theorem excl_4_4_2_2_1_1 (F : Finset (Finset A)) (m : Finset A → ℕ)
    (hA : Fintype.card A = 15) (hcard : ∀ S ∈ F, S.card = 5)
    (h5 : ∀ a, tot F m a ≤ 5)
    {S1 S2 T1 T2 : Finset A} (hS1 : S1 ∈ F) (hS2 : S2 ∈ F) (hT1 : T1 ∈ F) (hT2 : T2 ∈ F)
    (hS : S1 ≠ S2) (hT : T1 ≠ T2) (hT1S1 : T1 ≠ S1) (hT1S2 : T1 ≠ S2)
    (hT2S1 : T2 ≠ S1) (hT2S2 : T2 ≠ S2)
    (hmS1 : m S1 = 4) (hmS2 : m S2 = 4) (hmT1 : m T1 = 2) (hmT2 : m T2 = 2) : False :=
  excl_442211 F m hA hcard h5 hS1 hS2 hT1 hT2 hS hT hT1S1 hT1S2 hT2S1 hT2S2
    hmS1 hmS2 hmT1 hmT2

end K58

#print axioms K58.sum_tot
#print axioms K58.disjoint_of_add_gt
#print axioms K58.inc_card_le_three
#print axioms K58.no_four_heavy
#print axioms K58.tot_even
#print axioms K58.no_all_even
#print axioms K58.excl_2_7
#print axioms K58.excl_4_2_2_2_2_2
#print axioms K58.excl_3_3_3_3_1_1
#print axioms K58.excl_4_4_2_2_1_1
#print axioms K58.inc_mult_le_five


