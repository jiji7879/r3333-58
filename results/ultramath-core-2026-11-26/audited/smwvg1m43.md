# Archival report — old swarm `smwvg1m43` (Group D, audit by m4 of smwx73ni9)

Audit only; nothing here was recomputed with a solver. Sources: the 8 transcripts (extracted to
`evidence/`), the judge text (`evidence/verdicts_smwvg1m43.txt`), member reports, and the
committed records in `results/gap4-2026-11-25/` and `WALL_HANDOFF.md`.

## 0. Scope the swarm was given

Task text (`evidence/task1_smwvg1m43.txt`, first user message of each member): *"In the K58
campaign for R(3,3,3,3) <= 58, the frozen cover has 13,154 open 'gap four' rows: profile
**(15,15,15,12)**, a root `r` whose colour-0 arm `A0` has 15 vertices, and a requirement that at
least **11** vertices `a` of `A0` be **CRITICAL**, i.e. `d_0(a) >= 15`. They split into **149 rows
with root kinds `UUU-` and 13,005 with root kinds `TTT-`** (plus 9 charge-15 rows in profile
`(15,14,14,14)` that are **not** gap four)."*
Question put to the swarm: **does the recipe (families A, B, C) close the `TTT-` rows, and if not
what implied constraint does?** The three T rows differ from U only in the arm templates
(`T` instead of `U`) and the marked set (size 15 or 16, kind `T`, different placement). Family B
itself (for critical `a`: `|N_0(a) ∩ A_c| ≥ 4`, `c = 1,2,3`) never mentions a template, a marked
set or a placement.
Machinery named in the task: `.scratch/k58par` (bundle, `campaign/gap_four.py --row ID`),
`tools/gap4/strengthen.py`, `results/gap4-2026-11-25/README.md`, solvers under
`.ultramath/smwmq7hji/m3/bin/`, ledger `.scratch/k58/case-ledger.jsonl.gz`.

## 1. Acceptance ledger

29 `ultramath_submit` calls; **8 taken** by the platform (7 members; m7 never submitted). Only
**one judge verdict** is recoverable locally (m8, direction d5, transcript line 177 — copy in
`evidence/verdicts_smwvg1m43.txt`); the other six submissions carry **no judge text in the local
transcripts**, so their acceptance rests on the coordinator-written record, not on the members'
own titles. That record is:

* `WALL_HANDOFF.md` (line ~285): *"Another substantial run (`smwvg1m43`) is ended with **7
  accepted reports** including the bare-pilot measurements and Lean family chain."*
* `results/gap4-2026-11-25/README.md` (19,178 B, committed) attributes the verified content by
  member: m1 (bare vs augmented timings), m2 (pilot-equivalence framing), m3 (pilot rebuild
  audit), m4 (Lean chain), m5 (units-alone UNSAT), m6 (149-row distinctness), m8 (wall control).

Accepted / reproduced by the coordinator (each line is a citation, not a member claim):

1. **Bare pilot is what closes the rows.** Plain kissat refutes the `UUU` pilot in **41 s**
   (171,455 clauses, sha `85aea7fc…`), the row's own certified CNF in **44 s** (196,994 cl),
   `pilot + B` in ~50 s, `pilot + A+B+C` in 2–3 min. m1's seven-run measurement (bare wins by up
   to 6.6×, on 48 % of the clauses) and a controlled twin row `e792ec35` (closes bare in 20 s)
   are recorded there.
2. **Theorem E / framing correction (m2, re-checked in the record):** the `UUU` pilot
   `0684ba38` and a `TTT` pilot `0013b1f1` have **170,935 non-unit clauses equal as sorted lists**
   and 520 unit clauses differing in 151 entries; every model of a pilot is a triangle-free
   4-colouring of `K58`, so A, B, C hold in every model and *"the recipe closes a row exactly when
   that row's pilot is unsatisfiable"* — the families are a **proof aid, not the semantic reason**.
3. **`host(58) + units` alone is UNSAT (m5, "I reproduced" by the coordinator).** 135,498 clauses,
   sha `4b4be140fae38664019ac35a802b48221334ac6913de0a7f3355504aab058179`, DRAT
   47,666,743 B, `drat-trim` `s VERIFIED` (5,267 clauses in core, 20,048,679 steps); containment
   checked clause by clause against the `--dense` row CNF (196,994 cl), 0 missing. Charges 9 and 3
   of the same profile close the same way.
