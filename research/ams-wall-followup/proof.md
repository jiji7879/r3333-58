# AMS wall follow-up result

**Status: bounded result validated. No wall row, profile or Ramsey closure.**
The useful result is a new arm-3 configurable-maximality encoding with a measured
throughput gain, plus a conditional exact-parent Lean assembly that exposes its
remaining physical premises. MCTS and unconditional conditional Sinz are not the
way through on the tested instance.

## Gate

```text
PROVED #26. The argument was read only by the model that wrote it.
  self: PASS: final synthesis checked against every accepted result and all remaining physical obligations
  compute: PASS: all independent artifacts, solver statistics, hashes and final integrated Lean build pass
```

All eight underlying directions were read and independently replayed; the `self`
marker applies to this synthesis only. Every solver run is in its exact CNF scope
and every wall solver run is OPEN. No SAT/UNSAT or physical-colouring conclusion
has been drawn from timeouts.

## Confirmed outcomes

1. **A proved maximality normal form.** `normalForm_equisatisfiable` proves safe
   recolouring, path monotonicity, sequential normalisation, outside-suffix
   preservation, and exact three-clause fresh-witness semantics. The full build
   has the new `ConfigurableMaximal` module with only standard axioms (#2).
2. **An exact clause/allocation map:** 31 guarded native counters, 15 support
   families with 112 selectors each (96 P4 and 16 C5 in colour 2), one automatic
   sender and 12,921 contiguous disjoint auxiliaries. Five real physical
   obligations remain (#5).
3. **A verified CNF prefix equivalence:** 5,445 ordinary RUP additions prove all
   extra clauses. Replay recovers parent +315 = working. The streams are
   derivations, not empty-clause refutations. Strict whole-byte checks reject a
   93-byte truncated proof even when two native checkers print VERIFIED (#11).
4. **Direct MCTS failed twice, with a useful diagnosis:** full rollout with two
   simulations reaches only root depth 1 and emits the shallow four-cube tree;
   all its fresh leaves are OPEN at 1M (#8). The selective hybrid recovers the
   better closed-control tree with 3.13x less preparation than ten-sim, but raw
   wall selection is pure 0/1-cap-overshoot, all normalised candidates are equally
   unresolved, and greedy/cheap two-sim still wins overall (#14).
5. **Conditional Sinz is sound but slower on this wall.** The boundary form is
   projected-equivalent and back-propagates 460/460 actual violations while
   removing 4,560 recurrence guards at fixed order. All 12 matched runs are OPEN;
   guard-only CPU ratios are 1.170889 and 1.518565 (geometric mean 1.33344).
   Naive and naive-split have identical operation counts, so recurrence activation,
   not serialization, is the blocker (#17).
6. **Arm 3 is the first positive solver-encoding candidate.** Its 45 safe edges
   receive 2,520 fresh witnesses and 7,605 clauses. At 2M conflicts it uses
   399,144,507 propagations/120.766 CPU-s versus parent 838,419,903/222.721,
   both OPEN. An independent 1M rerun matched exact trajectory fields with
   262,186,194 versus 371,735,517 propagations and 48.027 versus 65.614 CPU-s,
   a 26.78% reduction. BCP removes 465 parent-satisfied suffix clauses without
   changing deterministic statistics or deleting any long MCF clause/witness
   (#20). This is existential equisatisfiability, not a DRAT consequence.
7. **The exact parent Lean emission and conditional assembly now exist.** All
   3,493,016 bytes match. The assembly links 31 fresh guarded native counters,
   15 exact-order support events and two bound-6 final counters with explicit
   disjoint allocation. The ticket theorem gives seven critical senders; omitting
   the unique forced sender gives six. `targetParent_satisfiable_of_ready`
   preserves exact scope instead of claiming physical closure (#23).

## Independent checks performed

All member reproductions ran: 1,800 saturation checks; generic/native and actual
Sinz audits; 542,952 small MCF colourings and 117,720 incidences; 256 lex pairs
and 3×4096 small matrices plus strict microproof; exact $K_{50}$ models;
semantic counter/support suffixes; the independent RUP prefix and misleading
truncated controls; 217 selective-MCTS manifest checks and four closed-control
certificates; the direct horizon toy, eight exact query bindings and four OPEN
receipts at 4,000,002 conflicts; conditional-Sinz byte regeneration and all
operation totals; arm3 independent A/B; and the whole-parent Lean equality plus
the ticket theorem. The integrated `lean/build.sh` passed after registering all
new modules and axiom reports.

For arm 3 the independent fresh pair exactly matched the report's deterministic
restarts/decisions/propagations, and the raw/BCP trajectories were identical.
All wall and arm experiments stayed below their resource bounds and have no proof
files or incremental proof claims.

## Remaining work, deliberately not claimed done

* Prove the physical base valuation for the 438 frozen units and their bound.
* Map candidate lists and fixed positives to `deg G x c`, including root-edge
  threshold 14.
* Prove the 15 actual true guards make their intersections exactly one of the
  112 named supports (colour 2, correct template).
* Prove the 15- and 31-guard sets plus vertex 17 equal physical sender sets,
  yielding the two adjusted guard-count equalities of 6.
* Instantiate those as `ChainReady`, recheck DIMACS bytes, and only then combine
  an ordinary UNSAT proof with a physical-row semantic conclusion.

Until then even a completed parent CNF UNSAT proof is CNF-only. OPEN never means
SAT or UNSAT.

The arm-3 result is a throughput experiment only. A reasonable next bounded
experiment is one retained difficult leaf with a matched original-parent cube
and strict augmented proof plus its independent normal-form reduction—not a
production sweep or an identical higher-budget rerun.

## Files and source scope

Primary detailed evidence is [results/ams-wall-2026-11-28/](../../results/ams-wall-2026-11-28/README.md),
including `arm3/`, `semantic-assembly/`, `semantic-map/`, `conditional-sinz/`,
`mcts/`, `mcts-selective/`, `mcts/` and `certificate-audit/`. The claims ledger
and independent check records are under `research/ams-wall-followup/`.
