# Direction 5 (m2): checked reusable clauses on the retained request — measured boundary

**Verdict: nothing here is adoptable as a speedup.** The one checked, nontrivial,
narrow-clause family available for the retained row was instantiated on the exact
retained request bytes and measured at matched conflict caps and matched seeds in
both orders. Search CPU never improves reproducibly (0.993–1.473× base). 360 of the
960 clauses are already unit-propagation consequences of the request itself. A fresh
parent-level DRAT certificate for the remaining 600 was not reachable at a 120 s
cap, and the corrected child-CPU reruns confirm the solver is CPU-bound there
(bounded negative, not a refutation). No physical cut, no root/family hypothesis, no ledger, encoder, `run`,
`finalise`, solver default or committed tree file was touched. OPEN is not a verdict.

## 1. Destination pinned byte-exactly

`parent-cube.cnf` is regenerated from the frozen first-tier parent
`.scratch/arm3-hard-leaf/parent.cnf` (sha256 `90d06e32…f56ae`) plus the retained
cube `[-1413, 1014]` appended in cube order, under the canonical header
(`p cnf 19533 184337`). Its sha256 is
**`8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8`**, i.e. the
retained ordinary parent+cube named in the task. 19,533 vars; clause widths
438×1, 36,992×2, 134,649×3, 12,241×4, 15×113. Row
`06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`.

## 2. Source family, with role, guard and destination kept explicit

Source: the checked K15 square/matching rule set shipped for **exactly this row**
(wall index 25557) as
`.scratch/k58-square-spoke-wall-test-v1/src/next/batch-25557.json.gz`
(sha256 `48294797…b8c3c`; `id`, `parent` and `tier:first` fields match the row and
parent above; local theorem proof sha256 `4ca7a5d3…085d7`). That audit
(`research/k58-square-spoke-wall-test/audit.md`) proves the local K15 query
(315 vars / 1,825 clauses) UNSAT with a warning-free `s VERIFIED`, and separately
reconciles the guard scope, the vertex/colour bindings and the 9,287-set geometry
for the fourteen ordinary parents including this one.

- role: a derived, redundant-but-valid clause; not a learned clause of the
  destination search and not a physical cut.
- guard: each clause is `¬g ∨ ⋁_{v∈S} ¬E(32,v,1)` — one negative **free** sender
  guard literal (31 distinct guard vars, all > 6612, i.e. encoder auxiliaries) and
  four negative physical spokes (all ≤ 6612).
- destination: the request bytes above, so no re-encoding is implied.

Checks I ran myself (`build.py`, `build.json`): 960 rules, 960 distinct clauses,
all width 5, 31 distinct guards, 492 distinct physical variables; the recorded
`[x, c, palette, sites]` metadata decodes the four spoke literals exactly for
960/960 rules. Appending them gives `aug960` sha256 `603f8de8…936ba2`; appending
only the 600 non-UP-trivial ones gives `aug600` sha256 `8c15935b…b986`.

## 3. Does the family activate at the destination root?

Own propagator (`up.py`, `up.json`; deterministic, no solver):

- Root unit-propagation closure of the request assigns **1,865 of 19,533**
  variables, no conflict. No appended clause propagates at root: every guard is
  unassigned, so all 960 are inert until search assigns a guard.
- Under its own negation, **360/960** clauses are unit-propagation-refuted by the
  request alone (RUP consequences of the destination). These are report-only under
  the task rule: their refutation uses nothing but the request.
- The other **600** are not UP-derivable; their derivation needs the four-colour
  case analysis. 600 is exactly the "600 surviving falsifying cubes" count that
  the independent upstream audit records for this row — a count-level
  cross-check between two independently written propagators, not a re-proof.

## 4. Matched-cap measurement (PySAT CaDiCaL 1.9.5, pinned python-sat 1.9.dev22)

Convention copied from `results/next-directions-2026-11-28/kmt/kmt_bench.py`: one
fresh subprocess per call, fresh solver per call, `seed` configured, `conf_budget`,
no proof logging, search CPU reported separately from wall. Arms run in both
orders per seed. All runs OPEN at their cap, as expected; no UNSAT and no SAT is
claimed from a cap.

cap = 100,000 (`bench/`, 4 runs, 13.73 s search CPU total):

| seed | arm | status | search CPU s | propagations | decisions |
|---|---|---:|---:|---:|---:|
| 0 | base | OPEN | 3.792 | 32,489,100 | 529,694 |
| 0 | aug960 | OPEN | 3.772 | 34,966,844 | 544,937 |
| 1 | aug960 | OPEN | 3.072 | 22,561,769 | 794,031 |
| 1 | base | OPEN | 3.093 | 21,181,699 | 777,586 |

CPU ratio aug/base: 0.995 (s0), 0.993 (s1). RSS ratio 1.005 / 0.999.

cap = 300,000 (`bench2/`, 6 runs, 78.96 s search CPU total; three arms):

| seed | arm | status | search CPU s | propagations | decisions |
|---|---|---:|---:|---:|---:|
| 0 | base | OPEN | 14.213 | 107,082,692 | 1,010,038 |
| 0 | aug960 | OPEN | 14.456 | 114,258,265 | 1,012,024 |
| 0 | aug600 | OPEN | 14.544 | 122,520,727 | 876,052 |
| 1 | aug600 | OPEN | 14.665 | 120,493,784 | 883,669 |
| 1 | aug960 | OPEN | 11.124 | 87,118,482 | 1,417,031 |
| 1 | base | OPEN | 9.959 | 69,241,168 | 1,683,113 |

