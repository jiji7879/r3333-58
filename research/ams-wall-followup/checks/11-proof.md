# Independent K58 frontier certificate audit

## Outcome

The retained parent-to-working interface is now certificate-ready and independently
proved equivalent at the CNF level. All 5,445 additions in the exact 183,180-byte
CAS stream pass a from-scratch forward RUP check with all 5,130 deletions ignored.
Two native `drat-trim` builds independently report `s DERIVATION` with zero RAT
lemmas. A separate strict binary parser applies every addition/deletion to the
ordinary parent and recovers **exactly** the `working.cnf` clause multiset:
184,650 clauses, comprising the 184,335-clause parent plus 315 distinct clauses.
The stream has no empty addition and is not a refutation.

A fresh, sequential stock-Kissat 4.0.4 attempt on all five retained leaves used
10,081,254 conflicts in 600.270 elapsed seconds (489.834 child CPU seconds).
Every leaf remains **OPEN** at its 120-second cap. Therefore this work supplies
no leaf UNSAT certificate, no whole-parent CNF UNSAT proof, and no proof about
physical colourings.

Target and immutable inputs:

* row `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`,
  profile `(16,16,14,11)`, charge 7;
* parent `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae`;
* working `39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38`;
* CAS/RUP prefix `dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3`;
* five-leaf cube file `7785697399b5540c889c5d489af4c22165cf840f71eec125beeb483209917049`.

All inputs were copied into `inputs/` before use. The comprehensive machine-readable
receipt is `results/summary.json`.

## What the derivation proves, and what it does not

Let `P` be the ordinary parent and let the binary stream contain additions `A_i`
and deletions. `scripts/independent_rup.py` checks every `A_i` by unit propagation
against `P` and all earlier additions. Ignoring deletion records only enlarges
this clause database, so a successful check is stronger than required for the
original stream. RUP soundness gives `P ⊨ A_i` by induction. The independent
active-multiset replay then shows that the final active formula is exactly `W =
working.cnf`. Since `W` contains every parent clause and every extra clause of `W`
is entailed by `P`, **P and W are logically equivalent**, not merely equisatisfiable.

Consequently, an ordinary leaf proof produced on `W ∧ Q` can be prefixed with the
CAS derivation and replayed against `P ∧ Q`, where `Q` is written as explicit
unit clauses. If every cube in an exact cover had such a verified refutation,
parent UNSAT would follow. The present prefix has no empty clause, and no such
leaf set was obtained.

The five cubes are independently checked as a cover without solver trust. Over
their four split variables `{1014,1413,1417,1421}`, all 16 assignments satisfy
exactly one cube. This agrees with the separate full-binary-tree audit in
`checks/frontier-audit.json`.

## Fresh leaf searches and exact hashes

The solver was the binary in `dist/k58-massive-solver.zip`, version Kissat 4.0.4,
SHA-256 `b77de62fb1945d2ffab165b1f05e25c9e8ae7fc43de3a4fb8346fc2c9954097f`.
Each call used seed 0, eager binary proof output, a 120-second solver timer and
a 4,000,000-conflict cap; time was reached first in every case. Searches were
fresh processes with unit-clause cubes, not incremental or failed-assumption
status. These runs are not a matched performance A/B against CaDiCaL and imply
nothing about SAT or UNSAT.

The table gives the original-parent query hash / working query hash / discarded
unfinished-trace hash. Full receipts and sizes are in `results/summary.json`.

* `[-1413,-1014]`: 2,674,371 conflicts;
  `03e5037d80e5025c7c5291db17794f28528d3dfc5481c51ce13f3e75e24d5083` /
  `1ffc1eb44b7876b84cf720afc99336d8b6d4b3cc3fa73b7bc6e348d14de5e1a8` /
  `bb01fc6a9294ce601502c84143aaaa24776cffbd5fca919caf52dd5353835f07`.
* `[-1413,1014,-1421]`: 2,026,551 conflicts;
  `2cf1056ae4013a3862c68bda2d9654bdbfeb8854ddeaf45f9be533a368366497` /
  `13ab8fd3a6e7492e52dbceae9db317eed6a21132d658373c150f5de1674912b4` /
  `d642fca84290733cd0340c8173553f586ea4131645d1697fba7cbe7bdddd363e`.
