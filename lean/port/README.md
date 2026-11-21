# The K15/K16 classification, ported

`K58.Classified 15` and `K58.Classified 16` — the only unproved structural
premise the `n = 58` cover rests on — are **proved** here, derived from the
pinned `R_4(3) <= 60` development's own kernel-checked theorems
(`R4333.k16CriticalCatalogue_complete`, `R4333.k15CriticalCatalogue_complete`).

    bash lean/port/build_port.sh

rebuilds the fourteen-plus modules of `lean/K58` together with the port and
prints

    'K58.classified_16' depends on axioms: [propext, Classical.choice, Quot.sound]
    'K58.classified_15' depends on axioms: [propext, Classical.choice, Quot.sound]

Measured at 53-54 s. No `sorry`, no `native_decide`, no new axiom.

## Why it is not part of `lean/build.sh`

The upstream classification is compiled against **Lean 4.32.1** and its own
pinned Mathlib (7.4 GB prebuilt under
`.scratch/k60ref/formal/.lake/packages`), while `lean/` is on 4.33.1: the
4.32.1 oleans are rejected by a 4.33.1 compiler. `build_port.sh` therefore
copies `lean/K58/*.lean` into `lean/port/build/`, pins
`leanprover/lean4:v4.32.1` there, puts the pinned sources and package build
directories on `LEAN_PATH`, and compiles everything in that sandbox. Nothing
under `lean/K58` or `lean/build.sh` changes.

Rebuilding the upstream modules at 4.33.1 instead is a different job and is
measured, not done: `CheckedLRAT`/`Basic` compile, `FiniteColorCNF` needs three
patches, `CatalogueBaseLiteral`/`CNF`/`LeavesK16Refined` compile, and
`CatalogueBaseCNFSemantics` fails at five sites; 26 modules were not tried.
See `PORT_NOTES.md`.

## Status

`Classified` is proved and *used nowhere yet*: the marking lemma is still the
critical path to a theorem at `n = 58`, and it is unstarted.
