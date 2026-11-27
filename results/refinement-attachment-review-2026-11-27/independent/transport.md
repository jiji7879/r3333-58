# Direction E audit: proof transport and graph-to-CNF projection

## Verdict

**The worked quickstart transport and one bounded larger-package owner/recipient replay pass independently, with exact query/proof identities. The source-level all-recipient argument is sound when its two separate checks are both run.** I found no counterexample to the sampled transport or to the stated conditional graph-to-CNF encoding.

There is one checker-protocol defect in the quick package: `K58_review/formulas.py:175-178` calls `drat-trim` with `-w`, suppressing warnings. That violates the required strict/native acceptance policy. I rebuilt the sample independently and reran every decisive proof with `-i -U`, **without `-w`**, requiring exit 0, exactly one `s VERIFIED` status, and no warning on either output stream. All passed. Thus the defect does not invalidate the independently checked sample.

The full-package totals are not freshly established by this bounded audit. Stored ledgers agree arithmetically with their summaries, but that is not historical checker execution.

## Fresh checks performed

### 1. Independent quick transport reconstruction

`checks/independent_transport.py` imports none of the package Python code. It independently:

- constructs the local formula, revised owner circuit, representative, guarded parent, children, and coverage query;
- parses and signed-relabels every binary proof step;
- checks injectivity and all physical missing-color interface premises for all 91 arm edges;
- checks 1,381 non-ALO local clauses as direct physical images and treats the 91 three-color ALO clauses as the RUP prefix;
- matches all retained SHA-256 identities before native replay.

The resulting key identities are:

| Object | SHA-256 |
| --- | --- |
| Frozen ordinary row | `44082b06b1803f45d61f1a595b3f938708362782a8ee0ea23aab22cd0e8bd2d8` |
| Representative | `afbab09a68937e6674e23fbddc6905cdfd8a86372007c7f6713d64e9863b8afd` |
| Guarded worked parent | `2c339aec5100b8cd5608968f7f7cc97ac30eac34246c10807f06cea11c773244` |
| Local query/proof | `baf5ba5fac6c4c3553486ae6a98e50a48e0785f024fbd65e85f1c39ea10e1ff8` / `cbc5abba999156c727037e6e73d826937604f29a40cc5fb1d9ad4a8c59eaf15b` |
| Color-0 query/lifted proof | `b841ae190fbe66819c1d552dd87c627468078654913556d167b3fa7af8a5af40` / `1b557154b7f40a282e1846d1ef7e89e062f0eb5dc68cf62f8edbe01777b5f1d0` |
| Direct retained-color-1 coverage query/proof | `364c1d632b8f220ebb185e7a43ad23b733abc62163f9b5032d79fa9611ec9b95` / `6a22c515098b6d0a2f095c2805edde6621302036372ad35a086a451459726632` |

Strict native outcomes in `artifacts-transport-v2/summary.json` and the adjacent `.log` files:

| Check | Exit | Result |
| --- | ---: | --- |
| Local proof | 0 | VERIFIED, warning-free |
| Physical color 0 | 0 | VERIFIED, warning-free |
| Physical colors 2 and 3 | 0 each | VERIFIED by unit propagation, warning-free |
| Direct coverage excluding color 1 | 0 | VERIFIED, warning-free |
| Minimal physical interface | 0 | VERIFIED, warning-free |
| Remove root spoke / missing-color triangle / four-color ALO | 1 each | expected `NOT VERIFIED` |

This independently supports colors 0,2,3 being refuted and color 1 remaining unresolved, and proves that every model of that **seven-spoke guarded parent** uses physical color 1. It does not establish SAT/UNSAT for color 1, the original unguarded representative, a wall row, or a Ramsey bound. The direct coverage certificate, not a child certificate alone, supplies the parent replacement argument.

The toy rejections demonstrate the required logical identity. If palette is `{0,1,3}` and missing color is 2, then for each interior edge `uv`:

```
(0,u,2) and (0,v,2), together with the host triangle on {0,u,v}, imply not (u,v,2).
```

Negating the three local ALO literals makes the physical four-color ALO select color 2; the two spoke units and triangle then conflict. Removing any tested premise defeats that RUP derivation.

### 2. Bounded larger-package fresh replay

`checks/replay_selected_full.py` ran the larger package's routines only for arm 14, pair `21012/22101`, rank 46, on row `ffe5d8dbbc769665f369b6bc7f95585435ad8351331f8efde97448eb0fba501b`. No solver search was started.

Fresh results in `outputs/full-selected-transport.json`:

- the generic arm-14 interface passed: 1,375 direct axioms and 91 RUP ternary clauses;
- root and guarded colors 0/1 passed additions-only forward `-f -U` local replay, with exact stored query, original-proof, additions-proof hashes and byte counts;
- root and guarded colors 0/1 passed strict native physical transport;
- regenerated physical query hashes agreed between the independent transport census routine and direct native-lift routine;
- representative `afbab09a68937e6674e23fbddc6905cdfd8a86372007c7f6713d64e9863b8afd` and parent `44082b06...d2d8` matched the quick binding.

These are seven fresh checker invocations (one interface, three additions-only local cases, three physical lifts) for one family and recipient, not 2,469-family or all-recipient replay.