4. **Pilot rebuild audit (m3):** `audit_pilot.py` rebuilds the pilot as
   `base(58) + units + extra` with `171455 = 134995 + 503 + 35957`, no difference at any index.
5. **Lean chain (m4)**: `five_bound`, `card_nb_le_sixteen`, `familyB`, `familyC`,
   `dual_five_bound`, `exact_pattern`, compiling in **2.8 s**, no `sorry`, axioms only
   `[propext, Classical.choice, Quot.sound]`, with `R(3,3) = 6` and `R(3,3,3) = 17` as explicit
   hypotheses. `exact_pattern` also shows no single-vertex sharpening of B exists (A+B+flag pin
   the pattern to `(5,5,5)` or a permutation of `(4,5,5)`). Retained at
   `lean/K58/GapFamilies.lean` and `m4/K58Chain.lean` (11,270 B).
6. **Row distinctness (m6):** all 149 `UUU-` rows have pairwise distinct frozen unit sets up to
   vertex and colour permutation — 149 distinct unit sha256, 149 isomorphism classes (networkx
   VF2 agreeing); all 13,154 gap-four rows and all 83,440 rows of the profile are singletons. So a
   certified refutation closes exactly its own row; only the *recipe* transports.
7. **The one judge verdict (m8, d5)** verified: Theorem E matches, A′ (`|N_c(y) ∩ A_p| ≤ 5`) is
   correct and is *not new* (it is m4's kernel-checked `dual_five_bound`, though m8's two
   certificates are new), and the hazard report on `tools/gap4/strengthen.py` is correct.
8. **Wall measurement (m8, recorded):** `(15,15,14,13)` charge-1 row UNKNOWN at 20 min with the
   families, UNKNOWN bare, **units alone UNKNOWN at 15 min**; positive control charge-10 row of
   `(16,15,15,11)` UNSAT in 2.26 s.

Rejections: the local record shows **no direction of this swarm marked rejected/dead** except that
m8's d5 was "rejected as a solution" once and sent back — the reason given was that the submission
re-derived an accepted result instead of doing the registered experiment, *"The claims are right
and I checked them"*. Everything else was accepted **as a report**, not as a solution: no row
closure and no bound was claimed by this swarm; the campaign's closures came from the concurrent
batch.

## 2. Exact scope and OPEN objects

* **What is established**: the gap-four rows are **UNSAT**, and they are UNSAT **because the
  pilot/units are** — the implied families A, B, C are entailed and therefore never needed. The
  whole `(15,15,15,12)` profile (20,166 open rows) closes by plain solving at a median ~45 s
  (sweep mean over 18 certified rows: 46 s). Every `TTT-` row tested here closed; `TTT` templates and the marked set do not obstruct the recipe. That is
  a measured sample (three `TTT-` rows, by m1, m3, m5 and m6 with independent rebuilds), not a
  proof about all 13,005 `TTT-` rows.
* **Not established, and must not be read into the record**: `R_4(3) ≤ 58` is **not proved**;
  the frozen cover's 113,179 rows are not closed; a row closure is a sub-case. The record says it
  in so many words ("The bound does not move").
* **OPEN**: profile `(15,15,14,13)` (7,732 rows) and the six small wall profiles —
  units alone UNKNOWN at 900 s, row CNF bare UNKNOWN at 1200 s, row CNF + A + B UNKNOWN at
  1200 s. m8 measured that A, B "do not bite outside the gap-four block", so the lever there is
  the row's *charge/total-critical mass*, not the lemma. Also open: the transfer of the recipe to
  the **9 charge-15 rows of `(15,14,14,14)`** (`campaign/gap_four.py` asserts profile
  `(15,15,15,12)`, so those rows must be built with `tools/pb/balance.py --dense`).
* **Solver honesty**: every UNKNOWN in this record is a capped timeout. None of them is evidence
  of satisfiability or of unsatisfiability.

## 3. Retained in Git

* **`results/gap4-2026-11-25/README.md`** — the integrated record (corrections, hashes, the
  units-alone result, the tiers table, the Lean chain, cost model), plus
  `results/gap4-2026-11-25/open-row-ids-15151512.txt` (1,310,790 B), `sweep/*.tsv`
  (`cert_A.tsv`, `bare_C..F.tsv`; the whole directory is 1.4 MB).
* `tools/gap4/{strengthen.py, add_families.py, run_units_bulk.sh}`,
  `tools/pb/balance.py` (with its documented `balance=False` hazard),
  `lean/K58/GapFamilies.lean` (the family lemmas), `review/ERRATA.md` (the
  `dense.marked_threshold` empty-clause hazard).
