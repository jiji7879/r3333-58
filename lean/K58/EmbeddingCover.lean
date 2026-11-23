import K58.CaseExpansion

namespace K58

variable {n m : ℕ} (S : EdgeCol (Fin n) 3) (a : Fin 4) (T : EdgeCol (Fin m) 3) (b : Fin 4)

private def fits (u x : Fin n) (v y : Fin m) : Prop :=
  v ≠ y ∧ a.succAbove (S.col u x) = b.succAbove (T.col v y)

private theorem canonicalEmbedding_mem (group : List (Fin m → Fin m)) (f : Fin n → Fin m)
    (xs : List (Fin n)) (chosen : List (Fin n × Fin m))
    (hxs : xs.Pairwise fun u x => fits S a T b u x (f u) (f x))
    (hc : ∀ z ∈ chosen, ∀ x ∈ xs, fits S a T b z.1 x z.2 (f x))
    (hmin : ∀ g ∈ group, chosen.reverse.map Prod.snd ++ xs.map f ≤
      (chosen.reverse.map Prod.snd ++ xs.map f).map g) :
    (chosen.reverse.map Prod.snd ++ xs.map f).map Fin.val ∈
      supportEmbeddings S a T b group xs chosen := by
  induction xs generalizing chosen with
  | nil =>
    have test : group.all (fun g => decide
        (chosen.reverse.map Prod.snd ≤ (chosen.reverse.map Prod.snd).map g)) = true :=
      List.all_eq_true.mpr fun g hg => decide_eq_true (by simpa using hmin g hg)
    simp only [supportEmbeddings, List.map_nil, List.append_nil, test, if_true, List.mem_singleton]
  | cons x xs ih =>
    have test : (chosen.all fun z => decide
        (z.2 ≠ f x ∧ a.succAbove (S.col z.1 x) = b.succAbove (T.col z.2 (f x)))) = true := by
      apply List.all_eq_true.mpr
      intro z hz
      apply decide_eq_true
      exact hc z hz x List.mem_cons_self
    have hstep : ∀ z ∈ (x, f x) :: chosen, ∀ u ∈ xs, fits S a T b z.1 u z.2 (f u) := by
      intro z hz u hu
      rcases List.mem_cons.mp hz with rfl | hz
      · exact (List.pairwise_cons.mp hxs).1 _ hu
      · exact hc z hz _ (List.mem_cons_of_mem _ hu)
    have hw : ((x, f x) :: chosen).reverse.map Prod.snd ++ xs.map f =
        chosen.reverse.map Prod.snd ++ (x :: xs).map f := by simp [List.append_assoc]
    have hm := ih _ (List.pairwise_cons.mp hxs).2 hstep (by simpa only [hw] using hmin)
    apply List.mem_flatMap.mpr
    refine ⟨f x, List.mem_finRange _, ?_⟩
    simpa only [test, if_true, hw] using hm

/-- Every legal ordered support embedding has a representative in the same list
used by the ledger decoder. One colour-preserving target automorphism realizes
the choice on the entire support. -/
theorem support_embedding_represented (group : List (Fin m → Fin m))
    (hgroup : group = PositionSearch.automorphisms T) (xs : List (Fin n)) (f : Fin n → Fin m)
    (hfit : xs.Pairwise fun u x => f u ≠ f x ∧
      a.succAbove (S.col u x) = b.succAbove (T.col (f u) (f x))) :
    ∃ e : Equiv.Perm (Fin m), (∀ i j, i ≠ j → T.col (e i) (e j) = T.col i j) ∧
      (xs.map fun x => (e (f x)).val) ∈ supportEmbeddings S a T b group xs [] := by
  classical
  subst group
  let F := PositionSearch.automorphisms T
  let word := fun g : Fin m → Fin m => xs.map (g ∘ f)
  let W := F.toFinset.image word
  have hid : id ∈ F := (PositionSearch.mem_automorphisms_iff T _).mpr
    ⟨Function.bijective_id, fun _ _ _ => rfl⟩
  have hW : W.Nonempty := ⟨word id, Finset.mem_image.mpr ⟨_, List.mem_toFinset.mpr hid, rfl⟩⟩
  obtain ⟨g, hgin, hword⟩ := Finset.mem_image.mp (W.min'_mem hW)
  obtain ⟨hg, hcol⟩ := (PositionSearch.mem_automorphisms_iff T g).mp (List.mem_toFinset.mp hgin)
  have least (u : Fin m → Fin m) (hu : u ∈ F) : word g ≤ (word g).map u := by
    obtain ⟨hub, huc⟩ := (PositionSearch.mem_automorphisms_iff T _).mp hu
    have hcomp : u ∘ g ∈ F := (PositionSearch.mem_automorphisms_iff T _).mpr
      ⟨hub.comp hg, fun i j hij => (huc _ _ (hg.injective.ne hij)).trans (hcol i j hij)⟩
    have h := W.min'_le (word (u ∘ g)) (Finset.mem_image.mpr
      ⟨u ∘ g, List.mem_toFinset.mpr hcomp, rfl⟩)
    rw [← hword] at h
    simpa only [word, List.map_map, Function.comp_assoc] using h
  have hfit' : xs.Pairwise fun u x => fits S a T b u x (g (f u)) (g (f x)) := by
    apply hfit.imp
    intro u x hx
    exact ⟨hg.injective.ne hx.1, hx.2.trans (congrArg b.succAbove (hcol _ _ hx.1)).symm⟩
  refine ⟨Equiv.ofBijective g hg, hcol, ?_⟩
  have h := canonicalEmbedding_mem S a T b F (g ∘ f) xs [] hfit' (by simp)
    (by simpa [word] using least)
  simpa only [List.reverse_nil, List.map_nil, List.nil_append, List.map_map,
    Function.comp_def, Equiv.ofBijective_apply] using h

end K58
