/-
# The root degree lemma of the singleton-perfect-balance line

Formalises the one structural lemma of the `results/pb-codegree-2026-11-24`
line (ledger entry `#33`).  `V = Fin 58`, a symmetric 4-colouring of the edges
of the complete graph, no monochromatic triangle.  If `u v` is blue (colour 0)
with exactly 14 common red (colour 3) neighbours, every red degree is at most
16, every other colour degree at most 14, and `v` has at least 15 red
neighbours, then `v` has exactly 13 blue neighbours and `u` exactly 16 red ones.

The content is one inequality.  Inside the blue neighbourhood of `v`, the
vertices other than `u` split by their colour to `u`; the ones red to `u` avoid
the 14 common red neighbours, and each of the other two classes is a
two-coloured set with no monochromatic triangle, hence has at most five
elements (`pb_two_colour_card_le_five`, which is `R(3,3) <= 6`).

Names carry the prefix `pb_` so that nothing here can collide with the
campaign's own `K58` development.
-/
import Mathlib
import K58.Basic

open Finset

namespace K58

lemma pb_fin2_cases (a : Fin 2) : a = 0 ∨ a = 1 := by revert a; decide

lemma pb_fin4_cases (a : Fin 4) : a = 0 ∨ a = 1 ∨ a = 2 ∨ a = 3 := by revert a; decide

lemma pb_fin2_eq_one_of_ne_zero {a : Fin 2} (h : a ≠ 0) : a = 1 := by
  rcases pb_fin2_cases a with h0 | h1
  · exact absurd h0 h
  · exact h1

