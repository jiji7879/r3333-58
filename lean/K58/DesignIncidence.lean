/-
  The design (incidence) filter for the zero-set multiplicity layer of a 14-arm.

  Data.  `κ` indexes the classes of equal zero sets in an ordinary arm, `α` is
  the 15-point colour-0 arm of the root.  Class `i` has multiplicity `m i`
  (the number of arm vertices with that zero set) and support `S i` (the zero
  set itself, a 5-subset of `α`).  The established incidence law of the
  instance is that every point of `α` lies in classes whose multiplicities sum
  to 4 or 5.

  Proved here, sorry-free and with no `native_decide`:
    * `mult_le_five`      : every multiplicity is at most 5;
    * `card_large_le_three`: at most three classes have multiplicity ≥ 3;
    * `not_all_even`      : not all multiplicities are even.
  Axioms are the three standard ones (checked at the bottom).
-/
import Mathlib

set_option linter.unusedSectionVars false

open Finset

namespace K58

variable {κ α : Type*} [Fintype κ] [DecidableEq κ] [Fintype α] [DecidableEq α]

/-- The multiplicity of the point `a`: the number of arm vertices seeing `a` in colour 0. -/
def wtD (m : κ → ℕ) (S : κ → Finset α) (a : α) : ℕ :=
  ∑ i, m i * (if a ∈ S i then 1 else 0)

/-- A design: distinct 5-element supports, every point of total 4 or 5. -/
structure Design (m : κ → ℕ) (S : κ → Finset α) : Prop where
  card_support : ∀ i, (S i).card = 5
  total_lower : ∀ a, 4 ≤ wtD m S a
  total_upper : ∀ a, wtD m S a ≤ 5

variable {m : κ → ℕ} {S : κ → Finset α}

lemma wt_nonneg (a : α) : 0 ≤ wtD m S a := Nat.zero_le _

/-- A point of the support of class `i` contributes at least `m i` to the total. -/
lemma mult_le_wt {i : κ} {a : α} (ha : a ∈ S i) : m i ≤ wtD m S a := by
  have h : m i * (if a ∈ S i then 1 else 0) ≤ wtD m S a :=
    Finset.single_le_sum (f := fun j => m j * (if a ∈ S j then 1 else 0))
      (fun j _ => Nat.zero_le _) (Finset.mem_univ i)
  simpa [ha] using h

/-- If two classes both meet a point, their multiplicities sum to at most 5. -/
lemma add_le_five (h : Design m S) {i j : κ} {a : α} (hij : i ≠ j) (hi : a ∈ S i)
    (hj : a ∈ S j) : m i + m j ≤ 5 := by
  have hsub : ({i, j} : Finset κ) ⊆ Finset.univ := Finset.subset_univ _
  have hle : ∑ k ∈ ({i, j} : Finset κ), m k * (if a ∈ S k then 1 else 0) ≤ wtD m S a :=
    Finset.sum_le_sum_of_subset_of_nonneg hsub (fun k _ _ => Nat.zero_le _)
  have hset : ∑ k ∈ ({i, j} : Finset κ), m k * (if a ∈ S k then 1 else 0) = m i + m j := by
    rw [Finset.sum_insert (by simp [hij]), Finset.sum_singleton]
    simp [hi, hj]
  have h5 := h.total_upper a
  rw [hset] at hle
  omega

/-- **Every multiplicity is at most five.** -/
theorem mult_le_five (h : Design m S) (i : κ) : m i ≤ 5 := by
  have hconst : ∑ _a ∈ S i, m i = (S i).card * m i := by
    rw [Finset.sum_const, smul_eq_mul]
  have hsum : (S i).card * m i ≤ ∑ a ∈ S i, wtD m S a := by
    rw [← hconst]
    exact Finset.sum_le_sum (fun a ha => mult_le_wt ha)
  have hub : ∑ a ∈ S i, wtD m S a ≤ (S i).card * 5 := by
    calc ∑ a ∈ S i, wtD m S a ≤ ∑ _a ∈ S i, 5 :=
          Finset.sum_le_sum (fun a _ => h.total_upper a)
      _ = (S i).card * 5 := by rw [Finset.sum_const, smul_eq_mul]
  rw [h.card_support i] at hsum hub
  omega

