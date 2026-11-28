# Admission policy for K58 solver speedups — `k58-admission-1`

**Status: proposal, opt-in only. No production file, default, ledger, encoder,
`run` or `finalise` is touched by anything here.**

A speedup claim enters this policy as one *normalised evidence record* and leaves
it with exactly one decision: `OPT_IN_EVIDENCE_BACKED`, `OPT_IN_SINGLE_CASE`,
`REJECT` or `INCOMPLETE`. Nothing else is adoptable, and no decision ever
upgrades a solver status. `gate.py` implements the decision function,
`adapters.py` builds records from the artifacts already in the bank, and
`run_audit.py` reproduces the audit of `results/next-directions-2026-11-28/`.

What the gate is **not**: it does not check proofs, re-run solvers, hash CNF
files on disk, or judge whether a mathematical premise is true. It checks that a
record *carries* the evidence the doctrine requires, and that the arithmetic of
that evidence supports the claimed direction. Statements attested inside a
receipt are taken as attested; the gate records that it did so.

---

## 1. Decisions and exit codes

| decision | exit | meaning |
|---|---|---|
| `OPT_IN_EVIDENCE_BACKED` | 0 | eligible for an explicit opt-in override, reproducible on ≥2 independent pinned cases |
| `OPT_IN_SINGLE_CASE` | 0 | eligible for an opt-in override **labelled single-case / limited**; not general |
| `REJECT` | 2 | the record contains decisive negative or invalidating evidence; do not retry the same design |
| `INCOMPLETE` | 3 | evidence missing, unpinned or non-comparable; fail closed, treat as reject until repaired |

`default_eligible` is always `false`. The task forbids changing solver defaults,
so the only non-reject outcomes are opt-in overrides; the difference between the
two is whether the effect has been shown to generalise beyond one case.

Two modes:

* `admission` — prospective, used before an override is merged. Everything is
  required, including pre-registration.
* `audit` — retrospective, used on already-published receipts. Only
  `R3_prereg` (pre-registration, arm list, run count) is waived, because it
  cannot be repaired after the fact; every other rule still blocks. A waived
  rule is recorded with `"waived": true`.

## 2. Vocabulary

* **Claim classes**: `certificate` (same CNF, different proof/check pipeline),
  `search` (clause set, restart order, heuristics), `options` (solver option
  values), `engine` (solver binary/version), `encoding` (formula encoding or
  added derived clauses), `preprocessing` (one-shot CNF transform), `policy`
  (this document — not measurable, always `INCOMPLETE`).
* **Closed statuses** (a refutation): `VERIFIED_UNSAT`, `CHECKED_UNSAT`,
  `UNSAT`. Everything else — `OPEN`, `UNKNOWN`, `TIMEOUT`, `PROOF_PENDING`,
  `COVER_READY`, `MODEL_READY`, `SAT`, `VERIFIED_SAT`, `CHECK_FAILED` — is not a
  refutation. `COVER_READY` is not `VERIFIED_UNSAT`; a model is not a refutation.
* **Trust levels**: `cross_checked` (default) charges and requires two
  independent checker binaries; `single_checker` charges one. The bank has no
  formally verified checker, so the default is `cross_checked`; a claim may be
  evaluated at `single_checker` only if the receipt declares
  `certificate.cost_basis` accordingly, and the verdict says so.

## 3. The evidence record (schema 1)

```
schema            1
claim             {id, class, statement, scope, closure_claimed}
prereg            {registered_before_run, declared_arms, primary_metric, margin,
                   max_runs, cases, caps, seeds, orders, declared_exclusions}
pins.inputs       {<case>: {baseline: {sha256, bytes}, treatment: {sha256, bytes}}}
                  (a single-case record may instead use {baseline: PIN, treatment: PIN})
pins.solver       {id, version, sha256}
pins.checkers     [{id, sha256, role?}]
transform         {kind, declared_delta, binding, derivation}
certificate       {status, checker_sha256, checker_exit, verified_line, relax_used,
                   cost_basis, cross_check}
runs              [{case, arm, seed, order, cap, status, metrics, counters?,
                    metric_valid?, solver_sha256?}]
controls          [{id, role, semantics_rejected, apparent_ratio?}]
```

`metrics` carries `search_cpu_s`, `check_cpu_s`, `prep_cpu_s`, and optionally
`proof_bytes`, `retained_bytes`, `maxrss_kb`. The composite CPU cost of a run is
`search + check + prep`; **nothing is excluded from it**: preprocessing, proof
checking and any mandatory second check are all charged to the arm that needs
them. `counters` holds the solver statistics (`conflicts`, `decisions`, …).

`primary_metric` must be a cost (`composite_cpu_s`, `proof_bytes`,
`retained_bytes`, `maxrss_kb`). `conflicts` may be recorded but cannot license
adoption: the repository's own native-policy note observes that search-only made
1.65× the conflicts in the same wall-time budget, so conflicts are not a
policy-invariant unit of work.

