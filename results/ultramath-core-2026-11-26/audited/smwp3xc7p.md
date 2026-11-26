# Archival report — old swarm `smwp3xc7p` (Group D, audit by m4 of smwx73ni9)

Audit only: every statement is a citation to a file read here or to a command run here
(`du -sb`, `sha256sum`, JSON extraction of the 8 transcripts). No solver of this session ran.

## 0. Scope the swarm was given

Task text: *"R(3,3,3,3) = R_4(3), the 4-colour Ramsey number for triangles … Currently
51 <= R_4(3) <= 60 (lower: Chung 1973; upper: arXiv:2610.36648, a preprint with two-solver but no
DRAT verification). We want R >= 52, i.e. a good K_51."* (`.ultramath/smwp3xc7p/transcripts/m1.jsonl`
first user message; copy at `evidence/task1_smwp3xc7p.txt`).
Two handed-down experiments: (1) the **single-circulant** family on `Z/52` (colour 3 exactly a
triangle-free circulant with distance set `D ⊆ {1..26}`; the handoff claimed 217 orbits and 71
inclusion-maximal sets — explicitly to be recomputed, not trusted); (2) the **six pentagon
configurations** reduction for a good `K_51`/`K_52`. Plus directions 4–8: audits of the degree
restriction, an independent verifier, non-circulant structured families, LNS, Lean/encoding audits.

## 1. Acceptance ledger

34 `ultramath_submit` calls; **8 taken** by the platform, the rest refused for input length
(`evidence/raw_submit_board.json`). Full judge texts: `evidence/verdicts_smwp3xc7p.txt`
(8 restart messages). Committed coordinator record: **`results/run_smwp3xc7p_report.md`**
(6,558 B) — its "Accepted results" section is the acceptance authority used here.

### What the coordinator accepted / verified

1. **m7 (d6) — cyclic two-orbit classification.** For `2 ≤ m ≤ 26`, good 4-colourings of
   `K_{2m}` invariant under a cyclic action with two orbits of size `m` exist exactly for
   `m ∈ {2,4,5,7,8,10,11,13,14,16,17,19,20,22}` and for no `m ∈ {3,6,9,…,21,23,24,25,26}`;
   the 11 empty cases carry DRAT proofs (two replayed by the judge), the 14 non-empty cases are
   verified matrices. Consequence: no good `K_46/K_48/K_50/K_52` has an automorphism of cycle
   type two `m`-cycles with `m ≥ 23`. Recorded as **accepted** in
   `results/run_smwp3xc7p_report.md` ("Accepted results" 1).
2. **m3 (d8) — K58 cover.** **1,018** previously OPEN cases of the frozen 113,179-case cover are
   now CERTIFIED, each with a DRAT replay against a CNF regenerated from the frozen ledger row;
   64 replayed by the judge with the repo verifier, 0 failures, and a truncated certificate
   correctly rejected (negative control). OPEN **111,035 → 110,017**. The committed record
   states explicitly: *"Quote 1,018, not 1,050: 32 of the 1,050 certificates were re-derivations
   for cases already certified."* Upper-bound work only; **`R_4(3) ≤ 58` is still unproved** (the
   113,179-case reduction itself remains unaudited).
3. **m4 (d1) — circulant census, judge-recomputed**: 33,752 triangle-free distance sets, 1,102
   inclusion-maximal, **104 unit orbits**; "I computed these before your report existed, so this
   is now a genuine double-check, and the handoff's 217/71 should be treated as wrong."
4. **m1 (d7) — profile counts**: 47 colour-degree profiles at `n=51`, 39 at `n=52`, 6 at `n=60`;
   `nauty-geng -t -d2 -D5 13` returns exactly 6,723,525 triangle-free graphs, so the 6.69M/6.72M
   figure is real.
5. **m8 (d4) — LEDGER F2 closure** (the K16/K15 3-colouring classification reproduced
   independently, `|Aut|` 160/32 and 10/2) and the exact link alphabet; second judge verdict:
   all six colour classes of the 16-link are `srg(16,5,0,2)` (Clebsch), `λ=0, μ=2, α=5`.
6. **m8 (d12) — correction to the judge's own d7 verdict**, accepted: from `|N_c(x) ∩ N| ≤ 5`
   for `c ≠ 0` one gets **at least `16 − 3·5 = 1`** colour-0 edge into the link, **not 6**;
   the "6" would need only two other colours. This correction stands in
   `results/run_smwp3xc7p_report.md` ("One judge error, caught by a member").

