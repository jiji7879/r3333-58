# Verification record for the manuscript

Preparation date: 25 November 2026. The mathematical source snapshot began at
`35140c07b27e922dfa0fde19dafdaa4b0bf703fe`; independent reviewers also saw the
concurrent classification/handoff revision `abf04ef8458e3a4760cbefa31654e0fe3490360c`.
The manuscript and its supplementary files are new deliverables, not results that
were already in either base revision.

## Checks rerun for this draft

### Numerical and document checks

```sh
python3 paper/check_claims.py
bash paper/build.sh
```

The first command exited 0: eleven profiles, exactly the two expected reciprocal
candidates, totals `(CERTIFIED=98142, OPEN=12893, LEGACY=2144)` summing to
113179, the 1308/11585 OPEN split, and the 496-certificate arithmetic. It also
checked the two elementary inequalities in the mixed-cut proof. This is an
arithmetic check, not a SAT or ledger-proof audit.

The LaTeX build exited 0 and produced `main.pdf`. Its final log had no undefined
citations/references, LaTeX warnings, overfull boxes or underfull boxes.
The published background bounds were checked against Radziszowski's DS1.18 PDF
(24 April 2026), whose Section 6.1.1 states `51 <= R(3,3,3,3) <= 62`. Tatarevic's
arXiv:2610.36648v2 abstract and full text were also read; its claimed 60 bound
is cited as a preprint, not independently reproduced here.

### Full replay of the common-critical certificate

The supplied archive was `attachments/let-s-try-and-rbdv/K58_common_critical_color_certificate.zip`,
with independently recomputed SHA-256
`9bd2f2ee9f3815746fe0a98a747c10cb1c507f8e4fb7983e23e933546cde686a`.
The ZIP inventory has 509 files; `SHA256SUMS` has 508 entries, because the
manifest does not hash itself. From the extracted package in
`.scratch/common-critical-audit/`, the rerun was:

```sh
TMPDIR=<project-scratch-tmp> /usr/bin/time \
  -f 'WALL %e s\nMAXRSS %M KB' python3 verify.py --jobs 2
```

It exited 0 in 179.24 seconds (65,240 KB maximum RSS), reporting

```json
{"checked": {"catalog": 2, "slots": 247, "words": 247}, "orbits": 247, "placements": 4356, "total": 496}
```

The output is retained as
`../results/common-critical-audit-2026-11-25/manuscript-replay.log`.
A separate accepted reviewer rebuilt drat-trim from the supplied C source and
replayed the same 496 proofs in 118.28 seconds with the identical counts.
These runs replay the supplied encodings and proof checker; they are not new
independent encoder implementations or a Lean proof.
Some ZIP extractors (including the Python standard-library method used by two
reviewers) drop the bundled checker's executable bit. In that case restore it or
rebuild the supplied C checker and pass `--checker`; the resulting
`PermissionError` is not a SAT or DRAT failure.

### Conditional Lean profile check

From the repository root:

```sh
LEAN_PATH="$PWD/lean:$LEAN_PATH" lean paper/lean/ReciprocityBoundary.lean
```

Lean 4.33.1 exited 0. The final `reciprocal_profile_with_certificate` and its
connectivity/profile components printed only `[propext, Classical.choice,
Quot.sound]`. No `sorryAx` or `native_decide` axiom occurs. The finite
`CommonCriticalCertificate` remains an explicit premise of the final theorem.

For the additional row-label audit, the coordinator independently ran
`.ultramath/smwwouesu/m5/audit_reciprocity_profiles.py`. It passed identity,
family and wall checks and produced 113,143 reciprocity-incompatible labels and
36 compatible labels (18 in each exceptional profile). Its arithmetic Lean
artifact and a second independent soundness artifact (`m7`) also compiled with
only the three standard axioms. The 36-label detail is deliberately not used as
a main theorem of the paper and is not a new UNRESTRICTED UNSAT count.

### Base K58 build

The first attempt exposed an incomplete upstream cache and a path mismatch:
`build-catalogue.sh` writes `replay/.catalogue`, whereas `build.sh` looked for
`.catalogue`. `lean/build.sh` and its ignore rule have been corrected, the
upstream closure is being rebuilt, and the temporary local symlink has been
removed.

**At this draft's commit snapshot, that full rebuild and an additional
coordinator rerun of the semantic-table enumeration were still running. No
successful base-build result is claimed in this version.** Their completion
status is intentionally left for a subsequent verification update. The common
496-certificate replay and the supplementary conditional Lean check above are
separate completed checks and do not depend on treating this running job as a
pass.

The successful reviewer-side semantic enumeration took 241.784 s and checked
45 literal slot constraints (4,940 calls), 24 four-anchor word constraints
(170 calls), and all 4,356 placements. The coordinator's first additional run
hit a 300 s limit before printing a result; that timeout was not treated as
mathematical evidence, and a longer rerun was started.

## What was not independently rerun or established for this paper

* The 1,588-module generated frozen-cover replay was **not rerun** during paper
  preparation. The paper records the earlier tracked successful audit in
  `review/LANDING_GLUE.md` and `review/LEAN_FROZEN_COVER_VERIFIED.md`; it does
  not call that record a fresh run.
* The release containing the 98,142 owner-reported case certificates contains no
  corresponding proof bytes. Its 0-failure replay line and 12-of-12 sampled CNF
  reproductions belong to the audited release record. No 98,142-case proof replay
  was performed here.
* No unrestricted OPEN row was closed, no UNKNOWN solver result was promoted to
  UNSAT, and no claim `R(3,3,3,3) <= 58` is made.
* The 496 common-critical DRAT certificates are not yet a pure Lean-kernel proof.
  The supplementary Lean file checks only the conditional profile implication
  after naming that finite result as a premise.
* The ticket-gap argument is checked mathematical prose, not a Lean declaration.
* A fresh-clone public release test was not performed. The common-critical ZIP
  and its source note are ignored attachments and must accompany any external
  reproduction package; a clean checkout of the repository alone does not supply
  the proof payload.
