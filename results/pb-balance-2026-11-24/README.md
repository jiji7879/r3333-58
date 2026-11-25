# Perfect balance on K58

A good colouring of K58 has d_0+d_1+d_2+d_3 = 57 at every vertex. **Perfect
balance** is d_c(v) in {14,15} for all v and c; since 14+14+14+15 = 57 this says
exactly one colour has degree 15 at each vertex and the other three have 14.

> This decides a sub-case only. `R_4(3) in [51,62]` does not move, and no row of
> the wall has been closed.

## The split is complete, and it costs one line

`K58.FrozenCover` (`lean/K58/Ledger.lean:27`) is

    forall G : EdgeCol (Fin 58) 4, TriangleFree G -> exists k in frozenKeys, RealizesKey G k

with `frozenKeys_length = 113179` kernel-checked by `decide +kernel` and the cover
itself proved in `K58.Replay.frozenCover` (recorded green in `PROOFS.md`; the
`ReplayGen` tree is not built in this checkout, so that one step is taken from the
record rather than re-run here). `RealizesKey` pins the root's degree profile to
the family's profile, and perfect balance forces every vertex's profile to
(15,14,14,14). Hence every perfectly balanced good colouring is realised by one
of the 381 rows - unconditionally, with no appeal to the ledger's provenance.

So closing the 352 live rows would prove that K58 has no perfectly balanced good
4-colouring, and a SAT row would exhibit one.

## Which rows are relevant, and why

The frozen cover (`.scratch/k58/case-ledger.jsonl.gz`, 113,179 rows) pins the
degree profile of one root vertex. Under perfect balance that root has profile
(15,14,14,14), so **every perfectly balanced good colouring falls in one of the
381 rows with `family.profile == [15,14,14,14]`** - all 381 currently OPEN. So

    no perfectly balanced good colouring of K58  <=>  all 381 rows UNSAT.

Counts inside the 381, cross-tabulated from the ledger: `(T,-,-,-)` arm 0 charge
15 at mark 5 gives 9 rows, `(T,-,-,-)` arm 1 charge 1 at mark 0 gives 299,
`(U,-,-,-)` arm 0 charge 3 gives 9, `(U,-,-,-)` arm 1 charge 5 gives 64; 352 have
`marked_size = 15` and 29 have `marked_size = 16`.

An independent audit (`smwvchrlk/m5`) re-derived the same completeness from the
ledger alone - thresholds `(15-1)+3(1-1) = 14 < 15` and `(3-1)+3(5-1) = 14 < 15`,
both tight; position coverage; and the enumeration counts 299/299, 64/64, 9/9 and
9-of-23 at mark position 5 - and recorded that the program which produced the
ledger is absent from the repository. That gap does not affect the argument above,
which quantifies over the Lean list rather than over the ledger file.

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

One row is 292,436 variables and 706,488 clauses with balance against 6,612 and
135,304 without it (row `5da5b4ca2d16`). Both sides of the degree window are
emitted: the lower bound `d_c(v) >= 14` for all 232 (vertex, colour) pairs and the
upper bound `d_c(v) <= 15`, which is implied by the lower bounds together with the
count over the 57 edges at `v` but which CDCL does not reach on its own - with the
lower bounds alone the same row is 146,276 variables and 407,904 clauses, and two
of the 29 ticket-pin rows ran 300 s there without a verdict. `--dense` additionally
adds the row threshold, which is what the certified rows carry; `host + units` is a
relaxation of the certified row, so an UNSAT of the relaxation transfers to the row
and a SAT of it decides nothing.
`tools/pb/balance_selftest.py` checks the at-least-14 gadget in **both**
polarities and checks the edge-literal map against the frozen encoder's; the
control without balance is not instantly UNSAT, which is the check that the
retracted encoder of 2026-11-24 would have failed.

## Where perfect balance is arithmetically impossible

Counting edges per colour, `2|E_c| = sum_v d_c(v)`. When `n-1 = 4q` exactly (that
is `n = 1 mod 4`) every vertex has degree exactly `q` in every colour, so
`2|E_c| = n q` and the order is impossible when `n q` is odd, i.e. when `q` is odd,
i.e. when **n = 5 mod 8**. When `n` is not `1 mod 4` the deficient colours move
between vertices, `sum_v d_c(v) = n q + t_c` with `t_c` the number of vertices whose
colour-c degree is `q+1`, and the parity condition is satisfiable.

So perfect balance is impossible exactly at n = 5, 13, 21, 29, 37, 45, 53, ...
(`.scratch/pb/parity.py` checks the claim for every n from 2 to 79). **Among the
orders 51..58 only 53 is excluded this way**; 51, 52, 54, 55, 56, 57 and 58 are all
arithmetically live. This corrects a report from `smwvchrlk/m6`, which applied the
uniform-degree count to K51 and K55, where no uniform degree vector exists at all
(4t = 50 and 4t = 54 have no integer solution), and to K15, K19 and K23, where the
degrees are 4/3, 5/4 and 6/5 and the count gives no contradiction.

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

## What the live rows cost

