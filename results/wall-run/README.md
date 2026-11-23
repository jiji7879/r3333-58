# The wall run and the partition proof, checked here

Package: `attachments/let-s-try-and-wcbj/K58_wall_run_and_partition_proof.zip`
(23.3 MiB), unpacked at `.scratch/wall/K58_wall_run_and_partition_proof/`.  Its
`previous/` directory is exactly the earlier `K58_twisted_partition_screen`
package, so this one is that plus the new exclusion layer.

## The run (throughput, not attack)

`wall-run.tsv`: **412 rows, all OPEN** — 405 parents (the 381 rows of
`(15,14,14,14)` plus 4 sampled rows from each of the other six wall profiles) and
the 7 unrestricted uniform children — at a five-second / 20,000-conflict cap each,
**671.5 solver CPU seconds** in total.  No case closed, no certificate produced.

## The result: the twisted uniform partition family is empty

The 3,093 labelled partition designs of a 14-arm (blocks of 5, 5, 4 sharing
zero-sets) were reduced to 138 with a local join, then 116 after the previous
package's two-vertex screen.  This package adds a sharper necessary condition — for
every sender `a` and each of the other two arms `H`, some `x ∈ H` has a zero edge to
`a` (at least four do), and `x`'s colour vector to the fixed `B` part must be
realisable under an embedding into `T⁻` or `U⁻` — and reports **116 of 116 excluded**:
1,624 labelled joins, **1,528 new DRAT proofs**, plus the 88 of the previous layer.

`python3 verify.py --drat-trim .scratch/satcheck/bin/drat-trim --workers 2` was run
here: **exit 0 in 3 min 24 s, output identical to `REPLAY.txt` line for line**,
ending `VERIFIED 1624 labelled joins, 1528 new DRAT proofs.` and
`Completely excluded partitions: 116 of 116. Remaining: []`.

So the answer to "which partition designs survive" is **none**.  That closes the
whole §4 line of work — the 3,093-partition family cannot occur in a branch object.

**What carries it is the computation, not the prose.**  The README's counting
argument concludes "at most one zero-set occurs five times per arm, and three classes
cover at most 5+4+4 = 13 vertices", but nothing there excludes an arm with four or
more distinct zero-sets, which would cover 14 without difficulty.  The gap does not
matter for the conclusion, because the exhaustive exclusion is what establishes it;
it matters if anyone tries to extend the argument by hand to a weaker family.

## The queue filter

`cube-comparison.tsv`: on the same ten-pin cube for each of the seven uniform
children, the stock runner made 10 solver calls (4 OPEN, 3 restricted cubes certified
UNSAT) and the screen rejected **all seven with 0 solver calls**.  The three
`VERIFIED_CHILD_UNSAT` rows are *restricted* cubes, not the unrestricted children,
which stay OPEN.

Not shipped in `k58-solver.zip` yet: a filter that skips work could hide a witness if
its premise were wrong.  With this replay the premise is verified for the 1,528
certificates, so wiring it in is now a mechanical step.
