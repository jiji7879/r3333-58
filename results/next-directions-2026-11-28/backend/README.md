# Direction 3 — matched backend comparison: report

**Verdict-sized scope statement.** On a bounded matched panel I measured the
three SAT backends already present in this repository against each other, on
byte-identical CNFs at equal conflict caps, with every refutation replayed by
`drat-trim`. The result is **negative for every engine swap and every portfolio
addition** and **positive for two narrower things**: the native CaDiCaL 2.1.2
opt-in is a reproducible ~6.5 % CPU and ~42 % peak-RSS win on OPEN leaves at a
matched conflict cap, and a conflict cap is not a portable budget between
engines, so a second engine retried at the *same* conflict cap is the wrong
lever. No default, cap, encoder, ledger, `run` or `finalise` file was touched.
Nothing here is a Ramsey bound, a wall closure, a `ChainReady` claim, or a
statement about `R_4(3)`; the retained interval stays $51 \le R_4(3) \le 62$.

## What was compared

| engine | identity | pinned by |
|---|---|---|
| `py195` | CaDiCaL 1.9.5 through `python-sat 1.9.dev22` — the production incumbent | `.scratch/k58/.venv` |
| `cad212` | the repository's native CaDiCaL 2.1.2 | sha256 `a4a6dc61…7e48b` |
| `kis404` | the repository's native Kissat 4.0.4 | sha256 `b77de62f…4097f` |

Everything is run through my own harness (`panel.py`), one fresh process per
run, `wait4` CPU accounting, and `drat-trim` (sha256 `48891f3f…03bce`) for any
refutation. A refutation is recorded only when the proof was freshly written by
that run, `drat-trim` exits 0, prints `s VERIFIED`, **and** reports parsing
exactly the file's byte count (a valid prefix followed by extra bytes is
rejected, as in `check_trace`). A CNF that closes by unit propagation alone
would disqualify its own certificate; the BCP check says none of the ten CNFs
used here does, so no certificate below is vacuous.

Case A is the retained request: row `06861a3d…`, cube `[-1413, 1014]`, sha256
`8791f627…`. Case B is the already-closed `H8-word0` child, sha256 `e8cc9784…`.
Phase 2 and 3 extend to the complete `H1..H8-word0` family; Phase 4 re-seeds the
two closed ones. **80 processes (68 panel runs + 12 plumbing-smoke runs), 30
verified refutations, 183.3 s of measured solver CPU** (the member budget is
480 s).

Pre-registrations were written before each phase and are in this directory:
`PRE-REGISTRATION.md` (phases 1), `PHASE2-PRE-REGISTRATION.md`,
`PHASE3-PRE-REGISTRATION.md`, `PHASE4-PRE-REGISTRATION.md`. `analyze.py` computes
every rule outcome from the receipts; no number in this report is typed by hand
except the ones `analysis.json` also contains.

## Phase 1 — the retained cube and one closed case

Case A, retained parent+cube, matched 100,000-conflict cap, three `trace` runs
per engine (two seed-0 orders, one seed-1). All twelve runs are OPEN at the
cap in every engine: **no closure of the retained request is claimed or seen.**

| engine | conflicts | solver CPU s (gm) | process CPU s (gm) | vs incumbent | peak RSS MiB | props/conflict |
|---|---|---|---|---|---|---|
| `py195` | 100,001–100,002 | 3.565 | 3.630 | 1.000 | 87.7 | 282 |
| `cad212` | 100,000 | 3.409 | 3.410 | **0.939** | **50.9** | 297 |
| `kis404` | 100,001–100,002 | 4.293 | 4.294 | 1.183 | 53.0 | **574** |

Case B, `H8-word0`, matched 60,000-conflict cap, seed 0, two `trace` runs:

| engine | verdict | conflicts | solver CPU s | drat-trim CPU s | total certificate CPU s (gm) | proof bytes |
|---|---|---|---|---|---|---|
| `py195` | UNSAT verified | 32,316 | 1.371 / 1.459 | 0.857 / 0.877 | **2.281** | 8,645,007 |
| `cad212` | UNSAT verified | 49,226 | 1.720 / 1.740 | 0.991 / 1.003 | 2.727 | 9,529,642 |
| `kis404` | UNSAT verified | 17,319 | 1.300 / 1.300 | 1.369 / 1.352 | 2.660 | **5,453,359** |

Seed 1 at the same cap: `py195` **OPEN** at 60,002 conflicts, `cad212` **OPEN**
at 60,000, `kis404` UNSAT at 19,319. Two of the three engines therefore lose
this already-closed refutation by changing nothing but the seed.

Pre-registered outcomes, computed in `analysis.json`:

