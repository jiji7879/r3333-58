/-
K58 R3, direction C (swarm smx0gue0b, member m7): clause-level audit of the
41-atom decoder, senders 18..32.

`K58.R3Counter.counterAtoms` reads the emitted counter's 41 atoms as the
colour-1 host edges `(1+j, 18+k)` (j<16) and `(18+k, 33+i)` (i<25).  Here that
reading is checked against the emitted clause set itself: the variables at or
below each counter's own `oldTop` occurring in the emitted
`freshGuardedCounterStepAuto ... 41 14 ...` clauses are exactly those 41 atoms.

Each `decide` is a full kernel re-evaluation of one emitted counter CNF
(743 clauses, 2593 literals), ~15 s and ~4.5 GB peak, so the fifteen are split
into three files to keep one elaboration cheap.  No sorry, no native_decide,
no new axiom.
-/
import K58.CounterNeighboursAudit1

open K58
open K58.SenderReady
open K58.SemanticAssembly
open K58.SequentialCounter
open K58.EmittedBridge

set_option autoImplicit false

namespace K58.R3Counter

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `28`: the clauses read exactly the decoded atoms. -/
theorem audit_10 :
    inputAtomsOf (counterCNF ⟨10, by decide⟩) (rowOldTop ⟨10, by decide⟩ - 379) =
      (counterList ⟨10, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `29`: the clauses read exactly the decoded atoms. -/
theorem audit_11 :
    inputAtomsOf (counterCNF ⟨11, by decide⟩) (rowOldTop ⟨11, by decide⟩ - 379) =
      (counterList ⟨11, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `30`: the clauses read exactly the decoded atoms. -/
theorem audit_12 :
    inputAtomsOf (counterCNF ⟨12, by decide⟩) (rowOldTop ⟨12, by decide⟩ - 379) =
      (counterList ⟨12, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `31`: the clauses read exactly the decoded atoms. -/
theorem audit_13 :
    inputAtomsOf (counterCNF ⟨13, by decide⟩) (rowOldTop ⟨13, by decide⟩ - 379) =
      (counterList ⟨13, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `32`: the clauses read exactly the decoded atoms. -/
theorem audit_14 :
    inputAtomsOf (counterCNF ⟨14, by decide⟩) (rowOldTop ⟨14, by decide⟩ - 379) =
      (counterList ⟨14, by decide⟩).insertionSort (· ≤ ·) := by
  decide

/-! ## The audit for all fifteen senders -/

/-- **Clause-level audit of the decoder.**  For every sender `18+k` (`k : Fin 15`)
the emitted 41-of-14 counter clause set reads exactly the decoded forty-one
atoms at or below its own `oldTop`. -/
theorem counter_inputs_audit (k : Fin 15) :
    inputAtomsOf (counterCNF k) (rowOldTop k - 379) =
      (counterList k).insertionSort (· ≤ ·) := by
  fin_cases k
  · exact audit_0
  · exact audit_1
  · exact audit_2
  · exact audit_3
  · exact audit_4
  · exact audit_5
  · exact audit_6
  · exact audit_7
  · exact audit_8
  · exact audit_9
  · exact audit_10
  · exact audit_11
  · exact audit_12
  · exact audit_13
  · exact audit_14

#print axioms K58.R3Counter.counter_inputs_audit

end K58.R3Counter
