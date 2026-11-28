# Exact K58 parent binding and conditional semantic assembly

## Outcome

This direction produced an **exact whole-byte Lean/DIMACS identity** for the retained ordinary parent and a kernel-checked, compositional semantic-extension theorem for that exact formula. It did **not** close the physical-colouring row. The remaining physical premises are named below as theorem inputs, rather than being replaced by hashes, solver status, or `native_decide`.

No solver was called. There is consequently no new CNF-performance claim and no new SAT/UNSAT certificate or verdict.

## Retained identity

| item | value |
|---|---|
| row | `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06` |
| profile / arm / charge | `(16,16,14,11)` / arm 1 / 7 |
| recipe | `tables=True,total_critical=True,full_root=False` |
| parent | `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae` |
| working CNF | `39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38` |
| RUP/CAS prefix | `dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3` |
| repository HEAD inspected | `bb0544cfdc508c5e33de0855604ce90ee37978c8` |

The exact `K58.CaseKey` is:

```lean
{ planIndex := 29, arm := 1, markPosition := 0,
  secondSixteen := false, secondTwisted := true,
  rootPosition := 7, placement := fun _ => 0 }
```

The zero-based plan index is 29, not a one-based rank. The 458-entry Lean `caseUnitList` has 438 unique signed literals; its set and sorted order exactly match Python `gluing.units`. See `generated/unit-binding.json`.

The ordinary parent hash is the formula assembled here. The 315-cut working CNF and its CAS prefix are separate artifacts and are not silently included in `targetParentCNF`.

## Whole-parent binding

`lean/TargetParent.lean` defines `hostBaseCNF`, `targetUnitCNF`, the generated `targetSuffixCNF`, and

```lean
def targetParentCNF := hostBaseCNF ++ targetUnitCNF ++ targetSuffixCNF
```

Lean itself printed the resulting DIMACS. `generated/check_parent.py` compared the entire stream, including the header, with `inputs/parent.cnf`: **all 3,493,016 bytes match**, and the SHA-256 is the retained parent hash above.

| family | parent clauses (inclusive) | count | checked identity |
|---|---:|---:|---|
| host exactly-one + triangle exclusions | 1–134,995 | 134,995 | Lean `hostBaseCNF` |
| sorted frozen signed units | 134,996–135,433 | 438 | Lean `targetUnitCNF` |
| linked counter/support suffix | 135,434–184,335 | 48,902 | Lean `targetSuffixCNF` |

The host base has top variable 6,612. The suffix ends exactly at variable 19,533. The complete parent has 184,335 clauses. Independent suffix-only evidence is in `generated/suffix-binding.json`; the full binding is `generated/parent-binding.json`.

## Exact auxiliary allocation and clause-family map

`generated/semantic-map.json` gives every guard, input vector, bound, old/new allocation top, selector support, absolute clause range, and event hash. The map was independently reconstructed by `generated/semantic_map.py`, not accepted from the tracer.

- **31 guarded native at-least counters.** Every clause matches an independent transcription of `nativeAtLeastCNF`, followed by the negative guard. Guards 6613, 6814, …, 11586 label vertices 1–16 in critical arm 0; guards 11965, 12456, …, 18839 label vertices 18–32 in selected arm 1.
- **One guard-free forced sender.** Vertex 17 has 14 fixed positive other-arm edges, so its `needed` value is zero. It belongs to both the selected-arm and total-critical physical counts but has no guard.
- **15 support events.** Each follows the selected-arm vertex counter. Each has one target: arm 0, size 16, kind T, 112 selectors. All 16 positions are active on this parent. There are 1,793 implications/disjunction clauses per event: every implication precedes the guarded selector disjunction. This is the exact emitted order, not merely a permutation-insensitive claim.
- **Selected-arm total:** parent clauses 183,950–184,054, 15 guard inputs, bound 6, allocation 19,329→19,383.
- **Total-critical total:** parent clauses 184,055–184,335, 31 guard inputs, bound 6, allocation 19,383→19,533.
- Overall checks cover 22,007 native-counter clauses and 26,895 support clauses: all 48,902 suffix clauses.

