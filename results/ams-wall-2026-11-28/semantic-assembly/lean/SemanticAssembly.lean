import K58.EncoderExtensions

/-!
Compositional semantic assembly for the guarded-counter/support encoding.

The existing gadget theorems extend one valuation at a time.  This module adds
(a) the generator's actual support-clause order and active-position filter,
(b) fresh guard assignment fused with a guarded native counter, and
(c) a general chain theorem preserving every earlier clause family.  It makes
no claim that any physical colouring hypothesis is already proved.
-/
set_option autoImplicit false
namespace K58.SemanticAssembly

open K58
open K58.SequentialCounter
open K58.EncoderExtensions

/-- Every variable occurring in `F` is at most `top`. -/
def VarsBelow (F : CNF) (top : Nat) : Prop :=
  ∀ c ∈ F, ∀ l ∈ c, l.2 ≤ top

theorem formulaSat_preserved (v w : Valuation) (F : CNF) (top : Nat)
    (hb : VarsBelow F top) (he : ∀ a ≤ top, w a = v a)
    (hs : FormulaSat v F) : FormulaSat w F := by
  apply formulaSat_congr_below v w F (top + 1)
  · intro c hc l hl
    exact Nat.lt_succ_of_le (hb c hc l hl)
  · intro a ha
    exact he a (Nat.le_of_lt_succ ha)
  · exact hs

/-- Exactly one target family's clause order in `support_tables.py`: active
selector implications first, then the guarded selector disjunction. -/
def emittedSupportImplications (n : Nat) (x : Nat → Nat) (s : Nat)
    (p : Nat → Bool) (active : Nat → Bool) : CNF :=
  ((List.range n).filter active).map (fun j => [(false, s), (p j, x j)])

def emittedSupportFamilyCNF (g n k : Nat) (x : Nat → Nat) (sel : Fin k → Nat)
    (allowed : Fin k → Nat → Bool) (active : Nat → Bool) : CNF :=
  (List.finRange k).flatMap
      (fun i => emittedSupportImplications n x (sel i) (allowed i) active) ++
    [((false, g) :: (List.finRange k).map (fun i => (true, sel i)))]

/-- The full support formula satisfies the emitted active subset, despite the
main disjunction moving from the front to the back. -/
theorem formulaSat_emittedSupport_of_full
    (w : Valuation) (g n k : Nat) (x : Nat → Nat) (sel : Fin k → Nat)
    (allowed : Fin k → Nat → Bool) (active : Nat → Bool)
    (hs : FormulaSat w (supportFamilyCNF g n k x sel allowed)) :
    FormulaSat w (emittedSupportFamilyCNF g n k x sel allowed active) := by
  intro c hc
  unfold emittedSupportFamilyCNF at hc
  rcases List.mem_append.mp hc with himp | hmain
  · obtain ⟨i, hi, hc⟩ := List.mem_flatMap.mp himp
    obtain ⟨j, hj, rfl⟩ := List.mem_map.mp hc
    apply hs
    unfold supportFamilyCNF
    apply List.mem_append.mpr
    right
    apply List.mem_flatMap.mpr
    refine ⟨i, hi, ?_⟩
    apply List.mem_map.mpr
    refine ⟨j, (List.mem_filter.mp hj).1, rfl⟩
  · have hc : c = ((false, g) :: (List.finRange k).map (fun i => (true, sel i))) :=
      List.mem_singleton.mp hmain
    subst c
    apply hs
    unfold supportFamilyCNF
    apply List.mem_append.mpr
    left
    simp

/-- Encoding adequacy for the exact emitted support clause order/subset. -/
theorem satisfiable_emittedSupportFamily
    (v : Valuation) (g n k top : Nat) (x : Nat → Nat) (sel : Fin k → Nat)
    (allowed : Fin k → Nat → Bool) (active : Nat → Bool)
    (hg : g ≤ top)
    (inputs_below : ∀ j < n, x j ≤ top)
    (fresh : ∀ i, top < sel i)
    (hinj : Function.Injective sel)
    (hguard : v g = true → ∃ i, ∀ j < n, v (x j) = allowed i j) :
    ∃ w : Valuation, (∀ a ≤ top, w a = v a) ∧
      FormulaSat w (emittedSupportFamilyCNF g n k x sel allowed active) := by
  obtain ⟨w, hagree, hs⟩ := satisfiable_supportFamily v g n k top x sel allowed
    hg inputs_below fresh hinj hguard
  exact ⟨w, hagree, formulaSat_emittedSupport_of_full w g n k x sel allowed active hs⟩

