# Direction 6 — the exact physical/emitted bridge for the retained parent

Member m1, swarm smx0er1f6. Repo HEAD at time of work: `1c4d7f29665db8f23443733c7e3d2ab0df1b458e`
(a descendant of the `e856d75` in the brief; `git rev-parse HEAD` at the start of my first
command showed `1c4d7f2`). Nothing outside `.ultramath/smx0er1f6/m1/` was written; no solver
was run, no CNF was edited, no production file touched.

## Verdict-sized scope statement

The question was: can the 16 emitted atoms of a concrete sender be *derived* as the
T16-pinned coordinates that `lean/K58/SupportTransport.lean` assumes, or does the bridge stop
at a named missing fact?

Answer: the coordinate question is **closed, kernel-checked, for all fifteen senders**.
The atom of slot `j` of sender `18+k` is literally

    hostVar (1+j) (18+k) 1        (j < 16, k < 15)

i.e. the colour-1 edge between the *j-th arm-0 label* and the sender label — so the emitted
coordinate order is the arm-0 block order, and `SupportTransport`'s `er` is **forced**, not
chosen. The remaining obligations collapse to three, each named and each narrower than the
four gaps listed in the repository's own docstrings (see §5).

## Files

| file | lines | content |
|---|---|---|
| `EmittedBridge.lean` | ~250 | 17 theorems: atom decode, physical evaluation, the bridge to `SupportTransport`, the guard-counter decode, count ⇒ degree ⇒ `PinnedArm` |
| `TargetUnits.lean` | ~150 | 16 theorems: the retained key's plan data and that its own frozen units *are* the root's T16 pinning and the colour-1 root edges |
| `olean_dump.txt`, `dump.lean` | receipt | source-vs-olean numeral cross-check |
| `hashes.txt` | receipt | sha256 of both Lean files |

Re-run (sequential, ~8 s total, both exit 0, standard axioms only):

    cd <repo> && export LEAN_PATH=$PWD/lean:$LEAN_PATH
    lean .ultramath/smx0er1f6/m1/EmittedBridge.lean    # 200217e0560888dadca9446617998e42889d825265186654b12eb73817b04d8f
    lean .ultramath/smx0er1f6/m1/TargetUnits.lean      # c9f65bb0605972c78e4a6c1d75bf95153402f7b290f2a976c8b62f8726976041

Every `#print axioms` in both files reports only `[propext]`, `[propext, Classical.choice,
Quot.sound]` or (two) `[propext, Quot.sound]`. No `sorry`, no `native_decide`, no new axiom,
no `set_option` beyond `maxRecDepth`/`maxHeartbeats` for `decide`.

## 1. What the emitted atoms are (kernel-checked)

The retained key is `targetKey`: plan row 29, profile `(16,16,14,11)`, kinds `TU--`,
degree thresholds `[1,7,15,12]`, arm 1, mark position 0, root position 7, second block
15 vertices twisted. So the root is `0` and the arms are the label blocks

    arm 0 = 1..16 (degree 16, kind T)     arm 1 = 17..32 (16, U)
    arm 2 = 33..46 (14, -)                arm 3 = 47..57 (11, -)

`EmittedBridge.rowAtoms_val` / `rowAtomsList_val` (by `decide` on the emitted table):

    rowAtoms k j = hostVar (1+j) (18+k) 1                       (k : Fin 15, j : Fin 16)

so sender `18+k`'s 16 atoms are the colour-1 edges `(1,18+k) … (16,18+k)`. The independent
Python decode of the same numerals from `lean/K58/TargetSuffix.lean`'s source text agrees, and
the shipped olean's table equals the source table for all 15 senders (`olean_dump.txt`).

`EmittedBridge.realized_rowAtoms` (`realizedValuation_hostVar`): for the repository's own
physical valuation `realizedValuation G e p`,

    realizedValuation G e p (rowAtoms k j) = decide (G.col (e (1+j)) (e (18+k)) = p ⟨1⟩)

which is exactly `SupportTransport.support_mask_mem`'s conclusion
`decide (G.col q (er.symm j) = 1)` when `q = e (18+k)` and `er.symm j = e (1+j)`.

## 2. The bridge itself (kernel-checked)

* `emitted_mask_of_pinned` : hypotheses are exactly `support_mask_mem`'s (triangle-free, the
  sender joined to the root in colour 1, `PinnedArm G q 1 n t` with `n ∈ {15,16}`, the root
  arm-0 T16 pinning in the coordinates `er`) **plus** the two label identifications
  `e (18+k) = q`, `e (1+j) = er.symm j` and the palette gauge `p 1 = 1`. Conclusion: the 16
  emitted atoms of sender `18+k` are one of the 112 catalogue masks.
