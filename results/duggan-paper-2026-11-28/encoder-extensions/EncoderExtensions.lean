import K58.AtLeast

/-!
Encoding-extension lemmas for the guarded counters and support selectors in
`dense.marked_threshold` and `support_tables.support_clauses`.

The DIMACS literal `(b, a)` is satisfied when the valuation of `a` is `b`.
No graph theorem is hidden here: the support-shape premise is explicit.
-/
set_option autoImplicit false
namespace K58.EncoderExtensions

open K58
open K58.SequentialCounter

/-- Prefix every clause by the negative guard literal. -/
def prependGuard (g : Nat) (F : CNF) : CNF :=
  F.map (fun c => (false, g) :: c)

theorem formulaSat_prependGuard_of_false (v : Valuation) (g : Nat) (F : CNF)
    (hg : v g = false) : FormulaSat v (prependGuard g F) := by
  intro c hc
  obtain ⟨c', hc', rfl⟩ := List.mem_map.mp hc
  exact ⟨(false, g), by simp, hg⟩

theorem formulaSat_prependGuard_of_formula (v : Valuation) (g : Nat) (F : CNF)
    (hF : FormulaSat v F) : FormulaSat v (prependGuard g F) := by
  intro c hc
  obtain ⟨c', hc', rfl⟩ := List.mem_map.mp hc
  obtain ⟨l, hl, hv⟩ := hF c' hc'
  exact ⟨l, by simp [hl], hv⟩

/-- Complement only variables selected by a Boolean mask, in formulas and
valuations.  This is the transformation PySAT applies to the *inputs* of its
at-least counter; unlike `flipCNF`, it does not complement counter cells. -/
def flipWhereLit (p : Nat → Bool) (l : Literal) : Literal :=
  if p l.2 then (!l.1, l.2) else l

def flipWhereCNF (p : Nat → Bool) (F : CNF) : CNF :=
  F.map (fun c => c.map (flipWhereLit p))

def flipWhereValuation (p : Nat → Bool) (v : Valuation) : Valuation :=
  fun a => if p a then !v a else v a

def inputMask (x : Nat → Nat) (n a : Nat) : Bool :=
  (List.range n).any (fun i => x i == a)

theorem inputMask_self (x : Nat → Nat) (n i : Nat) (hi : i < n) :
    inputMask x n (x i) = true := by
  simp only [inputMask, List.any_eq_true]
  exact ⟨i, List.mem_range.mpr hi, by simp⟩

theorem formulaSat_flipWhere (p : Nat → Bool) (v : Valuation) (F : CNF) :
    FormulaSat v F → FormulaSat (flipWhereValuation p v) (flipWhereCNF p F) := by
  intro hF c hc
  obtain ⟨c', hc', rfl⟩ := List.mem_map.mp hc
  obtain ⟨l, hl, hv⟩ := hF c' hc'
  refine ⟨flipWhereLit p l, List.mem_map_of_mem hl, ?_⟩
  by_cases hp : p l.2
  · simpa [flipWhereLit, flipWhereValuation, hp] using congrArg Bool.not hv
  · simpa [flipWhereLit, flipWhereValuation, hp] using hv

theorem prefixCount_congr_of_lt (b c : Nat → Bool) (n : Nat)
    (h : ∀ i < n, b i = c i) : prefixCount b n = prefixCount c n := by
  induction n with
  | zero => rfl
  | succ n ih =>
      rw [prefixCount, prefixCount, h n (by omega), ih (fun i hi => h i (by omega))]

/-- The native PySAT `CardEnc.atleast` clause family: negate only the inputs of
its at-most sequential counter.  The older `atLeastCNF = flipCNF (counter ...)`
instead negates every cell literal and is not syntactically the emitted CNF. -/
def nativeAtLeastCNF (x : Nat → Nat) (n bound top : Nat) : CNF :=
  flipWhereCNF (inputMask x n) (counter x n (n - bound) top)