/-- Flipping signs does not change variable bounds. -/
theorem flipWhere_varsBelow (p : Nat → Bool) (F : CNF) (top : Nat)
    (h : VarsBelow F top) : VarsBelow (flipWhereCNF p F) top := by
  intro c hc l hl
  obtain ⟨c', hc', rfl⟩ := List.mem_map.mp hc
  obtain ⟨l', hl', rfl⟩ := List.mem_map.mp hl
  by_cases hp : p l'.2 <;> simp [flipWhereLit, hp, h c' hc' l' hl']

theorem top_le_finalTop (n k top : Nat) : top ≤ finalTop n k top := by
  unfold finalTop
  split_ifs <;> omega

/-- The native counter's complete bound is its already-computed `finalTop`. -/
theorem nativeAtLeast_varsBelow (x : Nat → Nat) (n bound top : Nat)
    (inputs : ∀ i < n, x i ≤ top) :
    VarsBelow (nativeAtLeastCNF x n bound top) (finalTop n (n - bound) top) := by
  unfold nativeAtLeastCNF
  apply flipWhere_varsBelow
  intro c hc l hl
  exact counter_atoms_le x n (n - bound) top inputs c hc l hl

/-- Guarding a native counter adds only the already bounded guard. -/
theorem guardedAtLeast_varsBelow (g : Nat) (x : Nat → Nat) (n bound top : Nat)
    (hg : g ≤ top) (inputs : ∀ i < n, x i ≤ top) :
    VarsBelow (guardedAtLeastCNF g x n bound top) (finalTop n (n - bound) top) := by
  intro c hc l hl
  unfold guardedAtLeastCNF prependGuard at hc
  obtain ⟨c', hc', rfl⟩ := List.mem_map.mp hc
  simp only [List.mem_cons] at hl
  rcases hl with rfl | hl
  · exact le_trans hg (top_le_finalTop n (n - bound) top)
  · exact nativeAtLeast_varsBelow x n bound top inputs c' hc' l hl

/-- Bound an emitted support family from separate input/selector/guard bounds. -/
theorem emittedSupport_varsBelow (g n k oldTop newTop : Nat) (x : Nat → Nat)
    (sel : Fin k → Nat) (allowed : Fin k → Nat → Bool) (active : Nat → Bool)
    (hg : g ≤ oldTop) (hnew : oldTop ≤ newTop)
    (inputs : ∀ j < n, x j ≤ oldTop) (selectors : ∀ i, sel i ≤ newTop) :
    VarsBelow (emittedSupportFamilyCNF g n k x sel allowed active) newTop := by
  intro c hc l hl
  unfold emittedSupportFamilyCNF at hc
  rcases List.mem_append.mp hc with himp | hmain
  · obtain ⟨i, hi, hc⟩ := List.mem_flatMap.mp himp
    obtain ⟨j, hj, rfl⟩ := List.mem_map.mp hc
    have hjn : j < n := List.mem_range.mp (List.mem_filter.mp hj).1
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hl
    rcases hl with rfl | rfl
    · exact selectors i
    · exact le_trans (inputs j hjn) hnew
  · have hc : c = ((false, g) :: (List.finRange k).map (fun i => (true, sel i))) :=
      List.mem_singleton.mp hmain
    subst c
    simp only [List.mem_cons] at hl
    rcases hl with rfl | hl
    · exact le_trans hg hnew
    · obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hl
      exact selectors i

