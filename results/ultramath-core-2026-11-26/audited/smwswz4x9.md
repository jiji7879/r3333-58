# Archival report — old swarm `smwswz4x9` (Group D, audit by m4 of smwx73ni9)

Audit only; no solver was run in this session. Main sources: the committed judge record
**`results/judge-smwswz4x9-m4.md`**, `results/arm-class-2026-11-24/README.md`, `PROOFS.md`,
`REPORT_2026-11-23.md`, the 8 transcripts and the member reports.

## 0. Scope the swarm was given

The zero-set / multiplicity layer of the K58 campaign, in the fully-sending uniform child of
profile `(15,14,14,14)`: `A` is the colour-0 arm of the root with `|A| = 15`, `B` an ordinary
**14-arm**, `Z(v) = {a ∈ A : a sees v in colour 0}` and the multiplicity of an outside vertex is
`m(v) = |Z(v)|`. With `m(v) = 5` forced in that child, the layer asks **which multiplicity
profiles a single ordinary arm can realise** and whether the layer can exclude the no-singleton
case `(3,3,2,2,2,2)`. Directions: A–H (six-distinct, no-singleton, repeated-pentagon codegree,
forced-singleton types, cross-arm transfer, design/incidence filter, per-type zero-set census,
and a Lean formalisation of the forced-pentagon parent rule).

## 1. Acceptance ledger — the coordinator's own verdict record exists for this swarm

`results/judge-smwswz4x9-m4.md` (5,542 B) opens: *"The swarm ended **solved**, 8 directions
accepted (d8 abandoned)"* and gives a direction-by-direction verdict table. Committed as
**12f0864** "Judge m4 of smwswz4x9: accepted, and the multiplicity layer is not exhausted after
all". That table, not the members' titles, is the acceptance authority below.
**"Solved" here is the platform's swarm state: it is a statement about this layer, not a Ramsey
bound, and no Ramsey bound follows from it.**

| dir | member | coordinator verdict (abridged from the committed table) |
|---|---|---|
| d1 | m2 | six-distinct verified **as far as the join layer**; residual reduced to 3 internal signatures; **join layer not replayed** |
| d2 | m5 | 48 candidates, **44 survive the incidence layer**, 4 excluded with DRAT and short proofs; layer exhausted *at that level* |
| d3 | m1 | repeated-pentagon codegree: finite core correct, chain checks out |
| d4 | m4 | per-type zero-set census: **37 types dead**, **33 profiles realised**, 219/113 reproduced — **accepted** (the only direction with its own committed judge file) |
| d5 | m8 | no-singleton case **compatible** with the whole layer; two new kernel lemmas; 219 census reproduced |
| d6 | m7 | cross-arm transfer **partial**: decided instances + kernel lemmas, **general statement not proved** |
| d7 | m6 | design filter decided for all **135 partitions** (53 with a design, 82 without) |
| d8 | m3 | abandoned (the `(15,14,14,14)` rows are the wall) |
| d9 | m3 | forced-pentagon parent rule **kernel-checked** |

Judge-side checks recorded in that file (independent code, not the member's):

* an own graph6 decoder + own placement search reproduces type 2 → 2 placements / 1 profile
  `(2,1^12)` and type 9 → 352 placements / 7 profiles;
* `R6` confirmed on its sharpest cases — `(5,4,4,1)` and `(5,5,4)` **are** realised (on type 9);
* `R1` confirmed by a second argument: the campaign's own `excluded14.txt` lists the **same 37
  types, entry for entry**;
* 5,180 witnesses over 295 types, 0 failures; data consistency (332 types, 332 `COMPLETE`
  searches, 37 with zero placements, 219 realising `(3,3,2,2,2,2)`, 48 allowed profiles of which
  33 realised and 15 never).
* **Explicitly not verified by the judge**: the exhaustive searches themselves (it re-ran 2 of
  332 types), so the 15 never-realised profiles and the other 330 completeness claims rest on
  the member's enumerator. **No DRAT exists for the 37**, as the member's §6 states.

## 2. Exact scope and OPEN objects

* **The layered result, in the corrected form** (this supersedes the campaign's old sentence
  "44 profiles survive and no multiplicity argument removes a survivor"):
  `48 arithmetic candidates → 4 excluded by the packages → 44 survive the incidence layer (m5)
  → only 33 are realised by some arm type (m4)`; the 11 that die at arm-realisation are listed in
  the judge file: `(4,2,1^8) (4,3,1^7) (4,4,1^6) (5,1^9) (5,2,1^7) (5,2,2,1^5)
  (5,2,2,2,1,1,1) (5,3,1^6) (5,3,2,1,1,1,1) (5,3,2,2,1,1) (5,3,3,1,1,1)`.
* m5's and m4's statements **do not contradict**: m5's model is the *incidence* layer (classes are
  distinct 5-subsets of `A`, `d(a) ∈ {4,5}`, witnesses are support families on 15 points); m4's
  model additionally requires the rows to be **admissible in the arm's own colouring**. The
  filter order matters when either number is quoted.
* **OPEN**: the general cross-arm transfer statement (m7: the free-board combined instance is
  UNKNOWN at k = 6); the six-distinct **join layer was never replayed** (m2); the arm-realisation
  census's completeness (2 of 332 types re-run by the judge); the no-singleton case is
  *compatible*, i.e. not excluded, so that branch of the campaign stays open.
* Nothing here closes a `(15,14,14,14)` case, proves W2, or moves `R_4(3)`. The judge file says
  so: the net effect is that "the zero-set multiplicity layer is now charted to its arm-level
  bottom (33 profiles)".

