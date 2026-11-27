# Attachment verification addendum — coordinator report

## Outcome

The supplied quickstart event and the larger frozen verification families
support the claimed scoped evidence. **983,774 representatives remain live on
11,585 ordinary wall rows. No original parent, wall row or Ramsey bound was
closed by this verification.** This is not a full Lean or graph-to-Ramsey
reduction certificate.

The worked physical refinement remains guarded: for representative 983585,
physical colors 0, 2 and 3 are refuted on edge (32,43), and color 1 is the sole
`OPEN_UNKNOWN` continuation. The parent is `REFINED`, not `CLOSED`.

## Independent review and configuration repair

Six independent swarm directions were used: quick reconstruction, event-log
semantics, my nine replacements, owner minimum 28, physical transport, and
package integrity/provenance. Accepted reports and the coordinator's replay
logs are included in this folder.

The final verdict must not be read as blanket verification of original
execution dates, producer signatures, binary builds or a global Ramsey theorem.
Those remain unverified or intentionally outside claim, as detailed below.

## Inputs and provenance

The two new ZIP manifests passed in full: 24 reviewer files and 3,308 addendum
files. Their ZIP hashes are
`57c572afbd7db2047facf614788a903924e01bb60ed3cb1f210922da1f5cff95` and
`42b5c997dc6ad341e42b1af0dc76c5ffc49fadc55a01838f20bbbc183039f9de`.
Both original input archives also passed their frozen manifests. The count is
30,336 entries including two manifests, hence 30,334 nonmanifest entries from
disjoint file sets.

Offline installation used hash-locked wheels only. It passed, along with
reconstruction of the pinned public commit/tree/blobs and upstream Kissat Git
tree. Object identity and wheel metadata are checked, not producer signatures;
the project commit is unsigned. The attached audit Markdown matches the
packaged `REPORT.md`, SHA-256
`de8caf4afb26e4341f99d2181c4dff3beaf3b2fc270f1e4a2065fcd135f81099`.
This newer addendum is separate from the earlier pinned report blob, whose
SHA-256 is `c7497681bc2c6cbd863f7241bd7f08abd8ac891a98e7ab318fab38c67e0799bd`.

## Worked event, with warnings unsuppressed

The supplied quickstart's `formulas.check_native` calls `-i -w -U`, and its
README recommends warning suppression. That does not meet this project's
strict acceptance policy. Worse, an independent control consisting of a valid
empty-clause addition followed by an invalid opcode still returns 0 and prints
`s VERIFIED`; the supplied `-w` predicate accepts it while the unsuppressed
output reports `WARNING: wrong binary prefix`.

`tools/refinement/review_quickstart.py` leaves the package inputs and manifest
unchanged and overrides only the native checker call. It requires `-i -U -t 300`,
return code zero, exactly one `s VERIFIED`, and no warning in the combined
output stream. It re-runs the exported cover independently.

The strict run passed in 1.34 seconds; fresh-extraction post-guard runs also
passed. A different host's 13-second observation is neither confirmed nor
refuted by these local measurements.

| Physical color on (32,43) | Supported result |
|---|---|
| 0 | refuted by the transported physical certificate |
| 1 | `OPEN_UNKNOWN`; no refutation or full model |
| 2 | refuted by physical unit propagation and empty-clause RUP |
| 3 | likewise refuted |

The direct cover certificate additionally refutes the guarded parent plus the
negation of color 1. Its emitted hashes match the recorded event, SHA-256
`364c1d632b8f220ebb185e7a43ad23b733abc62163f9b5032d79fa9611ec9b95` for the
query and `6a22c515098b6d0a2f095c2805edde6621302036372ad35a086a451459726632`
for the proof. Nine supplied invalid-record controls and independently added
semantic tamper checks are rejected. In particular, `CLOSED` cannot replace
`REFINED` while color 1 remains unresolved.

The frozen roster does not change. Representative 983585 remains in the queue
at revised rank 46, pair `21012/22101`.

## Minimum 28 for owner 21012/22100

The 147 earlier revised pairs require exactly 28 alternatives under both the
eight-pin and ten-pin conventions. The checks are now independent in two ways:

1. The 29 complete 13-vertex lower witnesses pass triangle, pentagon, pin and
   occurrence checks. Their disjoint constraints yield the hitting-set bound
   `20+6+2=28`, and they also supply one private deletion witness for each of
   the 28 chosen alternatives.
2. Independently regenerated DIMACS has 522 variables and 3,040 clauses, with
   the expected SHA-256. Its eight-pin cover has a strictly replayed
   10,535,211-byte RUP certificate and an LRAT proof with 200,064 additions and
   9,412,150 unit-propagation hints. A separate stdlib LRAT implementation
   confirms the same result and rejects deletion of a necessary hint.

The older 29-pair list still passes every single deletion test. This result
optimizes one local owner statement and does not itself remove any physical
representative. It must not be substituted for the upstream cover derivation
or survivor refutations.

## Full frozen-addendum batch

The coordinator ran **all 28 commands successfully** with three workers.
Wall time was **1110.05 seconds (18 min 30 s)**; user CPU time was
2844.19 seconds and system CPU time 292.98 seconds.
The timer produced zero for its memory field, so no maximum-memory claim is made.

