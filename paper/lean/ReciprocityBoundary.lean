import K58.Frontier
import K58.Ticket

namespace K58

/-- A directed walk in one colour, used only to expose the connectivity premise. -/
def ColourPath {V : Type*} (G : EdgeCol V 4) (c : Fin 4) (i j : V) : Prop :=
  Relation.ReflTransGen (fun a b => a ≠ b ∧ G.col a b = c) i j

/-- The finite common-two-critical conclusion, expressed with exactly its ambient degrees. -/
def CommonCriticalCertificate {V : Type*} [Fintype V] [DecidableEq V]
    (G : EdgeCol V 4) : Prop :=
  ∀ a b : Fin 4, a ≠ b → ∃ x, deg G x a ≤ 14 ∨ deg G x b ≤ 14

/-- A clique avoiding one colour has at most sixteen vertices. -/
theorem card_avoiding_colour_le_sixteen {V : Type*} [Fintype V] [DecidableEq V]
    (G : EdgeCol V 4) (hT : TriangleFree G) (c : Fin 4) (S : Finset V)
    (hS : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → G.col x y ≠ c) : S.card ≤ 16 := by
  by_contra hle
  simp only [not_le] at hle
  obtain ⟨T, hTS, hTcard⟩ := Finset.exists_subset_card_eq (show 17 ≤ S.card by omega)
  have hne : ∀ x ∈ T, ∀ y ∈ T, x ≠ y → G.col x y ≠ c := by
    intro x hx y hy hxy
    exact hS x (hTS hx) y (hTS hy) hxy
  have hcard : Fintype.card {d : Fin 4 // d ≠ c} = 3 := by
    have h1 : Fintype.card {d : Fin 4 // d = c} = 1 := Fintype.card_subtype_eq c
    have h2 := Fintype.card_subtype_compl (fun d : Fin 4 => d = c)
    rw [h1, Fintype.card_fin] at h2
    simp only [h2]
  let φ : {d : Fin 4 // d ≠ c} ≃ Fin 3 := Fintype.equivFinOfCardEq hcard
  let G3 : EdgeCol ↥T 3 :=
    { col := fun p q =>
        if hpq : p = q then 0
        else φ ⟨G.col p.1 q.1, hne p.1 p.2 q.1 q.2 (fun hh => hpq (Subtype.ext hh))⟩
      symm := by
        intro p q
        by_cases hpq : p = q
        · subst hpq; simp
        · have hqp : q ≠ p := Ne.symm hpq
          rw [dif_neg hpq, dif_neg hqp]
          congr 1
          exact Subtype.ext (G.symm p.1 q.1) }
  have h3 : TriangleFree G3 := by
    intro p q r hpq hqr hpr hmono
    have hpq2 : p.1 ≠ q.1 := fun hh => hpq (Subtype.ext hh)
    have hqr2 : q.1 ≠ r.1 := fun hh => hqr (Subtype.ext hh)
    have hpr2 : p.1 ≠ r.1 := fun hh => hpr (Subtype.ext hh)
    simp only [G3, dif_neg hpq, dif_neg hqr, dif_neg hpr] at hmono
    have e1 : G.col p.1 q.1 = G.col p.1 r.1 := by
      have hh := congrArg Subtype.val (φ.injective hmono.1)
      simpa using hh
    have e2 : G.col p.1 r.1 = G.col q.1 r.1 := by
      have hh := congrArg Subtype.val (φ.injective hmono.2)
      simpa using hh
    exact hT p.1 q.1 r.1 hpq2 hqr2 hpr2 ⟨e1, e2⟩
  exact three_colour_seventeen G3 (by simp [Fintype.card_coe, hTcard]) h3

/-- On 58 vertices every colour degree is at least nine. -/
theorem nine_le_deg {V : Type*} [Fintype V] [DecidableEq V]
    (G : EdgeCol V 4) (hT : TriangleFree G) (hV : Fintype.card V = 58)
    (i : V) (c : Fin 4) : 9 ≤ deg G i c := by
  have hsum := sum_deg_eq_card_sub_one G i
  rw [hV, Fin.sum_univ_four] at hsum
  have h0 := deg_le_sixteen G hT i 0
  have h1 := deg_le_sixteen G hT i 1
  have h2 := deg_le_sixteen G hT i 2
  have h3 := deg_le_sixteen G hT i 3
  fin_cases c <;> simp_all <;> omega

/-- The connectivity argument used by the new reciprocal-profile consequence. -/
theorem colourPath_all {V : Type*} [Fintype V] [DecidableEq V]
    (G : EdgeCol V 4) (hT : TriangleFree G) (hV : Fintype.card V = 58) :
    ∀ c i j, ColourPath G c i j := by
  intro c i j
  by_contra hij
  have step_of_mem {x y : V} (hy : y ∈ nbrC G x c) :
      ColourPath G c x y := by
    rw [mem_nbrC] at hy
    exact Relation.ReflTransGen.single ⟨Ne.symm hy.1, hy.2⟩
  have back_step_of_mem {x y : V} (hy : y ∈ nbrC G x c) :
      ColourPath G c y x := by
    rw [mem_nbrC] at hy
    exact Relation.ReflTransGen.single ⟨hy.1, by rw [G.symm]; exact hy.2⟩
  have hdisj : Disjoint (nbrC G i c) (nbrC G j c) := by
    rw [Finset.disjoint_left]
    intro x hxi hxj
    exact hij ((step_of_mem hxi).trans (back_step_of_mem hxj))
  have hcross : ∀ x ∈ nbrC G i c, ∀ y ∈ nbrC G j c, G.col x y ≠ c := by
    intro x hxi y hxj hxy
    have hxyne : x ≠ y := by
      intro heq
      subst y
      exact (Finset.disjoint_left.mp hdisj hxi) hxj
    apply hij
    exact (step_of_mem hxi).trans
      ((Relation.ReflTransGen.single ⟨hxyne, hxy⟩).trans (back_step_of_mem hxj))
  let S := nbrC G i c ∪ nbrC G j c
  have hS : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → G.col x y ≠ c := by
    intro x hx y hy hxy
    simp only [S, Finset.mem_union] at hx hy
    rcases hx with hxi | hxj <;> rcases hy with hyi | hyj
    · exact nbrC_indep G hT i c hxi hyi hxy
    · exact hcross x hxi y hyj
    · rw [G.symm x y]
      exact hcross y hyi x hxj
    · exact nbrC_indep G hT j c hxj hyj hxy
  have hcard := card_avoiding_colour_le_sixteen G hT c S hS
  have hcard_union : S.card = deg G i c + deg G j c := by
    simp only [S, Finset.card_union_of_disjoint hdisj, card_nbrC]
  have hi := nine_le_deg G hT hV i c
  have hj := nine_le_deg G hT hV j c
  omega

/-- Criticality is constant within each colour component, by reciprocity alone. -/
theorem criticality_constant_of_reciprocal {V : Type*} [Fintype V] [DecidableEq V]
    (G : EdgeCol V 4) (hR : Reciprocal G)
    (hconn : ∀ c i j, ColourPath G c i j) :
    ∀ c i j, (15 ≤ deg G i c ↔ 15 ≤ deg G j c) := by
  have forward : ∀ {c : Fin 4} {i j : V}, ColourPath G c i j →
      15 ≤ deg G i c → 15 ≤ deg G j c := by
    intro c i j path
    induction path with
    | refl => exact id
    | tail _ hab ih =>
        intro hi
        have hj := ih hi
        simpa only [hab.2] using crit_of_crit G hR hab.1 (by rwa [hab.2])
  intro c i j
  exact ⟨forward (hconn c i j), forward (hconn c j i)⟩

/-- The arithmetic/profile part of the new conditional implication.
    Connectivity and the finite certificate remain explicit premises. -/
theorem conditional_profile_boundary
    (G : EdgeCol (Fin 58) 4) (hT : TriangleFree G)
    (hconst : ∀ c i j, (15 ≤ deg G i c ↔ 15 ≤ deg G j c))
    (hcert : CommonCriticalCertificate G) (r : Fin 58) :
    (∃ c : Fin 4, (∀ i, 15 ≤ deg G i c) ∧
      ∀ b : Fin 4, b ≠ c → ∀ i, deg G i b ≤ 14) ∧
    (∃ σ : Equiv.Perm (Fin 4),
      [deg G r (σ 0), deg G r (σ 1), deg G r (σ 2), deg G r (σ 3)] =
        [15, 14, 14, 14] ∨
      [deg G r (σ 0), deg G r (σ 1), deg G r (σ 2), deg G r (σ 3)] =
        [16, 14, 14, 13]) := by
  obtain ⟨c, hc⟩ := exists_critical_colour G (by rfl) r
  have hone : ∃ c : Fin 4, (∀ i, 15 ≤ deg G i c) ∧
      ∀ b : Fin 4, b ≠ c → ∀ i, deg G i b ≤ 14 := by
    refine ⟨c, fun i => (hconst c r i).mp hc, ?_⟩
    intro b hbc i
    by_contra hlow
    have hbi : 15 ≤ deg G i b := by omega
    obtain ⟨x, hx | hx⟩ := hcert c b (Ne.symm hbc)
    · have hcx := (hconst c r x).mp hc
      omega
    · have hbx := (hconst b i x).mp hbi
      omega
  obtain ⟨c', hc'all, hother⟩ := hone
  refine ⟨⟨c', hc'all, hother⟩, ?_⟩
  obtain ⟨σ, hmem⟩ := root_degree_profile G hT r
  refine ⟨σ, ?_⟩
  have hunique : ∀ a b : Fin 4, a ≠ b →
      ¬ (15 ≤ deg G r a ∧ 15 ≤ deg G r b) := by
    intro a b hab h
    by_cases hac : a = c'
    · subst a
      have := hother b (Ne.symm hab) r
      omega
    · have := hother a hac r
      omega
  have hσ01 : σ 0 ≠ σ 1 := σ.injective.ne (by decide)
  simp [degreeProfiles58] at hmem
  rcases hmem with h | h | h | h | h | h | h | h | h | h | h
  · left
    rcases h with ⟨h0, h1, h2, h3⟩
    simp [h0, h1, h2, h3]
  · exfalso
    rcases h with ⟨h0, h1, h2, h3⟩
    exact hunique (σ 0) (σ 1) hσ01 ⟨by omega, by omega⟩
  · exfalso
    rcases h with ⟨h0, h1, h2, h3⟩
    exact hunique (σ 0) (σ 1) hσ01 ⟨by omega, by omega⟩
  · right
    rcases h with ⟨h0, h1, h2, h3⟩
    simp [h0, h1, h2, h3]
  all_goals
    exfalso
    rcases h with ⟨h0, h1, h2, h3⟩
    exact hunique (σ 0) (σ 1) hσ01 ⟨by omega, by omega⟩

/-- The full implication, with every non-reciprocity input still visible. -/
theorem reciprocal_conditional_profile_boundary
    (G : EdgeCol (Fin 58) 4) (hT : TriangleFree G) (hR : Reciprocal G)
    (hconn : ∀ c i j, ColourPath G c i j)
    (hcert : CommonCriticalCertificate G) (r : Fin 58) :
    (∃ c : Fin 4, (∀ i, 15 ≤ deg G i c) ∧
      ∀ b : Fin 4, b ≠ c → ∀ i, deg G i b ≤ 14) ∧
    (∃ σ : Equiv.Perm (Fin 4),
      [deg G r (σ 0), deg G r (σ 1), deg G r (σ 2), deg G r (σ 3)] =
        [15, 14, 14, 14] ∨
      [deg G r (σ 0), deg G r (σ 1), deg G r (σ 2), deg G r (σ 3)] =
        [16, 14, 14, 13]) :=
  conditional_profile_boundary G hT
    (criticality_constant_of_reciprocal G hR hconn) hcert r

/-- With the connectivity proved above, only the finite certificate remains a premise. -/
theorem reciprocal_profile_with_certificate
    (G : EdgeCol (Fin 58) 4) (hT : TriangleFree G) (hR : Reciprocal G)
    (hcert : CommonCriticalCertificate G) (r : Fin 58) :
    (∃ c : Fin 4, (∀ i, 15 ≤ deg G i c) ∧
      ∀ b : Fin 4, b ≠ c → ∀ i, deg G i b ≤ 14) ∧
    (∃ σ : Equiv.Perm (Fin 4),
      [deg G r (σ 0), deg G r (σ 1), deg G r (σ 2), deg G r (σ 3)] =
        [15, 14, 14, 14] ∨
      [deg G r (σ 0), deg G r (σ 1), deg G r (σ 2), deg G r (σ 3)] =
        [16, 14, 14, 13]) := by
  exact reciprocal_conditional_profile_boundary G hT hR
    (colourPath_all G hT (by rfl)) hcert r

#print axioms K58.criticality_constant_of_reciprocal
#print axioms K58.conditional_profile_boundary
#print axioms K58.reciprocal_conditional_profile_boundary
#print axioms K58.colourPath_all
#print axioms K58.reciprocal_profile_with_certificate

end K58
