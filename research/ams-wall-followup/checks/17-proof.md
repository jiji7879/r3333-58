# Conditional-boundary Sinz on the exact K58 wall parent

## Outcome

**Scoped result: a sound encoding transformation, but a reproducible negative CNF-performance result on the requested parent.** Boundary guarding was validated independently on every actual target counter gadget. In a new clause-order-controlled CaDiCaL experiment it reduced decisions but increased propagation and search CPU on both seeds at the same one-million-conflict cap. Its geometric-mean search-CPU ratio to the exact guard control was **1.33344** (1.17089 and 1.51856). All 12 full-CNF performance calls remained **OPEN**.

This is not an UNSAT certificate, a SAT result, a wall-row decomposition, or a physical-colouring theorem. No proof file was generated in these performance runs. The precise blocker is measured below: unconditional recurrence work costs more propagation/CPU without reducing conflicts by the cap.

## Exact binding

The sole row is `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`, profile `(16,16,14,11)`, charge 7. The generator rebuilds `tables=True,total_critical=True,full_root=False` and requires byte equality with the copied retained parent before emitting output.

| artifact | SHA-256 | use here |
|---|---|---|
| ordinary parent | `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae` | common 184,335-clause body; contextual solver control |
| working CNF | `39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38` | retained provenance only; not a benchmark query |
| RUP/CAS prefix | `dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3` | retained provenance only; no proof replay requested or claimed |
| naive two5 query | `bac8c106d698a0734ca8dbec535b0ccc212d8329f5cd79b49e25f6071420d05b` | production-order guarded control |
| naive-split query | `02fc6b42b7edb93aa7647b5bbcc384a1a1328b64e6d1a1afba96657fdbe00f5d` | exact clause-order control |
| boundary two5 query | `fa8be04c4d10d38f803a0db34109732ee551ea1c85d4e834d369d5a73bd25cdc` | recurrence-unguarded variant |

Every augmented query has 22,362 variables and 189,251 clauses: the parent plus 2,829 fresh variables and 4,916 clauses. `EXPECTED_SHA256` also pins the plan (`683969b82a6459befa58d75321fc1873dc26b63d01c5a9c64b8bfa0e46c1c29e`). Every solver receipt repeats its actual whole-query hash; `src/summarize_results.py` hashes the files again.

## Encoding and its semantic scope

For one conditional at-least gadget, let `E` be the Sinz prefix/input recurrence clauses and `O` its overflow/bound clauses. The three tested policies are

* **naive:** prepend `-g` to every clause of `E ∪ O`, using the production PySAT clause sequence;
* **naive-split:** prepend `-g` to every clause, using `split_atleast`'s recurrence-then-overflow sequence;
* **boundary:** leave `E` unchanged and prepend `-g` only to `O`.

The existential projected relation is `g ⇒ at-least-k(inputs)`. With `g` true, naive-split and boundary are exactly the same hard `E ∧ O`. With `g` false, every naive clause is satisfied; for boundary, evaluate each Sinz cell by its canonical prefix threshold to satisfy `E`, while every guarded `O` clause is already satisfied. Thus auxiliary satisfiability is preserved in both directions. Variable allocation is unchanged.

This argument establishes equivalence **between the augmented encodings**. It does not independently reprove all of the older two5 augmentation's physical justification and does not assemble Lean to the full parent.

### Independent controls

`src/audit_wall.py` parses the actual DIMACS itself and establishes:

* byte-for-byte preservation of all 184,335 parent clauses in both outputs;
* 93 actual target counter gadgets and 93 selector-pair clauses;
* 7,104 projected SAT-assumption checks, zero mismatches;
* 460 violating physical assignments tested: boundary BCP derived guard negation 460/460 times, naive did so 8/460;
* exactly 4,560 guard occurrences removed, reducing suffix literals from 17,273 to 12,713 (26.4%).

Small gadgets were exhaustive; larger ones used deterministic threshold, alternating and seeded assignments. This is supplemented by the previously accepted generic exhaustive counter proof, not presented as exhaustive testing of the 15-input gadgets.

`src/audit_order.py` adds the control missing from a simple legacy-naive/boundary comparison:

* legacy naive and naive-split have exactly the same clause multiset for every one of the 93 gadgets;
* naive-split and boundary agree **positionally** except that each of exactly 4,560 recurrence clauses has `-g` prepended in naive-split;
* another 7,104 projected SAT-assumption checks on naive-split passed.

Consequently the stage-2 A/B isolates guard removal rather than silently mixing it with clause serialization order.

## Matched performance experiment

`BENCHMARK_PLAN.md` was written before stage 1 and amended with the order-control design before stage 2. Runs used fresh k58-massive-solver-compatible **CaDiCaL 1.9.5 through PySAT 1.9.dev22**, seeds 0 and 1, requested conflict cap 1,000,000, 240-second subprocess caps, no proof logging, and sequential calls. Total observed driver time was 8m19.35s for stage 1 and 6m26.87s for stage 2. This stayed below the 30-minute experiment budget. All results below are search-process CPU seconds, not shared-VM wall timings.

