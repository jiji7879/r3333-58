/-
K58/Ticket.lean -- direction d2 of swarm smwr8io45.

Audit of the "all tickets returned" (reciprocal-ticket) section:
the criticality sets `C_c` and what the hypotheses really give.

Main results (all axiom-clean, no `sorry`):

* `nbrC_subset_Crit`   : under (R) every colour-`c` neighbour of a `c`-critical
                         vertex is `c`-critical, i.e. `C_c` is closed under
                         `c`-adjacency (it is a union of colour-`c` components).
* `deg_add_deg_le_card` : for `i ∈ C_c` and `j ∈ N_c(i)`, `d_c(i) + d_c(j) ≤ |C_c|`.
                         The neighbourhoods are disjoint because `N_c(i)` is
                         `c`-independent -- this is where triangle-freeness enters.
* `crit_card_ge_thirty` : `C_c` nonempty ⟹ `30 ≤ |C_c|`.
                         (So the bound 30 is *correct*; the weaker "16" that comes
                         from closure plus minimum degree alone is not the truth.)
* `crit_card_ge_thirty_one` : some member of `C_c` has `c`-degree 16 ⟹ `31 ≤ |C_c|`.
* `crit_eq_univ`       : if every vertex has a `c`-critical colour-`c` neighbour
                         then colour `c` is critical at every vertex.
* `uniform_branch_zero_critical` : in the fully sending uniform branch of the
                         `(15,14,14,14)` root, (R) makes colour 0 critical at
                         every one of the 58 vertices.
* `ten_outside`        : hence every outside vertex has at least `15 - 5 = 10`
                         colour-0 neighbours outside the arm.
-/
import K58.Basic

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V] {k : ℕ}

/-- The colour-`c` neighbourhood of `i`. -/
noncomputable def nbrC (G : EdgeCol V k) (i : V) (c : Fin k) : Finset V :=
  Finset.univ.filter (fun j : V => j ≠ i ∧ G.col i j = c)

theorem mem_nbrC {G : EdgeCol V k} {i j : V} {c : Fin k} :
    j ∈ nbrC G i c ↔ j ≠ i ∧ G.col i j = c := by
  simp [nbrC]

theorem card_nbrC (G : EdgeCol V k) (i : V) (c : Fin k) :
    (nbrC G i c).card = deg G i c := rfl

/-- `C_c`: the set of vertices at which colour `c` is critical. -/
noncomputable def Crit (G : EdgeCol V k) (c : Fin k) : Finset V :=
  Finset.univ.filter (fun i : V => 15 ≤ deg G i c)

theorem mem_Crit {G : EdgeCol V k} {i : V} {c : Fin k} :
    i ∈ Crit G c ↔ 15 ≤ deg G i c := by
  simp [Crit]

/-- (R): every ticket is returned.  An edge is critical at one end exactly when
it is critical at the other. -/
def Reciprocal (G : EdgeCol V k) : Prop :=
  ∀ i j : V, i ≠ j → (15 ≤ deg G i (G.col i j) ↔ 15 ≤ deg G j (G.col i j))

/-- One direction of (R). -/
theorem crit_of_crit (G : EdgeCol V k) (hR : Reciprocal G) {i j : V} (hij : i ≠ j)
    (h : 15 ≤ deg G i (G.col i j)) : 15 ≤ deg G j (G.col i j) :=
  (hR i j hij).mp h

/-- **Closure**: under (R), `C_c` is closed under colour-`c` adjacency. -/
theorem nbrC_subset_Crit (G : EdgeCol V k) (hR : Reciprocal G) {c : Fin k} {i : V}
    (hi : i ∈ Crit G c) : nbrC G i c ⊆ Crit G c := by
  intro j hj
  rw [mem_nbrC] at hj
  obtain ⟨hji, hcol⟩ := hj
  rw [mem_Crit] at hi ⊢
  have hcrit : 15 ≤ deg G i (G.col i j) := by rw [hcol]; exact hi
  have h2 : 15 ≤ deg G j (G.col i j) := (hR i j (Ne.symm hji)).mp hcrit
  rwa [hcol] at h2

