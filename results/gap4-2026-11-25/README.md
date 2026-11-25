# Correction (2026-11-25, second revision): the rows close bare, and the families are a cost

Read this before the rest. The gap-four pilots are unsatisfiable and **plain kissat refutes
them in about a minute with no added constraints at all**:

| formula | clauses | verdict | time |
| --- | ---: | --- | ---: |
| bare pilot (UUU 0684ba38, sha `85aea7fc…`) | 171,455 | UNSAT | **41 s** |
| row's own certified CNF (`--dense`) | 196,994 | UNSAT | **44 s** |
| pilot + B | 188,405 | UNSAT | ~50 s |
| row CNF + A + B | 413,249 | UNSAT | ~50 s |
| pilot + A + B + C | 355,565 | UNSAT | 2–3 min |

Every model of a pilot is a triangle-free 4-colouring of K58, so A, B and C hold in every
model of every pilot (**Theorem E**): adding them cannot change a verdict, and on this
evidence they only add clauses. Swarm member m1 measured bare against augmented on the same
row seven times and bare won every time, by up to 6.6×, on 48% of the clauses; a controlled
twin of the UUU pilot (same placement and marked cell, only `root_kinds` differing, row
`e792ec35`) closes bare in 20 s.

So the earlier framing in this file -- "one elementary constraint closes the row" -- is
wrong twice: the row closes without the constraint, and with it the proof is slower. The
earlier UNKNOWNs on these rows came from solver caps of 30–70 seconds, not from difficulty.
What survives from the constraint work: the four statements are true and now
machine-checked in Lean (`five_bound`, `card_nb_le_sixteen`, `familyB`, `familyC`,
`dual_five_bound`, `exact_pattern`), and every closure certificate in this file is valid --
just not the cheapest route to it.

Practical consequence: 13,154 gap-four rows at 40–60 s each is roughly 180–220 CPU-hours,
about 15–18 hours on 12 cores, using the solver the campaign already has. The wall profiles
are the opposite case; see `results/gap4-2026-11-25/` batch logs and the (15,15,14,13) test.

# Row 0684ba38 (gap four, `UUU-`) is UNSAT

The first closed row of the 13,154 gap-four rows, and the first row this campaign has closed
without historical evidence. **The bound does not move**: this is one row of 31,751 open, and
the closure is of a sub-case, not of $R_4(3)\le 58$.

Row `0684ba380d0659cb756d081bfd111a1a7be6882ede00458548288370f5048f01`: family profile
$(15,15,15,12)$, root kinds `UUU-`, arm 0, mark position 1, marked size 15 kind `T`,
root position 4, placement $[6,11,0]$, charge 11. Ledger status `OPEN`, branch 442.

## Result

Let $P$ be the bundle's pilot CNF for this row (`.scratch/k58par/campaign/gap_four_UUU_442.cnf.gz`,
sha256 `740a3d3dcc1e25e10a5bda5745cf57163857b2d800e9018553266192dfe4a6a3`, raw
`85aea7fce5df2cb9bd3eda9ed8ea85c5e612383f7dbfb063694e2ac2d3e01261`, `p cnf 15613 171455`).
It is `host(58) + units(family, placement) + the charge-11 counters`, clause for clause.

Adding three **implied** constraint families gives a formula that is **UNSAT**:

| formula | clauses | sha256 |
| --- | ---: | --- |
| pilot | 171,455 | `85aea7fc…1261` (raw) |
| pilot + A + B + C | 355,565 | `e0ecfa7fcf8c5997cdc77497eff45ae806e403cb01fbeb60c25b2ed19f543ed8` |

* kissat 4.0.4: `s UNSATISFIABLE`
* CaDiCaL 3.0.1: `s UNSATISFIABLE` (independent solver, same CNF)
* DRAT: 48,197,098 bytes, `drat-trim … -c` prints **`s VERIFIED`**
  (5,272 of 355,565 clauses in core, 321,914 of 685,327 lemmas, 18,226,859 resolution steps)

Since the pilot is a relaxation of the row and the three families are theorems about any
triangle-free 4-colouring of $K_{58}$ with this root profile, **the row is UNSAT**.

