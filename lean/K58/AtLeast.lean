import K58.SequentialCounter

/-!
# The at-least encoding, exactly as PySAT emits it

`CardEnc.atleast(lits, bound)` with the default encoding is the staggered
sequential *at-most* counter applied to the negated literals: verified
clause-for-clause against `SequentialCounter.counter` for every `n ≤ 9` and
every bound.  This file records that identification and transports the
constructor's adequacy lemma across the polarity flip, which is the direction
`dense.marked_threshold` needs.

Flip a literal's polarity.
-/
set_option autoImplicit false
namespace K58.SequentialCounter
open K58

/-- The same clause with every literal's polarity reversed. -/
def flipLit (l : Literal) : Literal := (!l.1, l.2)

def flipClause (c : List Literal) : List Literal := c.map flipLit

def flipCNF (F : CNF) : CNF := F.map flipClause

theorem prefixCount_le (b : Nat → Bool) (n : Nat) : prefixCount b n ≤ n := by
  induction n with
  | zero => simp [prefixCount]
  | succ n ih => rw [prefixCount]; cases b n <;> simp <;> omega

theorem prefixCount_neg (b : Nat → Bool) (n : Nat) :
    prefixCount (fun i => !b i) n + prefixCount b n = n := by
  induction n with
  | zero => simp [prefixCount]
  | succ n ih =>
    rw [prefixCount, prefixCount]
    generalize b n = bn
    cases bn <;> simp_all <;> omega

theorem clauseSat_flip (v : Valuation) (c : List Literal) :
    ClauseSat v c → ClauseSat (!v ·) (flipClause c) := by
  rintro ⟨l, hl, h⟩
  refine ⟨flipLit l, List.mem_map_of_mem hl, ?_⟩
  simp only [flipLit]
  rw [← h]

theorem formulaSat_flip (v : Valuation) (F : CNF) :
    FormulaSat v F → FormulaSat (!v ·) (flipCNF F) := by
  intro h c hc
  obtain ⟨c', hc', rfl⟩ := List.mem_map.mp hc
  exact clauseSat_flip v c' (h c' hc')

/-- PySAT's `atleast` clause set: the at-most counter on the negations. -/
def atLeastCNF (x : Nat → Nat) (n bound top : Nat) : CNF :=
  flipCNF (counter x n (n - bound) top)

/-- **Encoding adequacy for at-least.**  If at least `bound` of the atoms
`x 0 … x (n-1)` are true, the counter cells can be filled so that every
`atleast` clause holds, leaving the atoms untouched. -/
theorem satisfiable_atLeast (v : Valuation) (x : Nat → Nat) (n bound top : Nat)
    (inputs_below : ∀ i < n, x i ≤ top)
    (hcount : bound ≤ prefixCount (fun i => v (x i)) n) :
    ∃ w : Valuation, (∀ a ≤ top, w a = v a) ∧ FormulaSat w (atLeastCNF x n bound top) := by
  have hcomp : prefixCount (fun i => !v (x i)) n + prefixCount (fun i => v (x i)) n = n :=
    prefixCount_neg (fun i => v (x i)) n
  have hb : prefixCount (fun i => !v (x i)) n ≤ n - bound := by omega
  obtain ⟨w', hw'agree, hw'sat⟩ :=
    satisfiable_extension (fun y => !v y) x n (n - bound) top inputs_below hb
  refine ⟨(fun a => Bool.not (w' a)), ?_, ?_⟩
  · intro a ha
    show Bool.not (w' a) = v a
    rw [hw'agree a ha]
    cases v a <;> rfl
  · exact formulaSat_flip w' _ hw'sat

end K58.SequentialCounter