/-- In a triangle-free colouring the colour-`c` neighbourhood of `i` is
`c`-independent, so it is disjoint from the colour-`c` neighbourhood of any of
its members. -/
theorem nbrC_disjoint (G : EdgeCol V k) (hT : TriangleFree G) {c : Fin k} {i j : V}
    (hij : i ≠ j) (hc : G.col i j = c) : Disjoint (nbrC G i c) (nbrC G j c) := by
  rw [Finset.disjoint_left]
  intro w hwi hwj
  rw [mem_nbrC] at hwi hwj
  obtain ⟨hwi', hci⟩ := hwi
  obtain ⟨hwj', hcj⟩ := hwj
  exact hT i j w hij (Ne.symm hwj') (Ne.symm hwi') ⟨by rw [hc, hci], by rw [hci, hcj]⟩

/-- The sharp two-neighbour count: for `i` critical in colour `c` and
`j ∈ N_c(i)`, the two neighbourhoods are disjoint and both lie in `C_c`. -/
theorem deg_add_deg_le_card (G : EdgeCol V k) (hT : TriangleFree G) (hR : Reciprocal G)
    {c : Fin k} {i : V} (hi : i ∈ Crit G c) {j : V} (hj : j ∈ nbrC G i c) :
    deg G i c + deg G j c ≤ (Crit G c).card := by
  rw [mem_nbrC] at hj
  obtain ⟨hji, hcol⟩ := hj
  have hji' : i ≠ j := Ne.symm hji
  have hsub_i : nbrC G i c ⊆ Crit G c := nbrC_subset_Crit G hR hi
  have hjC : j ∈ Crit G c := hsub_i (mem_nbrC.mpr ⟨hji, hcol⟩)
  have hsub_j : nbrC G j c ⊆ Crit G c := nbrC_subset_Crit G hR hjC
  have hdisj : Disjoint (nbrC G i c) (nbrC G j c) := nbrC_disjoint G hT hji' hcol
  have hu : (nbrC G i c ∪ nbrC G j c).card = (nbrC G i c).card + (nbrC G j c).card :=
    Finset.card_union_of_disjoint hdisj
  have hsub : nbrC G i c ∪ nbrC G j c ⊆ Crit G c := Finset.union_subset hsub_i hsub_j
  have hle : (nbrC G i c).card + (nbrC G j c).card ≤ (Crit G c).card := by
    rw [← hu]; exact Finset.card_le_card hsub
  rw [card_nbrC, card_nbrC] at hle
  exact hle

/-- **The `30` bound**: a nonempty `C_c` has at least 30 vertices. -/
theorem crit_card_ge_thirty (G : EdgeCol V k) (hT : TriangleFree G) (hR : Reciprocal G)
    {c : Fin k} (hne : (Crit G c).Nonempty) : 30 ≤ (Crit G c).card := by
  obtain ⟨i, hi⟩ := hne
  have hdi : 15 ≤ deg G i c := mem_Crit.mp hi
  have hpos : 0 < (nbrC G i c).card := by
    rw [card_nbrC]; omega
  obtain ⟨j, hj⟩ := Finset.card_pos.mp hpos
  have h1 : deg G i c + deg G j c ≤ (Crit G c).card :=
    deg_add_deg_le_card G hT hR hi hj
  rw [mem_nbrC] at hj
  obtain ⟨hji, hcol⟩ := hj
  have hjC : j ∈ Crit G c := nbrC_subset_Crit G hR hi (mem_nbrC.mpr ⟨hji, hcol⟩)
  have hdj : 15 ≤ deg G j c := mem_Crit.mp hjC
  omega

/-- If a member of `C_c` has colour-`c` degree 16 then `|C_c| ≥ 31`. -/
theorem crit_card_ge_thirty_one (G : EdgeCol V k) (hT : TriangleFree G)
    (hR : Reciprocal G) {c : Fin k} {i : V} (hi : i ∈ Crit G c) (h16 : 16 ≤ deg G i c) :
    31 ≤ (Crit G c).card := by
  have hpos : 0 < (nbrC G i c).card := by
    rw [card_nbrC]; omega
  obtain ⟨j, hj⟩ := Finset.card_pos.mp hpos
  have h1 : deg G i c + deg G j c ≤ (Crit G c).card :=
    deg_add_deg_le_card G hT hR hi hj
  rw [mem_nbrC] at hj
  obtain ⟨hji, hcol⟩ := hj
  have hjC : j ∈ Crit G c := nbrC_subset_Crit G hR hi (mem_nbrC.mpr ⟨hji, hcol⟩)
  have hdj : 15 ≤ deg G j c := mem_Crit.mp hjC
  omega