## 4. Rules

| rule | blocks | observed instance in this repository |
|---|---|---|
| `R1_schema` | unparseable / unevaluable record | — |
| `R2_pins` | missing input pin, solver binary pin, checker pin; exit ≠ 20; no literal `s VERIFIED`; relaxed check; cross-check is the same binary as the primary; cost basis ≠ trust; an `engine` claim without a per-run binary hash on both arms | `lrat` receipt: lrat-trim exits 20 **and** prints `s VERIFIED`; `missing_empty_clause` control exits 0 yet is rejected only via a warning line — exit code alone would have accepted it |
| `R3_prereg` | no pre-registration, undeclared arms, more runs than declared, measured cases/caps/seeds/orders outside the declared sets | every published receipt: pre-registration is unrecorded (waived in `audit`) |
| `R4_comparability` | inputs unpinned; a transform claim whose two inputs are byte-identical; a "no change" claim whose inputs differ; unpaired cells; different cap sets; solver changed while not claiming `engine`; an `engine` arm mixing two binaries | `sms` A/B: no input hash at all |
| `R5_status` | closure claimed while a run is OPEN/UNKNOWN/FAILED; closed run without a certificate block | — (generic cap-as-UNSAT guard) |
| `R6_control` | designated unsound control accepted by the semantics check, or an unsound control showing an apparent gain ≥ `1 − margin/2` | `sms`: the deliberately corrupted clauses give a 22.9 % apparent gain against the treatment's 20.5 % |
| `R7_semantics` | `encoding`/`preprocessing` without a pinned derivation marked `pass`; relaxed derivation; `engine`/`options` override not hash-bound into the cached leaf budget | `sms`: physical model-set invariance unproved; `native_leaf.py` shows what `binding=budget_hash` looks like (`native_sha256`, `native_policy`) |
| `R8_cost` | primary-metric geomean not ≤ `1 − margin`; any single cell > 1.0; per-seed spread > margin; fewer pairs than the design requires (≥4 for non-certificate, ≥2 for certificate) | `lrat` at `cross_checked`: geomean 1.1803 with H8 at 1.0246; `kmt`: 1.2504 / 1.2339 |
| `R9_quality` | no A/B and B/A replication for a search claim; certificate claim whose two arms do not record identical search counters; baseline order-replicate spread > margin/2; for `options`/`engine`/`search`, identical arm counters in every cell (inert knob); seeds that do not diverge in the baseline arm at the evaluation cap | `kmt`: order confounded with seed (ABBA over two seeds only); `sms`: 1.0 % order spread — resolvable; board `d4/f1`: the PySAT binding accepts unknown option names silently, and seed 0/1 are identical at a 2 000-conflict probe yet diverge sharply at 100 000 |
| `R10_exclusions` | a metric cell marked invalid but not declared in `prereg.declared_exclusions` | `lrat`: N14 and R11 retained-DRAT bytes not reproduced (`fresh_drat_matches_retained=false`), so their byte cells are invalid |
| `R11_generality` | (not a blocker) fewer than 2 independent cases caps the decision at `OPT_IN_SINGLE_CASE` | `lrat` byte claim survives on H7/H8 only |

Decision order: any `fail` → `REJECT`; else any `incomplete` → `INCOMPLETE`;
else ≥2 cases → `OPT_IN_EVIDENCE_BACKED`, otherwise `OPT_IN_SINGLE_CASE`
(also when a declared exclusion limits the usable cells).

## 5. Why these thresholds

**Margin 10 %.** The bank's own replicates set the floor. In the KMT receipt the
paired CPU ratios of the *same* encoding against the stock encoding were
1.1365 and 1.3758 at the 100k cap (spread 0.239) and 1.0444 and 1.4579 at 1M
(spread 0.414); the SMS receipt, which repeats each arm in both orders at the
same seed, spreads only 1.0 %. Conflict counts are exactly reproducible
(100001/100000/100001/100002 in the KMT 100k arm), CPU is not. So a gain smaller
than the seed-to-seed spread cannot be resolved by two seeds at all, and a
"gain" that appears in the mean while one cell regresses is not a gain. The gate
therefore demands *every* cell ≤ 1.0 and a per-seed sign agreement, not a mean.

**Cross-check charged by default.** `lrat` illustrates the cost of trust: on the
four already-closed CNFs the certificate route costs 0.27–0.70× the DRAT route
when only lrat-trim is charged, and 0.98–1.53× (geomean 1.1803) when the second
independent checker the experiment used is charged. Neither checker is formally
verified, so the conservative reading is the charged one; the cheaper reading is
admissible only as a declared `single_checker` claim.

**Inert knobs and inert seeds.** Two validity traps are cheap to fall into and
cannot be repaired by more CPU (board finding `d4/f1`, not independently re-run
here because the retained parent+cube CNF is not on disk):

