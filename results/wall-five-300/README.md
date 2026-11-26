# K58 wall-profile sweep: five rows per family, 300 seconds each

## Outcome

**Every one of the 35 selected rows remains OPEN after a genuine 300-second run.**

- 5 selected rows from each of the 7 wall profiles = **35 unique full row IDs**.
- 300 seconds per run, **no conflict limit**, using fresh Kissat 4.0.4 solves.
- **0 proved UNSAT, 0 SAT models, 0 closed rows.**
- No profile, family, or Ramsey-bound conclusion follows from this five-row sample.

The actual parents were ordinary frozen first-tier whole-row CNFs:
`tables=True,total_critical=True,full_root=False`, CAS off, depth 0. No
perfect-degree balancing, H-rise import, blanket degree cap, or local three-arm
formula was used. The frozen roster is `data/wall.jsonl.gz`, decompressed
SHA-256 `d5641e1ba875bc4ec5fbe156d48585f610e877f5232de7181eb464d4ad4fa2bc`,
with 11,585 rows.

The selection is exactly the five smallest values, in each family, of
`SHA256("wall5x300-v1|" + profile + "|" + full_row_id)`, with profile written
without parentheses and with commas and no spaces, for example `16,16,14,11`.
It is deterministic, **not a random or representative statistical sample**, and
does not establish mutual non-isomorphism of the selected rows.

## Deduplicated results

Every parent was independently regenerated from the pinned frozen encoder and
hashed. Each of the 35 input CNFs matched its receipt's parent digest. Every
selected row has a complete bounded receipt with return code 0,
`OPEN_AT_300_SECONDS`, `conflict_limit: null`, measured wall in [295,310]
seconds, and a recorded deleted unfinished proof trace. Conflict counts were
reparsed from the raw solver logs.

| profile | rows completed | range of conflicts | verdict |
| --- | ---: | --- | --- |
| `(15,14,14,14)` | 5 / 5 | 10,568,581–11,714,524 | all OPEN |
| `(15,15,14,13)` | 5 / 5 | 6,570,282–7,015,064 | all OPEN |
| `(16,14,14,13)` | 5 / 5 | 10,693,137–11,445,700 | all OPEN |
| `(16,15,13,13)` | 5 / 5 | 6,601,303–7,096,527 | all OPEN |
| `(16,15,14,12)` | 5 / 5 | 6,017,767–6,925,921 | all OPEN |
| `(16,16,13,12)` | 5 / 5 | 5,860,146–6,176,864 | all OPEN |
| `(16,16,14,11)` | 5 / 5 | 5,777,579–6,099,340 | all OPEN |

Exact full IDs, parent hashes, wall/CPU seconds, conflict counts, source CNFs
and receipts are in `deduplicated-coverage.json`. The agreed full-row-selection
file, including branches and selection-key digests, is
`canonical-selection.tsv`.

## One duplicate attempt

There were **36 completed bounded attempts**, not 36 different rows.
`479de1087a399687f477fde8eef64a8753ca66453d59008c9de1802e9fdd842a`,
profile `(16,15,13,13)`, was solved independently once by m6 (started
2026-11-26T17:28:08Z, 7,096,527 conflicts) and a second time by coordinator
S3 (started 2026-11-26T17:39:22Z, 7,232,322 conflicts). They share the exact
same parent SHA-256
`66707fb5e9d8d234f4ff45a59da2278398a92ca3a7a65ae778e5597ea2c268fb`.

The earlier receipt is used for the coverage table. Both are retained,
separately, in `primary-evidence/`. This one duplicate does not add coverage,
proof, or a second profile verdict. The nominal raw 300-second allocations are
10,500 seconds for the 35 selected rows plus 300 seconds for this duplicate.

Two coordinator lanes covered the formerly unclaimed profiles
`(15,15,14,13)/(16,15,13,13)` and `(16,15,14,12)`. Member m6's own ten rows
covered `(15,14,14,14)` and `(16,14,14,13)`; member m8's ten covered
`(16,16,13,12)` and `(16,16,14,11)`. Extra audit members validated the encoder,
checker, receipts and stale-artifact boundaries. The campaign ended with seven
finite reports accepted; that is not a closed mathematical problem.

## Important stale evidence, excluded

For the five selected `(15,14,14,14)` rows, old receipts under
`.ultramath/smwqx1yfw/m1/work/sweep/` say UNSAT with hundreds of added
lex-leader clauses and `extras:false`. Their producer confirms a different
host+units+lex formula, not the frozen first-tier parent plus its first-tier
tables/total-critical clauses. Representative input and proof files no longer
exist for replay.

These receipts do **not** close a row or eliminate that profile under the
current evidentiary standard. This is an admissibility and provenance issue,
not a newly proved statement that the historical UNSAT claim was false.
Likewise, a snapshot saying part of the 35 rows was `UNRUN` refers to its
timestamp, not to the final completed batch; the final deduplicated table
supersedes such intermediate allocations.

## Evidence and replication boundaries

`primary-evidence/index.json` indexes all 36 original-style `result.json` and
`solver.log` pairs, including the duplicate separately. Their recorded log
hashes and parsed conflict counts were independently checked. There are no
retained incomplete proof files: all 36 rows ended OPEN and their traces were
deleted.

`coordinator-manifest.json` contains the exact 15 coordinator-selected row and
parent records and the director/backend allocation. Raw prepared CNFs remain
under `.scratch/wall-five-300/rows/`. Member CNFs and original solver work
remain under `.ultramath/smwxrqkfl/`. Those are separate from this compact
committed receipt package and should not be mistaken for a preservation
archive of old proof material.

The runner `tools/run_wall_300.py` accepts an explicit `--seconds` and
`--bin-dir`; its default remains 300 seconds. On OPEN it deletes the unfinished
DRAT, on UNSAT it requires ordinary native replay with `s VERIFIED` against the
exact parent, and on SAT it does not silently promote an encoding model to a
K58 counterexample. `tools/coordinate_wall_five.py` rebuilds the frozen parent
before each run and refuses to reuse a changed prepared parent or stale work
directory. Initial failed wrapper launches with no ordinary result are
excluded; no conflict/timeouts were counted against rows from prior runs.

`SHA256SUMS` binds the compact report, exact selection and deduplicated table,
receipts, and retained logs.