/-- **Propagation**: if every vertex has a colour-`c` neighbour which is
colour-`c` critical, then colour `c` is critical everywhere. -/
theorem crit_eq_univ (G : EdgeCol V k) (hR : Reciprocal G) {c : Fin k}
    (h : ∀ i : V, ∃ j : V, j ≠ i ∧ G.col i j = c ∧ 15 ≤ deg G j c) :
    ∀ i : V, 15 ≤ deg G i c := by
  intro i
  obtain ⟨j, hji, hcol, hdeg⟩ := h i
  have hjC : j ∈ Crit G c := mem_Crit.mpr hdeg
  have hji' : i ≠ j := Ne.symm hji
  have hcol' : G.col j i = c := by rw [G.symm j i]; exact hcol
  have hiC : i ∈ Crit G c :=
    nbrC_subset_Crit G hR hjC (mem_nbrC.mpr ⟨hji', hcol'⟩)
  exact mem_Crit.mp hiC

/-- The same, in the shape used at a `(15,14,14,14)` root: hypotheses as in the
fully sending uniform branch, conclusion colour 0 critical everywhere. -/
theorem uniform_branch_zero_critical (G : EdgeCol V 4) (hR : Reciprocal G) (r : V)
    (hr : 15 ≤ deg G r (0 : Fin 4))
    (hA : ∀ a : V, a ∈ nbrC G r (0 : Fin 4) → 15 ≤ deg G a (0 : Fin 4))
    (hX : ∀ x : V, x ≠ r → x ∉ nbrC G r (0 : Fin 4) →
      (nbrC G x (0 : Fin 4) ∩ nbrC G r (0 : Fin 4)).Nonempty) :
    ∀ x : V, 15 ≤ deg G x (0 : Fin 4) := by
  refine crit_eq_univ G hR ?_
  intro x
  by_cases hxr : x = r
  · subst hxr
    have hpos : 0 < (nbrC G x (0 : Fin 4)).card := by
      rw [card_nbrC]; omega
    obtain ⟨a, ha⟩ := Finset.card_pos.mp hpos
    exact ⟨a, (mem_nbrC.mp ha).1, (mem_nbrC.mp ha).2, hA a ha⟩
  · by_cases hxn : x ∈ nbrC G r (0 : Fin 4)
    · refine ⟨r, ?_, ?_, hr⟩
      · rw [mem_nbrC] at hxn; exact Ne.symm hxn.1
      · rw [G.symm x r]; exact (mem_nbrC.mp hxn).2
    · obtain ⟨a, ha⟩ := hX x hxr hxn
      rw [Finset.mem_inter] at ha
      obtain ⟨hax, har⟩ := ha
      exact ⟨a, (mem_nbrC.mp hax).1, (mem_nbrC.mp hax).2, hA a har⟩

/-- Consequence for the word model: a colour-0 critical outside vertex has at
least `15 - 5 = 10` colour-0 neighbours outside the arm `A`. -/
theorem ten_outside (G : EdgeCol V k) {c : Fin k} {x : V} (A : Finset V) (_hxA : x ∉ A)
    (hdeg : 15 ≤ deg G x c) (hm : (nbrC G x c ∩ A).card ≤ 5) :
    10 ≤ (nbrC G x c \ A).card := by
  have h1 : (nbrC G x c \ A).card + (nbrC G x c ∩ A).card = (nbrC G x c).card :=
    Finset.card_sdiff_add_card_inter _ _
  rw [card_nbrC] at h1
  omega

/-- The colour-`c` neighbourhood of `r` carries no colour-`c` edge: the root
colour is *automatically* forbidden inside the arm.  (This is the constraint the
pair-level word model assumes, so it needs no separate hypothesis.) -/
theorem nbrC_indep (G : EdgeCol V k) (hT : TriangleFree G) (r : V) (c : Fin k)
    {a b : V} (ha : a ∈ nbrC G r c) (hb : b ∈ nbrC G r c) (hab : a ≠ b) :
    G.col a b ≠ c := by
  intro h
  rw [mem_nbrC] at ha hb
  exact hT r a b (Ne.symm ha.1) hab (Ne.symm hb.1)
    ⟨by rw [ha.2, hb.2], by rw [hb.2, h]⟩

