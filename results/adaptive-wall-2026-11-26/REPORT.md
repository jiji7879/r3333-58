# Adaptive K58 wall workflow: audit and prototype checkpoint

Date: 2026-11-26. Ultramath run `smwy2754s` (six members,
`moonshotai/kimi-k3.1-pro`) finished with all six directions accepted after
independent reproduction of the cited tests and bounded native replays.

## Outcome

The proposed strategy is viable as a proof-gated queue architecture:

1. apply already-validated rules to every matching signed parent;
2. close only exact replayed formulas;
3. enqueue composition rather than treating child coverage as a root proof;
4. learn from successful children only by assumption deletion and replay;
5. split survivors only under explicit matching measurements and budgets.

The main limitation is equally important: **the supplied evidence does not yet
measure a cohort-wide efficiency gain**. The artifacts support concrete local
closures and implementations, not a claim that adaptive splitting will solve
the 11,585-row wall or improve the Ramsey bound.

## Six direct whole-row certificates now independently replayed

All six direct rows in the separate `(15,15,15,12)` package passed on:

- their physical core;
- the regenerated exact original FIRST parent;
- the regenerated exact original RETRY parent.

Each core clause was checked to be a physical host clause or a signed pin of the
identified row. Empty-proof controls were rejected. Exact row IDs, branches,
charges, placements and the FIRST/RETRY/core/proof SHA-256 bindings are in
`whole-row-summary.json`; individual checker receipts are in
`whole-row-replays/`.

| Branch | Core vertices | Core clauses |
| ---: | ---: | ---: |
| 12311 | 34 | 4,150 |
| 20771 | 34 | 16,647 |
| 4376 | 34 | 4,223 |
| 18495 | 34 | 4,315 |
| 9011 | 34 | 4,663 |
| 23562 | 34 | 4,784 |

These are six case closures in the separate 20,166-row profile ledger. They
are **not** a profile closure, a seven-profile wall closure, a closure of the
six cutoff benchmark rows, or an `R(3,3,3,3)` result.

## Corrections to the reported campaign evidence

### Exact-H subcase arithmetic

The reported candidate reductions are arithmetically consistent:

- `12,579 -> 9,105` is `3,474` eliminated, or `27.617458%`;
- `1,108 -> 549` is `559` eliminated, or `50.451264%`.

The supplied copy-map receipts do not enumerate the initial/final exact-H
subcase sets. The forward files necessary to recover those identities were not
in the attachments. Consequently these percentages remain **reported, not
independently verified queue pruning**. The receipts concern cutoff queries,
not an enumerated exact-H identity queue.

### Six-case split/direct benchmark

Independent audits by two members reproduced:

- 48 split children: 22 UNSAT, 26 OPEN;
- two receipt-complete cutoff covers;
- 1,697,996 child conflicts in total;
- all six bundled direct probes OPEN, totalling 390,001 conflicts at a separate
  65,000-conflict cap;
- the two complete cutoffs are not unrestricted whole-row closures.

The bundled direct cap total is 390,000 versus 2,160,000 in child caps. The
reported equal-total one-of-six direct experiment is not present. Thus the
available data support `2/6 versus 0/6 at unmatched budgets`, not the claimed
matched `2/6 versus 1/6` result or a conflict/wall-time speedup. Tests rejected
OPEN/coverage-gap and non-Boolean closure labels. One of the six cases is
reverse-H; the other five are forward-H.

### Earlier 59/61 boundary indices

The older standalone package contains all 7,574 cutoff-58 packing receipts and
proof streams. Independent reconciliation found:

- all 7,574 receipts exactly equal to those in the older contact solver;
- all proof hashes matching over 102,662,262 decompressed bytes;
- 6,937 two-arm and 637 three-arm cases;
- no cutoff-60 receipt;
- 8,199 external contact UNSAT proofs absent locally.

A selected signed three-arm DRAT replay and its empty-proof control passed.
The `H >= 13` premise and whole cohort were not independently replayed. The
newer 61-edge claim requires another continuation tree and proof groups not
supplied here. The queue uses **61 as reported-only**, not as certified input.

The 937-row signed census and ledger also regenerated (933 improved, with the
reported bins), and one projected copy-map DRAT replayed. That is a static
coverage result plus a sample, not cohort-wide native certification.

