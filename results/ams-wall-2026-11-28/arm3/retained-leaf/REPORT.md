# Retained arm-3 leaf and opt-in maximality solver

## Status

**CNF identities, local normal-form/reduction lemmas to existing interfaces, the
ordinary physical base/unit bridge, the BCP residual equivalence, and bounded
solver measurements are established. The hard leaf remains OPEN. No augmented
CNF refutation, wall-row closure, physical-colouring exclusion, or Ramsey-bound
change is claimed.**

The unique target is row
`06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`,
profile `(16,16,14,11)`, charge 7. Its cube is `[-1413,1014]`, in that order:
1413 is negative and 1014 is positive. There was no wall sweep and no solver
experiment on another row.

Six directions in Ultramath `smx01fwza` are accepted for bounded components.
The residual reconstruction, per-edge semantics, cube-sensitive adversarial
proof gate, raw/residual benchmark, and physical base/unit bridge were all
recomputed by the coordinator. The first package submission was **not** accepted:
a consistently rehashed MCF mutant passed its original receipt-only load gate.
It was repaired independently before integration. Stock production defaults,
`finalise`, ledgers and the massive baseline archive were not modified.

## Exact query identities

| query | dimensions | SHA-256 |
|---|---:|---|
| ordinary parent | `p cnf 19533 184335` | `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae` |
| working CNF | — | `39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38` |
| CAS prefix | — | `dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3` |
| ordinary parent + cube | `p cnf 19533 184337` | `8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8` |
| raw arm-3, colour 0 | `p cnf 22053 191940` | `1bb7a7823b0ceac16d303de15c204b28b11d4354ec17fcf60dba7678754ff9d2` |
| raw arm-3 + cube | `p cnf 22053 191942` | `fface1b819e26261736cb516be9063e7be2b1be120253875947a4400d4ac912a` |
| parent-BCP residual, no cube | `p cnf 22053 191475` | `31108fb9204b9e615a6396bb6239019f04307e083786db3d2b8e181f82e38daa` |
| residual + cube | `p cnf 22053 191477` | `ffcaa2f5c37509ba2e4df2c7dcce6d47f859fc9740c7e2ca8b0555cf8a0b6ea4` |

Cube construction replaces only the header clause count and appends
`-1413 0\n1014 0\n` in that order. The ordinary parent body remains unchanged.
Arm 3 has 45 safe internal edges. Each contributes 56 fresh conjunction
witnesses and their three Tseitin clauses, followed by one 57-literal
normal-colour-or-two-edge-path disjunction: 2,520 witnesses and 7,605 added
clauses total. Witnesses are contiguous variables `19534..22053`, immediately
above the actual parent maximum 19,533 (not the physical maximum 6,612).

## Normal form, BCP and proof replay

The generator-free per-edge certificate reconstructs all 134,995 host clauses
and the actual non-host suffix, checks 180 changing physical variables against
that suffix and cube, and exhaustively verifies 20,160 Tseitin truth-table
assignments plus 5,130 long-clause path scenarios. It also detects a physically
shadowed witness, a suffix/cube dependency, a flipped sign, a missing long
clause, altered cube order/sign, and altered edge metadata. The receipt does
**not** identify physical `Sends` or prove candidate criticality/support geometry.

The retained Lean `normalForm_equisatisfiable` remains the mathematically
correct conditional reduction: sequential recolouring preserves triangle-free
colourings and established per-colour two-edge paths, while fixed parts of the
suffix are outside-dependent. `PhysicalBridge.lean` now closes the ordinary
`hbase` and `hvars` premises at the exact `targetParentCNF` interface:

```lean
targetParent_satisfiable_of_expanded_ready
```

Its remaining premises include triangle-freeness, `expandKey targetKey = some C`,
the physical `RealizesCaseAt G C e p` realization, and
`ChainReady 6612 (realizedValuation G e p) targetSuffixSteps`. It is a
satisfiability-existence assembly from a physical realization, not a CNF
refutation and not an assertion that such a physical realization exists.
`lean/build.sh` passed after adding the module to `order.txt` and importing it
in `Check.lean`; all new printed axiom lists consist only of `propext`,
`Classical.choice`/`choice` and `Quot.sound`. No `sorry`, `admit`,
`native_decide`, or added axioms were used.

A separate kernel-checked two-vertex counterexample shows why the cube guard is
essential. Without outside-dependence, normalisation can destroy a frozen cube
literal. Actual target cube literals decode to colour 0 on edge `(6,33)` and
colour 1 on edge `(4,36)`; neither is configurable.

For residualisation, independent watched-literal BCP represents 1,813 parent
units by an acyclic chronological reason trail and checks a final fixpoint.
Exactly 465 raw suffix clauses contain a satisfied parent-BCP literal and are
removed; 7,140 residual clauses survive. All 45 long clauses and all 2,520
witnesses survive literally. The assignment canonical-list digest is
`9d773ef00ac64b36bb7d764f323208534c635ea7a29ee7bb959e48f81e6edabd`,
and the reason-trail digest is
`6b55ee4604b410de842d9cbaa8da6b30cd4f7bbd4f113f1f1cdcdc1ff65a0041`.
The full deletion receipt is retained outside Git; selected audit text and its
exact count/hash identities are in this result directory. For every suffix
clause `C`, its residual `C'` is either removed because the parent entails `C`,
or obtained by deleting parent-false literals. Hence, on the same variable set,
`P AND raw_suffix` is logically equivalent to `P AND residual_suffix`, including
when the same cube is appended. This proves neither MCF entailment nor UNSAT.