CPU ratio over base: aug960 1.017 (s0) / 1.117 (s1); aug600 1.023 (s0) / 1.473 (s1).

Reading: not a gain at either cap. `aug600` lowers decisions reproducibly
(−13 % s0, −47 % s1) but raises propagations (+14 %, +74 %) and CPU does not
follow, so a decision-count drop is **not** a speedup signal on this formula.
Mechanism: the clauses are five literals wide with a free guard, are never
touched by the root closure, and 360 of them are already propagation-available.

## 5. Fresh destination-level certificate: bounded negative

`verify_clause.py` / `verify-clauses.json`. Two of the 600 non-trivial clauses
(first and middle) were put at the destination the hard way: query = exact request
+ one unit per clause literal (its negation), 19,533 vars / 184,342 clauses, run
through the repository's native CaDiCaL 2.1.2 under a wall cap and replayed with
the repository's `drat-trim` without `-w`.

**Measurement correction (this replaces an earlier receipt).** My first version
wrapped `subprocess.run` in `time.process_time()` and recorded that as
`solver_cpu_seconds`; it reported 0.000331 s and 0.000395 s for two 120 s-capped
runs, which is this driver process, not CaDiCaL. That receipt is retained as
`verify-clauses-with-invalid-cpu-field.json`, its CPU field is **void**, and the
real CPU/wall of those two historic runs **cannot be recovered** from it. What
that version does still establish is only its exit evidence: solver exit 0 and no
`s VERIFIED` line. The corrected path is:

- child CPU = `resource.getrusage(RUSAGE_CHILDREN)` delta, wall =
  `time.monotonic()`, both recorded per run;
- validated on a tiny fresh control, `p cnf 2 4` over the 2-clause UNSAT core:
  solver exit **20**, child CPU 0.0011 s, wall 0.0017 s, `drat-trim` exit 0 with
  exactly one `s VERIFIED`, so a zero/nonsense reading is visible rather than
  silent.

Corrected reruns, 20 s wall cap, same two clauses: solver exit **0 (unknown)**,
child CPU **19.977 s** and **19.991 s**, wall **20.005 s** each, zero
`s VERIFIED`, status `OPEN_unknown_at_cap`. So those runs are CPU-bound on real
solver work and were stopped by the cap, not by a verdict.

Therefore a bounded parent-level DRAT certificate for this family is **not**
available at this budget; the family is sound only through the local K15 gadget
theorem plus the upstream binding audit. That is the premise-strength boundary of
the reuse, and it is reported as such: I do **not** claim the 960 clauses were
independently re-proved at the destination, and exit 0 with zero verified lines is
OPEN, not a refutation, at either the historic 120 s cap or the corrected 20 s cap.

## 6. Adoption boundaries a coordinator can use

1. Do not adopt this family for this request on this evidence. The measured effect
   is neutral-to-negative search CPU, plus runs that cannot produce a
   destination-level certificate within 20 s (measured 19.98 s/19.99 s child CPU,
   exit 0) and did not within the earlier 120 s caps.
2. Keep the distinction the task asks for: a candidate whose negated cube is
   unit-propagation-refuted by the destination is *report-only* (360/960 here).
   Count and name those separately before any benchmark, or the "gain" is book-keeping.
3. Any future clause-reuse candidate should be admitted only if it (a) is not
   subsumed by a destination clause, (b) is not UP-trivial at the destination,
   (c) has an explicitly named certificate form (local gadget proof + binding
   check, or a bounded destination-level DRAT), and (d) shows non-regressing
   search CPU at two seeds in both orders at two caps, with propagations reported.
   `up.py` plus `bench.py`/`bench2.py` are a reusable, hash-pinned gate for (a)–(d)
   and are the only artifacts I propose for integration; they are helpers, not
   production defaults.
4. A reproducible decision-count reduction with unchanged conflicts is not
   evidence of speedup; on this formula it came with more propagation work.

## 7. Files, budget, and what was not done

Artifacts in this directory: `build.py`/`build.json` (pinned reconstruction,
regenerates every CNF used here byte-identically), `up.py`/`up.json` (propagator
and per-clause classification), `bench.py`/`bench/`, `bench2.py`/`bench2/`
(matched-cap receipts and per-run JSON), `verify_clause.py`/`verify-clauses.json`
(corrected child-CPU accounting, validated control, two 20 s-capped reruns),
`verify-clauses-with-invalid-cpu-field.json` (superseded record, CPU field void),
`clauses.txt` (the 960 clauses).

Cost accounting, with the units named: the two PySAT panels are measured in
process, 13.73 s and 78.96 s of search CPU (92.69 s). The corrected native reruns
measure 19.977 s + 19.991 s of child CPU, plus a negligible control and the
`drat-trim` calls on their (small, since the cap stops them before a verdict)
proof writes. The two superseded 120 s-capped runs cost unknown CPU — bounded in
wall at about 120 s each, with no accurate CPU figure recoverable — so I state no
total that includes them. No production file, ledger, encoder, default,
`run`/`finalise` path or other member's directory was modified; nothing was
committed. No new packages, no automorphism assumptions, no full sweep, no new
course of Ramsey bound; `51 ≤ R_4(3) ≤ 62` is untouched.
