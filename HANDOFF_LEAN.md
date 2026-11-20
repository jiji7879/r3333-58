# Handoff — two Lean obligations for the K58 reduction

**Audience:** a Lean-proficient session asked to finish two specific theorems.
Everything else in the reduction is already kernel-checked; these are the
remaining mathematical gaps. Do not change statements to make them easier —
if a statement looks wrong, say so and stop.

**Repository:** `jiji7879/r3333-58`, directory `lean/`. Build with `./build.sh`
(Lean 4.33.1 + Mathlib, ~15 s). Currently 31 theorems, no `sorry`, no
`native_decide`, every axiom list a subset of
`[propext, Classical.choice, Quot.sound]`.

## What is already done — do not redo it

| file | content |
|---|---|
| `K58/Basic.lean` | edge colourings; ticket bookkeeping; `sum_w_eq_sum_H`; `exists_root` (some vertex receives at least as many tickets as it sends) |
| `K58/TwoColour.lean` | `R(3,3) ≤ 6`; colour degrees ≤ 2 in a triangle-free 2-colouring |
| `K58/ThreeColour.lean` | `R(3,3,3) ≤ 17` |
| `K58/DegreeCap.lean` | `deg_le_sixteen`: every colour degree of a triangle-free 4-colouring is ≤ 16 |
| `K58/Reduction.lean` | `w_eq_sum_critical`, `H_eq_sum_armSenders`, `threshold_pigeonhole` |
| `K58/Main.lean` | `profile_sum`: Σ deg = 57, each ≤ 16 |
| `K58/Plans.lean` | the 41 frozen threshold plans and their slack inequality |
| `K58/Frontier.lean` | the eleven degree profiles; `balanced_root_arm_reaches`; `normalized_plan_arm_reaches` |
| `K58/Selection.lean` | `root_plan_arm`: **unconditionally**, a triangle-free colouring of `K_58` has a root with `H ≥ w`, a matching plan entry, and an arm of that root at the planned threshold |
| `K58/Templates.lean` | the U and T templates as objects; `template_triangleFree_15/16`; the statement `Classified n` |

Note: `Main.exists_arm_reaches` is **superseded and vacuous** — its hypothesis is
unsatisfiable at the zero degree vector, as `Frontier.original_threshold_hypothesis_impossible`
proves. `Frontier.balanced_root_arm_reaches` is the live version. Leave the old
theorem in place, marked.

---

# Obligation 1 — the K15/K16 classification

## Statement

`lean/K58/Templates.lean` already defines the objects and states the goal:

```lean
def IsoUpToColour {n : ℕ} (G H : EdgeCol (Fin n) 3) : Prop :=
  ∃ (e : Equiv.Perm (Fin n)) (p : Equiv.Perm (Fin 3)),
    ∀ i j, i ≠ j → G.col i j = p (H.col (e i) (e j))

def Classified (n : ℕ) : Prop :=
  ∀ G : EdgeCol (Fin n) 3, TriangleFree G → ∃ t : Bool, IsoUpToColour G (template n t)
```

**Deliver:** `theorem classified_15 : Classified 15` and
`theorem classified_16 : Classified 16`.

## The mathematics

`template n false` is U, `template n true` is T. U is the XOR difference
colouring of `ℤ₂⁴`: colour `x + y` by which of the three difference classes
`Δ₀ = {1,8,10,12,15}`, `Δ₁ = {2,3,7,11,13}`, `Δ₂ = {4,5,6,9,14}` it lands in.
T is U with colours 1 and 2 swapped on the 16 edges between `{1,2,8,11}` and
`{5,6,12,15}`.

The theorem is the classical classification: **Kalbfleisch–Stanton** for K16,
**Heinrich** for K15. It is true and independently verified by two different
computational routes (see *Evidence* below); what is missing is a Lean proof.

## Two routes, in order of expected cost

### Route A — port the K60 development (recommended first)

