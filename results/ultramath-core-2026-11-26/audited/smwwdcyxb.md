# `smwwdcyxb` — archival audit (Group A)

Read-only audit by swarm `smwx73ni9` / member m1, 2026-11-26. I read the member
transcripts, the coordinator handoff, the judge-critique restarts and the proof
stores under `.ultramath/smwwdcyxb` (22,009,836,573 bytes, 29,508 files,
m1–m8 + `transcripts/`). No solver was run, nothing was deleted, no file outside
`.ultramath/smwx73ni9/m1/` was written.

**Swarm problem** (verbatim from `transcripts/m1.jsonl` `[USER]`): reduce the
complete profile `(16,16,13,12)` from **140 OPEN frozen rows** to 0 with
independently verified exact coverage. The 140 rows split into **70 TU mixed,
56 TT, 14 UU**, charges **14/70/56**. Anchor row
`0404c3a224626a202cbfa4355bb0b19513ec815d182050440c580208861f2296`
(TU--, arm1, charge7, placement `[4,0,0]`). Hard exclusion: profile
`(15,14,14,14)` and `balance=True`.

## 0. Bottom line

* 8 members, **8 accepted directions** (d1–d3, d5, d6, d8–d10). Source of record:
  `results/final-smwwdcyxb-2026-11-26.md`, Git-tracked, last touched by commit
  `ef9a727`.
* That file states explicitly: this is **finite branch progress, not a proof of
  `R(3,3,3,3) <= 58`**. No full row was closed, no profile eliminated, no bound
  moved. The platform "solved" state means accepted finite submissions.
* **5 judge rejections** preceded acceptance, hitting m1, m2, m3 and m5 (twice).
  Rejections and repairs are evidence; the superseded text is still on disk in
  several member directories (§1.3, §6).
* The head-line mathematical content that survives is: 2 complete entrance
  families (**TT:2 and UT:3, 600+600 = 1200**), a 3-open-cube reciprocal
  frontier, a 25-object strict split per row (count discrepancy, §6.1), the
  K16 `(5,5,5)` regularity table, and the K15/K16 U/T classification
  certificates. The full raw-proof store is **not** a theorem.

## 1. Accepted vs claimed / rejected / unreviewed

### 1.1 What the verdict evidence is

| source | path | what it establishes |
| --- | --- | --- |
| coordinator handoff | `results/final-smwwdcyxb-2026-11-26.md` (tracked) | 8 accepted directions + per-direction limits |
| erratum | `results/verdict-correction-smwwdcyxb-m2.md` (tracked) | TT:3 was wrongly called complete; 1200 not 1800 |
| scoped entrance record | `results/entrance-brace-audit-2026-11-26/store-audit.json`, `AUDIT.md` (tracked) | 2,830/2,830 replays; per-family verified/open |
| frontier record | `results/cc-frontier-audit-2026-11-26/AUDIT.md` (tracked) | 343 nodes / 172 leaves / 169 certified / 3 open |
| m6 record | `results/m6-audit-2026-11-26/` (tracked) | 4 equal-kind parents, 21 hashes, n024 re-replay 264.3 s |
| per-submission | `transcripts/m*.jsonl` | `ultramath_submit` reply `{"submitted":true}`; after a rejection a new `[USER]` message quotes the judge |

There is **no per-submission verdict file** on disk. Acceptance of the final
submissions is established by the handoff/erratum/audit records above, *not* by
any member's own title or by the `submitted:true` reply (which only means the
platform took the report).

### 1.2 The eight accepted directions

