# K58 configurable-MCF arm-3 result (m6)

## Outcome

On the exact retained parent, restricting the existing safe configurable-MCF
construction to **arm 3, colour 0**, rather than arms 2 and 3 together, gives a
reproducible fixed-conflict-budget CNF-performance improvement. The optional
parent-BCP residual encoding removes another 465 suffix clauses without changing
CaDiCaL's deterministic search statistics at the tested cap.

**No run solved the parent or a leaf. Every run is OPEN at its conflict cap. No
proof stream was produced, no UNSAT/SAT certification is claimed, and no
physical-colouring or row-closure conclusion follows.** The favourable result is
CPU/propagation work at matched conflict caps, not time-to-solution.

See [REDUCTION.md](REDUCTION.md) for the complete equisatisfiability argument and
its boundary. The augmentation is not a DRAT consequence of the original parent.

## Identity and inputs

Repository HEAD was `bb0544cfdc508c5e33de0855604ce90ee37978c8`.
The unchanged baseline `dist/k58-massive-solver.zip` has SHA-256
`cc78f1d9f6f7901615b264c9ceaa3319bd152cd4caccc381a74ed742538bdb6a`.
The copied current MCF generator has SHA-256
`dbfb90714b302e1873d938a82fa2d0560203fd97dc7e7acd162bbe7033f80aed`.
The only row is `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`,
profile `(16,16,14,11)`, charge 7.

| query | SHA-256 |
|---|---|
| ordinary parent | `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae` |
| working CNF (retained identity; no splits used) | `39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38` |
| arm 2 only | `0102b5b1d0dfae01ed1f1d6e69b48e738c4f1b8fae429f46f7e70d901c759538` |
| arm 3 only | `1bb7a7823b0ceac16d303de15c204b28b11d4354ec17fcf60dba7678754ff9d2` |
| arms 2+3 | `8615e01a066ee43098451312857574f446961eab0e29c1f1e076b21672577fc8` |
| arm 3, parent-BCP residual | `31108fb9204b9e615a6396bb6239019f04307e083786db3d2b8e181f82e38daa` |
| arms 2+3, parent-BCP residual | `a43f5cac1f30300715610ff9c087167663888096a30924344eaa904aab5f81b9` |

RUP/CAS prefix identity remains
`dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3`.
It was not consumed because there were no leaf UNSAT calls. **Proof hashes:
none; proof files: none.** `results/query-sha256.txt` checks all seven CNF hashes.

## Exact variants

| variant | changing edges | added fresh variables | added clauses | total variables / clauses |
|---|---:|---:|---:|---:|
| parent | 0 | 0 | 0 | 19,533 / 184,335 |
| arm 2 | 81 | 4,536 | 13,689 | 24,069 / 198,024 |
| arm 3 | 45 | 2,520 | 7,605 | 22,053 / 191,940 |
| arms 2+3 | 126 | 7,056 | 21,294 | 26,589 / 205,629 |
| arm 3 BCP | 45 | 2,520 | 7,140 residual | 22,053 / 191,475 |
| arms 2+3 BCP | 126 | 7,056 | 20,118 residual | 26,589 / 204,453 |

The old union CNF regenerated with the exact accepted hash
`8615e01a…77fc8`. This rules out a silent generator or parent drift.

## Solver controls and matched A/B

All calls used fresh PySAT `cadical195` instances (python-sat 1.9.dev22), the
same default configuration, no cube assumptions, and the stated conflict cap.
Runs were sequential on the shared VM. CPU time and deterministic statistics
are the primary comparison; wall times are reported because shared load varied.

### Main one-million-conflict run

| query | status | decisions | propagations | solve CPU-s | solve wall-s |
|---|---|---:|---:|---:|---:|
| parent | OPEN | 2,322,342 | 371,735,517 | 61.971 | 67.385 |
| arm 2 | OPEN | 2,105,744 | 409,810,221 | 67.033 | 80.480 |
| arm 3 | OPEN | 3,745,976 | 262,186,194 | 51.828 | 74.264 |
| arms 2+3 | OPEN | 2,253,100 | 446,260,223 | 69.611 | 101.742 |
| arms 2+3 BCP | OPEN | 2,253,100 | 446,260,223 | 68.485 | 81.304 |

