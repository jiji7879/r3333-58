import K58.Basic
import Mathlib.Tactic

/-!
# Configurable maximal-colour normal form

Kernel-checks configurable-edge maximalisation, separately from DIMACS byte
layout and from full/pinned maximalisation.  An edge is normal for colour `c`
when it has colour `c` or some third vertex joins both endpoints by `c`.
Later steps only add `c`-edges, so old witnesses persist.
-/

namespace K58.ConfigurableMaximal

open K58
open Classical

variable {V : Type*} {k : ℕ}

/-- A two-edge colour-`c` path through a third vertex. -/
def TwoPath (G : EdgeCol V k) (c : Fin k) (u v : V) : Prop :=
  ∃ w, w ≠ u ∧ w ≠ v ∧ G.col u w = c ∧ G.col v w = c

/-- The condition imposed on every configurable edge. -/
def NormalAt (G : EdgeCol V k) (c : Fin k) (e : V × V) : Prop :=
  G.col e.1 e.2 = c ∨ TwoPath G c e.1 e.2

/-- Membership of an oriented pair in an undirected edge. -/
def OnEdge (e : V × V) (x y : V) : Prop :=
  (e.1 = x ∧ e.2 = y) ∨ (e.1 = y ∧ e.2 = x)

theorem onEdge_symm {e : V × V} {x y : V} (h : OnEdge e x y) : OnEdge e y x := by
  rcases h with h | h
  · exact Or.inr h
  · exact Or.inl h

theorem not_onEdge_of_left_ne {u v x y : V} (hxu : x ≠ u) (hxv : x ≠ v) :
    ¬ OnEdge (u, v) x y := by
  rintro (⟨hux, _⟩ | ⟨_, hvx⟩)
  · exact hxu hux.symm
  · exact hxv hvx.symm

theorem not_onEdge_of_right_ne {u v x y : V} (hyu : y ≠ u) (hyv : y ≠ v) :
    ¬ OnEdge (u, v) x y := by
  rintro (⟨_, hvy⟩ | ⟨huy, _⟩)
  · exact hyv hvy.symm
  · exact hyu huy.symm

