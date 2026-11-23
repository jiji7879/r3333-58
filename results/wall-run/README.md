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

## The queue filter is inert, and its benchmark was a budget artefact

m8 of `smwsrvi5g` audited the filter against the stock runner (second attempt, after
the first audited the wrong trigger — the package fires on **two distinct zero sets
each on five vertices of one arm**, not on all fourteen pinned). Findings, with the
decisive one verified here:

* **The stock queue is the empty cube** (`uniform.py` line 207: `[({}, {})]` when no
  `--cube` is given), so nothing is pinned and the filter cannot fire at all.
* **Where it can fire, its gain is zero.** The package's "4 OPEN of 7" comes from
  running the cube at the *parent row* budget (5 s / 20 000 conflicts). At the
  child's own defaults (12 s / 400 000) the runner closes everything: I ran
  `./k58.sh uniform --cube examples/B-5-5.json --seconds 12 --conflicts 400000` and
  got `{"VERIFIED_CHILD_UNSAT": 7}` — seven of seven, no OPEN.
* The rule's boundary: 0/1/2 pins, one fivefold set, 5+4, 4+4, ten pins on one zero
  set, 6+4, six pins and 5+5 across two arms all forward; two fivefold sets in one
  arm, 6+5 and fourteen pins are excluded.
* Operational defects in the package: a malformed cube aborts the queue before
  anything is forwarded; skipped cubes leave no record; the cube's scope is not
  checked against the selected child.

So the filter is **not shipped in `k58-solver.zip`**, and the reason is now measured
rather than precautionary: it saves nothing.

## The queue filter (original note)

`cube-comparison.tsv`: on the same ten-pin cube for each of the seven uniform
children, the stock runner made 10 solver calls (4 OPEN, 3 restricted cubes certified
UNSAT) and the screen rejected **all seven with 0 solver calls**.  The three
`VERIFIED_CHILD_UNSAT` rows are *restricted* cubes, not the unrestricted children,
which stay OPEN.

Not shipped in `k58-solver.zip` yet: a filter that skips work could hide a witness if
its premise were wrong.  With this replay the premise is verified for the 1,528
certificates, so wiring it in is now a mechanical step.
