# The frozen cover is verified

The gluing-and-transport checkpoint (`R3333_K58_Lean_gluing_and_transport.zip`)
was independently reproduced here. Its two headline theorems are kernel-checked
with no `sorry` and no extra axioms.

## Reproduction

Applied `k58-lean.patch` (5,751 lines) to `e62d8ab`, reused the K60 catalogue
build, then:

```
./build.sh                                  45 K58 modules, 0 errors, no sorry
python3 run_replay.py <lean> <replay> --jobs 4
  Checked 1764 complete families, 190736 raw placements, 77557 omitted transports
  31 m 59 s
```

The counts match the independent Python campaign exactly: 1,764 families,
190,736 raw placements, 77,557 omitted transports, 113,179 retained.

Axiom check on the endpoint, run separately against the replay output:

```
'K58.Replay.rawTransportCover' depends on axioms: [propext, Classical.choice, Quot.sound]
'K58.Replay.frozenCover'      depends on axioms: [propext, Classical.choice, Quot.sound]
```

## What this establishes

Every triangle-free 4-colouring of the edges of `K_58` satisfies the signed unit
clauses of at least one of the 113,179 frozen cases. That is the marking lemma,
which was the largest open piece of the formal reduction.

The chain, all kernel-checked:

| step | theorem |
| --- | --- |
| classification at 15 and 16 | `classified_15`, `classified_16` |
| every host realises a raw family | `exists_realized_raw_family` |
| family → a raw placement | `familyPlacementCover` |
| 190,736 placements → 113,179 frozen | `rawTransportCover_of_plans`, `K58.Replay.rawTransportCover` |
| assembly | `K58.Replay.frozenCover` |

## What remains

One layer, and it is not computation: **the encoding**. All 45 modules concern
signed units; none mentions a clause, a CNF, a DIMACS file or a cardinality
constraint. The SAT campaign refutes base + units + *extras* (per-arm
thresholds, `s_crit ≥ 2M − 57`, full-root `H ≥ w`, support selectors), so
`AllUnsat` is not yet applicable.

The missing lemma: a colouring realising a case's units admits an extension of
the auxiliary variables satisfying every clause of that case's formula. Its
counterpart in the pinned K60 development is `Core.coloring_satisfies_formula`.
Alongside it, PROOF_PLAN step 5 — binding Lean's clause families to the emitted
DIMACS — is still open; today only the units are hash-bound.

For the `full_root` tier the gap is narrowest: `RealizesFamily` already carries
`w G r ≤ H G r`, which is exactly the extra assumption that encoding adds.
