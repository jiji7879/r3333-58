/-
Independent, kernel-checked formalisation of the combinatorial core of the
"repeated zero neighbourhoods" claim (README §1 of the (15,14,14,14) package),
in the K58 development's own vocabulary.

Setting: `G` is a triangle-free 4-edge-colouring of a finite vertex set `V`,
`r` a root, `A = nbrC G r 0` its colour-`0` class.  For an outside vertex `x`,
`Z(x) = nbrC G x 0 ∩ A` is its *word support*; for a finite set `L`,
`wordClass G r L` is the set of vertices whose support is exactly `L`.

Main results:

* `card_le_sixteen_of_zeroFree` : a set carrying no colour-`0` edge has at most
  16 points (transported `R(3,3,3) ≤ 17`).
* `wordClass_card_le_six`     : if `|A| = 15` and `|L| = 5` then at most six
  vertices share the support `L`.
* `wordClass_pair_le`         : two distinct supports of size 5 that meet give
  `p(L) + p(M) + |L ∩ M| ≤ 11`.
* `no_three_pairwise`         : three distinct five-sets that meet pairwise
  cannot all be supports of five vertices each.
* `card_le_three`             : at most three distinct five-sets can each be the
  support of five or more vertices.

Nothing here uses the package's code; every step is checked by the Lean kernel.
-/
import K58.Arm
import K58.Ticket
import K58.ThreeColour

set_option linter.unusedSectionVars false

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ## The three-colour cap on a set with no colour-`0` edge -/

