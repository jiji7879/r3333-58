import K58.SecondRoot
import K58.EmbeddingCover
import Mathlib.Logic.Equiv.Fintype

namespace K58

/-- A free arm can send the vertices of any ordered support to its initial segment. -/
private theorem initial_segment {α : Type*} {m : ℕ} (s : List α) (f : α → Fin m)
    (hn : (s.map f).Nodup) : ∃ p : Equiv.Perm (Fin m), s.map (fun x => (p (f x)).val) = List.range s.length := by
  let l := s.map f
  let hlen : l.length ≤ m := by
    simpa only [Fintype.card_fin] using Fintype.card_le_of_injective l.get (List.nodup_iff_injective_get.mp hn)
  let g : Fin l.length → Fin m := Fin.castLE hlen
  obtain ⟨p, hp⟩ := Equiv.Perm.exists_extending_pair l.get g (List.nodup_iff_injective_get.mp hn) (Fin.castLE_injective hlen)
  refine ⟨p, List.ext_getElem (by simp) ?_⟩
  intro j hj hk
  have hjl : j < l.length := by simpa [l] using hj
  have h := congrArg Fin.val (hp ⟨j,hjl⟩)
  simpa [l, g, List.get_eq_getElem] using h

private theorem targetWords_cover {n m : ℕ} (C : EdgeCol (Fin n) 3) (a b : Fin 4)
    (kind : Char) (s : List (Fin n)) (f : Fin n → Fin m) (hn : (s.map f).Nodup)
    (hkind : (kind = '-' ∧ m < 15) ∨ ((kind = 'U' ∨ kind = 'T') ∧ (m = 15 ∨ m = 16)))
    (hfit : 15 ≤ m → s.Pairwise fun x y => f x ≠ f y ∧ a.succAbove (C.col x y) =
      b.succAbove ((template m (kind == 'T')).col (f x) (f y))) :
    ∃ (p : Equiv.Perm (Fin m)) (ws : List (List ℕ)) (j : Fin ws.length),
      targetWords C a b m kind s = some ws ∧
      ws[j.val] = s.map (fun x => (p (f x)).val) ∧
      (15 ≤ m → ∀ x y, x ≠ y → (template m (kind == 'T')).col (p x) (p y) =
        (template m (kind == 'T')).col x y) := by
  rcases hkind with ⟨rfl, hsmall⟩ | ⟨hk, hm⟩
  · obtain ⟨p,hp⟩ := initial_segment s f hn
    exact ⟨p, [List.range s.length], 0, by simp [targetWords], hp.symm, fun h => (by omega : False).elim⟩
  · have hnot : kind ≠ '-' := by rcases hk with rfl | rfl <;> decide
    rcases hm with rfl | rfl
    · obtain ⟨p, he, hw⟩ := support_embedding_represented C a _ b _ (named15_exact _) s f (hfit (by decide))
      obtain ⟨j,hj⟩ := List.mem_iff_get.mp hw
      exact ⟨p,_,j,by simp [targetWords, hnot, hk],hj, fun _ => he⟩
    · obtain ⟨p, he, hw⟩ := support_embedding_represented C a _ b _ (named16_target_group _) s f (hfit (by decide))
      obtain ⟨j,hj⟩ := List.mem_iff_get.mp hw
      exact ⟨p,_,j,by simp [targetWords, hnot, hk],hj, fun _ => he⟩

private theorem plan_target_kind : ∀ (i : Fin 41) (b : Fin 4), ∃ kind ∈ ['-','U','T'],
    (indexedPlan i).kinds.toList[b.val]? = some kind ∧
    ((kind = '-' ∧ plannedDegree (indexedPlan i) b < 15) ∨
      ((kind = 'U' ∨ kind = 'T') ∧ (plannedDegree (indexedPlan i) b = 15 ∨
       plannedDegree (indexedPlan i) b = 16))) := by decide

/-- A permutation of one arm preserves its template (when critical) and realizes
one placement index on all the ordered source vertices at once. -/
theorem supportTable_cover (k : CaseKey) (r : Fin k.secondSize) (c : Fin 3)
    (f : Fin k.secondSize → Fin (plannedDegree k.plan (k.arm.succAbove c)))
    (hn : ((supportAt k r (k.arm.succAbove c)).map f).Nodup)
    (hfit : let b := k.arm.succAbove c
      15 ≤ plannedDegree k.plan b → (supportAt k r b).Pairwise fun x y =>
        f x ≠ f y ∧ k.arm.succAbove ((template _ k.secondTwisted).col x y) =
          b.succAbove ((template _ (planTwisted k.plan b)).col (f x) (f y))) :
    let b := k.arm.succAbove c
    ∃ (p : Equiv.Perm (Fin (plannedDegree k.plan b))) (ws : List (List ℕ)) (j : Fin ws.length),
      supportTable k r c = some (supportAt k r b,ws) ∧
      ws[j.val] = (supportAt k r b).map (fun x => (p (f x)).val) ∧
      (15 ≤ plannedDegree k.plan b → ∀ x y, x ≠ y →
        (template _ (planTwisted k.plan b)).col (p x) (p y) = (template _ (planTwisted k.plan b)).col x y) := by
  let b := k.arm.succAbove c
  obtain ⟨kind, _, hk, hkind⟩ := plan_target_kind k.planIndex b
  change k.plan.kinds.toList[b.val]? = some kind at hk
  have htw : planTwisted k.plan b = (kind == 'T') := by simp [planTwisted, hk]
  obtain ⟨p, ws, j, hw, hj, he⟩ := targetWords_cover (template _ k.secondTwisted) k.arm b
    kind (supportAt k r b) f hn hkind (by simpa only [← htw] using hfit)
  refine ⟨p,ws,j,supportTable_of_words k r c kind ws hk hw,hj,?_⟩
  change 15 ≤ plannedDegree k.plan b → ∀ x y, x ≠ y → (template _ (planTwisted k.plan b)).col (p x) (p y) = (template _ (planTwisted k.plan b)).col x y
  rw [htw]
  exact he

end K58
