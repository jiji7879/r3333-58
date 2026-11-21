# Hard tail — the 20 `(16,15,15,11)` cases

Source: `R3333_K58_16_15_15_11_verified.zip` (458,078,256 bytes, Git LFS oid
`a2ba0b4f5628d7cfa66684786719fd65caad0164d43e5077bdea40e0b5b4b054`), pushed to
the connected repository and pulled here through the LFS batch API. The local
copy and the extracted tree were deleted after this record was made; the object
remains recoverable from the remote while the LFS object survives.

## Verified here

`python3 verify.py --hard hard.txt` on the extracted archive, with python-sat
1.9.dev22, zstd and a C compiler:

```
20 complete branch certificates accepted          (11 m 55 s)
```

All 20 statement lines in `verification.log` are the verifier's own output,
one per case, each naming the case id it accepted.

## What the 20 are

All 20 are ledger rows with `status = OPEN` and profile `(16,15,15,11)` — the
whole `(16,15,15,11)` part of the incoming `hard.txt`. The recipe recorded for
every one is

```json
{"tables": true, "total_critical": true, "full_root": true}
```

i.e. the **stronger** retry-tier encoding, which asserts `H(r) ≥ w(r)` directly.
That matters for the Lean bridge: the marking lemma proves exactly `w G r ≤ H G r`
(`RealizesFamily` carries it), so for these cases the extra clause set is the
case hypothesis rather than a consequence of it.

Evidence types: 9 direct certificates (`kind: core`, an UNSAT core on a subset
of vertices) and 11 cube-and-conquer splits (`kind: binary_cover`, 6 to 17
leaves), each leaf refuted separately and the split exhaustiveness checked by
the verifier.

## What is kept, and why

`BINDING.jsonl` — one row per case: `id`, `recipe`, `parent_cnf_sha256`,
`kind`, `leaves`, `core_clauses`. **7,664 bytes** for 20 cases, against 458 MB
of archive.

This is the part the Lean side cannot reconstruct. The Lean case list carries
case identities, and the CNF for a case is generated from `(ledger row,
recipe)` — but the ledger records no recipe. Without this table the parent
formula of each case cannot be tied to the Lean object.

## Integration note

These are **split** certificates, not single DRAT proofs of the parent. The
existing evidence pipeline (`cover_evidence.py`, `verify_parallel.py`) expects
one DRAT per case and would reject them. Admitting them needs either a direct
parent proof or a release format that carries a split with its own verifier.
The `AllUnsat` premise only needs "the parent is UNSAT", which the split
argument does establish; the bookkeeping is what needs extending.

## The remaining queue

`hard-next.txt` in the archive holds 20,157 ids: the incoming 20,185 minus the
20 verified here and minus 8 already certified in the incoming ledger.