For any future completed augmented proof, `scripts/strict_rup.py` independently
parses both CAS and leaf before joining, validates deletion records and
truncation, retains valid additions in order, requires a final derived empty
clause, and performs warning-fatal full-byte `drat-trim -i -U -W` replay. It
requires exactly one `s VERIFIED`, a RUP-only core and a byte read equal to the
whole normalized file length. Three real toy proof replays and seven
adversarial controls passed, including a warning fake checker, a short-read
fake checker, wrong query, truncation and cross-stream splice. These are
**toy proofs only**. There is no target DRAT because the target solver returned
OPEN. A genuine future proof would still need the agreed second-verifier
review before broader certificate promotion.

## Measurements on the exact retained leaf

All calls used fresh default CaDiCaL 1.9.5 through `python-sat==1.9.dev22`, with
proof enabled, only conflict-budget settings, and no search wall timeout.
Conflict-count overshoots are Solver API budget granularity, not completed
searches. CPU values below solve only; preprocessing is excluded.

| paired queries | parent propagations / CPU-s | variant propagations / CPU-s | statuses |
|---|---:|---:|---|
| raw, 2M, parent first | 855,298,483 / 209.925347 | 884,198,407 / 209.685391 | both OPEN |
| raw, 1M, raw first | 381,196,308 / 64.463594 | 385,980,874 / 60.644920 | both OPEN |
| residual, 1M, parent first | 381,196,308 / 73.054778 | 385,980,874 / 64.169473 | both OPEN |
| residual, 1M, residual first | 381,196,308 / 65.654855 | 385,980,874 / 61.450189 | both OPEN |
| residual, 1M, coordinator replay | 381,196,308 / 62.374832 | 385,980,874 / 61.123102 | both OPEN |

At 2M raw arm 3 used **3.3789% more propagations**, with only **0.1143% less
measured solve CPU**. At 1M raw and residual used **1.2551% more
propagations**, while sharing exactly the same deterministic
conflicts/decisions/restarts/propagations at that cap. The coordinator's third
1M pair used 123.49 user CPU-s total and repeated all deterministic counters.
These numbers refute transferring the earlier no-cube propagation improvement
to this exact leaf; they do not support a speed claim for completed search.
`rejected-historical-no-cube-1m.jsonl` was explicitly excluded by m5 because
both its queries omit the cube.

No target `SAT`, `UNSAT`, model, or finished/incomplete target proof was
obtained. The raw and residual validation commands report PASS for byte
identity, allocation, counters, negative controls, and OPEN/result selection;
they do not certify a refutation.

## Solver integration

`tools/mcf/` is the source-only delivery. `create_variant.sh` copies an
unpacked massive package into a **new** directory and adds the independent
`k58-mcf.sh` command. It never adds maximality to the stock `run` default or
`finalise`. Required baseline ZIP SHA-256 is
`cc78f1d9f6f7901615b264c9ceaa3319bd152cd4caccc381a74ed742538bdb6a`;
stock `k58.sh` remains
`43f20cd7100775efcd16834934de9ceaeda82c0c43861cd04c217e54d7d844ad`.

The installed variant accepts only this exact row/tier/arm/colour/cube. It
regenerates all queries and rule metadata from the frozen inputs at prepare
**and every prepared-tree load**, compares body/cube/suffix bytes and complete
normal-form rule JSON, and refuses unsafe adjustables, wrong signs, stale
headers, duplicate or shadowed allocations and coordinated receipt mutations.
There is no fallback to ordinary `run` on an exception. The proof gate uses the
independent strict parser described above. Sources, reproduction commands,
exact hashes, and scope are in `tools/mcf/MCF_README.md`.

A fresh copied package passed **23 controls** in
`package-validation/summary.json`: exact preparation/dry-run/hash checks,
balanced one-conflict OPEN interface calls, independent schema reconstruction,
toy strict and CAS replay, ten primitive tests (807,936 K4 normalisations),
wrong input/sign/arm/colour/hash rejection, both rehashed-query tampering
controls, and the actual stock wallcc **20/20** suite. The package's OPEN files
record `python_sat_version: 1.9.dev22` and contain no proof/model artifact.

This is the requested opt-in solving capability, not deployment of global MCF.
Arm-3-BCP is checked mathematically and benchmarked but excluded from this
raw-only production interface. No other arm or row is silently enabled.

## Remaining obligations

1. Connect every candidate list and hit count to physical `deg G x c`/`Sends`,
   including root-edge threshold 14 and the safe omission convention.
2. Prove every selected physical sender lies in the exact named 112-support
   catalogue for its template/colour.
3. Prove the coded 15 selected guards plus automatic sender vertex 17 and the
   coded 31 critical guards plus vertex 17 equal the physical sender sets, so
   the two charge-derived 7 bounds become the emitted bounds 6.
4. Instantiate those physical facts as the sequential
   `ChainReady 6612 ... targetSuffixSteps` hypothesis.
5. If a real augmented leaf UNSAT is ever obtained, assemble the separate
   normal-form, cube-cover, CAS/leaf and physical-semantic proofs, with the
   additional independent proof-verification review. This single experimental
   leaf and its toy controls do none of those steps by themselves.

No proof of a wall row, degree profile, `K51` colouring, `R_4(3) <= 58`, or a
changed accepted bound (`51 <= R_4(3) <= 62`) follows from this work.