* `WALL_HANDOFF.md` (the "7 accepted reports" line). `.gitignore` keeps `.ultramath/`, `*.cnf`,
  `*.drat` out of Git, so swarm bytes are not tracked.
* The raw TTT/units proof bytes were **deleted after hashing by policy** inside the record itself
  ("Proofs deleted after hashing", TTT table); only hashes and byte counts survive there.

## 4. Reproduction

```sh
python3 tools/pb/balance.py ROW_ID row.cnf --dense            # ROW_ID from the ledger
kissat -q --time=600 row.cnf row.drat && drat-trim row.cnf row.drat -c   # expect ~45 s in (15,15,15,12)
python3 tools/gap4/add_families.py row.cnf row2.cnf --profile 15,15,14,13 --arm 0
# older, profile-hardcoded form (do NOT use on (15,14,14,14) rows):
python3 tools/gap4/strengthen.py pilot.cnf strong.cnf          # sha e0ecfa7f…, 355,565 clauses
```

## 5. Raw-evidence inventory (measured now)

* `smwvg1m43`: **563 files, 3,289,571,965 B (3.29 GB)**; transcripts 6.9 MB.
  Per member: m3 954.8 MB, m1 757.1 MB, m6 750.0 MB, m5 407.8 MB, m7 223.7 MB, m8 177.5 MB,
  m4 11.0 MB, m2 0.8 MB.
* Largest: `m6/proof/TTT969_bare.drat` **131,594,341 B** (byte-identical to
  `m3/work/ttt/0013b1f1…drat` — a duplicate pair, 131.6 MB redundant); `T15b_B.drat` 127.9 MB;
  `T16_bare.drat` 121.2 MB; `T15b_bare.drat` 113.5 MB; `TTT969_B.drat` 113.3 MB;
  `T16_B.drat` 110.6 MB; `m1/work/bare_8b27…drat` 97.6 MB; `m3/work/ttt/e9a7…drat` 97.4 MB;
  `m1/work/strong_ttt.drat` 95.5 MB.
* Text/source ≤ 2 MiB: **310 files, 10.67 MB** (10.47 MB unique). Proofs and CNFs are
  3,278.1 MB (99.6 % of the swarm).

## 6. Corrections and qualifications (carry forward)

* **The "one elementary constraint closes the row" framing is wrong twice** and is retracted in
  the record itself: the row closes **without** the constraint, and with it the proof is slower.
  The earlier UNKNOWNs on these rows came from solver caps of 30–70 s, not from difficulty.
* **A, B, C are entailed by the pilot** (Theorem E). An entailed family cannot change
  satisfiability; it can only change how hard a witness is to find. Never report a family as the
  reason a row is UNSAT.
* **Two tool hazards, both accepted from the swarm**: `tools/gap4/strengthen.py` hard-codes the
  `(15,15,15,12)` partition and must never be pointed at a `(15,14,14,14)` row (use
  `add_families.py --profile --arm`); `tools/pb/balance.py`'s API `build()` defaults
  `balance=True`, so direct API use must pass `balance=False` or perfect balance is smuggled into
  a wall row and yields an invalid closure.
* **A third hazard (not this swarm's)**: `dense.marked_threshold` returns a single empty clause
  when the charge exceeds the guards — that would manufacture a closure in milliseconds
  (`review/ERRATA.md`).
* m8's d5 submission was **not** the registered experiment and was sent back once for that
  reason even though its claims were right; do not cite that submission as the wall measurement.
* Scope quote to keep exact: "13,154 open gap-four rows: profile (15,15,15,12) … 149 `UUU-` and
  13,005 `TTT-`", plus 9 charge-15 `(15,14,14,14)` rows that are **not** gap four.

## 7. Archive disposition (recommendation)

* Keep `results/gap4-2026-11-25/` (1.4 MB) and the readable core (310 files, 10.7 MB); they
  contain every statement this swarm established.
* Hash-manifest and remove the 3.28 GB of DRAT/CNF bytes: the closures are row-local, the record
  already deleted its TTT proofs after hashing, and any row can be re-closed bare in ~45 s
  (`tools/pb/balance.py --dense` + kissat). The duplicate `TTT969_bare.drat` pair (131.6 MB) is
  pure redundancy.
* **Keep nothing solver-wise for the wall rows**: `(15,15,14,13)` and the six small profiles are
  measured UNKNOWN records — do not re-run them as a "fix", and do not read their timeouts as
  evidence either way.