/-- Colours `1,2,3` rewritten as the three colours of a triangle-free colouring. -/
def colCode (c : {c : Fin 4 // c ≠ 0}) : Fin 3 :=
  ⟨c.1.val - 1, by
    have h1 : c.1.val < 4 := c.1.isLt
    have h2 : c.1.val ≠ 0 := fun hh => c.2 (Fin.ext (by simpa using hh))
    omega⟩

theorem colCode_inj : Function.Injective colCode := by
  rintro ⟨c, hc⟩ ⟨d, hd⟩ he
  have hc' : c.val ≠ 0 := fun hh => hc (Fin.ext (by simpa using hh))
  have hd' : d.val ≠ 0 := fun hh => hd (Fin.ext (by simpa using hh))
  have hval : c.val - 1 = d.val - 1 := congrArg Fin.val he
  have : c.val = d.val := by omega
  exact Subtype.ext (Fin.ext this)

/-- **A zero-free set has at most sixteen points.**  A set with no colour-`0`
edge carries a triangle-free three-colouring, and `R(3,3,3) = 17`. -/
theorem card_le_sixteen_of_zeroFree (G : EdgeCol V 4) (h : TriangleFree G) (S : Finset V)
    (hS : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → G.col x y ≠ 0) : S.card ≤ 16 := by
  by_contra hcon
  push Not at hcon
  obtain ⟨T, hTS, hTcard⟩ := Finset.exists_subset_card_eq (show 17 ≤ S.card by omega)
  have hT : ∀ x ∈ T, x ∈ S := fun x hx => hTS hx
  -- the induced three-colouring on `T`
  let G3 : EdgeCol ↥T 3 :=
    { col := fun p q =>
        if hpq : p = q then 0
        else colCode ⟨G.col p.1 q.1,
          hS p.1 (hT p.1 p.2) q.1 (hT q.1 q.2) (fun hh => hpq (Subtype.ext hh))⟩
      symm := by
        intro p q
        by_cases hpq : p = q
        · subst hpq; simp
        · have hqp : q ≠ p := Ne.symm hpq
          rw [dif_neg hpq, dif_neg hqp]
          congr 1
          exact Subtype.ext (G.symm p.1 q.1) }
  have h3 : TriangleFree G3 := by
    intro p q s hpq hqs hps hmono
    have hpq' : ¬ (p = q) := hpq
    have hqs' : ¬ (q = s) := hqs
    have hps' : ¬ (p = s) := hps
    simp only [G3, dif_neg hpq', dif_neg hqs', dif_neg hps'] at hmono
    have e1 : G.col p.1 q.1 = G.col p.1 s.1 := by
      have hh := congrArg Subtype.val (colCode_inj hmono.1)
      simpa using hh
    have e2 : G.col p.1 s.1 = G.col q.1 s.1 := by
      have hh := congrArg Subtype.val (colCode_inj hmono.2)
      simpa using hh
    have hpq2 : p.1 ≠ q.1 := fun hh => hpq (Subtype.ext hh)
    have hqs2 : q.1 ≠ s.1 := fun hh => hqs (Subtype.ext hh)
    have hps2 : p.1 ≠ s.1 := fun hh => hps (Subtype.ext hh)
    exact h p.1 q.1 s.1 hpq2 hqs2 hps2 ⟨e1, e2⟩
  exact three_colour_seventeen G3 (by simp [Fintype.card_coe, hTcard]) h3

/-! ## The word support of an outside vertex -/

/-- The five zero neighbours of `x` inside the colour-`0` class `A` of `r`. -/
noncomputable def wordSup (G : EdgeCol V 4) (r x : V) : Finset V :=
  (nbrC G x 0) ∩ (nbrC G r 0)

/-- The vertices whose word support is exactly `L`. -/
noncomputable def wordClass (G : EdgeCol V 4) (r : V) (L : Finset V) : Finset V :=
  Finset.univ.filter (fun x : V => wordSup G r x = L)

theorem mem_wordClass {G : EdgeCol V 4} {r x : V} {L : Finset V} :
    x ∈ wordClass G r L ↔ wordSup G r x = L := by
  simp [wordClass]

/-- Every support lies inside `A`. -/
theorem wordSup_subset (G : EdgeCol V 4) (r x : V) :
    wordSup G r x ⊆ nbrC G r 0 := Finset.inter_subset_right

/-- A colour-`0` class is independent in colour `0`. -/
theorem col0_indep (G : EdgeCol V 4) (h : TriangleFree G) (r : V) :
    ∀ x ∈ nbrC G r 0, ∀ y ∈ nbrC G r 0, x ≠ y → G.col x y ≠ 0 := by
  intro x hx y hy hxy hc
  obtain ⟨hxr, hxc⟩ := mem_nbrC.mp hx
  obtain ⟨hyr, hyc⟩ := mem_nbrC.mp hy
  exact h r x y hxr.symm hxy hyr.symm ⟨by rw [hxc, hyc], by rw [hyc, hc]⟩

/-- A vertex meeting `A` in colour `0` is not in `A`: `A` is `0`-independent. -/
theorem not_mem_A_of_zero_neighbour (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    {x z : V} (hz : z ∈ nbrC G x 0) (hzA : z ∈ nbrC G r 0) : x ∉ nbrC G r 0 := by
  intro hx
  obtain ⟨hxz, hxzc⟩ := mem_nbrC.mp hz
  exact col0_indep G h r x hx z hzA (Ne.symm hxz) hxzc


/-! ## Consequences of a shared support -/

/-- Colour-`0` monochromatic triangles do not exist. -/
theorem col0_not_triangle (G : EdgeCol V 4) (h : TriangleFree G) {x y z : V}
    (hxy : x ≠ y) (hyz : y ≠ z) (hxz : x ≠ z)
    (h1 : G.col x y = 0) (h2 : G.col x z = 0) (h3 : G.col y z = 0) : False :=
  h x y z hxy hyz hxz ⟨by rw [h1, h2], by rw [h2, h3]⟩

/-- A point of the support of `x` is a colour-`0` neighbour of `x` inside `A`. -/
theorem zero_of_mem_wordClass (G : EdgeCol V 4) (r : V) {L : Finset V} {x z : V}
    (hx : x ∈ wordClass G r L) (hz : z ∈ L) :
    z ≠ x ∧ G.col x z = 0 ∧ z ∈ nbrC G r 0 := by
  have hwx : wordSup G r x = L := mem_wordClass.mp hx
  have hz' : z ∈ wordSup G r x := by rw [hwx]; exact hz
  obtain ⟨h1, h2⟩ := Finset.mem_inter.mp hz'
  obtain ⟨hzx, hcol⟩ := mem_nbrC.mp h1
  exact ⟨hzx, hcol, h2⟩

/-- A vertex with a nonempty support lies outside `A`. -/
theorem notMem_A_of_mem_wordClass (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    {L : Finset V} (hL : L.Nonempty) {x : V} (hx : x ∈ wordClass G r L) :
    x ∉ nbrC G r 0 := by
  obtain ⟨z, hz⟩ := hL
  obtain ⟨hzx, hcol, hzA⟩ := zero_of_mem_wordClass G r hx hz
  intro hxA
  exact col0_indep G h r x hxA z hzA (Ne.symm hzx) hcol

/-- Two vertices sharing a nonempty support are not joined in colour `0`. -/
theorem col_ne_zero_of_same_class (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    {L : Finset V} (hL : L.Nonempty) {x y : V}
    (hx : x ∈ wordClass G r L) (hy : y ∈ wordClass G r L) (hxy : x ≠ y) :
    G.col x y ≠ 0 := by
  intro hcol
  obtain ⟨z, hz⟩ := hL
  obtain ⟨hzx, hxz, -⟩ := zero_of_mem_wordClass G r hx hz
  obtain ⟨hzy, hyz, -⟩ := zero_of_mem_wordClass G r hy hz
  exact col0_not_triangle G h hxy (Ne.symm hzy) (Ne.symm hzx) hcol hxz hyz

/-- Two vertices of classes with meeting supports are not joined in colour `0`. -/
theorem col_ne_zero_of_meet (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    {L M : Finset V} (hm : (L ∩ M).Nonempty) {x y : V}
    (hx : x ∈ wordClass G r L) (hy : y ∈ wordClass G r M) (hxy : x ≠ y) :
    G.col x y ≠ 0 := by
  intro hcol
  obtain ⟨z, hz⟩ := hm
  obtain ⟨hzL, hzM⟩ := Finset.mem_inter.mp hz
  obtain ⟨hzx, hxz, -⟩ := zero_of_mem_wordClass G r hx hzL
  obtain ⟨hzy, hyz, -⟩ := zero_of_mem_wordClass G r hy hzM
  exact col0_not_triangle G h hxy (Ne.symm hzy) (Ne.symm hzx) hcol hxz hyz

/-- A member of a class with nonempty support has no colour-`0` edge to a point of
`A` outside the support. -/
theorem col_ne_zero_of_notMem (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    {L : Finset V} (hL : L.Nonempty) {x z : V} (hx : x ∈ wordClass G r L)
    (hz : z ∈ nbrC G r 0) (hzL : z ∉ L) : G.col x z ≠ 0 := by
  intro hcol
  have hwx : wordSup G r x = L := mem_wordClass.mp hx
  have hzx : z ≠ x := by
    rintro rfl
    exact notMem_A_of_mem_wordClass G h r hL hx hz
  have hmem : z ∈ wordSup G r x :=
    Finset.mem_inter.mpr ⟨mem_nbrC.mpr ⟨hzx, hcol⟩, hz⟩
  rw [hwx] at hmem
  exact hzL hmem

/-! ## The fibre bound -/

/-- **At most six vertices share a five-element support.**  The class together
with `A ∖ L` carries no colour-`0` edge, so it has at most sixteen points. -/
theorem wordClass_card_le_six (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hA : (nbrC G r 0).card = 15) (L : Finset V) (hL : L.card = 5) :
    (wordClass G r L).card ≤ 6 := by
  classical
  have hLne : L.Nonempty := by
    rw [← Finset.card_pos, hL]
    omega
  rcases Finset.eq_empty_or_nonempty (wordClass G r L) with hemp | hne
  · rw [hemp]
    exact Nat.zero_le _
  · have hLsub : L ⊆ nbrC G r 0 := by
      obtain ⟨x, hx⟩ := hne
      rw [← mem_wordClass.mp hx]
      exact wordSup_subset G r x
    set T : Finset V := nbrC G r 0 \ L with hTdef
    have hdisj : Disjoint (wordClass G r L) T := by
      rw [Finset.disjoint_left]
      intro x hx hxT
      exact notMem_A_of_mem_wordClass G h r hLne hx (Finset.mem_sdiff.mp hxT).1
    have hTcard : T.card = 10 := by
      rw [hTdef, Finset.card_sdiff_of_subset hLsub, hA, hL]
    have hfree : ∀ x ∈ wordClass G r L ∪ T, ∀ y ∈ wordClass G r L ∪ T, x ≠ y →
        G.col x y ≠ 0 := by
      intro x hx y hy hxy
      rcases Finset.mem_union.mp hx with hx' | hx'
      · rcases Finset.mem_union.mp hy with hy' | hy'
        · exact col_ne_zero_of_same_class G h r hLne hx' hy' hxy
        · exact col_ne_zero_of_notMem G h r hLne hx' (Finset.mem_sdiff.mp hy').1
            (Finset.mem_sdiff.mp hy').2
      · rcases Finset.mem_union.mp hy with hy' | hy'
        · exact fun hc => col_ne_zero_of_notMem G h r hLne hy' (Finset.mem_sdiff.mp hx').1
            (Finset.mem_sdiff.mp hx').2 (by rw [G.symm y x]; exact hc)
        · exact col0_indep G h r _ (Finset.mem_sdiff.mp hx').1 _
            (Finset.mem_sdiff.mp hy').1 hxy
    have hcard := card_le_sixteen_of_zeroFree G h _ hfree
    rw [Finset.card_union_of_disjoint hdisj, hTcard] at hcard
    omega

/-! ## The two-class bound -/

/-- **Two classes with meeting supports.**  If `L ≠ M` are five-sets with
`L ∩ M ≠ ∅` then `p(L) + p(M) + |L ∩ M| ≤ 11`. -/
theorem wordClass_pair_le (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hA : (nbrC G r 0).card = 15) (L M : Finset V) (hL : L.card = 5) (hM : M.card = 5)
    (hLM : L ≠ M) (hmeet : (L ∩ M).Nonempty) :
    (wordClass G r L).card + (wordClass G r M).card + (L ∩ M).card ≤ 11 := by
  classical
  have hLne : L.Nonempty := by rw [← Finset.card_pos, hL]; omega
  have hMne : M.Nonempty := by rw [← Finset.card_pos, hM]; omega
  -- the degenerate cases: one class empty
  rcases Finset.eq_empty_or_nonempty (wordClass G r L) with hempL | hneL
  · have h1 := wordClass_card_le_six G h r hA M hM
    have h2 : (L ∩ M).card ≤ 5 := by
      have : (L ∩ M).card ≤ M.card := Finset.card_le_card Finset.inter_subset_right
      omega
    rw [hempL, Finset.card_empty]
    omega
  rcases Finset.eq_empty_or_nonempty (wordClass G r M) with hempM | hneM
  · have h1 := wordClass_card_le_six G h r hA L hL
    have h2 : (L ∩ M).card ≤ 5 := by
      have : (L ∩ M).card ≤ L.card := Finset.card_le_card Finset.inter_subset_left
      omega
    rw [hempM, Finset.card_empty]
    omega
  -- the main case
  have hLsub : L ⊆ nbrC G r 0 := by
    obtain ⟨x, hx⟩ := hneL
    rw [← mem_wordClass.mp hx]
    exact wordSup_subset G r x
  have hMsub : M ⊆ nbrC G r 0 := by
    obtain ⟨x, hx⟩ := hneM
    rw [← mem_wordClass.mp hx]
    exact wordSup_subset G r x
  set T : Finset V := nbrC G r 0 \ (L ∪ M) with hTdef
  have hTcard : T.card = 15 - (L ∪ M).card := by
    rw [hTdef, Finset.card_sdiff_of_subset (Finset.union_subset hLsub hMsub), hA]
  have hdisjLM : Disjoint (wordClass G r L) (wordClass G r M) := by
    rw [Finset.disjoint_left]
    intro x hx hx'
    exact hLM ((mem_wordClass.mp hx).symm.trans (mem_wordClass.mp hx'))
  have hdisjLT : Disjoint (wordClass G r L) T := by
    rw [Finset.disjoint_left]
    intro x hx hxT
    exact notMem_A_of_mem_wordClass G h r hLne hx (Finset.mem_sdiff.mp hxT).1
  have hdisjMT : Disjoint (wordClass G r M) T := by
    rw [Finset.disjoint_left]
    intro x hx hxT
    exact notMem_A_of_mem_wordClass G h r hMne hx (Finset.mem_sdiff.mp hxT).1
  have hfree : ∀ x ∈ wordClass G r L ∪ wordClass G r M ∪ T,
      ∀ y ∈ wordClass G r L ∪ wordClass G r M ∪ T, x ≠ y → G.col x y ≠ 0 := by
    intro x hx y hy hxy
    rcases Finset.mem_union.mp hx with hx' | hx'
    · rcases Finset.mem_union.mp hx' with hx'' | hx''
      · rcases Finset.mem_union.mp hy with hy' | hy'
        · rcases Finset.mem_union.mp hy' with hy'' | hy''
          · exact col_ne_zero_of_same_class G h r hLne hx'' hy'' hxy
          · exact col_ne_zero_of_meet G h r hmeet hx'' hy'' hxy
        · exact col_ne_zero_of_notMem G h r hLne hx''
            (Finset.mem_sdiff.mp hy').1
            (fun hc => (Finset.mem_sdiff.mp hy').2 (Finset.mem_union_left M hc))
      · rcases Finset.mem_union.mp hy with hy' | hy'
        · rcases Finset.mem_union.mp hy' with hy'' | hy''
          · exact fun hc => col_ne_zero_of_meet (x := y) (y := x) G h r hmeet hy'' hx''
              (Ne.symm hxy) (by rw [G.symm y x]; exact hc)
          · exact col_ne_zero_of_same_class G h r hMne hx'' hy'' hxy
        · exact col_ne_zero_of_notMem G h r hMne hx''
            (Finset.mem_sdiff.mp hy').1
            (fun hc => (Finset.mem_sdiff.mp hy').2 (Finset.mem_union_right L hc))
    · rcases Finset.mem_union.mp hy with hy' | hy'
      · rcases Finset.mem_union.mp hy' with hy'' | hy''
        · exact fun hc => col_ne_zero_of_notMem G h r hLne hy''
            (Finset.mem_sdiff.mp hx').1
            (fun hc' => (Finset.mem_sdiff.mp hx').2 (Finset.mem_union_left M hc'))
            (by rw [G.symm y x]; exact hc)
        · exact fun hc => col_ne_zero_of_notMem G h r hMne hy''
            (Finset.mem_sdiff.mp hx').1
            (fun hc' => (Finset.mem_sdiff.mp hx').2 (Finset.mem_union_right L hc'))
            (by rw [G.symm y x]; exact hc)
      · exact col0_indep G h r _ (Finset.mem_sdiff.mp hx').1 _
          (Finset.mem_sdiff.mp hy').1 hxy
  have hcard := card_le_sixteen_of_zeroFree G h _ hfree
  have hun : (wordClass G r L ∪ wordClass G r M ∪ T).card
      = (wordClass G r L).card + (wordClass G r M).card + T.card := by
    rw [Finset.card_union_of_disjoint]
    · rw [Finset.card_union_of_disjoint hdisjLM]
    · rw [Finset.disjoint_union_left]
      exact ⟨hdisjLT, hdisjMT⟩
  have h1 : (wordClass G r L).card + (wordClass G r M).card + T.card ≤ 16 := by
    rw [← hun]
    exact hcard
  have hsum : (L ∪ M).card + (L ∩ M).card = 10 := by
    have := Finset.card_union_add_card_inter L M
    omega
  have h2 : T.card = 5 + (L ∩ M).card := by
    rw [hTcard]
    omega
  have h3 := h1
  rw [h2] at h3
  omega

/-! ## Three classes cannot be pairwise meeting -/

/-- A two-term intersection bound. -/
theorem card_inter_union_le_two (s a b : Finset V) :
    (s ∩ (a ∪ b)).card ≤ (s ∩ a).card + (s ∩ b).card := by
  have hsub : s ∩ (a ∪ b) ⊆ (s ∩ a) ∪ (s ∩ b) := by
    intro x hx
    simp only [Finset.mem_inter, Finset.mem_union] at hx ⊢
    tauto
  calc (s ∩ (a ∪ b)).card ≤ ((s ∩ a) ∪ (s ∩ b)).card := Finset.card_le_card hsub
    _ ≤ (s ∩ a).card + (s ∩ b).card := Finset.card_union_le _ _

/-- A three-term intersection bound. -/
theorem card_inter_union_le_three (s a b c : Finset V) :
    (s ∩ (a ∪ b ∪ c)).card ≤ (s ∩ a).card + (s ∩ b).card + (s ∩ c).card := by
  have hsub : s ∩ (a ∪ b ∪ c) ⊆ (s ∩ a) ∪ (s ∩ b) ∪ (s ∩ c) := by
    intro x hx
    simp only [Finset.mem_inter, Finset.mem_union] at hx ⊢
    tauto
  calc (s ∩ (a ∪ b ∪ c)).card ≤ ((s ∩ a) ∪ (s ∩ b) ∪ (s ∩ c)).card :=
        Finset.card_le_card hsub
    _ ≤ (s ∩ a).card + (s ∩ b).card + (s ∩ c).card := by
        have h1 := Finset.card_union_le ((s ∩ a) ∪ (s ∩ b)) (s ∩ c)
        have h2 := Finset.card_union_le (s ∩ a) (s ∩ b)
        omega

/-- The class of a five-set is nonempty, and its set lies in `A`. -/
theorem subset_of_five_le (G : EdgeCol V 4) (r : V) {L : Finset V}
    (hp : 5 ≤ (wordClass G r L).card) : L ⊆ nbrC G r 0 := by
  have hne : (wordClass G r L).Nonempty := Finset.card_pos.mp (by omega)
  obtain ⟨x, hx⟩ := hne
  rw [← mem_wordClass.mp hx]
  exact wordSup_subset G r x

/-- **No three classes are pairwise meeting.**  Three five-sets meeting pairwise
carry `5 + 5 + 5` words whose union with `A` outside the union of the five-sets
has order at least `17`, impossible in three colours. -/
theorem no_three_pairwise (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hA : (nbrC G r 0).card = 15) (L M N : Finset V)
    (hL : L.card = 5) (hM : M.card = 5) (hN : N.card = 5)
    (hLM : L ≠ M) (hLN : L ≠ N) (hMN : M ≠ N)
    (hmLM : (L ∩ M).Nonempty) (hmLN : (L ∩ N).Nonempty) (hmMN : (M ∩ N).Nonempty)
    (hpL : 5 ≤ (wordClass G r L).card) (hpM : 5 ≤ (wordClass G r M).card)
    (hpN : 5 ≤ (wordClass G r N).card) : False := by
  classical
  have hLne : L.Nonempty := by rw [← Finset.card_pos, hL]; omega
  have hMne : M.Nonempty := by rw [← Finset.card_pos, hM]; omega
  have hNne : N.Nonempty := by rw [← Finset.card_pos, hN]; omega
  have hLsub : L ⊆ nbrC G r 0 := subset_of_five_le G r hpL
  have hMsub : M ⊆ nbrC G r 0 := subset_of_five_le G r hpM
  have hNsub : N ⊆ nbrC G r 0 := subset_of_five_le G r hpN
  -- `|L ∪ M| ≤ 9`
  have hLM10 : (L ∪ M).card + (L ∩ M).card = 10 := by
    have := Finset.card_union_add_card_inter L M
    omega
  -- `|L ∪ M ∪ N| ≤ 13`
  have hNInter : 1 ≤ (N ∩ (L ∪ M)).card := by
    obtain ⟨a, ha⟩ := hmLN
    have : a ∈ N ∩ (L ∪ M) := by
      obtain ⟨haL, haN⟩ := Finset.mem_inter.mp ha
      exact Finset.mem_inter.mpr ⟨haN, Finset.mem_union_left M haL⟩
    exact Finset.card_pos.mpr ⟨a, this⟩
  have hLMge : 1 ≤ (L ∩ M).card := by
    obtain ⟨a, ha⟩ := hmLM
    exact Finset.card_pos.mpr ⟨a, ha⟩
  have h3 : (L ∪ M ∪ N).card + (N ∩ (L ∪ M)).card = (L ∪ M).card + 5 := by
    have h := Finset.card_union_add_card_inter (L ∪ M) N
    rw [hN, Finset.inter_comm] at h
    exact h
  have hu13 : (L ∪ M ∪ N).card ≤ 13 := by omega
  -- the zero-free set
  set T : Finset V := nbrC G r 0 \ (L ∪ M ∪ N) with hTdef
  have hTsub : T ⊆ nbrC G r 0 := Finset.sdiff_subset
  have hTcard : T.card = 15 - (L ∪ M ∪ N).card := by
    rw [hTdef, Finset.card_sdiff_of_subset (Finset.union_subset (Finset.union_subset hLsub hMsub) hNsub), hA]
  have hnotL : ∀ z ∈ T, z ∉ L := by
    intro z hz
    exact fun hc => (Finset.mem_sdiff.mp hz).2 (Finset.mem_union_left N (Finset.mem_union_left M hc))
  have hnotM : ∀ z ∈ T, z ∉ M := by
    intro z hz
    exact fun hc => (Finset.mem_sdiff.mp hz).2 (Finset.mem_union_left N (Finset.mem_union_right L hc))
  have hnotN : ∀ z ∈ T, z ∉ N := by
    intro z hz
    exact fun hc => (Finset.mem_sdiff.mp hz).2 (Finset.mem_union_right (L ∪ M) hc)
  have hfree : ∀ x ∈ wordClass G r L ∪ wordClass G r M ∪ wordClass G r N ∪ T,
      ∀ y ∈ wordClass G r L ∪ wordClass G r M ∪ wordClass G r N ∪ T, x ≠ y →
      G.col x y ≠ 0 := by
    intro x hx y hy hxy
    have hx' : x ∈ wordClass G r L ∪ wordClass G r M ∪ wordClass G r N ∨ x ∈ T :=
      Finset.mem_union.mp hx
    have hy' : y ∈ wordClass G r L ∪ wordClass G r M ∪ wordClass G r N ∨ y ∈ T :=
      Finset.mem_union.mp hy
    rcases hx' with hx'' | hxT
    · rcases Finset.mem_union.mp hx'' with hx3 | hx3
      · rcases Finset.mem_union.mp hx3 with hxL | hxM
        · rcases hy' with hy'' | hyT
          · rcases Finset.mem_union.mp hy'' with hy3 | hy3
            · rcases Finset.mem_union.mp hy3 with hyL | hyM
              · exact col_ne_zero_of_same_class G h r hLne hxL hyL hxy
              · exact col_ne_zero_of_meet G h r hmLM hxL hyM hxy
            · exact col_ne_zero_of_meet G h r hmLN hxL hy3 hxy
          · exact col_ne_zero_of_notMem G h r hLne hxL (hTsub hyT) (hnotL y hyT)
        · rcases hy' with hy'' | hyT
          · rcases Finset.mem_union.mp hy'' with hy3 | hy3
            · rcases Finset.mem_union.mp hy3 with hyL | hyM
              · exact fun hc => col_ne_zero_of_meet G h r hmLM hyL hxM hxy.symm
                  (by rw [G.symm y x]; exact hc)
              · exact col_ne_zero_of_same_class G h r hMne hxM hyM hxy
            · exact col_ne_zero_of_meet G h r hmMN hxM hy3 hxy
          · exact col_ne_zero_of_notMem G h r hMne hxM (hTsub hyT) (hnotM y hyT)
      · rcases hy' with hy'' | hyT
        · rcases Finset.mem_union.mp hy'' with hy3 | hy3
          · rcases Finset.mem_union.mp hy3 with hyL | hyM
            · exact fun hc => col_ne_zero_of_meet G h r hmLN hyL hx3 hxy.symm
                (by rw [G.symm y x]; exact hc)
            · exact fun hc => col_ne_zero_of_meet G h r hmMN hyM hx3 hxy.symm
                (by rw [G.symm y x]; exact hc)
          · exact col_ne_zero_of_same_class G h r hNne hx3 hy3 hxy
        · exact col_ne_zero_of_notMem G h r hNne hx3 (hTsub hyT) (hnotN y hyT)
    · rcases hy' with hy'' | hyT
      · rcases Finset.mem_union.mp hy'' with hy3 | hy3
        · rcases Finset.mem_union.mp hy3 with hyL | hyM
          · exact fun hc => col_ne_zero_of_notMem G h r hLne hyL (hTsub hxT) (hnotL x hxT)
              (by rw [G.symm y x]; exact hc)
          · exact fun hc => col_ne_zero_of_notMem G h r hMne hyM (hTsub hxT) (hnotM x hxT)
              (by rw [G.symm y x]; exact hc)
        · exact fun hc => col_ne_zero_of_notMem G h r hNne hy3 (hTsub hxT) (hnotN x hxT)
            (by rw [G.symm y x]; exact hc)
      · exact col0_indep G h r _ (hTsub hxT) _ (hTsub hyT) hxy
  have hcard := card_le_sixteen_of_zeroFree G h _ hfree
  have hdisj1 : Disjoint (wordClass G r L) (wordClass G r M) := by
    rw [Finset.disjoint_left]
    intro x hx hx'
    exact hLM ((mem_wordClass.mp hx).symm.trans (mem_wordClass.mp hx'))
  have hdisj2 : Disjoint (wordClass G r L) (wordClass G r N) := by
    rw [Finset.disjoint_left]
    intro x hx hx'
    exact hLN ((mem_wordClass.mp hx).symm.trans (mem_wordClass.mp hx'))
  have hdisj3 : Disjoint (wordClass G r M) (wordClass G r N) := by
    rw [Finset.disjoint_left]
    intro x hx hx'
    exact hMN ((mem_wordClass.mp hx).symm.trans (mem_wordClass.mp hx'))
  have hdisj4 : ∀ Li : Finset V, Li = L ∨ Li = M ∨ Li = N →
      Disjoint (wordClass G r Li) T := by
    rintro Li (rfl | rfl | rfl)
    · rw [Finset.disjoint_left]
      intro x hx hxT
      exact notMem_A_of_mem_wordClass G h r hLne hx (hTsub hxT)
    · rw [Finset.disjoint_left]
      intro x hx hxT
      exact notMem_A_of_mem_wordClass G h r hMne hx (hTsub hxT)
    · rw [Finset.disjoint_left]
      intro x hx hxT
      exact notMem_A_of_mem_wordClass G h r hNne hx (hTsub hxT)
  have hun : (wordClass G r L ∪ wordClass G r M ∪ wordClass G r N ∪ T).card
      = (wordClass G r L).card + (wordClass G r M).card + (wordClass G r N).card
        + T.card := by
    rw [Finset.card_union_of_disjoint]
    · rw [Finset.card_union_of_disjoint]
      · rw [Finset.card_union_of_disjoint hdisj1]
      · rw [Finset.disjoint_union_left]
        exact ⟨hdisj2, hdisj3⟩
    · rw [Finset.disjoint_union_left, Finset.disjoint_union_left]
      exact ⟨⟨hdisj4 L (Or.inl rfl), hdisj4 M (Or.inr (Or.inl rfl))⟩,
        hdisj4 N (Or.inr (Or.inr rfl))⟩
  rw [hun] at hcard
  omega

/-! ## At most three fivefold classes -/

/-- **The union bound for four five-sets.**  Four five-subsets of a 15-set
satisfy `Σ_{i<j} |L_i ∩ L_j| ≥ 5`. -/
theorem sum_inter_four_ge (A L0 L1 L2 L3 : Finset V) (hA : A.card = 15)
    (h0 : L0 ⊆ A) (h1 : L1 ⊆ A) (h2 : L2 ⊆ A) (h3 : L3 ⊆ A)
    (hc0 : L0.card = 5) (hc1 : L1.card = 5) (hc2 : L2.card = 5) (hc3 : L3.card = 5) :
    5 ≤ (L0 ∩ L1).card + (L0 ∩ L2).card + (L0 ∩ L3).card
      + (L1 ∩ L2).card + (L1 ∩ L3).card + (L2 ∩ L3).card := by
  classical
  have e01 : (L0 ∪ L1).card + (L0 ∩ L1).card = 10 := by
    have := Finset.card_union_add_card_inter L0 L1
    omega
  have e012 : (L0 ∪ L1 ∪ L2).card + (L2 ∩ (L0 ∪ L1)).card = (L0 ∪ L1).card + 5 := by
    have h := Finset.card_union_add_card_inter (L0 ∪ L1) L2
    rw [hc2, Finset.inter_comm] at h
    exact h
  have i2 : (L2 ∩ (L0 ∪ L1)).card ≤ (L0 ∩ L2).card + (L1 ∩ L2).card := by
    have h := card_inter_union_le_two L2 L0 L1
    rw [Finset.inter_comm L2 L0, Finset.inter_comm L2 L1] at h
    exact h
  have e0123 : (L0 ∪ L1 ∪ L2 ∪ L3).card + (L3 ∩ (L0 ∪ L1 ∪ L2)).card
      = (L0 ∪ L1 ∪ L2).card + 5 := by
    have h := Finset.card_union_add_card_inter (L0 ∪ L1 ∪ L2) L3
    rw [hc3, Finset.inter_comm] at h
    exact h
  have i3 : (L3 ∩ (L0 ∪ L1 ∪ L2)).card
      ≤ (L0 ∩ L3).card + (L1 ∩ L3).card + (L2 ∩ L3).card := by
    have h := card_inter_union_le_three L3 L0 L1 L2
    rw [Finset.inter_comm L3 L0, Finset.inter_comm L3 L1, Finset.inter_comm L3 L2] at h
    exact h
  have hU : (L0 ∪ L1 ∪ L2 ∪ L3).card ≤ 15 := by
    rw [← hA]
    exact Finset.card_le_card (Finset.union_subset
      (Finset.union_subset (Finset.union_subset h0 h1) h2) h3)
  omega

/-- **At most three distinct five-sets can each carry five words.**  Four of them
satisfy `Σ_{i<j} |L_i ∩ L_j| ≥ 5` with every term at most one, so some three meet
pairwise, which `no_three_pairwise` excludes. -/
theorem card_le_three (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hA : (nbrC G r 0).card = 15) (S : Finset (Finset V))
    (hsub : ∀ L ∈ S, L ⊆ nbrC G r 0) (hcard : ∀ L ∈ S, L.card = 5)
    (hfive : ∀ L ∈ S, 5 ≤ (wordClass G r L).card) : S.card ≤ 3 := by
  classical
  by_contra hcon
  push Not at hcon
  obtain ⟨L0, hL0S⟩ := Finset.card_pos.mp (show 0 < S.card by omega)
  obtain ⟨L1, hL1S⟩ := Finset.card_pos.mp (show 0 < (S.erase L0).card by
    rw [Finset.card_erase_of_mem hL0S]; omega)
  obtain ⟨L2, hL2S⟩ := Finset.card_pos.mp (show 0 < ((S.erase L0).erase L1).card by
    rw [Finset.card_erase_of_mem hL1S, Finset.card_erase_of_mem hL0S]; omega)
  obtain ⟨L3, hL3S⟩ := Finset.card_pos.mp
    (show 0 < (((S.erase L0).erase L1).erase L2).card by
      rw [Finset.card_erase_of_mem hL2S, Finset.card_erase_of_mem hL1S,
        Finset.card_erase_of_mem hL0S]; omega)
  have hL0 : L0 ∈ S := hL0S
  have hL1 : L1 ∈ S := (Finset.mem_erase.mp hL1S).2
  have h20 : L2 ≠ L0 := (Finset.mem_erase.mp (Finset.mem_erase.mp hL2S).2).1
  have h21 : L2 ≠ L1 := (Finset.mem_erase.mp hL2S).1
  have hL2 : L2 ∈ S := (Finset.mem_erase.mp (Finset.mem_erase.mp hL2S).2).2
  have h32 : L3 ≠ L2 := (Finset.mem_erase.mp hL3S).1
  have h31 : L3 ≠ L1 := (Finset.mem_erase.mp (Finset.mem_erase.mp hL3S).2).1
  have h30 : L3 ≠ L0 := (Finset.mem_erase.mp (Finset.mem_erase.mp (Finset.mem_erase.mp hL3S).2).2).1
  have hL3 : L3 ∈ S := (Finset.mem_erase.mp (Finset.mem_erase.mp (Finset.mem_erase.mp hL3S).2).2).2
  have h10 : L1 ≠ L0 := (Finset.mem_erase.mp hL1S).1
  -- the pair capacities
  have ht : ∀ L ∈ S, ∀ M ∈ S, L ≠ M → (L ∩ M).card ≤ 1 := by
    intro L hLS M hMS hLM
    by_cases hm : (L ∩ M).Nonempty
    · have h1 := wordClass_pair_le G h r hA L M (hcard L hLS) (hcard M hMS) hLM hm
      have h2 := hfive L hLS
      have h3 := hfive M hMS
      omega
    · have hemp : L ∩ M = ∅ := Finset.not_nonempty_iff_eq_empty.mp hm
      rw [hemp, Finset.card_empty]
      omega
  have hsum := sum_inter_four_ge (nbrC G r 0) L0 L1 L2 L3 hA
    (hsub L0 hL0) (hsub L1 hL1) (hsub L2 hL2) (hsub L3 hL3)
    (hcard L0 hL0) (hcard L1 hL1) (hcard L2 hL2) (hcard L3 hL3)
  have b01 := ht L0 hL0 L1 hL1 (Ne.symm h10)
  have b02 := ht L0 hL0 L2 hL2 (Ne.symm h20)
  have b03 := ht L0 hL0 L3 hL3 (Ne.symm h30)
  have b12 := ht L1 hL1 L2 hL2 (Ne.symm h21)
  have b13 := ht L1 hL1 L3 hL3 (Ne.symm h31)
  have b23 := ht L2 hL2 L3 hL3 (Ne.symm h32)
  have htri :
      (1 ≤ (L0 ∩ L1).card ∧ 1 ≤ (L0 ∩ L2).card ∧ 1 ≤ (L1 ∩ L2).card) ∨
      (1 ≤ (L0 ∩ L1).card ∧ 1 ≤ (L0 ∩ L3).card ∧ 1 ≤ (L1 ∩ L3).card) ∨
      (1 ≤ (L0 ∩ L2).card ∧ 1 ≤ (L0 ∩ L3).card ∧ 1 ≤ (L2 ∩ L3).card) ∨
      (1 ≤ (L1 ∩ L2).card ∧ 1 ≤ (L1 ∩ L3).card ∧ 1 ≤ (L2 ∩ L3).card) := by
    omega
  have key : ∀ (X Y Z : Finset V), X ∈ S → Y ∈ S → Z ∈ S → X ≠ Y → X ≠ Z → Y ≠ Z →
      1 ≤ (X ∩ Y).card → 1 ≤ (X ∩ Z).card → 1 ≤ (Y ∩ Z).card → False := by
    intro X Y Z hXS hYS hZS hXY hXZ hYZ h1 h2 h3
    exact no_three_pairwise G h r hA X Y Z (hcard X hXS) (hcard Y hYS) (hcard Z hZS)
      hXY hXZ hYZ (Finset.card_pos.mp (by omega)) (Finset.card_pos.mp (by omega))
      (Finset.card_pos.mp (by omega)) (hfive X hXS) (hfive Y hYS) (hfive Z hZS)
  rcases htri with ⟨h1, h2, h3⟩ | ⟨h1, h2, h3⟩ | ⟨h1, h2, h3⟩ | ⟨h1, h2, h3⟩
  · exact key L0 L1 L2 hL0 hL1 hL2 (Ne.symm h10) (Ne.symm h20) (Ne.symm h21) h1 h2 h3
  · exact key L0 L1 L3 hL0 hL1 hL3 (Ne.symm h10) (Ne.symm h30) (Ne.symm h31) h1 h2 h3
  · exact key L0 L2 L3 hL0 hL2 hL3 (Ne.symm h20) (Ne.symm h30) (Ne.symm h32) h1 h2 h3
  · exact key L1 L2 L3 hL1 hL2 hL3 (Ne.symm h21) (Ne.symm h31) (Ne.symm h32) h1 h2 h3

/-! ## The reduction to nine distinct supports -/

/-- **At least nine distinct supports.**  In the `(15,14,14,14)` setting the
`58 - 1 - 15 = 42` outside vertices each have a five-element support; each support
carries at most six of them and at most three supports carry five or more.  Then
`42 ≤ 4k + 6`, so `k ≥ 9`.  (The package's sharper bound of twelve needs the
integer certificates of its §2 on top of this.) -/
theorem distinct_supports_ge_nine (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hV : Fintype.card V = 58) (hA : (nbrC G r 0).card = 15)
    (hword : ∀ x : V, x ≠ r → x ∉ nbrC G r 0 → (wordSup G r x).card = 5) :
    9 ≤ (((Finset.univ \ nbrC G r 0) \ {r}).image (fun x => wordSup G r x)).card := by
  classical
  set W : Finset V := (Finset.univ \ nbrC G r 0) \ {r} with hWdef
  set f : V → Finset V := fun x => wordSup G r x with hfdef
  have hr0 : r ∉ nbrC G r 0 := by
    rw [mem_nbrC]
    exact fun hh => hh.1 rfl
  have hW42 : W.card = 42 := by
    have h1 : (Finset.univ \ nbrC G r 0 : Finset V).card = 58 - 15 := by
      rw [Finset.card_sdiff_of_subset (Finset.subset_univ _), Finset.card_univ, hV, hA]
    have h2 : ({r} : Finset V) ⊆ (Finset.univ \ nbrC G r 0) := by
      intro x hx
      rw [Finset.mem_singleton] at hx
      subst hx
      exact Finset.mem_sdiff.mpr ⟨Finset.mem_univ _, hr0⟩
    rw [hWdef, Finset.card_sdiff_of_subset h2, h1, Finset.card_singleton]
  -- every member of `W` has a five-element support
  have hW5 : ∀ x ∈ W, (f x).card = 5 := by
    intro x hx
    rw [hWdef, Finset.mem_sdiff, Finset.mem_sdiff, Finset.mem_singleton] at hx
    exact hword x hx.2 hx.1.2
  -- each fibre is at most six
  have hfib6 : ∀ L ∈ W.image f, (W.filter (fun x => f x = L)).card ≤ 6 := by
    intro L hL
    obtain ⟨x, hxW, hxL⟩ := Finset.mem_image.mp hL
    have hsub : W.filter (fun y => f y = L) ⊆ wordClass G r L := by
      intro y hy
      exact mem_wordClass.mpr (Finset.mem_filter.mp hy).2
    refine le_trans (Finset.card_le_card hsub) (wordClass_card_le_six G h r hA L ?_)
    rw [← hxL]
    exact hW5 x hxW
  -- the set of supports carrying five or more words
  set T : Finset (Finset V) :=
    (W.image f).filter (fun L => 5 ≤ (W.filter (fun x => f x = L)).card) with hTdef
  have hTsub : T ⊆ W.image f := Finset.filter_subset _ _
  have hT3 : T.card ≤ 3 := by
    refine card_le_three G h r hA T ?_ ?_ ?_
    · -- each member of `T` is a five-set inside `A`
      intro L hL
      have hLT : L ∈ T := hL
      have hL5 : 5 ≤ (W.filter (fun x => f x = L)).card := (Finset.mem_filter.mp hLT).2
      have hne : (W.filter (fun x => f x = L)).Nonempty := Finset.card_pos.mp (by omega)
      obtain ⟨x, hx⟩ := hne
      have hxeq : f x = L := (Finset.mem_filter.mp hx).2
      have hcls : 5 ≤ (wordClass G r L).card := by
        have hsub : W.filter (fun y => f y = L) ⊆ wordClass G r L := by
          intro y hy
          exact mem_wordClass.mpr (Finset.mem_filter.mp hy).2
        calc 5 ≤ (W.filter (fun y => f y = L)).card := hL5
          _ ≤ (wordClass G r L).card := Finset.card_le_card hsub
      rw [← hxeq]
      exact wordSup_subset G r x
    · intro L hL
      obtain ⟨x, hxW, hxL⟩ := Finset.mem_image.mp (hTsub hL)
      rw [← hxL]
      exact hW5 x hxW
    · intro L hL
      have hL5 : 5 ≤ (W.filter (fun x => f x = L)).card := (Finset.mem_filter.mp hL).2
      have hsub : W.filter (fun y => f y = L) ⊆ wordClass G r L := by
        intro y hy
        exact mem_wordClass.mpr (Finset.mem_filter.mp hy).2
      calc 5 ≤ (W.filter (fun y => f y = L)).card := hL5
        _ ≤ (wordClass G r L).card := Finset.card_le_card hsub
  -- the fibre sum, split at `T`
  have hsum : W.card = ∑ L ∈ W.image f, (W.filter (fun x => f x = L)).card :=
    Finset.card_eq_sum_card_image f W
  have hsplit : ∑ L ∈ W.image f, (W.filter (fun x => f x = L)).card
      = ∑ L ∈ (W.image f) \ T, (W.filter (fun x => f x = L)).card
        + ∑ L ∈ T, (W.filter (fun x => f x = L)).card :=
    (Finset.sum_sdiff hTsub).symm
  have hA1 : ∑ L ∈ T, (W.filter (fun x => f x = L)).card ≤ T.card * 6 := by
    calc ∑ L ∈ T, (W.filter (fun x => f x = L)).card
        ≤ ∑ _L ∈ T, 6 := Finset.sum_le_sum (fun L hL => hfib6 L (hTsub hL))
      _ = T.card * 6 := Finset.sum_const_nat (fun _ _ => rfl)
  have hA2 : ∑ L ∈ (W.image f) \ T, (W.filter (fun x => f x = L)).card
      ≤ ((W.image f) \ T).card * 4 := by
    calc ∑ L ∈ (W.image f) \ T, (W.filter (fun x => f x = L)).card
        ≤ ∑ _L ∈ (W.image f) \ T, 4 := by
          refine Finset.sum_le_sum ?_
          intro L hL
          have hLimg : L ∈ W.image f := (Finset.mem_sdiff.mp hL).1
          have hLnot : L ∉ T := (Finset.mem_sdiff.mp hL).2
          have h6 := hfib6 L hLimg
          by_contra hcon
          exact hLnot (Finset.mem_filter.mpr ⟨hLimg, by omega⟩)
      _ = ((W.image f) \ T).card * 4 := Finset.sum_const_nat (fun _ _ => rfl)
  have hcardT : ((W.image f) \ T).card = (W.image f).card - T.card :=
    Finset.card_sdiff_of_subset hTsub
  omega


/-! ## The pairwise capacity `c(i,j)` of the package's §2 -/

/-- Distinct five-sets meet in at most four points. -/
theorem inter_card_le_four {L M : Finset V} (hL : L.card = 5) (hM : M.card = 5)
    (hLM : L ≠ M) : (L ∩ M).card ≤ 4 := by
  have h1 : (L ∩ M).card ≤ 5 := by
    calc (L ∩ M).card ≤ L.card := Finset.card_le_card Finset.inter_subset_left
      _ = 5 := hL
  by_contra hcon
  push Not at hcon
  have h5 : (L ∩ M).card = 5 := le_antisymm h1 (by omega)
  have he : L ∩ M = L :=
    Finset.eq_of_subset_of_card_le Finset.inter_subset_left (by rw [h5, hL])
  have hsub : L ⊆ M := by
    intro x hx
    have hx' : x ∈ L ∩ M := by rw [he]; exact hx
    exact (Finset.mem_inter.mp hx').2
  exact hLM (Finset.eq_of_subset_of_card_le hsub (by rw [hL, hM]))

/-- **The capacity `c(i,j)`.**  Two distinct five-sets `L ≠ M` with `p(L) = i` and
`p(M) = j` meet in at most `max 0 (min 4 (11 - (i + j)))` points — exactly the
intersection bound the package's §2 uses to build its inequality matrix. -/
theorem capacity_aux (a i j : ℕ) (ha : a ≤ 4) (hij : i + j + a ≤ 11) :
    a ≤ max 0 (min 4 (11 - (i + j))) := by
  omega

/-- **The capacity `c(i,j)`.**  Two distinct five-sets `L ≠ M` with `p(L) = i` and
`p(M) = j` meet in at most `max 0 (min 4 (11 - (i + j)))` points — exactly the
intersection bound the package's §2 uses to build its inequality matrix. -/
theorem inter_card_le_capacity (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hA : (nbrC G r 0).card = 15) {L M : Finset V} (hL : L.card = 5) (hM : M.card = 5)
    (hLM : L ≠ M) :
    (L ∩ M).card ≤ max 0 (min 4 (11 - ((wordClass G r L).card + (wordClass G r M).card))) := by
  have h4 := inter_card_le_four hL hM hLM
  by_cases hm : (L ∩ M).Nonempty
  · have hpair := wordClass_pair_le G h r hA L M hL hM hLM hm
    exact capacity_aux _ _ _ h4 hpair
  · have hemp : L ∩ M = ∅ := Finset.not_nonempty_iff_eq_empty.mp hm
    rw [hemp, Finset.card_empty]
    exact Nat.zero_le _

/-- **A sixfold class is disjoint from every fivefold class.** -/
theorem sixfold_disjoint (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hA : (nbrC G r 0).card = 15) {L M : Finset V} (hL : L.card = 5) (hM : M.card = 5)
    (hLM : L ≠ M) (h6 : 6 ≤ (wordClass G r L).card) (h5 : 5 ≤ (wordClass G r M).card) :
    L ∩ M = ∅ := by
  by_contra hne
  have hm : (L ∩ M).Nonempty := Finset.nonempty_iff_ne_empty.mpr hne
  have hpair := wordClass_pair_le G h r hA L M hL hM hLM hm
  have h1 : 1 ≤ (L ∩ M).card := Finset.card_pos.mpr hm
  omega

/-- **At most two fivefold classes pass through a point of `A`.** -/
theorem two_fivefold_at_point (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hA : (nbrC G r 0).card = 15) (S : Finset (Finset V))
    (hcard : ∀ L ∈ S, L.card = 5) (hfive : ∀ L ∈ S, 5 ≤ (wordClass G r L).card)
    {a : V} (haS : ∀ L ∈ S, a ∈ L) : S.card ≤ 2 := by
  classical
  by_contra hcon
  push Not at hcon
  obtain ⟨L0, hL0S⟩ := Finset.card_pos.mp (show 0 < S.card by omega)
  obtain ⟨L1, hL1S⟩ := Finset.card_pos.mp (show 0 < (S.erase L0).card by
    rw [Finset.card_erase_of_mem hL0S]; omega)
  obtain ⟨L2, hL2S⟩ := Finset.card_pos.mp (show 0 < ((S.erase L0).erase L1).card by
    rw [Finset.card_erase_of_mem hL1S, Finset.card_erase_of_mem hL0S]; omega)
  have hL1 : L1 ∈ S := (Finset.mem_erase.mp hL1S).2
  have hL2 : L2 ∈ S := (Finset.mem_erase.mp (Finset.mem_erase.mp hL2S).2).2
  have h10 : L1 ≠ L0 := (Finset.mem_erase.mp hL1S).1
  have h21 : L2 ≠ L1 := (Finset.mem_erase.mp hL2S).1
  have h20 : L2 ≠ L0 := (Finset.mem_erase.mp (Finset.mem_erase.mp hL2S).2).1
  have hm01 : (L0 ∩ L1).Nonempty := ⟨a, Finset.mem_inter.mpr ⟨haS L0 hL0S, haS L1 hL1⟩⟩
  have hm02 : (L0 ∩ L2).Nonempty := ⟨a, Finset.mem_inter.mpr ⟨haS L0 hL0S, haS L2 hL2⟩⟩
  have hm12 : (L1 ∩ L2).Nonempty := ⟨a, Finset.mem_inter.mpr ⟨haS L1 hL1, haS L2 hL2⟩⟩
  exact no_three_pairwise G h r hA L0 L1 L2 (hcard L0 hL0S) (hcard L1 hL1)
    (hcard L2 hL2) (Ne.symm h10) (Ne.symm h20) (Ne.symm h21) hm01 hm02 hm12
    (hfive L0 hL0S) (hfive L1 hL1) (hfive L2 hL2)

/-! ## A sender's zero neighbourhood covers thirteen points -/

/-- **The sender cover.**  If `a` is a point of the 15-arm with `d_0(a) = 15`, the
fourteen outside colour-`0` neighbours of `a` have supports whose union meets `A`
in at least 13 points: otherwise the fourteen words together with the complement
of that union would be a zero-free set of order 17. -/
theorem sender_union_ge_thirteen (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hA : (nbrC G r 0).card = 15) {a : V} (ha : a ∈ nbrC G r 0)
    (hda : (nbrC G a 0).card = 15) :
    13 ≤ ((nbrC G a 0 \ {r}).biUnion (fun x => wordSup G r x)).card := by
  classical
  set X : Finset V := nbrC G a 0 \ {r} with hXdef
  set U : Finset V := X.biUnion (fun x => wordSup G r x) with hUdef
  obtain ⟨har, harc⟩ := mem_nbrC.mp ha
  have hrA : r ∈ nbrC G a 0 := mem_nbrC.mpr ⟨har.symm, by rw [G.symm a r]; exact harc⟩
  have hX14 : X.card = 14 := by
    rw [hXdef, Finset.card_sdiff_of_subset (Finset.singleton_subset_iff.mpr hrA), hda,
      Finset.card_singleton]
  have hUsub : U ⊆ nbrC G r 0 := by
    intro z hz
    rw [hUdef, Finset.mem_biUnion] at hz
    obtain ⟨x, -, hx⟩ := hz
    exact wordSup_subset G r x hx
  have hXA : ∀ x ∈ X, x ∉ nbrC G r 0 := by
    intro x hx hxA
    obtain ⟨hxa, hxcol⟩ := mem_nbrC.mp (Finset.mem_sdiff.mp hx).1
    exact col0_indep G h r a ha x hxA (Ne.symm hxa) hxcol
  have hfree : ∀ p ∈ X ∪ (nbrC G r 0 \ U), ∀ q ∈ X ∪ (nbrC G r 0 \ U), p ≠ q →
      G.col p q ≠ 0 := by
    intro p hp q hq hpq
    rcases Finset.mem_union.mp hp with hpX | hpT <;> rcases Finset.mem_union.mp hq with hqX | hqT
    · obtain ⟨hpa, hpcol⟩ := mem_nbrC.mp (Finset.mem_sdiff.mp hpX).1
      obtain ⟨hqa, hqcol⟩ := mem_nbrC.mp (Finset.mem_sdiff.mp hqX).1
      intro hcol
      exact h a p q (Ne.symm hpa) hpq (Ne.symm hqa)
        ⟨by rw [hpcol, hqcol], by rw [hqcol, hcol]⟩
    · intro hcol
      have hqA : q ∈ nbrC G r 0 := (Finset.mem_sdiff.mp hqT).1
      have hpX' : p ∈ nbrC G a 0 := (Finset.mem_sdiff.mp hpX).1
      have hqp : q ≠ p := by
        rintro rfl
        exact hXA _ hpX hqA
      have hqU : q ∈ U := by
        rw [hUdef, Finset.mem_biUnion]
        exact ⟨p, hpX, Finset.mem_inter.mpr ⟨mem_nbrC.mpr ⟨hqp, hcol⟩, hqA⟩⟩
      exact (Finset.mem_sdiff.mp hqT).2 hqU
    · intro hcol
      have hpA : p ∈ nbrC G r 0 := (Finset.mem_sdiff.mp hpT).1
      have hqX' : q ∈ nbrC G a 0 := (Finset.mem_sdiff.mp hqX).1
      have hpq' : p ≠ q := hpq
      have hpU : p ∈ U := by
        rw [hUdef, Finset.mem_biUnion]
        exact ⟨q, hqX, Finset.mem_inter.mpr
          ⟨mem_nbrC.mpr ⟨hpq', by rw [G.symm q p]; exact hcol⟩, hpA⟩⟩
      exact (Finset.mem_sdiff.mp hpT).2 hpU
    · exact col0_indep G h r _ (Finset.mem_sdiff.mp hpT).1 _
        (Finset.mem_sdiff.mp hqT).1 hpq
  have hdisj : Disjoint X (nbrC G r 0 \ U) := by
    rw [Finset.disjoint_left]
    intro x hx hx'
    exact hXA x hx (Finset.mem_sdiff.mp hx').1
  have hTcard : (nbrC G r 0 \ U).card = 15 - U.card := by
    rw [Finset.card_sdiff_of_subset hUsub, hA]
  have hcard := card_le_sixteen_of_zeroFree G h _ hfree
  rw [Finset.card_union_of_disjoint hdisj, hX14, hTcard] at hcard
  omega

/-- **A sender sees at least three different five-sets.**  The fourteen supports
of a sender's zero neighbours cannot be covered by two five-sets: each contains
`a`, so their union has at most nine points, while the covers reach thirteen. -/
theorem sender_not_two_supports (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hA : (nbrC G r 0).card = 15) {a : V} (ha : a ∈ nbrC G r 0)
    (hda : (nbrC G a 0).card = 15) {L M : Finset V} (hL : L.card = 5) (hM : M.card = 5)
    (haL : a ∈ L) (haM : a ∈ M) :
    ¬ ((nbrC G a 0 \ {r}).biUnion (fun x => wordSup G r x)) ⊆ L ∪ M := by
  intro hsub
  have h1 := sender_union_ge_thirteen G h r hA ha hda
  have h2 : (L ∪ M).card ≤ 9 := by
    have hsum := Finset.card_union_add_card_inter L M
    have hlt : 1 ≤ (L ∩ M).card := Finset.card_pos.mpr ⟨a, Finset.mem_inter.mpr ⟨haL, haM⟩⟩
    omega
  have h3 : ((nbrC G a 0 \ {r}).biUnion (fun x => wordSup G r x)).card ≤ (L ∪ M).card :=
    Finset.card_le_card hsub
  omega

/-- **A sixfold class excludes every other fivefold or sixfold class at its
points.**  This is the pattern restriction `t_5 = 0 or t_4 + t_5 = 1` of the
package's §2. -/
theorem sixfold_excludes_at_point (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (hA : (nbrC G r 0).card = 15) {L M : Finset V} (hL : L.card = 5) (hM : M.card = 5)
    (hLM : L ≠ M) (h6 : 6 ≤ (wordClass G r L).card) (h5 : 5 ≤ (wordClass G r M).card)
    {a : V} (haL : a ∈ L) (haM : a ∈ M) : False := by
  have hemp := sixfold_disjoint G h r hA hL hM hLM h6 h5
  have hmem : a ∈ L ∩ M := Finset.mem_inter.mpr ⟨haL, haM⟩
  rw [hemp] at hmem
  exact Finset.notMem_empty a hmem

end K58

#print axioms K58.card_le_sixteen_of_zeroFree
#print axioms K58.wordClass_card_le_six
#print axioms K58.wordClass_pair_le
#print axioms K58.card_inter_union_le_two
#print axioms K58.card_inter_union_le_three
#print axioms K58.no_three_pairwise
#print axioms K58.sum_inter_four_ge
#print axioms K58.card_le_three
#print axioms K58.distinct_supports_ge_nine
#print axioms K58.inter_card_le_four
#print axioms K58.inter_card_le_capacity
#print axioms K58.sixfold_disjoint
#print axioms K58.two_fivefold_at_point
#print axioms K58.sender_union_ge_thirteen
#print axioms K58.sender_not_two_supports
#print axioms K58.sixfold_excludes_at_point