### Stage 1: production naive versus boundary

| seed | parent | naive | boundary | statuses |
|---:|---:|---:|---:|---|
| 0 | 69.6829 | 61.0641 | 69.2601 | all OPEN |
| 1 | 75.4039 | 56.3962 | 73.3862 | all OPEN |

The unaugmented parent is contextual, not the Sinz control. Boundary/naive CPU ratios were 1.13422 and 1.30126. No call terminated with SAT or UNSAT.

### Stage 2: exact guard-only and order-only controls

| seed | naive-split | boundary | naive | statuses |
|---:|---:|---:|---:|---|
| 0 | 64.2403 | 75.2183 | 63.0931 | all OPEN |
| 1 | 51.2802 | 77.8723 | 51.0760 | all OPEN |

The controlled guard-only measurements are:

| seed | CPU boundary / naive-split | normalized CPU ratio | decisions ratio | propagations ratio | restarts ratio |
|---:|---:|---:|---:|---:|---:|
| 0 | 1.170889 | 1.170895 | 0.829838 | 1.049580 | 1.107294 |
| 1 | 1.518565 | 1.518567 | 0.513095 | 1.618011 | 0.914080 |

Normalized CPU is per million reported conflicts. CaDiCaL reported 1,000,000 conflicts for boundary, versus 1,000,005 and 1,000,001 for the two naive/naive-split runs after the same requested cap. This tiny internal overshoot is disclosed; both raw and normalized ratios give the same direction. The geometric-mean raw ratio is 1.3334436; normalized is 1.3334476.

The order-only ratios naive/naive-split were 0.98214 and 0.99602. More informatively, **conflicts, decisions, propagations and restarts were identical between naive and naive-split at each seed**. Repeated naive and repeated boundary runs also had exactly matching operation counts across stages. Thus the ordering did not change the observed CaDiCaL search trajectory, while guard removal did. Timing variation is retained rather than hidden by substituting deterministic operation counts for CPU.

Raw per-call receipts and logs are in `results/benchmark-1m/` and `results/benchmark-order-1m/`. `results/analysis.json` is independently recomputed from them by `src/summarize_results.py`.

## Structural conclusion and limits

Leaving all 4,560 recurrence clauses unguarded gives stronger local BCP, but those clauses are active even while guards are unassigned. On this exact parent the measured trade was **17.0% and 48.7% fewer decisions**, accompanied by **5.0% and 61.8% more propagations** and **17.1% and 51.9% more CPU** in the guard-only pairs. Neither seed reduced conflict work below the common cap or reached a verdict. The route therefore fails this bounded wall-performance gate for a precise reason: unconditional counter propagation becomes active search work, and its decision saving did not pay for itself. Stronger abstract BCP alone is not a wall speedup argument.

This does not prove that no selective/mixed conditionalization or larger-budget run could help, and it does not claim a universal solver ranking. The experiment covers one ordinary parent, two seeds and one cap on a shared four-core VM. No MCTS run was part of this direction. The negative conclusion is a controlled bounded-performance result, not merely a recommendation to try longer.

### Three-way claim separation

1. **CNF performance:** 12 queries ran and all are OPEN at their budget. CPU/operation measurements are reported only for the exact hashed CNFs.
2. **CNF UNSAT certification:** none produced. No naive incremental status, unfinished proof stream, or OPEN result is used as evidence of SAT or UNSAT. The retained CAS hash is provenance, not a proof receipt for any augmentation.
3. **Physical colourings:** no conclusion. The ordinary parent is the stated first-tier relaxation; UNSAT of a certified relaxation would transfer, but SAT would not provide a semantic-row model. The full physical criticality/support/allocation/unit/Lean-DIMACS bridge remains outside this experiment.

## Reproduction and files

From this member directory:

```sh
bash reproduce.sh
```

The quick reproduction checks hashes, regenerates all three CNFs byte-for-byte in a private temporary directory, runs both audits, and verifies all retained receipt summaries. It does not silently rerun the 15-minute benchmark or overwrite raw benchmarks.

* `src/two5_wall_encoder.py`: exact-parent three-policy generator;
* `src/guarded_counter.py`: copied accepted counter implementation used by the generator;
* `src/audit_wall.py`, `src/audit_order.py`: independent semantic/order controls;
* `src/benchmark_ab.py`, `src/benchmark_stage2.py`: one fresh solver process per call;
* `src/summarize_results.py`: independent ratios and determinism checks;
* `results/audit.json`, `results/audit-order.json`, `results/analysis.json`: compact outputs;
* `results/benchmark-1m/`, `results/benchmark-order-1m/`: complete per-call JSON/log receipts.

Total retained data is approximately 18 MB. No proof file, let alone a proof over 1 GB, was created.
