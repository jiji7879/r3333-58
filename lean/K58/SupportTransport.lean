/-
K58: physical-to-coded support transport for a guarded sender.

Hypotheses are the ones named in
`results/literature-next-2026-11-28/k60-source-audit.md` §4 (priority 1): a
triangle-free four-colouring, the sender `x` in the root's arm 1 with the root
edge in colour 1, the sender's arm pinned to a critical template of order 15 or
16, and the root's arm 0 pinned to the T16 template (`PinnedArm G r 0 16 true`)
whose coordinates are exactly the emitted coordinate order.  Nothing is invented:
every vertex used is a real neighbour of `x`, and the two `PinnedArm` structures
are hypotheses, not conclusions.

Conclusion: the emitted support mask of `x` over the 16 root coordinates,
namely `j ↦ (G.col x y_j = 1)`, is one of the 112 entries of the production list
`targetSupports` -- the exact `∃ i, ∀ j < 16, v (x j) = supportBit targetSupports i j`
shape that `K58.SemanticAssembly.emittedSupportStep.ready` asks for at
`sender = 18 .. 32` of the retained parent.

What this does NOT do (see NOTES.md): it does not prove that a coded guard
equals a physical `Sends` event, that the emitted atom order is the pinned
coordinate order, that vertex 17 plus the coded sets exhaust the senders, or
`ChainReady`.
-/
import K58.SupportCatalogue

set_option autoImplicit false
namespace K58.SupportTransport
open K58
open K58.SemanticAssembly
open K58.SupportCatalogue

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The local (template) palette of the sender's arm: physical colour 1 = local 0
(the marked colour), physical colour 2 = local 1 (the path colour),
physical colour 3 = local 2.  This is `Fin.succAbove 1` on `Fin 3 → Fin 4`. -/
theorem succAbove_one_zero : (1 : Fin 4).succAbove (0 : Fin 3) = 0 := by decide
theorem succAbove_one_one : (1 : Fin 4).succAbove (1 : Fin 3) = 2 := by decide
theorem succAbove_zero_two : (0 : Fin 4).succAbove (2 : Fin 3) = 3 := by decide

/-- Root-coordinate map from physical vertices in the root's arm 0. -/
noncomputable def rootCoord (G : EdgeCol V 4) (r : V) (er : ↥(arm G r 0) ≃ Fin 16)
    (v : V) : Fin 16 := if h : v ∈ arm G r 0 then er ⟨v, h⟩ else 0

theorem rootCoord_of_mem (G : EdgeCol V 4) (r : V) (er : ↥(arm G r 0) ≃ Fin 16)
    {v : V} (h : v ∈ arm G r 0) : rootCoord G r er v = er ⟨v, h⟩ := by
  simp [rootCoord, h]

/-- The mask set in root coordinates. -/
noncomputable def rootMask (G : EdgeCol V 4) (r : V) (er : ↥(arm G r 0) ≃ Fin 16)
    (S : Finset V) : Finset (Fin 16) := S.image (rootCoord G r er)

