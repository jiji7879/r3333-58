import K58.Templates

namespace K58

namespace PositionSearch

variable {n : ℕ}

/-- Extend a partial colour-preserving map by testing the edges to the
vertices already assigned. An entire permutation is returned only at a leaf. -/
def maps (C : EdgeCol (Fin n) 3) : List (Fin n) → List (Fin n) →
    (Fin n → Fin n) → List (Fin n → Fin n)
  | [], _, f => [f]
  | x :: xs, done, f =>
    (List.finRange n).flatMap fun y =>
      if done.all (fun u => decide (y ≠ f u ∧ C.col y (f u) = C.col x u)) then
        maps C xs (x :: done) (Function.update f x y)
      else []

private def Partial (C : EdgeCol (Fin n) 3) (D : List (Fin n)) (f : Fin n → Fin n) : Prop :=
  ∀ i ∈ D, ∀ j ∈ D, i ≠ j → f i ≠ f j ∧ C.col (f i) (f j) = C.col i j

private theorem step {C : EdgeCol (Fin n) 3} {D : List (Fin n)} {f : Fin n → Fin n}
    {x y : Fin n} (hD : Partial C D f)
    (hy : ∀ u ∈ D, y ≠ f u ∧ C.col y (f u) = C.col x u) :
    Partial C (x :: D) (Function.update f x y) := by
  intro i hi j hj hij
  by_cases hix : i = x
  · subst i
    have hjx := Ne.symm hij
    have hjD := (List.mem_cons.mp hj).resolve_left hjx
    simpa [Function.update, hjx] using hy j hjD
  · have hiD := (List.mem_cons.mp hi).resolve_left hix
    by_cases hjx : j = x
    · subst j
      obtain ⟨hneq, hc⟩ := hy i hiD
      simpa [Function.update, hix] using
        And.intro hneq.symm ((C.symm (f i) y).trans (hc.trans (C.symm x i)))
    · have hjD := (List.mem_cons.mp hj).resolve_left hjx
      simpa [Function.update, hix, hjx] using hD i hiD j hjD hij

private theorem maps_sound (C : EdgeCol (Fin n) 3) (xs D : List (Fin n))
    (f : Fin n → Fin n) (hn : xs.Nodup) (hd : xs.Disjoint D) (hf : Partial C D f)
    {g : Fin n → Fin n} (hg : g ∈ maps C xs D f) : Partial C (xs ++ D) g := by
  induction xs generalizing D f with
  | nil => simpa [maps] using (show Partial C D g from (List.mem_singleton.mp hg) ▸ hf)
  | cons x xs ih =>
    obtain ⟨y, _, hg'⟩ := List.mem_flatMap.mp hg
    split at hg'
    next h =>
      have hall := List.all_eq_true.mp h
      have hd' : xs.Disjoint (x :: D) := by
        intro a ha h
        rcases List.mem_cons.mp h with rfl | h
        · exact (List.nodup_cons.mp hn).1 ha
        · exact hd (List.mem_cons_of_mem _ ha) h
      have h' := ih (x :: D) _ (List.nodup_cons.mp hn).2 hd'
        (step hf (fun u hu => of_decide_eq_true (hall u hu))) hg'
      intro i hi j hj hij
      apply h' i _ j _ hij
      · simpa [List.mem_append, or_assoc, or_left_comm, or_comm] using hi
      · simpa [List.mem_append, or_assoc, or_left_comm, or_comm] using hj
    next h => simp at hg'

private theorem maps_complete (C : EdgeCol (Fin n) 3) (e : Equiv.Perm (Fin n))
    (he : ∀ i j, i ≠ j → C.col (e i) (e j) = C.col i j)
    (xs D : List (Fin n)) (f : Fin n → Fin n) (hn : xs.Nodup) (hd : xs.Disjoint D)
    (hf : ∀ i ∈ D, f i = e i) :
    ∃ g ∈ maps C xs D f, ∀ i ∈ xs ++ D, g i = e i := by
  induction xs generalizing D f with
  | nil => exact ⟨f, List.mem_singleton_self _, by simpa using hf⟩
  | cons x xs ih =>
    have hD : x ∉ D := fun hx => hd List.mem_cons_self hx
    have hd' : xs.Disjoint (x :: D) := by
      intro a ha h
      rcases List.mem_cons.mp h with rfl | h
      · exact (List.nodup_cons.mp hn).1 ha
      · exact hd (List.mem_cons_of_mem _ ha) h
    have hstep : ∀ i ∈ x :: D, Function.update f x (e x) i = e i := by
      intro i hi
      rcases List.mem_cons.mp hi with rfl | hi
      · simp
      · simpa [Function.update, show i ≠ x from fun h => hD (h ▸ hi)] using hf i hi
    obtain ⟨g, hg, hend⟩ := ih _ _ (List.nodup_cons.mp hn).2 hd' hstep
    refine ⟨g, List.mem_flatMap.mpr ⟨e x, List.mem_finRange _, ?_⟩, ?_⟩
    · have hcheck : (D.all fun u => decide (e x ≠ f u ∧ C.col (e x) (f u) = C.col x u)) = true := by
        apply List.all_eq_true.mpr
        intro u hu
        have hxu : x ≠ u := fun h => hD (h ▸ hu)
        simpa only [hf u hu, decide_eq_true_eq] using And.intro (e.injective.ne hxu) (he x u hxu)
      simpa only [hcheck, if_true] using hg
    · intro i hi
      apply hend
      simpa [List.mem_append, or_assoc, or_left_comm, or_comm] using hi

def automorphisms (C : EdgeCol (Fin n) 3) := maps C (List.finRange n) [] id

theorem mem_automorphisms_iff (C : EdgeCol (Fin n) 3) (f : Fin n → Fin n) :
    f ∈ automorphisms C ↔ Function.Bijective f ∧
      ∀ i j, i ≠ j → C.col (f i) (f j) = C.col i j := by
  constructor
  · intro h
    have hp := maps_sound C (List.finRange n) [] id (List.nodup_finRange n)
      (by simp) (by intro i hi; simp at hi) h
    have hall (x : Fin n) : x ∈ List.finRange n ++ [] := by simp
    have hinj : Function.Injective f := by
      intro i j h
      by_contra hne
      exact (hp i (hall i) j (hall j) hne).1 h
    exact ⟨Finite.injective_iff_bijective.mp hinj, fun i j h => (hp i (hall i) j (hall j) h).2⟩
  · rintro ⟨hbij, he⟩
    obtain ⟨g, hg, hgf⟩ := maps_complete C (Equiv.ofBijective f hbij) he (List.finRange n) [] id
      (List.nodup_finRange n) (by simp) (by simp)
    have : g = f := funext (fun i => hgf i (by simp))
    exact this ▸ hg

end PositionSearch
end K58
