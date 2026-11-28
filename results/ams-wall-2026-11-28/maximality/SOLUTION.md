# Pure-kernel configurable maximalisation

## Result

`ConfigurableMaximal.lean` formalises and Lean 4.33.1 kernel-checks the
configurable-edge maximal-colour normal form used by
`tools/duggan/maximal_normal_form.py`.  This is a general theorem about
physical `K58.EdgeCol` colourings and an outside-dependent suffix predicate.
It is not a theorem about full/pinned MCF, a DIMACS byte assembly, or solver
performance.

The main proved equivalence is

```lean
theorem normalForm_equisatisfiable (c : Fin k) (es : List (V × V))
    (S : EdgeCol V k → Prop) (hS : OutsideDependent es S) :
    (∃ G, TriangleFree G ∧ S G) ↔
      (∃ G, TriangleFree G ∧ S G ∧ ∀ e ∈ es, NormalAt G c e)
```

Here `NormalAt G c (u,v)` means that `G.col u v = c` or there is a third
vertex `w`, distinct from both `u` and `v`, with
`G.col u w = G.col v w = c`.  `OutsideDependent es S` says precisely that
`S` transfers between two colourings whenever all entries outside the
undirected edges in `es` agree.  `EdgeCol` already supplies a single colour
for every ordered entry and symmetry, so no separate exactly-one hypothesis is
lost.

## Proof checked by the kernel

For an edge `uv`, `recolour G u v c` changes that undirected entry to `c` and
leaves every other entry unchanged.

1. **Safe step.** If no third vertex forms a two-edge `c`-path between `u`
   and `v`, the new colouring is triangle-free.  A new monochromatic triangle
   must use the changed edge; its other two edges are unchanged, and their
   common third endpoint would give the prohibited path.  The theorem also
   records that any non-`c` colour in the new colouring was present on the same
   entry before recolouring.  Formally this is
   `triangleFree_recolour`; it needs no off-diagonal hypothesis.
2. **Monotonicity.** Recolouring to `c` retains every old `c`-entry
   (`recolour_preserves_c`).  Consequently every old two-edge `c`-path and
   every established `NormalAt` condition persists (`twoPath_mono` and
   `normalAt_mono`).  This is why processing one edge cannot invalidate an
   earlier edge.
3. **Sequential construction.** `step` leaves an already-normal edge alone
   and otherwise performs the safe recolouring.  `normalise` processes the
   supplied list from left to right.  Induction proves triangle freedom,
   `c`-colour preservation, agreement on every entry outside the list, and
   normality of every listed edge at the end
   (`triangleFree_normalise`, `preservesColour_normalise`,
   `normalise_apply_of_not_mem`, `normalAt_normalise`).
4. **Suffix and equivalence.** `normalise_suffix` applies the explicit
   outside-agreement hypothesis to preserve `S` with the same suffix witness.
   Taking the normalised colouring proves the forward implication; dropping
   the extra conjunction proves the reverse implication.

The CNF witness semantics is separated into two small theorems.
`WitnessBinding left right y` is the conjunction of the meanings of

```text
-y left
-y right
y -left -right
```

and `witnessBinding_iff` proves that this is exactly
`y = true ↔ left = true ∧ right = true`.  For all witnesses indexed by `W`,
`fresh_witness_disjunction` then proves

```lean
(xuv = true ∨ ∃ w, y w = true) ↔
  (xuv = true ∨ ∃ w, left w = true ∧ right w = true)
```

Taking `W` to be the subtype of third vertices gives the long maximal-normal
form clause.  No DRAT consequence of the original formula is asserted: the
result is existential normal-form equisatisfiability.

## Exact retained-row controls

Repository HEAD inspected: `bb0544cfdc508c5e33de0855604ce90ee37978c8`.
The only target context is row
`06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`,
profile `(16,16,14,11)`, charge 7, configurable arms 2 and 3, target colour 0.
The retained identities were read and recomputed successfully:

* parent `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae`;
* working CNF `39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38`;
* RUP/CAS prefix `dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3`;
* existing augmented MCF CNF `8615e01a066ee43098451312857574f446961eab0e29c1f1e076b21672577fc8`.

`artifact_identity.json` records a fresh whole-byte prefix/count check.  The
parent and augmented headers are respectively `p cnf 19533 184335` and
`p cnf 26589 205629`.  After removing each header, the augmented bytes start
with exactly the parent clause body.  The following suffix has exactly 21,294
clauses.  There are 126 rules, each with 56 third-vertex witnesses, hence
7,056 fresh variables and `126 * (3 * 56 + 1) = 21,294` clauses.
The accepted build metadata hash is
`45e5203eb3d85996e2e1c3cdc73ac6e556edc9c649cbec3ff3ce0b7bfb92c6e0`.

No SAT query or DRAT/RUP proof was generated in this direction, so there is no
new query or proof hash to report.  The historical accepted pilot had original
and augmented both OPEN at one million conflicts and is not reused here as
SAT/UNSAT evidence or as a favourable performance claim.  No new CNF
performance run or wall decomposition was attempted.

## What remains before using an augmented UNSAT proof on this row

The generic theorem is proved, but its actual-row CNF instance is deliberately
not claimed.  A complete use still requires all of the following bindings
against the hashed DIMACS:

1. materialise the 126 ordered pairs as `es` and prove that the host
   exactly-one/symmetry/no-triangle clauses yield the `EdgeCol` model used
   above;
2. instantiate `S` with the **entire actual non-host suffix and its auxiliary
   assignment**, and prove `OutsideDependent es S`, not merely cite the
   builder's disjoint-variable assertion;
3. bind each of the 56 `left`/`right` literals and each fresh `y` to the
   corresponding physical path proposition, including freshness, total and
   disjoint variable allocation, and the exact `ClauseSat` interpretation of
   every emitted clause;
4. verify that the formula assembled in Lean is byte/hash-identical to the
   augmented CNF whose proof is checked;
5. for a physical-colouring row exclusion, separately finish the already
   documented guard/criticality, all-profile support, total-allocation and
   frozen-unit semantic bridge.  The ordinary parent is a relaxation: its
   UNSAT can transfer only after the relevant assembly; a SAT model does not
   establish the semantic row.

Thus the precise remaining blocker is not the normal-form combinatorics.  It
is the exact DIMACS-to-`EdgeCol`/suffix assembly, together with the previously
identified physical-row bridge.

## Reproduction and verification

Run from this directory:

```sh
./build.sh
```

This compiles `ConfigurableMaximal.lean`, produces
`ConfigurableMaximal.olean`, and runs `Check.lean`.  `build.log` and
`check.log` capture the successful commands.  The axiom report for the main
theorem is exactly `[propext, Classical.choice, Quot.sound]`;
`witnessBinding_iff` uses no axioms, and the witness disjunction uses only
`[propext, Quot.sound]`.  A source scan finds no `sorry`, `admit`, `axiom`, or
`native_decide` in the new Lean modules.  Input source hashes and hashes of
the new module/object are in `SHA256SUMS`.
