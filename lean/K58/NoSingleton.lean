/-
Kernel-checked core of the no-singleton multiplicity layer of the (15,14,14,14)
branch of the K58 profile, together with the rigidity of a high-codegree pair.

A. `template_class_triple_T/U`: for BOTH classified rooted 15-point templates and
   EVERY root, the three colour classes of the root have sizes 4,5,5 in some order.
B. `partition_law`: if every sender's triple of arm weights is a permutation of
   (4,5,5) and each arm's total is 70 = 14*5, each arm has exactly five weight-4
   senders and the three weight-4 sets partition the senders.
C. `codegree_le_ten_of_cross`: in a no-singleton arm (classes of multiplicity 2 or
   3, every sender in two classes) a pair with m_B = 5 whose members lie on
   opposite sides of the A_C/A_D split has |N_0(a) n N_0(b)| = 1+m_B+m_C+m_D <= 10.
-/
import Mathlib

open Finset
open scoped BigOperators

namespace K58

/-! ## A. The two templates -/

/-- The T template, 15 x 15, colours 1..3 off the diagonal. -/
def NS_Tm : List (List Nat) :=
  [[0, 1, 2, 2, 3, 3, 3, 2, 1, 3, 1, 2, 1, 2, 3],
      [1, 0, 2, 2, 3, 2, 3, 3, 3, 1, 2, 1, 3, 1, 1],
      [2, 2, 0, 1, 3, 3, 2, 3, 1, 2, 1, 3, 2, 1, 1],
      [2, 2, 1, 0, 2, 3, 3, 3, 2, 1, 3, 1, 1, 3, 2],
      [3, 3, 3, 2, 0, 1, 2, 2, 1, 2, 3, 1, 1, 3, 1],
      [3, 2, 3, 3, 1, 0, 2, 2, 3, 1, 1, 2, 3, 1, 2],
      [3, 3, 2, 3, 2, 2, 0, 1, 2, 1, 1, 3, 1, 2, 1],
      [2, 3, 3, 3, 2, 2, 1, 0, 1, 3, 2, 1, 2, 1, 3],
      [1, 3, 1, 2, 1, 3, 2, 1, 0, 1, 2, 2, 2, 3, 3],
      [3, 1, 2, 1, 2, 1, 1, 3, 1, 0, 2, 2, 3, 3, 2],
      [1, 2, 1, 3, 3, 1, 1, 2, 2, 2, 0, 1, 3, 2, 3],
      [2, 1, 3, 1, 1, 2, 3, 1, 2, 2, 1, 0, 3, 3, 3],
      [1, 3, 2, 1, 1, 3, 1, 2, 2, 3, 3, 3, 0, 1, 2],
      [2, 1, 1, 3, 3, 1, 2, 1, 3, 3, 2, 3, 1, 0, 2],
      [3, 1, 1, 2, 1, 2, 1, 3, 3, 2, 3, 3, 2, 2, 0]]

/-- The U template, 15 x 15. -/
def NS_Um : List (List Nat) :=
  [[0, 1, 2, 2, 3, 3, 3, 2, 1, 3, 1, 2, 1, 2, 3],
      [1, 0, 2, 2, 3, 3, 2, 3, 3, 1, 2, 1, 2, 1, 1],
      [2, 2, 0, 1, 3, 2, 3, 3, 1, 2, 1, 3, 3, 1, 1],
      [2, 2, 1, 0, 2, 3, 3, 3, 2, 1, 3, 1, 1, 3, 2],
      [3, 3, 3, 2, 0, 1, 2, 2, 1, 2, 3, 1, 1, 3, 1],
      [3, 3, 2, 3, 1, 0, 2, 2, 2, 1, 1, 3, 3, 1, 2],
      [3, 2, 3, 3, 2, 2, 0, 1, 3, 1, 1, 2, 1, 2, 1],
      [2, 3, 3, 3, 2, 2, 1, 0, 1, 3, 2, 1, 2, 1, 3],
      [1, 3, 1, 2, 1, 2, 3, 1, 0, 1, 2, 2, 3, 3, 3],
      [3, 1, 2, 1, 2, 1, 1, 3, 1, 0, 2, 2, 3, 3, 2],
      [1, 2, 1, 3, 3, 1, 1, 2, 2, 2, 0, 1, 3, 2, 3],
      [2, 1, 3, 1, 1, 3, 2, 1, 2, 2, 1, 0, 2, 3, 3],
      [1, 2, 3, 1, 1, 3, 1, 2, 3, 3, 3, 2, 0, 1, 2],
      [2, 1, 1, 3, 3, 1, 2, 1, 3, 3, 2, 3, 1, 0, 2],
      [3, 1, 1, 2, 1, 2, 1, 3, 3, 2, 3, 3, 2, 2, 0]]