/-- Encoding adequacy for the actual native PySAT clause shape. -/
theorem satisfiable_nativeAtLeast
    (v : Valuation) (x : Nat → Nat) (n bound top : Nat)
    (inputs_below : ∀ i < n, x i ≤ top)
    (hcount : bound ≤ prefixCount (fun i => v (x i)) n) :
    ∃ w : Valuation, (∀ a ≤ top, w a = v a) ∧
      FormulaSat w (nativeAtLeastCNF x n bound top) := by
  let p := inputMask x n
  let v0 := flipWhereValuation p v
  have hv0 (i : Nat) (hi : i < n) : v0 (x i) = !v (x i) := by
    simp only [v0, flipWhereValuation, p, inputMask_self x n i hi, if_true]
  have hcomp := prefixCount_neg (fun i => v (x i)) n
  have hb : prefixCount (fun i => v0 (x i)) n ≤ n - bound := by
    rw [prefixCount_congr_of_lt _ _ n hv0]
    omega
  obtain ⟨w', hagree, hsat⟩ := satisfiable_extension v0 x n (n - bound) top
    inputs_below hb
  refine ⟨flipWhereValuation p w', ?_, formulaSat_flipWhere p w' _ hsat⟩
  intro a ha
  by_cases hp : p a <;> simp_all [flipWhereValuation, v0]

/-- The exact clause shape obtained by guarding every native
`CardEnc.atleast` clause. -/
def guardedAtLeastCNF (g : Nat) (x : Nat → Nat) (n bound top : Nat) : CNF :=
  prependGuard g (nativeAtLeastCNF x n bound top)

/-- If the guard is true only when the semantic at-least condition holds, then
all guarded counter clauses can be satisfied without changing the inputs or the
guard.  This covers both the sender and the non-sender cases. -/
theorem satisfiable_guardedAtLeast
    (v : Valuation) (g : Nat) (x : Nat → Nat) (n bound top : Nat)
    (_hg : g ≤ top)
    (inputs_below : ∀ i < n, x i ≤ top)
    (hguard : v g = true → bound ≤ prefixCount (fun i => v (x i)) n) :
    ∃ w : Valuation, (∀ a ≤ top, w a = v a) ∧
      FormulaSat w (guardedAtLeastCNF g x n bound top) := by
  cases hgv : v g with
  | false =>
      exact ⟨v, fun _ _ => rfl, formulaSat_prependGuard_of_false v g _ hgv⟩
  | true =>
      obtain ⟨w, hagree, hsat⟩ := satisfiable_nativeAtLeast v x n bound top
        inputs_below (hguard hgv)
      exact ⟨w, hagree, formulaSat_prependGuard_of_formula w g _ hsat⟩

/-- A selector asserts the complete characteristic function `p` on `n` atoms.
The real generator omits implications for already pinned atoms; proving the
full family is stronger and covers the emitted subset. -/
def supportImplications (n : Nat) (x : Nat → Nat) (s : Nat) (p : Nat → Bool) : CNF :=
  (List.range n).map (fun j => [(false, s), (p j, x j)])

/-- One disjunction over support selectors plus each selector's implications. -/
def supportFamilyCNF (g n k : Nat) (x : Nat → Nat) (sel : Fin k → Nat)
    (allowed : Fin k → Nat → Bool) : CNF :=
  [((false, g) :: (List.finRange k).map (fun i => (true, sel i)))] ++
    (List.finRange k).flatMap (fun i => supportImplications n x (sel i) (allowed i))

/-- Keep every non-selector value, make the chosen selector true (if any), and
make every other selector false. -/
noncomputable def selectorExtension (v : Valuation) {k : Nat} (sel : Fin k → Nat)
    (chosen : Option (Fin k)) : Valuation :=
  fun a => if h : ∃ i, sel i = a then
    if chosen = some (Classical.choose h) then true else false
  else v a

theorem selectorExtension_not (v : Valuation) {k : Nat} (sel : Fin k → Nat)
    (chosen : Option (Fin k)) (a : Nat) (ha : ¬ ∃ i, sel i = a) :
    selectorExtension v sel chosen a = v a := by
  simp [selectorExtension, ha]

theorem selectorExtension_sel (v : Valuation) {k : Nat} (sel : Fin k → Nat)
    (hinj : Function.Injective sel) (chosen : Option (Fin k)) (i : Fin k) :
    selectorExtension v sel chosen (sel i) =
      if chosen = some i then true else false := by
  unfold selectorExtension
  split
  · rename_i h
    have hc : Classical.choose h = i := hinj (Classical.choose_spec h)
    rw [hc]
  · rename_i h
    exact False.elim (h ⟨i, rfl⟩)

