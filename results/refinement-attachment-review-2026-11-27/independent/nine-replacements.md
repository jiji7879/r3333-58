# Direction C audit: coordinator replacements versus reviewer semantics

## Verdict

**The nine committed replacements are mathematically supported on their exact guarded CNFs.** I independently rebound every query and replayed all 18 consequential certificates (nine covers and nine sibling exclusions). Every accepted successor is a unit strengthening of its audited parent, and every continuation remains `OPEN_UNKNOWN`. I found no incorrect `CLOSED`, SAT, whole-representative, row, or Ramsey promotion in these nine records.

**There is nevertheless a serious, configuration-dependent verifier defect.** `tools/refinement/queue_refine.py` uses Python `assert` for proof acceptance and semantic checks. A tiny negative control is rejected by normal Python but accepted by `python3 -O`, which emits an unsound singleton replacement. This does not invalidate the nine separately replayed proofs, but optimized Python must not be used for this verifier.

The audit target was coordinator commit `a74f7c2915f4482f5f7906bb2ca451acd031de4d`. The evidence ZIP hashed to `c0b73190fd7884e5420aa198c2a33362386b6235fd6f83fb8c524630c2ace158`, matching the committed summary. For a stable negative-control replay, `coordinator-a74/queue_refine.py` is a private copy of that commit's source, SHA-256 `c3b0820992f41f24a636a8069f4dc4c2ee52d71c02b3527b637d54672403edd9`. The shared coordinator tree advanced during this audit; later changes are outside this commit-scoped verdict and were not reviewed.

## 1. Binary cover versus the reviewer's four physical colors

The reviewer requires four branch records in `K58_review/ledger.py:83-100` and rebuilds their exact identities in `review.py:76-122`. The coordinator instead records two literals in `tools/refinement/queue_refine.py:113-149`. These shapes are different, but the coordinator does **not** need to enumerate four physical colors to establish its logical replacement.

For exact parent $P$, survivor literal $x$, and excluded literal $y$, my script derives $x$ and $y$ from the actual CNF extensions and checks:

1. `refined.cnf` is exactly $P\land x$;
2. the excluded query is exactly $P\land y$ and has a strictly replayed refutation;
3. `cover.cnf` is exactly $P\land\neg x\land\neg y$ and has a strictly replayed refutation.

Thus

$$P\models x\lor y,\qquad P\models\neg y,\qquad\text{so }P\models x.$$

Conversely $P\land x\models P$ is immediate. Therefore $P$ and $P\land x$ have exactly the same models, not merely an inferred SAT/UNSAT label. The cover discharges all possibilities outside the binary split; the sibling exclusion alone would not do so. Conversely, the cover alone leaves both children possible. Both obligations are independently necessary, and the script includes small model-set controls for both failure modes.

The coordinator establishes this argument at `tools/refinement/assemble.py:137-148` and rechecks it at `queue_refine.py:125-146`. `verify_release.py:81-95` also names the two checks separately. This agrees with the reviewer's direct-cover semantics, although an adapter to the reviewer's literal four-branch event schema would have to construct those physical branches rather than relabel the two abstract records.

## 2. Independent replay of all nine replacements

I inspected the quickstart source and checker entry points before compiling its vendored `drat-trim.c`; my driver, not the quickstart driver, supplied strict options. Checker source SHA-256 was `d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee`; locally built executable SHA-256 was `3a62f702b49fdfddd8c12885110b0947f021eced7fa3e0139b3bb94fd2f1f874`.

Command (from `.ultramath/smwyob8l4/m1/`):

```sh
cc -O2 quick-src/K58_review/vendor/drat-trim.c -o bin/drat-trim
python3 -B audit_replacements.py \
  --archive ../../../dist/k58-refinement-pilot-audit.zip \
  --checker bin/drat-trim --out replacement-replay
```

Exact stdout, also in `replacement-replay-command.log`:

```text
PASS node 1: arm 11, survivor 6550, excluded 6551; strict cover+sibling replay
PASS node 2: arm 12, survivor 6421, excluded 6423; strict cover+sibling replay
PASS node 3: arm 12, survivor 6423, excluded 6421; strict cover+sibling replay
PASS node 4: arm 13, survivor 5434, excluded 5433; strict cover+sibling replay
PASS node 5: arm 13, survivor 5442, excluded 5444; strict cover+sibling replay
PASS node 6: arm 13, survivor 5444, excluded 5442; strict cover+sibling replay
PASS node 7: arm 14, survivor 5442, excluded 5441; strict cover+sibling replay
PASS node 8: arm 14, survivor 5442, excluded 5441; strict cover+sibling replay
PASS node 9: arm 14, survivor 5442, excluded 5441; strict cover+sibling replay
{
  "replacements_verified": 9,
  "distinct_guarded_parents": 9,
  "all_survivors_open_unknown": true
}
```