## 3. Retained in Git

* **`results/judge-smwswz4x9-m4.md`** — the swarm's board verbatim plus the 44 → 33 correction
  (5,542 B). This is the file to keep.
* **`results/arm-class-2026-11-24/README.md`** (8,901 B) — the reused-object record: the
  literature's 115 classes and the campaign's 332 roles are the same set
  (`102·3 + 13·2 = 332`, `102·6 + 13·3 = 651`); the cover/placement census is m4's computation
  reproduced; the answer depends on the **role**, not the class (88 always survive, 5 never,
  22 mixed); the per-sender triple test has **exactly zero** pruning power (600 completions over
  all 30 roots); the nine-position matching test is vacuous; the core cannot supply the floor;
  Theorem V; m8's role 24 vs 155; root+A+B gives 1180 accepted, 0 rejected.
* **`PROOFS.md` §(zero-set multiplicity)** and `REPORT_2026-11-23.md` §3, plus the committed
  `.lean` counterparts `lean/K58/{Multiplicity, Incidence, DesignIncidence, ForcedPentagon,
  ProfilesIncidence}.lean`.
* The swarm's own `m5/Profiles.lean`, `m5/Incidence.lean`, `m3/…` Lean files remain only under
  `.ultramath/` (which `.gitignore` excludes).

## 4. Reproduction

```sh
cd .ultramath/smwswz4x9/m5 && python3 decide_all.py && python3 check_witness.py && python3 verify_drat.py
#   48 kissat runs -> 44 SAT / 4 UNSAT; 4/4 proofs replayed against CNFs regenerated from encoder.py
cd .ultramath/smwswz4x9/m6 && python3 verify_all.py     # design filter for all 135 partitions
cd .ultramath/smwswz4x9/m1 && python3 verify_certs.py   # repeated-pentagon codegree certificates
```

Judge-side independent reproduction is described in `results/judge-smwswz4x9-m4.md` §"What the
judge checked, with its own code".

## 5. Raw-evidence inventory (measured now)

* `smwswz4x9`: **761 files, 3,207,554,246 B (3.21 GB)**; transcripts 9.5 MB.
  Per member: m5 3,114.4 MB, m6 72.8 MB, m7 3.7 MB, m1 2.9 MB, m3 2.0 MB, m4 1.9 MB,
  m8 0.2 MB, m2 0.1 MB.
* Largest: `m5/work/p40_2_2_2_2_2_2_2.proof` **1,698,693,120 B** and `m5/work2/pr`
  **1,029,701,632 B** — together **2.73 GB, i.e. 85 % of this swarm**, and **neither is cited in
  `m5/REPORT.md`**: they are solver proof dumps from exploratory runs (`t1.py` starts kissat with
  `timeout=300`, so `pr` can be a proof from a killed run). No `s VERIFIED` record exists for
  either. The cited DRAT refutations are much smaller and live in `m5/work/dec/*.drat`
  (`work/dec` is 15 MB, 4 proofs, 4/4 replayed).
* Other large: `m5/work/p19_4_2_2_2_2_2.proof` 360,662,751 B (same unreferenced class);
  `m1/certs.tsv` 2,849,555 B; `m6/certs/*/d.cnf` ≈1.5–1.8 MB each.
* Text/source ≤ 2 MiB: **219 files, 12.35 MB** (12.33 MB unique) — the readable core is 0.4 % of
  the bytes.

## 6. Corrections and qualifications (carry forward)

* **48 is the candidate list, not the survivor set.** The judge's correction: the member's report
  called the 48 "profiles that survive the established theorems", but 4 of them are excluded by
  the campaign's own theorems (all four appear among the member's own 15 never-realised).
  **The surviving set is 44.**
* **Do not state "the multiplicity layer is exhausted" without its layer.** It is exhausted *at
  the incidence layer* (44); the arm-realisation layer removes 11 more (33). The old campaign
  sentence is superseded.
* **The 37 dead types have no DRAT**; the no-placement census is a member enumerator, only
  2 of 332 types re-checked by the judge.
* **m7's cross-arm transfer is partial**: decided instances and kernel lemmas exist, the general
  statement does not; the free-board combined instance is UNKNOWN at k = 6 (a timeout).
* **m2's six-distinct verification stops at the join layer**; the join layer was not replayed.
* The platform state "solved" must never be quoted as a mathematical result about `R_4(3)`; the
  committed `PROOFS.md` uses it only for the layer ("both closed solved at 8 of 8").

## 7. Archive disposition (recommendation)

* **Delete-first candidates (with a hash manifest first): `m5/work/p40_2_2_2_2_2_2_2.proof` and
  `m5/work2/pr` — 2.73 GB, uncited, unverified.** They carry no verdict and no statement depends
  on them; keeping them risks a later reader mistaking a partial proof dump for a certificate.
  The same applies to `m5/work/p19_4_2_2_2_2_2.proof` (361 MB) unless a citation is found.
* Keep the 12.35 MB readable core, `m5/work/dec/*.drat` (15 MB, the four replayed refutations),
  `m1/certs.tsv`, `m6/certs/` (72.8 MB, the design-certificate CNFs) and
  `evidence/file-manifest.json`; those are small and unique.
* Keep the four `.lean` files under `.ultramath/smwswz4x9/m5/` only if the repo's
  `lean/K58/{Multiplicity,Incidence,DesignIncidence}.lean` are confirmed to contain them
  (they exist and are committed; the swarm copies are 12,030 B and 19,490 B).
* Do not re-open: the incidence layer (decided), the design filter for 135 partitions (decided),
  or the no-singleton compatibility question (answered: compatible).