* the PySAT CaDiCaL 1.9.5 binding accepts unknown option names silently — a
  mistyped knob returns bit-identical counters. So an `options`/`engine`/`search`
  arm whose counters never move is a no-op, whatever its CPU did; `R9` refuses it
  instead of adopting the CPU difference.
* seeds 0/1 were identical at a 2 000-conflict probe and sharply different at
  100 000 conflicts. A short-cap A/B therefore validates nothing about a knob,
  and a matched-seed panel must show seed divergence **at the evaluation cap**
  before its seed dimension means anything; `R9` refuses a panel whose baseline
  arm has identical counters across seeds.

## 6. Bounded design, and the stopping rule

A candidate gets **one** bounded design, registered before the first call:

* at most **2 caps**, **2 seeds**, **2 orders** (A/B and B/A), **2 arms** →
  at most **16 solver calls** per candidate;
* every call has a positive finite conflict cap *and* a wall cap; CPU is the
  measured quantity, conflicts are reported;
* the case list is fixed in advance and consists of already-closed or
  hash-pinned cases — no arm is selected after looking at an arbitrary open
  population;
* 8-minute member budget: at the retained parent+cube a 100k-conflict call costs
  ≈3.8 s CPU (KMT receipt), so 16 calls ≈ 60 s + proof checks ≈ 4 s. At the 1M
  cap a call costs ≈60 s, so 8 calls already exhaust the budget: **1M-cap runs
  are capability measurements, not admission measurements**.

Stop as soon as one of these holds, and record which:

1. **Adopt-shaped**: every paired cell ≤ 1.0 with geomean ≤ `1 − margin`, sign
   agrees across both seeds and both orders, and the effect reproduces on a
   second pinned case → `OPT_IN_EVIDENCE_BACKED`; on one case →
   `OPT_IN_SINGLE_CASE`.
2. **Negative**: geomean > `1 − margin`, or any cell regresses, or the per-seed
   spread exceeds the margin, or an unsound control mimics the gain → `REJECT`
   and *do not re-fit the design to a control*.
3. **Unresolvable**: budget exhausted while the spread still exceeds the margin →
   `INCOMPLETE`; report the bound reached, do not convert it into a trend.

## 7. Defaults vs overrides

| item | default | may it be an opt-in override? |
|---|---|---|
| engine | PySAT CaDiCaL 1.9.5 | only with `engine` class evidence and a binary pin |
| native policy | `default` when `--engine native` | yes, `options` class, hash-bound into the budget |
| proof format | DRAT + drat-trim | yes, `certificate` class, explicit checker path |
| preprocessing / encoding additions | off | yes, only with a pinned derivation (`R7`) |
| statuses, ledger, frozen coverage, accepted interval | — | **never** |
| conflict cap / wall cap as a result | — | **never** (`OPEN` stays `OPEN`) |

An override must invalidate cached results when it changes: `native_leaf.py`
already does this by putting `native`, `native_policy` and `native_sha256` into
the per-leaf `budget`, and `campaign.py` re-runs a leaf when the budget differs.
That is the model `R7` requires (`binding=budget_hash`).

## 8. Fail-closed test contract

Before an override is merged, the coordinator requires:

1. a committed record under `results/…/admission/<name>.json` and its verdict
   from `python3 gate.py <record> --mode admission --out <verdict>`;
2. exit code 0 from the gate. `REJECT` (2) and `INCOMPLETE` (3) are both
   non-mergeable; a timeout or missing artifact is `INCOMPLETE`, never a pass;
3. the verdict's `required_scope` pasted verbatim into the result README;
4. every arm that was run, including discarded ones, present in `runs`;
5. no change to `tools/color-resolved-wallcc/campaign.py` defaults,
   `run`/`finalise`, the ledgers, the frozen coverage or the encoders; an
   override is an explicit flag whose value is part of the cached budget;
6. `python3 tests/test_gate.py` passing (26 cases, including cap-as-UNSAT,
   control-equivalence, hidden regression, seed instability, unpinned solver,
   relaxed certificate, same-binary cross-check).

## 9. Limits of this gate

* It trusts the record's attested facts. A fabricated `runs` entry passes.
  Independent replay stays a separate obligation (that is the reviewer role).
* `pins.inputs` are compared to each other, never to the file on disk; the
  adapters take the hashes from the published receipts.
* It cannot distinguish "no gain" from "gain below the measured noise floor";
  both are `REJECT`/`INCOMPLETE` for adoption purposes, and the verdict says
  which.
* The 10 % margin is a policy choice anchored in the bank's replicate spread,
  not a statistical guarantee; the per-seed and per-cell rules do the real work.
* Board findings are cited as evidence and encoded as rules; they are not re-run
  here. `d4/f1`'s traps are enforced by `R9`, but the underlying solver calls
  belong to that member, not to this audit.