/-- The colour degrees at a vertex sum to `|V| - 1`. -/
theorem sum_deg_eq_card_sub_one (G : EdgeCol V k) (i : V) :
    ∑ c : Fin k, deg G i c = Fintype.card V - 1 := by
  have key : Fintype.card V - 1 = ∑ c : Fin k, (nbrC G i c).card := by
    have hcard : (Finset.univ.erase i).card = ∑ c : Fin k, (nbrC G i c).card := by
      rw [Finset.card_eq_sum_card_fiberwise (t := Finset.univ)
        (f := fun j : V => G.col i j) (fun x _ => Finset.mem_univ _)]
      refine Finset.sum_congr rfl fun c _ => ?_
      congr 1
      ext j
      simp [nbrC, Finset.mem_erase, and_comm]
    rwa [Finset.card_erase_of_mem (Finset.mem_univ i), Finset.card_univ] at hcard
  have h : (∑ c : Fin k, (nbrC G i c).card) = ∑ c : Fin k, deg G i c :=
    Finset.sum_congr rfl fun c _ => card_nbrC G i c
  rw [key, h]

/-- **Weak reading of "one colour is critical at every vertex"**: at `n = 58`,
*every* vertex has a critical colour, with no ticket hypothesis at all.  It is
pigeonhole: `57 = 4·14 + 1`. -/
theorem exists_critical_colour (G : EdgeCol V 4) (hV : Fintype.card V = 58) (i : V) :
    ∃ c : Fin 4, 15 ≤ deg G i c := by
  by_contra h
  push Not at h
  have h2 : ∑ c : Fin 4, deg G i c ≤ 4 * 14 :=
    calc ∑ c : Fin 4, deg G i c ≤ ∑ _c : Fin 4, 14 :=
          Finset.sum_le_sum fun c _ => by have := h c; omega
      _ = 4 * 14 := by simp
  rw [sum_deg_eq_card_sub_one, hV] at h2
  omega

/-- Every member of a `30`-vertex `C_c` has colour-`c` degree exactly 15. -/
theorem deg_eq_fifteen_of_card_thirty (G : EdgeCol V k) (hT : TriangleFree G)
    (hR : Reciprocal G) {c : Fin k} (hcard : (Crit G c).card = 30) {u : V}
    (hu : u ∈ Crit G c) : deg G u c = 15 := by
  have hpos : 0 < (nbrC G u c).card := by
    have := mem_Crit.mp hu
    rw [card_nbrC]; omega
  obtain ⟨v, hv⟩ := Finset.card_pos.mp hpos
  have h1 : deg G u c + deg G v c ≤ (Crit G c).card := deg_add_deg_le_card G hT hR hu hv
  have hvC : v ∈ Crit G c := nbrC_subset_Crit G hR hu hv
  have hdv : 15 ≤ deg G v c := mem_Crit.mp hvC
  have hdu : 15 ≤ deg G u c := mem_Crit.mp hu
  omega