### 3. First-tier encoding controls and one actual row

`checks/replay_selected_row.py` freshly recomputed the independent first-tier digest for the selected row: 419 fixed and 39,909 other suffix clauses, yielding `44082b06...d2d8`. This is one actual row replay, not acceptance of the stored 11,585-row log.

`checks/encoding_controls.py` exhaustively tested the documented counter recurrence for every `1 <= k <= n <= 7`: 28 configurations, 1,538 complete input assignments, and 3,076 guarded outcomes. Every formula-with-auxiliary-variables satisfiability result agreed with the input cardinality threshold. It also recomputed 6,612 injected physical variables, 11,571 edge clauses, 123,424 triangle clauses, 134,995 total host clauses, and host SHA-256 `c68e1cc384a4982b29691edc76078a175739f8fde358c07de4297c6ae8b86fc1`.

### 4. Stored-ledger consistency, explicitly not replay

`checks/ledger_consistency.py` independently aggregated the stored transport rows and obtained 11,585 rows, 983,774 live recipients, 983,774 root and 1,966,300 child queries, 3,066 empty-owner queries, 17,618,107 root occurrences, 24,921,805 child occurrences, and 2,469 matched physical samples, matching the supplied summary. The additions ledger has 2,469 distinct `(arm,pair,case)` keys with case counts 829 root, 634 color 0, 823 color 1, 182 color 2, and one empty owner. These checks establish data consistency and uniqueness only.

## Source review and necessary premises

- `audit_rup_transport.py:26-70` proves a generic four-color physical arm interface. `:73-103` regenerates exact local queries, checks source hashes, drops only deletion records, and freshly checks the resulting additions candidates in forward RUP mode. `:123-126` enforces the full 830-owner/2,469-case totals only when run without a limit.
- `audit_transport.py:75-100` checks physical edge injection, auxiliary offsets, exact owner-selector mapping and clause images. `:112-163` checks each actual row host, signed root/pentagon units, representative/query construction and selected direct-replay hashes. `:194-198` enforces full census totals only on an unlimited run.
- These routines are complementary. `audit_transport.py` does **not** consume the additions-only proof ledger, so running it alone proves query identities, not local UNSAT proofs. `audit_batch.py:38-40` correctly runs the independent first-tier check, additions-only proof/interface check, and per-recipient transport check in that order. Any reproduction citing the full argument must retain all three obligations, especially both transport routines.
- Child queries preserve the guard: `propagate_rules.py:23-30`, `audit_transport.py:63-67,92-95`, and `campaign_solver.py:95-116` all add the pivot unit before child transport. Only the `empty` case is cross-checked to a closed-parent ledger (`audit_transport.py:153-155`). Root/child consequences strengthen searches but do not close a surviving original parent.
- `audit_first_tier.py:126-142` implements the tested staggered counter; `:145-194` reconstructs a declared marked row and binds it to the archived digest. The narrative correctly limits graph-to-CNF soundness to colorings realizing the declared row/threshold hypotheses and explicitly leaves upstream classification, complete case coverage and survivor certificates outside its global theorem claim.
- At committed coordinator revision `a74f7c2915f4482f5f7906bb2ca451acd031de4d`, `tools/refinement/cube_probe.py:151-190` uses the same signed injection, physical prefix, exact target units and warning-free `-i -U` acceptance. The checked new transport semantics agree with that committed mechanism. This direction did not re-audit the coordinator's nine replacement records.

## Remaining untested commitments / non-inferences

- I did not replay all 2,469 additions-only proofs, all four interfaces, all 11,585 row encodings/recipient projections, the 2,950,074 physical consequence queries, or the 3,066 closed parents. Only the bounded cases above were fresh executions.
- The totals 3,066/983,774 and the frozen 983,774 campaign roster remain stored/report claims in this direction, though their transport-ledger arithmetic is internally consistent. No total change or whole-row closure is inferred.
- I did not prove the upstream critical-template classification, complete campaign enumeration, or a graph-to-CNF-to-Ramsey theorem; I ran no Lean replay. Exact archived CNF hashes alone cannot supply those mathematical premises.
- I made no runtime claim and started no K58 search. No OPEN case was promoted to SAT or UNSAT.

## Reproduction and evidence

From this member directory, with the already inspected inputs installed under `audit_e/installed`:

```sh
python3 audit_e/checks/encoding_controls.py
python3 audit_e/checks/ledger_consistency.py
python3 audit_e/checks/replay_selected_row.py
audit_e/installed/.venv/bin/python audit_e/checks/replay_selected_full.py
# The output directory must be new for each independent quick recheck:
python3 audit_e/checks/independent_transport.py \
  --quick audit_e/quick-src/K58_review \
  --checker audit_e/checks/drat-trim \
  --out audit_e/recheck-transport
```

Primary outputs: `outputs/independent-transport-v2-command.txt`, `artifacts-transport-v2/summary.json` and `artifacts-transport-v2/*.log`, `outputs/full-selected-transport.json`, `outputs/first-tier-selected-row.json`, `outputs/encoding-controls.json`, and `outputs/ledger-consistency.json`. Input and final evidence hashes are in `inventory/input-sha256.txt` and `outputs/final-evidence-sha256.txt`.