* `emitted_sender_step_ready` : the emitted `senderStep` of row `k` is therefore `.ready` at
  `realizedValuation G e p` (via `SenderReady.sender_family_ready`). No coded premise, no
  guess about coordinate order.

The palette gauge `p 1 = 1` is a genuine gauge, not a loss: `realizedValuation G e p` is
`realizedValuation (p⁻¹-recoloured G) e refl`, and recolouring preserves `TriangleFree`, every
clause of `hostBaseCNF`, and the truth value of every signed unit. I did not formalise that
reduction; it is one sentence of set-up, and `EmittedBridge.realized_rowAtoms_refl` is the
`p = refl` form.

## 3. The guard counter is a faithful degree count (kernel-checked)

`counterList18_decode`: the 41 atoms of sender 18's guard counter are

    [hostVar (1+j) 18 1 : j < 16] ++ [hostVar 18 (33+i) 1 : i < 25]

i.e. colour-1 edges to arm 0 (16 vertices) and arms 2+3 (14+11 = 25 vertices). The 41 atoms
are `arm 0 ∪ arm 2 ∪ arm 3`. `counter18_avoids_fin` / `excludedAtoms18_disjoint`: the 17
atoms the counter does *not* read are exactly the root edge `(0,18)` and the sixteen arm-1
edges `(17,18) … (32,18)` (`excludedAtoms18_length = 17`).

That omission is harmless, and `triangle_free_third_ne` is why: two colour-1 edges of a
triangle forbid the third, so with `G.col r s = 1` and `G.col r q = 1`, no arm-1 sibling `s`
can be colour-1 adjacent to `q`. Hence

    deg G q 1 = 1 + (true atoms of the counter)

given the root edge and the label partition — the emitted guard is not merely a lower bound
but the sender's colour-1 degree minus the root edge. `deg_ge_of_counted` proves the bound
form rigorously (14 counted colour-1 neighbours + the root edge ⇒ `deg ≥ 15`), and
`sender_pinned_of_count` then gives

    Sends G q r  ∧  deg G q 1 ≤ 16  ∧  ∃ t, PinnedArm G q 1 (deg G q 1) t

using `deg_le_sixteen` (`K58.ArmPinned`) and `pin_of_named_classification` with the
order-15/16 classification carried as the explicit hypothesis `hclass` — exactly the form
`SupportTransport.support_mask_mem_of_deg` already uses. Composed in
`emitted_sender_step_ready_of_count`: if the emitted guard's count is met (a set `W` of 14
colour-1 neighbours), the *emitted support step of that sender is ready at the physical
valuation*. So the "coded counter ‡ physical `Sends`" gap is closed **at the level of the
degree test**; the identification that carries content is the count-to-`W` step (§6 R3).

## 4. The root side is frozen by the key's own units (kernel-checked)

`TargetUnits.lean`, against the retained key's plan `targetPlan = plans.get 29`
(`prof = [16,16,14,11]` and `kinds = "TU--"` are `decide`), proves by `decide` on
`rootUnitList targetPlan` itself:

* `arm0_block_units` : for `i < j < 16`, the unit
  `ColourUnit.ofEdge (1+i) (1+j) (0.succAbove (template 16 true).col i j)` is a root unit —
  the T16 template on arm 0 **in emitted label order**. That is precisely `hroot`.
* `arm0_root_units` : the root edges into arm 0 are colour 0.
* `arm1_root_units` : the root edges into arm 1 are colour **1** for all sixteen vertices
  `17..32` — so the `hqr : G.col q r = 1` hypothesis of `SupportTransport` is frozen by the
  key for every sender `e (18+k)`.
* `chain: root_units_subset` → `targetUnitCNF_mem` → `hroot_of_unit_mem` /
  `root_edge_colour_of_unit_mem` : a `FormulaSat` model of `targetUnitCNF` therefore has
  `G.col (e (1+i)) (e (1+j)) = 0.succAbove (template 16 true).col i j` and
  `G.col (e 0) (e (17+i)) = 1`, using `List.mem_eraseDups` / `List.mem_mergeSort`.