| dir / member | accepted result (coordinator wording, abridged) | explicitly NOT established |
| --- | --- | --- |
| d1 / m4 | strict case of every one of the 140 rows covered by 25 one-small-critical cubes → 3,500 first-level objects; parents rebuilt, representative reductions replayed; Lean witness chain checked | no cube and no strict branch eliminated; long CDCL runs UNKNOWN |
| d2 / m7 | 343-node binary tree for the named augmented reciprocal CNF: 169 certified leaves, exactly 3 open cubes; leaf formulas + proofs hash-checked; one large external proof freshly replayed (347.168 s); two mixed-orientation 33-vertex zero-clone SAT models checked | no row/ticket branch closed; "clone-free" is loose — 2 cubes carry one positive clone selector, the 3rd pins only 12 |
| d3 / m1 | marked-free reciprocal parent for the 70 TU rows + exact 4-way reduction; 15 verified K16 local degree refutations; reproducible complete C4 family audit | the reciprocal parent itself UNKNOWN; no row closure |
| d5 / m8 | hash-pinned active/inactive refinements for all 140 rows; complete independent rebuild of all 280 frontier formulas; kernel-checked ticket-mass lemmas | neither balanced-active nor balanced-inactive refuted; strengthening experiments UNKNOWN |
| d6 / m2 | 2,830 stored entrance DRATs replayed with CNF/proof hashes; 3,600 keys matched to the 770-case residual | acceptance limited to TT:2 + UT:3 (1,200); not a no-entrance theorem; not the strict or balanced-active branch |
| d9 / m3 | complete finite K15/K16 U/T classification certificates: 388 order-16 candidates, 1,021,416 → **7,145** survivors, complete split/blocking chains, placement-orbit bookkeeping | no row eliminated; earlier cover/raw-transport "open gaps" must not be resurrected |
| d10 / m5 | physical colouring checker: 12 valid artifacts pass, the labelled one-defect K51 artifact rejected; 16-vertex templates matched to pinned templates; fully critical attached 16-arm realisable locally at K32 | local search found no K58 model — **not** impossibility evidence |
| d8 / m6 | n017, n022, n024 refuted with hash-matched DRATs on augmented formulas; 4 marked-free TT/UU parents clause-audited; counting witnesses re-verified in exact rational arithmetic | only `n025` remains of the original 13-leaf decomposition; auxiliary leaves are not rows; equal-kind parents unrefuted |

### 1.3 Rejected claims, with the judge's reason (all in `transcripts/`)

1. **m1 / d3, rejection 1** (`transcripts/m1.jsonl`, index 241): K16 table has
   **15** refutations (k=0..15 minus 5), not the "11" written in §4/PROOF;
   `rec-H-clone-c4.cnf` not reproducible (`c4free=581760`, current builder adds
   1745280, `audit-B1.log` said 629280). Repaired in `REPAIRS.md`; rebuilt
   byte-for-byte, MANIFEST refreshed; resubmitted; accepted.
2. **m2 / d6, rejection 1** (`transcripts/m2.jsonl`, index 244): "an entrance is
   only β_r≥1, not the root-strict condition"; the α=β=1 example has an entrance
   and is balanced-active; claimed coverage 3,391/3,402 was wrong (0.5,5,5
   shapes: UU:2 600 + UT:2 600 + TT:2 600 + UT:3 600 + UU:3 398 + TT:3 593
   + 11 cases); "2400 complete" wrong; `run_ent` deleted the DRATs so nothing
   was replayable. Repaired by keeping the proof bytes (now 8.62 GB store),
   resubmitted; accepted with the narrowed 1,200-case scope.
3. **m3 / d9, rejection 1** (`transcripts/m3.jsonl`, index 271): shipped
   `certpipe.py` had no CLI and no `has_alpha6`, so `python3 certpipe.py 15
   surv15.txt` could not rebuild `surv15.txt`; `drive.py` deleted final CNF/DRAT;
   anchor receipt 67,894 clauses vs REPORT.md's 67,219. Repaired with
   `alpha5.py` + `certify.py`; accepted.
