# Proof-carrying cube-and-conquer refinement pilot

## Outcome

The bounded plan produced **nine fully proof-linked conditional single-survivor
refinements**, not a general theory and not a wall-row closure. A complete-cover
certificate and a sibling-exclusion certificate independently support every
replacement. Initially all nine surviving nodes remained `OPEN_UNKNOWN`.

A subsequent eight-search comparison left the first examples for arms 11–13
`OPEN_UNKNOWN` at three seconds per query. For arm 14 it refuted the guard parent
and the refined child. Both fresh deletion-free proof transformations passed
strict warning-free replay. This closes **one guarded inner region** identified
in this pilot, not its unguarded original representative, wall row, or Ramsey
bound.

No broad parent sweep or long DAG search was run.

## Learner scope

`tools/refinement/cube_probe.py` used four deterministic nonempty binary labels,
one for each arm size 11–14. Its 80 local searches comprised 16 shallow and 64
ternary probes. It found 45 locally feasible cube assignments, 19 transported
UNSAT assignments, and nine unique-survivor conditional values. Local models were
validated as local arm models only; they are not K58 models.

The handoff's provenance bug was fixed by resolving each stored `log` field under
the original cohort directory. Rebuilt queries are also compared byte-for-byte
with the stored query before proof replay. The assembler writes exact parent,
refined-child, sibling and cover queries; cached status names are never used as
proof.

## Why each replacement preserves satisfiability

Let $P$ be the exact guarded query containing the unmodified representative and
all retained root exclusions, original pivot, child exclusions and cube guards.
Let $x$ be the surviving colour's physical literal and $y$ the other candidate's
physical literal. Two independently checked obligations hold:

1. $P\land\neg x\land\neg y$ is UNSAT, so $P\vdash x\lor y$;
2. $P\land y$ is UNSAT.

Consequently every model of $P$ satisfies $x$, and every model of $P\land x$ is a
model of $P$. Replacing $P$ by $P\land x$ is therefore SAT-preserving on this
guarded region. It requires no assumption that the survivor is SAT: its status
stays `OPEN_UNKNOWN`.

For each of the nine nodes, the first cover obligation has a binary `a\0` proof
that passes strict `-i -U` checking by unit propagation. The second has the
transported physical proof from the cohort. Both are rerun from disk by the queue
verifier. The two colour literals are distinct variables even though they belong
to one edge; completeness comes from the cover proof, not variable identity.

## Queue semantics verified

`tools/refinement/queue_refine.py` re-derives the two choices from exact query
extensions, checks query/proof bytes and hashes, and replays both certificates.
Its nine-record ledger occupies nine queue slots before and after replacement;
dedup alone is not counted as progress.

For an exact certified cover:

- zero unresolved children closes that inner node only when all children have
  checked UNSAT evidence;
- one unresolved child permits replacement after every other child is proved
  UNSAT, retaining the complete proof history;
- two or more unresolved children are never pruned: keep the parent queued, or
  expand only when all unresolved children fit in free slots ($k-1$ extra slots
  when replacing one queued parent).

`tools/refinement/test_queue.py` exhaustively checks status vectors, bounded
abstract model covers and backpressure. All three test units pass. The queue
implementation itself ran no solver search.

## Bounded direct comparison

`tools/refinement/compare.py` and `cadical_leaf.py` used fresh proof-logging
CaDiCaL 1.9.5 processes and the runtime's native deadline helper. Setup, search,
proof extraction and checking are separate fields. Each leaf also had an external
25-second process-group cutoff.

| Arm | Guard parent | Search s | Refined child | Search s |
|---|---:|---:|---:|---:|
| 11 | OPEN_UNKNOWN | 3.007 | OPEN_UNKNOWN | 3.002 |
| 12 | OPEN_UNKNOWN | 3.002 | OPEN_UNKNOWN | 3.002 |
| 13 | OPEN_UNKNOWN | 3.002 | OPEN_UNKNOWN | 3.005 |
| 14 | VERIFIED_UNSAT | 1.039 | VERIFIED_UNSAT | 1.202 |