### Newer boundary and strengthening packages

The independently replayed samples included the square/six 384-goal entailment
query, extension `E <= 56`, exact-57 zero-site H11 and ranked H12 cases. Their
positive and empty-proof checks passed with a separately compiled checker.
The full 179/326 boundary proof sets, other reverse-H premises and other
original-row searches were not rerun. These remain dependent/cutoff evidence,
not four-row closures.

The square/six strengthening clauses can become queue rules only with their
exact source formula, target map and RUP entailment certificate. They do not
close their parent.

## Consolidated implementation

`tools/adaptive_wall/` now tracks:

- `case_queue.py`: SQLite/CAS open cases, immutable exact formulas and signed
  contexts, rule flushing, exact binary coverage, ancestor pruning, worker
  leases, RUP-only cut materialization and independent whole-parent closure;
- `cubelearn.py`: exact parent/cube children, traced assumption deletion,
  checked necessary-assumption models, and replay-gated signed transport;
- `split_policy.py`, `benchmark_audit.py`, `projection_bindings.py`: bounded
  paired comparisons and receipt/projection accounting;
- `replay_941.py`: bounded representative driver with no SAT search;
- tests and `README.md`.

The consolidated test command ran **47 tests, all passing**. Log:
`tests.log`. No broad SAT search was launched; only the tiny synthetic
learner-minimization test invokes Kissat.

The learner's real five-assumption branch retained all five assumptions, so
no large-cube reduction was demonstrated. The supplied broad case-core
locations lacked the required bytes, which stay unresolved. A fresh driver
replay of row `941d…` additionally verified FIRST/RETRY transport and rejected
a one-unit relaxation as NOT_APPLICABLE/OPEN.

### State and proof boundaries retained by the implementation

- Timeouts and raw UNSAT/SAT receipts are attempts, not closure.
- A child cover yields `COMPOSE`, not root `VERIFIED_UNSAT`.
- A closed strengthened residual does not close the original parent.
- An exact ancestor refutation prunes its open subtree.
- Equality of the original registered formula and independent replay are
  required for original-case closure.
- RUP implies entailment. Generic DRAT/RAT is not relabelled as per-cut
  logical implication merely because a full leaf refutation verifies.
- Deletion of a whole assumption weakens the query and therefore needs a new
  proof. A SAT model after attempted deletion proves necessity; an unresolved
  deletion stays UNKNOWN, never TESTED_MINIMAL.
- Signed transport requires exact source containment, matching context and a
  fresh exact-target replay, including mapped signed units and DRAT extension
  variables.

## Real queue integration and what remains

`tools/adaptive_wall/import_six.py` also exercised the actual `CaseQueue` root
closure path, rather than validating only fixtures. It regenerated all six
exact FIRST parents with the checked frozen encoder, checked their published
hashes, registered their signed identities and replayed each original proof.
The final queue has **six VERIFIED_UNSAT cases and zero open tasks**. The
SQLite database and artifacts remain ignored in `.scratch`; the exact import
summary is `queue-import-summary.json`. This is not a larger cohort import and
does not make unregistered wall rows closed.

The six identities and case statuses have not been promoted to a running live
adaptive campaign. Before one, the remaining required connections are:

1. a checked exhaustive K58 signed-map matcher and transformed target proofs;
2. WallCC's checked split-proof composer, with `COMPOSE` kept pending until
   original replay succeeds;
3. measured direct/split estimators feeding the queue's `SplitEvidence`;
4. all required proof/core bytes and previous H-floor premises for any imported
   cohort bounds.

A sensible next bounded phase is to import parent-entailed strengthening rules
only on their exact targets and compare one direct pilot with one bounded
split on one OPEN parent. No cohort-wide H floor or edge bound should enter
that experiment without its required native evidence. The frozen-formula
validator is now demonstrated for these six real parents, but it is not a
substitute for those four integrations.

## Provenance and auxiliary records

The full reviewed member reports are preserved in `.ultramath/smwy2754s/m1` to
`m6`. The consolidated sources in `tools/adaptive_wall` are unchanged from the
accepted implementations except repository-relative test paths. Original ZIPs,
other sessions' untracked files and other members' artifacts were not modified
or committed.
