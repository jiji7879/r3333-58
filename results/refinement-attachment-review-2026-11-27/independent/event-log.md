# Direction B — event-log soundness and state integrity audit

## Scope and bottom line

Audited the quickstart state transition, the event-sourcing protocol in its README, the cached-receipt reconstruction in the larger overlay, and coordinator commit `a74f7c2915f4482f5f7906bb2ca451acd031de4d` (`a74f7c2`). Package source was extracted and read before any of it was executed. Coordinator probes use private copies obtained with `git show a74f7c2:...`, not the subsequently changing worktree; `results/source-identity.log` records matching hashes.

**The singleton quickstart transition is conservative, but the claimed general proof-checked append-only event log is not implemented in the supplied artifacts.** The quickstart rebuilds one fixed event and one static before/after view. It has no ordered-log loader, active-parent state fold, batch transition, stale-parent check, or prior-prefix commitment.

**Separately, the coordinator at `a74f7c2` has a conditional but concrete soundness failure under `python -O`.** Disabled assertions allow false closure decisions and allow `build_ledger` to publish `VERIFIED_UNSAT` when both checker calls failed. Normal Python rejects the same fixtures. This does not falsify the reported normal-mode proof replays, but optimized Python must be forbidden until all proof/status gates are explicit checks.

No campaign search, full quickstart run, full replay, runtime measurement, or historical execution claim was made here.

## Verdict matrix

| Claim/property | Audit result | Basis |
|---|---|---|
| Four-child singleton event binds parent, guard, owner, palette, child query hashes, refutations and survivor | **Supported at state-machine/source level** | `K58_review/ledger.py:79-101`, fresh construction in `review.py:47-129`; synthetic-grant unit probes |
| Altered `CLOSED` parent with an unrefuted survivor fails | **Pass in transition probe** | Exact rejection: `singleton refinement status mismatch` |
| Cached sibling proof or unsupported SAT status can promote the survivor | **Rejected in transition probe** | Exact-query/proof grant pair and status whitelist |
| All views are regenerated after arbitrary batches from an authoritative append-only log | **Not implemented** | README `:60-66` is a protocol for subsequent batches; code handles one hard-coded event |
| General `CLOSED`, multiple survivors, `VERIFIED_SAT`, duplicate/stale-parent handling | **Not implemented by quickstart transition** | Only exactly one `OPEN_UNKNOWN` survivor is accepted; there is no current-view argument |
| Coordinator normal-mode queue policy rejects SAT/arbitrary statuses | **Pass** | `coordinator_status_probe.py` with Python 3.12.14, assertions enabled |
| Coordinator remains sound under optimized Python | **Fail** | `coordinator_status_probe.py` and `optimized_build_probe.py` with `-O` |
| Larger overlay rechecks cached direct UNSAT/SAT evidence and reconstructs aggregate status | **Supported by source inspection only** | `conquer.py:27-65,100-114,129-179`; no execution in this direction |

## 1. Commit-pinned coordinator: `python -O` removes proof and status gates

At `a74f7c2`, `tools/refinement/queue_refine.py`:

- uses `assert` for child-schema validation at `:57-59`;
- uses assertions for query construction, hashes and both successful proof checks at `:83-132`;
- then unconditionally constructs the excluded child with status `VERIFIED_UNSAT` at `:134-142`.

Python removes these assertions with `-O` or `PYTHONOPTIMIZE`. This is not merely a malformed-input robustness issue: disabled checks change the logical verdict.

### Abstract status probe

Normal mode rejected `VERIFIED_SAT`, arbitrary `CACHED_CLOSED`, and an empty child vector. With `python -O`, all three returned:

```json
{"action":"CLOSE_NODE_BY_COMPLETE_COVER","queue_delta":-1,"unresolved":0}
```

The incomplete-cover control still returned `KEEP_PARENT_QUEUED`, so this is specifically the disappearing validation, not a blanket change to every path. See `results/coordinator-status.log`.

### Actual ledger-builder probe

`optimized_build_probe.py` creates a one-node exact CNF fixture and uses `/bin/false` as the checker, making both `strict_check` calls return code 1 and `verified:false`.

