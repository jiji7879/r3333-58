# The independent-14 bound: `|armFar| <= 4`, certified

For a triangle-free 4-edge-colouring `G` and a set `X` of 14 points with no
colour-`c` edge inside it, `armFar G X c = {y ∉ X : col(y,x) ≠ c for all x ∈ X}`
has at most four points. The kernel's `armFar_le_five` gives five; this is the
truth, and it is sharp (`far18.col`, an 18-vertex colouring with exactly four).

Member m6 of swarm `smwrmwgf7`, accepted 2026-11-22. Every number below was re-run
by the coordinator before acceptance.

* `PROOF.md` — the proof: the extremal five-point case is a `0`-coloured `C_5`
  plus a `γ`-coloured `C_5` with all five patterns `(5,5,4)` deficient in `γ`
  (kernel-checked in `ArmFarRigid.lean` up to step 3); then a finite exhaustion:
  any counterexample has `X ∪ {z}` a colour-`c`-free 15-set, hence by
  `K58.Classified 15` one of the two 15-point templates, hence `X` is a 16-point
  template minus two points — 240 labelled cases, each UNSAT.
* `manifest.txt` — the 240 `(cnf, drat)` sha256 pairs with the drat-trim verdict:
  `verified 240, failures 0`.
* `far_certify.py` — regenerates all 240 CNFs from scratch, writes each DRAT,
  replays it, records both hashes. 34 s wall.
* `far_sanity.py` — the guard that matters: the same encoder at four far points is
  SAT for all 240, every model re-checked. (An over-constrained encoder shows up
  here, not in the UNSAT run.)
* `far18_check.py`, `far18.col` — the sharpness witness; also passes
  `python3 tools/verify_coloring.py`.
* `ArmFarFour.lean`, `ArmFarRigid.lean` — axiom-clean
  (`[propext, Classical.choice, Quot.sound]`, no `sorry`, no `native_decide`):
  `K58.armFar_four_attained`, `armFar_five_zero_degree`,
  `armFar_five_nonzero_degree`. `ArmFarBase.lean` is a verbatim copy of
  `lean/supplement/m4/Interface.lean`, needed because that file is not on
  `build.sh`'s import path; compile from this directory with
  `LEAN_PATH=$PWD:$REPO/lean:$LEAN_PATH lean ArmFarFour.lean`.
* `far_typecheck.py` — the reduction is not empty: the witness's own `X` is
  `T` minus two vertices in 96 of the 240 labelled restrictions.

Rerun everything:

```sh
cd results/armfar14
python3 far_certify.py && python3 far_sanity.py && python3 far18_check.py
python3 ../../tools/verify_coloring.py far18.col
export LEAN_PATH="$PWD:$(git rev-parse --show-toplevel)/lean:$LEAN_PATH"
lean ArmFarFour.lean && lean ArmFarRigid.lean
```

Not claimed: `armFar_le_four` is not itself a kernel theorem — the upper bound
rests on the classification (`lean/port/`, itself kernel-checked) plus the 240
DRAT instances. The classification-free 19-vertex instance is UNKNOWN at 270 s
and is not decided anywhere.
