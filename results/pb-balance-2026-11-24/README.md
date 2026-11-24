# Perfect balance on K58

A good colouring of K58 has d_0+d_1+d_2+d_3 = 57 at every vertex. **Perfect
balance** is d_c(v) in {14,15} for all v and c; since 14+14+14+15 = 57 this says
exactly one colour has degree 15 at each vertex and the other three have 14.

> This decides a sub-case only. The bound `R_4(3) in [51,62]` does not move.

## Which rows are relevant

The frozen cover (`.scratch/k58/case-ledger.jsonl.gz`, 113,179 rows) pins the
degree profile of one root vertex. A row with a part <= 13 has a vertex of degree
<= 13 already, so perfect balance is incompatible with it. So perfect balance
selects exactly the rows with `family.profile == [15,14,14,14]`: **381 rows, all
of them OPEN**. Of these, 308 have `root_kinds[0] = T` and 73 `U`; 352 have
`marked_size = 15` and 29 have `marked_size = 16`.

## Lemma 1 (hand proof): the 29 `marked_size = 16` rows are dead

The ticket pin in `gluing.units` fixes `q = groups[arm][mark_position]` to have
colour `arm` to every vertex of the marked set and a colour other than `arm` to
every vertex outside it. When `marked_size = 16` the marked set has 16 vertices,
and `q` is colour-`arm` adjacent to all of them, so

    d_arm(q) >= 16,

while perfect balance requires d_arm(q) <= 15. So every row with
`marked_size = 16` is excluded under perfect balance, with no search.

Checked instance (`c5eff016e42f...`, marked_size 16): vertex 6 has 16 forced
colour-0 neighbours, namely 0, 16-20, 30-34 and 44-48 - the root plus the three
five-sets of the marked placement. Reproduce with
`tools/pb/pincheck.py`, which recomputes the forced-true and forced-false
counts per (vertex, colour) for all 381 rows:

    dead by forced degree >= 16 : 29
    dead by forced degree <= 13 : 0
    alive (need a solver)       : 352

For `marked_size = 15` the same pin forces exactly d_arm(q) = 15 under balance,
and the other 42 edges at `q` must then split 14/14/14 over the other three
colours.

The pin at `q` covers **all** 57 edges at `q` (16 positives, 41 negatives), so
`d_arm(q) = 16` is forced exactly, not merely bounded below. In all 29 rows the
ticket vertex `q` lies outside the marked set - otherwise the count would be 15 -
and the 29 split 21 `T` / 8 `U`; the 352 split 287 `T` / 65 `U`.

**Why 381 is the whole list.** Under perfect balance a row is dead as soon as one
of its vertices has a pinned degree outside {14,15}. The root alone kills every
other profile: each of the 11 profiles of the cover has a part <= 13 or a part
>= 16 except `(15,14,14,14)`, so the 381 rows are the only ones a perfectly
balanced colouring could satisfy. (Running the same count on the other profiles is
a sanity check on the counting, not a second route: 4,561 of the 83,440
`(15,15,15,12)` rows die on a forced degree >= 16, and all 16,173
`(16,15,15,11)` rows die.)

## Status

| statement | rows | how |
| --- | ---: | --- |
| dead under perfect balance | 29 | Lemma 1, hand proof |
| open under perfect balance | 352 | `tools/pb/balance.py` adds `d_c(v) >= 14` for all 232 (v,c) pairs to the row CNF |

`tools/pb/balance.py ROW_ID OUT.cnf --balance` builds one; the control without
`--balance` is the frozen row. One row is 146,276 variables and 407,904 clauses
with balance, against 6,612 and 135,304 without it.

**Which CNF is "the row", and why it matters.** `gluing.host` + `gluing.units` is
a *relaxation*: the certified row CNF is `host + units + dense.marked_threshold`
(`tables=True, total_critical=True, full_root=False`), and on row
`325a259ab5fd...` the threshold is 74,555 clauses - 210,068 clauses in all against
the relaxation's 135,304. Rebuilt here through `tools/pb/balance.py --dense`, the
clause set matches that certified instance exactly: same 25,672 variables, same
210,068 clauses, zero differences either way. So

- **UNSAT of the relaxation transfers** to the row, and to the row under perfect
  balance, which is the direction that would close anything;
- **SAT of the relaxation decides nothing** - the row's threshold constraints may
  still kill it;
- the instances the runs above use are the relaxation, so a timeout or an UNSAT
  there says nothing about the 352 rows unless it is UNSAT.

With `--dense --balance` the same row is 165,336 variables and 482,668 clauses,
which is the honest size of the thing a verdict on the row would have to decide.

`tools/pb/balance_selftest.py` checks the at-least-14 gadget in **both**
polarities and checks the edge-literal map against the frozen encoder's own.
Run 2026-11-24: eight checks, all ok, literal map 0 mismatches.

`tools/pb/pincheck.py` is the search-free half: it builds no CNF and counts the
unit clauses of each row, printing the forced window per (vertex, colour).

## Next

The 352 survivors are one solver verdict each. The first instance being tried is
row `5da5b4ca2d16...` (146,276 variables, 407,904 clauses with balance); the
control without balance is the same row at 6,612 / 135,304 and is a wall row, so
the question the run answers is whether perfect balance is the missing
propagation, not whether the row closes.
