import Mathlib

/-!
# Semantic bridge for the K58 directional contact flags

The physical encoder uses fourteen marked-colour contacts after removing the
one distinguished contact.  These definitions are propositional renderings of
the exact DIMACS clauses.  No Ramsey statement is assumed or proved here.
-/

namespace ContactBridge

abbrev Hits := Fin 14 → Bool
abbrev Sites := Fin 15 → Bool

def contactCount (x : Hits) : Nat :=
  (Finset.univ.filter (fun j => x j = true)).card

/-- Executable evaluation of the fourteen `miss` clauses. -/
def missClausesHold (h : Bool) (x : Hits) : Bool :=
  (List.finRange 14).all (fun miss => !h || (List.finRange 14).any (fun j => j != miss && x j))

/-- Executable evaluation of all `C(14,2)` converse pair clauses. -/
def pairClausesHold (h : Bool) (x : Hits) : Bool :=
  (List.finRange 14).all (fun a => (List.finRange 14).all (fun b =>
    (a == b) || !x a || !x b || h))

/-- All physical high-flag clauses. -/
def FlagClauses (h : Bool) (x : Hits) : Bool :=
  missClausesHold h x && pairClausesHold h x

/-- Boolean biconditional between `h` and at least two additional contacts. -/
def flagMeaning (h : Bool) (x : Hits) : Bool :=
  h == decide (2 ≤ contactCount x)

lemma missClausesHold_true_iff (h : Bool) (x : Hits) :
    missClausesHold h x = true ↔ ∀ m : Fin 14, h = false ∨ ∃ j, j ≠ m ∧ x j = true := by
  simp only [missClausesHold, List.all_eq_true, Bool.or_eq_true, Bool.not_eq_true_eq_eq_false,
    List.any_eq_true, Bool.and_eq_true, bne_iff_ne, List.mem_finRange,
    forall_const, true_and]

lemma pairClausesHold_true_iff (h : Bool) (x : Hits) :
    pairClausesHold h x = true ↔ ∀ a b : Fin 14,
      a = b ∨ x a = false ∨ x b = false ∨ h = true := by
  simp only [pairClausesHold, List.all_eq_true, Bool.or_eq_true, beq_iff_eq,
    Bool.not_eq_true_eq_eq_false, List.mem_finRange, forall_const, or_assoc]

lemma missClausesHold_true_high (x : Hits) :
    missClausesHold true x = true ↔ 2 ≤ contactCount x := by
  rw [missClausesHold_true_iff]
  simp only [Bool.true_eq_false, false_or]
  constructor
  · intro h
    obtain ⟨a, _, ha⟩ := h 0
    obtain ⟨b, hba, hb⟩ := h a
    rw [contactCount, ← Nat.lt_iff_add_one_le, Finset.one_lt_card]
    exact ⟨a, by simp [ha], b, by simp [hb], Ne.symm hba⟩
  · intro h m
    rw [contactCount, ← Nat.lt_iff_add_one_le, Finset.one_lt_card] at h
    obtain ⟨a, ha, b, hb, hab⟩ := h
    have ha' : x a = true := (Finset.mem_filter.mp ha).2
    have hb' : x b = true := (Finset.mem_filter.mp hb).2
    by_cases hma : m = a
    · exact ⟨b, hma ▸ Ne.symm hab, hb'⟩
    · exact ⟨a, Ne.symm hma, ha'⟩

lemma pairClausesHold_false_low (x : Hits) :
    pairClausesHold false x = true ↔ contactCount x ≤ 1 := by
  rw [pairClausesHold_true_iff]
  simp only [Bool.false_eq_true, or_false]
  constructor
  · intro h
    by_contra! hc
    have hc : 2 ≤ contactCount x := by omega
    rw [contactCount, ← Nat.lt_iff_add_one_le, Finset.one_lt_card] at hc
    obtain ⟨a, ha, b, hb, hab⟩ := hc
    have ha' : x a = true := (Finset.mem_filter.mp ha).2
    have hb' : x b = true := (Finset.mem_filter.mp hb).2
    simpa [hab, ha', hb'] using h a b
  · intro h a b
    by_cases hab : a = b
    · exact Or.inl hab
    by_cases ha : x a = true <;> by_cases hb : x b = true
    · exfalso
      have hc : 2 ≤ contactCount x := by
        rw [contactCount, ← Nat.lt_iff_add_one_le, Finset.one_lt_card]
        exact ⟨a, by simp [ha], b, by simp [hb], hab⟩
      omega
    all_goals simp_all

lemma missClausesHold_false (x : Hits) : missClausesHold false x = true := by
  rw [missClausesHold_true_iff]
  intro m
  exact Or.inl rfl

lemma pairClausesHold_true (x : Hits) : pairClausesHold true x = true := by
  rw [pairClausesHold_true_iff]
  exact fun _ _ => Or.inr (Or.inr (Or.inr rfl))