The old full-support Lean shape puts the disjunction first and always includes all positions. The new `emittedSupportFamilyCNF` instead uses implications-first and an explicit active mask, matching the actual generator. `satisfiable_emittedSupportFamily` proves adequacy of that exact shape.

## New compositional theorem

`lean/SemanticAssembly.lean` adds:

1. native/guarded variable bounds from the existing `counter_atoms_le`;
2. fresh guard assignment fused with a guarded counter (`freshGuardedCounterStepAuto`), with an explicit proof that no input is the fresh guard;
3. native final-counter and emitted-support steps; and
4. `chain_extend`, which preserves every earlier clause family through successive fresh-variable extensions.

The complete theorem in `lean/TargetParent.lean` is:

```lean
theorem targetParent_satisfiable_of_ready (v : Valuation)
    (hbase : FormulaSat v (hostBaseCNF ++ targetUnitCNF))
    (hvars : VarsBelow (hostBaseCNF ++ targetUnitCNF) 6612)
    (hready : ChainReady 6612 v targetSuffixSteps) :
    ∃ w : Valuation, (∀ a ≤ 6612, w a = v a) ∧
      FormulaSat w targetParentCNF
```

It and its dependencies print only standard axioms `[propext, Classical.choice, Quot.sound]`, with no `sorryAx`. Some small concrete allocation inequalities use ordinary `by decide`; there is no `native_decide`.

## Physical ticket progress

`lean/TicketPremises.lean` proves

```lean
seven_critical_senders_of_16_16_14_11 :
  w G r ≤ H G r → 7 ≤ armSenders G r 0 + armSenders G r 1
```

under the four exact degree equalities. The proof uses `w=32`, `H` as the sum of four arm-sender counts, and the small-arm bounds 14 and 11. `six_of_adjusted_guard_count` then states precisely the two remaining guard-set equalities needed after omitting one forced sender: mapping the coded sets exactly to the physical sender sets turns both 7-bounds into the emitted 6-bounds.

These are physical premises for CNF adequacy only; neither theorem asserts that the parent is unsatisfiable.

## Remaining obligations — exact, not hidden

The full-parent theorem reduces the unfinished physical bridge to the following:

1. **Base and units:** construct the physical valuation and prove `hbase` from triangle-freeness and `RealizesKey`/`RealizesCase`, including its common host and colour permutations. The signed units themselves are now bound exactly. `hvars` is the separate elementary proof that all base/unit variables are at most 6,612.
2. **Candidate criticality:** bind each emitted candidate list and fixed-positive count to `deg G x c`, including the root edge and the safe omission of same-root-arm edges. This shows that the freshly assigned true guards represent physical `Sends`, not merely Boolean threshold predicates.
3. **Support membership:** for each of the 15 listed guards, prove that a true physical sender makes its actual P4/C5 intersection one of the 112 explicit `targetSupports`. `K58.pinned_support_shape` is available, but its transport into this exact named target template and catalogue has not been assembled here.
4. **Adjusted guard-set totals:** prove the coded 15-guard set plus vertex 17 is exactly the physical selected-arm sender set, and the coded 31-guard set plus vertex 17 is exactly the physical critical-arm sender set. Combine these with charge 7 and the proved seven-critical-senders theorem.
5. **Sequential instantiation:** use 2–4 to discharge `ChainReady`; the linked old/new tops and all fresh disjoint intervals are already explicit in `targetSuffixSteps` and `generated/semantic-map.json`.

Until all five are proved, a DRAT refutation of this parent would remain only a CNF-level result. A SAT model of the relaxation would still not supply a physical model, and timeout/OPEN would remain UNKNOWN.

## Reproduction

Run `bash reproduce.sh` from this directory. It regenerates the trace and semantic map, builds the new Lean modules, exports the Lean parent, checks the whole-byte and unit bindings, and compiles the physical ticket theorem. The shared virtual environment is used only for the existing Python/PySAT generator. No wall search or proof production is run.
