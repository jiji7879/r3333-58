# K58 40,000-trial data and usefulness audit (member m1, direction C)

## Judgment

**Limited use only.** The package is arithmetically coherent and potentially useful as an exact filtering / representative-partition layer, conditional on the separate symmetry and strict-proof audits. It is **not evidence of a full-row solver speedup**, and it does not justify a broad additional preferred-job sweep. In particular, representative-count compression is not a mathematical wall reduction: the supplied row queue still has **all 11,585 ordinary wall rows OPEN**, and these probe receipts close **zero whole rows**. This is consistent with the previously validated wall status and the earlier unsplit A/B/C and 1,000-pattern experiments finding no solver improvement.

The strongest budget-relevant result is:

- Among C's **6,641 locally realizable** sorted cases, raw and sorted both produced **0 UNSAT**.
- Their conflicts were **855,611 raw vs 856,193 sorted**: sorted used **582 more** (+0.0680216%), with effectively identical cap saturation.
- All **2,418** reported sorted `UNSAT_SORTED_ARM` outcomes are among the other **3,359** cases that the supplied complete local table already excludes. The remaining **941** such table-excluded cases were still `OPEN` at the cap.

Thus C demonstrates local representative elimination, not improved solving of the surviving K58 problems. D gives no positive signal: all **10,000/10,000** preferred jobs are cap-`OPEN`.

## What was independently checked

I worked only in `.ultramath/smwy7kg2n/m1/`, did not alter tracked/shared files, and ran no SAT solver or new K58 search. The checked repository base is `8e5a10eb58de4c4b50b128eadc9a36c4b105ee4f`.

Private input hashes:

```
10398532cfbccfa8fcc680f34308ad9465d71f976cbac56b117298ff3a08cae6  K58_40000_pattern_trials.tsv
c59d0dbbd8e2108ab0f376377a489f26897246f3ff3d971983ebd5b3523e387a  K58_wall_10k_batches.zip
93055577ff1adb617949a66376c48940a3e1177a7874ff00bae7a2ed17c9386a  K58_wall_batch_handoff.md
```

The ZIP has 2,125 entries / 30,721,314 uncompressed bytes; Python `ZipFile.testzip()` returned `None`. The TSV has 40,001 lines / 6,232,882 bytes. Its bytes exactly equal the decompression of bundled `results/trials.tsv.gz`.

From my own directory, the decisive command was:

```sh
python3 work/audit.py > work/audit_run.log 2>&1
```

It exited 0. The final run has **20 named checks and no failed Boolean check**. Output hashes:

```
f8845d7d4dec53590d14bc4595c88407ecb68d8e23011836916fd1ce863c643e  work/audit.py
93392c97f40f629efc95d0d8aa6818432dde2650a11f44632d9ce262481c1e79  work/audit_results.json
144264d09b1d2c2c42e6e0e7adbf6de09e1ce9d093213a68c70cab81d29bb40a  work/audit_run.log
```

The independent standard-library parser did all of the following, not merely inspect previews:

1. Parsed all 40,000 trial rows; found exactly 10,000 per wave, ranks 0--9,999 in each wave, 40,000 distinct global indices, 40,000 distinct `(row_id,w,z)` physical identities, and 11,134 distinct rows.
2. Rebuilt the 60,817,332-cell raw roster from `wall.jsonl.gz`, `campaign.tsv`, `physical-bindings.jsonl.gz`, and the pair index. Every trial's row, profile, arm, words, and global index matched the reconstructed roster.
3. Reproduced the exact seeded samples without importing bundle code: A/B (`Random(581433326).sample`), C's conditional 8,254,067-survivor frame (`581433327`), and D's conditional 3,604,436-preferred frame (`581433328`). This confirms the stated conditional sampling and exclusions. These are job-weighted, not equal-row, samples; rows can recur across waves although all physical identities are distinct.
4. Recomputed all 40,000 ordering stages and both local-table flags from the supplied capacity table, 3,951 sorted outcome rows (3,330 SAT pairs), and four preferred catalogs. Every value matched.
5. Parsed **all 751 block-level gzipped receipts** across the four cheap probe runs. They reconstruct every top-level receipt exactly, including identities, group/block IDs, conflicts, statuses, and block seconds. Every aggregate count/conflict/verdict metadata value matched. All probe cells join back to the external TSV exactly.
6. Recomputed all 11,585 row-queue arm sizes and counts, contiguous preferred index intervals ending at 3,604,436, and all 10,000 per-row D probe charges. Every `root_status` is `OPEN`.
7. Joined all A/B marked-neighborhood receipts: 17,836 stored partial-graph SAT receipts are reused over 20,000 trials. The separate three-arm projection file has 9,950 distinct receipts reused over 10,000 A trials, giving 61 SAT and 9,939 OPEN, as claimed. These are explicitly not unrestricted whole-row certificates.

