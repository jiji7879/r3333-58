import K58.EmittedBridge
import K58.Marking

open K58
open K58.SequentialCounter
open K58.SenderReady
open K58.SemanticAssembly

set_option autoImplicit false

namespace K58.CountBridge

/-- Number of true bits among the first `n` Bits, as a finite index set. -/
def trueIndices (b : Nat → Bool) (n : Nat) : Finset Nat :=
  (Finset.range n).filter (fun i => b i)

theorem card_trueIndices (b : Nat → Bool) (n : Nat) :
    (trueIndices b n).card = prefixCount b n := by
  induction n with
  | zero => simp [trueIndices, prefixCount]
  | succ n ih =>
      rw [prefixCount, ← ih]
      change ((Finset.range (n + 1)).filter (fun i => b i)).card =
        (trueIndices b n).card + if b n then 1 else 0
      rw [Finset.range_add_one, Finset.filter_insert]
      cases hb : b n <;> simp [hb, trueIndices]

/-- Vertices selected by a true emitted prefix count. -/
def countedVertices (b : Nat → Bool) (n : Nat) (vertex : Nat → Fin 58) : Finset (Fin 58) :=
  (trueIndices b n).image vertex

/-- A true count on decoded atoms yields exactly the finite set required by
`EmittedBridge.deg_ge_of_counted`.  Injectivity is needed only below `n`. -/
theorem exists_neighbour_finset_of_count
    (G : EdgeCol (Fin 58) 4) (q r : Fin 58)
    (b : Nat → Bool) (n : Nat) (vertex : Nat → Fin 58)
    (hinj : ∀ i, i < n → ∀ j, j < n → vertex i = vertex j → i = j)
    (hne : ∀ i, i < n → vertex i ≠ q)
    (hcol : ∀ i, i < n → b i = true → G.col q (vertex i) = 1)
    (hroot : ∀ i, i < n → vertex i ≠ r)
    (hcount : 14 ≤ prefixCount b n) :
    ∃ W : Finset (Fin 58),
      (∀ x ∈ W, x ≠ q ∧ G.col q x = 1) ∧ r ∉ W ∧ 14 ≤ W.card := by
  let W := countedVertices b n vertex
  have hsub : Set.InjOn vertex (trueIndices b n) := by
    intro i hi j hj he
    apply hinj i _ j _ he
    · exact List.mem_range.mp (Finset.mem_filter.mp hi).1
    · exact List.mem_range.mp (Finset.mem_filter.mp hj).1
  have hW : ∀ x ∈ W, x ≠ q ∧ G.col q x = 1 := by
    intro x hx
    obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hx
    have hin : i < n := List.mem_range.mp (Finset.mem_filter.mp hi).1
    have hbit : b i = true := by simpa using (Finset.mem_filter.mp hi).2
    exact ⟨hne i hin, hcol i hin hbit⟩
  have hrW : r ∉ W := by
    intro hr
    obtain ⟨i, hi, hir⟩ := Finset.mem_image.mp hr
    have hin : i < n := List.mem_range.mp (Finset.mem_filter.mp hi).1
    exact hroot i hin hir
  have hcard : W.card = prefixCount b n := by
    change ((trueIndices b n).image vertex).card = prefixCount b n
    rw [Finset.card_image_of_injOn hsub, card_trueIndices]
  exact ⟨W, hW, hrW, hcard ▸ hcount⟩

/-- The count supplies the finite set in exactly the form used by the current
physical degree lemma. -/
theorem deg_ge_of_emitted_count
    (G : EdgeCol (Fin 58) 4) (q r : Fin 58)
    (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (b : Nat → Bool) (n : Nat) (vertex : Nat → Fin 58)
    (hinj : ∀ i, i < n → ∀ j, j < n → vertex i = vertex j → i = j)
    (hne : ∀ i, i < n → vertex i ≠ q)
    (hcol : ∀ i, i < n → b i = true → G.col q (vertex i) = 1)
    (hroot : ∀ i, i < n → vertex i ≠ r)
    (hcount : 14 ≤ prefixCount b n) : 15 ≤ deg G q 1 := by
  obtain ⟨W, hW, hrW, hcard⟩ :=
    exists_neighbour_finset_of_count G q r b n vertex hinj hne hcol hroot hcount
  exact EmittedBridge.deg_ge_of_counted G q r hqr_ne hqr W hW hrW hcard

/-- No fresh classification premise is needed: it is already implemented by
`critical_arm_pinned`, including both template palettes. -/
theorem sender_pinned_of_count_classified
    (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (W : Finset (Fin 58)) (hW : ∀ x ∈ W, x ≠ q ∧ G.col q x = 1)
    (hrW : r ∉ W) (hcard : 14 ≤ W.card) :
    Sends G q r ∧ deg G q 1 ≤ 16 ∧ ∃ t : Bool, PinnedArm G q 1 (deg G q 1) t := by
  have hlo : 15 ≤ deg G q 1 :=
    EmittedBridge.deg_ge_of_counted G q r hqr_ne hqr W hW hrW hcard
  have hhi : deg G q 1 ≤ 16 := deg_le_sixteen G hG q 1
  have hd : deg G q 1 = 15 ∨ deg G q 1 = 16 := by omega
  have hsends : Sends G q r := ⟨hqr_ne.symm, by rw [hqr]; exact hlo⟩
  obtain ⟨t, ht⟩ := critical_arm_pinned G hG q 1 hd
  exact ⟨hsends, hhi, t, ht⟩

#print axioms K58.CountBridge.card_trueIndices
#print axioms K58.CountBridge.exists_neighbour_finset_of_count
#print axioms K58.CountBridge.deg_ge_of_emitted_count
#print axioms K58.CountBridge.sender_pinned_of_count_classified

end K58.CountBridge
