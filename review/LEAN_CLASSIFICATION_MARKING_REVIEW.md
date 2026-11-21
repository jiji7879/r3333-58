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

## The hard tail (20,185 cases) and what Lean needs from it

`hard.txt` contains 20,185 ids, all OPEN in the frozen ledger:

| profile | cases |
| --- | ---: |
| `(15,15,15,12)` | 20,165 |
| `(16,15,15,11)` | 20 |

All 20,185 are real ledger rows and none is duplicated.

**What the Lean binding needs from a certificate archive is a small table, not
the archive.** The Lean case list `frozenKeys` carries case identities; the CNF
for a case is generated from `(ledger row, recipe)`, and the ledger does not
record the recipe — that is a known defect. The recipe therefore exists only in
the certificates' `verified.json`. So the irreducible artifact is, per case:
`id`, `recipe`, `cnf_sha256`. Measured: **2,594 bytes for 19 cases**, so about
**2.8 MB for 20,185** — against tens of GB of certificates.

`tools/hard_tail.py` does that extraction: it regenerates each CNF from the
ledger row and the recorded recipe, checks it against the recorded hash,
decompresses the certificate and replays it with drat-trim, and writes only the
binding row. Measured 1.2 s per case at 4 workers (18 verified, 1 correctly
reported as having no certificate). At 12 workers the 20,185 cases project to
~35 minutes, plus the cost of unpacking the archive.

After that the archive can be deleted: the certificates are reproducible from
`(ledger row, recipe)`, which is exactly what the table preserves.

## The gluing-and-transport checkpoint

Artifact: `R3333_K58_Lean_gluing_and_transport.zip` (6.7 MiB), cumulative patch
`k58-lean.patch` (5,751 lines) against `e62d8ab`.

**Reproduced here.** Patch applies; the K60 catalogue is reused from the earlier
build; `./build.sh` compiles **45 K58 modules with 0 errors and no `sorry`**,
and the 30 axiom lines in the log are all within
`[propext, Classical.choice, Quot.sound]`. The two marking obligations are no
longer premises:

| theorem | was | now |
| --- | --- | --- |
| `K58.familyPlacementCover` | geometric premise | **proved** |
| `K58.rawCover` | — | **proved** |
| `K58.rawTransportCover_of_plans` | finite premise | **proved** |
| `K58.frozenCover_of_transports` | conditional | **proved** |

The declared counts match the independent ones: 41 plans summing to 190,736 raw
placements and 77,557 omitted transports, against 113,179 retained.

**Replay.** `run_replay.py --plan 0` checked 28 families, 852 raw placements and
544 omitted transports in 77 s, matching the plan-0 row of their
`kernel-status.json` exactly. The full replay (1,764 families, 1,588 generated
modules) was started here; it is the step that closes `K58.Replay.frozenCover`.

## The gap this exposes

The 45 Lean modules contain **no clause, CNF, DIMACS or cardinality notion at
all** (checked by search). `RealizesCase` asserts that a colouring satisfies the
case's signed **unit** clauses under a vertex and colour permutation:

```lean
def RealizesCase (G : EdgeCol (Fin 58) 4) (C : ExpandedCase) : Prop :=
  ∃ (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)), ∀ u ∈ caseUnits C, ...
```

The SAT campaign refutes the **CNF**, which is base + units + extra clauses
(per-arm thresholds, `s_crit ≥ 2M − 57`, support tables). Applying `AllUnsat`
therefore needs one more lemma:

> a genuine colouring realising a case's units satisfies that case's extra
> clauses.

That is the over-constraint question from the original review. The audit settled
it computationally — 592,023 sender-count vectors, support tables derived from
the classification — but nothing formalises it. It is the analogue of the K60
development's `Core.coloring_satisfies_formula`, and until it exists the Lean
theorem is "a counterexample satisfies some case's units", not "a counterexample
satisfies some case's CNF".

This is now the shortest statement of what remains on the formal side.