### Rejected / not accepted as solutions

Every submission of this swarm was rejected as a solution. Directions **d4 and d7** (each two
rejections) and **d11** (two rejections) ended **dead**; **d2, d3, d5, d9, d10** were abandoned
(d2 "pre-closed by prior work"; d5 and d9 "run ended without a solution"; d3 and d10 "scope
exhausted"). **d6** is the only direction the platform marked `succeeded`, and that is a
statement about the platform's bookkeeping, **not** about a Ramsey bound: the accepted content is
the cyclic classification above.

Unreviewed / unsupported by any verdict found locally: m2's `AUDIT_REPORT.md` (14,994 B) beyond
what the committed record uses; m5's local-search logs (`err2.txt`, `err3.txt`, `err4.txt`);
m6's `report_final_m6.md`/`report_d10_edge_link.md`; the verification status of the large
`m4/out/pw/*.drat` and `m2/sym_work/p17_*.drat` files (no per-file `s VERIFIED` record was
located next to them in this audit).

## 2. Exact scope and OPEN objects

* **Lower bound: no good `K_51` exists in any family tried, and none was found.** The bound
  `R_4(3) ≥ 52` is **not** improved; `51 ≤ R_4(3) ≤ 60` is unchanged.
* **Experiment 1 (single circulant on `Z/52`)**: 6 of the 104 maximal masks excluded by
  DRAT-free counting (four by colour degree 17,17,18,26; two by `α(C(D)) = 20, 26 > 16`); the
  translation-invariant (Cayley) subfamily closed for all 104 masks by DRAT-verified UNSAT; the
  fully circulant subfamily decided for `n = 45,46,50,51,52,53` (no good circulant colouring;
  SAT at `n = 40,43,44` with verified models). **98 orbits remain OPEN**, every sound relaxation
  tested is satisfiable, and full instances were undecided at up to 50 min per mask.
* **Experiment 2 (six pentagons)**: the reduction is sound but **inert** — fixing A, B, C pins
  ≤ 30 of 1,275 edges (2.4 %), one verified `K_50` already contains 2,236 such 5-sets, and all 24
  instances tested were undecided at 60 s **including the six satisfiable by construction**.
  Recorded recommendation: *do not give this split more compute*.
* **Degree-16 cell**: `d_c(v) ≤ 16` (not 15), attained in every verified good `K_50`
  (13 vertices of profile `(11,11,11,16)` in `k50_z4z4_m6.col`, 16 in
  `k50_blockcayley_Z4xZ4_m4.col`, 19 in `k50_sanity_f2.col`, and in the 1-defect `K_51`); any
  split over link sizes 13/14/15 omits exactly those cases and must use **both** `K_16` templates.
* Open in the committed record: 98 circulant orbits; the degree-16 cell; general involutions;
  `Z/17` actions at `n = 51`; `Z/13` actions at `n = 52`; and the lower bound itself.

## 3. Retained in Git

* **`results/run_smwp3xc7p_report.md`** — the whole run's curated record (experiments, accepted
  results, corrections, open list, leverage table). This is the file to keep if only one is kept.
* `results/storage-cleanup-2026-11-26/{README.md, measurement.json, retained-source-sha256.json}`
  — record that **`.ultramath/smwp3xc7p/m8/scratch` (3,283,110,478 B) was already deleted on
  2026-11-26**, with 5,679 of its text files (2,790,180 B) preserved in
  `dist/legacy-scratch-text-2026-11-26.tar.gz`, sha256
  `5787069cc5f22801a74f0d3964c61d46229bba50def7a71b82e0811dc2c75375` (2,765,326 B, verified
  here to match). Raw DRAT/CNF/model bytes of that scratch are gone and were never claimed
  archived.
* `results/literature-r3333-2026-11-23.md`, `results/dc-experiment/exp.py`,
  `results/hailmary-*/…` mention the swarm; `artifacts/` (K50s, K15/K16 templates,
  `k51_relax_m3_1defect_NOT_a_valid_colouring.col`) are the verified objects it used.
* `.gitignore` excludes `.ultramath/`, `*.cnf`, `*.drat` — no swarm byte is in Git.

## 4. Reproduction

