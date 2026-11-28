# R3 proof and ledger status

**Status — PROVED #18. The argument was checked by: lean, model.** The gate
additionally records an independent finite computation. This settles all-sender
R3 at the physical valuation. It does not settle sequential `ChainReady`, any
wall profile, or a new Ramsey bound. The accepted interval is still
$51\le R_4(3)\le62$.

## Established result

For every `k : Fin 15`, sender `18+k`, the actual forty-one emitted counter
atoms have a coordinate decoding to distinct non-sender, non-root labels. From

```lean
14 <= prefixCount
  (fun i => realizedValuation G e p (emittedCounterAtoms k i)) 41
```

with `e (senderFin k) = q`, `e zeroFin = r`, `p one = 1`, the appropriate root
pinning/coherence and `TriangleFree G`, the theorem
`K58.R3Counter.emitted_sender_step_ready_of_emitted_count_classified` proves
the emitted sender's support step ready at `realizedValuation G e p`.
No separate `W`, membership/root/cardinality hypotheses, or `hclass` argument
is required. Those are constructed or discharged by the proof, not hidden in a
shortened premise list.

The theorem is not a proof of numerical count ⇒ abstract support-catalogue
membership. Physical colour-1 incidence and the actual template geometry sit
between them exactly as intended.

## Argument

1. The raw 15×41 input list is decoded into genuine coloured host edges. Each
   sender has sixteen labels `1 … 16` and twenty-five labels `33 … 57`,
   excluding the sender and root. These labels are injective.
2. Actual emitted clauses, selected by each counter's own allocation, are
   reread with `inputAtomsOf`. `counter_inputs_audit` checks all fifteen
   individually against precisely those decoded atoms, up to sorting.
3. The true Boolean positions form a finite index set; the image under the
   injective endpoint/host-permutation map is `W`. Its size equals the full
   `prefixCount`, so at least 14 vertices contribute.
4. `realizedValuation_hostVar_unsorted`, `p one = 1`, and injectivity turn true
   atoms into actual nonloop colour-1 neighbours. Root label avoidance gives
   `r ∉ W`. No diagonal/dummy-colour assumption is used.
5. The root edge adds the fifteenth distinct neighbour, whereupon
   `deg_le_sixteen` (using `TriangleFree`) confines the sender arm to order
   fifteen or sixteen. The real imported classifications plus template palette
   symmetries provide the literal-colour `PinnedArm` hypothesis.
6. `SupportTransport.support_mask_mem` and the exact emitted coordinate map
   finally return the support step's catalogue predicate at that valuation.

Lean sources: `lean/K58/CounterNeighbours.lean`, the three split
`CounterNeighboursAudit*.lean` modules, `ClassifiedBridge.lean`, and
`CountedSenderReady.lean`. `K58.Check.lean` and `lean/order.txt` integrate the
library. The clean consolidated proof source is `checks/17-proof.md`.

## Checks and exact scope

- `bash lean/build.sh` (job `jmx0hmr7s`) exited **0 in 281.39 s**; maximum RSS
  **6,782,744 KiB**. All fifteen counters' input sets were elaborated and
  checked. `checks/root-build.log` is the complete retained output.
- Across it and m3/m5 independent checks, **501** `depends on axioms` outputs
  were scanned: all were within `propext`, `Classical.choice`, `Quot.sound`.
  There is no `sorryAx`, `native_decide`, custom axiom or proof artifact used
  as a mathematical axiom.
- `checks/17-model.md` is the independent statement audit of the delegate's
  construction. It confirms quantifier range, root/coordinate obligations,
  physical orientation and catalogue-consumer type, with no gap found.
- `checks/17-compute.md` records a separate host-rank decoder reproduction: all
  fifteen rows have 41 correct atoms, correct guard allocation and correct
  first-sixteen support prefix. The literal table matches digit for digit.
- Six directions were checked and accepted within their proper scopes: m8
  generic/sender-18 count-to-W, m4 literal-colour classification, m6
  count-driven sender-18 readiness, m7's audited all-sender decoder, and m3/m5
  control and aggregation interfaces. These are six useful components, not six
  unrelated solutions to the whole program. m3's witnesses do not include a
  triangle-free K58; m5's counterexample shows only why pointwise readiness
  does not imply `ChainReady`. The accepted count does not assert that every
  direction succeeded. m7's all-sender construction was kernel-replayed in
  production, including its fifteen exact input audits.

An initial monolithic audit was stopped for time; it is not counted as a
successful check. A preliminary ledger entry was replaced only to stop citing a
later sequential obligation as if it were a premise. No Lean statement or
mathematical argument was weakened in that bookkeeping correction.

## Remaining obligations

These are open follow-up obligations, not hypotheses hidden in the delivered
R3 theorem.

1. At every counter-model valuation, demonstrate `guard = true →
   14 ≤ prefixCount`. For `guardedAtLeastCNF`, reverse soundness of the staggered
   sequential counter is the mathematical requirement; count-to-satisfiability
   alone gives the other direction, and the fresh extension's guard assignment
   does not discharge all models quantified by `ChainReady`.
2. Transport physical readiness to those models, identify abstract sender-step
   descriptions with the exact emitted chain positions, and finish sequential
   `ChainReady`.
3. Discharge `expandKey` / `ColourUnit.ofEdge` plan and encoding bookkeeping,
   palette coherence, and the final native `AtLeast(15,6)` / `AtLeast(31,6)`
   guard obligations.

The source includes a conditional count-to-satisfiability theorem in the
member's further experiments; it does not by itself identify every emitted
counter CNF with the expected list and is not used to assert ChainReady here.

## Literature and provenance

No external literature search was needed for this self-contained finite
Boolean/finite-set deduction. The order-15/16 classification, however, is not a
new elementary proof: it is the existing pinned R4333Lean catalogue imported
through `K58.classified_15/16`, whose required literal-colour form is derived
using the existing palette-symmetry theorems. Both report only permitted
standard axioms. Their mathematical scope and literal-colour mismatch were
 checked explicitly, not inferred from an axiom-clean printout.

Artifacts and reviews: `swarm smx0gue0b` (eight members, deepseek model, max
reasoning; bounded Lean directions). The final axiom/statement gate is
`ledger.md` plus `checks/17-*`. Logs are small text records only: no CNF, DRAT,
LRAT, archive or `.olean` is part of this deliverable.
