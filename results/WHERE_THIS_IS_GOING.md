## CORRECTION, 2026-11-24: this programme closes ZERO rows

**Retract the framing below.** Everything in it about the cover census is accurate, but the inference
— that driving the census to zero would close the branch, and that closing the branch is progress —
is wrong, and this file led with it. The campaign encoder
(`.scratch/handoff/first_case/start.py:70`) emits **two complementary children per row**:

```python
for name, branch in [('at_most_five', [[-z] for z in flags]), ('some_six', [flags])]:
```

`at_most_five` is exactly the `m(x) <= 5` hypothesis on which the whole uniform fully-sending branch
rests. A row is decided only when **both** children are, so a refutation of that branch — however
complete — closes **0 of the 381 rows** of `(15,14,14,14)` and 0 of the 31,751 open rows. Measured
reach: **7 of 63,502 open (row, child) pairs**, 0.011 %; one row per 4,536 open rows.

And the saturated-interface machinery cannot be lifted: zero interface slack occurs at exactly nine
rows in the whole cover (all the charge-15 block of this profile), and **the next-tightest obligation
has 56 of 210 units of slack**. So the branch is not the tight corner of the cover; it is a tight
corner of 9 rows out of 31,751.

**Where the effort belongs instead.** 13,154 open rows — 41.4 % of the whole open cover — sit at
gap 4, all in `(15,15,15,12)`, and the statement they need is *"at least 11 of the 15 points of the
15-arm are critical"*. That is the nearest quantity worth building, and it is 35 times the row count
of the branch this file was written to pursue.

The census below is still correct as a census, and the exclusions are still certified. They are just
worth nothing at row level.

---

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
| − (4,3,1,1,1) and three further patterns | −18,102 | fourfold-light 18102 bundle |
| **remaining** | **1,346** on 66 roles | |
| partition-cover shape | → **0** | partition-cover bundle |

And the geometry breakdown in the double-four summary shows the family is not homogeneous:

| exceptional-sender geometry | covers | covers with a join to `A` |
| --- | ---: | ---: |
| 2+2 | 30,888 | 18,492 |
| 2+3 | 250 | 197 |
| 3+3 | 12 | **0** |

So `3+3` is already dead, `2+3` is nearly dead, and `2+2` is the bulk. The latest step enumerated
**250,986,773 joins** to remove 18,102 covers, and every one of the 1,346 survivors has a
complementary pair of supported pentagons outside the light support (1,340 with deletion sizes 6,7).

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

## Defects found in the delivered bundles (2026-11-24)

Both are harness bugs, not mathematical errors, and both were caught by running the verifiers.

1. **`K58_double_four_pentagon_exclusion`**: `verify.py` asserts every file in `evidence/` matches
   its regeneration, and fails on `unquotiented_reference.tsv` — the published table lists different
   role/cover pairs (T/590, T/1990, T/2180, T/4286) than the shipped code reproduces (T/134, T/760,
   T/1738, T/3868). Everything substantive matches (`double_four_covers.tsv.gz`,
   `board_counts.tsv.gz`, `roles.tsv`, `summary.json` all byte-identical to the regeneration), so the
   31,150 / 19,448 figures stand; one auxiliary reference table is stale.
2. **`K58_fourfold_light_18102_exclusions`**: `verify.py` line 28 passes an integer `0` as a
   subprocess argument and dies with `TypeError: expected str, bytes or os.PathLike object, not int`
   before reaching the evidence comparison. **With that one argument patched to `'0'` the check runs
   to completion: exit 0 in 27 minutes, "Every published table matches."** All 336 progress lines show
   `0 pass`, i.e. no cover survives the sender test, and both seven-set enumerations (3,255 and 681
   representative seven-sets) complete. So the exclusions themselves verify; only the harness was
   broken.

## A soundness trap worth recording: covers are multisets

Two members of swarm `smwv2qfbi` found the same error independently, from opposite ends.

**The trap.** A cover is a *multiset* of supports — the census stores masks with multiplicities and
never labels which of the 15 senders carries which support. Deciding a cover under a **fixed
sender-to-support assignment** therefore answers a strictly stronger question than the one that
matters, and can return UNSAT when the cover is realisable.

**The evidence.** m2 reports four covers (8, 11, 12, 15, with bundle join counts 48,701 / 12,252 /
306 / 156) that are UNSAT for 144 random fixed assignments — every one DRAT-verified — while a
formulation that *quantifies* the assignment (one Boolean per sender × support, one support per
sender, exact multiplicities) returns SAT on those same four covers, matching the bundle's joins.
m7 found the same thing from the encoder side: a pinned sender identification is refuted in 0.02 s.

**The consequence, which is the reason this is written down.** An unquantified sweep reports **all
1,346 open covers dead** — and that result is an **artefact**. Anyone who ran the naive sweep and
trusted it would have concluded the branch was closed and moved on.

**The honest cost of the real question**: 1,086 classes after residual symmetry (866 singletons, 200
of size 2, 20 of size 4), 2,172 instances with both templates, 19.3 % saved by symmetry. Only 54 of
the 66 roles have trivial automorphism group, so there is little more to win there.