/-- **The equality case**: a `C_c` of exactly 30 vertices splits into two
15-sets which are each colour-`c` independent, and the colour-`c` graph between
them is complete.  So `C_c` carries `K_{15,15}` in colour `c` and nothing else,
which is what the control object `k30_control_C15x15.col` realises. -/
theorem crit_thirty_structure (G : EdgeCol V k) (hT : TriangleFree G) (hR : Reciprocal G)
    {c : Fin k} (hcard : (Crit G c).card = 30) {u : V} (hu : u ∈ Crit G c) :
    (nbrC G u c).card = 15 ∧ (Crit G c \ nbrC G u c).card = 15 ∧
      (∀ v ∈ nbrC G u c, nbrC G v c = Crit G c \ nbrC G u c) ∧
      (∀ w ∈ Crit G c \ nbrC G u c, nbrC G w c = nbrC G u c) := by
  have hu15 : deg G u c = 15 := deg_eq_fifteen_of_card_thirty G hT hR hcard hu
  have hsub : nbrC G u c ⊆ Crit G c := nbrC_subset_Crit G hR hu
  have hNcard : (nbrC G u c).card = 15 := by rw [card_nbrC]; exact hu15
  have hcompl : (Crit G c \ nbrC G u c).card = 15 := by
    have h1 : (Crit G c \ nbrC G u c).card
        = (Crit G c).card - (nbrC G u c ∩ Crit G c).card := Finset.card_sdiff
    rw [Finset.inter_eq_left.mpr hsub, hcard, hNcard] at h1
    omega
  have key : ∀ v ∈ nbrC G u c, nbrC G v c = Crit G c \ nbrC G u c := by
    intro v hv
    have hvC : v ∈ Crit G c := hsub hv
    have hv15 : deg G v c = 15 := deg_eq_fifteen_of_card_thirty G hT hR hcard hvC
    have hsubv : nbrC G v c ⊆ Crit G c := nbrC_subset_Crit G hR hvC
    rw [mem_nbrC] at hv
    obtain ⟨hvu, hcol⟩ := hv
    have hdisj : Disjoint (nbrC G u c) (nbrC G v c) := nbrC_disjoint G hT (Ne.symm hvu) hcol
    have hsub' : nbrC G v c ⊆ Crit G c \ nbrC G u c := by
      intro z hz
      exact Finset.mem_sdiff.mpr ⟨hsubv hz, Finset.disjoint_right.mp hdisj hz⟩
    have hcards : (nbrC G v c).card = (Crit G c \ nbrC G u c).card := by
      rw [card_nbrC, hv15, hcompl]
    exact Finset.eq_of_subset_of_card_le hsub' (le_of_eq hcards.symm)
  refine ⟨hNcard, hcompl, key, ?_⟩
  intro w hw
  rw [Finset.mem_sdiff] at hw
  obtain ⟨hwC, hwu⟩ := hw
  have hw15 : deg G w c = 15 := deg_eq_fifteen_of_card_thirty G hT hR hcard hwC
  have hsubw : nbrC G u c ⊆ nbrC G w c := by
    intro v hv
    have hwv : w ∈ nbrC G v c := by
      rw [key v hv]
      exact Finset.mem_sdiff.mpr ⟨hwC, hwu⟩
    rw [mem_nbrC] at hwv ⊢
    exact ⟨Ne.symm hwv.1, by rw [G.symm w v]; exact hwv.2⟩
  have hcards : (nbrC G w c).card = (nbrC G u c).card := by
    rw [card_nbrC, card_nbrC, hw15, hu15]
  exact (Finset.eq_of_subset_of_card_le hsubw (le_of_eq hcards)).symm



/-!  ## Weakening the reciprocity hypothesis (d2, second round)

The question put to me: `uniform_branch_zero_critical` assumes the *global*
reciprocity (R); which instances of (R) does its proof actually use, and does
replacing (R) by "the colour-0 tickets sent from the arm are returned" make the
theorem cover strictly more roots?

Answer, proved here: the proof uses (R) at exactly one edge per vertex (the
colour-0 edge from a neighbour already known to be 0-critical), and in the
branch those edges' hypotheses are *always satisfied* (`d_0 a = 15` for
`a ∈ A`).  So the weakened hypothesis is **equivalent to the conclusion**
(`arm_returns_iff_zero_critical`): it buys nothing, and no theorem of this shape
can cover an extra root.  What *is* weaker, and non-vacuous, is the hypothesis
of the `30` bound: it needs closure in **one** colour only, and only in the
forward direction (`crit_card_ge_thirty_of_color`), i.e. one quarter of (R).
-/

/-- (R) restated: for every colour `c`, no colour-`c` edge crosses the cut
`(C_c, V \ C_c)`. -/
theorem reciprocal_iff_cuts (G : EdgeCol V k) :
    Reciprocal G ↔ ∀ (c : Fin k) (i j : V), i ≠ j → G.col i j = c →
      (15 ≤ deg G i c ↔ 15 ≤ deg G j c) := by
  constructor
  · intro hR c i j hij hcol
    rw [← hcol]
    exact hR i j hij
  · intro h i j hij
    exact h (G.col i j) i j hij rfl

