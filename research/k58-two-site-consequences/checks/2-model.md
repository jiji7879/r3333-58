# Independent model checks for ledger entry 2

Ultramath swarm `smwze4dpo` used four members with the model
`deepseek/deepseek-v4.1-flash`, separate from the coordinator/writer. It had a
75-minute initial deadline and 100 steps per member. Three mathematical or
forensic audits were accepted after direct inspection and fresh execution;
the fourth direction was not counted as a success. The swarm is now closed.
No member was permitted to modify production ledgers, coordinator scratch or
search behaviour.

## Direction d2 / m2 — strict closures: accepted after repair

Report: `.ultramath/smwze4dpo/m2/REPORT.md`.

It reconstructed every twelve-case `search` and `unsplit` query and its proof
content hash, then independently replayed binary DRAT with no `-w`. It passed
both signature block covers and demonstrated the junk-suffix warning failure
of the packaged verifier.

I rejected its first report because it silently omitted the 5,201 owner-
auxiliary clauses from its local witness projection (19,485 instead of 24,686
clauses). I then ran the repaired `replay12.py` in `.scratch/two-site-
consequences-v1/strict-m2-review`. All 286 checks pass, including clause-for-
clause equality with the full projection, all 12+12 cases, and all eight
cross-pivot checks. I compared fresh and member receipts; only the local
checker path and binary hash differ. The scope corrections about unsplit
queries and extra `branch-h` units are required for interpreting the result.
Verdict: accepted as scoped formula-level evidence, not a branch or Ramsey
result.

## Direction d4 / m4 — semantics and owner subset lattice: accepted after repair

Report: `.ultramath/smwze4dpo/m4/AUDIT-C.md`.

It evaluated 157 local witnesses and replayed 34 owner/subset refutations,
then reconstructed the complete antecedent/subset coverage and six live
two-site cases.

My fresh reading found two genuine structural diagnostic defects, despite
its correct principal replays: the implementation constructed positive AMO
and triangle clauses rather than negative ones, and it compared owner cubes
to ordinary-row units instead of each reconstructed signed parent's units.
I rejected that first report. The corrected scripts were rerun from source
in `.scratch/two-site-consequences-v1/semantic-review-v2`: every K58/K30
axiom count is exact, all 157 witnesses pass, 17+17 replays pass without
warnings, no subset is uncovered, all 47 owner cubes belong to the correct
parent, and projection containment passes. Its corrected receipts agree with
fresh outputs up to timing metadata. Verdict: accepted with the local-model
and no-transfer restrictions intact.

## Direction d3 / m3 — archive and provenance: accepted with its limits

Report: `.ultramath/smwze4dpo/m3/REPORT.md`.

It distinguished unzip/manifest self-consistency from formula derivation,
checked owner-delta reconstruction and event bindings, and refused to count
historical event proof digests whose byte proofs are absent. It identified
111 `.rup.gz` files, 99 referenced in JSON and 12 unused/unreferenced files.
None of those unreferenced files is accepted as evidence here.

Its six receipts reproduce byte-identically in a separate coordinator rerun:
04-parents, 05-bindings, 06-secondary, 07-final, 09-search-identity and
11-frontier-identity. This supports the conclusion of that direction without
taking source absence as proof of general impossibility. Its stated block on
the specific `case0_report_audit/` source route is superseded in scope by the
coordinator's independent regeneration through the actually restored
`audited-K58/revised.py::export`, with 47/47 formula hashes and cubes matched.

## Direction d1 / m1 — not accepted and not called a check

This member ended without a solution; its direction is marked `abandoned`.
No "coverage review" credit is assigned for it. The coordinator replaced the
missing counting work with a new independently written finite
recomputation: 3,701 assertions and 42 additional strict replays. That
independent checker evaluates all eight local tables, reconstructs the exact
subset minima and all three frontier proofs. It relies on no m1 claim.

**Net result:** three corrected, specifically reviewed model reports support
different parts of the package. They do not support a whole-pivot closure, a
uniform two-site transfer to all wall rows, or any Ramsey conclusion.
