/-
K58 supplement (swarm smwrmwgf7, member m6): **the extremal case of the
independent-14 bound is rigid.**

`armFar_le_five` (kernel-checked, `lean/supplement/m4/Interface.lean`) says a
14-point colour-`c`-free set has at most five far points.  This file proves what
happens at the extreme: if there are exactly five, then every far point has
exactly **two** colour-`c` edges into the far set — so the colour-`c` graph on the
five far points is a 5-cycle, and (the same argument in the other direction,
`armFar_le_two` + `indep_le_sixteen`) so is its complement.

This is the first step of the proof that the bound is really 4.  It is the part
that a hand argument can do; the case that has to be killed after it is not local
(see the member's REPORT.md, `PROOF.md` §2-3).

The declarations of `ArmFarBase.lean` are a verbatim copy of
`lean/supplement/m4/Interface.lean` (armFar, indep_le_sixteen, armFar_le_two, …),
which is not on `lean/build.sh`'s import path; the copies are only so that this
file builds on its own.  Lift `armFar_five_zero_degree` next to them in `lean/`;
it needs nothing that is not there.
-/
import ArmFarBase

namespace K58

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- **Rigidity of the extremal case.**  If a 14-point colour-`c`-free set `X` has
exactly five far points, then every far point `z` has exactly two colour-`c`
neighbours among them: three would either close a `c`-triangle through `z` or give
a 17-point `c`-free set, and a `c`-free 15-set has at most two far points. -/
theorem armFar_five_zero_degree (G : EdgeCol V 4) (h : TriangleFree G)
    (X : Finset V) (c : Fin 4)
    (hX : ∀ x ∈ X, ∀ y ∈ X, x ≠ y → G.col x y ≠ c) (h14 : X.card = 14)
    (hZ : (armFar G X c).card = 5) :
    ∀ z ∈ armFar G X c,
      ((((armFar G X c).erase z).filter (fun y => G.col z y = c))).card = 2 := by
  intro z hz
  have hzX : z ∉ X := (mem_armFar.mp hz).1
  have hzXc : ∀ x ∈ X, G.col z x ≠ c := (mem_armFar.mp hz).2
  -- `X ∪ {z}` is `c`-free
  have hXz : ∀ x ∈ X ∪ {z}, ∀ y ∈ X ∪ {z}, x ≠ y → G.col x y ≠ c := by
    intro x hx y hy hxy
    rcases mem_union.mp hx with hxX | hxz
    · rcases mem_union.mp hy with hyX | hyz
      · exact hX x hxX y hyX hxy
      · rw [mem_singleton.mp hyz, G.symm x z]
        exact hzXc x hxX
    · rcases mem_union.mp hy with hyX | hyz
      · rw [mem_singleton.mp hxz]
        exact hzXc y hyX
      · exact absurd ((mem_singleton.mp hxz).trans (mem_singleton.mp hyz).symm) hxy
  have hXz_card : 15 ≤ (X ∪ {z}).card := by
    have hdisj : Disjoint X ({z} : Finset V) := by
      rw [Finset.disjoint_singleton_right]
      exact hzX
    rw [Finset.card_union_of_disjoint hdisj, h14, Finset.card_singleton]
  -- the non-`c` neighbours of `z` in `armFar` are far points of `X ∪ {z}`
  have hBsub : ((armFar G X c).erase z).filter (fun y => G.col z y ≠ c)
      ⊆ armFar G (X ∪ {z}) c := by
    intro y hy
    rw [mem_filter, mem_erase] at hy
    obtain ⟨⟨hyz, hyZ⟩, hyc⟩ := hy
    rw [mem_armFar] at hyZ ⊢
    obtain ⟨hyX, hyXc⟩ := hyZ
    refine ⟨?_, ?_⟩
    · intro hmem
      rcases mem_union.mp hmem with h' | h'
      · exact hyX h'
      · exact hyz (mem_singleton.mp h')
    · intro x hx
      rcases mem_union.mp hx with h' | h'
      · exact hyXc x h'
      · rw [mem_singleton.mp h', G.symm y z]
        exact hyc
  have hB2 : (((armFar G X c).erase z).filter (fun y => G.col z y ≠ c)).card ≤ 2 :=
    le_trans (Finset.card_le_card hBsub) (armFar_le_two G h hXz hXz_card)
  -- three `c`-neighbours of `z` in `armFar` would give a 17-point `c`-free set
  have hA2 : (((armFar G X c).erase z).filter (fun y => G.col z y = c)).card ≤ 2 := by
    by_contra hle
    rw [not_le] at hle
    obtain ⟨T, hTsub, hTcard⟩ := Finset.exists_subset_card_eq (s :=
      ((armFar G X c).erase z).filter (fun y => G.col z y = c)) (show 3 ≤ _ by omega)
    have hTmem : ∀ y ∈ T, y ∈ (armFar G X c).erase z ∧ G.col z y = c :=
      fun y hy => mem_filter.mp (hTsub hy)
    have hTZ : ∀ y ∈ T, y ∈ armFar G X c := fun y hy => (mem_erase.mp (hTmem y hy).1).2
    have hTz : ∀ y ∈ T, G.col z y = c := fun y hy => (hTmem y hy).2
    have hTne : ∀ y ∈ T, y ≠ z := fun y hy => (mem_erase.mp (hTmem y hy).1).1
    have hTX : ∀ y ∈ T, y ∉ X := fun y hy => (mem_armFar.mp (hTZ y hy)).1
    have hTXc : ∀ y ∈ T, ∀ x ∈ X, G.col y x ≠ c := fun y hy => (mem_armFar.mp (hTZ y hy)).2
    -- two `c`-adjacent points of `T` would close a `c`-triangle through `z`
    have hpair : ∀ y ∈ T, ∀ y' ∈ T, y ≠ y' → G.col y y' ≠ c := by
      intro y hy y' hy' hyy' hc
      have h1 : G.col z y = c := hTz y hy
      have h2 : G.col z y' = c := hTz y' hy'
      exact h z y y' (hTne y hy).symm hyy' (hTne y' hy').symm
        ⟨by rw [h1, h2], by rw [h2, hc]⟩
    -- so `X ∪ T` is `c`-free, with 17 points
    have hfree : ∀ y ∈ X ∪ T, ∀ y' ∈ X ∪ T, y ≠ y' → G.col y y' ≠ c := by
      intro y hy y' hy' hyy'
      rcases mem_union.mp hy with hyX | hyT
      · rcases mem_union.mp hy' with hy'X | hy'T
        · exact hX y hyX y' hy'X hyy'
        · rw [G.symm y y']
          exact hTXc y' hy'T y hyX
      · rcases mem_union.mp hy' with hy'X | hy'T
        · exact hTXc y hyT y' hy'X
        · exact hpair y hyT y' hy'T hyy'
    have hcard : (X ∪ T).card = 17 := by
      have hdisj : Disjoint X T :=
        Finset.disjoint_left.mpr (fun a ha haT => hTX a haT ha)
      rw [Finset.card_union_of_disjoint hdisj, h14, hTcard]
    have := indep_le_sixteen G h c (X ∪ T) hfree
    omega
  -- the two pieces partition the four remaining far points
  have hsplit := Finset.card_filter_add_card_filter_not
    (s := (armFar G X c).erase z) (p := fun y => G.col z y = c)
  have hcardErase : ((armFar G X c).erase z).card = 4 := by
    rw [Finset.card_erase_of_mem hz, hZ]
  rw [hcardErase] at hsplit
  have hB2' : (((armFar G X c).erase z).filter (fun y => ¬ (G.col z y = c))).card ≤ 2 := by
    simpa only [ne_eq] using hB2
  omega

end K58

namespace K58

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- **The extremal case, both directions.**  At five far points every far point has
exactly two colour-`c` and exactly two non-`c` edges among the far points, so both
the colour-`c` graph on the five far points and its complement are 5-cycles. -/
theorem armFar_five_nonzero_degree (G : EdgeCol V 4) (h : TriangleFree G)
    (X : Finset V) (c : Fin 4)
    (hX : ∀ x ∈ X, ∀ y ∈ X, x ≠ y → G.col x y ≠ c) (h14 : X.card = 14)
    (hZ : (armFar G X c).card = 5) :
    ∀ z ∈ armFar G X c,
      ((((armFar G X c).erase z).filter (fun y => G.col z y ≠ c))).card = 2 := by
  intro z hz
  have hA := armFar_five_zero_degree G h X c hX h14 hZ z hz
  have hsplit := Finset.card_filter_add_card_filter_not
    (s := (armFar G X c).erase z) (p := fun y => G.col z y = c)
  have hcardErase : ((armFar G X c).erase z).card = 4 := by
    rw [Finset.card_erase_of_mem hz, hZ]
  rw [hcardErase, hA] at hsplit
  have : (((armFar G X c).erase z).filter (fun y => ¬ (G.col z y = c))).card = 2 := by
    omega
  simpa only [ne_eq] using this

end K58

#print axioms K58.armFar_five_zero_degree
#print axioms K58.armFar_five_nonzero_degree
