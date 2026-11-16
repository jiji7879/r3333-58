/-
K58: `R(3,3) ≤ 6`, in the form needed for the colour-degree cap.

In a triangle-free 2-colouring every colour-degree is at most 2, so a
triangle-free 2-colouring of `K_m` has `m ≤ 5`.
-/
import K58.Basic

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The colour degrees at a vertex sum to `|V| - 1`. -/
theorem sum_deg {k : ℕ} (G : EdgeCol V k) (i : V) :
    ∑ a : Fin k, deg G i a = Fintype.card V - 1 := by
  have hmaps : Set.MapsTo (fun j : V => G.col i j)
      ↑(Finset.univ.erase i) ↑(Finset.univ : Finset (Fin k)) :=
    fun x _ => Finset.mem_univ _
  have h := Finset.card_eq_sum_card_fiberwise
    (s := Finset.univ.erase i) (t := (Finset.univ : Finset (Fin k)))
    (f := fun j : V => G.col i j) hmaps
  rw [Finset.card_erase_of_mem (Finset.mem_univ i), Finset.card_univ] at h
  have hfib : ∀ b : Fin k, {a ∈ Finset.univ.erase i | G.col i a = b}.card = deg G i b := by
    intro b
    rw [deg]
    congr 1
    ext j
    simp only [Finset.mem_filter, Finset.mem_erase, Finset.mem_univ, and_true]
    tauto
  rw [h]
  exact Finset.sum_congr rfl fun b _ => (hfib b).symm

/-- In a triangle-free 2-colouring, every colour-degree is at most 2. -/
theorem deg_le_two_of_two_colour (G : EdgeCol V 2) (h : TriangleFree G)
    (i : V) (a : Fin 2) : deg G i a ≤ 2 := by
  by_contra hle
  simp only [not_le] at hle
  have hs : 2 < (Finset.univ.filter (fun j : V => j ≠ i ∧ G.col i j = a)).card := hle
  obtain ⟨x, hx, y, hy, z, hz, hxy, hxz, hyz⟩ := Finset.two_lt_card.mp hs
  have hne : ∀ u v : V, u ∈ Finset.univ.filter (fun j : V => j ≠ i ∧ G.col i j = a) →
      v ∈ Finset.univ.filter (fun j : V => j ≠ i ∧ G.col i j = a) → u ≠ v →
      G.col u v ≠ a := by
    intro u v hu hv huv hc
    have hu2 : u ≠ i ∧ G.col i u = a := by simpa using hu
    have hv2 : v ≠ i ∧ G.col i v = a := by simpa using hv
    exact h i u v (Ne.symm hu2.1) huv (Ne.symm hv2.1)
      ⟨by rw [hu2.2, hv2.2], by rw [hv2.2, hc]⟩
  have hone : ∀ b : Fin 2, b ≠ a → b = a + 1 := by
    intro b hb
    fin_cases a <;> fin_cases b <;> simp_all
  have e1 : G.col x y = a + 1 := hone _ (hne x y hx hy hxy)
  have e2 : G.col y z = a + 1 := hone _ (hne y z hy hz hyz)
  have e3 : G.col x z = a + 1 := hone _ (hne x z hx hz hxz)
  exact h x y z hxy hyz hxz ⟨by simp only [e1, e3], by simp only [e3, e2]⟩

/-- `R(3,3) ≤ 6`: no triangle-free 2-colouring of a six-point set. -/
theorem two_colour_six (G : EdgeCol V 2) (hV : Fintype.card V = 6)
    (h : TriangleFree G) : False := by
  have : Nonempty V := Fintype.card_pos_iff.mp (by omega)
  have h0 : deg G (Classical.arbitrary V) 0 ≤ 2 :=
    deg_le_two_of_two_colour G h _ 0
  have h1 : deg G (Classical.arbitrary V) 1 ≤ 2 :=
    deg_le_two_of_two_colour G h _ 1
  have hsum := sum_deg G (Classical.arbitrary V)
  rw [Fin.sum_univ_two, hV] at hsum
  omega

end K58
