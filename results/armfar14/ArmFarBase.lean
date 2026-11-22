/-
K58 supplement (swarm smwr0lr3q, member m4): the two load-bearing arms of the
Family-A argument that the development names but does not contain.

`Mixture.lean`'s docstring promises an `interface` theorem (the double count
behind the interface count `sum_x m_x = 210 + t`) and it is not there; `deg_le_sixteen`
proves the degree cap only for a literal colour class.  Here:

* `indep_le_sixteen`  : an arbitrary `c`-independent set has at most 16 points
                        (`deg_le_sixteen` for every `c`-free set, not just a class);
* `interface_sum`     : `|A| + #{c-edges A -- outside}` counted from the outside
                        equals `sum_{a in A} deg a c`, for `A = nbr G r c`;
* `interface`         : the record's form, `sum_x m_x = sum_{a in A} (deg a c - 1)`;
* `saturation_clique` : `|X| >= 15` -> the set of points with no `c`-edge into `X`
                        is a `c`-clique, hence has at most 2 points;
* `saturation`        : `|X| >= 14` -> that set has at most 5 points.

`X` is only required to be `c`-independent, so these are the general bounds of
the review's "arm-set saturation" paragraph, which were previously checked by
hand on objects only.
-/
import K58.Corollaries

namespace K58

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ## An arbitrary `c`-free set has at most 16 points -/