4. **m5 / d7, rejection 1** (`transcripts/m5.jsonl`, index 467): "SUPPORT GAP IS
   FALSE" — `K58.supportShape_no_cycle4`, `pinned_support_no_cycle4`,
   `critical_support_no_cycle4` already check in `smwvpsb38/m5`; `full_root=True`
   encodes `H>=w=32`, not `H=32`; `RealizesFamily` already has `w<=H` so
   `H<=6` is not an extra row obligation; the reciprocal residual was stale.
5. **m5 / d7, rejection 2 → direction dead** (`transcripts/m5.jsonl`, index 564):
   raw transport is not a fresh open gap (the tracked 1,588-module replay prints
   `K58.Replay.rawTransportCover` and `K58.Replay.frozenCover` with standard
   axioms); the Romulus rejection was a negative control on the wrong proof;
   `root + 94 cuts` has SHA `a9bb080f20e3…` and replays.
   m5 then registered d10; that submission was accepted. **Consequence:
   `m5/REPORT.md` and `m5/COVERAGE_TREE.md` are the rejected d7 artifacts; the
   accepted m5 report is `m5/REPORT_D10.md`.**

### 1.4 Unreviewed / withdrawn

* Nothing in this swarm is "unreviewed": every member eventually had an accepted
  submission. The 5 rejections above are the only judge verdicts on disk.
* Withdrawn claims still present in files: TT:3 "complete" (erratum), m2's
  3,391/3,402 coverage (superseded by `store-audit.json`), m3's 67,219 clauses
  (superseded by 67,894), m5's d7 "support gap"/"fifth branch" wording.
* The coordinator's own first m2 verdict was wrong (it named TT:2, TT:3, UT:3 as
  complete = 1,800). `verdict-correction-smwwdcyxb-m2.md` supersedes it.

## 2. Exact scope and remaining OPEN objects

**Profile bookkeeping.** 140 OPEN frozen rows of colour-degree profile
`(16,16,13,12)` = 70 TU mixed + 56 TT + 14 UU, charges 14/70/56 for charge 1/4/7.
Local degree multisets are not frozen-row work; `(15,14,14,14)` is excluded.

**Literal hypothesis distinctions that reports depend on** (each one is a place
where earlier reports went wrong):

* an entrance is **β_r ≥ 1**, not strictness **β_r > α_r**; with `w=32`,
  `H−w = β−α`, so `α=β=1` has an entrance and is balanced-active;
