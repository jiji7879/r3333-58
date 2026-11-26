# Independent final coverage assessment — 35 K58 wall rows

## Outcome

**All 35 declared depth-two plans were completed and all 140 leaf workers were executed. No whole row was closed.** The final per-cube frontier is:

| leaf outcome | count |
|---|---:|
| OPEN, conflict limit | 139 |
| CHECKED_UNSAT receipt and independently replayed ordinary DRAT | 1 |
| CHECKED_SAT / CHECK_FAILED / PROOF_PENDING / NOT_RUN | 0 |
| **Total** | **140** |

Thus **zero complete covers, zero verified whole-row results, and zero parent DRAT exports** are claimed. Every row retains at least one OPEN cube. No `R(3,3,3,3)` or profile-elimination conclusion follows.

The complete 35-row frontier is `frontier.rows.tsv`; the complete 140-cube ledger is `frontier.cubes.tsv`. They include full 64-hex IDs, profile, branch, parent and plan SHA, actual `{r,r0,r1}` split variables, cube ancestry and signs, budgets, conflicts, timings, proof hashes, replay status, shared-pass accounting and verifier bindings. `live-coverage.json` is the full nested audit; `result.json` is the compact checked summary.

## What was independently checked

- Canonical selection: 35 distinct rows, five per profile. Selection SHA-256 `86188322ae02e4e25b6eafe83564acb9c3592d1ecf19213b7921b3920442302a`; frozen uncompressed roster SHA-256 `d5641e1ba875bc4ec5fbe156d48585f610e877f5232de7181eb464d4ad4fa2bc`.
- **35/35 static plan audits PASS.** Every plan is tier `first`, depth exactly 2, CAS `pentagon`, arm mode `both`, lookahead 12, with its arm pair tied to the frozen row. The selection metadata was compared to the frozen roster, including branch, profile, root kinds, arm and placement.
- All 35 stored `parent.cnf` files are byte-identical to fresh regeneration with `tables=True,total_critical=True,full_root=False`; they are not historical lex-augmented or depth-zero inputs. There are 35 distinct parent hashes and 35 distinct plan hashes.
- Every `working.cnf` preserves the exact original parent clause prefix and adds exactly the plan's declared cut count. Parent, working and CAS hashes match the plan. Each tree reconstructs exactly four cubes with signs `-v` on branch 0 and `+v` on branch 1.
- **Shared first pass:** 35/35 receipts are OPEN by the 350,000-per-cube/1,000-tail conflict limits, exactly zero by the 300-second wall limit. There are no shared VERIFIED_UNSAT or SAT receipts, so no shared trim/core replay is applicable and no shared proof credit is given.
- **Leaf phase:** all 140 receipts bind to the exact plan/node/cube. All use CaDiCaL 1.9.5 / python-sat 1.9.dev22, proof `eager`, 300 seconds, 1,000,000 conflicts and checker limit 600. The 139 OPEN leaves all explicitly say `conflict limit`; their native counters range from 1,000,000 to 1,000,006 and elapsed times from 38.132 to 68.831 seconds. No UNKNOWN/timeout is treated as UNSAT.
- **Final pinned `wallcc.py verify`:** all 35 plans were checked with `--jobs 1 --check-seconds 600 --expect-sha256 ORIGINAL_PARENT_SHA`. All 35 verdicts are OPEN; aggregate cube verdicts are exactly `OPEN:139, VERIFIED_UNSAT:1`. Raw commands and outputs are in `wallcc-verify.json` and `verify-logs/`.
- No complete cover was eligible for `export-drat`; consequently no export was attempted and no parent proof bytes are claimed. This is not an export failure: the prerequisite complete cover does not exist.

## Per-profile frontier

| profile | plans | cubes | independently certified leaves | OPEN leaves | complete rows |
|---|---:|---:|---:|---:|---:|
| 15,14,14,14 | 5 | 20 | 0 | 20 | 0 |
| 15,15,14,13 | 5 | 20 | 1 | 19 | 0 |
| 16,14,14,13 | 5 | 20 | 0 | 20 | 0 |
| 16,15,13,13 | 5 | 20 | 0 | 20 | 0 |
| 16,15,14,12 | 5 | 20 | 0 | 20 | 0 |
| 16,16,13,12 | 5 | 20 | 0 | 20 | 0 |
| 16,16,14,11 | 5 | 20 | 0 | 20 | 0 |
| **Total** | **35** | **140** | **1** | **139** | **0** |