Full results and cross-tabs are in `work/audit_results.json`; executable assertions are in `work/audit.py`.

## Exact counts and arithmetic

The independently weighted table agrees with the handoff:

| Arm | rows | raw/row | after degree/row | exact sorted/row | preferred/row |
|---:|---:|---:|---:|---:|---:|
| 11 | 40 | 5,361 | 1,308 | 1,272 | 1,214 |
| 12 | 628 | 5,361 | 1,249 | 1,049 | 941 |
| 13 | 3,374 | 5,361 | 743 | 692 | 530 |
| 14 | 7,543 | 5,190 | 651 | 317 | 156 |
| **weighted total** | **11,585** | **60,817,332** | **8,254,067** | **5,435,591** | **3,604,436** |

`1 - 3,604,436 / 60,817,332 = 94.07334080357225%`, so the reported scheduling compression is arithmetically correct. Preferred also retains 43.6686060% of after-degree labels and 66.3117589% of exact-sorted labels. None of these ratios closes an ordinary wall row.

All stage counts reproduce:

| Wave | SWAP | COLUMN | SORTED_ARM | REASSIGN | PREFERRED |
|---|---:|---:|---:|---:|---:|
| A | 5,007 | 3,632 | 461 | 310 | 590 |
| B | 5,018 | 3,596 | 456 | 313 | 617 |
| C | 0 | 0 | 3,359 | 2,250 | 4,391 |
| D | 0 | 0 | 0 | 0 | 10,000 |

`REASSIGN` is a represented/reassignable label, not a raw-cell UNSAT closure.

## Solver receipts: statuses, actual work, and comparability

The receipt aggregates are internally consistent:

| Run | cells | cap | outcomes | total conflicts | reported elapsed s | workers | groups / blocks |
|---|---:|---:|---|---:|---:|---:|---:|
| A+B raw | 20,000 | 128 | 20,000 OPEN | 2,576,473 | 62.565 | 4 | 36 / 152 |
| C raw | 10,000 | 128 | 10,000 OPEN | 1,288,377 | 28.035 | 4 | 36 / 77 |
| C sorted | 10,000 | 128 | 7,582 OPEN; 2,418 UNSAT_SORTED_ARM | 1,011,952 | 101.044 | 3 | 243 / 263 |
| D preferred | 10,000 | 128 | 10,000 OPEN | 1,289,283 | 44.539 | 4 | 239 / 259 |

The times above are supplied receipt metadata, independently cross-checked against every block, not new benchmark measurements. C raw and C sorted have the same 10,000 identities, ranks, caps, and even all 10,000 physical-assumption hashes, but **all 10,000 formula-group hashes differ**, as expected after adding sorting. Their grouping, shared-learning history, and worker counts also differ. Summed block seconds are 105.8953 raw vs 281.4424 sorted (2.65774x). Consequently this is not a controlled runtime experiment and certainly does not prove speedup.

The exact C stage/status cross-tab is decisive:

| C stage | raw UNSAT | sorted UNSAT_SORTED_ARM | sorted OPEN |
|---|---:|---:|---:|
| SORTED_ARM (3,359; excluded by complete local table) | 0 | 2,418 | 941 |
| REASSIGN (2,250; locally realizable) | 0 | 0 | 2,250 |
| PREFERRED (4,391; locally realizable) | 0 | 0 | 4,391 |

