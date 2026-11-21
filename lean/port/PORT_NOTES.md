# Porting the kernel-checked K15/K16 classification into `lean/`

**Result.** `K58.Classified 16` and `K58.Classified 15` — the only unproved
structural premise the `n = 58` cover rests on — are now *proved*, from the
pinned `n = 60` development's own kernel-checked theorems, with axioms
`[propext, Classical.choice, Quot.sound]`, no `sorry`, no `native_decide`.
The campaign's whole Lean tree plus the port builds in **40 s**.

## Files in this directory

| file | role |
| --- | --- |
| `K58/ClassifiedPort.lean` | drop-in module for `lean/K58/`; the port |
| `build_port.sh` | rebuilds `lean/K58/*` + the port in this directory and prints the axioms |

## What the port does, precisely

`K58.Classified n` (`lean/K58/Templates.lean:70`) says: every `EdgeCol (Fin n) 3`
that is `TriangleFree` is `IsoUpToColour` to `template n t` for some `t : Bool`.

1. `toR4333` — the same colouring as an `R4333.EdgeColoring (Fin n)
   R4333.ThreeColor`; `R4333.ThreeColor` is `Fin 3` by definition, so this is a
   change of structure only, no isomorphism.
2. `r4333_noMono` — `K58.TriangleFree` implies
   `R4333.NoMonochromaticTriangle`; the two predicates differ only in
   `PairwiseDistinct x y z` versus three inequality hypotheses.
3. `k16Untwisted_eq`, `k16Twisted_eq`, `k15Untwisted_eq`, `k15Twisted_eq` — the
   upstream catalogue entries **are** this repository's `template n false/true`:
   both are the `Z_2^4` XOR difference table plus the same sixteen-edge trade
   (`dc`/`trade` here, `untwistedDifferenceColor`/`k16TradeCodes` there). The
   identifications are kernel `decide` over the edge pairs, exactly as
   `template_triangleFree_16` is proved.
4. `classified_of_catalogue` — a catalogue consisting of the two templates
   classifies; it transports upstream `WeakColorEquiv` (vertex equiv + colour
   equiv) into `IsoUpToColour` (vertex perm + colour perm).
5. `classified_16`, `classified_15` — the two theorems, from
   `R4333.k16CriticalCatalogue_complete` / `R4333.k15CriticalCatalogue_complete`.

Note: `Classified` is currently *stated* but not *used* anywhere in `lean/`
(`grep -rn Classified lean/` finds only `Templates.lean`), so the port changes no
existing proof; the marking lemma will consume it. The docstring in
`Templates.lean` ("not proved here") should be updated.

## Integration: three changes for the coordinator

```sh
cp .ultramath/smwr0lr3q/m1/port/K58/ClassifiedPort.lean lean/K58/
# 1. add ClassifiedPort to the file list in lean/build.sh
# 2. pin the toolchain:  echo leanprover/lean4:v4.32.1 > lean/lean-toolchain
# 3. extend LEAN_PATH (build_port.sh prints it):
#    <repo>/.scratch/k60ref/formal/src  plus the nine package lib dirs
#    (mathlib batteries Qq aesop proofwidgets importGraph LeanSearchClient
#     plausible Cli) under <repo>/.scratch/k60ref/formal/.lake/packages/*/.lake/build/lib/lean
```

The toolchain pin is not optional: the upstream oleans are 4.32.1 and Lean
refuses to read them from 4.33.1 (`error: failed to read file … incompatible
header`). `lean/README.md` currently advertises 4.33.1 and must be updated.

## Durability warning

The pinned Mathlib build the port imports through is **7.4 GB in
`<repo>/.scratch/k60ref/formal/.lake/packages`** — a cache directory. Copy that
tree somewhere durable before depending on it, or take the rebuild route below.

## The other route (rebuild upstream in the campaign's 4.33.1): measured, not finished

Patch set needed; measured frontier with toolchain 4.33.1 + `/opt/mathlib`:

| module | result |
| --- | --- |
| `R4333Lean.CheckedLRAT` | OK (Mathlib's LRAT machinery still works) |
| `R4333Lean.Basic` | OK |
| `R4333Lean.FiniteColorCNF` | **3 patch sites, then OK** (see below) |
| `R4333Lean.CatalogueBaseLiteral`, `CatalogueBaseCNF`, `CatalogueBaseCNFLeavesK16Refined` | OK (63 s for the last) |
| `R4333Lean.CatalogueBaseCNFSemantics` | **fails at 5 sites**, errors `simp made no progress` (lines 32, 42, 54, 65, 80) |
| remaining 26 modules | not attempted |

Drift pattern 1 (`FiniteColorCNF.lean`, lines 184, 203, 239). The script
`simp only [atLeastOneClauses, List.mem_map] at hclause` no longer reduces
`clause ∈ List.map f l` in that position, so the following
`obtain ⟨…, rfl⟩ := hclause` meets a raw `List.Mem` term and Lean reports
`Tactic 'cases' failed … Dependent elimination failed: Failed to solve equation
List.map … = clause :: as at case List.Mem.head`. Fix used here: replace the
`obtain` by `List.mem_map.mp hclause` plus `subst` (and drop the now-unused
`List.mem_map` from the `simp only` set).

Drift pattern 2 (`CatalogueBaseCNFSemantics.lean`): `simp only
[List.mem_singleton] at hclause` now errors `simp made no progress` — Mathlib's
`failIfUnchanged` default turned a no-op rewrite into an error.

So a 4.33.1 self-contained port is a mechanical patching job over a 700 KB,
32-module development, not a drop-in; I stopped at the first module after the
frontier above and did not measure the rest.

## Not claimed

The upstream development's own correctness (32 modules, 55 CNF/LRAT pairs) is
its author's. I replayed its two classification endpoints from the pinned oleans
and checked their axioms; nothing here concerns its 296,081-formula SAT boundary.