Nothing on the 352 closes at the budgets tried. Row `5da5b4ca2d16` ran 40 minutes
under Kissat 4.0.4 on a contended 4-core box on the one-sided encoding (146,276
variables / 407,904 clauses) and came back UNKNOWN with 557 MB of DRAT; rebuilt
two-sided (292,436 / 706,488) the same row is UNKNOWN after 1,430,758 conflicts at
8,521 per second with 320 MB of DRAT. So the encoding repair is decisive exactly
where a local counting contradiction exists and buys nothing here.
`smwvchrlk/m7` sampled four other live rows at 700 s each, all UNKNOWN. For comparison the 29 dead rows close in under 0.2 s each with
0.75 MB proofs, so the split between the two halves is not gradual: it is the
difference between a counting contradiction and a full 58-vertex search.

**No isomorphism reduction is available.** `smwvchrlk/m4` computed the orbit
decomposition of the 381 pinned instances: **381 classes, 381 rows** - no two rows
are isomorphic, so the 352 cannot be collapsed into a smaller set of
representatives. Each row genuinely needs its own decision.

## Status

| statement | rows | how |
| --- | ---: | --- |
| dead under perfect balance | 29 | Lemma 1 by hand, and now replay-checked UNSAT by an independent encoder |
| open under perfect balance | 352 | UNKNOWN at 700 s on four sampled rows, UNKNOWN at 40 min and 557 MB of DRAT on a fifth; no isomorphism reduction (381 classes) |

## Replay-checked certificates for the 29

`smwvchrlk/m7` built a second encoder from scratch and closed the 29 rows with
Kissat 4.0.4 text DRAT, ~0.75 MB and under 0.2 s each, `drat-trim` reporting
`s VERIFIED`. I verified one end to end here and checked that its CNF is the
right instance and not a lookalike:

* all 134,995 host clauses of `gluing.host(58)` are present (one-hot, at-most-one
  and every monochromatic-triangle clause), as sorted multisets;
* its 323 unit clauses are set-equal to `gluing.units` for that row, and among all
  381 rows exactly one has that unit set, so the CNF is that row;
* `drat-trim` on `c5eff016e42f_exact.cnf` with its proof gives `s VERIFIED`;
* the 29 UNSAT ids in its ledger are exactly the 29 rows the hand proof kills;
* three `balance=none` controls come back UNKNOWN, not UNSAT.

Caveat recorded: its own DRUP checker reports `RuntimeError('skipped')` on all 29,
so those rest on `drat-trim` plus my replay, and the checker itself is tested only
on two small instances.

## The instance and the encoding (gate check, 2026-11-25)

Two things decide whether a verdict here means anything, and both were open.

**`host + units` is a relaxation, not the row.** The certified row CNF is
`host + units + dense.marked_threshold(tables=True, total_critical=True,
full_root=False)`. On row `325a259b...` the threshold is 74,555 clauses: 210,068
clauses in all against the relaxation's 135,304, and rebuilding it through
`tools/pb/balance.py --dense` reproduces that certified instance clause for clause
(25,672 variables, 0 differences either way). So an UNSAT of the relaxation
transfers to the row under perfect balance, and a SAT of it decides nothing. The
instances recorded above are the relaxation, so every UNSAT there is a statement
about the row and every timeout there is a statement about nothing.

**The balance encoding must be two-sided.** With only `d_c(v) >= 14`, the ticket-pin
rows are UNSAT by `16 + 3*14 > 57` yet CDCL does not find it: two of the 29 ran
300 s and wrote 76 MB and 120 MB of DRAT with no verdict. The implied upper bound
`d_c(v) <= 15` needs the global count over all 57 edges at `v`, which unit
propagation does not see. Adding `at_most(15)` per (vertex, colour) - the same
formula up to an implied clause - turns each of the 29 into a 0.05 s refutation,
and `tools/pb/balance.py` now emits both sides (146,276 variables / 407,908
clauses become 292,436 / 706,502).

**The 29, closed by a third encoder.** `tools/pb/close_dead.py` builds each
ticket-pin row's relaxation, solves it with Kissat 4.0.4 and replays with
drat-trim: 29/29 UNSAT, `s VERIFIED`, 0.04-0.12 s each, 47 s in total, 23.9 MB of
proofs. `ticketpin29.tsv` holds per row the CNF sha256, the proof sha256, the
checker line and the time; artifacts are in `.scratch/pb/ticketpin29/`.

**Consequence for the 352.** The four sampled rows reported UNKNOWN above were run
on the one-sided encoding. Before reading anything into that, rebuild them with the
current `tools/pb/balance.py`; a timeout on the weak encoding is not evidence about
the mathematics.

**Two-sided does not rescue the live rows.** Row `5da5b4ca` rebuilt with both
bounds is 292,436 variables / 706,488 clauses (CNF sha256 `8aa68286…`); Kissat
4.0.4 returns `s UNKNOWN` after 1,430,758 conflicts at 8,521/s (167.9 s process
time inside a 600 s wall cap) with 320 MB of DRAT. So the encoding repair above is
decisive exactly where a local counting contradiction exists - the 29 - and buys
nothing on the 352, where the search is the full 58-vertex problem. The one-sided
40-minute UNKNOWN and this one differ in nothing that matters: both are timeouts,
and neither is evidence.
