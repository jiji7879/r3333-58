/-
K54: the anchor-class capacity table `16, 5, 2, 1`.

The count decomposition for `R(3,3,3,3) ≤ 54` bounds, for every set of outsiders sharing
`m` distinct anchor spokes (colour `h i` at vertex `p i`), how many of them there can be:
at most `16, 5, 2, 1` for `m = 1, 2, 3, 4`.  The archived justification is three separate
SAT runs (`R(3,3) ≤ 6`, `R(3,3,3) ≤ 17`, `R(3) = 3`) plus prose.  Here the table is a
consequence of the kernel-checked Ramsey bounds in `K58/TwoColour.lean` and
`K58/ThreeColour.lean`: a set whose pairwise edges avoid a fixed set `C` of `m` colours,
inside a triangle-free 4-colouring, is a triangle-free `(4 - m)`-colouring of a complete
graph on that set.  Board-independent: no board, rectangle or count variable appears.
-/
import K58.ThreeColour
import Mathlib.Tactic.IntervalCases

namespace K54Cap

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The capacity table: `m` forbidden colours leave `4 - m` colours for the mutual edges,
so the size of the set is at most `cap m` (for `m ≥ 1`). -/
def cap : ℕ → ℕ
  | 1 => 16
  | 2 => 5
  | 3 => 2
  | _ => 1

/-- Restrict a triangle-free 4-colouring to a subset `T ⊆ S`, renaming the colours that
are not forbidden by a bijection `e`. -/
theorem restrict (G : K58.EdgeCol V 4) (h : K58.TriangleFree G) (S : Finset V)
    (C : Finset (Fin 4)) (hS : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → G.col x y ∉ C)
    (m : ℕ) (hm : 0 < m) (e : {c : Fin 4 // c ∉ C} ≃ Fin m)
    (T : Finset V) (hTS : T ⊆ S) :
    ∃ G' : K58.EdgeCol {x // x ∈ T} m, K58.TriangleFree G' := by
  classical
  refine ⟨{ col := ?_, symm := ?_ }, ?_⟩
  · intro x y
    by_cases hxy : x = y
    · exact ⟨0, hm⟩
    · exact e ⟨G.col x.1 y.1, hS x.1 (hTS x.2) y.1 (hTS y.2) (fun h' => hxy (Subtype.ext h'))⟩
  · intro x y
    by_cases hxy : x = y
    · subst hxy; rfl
    · have hne : ¬ (y = x) := fun h' => hxy h'.symm
      simp only [dif_neg hxy, dif_neg hne, G.symm]
  · intro i j l hij hjl hil hmono
    have hv : ∀ a b : {x // x ∈ T}, a ≠ b →
        G.col a.1 b.1 ∉ C := fun a b hab =>
      hS a.1 (hTS a.2) b.1 (hTS b.2) (fun h' => hab (Subtype.ext h'))
    have key : ∀ a b : {x // x ∈ T}, (hab : a ≠ b) → ∀ c d : {x // x ∈ T}, (hcd : c ≠ d) →
        (if hab' : a = b then (⟨0, hm⟩ : Fin m) else e ⟨G.col a.1 b.1, hv a b hab'⟩) =
        (if hcd' : c = d then (⟨0, hm⟩ : Fin m) else e ⟨G.col c.1 d.1, hv c d hcd'⟩) →
        G.col a.1 b.1 = G.col c.1 d.1 := by
      intro a b hab c d hcd hEq
      rw [dif_neg hab, dif_neg hcd] at hEq
      exact congrArg Subtype.val (e.injective hEq)
    have h1 : G.col i.1 j.1 = G.col i.1 l.1 := key i j hij i l hil hmono.1
    have h2 : G.col i.1 l.1 = G.col j.1 l.1 := key i l hil j l hjl hmono.2
    exact h i.1 j.1 l.1 (fun h' => hij (Subtype.ext h')) (fun h' => hjl (Subtype.ext h'))
      (fun h' => hil (Subtype.ext h')) ⟨h1, h2⟩

