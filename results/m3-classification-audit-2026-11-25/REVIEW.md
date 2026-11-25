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
