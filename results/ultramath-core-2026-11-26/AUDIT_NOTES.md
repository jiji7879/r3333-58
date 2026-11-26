# Audit and verdict notes

## Accepted audit outputs

`smwx73ni9` used four members with 100 model calls and 120 minutes. Member m1
(A) and member m4 (D) produced reports, indices and raw-file inventories. The
other two directions ended without a solution. Both supplied audits were judged
and accepted **as archival/provenance work**, not as Ramsey-bound arguments.
The preservation archive explicitly excluded this live audit until it stopped;
it remains intact.

## Corrections made during curation

- The platform's actual `smwx2syxr` records have eight per-direction accepted
  verdicts, not merely swarm-level acceptance. `AUDIT_NOTES` and
  `CORE_POINTS` cite these verdicts rather than relying on the auditor's local
  lack-of-a-per-direction-file finding.
- The complete entrance families remain TT:2 and UT:3 only (1,200 cases).
- The recursive-count discrepancy, 25-versus-29 strict-cube wording, is retained
  as unresolved rather than choosing one convenient narrative.
- The report sizes are historical byte-inventory snapshots and use a mixture
  of hardlinked-file counts and `du`; pruning's actual measurements are kept
  separately. They are not proof counts.
- Retained raw classification/entrance/clone-family trees are exceptions to
  general raw-history retirement. They do not imply that every deleted DRAT
  cited by an old script can still be replayed here.

## Unverified and incomplete

The six audited reports describe which replays and enumerations were checked
and which were only read. The other 27 inventoried old swarms have no fresh
acceptance-by-direction review in this campaign. No audit was converted into a
closure of a frozen row, uniform child, profile, or Ramsey bound.

The small proof exceptions were checked again after pruning:
`circ58` one/one VERIFIED and four/four incidence proofs VERIFIED, using
`.scratch/satcheck/bin/drat-trim`. The primary m2 entrance store and complete
m1/m3 classification material were retained without repeating their costly
full replays. `smwx2syxr/m1` retained its Lean source and environment without
adding it to the normal repository build.
