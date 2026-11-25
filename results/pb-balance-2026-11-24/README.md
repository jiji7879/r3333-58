# Perfect balance on K58

A good colouring of K58 has d_0+d_1+d_2+d_3 = 57 at every vertex. **Perfect
balance** is d_c(v) in {14,15} for all v and c; since 14+14+14+15 = 57 this says
exactly one colour has degree 15 at each vertex and the other three have 14.

> This decides a sub-case only. `R_4(3) in [51,62]` does not move, and no row of
> the wall has been closed.

## Which rows are relevant, and why the split is complete

The frozen cover (`.scratch/k58/case-ledger.jsonl.gz`, 113,179 rows) pins the
degree profile of one root vertex and is complete for all good colourings
(`K58.Replay.frozenCover`, kernel-checked). Under perfect balance that root has
profile (15,14,14,14), so **every perfectly balanced good colouring falls in one
of the 381 rows with `family.profile == [15,14,14,14]`** - all 381 currently
OPEN. So

    no perfectly balanced good colouring of K58  <=>  all 381 rows UNSAT.

Counts inside the 381: 308 have `root_kinds[0] = T`, 73 `U`; 352 have
`marked_size = 15`, 29 have `marked_size = 16`.

## Lemma 1 (hand proof, no search): the 29 `marked_size = 16` rows are dead

`gluing.units` pins the ticket vertex `q = groups[arm][mark_position]` to colour
`arm` towards every vertex of the marked set and to a different colour towards
every other vertex, so **all 57 edges at `q` are pinned** and `q` is never itself
in the marked set. Hence

    d_arm(q) = marked_size   exactly,

while perfect balance allows at most 15. So every row with `marked_size = 16` is
excluded, with no search.

Verified four ways, independently:

* the ticket lemma over all 381 rows (my recomputation from the frozen encoder):
  `(marked_size, pinned-in-arm-colour, total pinned edges at q)` gives
  `(15, 57, 57): 338`, `(15, 57, 71): 14`, `(16, 57, 57): 25`,
  `(16, 57, 71): 4` - so `d_arm(q)` is 15 for 352 rows and 16 for 29;
* forced-degree counting per (vertex, colour) over all 381 rows:
  `.scratch/pb/pincheck2.py` -> 29 dead by "some colour degree >= 16", 0 by
  "<= 13", 352 alive;
* a full propagation closure with balance as a rule (exactly-14 forces, 15
  placed excludes, 16 contradicts) reaches the same 29 and closes nothing else:
  `.scratch/pb/propagate.py` -> `dead by propagation 29, still alive 352`;
* `smwvchrlk/m7`'s independent pin reconstruction, which agrees literal for
  literal with `gluing.units` on all 381 rows.

Worked example: row `c5eff016e42f...` (marked_size 16) forces vertex 6 to have 16
colour-0 neighbours, namely 0, 16-20, 30-34 and 44-48. In the 15-case
(`5da5b4ca2d16...`) the same vertex has exactly 15: 0, 16-19, 30-34, 44-48,
splitting (1,4,5,5) over the arms.

## The other 352 rows are open

Perfect balance does not propagate: the closure above reaches a fixpoint with no
contradiction on all 352. They need search, and no row has ever been decided
under perfect balance (the frozen pipeline imposes no degree lower bound at all;
the only `d_c(v) >= 14` in the tree is `tools/pb/balance.py`).

    python3 tools/pb/balance.py ROW_ID OUT.cnf --balance      # one instance
    python3 tools/pb/balance.py ROW_ID OUT.cnf                # the frozen row, as a control

One row is 146,276 variables and 407,904 clauses with balance against 6,612 and
135,304 without it (row `5da5b4ca2d16`, sha256 `53e63b14...` and `b01fdca1...`).
`tools/pb/balance_selftest.py` checks the at-least-14 gadget in **both**
polarities and checks the edge-literal map against the frozen encoder's; the
control without balance is not instantly UNSAT, which is the check that the
retracted encoder of 2026-11-24 would have failed.

## Calibration: perfect balance is not vacuous

For r = 4 the balanced value - the largest n whose good 4-colouring has every
colour degree in {q, q+1} - is at least 10. Witnesses: n = 6 (exhaustively, all
138,240 perfectly balanced good colourings; 1,440 of them reciprocal, colour 0 a
6-cycle and colours 1,2,3 perfect matchings) and n = 10 (an explicit matrix,
`smwvchrlk/m2/k10_pb.col`, independently checked: no monochromatic triangle, all
ten degree multisets (2,2,2,3)). My own probe finds perfectly balanced good
4-colourings at n = 9, 10, 11, 12 and none at 13, where 13*3 is odd so a
3-regular colour class on 13 vertices cannot exist - the parity obstruction
`n*q` even.

So perfect balance is satisfiable in general, and any obstruction at 58 is a
property of 58, not of the assumption.

## Conditional structure (needs reciprocity, which PB does not supply)

`smwvchrlk/m2`: if a perfectly balanced good colouring of K_n with n = 4a+2 were
also **reciprocal** (every edge critical at either both ends or neither), then
each k_c = #{v : d_c(v) = a+1} lies in {0, 2a+2, n}; no sum of 2a+2's equals
4a+2, so one colour has k_c = n and the rest 0. At n = 58 that means colour 0 is
15-regular and the other three 14-regular - the campaign's singleton branch with
a constant critical degree. This is conditional: reciprocity is unproven and
fails at n = 50, and the K6 enumeration above exhibits reciprocal perfectly
balanced colourings, so PB does not force it. An earlier form of this theorem
posted on the board was wrong (it dropped the k_c = n case) and was retracted by
its author after an exhaustive K6 check.

## A bad citation to record

`smwvchrlk/m2` cited `attachments/see-what-you-can-yel5/K58_15141414_research_report.md`
section 4 for a decode of the row's pins. **That file does not exist** in this
repository; the only attachment supplied is `K58_PB_parallel_handoff.md`. The
decode itself is correct - I reproduced it independently - but the citation is
not.

## Status

| statement | rows | how |
| --- | ---: | --- |
| dead under perfect balance | 29 | Lemma 1, hand proof, four independent checks |
| open under perfect balance | 352 | solver; one instance run to a 40-minute cap, see below |