**Tested here, and it works.** The whole `R4333Lean` closure compiles on this
machine at its own pins: 33 modules, **32 compiled and 0 failed** (the 33rd is
`CriticalTemplatePaletteSymmetry`, not in `CriticalCatalogues`'s closure). Time:
about 20 minutes, after `lake exe cache get` pulled the 8,639-file Mathlib cache
(7.4 GB, ~10 min). The two theorems then report

```
'R4333.k16CriticalCatalogue_complete' depends on axioms: [propext, Classical.choice, Quot.sound]
'R4333.k15CriticalCatalogue_complete' depends on axioms: [propext, Classical.choice, Quot.sound]
```

So the *content* is available and kernel-clean. What remains is bridging their
definitions to ours:

* theirs: `ThreeColor`, `ThreeColorCatalogue`, `ThreeColorCatalogueComplete 16 k16CriticalCatalogue`,
  a `WeakColorEquiv` allowing simultaneous vertex and colour relabelling;
* ours: `EdgeCol (Fin n) 3`, `template n t`, `IsoUpToColour`, `Classified n`.

The bridge is: define a map `EdgeCol (Fin n) 3 → their colouring type`, prove it
preserves triangle-freeness, apply their theorem, then read off
`IsoUpToColour` from `WeakColorEquiv` and check that their `k16CriticalCatalogue`
entries are our `template n t` (they are — the audit confirmed the matrices are
bit-identical to `gluing.template`). That is adapter work, not new mathematics.

**Exact steps used to reproduce the build:**

```sh
git clone https://github.com/milostatarevic/r3333-upper-bound
cd r3333-upper-bound/formal
lake exe cache get                     # 8,639 files, ~7.4 GB, ~10 min
T=~/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lean
LP="$PWD/src"; for p in .lake/packages/*/.lake/build/lib/lean; do LP="$LP:$PWD/$p"; done
env LEAN_PATH="$LP" $T -o src/R4333Lean/CriticalCatalogues.olean src/R4333Lean/CriticalCatalogues.lean
```

(`lake build` does not work here — the package declares no `lean_lib` and ships
its own `build.py` driver. Compile in topological order of the `import` graph
with `lean -o`, as above.)

`https://github.com/milostatarevic/r3333-upper-bound` at commit
`6c3f2fd0386335321801fa4079397d4a4c1962f3` proves exactly this, in Lean, with no
catalogue-completeness hypothesis:

* `formal/src/R4333Lean/CriticalCatalogues.lean`:
  `k16CriticalCatalogue_complete : ThreeColorCatalogueComplete 16 k16CriticalCatalogue`
  and `k15CriticalCatalogue_complete`.
* Its dependency closure is 32 modules with **55 CNF/LRAT pairs**, replayed by
  `CheckedLRAT.lean` at kernel level (the LRAT importer checks definitional
  equality against the Lean-side formula before submitting the proof term).

Version skew remains: that project pins **Lean 4.32.1** and Mathlib rev
`520045ab14e26149ee970e2e617ca04b09bde5d6`; this repository is on **4.33.1**
with a different Mathlib. Two sub-routes:

* **A1.** Build their tree at their pins (a `lake exe cache get` succeeds and
  takes ~10 min, ~7.4 GB), then port the *statements* across and re-derive them
  in our Mathlib. Cheapest if the API used is stable.
* **A2.** Vendor their whole classification closure into our project at our
  pins, fixing whatever breaks. Their closure is self-contained (their CLAUDE
  notes say the classification files use no project axiom), so this is
  mechanical but potentially tedious.

Either way, the *definitions* differ: they use `ThreeColor` and a
`WeakColorEquiv`, we use `EdgeCol (Fin n) 3` and `IsoUpToColour`. Write adapter
lemmas rather than rewriting their proofs.

### Route B — prove it here from scratch

The mathematical skeleton, if A fails:

**K16.** Each colour degree is ≤ 5 (from `R(3,3) ≤ 6`, already available as
`deg_le_two_of_two_colour` composed with the restriction argument in
`DegreeCap.lean`), and the three sum to 15, so every vertex has colour degrees
`(5,5,5)`. Hence the colour-0 graph is triangle-free and 5-regular on 16
vertices. There are 388 such graphs; exactly one admits a completion into a
triangle-free 3-colouring, with 72 completions = 12 U + 60 T. The hard content
is **uniqueness of the Clebsch graph** among triangle-free 5-regular graphs on
16 vertices, which is where the K60 development spends most of its effort
(`ClebschUniqueness.lean`, `K16CatalogueFromSRG.lean`).

**K15.** Every good 3-colouring of K15 extends to one of K16 by adjoining a
vertex (the "deficient colour" argument), then apply K16 and check the deletion
maps (`CriticalTemplateDeletion.lean` there).

Realistically Route B is a multi-week project. Route A is days.

## Evidence that the statement is true

Independently verified here by two different computations (both reproducible):

* **K16:** `nauty-geng -t -d5 -D5 16` lists all 388 triangle-free 5-regular
  graphs; backtracking over each finds exactly one that admits any completion —
  72 colourings, 12 isomorphic to U and 60 to T, none outside the catalogue.
* **K15:** an exact count identity. Normalising vertex 0 to have deficient
  colour 0 and colour classes `{1..4}, {5..9}, {10..14}`, the C4 and 2K2 splits
  admit **0** completions and P4 admits 600 per labelled configuration; scaled,
  the total is 1,036,800 = 172,800 (U-minus) + 864,000 (T-minus) by Burnside —
  an exact match.
* The automorphism orders 160 / 32 / 10 / 2 and transversal vertex orbits are
  confirmed in `K58/Templates.lean`'s neighbours and in the audits.

Reproduce the K16 count: `nauty-geng -t -d5 -D5 16 | wc -l` → 388.

## Success criterion

```sh
cd lean && ./build.sh          # green
```

with `classified_15` and `classified_16` in `K58/Check.lean`'s axiom list and
printing only `[propext, Classical.choice, Quot.sound]`. **No `sorry`, no
`native_decide`, no new axioms.** `native_decide` would make this fast and is
not acceptable: it adds compiled-code trust, which is the whole point of the
exercise.

---

# Obligation 2 — the marking lemma

## Statement to prove

This is the bridge from the abstract threshold argument to the concrete case
list. In words:

> Let `G` be a triangle-free 4-colouring of `K_58`, `r` a root with `H(r) ≥ w(r)`,
> and `a` an arm of `r` whose senders reach the threshold `t` that
> `Selection.root_plan_arm` produces. Then `G` satisfies the **unit clauses** of
> one of the emitted cases for that `(profile, kinds, arm)`.

"The emitted cases" is the frozen list of 113,179, whose generators are Python
(`gluing.py`: `families`, `units`, `orbit_data`; `palette_quotient.py`;
`support_tables.py`) and whose content is: fix the root's critical arms to
literal copies of U or T, fix one sender `q` and its neighbourhood (a second
classified block sharing `r`), pin the supports to reference paths/cycles, and
record the cross-colouring as one of 600 words.

## Decomposition, in dependency order

1. **Root pinning.** If `d_c(r) ∈ {15,16}` then `N_c(r)` is a triangle-free
   3-colouring of `K_15`/`K_16`, so by Obligation 1 there is a vertex
   permutation and colour permutation carrying it onto `template n t`, with the
   palette convention "the three remaining host colours in increasing order".
   Requires Obligation 1.
2. **The marked sender.** The arm has at least `t` senders, so any set of
   `d − t + 1` positions in the arm contains one (`threshold_pigeonhole` already
   gives the count; this is the combinatorial step from "enough senders" to
   "this specific `q` sends"). Then `N_a(q)` is a second critical neighbourhood
   sharing `r`, again classified by Obligation 1.
3. **Supports.** For each other critical arm `b`, the set
   `S = N_a(q) ∩ N_b(r)` is 2-coloured with the two colours outside `{a,b}`,
   triangle-free, so |S| ∈ {4,5}; when 5 it is a C5, when 4 a P4 (never a
   C4+2C2). The 5-case follows from `R(3,3) ≤ 6`; the 4-case needs the
   classification. This is the lemma the audit flagged as unstated in the
   original bundle.
4. **Palette and orbit reduction.** Every palette relabelling of U and T is
   realised by a vertex permutation fixing a specified reference position
   (verified computationally; needs a Lean proof), which is what makes the
   fixed-palette convention sound. Then the 20,617 palette-dropped cases of the
   cover are covered by explicit symmetry witnesses.
5. **Assembly.** Compose 1–4 with `Selection.root_plan_arm` to conclude that a
   counterexample satisfies some emitted case's units.

## What "emitted case" means formally

The Python generator, not a Lean definition. **You must first decide how to
represent the case list in Lean** — that is an unavoidable design commitment and
it should be made explicitly and documented. The two honest options:

* **(i) A Lean definition** mirroring `gluing.py`'s enumeration, with a proved
  theorem that its length is 113,179 and that its elements are exactly the
  ledger's rows (compare against the frozen `case-ledger.jsonl.gz` hashes).
  Then "satisfies the units of one of them" is a Lean statement.
* **(ii) An opaque list plus a hash**: define `cases : List Case` by a
  `def` whose body is the data, derive the CNF from it in Lean, and bind it to
  the Python by comparing SHA-256 of the generated DIMACS. Cheaper, but the
  generator's *completeness* argument (that the enumeration is exhaustive)
  then lives outside Lean.

Option (i) is what makes the result a proof. Option (ii) makes it a
proof-with-a-computational-premise, like the K60 development's
`ExactInputs.AllUnsat`. Say which you chose and why.

## Realistic scale

This is the largest remaining piece and the K60 analogue took months. Its
counterpart there spans `CommonCover.lean`, `CommonCompleteD.lean`,
`CommonCompleteE.lean`, `MarkedBounds.lean`. If you are working with a time
budget, do Obligation 1 first — it is self-contained, it is needed by Obligation
2 anyway, and it is the piece with a known existing proof to port.

## What is *not* being asked

* Not the `ExactInputs.AllUnsat` premise (that is the SAT campaign, running
  separately).
* Not the CNF encoding itself in Lean — only enough to state "the units of some
  case hold".
* Not a change to any existing statement. If `root_plan_arm` or
  `balanced_root_arm_reaches` looks wrong, report it; do not weaken it.

## Verification commands

```sh
cd lean && ./build.sh                  # must be green, ~15 s
grep -rn "sorry\|native_decide\|admit" K58/   # must be empty
./build.sh | grep "axioms"             # every line a subset of
                                       # [propext, Classical.choice, Quot.sound]
```

Register new theorems in `K58/Check.lean` so the axiom check covers them.

## Context you should have

* `review/K58_CAMPAIGN_REVIEW.md` — what the underlying computational campaign
  is and what has been audited.
* `HANDOFF.md` — the whole project state, including the SAT side.
* `lean/README.md` — the current formal development.
* The full Python generators are in the handoff bundle
  `R3333_K58_LLM_handoff.zip`, mirrored at `dist/k58-solver.zip`.
