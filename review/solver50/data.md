# Direction C — bounded experiment and receipt audit

## Verdict

No new solve was launched, and no whole K58 row is closed by this audit. The receipts support the **sorted/two-smallest representation plus the exact local-arm proof path** as the only measured source of representative closures. They do **not** show that shared learning closes any locally surviving representative at three seconds.

The decisive 3-second fact is easy to miss in the summary: all nine stored UNSAT receipts are for queries already labeled `EXCLUDED` by the exact ordered-arm table. The three tested sorted `ARM_WITNESS` queries all timed out, as did all six earlier-preferred and all six new-cover queries. Thus the supplied 3-second results contain **zero demonstrations of a new closure beyond the local table**.

The 4,589 sorted jobs with `cadical=OPEN` but `sorted_arm=EXCLUDED` should go through the independently checked local-proof/original-parent replay route, not be advertised as new solver discoveries. The remaining 32,576 sorted `ARM_WITNESS` jobs are the relevant untested population. Three have timed out at three seconds; 32,573 have no 3-second receipt in this fresh sorted cohort. There is no receipt-based reason to call any particular survivor likely to close: all cap-128 survivors merely exhausted a conflict budget, and their conflict counts do not measure proximity to a proof.

## What was independently checked

HEAD was `d19284ac7a1698a3296197cf0c133c6d5c1331e6`. The supplied representative gzip had SHA-256 `897334cfcaceae03f13a0d242fb886c0633bc712d353a094373f7e5b5a539743`; the solver/proof zip had `e8a9fe88fbc7b647d6dd37e5ec5c257cb13365fa4dfd18685a2e1a599c378496`.

`audit.py` parsed the attachment rather than trusting the prose. The 150,000 data rows are byte-identical after decompression to the bundle's `round50/campaign-ledger.tsv.gz` (21,346,209 bytes; SHA-256 `63bbb8b466013c456367d5029b2cf73d162830be34ee2fb71c300b66fc06191b`). For each of the four new bulk passes, all 50,000 source identities and ranks match the consolidated receipts, and every consolidated receipt equals its block receipt. It performed the same identity/block checks for the four earlier cap-128 passes (50,000 jobs total). Conflict totals, status totals, block counts and block times also match the JSON summaries.

| Convention / pass | Jobs | Distinct rows | Result at nominal cap 128 | Conflicts |
|---|---:|---:|---|---:|
| Fresh sorted, F | 50,000 | 11,398 | 12,835 `UNSAT_SORTED_ARM`; 37,165 `OPEN` | 4,971,860 |
| Earlier preferred, E | 50,000 | 11,585 | 50,000 `OPEN` | 6,446,729 |
| New cover plain, G | 50,000 | 7,023 | 50,000 `OPEN` | 6,446,770 |
| Same new jobs, edge cuts | 50,000 | 7,023 | 50,000 `OPEN` | 6,446,210 |

The sorted partition is exact in the table:

| Sorted class | Jobs | Conflict sum | Min / median / max |
|---|---:|---:|---|
| `UNSAT_SORTED_ARM`, also `EXCLUDED` | 12,835 | 179,971 | 0 / 1 / 127 |
| cap-`OPEN`, `EXCLUDED` | 4,589 | 591,873 | 128 / 129 / 137 |
| cap-`OPEN`, `ARM_WITNESS` | 32,576 | 4,200,016 | 128 / 128 / 205 |

All 12,835 solver-false statuses occur among the 17,424 local exclusions. The bulk status is `UNSAT_SORTED_ARM`, not a fresh full-formula `VERIFIED_UNSAT` receipt. Its mathematical use depends on the separately audited local proof and exact parent/cube transfer; this direction did not replay those proofs.

For comparison, earlier wave C had 2,418/10,000 solver-and-local closures (24.18%) and 3,359/10,000 exact exclusions (33.59%). Fresh F has 25.67% and 34.848%, respectively. These are descriptive rates for different sampled identities, not evidence of a solver improvement. Earlier A and B each had 0/10,000 raw closures; D had 0/10,000 preferred closures. E and both G passes also had zero.

The useful architecture control is internal to C: exactly the same 10,000 raw identities at nominal cap 128 gave **0/10,000 raw closures versus 2,418/10,000 sorted closures**. Conflicts were 1,288,377 raw and 1,011,952 sorted, although the lower sorted total includes early termination of solved jobs. This supports choosing sorted naming for closure rate without increasing the budget. It is not a controlled timing win: raw used four workers, 28.035 s wall and 105.8953 summed-block seconds; sorted used three workers, 101.044 s wall and 281.4424 summed-block seconds. Formula, grouping and learned-state paths also differ.

