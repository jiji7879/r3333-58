# Outstanding m3/d9 review: rejected pending finite-artifact repair

The report was not accepted. Nothing in this note is a row-closure claim.

Checked independently:
- `geng -q -t -d5 -D5 16` has 388 outputs and the listed `g16.txt` hashes match
  the member's `SHA256SUMS`.
- The n=16 degree reduction, complete split encoding, and exact vertex+colour
  backtracking implement the advertised mathematical statement.
- `registry140.jsonl` has 140 distinct IDs and hashes, with the expected
  70/56/14 TU/TT/UU and 14/70/56 charge partitions; all 140 rows say `full_root=true`.
- Fresh regeneration of the anchor true-scope formula gives 67,894 threshold clauses,
  203,323 clauses in total, and hash
  `089598a0581a95a69d2531d1916258db766b7ff974f6b61575e220d0806842e2`,
  matching the registry rather than REPORT.md's 67,219.
- `RealizesFamily` does include `w G r <= H G r`, so the prior fifth deficient-root
  interpretation really was mistaken under the row's semantic scope.
- The corrected reciprocal hash in the report has 64 hex digits and matches disk.

Reasons `Classified 15` is not accepted yet:
1. The documented filter command `python3 certpipe.py 15 surv15.txt` cannot rebuild the
   survivor table: `certpipe.py` has no CLI or `has_alpha6`, and no filter implementation
   occurs in any shipped Python file. Supply and independently reproduce the exact
   1,021,416 input -> 7,145 survivor computation.
2. `drive.py` deletes the final CNFs and DRAT traces, so `classified15.json` retains
   hashes rather than replayable proof bytes. Supply final proofs or a deterministic
   full regeneration and independently verify all 7,144 no-split certificates and the
   final 72-blocking-clause certificate, not merely examples.
3. Correct the 67,219/67,894 prose mismatch.

The full fresh n=16 regeneration completed in **71 s**. It processed all 388
candidates, replayed every terminal certificate, found the same single colour-0 graph
with a split, and obtained 72 splits = 12 U + 60 T with no exception or failure.
Every per-graph final CNF/proof hash is identical to the member's JSON. Outputs:
`classified16-independent.json` (SHA-256
`56246b439819f4aa351d76d6d65dbc18b3e29a710fb6a6ed7b4fce799a1185c7`)
and `classified16-independent.log`. **`Classified 16` is independently established as
a finite computational certificate.** The
`Classified 15` rejection does not invalidate that result or the useful true-root
semantic correction.

## Resolution of the repaired submission — accepted

The repaired artifact supplied exactly the missing evidence, and the full
independent replay passed:

- `alpha5.py check`: 1,014,271 independent-6 exclusion witnesses, 7,145 survivors
  without an independent 6-set, and the full 1,021,416 input partition, 0 failures
  in 50.80 s (`repair-alpha-check.log`).
- `certify.py verify 16`: 388 graphs, 460 iterations, 72 splits, 0 failures in
  51.99 s (`repair-cert16-verify.log`).
- `certify.py verify 15`: 7,145 graphs, 7,217 iterations, 72 splits, 0 failures in
  879.23 s (`repair-cert15-verify.log`).
- An independent manifest audit matched the exact distinct input graph sets and
  required one terminal UNSAT per graph, with no truncated SAT-only record
  (`repaired-manifest-coverage.json`).

The 12 U + 60 T split totals, exact vertex+colour backtracking and corrected
67,894-clause anchor were confirmed. **The repaired `Classified 15` certificate,
`Classified 16`, the true-root registry and the finite placement-orbit bookkeeping
are accepted.** `RealizesKey`/RawTransportCover and the Lean mapping to
`gluing.units` remain open; no frozen row or profile was closed.

The final package checksum has two ancillary defects only: a stale duplicate
`./PROOF.md` digest and a prose manifest line without a valid digest. They do not
affect the independently rebuilt CNF chains or replayed DRAT proofs and are recorded
in `repaired-file-hashes.log` rather than hidden.
