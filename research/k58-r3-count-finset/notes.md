# R3 working notes

1. The current `K58.EmittedBridge.emitted_sender_step_ready_of_count` assumes
   `W`, membership and non-root facts, and cardinal lower bound separately.
   `K58.SenderReady.counterModel_count` shows that the count alone does not
   supply a catalogue mask. The mathematical content required here is the
   translation through the *physical* valuation, including injective labels.
   Work under this folder and `.ultramath/smx0gue0b`; leave all unrelated
   working-tree files alone.

2. Existing exact `counterList18_decode` divides the atoms into 16 arm-0 labels
   `1..16` and 25 labels `33..57`, all oriented toward sender 18. The root and
   arm-1 labels are absent. A physical map should take each true atom to its
   other endpoint, transported by the host equivalence `e`; non-loop and root
   exclusion facts then follow by arithmetic and injectivity of `e`.

3. `K58.Classification.classified_15` and `.classified_16` already exist at HEAD
   and import the pinned R4333Lean catalogue. Integration must check whether
   `Classified n` matches the explicit `hclass` parameter before treating R1 as
   discharged. The build script adds the pinned catalogue to `LEAN_PATH`.

4. Swarm `smx0gue0b` has eight members with distinct R3 facets. No broad solver
   panel, no rush to `ChainReady`, and no unreviewed acceptance. Prior reminders
   for `smx0er1f6` concern already accepted, integrated results; that run ended.

5. External literature is not needed for this finite Boolean/finset deduction or
   for direct Lean bookkeeping. The actual external classification is already
   supplied by the repository's pinned R4333Lean dependency; claim only its
   existing compiled scope after rebuilding.

6. The coordinator's `work/R3Prototype.lean` now compiles. It proves
   `card_trueIndices`, which equates the filter of `Finset.range n` by a Boolean
   vector to `prefixCount`; `exists_neighbour_finset_of_count`, which uses only
   injectivity below `n` and endpoint/colour/root compatibility to construct the
   required `W`; and `deg_ge_of_emitted_count`, applying the existing degree
   lemma. It also proves `sender_pinned_of_count_classified` using
   `critical_arm_pinned`, with no fresh `hclass` hypothesis. All four axiom
   reports contain only `propext`, `Classical.choice`, and `Quot.sound`.
   Focused compile: 1.58 s wall, 3.40 GiB maximum RSS; see
   `checks/prototype.log`. This proves the generic mechanism, not any concrete
   emitted sender: the exact atom-to-vertex map and the all-sender audit remain.

7. Accepted m8/d1: independent full recompilation of
   `.ultramath/smx0gue0b/m8/{PrefixCountFinset,Audit}.lean` passed. It proves
   generic physical neighbour construction and the sender-18 case, not the other
   fourteen or guard-to-count soundness. `checks/m8-independent.log` is the
   coordinator's re-run, not a copy of the reporter's log. Accepted m4/d5:
   independently compiled `R1Snippet` and `R1Classified`, confirming the exact
   literal-colour classification conversion and only standard axioms. Its
   source is now candidate module `lean/K58/ClassifiedBridge.lean`.

8. Accepted m6/d3: independent recompilation of `R3Count18.lean` passed. This
   adds full count-driven sender-18 support-step readiness and an all-k assembly
   conditional on decoder hypotheses. It does not itself identify senders 19–32.
   Its `..._of_guardcount` implication does not prove that implication from
   counter satisfaction: this remains an explicit successor to R3. Member m7 has
   independently provided an all-sender decoder/geometric construction in draft
   `R3Counter.lean`; strictly missing at this note is the complete clause-level
   input audit for all fifteen. Its cost is about 15 kernel-seconds per sender.

9. The coordinator's duplicate draft `work/AllSenders.lean` has not passed its
   emitted-input audit and must not be presented as proved or integrated. The
   expensive `by decide` comparisons were stopped at 180 s and 120 s, and a fresh
   direct comparison is not needed while m7's carefully split audit is running.
   The earlier `R3Prototype.lean` remains valid but its generic part is now
   largely subsumed by m8; no part of it is counted as all-sender completion.

10. Root build `jmx0hmr7s` is running in the background against the integrated
    three production layers. The new narrow assembly theorem in
    `CountedSenderReady.lean` uses the actual `emittedCounterAtoms` and the
    imported classification. No all-sender theorem is yet marked proved in the
    ledger. A candidate report is at
    `results/next-directions-2026-11-28/r3/README.md`, marked pending.