* `full_root=True` encodes the floor **`H >= 32`**, not `H = 32`;
* `K58.SecondRoot.RealizesFamily` puts **`w <= H` inside the row scope**, so a
  deficient root is *not* a fifth row obligation (m3 abandoned direction F for
  exactly this; m5's rejected §9 resurrected it);
* the global cap **`d_c(v) <= 16`** comes from `three_colour_seventeen`; familyA
  caps require `c != q`; C4-free critical supports require a **critical source**.
  These are not unconditional `|N_c(x) ∩ A_c| <= 5` bounds;
* equal-kind (**TT/UU**) parents correctly **omit** the mixed clone cap, which TU
  rows carry; the 33-vertex 16-clone equal-kind colourings delimit that;
* `gen-L4` covers the **reciprocal and residual-inactive** children of the 70 TU
  rows (it forces the 57 criticality flags) and therefore does **not** cover
  balanced-active;
* the marked-free parents are **relaxations**: UNSAT transfers to the row, SAT is
  **not** a row counterexample;
* entrance families, literally: `TT:2` = T/T entrance in the **13-class**;
  `UT:3` = U/T entrance in the **12-class**; `TT:3` = T/T entrance in the
  **12-class** (partial); `UT:2` 13-class; `UU:2` 13-class; `UU:3` 12-class.

**OPEN objects (all still open):**

1. **All 140 rows** under their own hypotheses: no refutation and no physical
   countermodel. Exact refinements exist; an exact frontier is not an elimination.
2. Reciprocal C&C frontier: 3 open cubes, all starting with the six-literal
   `n025` cube — `r5_n025b2-019` (21 literals, UNKNOWN), `c485-022` (20,
   OPEN_NO_BUDGET), `c485_029-033` (12, OPEN_NO_BUDGET)
   (`m7/cc/merged-tree.json`, read directly).
3. Strict (d1), mixed, balanced-active (d5/d8), balanced-inactive branches.
4. Entrance store: **770 open (5,5,5) cases** — TT:3 157, UT:2 4, UU:2 9,
   UU:3 600 — plus the **4,740** degree-15 brace cases of shapes (4,5,5),
   (5,4,5), (5,5,4), not completed.
5. A complete semantic encoder bridge from real colourings to the CNF
   auxiliary/cardinality selectors (m6 delivered leaf/parent progress only).
6. m7's caveat: `n022`/`n025` cubes are clone-selector-positive, not
   "clone-free" in the loose sense.

## 3. Retained in Git

Nothing under `.ultramath/` is tracked (`repo/.gitignore` lists `.ultramath/`).
What Git retains is the coordinator's reports, audits and integrated copies:

| path | status | content |
| --- | --- | --- |
| `results/final-smwwdcyxb-2026-11-26.md` | tracked (`ef9a727`) | accepted directions + limits |
| `results/verdict-correction-smwwdcyxb-m2.md` | tracked | entrance scope erratum (1200/443) |
| `results/entrance-brace-audit-2026-11-26/` (20 files incl. `AUDIT.md`, `store-audit.json`, `accepted-scope.json`, `manifest.jsonl`, `residual.tsv`, 6 `verify-*.log`) | tracked | entrance replays + family counts |
| `results/cc-frontier-audit-2026-11-26/` (`AUDIT.md`, `audit_tree.py`, ledger JSONs) | tracked | 343/172/169/3 frontier audit |
| `results/m6-audit-2026-11-26/` | tracked | equal-kind parents, 21 hashes, n024 replay |
| `results/storage-cleanup-2026-11-26/` | tracked | the 2026-11-26 deletions + preserved-source manifest |
| `results/entrance-brace-audit-2026-11-26/ENTRANCE.md` | tracked | m2's corrected entrance report copy |

The members' own reports, Lean files and proof bytes are **not** in Git:
`m4/lean/WitnessChain.lean` (6,306 B), `m8/lean/TicketMass.lean` (2,611 B),
`m6/PROOF.md`, `m1/PROOF.md`, `m2/proofs/…` exist only under `.ultramath/`.

## 4. Reproduction commands and source paths

Commands **I actually ran** in this audit (read-only):

```sh
cd .ultramath/smwwdcyxb/m1 && sha256sum -c MANIFEST.sha256          # 25/25 OK
cd .ultramath/smwwdcyxb/m6 && sha256sum -c MANIFEST.sha256          # 21/21 OK
find .ultramath/smwwdcyxb/m2/proofs -name '*.drat.gz' | wc -l       # 3039
python3 - <<'P'   # manifest verdict census -> 2830 UNSAT + 2 UNKNOWN
import json;print(sum(json.loads(l)['verdict']=='UNSAT' for l in open('.ultramath/smwwdcyxb/m2/proofs/manifest.jsonl')))
P
wc -l .ultramath/smwwdcyxb/m3/work/surv15.txt                       # 7145
wc -l .ultramath/smwwdcyxb/m4/rows/SUMMARY.tsv                      # 141 = header+140
wc -l .ultramath/smwwdcyxb/m5/rows140.tsv .ultramath/smwwdcyxb/m8/work/runs/root-active-140.jsonl  # 141 / 140
python3 -c "import json;t=json.load(open('.ultramath/smwwdcyxb/m7/cc/merged-tree.json'));print(len(t['nodes']),len(t['leaves']),len(t['open_leaves']))"   # 343 172 3
```

Member-documented reproduction (not re-run by me, solver work):

* m1: `python3 build_rec.py rebuild-H.cnf --clone --c4` must reproduce
  `rec-H-clone-c4.cnf` byte-for-byte (SHA `0398839b…`); `validate_rec.py`,
  `symmetry_check.py`; the K16 table from `k16_regular.py` + `k16-local-table.json`.
* m2: `guardrow.py` + `m2/proofs/manifest.jsonl` + `residual.tsv`; the audit
  harness is `results/entrance-brace-audit-2026-11-26/{check_store.py,
  replay_missing.py, finish_audit.py, drive_ent.py}`.
* m3: `m3/work/{alpha5.py, certify.py}`; survivors `work/surv15.txt` (7,145
  lines), registry `work/registry140.jsonl` (140 rows).
* m5: `m5/checkcol.py` (colouring checker), `crosscheck_artifacts.py` (template
  isomorphism), `seek_row.py`.
* m6: `m6/MANIFEST.sha256` (21 entries), `REPRODUCIBLE.sha256`, `lc*.drat`.
* m7: `m7/cc/merge_cc.py`, `COVERAGE.md`, `external_verifications.json`.

## 5. Raw-evidence inventory (bytes, measured by `du -sb` / `stat`)

| path | bytes | files | note |
| --- | ---: | ---: | --- |
| `.ultramath/smwwdcyxb` | 22,009,836,573 | 29,508 | whole swarm |
| `m2/proofs` | 8,619,795,662 | 3,042 | 3,039 `.drat.gz` + manifest/replay/residual; manifest 2,832 records |
| `m7/cc` | 7,593,520,757 | 1,179 | C&C runs, nodes, proofs |
| `m4` | 2,203,249,631 | 819 | strict-branch CNFs, 12 files in `strict/` |
| `m6` | 1,799,898,022 | 188 | 3 big DRATs below |
| `m5` | 1,113,416,092 | 1,039 | probe DRATs, Lean census `.olean`s |
| `m1` | 444,782,831 | 91 | rec-*.cnf + `k16-regular/*.drat` |
| `m3` | 222,591,115 | 23,068 | many small cert files |
| `m8` | 657,223 | 47 | small; JSONL ledgers |
| `transcripts` | 11,811,465 | 8 | full member conversation logs |
| text/source files ≤2 MiB, all members | 24,731,099 | 2,024 | the "readable core" |

Largest single proofs (manifest candidates):

| file | bytes |
| --- | ---: |
| `m7/cc/run5/r5_core024-001/failed/r5_core024-001-001.drat` | 973,995,039 |
| `m7/cc/run5/r5_n025a-015/failed/r5_n025a-015-001.drat` | 795,753,847 |
| `m7/cc/run6/n025b_core/failed/n025b_core-001.drat` | 622,412,051 |
| `m7/cc/run11/c485_028/failed/c485_028-001.drat` | 585,308,080 |
| `m6/lc6-n024.drat` | 498,189,884 |
| `m7/cc/run4/core017/failed/core017-001.drat` | 417,440,099 |
| `m6/lc2-n017.drat` | 393,820,584 |
| `m7/cc/run10/c485_032/verified/c485_032-001.drat.gz` | 383,865,054 |
| `m6/lc-n022.drat` | 235,672,894 |
| `m2/proofs/TT_3_5,5,5/bb80b0c8….drat.gz` | 169,028,839 |

(The `failed/` names are original checker timeouts that were later verified
externally — see `m7/cc/COVERAGE.md` and `external_verifications.json`; do not
read them as failures.)

## 6. Qualifications, corrections, and what I could NOT verify

1. **Cube count mismatch (unresolved).** The handoff says "25 one-small-critical
   cubes, 3,500 objects". The shipped `m4/certs.json` holds **29** cubes under
   `beta0_with_root_flags` plus four singleton groups (`root_flag_0_must_be_true`,
   `…_1_must_be_true`, `…_2_must_be_false`, `…_3_must_be_false`). I did not
   reconcile 25 vs 29; do not quote 25 as evidence-checked.
2. **Store size vs manifest size.** `m2/proofs` holds **3,039** `.drat.gz` files
   but the manifest has **2,832** records (2,830 UNSAT + 2 UNKNOWN). Directory
   counts are *not* proof counts: `UU_3_5,5,5` has 40 files and 0 manifest
   records; `TT_3` has 599 files and 445 records. Count by manifest, never by
   `ls | wc -l`.
3. **`m2/.scratch` is gone.** The 2.78 GB scratch (the first, rejected
   submission's `ent/coverage.txt`, `ent/ledger.jsonl`) was deleted on
   2026-11-26. Only 42 text files survive inside
   `dist/legacy-scratch-text-2026-11-26.tar.gz` (I checked: 8,386 entries, 42 under
   `.ultramath/smwwdcyxb`). The first-submission evidence paths are therefore
   **dead paths**; the live record is `m2/proofs/`.
4. **"Solved" ≠ theorem.** Eight accepted finite submissions; the handoff is
   categorical that no row, profile or bound moved.
5. **No UNKNOWN was ever promoted.** Every UNKNOWN/timeout in these reports is
   recorded as UNKNOWN (`rec-B1` 900 s/1.65M conflicts, four strict cubes
   700–1100 s, `m7` three open cubes, etc.). Do not read `failed/` or `UNKNOWN`
   as UNSAT.
6. **Not verified here:** the 2,830 drat-trim replays (I read
   `store-audit.json`, I did not re-replay 8.6 GB); m4's 3,500 per-row objects;
   m7's external 347 s replay; m3's 388-candidate enumeration (I only confirmed
   `surv15.txt` = 7,145 lines and `registry140.jsonl` = 140 rows); m5's k32
   colouring (checker not re-run); m6's n024 replay (264.3 s, recorded in
   `results/m6-audit-2026-11-26/`). What **I** verified myself: m1 MANIFEST
   25/25, m6 MANIFEST 21/21, all byte totals and file counts above, the
   `merged-tree.json` node/leaf/open counts, and the row counts of the four
   140-row ledgers.

## 7. Retention recommendation

* **Keep (small, unique, not in Git):** `m1/{REPORT.md,PROOF.md,REPAIRS.md,
  MANIFEST.sha256}`, `m2/ENTRANCE.md`, `m3/work/{REPORT.md,PROOF.md,SHA256SUMS,
  registry140.jsonl,RUNS.tsv}`, `m4/{REPORT.md,certs.json,rows/SUMMARY.tsv}`,
  `m5/{REPORT_D10.md,rows140.tsv,dispatch140.tsv,checkcol.py}`,
  `m6/{REPORT.md,PROOF.md,MANIFEST.sha256}`, `m7/cc/COVERAGE.md`,
  `m8/{REPORT.md,PROOF.md,MANIFEST.sha256}`, `m4/lean/WitnessChain.lean` (6,306 B),
  `m8/lean/TicketMass.lean` (2,611 B). Total is a few hundred KB.
* **Manifest then drop:** `m2/proofs` (8.62 GB), `m7/cc` run trees (7.59 GB),
  `m4/strict` + `m4/rows` CNFs (2.2 GB), `m6/lc*.drat` (1.13 GB), `m5/work/probe`
  (0.9 GB), `m1/k16-regular/*.drat` (0.3 GB). Hash lists already exist for m1
  (25), m6 (21), m8, m4 (80 KB MANIFEST) — reuse them rather than recomputing.
* **Retain separately (tiny, unique):** `m1/k16-regular.json` (4,905 B, the 15
  refutations) and the 3 small `lc`/`rec` receipts; `m4/lean/WitnessChain.lean`;
  `m8/lean/TicketMass.lean`; `m7/cc/merged-tree.json` (the 3-cube frontier).
* **Do not re-run:** blanket degree caps, ticket cuts, the 4 UNKNOWN 900–1100 s
  reciprocal cases, or the `(15,14,14,14)` profile. These are measured
  no-improvement/OPEN records, not pending work.
