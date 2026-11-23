import K58.ArmPinned

namespace K58

/-- In increasing order around a path or cycle, the consecutive pairs are
edges, with an additional closing edge exactly at order five. -/
def supportEdge (m i j : ℕ) : Prop :=
  j = i + 1 ∨ (m = 5 ∧ i = 0 ∧ j = 4)

instance (m i j : ℕ) : Decidable (supportEdge m i j) := by
  unfold supportEdge; infer_instance

/-- A path on four or a cycle on five, in colour c on exactly the indicated vertices. -/
def SupportShape {V : Type*} {k : ℕ} (G : EdgeCol V k) (S : V → Prop) (c : Fin k) : Prop :=
  ∃ m, (m = 4 ∨ m = 5) ∧ ∃ f : Fin m ↪ V,
    (∀ x, S x ↔ ∃ i, f i = x) ∧ ∀ i j, i < j →
      (G.col (f i) (f j) = c ↔ supportEdge m i.val j.val)

private def walk {V : Type} [DecidableEq V] (edge : V → V → Bool) :
    ℕ → V → List V → List V
  | 0, _, _ => []
  | k+1, x, remaining => match remaining.find? (edge x) with
    | none => []
    | some y => y :: walk edge k y (remaining.erase y)

private def supportOrder {n : ℕ} (t : Bool) (r : Fin n) (b c : Fin 3) : List (Fin n) :=
  let G := template n t
  let vertices := (List.finRange n).filter fun x => decide (x ≠ r ∧ G.col r x = b)
  let edge := fun x y => decide (x ≠ y ∧ G.col x y = c)
  let start := (vertices.find? fun x => (vertices.filter (edge x)).length == 1).or vertices.head?
  match start with
  | none => []
  | some x => x :: walk edge 4 x (vertices.erase x)

private def ValidOrder {n : ℕ} (t : Bool) (r : Fin n) (b c : Fin 3)
    (xs : List (Fin n)) : Prop :=
  (xs.length = 4 ∨ xs.length = 5) ∧ xs.Nodup ∧
    (∀ x, (x ≠ r ∧ (template n t).col r x = b) ↔ x ∈ xs) ∧
    ∀ i j : Fin xs.length, i < j →
      ((template n t).col (xs.get i) (xs.get j) = c ↔ supportEdge xs.length i.val j.val)

private instance {n : ℕ} (t : Bool) (r : Fin n) (b c : Fin 3) (xs : List (Fin n)) :
    Decidable (ValidOrder t r b c xs) := by unfold ValidOrder; infer_instance

private theorem shape_of_order {n : ℕ} {t : Bool} {r : Fin n} {b c : Fin 3}
    {xs : List (Fin n)} (h : ValidOrder t r b c xs) :
    SupportShape (template n t) (fun x => x ≠ r ∧ (template n t).col r x = b) c := by
  rcases h with ⟨hlen, hnd, hmem, hedge⟩
  refine ⟨xs.length, hlen, ⟨xs.get, ?_⟩, ?_, hedge⟩
  · exact (List.nodup_iff_injective_get.mp hnd)
  · intro x
    exact (hmem x).trans List.mem_iff_get

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
private theorem orders15 : ∀ (t : Bool) (r : Fin 15) (b c : Fin 3), b ≠ c →
    ValidOrder t r b c (supportOrder t r b c) := by decide

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
private theorem orders16 : ∀ (t : Bool) (r : Fin 16) (b c : Fin 3), b ≠ c →
    ValidOrder t r b c (supportOrder t r b c) := by decide

theorem template_support_shape {n : ℕ} (hn : n = 15 ∨ n = 16)
    (t : Bool) (r : Fin n) (b c : Fin 3) (hbc : b ≠ c) :
    SupportShape (template n t) (fun x => x ≠ r ∧ (template n t).col r x = b) c := by
  rcases hn with rfl | rfl
  · exact shape_of_order (orders15 t r b c hbc)
  · exact shape_of_order (orders16 t r b c hbc)

/-- The intersection with a second root arm is exactly the ordered support.
The two colour indices b and c use the named palette of the sender's block. -/
theorem pinned_support_shape {V : Type*} [Fintype V] [DecidableEq V]
    (G : EdgeCol V 4) (q r : V) (a : Fin 4) {n : ℕ} {t : Bool}
    (hn : n = 15 ∨ n = 16) (hp : PinnedArm G q a n t) (hr : r ∈ arm G q a)
    (b c : Fin 3) (hbc : b ≠ c) :
    SupportShape G (fun x => x ∈ arm G q a ∧ x ∈ arm G r (a.succAbove b)) (a.succAbove c) := by
  obtain ⟨e, he⟩ := hp
  let u : ↥(arm G q a) := ⟨r, hr⟩
  obtain ⟨m, hm, f, hf, hedge⟩ := template_support_shape hn t (e u) b c hbc
  let g : Fin m ↪ V := (f.trans e.symm.toEmbedding).trans ⟨Subtype.val, Subtype.val_injective⟩
  have hed (x y : ↥(arm G q a)) (hxy : x ≠ y) (d : Fin 3) :
      G.col x.val y.val = a.succAbove d ↔ (template n t).col (e x) (e y) = d := by
    rw [he x y hxy]
    exact (Fin.succAbove_right_injective (p := a)).eq_iff
  refine ⟨m, hm, g, ?_, ?_⟩
  · intro x
    constructor
    · rintro ⟨hx, hxr⟩
      obtain ⟨hne, hcol⟩ := (Finset.mem_filter.mp hxr).2
      let v : ↥(arm G q a) := ⟨x, hx⟩
      have hvu : v ≠ u := fun h => hne (congrArg Subtype.val h)
      obtain ⟨i, hi⟩ := (hf _).mp ⟨e.injective.ne hvu, (hed u v hvu.symm b).mp hcol⟩
      refine ⟨i, ?_⟩
      change (e.symm (f i)).val = x
      rw [hi, Equiv.symm_apply_apply]
    · rintro ⟨i, rfl⟩
      let v := e.symm (f i)
      have hv : e v = f i := e.apply_symm_apply _
      obtain ⟨hne, hcol⟩ := (hf (f i)).mpr ⟨i, rfl⟩
      rw [← hv] at hne hcol
      have hvu : v ≠ u := fun h => hne (congrArg e h)
      refine ⟨v.property, Finset.mem_filter.mpr ⟨Finset.mem_univ _, ?_, ?_⟩⟩
      · exact fun h => hvu (Subtype.ext h)
      · exact (hed u v hvu.symm b).mpr hcol
  · intro i j hij
    have hne := e.symm.injective.ne (f.injective.ne hij.ne)
    exact (hed _ _ hne c).trans (by simpa only [Equiv.apply_symm_apply] using hedge i j hij)

end K58