/-- Size of the colour-`c` class of the root `rt`. -/
def classSize (M : List (List Nat)) (rt c : Nat) : Nat :=
  ((List.range 15).filter (fun y => y != rt && (M.getD rt []).getD y 0 == c)).length

/-- `(a,b,c)` is a permutation of `(4,5,5)`. -/
def is455 (a b c : Nat) : Bool :=
  (a == 4 && b == 5 && c == 5) || (a == 5 && b == 4 && c == 5) ||
    (a == 5 && b == 5 && c == 4)

theorem template_class_triple_T :
    (List.range 15).all (fun rt =>
      is455 (classSize NS_Tm rt 1) (classSize NS_Tm rt 2) (classSize NS_Tm rt 3)) = true := by
  decide

theorem template_class_triple_U :
    (List.range 15).all (fun rt =>
      is455 (classSize NS_Um rt 1) (classSize NS_Um rt 2) (classSize NS_Um rt 3)) = true := by
  decide

/-! ## B. The partition law -/

section Partition

variable {A : Type*} [Fintype A] [DecidableEq A]

/-- Counting helper: a `{4,5}`-valued function on a 15-point set whose total is
`70` has exactly five points of value `4`. -/
theorem card_four_of_sum (w : A → ℕ) (hcard : Fintype.card A = 15)
    (hw : ∀ a, w a = 4 ∨ w a = 5) (hsum : ∑ a, w a = 70) :
    (univ.filter (fun a => w a = 4)).card = 5 := by
  classical
  have hdisj : Disjoint (univ.filter (fun a => w a = 4))
      (univ.filter (fun a => w a = 5)) := by
    rw [Finset.disjoint_filter]
    intro a _ h4 h5
    omega
  have hunion : (univ.filter (fun a => w a = 4)) ∪ (univ.filter (fun a => w a = 5))
      = univ := by
    ext a
    simp only [mem_union, mem_filter, mem_univ, true_and]
    constructor
    · intro _; trivial
    · intro _
      rcases hw a with h | h
      · exact Or.inl h
      · exact Or.inr h
  have hsplit : (univ.filter (fun a => w a = 4)).card +
      (univ.filter (fun a => w a = 5)).card = Fintype.card A := by
    rw [← Finset.card_union_of_disjoint hdisj, hunion, Finset.card_univ]
  have hsum' : ∑ a, w a = 4 * Fintype.card A +
      (univ.filter (fun a => w a = 5)).card := by
    have h1 : ∑ a, w a = ∑ a, (4 + if w a = 5 then 1 else 0) := by
      apply Finset.sum_congr rfl
      intro a _
      rcases hw a with h | h <;> simp [h]
    rw [h1, Finset.sum_add_distrib]
    simp [Finset.sum_boole, Finset.card_univ, Nat.mul_comm]
  omega