## The three families

Write $A_0 = N_0(r) = \{1,\dots,15\}$, $A_1 = \{16,\dots,30\}$, $A_2 = \{31,\dots,45\}$,
$A_3 = \{46,\dots,57\}$, $x_c(a) = |N_0(a)\cap A_c|$, $m(y) = |N_0(y)\cap A_0|$. All three
facts use only: no monochromatic triangle, and the two counts $R(3,3)=6$, $R(3,3,3)=17$.

**A. $x_c(a)\le 5$ for every $a\in A_0$ and $c\in\{1,2,3\}$.**
For $y\ne y'\in N_0(a)\cap A_c$: $\chi(yy')\ne 0$ (else $a,y,y'$ is monochromatic) and
$\chi(yy')\ne c$ (else $r,y,y'$ is, since $y,y'\in A_c$). So $N_0(a)\cap A_c$ is
2-coloured with no monochromatic triangle, hence has at most $R(3,3)-1 = 5$ vertices.

**B. $d_0(a)\ge 15$ implies $x_c(a)\ge 4$ for every $c\in\{1,2,3\}$.**
$N_0(a)$ has all internal colours in $\{1,2,3\}$ (colour 0 on $y,y'\in N_0(a)$ would make
$a,y,y'$ monochromatic) and contains no monochromatic triangle, so it is a triangle-free
3-coloured complete graph on $d_0(a)$ vertices; a 3-colouring of $K_{17}$ always has a
monochromatic triangle, so $d_0(a)\le 16$. In a triangle-free 3-colouring every colour
degree is at most 5 (a colour class of size 6 would be a triangle-free 2-colouring of $K_6$),
and the three colour degrees of $r$ inside $N_0(a)$ sum to $d_0(a)-1\in\{14,15\}$; they are
exactly $x_1(a),x_2(a),x_3(a)$. Three numbers $\le 5$ summing to 14 or 15 are each $\ge 4$.

**C. $m(y)\le 12$ for $y\in A_1\cup A_2$.**
The arm carries a $T/U$ template whose three colour classes have degrees 4 and 5, so $y$ has
4 or 5 colour-0 neighbours inside its own arm; $d_0(y)\le 16$; hence $m(y)\le 16-4 = 12$.

The same three statements hold for every gap-four row (they never mention the placement), so
the recipe is row-independent; only the pilot changes.

## The implication chain

1. Pilot $\subseteq$ row. The pilot's `host(58)` is "one colour per edge" plus "no
   monochromatic triangle", true of any colouring; its 503 units are exactly
   `gluing.units(family, placement)`; its counters define `flag_a <=> d_0(a) >= 15` and then
   require at least 11 of the 15 flags — the row's charge-11 obligation. Everything else the
   row's certified CNF adds (the dense `tables` and `total_critical` restrictions) only makes
   the row stronger. Audit: `audit_pilot.py` in the swarm's m5 directory rebuilt the pilot as
   `base(58) + units + extra`, `171455 = 134995 + 503 + 35957`, no difference at any index.
2. A, B, C are implied by the row (proofs above).
3. Therefore a colouring satisfying the row satisfies the strengthened CNF, which is UNSAT.

## Reproduce

```sh
zcat .scratch/k58par/campaign/gap_four_UUU_442.cnf.gz > pilot.cnf        # 85aea7fc…
python3 tools/gap4/strengthen.py pilot.cnf strong.cnf                   # e0ecfa7f…
kissat -q --time=3600 strong.cnf strong.drat                            # s UNSATISFIABLE
drat-trim strong.cnf strong.drat -c                                     # s VERIFIED
cadical -q strong.cnf                                                   # s UNSATISFIABLE
```

`tools/gap4/strengthen.py` rebuilds `strong.cnf` bit for bit from the pilot; it rebuilds the
pilot's flag variables with the same sequential counter the bundle's `campaign/gap_four.py`
uses, and the rebuilt counter clauses were checked to be a subset of the pilot's (0 missing).

## The sharp form: family B alone closes the row

B is the only family needed. `pilot + B` is 188,405 clauses, built by
`python3 tools/gap4/strengthen.py pilot.cnf out.cnf --families B`; kissat and CaDiCaL both
return UNSAT, and drat-trim prints **`s VERIFIED`** on a 53,514,003-byte proof
(5,342 of 188,405 clauses in core, 354,053 of 742,105 lemmas, 21,016,020 resolution steps).
So the row is closed by one elementary statement: *a critical vertex sends at least four
colour-0 edges into each of the other three arms*. No use of the K15/K16 classification, no
search, no counting.

## Ladder boundary (measured after the closure)

m1's level L2 -- the pilot minus the 11,480 triples entirely inside A1 u A2 u A3 -- is
**SAT** (kissat, 23m59s), so the all-outer triangle clauses are not what closes the row;
family B is. L1p + family A alone is also SAT.

## Transport: one row, not many

All 149 `UUU-` rows have pairwise distinct frozen unit sets up to vertex and colour
permutation (swarm member m6, re-verified: 149 distinct unit sha256, 149 isomorphism classes,
networkx VF2 agreeing). The same run reports all 13,154 gap-four rows and all 83,440 rows of
the profile as singletons. So a certified refutation closes exactly its own row; the batch
below is per row, and the recipe (not the result) is what transports.

## Framing correction (verified 2026-11-25)

The two pilots of the block are the same formula up to their units: the UUU pilot
(0684ba38) and a TTT pilot (0013b1f1) have 170,935 non-unit clauses that are **equal as
sorted lists**, and their 520 unit clauses differ in 151 entries only. Every model of a
pilot is a triangle-free 4-colouring of K58, so family B holds in **every** model of
**every** gap-four pilot. Consequently B cannot change satisfiability:

> the recipe closes a row exactly when that row's pilot is unsatisfiable.

B is a proof aid, not the semantic reason. The semantic content is that the pilot is
UNSAT; B is what makes that provable in minutes rather than not at all. The same holds for
A and C. (Found by swarm member m2, re-checked here by rebuilding both pilots.)

If a pilot ever comes back SAT, no implied family can close that row, and the lever is the
row's own `total_critical`: at least `2*45-57 = 33` of the 45 vertices of A0 u A1 u A2 must
be senders, of which the pilot keeps only the arm-0 half. That path is untested.

## TTT rows (the 13,005-row group)

Two certified, by the same recipe and the same `tools/gap4/strengthen.py`:

| row | marked size | CNF sha256 | verdict | time | DRAT |
| --- | ---: | --- | --- | ---: | --- |
| 0013b1f1… | 15 | `e603f44ccbf2e663…` | UNSAT | 269 s | 176.0 MB, `s VERIFIED`, proof sha `0d521ca1…` |
| 027fe1f8… | 16 | `a230bdc50f1f422d…` | UNSAT | 27 s | 32.5 MB, `s VERIFIED`, proof sha `f9b0dccc…` |

Proofs deleted after hashing. So the `T` templates and the marked set do not obstruct the
recipe; `UUU` and `TTT` pilots are the same formula up to units, as above.

### Third TTT row and the handoff tool

`001567f8…` (marked 15) is also UNSAT: 99 s, 105.8 MB DRAT `s VERIFIED`, CNF sha256
`d0e7f247788323fe…`, proof sha `58efb9b8318b011f…`. Three of three TTT rows certified
(269 s, 27 s, 99 s).

`tools/gap4/add_families.py` appends A and B to **any** row CNF built by the campaign's
encoder, for any profile and arm (same edge numbering, fresh counters for the flags). On
row 0684ba38's own certified CNF -- `host + 503 units + dense threshold`, 196,994 clauses
-- it gives 413,249 clauses, 33,585 variables, sha256 `77faf2a9e37008a3…`. That run removes
the pilot from the argument: if the row's own clause set plus A and B is UNSAT, the closure
rests only on the two elementary lemmas and the encoder's output, not on the pilot being a
relaxation.

### Machine-checked chain

Swarm member m4 formalised the two lemmas in Lean 4 + Mathlib: `five_bound`,
`card_nb_le_sixteen`, `familyB`, `familyC`, `dual_five_bound`, `exact_pattern`, all
compiling in 2.8 s with no `sorry` and depending only on `[propext, Classical.choice,
Quot.sound]`, with `R(3,3)=6` and `R(3,3,3)=17` as explicit hypotheses. The repo's Lean core
already proves both Ramsey facts, so the chain can be made unconditional. `exact_pattern`
also shows no single-vertex sharpening of B exists: A+B+flag pin the pattern to `(5,5,5)` or
a permutation of `(4,5,5)`.

### The strong form: the row's own CNF closes

`tools/gap4/add_families.py` on row 0684ba38's **certified row CNF** -- `host(58) + 503
units + dense.marked_threshold(tables=True, total_critical=True, full_root=False)`,
196,994 clauses, built by `tools/pb/balance.py --dense` -- gives 413,249 clauses and
33,585 variables, sha256 `77faf2a9e37008a33e3c6a7e1fba47fd71a45781444ef219a1989f270e00fa0d`.

* kissat: `s UNSATISFIABLE` in about 50 s
* DRAT: 55,491,309 bytes, `drat-trim -c` prints **`s VERIFIED`**

So the closure no longer rests on the pilot being a relaxation of the row: the row's own
clause set plus families A and B is already contradictory. The only inputs are the
campaign's encoder output and the two elementary lemmas, which are machine-checked in Lean.
It is also *faster* than the pilot route (50 s against 2-4 minutes), so this is the form to
hand to the campaign's 12-core batch.

## The tiers, measured (2026-11-25)

Every row below was built with `tools/pb/balance.py --dense` (or the bundle's pilot) and
solved bare, no added family, by kissat 4.0.4 under `nice`.

| profile | open rows | charge | object | verdict | time |
| --- | ---: | --- | --- | --- | ---: |
| (15,15,15,12) | 13,154 | 11 | pilot, 171,455 cl | UNSAT | 41 s (certified) |
| (15,15,15,12) | 13,154 | 11 | row CNF, 196,994 cl | UNSAT | 44 s |
| (15,15,15,12) | 5,982 | 9 | row CNF, 199,526 cl | UNSAT | 52 s |
| (15,15,15,12) | 1,030 | 3 | row CNF, 196,946 cl | UNSAT | 39 s |
| (15,15,14,13) | 7,732 | 1–3 | row CNF + A + B, 371,324 cl | UNKNOWN | 20 min |
| (15,15,14,13) | 7,732 | 1 | row CNF, 173,594 cl | running | — |

So the whole (15,15,15,12) profile — 20,166 open rows — is refuted by plain solving at a
median of about 45 s (sweep mean over 18 certified rows: 46 s). That is roughly
250 CPU-hours, about a day on 12 cores, using the shipped solver and no new machinery.
The small profiles are the opposite: a charge-1 row of (15,15,14,13) does not close in
20 minutes even with the families, and the families are entailed by the row anyway, so
they cannot close it. Difficulty tracks the row's charge, not the profile: charge 9 and 3
rows fall in under a minute, charge 1 does not fall at all in this budget.

Practical recipe for the handoff:

    python3 tools/pb/balance.py ROW_ID row.cnf --dense
    kissat -q --time=600 row.cnf row.drat          # expect ~45 s in (15,15,15,12)
    drat-trim row.cnf row.drat -c                  # s VERIFIED

No patch to the bundle is needed: the row CNF alone is UNSAT in this profile.

## Batch status

`tools/gap4` recipe, one pilot per row, `--families ABC`, proof + drat-trim per row,
proof deleted after hashing (log: `.scratch/gap4/batch/cert_{A,B}.tsv`). At the time of
writing: 30 rows UNSAT with `s VERIFIED` proofs plus the pilot, and the sweep continues.

## What this does and does not say

* One row of the 13,154 gap-four rows, and of the 31,751 open rows. The other 148 `UUU-` rows
  and the 13,005 `TTT-` rows each have their own pilot; the three families are shared, so the
  natural next step is the same recipe on those pilots.
* It does not touch the seven small profiles, the nine charge-15 rows of $(15,14,14,14)$, or
  the 7,012 open rows outside the gap-four block.
* $R_4(3)$ stays in $[51,62]$.