| rule | `cad212` | `kis404` |
|---|---|---|
| R1 certificate cheaper than incumbent on case B | **false** (2.727 vs 2.281 s) | **false** (2.660 vs 2.281 s) |
| R2 no case-A regression (CPU ≤ 1.10×) | true (0.939) | **false** (1.183) |
| R3 counters reproducible across the two seed-0 runs | true | true |
| **admitted** | **no** | **no** |

R3 is exact, not approximate: the repeated seed-0 runs reproduce conflicts *and*
decisions *and* propagations for all three engines, and the conflicting literals
are the same numbers the accepted KMT bank recorded for this cube
(`100001 / 529694 / 32489100` for the incumbent at seed 0) — my harness
reproduces an accepted baseline receipt independently.

* **P1 (trajectory identity): false at the panel cap, true only early.** At a
  2,000-conflict cap both CaDiCaLs produce *identical* conflicts, decisions and
  propagations on `H8-word0` (`2001 / 31444 / 541429`; receipts in
  `receipts/smoke/`). By 100,000 conflicts on case A they differ
  (538,733 vs 529,694 decisions). So an early-conflict comparison that shows two
  CaDiCaL versions searching "identically" does not survive to the caps this
  pipeline uses, and counters are not comparable across the versions.
* **P2 (cap portability): true, strongly.** Kissat spends **2.04×** the
  propagations per conflict on the same CNF (574 vs 282). A portfolio that gives
  every engine the same conflict cap is not a matched budget; it hands Kissat
  ~2× the work per capped call and still charges it the same cap.
* **P3 (proof-trail overhead): false at this scale.** Trace/plain process-CPU
  ratios are 1.046 (`py195`), 1.041 (`cad212`), 1.001 (`kis404`) on case A. Binary
  DRAT logging is free next to the search at 100k conflicts; the certificate
  cost is in the *checker*, not in the solve.

## Phase 2 — does a second engine earn a place in the portfolio?

All eight `H1..H8-word0` children, both engines, one matched 100,000-conflict cap,
seed 0:

Search CPU seconds in brackets.

| case | `py195` | `kis404` |
|---|---|---|
| H1 | OPEN 100,000 (4.65 s) | OPEN 100,001 (5.05 s) |
| H2 | OPEN 100,005 (4.68 s) | OPEN 100,000 (4.86 s) |
| H3 | OPEN 100,002 (3.28 s) | OPEN 100,000 (4.91 s) |
| H4 | OPEN 100,007 (3.14 s) | OPEN 100,003 (4.98 s) |
| H5 | OPEN 100,000 (4.47 s) | OPEN 100,001 (4.86 s) |
| H6 | OPEN 100,002 (3.20 s) | OPEN 100,000 (5.14 s) |
| H7 | **UNSAT** 19,433, cert 1.73 s, 6,788,182 B | **UNSAT** 26,853, cert 2.95 s, 6,097,087 B |
| H8 | **UNSAT** 32,316, cert 2.31 s, 8,645,007 B | **UNSAT** 17,319, cert 2.41 s, 5,453,359 B |

| rule | outcome |
|---|---|
| C1 kissat also closes everything the incumbent closes | true (H7, H8) |
| C2 kissat's certificate cost ≤ 1.10× on those cases | **false** (1.334×) |
| C3 kissat closes something the incumbent leaves OPEN at the cap | **false** (nothing) |
| **kissat admitted as a closure engine** | **no** |

The incumbent is cheaper in 6 of the 8 cases at the matched cap. Kissat's proofs
are the smallest (5.45 MB vs 8.65 MB on H8), which is a storage property, not a
speedup — it does not repay a 33 % certificate-CPU premium on these two cases.

## Phase 3 — replicating the one positive result

The Phase-1 `cad212` CPU/RSS advantage, tested on all six open cases from
Phase 2, with the incumbent side taken from the Phase-2 receipts and two
incumbent re-runs as drift controls:

| case | `cad212` CPU s | incumbent CPU s | ratio | `cad212` RSS | incumbent RSS |
|---|---|---|---|---|---|
| H1 | 4.406 | 4.716 | 0.934 | 46.9 | 89.2 |
| H2 | 4.450 | 4.748 | 0.937 | 51.7 | 89.9 |
| H3 | 2.905 | 3.354 | 0.866 | 52.1 | 88.9 |
| H4 | 3.401 | 3.208 | 1.060 | 52.1 | 89.9 |
| H5 | 4.117 | 4.543 | 0.906 | 52.2 | 88.2 |
| H6 | 2.993 | 3.272 | 0.915 | 52.2 | 88.9 |

* S1 (≤ 1.10× on ≥ 5 of 6): **true**, 6 of 6; geometric mean **0.935**.
* S2 (lower RSS on all 6): **true**, 46.9–52.2 MiB against 88.2–89.9 MiB — a
  factor of ~0.58, far outside measurement noise.