/-- One linked extension item.  `ready` may inspect the valuation produced by
all previous items; `extend` must preserve every variable at or below `oldTop`. -/
structure ExtensionStep where
  oldTop : Nat
  newTop : Nat
  clauses : CNF
  ready : Valuation → Prop
  old_le : oldTop ≤ newTop
  bounded : VarsBelow clauses newTop
  extend : ∀ v : Valuation, ready v →
    ∃ w : Valuation, (∀ a ≤ oldTop, w a = v a) ∧ FormulaSat w clauses

/-- Readiness after the actual, sequentially constructed prefixes. -/
def ChainReady (top : Nat) (v : Valuation) : List ExtensionStep → Prop
  | [] => True
  | s :: ss =>
      s.oldTop = top ∧ s.ready v ∧
        ∀ w : Valuation, (∀ a ≤ top, w a = v a) → FormulaSat w s.clauses →
          ChainReady s.newTop w ss

/-- Build one valuation for a whole linked family list.  Earlier clauses remain
satisfied because later extensions preserve their complete variable range. -/
theorem chain_extend (steps : List ExtensionStep) :
    ∀ (top : Nat) (v : Valuation), ChainReady top v steps →
      ∃ w : Valuation, (∀ a ≤ top, w a = v a) ∧
        FormulaSat w (steps.flatMap ExtensionStep.clauses) := by
  induction steps with
  | nil =>
      intro top v _
      exact ⟨v, fun _ _ => rfl, by simp [FormulaSat]⟩
  | cons s ss ih =>
      intro top v h
      obtain ⟨hlink, hready, htail⟩ := h
      obtain ⟨w, hw, hs⟩ := s.extend v hready
      have hw' : ∀ a ≤ top, w a = v a := by
        intro a ha
        exact hw a (by omega)
      obtain ⟨z, hz, hzs⟩ := ih s.newTop w (htail w hw' hs)
      refine ⟨z, ?_, ?_⟩
      · intro a ha
        calc
          z a = w a := hz a (by have := s.old_le; omega)
          _ = v a := hw' a ha
      · change FormulaSat z (s.clauses ++ ss.flatMap ExtensionStep.clauses)
        apply (formulaSat_append z s.clauses _).mpr
        refine ⟨?_, hzs⟩
        exact formulaSat_preserved w z s.clauses s.newTop s.bounded hz hs

/-- Set one fresh variable, without changing any older variable. -/
def setValue (v : Valuation) (g : Nat) (b : Bool) : Valuation :=
  fun a => if a = g then b else v a

/-- Fuse the generator's allocation `guard := oldTop + 1` with its guarded
native counter.  The guard is set to the exact semantic at-least predicate, so
this step is unconditionally ready. -/
def freshGuardedCounterStep (oldTop g n bound newTop : Nat) (x : Nat → Nat)
    (hg : oldTop < g) (hnew : g ≤ newTop)
    (inputs_below : ∀ i < n, x i ≤ oldTop)
    (hb : VarsBelow (guardedAtLeastCNF g x n bound g) newTop) : ExtensionStep where
  oldTop := oldTop
  newTop := newTop
  clauses := guardedAtLeastCNF g x n bound g
  ready := fun _ => True
  old_le := by omega
  bounded := hb
  extend := by
    intro v _
    let b : Bool := decide (bound ≤ prefixCount (fun i => v (x i)) n)
    let v0 : Valuation := setValue v g b
    have hv0g : v0 g = b := by simp [v0, setValue]
    have hguard : v0 g = true → bound ≤ prefixCount (fun i => v (x i)) n := by
      intro ht
      have hb : b = true := by rw [← hv0g]; exact ht
      have hd : decide (bound ≤ prefixCount (fun i => v (x i)) n) = true := by
        simpa [b] using hb
      exact of_decide_eq_true hd
    have hinputs : ∀ i < n, v0 (x i) = v (x i) := by
      intro i hi
      have hxi : x i ≠ g := by have := inputs_below i hi; omega
      simp [v0, setValue, hxi]
    have hcount : prefixCount (fun i => v0 (x i)) n =
        prefixCount (fun i => v (x i)) n :=
      prefixCount_congr_of_lt _ _ n hinputs
    have hguard0 : v0 g = true → bound ≤ prefixCount (fun i => v0 (x i)) n := by
      intro ht
      rw [hcount]
      exact hguard ht
    obtain ⟨w, hagree, hs⟩ := satisfiable_guardedAtLeast v0 g x n bound g
      le_rfl (fun i hi => le_trans (inputs_below i hi) (Nat.le_of_lt hg)) hguard0
    refine ⟨w, ?_, hs⟩
    intro a ha
    calc
      w a = v0 a := hagree a (by omega)
      _ = v a := by simp [v0, setValue, show a ≠ g by omega]

/-- Same fresh-guarded step with its bound discharged by `finalTop`. -/
def freshGuardedCounterStepAuto (oldTop g n bound newTop : Nat) (x : Nat → Nat)
    (hg : oldTop < g) (hfinal : finalTop n (n - bound) g ≤ newTop)
    (inputs_below : ∀ i < n, x i ≤ oldTop) : ExtensionStep :=
  freshGuardedCounterStep oldTop g n bound newTop x hg
    (le_trans (top_le_finalTop n (n - bound) g) hfinal) inputs_below
    (fun c hc l hl => le_trans
      (guardedAtLeast_varsBelow g x n bound g le_rfl
        (fun i hi => le_trans (inputs_below i hi) (Nat.le_of_lt hg)) c hc l hl) hfinal)

/-- A native unguarded at-least counter, used for the selected-arm and total
critical requirements after all their input guards have been assigned. -/
def nativeCounterStep (oldTop n bound newTop : Nat) (x : Nat → Nat)
    (hnew : oldTop ≤ newTop)
    (inputs_below : ∀ i < n, x i ≤ oldTop)
    (hb : VarsBelow (nativeAtLeastCNF x n bound oldTop) newTop) : ExtensionStep where
  oldTop := oldTop
  newTop := newTop
  clauses := nativeAtLeastCNF x n bound oldTop
  ready := fun v => bound ≤ prefixCount (fun i => v (x i)) n
  old_le := hnew
  bounded := hb
  extend := by
    intro v hcount
    exact satisfiable_nativeAtLeast v x n bound oldTop inputs_below hcount

/-- Same native step with its bound discharged by `finalTop`. -/
def nativeCounterStepAuto (oldTop n bound newTop : Nat) (x : Nat → Nat)
    (hfinal : finalTop n (n - bound) oldTop ≤ newTop)
    (inputs_below : ∀ i < n, x i ≤ oldTop) : ExtensionStep :=
  nativeCounterStep oldTop n bound newTop x
    (le_trans (top_le_finalTop n (n - bound) oldTop) hfinal) inputs_below
    (fun c hc l hl => le_trans
      (nativeAtLeast_varsBelow x n bound oldTop inputs_below c hc l hl) hfinal)

/-- A support item placed after its counter.  Its readiness is exactly the
physical implication that a true guard has an allowed P4/C5 support. -/
def emittedSupportStep (oldTop g n k newTop : Nat) (x : Nat → Nat)
    (sel : Fin k → Nat) (allowed : Fin k → Nat → Bool) (active : Nat → Bool)
    (hg : g ≤ oldTop) (hnew : oldTop ≤ newTop)
    (inputs_below : ∀ j < n, x j ≤ oldTop)
    (fresh : ∀ i, oldTop < sel i) (hinj : Function.Injective sel)
    (hb : VarsBelow (emittedSupportFamilyCNF g n k x sel allowed active) newTop) :
    ExtensionStep where
  oldTop := oldTop
  newTop := newTop
  clauses := emittedSupportFamilyCNF g n k x sel allowed active
  ready := fun v => v g = true → ∃ i, ∀ j < n, v (x j) = allowed i j
  old_le := hnew
  bounded := hb
  extend := by
    intro v hguard
    exact satisfiable_emittedSupportFamily v g n k oldTop x sel allowed active
      hg inputs_below fresh hinj hguard

#print axioms K58.SemanticAssembly.satisfiable_emittedSupportFamily
#print axioms K58.SemanticAssembly.chain_extend
#print axioms K58.SemanticAssembly.freshGuardedCounterStep

end K58.SemanticAssembly