Total completed search time was 20.262 seconds, within the declared 24-second
budget. These are distinct formulas. No runtime improvement is inferred from
conflict counts, search-time ratios or this sample. A cutoff or exhausted budget
remains unknown.

The arm-14 guard parent is `nodes/7/parent.cnf`, query SHA-256
`26fceae0eb90a315fa5b463e909feb5f1c8acd3f0c4b0974dc07ad8d7324a292`.
The refined child has query SHA-256
`74bf323df1722117b4fbdbfecf82ea2554c64c4afb27dd4d164586dc0dec4a36`.
Their strict deletion-free proof SHA-256 values respectively are
`467a694a80cdf6631a0b1792e946a6044c30836ecf3134ea1444063b8246067e` and
`4a9dcd4bcc213f37386fc3cb4f181c83c6184f4359c38e07a61b2144ba0fa37c`.

### Attempt accounting and the proof-warning repair

An initial Python-interrupt harness failed to produce usable three-second
receipts: four physical attempts hit the 25-second hard cutoff and remain
`OPEN_UNKNOWN`. They are not in the comparison's timing or verdict counts.
Together with the eight completed calls, that is 12 physical attempts. An earlier
startup failed before solving because resolving the venv Python symlink hid its
installed extension; it is not counted as a physical search. The final resume
reused completed leaves by exact identity instead of rerunning them.

The raw arm-14 CaDiCaL traces produced unit-deletion warnings under backward
checking and were not accepted. Dropping binary `d` records only discards
optional clause-deletion instructions; all `a` records and the final added empty
clause remain byte-identical. This can strengthen RUP premises but cannot add a
new deduction rule. The transformed proofs were checked afresh with `-i -U`,
without `-w`, and accepted only with exactly one `s VERIFIED` and zero warnings.
The raw parent/child traces were 8,445,894/10,027,052 bytes; the checked
deletion-free traces are 4,047,273/4,733,894 bytes.

The malformed-prefix negative control was also informative: `drat-trim` returned
0 and printed `s VERIFIED` after warning about the wrong binary prefix because
unit propagation closed that query. The strict wrapper rejected it because of
the warning. Neither a return code nor a success line alone is sufficient.

## Evidence bundle

The audit bundle is `dist/k58-refinement-pilot-audit.zip` (93,327,839 bytes),
SHA-256 `c0b73190fd7884e5420aa198c2a33362386b6235fd6f83fb8c524630c2ace158`.
Its CRC test passed. A fresh extraction passed all 495 filename/hash entries in
its manifest. Replaying from that extraction produced byte-identical summary
JSON to the direct independent replay. The bundle stays outside Git; only source
and small reports/logs are committed.

## Independent check

`tools/refinement/verify_release.py` reopens the physical artifacts and reruns
checks without campaign imports or reliance on recorded statuses. It passed:

- **78 strict positive replay calls**;
- **42 distinct query/proof pairs**;
- all 31 cohort proof artifacts, nine sibling exclusions, nine complete covers,
  27 stock transport checks and two fresh conditional-search proofs;
- equality of raw and normalized addition records;
- strict rejection of the malformed binary-prefix control.

See [replay summary](independent-replay/replay-summary.json) and
[full replay output](independent-replay/replay.log). Positive checks contain no
warnings and no `-w` flag.

The Ultramath run `smwymdevf` ended without member submissions, so no member
solution was accepted. Its shared transport counterexamples reinforced the same
coverage and cache-status restrictions used here; the results above rest on the
fresh physical replays, not on that status alone.

## Limits

This is a proof-carrying mechanism demonstrated on a small deterministic cohort.
The nine rules retain their row, owner, palette/mapping, branch and guards. They
are not unrestricted or population-level forcing rules. No whole original parent,
ordinary wall row or Ramsey bound was closed, and no general speedup was shown.