/-- **Partition law.**  If each sender's triple of arm weights is a permutation of
`(4,5,5)`, and each arm's total weight is `70 = 14 * 5`, then each arm has exactly
five weight-4 senders, and the three weight-4 sets are pairwise disjoint with
union the whole sender set. -/
theorem partition_law (wB wC wD : A → ℕ) (hcard : Fintype.card A = 15)
    (htriple : ∀ a, (wB a = 4 ∧ wC a = 5 ∧ wD a = 5) ∨
      (wB a = 5 ∧ wC a = 4 ∧ wD a = 5) ∨ (wB a = 5 ∧ wC a = 5 ∧ wD a = 4))
    (hB : ∑ a, wB a = 70) (hC : ∑ a, wC a = 70) (hD : ∑ a, wD a = 70) :
    (univ.filter (fun a => wB a = 4)).card = 5 ∧
    (univ.filter (fun a => wC a = 4)).card = 5 ∧
    (univ.filter (fun a => wD a = 4)).card = 5 ∧
    Disjoint (univ.filter (fun a => wB a = 4)) (univ.filter (fun a => wC a = 4)) ∧
    Disjoint (univ.filter (fun a => wB a = 4)) (univ.filter (fun a => wD a = 4)) ∧
    Disjoint (univ.filter (fun a => wC a = 4)) (univ.filter (fun a => wD a = 4)) ∧
    (univ.filter (fun a => wB a = 4) ∪ univ.filter (fun a => wC a = 4) ∪
      univ.filter (fun a => wD a = 4)) = univ := by
  classical
  have hB45 : ∀ a, wB a = 4 ∨ wB a = 5 := by
    intro a; rcases htriple a with ⟨h, -, -⟩ | ⟨h, -, -⟩ | ⟨h, -, -⟩ <;> omega
  have hC45 : ∀ a, wC a = 4 ∨ wC a = 5 := by
    intro a; rcases htriple a with ⟨-, h, -⟩ | ⟨-, h, -⟩ | ⟨-, h, -⟩ <;> omega
  have hD45 : ∀ a, wD a = 4 ∨ wD a = 5 := by
    intro a; rcases htriple a with ⟨-, -, h⟩ | ⟨-, -, h⟩ | ⟨-, -, h⟩ <;> omega
  have hb4 := card_four_of_sum wB hcard hB45 hB
  have hc4 := card_four_of_sum wC hcard hC45 hC
  have hd4 := card_four_of_sum wD hcard hD45 hD
  refine ⟨hb4, hc4, hd4, ?_, ?_, ?_, ?_⟩
  · rw [Finset.disjoint_left]
    intro a ha ha'
    simp only [mem_filter, mem_univ, true_and] at ha ha'
    rcases htriple a with ⟨h, h', -⟩ | ⟨h, h', -⟩ | ⟨h, h', -⟩ <;> omega
  · rw [Finset.disjoint_left]
    intro a ha ha'
    simp only [mem_filter, mem_univ, true_and] at ha ha'
    rcases htriple a with ⟨h, -, h'⟩ | ⟨h, -, h'⟩ | ⟨h, -, h'⟩ <;> omega
  · rw [Finset.disjoint_left]
    intro a ha ha'
    simp only [mem_filter, mem_univ, true_and] at ha ha'
    rcases htriple a with ⟨-, h, h'⟩ | ⟨-, h, h'⟩ | ⟨-, h, h'⟩ <;> omega
  · ext a
    simp only [mem_union, mem_filter, mem_univ, true_and]
    constructor
    · intro _; trivial
    · intro _
      rcases htriple a with ⟨h, -, -⟩ | ⟨-, h, -⟩ | ⟨-, -, h⟩
      · exact Or.inl (Or.inl h)
      · exact Or.inl (Or.inr h)
      · exact Or.inr h

end Partition

/-! ## C. Rigidity: a cross-part pair has codegree at most 10 -/

section Rigidity

variable {A C : Type*} [Fintype A] [DecidableEq A] [Fintype C] [DecidableEq C]

/-- The codegree contribution `m_X(a,b)`: total multiplicity of the classes of one
arm that contain both senders. -/
def mcodeg (p : C → ℕ) (cls : A → Finset C) (a b : A) : ℕ :=
  ∑ c ∈ cls a ∩ cls b, p c

/-- `m` is symmetric in the two senders. -/
theorem mcodeg_comm (p : C → ℕ) (cls : A → Finset C) (a b : A) :
    mcodeg p cls a b = mcodeg p cls b a := by
  rw [mcodeg, mcodeg, Finset.inter_comm]

/-- The weight of a sender in one arm. -/
def wt (p : C → ℕ) (cls : A → Finset C) (a : A) : ℕ :=
  ∑ c ∈ cls a, p c

/-- A sender of weight 4 has both its classes of multiplicity 2. -/
theorem classes_eq_two_of_wt_four (p : C → ℕ) (cls : A → Finset C)
    (hcard : ∀ a, (cls a).card = 2) (hp : ∀ c, p c = 2 ∨ p c = 3)
    (a : A) (h : wt p cls a = 4) : ∀ c ∈ cls a, p c = 2 := by
  classical
  intro c hc
  by_contra h2
  have hc3 : p c = 3 := by rcases hp c with h' | h' <;> omega
  have hgt : 0 < ((cls a).erase c).card := by
    have h1 := Finset.card_erase_of_mem hc
    have h2' := hcard a
    omega
  obtain ⟨c', hc'⟩ := Finset.card_pos.mp hgt
  have hc'2 : 2 ≤ p c' := by rcases hp c' with h' | h' <;> omega
  have hle : p c' ≤ ∑ x ∈ (cls a).erase c, p x :=
    Finset.single_le_sum (f := p) (fun _ _ => Nat.zero_le _) hc'
  have hsplit : wt p cls a = p c + ∑ x ∈ (cls a).erase c, p x := by
    rw [wt, Finset.add_sum_erase _ (f := p) hc]
  omega