theorem selectorExtension_agree (v : Valuation) {k : Nat} (sel : Fin k → Nat)
    (chosen : Option (Fin k)) (top : Nat) (fresh : ∀ i, top < sel i)
    (a : Nat) (ha : a ≤ top) : selectorExtension v sel chosen a = v a := by
  apply selectorExtension_not
  rintro ⟨i, hi⟩
  have h := fresh i
  omega

/-- Encoding adequacy of the guarded support table.  If the guard is false no
support is required.  If it is true, the physical support must equal one of the
listed allowed supports; exactly that selector is then selected. -/
theorem satisfiable_supportFamily
    (v : Valuation) (g n k top : Nat) (x : Nat → Nat) (sel : Fin k → Nat)
    (allowed : Fin k → Nat → Bool)
    (hg : g ≤ top)
    (inputs_below : ∀ j < n, x j ≤ top)
    (fresh : ∀ i, top < sel i)
    (hinj : Function.Injective sel)
    (hguard : v g = true → ∃ i, ∀ j < n, v (x j) = allowed i j) :
    ∃ w : Valuation, (∀ a ≤ top, w a = v a) ∧
      FormulaSat w (supportFamilyCNF g n k x sel allowed) := by
  cases hgv : v g with
  | false =>
      let chosen : Option (Fin k) := none
      let w := selectorExtension v sel chosen
      have hagree : ∀ a ≤ top, w a = v a :=
        selectorExtension_agree v sel chosen top fresh
      refine ⟨w, hagree, ?_⟩
      intro c hc
      obtain hmain | hall := List.mem_append.mp hc
      · have hc : c = (false, g) :: (List.finRange k).map (fun i => (true, sel i)) :=
          List.mem_singleton.mp hmain
        subst c
        exact ⟨(false, g), by simp, (hagree g hg).trans hgv⟩
      · obtain ⟨i, hi, hc⟩ := List.mem_flatMap.mp hall
        obtain ⟨j, hj, rfl⟩ := List.mem_map.mp hc
        refine ⟨(false, sel i), by simp, ?_⟩
        change selectorExtension v sel chosen (sel i) = false
        rw [selectorExtension_sel v sel hinj chosen i]
        simp [chosen]
  | true =>
      obtain ⟨i, hsupport⟩ := hguard hgv
      let chosen : Option (Fin k) := some i
      let w := selectorExtension v sel chosen
      have hagree : ∀ a ≤ top, w a = v a :=
        selectorExtension_agree v sel chosen top fresh
      refine ⟨w, hagree, ?_⟩
      intro c hc
      obtain hmain | hall := List.mem_append.mp hc
      · have hc : c = (false, g) :: (List.finRange k).map (fun i => (true, sel i)) :=
          List.mem_singleton.mp hmain
        subst c
        refine ⟨(true, sel i), by simp, ?_⟩
        change selectorExtension v sel chosen (sel i) = true
        rw [selectorExtension_sel v sel hinj chosen i]
        simp [chosen]
      · obtain ⟨i', hi', hc⟩ := List.mem_flatMap.mp hall
        obtain ⟨j, hj, rfl⟩ := List.mem_map.mp hc
        have hjn : j < n := List.mem_range.mp hj
        by_cases hii : i' = i
        · subst i'
          refine ⟨(allowed i j, x j), by simp, ?_⟩
          exact (hagree (x j) (inputs_below j hjn)).trans (hsupport j hjn)
        · refine ⟨(false, sel i'), by simp, ?_⟩
          change selectorExtension v sel chosen (sel i') = false
          rw [selectorExtension_sel v sel hinj chosen i']
          have hii' : i ≠ i' := Ne.symm hii
          simp [chosen, hii']

/-- A tiny kernel-checked witness that the legacy flip-all binding is not the
native PySAT binding.  This is syntactic inequality, not a claim that the two
formulas have different satisfiability after auxiliary renaming. -/
theorem legacy_atLeastCNF_not_native :
    K58.SequentialCounter.atLeastCNF (fun i => i + 1) 3 2 4 ≠
      nativeAtLeastCNF (fun i => i + 1) 3 2 4 := by decide

#print axioms K58.EncoderExtensions.legacy_atLeastCNF_not_native
#print axioms K58.EncoderExtensions.satisfiable_nativeAtLeast
#print axioms K58.EncoderExtensions.satisfiable_guardedAtLeast
#print axioms K58.EncoderExtensions.satisfiable_supportFamily

end K58.EncoderExtensions
