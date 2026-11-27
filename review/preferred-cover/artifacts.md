# K58 representative-pair package: artifact and proof audit

## Judgment

**Useful in a narrow sense, but not a mathematical wall reduction and not current justification for more broad K58 solver budget.** The package contains strong, replayable evidence for its *finite local-arm tables* and for exact queue arithmetic. In my independent implementation, all 608 local cover certificates passed strict binary RUP checking and all 3,330 stored complete-arm witnesses were valid. The 3,604,436 preferred jobs form an exact contiguous index over the 11,585-row supplied roster, every one still marked OPEN.

That establishes the integrity and local-formula content of the artifact, not by itself the unrestricted K58 theorem. Whole-row/root use still depends on the separate physical symmetry, original-parent and export-equivalence audits. Only 42 full-parent sorted-guard transport examples have stored lifted receipts; they all replayed, but the 2,418 C statuses are not 2,418 independently stored full-parent proofs.

Retain the local tables as cheap preprocessing and as a possible canonical root partition after semantic signoff. Do not infer that 94.07% fewer representative jobs closes any of the 11,585 OPEN rows. The existing probes do not show a solver speedup on locally realizable cases or any preferred-job closure, so another broad batch/new-full-row search is not warranted by this evidence.

## Integrity and provenance

I copied/extracted only under `.ultramath/smwy7kg2n/m2/`; no tracked or shared file was edited and no new K58 search/export solve was run.

Input SHA-256 values:

```text
93055577ff1adb617949a66376c48940a3e1177a7874ff00bae7a2ed17c9386a  K58_wall_batch_handoff.md
10398532cfbccfa8fcc680f34308ad9465d71f976cbac56b117298ff3a08cae6  K58_40000_pattern_trials.tsv
c59d0dbbd8e2108ab0f376377a489f26897246f3ff3d971983ebd5b3523e387a  K58_wall_10k_batches.zip
```

Commands (from the member directory):

```sh
unzip -t ../../../attachments/let-s-try-and-rbdv/K58_wall_10k_batches.zip
cd extracted/K58_wall_10k_batches
sha256sum -c SHA256SUMS
```

Results: ZIP CRC test passed; 2,125 unique, safe entry names; exactly 2,124 payload files other than `SHA256SUMS`; the manifest path set equals that payload set; all 2,124 hashes passed, with no missing or unlisted files. The external TSV and `gzip -dc results/trials.tsv.gz` are byte-identical and have the TSV hash above.

These are consistency checks, not signatures establishing who generated the bundle.

## Strict replay, including a required local patch

The supplied central checker helper `cover_proofs.py:25` used `drat-trim -i -w -U`. Here `-w` suppresses warnings, but the audit explicitly required never using it. I removed only `'-w'` in my extracted copy; the strict line became:

```python
p1=subprocess.run([str(HERE/'tools/drat-trim'),str(q),str(p),'-i',*extra],capture_output=True)
```

Offline setup installed only bundled wheels and compiled the bundled checker source. Environment: Python 3.12.14, `python-sat 1.9.dev22`, Kissat 4.0.4. The freshly compiled checker was run with `-i -U`, never `-w`.

```sh
sh setup.sh
TMPDIR="$PWD/../../.scratch" /usr/bin/time -v \
  .venv/bin/python verify.py --jobs 1
```

The supplied verifier, with this strict helper patch and **one worker**, exited 0 in 83.70 s (305,492 KiB maximum RSS). Its output reports:

```text
Checked ordinary signed units and anonymous-site transpositions on 11585 rows. ... templates 41
Replayed 608 cover certificates and all sample physical sorted-guard proofs.
Every retained job has a checked local coloring satisfying its ownership guard.
Rebuilt sampled physical projection maps and verified arm colorings.
Checked identities, scoped assumptions and results for 50000 full-order CaDiCaL probes.
Verified 40,000 distinct sampled cells and the 3604436 job root cover on all 11,585 rows.
```

Here “checked ... probes” means receipt/assumption/hash/status validation, not rerunning those 50,000 solver queries. The run did not launch a K58 search; its SAT calls are finite witness/ownership checks in the supplied verifier.

## Independent local-CNF and proof audit

`audit_independent.py` does not import any supplied encoder and makes zero SAT/SMT calls. From elementary one-color-per-edge, triangle-free, fixed-pentagon and lexicographic constraints, it independently:

* reconstructed the 76 valid words and all 5,776 ordered pair-index keys;
* built all 304 sorted-table queries and all 304 preferred-cover queries;
* required every regenerated CNF SHA-256 and every decompressed proof SHA-256/byte count to match its receipt;
* called the compiled `drat-trim QUERY PROOF -i -U` sequentially on every one of the 608 proofs;
* validated every stored SAT arm model directly against every triangle, the fixed pentagon, sorted outside words and its claimed first two words;
* checked that all 2,841 preferred catalog labels have an independently validated ownership witness;
* recomputed roster identities, physical arm bindings, per-size counts and global index boundaries directly from JSON/TSV.