- Normal Python: `build_ledger` **REJECT**.
- `python -O`: `build_ledger` **ACCEPT**, records `REFINED_NOT_CLOSED`, `REPLACE_WITH_ONE_OPEN_CHILD`, and an excluded child labeled `VERIFIED_UNSAT`, while retained receipts say both strict checks are false.

Exact output is in `results/optimized-build.log`. The existing three coordinator tests pass in both normal and optimized modes because they contain no invalid-status or failed-proof case (`results/coordinator-tests.log`).

**Required repair:** replace proof/status/schema assertions with unconditional exceptions, or at minimum add the same startup guard used by the larger package (`overlay/engine/proof_status.py:4-5`: reject `not __debug__`). Add negative tests for failed proofs, SAT/unknown statuses and empty children under both modes. Other assertion-based coordinator verification entry points need the same review; they were not exhaustively audited here.

## 2. The event-log architecture is a specification, not supplied machinery

`K58_review/README.md:60-66` explicitly calls this a “Protocol for subsequent campaign batches.” It requires future event streams, replay from frozen input, and distinct `REFINED`/`CLOSED`/`OPEN_UNKNOWN`/`VERIFIED_SAT` states.

The implementation contains only `audit_census`, `transition`, and `rejection_controls` in `ledger.py`. `review.py:163-168` does the following:

1. freshly rebuild one predetermined event and its grants;
2. check the retained event against that expected event;
3. require full JSON equality;
4. compare a freshly constructed one-event static ledger.

That is useful for representative 983585, but it is not a generic event fold. In particular there is no enforcement of:

- ordered event sequence, unique event identity, previous-log digest, or preserved published prefix;
- exact active-parent membership before applying an event;
- rejection of duplicate/orphan/stale-parent events;
- deterministic removal of a parent and addition of every unresolved child;
- atomic commit versus rejection of a whole batch;
- descendant linkage to a retained survivor, safe deduplication, or canonical view hashes;
- general closure, multi-survivor expansion, or SAT-model view transitions.

The probe submits the same valid parent event twice. Both calls return the same survivor because `transition(event, expected, grants)` has neither a log nor a current view. This is not idempotence checking; duplicate detection is absent.

An append-only file or hash chain alone would also not establish historical completeness: a writer can rewrite a whole private chain. A verifier needs the frozen genesis and an externally retained/published prior prefix or commitment to test that the new log extends, rather than replaces, the old one.

## 3. What the singleton transition does—and does not—check

The positive property is real and narrow. `ledger.py:81-100` checks event/guard, parent/pivot, exactly four distinct physical colors, each child query against the regenerated query, an exact `(query hash, proof hash)` grant for every claimed UNSAT branch, no proof on OPEN, exactly one unresolved branch, `REFINED`, exact survivor identity, and the direct-cover grant.

My state-only probe confirmed rejection of:

- altered `CLOSED` with the color-1 survivor still OPEN;
- survivor promoted using a sibling proof;
- `VERIFIED_SAT` in the exclusion-only child schema;
- omitted continuation, changed owner/palette, wrong cover receipt;
- multiple unresolved survivors and zero-survivor `CLOSED` (the latter two are unsupported states, not soundness bugs).

The nine supplied mutation controls also pass in this isolated state test. **The grants were synthetic pairs copied from the retained event; this probe deliberately did not replay proofs.** It tests authorization logic, not the underlying RUP certificates.

Two boundaries matter:

1. `transition` alone accepted changing a child's recorded `literal` to `999999` while retaining its exact query hash. The actual public runner subsequently rejects this through `review.py:166` full-event equality. Thus there is no supplied-runner bypass, but `transition` must not be reused alone as a generic log validator without adding literal/schema checks and preserving the equality/reconstruction gate.
2. Persistent quickstart branch records hold status, query/proof hashes and a recipe, not checker version/digest, arguments, exit code and warning-free diagnostics. The in-memory `grants` set enforces “checked in this invocation,” but hashes in a detached event log do not themselves prove that history. A durable event system needs available proof/model artifacts plus reproducible strict receipts, or an independently trusted replay service.

## 4. Larger overlay: stronger cached-receipt behavior, but not event sourcing

Source inspection of `K58_verification/overlay/conquer.py` found the expected direct-cache obligations:

- `:27-52`: exact query/base/branch binding, allowed status, valid budget/backend, then strict replay of cached UNSAT evidence or rechecking of the SAT model;
- `:59-65`: cached OPEN is reused only as OPEN at sufficient matching budget/backend;
- `:100-114`: the two-child cover is itself refuted on the strengthened parent;
- `:153-176`: cover closure requires both expected children UNSAT, SAT models are checked against parent and physical graph, and verify-only compares the entire reconstructed aggregate with the saved answer.

`cover_proofs.py:26-29` supplies ordinary native cached replay with `-i` (cover replay adds `-U`) and rejects `-w`; `proof_status.py:13-20` requires return code 0, exactly one clean `s VERIFIED`, and no warnings. Thus the two modes match the required distinction in source.

This is good local receipt discipline. It does not supply the quickstart protocol's multi-event view fold. These larger-overlay observations are source-level; its controller tests and live receipts were not rerun in this direction.

## 5. Minimum obligations for an authoritative implementation

1. **Genesis and ordering:** freeze roster/formulas/encoder and starting-view hashes; use a canonical ordered event encoding and verify extension of a retained prior prefix.
2. **Active-parent check:** apply an event only to the exact active query and semantic context; reject duplicates, stale parents and orphaned descendants.
3. **Fresh semantic reconstruction:** regenerate parent, palette/owner mapping, every signed child and exhaustive split from source, not from cached status strings.
4. **Evidence before mutation:** replay every UNSAT proof strictly on its exact query, recheck every SAT model, and keep additions-only candidates subject to their own strict replay. OPEN never authorizes removal.
5. **Total fold:** survivor set equals every unresolved branch; close only with complete cover and zero survivors; retain all multiple survivors subject to slots; keep SAT, CLOSED, REFINED and OPEN_UNKNOWN distinct.
6. **Atomic deterministic views:** regenerate from genesis after each batch, with canonical event-prefix/view hashes and an explicit all-or-nothing batch rule.
7. **Durable receipts:** retain exact artifact bytes or a content-addressed availability guarantee, checker identity/flags/exit/warning diagnostics, and parent/child/proof links.

## 6. What a log alone still cannot prove

Even a correct fold establishes only conditional SAT-preservation/refutation for the exact encoded queries covered by checked evidence. It does **not** by itself establish:

- correctness or completeness of graph-to-CNF encoding, upstream classification, campaign enumeration, or all-recipient transport;
- closure of an unguarded original representative, wall row, or Ramsey problem from a guarded child;
- SAT or UNSAT for any `OPEN_UNKNOWN` node;
- producer identity, publication time, or that an external campaign remained byte-unchanged;
- the 13-second/12-minute timings or any general runtime improvement;
- historical availability of proof artifacts or correctness of an unsupported checker binary.

## Artifacts and reproduction

Run from `.ultramath/smwyob8l4/m5/` with Python 3.12.14:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 state_machine_audit.py
PYTHONDONTWRITEBYTECODE=1 python3 coordinator_status_probe.py
PYTHONDONTWRITEBYTECODE=1 python3 -O coordinator_status_probe.py
PYTHONDONTWRITEBYTECODE=1 python3 optimized_build_probe.py
PYTHONDONTWRITEBYTECODE=1 python3 -O optimized_build_probe.py
PYTHONDONTWRITEBYTECODE=1 python3 coordinator/test_queue.py
PYTHONDONTWRITEBYTECODE=1 python3 -O coordinator/test_queue.py
```

- `state_machine_audit.py`; output `results/state-machine.log`
- `coordinator_status_probe.py`; output `results/coordinator-status.log`
- `optimized_build_probe.py`; output `results/optimized-build.log`
- `coordinator/test_queue.py`; output `results/coordinator-tests.log`
- `results/source-identity.log` — audit commit, current HEAD when rechecked, and pinned-copy hashes

## Explicitly outside this direction's tested claims

The representative's actual RUP certificates and public tamper driver; 983,774 live and 3,066 closed counts; minimum 28; cap-128 exhaustive receipt replay; full proof transport/first-tier encoding; frozen-total arithmetic; manifests/provenance; quick/full runtime; and any assertion about how historical coordinator invocations were launched. Those require the other directions' evidence and must not be inferred from this state-machine audit.