* `[-1413,1014,1421]`: 1,801,502 conflicts;
  `203ccce0f865817926c35c280a322dabe42a673f2805b3feb47ed683d34b1898` /
  `6153d24a4f8355c22963bda93d24c6db9eb0e82eb3339e900475e9bd9f398c43` /
  `b8c3d7d17f9aac6bf21816ec027c4a4a15bc6881951c01dd447bf559c4c2bb4d`.
* `[1413,-1417]`: 1,753,335 conflicts;
  `0063e5efb96a3b9ea5f47ea038898dc5d34ac6cc661297ea5f9323599a9b565d` /
  `b02bdad1b719a4f5e333437f407643c180c222e15b73bf60811dc2c1795cf6ec` /
  `9d6642ababbe95a83f6360e2a5c0bbb304804ca9963e83811d23895a356e482a`.
* `[1413,1417]`: 1,825,495 conflicts;
  `211d409efef1ad3310d6eafc852def19b5ac920ceb95e0bb7324c09cb644ee1b` /
  `a9bfe21761f9792cc119573b6fd11bc51a7e8e7f44d3d77864017b835843c6da` /
  `90c0b010f89a4c1e5a55c70c959840d975cfd9b2321c9a117ab4202b67c56114`.

Every log contains exactly `s UNKNOWN`. `scripts/audit_run.py` independently
recomputes all ten CNF query hashes from the retained parent/working files and
cubes, checks the logs and conflict counts, and verifies that no `leaf.drat` or
normalized proof remains. The incomplete traces (260,539,124 to 445,103,523
bytes, each below 1 GB) were hashed and deleted and are not certificate evidence.

## Strict certificate controls

`scripts/run_frontier_kissat.py` accepts a real leaf UNSAT result only after:

1. consuming the complete CAS+leaf binary streams and requiring a final, fully
   terminated added empty clause;
2. streaming additions-only normalization, never `-w` and never suppressing a
   malformed record;
3. replay against exactly original parent plus cube using `-i -U -t 300`;
4. return code 0, exactly one `s VERIFIED`, no warning/error/`NOT VERIFIED`, and
   proof-read byte count equal to the actual normalized file size; and
5. the same rules with the independently built second checker.

Known K6 positive proof passes both checkers; a K5/wrong-query control rejects.
A particularly important negative control removed only the final zero byte of
the valid 94-byte K6 binary proof. Both checker builds returned 0 and printed
`s VERIFIED`, while claiming to have read 94 bytes from the 93-byte file. Both
are rejected here: the independent streaming parser rejects the missing final
zero, and the native byte-count equality check fails. Thus status text alone is
explicitly insufficient. The CAS derivation alone also fails the refutation
parser because it has no empty addition. Logs and all hashes are in
`checks/controls/summary.json`.

## Precise remaining blocker

The tree and parent-to-working prefix are no longer unverified bookkeeping. The
missing mathematical/computational objects are five ordinary refutations of the
exact original parent plus their respective cubes. None was emitted by this
fresh Kissat pass. Longer or different searches remain experiments, not evidence.
This is a bounded search result together with a completed prefix proof audit,
not a claim that the leaves cannot be solved.

No DIMACS/Lean full-parent semantic assembly was attempted here. Even a future
complete CNF UNSAT cover would still be only a proof of the ordinary relaxation
until physical criticality guards, all P4/C5 support membership, allocation,
unit meanings, and exact Lean/DIMACS assembly are proved. SAT, OPEN, or timeout
would not supply a physical model or row closure.

## Reproduction

Run `bash reproduce.sh` from this directory. It verifies input/tool hashes,
rechecks the exact cover and retained run receipts, repeats both native derivation
replays, runs the independent RUP proof and controls, and recomputes the summary.
The 10-minute solver experiment is not rerun; its exact runner is
`scripts/run_frontier_kissat.py` if a fresh separately capped experiment is wanted.
