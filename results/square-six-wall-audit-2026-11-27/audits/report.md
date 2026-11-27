# Direction B: design audit for the bounded direct-wall experiment

## Scope and outcome

This was a static, solver-free audit of the stock versus stock+1,020-short-rule comparison. I did **not** launch CaDiCaL, another SAT solver, drat-trim, a broad enumerator, or a fresh search. I did not regenerate the parent with `row_formula`, and I do not report any new cube status.

The package does not define six universal inference rules. The proposed augmented arm contains 189 stock pentagon clauses and 1,020 selected instantiations of the README's local conditional triangle implication. The square/six-vertex obstruction discussion and the earlier 384 direct goals must not be silently replaced by another imagined set of “six rules.”

The input comparison is soundly structured: exact parent bytes, stock clauses, clause order, and cube assumptions can be held fixed, with only the 1,020 short clauses added in the second arm. The main acceptance risks are proof handling, using old benchmark receipts as new timed results, and premature row-level aggregation.

## Checks actually executed

My independent script uses only the Python standard library and does not import a package module:

```sh
P=/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo
python3 audit_inputs.py \
  --package "$P/.scratch/square-six-v1/src/K58_square_six" \
  --zip "$P/attachments/let-s-try-and-rbdv/K58_square_six_rules.zip" \
  > audit-results.json
```

Normal-mode result: exit 0, **126/126 assertions passed**. The full output is `audit-results.json`; expected leaf hashes are in `leaf-hashes.tsv`.

* The archive has 39 files including `SHA256SUMS`; all 38 manifest payload hashes match both the extracted files and archive members, with no unmanifested payload.
* Original parent SHA-256: `33b7898ed58bd1a3a2e088f57d4bc9d01b5397e7b72f1f5f1449a7bf16f4a02a`.
* Rebuilt stock formula SHA-256: `cb2df48f63eb7ba91d3bdb92a92cc830e5f0826d89366b52d68af80e221d33dd`.
* Rebuilt stock+short formula SHA-256: `6267a8fe7ee242ac6aabf18a440cc19686505ea78e269f465ec263a5636d856d`.
* Rebuilt combined prefix SHA-256: `6bcc793f59fc3a4e3f4e04c751be03c8bddfc71208fe7f409b7934856d0d3936`.
* The stock and augmented bodies are byte-for-byte `parent_body + stock_rows` and `stock_body + short_rows`. There are 189 and 1,020 ordered, internally unique, mutually disjoint additions. No direct-formula variable exceeds the original 19,425-variable range.
* All 40 old benchmark records use the independently reconstructed assumptions; this is a consistency check, not a validation of their solver statuses.

A structural binary-DRAT parser additionally found:

| Bytes | additions | deletions | unit deletions | empty additions |
| :-- | --: | --: | --: | --: |
| `stock-prefix.drat` | 3,267 | 3,078 | 0 | 0 |
| `wedges-prefix.drat` | 1,020 | 0 | 0 | 0 |
| `implication.drat` | 1,537 | 0 | 0 | 1 |
| `wedges.drat` | 2,041 | 0 | 0 | 1 |

These counts are record-structure checks only, **not proof validation**.

## Exact query serialization and cubes

Write `P` for the original parent, `S` for the ordered 189 stock clauses, `W` for the ordered 1,020 short clauses, and `U_b` for the three cube literals as **three separate unit clauses**.

The two native arms must be `P+S+U_b` and `P+S+W+U_b`. They are not byte-equal; they become logically equivalent original-parent problems only after the additions are certified as consequences. The experiment has no raw-parent arm, so it cannot isolate stock-versus-no-stock performance.

Appending `[U_b]` as one three-literal clause is wrong. The unit serialization and resulting headers are:

| Formula | variables | clauses |
| :-- | --: | --: |
| `P` | 19,425 | 184,117 |
| `P+S` | 19,425 | 184,306 |
| `P+S+W` | 19,425 | 185,326 |
| `P+U_b`, original-parent proof target | 19,425 | 184,120 |
| `P+S+U_b`, native stock leaf | 19,425 | 184,309 |
| `P+S+W+U_b`, native augmented leaf | 19,425 | 185,329 |

`build.py:21-25,35-36` implements precisely the base append and stock-then-short ordering. Do not use the selector/auditing formula from `verify.py:20-24,52-64` as a direct query: its extra selector variables and all-selectors clause encode violation obligations, not the wall search.

The path split variables are 294 at `r`, 2,846 at both `r0/r1`, and 2,850 at every depth-two node. Enumerating all eight sign patterns therefore gives an exhaustive, pairwise-disjoint partition on three variables:

| cube | assumptions |
| :-- | :-- |
| r000 | -294, -2846, -2850 |
| r001 | -294, -2846, +2850 |
| r010 | -294, +2846, -2850 |
| r011 | -294, +2846, +2850 |
| r100 | +294, -2846, -2850 |
| r101 | +294, -2846, +2850 |
| r110 | +294, +2846, -2850 |
| r111 | +294, +2846, +2850 |

All three absolute variables are distinct physical variables below the saved `split_limit=6612`. `leaf-hashes.tsv` records the cube-unit-fragment, original-parent-leaf, stock-leaf, and augmented-leaf SHA-256 for all eight cubes. Actual-run hashes should match these values after the coordinator's parent regeneration matches the packaged parent.

## Execution controls for the 16 searches

