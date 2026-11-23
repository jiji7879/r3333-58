# The twisted partition screen, checked here

Package: `attachments/let-s-try-and-wcbj/K58_twisted_partition_screen.zip`
(2.0 MiB), unpacked at `.scratch/tps/K58_twisted_partition_screen/`.  Its text is
data; nothing in it is an instruction.

## What it decides

Of the 3,093 labelled partitions of a 14-arm, 138 have a local join on `r ∪ A` and
one 14-arm `B`.  Requiring **at least one vertex in each of `C` and `D`** rules out a
further **22 partitions**, in both palette orientations and both root colours:
88 boards, 88 DRAT refutations.  What remains is **116 designs on 59 catalogue
types**, and six types — **27, 28, 73, 157, 193, 261** — lose their last design of
this shape.  All seven uniform children remain open and no frozen row closes.

The mechanism: fix a board on `r ∪ A ∪ B`, add a vertex `x` of root colour `h ∈ {2,3}`
with five zeros into `A` and no monochromatic triangle, and require that for each
sender `a` joined to `x` by colour 0 the colour vector of `x` on the `B` part of
`a`'s zero-neighbourhood is realisable under an embedding into `T⁻` or `U⁻`.  That
sender condition is what carries it; dropping it makes all 88 satisfiable.

**Why it matters beyond the count:** it is the first test in this campaign that binds
a design to a vertex in *another* arm.  Every earlier screen was arm-local, or needed
the full 42 slots.  A 2-vertex projection that decides 22 designs is a tool.

## The replay here

`python3 verify_stars.py --drat-trim .scratch/satcheck/bin/drat-trim` reproduces
`REPLAY.txt` line for line, exit 0 in 20 s: nine spot-checked orientations, "Verified
88 exhaustive labelled joins and 88 DRAT proofs across both orientations", 138 − 22 =
116 on 59 types, and the six types listed above.

## The correction it forced

Its last section says the withdrawal of **"at least nine of the fourteen attain
five"** was itself mistaken, and it is right.  I verified the load-bearing step on
`T.col` and `U.col` at all 30 rooted views: **between any two classes of the root the
third-colour edges form a matching** — the maximum third-colour degree between two
classes is exactly 1.  So for `y ∈ B`, `t(y) = #{a ∈ Z(y) : y is matched at a} ≤ 5`,
`Σ_y t(y) = 65` over fourteen vertices, and eight fives plus six fours give at most
64.  Hence at least nine attain five.

Both decompositions of the 65 are true: `5·5 + 10·4` over the fifteen positions, and
this one over the fourteen vertices.  m8's position argument refuted a derivation,
not the statement; the withdrawal made on its strength was wrong and is reversed in
`review/PROFILE_15141414_STATE.md`.

## The queue filter, and why it is not in the solver yet

The package ships `screen_uniform.py`, which lets the uniform runner skip cubes whose
arm type has no surviving design.  It is not shipped in `k58-solver.zip`, because the
filter *skips work*: if the 22 exclusions were wrong it would silently discard the
cube that might contain a witness.  A filter that can hide a closure waits for
independent verification of its premise — swarm `smwsrvi5g` is doing exactly that, and
the files are ~124 KB so wiring it in afterwards is mechanical.