All older block ledgers matched their consolidated rows: A/B raw 20,000 `OPEN` with 2,576,473 conflicts, C raw 10,000 `OPEN` with 1,288,377, C sorted as above, and D preferred 10,000 `OPEN` with 1,289,283. Their identity/status/conflict fields also match `trials.tsv.gz` for all 30,000 raw, 10,000 C-sorted and 10,000 D-preferred incidences. Separately, all 512 cold original-formula Kissat controls matched their A/B source identities and stayed `OPEN`; conflicts ranged from 512 to 518 at cap 512. Their actual per-query times were 0.1398–0.5085 s (median 0.1618, sum 89.41 s). These are cold Kissat measurements, not evidence about shared-learning CaDiCaL or a 3-second timeout.

### Overlap and untested scope

Independently recomputed raw `(row_id,w,z)` intersections:

- sorted versus earlier preferred: **0**;
- new versus earlier preferred: **92**;
- new versus sorted: **49**;
- new versus the prior 40,000: **35**;
- sorted or earlier preferred versus the prior 40,000: **0** each.

These are raw identity overlaps, not necessarily equal formulas under different ownership guards. No verdict should be transported across conventions from these labels alone.

The queue arithmetic sums to 3,604,436 old and 1,101,974 new representative jobs. This is a 69.4273% reduction in scheduled jobs, not a reduction in OPEN rows. The first new 50,000 represent only 7,023 rows; 4,562 rows do not occur in that cohort. Six of those 50,000 have timed 3-second receipts (all OPEN), leaving 49,994 in that cohort without one. A further 1,051,974 new-cover jobs lie after offset 49,999 and are outside this cap-128 pass. All 11,585 queue root statuses remain `OPEN` in the data.

### Joining-edge comparison

The paired new-cover files really do contain the same 50,000 jobs in the same rank order, group and block. Exactly 4,395 assumption hashes change, precisely the jobs whose joining-color list changes. The independent joining totals are 4,395 affected, 4,169 newly forced, and 4,400 color children excluded (earlier preferred: 3,421, 3,328 and 3,421).

Nevertheless, both passes close zero. Cuts-minus-plain conflicts sum to **−560**, with 13,597 negative, 22,886 zero and 13,517 positive per-job deltas. On the 4,395 directly affected jobs the sum is only **−33**; the other −527 occurs downstream under shared learned state. Conflict paths are therefore order/state dependent, not independent per-job measurements.

The runtime comparison is not controlled: plain used four workers and edge used five, with different verification load. Plain wall time was 169.728 s and edge 149.274 s, but summed block time moved in the opposite direction, **635.5350 s to 697.6259 s (+62.0909 s)**. No joining-edge speedup or 3-second closure advantage is justified by these receipts.

### What the receipts call time

The cap-128 passes record wall seconds per **block**, not per cube. Blocks contain 1–192 jobs and include solver initialization and shared-state reuse. Summed-block milliseconds per job below is only a throughput descriptor, not per-call latency or CPU time.

| Pass | Workers | Run wall s | Sum block s | Median / p95 block s | Sum-block ms/job |
|---|---:|---:|---:|---:|---:|
| Sorted | 3 | 175.489 | 484.2523 | 1.0622 / 2.6209 | 9.685 |
| Earlier preferred | 4 | 202.910 | 762.0319 | 1.7833 / 3.6863 | 15.241 |
| New plain | 4 | 169.728 | 635.5350 | 1.6931 / 3.2834 | 12.711 |
| New edge | 5 | 149.274 | 697.6259 | 1.7129 / 3.3406 | 13.953 |

The 24 timed receipts use a different metric: the 3-second timer begins after encoding and solver setup. Fifteen OPEN searches took 3.002332–3.015395 s (maximum recorded overrun 15.395 ms). The largest sum of encode + setup + search + check fields is 4.685144 s. These are consequently not hard three-second end-to-end process receipts.

Nine stored proof byte strings match their recorded lengths and SHA-256 hashes. Their searches took 0.004452–0.077701 s and used 152–998 conflicts. This audit did **not** replay them. The shipped `timed50.py` invokes `drat-trim ... -i -w`, so the shipped checker command alone does not meet the present standard. No tamper/negative control was found in the shipped Python/Markdown sources searched here. Direction A's board subsequently reported independent, exact-query regeneration and successful `drat-trim -i`-only replay of all nine, with both bad-tag and wrong-query controls rejected; that separate result is the applicable proof-control check, not work claimed by this direction.

## Small predeclared A/B experiment

**Purpose:** test architecture, not a larger conflict budget or deeper binary tree. Compare fresh proof-logging CaDiCaL with block-shared learning on exactly the same locally surviving sorted queries, at the same real three-second per-call cutoff.