Against the parent in this run, raw arm 3 used **29.47% fewer propagations** and
**16.37% less CPU**. Its wall time was worse in this particular loaded segment
(74.264 versus 67.385 seconds), so this first row alone is not presented as a
wall-clock win. Arms 2 and 2+3 were worse than the parent in CPU and propagation
work; the benefit is specific to the smaller arm-3 subset, not a general claim
that more MCF is better.

### Higher-cap replication

| cap | query | status | decisions | propagations | solve CPU-s | solve wall-s |
|---:|---|---|---:|---:|---:|---:|
| 2,000,000 | arm 3 | OPEN | 8,996,881 | 399,144,507 | 120.766 | 142.264 |
| 2,000,000 | parent | OPEN | 5,463,922 | 838,419,903 | 222.721 | 225.700 |

At two million conflicts arm 3 used **52.39% fewer propagations**, **45.78%
less CPU**, and 36.97% less measured wall time. This is the strongest matched
A/B, but it still has no completed search against which to measure total proof
cost.

### BCP equivalence in the actual solver and adjacent timing repeat

Raw arm 3 and arm-3-BCP had exactly the same restarts (36,892), conflicts,
decisions (3,745,976), and propagations (262,186,194) at one million conflicts.
Raw/BCP union likewise had identical statistics. Thus this explicit residual
simplification does not explain away the arm-3 gain and did not perturb the
observed CaDiCaL trajectory.

A final adjacent pair gave:

| query | status | propagations | solve CPU-s | solve wall-s |
|---|---|---:|---:|---:|
| arm 3 BCP | OPEN | 262,186,194 | 53.549 | 54.203 |
| parent | OPEN | 371,735,517 | 70.073 | 70.874 |

Here arm-3-BCP reduced CPU by **23.58%** and wall time by **23.52%**, with the
same deterministic search statistics as its earlier repetitions. All receipts,
including parse times and memory observations, are in `results/*.jsonl` and
`results/summary.json`.

## Independent exact controls

* `scripts/audit_mcf.py` does not import the generator or the solver package.
  It recomputes the host/non-host boundary, every allowed edge, every variable
  allocation, every Tseitin definition, and every long clause. It passed all
  three raw variants and rejected sign-mutation and deleted-clause controls.
* `scripts/verify_bcp.py` independently recomputed the 1,813-literal closure by
  repeated complete-clause scans (a different algorithm from the builder's
  occurrence-counter BCP), checked every residual and renaming, and passed both
  BCP variants. Its mutation/deletion controls were rejected.
* No long MCF clause is satisfied by parent BCP. The 126 union long clauses all
  remain at length 57. This is a precise reason that BCP alone does not remove
  the maximal-normal-form burden.
* The generator's exhaustive small control passed 3,156 good $K_4$ colourings,
  807,936 normalisation runs, and 183,168 configurable-edge steps.
* `scripts/check_receipts.py` checks saved input/output hashes, all OPEN
  statuses, control PASS receipts, and exact raw/BCP statistics.

## Structural blocker and next valid use

The favourable arm-3 policy does not yet close the wall. Parent BCP leaves all
45 arm-3 MCF long clauses and all 2,520 witnesses intact; the augmented formula
therefore remains a substantially different, non-DRAT-entailed search problem.
At two million conflicts it was still OPEN and had more decisions than the
parent, despite much less propagation work. These measurements identify a useful
encoder candidate, not evidence of a shorter completed proof.

The next justified experiment is narrow: use the exact arm-3 or arm-3-BCP CNF on
one already retained hard leaf with a matched ordinary parent-plus-cube control.
If it closes, emit and strictly check an ordinary proof for the precise augmented
query and combine it only with the checked configurable-MCF reduction; do not
pretend the MCF suffix is parent-derived DRAT. Do not launch a wall sweep from
these OPEN-only timings.

## Reproduction

From `.ultramath/smwzzs8qs/m6/`:

```sh
bash reproduce.sh          # exact builds, hashes, audits and receipt checks
bash reproduce.sh --solve  # additionally repeat all capped CaDiCaL A/B runs
```

The solve replay is intentionally capped to this one row and the listed variants;
it takes roughly 15--20 minutes on the shared VM. No command writes outside this
member directory.