```sh
# K58 cover replay (m3), all paths under .ultramath/smwp3xc7p/m3/
cd w && unzip -q -o ../../../../dist/k58-solver.zip && cd k58-solver && ./k58.sh setup
EV=$PWD/ev0 ./k58.sh run --publication --tier both --output ev0 --kissat bin/kissat \
  --checker bin/drat-trim --profile 16,15,15,11 --kinds UUU- --include-closed --workers 2
EV=$PWD/ev0 WORKERS=3 ./k58.sh finalise --release release-final
sha256sum release-final/manifest.json   # b4d44efa922a3ddaf31855a2faf739a49eb2dfa117cec08aa03ba80d117a335b
# cyclic-orbit closures (m7): python3 bc.py / r4.py in .ultramath/smwp3xc7p/m7/ (report.md §files)
```

## 5. Raw-evidence inventory (measured now)

* `smwp3xc7p`: **10,012 files, 3,568,165,846 B (3.57 GB)**; transcripts 10.3 MB.
  Per member: m3 2,019.5 MB, m4 926.3 MB, m2 430.4 MB, m7 138.5 MB, m1 31.9 MB, m5 8.5 MB,
  m8 2.7 MB (its 3.28 GB scratch is already deleted), m6 0.1 MB.
* Largest: `m4/out/pw/pw_099_18.drat` 281,223,168 B; `pw_099_19.drat` 274,276,352 B;
  `m2/sym_work/p17_uc2.drat` 244,318,208 B; `m2/sym_work/p17_u.drat` 183,444,967 B;
  `m4/out/pw/pw_099_20.drat` 111,431,680 B; `m7/cnf/k50_Z25.drat` 57,054,679 B;
  `m7/cnf/k52_Z26.drat` 54,278,639 B.
* The verified K58 evidence under `m3/w/k58-solver/`: `ev0` **1.8 GB** (per-case CNFs + DRATs +
  logs), `release-final` **4.8 MB** (`manifest.json`, `cases.jsonl.gz` 5,014,485 B), `.venv`
  **27 MB** (a Python virtualenv: tooling, not evidence; also the reason three 31,896,496 B
  interpreter binaries appear in the byte table).
* Text/source ≤ 2 MiB: **6,740 files, 24.70 MB** (24.58 MB unique). 2,147 files under this swarm
  contain the string `s VERIFIED`; that is batch evidence, per-case, and was not re-audited here.

## 6. Corrections and qualifications (carry forward verbatim)

* Handoff circulant census **217 / 71 is wrong**; the true census is 33,752 / 1,102 / **104
  orbits** (three independent computations).
* **"Every colour degree ≤ 15" is false**; the bound is 16 and it is attained in every verified
  good `K_50`; the provable window for a circulant colour class is `[3,16]`, so
  "degree 12, 13, 14 or 15" is not a theorem (maximal triangle-free masks exist at degrees
  10, 11, 16, 17, 18, 26).
* **Template gluing must be done at the LABELLED level**: instantiating one representative per
  isomorphism class manufactures false inconsistencies (a labelled version declared 11 of 13
  orbits inconsistent; the unconditional instances are all satisfiable).
* **1,050 → 1,018**: quote the number of *newly* closed cases. 32 certificates were
  re-derivations of already-certified cases.
* m1's d11 table had two wrong entries; the involution row is **650** orbits of unordered pairs
  (25 fixed edges + 625 two-element orbits; `25 + 25 + 2·C(25,2) = 650`), not 350; and the
  corrected table gives "every exhaustive row leaves at least 1,139 free variables, and the rows
  below that (50, 650, 676, 936) are all non-exhaustive".
* A judge error, corrected by m8 and now standing in the record: the colour-0 count into the
  link is `≥ 1`, not `≥ 6`.

## 7. Archive disposition (recommendation)

* Keep `results/run_smwp3xc7p_report.md` as the authoritative text; keep the **readable core**
  (6,740 text files, 24.7 MB) and `evidence/file-manifest.json`.
* For the K58 evidence keep **`m3/w/k58-solver/release-final/` (4.8 MB: manifest + case list)**
  and the per-case `verified.json`/logs; hash-manifest **`ev0` (1.8 GB)** and allow removal — the
  certificates are regenerable (m3 measured 1.3 h solver + 1.4 h checker CPU) and were replayed
  by the judge, so the *statement* does not depend on the stored bytes.
* Remove without retention: `.venv` (27 MB tooling) and the two duplicate interpreter copies.
* Do **not** re-run: the six-pentagon split (measured inert, six satisfiable controls also
  undecided) and the 98 circulant orbits at previous budgets (measured OPEN, all relaxations
  satisfiable).