All 18 calls used `-i -U -t 60`, with no `-w`; all returned 0, printed exactly one standalone `s VERIFIED`, and emitted zero warnings. The complete commands, outputs, full query/proof hashes, owners, guards, row identifiers, and literals are in `replacement-replay/summary.json` and the 18 per-node logs. This is proof replay only, not a K58 search or a runtime measurement.

## 3. Reproduced unsound acceptance under `python -O`

The decisive gates at `tools/refinement/queue_refine.py:131-132` are assertions, as are the identity checks at lines 90-129. Python removes them under `-O`. By contrast, the reviewer's `K58_review/formulas.py:14-16` implements `need` with an explicit `raise`, and its transition checks call `need`.

My independent control uses $P=(x\lor y)$, proposed survivor $P\land x$, and alleged excluded child $P\land y$. The cover $P\land\neg x\land\neg y$ is genuinely UNSAT, but $P\land y$ is SAT at $(x,y)=(\mathrm{false},\mathrm{true})$. The same bogus empty proof is supplied for both. The native checker rejects the excluded child and accepts the cover, so this isolates the coordinator's assert handling rather than a malformed fixture.

Command:

```sh
python3 -B optimized_assert_control.py \
  --coordinator coordinator-a74/queue_refine.py \
  --checker bin/drat-trim --out optimized-control
```

Key exact output from `optimized-control-command.log` and `optimized-control/summary.json`:

```text
"normal_returncode": 1,
"normal_rejected_invalid_sibling": true,
"optimized_returncode": 0,
"optimized_emitted_unsound_replacement": true,
"optimized_node_status": "REFINED_NOT_CLOSED",
"optimized_action": "REPLACE_WITH_ONE_OPEN_CHILD"
```

The emitted refinement loses exactly the parent model `[false, true]`; see `optimized-control/summary.json`. The normal rejection is at `queue_refine.py:131` in `optimized-control/normal.log`; the successful optimized stdout is in `optimized-control/optimized.log`. The fix is to replace verification assertions with explicit exceptions (and test under `-O`), not merely to suppress warnings or trust a cached status.

## 4. Queue and status semantics: what is and is not established

I independently ran the three coordinator queue tests with bytecode writing disabled. All passed; exact output is in `queue-tests-command.log`. They support the abstract status-transition policy, including no closure while an `OPEN_UNKNOWN` child remains.

They do **not** prove a general event-log implementation. `decide` at `queue_refine.py:43-73` consumes a Boolean `complete_cover` and child status strings. `build_ledger` supplies freshly checked values for the nine singleton cases, but `test_queue.py:19-62` uses synthetic labels and model sets. Zero-open closure and multi-open expansion therefore still require their callers to bind exact queries and replayed proofs; the tests alone cannot discharge those obligations.

The coordinator queue is also an **initial replacement snapshot**, not a regenerated post-comparison view. In the supplied ZIP, node 7 remains `REFINED_NOT_CLOSED`, its survivor remains `OPEN_UNKNOWN`, and `unresolved_nodes` is 9, while the separate comparison receipt labels both node-7 guarded parent and refined child `VERIFIED_UNSAT`. Exact records are in `status-view-command.log`. This is not an unjustified closure and does not contradict the coordinator report's explicit “initially”/“subsequent” chronology. It would be stale if consumed as the current authoritative ledger. I did not replay those two later comparison proofs in this direction.

Accordingly, the reviewer's `REFINED` with an open continuation and the coordinator's `REFINED_NOT_CLOSED` are compatible scoped labels. Neither makes `OPEN` mean SAT or UNSAT. Neither a guarded replacement nor the later guarded-node refutation closes the unguarded original representative. A guarded child refutation alone likewise cannot refute its original parent.

## Tested commitments

- Nine exact CNF parent/refined/excluded/cover identities and hashes.
- Nine sibling and nine cover certificates under strict warning-free native replay.
- Singleton status and queue identities for those nine records.
- Abstract three coordinator unit tests.
- Normal-versus-optimized behavior on a decisive unsound tiny control.

## Untested or deliberately not inherited

- I did not regenerate the nine parents from the original campaign roster or independently prove the upstream first-tier encoding. The verdict starts at the exact guarded parent CNFs in the coordinator ZIP.
- I did not rerun the coordinator's other 60 replay calls, any fresh CaDiCaL search, the quickstart review, its full replay, the larger verification package, the minimum-28 evidence, or exhaustive cap128 claims.
- I did not verify a frozen total of 983,774, whole-row coverage, a Ramsey bound, or any runtime improvement. No such result follows from this audit.
- Native `drat-trim` remains a trusted checker binary built from the inspected supplied C source; this is not a formal proof of the checker itself.