lemma FlagClauses_true_iff (h : Bool) (x : Hits) :
    FlagClauses h x = true ↔ (h = true ↔ 2 ≤ contactCount x) := by
  cases h
  · simp [FlagClauses, missClausesHold_false, pairClausesHold_false_low]
  · simp [FlagClauses, missClausesHold_true_high, pairClausesHold_true]

theorem flagClauses_eq_meaning :
    ∀ (h : Bool) (x : Hits), FlagClauses h x = flagMeaning h x := by
  intro h x
  apply Bool.eq_iff_iff.mpr
  rw [FlagClauses_true_iff]
  cases h <;> simp [flagMeaning]

/-- The propositional reading of the preceding Boolean equality. -/
theorem flagClauses_true_iff :
    ∀ (h : Bool) (x : Hits),
      FlagClauses h x = true ↔ (h = true ↔ 2 ≤ contactCount x) := by
  intro h x
  rw [flagClauses_eq_meaning]
  cases h <;> simp [flagMeaning]

/-- Two contacts with `h=false` satisfy the forward miss clauses, but not all guards. -/
theorem one_sided_miss_clauses_do_not_converse :
    let x : Hits := fun j => decide (j.val < 2)
    missClausesHold false x = true ∧ FlagClauses false x = false := by
  decide

/-- The high sites represented by a vector of fifteen flags. -/
def highSites (high : Sites) : Finset (Fin 15) :=
  Finset.univ.filter (fun i => high i = true)

/--
The exact-layer lifting step.  `Eligible` is the independently checked
classifier predicate.  The second hypothesis says that every eligible exact
`k`-high pattern is refuted; no unlabelled-isomorphism transfer is hidden here.
The physical proof supplies the equality of `highSites high` with its pulled
back candidate before invoking this theorem.
-/
theorem floor_step {k : Nat} (high : Sites)
    (Eligible : Finset (Fin 15) → Prop)
    (previous : k ≤ (highSites high).card)
    (eligible : Eligible (highSites high))
    (no_exact_layer : ∀ S : Finset (Fin 15),
      S.card = k → Eligible S → highSites high ≠ S) :
    k + 1 ≤ (highSites high).card := by
  by_contra! not_next
  have exact_k : (highSites high).card = k := by omega
  exact no_exact_layer (highSites high) exact_k eligible rfl

/-- The H6-to-H7 instance, with the certified H≥6 floor as an explicit input. -/
theorem reverse_H7_of_previous_and_exact6 (high : Sites)
    (Eligible : Finset (Fin 15) → Prop)
    (previous_H6 : 6 ≤ (highSites high).card)
    (eligible : Eligible (highSites high))
    (no_exact6 : ∀ S : Finset (Fin 15),
      S.card = 6 → Eligible S → highSites high ≠ S) :
    7 ≤ (highSites high).card := by
  exact floor_step high Eligible previous_H6 eligible no_exact6

/--
Composition used by the checked local certificate chain. The five exact-layer
hypotheses correspond to 2415, 5455, 6435, 5005 and 3003 physical masks per
row. Eligibility of the actual high set and every symmetry pullback remains an
explicit premise; this theorem does not silently GLU unlabelled classes.
-/
theorem reverse_H11_of_exact6_to_exact10 (high : Sites)
    (Eligible : Finset (Fin 15) → Prop)
    (previous_H6 : 6 ≤ (highSites high).card)
    (eligible : Eligible (highSites high))
    (no_exact6 : ∀ S : Finset (Fin 15),
      S.card = 6 → Eligible S → highSites high ≠ S)
    (no_exact7 : ∀ S : Finset (Fin 15),
      S.card = 7 → Eligible S → highSites high ≠ S)
    (no_exact8 : ∀ S : Finset (Fin 15),
      S.card = 8 → Eligible S → highSites high ≠ S)
    (no_exact9 : ∀ S : Finset (Fin 15),
      S.card = 9 → Eligible S → highSites high ≠ S)
    (no_exact10 : ∀ S : Finset (Fin 15),
      S.card = 10 → Eligible S → highSites high ≠ S) :
    11 ≤ (highSites high).card := by
  have h7 := floor_step high Eligible previous_H6 eligible no_exact6
  have h8 := floor_step high Eligible h7 eligible no_exact7
  have h9 := floor_step high Eligible h8 eligible no_exact8
  have h10 := floor_step high Eligible h9 eligible no_exact9
  exact floor_step high Eligible h10 eligible no_exact10

#print axioms flagClauses_eq_meaning
#print axioms flagClauses_true_iff
#print axioms one_sided_miss_clauses_do_not_converse
#print axioms floor_step
#print axioms reverse_H11_of_exact6_to_exact10

end ContactBridge
