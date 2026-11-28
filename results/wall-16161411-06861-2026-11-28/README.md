# One `(16,16,14,11)` row: bounded attempt and tested improvements

## Outcome

**Row `06861a3df60c…` remains OPEN.** It was not closed, no satisfying model was found,
and no output licenses a change to the profile, the production ledger or a Ramsey bound.
This is a compact handoff; the raw working inputs and logs are under `.scratch/k58-row-16161411/`.

* Frozen first-tier parent: 19,533 variables, 184,335 clauses, 3,493,016 bytes.
* Parent SHA-256: `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae`.
* Row: TU--, arm 1, marked 15/T, branch 38, **charge 7** (not the generic dense threshold 4).
* Plain first-tier attempt: full parent, `cuts = 0`, `working.cnf == parent.cnf`,
  native CaDiCaL 2.1.2, seed 0, eager DRAT, 2M-conflict/180-second cap.
  It reached the **wall-time** cap at 180.01 seconds; the timeout receipt reported no conflict count.

The existing repository measurements were also checked rather than repeated:
600 s Kissat at 10,349,282 conflicts; four pentagon leaves at about 1M conflicts each;
both colour children at 600 s, and the 2M-conflict square-spoke panel. All stayed OPEN.

## Matched short controls

All jobs use native CaDiCaL 2.1.2, seed 0, the same 500k-conflict cap and eager DRAT.
These are experiments, not terminal claims. Incomplete traces were not retained.

| variant | input / premise | conflicts | solver seconds | result |
| --- | --- | ---: | ---: | --- |
| plain | first-tier original | 500,001 | 50.604 | OPEN |
| two square consequences | original + 2 RUP clauses | 500,000 | 28.654 | OPEN |
| full-root | retry-tier H(r) >= w(r) | 500,000 | 29.570 | OPEN |
| arm-2 RUP batch | original + 2,160 RUP clauses | 500,003 | 27.947 | OPEN |

The two square clauses replayed as `VERIFIED_CLAUSES` against the exact parent.
`full_root` is a separate balanced-root formulation, not a plain first-tier implication claim.
Differences in search path, eager proof cost and concurrent VM load prevent a blanket speed claim.

## Solver-policy comparison on the exact original CNF

| policy | wall cap | conflicts | result |
| --- | ---: | ---: | --- |
| default | 120.02 s | 1,566,787 | UNKNOWN |
| search-only | 120.01 s | 2,586,173 | UNKNOWN |

Search-only produced **1.65× the default conflicts** on the identical parent, but did not close it.
This is the most concrete measured improvement found: an **option portfolio on the same CNF**,
not a new theorem. The switches were:

```sh
cadical --seed=0 -t 120 \
  --elim=false --probe=false --vivify=false \
  --subsume=false --ternary=false --block=false --stabilize=false \
  parent.cnf proof.drat
```

## Independently checked clause families

* **Arm batch.** All **3,060** six-literal clauses were independently checked with a new
  selector miter against the exact parent, using `-I -U -f -W`: exit 0, one exact
  `s VERIFIED`, zero RAT and no warnings. Query `e0a1c92f9acacf9f7b4caaa465c4f7551b41b53476bd5d1200d93b065fac5511`;
  ASCII proof `36862081f7e19653af2e83fbe72e17f948a3fdb992972f8ae9aa7d579aed7dc6`.
  These are propagation-level implied clauses, not new global information. They add no auxiliary variables.
* **Arm-2 speed probe.** The 2,160-clause arm-2-only CNF has SHA `72690a9a9de8fea1e802f0ef35509cf4ffb466b2d546f6ce97cf65fed7e27a0c`.
  Apart from the 500k probe above, the same CNF with the search-only policy reached
  **2,487,689 conflicts in 120 seconds** and remained UNKNOWN. No original-parent proof composition was needed.
* **Pentagon subset.** **300** RUP clauses passed the same strict protocol:
  query `8603826ab5b819a1ba0e871e759bb7e0e316b0eb975e078ebc132e503943f99a`,
  proof `32dfb14f5d2df1f1fbb51f1823f2de41240f7f9287f572e188db15ccb98ce8e3`.
  An initial malformed miter control with embedded empty clauses was discarded, not counted.

### The remaining fifteen cuts

The other 15 members of the prior 315-cut batch were not RUP and had no RAT witness in
the independent unit-seeded check. Each individual negation query was run to a 200k-conflict
cap; all remained OPEN. **Unproven is not false:** no implication verdict follows from these
caps, but those 15 clauses must not be used as unconditional without an actual proof.
Any future proof must be checked on the original parent and must not rely on the circular prefix.

## Recommended next step

Do not spend another blind timeout on this row. Use a small CaDiCaL policy portfolio for
execution, and focus structural work on genuinely new implications for the undetermined edges.
The search audit found 1,257 undetermined edges after level-0 propagation and no auxiliary
literals assigned: shallow edge cubes did not close a child (0/120 single-edge and 0/32 two-edge
tested cubes), so a useful split needs stronger derived clauses first.

The generic clause-walk falsification direction found no model (best assignment: 38 violated
clauses), which is not UNSAT evidence. A model-side continuation should colour every edge
by construction rather than leaving missing-edge colours for generic WalkSAT to repair.

Three scoped Ultramath audits were accepted: arm-implied constraints; CAS transfer limits;
and the model-side null experiment. The policy/difficulty member ended on budget after
writing measurements; its modest throughput result was independently extended by the
matched 120-second runs here. No accepted report is a row closure.

See [receipts.json](receipts.json) for machine-readable experiment and proof-check metadata.
The production ledger, queue, supplied archives and candidate inputs were not modified.
