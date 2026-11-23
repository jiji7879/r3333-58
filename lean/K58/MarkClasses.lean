import K58.NamedAutomorphisms
import K58.Palette
import K58.Plans

namespace K58

/-- Allowed relabellings preserve the size and kind of each other arm.
Elements of Fin 3 name the three remaining host colours in increasing order. -/
def PositionOrbit {n : ℕ} {α : Type*} (tag : Fin 3 → α) (t : Bool) (x y : Fin n) : Prop :=
  ∃ p : Equiv.Perm (Fin 3), (∀ c, tag (p c) = tag c) ∧ ∃ e : Equiv.Perm (Fin n),
    e x = y ∧ ∀ i j, i ≠ j → (template n t).col (e i) (e j) = p ((template n t).col i j)

def positionOrbit15 {α : Type*} [DecidableEq α] (tag : Fin 3 → α) (t : Bool) (x : Fin 15) :
    Finset (Fin 15) :=
  ((List.finRange 6).flatMap fun code =>
    if ∀ c, tag (R4333.criticalPaletteColorMap code c) = tag c then
      (named15 t).map fun f => f (R4333.k15PaletteVertexMap t code x)
    else []).toFinset

theorem mem_positionOrbit15 {α : Type*} [DecidableEq α] (tag : Fin 3 → α)
    (t : Bool) (x y : Fin 15) : y ∈ positionOrbit15 tag t x ↔ PositionOrbit tag t x y := by
  have realized (code : Fin 6) (i j : Fin 15) (h : i ≠ j) :
      (template 15 t).col (R4333.k15PaletteVertexEquiv t code i) (R4333.k15PaletteVertexEquiv t code j) =
        R4333.criticalPaletteColorEquiv code ((template 15 t).col i j) := by
    simpa only [R4333.k15PaletteVertexEquiv_apply, R4333.criticalPaletteColorEquiv_apply,
      catalogue_col_15] using R4333.k15PaletteVertexMap_preserves t code i j h
  simp only [positionOrbit15, List.mem_toFinset, List.mem_flatMap]
  constructor
  · rintro ⟨code, _, hy⟩
    split at hy
    next htag =>
      obtain ⟨f, hf, rfl⟩ := List.mem_map.mp hy
      rw [named15_exact, PositionSearch.mem_automorphisms_iff] at hf
      let g := R4333.k15PaletteVertexEquiv t code
      refine ⟨R4333.criticalPaletteColorEquiv code, htag, g.trans (Equiv.ofBijective f hf.1), rfl, ?_⟩
      intro i j hij
      exact (hf.2 _ _ (g.injective.ne hij)).trans (realized code i j hij)
    next h => simp at hy
  · rintro ⟨p, htag, e, hxy, he⟩
    let code := R4333.criticalPaletteCode p
    let g := R4333.k15PaletteVertexEquiv t code
    let f := g.symm.trans e
    have hp : R4333.criticalPaletteColorEquiv code = p := R4333.criticalPaletteColorEquiv_code p
    have htag' : ∀ c, tag (R4333.criticalPaletteColorMap code c) = tag c := by
      simpa only [← R4333.criticalPaletteColorEquiv_apply, hp] using htag
    refine ⟨code, List.mem_finRange _, ?_⟩
    rw [if_pos htag']
    refine List.mem_map.mpr ⟨f, ?_, ?_⟩
    · rw [named15_exact, PositionSearch.mem_automorphisms_iff]
      refine ⟨f.bijective, ?_⟩
      intro i j hij
      have h := realized code (g.symm i) (g.symm j) (g.symm.injective.ne hij)
      change (template 15 t).col (g (g.symm i)) (g (g.symm j)) = _ at h
      rw [g.apply_symm_apply, g.apply_symm_apply, hp] at h
      exact (he _ _ (g.symm.injective.ne hij)).trans h.symm
    · change e (g.symm (g x)) = y
      simpa only [g.symm_apply_apply] using hxy

/-- The minimal position and weight of every palette-augmented class. -/
def markClasses15 {α : Type*} [DecidableEq α] (tag : Fin 3 → α) (t : Bool) :
    List (Fin 15 × ℕ) :=
  (List.finRange 15).filterMap fun x =>
    let orbit := positionOrbit15 tag t x
    if ∀ y ∈ orbit, x ≤ y then some (x, orbit.card) else none

/-- Distinct tags freeze all three colour names, recovering the named vertex orbits. -/
theorem named_position_counts15 :
    (markClasses15 (id : Fin 3 → Fin 3) false).length = 3 ∧
    (markClasses15 (id : Fin 3 → Fin 3) true).length = 9 := by decide

/-- Plans name host colours 0 through 3. Equal tags can be interchanged. -/
def planTag (P : Plan) (a : Fin 4) (i : Fin 3) : Option ℕ × Option Char :=
  let j := (a.succAbove i).val
  (P.prof[j]?, P.kinds.toList[j]?)

theorem markClasses15_TTT : markClasses15 (planTag ⟨[15,15,15,12], "TTT-", [11,11,11,13]⟩ 0) true =
    [(0,4), (2,4), (4,4), (5,2), (6,1)] := by decide

theorem markClasses15_UUU : markClasses15 (planTag ⟨[15,15,15,12], "UUU-", [11,11,11,13]⟩ 0) false =
    [(0,10), (1,5)] := by decide

/-- All sixteen marked positions form one class, even with the palette fixed. -/
theorem positionOrbit16_all {α : Type*} (tag : Fin 3 → α) (t : Bool) (x y : Fin 16) :
    PositionOrbit tag t x y := by
  let A := R4333.k16TemplateToLastEquiv t
  let e := (A x).trans (A y).symm
  have last (i : Fin 16) : A i i = Fin.last 15 := R4333.k16TemplateToLastMap_deleted t i
  have hA (v i j : Fin 16) (h : i ≠ j) :
      (template 16 t).col i j = (template 16 t).col (A v i) (A v j) := by
    simpa only [A, R4333.k16TemplateToLastEquiv_apply, catalogue_col_16] using R4333.k16TemplateToLastMap_preserves t v i j h
  refine ⟨Equiv.refl _, fun _ => rfl, e, (A y).symm_apply_eq.mpr ((last x).trans (last y).symm), ?_⟩
  intro i j hij
  have h := hA y (e i) (e j) (e.injective.ne hij)
  simp only [e, Equiv.trans_apply, Equiv.apply_symm_apply] at h
  exact h.trans (hA x i j hij).symm

/-- The four branches used by the generator: U15, T15, one transitive K16
class or an untemplated arm with free vertex labels. -/
def markClasses (P : Plan) (a : Fin 4) : List (ℕ × ℕ) :=
  let n := P.prof[a.val]?.getD 0
  if n = 15 then
    (markClasses15 (planTag P a) (P.kinds.toList[a.val]? == some 'T')).map
      (fun r => (r.1.val, r.2))
  else [(0, n)]

end K58
