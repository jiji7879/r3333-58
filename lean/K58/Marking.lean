import K58.Classification
import K58.Palette
import K58.Support

namespace K58

private theorem named_of_palette {n : ℕ} (hc : Classified n)
    (hp : ∀ t (p : Equiv.Perm (Fin 3)), ∃ e : Equiv.Perm (Fin n),
      ∀ i j, i ≠ j → (template n t).col (e i) (e j) = p ((template n t).col i j))
    (G : EdgeCol (Fin n) 3) (hG : TriangleFree G) :
    ∃ t, ∃ e : Equiv.Perm (Fin n), ∀ i j, i ≠ j →
      G.col i j = (template n t).col (e i) (e j) := by
  obtain ⟨t, v, p, hv⟩ := hc G hG
  obtain ⟨e, he⟩ := hp t p
  exact ⟨t, v.trans e, fun i j hij => (hv i j hij).trans (he _ _ (v.injective.ne hij)).symm⟩

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Pin any critical arm using literal host colours in their increasing order. -/
theorem critical_arm_pinned (G : EdgeCol V 4) (hG : TriangleFree G) (r : V) (a : Fin 4)
    (hd : deg G r a = 15 ∨ deg G r a = 16) :
    ∃ t, PinnedArm G r a (deg G r a) t := by
  rcases hd with h | h
  · rw [h]
    exact pin_of_named_classification (named_of_palette classified_15 palette_15) G hG r a h
  · rw [h]
    apply pin_of_named_classification _ G hG r a h
    apply named_of_palette classified_16
    intro t p
    obtain ⟨e, _, he⟩ := palette_16_fixing t p 0
    exact ⟨e, he⟩

/-- The chosen sender has a second pinned block; the original root lies in it. -/
theorem marked_sender_pinned (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (r : Fin 58) (a : Fin 4) (t : ℕ) (M : Finset (Fin 58)) (hM : M ⊆ arm G r a)
    (hm : deg G r a - t + 1 ≤ M.card) (ht : t ≤ armSenders G r a) :
    ∃ q ∈ M, Sends G q r ∧ r ∈ arm G q a ∧ (deg G q a = 15 ∨ deg G q a = 16) ∧
      ∃ k, PinnedArm G q a (deg G q a) k := by
  obtain ⟨q, hq, hs⟩ := marked_sender G r a t M hM hm ht
  obtain ⟨hqr, hcol⟩ := (Finset.mem_filter.mp (hM hq)).2
  have hrev := (G.symm q r).trans hcol
  have hlo : 15 ≤ deg G q a := hrev ▸ hs.2
  have hhi := deg_le_sixteen G hG q a
  have hd : deg G q a = 15 ∨ deg G q a = 16 := by omega
  exact ⟨q, hq, hs, Finset.mem_filter.mpr ⟨Finset.mem_univ _, hqr.symm, hrev⟩,
    hd, critical_arm_pinned G hG q a hd⟩

end K58