/-- **Cross-part bound.**  If `a` has weight 4 and `b` has weight 5 in one arm,
then they contribute at most 2 to the codegree. -/
theorem mcodeg_le_two_of_four_five (p : C → ℕ) (cls : A → Finset C)
    (hcard : ∀ a, (cls a).card = 2) (hp : ∀ c, p c = 2 ∨ p c = 3)
    {a b : A} (ha : wt p cls a = 4) (hb : wt p cls b = 5) :
    mcodeg p cls a b ≤ 2 := by
  classical
  have hcls : ∀ c ∈ cls a, p c = 2 := classes_eq_two_of_wt_four p cls hcard hp a ha
  have hne : cls a ≠ cls b := by
    intro hh
    have hh' : wt p cls a = wt p cls b := by
      unfold wt
      rw [hh]
    omega
  have hlt : (cls a ∩ cls b).card < 2 := by
    have hle : (cls a ∩ cls b).card ≤ 2 := by
      have h1 := Finset.card_le_card (Finset.inter_subset_left : cls a ∩ cls b ⊆ cls a)
      have h2 : (cls a).card = 2 := hcard a
      omega
    rcases lt_or_eq_of_le hle with h | h
    · exact h
    · exfalso
      have heq : cls a ∩ cls b = cls a :=
        Finset.eq_of_subset_of_card_le Finset.inter_subset_left (by rw [h, hcard a])
      have hsub : cls a ⊆ cls b := by rw [← heq]; exact Finset.inter_subset_right
      exact hne (Finset.eq_of_subset_of_card_le hsub (by rw [hcard a, hcard b]))
  have hsum : mcodeg p cls a b = (cls a ∩ cls b).card * 2 := by
    rw [mcodeg, Finset.sum_congr rfl
      (fun c hc => hcls c (Finset.mem_of_mem_inter_left hc))]
    simp [Finset.sum_const, smul_eq_mul]
  omega

/-- **Rigidity of the cross-part case.**  In a no-singleton arm (classes of
multiplicity 2 or 3, every sender in exactly two classes), if the pair `{a,b}`
has `m_B = 5` and the two senders lie on opposite sides of the `A_C`/`A_D` split
(`a` of weight 4 and `b` of weight 5 in arm C, reversed in arm D), then
`|N_0(a) ∩ N_0(b)| = 1 + m_B + m_C + m_D ≤ 10`. -/
theorem codegree_le_ten_of_cross
    (pB : C → ℕ) (clsB : A → Finset C) (pC : C → ℕ) (clsC : A → Finset C)
    (pD : C → ℕ) (clsD : A → Finset C)
    (hcardB : ∀ a, (clsB a).card = 2) (hcardC : ∀ a, (clsC a).card = 2)
    (hcardD : ∀ a, (clsD a).card = 2)
    (hpB : ∀ c, pB c = 2 ∨ pB c = 3) (hpC : ∀ c, pC c = 2 ∨ pC c = 3)
    (hpD : ∀ c, pD c = 2 ∨ pD c = 3)
    {a b : A} (hB : mcodeg pB clsB a b = 5)
    (haC : wt pC clsC a = 4) (hbC : wt pC clsC b = 5)
    (haD : wt pD clsD a = 5) (hbD : wt pD clsD b = 4) :
    1 + mcodeg pB clsB a b + mcodeg pC clsC a b + mcodeg pD clsD a b ≤ 10 := by
  have h1 := mcodeg_le_two_of_four_five pC clsC hcardC hpC haC hbC
  have h2 := mcodeg_le_two_of_four_five pD clsD hcardD hpD hbD haD
  rw [mcodeg_comm pD clsD a b]
  omega

end Rigidity

end K58

#print axioms K58.template_class_triple_T
#print axioms K58.template_class_triple_U
#print axioms K58.card_four_of_sum
#print axioms K58.partition_law
#print axioms K58.classes_eq_two_of_wt_four
#print axioms K58.mcodeg_comm
#print axioms K58.mcodeg_le_two_of_four_five
#print axioms K58.codegree_le_ten_of_cross
