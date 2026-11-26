# Archival report — old swarm `smwr3llof` (Group D, audit by m4 of smwx73ni9)

Status of this report: audit only. Nothing here was produced by a solver run in this session;
every claim below is a citation to a file I read or to a command I ran (`sha256sum`,
`du -sb`, `python3` JSON extraction of the transcripts).

## 0. What the swarm was asked to do

Task text (verbatim header): *"Verify and use an external handoff bundle on the (15,14,14,14)
wall, and close frozen case baa4e014 by split"*.
Literal scope as stated to the members (`.ultramath/smwr3llof/transcripts/m1.jsonl`, first
user message; copy at `evidence/task1_smwr3llof.txt`):

* campaign state `R_4(3) ∈ [51,62]`; a frozen cover reduces `R_4(3) ≤ 58` to **113,179 cases
  (31,751 OPEN)**; the seven wall profiles hold 11,585; profile `(15,14,14,14)` = **381 cases,
  all OPEN**, `T---` 308, `U---` 73; thresholds `(15,1,1,1)` and `(3,5,5,5)`.
* Target statement **W2**: no triangle-free 4-colouring of `K_58` has a vertex of profile
  `(15,14,14,14)` with `H(v) ≥ 15 = w(v)`.
* The case: `baa4e014…`, `T---`, arm 0, **charge 15**, marked `T` of order 15, branch 2;
  physical labels `r=0, A=1–15, B=16–29, C=30–43, D=44–57`; marked sender 6 with its four
  positions in `B` being `16,17,18,19`.
* Acceptance standard set in the task: a solution is a proof of W2 or of one family, or a case
  closed with a DRAT proof replayed against the **regenerated** CNF plus a **proved-sound split**.

## 1. Acceptance ledger (submitted vs accepted vs rejected vs unreviewed)

Evidence: 51 `ultramath_submit` calls recovered from the 8 transcripts; 9 were taken by the
platform (`{"direction":"dN","submitted":true}`), the rest were refused *before judging* for
input length > 1500 bytes (`evidence/raw_submit_board.json`). Judge verdicts are the restart
messages reproduced in full in `evidence/verdicts_smwr3llof.txt` (7 messages).

| member | direction | submitted | judge outcome |
|---|---|---|---|
| m2 | d7 | line 252 | **accepted as a report, not a solution** — "Not a solution; rejected as one." No second judge text (direction left `active`). |
| m3 | d3 | lines 253, 374 | rejected twice-as-text-once: first rejection ("Not a solution; rejected as one") then resubmission taken. No closure accepted. |
| m5 | d5 | line 169 | rejected once as a solution; four items explicitly **VERIFIED** by the judge. |
| m6 | d8 | lines 183, 266 | **two rejections → direction dead.** Second verdict settles the shape-scope question in the member's favour. |
| m7 | d6 | lines 201, 248 | **two rejections → direction dead.** Item 4 of the first submission was *wrong* and was retracted. |
| m8 | d9 | line 217 | rejected once as a solution; four items verified, one DRAT-backed exclusion. |
| m1 | d2 | — never submitted | REPORT.md only (`m1/REPORT.md`, 19,215 B). Unreviewed. |
| m4 | d1 | — never submitted | directory has `cuts/ data/ scripts/ work/` and **no report**; unreviewed, nothing to retain. |

**No submission of this swarm was accepted as a solution.** No case was closed, no family
proved, W2 unproved. The "solved"/state field of a platform board is *not* used anywhere in this
report: the only board snapshot recoverable from the transcripts for this swarm is a mid-run one
(`m8.jsonl` line 105) in which every direction is `active` with `rejections = 0`, i.e. it
predates the rejections and is not evidence of anything.

What the coordinator **did** verify or record (each line is coordinator-side, not a member title):

1. Bundle item 3 (extremal-join / 17-vertex theorem): all **108** stored refutations replay,
   519,805 steps, 338,587 lemmas, all RUP, zero RAT, zero deletions used — judge replayed it and
   called the all-RUP/no-deletion standard the house standard. Also recorded in
   `review/WALL_15141414_SWARM.md` §12 ("Bundle item 3 verified").
2. Bundle item 1: verified end to end by independent reimplementation — 115 catalogue rows,
   27 independence exclusions, 45 path/pentagon exclusions, 300 passing, 618 positive covers,
   18,276 named four-sets; `review/WALL_15141414_SWARM.md` §12.
3. Bundle item 2 (second bundle): "verified three ways" — **3,093 of 18,276** marked paths
   excluded in 72 of 300 orientations, **15,183** surviving, old 2,194 contained in the new
   list; `review/WALL_15141414_SWARM.md` §12.
4. The `baa4e014` split `uniform` / `some_six` is **sound, disjoint and exhaustive**, reproduced
   byte-exactly by three independent encoders: frozen CNF `71edaaa0…` (146,098 clauses),
   uniform `8e0b49a9…`, some_six `f5324082…`. The `some_six` child is a *single* 42-literal
   clause, `at_most_five` is 42 unit clauses (judge re-derived both).
