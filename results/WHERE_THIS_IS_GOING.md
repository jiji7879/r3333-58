# What the end goal is, and what these bundles do toward it

Written because the person asked. Every number below is from a delivered artefact or a verified
computation in this repository.

## The end goal

**`R_4(3) ≤ 58`** — no triangle-free 4-colouring of `K_58` exists. The published interval is
`[51, 62]`; a `K_58` colouring would give `R_4(3) ≥ 59`; refuting all 113,179 frozen cover rows gives
`≤ 58`.

## Why it cannot be done row by row

Measured, repeatedly:

| attempt | result |
| --- | --- |
| 12 s, 60 s, 70 s, 300 s on wall rows | 0 closed of every sample |
| 1 h at 200 M conflicts, four profiles | 0 of 4 |
| 2 h 8 m on a full core, 170,229,433 conflicts | UNKNOWN, 45 GB of proof |
| 20 exact-total instances at 58 vertices, 10 M conflicts each | 20 of 20 inconclusive |

At 21 GB of certificate per search-hour, the wall is not a budget problem. 11,585 rows would need
roughly 500 GB *per row* at the depth measured.

## So the only route is bulk exclusion

Close many rows at once by proving a **structural hypothesis impossible**, where that hypothesis is
shared by a whole family of rows. That is what every bundle since `K58_partition_branch_exclusion`
does. The unit is not a row but a **cover**: a multiset of supports on one arm, with multiplicities,
consistent with the uniform fully-sending branch.

## The arithmetic that makes it a plan

Inside the uniform fully-sending branch of `(15,14,14,14)`, arm by arm:

| step | covers | source |
| --- | ---: | --- |
| fourfold-light covers, total | **56,588** | census |
| − fivefold heavy support | −5,990 | fourfold-light bundle |
| − heavy multiplicity (4,4,1,1) | −31,150 | double-four bundle |
| **remaining** | **19,448** | |
| partition-cover shape | → **0** | partition-cover bundle |

And the geometry breakdown in the double-four summary shows the family is not homogeneous:

| exceptional-sender geometry | covers | covers with a join to `A` |
| --- | ---: | ---: |
| 2+2 | 30,888 | 18,492 |
| 2+3 | 250 | 197 |
| 3+3 | 12 | **0** |

So `3+3` is already dead, `2+3` is nearly dead, and `2+2` is the bulk.

Each exclusion removes blocks of tens of thousands at once. That is the difference between this and
searching: search closes nothing at any budget; this closes 31,150 covers with one local theorem.

## What is missing, and it is the crux

A cover census gives **necessary conditions on one arm**. A surviving cover still has to glue to the
other two arms, and the two-arm layer does not help: every instance of `root + A + B` under the
uniform-child constraints is **satisfiable** (1,180 of 1,180, verified independently). So driving the
census to zero would not by itself close the branch — the surviving covers are all realisable on two
arms, and the obstruction must come from the **third arm** or from a global count.

That is exactly where the campaign's other verified facts point: the density of exclusions is
one-arm (covers, partitions, supports) and two-arm (star family: nothing), so the next bite has to be
three-arm.

## What would count as help, ranked

1. **A three-arm condition with bite.** m4's disjoint-zero-set condition — at least `10 − g(x)`
   other-arm vertices must meet `Z(x)`, violated by every random layer yet satisfiable on a witness —
   is the only joint constraint with measured bite so far.
2. **Collapsing the remaining 19,448 covers to few geometries.** If the survivors fall into a small
   number of shapes, the gluing problem becomes finite and attackable. The `2+2` dominance suggests it
   might.
3. **A global count that does not factor.** Everything tried so far (tickets, codegrees, degree sums)
   is an identity or a theorem of the instance and adds nothing.

## The honest position

The programme is coherent: a finite ledger that shrinks by tens of thousands per theorem, every
exclusion certified. It is not close. 19,448 covers remain, the branch closure needs a third-arm
argument nobody has, and four or five sibling branches remain after that. `R_4(3)` stays in
`[51, 62]` until all of it is done.