1. Generate and hash every base and leaf before solving. Run exactly 16 fresh native processes: eight stock and eight augmented, with no incremental solver reuse, imported learned/status-cache clauses, or parent-status shortcut. Both arms must include the 189 stock clauses and exactly the same cube units.
2. Fix a nonadaptive order before starting. The canonical cube order above must be the same in both arms; matched cube-pair ordering is also acceptable if recorded. Use the same native binary, options, deterministic seed/configuration, and proof settings in every arm. Do not stop early because one arm appears faster. “Cold” here means no solver-state reuse, not a claim about cold operating-system caches.
3. Apply the native 3-second deadline and an outer wall-clock hard kill to every process. Precompute setup outside search timing. Report Python setup/serialization/hash time separately from native process wall time. Conservatively charge native process wall time to the 48-second search ledger unless the native log rigorously separates parsing/proof I/O from search; do not silently subtract overhead. Check both each-query deadline compliance and realized total `<=48 s`. An overrun invalidates the bounded timing comparison rather than being edited down.
4. Preserve native argv, binary/version identity, stdout/stderr, exit code, start/end monotonic timestamps, setup and native durations, raw and cleaned proof hashes, and all four formula identities per leaf. Timings from 16 single cold runs are descriptive only, not a statistically supported speedup claim.
5. The packaged `benchmark.py:36-43` is a different experiment: PySAT CaDiCaL 1.9.5, 30,000-conflict budgets, assumptions, Python `process_time`, and no proof or query hashes in its records. Its old `OPEN` rows and CPU times cannot stand in for this native 3-second experiment.

## Status and UNSAT certificate gates

Keep raw native output separate from the audited final status:

* Explicit internal or external deadline exhaustion is `OPEN`, retaining the raw `UNKNOWN` output if that is what the solver printed.
* A native `UNKNOWN` not established to be a timeout remains `UNKNOWN`.
* Exit 20/raw UNSAT without a complete, accepted proof is `CERTIFICATE_FAILURE`, not audited UNSAT and not a convenient `OPEN`.
* Exit 10/raw SAT without a complete accepted model is `MODEL_FAILURE`, not audited SAT.
* Crashes, malformed inputs, launcher failures, and resource-accounting failures remain errors. Do not relabel them OPEN/UNKNOWN.

For every raw UNSAT, retain the raw native proof and construct a deletion-free native suffix. Remove complete binary `d` records only, preserve all `a` records byte-for-byte, and hash both raw and regularized proofs. This regularization is mandatory when native backward checking reports unit-deletion warnings; using it uniformly also makes the final candidate deletion-free when the raw suffix contains other deletions. An already addition-only suffix remains byte-identical. Do not use `-p` or warning suppression as a substitute. The fixed packaged prefix must not be silently rewritten; in particular, “deletion-free native suffix” does not imply that the combined stock prefix is addition-only.

Perform two independent strict checks:

1. **Exact native leaf:** cleaned native suffix against `P+S+U_b` or `P+S+W+U_b`, as appropriate.
2. **Original-parent binding:** `stock-prefix.drat + cleaned_native_suffix` against `P+U_b` for stock; `stock-prefix.drat + wedges-prefix.drat + cleaned_native_suffix` against the same `P+U_b` for augmented.

Adding fixed cube units preserves the RUP steps of the prefix, and replaying the native suffix after those derived additions binds the leaf refutation to the original parent. The local native-leaf check alone does not establish that binding.

Each checker invocation is exactly ordinary binary RUP mode:

```sh
drat-trim QUERY.cnf PROOF.drat -i -U
```

Use the actual `.cnf`/`.drat` filenames in practice. Acceptance requires return code 0, exactly one output line equal to `s VERIFIED` after CR/LF normalization, zero case-insensitive `WARNING` occurrences, and retained normal-mode output. Any warning or failed/missing original-parent replay blocks audited UNSAT. No `-w`, substring-only acceptance, or `-i`-only replay.

This deliberately strengthens two packaged interfaces: `verify.py:12-18` currently invokes `-i -U -w` and accepts a `b's VERIFIED'` substring; `README.md:70-75` illustrates `-i` without `-U`. Those receipts remain package evidence, but they do not by themselves satisfy this experiment's stricter normal-mode gate. The coordinator's strict prefix validation must finish before its bytes are relied upon.

## SAT model gate and aggregation

Parse native `v` records independently. Require a consistent assignment for every variable occurring in the exact native formula (missing assignments are not automatically false). Check all clauses of that exact leaf, including all parent, stock, short-in-the-augmented-arm, and cube-unit clauses. Decode all `58*57/2` edges using one variable of each four-color group per edge; require exactly one color per edge and no monochromatic triangle over any of the four colors. Keep the checked model and checker output. A model for one arm is not a certificate for the other arm unless separately checked there.

Aggregate only after these gates:

* Certified UNSAT on selected leaves says nothing by itself about an unresolved leaf.
* A whole-row UNSAT conclusion requires every one of the eight disjoint cubes to have an actual accepted refutation bound to the original parent, plus the cube-coverage check. One failed, OPEN, or UNKNOWN leaf blocks this inference. For a clean per-arm comparison, report eight-leaf completion separately for each arm.
* Prefix verification proves soundness of added clauses, not completeness of the search or a row refutation. Partial propagation, status-cache entries, and raw native UNSAT counts cannot be promoted into a learned whole-row result.
* Otherwise report the bounded per-cube outcomes and leave the row OPEN/UNKNOWN as the existing evidence dictates. No Ramsey-global conclusion follows.

## Source artifacts

Audit implementation and outputs are in this member directory:

* `audit_inputs.py` — independent standard-library checks, no package imports or solver execution.
* `audit-results.json` — 126 passing checks and computed identities.
* `leaf-hashes.tsv` — expected hashes for the exact eight cube serializations.
* `report.md` — this report.

Read-only package sources audited: `README.md`, `build.py`, `verify.py`, `benchmark.py`, `general.py`, `catalog.py`, `equality_inputs.py`, `tools/drat-trim.c`, and the relevant evidence JSON/log artifacts under `.scratch/square-six-v1/src/K58_square_six/`.
