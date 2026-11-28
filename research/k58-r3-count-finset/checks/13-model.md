# Other-model and coordinator statement review for entry 13

The core decoder and all-sender construction were written by m7, classification
by m4, and generic/sender-18 alternatives by m8/m6 of `smx0gue0b`.
Review by the coordinator is an independent model reading of those artifacts,
not of the coordinator's own discarded attempt.

- Source-level trace agrees with 13-read.md; no assumption that W already exists,
  no assumption that a numeric count directly yields a catalogue mask, and no
  chain-ready conclusion.
- m8's independent generic count-to-W replay confirms the finite-combinatorial
  mechanism; it does not discharge the other fourteen senders by itself.
- m6's independent complete sender-18 support-step handling confirms the
  physical classification/coordinate interface. Its per-sender decoders are
  hypotheses, not unproved universal commuting data.
- m4's palette bridge was compiled from both public and independent-route files.
- m5's aggregation counterexample independently distinguishes readiness on all
  clauses' valuations from the originally realised sole valuation.
- Independent numerical decoding (`m7-extraction.log`) reproduces the raw table
  digit for digit, so correctness does not rest on hand transcription.

Under the declared all-sender physical-valuation scope, no model/path mismatch
or extra semantic shortcut was found.


## Adversarial follow-up (m2/m1)

The final independent review identified an important semantic qualification:
auxiliary guards are above 6612 and therefore false at realizedValuation.
Hence bare `.ready (realizedValuation)` is vacuous. This does not falsify
W/cardinality, degree criticality or the physical support mask, but it changes
which endpoint is meaningful. `PhysicalGuard` and the explicit catalogue mask,
agreeing-atom proofs and guard-true witness in `PhysicalGuard.lean` have now
been added and root-built. The goal statement never asserted ChainReady.
The valid finite counting theorem is not retracted, but its presentation is
amended accordingly. All eight directions were accepted, including these two
review directions, and the complete swarm has finished.

M1 independently exposed the degenerate code equality
`hostVar 32 33 one = hostVar 32 32 one`. Its source code and compiler replay
confirm that no-loop should mean distinct actual endpoints, not inequality to
that degenerate code. The integrated construction uses exactly distinct
endpoints, so this warning does not invalidate it.