/-- Set one undirected edge to colour `c`; all other entries are unchanged. -/
noncomputable def recolour (G : EdgeCol V k) (u v : V) (c : Fin k) : EdgeCol V k where
  col x y := if OnEdge (u, v) x y then c else G.col x y
  symm x y := by
    by_cases h : OnEdge (u, v) x y
    · have h' : OnEdge (u, v) y x := onEdge_symm h
      rw [if_pos h, if_pos h']
    · have h' : ¬ OnEdge (u, v) y x := fun hy => h (onEdge_symm hy)
      rw [if_neg h, if_neg h']
      exact G.symm x y

@[simp] theorem recolour_apply_same (G : EdgeCol V k) (u v : V) (c : Fin k) :
    (recolour G u v c).col u v = c := by
  exact if_pos (Or.inl ⟨rfl, rfl⟩)

@[simp] theorem recolour_apply_same_rev (G : EdgeCol V k) (u v : V) (c : Fin k) :
    (recolour G u v c).col v u = c := by
  rw [(recolour G u v c).symm]
  exact recolour_apply_same G u v c

theorem recolour_apply_of_not_onEdge (G : EdgeCol V k) (u v : V) (c : Fin k)
    {x y : V} (h : ¬ OnEdge (u, v) x y) :
    (recolour G u v c).col x y = G.col x y := by
  exact if_neg h

/-- Recolouring to `c` never removes a colour-`c` edge. -/
theorem recolour_preserves_c (G : EdgeCol V k) (u v : V) (c : Fin k)
    {x y : V} (hxy : G.col x y = c) : (recolour G u v c).col x y = c := by
  by_cases h : OnEdge (u, v) x y
  · exact if_pos h
  · rw [recolour_apply_of_not_onEdge _ _ _ _ h]
    exact hxy

/-- Any non-`c` colour in the new colouring was already present. -/
theorem eq_old_of_recolour_ne_c (G : EdgeCol V k) (u v : V) (c : Fin k)
    {x y : V} {d : Fin k} (hdc : d ≠ c)
    (hxy : (recolour G u v c).col x y = d) : G.col x y = d := by
  by_cases h : OnEdge (u, v) x y
  · have hc : (recolour G u v c).col x y = c := if_pos h
    rw [hc] at hxy
    exact (hdc hxy.symm).elim
  · rwa [recolour_apply_of_not_onEdge _ _ _ _ h] at hxy

theorem twoPath_symm (G : EdgeCol V k) (c : Fin k) {u v : V}
    (h : TwoPath G c u v) : TwoPath G c v u := by
  obtain ⟨w, hwu, hwv, huw, hvw⟩ := h
  exact ⟨w, hwv, hwu, hvw, huw⟩

/-- With no two-edge `c`-path between the endpoints, setting `uv` to `c`
cannot create a monochromatic triangle. -/
theorem triangleFree_recolour (G : EdgeCol V k) {u v : V} (c : Fin k)
    (hpath : ¬ TwoPath G c u v) (hG : TriangleFree G) :
    TriangleFree (recolour G u v c) := by
  intro i j l hij hjl hil hmono
  apply hG i j l hij hjl hil
  by_cases hij' : OnEdge (u, v) i j
  · change (u = i ∧ v = j) ∨ (u = j ∧ v = i) at hij'
    exfalso
    rcases hij' with ⟨hi, hj⟩ | ⟨hi, hj⟩
    · subst i; subst j
      have hu := not_onEdge_of_right_ne (x := u) hil.symm hjl.symm
      have hv := not_onEdge_of_right_ne (x := v) hil.symm hjl.symm
      rw [recolour_apply_same, recolour_apply_of_not_onEdge _ _ _ _ hu,
        recolour_apply_of_not_onEdge _ _ _ _ hv] at hmono
      exact hpath ⟨l, hil.symm, hjl.symm, hmono.1.symm,
        hmono.2.symm.trans hmono.1.symm⟩
    · subst i; subst j
      have hu := not_onEdge_of_right_ne (x := u) hjl.symm hil.symm
      have hv := not_onEdge_of_right_ne (x := v) hjl.symm hil.symm
      rw [recolour_apply_same_rev, recolour_apply_of_not_onEdge _ _ _ _ hu,
        recolour_apply_of_not_onEdge _ _ _ _ hv] at hmono
      exact hpath ⟨l, hjl.symm, hil.symm, hmono.2.symm.trans hmono.1.symm,
        hmono.1.symm⟩
  by_cases hil' : OnEdge (u, v) i l
  · change (u = i ∧ v = l) ∨ (u = l ∧ v = i) at hil'
    exfalso
    rcases hil' with ⟨hi, hl⟩ | ⟨hi, hl⟩
    · subst i; subst l
      have hu := not_onEdge_of_right_ne (x := u) hij.symm hjl
      have hv := not_onEdge_of_left_ne (y := v) hij.symm hjl
      rw [recolour_apply_same, recolour_apply_of_not_onEdge _ _ _ _ hu,
        recolour_apply_of_not_onEdge _ _ _ _ hv] at hmono
      exact hpath ⟨j, hij.symm, hjl, hmono.1,
        (G.symm v j).trans hmono.2.symm⟩
    · subst i; subst l
      have hu := not_onEdge_of_left_ne (y := u) hjl hij.symm
      have hv := not_onEdge_of_right_ne (x := v) hjl hij.symm
      rw [recolour_apply_same_rev, recolour_apply_of_not_onEdge _ _ _ _ hu,
        recolour_apply_of_not_onEdge _ _ _ _ hv] at hmono
      exact hpath ⟨j, hjl, hij.symm, (G.symm u j).trans hmono.2.symm,
        hmono.1⟩
  by_cases hjl' : OnEdge (u, v) j l
  · change (u = j ∧ v = l) ∨ (u = l ∧ v = j) at hjl'
    exfalso
    rcases hjl' with ⟨hj, hl⟩ | ⟨hj, hl⟩
    · subst j; subst l
      have hu := not_onEdge_of_left_ne (y := u) hij hil
      have hv := not_onEdge_of_left_ne (y := v) hij hil
      rw [recolour_apply_same, recolour_apply_of_not_onEdge _ _ _ _ hu,
        recolour_apply_of_not_onEdge _ _ _ _ hv] at hmono
      exact hpath ⟨i, hij, hil, (G.symm u i).trans
        (hmono.1.trans hmono.2), (G.symm v i).trans hmono.2⟩
    · subst j; subst l
      have hu := not_onEdge_of_left_ne (y := u) hil hij
      have hv := not_onEdge_of_left_ne (y := v) hil hij
      rw [recolour_apply_same_rev, recolour_apply_of_not_onEdge _ _ _ _ hu,
        recolour_apply_of_not_onEdge _ _ _ _ hv] at hmono
      exact hpath ⟨i, hil, hij, (G.symm u i).trans hmono.2,
        (G.symm v i).trans (hmono.1.trans hmono.2)⟩
  constructor
  · calc
      G.col i j = (recolour G u v c).col i j :=
        (recolour_apply_of_not_onEdge _ _ _ _ hij').symm
      _ = (recolour G u v c).col i l := hmono.1
      _ = G.col i l := recolour_apply_of_not_onEdge _ _ _ _ hil'
  · calc
      G.col i l = (recolour G u v c).col i l :=
        (recolour_apply_of_not_onEdge _ _ _ _ hil').symm
      _ = (recolour G u v c).col j l := hmono.2
      _ = G.col j l := recolour_apply_of_not_onEdge _ _ _ _ hjl'

/-- `H` retains every `c`-coloured entry of `G`. -/
def PreservesColour (G H : EdgeCol V k) (c : Fin k) : Prop :=
  ∀ x y, G.col x y = c → H.col x y = c

theorem twoPath_mono {G H : EdgeCol V k} {c : Fin k} {u v : V}
    (h : TwoPath G c u v) (hc : PreservesColour G H c) : TwoPath H c u v := by
  obtain ⟨w, hwu, hwv, huw, hvw⟩ := h
  exact ⟨w, hwu, hwv, hc u w huw, hc v w hvw⟩

theorem normalAt_mono {G H : EdgeCol V k} {c : Fin k} {e : V × V}
    (h : NormalAt G c e) (hc : PreservesColour G H c) : NormalAt H c e := by
  rcases h with h | h
  · exact Or.inl (hc _ _ h)
  · exact Or.inr (twoPath_mono h hc)

/-- Process one configurable edge exactly as the Python normaliser does. -/
noncomputable def step (G : EdgeCol V k) (c : Fin k) (e : V × V) : EdgeCol V k :=
  if NormalAt G c e then G else recolour G e.1 e.2 c

theorem normalAt_step (G : EdgeCol V k) (c : Fin k) (e : V × V) :
    NormalAt (step G c e) c e := by
  by_cases h : NormalAt G c e
  · simp [step, h]
  · rw [step, if_neg h]
    exact Or.inl (recolour_apply_same G e.1 e.2 c)

theorem preservesColour_step (G : EdgeCol V k) (c : Fin k) (e : V × V) :
    PreservesColour G (step G c e) c := by
  intro x y hxy
  by_cases h : NormalAt G c e
  · simpa [step, h] using hxy
  · rw [step, if_neg h]
    exact recolour_preserves_c G _ _ _ hxy

theorem triangleFree_step (G : EdgeCol V k) (c : Fin k) (e : V × V)
    (hG : TriangleFree G) : TriangleFree (step G c e) := by
  by_cases h : NormalAt G c e
  · simpa [step, h] using hG
  · rw [step, if_neg h]
    exact triangleFree_recolour G c (fun hp => h (Or.inr hp)) hG

theorem step_apply_of_not_onEdge (G : EdgeCol V k) (c : Fin k) {e : V × V}
    {x y : V} (hxy : ¬ OnEdge e x y) : (step G c e).col x y = G.col x y := by
  by_cases h : NormalAt G c e
  · simp [step, h]
  · rw [step, if_neg h]
    exact recolour_apply_of_not_onEdge G _ _ _ hxy

/-- Sequentially normalise the supplied list, from left to right. -/
noncomputable def normalise (G : EdgeCol V k) (c : Fin k) :
    List (V × V) → EdgeCol V k
  | [] => G
  | e :: es => normalise (step G c e) c es

@[simp] theorem normalise_nil (G : EdgeCol V k) (c : Fin k) :
    normalise G c [] = G := rfl

@[simp] theorem normalise_cons (G : EdgeCol V k) (c : Fin k) (e : V × V)
    (es : List (V × V)) :
    normalise G c (e :: es) = normalise (step G c e) c es := rfl

theorem preservesColour_normalise (G : EdgeCol V k) (c : Fin k) (es : List (V × V)) :
    PreservesColour G (normalise G c es) c := by
  induction es generalizing G with
  | nil => intro x y hxy; exact hxy
  | cons e es ih =>
    intro x y hxy
    exact ih (step G c e) x y (preservesColour_step G c e x y hxy)

theorem triangleFree_normalise (G : EdgeCol V k) (c : Fin k) (es : List (V × V))
    (hG : TriangleFree G) : TriangleFree (normalise G c es) := by
  induction es generalizing G with
  | nil => exact hG
  | cons e es ih => exact ih (step G c e) (triangleFree_step G c e hG)

/-- All previously established normal conditions survive the tail of the run. -/
theorem normalAt_normalise (G : EdgeCol V k) (c : Fin k) (es : List (V × V)) :
    ∀ e ∈ es, NormalAt (normalise G c es) c e := by
  induction es generalizing G with
  | nil => simp
  | cons e es ih =>
    intro f hf
    by_cases hfe : f = e
    · subst f
      exact normalAt_mono (normalAt_step G c e) (preservesColour_normalise (step G c e) c es)
    · exact ih (step G c e) f ((List.mem_cons.mp hf).resolve_left hfe)

theorem normalise_apply_of_not_mem (G : EdgeCol V k) (c : Fin k) {es : List (V × V)}
    {x y : V} (hxy : ∀ e ∈ es, ¬ OnEdge e x y) :
    (normalise G c es).col x y = G.col x y := by
  induction es generalizing G with
  | nil => rfl
  | cons e es ih =>
    calc
      (normalise G c (e :: es)).col x y = (step G c e).col x y :=
        ih (step G c e) (fun f hf => hxy f (List.mem_cons_of_mem e hf))
      _ = G.col x y := step_apply_of_not_onEdge G c (hxy e List.mem_cons_self)

/-- A non-host suffix can use arbitrary retained auxiliary information, but its
physical part may depend only on entries outside the configurable edge list. -/
def OutsideDependent (es : List (V × V)) (S : EdgeCol V k → Prop) : Prop :=
  ∀ G H, (∀ x y, (∀ e ∈ es, ¬ OnEdge e x y) → H.col x y = G.col x y) → S G → S H

theorem normalise_suffix (G : EdgeCol V k) (c : Fin k) (es : List (V × V))
    {S : EdgeCol V k → Prop} (hS : OutsideDependent es S) (hs : S G) :
    S (normalise G c es) := by
  exact hS G (normalise G c es)
    (fun x y hxy => normalise_apply_of_not_mem G c hxy) hs

/-- Physical existence before and after imposing the configurable normal form.
The backward implication is immediate; the forward implication is the explicit
normalising construction above. -/
theorem normalForm_equisatisfiable (c : Fin k) (es : List (V × V))
    (S : EdgeCol V k → Prop) (hS : OutsideDependent es S) :
    (∃ G, TriangleFree G ∧ S G) ↔
      (∃ G, TriangleFree G ∧ S G ∧ ∀ e ∈ es, NormalAt G c e) := by
  constructor
  · rintro ⟨G, hG, hs⟩
    exact ⟨normalise G c es, triangleFree_normalise G c es hG,
      normalise_suffix G c es hS hs, normalAt_normalise G c es⟩
  · rintro ⟨G, hG, hs, _⟩
    exact ⟨G, hG, hs⟩

/-- Satisfaction of the three clauses `¬y∨left`, `¬y∨right`, and
`y∨¬left∨¬right`. -/
def WitnessBinding (left right y : Bool) : Prop :=
  (y = true → left = true) ∧ (y = true → right = true) ∧
    (left = true ∧ right = true → y = true)

theorem witnessBinding_iff (left right y : Bool) : WitnessBinding left right y ↔
    (y = true ↔ left = true ∧ right = true) := by
  constructor
  · rintro ⟨hl, hr, hlr⟩
    exact ⟨fun hy => ⟨hl hy, hr hy⟩, hlr⟩
  · intro h
    exact ⟨fun hy => (h.mp hy).1, fun hy => (h.mp hy).2, h.mpr⟩

/-- Exact Boolean content of the fresh-witness binding and long normal-form
clause.  Take `W` to be the subtype of vertices distinct from both endpoints. -/
theorem fresh_witness_disjunction {W : Sort*} (xuv : Bool)
    (left right y : W → Bool)
    (hy : ∀ w, WitnessBinding (left w) (right w) (y w)) :
    (xuv = true ∨ ∃ w, y w = true) ↔
      (xuv = true ∨ ∃ w, left w = true ∧ right w = true) := by
  simp only [witnessBinding_iff] at hy
  simp only [hy]

end K58.ConfigurableMaximal