/-- **At most three classes have multiplicity at least three.** -/
theorem card_large_le_three (h : Design m S) (hα : Fintype.card α = 15) :
    (Finset.univ.filter (fun i => 3 ≤ m i)).card ≤ 3 := by
  set t := Finset.univ.filter (fun i => 3 ≤ m i) with ht
  have hdisj : ∀ i ∈ t, ∀ j ∈ t, i ≠ j → Disjoint (S i) (S j) := by
    intro i hi j hj hij
    rw [Finset.disjoint_left]
    intro a hai haj
    have h3i : 3 ≤ m i := (Finset.mem_filter.mp hi).2
    have h3j : 3 ≤ m j := (Finset.mem_filter.mp hj).2
    have := add_le_five h hij hai haj
    omega
  have hcard : (t.biUnion S).card = ∑ i ∈ t, (S i).card :=
    Finset.card_biUnion hdisj
  have hsub : t.biUnion S ⊆ Finset.univ := Finset.subset_univ _
  have hle : (t.biUnion S).card ≤ 15 := by
    rw [← hα]
    exact Finset.card_le_univ _
  have hsum : ∑ i ∈ t, (S i).card = t.card * 5 := by
    have : ∑ i ∈ t, (S i).card = ∑ _i ∈ t, 5 :=
      Finset.sum_congr rfl (fun i _ => h.card_support i)
    rw [this, Finset.sum_const, smul_eq_mul]
  rw [hcard, hsum] at hle
  omega

/-- A total that is even and lies in `{4,5}` equals 4. -/
lemma eq_four_of_even {w : ℕ} (h4 : 4 ≤ w) (h5 : w ≤ 5) (he : 2 ∣ w) : w = 4 := by
  obtain ⟨k, hk⟩ := he
  omega

/-- **Not all multiplicities are even.** -/
theorem not_all_even (h : Design m S) (hα : Fintype.card α = 15)
    (hsum : ∑ i, m i = 14) : ¬ ∀ i, 2 ∣ m i := by
  intro hev
  have hwev : ∀ a, 2 ∣ wtD m S a := by
    intro a
    refine Finset.dvd_sum (fun i _ => ?_)
    by_cases ha : a ∈ S i
    · simpa [ha] using hev i
    · simp [ha]
  have hw4 : ∀ a, wtD m S a = 4 := fun a =>
    eq_four_of_even (h.total_lower a) (h.total_upper a) (hwev a)
  have hdouble : ∑ a, wtD m S a = ∑ i, m i * (S i).card := by
    have hswap : ∀ i, (∑ a, m i * (if a ∈ S i then 1 else 0)) = m i * (S i).card := by
      intro i
      rw [← Finset.mul_sum]
      have hone : (∑ a, (if a ∈ S i then (1:ℕ) else 0)) = (S i).card := by
        rw [Finset.sum_ite_mem, Finset.univ_inter]
        exact (Finset.card_eq_sum_ones (S i)).symm
      rw [hone]
    simp only [wtD]
    rw [Finset.sum_comm]
    exact Finset.sum_congr rfl (fun i _ => hswap i)
  have hleft : ∑ a, wtD m S a = 60 := by
    rw [Finset.sum_congr rfl (fun a _ => hw4 a)]
    simp [Finset.card_univ, hα]
  have hright : ∑ i, m i * (S i).card = 70 := by
    have h1 : ∑ i, m i * (S i).card = ∑ i, m i * 5 :=
      Finset.sum_congr rfl (fun i _ => by rw [h.card_support i])
    have h2 : ∑ i, m i * 5 = (∑ i, m i) * 5 := (Finset.sum_mul Finset.univ m 5).symm
    rw [h1, h2, hsum]
  omega

/-- Concrete corollary: the profile `(3,3,3,3,1,1)` has no design. -/
theorem no_design_three_three_three_three_one_one {S : Fin 6 → Finset α}
    (h : Design (![3, 3, 3, 3, 1, 1] : Fin 6 → ℕ) S) (hα : Fintype.card α = 15) : False := by
  have h3 : (Finset.univ.filter
      (fun i : Fin 6 => 3 ≤ (![3, 3, 3, 3, 1, 1] : Fin 6 → ℕ) i)).card ≤ 3 :=
    card_large_le_three h hα
  have h4 : (Finset.univ.filter
      (fun i : Fin 6 => 3 ≤ (![3, 3, 3, 3, 1, 1] : Fin 6 → ℕ) i)).card = 4 := by decide
  omega

/-- Concrete corollary: the profile `(2,2,2,2,2,2,2)` has no design (parity). -/
theorem no_design_seven_twos {S : Fin 7 → Finset α}
    (h : Design (![2, 2, 2, 2, 2, 2, 2] : Fin 7 → ℕ) S) (hα : Fintype.card α = 15) : False :=
  not_all_even (m := (![2, 2, 2, 2, 2, 2, 2] : Fin 7 → ℕ)) (S := S) h hα (by decide) (by decide)

end K58

#print axioms K58.mult_le_five
#print axioms K58.card_large_le_three
#print axioms K58.not_all_even
#print axioms K58.no_design_three_three_three_three_one_one
#print axioms K58.no_design_seven_twos
