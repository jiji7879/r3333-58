# Emitted-coordinate and root-unit bridge

**Scoped progress, not a `ChainReady` proof.** Two accepted member files are now
integrated as `lean/K58/EmittedBridge.lean` and `lean/K58/TargetUnits.lean`.
The coordinator independently compiled them and incorporated them into the full
root Lean build. `bash lean/build.sh` passed in **19.67 s** (6.77 GB maximum
RSS), with no `sorry`, `native_decide` or custom axiom. Every registered axiom
list is empty or within `propext`, `Classical.choice`, and `Quot.sound`.

## What is now kernel-checked

- `K58.EmittedBridge.rowAtoms_val`: the slot of sender `18+k` at index `j` is
  exactly `hostVar (1+j) (18+k) 1`. The emitted coordinate order is therefore
  the arm-0 label order at all fifteen senders, not an arbitrary permutation.
- `K58.EmittedBridge.realized_rowAtoms`: the repository's physical valuation
  reads those atoms as precisely the colour of the corresponding physical edge.
- `K58.EmittedBridge.emitted_mask_of_pinned`: when the sender and root arms are
  pinned and the labels are identified, those atoms form one of the 112
  catalogue masks. `emitted_sender_step_ready` obtains the actual emitted
  `ExtensionStep.ready` proposition, not a different convenience predicate.
- `K58.TargetUnits.arm0_block_units`, `arm0_root_units` and `arm1_root_units`:
  the retained key's own unit list includes the T16 arm-0 template and the
  colour-1 root edges into every arm-1 label `17..32`.
- `triangle_free_third_ne`, `deg_ge_of_counted`, and `sender_pinned_of_count`:
  any `Finset` of 14 genuine colour-1 neighbours, together with the appropriate
  root edge and $\deg\le16$, yields the critical degree hypothesis. Under the
  explicitly supplied order-15/16 classification, it gives the sender's
  `PinnedArm`. Consequently, a correctly identified count of true neighbours
  can feed the emitted-step theorem.

These are meaningful auxiliary facts: the unknown coordinate order is no
longer part of the gap at this parent. They also constrain preprocessing. The T
units cannot be deleted or permuted as if they were decoration, and the support
catalogue is order-sensitive. The 41-of-14 counter must not silently become a
claim about the entire colour-1 arm shape.

## What is still open

1. **Count bridge (R3).** Convert the actual emitted counter style
   `14 <= prefixCount (fun i => v (counterAtoms18 i)) 41` into a `Finset` of 14
   real colour-1 neighbours, using list injectivity and the physical valuation.
   Supplying a `Finset` by hypothesis, as in the accepted theorem, is not the
   same as proving that bridge from the emitted counter.
2. **Bookkeeping (R2).** Show that `expandKey targetKey = some C` implies
   `C.key.plan = targetPlan`; unwrap `ColourUnit.ofEdge` to the emitted literal
   forms. These were left explicit rather than guessed.
3. **Classification (R1).** The order-15/16 critical-template classification
   remains a hypothesis in this local bridge, not a new proof supplied here.
4. **Final guards and chain (R4/R5).** The two final counters, coded-plus-
   automatic guard exhaustiveness, and sequential `ChainReady` are not proved.

The palette gauge and moreover `expandKey` success remain explicit where they
occur in the conditional source. No coded guard is silently identified with a
physical `Sends` event. No wall row, profile, or bound follows.

The member's detailed report is [findings.md](findings.md), containing the
exact declarations and residual R1–R5 obligations. The compiled root log is
[build.txt](build.txt). Use `K58.Check` to inspect the axioms of the integrated
results.
