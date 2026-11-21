# Review — the classification-and-marking checkpoint

Artifact: `R3333_K58_Lean_classification_and_marking.zip` (457.9 KiB), patch
`k58-lean.patch` (4,398 lines) against `e62d8ab`.

## Verdict

**The classification is done, and the marking lemma is reduced to two named
obligations.** Everything claimed is reproduced here. No `sorry`, no
`native_decide`, no new axioms.

## What was reproduced

| check | result |
| --- | --- |
| `git apply --check` on `e62d8ab` and on current HEAD | clean |
| catalogue port to Lean 4.33.1 (`build-catalogue.sh`) | 32 modules built, 0 errors |
| full `./build.sh` | 34 K58 modules built, 0 errors |
| `#print axioms` lines in the build log | 173 declared, all ⊆ `[propext, Classical.choice, Quot.sound]` |
| `sorry` / `native_decide` / `axiom` in added lines | none |
| `frozenKeys_length` | 113,179 |
| `rawFamilies_length` | 1,764 |
| `rows_by_plan` (regenerated ledger) | sums to 113,179 |
| retained + explicit transports | 113,179 + 77,557 = 190,736 = raw placements |
| support tables | 5,292 = 3 × 1,764, three per family |

## The two obligations, and whether they are satisfiable

The final theorem is

```lean
K58.frozenCover_of_family_placements
  (placements : K58.FamilyPlacementCover)
  (transports : K58.RawTransportCover) : K58.FrozenCover
```

`FrozenCover` is the right statement: every triangle-free 4-colouring of `K_58`
satisfies the units of one of the 113,179 frozen cases.

**Vacuity check on the geometric obligation.** `FamilyPlacementCover` asks, for
each realised family `f`, for a member of `rawPlacements f`. If any family had
an empty placement list the obligation would be unprovable. Checked by
evaluation over all 1,764 families:

```
rawFamilies.length = 1764
min placement count = 1
total placements    = 190736
families with zero placements = 0
```

So the obligation is satisfiable, though the margin at the thin end is one: at
least one family has a single placement, so an error in one of its three
support tables would be fatal and is worth a targeted look.

**The finite obligation.** `RawTransportCover` needs, for each of the 77,557
omitted raw placements, a vertex permutation of 58 labels and a palette
permutation whose transport carries the units onto a frozen case. The archive
supplies explicit witnesses for all of them and a Python verifier checks
bijectivity, the signed-unit transport, and that the image is a complete
retained unit set (38,666,290 signed units). That is strong external evidence,
not a Lean proof; replaying the finite coverage inside Lean remains open.

## The boundary that is still outside Lean

The patch chose option (ii) from the handoff: the frozen case table is a literal
compressed table, and the marking theorem concludes that a counterexample
satisfies the **signed unit clauses** of a frozen case. The step from units to
the actual DIMACS file is the Python encoder, bound by hashes. As the README
says, a DIMACS-level binding would need the CNF recipe formalised too.

So the remaining formal chain is: `FamilyPlacementCover` → `RawTransportCover`
→ `FrozenCover` → (units-to-CNF bridge) → `AllUnsat` → no good colouring.

## Discrepancy worth fixing

`results/versions.json` records `python_sat: 1.9.dev24`; the campaign's verifier
pins **1.9.dev22** and refuses other versions because it regenerates CNFs through
`pysat.card.CardEnc`. The Python verifiers in this archive do not import `pysat`,
so none of these comparisons is affected — but a recorded version that the
release verifier would reject is a trap for whoever reruns it. Record dev22.

## What this means for the next run

The classification is no longer the gate. `classified_15` and `classified_16`
are proved and axiom-clean, and the palette correction raised earlier is
formalised (`palette_15`, `palette_16_fixing`, `no_marked_swap_15`).

Two things remain, in order of tractability:

1. **`RawTransportCover`** — a finite check over 77,557 explicit witnesses. The
   data exists and has been checked externally; the work is making Lean replay
   it. Bounded and mechanical, though it may be slow.
2. **`FamilyPlacementCover`** — the geometric step: from a realised family,
   identify the three physical support intersections, apply
   `support_embedding_represented` in each critical target arm, extend the free
   arm's matching to a permutation, and show the resulting indices make
   `expandKey` return the same attachment, then apply
   `attached_block_realizes`.

Neither is a research problem any more; both are engineering with a known
target statement.
