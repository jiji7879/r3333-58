# Two 300-second whole-row trials

## Outcome

Both intended runs exhausted their 300-second wall-clock limits with **OPEN**.
Neither proves UNSAT or SAT, no frozen row is closed, and no Ramsey bound is
established. No conflict cap was imposed.

| parent | engine | exact input SHA-256 | conflicts | measured wall s | user CPU s | result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `0404…`, forward-11/reverse-11 plus 590 replayed exact-11 exclusions | Kissat 4.0.4 | `271c2a1d1b7564bfff538bf994f0b25b3c2f9e82aa4ed5bec638e868303e8b56` | 5,781,153 | 300.043 | 299.421 | OPEN |
| `0093a6b3…`, full first-tier row plus existing cuts and reverse H>=10 | CaDiCaL 2.1.2 | `ad2c39bbf68b16f9539d1f31f3e3f7fc67aed09da29562d3404a8ed19f62935b` | 3,706,681 | 300.011 | 299.264 | OPEN |

The first parent is the **unreduced** `0404` CNF in
`.ultramath/smwxbvh79/m2/work/h11-certified/parent.cnf` (20,580 variables,
226,600 clauses). The old one-million-conflict baseline used a root-reduced
variant. Therefore its conflict count and wall time are not a like-for-like
speed comparison.

The second parent is `.ultramath/smwxbvh79/m4/out/0093-H10.cnf` (18,844
variables, 177,613 clauses). Its prior conflict cap was one million, reached
in 72.77 wall seconds. This run reached about 3.706 million conflicts without
closing the row. Difficulty is not evidence that it is UNSAT.

Maximum process RSS was approximately 43 MB for Kissat and 124 MB for CaDiCaL;
both fit comfortably on the VM. Their full solver logs and launch receipts are
copied beside this file (see `SHA256SUMS`).

## Launch failure accounting, not proof evidence

A defective first launcher wrote no solver output because an output directory
was absent. Subsequent CaDiCaL launch attempts incorrectly used 25-second
foreground tool timeouts; one further attempt used a 300-second tool timeout,
allowing no time for the runner to save its receipt. Those attempts were aborted
before becoming certified runs. They delayed the CaDiCaL run and prevented a
clean parallel-benchmark comparison with the original sequential Kissat job.
The completed CaDiCaL run used a 330-second tool timeout, longer than the
solver's own proper 300-second clock, and returned a normal code-0 OPEN receipt.

The small local logs of those failed starts remain under
`.scratch/wall-row-300-2026-11-26/`. All their unfinished DRAT prefixes were
explicitly removed. The two completed `result.json` files record
`unfinished_trace_deleted: true` as well. **Only the two completed runs in the
table above count toward the 300-second result.**

There was no model to decode or promote to a physical K58 colouring.