/-- Local colour transfer through the root pinning: physical colour
`0.succAbove d` is local colour `d`. -/
theorem local_colour (G : EdgeCol V 4) (r : V) (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val = (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    {x y : V} (hx : x ∈ arm G r 0) (hy : y ∈ arm G r 0) (hxy : x ≠ y) (d : Fin 3) :
    (G.col x y = (0 : Fin 4).succAbove d) ↔ (template 16 true).col (er ⟨x, hx⟩) (er ⟨y, hy⟩) = d := by
  have hne : (⟨x, hx⟩ : ↥(arm G r 0)) ≠ ⟨y, hy⟩ := fun h => hxy (congrArg Subtype.val h)
  rw [hroot ⟨x, hx⟩ ⟨y, hy⟩ hne]
  exact (Fin.succAbove_right_injective (p := (0 : Fin 4))).eq_iff

theorem decide_congr_iff {p q : Prop} [Decidable p] [Decidable q] (h : p ↔ q) :
    decide p = decide q := by
  by_cases hp : p
  · have hq : q := h.mp hp
    simp [hp, hq]
  · have hq : ¬ q := fun hq => hp (h.mpr hq)
    simp [hp, hq]

/-- The emitted ready proposition at `sender`-style coordinates: a mask that is
one catalogue entry makes `emittedSupportStep.ready` hold for a valuation that
agrees with the mask on the 16 atom variables. -/
theorem ready_of_mask {v : Valuation} {g : Nat} {x : Nat → Nat} {mask : Fin 16 → Bool}
    (hmask : ∃ i : Fin 112, ∀ j : Fin 16, mask j = supportBit targetSupports i j)
    (hv : ∀ j : Fin 16, v (x j) = mask j) :
    v g = true → ∃ i : Fin 112, ∀ j < 16, v (x j) = supportBit targetSupports i j := by
  intro _
  obtain ⟨i, hi⟩ := hmask
  exact ⟨i, fun j hj => by rw [hv ⟨j, hj⟩, hi ⟨j, hj⟩]⟩

/-- **The transport theorem.**  In a triangle-free four-colouring `G` with
`sender x = q` and `root r`, `G.col q r = 1`, the sender's colour-1 arm pinned to
a critical template (`PinnedArm G q 1 n t`, `n = 15 ∨ n = 16`) and the root's
arm 0 pinned to `T16` in the emitted coordinates `er`, the emitted support mask
is a catalogue entry. -/
theorem support_mask_mem (G : EdgeCol V 4) (hG : TriangleFree G) (q r : V)
    (hqr_ne : q ≠ r) (hqr : G.col q r = 1) {n : ℕ} {t : Bool} (hn : n = 15 ∨ n = 16)
    (hsender : PinnedArm G q 1 n t) (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val = (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y))) :
    ∃ i : Fin 112, ∀ j : Fin 16,
      (decide (G.col q (er.symm j).val = 1)) = supportBit targetSupports i j := by
  -- the root lies in the sender's arm 1
  have hr_mem : r ∈ arm G q 1 :=
    Finset.mem_filter.mpr ⟨Finset.mem_univ _, hqr_ne.symm, hqr⟩
  -- the physical support shape at the sender: a colour-2 P4 or C5
  have hshape : SupportShape G (fun x => x ∈ arm G q 1 ∩ arm G r 0) 2 := by
    have h := pinned_support_shape G q r 1 hn hsender hr_mem (0 : Fin 3) (1 : Fin 3)
      (by decide)
    simpa [Finset.mem_inter, succAbove_one_zero, succAbove_one_one] using h
  obtain ⟨m, hm, f, hf, hedge⟩ := hshape
  -- the support is exactly the range of `f`
  have hSord : arm G q 1 ∩ arm G r 0 = Finset.univ.image f := by
    ext x
    simp only [Finset.mem_inter, Finset.mem_image, Finset.mem_univ, true_and]
    exact (Finset.mem_inter).symm.trans (hf x)
  set S : Finset V := Finset.univ.image f with hSdef
  have hf_inj : Function.Injective f := f.injective
  have hS_iff : ∀ v : V, v ∈ S ↔ (v ∈ arm G q 1 ∧ v ∈ arm G r 0) := by
    intro v
    have h := congrArg (fun s : Finset V => v ∈ s) hSord
    exact Iff.trans (Iff.of_eq h.symm) Finset.mem_inter
  have hS_card : S.card = m := by
    rw [hSdef, Finset.card_image_of_injective _ hf_inj, Finset.card_univ,
      Fintype.card_fin]
  -- membership facts for the four/five template positions
  have hmemS : ∀ i : Fin m, f i ∈ S := fun i =>
    Finset.mem_image.mpr ⟨i, Finset.mem_univ _, rfl⟩
  have hmemArm : ∀ i : Fin m, f i ∈ arm G q 1 ∩ arm G r 0 := by
    intro i; rw [hSord]; exact hmemS i
  have hqcol : ∀ i : Fin m, G.col q (f i) = 1 := fun i =>
    (Finset.mem_filter.mp (Finset.mem_inter.mp (hmemArm i)).1).2.2
  have hqne : ∀ i : Fin m, q ≠ f i := fun i =>
    ((Finset.mem_filter.mp (Finset.mem_inter.mp (hmemArm i)).1).2.1).symm
  have hrcol : ∀ i : Fin m, G.col r (f i) = 0 := fun i =>
    ((Finset.mem_filter.mp (Finset.mem_inter.mp (hmemArm i)).2).2).2
  have hrne : ∀ i : Fin m, r ≠ f i := fun i =>
    ((Finset.mem_filter.mp (Finset.mem_inter.mp (hmemArm i)).2).2.1).symm
  have hfne : ∀ i j : Fin m, i ≠ j → f i ≠ f j := fun i j hij h => hij (hf_inj h)
  -- triangle-freeness: no colour-1 and no colour-0 pair inside the support
  have hne1 : ∀ i j : Fin m, i ≠ j → G.col (f i) (f j) ≠ 1 := by
    intro i j hij hc
    exact hG q (f i) (f j) (hqne i) (hfne i j hij) (hqne j)
      ⟨by rw [hqcol i, hqcol j], by rw [hqcol j, hc]⟩
  have hne0 : ∀ i j : Fin m, i ≠ j → G.col (f i) (f j) ≠ 0 := by
    intro i j hij hc
    exact hG r (f i) (f j) (hrne i) (hfne i j hij) (hrne j)
      ⟨by rw [hrcol i, hrcol j], by rw [hrcol j, hc]⟩
  have hne1' : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → G.col x y ≠ 1 := by
    intro x hx y hy hxy
    rw [hSdef] at hx hy
    obtain ⟨i, -, rfl⟩ := Finset.mem_image.mp hx
    obtain ⟨j, -, rfl⟩ := Finset.mem_image.mp hy
    exact hne1 i j (fun h => hxy (by rw [h]))
  have hne0' : ∀ x ∈ S, ∀ y ∈ S, x ≠ y → G.col x y ≠ 0 := by
    intro x hx y hy hxy
    rw [hSdef] at hx hy
    obtain ⟨i, -, rfl⟩ := Finset.mem_image.mp hx
    obtain ⟨j, -, rfl⟩ := Finset.mem_image.mp hy
    exact hne0 i j (fun h => hxy (by rw [h]))
  -- root coordinates: injective on the support, and local colours are the template's
  have hcoord_mem : ∀ v ∈ S, v ∈ arm G r 0 := fun v hv => by
    rw [← hSord] at hv
    exact (Finset.mem_inter.mp hv).2
  have hinjOn : ∀ x ∈ S, ∀ y ∈ S, rootCoord G r er x = rootCoord G r er y → x = y := by
    intro x hx y hy h
    rw [rootCoord_of_mem G r er (hcoord_mem x hx),
      rootCoord_of_mem G r er (hcoord_mem y hy)] at h
    exact congrArg Subtype.val (er.injective h)
  have hinner : ∀ x ∈ S, ∀ y ∈ S, x ≠ y →
      ((template 16 true).col (rootCoord G r er x) (rootCoord G r er y) = 0 ↔
        G.col x y = 1) := by
    intro x hx y hy hxy
    rw [rootCoord_of_mem G r er (hcoord_mem x hx),
      rootCoord_of_mem G r er (hcoord_mem y hy)]
    exact (local_colour G r er hroot (hcoord_mem x hx) (hcoord_mem y hy) hxy 0).symm
  have hshape_inner : ∀ x ∈ S, ∀ y ∈ S, x ≠ y →
      ((template 16 true).col (rootCoord G r er x) (rootCoord G r er y) = 1 ↔
        G.col x y = 2) := by
    intro x hx y hy hxy
    rw [rootCoord_of_mem G r er (hcoord_mem x hx),
      rootCoord_of_mem G r er (hcoord_mem y hy)]
    exact (local_colour G r er hroot (hcoord_mem x hx) (hcoord_mem y hy) hxy 1).symm
  have houter : ∀ x ∈ S, ∀ y ∈ S, x ≠ y →
      ((template 16 true).col (rootCoord G r er x) (rootCoord G r er y) = 2 ↔
        G.col x y = 3) := by
    intro x hx y hy hxy
    rw [rootCoord_of_mem G r er (hcoord_mem x hx),
      rootCoord_of_mem G r er (hcoord_mem y hy)]
    have := (local_colour G r er hroot (hcoord_mem x hx) (hcoord_mem y hy) hxy 2).symm
    simpa [succAbove_zero_two] using this
  -- the mask set
  set T : Finset (Fin 16) := rootMask G r er S with hT
  have hT_mem : ∀ j : Fin 16, j ∈ T ↔ (er.symm j).val ∈ S := by
    intro j
    rw [hT, rootMask, Finset.mem_image]
    constructor
    · rintro ⟨x, hx, hxj⟩
      rw [rootCoord_of_mem G r er (hcoord_mem x hx)] at hxj
      have hxs : x = (er.symm j).val := by
        have h1 : er ⟨x, hcoord_mem x hx⟩ = j := hxj
        rw [← h1]
        simp
      rw [← hxs]; exact hx
    · intro h
      refine ⟨(er.symm j).val, h, ?_⟩
      rw [rootCoord_of_mem G r er (hcoord_mem (er.symm j).val h)]
      exact (congrArg er (Subtype.ext rfl)).trans (er.apply_symm_apply j)
  have hT_card : T.card = m := by
    rw [hT, rootMask, Finset.card_image_of_injOn]
    · exact hS_card
    · intro x hx y hy h
      exact hinjOn x hx y hy h
  have hcoord_apply : ∀ j : Fin 16, rootCoord G r er (er.symm j).val = j := by
    intro j
    rw [rootCoord_of_mem G r er (er.symm j).property]
    exact (congrArg er (Subtype.ext rfl)).trans (er.apply_symm_apply j)
  -- the pointwise conclusion once `T` is a catalogue entry
  have concl : inCatalogue T = true → ∃ i : Fin 112, ∀ j : Fin 16,
      (decide (G.col q (er.symm j).val = 1)) = supportBit targetSupports i j := by
    intro hcat
    obtain ⟨i, -, hi⟩ := List.any_eq_true.mp hcat
    refine ⟨i, fun j => ?_⟩
    have hpat : patternNat i.val = T := of_decide_eq_true hi
    have hjT : (j ∈ T) ↔ (targetSupports.getD i.val []).contains j.val = true := by
      rw [← hpat]; simp [patternNat]
    have hqj : (er.symm j).val ∈ arm G q 1 ↔ G.col q (er.symm j).val = 1 := by
      constructor
      · intro h
        exact (Finset.mem_filter.mp h).2.2
      · intro h
        refine Finset.mem_filter.mpr ⟨Finset.mem_univ _, ?_, h⟩
        intro hq
        have hmem : (er.symm j).val ∈ arm G r 0 := (er.symm j).property
        rw [hq] at hmem
        have h0 : G.col r q = 0 := (Finset.mem_filter.mp hmem).2.2
        rw [← G.symm q r, hqr] at h0
        exact absurd h0 (by decide)
    have hiff : (G.col q (er.symm j).val = 1) ↔ (j ∈ T) := by
      have h1 : (G.col q (er.symm j).val = 1) ↔ (er.symm j).val ∈ arm G q 1 := hqj.symm
      have h2 : (er.symm j).val ∈ arm G q 1 ↔ (er.symm j).val ∈ S := by
        refine ⟨fun h => ?_, fun h => (hS_iff (er.symm j).val).mp h |>.1⟩
        exact (hS_iff (er.symm j).val).mpr ⟨h, (er.symm j).property⟩
      exact h1.trans (h2.trans (hT_mem j).symm)
    refine Bool.eq_iff_iff.mpr ?_
    rw [decide_eq_true_eq]
    exact hiff.trans hjT
  rcases hm with rfl | rfl
  · -- four-vertex support: an ordered colour-2 P4 with colour-3 diagonals
    have hback : ∀ k : Fin 4, (er.symm (rootCoord G r er (f k))).val ∈ S := by
      intro k
      rw [rootCoord_of_mem G r er (hcoord_mem (f k) (hmemS k))]
      simpa using hmemS k
    have hT4 : T = {rootCoord G r er (f ⟨0, by decide⟩), rootCoord G r er (f ⟨1, by decide⟩),
        rootCoord G r er (f ⟨2, by decide⟩), rootCoord G r er (f ⟨3, by decide⟩)} := by
      ext j
      rw [hT_mem j]
      simp only [Finset.mem_insert, Finset.mem_singleton]
      constructor
      · intro hj
        rw [hSdef] at hj
        obtain ⟨k, -, hk⟩ := Finset.mem_image.mp hj
        have hjk : j = rootCoord G r er (f k) := by
          rw [rootCoord_of_mem G r er (hcoord_mem (f k) (hmemS k)), ← er.apply_symm_apply j]
          exact congrArg er (Subtype.ext hk).symm
        subst hjk
        fin_cases k <;> simp
      · rintro (rfl | rfl | rfl | rfl)
        exacts [hback _, hback _, hback _, hback _]
    have e01 : G.col (f ⟨0, by decide⟩) (f ⟨1, by decide⟩) = 2 := by
      have h := hedge ⟨0, by decide⟩ ⟨1, by decide⟩ (by decide)
      simpa [supportEdge] using h
    have e12 : G.col (f ⟨1, by decide⟩) (f ⟨2, by decide⟩) = 2 := by
      have h := hedge ⟨1, by decide⟩ ⟨2, by decide⟩ (by decide)
      simpa [supportEdge] using h
    have e23 : G.col (f ⟨2, by decide⟩) (f ⟨3, by decide⟩) = 2 := by
      have h := hedge ⟨2, by decide⟩ ⟨3, by decide⟩ (by decide)
      simpa [supportEdge] using h
    have d02 : G.col (f ⟨0, by decide⟩) (f ⟨2, by decide⟩) ≠ 2 := by
      have h := hedge ⟨0, by decide⟩ ⟨2, by decide⟩ (by decide)
      simpa [supportEdge] using h
    have d03 : G.col (f ⟨0, by decide⟩) (f ⟨3, by decide⟩) ≠ 2 := by
      have h := hedge ⟨0, by decide⟩ ⟨3, by decide⟩ (by decide)
      simpa [supportEdge] using h
    have d13 : G.col (f ⟨1, by decide⟩) (f ⟨3, by decide⟩) ≠ 2 := by
      have h := hedge ⟨1, by decide⟩ ⟨3, by decide⟩ (by decide)
      simpa [supportEdge] using h
    have hthree : ∀ i j : Fin 4, i ≠ j → G.col (f i) (f j) ≠ 2 → G.col (f i) (f j) = 3 := by
      intro i j hij h2
      have h0 := hne0 i j hij
      have h1 := hne1 i j hij
      have hv := (G.col (f i) (f j)).isLt
      refine Fin.ext (by
        have hz : (G.col (f i) (f j)).val ≠ 0 := fun h => h0 (Fin.ext h)
        have ho : (G.col (f i) (f j)).val ≠ 1 := fun h => h1 (Fin.ext h)
        have ht : (G.col (f i) (f j)).val ≠ 2 := fun h => h2 (Fin.ext h)
        omega)
    have eq1 : (template 16 true).col (rootCoord G r er (f ⟨0, by decide⟩))
        (rootCoord G r er (f ⟨1, by decide⟩)) = 1 :=
      (hshape_inner (f ⟨0, by decide⟩) (hmemS _) (f ⟨1, by decide⟩) (hmemS _)
        (hfne _ _ (by decide))).mpr e01
    have eq2 : (template 16 true).col (rootCoord G r er (f ⟨1, by decide⟩))
        (rootCoord G r er (f ⟨2, by decide⟩)) = 1 :=
      (hshape_inner (f ⟨1, by decide⟩) (hmemS _) (f ⟨2, by decide⟩) (hmemS _)
        (hfne _ _ (by decide))).mpr e12
    have eq3 : (template 16 true).col (rootCoord G r er (f ⟨2, by decide⟩))
        (rootCoord G r er (f ⟨3, by decide⟩)) = 1 :=
      (hshape_inner (f ⟨2, by decide⟩) (hmemS _) (f ⟨3, by decide⟩) (hmemS _)
        (hfne _ _ (by decide))).mpr e23
    have eq4 : (template 16 true).col (rootCoord G r er (f ⟨0, by decide⟩))
        (rootCoord G r er (f ⟨2, by decide⟩)) = 2 :=
      (houter (f ⟨0, by decide⟩) (hmemS _) (f ⟨2, by decide⟩) (hmemS _)
        (hfne _ _ (by decide))).mpr (hthree _ _ (by decide) d02)
    have eq5 : (template 16 true).col (rootCoord G r er (f ⟨0, by decide⟩))
        (rootCoord G r er (f ⟨3, by decide⟩)) = 2 :=
      (houter (f ⟨0, by decide⟩) (hmemS _) (f ⟨3, by decide⟩) (hmemS _)
        (hfne _ _ (by decide))).mpr (hthree _ _ (by decide) d03)
    have eq6 : (template 16 true).col (rootCoord G r er (f ⟨1, by decide⟩))
        (rootCoord G r er (f ⟨3, by decide⟩)) = 2 :=
      (houter (f ⟨1, by decide⟩) (hmemS _) (f ⟨3, by decide⟩) (hmemS _)
        (hfne _ _ (by decide))).mpr (hthree _ _ (by decide) d13)
    exact concl (by rw [hT4]; exact p4_complete _ _ _ _ eq1 eq2 eq3 eq4 eq5 eq6)
  · -- five-vertex support: the emitted five-set check needs only marked independence
    have hcard5 : T.card = 5 := by rw [hT_card]
    have hind5 : indep0 T := by
      intro a ha b hb hab hcol
      have ha' : (er.symm a).val ∈ S := (hT_mem a).mp ha
      have hb' : (er.symm b).val ∈ S := (hT_mem b).mp hb
      have hne : (er.symm a).val ≠ (er.symm b).val :=
        fun h => hab (er.symm.injective (Subtype.ext h))
      have key := hinner (er.symm a).val ha' (er.symm b).val hb' hne
      rw [hcoord_apply a, hcoord_apply b] at key
      exact hne1' _ ha' _ hb' hne (key.mp hcol)
    exact concl (c5_complete T hcard5 hind5)

/-- The same statement with `PinnedArm` as the root hypothesis (the form the
physical memo states): root arm 0 pinned to `T16` at the emitted coordinates. -/
theorem support_mask_mem_of_pinned (G : EdgeCol V 4) (hG : TriangleFree G) (q r : V)
    (hqr_ne : q ≠ r) (hqr : G.col q r = 1) {n : ℕ} {t : Bool} (hn : n = 15 ∨ n = 16)
    (hsender : PinnedArm G q 1 n t) (hroot : PinnedArm G r 0 16 true) :
    ∃ (er : ↥(arm G r 0) ≃ Fin 16), ∃ i : Fin 112, ∀ j : Fin 16,
      (decide (G.col q (er.symm j).val = 1)) = supportBit targetSupports i j := by
  obtain ⟨er, her⟩ := hroot
  exact ⟨er, support_mask_mem G hG q r hqr_ne hqr hn hsender er her⟩


/-- The emitted `ready` field of `K58.SemanticAssembly.emittedSupportStep` is
*definitionally* the proposition this port discharges: no new semantic
predicate is introduced. -/
theorem emittedSupportStep_ready_shape (oldTop g n k newTop : Nat) (x : Nat → Nat)
    (sel : Fin k → Nat) (allowed : Fin k → Nat → Bool) (active : Nat → Bool)
    (hg : g ≤ oldTop) (hnew : oldTop ≤ newTop) (inputs_below : ∀ j < n, x j ≤ oldTop)
    (fresh : ∀ i, oldTop < sel i) (hinj : Function.Injective sel)
    (hb : VarsBelow (emittedSupportFamilyCNF g n k x sel allowed active) newTop)
    (v : Valuation) :
    (emittedSupportStep oldTop g n k newTop x sel allowed active hg hnew inputs_below
      fresh hinj hb).ready v
      = (v g = true → ∃ i, ∀ j < n, v (x j) = allowed i j) := rfl


/-- **The emitted readiness obligation at an arbitrary guard.**  Same hypotheses
as `support_mask_mem`, no restriction on the guard number or on the atom list:
any valuation that agrees with the physical mask on 16 atoms satisfies the
emitted `ready` proposition at that guard.  All 15 arm-1 support events of the
retained parent (guards `11965, 12456, 12947, 13438, 13929, 14420, 14911,
15402, 15893, 16384, 16875, 17366, 17857, 18348, 18839`) are instances with
their own atom lists. -/
theorem ready_at_guard (G : EdgeCol V 4) (hG : TriangleFree G) (q r : V)
    (hqr_ne : q ≠ r) (hqr : G.col q r = 1) {n : ℕ} {t : Bool} (hn : n = 15 ∨ n = 16)
    (hsender : PinnedArm G q 1 n t) (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val = (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (g : Nat) (atoms : Nat → Nat) {v : Valuation}
    (hv : ∀ j : Fin 16, v (atoms j) = decide (G.col q (er.symm j).val = 1)) :
    v g = true → ∃ i : Fin 112, ∀ j < 16, v (atoms j) = supportBit targetSupports i j :=
  ready_of_mask (support_mask_mem G hG q r hqr_ne hqr hn hsender er hroot) hv

/-- The 16 emitted atoms of the arm-1 support event at guard `11965`
(sender vertex 18) in `lean/K58/TargetSuffix.lean`. -/
def sender18Atoms : Nat → Nat :=
  listAtoms [294, 514, 730, 942, 1150, 1354, 1554, 1750, 1942, 2130, 2314, 2494,
    2670, 2842, 3010, 3174]

theorem sender18Atoms_eq_listAtoms :
    sender18Atoms = listAtoms [294, 514, 730, 942, 1150, 1354, 1554, 1750, 1942,
      2130, 2314, 2494, 2670, 2842, 3010, 3174] := rfl

/-- **The emitted readiness obligation of guard `11965`, discharged from the
physical colouring.**  If `v` agrees with the physical mask of the sender on the
16 emitted atoms, then the emitted `ready` proposition holds at `g = 11965`,
`n = 16`, `k = 112`, `allowed = supportBit targetSupports`. -/
theorem sender18_ready (G : EdgeCol V 4) (hG : TriangleFree G) (q r : V)
    (hqr_ne : q ≠ r) (hqr : G.col q r = 1) {n : ℕ} {t : Bool} (hn : n = 15 ∨ n = 16)
    (hsender : PinnedArm G q 1 n t) (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val = (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    {v : Valuation} (hv : ∀ j : Fin 16, v (sender18Atoms j) = decide (G.col q (er.symm j).val = 1)) :
    v 11965 = true → ∃ i : Fin 112, ∀ j < 16, v (sender18Atoms j) = supportBit targetSupports i j :=
  ready_of_mask (support_mask_mem G hG q r hqr_ne hqr hn hsender er hroot) hv


/-- **Degree form.**  When the sender's colour-1 degree is exactly `n ∈ {15,16}`
and the order-`n` critical-template classification is available, `PinnedArm`
follows (`K58.pin_of_named_classification`), so the only remaining physical
premise of `support_mask_mem` is the root pinning.  The classification itself is
the Kalbfleisch–Stanton / Heinrich statement recorded as `K58.Classified`; it is
a hypothesis here, exactly as in `lean/K58/ArmPinned.lean`. -/
theorem support_mask_mem_of_deg (G : EdgeCol V 4) (hG : TriangleFree G) (q r : V)
    (hqr_ne : q ≠ r) (hqr : G.col q r = 1) {n : ℕ} (hn : n = 15 ∨ n = 16)
    (hclass : ∀ C : EdgeCol (Fin n) 3, TriangleFree C →
      ∃ t : Bool, ∃ e : Equiv.Perm (Fin n), ∀ i j, i ≠ j →
        C.col i j = (template n t).col (e i) (e j))
    (hdeg : deg G q 1 = n) (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val = (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y))) :
    ∃ i : Fin 112, ∀ j : Fin 16,
      (decide (G.col q (er.symm j).val = 1)) = supportBit targetSupports i j := by
  obtain ⟨t, ht⟩ := pin_of_named_classification hclass G hG q 1 hdeg
  exact support_mask_mem G hG q r hqr_ne hqr hn ht er hroot

end K58.SupportTransport
