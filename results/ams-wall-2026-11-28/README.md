# AMS wall follow-up evidence

**Outcome:** eight accepted directions, one real encoding-speed improvement and
one conditional exact-parent semantic assembly. All wall solver runs remain
OPEN. No physical-row, profile or Ramsey closure.

## Main positive result: configurable maximalisation arm 3

`arm3/` contains the exact parent+45 configurable edges CNF novel search policy.
At 2,000,000 conflicts, arm 3 used 399,144,507 propagations/120.766 CPU-s versus
parent 838,419,903/222.721, both OPEN. An independent coordinator 1M pair used
262,186,194 versus 371,735,517 propagations and 48.027 versus 65.614 CPU-s.
BCP residual removes 465 parent-satisfied suffix clauses and preserves all 45
long MCF clauses and every witness. Read `arm3/REPORT.md`, `arm3/REDUCTION.md`
and `arm3/results/coordinator-arm3-1m.jsonl`.

This is a sound existential augmentation, not the parent's DRAT implication.
Every solver call is still OPEN. Suggested next bounded use: arm3 or BCP-arm3 on
one already retained hard leaf with original-parent cube and certified reduction,
not a sweep.

## Semantic memory/readiness and exact assembly

`SEMANTIC_READINESS.md` records the pre-run memory check: correct native
counter bindings and the missing physical-to-DIMACS assembly.

`semantic-map/REPORT.md` gives the exact clause/allocation inventory: 31 sender
counters, 15 support families / 1,680 selectors, 112 colour-2 supports, 31 floor
guards plus one automatic sender, and 12,921 disjoint auxiliaries. `semantic-assembly/SEMANTIC_ASSEMBLY.md` supplies the exact Lean/DIMACS parent
(all 3,493,016 bytes) and `targetParent_satisfiable_of_ready` with `hbase`,
`hvars` and `ChainReady` left explicit. Main `lean/` also contains
`K58.ConfigurableMaximal.normalForm_equisatisfiable` and the new chain,
support-shape and ticket modules with only standard axioms. Full `lean/build.sh`
passes after integration.

Five physical obligations remain: base/438-unit realization, candidate
criticality, exact 112 support membership, adjusted guard-set totals, and
sequential `ChainReady`. No physical result may be inferred before they are done.

## Conditional Sinz

`conditional-sinz/ASSESSMENT.md`: exact projected equivalence and 93 gadgets,
14,208 SAT project/control checks and 460/460 boundary back-propagation. The
boundary/naive-split geometric-mean CPU ratio is 1.3334 (both seeds slower).
Naive/naive-split operations are identical, isolating activation cost rather
than clause ordering. All 12 runs stayed OPEN. This supports the encoding but
not deployment on this parent.

## MCTS and certificate checks

* `mcts/REPORT.md`: the full-rollout two-simulation wall configuration emits the
  same shallow tree. Actual MCTS.py and the toy show root depth 1 at horizons 2
  and 22, so it is not a deep rollout. All four leaves stayed OPEN at 1M.
* `mcts-selective/REPORT.md`: the hybrid obtains a known MCTS tree with 3.13x
  cheaper preparation on the closed control, but not better than greedy or cheap
  two-sim, and its raw wall selection is a 0/1-conflict cap-overshoot artefact.
  Every normalised candidate key is `(2 OPEN, 40000)`.
* `certificate-audit/SOLUTION.md`: 5,445 independent RUP additions prove
  `parent ≡ working` at 184,650 clauses, with zero refutation. All five Kissat
  leaves stayed OPEN after 10,081,254 conflicts. The 93-byte truncated control
  misleadingly prints VERIFIED in two checkers and is rejected by strict parsing
  plus whole-byte gates.

These are CNF performance/certificate scopes only; none supplies physical
colouring semantics without the assembly obligations above.