Command and result:

```sh
TMPDIR="$PWD/.scratch" /usr/bin/time -v \
  extracted/K58_wall_10k_batches/.venv/bin/python audit_independent.py
```

Exit 0 in 28.54 s (152,508 KiB maximum RSS). It regenerated 6,050,667 sorted-query bytes and 26,028,176 preferred-query bytes; replayed 2,273,933 sorted-proof bytes and 7,616,831 preferred-proof bytes; **608/608 returned `s VERIFIED`, with zero outputs containing `WARNING`**. A negative control on a satisfiable no-blocker query with an empty proof returned 1 and `s NOT VERIFIED`, so the audit was not merely accepting every invocation.

Exact independently recomputed counts:

| Stage | size 11 | size 12 | size 13 | size 14 | Weighted total |
|---|---:|---:|---:|---:|---:|
| Wall rows | 40 | 628 | 3,374 | 7,543 | 11,585 |
| Raw live ordered pairs/row | 5,361 | 5,361 | 5,361 | 5,190 | 60,817,332 |
| Capacity survivors | 1,308 | 1,249 | 743 | 651 | 8,254,067 |
| Sorted SAT pairs | 1,272 | 1,049 | 692 | 317 | 5,435,591 |
| Preferred pairs | 1,214 | 941 | 530 | 156 | 3,604,436 |

There are 3,330 SAT outcomes and 621 local refutation candidates (36, 200, 51, 334 by size). All 3,330 models passed direct validation. Preferred scheduling reduction is `100*(1-3604436/60817332) = 94.07334080357225%`.

The queue has one unique row per roster ID, sorted row order, correct arm sizes and outside physical vertices, contiguous `[index_begin,index_end_exclusive)` intervals ending at exactly 3,604,436, and D-sample counts matching every `preferred_jobs_probed`. All 11,585 `root_status`, campaign `root_status` and `ledger` values remain **OPEN**.

## What is certified versus only recorded

### Established within the supplied encodings

* Each local sorted exclusion set is certified by its corresponding one of 304 strict RUP refutations; all complementary cases have checked full-arm witnesses.
* Each size/second-word preferred avoidance formula is refuted by one of 304 strict RUP proofs. Together with checked catalog/model ownership witnesses, this is strong finite evidence for the complete local preferred cover under the supplied sorted-arm encoding.
* The supplied 42 full-first-tier-parent sorted-guard/query hashes and lifted RUP receipts all replayed in the strict patched verifier. This checks physical cubes, guards, parent/query hashes and proof bytes on those examples.
* Roster bindings, local tables, catalog roster coverage, exact queue indices and artifact hashes are internally complete and reproducible as described above.

### Not established by these receipts alone

* The 42 physical examples do not constitute 3.6 million full-parent UNSAT proofs, nor do they independently prove the first-tier encoder is the original K58 problem. General physical symmetry/export equivalence remains a semantic prerequisite, and pre-existing-cube use requires the additional permutation-invariance caveat stated in the handoff.
* A/B raw runs and C raw controls are capped OPEN/timeout records, not closures or SAT witnesses. The 512 cold controls were hash/receipt checked, not rerun.
* C's `UNSAT_SORTED_ARM` status is not a stored full-parent DRAT proof. In `cheap.py::certify`, when `(n,w,z)` is absent from the sorted SAT table, the function returns `UNSAT_SORTED_ARM` before constructing/running its Kissat proof block. The local exclusion is certified as above, but actual full-parent proof transport was not materialized for each such C cell.
* D supplies no UNSAT certificate: all 10,000 are OPEN at cap 128. A representative job would close only its exact restricted class after a verified UNSAT; a whole row requires all preferred classes for that row or an unrestricted-parent refutation.

For C, independently joining the sorted receipts to the local table gives:

```text
3,359 exact local exclusions = 2,418 UNSAT_SORTED_ARM + 941 cap-OPEN
6,641 locally realizable cases = 6,641 cap-OPEN (no sorted UNSAT)
```

Thus 2,418 and 3,359 are **not additive**. Among the 6,641 locally realizable cases, the recorded aggregate work was 855,611 raw conflicts versus 856,193 sorted conflicts (+582), with zero closures in either representation. D likewise had 10,000/10,000 cap hits. Consequently the demonstrated benefit is local/preprocessing classification, not improved solving of surviving K58 jobs.

## Evidence files

* `audit_independent.py`: independent tables/models/CNFs/proofs/roster audit, no solver.
* `independent-results.json`: machine-readable successful results.
* `evidence.txt`: exact successful tool, integrity, verifier and usefulness outputs.
* `logs/`: separate original outputs, including strict verifier and independent-audit timing.
