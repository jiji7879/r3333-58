/-
# The forced-pentagon layer of the K58 zero-set argument

Kernel-checks the colouring lemma behind the "parent rule" of
`K58_fivefold_arm_obstruction` (section "A parent rule using only positive
pins"), stated as a theorem about a four-colouring of a complete graph with no
monochromatic triangle.
-/
import K58.Basic


set_option linter.unusedSectionVars false

namespace K58

namespace ForcedPentagon

/-- A four-colouring of the edges of a complete graph: the project's
`K58.EdgeCol V 4`. -/
abbrev Colouring (V : Type*) := EdgeCol V 4

namespace Colouring

variable {V : Type*} [DecidableEq V] (C : Colouring V)

/-- The triangle on `x, y, z` is monochromatic. -/
def Mono (x y z : V) : Prop :=
  ∃ k : Fin 4, C.col x y = k ∧ C.col x z = k ∧ C.col y z = k

/-- There is no monochromatic triangle. -/
def NoMono : Prop :=
  ∀ x y z : V, x ≠ y → y ≠ z → x ≠ z → ¬ C.Mono x y z

variable {C}

instance decidableMono (C : Colouring V) (x y z : V) : Decidable (C.Mono x y z) := by
  unfold Colouring.Mono
  infer_instance

instance decidableNoMono [Fintype V] (C : Colouring V) : Decidable C.NoMono := by
  unfold Colouring.NoMono
  infer_instance

/-- A set whose pairs all have one colour has at most two points, since three
would form a monochromatic triangle. -/
theorem card_le_two_of_clique (h : C.NoMono) {S : Finset V} {k : Fin 4}
    (hpair : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → C.col x y = k) : S.card ≤ 2 := by
  by_contra hle
  rw [not_le] at hle
  obtain ⟨a, ha, b, hb, c, hc, hab, hac, hbc⟩ := Finset.two_lt_card.mp hle
  exact h a b c hab hbc hac
    ⟨k, hpair a ha b hb hab, hpair a ha c hc hac, hpair b hb c hc hbc⟩

/-- In a five-set using only two colours, every vertex has exactly two
neighbours in each of the two colours. -/
theorem degree_two_of_two_colours (h : C.NoMono) {S : Finset V} (hS : S.card = 5)
    {k l : Fin 4} (hkl : k ≠ l)
    (hcol : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → C.col x y = k ∨ C.col x y = l)
    {x : V} (hx : x ∈ S) :
    (S.filter fun y => y ≠ x ∧ C.col x y = k).card = 2 := by
  classical
  let R : Finset V := S.filter fun y => y ≠ x ∧ C.col x y = k
  let B : Finset V := S.filter fun y => y ≠ x ∧ C.col x y = l
  have hRle : R.card ≤ 2 := by
    apply card_le_two_of_clique (C := C) h (k := l)
    intro y1 hy1 y2 hy2 hne
    have hy1' : y1 ∈ S.filter (fun y => y ≠ x ∧ C.col x y = k) := hy1
    have hy2' : y2 ∈ S.filter (fun y => y ≠ x ∧ C.col x y = k) := hy2
    have hy1S : y1 ∈ S := (Finset.mem_filter.mp hy1').1
    have hy2S : y2 ∈ S := (Finset.mem_filter.mp hy2').1
    have hy1x : y1 ≠ x := (Finset.mem_filter.mp hy1').2.1
    have hy2x : y2 ≠ x := (Finset.mem_filter.mp hy2').2.1
    have h1 : C.col x y1 = k := (Finset.mem_filter.mp hy1').2.2
    have h2 : C.col x y2 = k := (Finset.mem_filter.mp hy2').2.2
    rcases hcol y1 hy1S y2 hy2S hne with hk | hl
    · exfalso
      exact h x y1 y2 hy1x.symm hne hy2x.symm ⟨k, h1, h2, hk⟩
    · exact hl
  have hBle : B.card ≤ 2 := by
    apply card_le_two_of_clique (C := C) h (k := k)
    intro y1 hy1 y2 hy2 hne
    have hy1' : y1 ∈ S.filter (fun y => y ≠ x ∧ C.col x y = l) := hy1
    have hy2' : y2 ∈ S.filter (fun y => y ≠ x ∧ C.col x y = l) := hy2
    have hy1S : y1 ∈ S := (Finset.mem_filter.mp hy1').1
    have hy2S : y2 ∈ S := (Finset.mem_filter.mp hy2').1
    have hy1x : y1 ≠ x := (Finset.mem_filter.mp hy1').2.1
    have hy2x : y2 ≠ x := (Finset.mem_filter.mp hy2').2.1
    have h1 : C.col x y1 = l := (Finset.mem_filter.mp hy1').2.2
    have h2 : C.col x y2 = l := (Finset.mem_filter.mp hy2').2.2
    rcases hcol y1 hy1S y2 hy2S hne with hk | hl
    · exact hk
    · exfalso
      exact h x y1 y2 hy1x.symm hne hy2x.symm ⟨l, h1, h2, hl⟩
  have hdisj : Disjoint R B := by
    rw [Finset.disjoint_left]
    intro y hyR hyB
    have hyR' : y ∈ S.filter (fun y => y ≠ x ∧ C.col x y = k) := hyR
    have hyB' : y ∈ S.filter (fun y => y ≠ x ∧ C.col x y = l) := hyB
    have h1 : C.col x y = k := (Finset.mem_filter.mp hyR').2.2
    have h2 : C.col x y = l := (Finset.mem_filter.mp hyB').2.2
    exact hkl (h1.symm.trans h2)
  have hcover : S.erase x = R ∪ B := by
    ext y
    simp only [Finset.mem_erase, Finset.mem_union]
    constructor
    · rintro ⟨hyx, hyS⟩
      rcases hcol x hx y hyS (Ne.symm hyx) with hk | hl
      · exact Or.inl (by show y ∈ S.filter (fun y => y ≠ x ∧ C.col x y = k); exact Finset.mem_filter.mpr ⟨hyS, hyx, hk⟩)
      · exact Or.inr (by show y ∈ S.filter (fun y => y ≠ x ∧ C.col x y = l); exact Finset.mem_filter.mpr ⟨hyS, hyx, hl⟩)
    · rintro (hy | hy)
      · exact ⟨(Finset.mem_filter.mp (show y ∈ S.filter (fun y => y ≠ x ∧ C.col x y = k) from hy)).2.1,
               (Finset.mem_filter.mp (show y ∈ S.filter (fun y => y ≠ x ∧ C.col x y = k) from hy)).1⟩
      · exact ⟨(Finset.mem_filter.mp (show y ∈ S.filter (fun y => y ≠ x ∧ C.col x y = l) from hy)).2.1,
               (Finset.mem_filter.mp (show y ∈ S.filter (fun y => y ≠ x ∧ C.col x y = l) from hy)).1⟩
  have hcard : R.card + B.card = 4 := by
    have h1 : (S.erase x).card = 4 := by
      rw [Finset.card_erase_of_mem hx, hS]
    rwa [hcover, Finset.card_union_of_disjoint hdisj] at h1
  have hRle' : (S.filter (fun y => y ≠ x ∧ C.col x y = k)).card ≤ 2 := hRle
  have hBle' : (S.filter (fun y => y ≠ x ∧ C.col x y = l)).card ≤ 2 := hBle
  have hcard' : (S.filter (fun y => y ≠ x ∧ C.col x y = k)).card
      + (S.filter (fun y => y ≠ x ∧ C.col x y = l)).card = 4 := hcard
  show (S.filter (fun y => y ≠ x ∧ C.col x y = k)).card = 2
  omega


/-- The degree of a point `y` into a two-coloured four-set `P` is exactly two in
each of the colours. -/
theorem degree_into_four (h : C.NoMono) {P : Finset V} (hP : P.card = 4) {y : V}
    (hy : y ∉ P) {k l : Fin 4} (hkl : k ≠ l)
    (hcol : ∀ a ∈ insert y P, ∀ b ∈ insert y P, a ≠ b → C.col a b = k ∨ C.col a b = l) :
    (P.filter fun q => C.col y q = k).card = 2 := by
  classical
  have hS : (insert y P).card = 5 := by
    rw [Finset.card_insert_of_notMem hy, hP]
  have h := degree_two_of_two_colours (C := C) h (S := insert y P) hS (k := k) (l := l)
    hkl hcol (x := y) (Finset.mem_insert_self y P)
  have hfil : (insert y P).filter (fun q => q ≠ y ∧ C.col y q = k)
      = P.filter (fun q => C.col y q = k) := by
    ext q
    simp only [Finset.mem_filter, Finset.mem_insert]
    constructor
    · rintro ⟨hq, hqy, hc⟩
      rcases hq with rfl | hqP
      · exact absurd rfl hqy
      · exact ⟨hqP, hc⟩
    · rintro ⟨hqP, hc⟩
      exact ⟨Or.inr hqP, fun hq => hy (hq ▸ hqP), hc⟩
  rwa [hfil] at h

/-- Endpoint lemma: for a two-coloured four-block `P` completed by `y`, the
colour-`k` neighbours of `y` in `P` are exactly the endpoints of the colour-`k`
path on `P`. -/
theorem endpoint (h : C.NoMono) {P : Finset V} (hP : P.card = 4) {y : V} (hy : y ∉ P)
    {k l : Fin 4} (hkl : k ≠ l)
    (hcol : ∀ a ∈ insert y P, ∀ b ∈ insert y P, a ≠ b → C.col a b = k ∨ C.col a b = l)
    {p : V} (hp : p ∈ P) :
    C.col y p = k ↔ (P.filter fun q => q ≠ p ∧ C.col p q = k).card = 1 := by
  classical
  have hS : (insert y P).card = 5 := by
    rw [Finset.card_insert_of_notMem hy, hP]
  have hsplit : (insert y P).filter (fun q => q ≠ p ∧ C.col p q = k)
      = if C.col p y = k then insert y (P.filter fun q => q ≠ p ∧ C.col p q = k)
        else P.filter fun q => q ≠ p ∧ C.col p q = k := by
    rw [Finset.filter_insert]
    have hpy : y ≠ p := fun h => hy (h ▸ hp)
    simp [hpy]
  have hdegp : (P.filter fun q => q ≠ p ∧ C.col p q = k).card
      + (if C.col p y = k then 1 else 0) = 2 := by
    have h := degree_two_of_two_colours (C := C) h (S := insert y P) hS (k := k) (l := l)
      hkl hcol (x := p) (Finset.mem_insert_of_mem hp)
    rw [hsplit] at h
    by_cases hpy : C.col p y = k
    · rw [if_pos hpy] at h ⊢
      rw [Finset.card_insert_of_notMem (by simp [hy])] at h
      omega
    · rw [if_neg hpy] at h ⊢
      simpa using h
  constructor
  · intro hpk
    have hpy : C.col p y = k := (C.symm p y).trans hpk
    rw [if_pos hpy] at hdegp
    omega
  · intro hone
    by_contra hne
    have hne' : ¬ C.col p y = k := by rw [C.symm p y]; exact hne
    rw [if_neg hne'] at hdegp
    omega


/-- An edge that avoids colours 0 and 1 has colour 2 or 3. -/
theorem eq_two_or_three {x y : V} (h0 : C.col x y ≠ 0) (h1 : C.col x y ≠ 1) :
    C.col x y = 2 ∨ C.col x y = 3 := by
  have hcases : ∀ t : Fin 4, t = 0 ∨ t = 1 ∨ t = 2 ∨ t = 3 := by decide
  rcases hcases (C.col x y) with h | h | h | h
  · exact absurd h h0
  · exact absurd h h1
  · exact Or.inl h
  · exact Or.inr h

/-- Two vertices of the colour-1 arm of `r` are not joined in colour 1. -/
theorem ne_one_of_arm (h : C.NoMono) {r x y : V} (hx : C.col r x = 1) (hy : C.col r y = 1)
    (hrx : r ≠ x) (hry : r ≠ y) (hxy : x ≠ y) : C.col x y ≠ 1 := by
  intro hc
  exact h r x y hrx hxy hry ⟨1, hx, hy, hc⟩

/-- Two vertices that both see `a` in colour 0 are not joined in colour 0. -/
theorem ne_zero_of_common_zero (h : C.NoMono) {a x y : V} (hx : C.col a x = 0)
    (hy : C.col a y = 0) (hax : a ≠ x) (hay : a ≠ y) (hxy : x ≠ y) : C.col x y ≠ 0 := by
  intro hc
  exact h a x y hax hxy hay ⟨0, hx, hy, hc⟩

/-- Two completions of a two-coloured four-block are not joined in either of
the two colours. -/
theorem completion_colour_ne (h : C.NoMono) {P : Finset V} (hP : P.card = 4)
    {y z : V} (hy : y ∉ P) (hz : z ∉ P) (hyz : y ≠ z)
    {k l : Fin 4} (hkl : k ≠ l)
    (hcoly : ∀ a ∈ insert y P, ∀ b ∈ insert y P, a ≠ b → C.col a b = k ∨ C.col a b = l)
    (hcolz : ∀ a ∈ insert z P, ∀ b ∈ insert z P, a ≠ b → C.col a b = k ∨ C.col a b = l) :
    C.col y z ≠ k := by
  intro hk
  have hdeg : (P.filter fun q => C.col y q = k).card = 2 :=
    degree_into_four h hP hy hkl hcoly
  have hpos : 0 < (P.filter fun q => C.col y q = k).card := by rw [hdeg]; omega
  obtain ⟨p, hp⟩ := Finset.card_pos.mp hpos
  have hpP : p ∈ P := (Finset.mem_filter.mp hp).1
  have hyp : C.col y p = k := (Finset.mem_filter.mp hp).2
  have h1 : (P.filter fun q => q ≠ p ∧ C.col p q = k).card = 1 :=
    (endpoint h hP hy hkl hcoly hpP).mp hyp
  have hzp : C.col z p = k := (endpoint h hP hz hkl hcolz hpP).mpr h1
  exact h y p z (fun e => hy (e ▸ hpP)) (fun e => hz (e ▸ hpP)) hyz
    ⟨k, hyp, hk, (C.symm p z).trans hzp⟩

/-- Two completions of a five-set using only colours 2 and 3, both lying in the
colour-1 arm of a vertex (so their own edge avoids colour 1), are joined in
colour 0. -/
theorem two_completions_zero (h : C.NoMono) {P : Finset V} (hP : P.card = 4)
    {y z : V} (hy : y ∉ P) (hz : z ∉ P) (hyz : y ≠ z)
    (hcoly : ∀ a ∈ insert y P, ∀ b ∈ insert y P, a ≠ b → C.col a b = 2 ∨ C.col a b = 3)
    (hcolz : ∀ a ∈ insert z P, ∀ b ∈ insert z P, a ≠ b → C.col a b = 2 ∨ C.col a b = 3)
    (hne1 : C.col y z ≠ 1) : C.col y z = 0 := by
  have hcases : ∀ t : Fin 4, t = 0 ∨ t = 1 ∨ t = 2 ∨ t = 3 := by decide
  rcases hcases (C.col y z) with hc0 | hc1 | hc2 | hc3
  · exact hc0
  · exact absurd hc1 hne1
  · exact absurd hc2 (completion_colour_ne h hP hy hz hyz (k := 2) (l := 3) (by decide) hcoly hcolz)
  · exact absurd hc3 (completion_colour_ne h hP hy hz hyz (k := 3) (l := 2) (by decide)
      (fun a ha b hb hne => (hcoly a ha b hb hne).symm)
      (fun a ha b hb hne => (hcolz a ha b hb hne).symm))


/-- Parent rule.  Let `P` be a four-set inside the colour-1 arm of `r` whose
points all see every `a ∈ L` in colour 0, with `L` nonempty.  Then at most two
further colour-1 neighbours of `r` can see a point of `L` in colour 0. -/
theorem at_most_two_completions (h : C.NoMono) {r : V} {P L Y : Finset V}
    (hP : P.card = 4)
    (hrP : ∀ p ∈ P, C.col r p = 1) (hrne : ∀ p ∈ P, r ≠ p)
    (hL : L.Nonempty) (hLP : ∀ a ∈ L, ∀ p ∈ P, C.col a p = 0)
    (hLne : ∀ a ∈ L, ∀ p ∈ P, a ≠ p)
    (hY : ∀ y ∈ Y, y ∉ P ∧ r ≠ y ∧ C.col r y = 1 ∧ ∃ a ∈ L, a ≠ y ∧ C.col a y = 0) :
    Y.card ≤ 2 := by
  classical
  by_contra hle
  rw [not_le] at hle
  obtain ⟨y, hyY, z, hzY, w, hwY, hyz, hyw, hzw⟩ := Finset.two_lt_card.mp hle
  obtain ⟨hyP, hyr, hy1, ay, hayL, hayy, hay0⟩ := hY y hyY
  obtain ⟨hzP, hzr, hz1, az, hazL, hazz, haz0⟩ := hY z hzY
  obtain ⟨hwP, hwr, hw1, aw, hawL, haww, haw0⟩ := hY w hwY
  have hcoly : ∀ a ∈ insert y P, ∀ b ∈ insert y P, a ≠ b → C.col a b = 2 ∨ C.col a b = 3 := by
    intro a ha b hb hab
    rcases Finset.mem_insert.mp ha with rfl | haP
    · rcases Finset.mem_insert.mp hb with rfl | hbP
      · exact absurd rfl hab
      · apply eq_two_or_three
        · exact ne_zero_of_common_zero h hay0 (hLP ay hayL b hbP) hayy (hLne ay hayL b hbP) hab
        · exact ne_one_of_arm h hy1 (hrP b hbP) hyr (hrne b hbP) hab
    · rcases Finset.mem_insert.mp hb with rfl | hbP
      · apply eq_two_or_three
        · exact ne_zero_of_common_zero h (hLP ay hayL a haP) hay0 (hLne ay hayL a haP) hayy hab
        · exact ne_one_of_arm h (hrP a haP) hy1 (hrne a haP) hyr hab
      · apply eq_two_or_three
        · obtain ⟨a0, ha0⟩ := hL
          exact ne_zero_of_common_zero h (hLP a0 ha0 a haP) (hLP a0 ha0 b hbP)
            (hLne a0 ha0 a haP) (hLne a0 ha0 b hbP) hab
        · exact ne_one_of_arm h (hrP a haP) (hrP b hbP) (hrne a haP) (hrne b hbP) hab
  have hcolz : ∀ a ∈ insert z P, ∀ b ∈ insert z P, a ≠ b → C.col a b = 2 ∨ C.col a b = 3 := by
    intro a ha b hb hab
    rcases Finset.mem_insert.mp ha with rfl | haP
    · rcases Finset.mem_insert.mp hb with rfl | hbP
      · exact absurd rfl hab
      · apply eq_two_or_three
        · exact ne_zero_of_common_zero h haz0 (hLP az hazL b hbP) hazz (hLne az hazL b hbP) hab
        · exact ne_one_of_arm h hz1 (hrP b hbP) hzr (hrne b hbP) hab
    · rcases Finset.mem_insert.mp hb with rfl | hbP
      · apply eq_two_or_three
        · exact ne_zero_of_common_zero h (hLP az hazL a haP) haz0 (hLne az hazL a haP) hazz hab
        · exact ne_one_of_arm h (hrP a haP) hz1 (hrne a haP) hzr hab
      · apply eq_two_or_three
        · obtain ⟨a0, ha0⟩ := hL
          exact ne_zero_of_common_zero h (hLP a0 ha0 a haP) (hLP a0 ha0 b hbP)
            (hLne a0 ha0 a haP) (hLne a0 ha0 b hbP) hab
        · exact ne_one_of_arm h (hrP a haP) (hrP b hbP) (hrne a haP) (hrne b hbP) hab
  have hcolw : ∀ a ∈ insert w P, ∀ b ∈ insert w P, a ≠ b → C.col a b = 2 ∨ C.col a b = 3 := by
    intro a ha b hb hab
    rcases Finset.mem_insert.mp ha with rfl | haP
    · rcases Finset.mem_insert.mp hb with rfl | hbP
      · exact absurd rfl hab
      · apply eq_two_or_three
        · exact ne_zero_of_common_zero h haw0 (hLP aw hawL b hbP) haww (hLne aw hawL b hbP) hab
        · exact ne_one_of_arm h hw1 (hrP b hbP) hwr (hrne b hbP) hab
    · rcases Finset.mem_insert.mp hb with rfl | hbP
      · apply eq_two_or_three
        · exact ne_zero_of_common_zero h (hLP aw hawL a haP) haw0 (hLne aw hawL a haP) haww hab
        · exact ne_one_of_arm h (hrP a haP) hw1 (hrne a haP) hwr hab
      · apply eq_two_or_three
        · obtain ⟨a0, ha0⟩ := hL
          exact ne_zero_of_common_zero h (hLP a0 ha0 a haP) (hLP a0 ha0 b hbP)
            (hLne a0 ha0 a haP) (hLne a0 ha0 b hbP) hab
        · exact ne_one_of_arm h (hrP a haP) (hrP b hbP) (hrne a haP) (hrne b hbP) hab
  have hyz0 : C.col y z = 0 :=
    two_completions_zero h hP hyP hzP hyz hcoly hcolz (ne_one_of_arm h hy1 hz1 hyr hzr hyz)
  have hyw0 : C.col y w = 0 :=
    two_completions_zero h hP hyP hwP hyw hcoly hcolw (ne_one_of_arm h hy1 hw1 hyr hwr hyw)
  have hzw0 : C.col z w = 0 :=
    two_completions_zero h hP hzP hwP hzw hcolz hcolw (ne_one_of_arm h hz1 hw1 hzr hwr hzw)
  exact h y z w hyz hzw hyw ⟨0, hyz0, hyw0, hzw0⟩



/-- Two completions have no common zero-neighbour (package 1: "Consequently `y`
and `z` have no common zero neighbour"). -/
theorem completions_no_common_zero (h : C.NoMono) {P : Finset V} (hP : P.card = 4)
    {y z : V} (hy : y ∉ P) (hz : z ∉ P) (hyz : y ≠ z)
    (hcoly : ∀ a ∈ insert y P, ∀ b ∈ insert y P, a ≠ b → C.col a b = 2 ∨ C.col a b = 3)
    (hcolz : ∀ a ∈ insert z P, ∀ b ∈ insert z P, a ≠ b → C.col a b = 2 ∨ C.col a b = 3)
    (hne1 : C.col y z ≠ 1) {a : V} (hay : a ≠ y) (haz : a ≠ z)
    (haY : C.col a y = 0) (haZ : C.col a z = 0) : False := by
  have hyz0 : C.col y z = 0 := two_completions_zero h hP hy hz hyz hcoly hcolz hne1
  exact h a y z hay hyz haz ⟨0, haY, haZ, hyz0⟩

/-- `K58.TriangleFree` gives the `∃`-form used by the lemmas above. -/
theorem triangleFree_noMono {C : Colouring V} (h : TriangleFree C) : C.NoMono := by
  intro x y z hxy hyz hxz hmono
  obtain ⟨k, h1, h2, h3⟩ := hmono
  exact h x y z hxy hyz hxz ⟨by rw [h1, h2], by rw [h2, h3]⟩

/-- The parent rule in the project's `TriangleFree` form: at most two
completions. -/
theorem at_most_two_completions_of_triangleFree {C : Colouring V} (h : TriangleFree C)
    {r : V} {P L Y : Finset V} (hP : P.card = 4)
    (hrP : ∀ p ∈ P, C.col r p = 1) (hrne : ∀ p ∈ P, r ≠ p)
    (hL : L.Nonempty) (hLP : ∀ a ∈ L, ∀ p ∈ P, C.col a p = 0)
    (hLne : ∀ a ∈ L, ∀ p ∈ P, a ≠ p)
    (hY : ∀ y ∈ Y, y ∉ P ∧ r ≠ y ∧ C.col r y = 1 ∧ ∃ a ∈ L, a ≠ y ∧ C.col a y = 0) :
    Y.card ≤ 2 :=
  at_most_two_completions (C := C) (triangleFree_noMono h) hP hrP hrne hL hLP hLne hY

/-- Two completions of a two-coloured four-block, in `TriangleFree` form. -/
theorem two_completions_zero_of_triangleFree {C : Colouring V} (h : TriangleFree C)
    {P : Finset V} (hP : P.card = 4) {y z : V} (hy : y ∉ P) (hz : z ∉ P) (hyz : y ≠ z)
    (hcoly : ∀ a ∈ insert y P, ∀ b ∈ insert y P, a ≠ b → C.col a b = 2 ∨ C.col a b = 3)
    (hcolz : ∀ a ∈ insert z P, ∀ b ∈ insert z P, a ≠ b → C.col a b = 2 ∨ C.col a b = 3)
    (hne1 : C.col y z ≠ 1) : C.col y z = 0 :=
  two_completions_zero (C := C) (triangleFree_noMono h) hP hy hz hyz hcoly hcolz hne1

/-- A five-set using only two colours has degree two in each colour, in
`TriangleFree` form. -/
theorem degree_two_of_two_colours_of_triangleFree {C : Colouring V} (h : TriangleFree C)
    {S : Finset V} (hS : S.card = 5) {k l : Fin 4} (hkl : k ≠ l)
    (hcol : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → C.col x y = k ∨ C.col x y = l)
    {x : V} (hx : x ∈ S) :
    (S.filter fun y => y ≠ x ∧ C.col x y = k).card = 2 :=
  degree_two_of_two_colours (C := C) (triangleFree_noMono h) hS hkl hcol hx

/-! ### Sharpness and non-vacuity

The bound `2` of `at_most_two_completions` is attained.  The following explicit
triangle-free four-colouring of `K₉` has `P = {0,1,2,3}` inside the colour-1 arm
of `r = 8`, the two common zero-neighbours `6, 7`, and exactly the two
completions `4, 5`.
-/

/-- The explicit board. -/
def sharpCol : Fin 9 → Fin 9 → Fin 4 :=
  ![![0, 2, 3, 3, 2, 2, 0, 0, 1],
    ![2, 0, 2, 3, 3, 3, 0, 0, 1],
    ![3, 2, 0, 2, 3, 3, 0, 0, 1],
    ![3, 3, 2, 0, 2, 2, 0, 0, 1],
    ![2, 3, 3, 2, 0, 0, 0, 1, 1],
    ![2, 3, 3, 2, 0, 0, 1, 0, 1],
    ![0, 0, 0, 0, 0, 1, 0, 2, 0],
    ![0, 0, 0, 0, 1, 0, 2, 0, 0],
    ![1, 1, 1, 1, 1, 1, 0, 0, 0]]

/-- The sharp board as a colouring. -/
def sharpBoard : Colouring (Fin 9) where
  col := sharpCol
  symm := by decide

theorem sharpBoard_noMono : sharpBoard.NoMono := by
  show ∀ x y z : Fin 9, x ≠ y → y ≠ z → x ≠ z → ¬ Colouring.Mono sharpBoard x y z
  decide

/-- The four-block. -/
def P9 : Finset (Fin 9) := {0, 1, 2, 3}

/-- The two common zero-neighbours. -/
def L9 : Finset (Fin 9) := {6, 7}

/-- The two completions. -/
def Y9 : Finset (Fin 9) := {4, 5}

/-- The parent rule applies to the sharp board and its bound is attained. -/
theorem sharp_attained : Y9.card = 2 := by
  have hle : Y9.card ≤ 2 :=
    at_most_two_completions (C := sharpBoard) sharpBoard_noMono (r := 8) (P := P9) (L := L9)
      (Y := Y9) (by decide) (by decide) (by decide) (by decide) (by decide) (by decide) (by decide)
  have hcard : Y9.card = 2 := by decide
  omega

end Colouring

end ForcedPentagon

end K58