* S3 (drift controls reproduce counters): **true** — the incumbent re-runs on H3
  and H6 reproduce conflicts, decisions and propagations exactly
  (`100002 / 676934 / 18896645` and `100002 / 693893 / 22166416`). Their CPU
  moved by ±5 % between time windows, so the ~6.5 % CPU advantage is real in the
  mean but sits near the noise floor of a shared 4-core VM; **the memory
  advantage is the robust part**.

This replicates the positive Phase-1 result on six further leaves and is the
only engine advantage in this report I am willing to call replicated.

## Phase 4 — how much of a cap outcome is the seed?

The two closed cases at a 60,000-conflict cap, four seeds each (descriptive only;
it cannot change the Phase 1–3 verdicts):

| case | engine | conflicts-to-close by seed 0/1/2/3 | spread | seeds closing |
|---|---|---|---|---|
| H7 | `py195` | 19,433 / 23,783 / 23,829 / 22,667 | 1.23× | 4/4 |
| H7 | `kis404` | 26,853 / 27,837 / 29,604 / 28,869 | 1.10× | 4/4 |
| H8 | `py195` | 32,316 / **OPEN at 60,002** / 37,679 / 14,492 | ≥ 2.60× | 3/4 |
| H8 | `kis404` | 17,319 / 19,319 / 18,595 / 18,071 | 1.12× | 4/4 |

On `H8-word0` a seed change moves the incumbent's conflicts-to-close from 14,492
to beyond 60,000 — a spread (≥ 2.60×) larger than the between-engine gap
(1.54×), while Kissat's spread across the same four seeds is 1.12×. At seed 3 the
incumbent closes H8 *earlier* than Kissat (14,492 vs 18,071), so the Phase-1
"Kissat needs 1.87× fewer conflicts on H8" reading is seed-noise-dominated: it is
a fact about (engine, seed, cap), not about the engine. At seed 0 the H7/H8 seed-0
receipts also reproduce *exactly* in these later runs, so this is not run-to-run
noise but a genuine seed effect.

Pre-registered reading: seed choice is the cheaper lever (it exceeds the engine
gap on one of two cases, and the largest effect found), so a cap-OPEN on a
closure-critical leaf should be re-tried at a second seed before the conflict cap
is raised or another engine is paid for. Cost of the retry: ~1–3 s per leaf.

## What can be adopted, and what genuinely cannot

| item | status | evidence |
|---|---|---|
| Keep `py195` as the default engine | **keep** | cheapest total certificate cost on both closed cases; cheapest CPU in 7 of the 8 family cases |
| `cad212` native opt-in for OPEN leaves | **supported as an opt-in** (already exists) | 0.935× CPU (replicated 6/6), 0.53–0.59× peak RSS, i.e. ~42 % lower (replicated 6/6), counters reproducible |
| `cad212` as a *throughput or conflict-count* win | **not adoptable** | 49,226 conflicts against the incumbent's 32,316 on H8 (certificate cost 1.20×); the retained bank's H7 receipt shows the same direction (23,143 against 19,433) |
| `kis404` as a portfolio/closure engine | **not adoptable** | C2 and C3 both fail; 1.33× certificate cost; 2.04× propagations per conflict |
| `kis404` as an independent oracle | **keep** (its present role) | smallest proofs; stable across seeds; closes H8 at every seed |
| equal conflict cap for every engine | **not adoptable as a matched budget** | 2.04× difference in work per conflict |
| one-seed cap-OPEN as evidence of leaf hardness | **not adoptable** | H8 seed 1 OPEN at 60k vs 14,492 at seed 3, same engine, same bytes |
| raising the conflict cap as the first remedy for an OPEN leaf | **not supported** | the measured lever is re-seeding: ≥ 2.6× effect for ~1.5 s |
| native LRAT, clause import, preprocessing, MCF, static lex, KMT | **out of scope here** | not tested in this direction; see the earlier rejected list |

Full reproduction commands, byte hashes of every executable and every CNF, and
the fail-closed admission contract are in [ADOPTION.md](ADOPTION.md).

## Non-claims

* No engine was shown to make a hard leaf close that would not close otherwise:
  the six open family cases are OPEN at 100,000 conflicts in every engine, and
  the retained request is OPEN at 100,000 in every engine (and OPEN at 1,000,000
  with the incumbent in the retained bank).
* The two UNSAT verdicts below (H7, H8) are refutations of those exact CNFs in
  their own physical scope. They are not a wall closure, not a cover step, not
  `ChainReady`, and not a bound on `R_4(3)`.
* Contact with the accepted KMT receipts is a *reproduction of their counters*,
  not a re-adoption of that encoding.
* CPU figures come from a shared 4-core VM: CPU time is the currency, wall time
  is not reported as evidence, and ±5 % cross-window drift is stated rather than
  netted out. "Process CPU" is the whole child process (so it charges the python
  interpreter ~0.06–0.1 s); "search CPU" is the engine's own solve time. The two
  never mix inside one table.
