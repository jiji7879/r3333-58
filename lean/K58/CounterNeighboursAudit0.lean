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
import K58.CounterNeighbours

open K58
open K58.SenderReady
open K58.SemanticAssembly
open K58.SequentialCounter
open K58.EmittedBridge

set_option autoImplicit false

namespace K58.R3Counter

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `18`: the clauses read exactly the decoded atoms. -/
theorem audit_0 :
    inputAtomsOf (counterCNF ⟨0, by decide⟩) (rowOldTop ⟨0, by decide⟩ - 379) =
      (counterList ⟨0, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `19`: the clauses read exactly the decoded atoms. -/
theorem audit_1 :
    inputAtomsOf (counterCNF ⟨1, by decide⟩) (rowOldTop ⟨1, by decide⟩ - 379) =
      (counterList ⟨1, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `20`: the clauses read exactly the decoded atoms. -/
theorem audit_2 :
    inputAtomsOf (counterCNF ⟨2, by decide⟩) (rowOldTop ⟨2, by decide⟩ - 379) =
      (counterList ⟨2, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `21`: the clauses read exactly the decoded atoms. -/
theorem audit_3 :
    inputAtomsOf (counterCNF ⟨3, by decide⟩) (rowOldTop ⟨3, by decide⟩ - 379) =
      (counterList ⟨3, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `22`: the clauses read exactly the decoded atoms. -/
theorem audit_4 :
    inputAtomsOf (counterCNF ⟨4, by decide⟩) (rowOldTop ⟨4, by decide⟩ - 379) =
      (counterList ⟨4, by decide⟩).insertionSort (· ≤ ·) := by
  decide

end K58.R3Counter