| Frozen stage | Result |
| --- | --- |
| Queue and saved cap128 transcript | 3,066 closed, 983,774 live; 1,101,974 saved UNKNOWN returns and matching counter triples |
| Full closed-parent checks | all 3,066 exact representatives verified |
| Selected physical consequence queries | 2,469 native RUP replays |
| Revised replacement cover/symmetry | 304 cover and 718 symmetry proofs |
| Original-order symmetry | 765 final and 707 intermediate certificates, with 1,084 retained-case witnesses |
| Selected edge domains | 7,539 original and 6,930 revised affected entries |
| Additions-only transport | 2,469 forward proofs and all four physical arm interfaces |
| First-tier encoding | 11,585 matching parent hashes, 134,995 host clauses, 456,079,506 suffix clauses |
| All-recipient projection | 983,774 root and 1,966,300 child queries, 2,469 sample hash matches |
| Panels and controls | all bounded receipt checks, joining-colour complements, repaired-cache controls and K5/K6 checks passed |

The control log contains warning lines from rejected raw/native checks and deliberate
negative controls. Those are not accepted warning-bearing proofs: fresh producer
traces may yield an additions-only candidate only after a separate strict replay.
Cached certificates are checked as stored; no candidate inherits a cached terminal
status. Ordinary positive replay acceptance does not suppress warnings.

The log distinguishes replay from newly launched searches. In particular:

- all 1,101,974 saved cap128 transcript entries return `UNKNOWN` and match all
  1,101,974 historical counter triples. This validates the saved execution
  transcript, not contemporaneous attestations of its date, engine identity or
  producer;
- all 3,066 closed full representatives pass individual proof replay;
- all 2,469 selected physical consequence queries pass native replay;
- the independent first-tier encoder matches all 11,585 parent hashes and
  accounts for 456,079,506 suffix clauses on top of 134,995 host clauses;
- the normative transport argument requires all three checks: independent
  first-tier encoding, additions-only local/interface proofs, and all-recipient
  physical query construction. A per-row hash computation alone does not prove
  a local refutation.

No fresh cap128 sweep, generic wall search, runtime ranking, full Kissat binary
rebuild or Lean kernel replay was performed in this coordinator pass. Frozen
panel and control evidence was replayed from the supplied installed copy.

## Coordinator hardening and status views

An independent audit found that `a74f7c2` used `assert` for proof/status gates.
With `python -O`, a demonstrator could emit `VERIFIED_UNSAT` while `/bin/false`
served as checker. Normal Python rejected the same fixtures, so the published
proof observations were not refuted, but optimized mode was unsafe.

All seven coordinator proof-bearing scripts now fail immediately with
assertions disabled. `tools/refinement/test_optimized_guards.py` exercises all
seven paths with `python -O`; it and the existing queue tests pass. The ordinary
post-guard 78-check replay is byte-identical to its previous summary. Refreshed
bundles also pass fresh-extraction manifest checks and replay.

The nine single-survivor replacements remain correct on exact guarded CNFs:
each has a sibling exclusion and a cover, hence identical model sets of
`P` and `P+x`. They do not require an explicit four-color branch record in this
representation because the cover discharges every alternative in the exact
binary encoding.

Their queue snapshots must not be used as a current authoritative event log:

- after replacement: nine `OPEN_UNKNOWN` guarded nodes;
- after comparison: node 7 is refuted, leaving eight such nodes.

The supplied quickstart implements one carefully checked event, not a general
ordered append-only event-log fold. There is no generic duplicate/stale-parent
check, batch atomicity, prior-prefix commitment, multi-survivor/SAT general
view, or durable authorization by a bare hash. The proposed architecture is
sound as a protocol, not as an already supplied implementation.

## Evidence packages

- `dist/k58-refinement-pilot-audit.zip`: guarded coordinator archive, 93,330,972
  bytes, SHA-256
  `2a63073549b8c1e73b9b53eb454712a976d2a7b3e94af6ceb9ff3e632983cb4c`.
- `dist/k58-quickstart-strict-replay.zip`: original quickstart plus strict
  wrapper, checker, observations and direct cover, 3,097,133 bytes, SHA-256
  `e91aee1b0a85f49082b022cdaf1ce28715de38c5efa7019ec5335ed41c4f4489`.

The main ZIP's 497 manifest entries pass. Its post-guard unpacked 78-proof replay
matches the direct JSON summary byte-for-byte. The strict quickstart ZIP contains
35 files including its generated manifest; all 34 listed member digests and the
ZIP CRC check pass, and it replays successfully from a new extraction.

## What is not established

- The quickstart's own full-original replay: it requires
  `K58_portable_learning.zip` with SHA-256
  `bf26cbcf1d1e07c8bb8f11cbc8055e71e4a7c7ab3990f1e72632a26c8071910e`.
  That file was not attached or found in the existing working state. The
  supplied library link returned HTML, not the archive. Its claimed 12-minute
  full replay, all 195 rule certificates, and 327 held-out transfers remain
  unverified by this direction. The reconstructed 829-class arithmetic uses
  stored class records and is not regeneration of their SAT screens.
- Original execution dates, execution provenance and signatures; fresh source
  builds; runtime improvements; or retroactive allocation of wall-clock totals.
- The upstream classification/completeness bridge, whole-wall Ramsey theorem,
  or a Lean kernel replay of the whole graph reduction.

In short, the attachments strengthen the exact certificate and encoding audit.
They do not close the global proof itself.