/-- The `c`-th conjunct of (R): no colour-`c` edge crosses the cut
`(C_c, V \ C_c)`.  Quantified over ordered pairs, so it gives both directions. -/
def ColorClosed (G : EdgeCol V k) (c : Fin k) : Prop :=
  ∀ i j : V, i ≠ j → G.col i j = c → 15 ≤ deg G i c → 15 ≤ deg G j c

theorem colorClosed_of_reciprocal (G : EdgeCol V k) (hR : Reciprocal G) (c : Fin k) :
    ColorClosed G c := by
  intro i j hij hcol hdeg
  have h := (reciprocal_iff_cuts G).mp hR c i j hij hcol
  exact h.mp hdeg

/-- **The `30` bound needs one quarter of (R)**: closure in one colour. -/
theorem nbrC_subset_Crit_of_colorClosed (G : EdgeCol V k) (hR : ColorClosed G c)
    {i : V} (hi : i ∈ Crit G c) : nbrC G i c ⊆ Crit G c := by
  intro j hj
  rw [mem_nbrC] at hj
  obtain ⟨hji, hcol⟩ := hj
  rw [mem_Crit] at hi ⊢
  exact hR i j (Ne.symm hji) hcol hi

/-- **The `30` bound needs one quarter of (R)**: only the `c`-th conjunct. -/
theorem crit_card_ge_thirty_of_colorClosed (G : EdgeCol V k) (hT : TriangleFree G)
    (hR : ColorClosed G c) (hne : (Crit G c).Nonempty) : 30 ≤ (Crit G c).card := by
  obtain ⟨i, hi⟩ := hne
  have hdi : 15 ≤ deg G i c := mem_Crit.mp hi
  have hpos : 0 < (nbrC G i c).card := by rw [card_nbrC]; omega
  obtain ⟨j, hj⟩ := Finset.card_pos.mp hpos
  rw [mem_nbrC] at hj
  obtain ⟨hji, hcol⟩ := hj
  have hji' : i ≠ j := Ne.symm hji
  have hsub_i : nbrC G i c ⊆ Crit G c := nbrC_subset_Crit_of_colorClosed G hR hi
  have hjC : j ∈ Crit G c := hsub_i (mem_nbrC.mpr ⟨hji, hcol⟩)
  have hsub_j : nbrC G j c ⊆ Crit G c := nbrC_subset_Crit_of_colorClosed G hR hjC
  have hdisj : Disjoint (nbrC G i c) (nbrC G j c) := nbrC_disjoint G hT hji' hcol
  have hu : (nbrC G i c ∪ nbrC G j c).card = (nbrC G i c).card + (nbrC G j c).card :=
    Finset.card_union_of_disjoint hdisj
  have hsub : nbrC G i c ∪ nbrC G j c ⊆ Crit G c := Finset.union_subset hsub_i hsub_j
  have hle : (nbrC G i c).card + (nbrC G j c).card ≤ (Crit G c).card := by
    rw [← hu]; exact Finset.card_le_card hsub
  rw [card_nbrC, card_nbrC] at hle
  have hdj : 15 ≤ deg G j c := mem_Crit.mp hjC
  omega

/-- **Propagation with the weakened hypothesis**: only the colour-0 tickets sent
*from the arm* need to be returned. -/
theorem zero_critical_of_arm_returns (G : EdgeCol V 4) (r : V)
    (hr : 15 ≤ deg G r (0 : Fin 4))
    (hA : ∀ a : V, a ∈ nbrC G r (0 : Fin 4) → 15 ≤ deg G a (0 : Fin 4))
    (hret : ∀ a x : V, a ∈ nbrC G r (0 : Fin 4) → x ≠ a → G.col a x = 0 →
      (15 ≤ deg G a (0 : Fin 4) → 15 ≤ deg G x (0 : Fin 4)))
    (hX : ∀ x : V, x ≠ r → x ∉ nbrC G r (0 : Fin 4) →
      (nbrC G x (0 : Fin 4) ∩ nbrC G r (0 : Fin 4)).Nonempty) :
    ∀ x : V, 15 ≤ deg G x (0 : Fin 4) := by
  intro x
  by_cases hxr : x = r
  · subst hxr; exact hr
  by_cases hxn : x ∈ nbrC G r (0 : Fin 4)
  · exact hA x hxn
  · obtain ⟨a, ha⟩ := hX x hxr hxn
    rw [Finset.mem_inter] at ha
    obtain ⟨hax, har⟩ := ha
    have hcol : G.col a x = 0 := by rw [G.symm a x]; exact (mem_nbrC.mp hax).2
    have hax' : x ≠ a := Ne.symm (mem_nbrC.mp hax).1
    exact hret a x har hax' hcol (hA a har)