11. Root build `jmx0hmr7s` COMPLETED with exit status 0 in 281.39 seconds and
    6,782,744 KiB maximum RSS. It compiled `ClassifiedBridge`, all four
    `CounterNeighbours*` modules, `CountedSenderReady`, and the root `K58.Check`.
    `counter_inputs_audit` covers every `k : Fin 15` from actual emitted clauses.
    `exists_neighbour_finset_emitted` constructs the physical neighbour set from
    actual counted input atoms. `emitted_sender_step_ready_of_emitted_count_classified`
    adds support readiness and eliminates the previous W bundle and separate
    classification premise. See `checks/root-build.log`. All 501 axiom lines over
    that log and m3/m5 independent checks contain only permitted standard axioms.
    This proves all-sender R3 at a physical valuation; #10 remains open.

12. Independent controls: m3 has a count-15 witness plus root T16 coordinates,
    not a triangle-free K58 witness. Its necessity examples show gauge, nonloop,
    root exclusion and root colour cannot be dropped. m5 establishes the exact
    universal aggregation requirement and its counterexample, not ChainReady.
    Both were independently compiled by the coordinator (m3 2.70 and 2.53 s;
    m5 2.30, 1.72 and 16.31 s) and accepted in that bounded scope. Logs:
    `checks/m3-{control,root}.log`, `checks/m5-{r3,chain,counter}.log`.

13. The accepted construction is not reduced merely to educational intuition:
    literal 15×41 input atoms were regenerated from source using independent
    host-variable arithmetic, allocation and first-16-support links checked,
    then all fifteen actual clause-level input sets were kernel-checked.
    `checks/m7-extraction.log` has the fifteen OK lines;
    `checks/m7-transcription-check.json` records exact table identity. The
    arbitrary-nonloop/rooted model choices still enter only as the explicitly
    named coordinate, palette, root and triangle-free premises.

14. M7 was re-read after formal submission and separately recompiled `R3Final`
    (1.71 s, `checks/m7-final.log`) and was accepted, completing six accepted
    directions. Its partial `R3Step` count-to-satisfiability corollary is not
    used as a guard-to-count soundness theorem or as proof of exact complete-CNF
    identity. The deliverable retains #10, exact key bookkeeping, and final
    native counter obligations as open. Ledger gate #18 is now PROVED checked
    by lean and another model, with numerical replay as well. Historical
    mechanical-ledger entry #13 was replaced by #18 solely because mentioning
    #10 in the earlier sentence encoded it as a dependency; no source or scope
    changed. The complete final proof text is `proof.md`.

15. Final adversarial review (m2, accepted direction 7) exposed that every
    auxiliary rowGuard is false at the ordinary physical valuation: bare
    `.ready (realizedValuation …)` is vacuous. The R3 finite-set and physical
    mask statements remain mathematical content, but their presentation must
    not imply that this bare proposition is useful end-to-end ChainReady.
    PhysicalGuard and a non-vacuous catalogue mask, agreeing-atom theorems,
    and a guard-true agreeing-atom witness are now integrated. The latest
    strengthened root build is exit 0 / 5.82 s / 6,813,156 KiB RSS; its
    declaration-level output in `checks/root-build-strengthened.log` again
    uses only standard axioms. All 15 exact audits in the first full root pass
    are unchanged and independently rerun by m1 too.

16. All eight swarm directions are accepted and `smx0gue0b` has finished
    (solved in the task's technical, accepted-submission sense). M1's loop
    collision `hostVar 32 33 one = hostVar 32 32 one` is valid and proves why
    code inequality cannot express no-loop; the real proof uses non-equal
    endpoints explicitly. M2's root/palette/duplication controls validate
    which assumptions remain essential. Independent remaining replays:
    m1 A–E 29.99–30.68 s each plus assembly/collision/table checks;
    m2 physical 2.47 s, all 25.47 s, classification 1.59 s,
    mask 1.55 s and rowaudit 119.28 s (4.41 GiB peak RSS).

17. The production warning comments and final root audit are complete. After
    the vacuity caveat was also added to `K58.Check.lean`, `bash lean/build.sh`
    ran again with only `K58/Check.lean` still needing re-elaboration: exit 0,
    2.90 s, 6,813,676 KiB RSS (`checks/root-build-final.log`). First commit
    `d3f8883157202b4ab6207fe2802b32cc2dec8d29` is pushed; this strengthened
    non-vacuity correction is intentionally a separate new commit, not an
    amend or force-push.
