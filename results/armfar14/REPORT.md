# Status: certified (independent-14 bound = 4, sharp) — partial on `M ≥ 7`

Member m6, swarm `smwrmwgf7`, target 3 of the profile brief ("kernel-check the two
paper proofs"). Directory: `.ultramath/smwrmwgf7/m6/`.

**Headline.** `|armFar G X c| ≤ 4` for `|X| = 14` is **true, certified, and sharp**;
`4` is attained by a kernel-checked `K_18` witness. `M ≥ 7` is **not** proved, by
anyone: I show below that the recorded chain yields at most `M ≥ 5`, and I locate the
two steps of it that fail.

---

## 1. Result 1 — the independent-14 bound is 4 (certified), and 4 is attained

**Claim.** Let `G` be a triangle-free 4-edge-colouring, `X` a 14-point set with no
colour-`c` edge inside, `armFar G X c = {y ∉ X : ∀x∈X, col(y,x) ≠ c}`. Then
`|armFar G X c| ≤ 4`. The kernel's `armFar_le_five` gives 5; 4 is the truth, and it
is sharp.

**Proof.** Written out in `PROOF.md`. Two halves:

*Upper bound* = the classification of good 3-colourings of `K_15`
(`K58.Classified 15`, kernel-checked in `lean/port/`; independently enumerated in
`artifacts/k3col_classification_m4.md`; matches Kalbfleisch–Stanton/Heinrich)
+ 240 UNSAT instances, one per `X = (U or T) minus two points`, each carrying a
DRAT proof replayed against its regenerated CNF: `cert/manifest.txt`, **240
verified, 0 failures**. Plus a hand argument (`PROOF.md` §2) showing the extremal
case `|Z| = 5` is a rigid pattern — the five far points form a colour-`c` `C_5` and
a single-ordinary-colour `C_5`, every one of them deficient in that ordinary colour.

*Sharpness* = `ArmFarFour.lean`: an explicit 18-vertex colouring (verified
independently by `tools/verify_coloring.py`) with `|X| = 14`, `X` colour-0-free and
exactly four far points, proved by `decide`. Compiles in 9 s, axioms
`[propext, Classical.choice, Quot.sound]`, no `sorry`, no `native_decide`.

**Why this matters to the campaign.** The state file uses `≤ 4` ("a bound of 4
replaces 5 in every model using it"), and the bound is correct — but the reason given
for it there does not survive inspection (`PROOF.md` §4): the quoted exchange lemmas
`K58.exchange_sixteen` / `K58.exchange_fifteen` are **not in the tree**
(`grep -rn exchange_sixteen lean/` finds nothing), and the surviving case (§2) is
locally consistent with everything an exchange rule supplies. Models may keep using
4; they should cite this certificate, not the one-liner.

---

## 2. Result 2 — `M ≥ 7`: the recorded proof does not go through (partial)

The statement is about hypothetical branch objects, so it cannot be refuted by a
witness; what I can do is check the chain. Notation: root `r`, `A = N_0(r)`, `|A| =
15`, `X` the 42 outside points with `m(x) = 5` each, `d_0(a) = 15` at every `a ∈ A`,
`μ(a,a') = |N_0(a) ∩ N_0(a')|`, `M = max_{u≠v} |N_0(u) ∩ N_0(v)|`.

**(a) "the 105 arm-pair codegrees sum to exactly 525 (mean 5), so some pair of
senders shares at least six points" — non sequitur.** The identity is right:
`Σ_{a<a'} μ = 105 + Σ_x C(m(x),2) = 105 + 42·10 = 525`, since `r` is a common
0-neighbour of every arm pair and no other arm point is. Mean 5 forces
`max μ ≥ 5`, not `≥ 6`; `μ ≡ 5` on all 105 pairs is exactly consistent with the sum,
and is exactly the all-codegree-5 family the record elsewhere says an explicit
`2-(15,5,4)` design realises ("incidence counting alone can never exclude" it, §22 of
the wall). The two sentences contradict each other; the correct one is the wall's
byproduct: **`M ≥ 5` bare**.

**(b) the "moment bound" `Σ(n_{aa'} − 4)² ≥ 294` has no source.** The exact identity
is `Σ_{a<a'} n² = Σ_{x,y ∈ X} C(|P_x ∩ P_y|, 2)` (`P_x = N_0(x) ∩ A`, `|P_x| = 5`).
The diagonal contributes `42·10 = 420` and the off-diagonal terms are *non-negative*,
so this identity gives a **lower** bound `Σ n² ≥ 420` — nothing more. Capping
`|P_x ∩ P_y| ≤ M` gives the **upper** bound `Σ n² ≤ 420 + 42·41·C(M,2)`, which can
only exclude large `M`. Combining with Cauchy–Schwarz (`Σ n² ≥ 420²/105 = 1680`) gives
`C(M,2) ≥ 0.73`, i.e. `M ≥ 2`. So no step of this form yields "some pair shares six".

**(c) the `C_x` route, recomputed.** The two derivations that *are* right:
`P = N_0(x) ∩ A` has 5 points; every `p ∈ P` has `d_0(p) − 2 = 13` 0-neighbours other
than `r, x`, so with `d(z) = |N_0(z) ∩ P|` over the 41 points of `X∖{x}`,
`Σ_z d(z) = 65`; and each pair `{p,q} ⊆ P` has both `r` and `x` among its common
0-neighbours, so `C_x := Σ_z C(d(z),2) = Σ_{{p,q}} (μ(p,q) − 2) ≤ 10(M − 2)`.
The lower bound the record quotes, `C_x ≥ 3 d_0(x) − 8 = 37` at `d_0(x) = 15`, does
**not** follow from `Σ d = 65`, `d ≤ 5`: the sharp minimum over 41 sites is
`C_x ≥ 24` (24 twos and 17 ones), and `C(d,2) ≥ 2d − 3` with 41 sites gives only 7.
With 24 the chain gives `M ≥ 5`. To reach `M ≥ 6` one needs `C_x ≥ 41`; for `M ≥ 7`,
`C_x ≥ 51`. So:

* the record's own numbers stop at **`M ≥ 6`**, not 7;
* its final step ("the `M = 6` rigidity closes it") is asserted with no derivation,
  and it is load-bearing;
* the sharp bound from the stated ingredients is `M ≥ 5`, which was already known.

**Verdict on `M ≥ 7`: open, and not reachable by the recorded chain.** This is a
correction to `review/PROFILE_15141414_STATE.md` §10 and §21 and to
`review/WALL_15141414_SWARM.md` §§21–22; it is *not* a claim that `M ≥ 7` is false.

---

## 3. Exact rerun commands

Run from the repository root unless stated. Nothing here writes inside `repo/`.

```sh
D=.ultramath/smwrmwgf7/m6

# 1. the 240-case certified exhaustion (30 s; rewrites $D/cert/ and its manifest)
cd $D && python3 far_certify.py            # -> verified 240, failures 0
        python3 far_sanity.py              # -> SAT 240, UNSAT 0, models re-checked OK 240

# 2. the sharpness witness, independently
cd $D && python3 far18_check.py            # writes far18.col
        python3 ../../../tools/verify_coloring.py far18.col

# 3. the kernel-checked sharpness theorem (9 s, needs the repo's built K58 oleans)
cd $D && LEAN_PATH="$PWD/../../../lean:$LEAN_PATH" lean ArmFarFour.lean
#   'K58.armFar_four_attained' depends on axioms: [propext, Classical.choice, Quot.sound]

# 3b. the kernel-checked rigidity of the extremal case (3 s; builds ArmFarBase first)
cd $D && export LEAN_PATH="$PWD:$PWD/../../../lean:$LEAN_PATH"
        lean -o ArmFarBase.olean ArmFarBase.lean && lean ArmFarRigid.lean
#   armFar_five_zero_degree / armFar_five_nonzero_degree: [propext, Classical.choice, Quot.sound]

# 4. the guard that the added constraints are sound (satisfiable side, 1 s)
cd $D && python3 far_aug_guard.py

# 5. the reduction validated on a real object: the sharpness witness's own X is
#    T-minus-two-points (and only that), so the case split is not empty
cd $D && python3 far_typecheck.py

# 6. the structural side facts quoted in PROOF.md §2
cd $D && python3 far_extcount.py           # extension counts ~30,000 for every X
```

`far_certify.py` regenerates every CNF from scratch, writes the DRAT proof with
`/opt/lean/bin/cadical`, replays it with `.scratch/satcheck/bin/drat-trim`, and
records the sha256 of both files. Two independent regenerations gave identical
sha256 for all 240 CNFs.

## 4. What I did not verify

* **`armFar_le_four` is not kernel-checked.** Its sharpness half and the rigidity of
  the extremal case are (`ArmFarFour.lean`, `ArmFarRigid.lean`). The upper
  bound rests on (i) the `K_15` classification — I read
  `artifacts/k3col_classification_m4.md`, `lean/port/README.md` and `PORT_NOTES.md`
  but did **not** rebuild `lean/port` (it writes into `repo/lean/port/build/`, needs
  the pinned Lean 4.32.1 toolchain) — and (ii) the 240 DRAT-replayed instances.
* **The classification-free 19-vertex instance is undecided**: `far_aug.py 5` UNKNOWN
  at 260–270 s with the sound additions A1–A3, and still UNKNOWN at 260 s with the
  forced `C_5` symmetry restriction. That is a measured wall, not a result.
* **`M ≥ 7`**: verified in neither direction. My audit checks the arithmetic of the
  recorded chain only; it does not test the statement on branch objects (none exist).
* I did not run `bash lean/build.sh` (it would overwrite `repo/lean/K58/*.olean`);
  my file compiles against the oleans already in the tree.
* Targets 1, 2, 4, 5, 6 of the brief are untouched here.

## 5. Files

| file | what it is |
| --- | --- |
| `PROOF.md` | the written proof: reduction, hand-rigidity of the extremal case, exhaustion, exactness and guards |
| `ArmFarFour.lean` | kernel-checked `armFar_four_attained` (18-vertex witness, `|armFar| = 4`) |
| `ArmFarRigid.lean`, `ArmFarBase.lean` | kernel-checked rigidity of the extremal case (`armFar_five_zero_degree`, `armFar_five_nonzero_degree`); `ArmFarBase.lean` is a verbatim copy of the supplement's `Interface.lean` so the file builds alone |
| `cert/` | 240 CNF + DRAT pairs and `manifest.txt` (sha256 of each, `VERIFIED`) |
| `far_certify.py` | the certified exhaustion driver (encoder + cadical + drat-trim) |
| `far_sanity.py` | satisfiable-side guard: all 240 `X` at 4 far points SAT and re-verified |
| `far18_check.py`, `far18.col` | the sharpness witness and its independent re-check |
| `gen_lean.py` | emits `ArmFarFour.lean` from `far18.col` |
| `far_aug.py`, `far_aug_guard.py` | the classification-free instance, its sound additions, and the guard that they preserve satisfiability |
| `far_fixed.py`, `far_extcount.py`, `far_test.py`, `far_dimacs.py` | exploration: frozen-`X` solver runs, extension counts, plain DIMACS |
| `far_witness.py` | **superseded**: the object it produces is *not* a witness (its `X` carries colour-0 edges — the first, buggy encoder). Kept as the record of that slip; `far19.col`, `far20.col` deleted. |

## 6. One process note worth passing on

My first `armFar` run "found a counterexample" — SAT with 5 far points — because the
frozen template colours were written as `0,1,2` while the branch colour is `0`, so
"`X` is colour-0-free" was silently violated. The independent verifier caught it; the
solver did not. Later, an added *sound-looking* constraint ("at most two non-zero
edges at each far point") was encoded as "at most one" and produced a 0.012 s UNSAT
whose DRAT core (`drat-trim -c`) used only 19 clauses, all inside `Z`. Both are the
`ERRATA` failure mode, both were caught by checking the *satisfiable* instance rather
than the claim: an added constraint is only trustworthy once the same code leaves a
known-satisfiable instance satisfiable.