The 2,418 local exclusions took 34,440 conflicts total (median 2, mean 14.2432, max 127). The 941 table-excluded-but-cap-OPEN cases consumed another 121,319 conflicts. All 3,359 consumed 155,759 sorted conflicts even though an exact prefilter could have omitted them before invoking K58 search. Meanwhile the 6,641 locally realizable cases contributed 855,611 raw vs 856,193 sorted conflicts and no closure under either convention.

Code inspection explains this. In `cheap.py:73-75`, the sorted proof receipt is consulted only inside `certify()`. In `cheap.py:120`, `certify()` is called only when `solve_limited()` already returned `False`; `None` becomes `OPEN`. Hence the complete table was **not applied before search**. The handoff's recommendation to apply the shared table before spending conflicts is sensible; the measured C sorted run did not implement that prefilter.

There is **no matched raw-vs-preferred or sorted-vs-preferred outcome table**. A/B have raw only, C has raw and sorted only, and D has preferred only. `preferred_label` is a catalog flag, not a preferred solver result. D also changes the sampling mix materially: C has arms 11/12/13/14 counts 49/943/3,001/6,007, whereas D has 119/1,632/4,979/3,270. In particular arm 14 falls from 60.07% of C to 32.70% of D. Raw-vs-C, C-vs-D, or 24.18%-vs-0% closure-rate comparisons therefore mix different formulas and frames.

## Saturation and any useful job-selection signal

`OPEN` here is a budget result, not closure and not a satisfying model. In D every job recorded at least 128 conflicts: 5,206 exactly 128 and 4,794 above 128 (reported delta maximum 188). All arms are fully OPEN: arm 11:119/119, arm 12:1,632/1,632, arm 13:4,979/4,979, arm 14:3,270/3,270. Every one of the seven profile strata is also fully OPEN. Tiny differences in cap-overshoot/conflict deltas are not a validated hardness ranking. With no early successes, closures, or per-job preferred timings, the receipts provide **no empirical feature for choosing among remaining preferred jobs**.

The separate 512 cold original-parent Kissat controls (first 256 ranks of each of A/B) are also all OPEN: 354 have exactly 512 conflicts and 158 report more (maximum 518), totaling 89.41 seconds. Different engine, cap, and sample prevent treating these as preferred speed controls.

C's sorted local exclusions are concentrated in arm 14 (2,086 of 2,418), but C's table-excluded population itself is concentrated there (3,010 of 3,359). This offers no useful signal for solving locally realizable/preferred jobs, all of which remain cap-OPEN. The useful deterministic signal is simply the exact local stage/catalog: remove locally impossible pairs before search and do not mistake reassignment for UNSAT.

## Proof-scope caveat

I did not independently check the symmetry theorem, recreate the physical formulas, or replay the RUP/DRAT files; those belong to the other directions. My validation of the 3,359 exclusions is therefore an exact consequence of the supplied complete table, not a new proof of that table or of the full K58 transport. Likewise, a generic `UNSAT_SORTED_ARM` receipt is not a newly checked per-job original-parent proof and never closes an entire row by itself.

One code-level issue for the strict replay audit: the bundled historical helpers call `drat-trim ... -i -w` at `cover_proofs.py:25`, `raw_glue.py:43`, and `cheap.py:86`. I ran none of them. Any coordinator replay should follow the requested `-i`, never `-w`, policy rather than inheriting those flags.

## Budget consequence

Use the compact tables as a queue/filter only after their mathematical and strict-proof certificates pass independent review. Do not spend budget interpreting the 94.0733% compression as wall progress, and do not launch a broad 128- or 512-conflict preferred search on the strength of these trials. If further solver evaluation is authorized, it should be a small matched experiment on the same locally realizable jobs, with identical solver setup/grouping and strict retained proofs, including preferred on those same identities; a fresh unmatched D batch would not repair the present comparison. No such experiment was run here.