5. The frozen CNF itself implies `sum_x m(x) ≥ 210` (per-block SAT at 14 units / UNSAT at 13);
   hence in the uniform child `m(x) = 5` for all 42 unconditionally.
6. Uniform-child biregularity: `d_0(a) = 15` for every arm point and `m(x) = 5` for every
   outside vertex (support sizes `(5,5,4)`); judge verified independently.
7. Colour-split interface identity `Σ_a e_f(N_0(a)) = 15·35 − 14·5 = 455` per ordinary colour,
   **1365** total `= 15·C(14,2)`; the judge re-checked it and classified it as a **check, not a
   constraint** (it cannot by itself give a contradiction).
8. Type-level system `(T)(V)(P)(Q)(N)` **with** the kernel-checked saturation bound
   `armFar_le_two` is **FEASIBLE** (m8's witness, judge ran it): the handoff's "may be
   infeasible" is dead and the type-level route cannot prove Family A.
9. `Z_58`-circulant exclusion: no circulant triangle-free 4-colouring of `K_58`. Judge replayed
   `drat-trim circ58.cnf circ58.drat` → `s VERIFIED` (1,177 of 123,627 clauses in core,
   392,264 of 509,748 lemmas, 0 RAT). **Existence-side only**: it removes a family of candidate
   colourings and does not advance the cover.

## 2. Exact scope and remaining OPEN objects

* **Uniform child of `baa4e014`**: open. Best-built form carries `m(x) ≤ 5` for all 42, the
  mixture bound `|M_c(x)| ≤ 5`, the same-word rule (36 words, both templates) and
  `≤ 16 with a missing ordinary colour`: 25,428 variables, 203,927 clauses, CaDiCaL **UNKNOWN**
  at 4.07 M conflicts in 244 s. With every cut that transfers as a clause: UNKNOWN at
  400k/600k/1.2M conflicts. A timeout here is a timeout.
* **Some-six child**: open; the 42-predicate prefix split is exhaustive but nothing closes it.
* **The 3,093-cut table is a module count, not a clause-level reduction**: it splits the uniform
  child into **15,183 (orientation, marked four-set) classes** whose orbits have ~10^10 labelled
  members, so it cannot be encoded as clauses. All 2,002 *physical* nine-sets fail without the
  orientation transport.
* **W2 unproved; `R_4(3) ≤ 58` unproved.** The 113,179-case cover reduction itself was never
  audited here (m2 audited only its soundness side: ledger row → plan → CNF),
  `m2/AUDIT.md`.
* Family-B scope fact (judge verified): **no `U---` row has charge 15**; the 73 split as 9 rows
  with arm 0 / charge 3 and 64 with arm 1 / charge 5. The bundle's three items therefore have no
  hypothesis among the 73 `U---` rows and cannot be ported there.
* Structured hunts left undecided: block-Cayley `Z_29 ⊕ Z_29` **UNKNOWN** at 400 s; block-Cayley
  `3×Z_19 + 1` **UNKNOWN** at 540 s (`m8/REPORT.md` §4). Both are single capped attempts.

## 3. Retained in Git (this swarm's knowledge, not its bytes)

`.gitignore` excludes `.ultramath/`, `*.cnf`, `*.drat`, `dist/`, so **no byte of this swarm is in
Git**. What is committed:

* `review/WALL_15141414_SWARM.md` §12 (round-three summary: items 1–3 verified, split settled,
  module-count reading, UNKNOWN budgets) and the header of `review/PROFILE_15141414_STATE.md`
  (names `smwr3llof` among the five rounds of the profile).
* `review/ERRATA.md` (hazard: `dense.marked_threshold` returns a single empty clause when the
  charge exceeds the guards — a manufactured closure hazard, not this swarm's result).
* Nothing under `results/`, `tools/`, `lean/`, `artifacts/` names this swarm; the Lean chain and
  the `tools/gap4`, `tools/pb` scripts it used already existed in the repo.

## 4. Reproduction (exact commands recorded by the members)

```sh
cd .ultramath/smwr3llof/m6/work/fc && python3 verify_split.py --row baa4e014 --child uniform
#  expects frozen CNF 71edaaa0…, uniform 8e0b49a9…, some_six f5324082…
cd .ultramath/smwr3llof/m8 && python3 circ_drat.py && drat-trim circ58.cnf circ58.drat   # s VERIFIED
cd .ultramath/smwr3llof/m5/work && python3 13_uniform42.py --cap 300 && python3 14_check_uniform42.py
#  uniform_mge5.cnf = uniform child + 42 proved units, sha256 9783d32a…
```

## 5. Raw-evidence inventory (bytes measured now with `du -sb` / per-file `stat`)

* `smwr3llof`: **1,405 files, 4,471,412,286 B (4.47 GB)**, transcripts 9.5 MB.
  Per member: m7 2,014.8 MB, m5 1,746.8 MB, m6 571.0 MB, m3 70.2 MB, m8 53.8 MB,
  m1 2.6 MB, m4 2.0 MB, m2 0.7 MB.
* Largest files: `m5/work/runs/uniform42/uniform_mge5_900.drat` **1,601,531,904 B**;
  `m7/runs/3efee19066b2.drat` 493.9 MB; `41ad024cd322.drat` 434.6 MB;
  `88bf7e10f142.drat` 381.3 MB; `h25a8034f36e3.drat` 340.8 MB; `h684a9ee2fa6f.drat` 248.9 MB;
  `m6/work/fc/br_m10.cnf.drat` 87.0 MB; `br_m11.cnf.drat` 80.7 MB;
  `m8/circ58.drat` 49.6 MB (the only large proof the judge replayed).
* Text/source ≤ 2 MiB: **445 files, 15.88 MB** (13.76 MB unique) — the whole readable core.

**Important provenance flags (do not inherit these as certificates):**

* `uniform_mge5_900.drat` (1.6 GB) belongs to a run whose log line 574 reads `c UNKNOWN` and
  whose tail is `raising signal 15 (SIGTERM)`
  (`m5/work/runs/uniform42/uniform_mge5_900.log`). A partial proof from a killed run with no
  verdict. This is UNKNOWN, not UNSAT.
* `m7/runs/*.drat` (1.9 GB) are **branch** proofs: `m7/runs/certify.jsonl` has 4 records,
  3 with `"verified": true` and `verify_tail: ["s VERIFIED", …]` (273,972,299 B and larger
  proofs), and **one with `"status": "UNKNOWN"`, tag `41ad024cd322`, 4,102,723 conflicts**.
  Verified branch UNSATs, not a closure of the uniform child.

## 6. Corrections and qualifications to carry forward

* **Retracted by their authors and confirmed by the judge (do not resurrect):**
  (a) m7 item 4, "the some_six child forces `m(x) ≥ 6` for all 42" — wrong; the children are
  complements, the split is valid;
  (b) m8's "18 extremal types × 2 < 42, therefore the uniform child is empty" — wrong; the false
  step was `|M_0| = 5 ⇒ (5,5,0)`. Correct census: **254,628 (T) / 254,088 (U)** types with
  `|M_0| = 5`, of which **18 per template** are extremal; two vertices of one extremal type
  admit exactly one colour, so `≤ 36` extremals, no contradiction. The retracted documents are
  deliberately kept as `m8/retracted_uniform_child_theorem_v1.md` and
  `m8/retracted_case_reduction_v1.md`.
* **Bundle phrasing that must not be inherited as a constraint**: "the uniform branch needs at
  least 26 distinct all-four-colour words" is not a constraint (254,610 (T) / 254,070 (U) such
  words exist). The verified content is the **count**: at most 16 of the 42 vertices can have a
  missing ordinary colour, equivalently at least 26 carry all four parts non-empty.
* **`345` is not a class count.** `345 = 332 + 13`: 13 classes are hit twice by the three
  project colours (`651 = 2·306 + 26 + 13` → `306 + 13 + 13 = 332`), so `345 = 332 + 13`,
  `45 = 37 + 8`, `27 = 24 + 3`, `300 = 295 + 5`. Recorded in `review/WALL_15141414_SWARM.md` §12
  as a correction to *this* swarm's clause "the 345 orientations do not double-count".
* **Not verified anywhere locally**: m1's "new classification-derived lemma" and "new marked
  filter that subsumes item 2's 2,194 cuts" (never submitted; no judge text); m1's and m2's
  claims beyond what §12 records; the 113,179-case cover reduction; the encoder's faithfulness
  (m3 replayed proofs against the encoder's own output only).

## 7. Archive disposition (recommendation)

* Retain the readable core (445 text files, 15.9 MB; dedupe-unique 13.8 MB) plus the
  per-file manifest in `evidence/file-manifest.json`.
* Manifest-and-remove the bulk (4,454.5 MB of `*.drat` / `*.cnf` / `*.gz` / large logs). The
  only large proof that is load-bearing for a coordinator-verified statement is
  `m8/circ58.drat` (49.6 MB, `s VERIFIED`); everything else is either a branch proof or the
  SIGTERM'd UNKNOWN partial. **Recommend keeping `circ58.cnf` + `circ58.drat` (≈52 MB) with
  hashes recorded, and re-generating rather than storing the rest** (`python3 circ_drat.py`
  reproduces both).
* Do not re-run: the 3,093-cut transfer as a clause family, the `m(x) ≤ 5` interface collapse,
  or the block-Cayley sweeps at 400/540 s; all four are measured UNKNOWN records, not open
  invitations.