## Sole certified leaf — not a row closure

| binding | value |
|---|---|
| full row ID | `3d443146013949bb1f01e907953c366c617e4178c4638cc2c8eb59d4e2745d1c` |
| profile / branch | `15,15,14,13` / `1347` |
| original parent SHA-256 | `d27d34c0d8336997d545c76120e040ff1aa0f448ef362d443502372d4c1a1ff2` |
| plan SHA-256 | `4dea9e14284398299ce866b63783269de8129b62efcc438997f2aa1a665841fa` |
| actual split tree | `{r:4262, r0:5104, r1:4645}` |
| closed node / cube | `r11` / `[4262,4645]` |
| leaf budget | 300 s; 1,000,000 conflicts; eager proof; check 600 s |
| ordinary leaf DRAT | 6,707 bytes; SHA-256 `1e605f06553a1152d358bccf16f49dcb7a4102da7ccb9d3adade9a2f662d3007` |
| matching CAS prefix SHA-256 | `036ec2b03282f64d5ccdc1336210ef9b4f565c07abbc04138971ad340a08a95f` |
| checker | `drat-trim` SHA-256 `a9571deb08430a3d7f7a72074440f53e2ad48196dced50b146835052a18e9066` |
| independent replay | `s VERIFIED`, ordinary binary DRAT `-i -p -t 600` on the original parent plus the exact two cube units, with the matching CAS prefix |
| replay binding SHA-256 | `fb3c2d3c6e139bb538b65f961a1122d81272a087e57292ce0448210c3bf0f9af` |
| raw replay log SHA-256 | `06b383eff2f4fbac95186c5e35fa91cb55cb05e427239b8d99aecccbc8daf33d` |

The other cubes of this row are `r00=[-4262,-5104]`, `r01=[-4262,5104]`, and `r10=[4262,-4645]`; all three are OPEN at conflict limits. The final parent verdict is therefore **OPEN with three OPEN cubes and one VERIFIED_UNSAT cube**. The valid child certificate is real progress but supplies no whole-row coverage credit.

## Retention and unfinished work

At the final snapshot, all six campaign directories together occupied 245,018,624 allocated bytes (well below 40 GiB). The exact retained ordinary-DRAT inventory was 35 plan CAS prefixes plus one leaf certificate, 5,123,535 bytes in total. No parent export, retained SAT model, raw/trim shared trace, OPEN leaf DRAT, attempt directory or unfinished prefix remained. No native search worker remained at the snapshot. The certificate paths and hashes are stable; the total-directory byte figure is only the stated `du` snapshot, not a content receipt.

What remains to close any row is explicit: solve every still-OPEN cube in `frontier.cubes.tsv` under a newly authorized budget/campaign, retain and independently replay each resulting ordinary DRAT, rerun strict complete-cover verification, and only then attempt export. The present campaign does not supply those proofs.

## Reproduction and evidence map

Run from `.ultramath/smwxwbjk8/m6` with `PYTHONDONTWRITEBYTECODE=1` and the pinned virtualenv Python:

1. `audit_coverage.py --replay --output live-coverage.json` — independent selection/roster/formula/tree/hash/receipt/budget audit and cached ordinary replay.
2. `audit_shared.py --coverage live-coverage.json --output live-shared.json` — shared first-pass and SAT/shared-proof accounting.
3. `verify_covers.py --coverage live-coverage.json --output wallcc-verify.json` — strict pinned verifier with explicit parent hashes.
4. `make_frontier.py --coverage live-coverage.json --shared live-shared.json --verify wallcc-verify.json` — complete row/cube TSV frontier and hash manifest.

Primary evidence:

- `result.json`: compact final outcome, per-profile counts, exact certified-leaf evidence, retention and evidence hashes.
- `live-coverage.json`: all 35 plans and 140 leaf audit records.
- `live-shared.json`: all 35 OPEN shared receipts and termination classifications.
- `wallcc-verify.json`, `verify-logs/`: all 35 final strict verifier bindings and raw outputs.
- `frontier.rows.tsv`, `frontier.cubes.tsv`, `frontier.manifest.json`: complete flat frontier and SHA bindings.
- `replay-cache.json`, `replay-logs/3d443146013949bb1f01e907953c366c617e4178c4638cc2c8eb59d4e2745d1c-r11-ordinary.log`: independently retained ordinary replay result and raw checker output.

This auditor launched no SAT search process; its heavy checks are source/hash inspection and proof replay only.