`candidates.tsv` fixes 12 exact `(convention,row_id,w,z)` queries before any run:

- six arm-13 jobs from existing sorted block 95, ranks 9, 22, 52, 70, 76, 99;
- six arm-14 jobs from existing sorted block 1, ranks 9496, 9995, 10191, 21911, 37059, 40970.

Every candidate is `ARM_WITNESS`, cap-128 `OPEN`, and has no existing 3-second receipt. Selection was deterministic: among blocks with at least six eligible jobs, choose the smallest block number in each target arm, then the six smallest ranks. The file includes full row IDs, profiles, raw indices, existing assumption hashes and conflicts. The `shared_group` value is only `cheap.py`'s canonical **grouping-metadata** hash, not a CNF hash; it is not sufficient query identity.

### Arms and cap

1. **Fresh arm:** regenerate the original first-tier parent plus exact physical cube and sorted ownership/sorting guard for each candidate; use a fresh proof-logging CaDiCaL instance for every job.
2. **Shared arm:** construct exactly the same two group formulas, use one fresh shared instance per block, and submit the six jobs in ascending candidate rank with learned-clause reuse. Do not preload any old block state or cache. Learned reuse across groups is forbidden.
3. Run each job once in each arm: **24 test calls, at most 72 seconds of solver-search budget in total**, plus initialization and independent proof checking. Do not retry, raise the budget, add a split, or extend the sample based on the result.
4. As harness controls, first replay the nine existing proofs strictly and require a one-byte tamper to fail. Rerun exactly two known fast UNSAT queries once per arm: `90085700bed34f6c9c51f5a733ef26e3cc3a2d529afbddc92e0d8610b971c53e / 00022/01200` and `b8854af690d6b7024fe2a2bbaf1d0aabcc601aeec4ff8cfc945807bd0ac82b08 / 01001/02201`, both under `sorted`. Use separate solver instances for these controls and exclude them from the 12-job outcome denominator. The resulting 24 test + 4 control calls have an absolute search-budget maximum of 84 seconds. An incorrect-query cache entry must be rejected before launch.
5. Use direction A's exact safe process/deadline recipe; this direction deliberately supplies no unvalidated solver launch command. Record encoding, setup, search, end-to-end process and check times separately. If the reciprocal timer cannot enforce the chosen cutoff or emit standalone valid proofs for incremental UNSAT calls, the shared arm is not cleared to count closures.

For both arms, a manifest must contain solver identity/configuration, original parent SHA-256, full query SHA-256, physical cube, ownership/guard literals, block/order, and cold-cache state, with byte-identical query hashes across arms. `UNSAT` counts only after an independent `drat-trim -i` replay against that exact original query succeeds without `-w`. SAT requires a complete checked model. Timeout, UNKNOWN, killed process, checker failure or stale/mismatched cache remains `OPEN`; none is a refutation.

The primary endpoint is the number of the 12 candidates with a newly replayable full-query UNSAT proof in each arm. Conflicts and timing are secondary. A 0–0 result means only 0/12 on these exact queries and must stop this test; it says nothing about other representatives, whole rows, or Ramsey numbers. Even a closure of all 12 would remain 12 representative jobs, not whole-row progress.

**Priority:** run this sorted-survivor A/B only after the proof/timer audit clears it. Do not prioritize another plain-versus-edge batch: the existing exact paired comparison has 0/50,000 versus 0/50,000 and no controlled timing advantage. The nine easy positive controls must not be counted as newly discovered exclusions.

## Reproduction

From `.ultramath/smwydhgx1/m3/`:

```sh
python3 audit.py > audit-output.txt
sha256sum audit.py audit.json candidates.tsv timed3s.tsv
```

Expected output hashes for this run:

```text
b96d75debe6b94944dd328573a762b348b0292da26d9895ad7acb00438037a6b  audit.py
041de2ffaa7dabd796019446264c4ad00e20ae3efa81a4cd05b93af200a614a7  audit.json
44e80c54d81042f012d392e2224d7044e6ae3a1feda0ef1a51dde3618c0e6cee  candidates.tsv
e279f6f3acdeb7443b6d8a417b544e71a66cdc4b819d01533d53f8fd63240b9c  timed3s.tsv
```

`audit-output.txt` is a pretty-printed copy of `audit.json`. `timed3s.tsv` exposes all 24 timed identities, their local class, prior bulk result, timings and query/proof hashes. `candidates.tsv` is the frozen experiment input.

Scope: this was a finite receipt/data audit. It did not verify the 1,101,974-job mathematical cover, regenerate candidate CNFs, replay proofs, test learned-clause transport, or run any solver. Those boundaries are required before converting this experiment design into a closure claim.
