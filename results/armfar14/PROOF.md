# The independent-14 bound is 4: a certified proof, and it is sharp

Member m6, swarm `smwrmwgf7`. Companion files: `REPORT.md` (status, reruns, audit),
`ArmFarFour.lean` (kernel-checked sharpness witness), `cert/` (240 DRAT
certificates + manifest), `far_*.py` (encoders and checks).

## 0. What is claimed

Throughout, `G` is a triangle-free edge-colouring of a complete graph with four
colours, `c` a colour (written `0`), `X` a finite set of vertices with **no
colour-`c` edge inside it** (a `c`-free set), and

```
armFar G X c  =  { y ∉ X : for every x ∈ X, col(y,x) ≠ c }
```

(the points "far" from `X`; kernel definition, `lean/supplement/m4/Interface.lean`).

> **Theorem (independent-14 bound).** If `|X| = 14` then `|armFar G X c| ≤ 4`.
>
> **Sharpness.** `4` is attained: `ArmFarFour.lean` proves, with axioms
> `[propext, Classical.choice, Quot.sound]` and no `sorry`, that there is a
> triangle-free 4-colouring of `K_18` with a 14-point `c`-free `X` and
> `|armFar G X c| = 4`. So `4` cannot be replaced by `3`.

This improves the kernel-checked `armFar_le_five` (`Interface.lean`; hypothesis
`14 ≤ X.card`, conclusion `≤ 5`) at exactly the point where the branch uses it,
and it is the bound the state file records as "`|armFar| ≤ 4`". The bound in that
file is **true**, but the reason given for it there ("the K59 argument's only size
input is the exchange rule on 16-sets with a 15-core") is not a proof, and I could
not turn it into one; see §4. The proof below is different: a finite exhaustion
over the two classified 15-point types, one DRAT-replayed UNSAT instance per case.

## 1. The two kernel facts the branch supplies

`lean/K58/Arm.lean` and `lean/supplement/m4/Interface.lean` already contain, axiom-clean:

* `indep_le_sixteen` : a `c`-free set has at most 16 points (`R(3,3,3) ≤ 17`);
* `armFar_le_two` : a `c`-free set with at least 15 points has at most 2 far points;
* `armFar_eq_empty` : a `c`-free set with at least 16 points has none;
* `mixture` (L1) : two colour classes of different colours meet in at most 5 points.

## 2. The extremal case `|Z| = 5` is rigid (kernel-checked)

Put `Z = armFar G X c` and suppose `|X| = 14`, `|Z| = 5`. Write `0` for `c`.

1. **`Z` has no `0`-triangle.** Three points of `Z` pairwise joined in colour `0`
   would be a monochromatic triangle of `G`.
2. **`Z` has no triangle in the other three colours.** If `y,y',y'' ∈ Z` are
   pairwise joined in colours `≠ 0`, then `X ∪ {y,y',y''}` is `c`-free (X is,
   and no point of `Z` has a `c`-edge into `X`) with 17 points, contradicting
   `indep_le_sixteen`. So the colour-`0` graph `H` on `Z` has a triangle-free
   complement, i.e. `α(H) ≤ 2`.
3. **Hence `H ≅ C_5`.** A graph on 5 vertices that is triangle-free with
   independent number ≤ 2 is a 5-cycle: if some vertex had `H`-degree `≠ 2`, then
   degree `0` or `1` leaves an independent triple, degree `3` forces a triangle in
   the complement, degree `4` a triangle in `H`. Equivalently, the `2`-colourings
   of `K_5` with no monochromatic triangle are exactly the twelve labelled
   `C_5`'s (12 of the 1024 two-colourings, every vertex of degree 2 in both
   colours).
   **So every `z ∈ Z` has exactly two `0`-edges and exactly two non-`0` edges into
   `Z`, and each colour class is a 5-cycle.** (This is the first statement of
   `armFar_le_five`'s argument that its own proof discards.)
4. **All five non-`0` edges of `Z` share one colour.** Let `{y,y'}` be a non-`0`
   edge of `Z`. Then `X ∪ {y,y'}` is a `c`-free set of 16 points, so (3-coloured,
   triangle-free) every one of its points has exactly 5 neighbours of each of the
   three ordinary colours (`R(3,3) ≤ 6`: a colour class carries a triangle-free
   2-colouring, so it has at most 5 points, and the three classes sum to 15).
   Applied to `y`: its counts on `X` are `(5,5,4)` with the deficient colour equal
   to `col(y,y')`. Applied to `y'` likewise. Since each point of `Z` has exactly
   two non-`0` edges and they must give the same deficient colour, walking round
   the 5-cycle shows all five non-`0` edges have one common colour `γ`, and every
   point of `Z` is **deficient in `γ`** on `X`.

Steps 1–3 are **kernel-checked**, in `ArmFarRigid.lean`:

* `armFar_five_zero_degree` : at five far points every far point has exactly two
  colour-`c` edges among them;
* `armFar_five_nonzero_degree` : and exactly two non-`c` ones.

Both compile against `ArmFarBase.lean` (a verbatim copy of
`lean/supplement/m4/Interface.lean`, needed because that file is not on
`lean/build.sh`'s import path) in 3 s, axioms
`[propext, Classical.choice, Quot.sound]`, no `sorry`, no `native_decide`. The
proof is the argument above: three `c`-neighbours of a far point either close a
`c`-triangle or give a 17-point `c`-free set (`indep_le_sixteen`), and the
non-`c` neighbours are far points of the 15-point set `X ∪ {z}`
(`armFar_le_two`). Step 4 is not kernel-checked.

So the extremal configuration is a single rigid pattern: a `0`-coloured `C_5`, a
`γ`-coloured `C_5`, five patterns `X → {1,2,3}` with counts `(5,5,4)`, each
deficient in `γ`. Nothing above is contradictory — and that is the point: no
counting or local argument excludes the case. What does exclude it lives in the
14-point structure of `X` itself.

## 3. The exhaustion over the classified 15-point types

**Input (classification).** `K58.Classified 15`: every triangle-free 3-colouring of
a 15-point complete graph is isomorphic, up to relabelling vertices and permuting
colours, to one of exactly two objects. It is kernel-checked in `lean/port/`
(derived from the pinned `R_4(3) ≤ 60` development's `k15CriticalCatalogue_complete`,
53 s at Lean 4.32.1, axioms `[propext, Classical.choice, Quot.sound]`), and
independently established by the exhaustive enumeration of
`artifacts/k3col_classification_m4.md` (nauty `geng` + DPLL over 1,021,416
candidate class graphs), which also matches the published classification
(Kalbfleisch–Stanton / Heinrich, as recorded by Tatarevic). The two objects are the
15-point induced subgraphs of the two verified 16-point templates
`artifacts/k16_template_U_aut160_m4.col` and `artifacts/k16_template_T_aut32_m4.col`
(automorphism orders 160 and 32).

**Reduction.** Let `G`, `X` be a counterexample: `|X| = 14`, `X` `c`-free,
`|Z| ≥ 5`; pick `z ∈ Z`. Then `X ∪ {z}` is a `c`-free 15-point set — `X` is
`c`-free and `z` has no `c`-edge into `X` — so its colouring on the three ordinary
colours is a triangle-free 3-colouring of `K_15`, hence, by the classification,
isomorphic to one of the two 15-point types. Therefore `X` is isomorphic, as a
coloured graph, to `(T or U) minus two points` — i.e. every `X` that has at least
one far point is one of the following 240 types. The far-point question is invariant
under relabelling `X` and under permuting the three ordinary colours, so the family
is complete:

```
for V in {U, T}:
  for {a,b} ⊆ V(V) with a < b:                       # 120 each, 240 in all
     X = V minus {a,b}, colours shifted to 1,2,3     # X is c-free
     ask: is there a triangle-free 4-colouring of K_19 with
          no 0-edge inside X and no 0-edge from Z = 14..18 into X ?
```

**Decision.** Every one of the 240 instances is UNSAT, each with a DRAT proof
replayed against its regenerated CNF (`cert/`, manifest with sha256 of both files,
`verified 240, failures 0`, 30 s wall for the whole sweep). Hence `|Z| ≤ 4`.
∎

## 4. Why this is not the proof the state file records, and what survives

The state file's justification is one sentence: *the K59 argument's only size input
is the exchange rule on 16-sets with a 15-core, and `X + a + b = 16` with
`16 = 3·5+1` gives `(5,5,5)`*. Three problems:

* the exchange rule quoted (`K58.exchange_sixteen`, `K58.exchange_fifteen`) is not
  in the tree — `grep -rn exchange_sixteen lean/` finds nothing, so it cannot be
  read, let alone checked; the record's own wording is that its 15/14 form is a
  disjunction ("either the spokes agree or both common counts are exactly 4"),
  which does not by itself forbid five far points;
* the arithmetic in that sentence is about 16-sets, while the case that survives is
  five points, a `C_5`, and five `(5,5,4)` patterns (§2) — a configuration that
  satisfies every local condition the exchange rule provides;
* §5 below exhibits a *satisfiable* sub-instance: the same 19-vertex encoding with
  the far-point requirement dropped to 4 is SAT for all 240 `X` (all 240 models
  re-verified), and the resulting extension count is ~30,000 patterns per `X`, so
  no "few extensions" counting gives the bound either.

What is true and useful: the statement holds, it is sharp, and it is now decided
rather than asserted. The price is the classification input of §3, which the
campaign already carries as a kernel-checked premise.

## 5. Exactness of the encoding, and the guards against the ERRATA failure modes

**Encoding.** Variables `v(i,j,γ)` for `i<j`, `γ ∈ {0,1,2,3}`. Clauses:
exactly one colour per pair; for every triangle and every colour, not all three
edges of that colour; the frozen colours of `X` (the template's colours shifted by
`+1`, so that the template's own colour `0` is not mistaken for the branch colour —
this is precisely the slip that produced a fake SAT in my first run); `¬v(i,j,0)`
for `i<j` in `X`; `¬v(z,x,0)` for `z` outside, `x ∈ X`. There are no cardinality,
ordering or symmetry clauses. So a model is exactly a triangle-free 4-colouring of
`K_{14+nZ}` extending the frozen colouring of `X` with `X` `c`-free and all of `Z`
far from `X`; UNSAT means no such colouring exists. Clause counts are checked
against the closed form `91 + 91 + 171·7 + C(19,3)·4 + 70 = 5325` for the 19-vertex
instances (frozen `X`: 91 units; `X` `c`-free: 91; exactly-one colour per pair:
`171·7`; triangle-free: `C(19,3)·4`; far: `70`), which is what the files contain.

**Guards.**

1. *Satisfiable side.* The same encoder at `nZ = 4` is SAT for **all 240** `X`, and
   all 240 models re-check (no monochromatic triangle, no `0`-edge inside `X`,
   exactly four far points) — `far_sanity.py`. An over-constrained encoder would
   have shown up here. The output for `X = T − {0,1}` is `far18.col`, verified by
   the repository's own `tools/verify_coloring.py`, and is the input of the Lean
   sharpness theorem.
2. *Independent reredundancy.* Every CNF is regenerated from scratch, its sha256
   recorded, and its proof replayed with `drat-trim` (240/240 VERIFIED, and a second
   regeneration reproduces all 240 sha256 values).
3. *A caught artefact of my own.* A first attempt added the (intended) constraint
   "at most two non-zero edges at each far point" but encoded "at most one"; the
   augmented instance reported UNSAT in 0.012 s, and `drat-trim -c` showed the core
   uses only 19 clauses, all of them inside `Z`. That is the signature of an
   over-constrained CNF — the failure mode of `review/ERRATA.md`. The general form of
   the addition is now generated by one function, and the guard is that the
   *satisfiable* instance (`nZ = 4`) stays satisfiable and satisfies every generated
   clause (`far_aug_guard.py`). The corrected 5-point instance is not decided by
   CDCL: UNKNOWN at 260 s and again at 270 s (cadical, proof file growing, no
   refutation); with the symmetry restriction that pins `Z` to its forced `C_5` it is
   still UNKNOWN at 260 s. So the case split of §3 is what makes the question
   tractable, and I claim nothing about the classification-free 19-vertex instance
   beyond that wall.
4. *The reduction is validated on a real object.* `far_typecheck.py` checks that the
   sharpness witness's own `X` — which does have far points — is isomorphic, up to a
   permutation of the three ordinary colours, to `T` minus two vertices (it is, in
   96 of the 240 labelled restrictions). So the case split does capture objects that
   occur, not merely objects I invented. (My first version of that checker said
   "none": it compared colours `1,2,3` of the witness against the template's
   `0,1,2` without the colour permutation, and counted the diagonal. Both slips are
   the same family as the one above.)