So neither `hroot` nor `hqr` is an extra mathematical assumption for the retained parent: both
are unit clauses of the parent, in the emitted coordinates. The only step I did not formalise
here is unwrapping `ColourUnit.ofEdge`'s `min`/`max` into the emitted 16-tuple of numerals and
the bookkeeping `C.key.plan = targetPlan` from `expandKey targetKey = some C`; the theorems are
stated with those as explicit hypotheses (`hplan`, the unit literal) rather than assumed.

## 5. Re-assessment of the four gaps the repository lists

`SupportTransport`'s docstring names four things it does not prove. Status after this work:

1. "the emitted atom order is the pinned coordinate order" — **closed** (§1, §2). The order is
   forced; the 16 atoms are the arm-0 labels in increasing order.
2. "a coded guard equals a physical `Sends` event" — **reduced to a count bridge plus the
   classification** (§3). The guard is an exact degree test up to the root edge, not a free
   coded premise; `SenderReady.counter_semantics_not_shape` still applies, but only because a
   valuation can satisfy the *count* while lying about the *shape* — the shape is what the
   arm pinning supplies, and that arm pinning is now derivable from the count (§3).
3. "vertex 17 plus the coded sets exhaust the senders" — **untouched** (not my direction).
4. "`ChainReady`" — **untouched**. The sequential assembly and the two final counters
   `AtLeast(15,6)` / `AtLeast(31,6)` remain the open end.

## 6. What is precisely still missing (the named minimal obligations)

* **R1 classification.** `hclass : Classified 15/16` — the Kalbfleisch–Stanton / Heinrich
  statement. It lives in `K58.Classification`/`K58.Marking`, which import `R4333Lean`
  (`replay/.catalogue/formal/src/R4333Lean`, build artefact under `replay/.catalogue/lib`,
  absent here). I therefore could **not** kernel-check `classified_15/16`,
  `critical_arm_pinned` or `KindPlan.root_plan_with_kinds` in this session; I read them at
  source. `lean/build.sh` is the intended route (it builds `replay/.catalogue/lib` first), so
  this is a session environment limitation, not a repository defect.
* **R2 bookkeeping.** (a) `expandKey targetKey = some C ⟹ C.key.plan = targetPlan`;
  (b) unwrapping `ColourUnit.ofEdge` (`min`/`max`) so that `targetUnitCNF_mem` yields the
  emitted literal `(true, hostVar (1+i) (1+j) …)`. Both are mechanical; I left them as
  explicit hypotheses rather than guess.
* **R3 the count bridge.** From the emitted counter step's semantics
  (`14 ≤ prefixCount (fun i => v (counterAtoms18 i)) 41`, cf. `SenderReady.counter_guard_true`)
  to a `Finset W` of 14 vertices, all colour-1 neighbours of the sender, on which
  `deg_ge_of_counted` applies. The list injectivity is `decide`-able through
  `counterList18_decode`; the `prefixCount`-to-cardinality step is elementary and **not**
  formalised here. This is the one remaining place where a valuation could satisfy the emitted
  guard while the physical degree statement fails.
* **R4/R5** items 3 and 4 of §5.

## 7. What this does and does not say about speed

Nothing here is a speedup and I claim none. It constrains *other* directions, and these are
inferences the coordinator should check rather than adopt:

* Deleting the arm-0 `T` units, or replacing the 41-of-14 guard by a stronger "deg ≥ 15"
  counter, is not a free "redundant constraint" removal or addition: the units are the
  `hroot`/`hqr` premises of the physical bridge (§4), and the guard's *weakness* is exactly
  what makes it a degree test rather than a shape assumption (§3). Any preprocessing pass
  (direction 2/3) that touches them must re-establish these lemmas.
* The 112-mask catalogue is order-sensitive (`SenderReady.coordinate_order_matters`), and the
  emitted order is now known to be the arm-0 label order — so an "equivalent up to
  reordering" clause-level rewrite of the support steps is *not* semantics-preserving unless
  the reordering is the identity on `1..16`.

## 8. Things I did not do

* No solver run at all: zero solver CPU, no CNF generated, no proof emitted or replayed.
* No edits outside `.ultramath/smx0er1f6/m1/`; no change to `lean/` (the two new files import
  the existing modules and live in my directory).
* No formalisation of the palette gauge, of R2(b), of R3, or of the `ClauseSat`/`caseUnitList`
  chain when `expandKey targetKey` is not known to succeed (it is not proved here that
  `expandKey targetKey` returns `some C`; every theorem that needs it takes it as a
  hypothesis, matching `PhysicalBridge.targetParent_satisfiable_of_expanded_ready`).