/-- **The weakening is vacuous**: over the branch hypotheses, "the colour-0
tickets sent from the arm are returned" is *equivalent* to the conclusion.  One
direction is `zero_critical_of_arm_returns`; the other is immediate, because in
the branch every arm vertex is 0-critical, so returning `a`'s ticket to `x`
asserts exactly `15 ≤ deg G x 0`. -/
theorem arm_returns_iff_zero_critical (G : EdgeCol V 4) (r : V)
    (hr : 15 ≤ deg G r (0 : Fin 4))
    (hA : ∀ a : V, a ∈ nbrC G r (0 : Fin 4) → 15 ≤ deg G a (0 : Fin 4))
    (hX : ∀ x : V, x ≠ r → x ∉ nbrC G r (0 : Fin 4) →
      (nbrC G x (0 : Fin 4) ∩ nbrC G r (0 : Fin 4)).Nonempty) :
    (∀ a x : V, a ∈ nbrC G r (0 : Fin 4) → x ≠ a → G.col a x = 0 →
        (15 ≤ deg G a (0 : Fin 4) → 15 ≤ deg G x (0 : Fin 4)))
      ↔ ∀ x : V, 15 ≤ deg G x (0 : Fin 4) := by
  constructor
  · intro hret
    exact zero_critical_of_arm_returns G r hr hA hret hX
  · intro h a x _ _ _ _; exact h x

/-- (R) is exactly the conjunction of its four one-colour parts. -/
theorem reciprocal_iff_all_colorClosed (G : EdgeCol V k) :
    Reciprocal G ↔ ∀ c : Fin k, ColorClosed G c := by
  constructor
  · intro hR c
    exact colorClosed_of_reciprocal G hR c
  · intro h i j hij
    constructor
    · intro hi
      exact h (G.col i j) i j hij rfl hi
    · intro hj
      exact h (G.col i j) j i (Ne.symm hij) (G.symm j i) hj

/-- **The dichotomy the cover can use.**  At `n = 58`, a vertex whose colour-0
degree is at most 14 is critical in one of the other three colours: `43 = 57 - 14
> 3 · 14`.  So the failure of "colour 0 critical here" is never cheap — it pins
a second critical class, which (under `ColorClosed` in that colour) then has at
least 30 vertices. -/
theorem exists_critical_of_not_zero (G : EdgeCol V 4) (hV : Fintype.card V = 58)
    (x : V) (h0 : deg G x (0 : Fin 4) ≤ 14) :
    ∃ c : Fin 4, c ≠ 0 ∧ 15 ≤ deg G x c := by
  by_contra h
  push Not at h
  have hsum := sum_deg_eq_card_sub_one G x
  rw [hV, Fin.sum_univ_four] at hsum
  have h1 : deg G x 1 ≤ 14 := by have := h 1 (by decide); omega
  have h2 : deg G x 2 ≤ 14 := by have := h 2 (by decide); omega
  have h3 : deg G x 3 ≤ 14 := by have := h 3 (by decide); omega
  omega

/-- **The usable dichotomy.**  At `n = 58`, if an outside vertex is not
colour-0 critical then it is critical in an ordinary colour, and then that
colour's part of (R) gives a second class of at least 30 vertices. -/
theorem second_class_of_not_zero (G : EdgeCol V 4) (hT : TriangleFree G)
    (hV : Fintype.card V = 58) (x : V) (h0 : deg G x (0 : Fin 4) ≤ 14)
    (hR : ∀ c : Fin 4, ColorClosed G c) :
    ∃ c : Fin 4, c ≠ 0 ∧ 15 ≤ deg G x c ∧ 30 ≤ (Crit G c).card := by
  obtain ⟨c, hc0, hcx⟩ := exists_critical_of_not_zero G hV x h0
  exact ⟨c, hc0, hcx, crit_card_ge_thirty_of_colorClosed G hT (hR c)
    ⟨x, mem_Crit.mpr hcx⟩⟩

end K58
