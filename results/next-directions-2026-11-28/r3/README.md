# R3: emitted counter to physical neighbours

**Scope.** This is a finite count/vertex-decoding result for the retained K58
parent. It does not establish a new Ramsey bound, close a wall profile, or
prove `ChainReady`. The accepted interval remains $51\le R_4(3)\le62$.

**Validation status: COMPLETE for all-sender R3 at the physical valuation.**
Background job `jmx0hmr7s` ran `bash lean/build.sh` and exited **0** after
**281.39 seconds**, with maximum RSS **6,782,744 KiB**. It compiled every
emitted-input audit and the root axiom checks. The retained log is
`research/k58-r3-count-finset/checks/root-build.log`. The problem ledger gates
this as **PROVED #18, checked by lean and another model**. Sequential
`ChainReady` and every later obligation remain open. Earlier independent member
replays and the numerical extraction check are described below.

## Theorem content

There are three Lean production layers:

* `lean/K58/CounterNeighbours.lean` gives the exact forty-one input atoms of
  every sender `18+k`, `k : Fin 15`, as host edges to the labels `1 … 16` and
  `33 … 57`. It proves those far labels injective, non-loop and distinct from
  `0`. Therefore a `14`-or-more true `prefixCount`, read through
  `realizedValuation` with `p 1 = 1`, yields a genuine `Finset` of at least
  fourteen physical colour-1 neighbours. Its cardinality equals the actual
  count, and the physical root `e 0` is absent.
* `CounterNeighboursAudit0.lean`, `…Audit1.lean` and `…Audit2.lean` re-read each
  emitted counter at its own `(oldTop,newTop)` and verify that the variables it
  reads below `oldTop` are precisely the same 41 atoms, in order up to
  permutation. The fifteen checks are intentionally split instead of bundling
  all kernel reductions into one elaboration.
* `ClassifiedBridge.lean` eliminates the old local-colour classification
  parameter. `Classified` allows a colour permutation; `palette_15` and
  `palette_16_fixing` turn the templates into the literal-colour form required
  by `pin_of_named_classification`. This uses the repository's pinned R4333Lean
  order-15/16 catalogue; it is not a new independent proof of that catalogue.
* `CountedSenderReady.lean` combines these facts. For every `k : Fin 15`,
  `emitted_sender_step_ready_of_emitted_count_classified` proves the emitted
  support step ready at the physical valuation from the actual emitted-atom
  count, without the former neighbour-set bundle or separate `hclass`.

Root and sender coordinate identifications, `p 1 = 1`, triangle-freeness, the
T16 arm-0 pinning and its coordinate coherence remain explicit hypotheses,
as they should be.

## Independent checks already performed

* m8/d1 (`PrefixCountFinset.lean` and `Audit.lean`) was recompiled independently:
  generic count/cardinality machinery and the sender-18 physical construction;
  no other sender and no guard-to-count sufficiency result.
* m6/d3 (`R3Count18.lean`) was recompiled independently: complete count-driven
  sender-18 support readiness, plus conditional all-k assembly. This is an
  alternative proof record, not a claim that its general sender inputs were
  discharged there.
* m4/d5 (`R1Snippet.lean` and `R1Classified.lean`) was recompiled independently:
  the exact literal-colour classification bridge and original theorems with the
  separate classification parameter removed.
* Every selected theorem in those replays reports only
  `propext`, `Classical.choice`, `Quot.sound`.
* A fresh implementation of host-variable arithmetic extracted all fifteen
  rows and passed their allocation and support-prefix checks. It regenerated
  exactly the 15 rows × 41 integers transcribed by the Lean decoder. The output
  is `extraction-replay.txt`; the parser is `decode_check.py`, relative to this
  repository rather than a hard-coded checkout.
* M7's audit declarations were first imported from completed `.olean` artifacts
  whose timestamps postdated their sources. The successful root build then
  independently re-elaborated all production sources and is the production
  check. `R3Final.lean` was separately recompiled in 1.71 s, reproducing the
  original sender-18 constants and emitted support theorem. M7's all-sender
  decoder was formally accepted after those checks.

Coordinator replay logs and the problem ledger live in
`research/k58-r3-count-finset/`, especially `checks/` and `proof.md` once the
root result is recorded.

To regenerate the independent table, run from the repository root:

```sh
mkdir -p .scratch/r3-counter
cd .scratch/r3-counter
python3 ../../results/next-directions-2026-11-28/r3/decode_check.py
cd ../..
```

The broad production proof/audit is `bash lean/build.sh`; it is Lean-only, not
a solver search.

## What remains open

1. At an arbitrary model produced by an emitted counter step, derive
   `guard = true → 14 ≤ prefixCount` from that step's CNF. The existing general
   library proves the other direction—count to a satisfying extension—and the
   emitted counter extension assigns the guard from the count. These are not
   the missing implication.
2. Transfer the physical catalogue reasoning to all such valuations and prove
   the identities between the abstract `senderStep` descriptions and the actual
   linked positions of `targetSuffixSteps`; then complete sequential
   `ChainReady`.
3. Finish the `expandKey` plan and `ColourUnit.ofEdge` bookkeeping and the
   palette-coherence details, followed by the final `AtLeast(15,6)` and
   `AtLeast(31,6)` obligations.

The finite neighbour-set gap R3 itself does not include these sequential
obligations, and this report does not silently include them in “proved”.

## Rejected checks and provenance

The coordinator initially tried a monolithic kernel `decide` comparison over
all fifteen counters. That was stopped after 180 s and replaced with split
per-sender audits; it was not a successful verification. The used decoder was
independently written and checked by m7 (`smx0gue0b`). Generic/sender-18 results
came from m8 and m6, the classification wiring from m4, and the sequential
interface criticism from m5. Only non-overlapping production modules are
integrated; the alternatives remain in their swarm directories.