/-- A finite point set with no colour-`c` edge inside has at most 16 points,
since it carries a triangle-free 3-colouring and `R(3,3,3) ≤ 17`. -/
theorem indep_le_sixteen (G : EdgeCol V 4) (h : TriangleFree G) (c : Fin 4)
    (T : Finset V) (hT : ∀ x ∈ T, ∀ y ∈ T, x ≠ y → G.col x y ≠ c) : T.card ≤ 16 := by
  by_contra hle
  simp only [not_le] at hle
  obtain ⟨U, hUT, hUcard⟩ := Finset.exists_subset_card_eq (show 17 ≤ T.card by omega)
  have hU17 : U.card = 17 := hUcard
  have hne : ∀ x ∈ U, ∀ y ∈ U, x ≠ y → G.col x y ≠ c := fun x hx y hy hxy =>
    hT x (hUT hx) y (hUT hy) hxy
  -- the three colours other than `c`, indexed by `Fin 3`
  have hcard : Fintype.card {d : Fin 4 // d ≠ c} = 3 := by
    have h1 : Fintype.card {d : Fin 4 // d = c} = 1 := Fintype.card_subtype_eq c
    have h2 := Fintype.card_subtype_compl (fun d : Fin 4 => d = c)
    rw [h1, Fintype.card_fin] at h2
    simp only [h2]
  let φ : {d : Fin 4 // d ≠ c} ≃ Fin 3 := Fintype.equivFinOfCardEq hcard
  let G3 : EdgeCol ↥U 3 :=
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
    have hpq' : ¬ (p = q) := hpq
    have hqr' : ¬ (q = r) := hqr
    have hpr' : ¬ (p = r) := hpr
    simp only [G3, dif_neg hpq', dif_neg hqr', dif_neg hpr'] at hmono
    have e1 : G.col p.1 q.1 = G.col p.1 r.1 := by
      have hh := congrArg Subtype.val (φ.injective hmono.1)
      simpa using hh
    have e2 : G.col p.1 r.1 = G.col q.1 r.1 := by
      have hh := congrArg Subtype.val (φ.injective hmono.2)
      simpa using hh
    have hpq2 : p.1 ≠ q.1 := fun hh => hpq (Subtype.ext hh)
    have hqr2 : q.1 ≠ r.1 := fun hh => hqr (Subtype.ext hh)
    have hpr2 : p.1 ≠ r.1 := fun hh => hpr (Subtype.ext hh)
    exact h p.1 q.1 r.1 hpq2 hqr2 hpr2 ⟨e1, e2⟩
  exact three_colour_seventeen G3 (by simp [Fintype.card_coe, hU17]) h3

/-- The colour class form, recovered. -/
theorem deg_le_sixteen' (G : EdgeCol V 4) (h : TriangleFree G) (i : V) (c : Fin 4) :
    deg G i c ≤ 16 := by
  have hT : ∀ x ∈ nbr G i c, ∀ y ∈ nbr G i c, x ≠ y → G.col x y ≠ c :=
    fun x hx y hy hxy => nbr_indep G h i c x hx y hy hxy
  have := indep_le_sixteen G h c (nbr G i c) hT
  rwa [nbr_card] at this

/-! ## The interface double count -/

/-- **Interface identity, subtraction-free form.**  For `A = N_c(r)`, the
number of colour-`c` edges from `A` to the rest of the graph equals
`sum_{a in A} deg a c - |A|`; here it is written so that no subtraction of
cardinalities is needed. -/
theorem interface_sum (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4) :
    ∑ a ∈ nbr G r c, deg G a c
      = (nbr G r c).card
        + ∑ x ∈ (Finset.univ \ (nbr G r c ∪ {r})), ((nbr G x c) ∩ (nbr G r c)).card := by
  classical
  -- the double count, before splitting off the arm
  have hswap : ∑ x : V, ((nbr G x c) ∩ (nbr G r c)).card
      = ∑ a ∈ nbr G r c, deg G a c := by
    have h1 : ∀ x : V, ((nbr G x c) ∩ (nbr G r c)).card
        = ∑ a ∈ nbr G r c, if a ∈ nbr G x c then 1 else 0 := by
      intro x
      rw [Finset.card_eq_sum_ones, ← Finset.sum_filter, Finset.filter_mem_eq_inter,
        Finset.inter_comm]
    calc ∑ x : V, ((nbr G x c) ∩ (nbr G r c)).card
        = ∑ x : V, ∑ a ∈ nbr G r c, if a ∈ nbr G x c then (1 : ℕ) else 0 :=
          Finset.sum_congr rfl fun x _ => h1 x
      _ = ∑ a ∈ nbr G r c, ∑ x : V, if a ∈ nbr G x c then (1 : ℕ) else 0 :=
          Finset.sum_comm
      _ = ∑ a ∈ nbr G r c, ∑ x : V, if x ∈ nbr G a c then (1 : ℕ) else 0 := by
          refine Finset.sum_congr rfl ?_
          intro a _
          refine Finset.sum_congr rfl ?_
          intro x _
          have hiff : (a ∈ nbr G x c) ↔ (x ∈ nbr G a c) := by
            simp only [nbr, Finset.mem_filter, Finset.mem_univ, true_and]
            constructor
            · rintro ⟨hax, hcol⟩
              exact ⟨hax.symm, by rw [G.symm a x]; exact hcol⟩
            · rintro ⟨hxa, hcol⟩
              exact ⟨hxa.symm, by rw [G.symm x a]; exact hcol⟩
          by_cases hh : a ∈ nbr G x c
          · rw [if_pos hh, if_pos (hiff.mp hh)]
          · rw [if_neg hh, if_neg (fun hc => hh (hiff.mpr hc))]
      _ = ∑ a ∈ nbr G r c, deg G a c := by
          refine Finset.sum_congr rfl ?_
          intro a _
          rw [← nbr_card, Finset.card_eq_sum_ones, ← Finset.sum_filter,
            Finset.filter_mem_eq_inter, Finset.univ_inter]
  -- `r` is not in its own arm
  have hrA : r ∉ nbr G r c := by simp [nbr]
  -- the arm contributes nothing
  have hzero : ∑ x ∈ nbr G r c, ((nbr G x c) ∩ (nbr G r c)).card = 0 := by
    refine Finset.sum_eq_zero ?_
    intro x hx
    have hempty : (nbr G x c) ∩ (nbr G r c) = ∅ := by
      refine Finset.eq_empty_iff_forall_notMem.mpr ?_
      intro y hy
      rw [Finset.mem_inter] at hy
      obtain ⟨hy1, hy2⟩ := hy
      simp only [nbr, Finset.mem_filter, Finset.mem_univ, true_and] at hy1
      exact nbr_indep G h r c x hx y hy2 (Ne.symm hy1.1) hy1.2
    rw [hempty, Finset.card_empty]
  -- `r` itself sees the whole arm
  have hr : ((nbr G r c) ∩ (nbr G r c)).card = (nbr G r c).card := by
    rw [Finset.inter_self]
  -- split the total sum at the arm and at `r`
  have hsplit : ∑ x : V, ((nbr G x c) ∩ (nbr G r c)).card
      = (∑ x ∈ nbr G r c, ((nbr G x c) ∩ (nbr G r c)).card)
        + ((nbr G r c) ∩ (nbr G r c)).card
        + ∑ x ∈ (Finset.univ \ (nbr G r c ∪ {r})), ((nbr G x c) ∩ (nbr G r c)).card := by
    have h1 := Finset.sum_sdiff (s₁ := nbr G r c ∪ {r})
      (s₂ := (Finset.univ : Finset V))
      (f := fun x => ((nbr G x c) ∩ (nbr G r c)).card) (Finset.subset_univ _)
    have hdisj : Disjoint (nbr G r c) ({r} : Finset V) := by
      rw [Finset.disjoint_singleton_right]
      exact hrA
    have h2 : ∑ x ∈ (nbr G r c ∪ {r}), ((nbr G x c) ∩ (nbr G r c)).card
        = (∑ x ∈ nbr G r c, ((nbr G x c) ∩ (nbr G r c)).card)
          + ((nbr G r c) ∩ (nbr G r c)).card := by
      rw [Finset.sum_union hdisj, Finset.sum_singleton]
    rw [h2] at h1
    omega
  rw [← hswap, hsplit, hzero, hr]
  omega

/-- **Interface identity** in the record's form: with `A = N_c(r)` and
`m_x = |N_c(x) ∩ A|` for `x` outside `A ∪ {r}`,
`sum_x m_x = sum_{a in A} (deg a c - 1)`. -/
theorem interface (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4) :
    ∑ x ∈ (Finset.univ \ (nbr G r c ∪ {r})), ((nbr G x c) ∩ (nbr G r c)).card
      = ∑ a ∈ nbr G r c, (deg G a c - 1) := by
  classical
  have hmain := interface_sum G h r c
  have hpos : ∀ a ∈ nbr G r c, 1 ≤ deg G a c := by
    intro a ha
    simp only [nbr, Finset.mem_filter, Finset.mem_univ, true_and] at ha
    have hmem : r ∈ Finset.univ.filter (fun j : V => j ≠ a ∧ G.col a j = c) := by
      simp only [Finset.mem_filter, Finset.mem_univ, true_and]
      exact ⟨(Ne.symm ha.1), by rw [G.symm a r]; exact ha.2⟩
    have := Finset.card_pos.mpr ⟨r, hmem⟩
    rwa [← deg] at this
  have htsub : ∑ a ∈ nbr G r c, (deg G a c - 1)
      = (∑ a ∈ nbr G r c, deg G a c) - (nbr G r c).card := by
    rw [Finset.card_eq_sum_ones]
    exact Finset.sum_tsub_distrib _ (fun a ha => hpos a ha)
  rw [htsub, hmain]
  omega



/-! ## Arm-set saturation -/

/-- The points outside `X` with no colour-`c` edge into `X`. -/
def armFar (G : EdgeCol V 4) (X : Finset V) (c : Fin 4) : Finset V :=
  Finset.univ.filter (fun y => y ∉ X ∧ ∀ x ∈ X, G.col y x ≠ c)

theorem mem_armFar {G : EdgeCol V 4} {X : Finset V} {c : Fin 4} {y : V} :
    y ∈ armFar G X c ↔ y ∉ X ∧ ∀ x ∈ X, G.col y x ≠ c := by
  simp [armFar]

/-- `X ∪ Z` is `c`-free, and therefore has at most 16 points. -/
theorem union_free_le_sixteen (G : EdgeCol V 4) (h : TriangleFree G) {X Z : Finset V}
    {c : Fin 4}
    (hXZ : ∀ y ∈ Z, y ∉ X)
    (hX : ∀ x ∈ X, ∀ y ∈ X, x ≠ y → G.col x y ≠ c)
    (hZX : ∀ y ∈ Z, ∀ x ∈ X, G.col y x ≠ c)
    (hZZ : ∀ y ∈ Z, ∀ y' ∈ Z, y ≠ y' → G.col y y' ≠ c) :
    X.card + Z.card ≤ 16 := by
  have hunion : ∀ p ∈ X ∪ Z, ∀ q ∈ X ∪ Z, p ≠ q → G.col p q ≠ c := by
    intro p hp q hq hpq
    rcases Finset.mem_union.mp hp with hpX | hpZ
    · rcases Finset.mem_union.mp hq with hqX | hqZ
      · exact hX p hpX q hqX hpq
      · rw [G.symm p q]; exact hZX q hqZ p hpX
    · rcases Finset.mem_union.mp hq with hqX | hqZ
      · exact hZX p hpZ q hqX
      · exact hZZ p hpZ q hqZ hpq
  have hbound := indep_le_sixteen G h c (X ∪ Z) hunion
  have hdisj : Disjoint X Z :=
    Finset.disjoint_left.mpr (fun a ha haZ => hXZ a haZ ha)
  rw [Finset.card_union_of_disjoint hdisj] at hbound
  exact hbound

/-- **Saturation, clique form.**  If `X` is `c`-free with at least 15 points, the
points with no colour-`c` edge into `X` are pairwise joined in colour `c`. -/
theorem armFar_clique (G : EdgeCol V 4) (h : TriangleFree G) {X : Finset V} {c : Fin 4}
    (hX : ∀ x ∈ X, ∀ y ∈ X, x ≠ y → G.col x y ≠ c) (h15 : 15 ≤ X.card) :
    ∀ y ∈ armFar G X c, ∀ y' ∈ armFar G X c, y ≠ y' → G.col y y' = c := by
  intro y hy y' hy' hyy'
  rw [mem_armFar] at hy hy'
  by_contra hc
  have hb := union_free_le_sixteen G h (X := X) (Z := {y, y'}) (c := c)
    (fun z hz => by
      rw [Finset.mem_insert, Finset.mem_singleton] at hz
      rcases hz with rfl | rfl
      · exact hy.1
      · exact hy'.1)
    hX
    (fun z hz x hx => by
      rw [Finset.mem_insert, Finset.mem_singleton] at hz
      rcases hz with rfl | rfl
      · exact hy.2 x hx
      · exact hy'.2 x hx)
    (fun z hz z' hz' hzz => by
      have hsymm : ∀ a b : V, G.col a b ≠ c → G.col b a ≠ c := by
        intro a b hab hba
        exact hab (by rw [G.symm a b]; exact hba)
      rw [Finset.mem_insert, Finset.mem_singleton] at hz hz'
      rcases hz with rfl | rfl <;> rcases hz' with rfl | rfl
      · exact absurd rfl hzz
      · exact hc
      · exact hsymm _ _ hc
      · exact absurd rfl hzz)
  rw [Finset.card_pair hyy'] at hb
  omega

/-- **Saturation, `m = 15` case.**  A 15-point `c`-free set has at most 2 points
with no colour-`c` edge into it. -/
theorem armFar_le_two (G : EdgeCol V 4) (h : TriangleFree G) {X : Finset V} {c : Fin 4}
    (hX : ∀ x ∈ X, ∀ y ∈ X, x ≠ y → G.col x y ≠ c) (h15 : 15 ≤ X.card) :
    (armFar G X c).card ≤ 2 := by
  by_contra hle
  simp only [not_le] at hle
  obtain ⟨T, hTsub, hTcard⟩ :=
    Finset.exists_subset_card_eq (s := armFar G X c) (show 3 ≤ (armFar G X c).card by omega)
  have hT3 : T.card = 3 := hTcard
  obtain ⟨a, ha⟩ := Finset.card_pos.mp (show 0 < T.card by omega)
  have h2 : (T.erase a).card = 2 := by rw [Finset.card_erase_of_mem ha, hT3]
  obtain ⟨b, hb⟩ := Finset.card_pos.mp (show 0 < (T.erase a).card by omega)
  have h1 : ((T.erase a).erase b).card = 1 := by
    rw [Finset.card_erase_of_mem hb, h2]
  obtain ⟨d, hd⟩ := Finset.card_pos.mp (show 0 < ((T.erase a).erase b).card by omega)
  obtain ⟨hba, hbT⟩ := Finset.mem_erase.mp hb
  obtain ⟨hdb, hdab⟩ := Finset.mem_erase.mp hd
  obtain ⟨hda, hdT⟩ := Finset.mem_erase.mp hdab
  have haF : a ∈ armFar G X c := hTsub ha
  have hbF : b ∈ armFar G X c := hTsub hbT
  have hdF : d ∈ armFar G X c := hTsub hdT
  have hab : a ≠ b := Ne.symm hba
  have had : a ≠ d := Ne.symm hda
  have hbd : b ≠ d := Ne.symm hdb
  have e1 := armFar_clique G h hX h15 a haF b hbF hab
  have e2 := armFar_clique G h hX h15 a haF d hdF had
  have e3 := armFar_clique G h hX h15 b hbF d hdF hbd
  exact h a b d hab hbd had ⟨by rw [e1, e2], by rw [e2, e3]⟩

/-- **Saturation, `m = 16` case.**  A 16-point `c`-free set is saturated. -/
theorem armFar_eq_empty (G : EdgeCol V 4) (h : TriangleFree G) {X : Finset V} {c : Fin 4}
    (hX : ∀ x ∈ X, ∀ y ∈ X, x ≠ y → G.col x y ≠ c) (h16 : 16 ≤ X.card) :
    armFar G X c = ∅ := by
  refine Finset.eq_empty_iff_forall_notMem.mpr ?_
  intro y hy
  rw [mem_armFar] at hy
  have hb := union_free_le_sixteen G h (X := X) (Z := {y}) (c := c)
    (fun z hz => by
      rw [Finset.mem_singleton] at hz
      subst hz
      exact hy.1)
    hX
    (fun z hz x hx => by
      rw [Finset.mem_singleton] at hz
      subst hz
      exact hy.2 x hx)
    (fun z hz z' hz' hzz => by
      rw [Finset.mem_singleton] at hz hz'
      exact absurd (hz.trans hz'.symm) hzz)
  rw [Finset.card_singleton] at hb
  omega



/-- **Saturation, `m = 14` case.**  A 14-point `c`-free set has at most 5 points
with no colour-`c` edge into it: six of them would 2-colour `K_6` by "colour `c`"
versus "not colour `c`", and a monochromatic triangle in either class is a
contradiction (`R(3,3) ≤ 6` for the second class, `R(3,3,3) ≤ 17` on `X` plus
three far points for the first). -/
theorem armFar_le_five (G : EdgeCol V 4) (h : TriangleFree G) {X : Finset V} {c : Fin 4}
    (hX : ∀ x ∈ X, ∀ y ∈ X, x ≠ y → G.col x y ≠ c) (h14 : 14 ≤ X.card) :
    (armFar G X c).card ≤ 5 := by
  by_contra hle
  simp only [not_le] at hle
  obtain ⟨T, hTsub, hTcard⟩ :=
    Finset.exists_subset_card_eq (s := armFar G X c)
      (show 6 ≤ (armFar G X c).card by omega)
  have hT6 : T.card = 6 := hTcard
  have hfar : ∀ y ∈ T, y ∉ X ∧ ∀ x ∈ X, G.col y x ≠ c :=
    fun y hy => mem_armFar.mp (hTsub hy)
  have hsymm : ∀ a b : V, G.col a b ≠ c → G.col b a ≠ c := by
    intro a b hab hba
    exact hab (by rw [G.symm a b]; exact hba)
  -- the two-colouring of `T` by "colour `c`" versus the rest
  let G2 : EdgeCol ↥T 2 :=
    { col := fun p q => if G.col p.1 q.1 = c then 0 else 1
      symm := by
        intro p q
        rw [G.symm p.1 q.1] }
  have h2 : TriangleFree G2 := by
    intro p q r hpq hqr hpr hmono
    have hpq' : p.1 ≠ q.1 := fun hh => hpq (Subtype.ext hh)
    have hqr' : q.1 ≠ r.1 := fun hh => hqr (Subtype.ext hh)
    have hpr' : p.1 ≠ r.1 := fun hh => hpr (Subtype.ext hh)
    by_cases hc : G.col p.1 q.1 = c
    · -- all three edges have colour `c`: a `c`-triangle of `G`
      have h0 : G2.col p q = 0 := by simp [G2, hc]
      have h1 : G2.col p r = 0 := by rw [← hmono.1]; exact h0
      have h2' : G2.col q r = 0 := by rw [← hmono.2]; exact h1
      have hpr_c : G.col p.1 r.1 = c := by
        by_contra hne
        have : G2.col p r = 1 := by simp [G2, hne]
        rw [h1] at this
        exact absurd this (by decide)
      have hqr_c : G.col q.1 r.1 = c := by
        by_contra hne
        have : G2.col q r = 1 := by simp [G2, hne]
        rw [h2'] at this
        exact absurd this (by decide)
      exact h p.1 q.1 r.1 hpq' hqr' hpr'
        ⟨by rw [hc, hpr_c], by rw [hpr_c, hqr_c]⟩
    · -- no edge has colour `c`: `X` plus the three points is `c`-free with 17 points
      have h1 : G2.col p q = 1 := by simp [G2, hc]
      have h2' : G2.col p r = 1 := by rw [← hmono.1]; exact h1
      have h3' : G2.col q r = 1 := by rw [← hmono.2]; exact h2'
      have hpr_nc : G.col p.1 r.1 ≠ c := by
        intro hcc
        have : G2.col p r = 0 := by simp [G2, hcc]
        rw [h2'] at this
        exact absurd this (by decide)
      have hqr_nc : G.col q.1 r.1 ≠ c := by
        intro hcc
        have : G2.col q r = 0 := by simp [G2, hcc]
        rw [h3'] at this
        exact absurd this (by decide)
      have hb := union_free_le_sixteen G h (X := X) (Z := ({p.1, q.1, r.1} : Finset V))
        (c := c)
        (fun z hz => by
          simp only [Finset.mem_insert, Finset.mem_singleton] at hz
          rcases hz with rfl | rfl | rfl
          · exact (hfar p.1 p.2).1
          · exact (hfar q.1 q.2).1
          · exact (hfar r.1 r.2).1)
        hX
        (fun z hz x hx => by
          simp only [Finset.mem_insert, Finset.mem_singleton] at hz
          rcases hz with rfl | rfl | rfl
          · exact (hfar p.1 p.2).2 x hx
          · exact (hfar q.1 q.2).2 x hx
          · exact (hfar r.1 r.2).2 x hx)
        (fun z hz z' hz' hzz => by
          simp only [Finset.mem_insert, Finset.mem_singleton] at hz hz'
          rcases hz with rfl | rfl | rfl <;> rcases hz' with rfl | rfl | rfl
          · exact absurd rfl hzz
          · exact hc
          · exact hpr_nc
          · exact hsymm _ _ hc
          · exact absurd rfl hzz
          · exact hqr_nc
          · exact hsymm _ _ hpr_nc
          · exact hsymm _ _ hqr_nc
          · exact absurd rfl hzz)
      have hZcard : ({p.1, q.1, r.1} : Finset V).card = 3 := by
        have h1 : p.1 ∉ ({q.1, r.1} : Finset V) := by simp [hpq', hpr']
        have h2 : q.1 ∉ ({r.1} : Finset V) := by simpa using hqr'
        rw [Finset.card_insert_of_notMem h1, Finset.card_insert_of_notMem h2,
          Finset.card_singleton]
      rw [hZcard] at hb
      omega
  exact two_colour_six G2 (by simp [Fintype.card_coe, hT6]) h2

end K58

/-! ## Axiom audit (kernel check: no `sorry`, no `native_decide`) -/

#print axioms K58.indep_le_sixteen
#print axioms K58.deg_le_sixteen'
#print axioms K58.interface_sum
#print axioms K58.interface
#print axioms K58.armFar_clique
#print axioms K58.armFar_le_two
#print axioms K58.armFar_eq_empty
#print axioms K58.armFar_le_five
