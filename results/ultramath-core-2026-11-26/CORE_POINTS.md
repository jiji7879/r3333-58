# Core points retained from Ultramath

These are curated from the coordinator records and the two accepted archival
audit reports (m1 and m4 of `smwx73ni9`). They are **not new proofs**. Where a
raw proof has been pruned, the corresponding finite statement is a historical
result requiring regeneration or restoration for local replay.

## `smwwdcyxb`: finite K58 progress, not a wall closure

- Eight accepted directions produced complete finite K15/K16 U/T
  classifications, an entrance reduction, branch/cube reductions, structural
  families, and physical-colouring checks. **No full row, profile, or new
  Ramsey bound was established.**
- Only **TT:2** and **UT:3** are complete normalized entrance families:
  **600/600 each**, hence **1,200**, not 1,800. TT:3 is 443/600. The family
  table is TT:2 600, TT:3 443, UT:2 596, UT:3 600, UU:2 591, UU:3 0. This
  leaves **770** shape-$(5,5,5)$ cases plus **4,740** degree-15 brace cases.
- An entrance means $\beta_r \ge 1$, not strictness $\beta_r>\alpha_r$.
  Balanced-active with equality is possible; a deficient root is already
  excluded by `RealizesFamily`'s $w(r)\le H(r)$ scope, not a separate row.
- The reciprocal refinement has 343 nodes, 172 leaves, **169 certified and
  exactly 3 open cubes**: `r5_n025b2-019`, `c485-022`, `c485_029-033`. All
  extend the named original `n025` cube. This is one augmented reciprocal
  branch, not the whole frozen row.
- The accepted strict case is a reduction, not elimination. Its cube-count
  wording is unresolved: handoff wording says 25 cubes per row; shipped
  `certs.json` has 29 entries plus four singleton groups. Do not quote an
  evidence-checked count without reconciling that difference.
- Equal-kind TT/UU parents must omit the mixed clone cap; equal-kind full-16
  countermodels exist. Marked-free parents are relaxations: UNSAT transfers,
  SAT is not a row counterexample.

Primary retained reports: [smwwdcyxb](audited/smwwdcyxb.md), the tracked
`results/final-smwwdcyxb-2026-11-26.md`, entrance brace audit and frontier
audit. The primary entrance and classification proof trees remain locally
available under the retention policy; the rest of the raw branch-proof trees
are not all retained.

## `smwx2syxr`: useful protocol repairs, no speed win

- Eight individually accepted submissions are attested by the live platform
  verdict records. These are **finite tooling and proof-semantic results**, not
  a wall result. (The archival auditor's statement that only swarm-level
  acceptance was available is corrected here.)
- `Saturation.lean` supplies the missing 16-arm/outside-point theorem and its
  clause, with the standard three axioms only. `Discharge.lean` discharges the
  Ramsey predicates needed by `GapFamilies`; the source-critical/template
  flags and separate declared bound obligations remain. Their source and
  environment were explicitly retained, not silently inserted into the central
  build.
- The auxiliary/cardinality bridge checks 741/971 gadgets and their encodings;
  it **does not certify the declared bounds themselves**.
- The valid cut's point coverage is TT--: 56×13 = 728, TU--: 70×12 = 840,
  UU--: 0, total **1,568 instances on 126 rows**. That is not an entrance
  proof for the other families. Unresolved entrance cases stay uncut.
- Blanket degree caps, ticket surcharges and root simplification are **not
  demonstrated speed levers**; measured runs were slower, cost-only, or
  inconclusive. Do not re-invest in the same experiments expecting free gains.
- Fresh ordinary per-leaf CNFs + DRAT and an exhaustive cover are the safe
  conservative route. A completed native all-cube inccnf run can replay at
  base only with its actual complete coverage and verified replay; IDRUP,
  a prefix, timeout or partial run is not a substitute.

See [the engineering audit](audited/smwx2syxr.md) and the integrated package
under `tools/selfcontained/wallcc/`. Its malformed m3 manifest has 9 valid
entries and 24 pasted `ls` lines, not 35 valid entries.

## Other audited runs

- **`smwp3xc7p`**: accepted two-orbit classification and 1,018 newly certified
  K58 cases (not 1,050). A judge correction changes the outside colour-0 edge
  bound to **at least 1**, not 6. No good $K_{51}$ was found and no lower bound
  moved. Measured pentagon split is inert; 98 circulant orbits stay open.
- **`smwvg1m43`**: gap-four pilot/row/unit closure is elementary; the A/B/C
  families are entailed aids, not the semantic reason. Wall inputs stay
  UNKNOWN at bounded budgets. Small-profile closure does not prove the bound;
  avoid rerunning old wall sweeps and do not enable `balance=True` accidentally.
- **`smwr3llof`**: finite bundle/split verifications and one DRAT-checked
  circulant exclusion, retained and replayed again here. Both children of the
  target remain open. The 1.6 GB uniform-run DRAT belongs to a killed UNKNOWN
  run and must not be treated as a certificate. No swarm submission was accepted
  as the requested case/family solution.
- **`smwswz4x9`**: the layered zero-set result is **48 candidates → 44 surviving
  incidence → 33 realised by an arm type**, not an exhausted multiplicity proof.
  The no-singleton case remains compatible. Only 2 of the 332 exhaustive types
  were re-run by the judge; the 37 dead types have no DRAT. Four incidence
  refutations and their CNFs remain and replayed again here.

See the four individual [audited reports](audited/) for exact hypotheses,
reproduction paths, hash inventories, corrections and unresolved items. Group D
file-size sums may count hardlinked files independently and differ slightly
from `du` totals; `smwp3xc7p`'s earlier scratch deletion is separately recorded.

## Secondary findings worth keeping clear

- Full circulant colour classes are not general good colourings; the old
  217/71 census was wrong, replaced by 33,752 triangle-free distance sets,
  1,102 maximal ones and 104 unit orbits in the reported computation.
- The provable global colour-degree cap is **16**, not 15. Degree counting
  alone has known feasible models and cannot settle the remaining profiles.
- Solver UNKNOWN, CDCL inactivity, local-search stagnation and partial proof
  dumps are not counterexamples, UNSAT or proofs that a route is exhausted.
- A SAT colouring of an intentionally smaller or relaxed problem is not
  necessarily a model of a frozen row. A clone means exactly one arm-coloured
  spoke, not a loose degree condition.

## Coverage of this curation

There are fresh detailed reports for six major historical swarms. The other
old runs are inventoried and source-indexed, not freshly re-adjudicated. The
accepted audit swarm had two members finish with reports and two leave their
assigned group directions abandoned. That is a limitation of the narrative
summary, not a loss of the source files covered by the source hash archive.
