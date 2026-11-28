# Pre-registered conditional-Sinz A/B (CNF performance only)

Date: 2026-11-28. One row only: `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`, profile `(16,16,14,11)`, charge 7, first-tier ordinary parent.

## Frozen inputs

* Parent: `inputs/parent.cnf`, SHA-256 `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae`.
* Naive two5 augmentation: `results/wall-two5-naive.cnf`, SHA-256 `bac8c106d698a0734ca8dbec535b0ccc212d8329f5cd79b49e25f6071420d05b`.
* Boundary two5 augmentation: `results/wall-two5-boundary.cnf`, SHA-256 `fa8be04c4d10d38f803a0db34109732ee551ea1c85d4e834d369d5a73bd25cdc`.

The naive/boundary forms have identical variable and clause counts. `src/audit_wall.py` must pass before the run. The unaugmented parent is contextual, not the Sinz control.

## Jobs and endpoint

Fresh k58-massive-solver-compatible CaDiCaL 1.9.5 through PySAT 1.9.dev22, no proof logging, seeds 0 and 1, 1,000,000 conflicts per job, 240-second subprocess cap. Six sequential jobs: parent, naive, boundary in seed 0; reverse order in seed 1. No additional seeds or variants will be selected for the primary report.

Primary pairwise endpoint: search-process CPU seconds for boundary versus naive at the same seed and conflict cap. Favourable bounded throughput requires lower boundary CPU in both seeds and a two-seed geometric-mean ratio at most 0.95. Decisions, propagations and restarts are secondary diagnostics. If a job finishes before the cap, its verdict/conflicts are recorded rather than replaced by budget-normalized numbers.

All OPEN/TIMEOUT results remain undecided. Any SAT/UNSAT solver status would be only an uncertified CNF status until independently checked; no physical-colouring conclusion follows. A timeout alone is not a solution. The unaugmented parent is the first-tier relaxation: even a checked model would not supply a semantic-row model.

## Stage 2: clause-order control (registered after stage 1 exposed the difference)

Stage 1 completed all six runs (all OPEN). Receipt inspection showed that the production naive path and split/boundary path do not use the same intra-gadget clause order. Stage 2 therefore adds the audited `naive-split` control, SHA-256 `02fc6b42b7edb93aa7647b5bbcc384a1a1328b64e6d1a1afba96657fdbe00f5d`. It has exactly the production naive clause multiset, while `naive-split` versus `boundary` differs positionally only by the 4,560 recurrence guards (`results/audit-order.json`).

Run fresh CaDiCaL195 jobs for all three augmented policies at both seeds 0 and 1, still 1,000,000 conflicts and a 240-second subprocess cap. Seed-0 order is naive-split, boundary, naive; seed-1 order is naive, boundary, naive-split. Report search CPU, conflicts, decisions, propagations and restarts for every call. The two pairwise questions are (i) boundary versus naive-split, isolating guard removal at fixed order, and (ii) naive versus naive-split, isolating legacy order at fixed naive guards. No outcomes from stage 1 will be hidden or used to select seeds. All statuses remain CNF-only and OPEN is undecided.
