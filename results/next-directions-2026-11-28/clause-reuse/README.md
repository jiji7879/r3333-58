# Clause-reuse result: reject the measured K15 family for speed

The accepted member report and receipts, including a coordinator-requested
measurement correction, are in `report.md`. This is a reproducible negative
result, not an abandoned inferred theorem failure.

- The retained request is pinned to the exact parent+cube SHA 8791f627….
- 960 K15 clauses associated with that exact row are decoded. **360 are already
  RUP-consequences of the request's unit propagation** and must be reported
  separately from the other 600, which require the case analysis.
- Matched 100,000-conflict ratios are 0.995 and 0.993. Matched 300,000 ratios
  reach 1.117 for all 960 clauses and 1.473 for the 600-clause subset.
  Propagations rise by up to 74%, while decisions decrease. This is the same
  misleading profile of “fewer decisions but more work per decision.”
- No CPU benefit reproduces across both seeds, both orderings and both caps.
  Two destination-native proof attempts remain OPEN with no `s VERIFIED`.
  Original historical timings involving parent-process Python time were marked
  void; corrected child-CPU measurements are about 20 s under each 20 s cap,
  with no proof verdict inferred.

Do not adopt these clauses for throughput. The local K15 theorem and binding
audit are useful provenance, but they do not establish a fresh, independent
parent-level DRAT implication for these 600 non-trivial clauses within the
allocated checking budget. Any new clause-reuse proposal must distinguish
UP-trivial clauses before benchmarking and carry its exact source guard and
destination hash.

Per-call data are in `build-receipts.json`, `bench/` and `bench2/`. Sources
`up.py`, `bench.py`, `bench2.py` and the corrected verifier
`verify_clause.py` are included as opt-in helpers, not production changes.
The exact parent state and RUP classification are in `up-receipt.json`.