/-- **R(3,3) ≤ 6** in the form used below: a nonempty set carrying a
triangle-free 2-colouring has at most five elements. -/
theorem pb_two_colour_card_le_five {α : Type*} [Fintype α] [DecidableEq α]
    (c : α → α → Fin 2) (_hsym : ∀ a b, c a b = c b a)
    (htri : ∀ a b d, a ≠ b → b ≠ d → a ≠ d →
      ¬ (c a b = c a d ∧ c a d = c b d))
    (hne : Nonempty α) : Fintype.card α ≤ 5 := by
  classical
  obtain ⟨x⟩ := hne
  set P : Finset α := univ.filter (fun y => y ≠ x ∧ c x y = 0) with hPdef
  set Q : Finset α := univ.filter (fun y => y ≠ x ∧ c x y = 1) with hQdef
  have hsplit : (univ.filter (fun y : α => y ≠ x)).card = P.card + Q.card := by
    have hunion : univ.filter (fun y : α => y ≠ x) = P ∪ Q := by
      ext y
      simp only [mem_filter, mem_union, mem_univ, true_and, hPdef, hQdef]
      constructor
      · intro hne
        rcases pb_fin2_cases (c x y) with h | h
        · exact Or.inl ⟨hne, h⟩
        · exact Or.inr ⟨hne, h⟩
      · rintro (⟨hne, -⟩ | ⟨hne, -⟩) <;> exact hne
    have hdisj : Disjoint P Q := by
      rw [Finset.disjoint_left]
      intro y hyP hyQ
      simp only [hPdef, hQdef, mem_filter] at hyP hyQ
      rw [hyP.2.2] at hyQ
      exact absurd hyQ.2.2 (by decide)
    rw [hunion, Finset.card_union_of_disjoint hdisj]
  have hcard : (univ.filter (fun y : α => y ≠ x)).card = Fintype.card α - 1 := by
    rw [Finset.filter_ne', Finset.card_erase_of_mem (mem_univ x), Finset.card_univ]
  -- in a triangle-free 2-colouring, two vertices of one colour at `x` are joined
  -- in the other colour
  have key : ∀ y z : α, y ≠ x → z ≠ x → c x y = 0 → c x z = 0 → y ≠ z → c y z = 1 := by
    intro y z hy hz hy0 hz0 hyz
    have hne0 : c y z ≠ 0 := by
      intro h0
      exact htri x y z (Ne.symm hy) hyz (Ne.symm hz)
        ⟨by rw [hy0, hz0], by rw [hz0, h0]⟩
    exact pb_fin2_eq_one_of_ne_zero hne0
  have key1 : ∀ y z : α, y ≠ x → z ≠ x → c x y = 1 → c x z = 1 → y ≠ z → c y z = 0 := by
    intro y z hy hz hy1 hz1 hyz
    have hne1 : c y z ≠ 1 := by
      intro h1
      exact htri x y z (Ne.symm hy) hyz (Ne.symm hz)
        ⟨by rw [hy1, hz1], by rw [hz1, h1]⟩
    rcases pb_fin2_cases (c y z) with h | h
    · exact h
    · exact absurd h hne1
  have hP2 : P.card ≤ 2 := by
    by_contra hcon
    rw [not_le] at hcon
    obtain ⟨a, ha, b, hb, d, hd, hab, had, hbd⟩ := Finset.two_lt_card.mp (by omega : 2 < P.card)
    simp only [hPdef, mem_filter] at ha hb hd
    have hab1 : c a b = 1 := key a b ha.2.1 hb.2.1 ha.2.2 hb.2.2 (by omega)
    have had1 : c a d = 1 := key a d ha.2.1 hd.2.1 ha.2.2 hd.2.2 (by omega)
    have hbd1 : c b d = 1 := key b d hb.2.1 hd.2.1 hb.2.2 hd.2.2 (by omega)
    exact htri a b d hab hbd had ⟨by rw [hab1, had1], by rw [had1, hbd1]⟩
  have hQ2 : Q.card ≤ 2 := by
    by_contra hcon
    rw [not_le] at hcon
    obtain ⟨a, ha, b, hb, d, hd, hab, had, hbd⟩ := Finset.two_lt_card.mp (by omega : 2 < Q.card)
    simp only [hQdef, mem_filter] at ha hb hd
    have hab0 : c a b = 0 := key1 a b ha.2.1 hb.2.1 ha.2.2 hb.2.2 (by omega)
    have had0 : c a d = 0 := key1 a d ha.2.1 hd.2.1 ha.2.2 hd.2.2 (by omega)
    have hbd0 : c b d = 0 := key1 b d hb.2.1 hd.2.1 hb.2.2 hd.2.2 (by omega)
    exact htri a b d hab hbd had ⟨by rw [hab0, had0], by rw [had0, hbd0]⟩
  omega

/-- A set whose internal edges avoid two of the four colours is two-coloured,
so if it has no monochromatic triangle it has at most five vertices. -/
theorem pb_card_le_five_of_avoids {α : Type*} [Fintype α] [DecidableEq α]
    (S : Finset α) (c : α → α → Fin 4) (hsym : ∀ a b, c a b = c b a)
    (p q : Fin 4) (hpq : p ≠ q)
    (havoid : ∀ a ∈ S, ∀ b ∈ S, a ≠ b → c a b = p ∨ c a b = q)
    (hno : ∀ a ∈ S, ∀ b ∈ S, ∀ d ∈ S, a ≠ b → b ≠ d → a ≠ d →
      ¬ (c a b = c a d ∧ c a d = c b d)) :
    S.card ≤ 5 := by
  classical
  rcases Finset.eq_empty_or_nonempty S with rfl | hne
  · simp
  -- transport to the subtype and use the 2-colour lemma
  set f : S → S → Fin 2 := fun a b => if c (a : α) (b : α) = p then 0 else 1 with hf
  have hsym' : ∀ a b : S, f a b = f b a := by
    intro a b; simp only [hf]; rw [hsym]
  have key2 : ∀ a b : S, (f a b = 0 ↔ c (a : α) (b : α) = p) := by
    intro a b; simp only [hf]; split_ifs with h
    · simp [h]
    · simp [h]
  have key3 : ∀ a b : S, (a : α) ≠ (b : α) → (c (a : α) (b : α) = q → f a b = 1) := by
    intro a b hab h
    simp only [hf]
    rw [if_neg (by rw [h]; exact Ne.symm hpq)]
  have htri' : ∀ a b d : S, a ≠ b → b ≠ d → a ≠ d →
      ¬ (f a b = f a d ∧ f a d = f b d) := by
    intro a b d hab hbd had hconj
    have hab' : ((a : α)) ≠ (b : α) := fun h => hab (Subtype.ext h)
    have hbd' : ((b : α)) ≠ (d : α) := fun h => hbd (Subtype.ext h)
    have had' : ((a : α)) ≠ (d : α) := fun h => had (Subtype.ext h)
    -- `f = 1` means the colour is `q`, by `havoid`
    have hq : ∀ x y : S, (x : α) ≠ (y : α) → f x y = 1 → c (x : α) (y : α) = q := by
      intro x y hxy hf1
      rcases havoid _ x.2 _ y.2 hxy with h | h
      · exfalso
        have h0 : f x y = 0 := (key2 x y).mpr h
        rw [hf1] at h0
        exact absurd h0 (by decide)
      · exact h
    have e1 : c (a : α) (b : α) = c (a : α) (d : α) := by
      rcases pb_fin2_cases (f a b) with h | h
      · rw [(key2 a b).mp h, (key2 a d).mp (by rw [← hconj.1]; exact h)]
      · rw [hq a b hab' h, hq a d had' (by rw [← hconj.1]; exact h)]
    have e2 : c (a : α) (d : α) = c (b : α) (d : α) := by
      rcases pb_fin2_cases (f a d) with h | h
      · rw [(key2 a d).mp h, (key2 b d).mp (by rw [← hconj.2]; exact h)]
      · rw [hq a d had' h, hq b d hbd' (by rw [← hconj.2]; exact h)]
    exact hno _ a.2 _ b.2 _ d.2 hab' hbd' had' ⟨e1, by rw [e2]⟩
  have hne' : Nonempty ↥S := by obtain ⟨a, ha⟩ := hne; exact ⟨⟨a, ha⟩⟩
  have hres := pb_two_colour_card_le_five f hsym' htri' hne'
  rwa [Fintype.card_coe] at hres

/-- **The root degree lemma.** -/
theorem pb_root_blue_degree (G : EdgeCol (Fin 58) 4) (htri : TriangleFree G)
    {u v : Fin 58} (huv : u ≠ v) (hblue : G.col u v = 0)
    (hcodeg : (univ.filter (fun x : Fin 58 =>
      x ≠ u ∧ x ≠ v ∧ G.col u x = 3 ∧ G.col v x = 3)).card = 14)
    (hred : ∀ x, deg G x 3 ≤ 16)
    (hord : ∀ x c, c ≠ 3 → deg G x c ≤ 14)
    (hrv : 15 ≤ deg G v 3) :
    deg G v 0 = 13 ∧ deg G u 3 = 16 := by
  classical
  -- the degree sum at `v`
  have hdegsum : deg G v 0 + deg G v 1 + deg G v 2 + deg G v 3 = 57 := by
    have hfib := Finset.card_eq_sum_card_fiberwise (s := univ.erase v) (t := (univ : Finset (Fin 4)))
      (f := fun y : Fin 58 => G.col v y) (fun x _ => mem_univ _)
    have hcard : (univ.erase v).card = 57 := by
      rw [Finset.card_erase_of_mem (mem_univ v), Finset.card_univ]
      simp
    rw [hcard] at hfib
    have hterm : ∀ a : Fin 4, ((univ.erase v).filter (fun y : Fin 58 => G.col v y = a)).card = deg G v a := by
      intro a
      rw [deg, ← Finset.filter_filter]
      congr 1
      ext y
      simp only [mem_filter, mem_erase, mem_univ, true_and]
      tauto
    rw [Finset.sum_congr rfl (fun a _ => hterm a)] at hfib
    rw [hfib, Fin.sum_univ_four]
  set A : Finset (Fin 58) := univ.filter (fun y => y ≠ v ∧ G.col v y = 0) with hA
  have hdegv : deg G v 0 = A.card := rfl
  have huin : u ∈ A := by
    simp only [hA, mem_filter, mem_univ, true_and]
    exact ⟨huv, by rw [G.symm, hblue]⟩
  set A' : Finset (Fin 58) := A.erase u with hA'
  have hA'card : A'.card = A.card - 1 := by
    rw [hA', Finset.card_erase_of_mem huin]
  set S3 : Finset (Fin 58) := A'.filter (fun x => G.col u x = 3) with hS3
  set S1 : Finset (Fin 58) := A'.filter (fun x => G.col u x = 1) with hS1
  set S2 : Finset (Fin 58) := A'.filter (fun x => G.col u x = 2) with hS2
  have hA'mem : ∀ x ∈ A', x ≠ v ∧ G.col v x = 0 ∧ x ≠ u := by
    intro x hx
    rw [hA', mem_erase, hA, mem_filter] at hx
    exact ⟨hx.2.2.1, hx.2.2.2, hx.1⟩
  have hnot0 : ∀ x ∈ A', G.col u x ≠ 0 := by
    intro x hx h0
    obtain ⟨hxv, hx0, hxu⟩ := hA'mem x hx
    exact htri u v x huv hxv.symm hxu.symm
      ⟨by rw [hblue, h0], by rw [h0, hx0]⟩
  have hcover : A' = S3 ∪ S1 ∪ S2 := by
    ext x
    simp only [hS3, hS1, hS2, mem_filter, mem_union]
    constructor
    · intro hx
      have h0 := hnot0 x hx
      rcases pb_fin4_cases (G.col u x) with hc | hc | hc | hc
      · exact absurd hc h0
      · exact Or.inl (Or.inr ⟨hx, hc⟩)
      · exact Or.inr ⟨hx, hc⟩
      · exact Or.inl (Or.inl ⟨hx, hc⟩)
    · rintro ((⟨hx, -⟩ | ⟨hx, -⟩) | ⟨hx, -⟩) <;> assumption
  have hd31 : Disjoint S3 S1 := by
    rw [Finset.disjoint_left]; intro x hx hy
    simp only [hS3, hS1, mem_filter] at hx hy
    rw [hx.2] at hy; exact absurd hy.2 (by decide)
  have hd32 : Disjoint S3 S2 := by
    rw [Finset.disjoint_left]; intro x hx hy
    simp only [hS3, hS2, mem_filter] at hx hy
    rw [hx.2] at hy; exact absurd hy.2 (by decide)
  have hd12 : Disjoint S1 S2 := by
    rw [Finset.disjoint_left]; intro x hx hy
    simp only [hS1, hS2, mem_filter] at hx hy
    rw [hx.2] at hy; exact absurd hy.2 (by decide)
  have hunion : (S3 ∪ S1 ∪ S2).card = S3.card + S1.card + S2.card := by
    rw [Finset.card_union_of_disjoint (Finset.disjoint_union_left.mpr ⟨hd32, hd12⟩),
        Finset.card_union_of_disjoint hd31]
  have hA'eq : A'.card = S3.card + S1.card + S2.card := by rw [hcover, hunion]
  -- the red class sits inside the red neighbourhood of `u`, off the 14 common ones
  have hS3sub : S3 ⊆ univ.filter (fun y : Fin 58 => y ≠ u ∧ G.col u y = 3) := by
    intro x hx
    simp only [hS3, mem_filter] at hx
    exact mem_filter.mpr ⟨mem_univ x, (hA'mem x hx.1).2.2, hx.2⟩
  have hdisj : Disjoint S3 (univ.filter (fun x : Fin 58 =>
      x ≠ u ∧ x ≠ v ∧ G.col u x = 3 ∧ G.col v x = 3)) := by
    rw [Finset.disjoint_left]
    intro x hx hx2
    simp only [hS3, mem_filter] at hx
    simp only [mem_filter, mem_univ, true_and] at hx2
    obtain ⟨-, -, hcu, hcv⟩ := hx2
    have hx0 : G.col v x = 0 := (hA'mem x hx.1).2.1
    rw [hcv] at hx0
    exact absurd hx0 (by decide)
  have hS3le : S3.card ≤ deg G u 3 - 14 := by
    have h1 : S3.card + (univ.filter (fun x : Fin 58 =>
        x ≠ u ∧ x ≠ v ∧ G.col u x = 3 ∧ G.col v x = 3)).card ≤
        (univ.filter (fun y : Fin 58 => y ≠ u ∧ G.col u y = 3)).card := by
      have hd : Disjoint S3 (univ.filter (fun x : Fin 58 =>
          x ≠ u ∧ x ≠ v ∧ G.col u x = 3 ∧ G.col v x = 3)) := hdisj
      rw [← Finset.card_union_of_disjoint hd]
      apply Finset.card_le_card
      intro x hx
      rcases Finset.mem_union.mp hx with h | h
      · exact hS3sub h
      · simp only [mem_filter, mem_univ, true_and] at h ⊢
        exact ⟨h.1, h.2.2.1⟩
    rw [hcodeg] at h1
    simp only [deg]
    omega
  -- the two other classes are two-coloured, hence small
  have hS1le : S1.card ≤ 5 := by
    apply pb_card_le_five_of_avoids S1 G.col G.symm 2 3 (by decide)
    · intro a ha b hb hab
      simp only [hS1, mem_filter] at ha hb
      have ha' := hA'mem a ha.1
      have hb' := hA'mem b hb.1
      have hne1 : G.col a b ≠ 1 := by
        intro h1
        exact htri a u b ha'.2.2 hb'.2.2.symm hab
          ⟨by rw [(G.symm a u), ha.2, h1], by rw [h1, hb.2]⟩
      have hne0 : G.col a b ≠ 0 := by
        intro h0
        exact htri v a b ha'.1.symm hab hb'.1.symm
          ⟨by rw [ha'.2.1, hb'.2.1], by rw [hb'.2.1, h0]⟩
      rcases pb_fin4_cases (G.col a b) with h | h | h | h
      · exact absurd h hne0
      · exact absurd h hne1
      · exact Or.inl h
      · exact Or.inr h
    · intro a _ b _ d _ hab hbd had
      exact htri a b d hab hbd had
  have hS2le : S2.card ≤ 5 := by
    apply pb_card_le_five_of_avoids S2 G.col G.symm 1 3 (by decide)
    · intro a ha b hb hab
      simp only [hS2, mem_filter] at ha hb
      have ha' := hA'mem a ha.1
      have hb' := hA'mem b hb.1
      have hne2 : G.col a b ≠ 2 := by
        intro h2
        exact htri a u b ha'.2.2 hb'.2.2.symm hab
          ⟨by rw [(G.symm a u), ha.2, h2], by rw [h2, hb.2]⟩
      have hne0 : G.col a b ≠ 0 := by
        intro h0
        exact htri v a b ha'.1.symm hab hb'.1.symm
          ⟨by rw [ha'.2.1, hb'.2.1], by rw [hb'.2.1, h0]⟩
      rcases pb_fin4_cases (G.col a b) with h | h | h | h
      · exact absurd h hne0
      · exact Or.inl h
      · exact absurd h hne2
      · exact Or.inr h
    · intro a _ b _ d _ hab hbd had
      exact htri a b d hab hbd had
  have hAcard : A.card = A'.card + 1 := by
    have hpos : 0 < A.card := Finset.card_pos.mpr ⟨u, huin⟩
    omega
  have hb_ge : 13 ≤ deg G v 0 := by
    have h1 := hord v 1 (by decide)
    have h2 := hord v 2 (by decide)
    have h3 := hred v
    omega
  have hb_le : deg G v 0 ≤ 13 := by
    have h1 := hred u
    omega
  have hb13 : deg G v 0 = 13 := by omega
  -- tightness gives the red degree of `u`
  have hrueq : deg G u 3 = 16 := by
    have h1 := hred u
    omega
  exact ⟨hb13, hrueq⟩


end K58