/-- One forbidden colour leaves three, so `R(3,3,3) ≤ 17` gives `|S| ≤ 16`. -/
theorem card_le_sixteen (G : K58.EdgeCol V 4) (h : K58.TriangleFree G) (S : Finset V)
    (C : Finset (Fin 4)) (hC : C.card = 1)
    (hS : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → G.col x y ∉ C) : S.card ≤ 16 := by
  classical
  have hcompl : Fintype.card {c : Fin 4 // c ∉ C} = 3 := by
    rw [Fintype.card_subtype_compl, Fintype.card_coe, hC]
    norm_num
  have e : {c : Fin 4 // c ∉ C} ≃ Fin 3 :=
    (Fintype.equivFin {c : Fin 4 // c ∉ C}).trans (finCongr hcompl)
  by_contra hlt
  push_neg at hlt
  obtain ⟨T, hTS, hTc⟩ := Finset.exists_subset_card_eq (show 17 ≤ S.card by omega)
  obtain ⟨G', hG'⟩ := restrict G h S C hS 3 (by norm_num) e T hTS
  have hcard : Fintype.card {x // x ∈ T} = 17 := by rw [Fintype.card_coe, hTc]
  exact K58.three_colour_seventeen G' hcard hG'

/-- Two forbidden colours leave two, so `R(3,3) ≤ 6` gives `|S| ≤ 5`. -/
theorem card_le_five (G : K58.EdgeCol V 4) (h : K58.TriangleFree G) (S : Finset V)
    (C : Finset (Fin 4)) (hC : C.card = 2)
    (hS : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → G.col x y ∉ C) : S.card ≤ 5 := by
  classical
  have hcompl : Fintype.card {c : Fin 4 // c ∉ C} = 2 := by
    rw [Fintype.card_subtype_compl, Fintype.card_coe, hC]
    norm_num
  have e : {c : Fin 4 // c ∉ C} ≃ Fin 2 :=
    (Fintype.equivFin {c : Fin 4 // c ∉ C}).trans (finCongr hcompl)
  by_contra hlt
  push_neg at hlt
  obtain ⟨T, hTS, hTc⟩ := Finset.exists_subset_card_eq (show 6 ≤ S.card by omega)
  obtain ⟨G', hG'⟩ := restrict G h S C hS 2 (by norm_num) e T hTS
  have hcard : Fintype.card {x // x ∈ T} = 6 := by rw [Fintype.card_coe, hTc]
  exact K58.two_colour_six G' hcard hG'

/-- Three forbidden colours leave one, so `|S| ≤ 2`. -/
theorem card_le_two (G : K58.EdgeCol V 4) (h : K58.TriangleFree G) (S : Finset V)
    (C : Finset (Fin 4)) (hC : C.card = 3)
    (hS : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → G.col x y ∉ C) : S.card ≤ 2 := by
  classical
  have hcompl : Fintype.card {c : Fin 4 // c ∉ C} = 1 := by
    rw [Fintype.card_subtype_compl, Fintype.card_coe, hC]
    norm_num
  obtain ⟨c0, hc0⟩ := Fintype.card_eq_one_iff.mp hcompl
  have hall : ∀ d : Fin 4, d ∉ C → d = c0 := by
    intro d hd
    exact congrArg Subtype.val (hc0 ⟨d, hd⟩)
  by_contra hlt
  push_neg at hlt
  obtain ⟨x, hx, y, hy, z, hz, hxy, hxz, hyz⟩ :=
    Finset.two_lt_card.mp (show 2 < S.card by omega)
  have e1 : G.col x y = G.col x z := by
    rw [hall _ (hS x hx y hy hxy), hall _ (hS x hx z hz hxz)]
  have e2 : G.col x z = G.col y z := by
    rw [hall _ (hS x hx z hz hxz), hall _ (hS y hy z hz hyz)]
  exact h x y z hxy hyz hxz ⟨e1, e2⟩

/-- Four forbidden colours leave none, so `|S| ≤ 1`. -/
theorem card_le_one' (G : K58.EdgeCol V 4) (S : Finset V)
    (C : Finset (Fin 4)) (hC : C.card = 4)
    (hS : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → G.col x y ∉ C) : S.card ≤ 1 := by
  have hC' : C = Finset.univ := by
    apply Finset.eq_univ_of_card
    simpa using hC
  rw [Finset.card_le_one]
  intro x hx y hy
  by_contra hne
  exact absurd (hS x hx y hy hne) (by rw [hC']; simp)

/-- **The anchor-class capacity table.**  In a triangle-free 4-colouring, a set whose
pairwise edges avoid a fixed nonempty colour set `C` has at most `cap |C|` vertices. -/
theorem card_le_cap (G : K58.EdgeCol V 4) (h : K58.TriangleFree G) (S : Finset V)
    (C : Finset (Fin 4)) (hne : C.Nonempty)
    (hS : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → G.col x y ∉ C) :
    S.card ≤ cap C.card := by
  have hpos : 1 ≤ C.card := Finset.card_pos.mpr hne
  have hle : C.card ≤ 4 := by simpa using Finset.card_le_univ C
  interval_cases hc : C.card
  · exact card_le_sixteen G h S C hc hS
  · exact card_le_five G h S C hc hS
  · exact card_le_two G h S C hc hS
  · exact card_le_one' G S C hc hS

/-- **The count model's class capacity**, in the form the decomposition uses it.  If a set
`W` of outsiders shares `m ≥ 1` distinct anchor spokes, namely `G.col (p i) w = hs i` for
distinct vertices `p i` and distinct colours `hs i`, and no anchor is in `W`, then
`|W| ≤ cap m`.  The forbidden colour on a pair of outsiders is each anchor colour. -/
theorem anchor_capacity (G : K58.EdgeCol V 4) (h : K58.TriangleFree G) (m : ℕ) (hm : 1 ≤ m)
    (p : Fin m → V) (hp : Function.Injective p) (hs : Fin m → Fin 4)
    (hsi : Function.Injective hs) (W : Finset V) (hdisj : ∀ i, p i ∉ W)
    (hW : ∀ w ∈ W, ∀ i, G.col (p i) w = hs i) : W.card ≤ cap m := by
  classical
  have hC : (Finset.univ.image hs).card = m := by
    rw [Finset.card_image_of_injective _ hsi, Finset.card_univ, Fintype.card_fin]
  have hne : (Finset.univ.image hs).Nonempty := by
    refine ⟨hs ⟨0, by omega⟩, ?_⟩
    exact Finset.mem_image_of_mem _ (Finset.mem_univ _)
  have := card_le_cap G h W (Finset.univ.image hs) hne ?_
  · rwa [hC] at this
  · intro x hx y hy hxy hmem
    obtain ⟨i, -, hi⟩ := Finset.mem_image.mp hmem
    have hxi : G.col (p i) x = hs i := hW x hx i
    have hyi : G.col (p i) y = hs i := hW y hy i
    exact h (p i) x y (fun h' => hdisj i (h' ▸ hx)) hxy (fun h' => hdisj i (h' ▸ hy))
      ⟨by rw [hxi, hyi], by rw [hyi, ← hi]⟩

end K54Cap
