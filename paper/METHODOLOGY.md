# Methodology — what we did, and what the enumeration costs

An outline of the process, not the mathematics. It covers how a supplied proof
package was received and checked, how the case enumeration was verified, and
what the remaining computation is estimated to cost. Numbers are measured
unless marked as estimates, and each says where it came from.

---

## 0. The shape of the problem

A claimed bound of this kind is a *certified enumeration*: a mathematical
reduction that turns a hypothetical counterexample into one of finitely many
explicit formulas, plus a refutation of every formula. Neither half is worth
anything alone. A refuted formula that the reduction does not actually reach
proves nothing; a reduction whose cases are never refuted proves nothing.

So the work had two independent halves and a binding between them, and the
methodology below is organised around that triangle.

---

## 1. Reception: pin, reproduce, then doubt

**1.1 Pin the toolchain before anything else.** The bundle names exact versions:
Kissat 4.0.4 at commit `8af8e56`, drat-trim at `2e3b2dc`, python-sat
`1.9.dev22`. This is not hygiene — the verifier regenerates every CNF through
`pysat.card.CardEnc`, so a different python-sat emits different clauses and
every stored certificate fails. The pin was load-bearing and we confirmed it: on
a machine with `1.9.dev17` the documented command refuses to run at all.

**1.2 Reproduce the published smoke test exactly.** The bundle ships five
replayable certificates and states the expected output. We reproduced it digit
for digit (`replayed=5, OPEN=111035`) before touching anything else. A package
that fails its own smoke test is not worth auditing.

**1.3 Then treat the package as untrusted.** Every subsequent claim was
re-derived independently. Nothing in the audit was accepted on the bundle's
authority, including statements the bundle made about itself.

---

## 2. Audit: eight independent directions

The reduction was attacked in parallel from directions chosen to be mutually
independent, each required to produce a checkable artifact rather than an
argument:

1. **Census** — re-derive the case count from the definitions, not the ledger.
2. **Threshold arithmetic** — does `H(r) ≥ w(r)` really force some arm past its
   threshold? Brute-forced over every sender-count vector.
3. **Symmetry quotient** — are the dropped cases genuinely images of retained
   ones? Checked with explicit permutation witnesses.
4. **Classification** — is the imported K₁₅/K₁₆ classification true, and
   instantiated correctly at n = 58?
5. **Kind dimension** — are there exactly two critical-block types at 15 and 16?
6. **Encoder calibration** — does the encoding admit genuine colourings?
7. **Support tables** — is the local pattern filter sound or over-constraining?
8. **Evidence pipeline** — can the verifier be made to accept something false?

**2.1 A verdict requires re-running the work.** Each submission was checked by
executing its scripts here, not by reading its summary. Five results were
accepted this way, on the evidence of the numbers coming out as reported.

**2.2 Positive and negative results were both sought.** The audit found six
defects, of which two matter beyond bookkeeping: a citation pointing at a file
that explicitly disclaims the property it is cited for, and a manifest format
under which a two-byte "certificate" with a hand-written checker log is
accepted. Both are in `review/ERRATA.md` with minimal fixes.

**2.3 One conclusion was retracted.** A soundness objection was raised against
the retry tier, then withdrawn after instrumenting the encoder and finding the
encoding was the case hypothesis itself. The retraction is recorded alongside the
claim. An audit that never retracts anything is not being run honestly.

---

## 3. The finding that reorganised the evidence

**Certificates are bit-reproducible.** Re-running the pinned solver uncapped on
the regenerated CNF, then trimming with the same drat-trim, reproduces the
stored certificate byte for byte — 10 of 10 sampled cases, across both tiers,
identical SHA-256 and identical length.

This changes what evidence *is*. The irreducible artifact is not the certificate
but `(ledger row, recipe, CNF hash)`: everything else regenerates. Storage stops
being a blocker (~200 GB → ~3 MB of manifests) at the cost of solver time at
review. It also means a release can be checked by re-solving rather than by
trusting transferred bytes.

---

## 4. Formalisation strategy

**4.1 Build the core from the mathematics, not from the code.** The Lean
development follows the argument — degree caps, ticket double counting, the
threshold pigeonhole — rather than transcribing the Python. That found a real
defect in our own first statement (a hypothesis unsatisfiable at the zero vector,
so the theorem was vacuous), caught by the collaborating session.

**4.2 Port rather than re-prove, but verify the port is possible first.** The
K₁₅/K₁₆ classification already exists in Lean upstream. Before committing to
that route we built the upstream closure here: 32 modules, 0 failures, both
classification theorems reporting only `[propext, Classical.choice, Quot.sound]`.
That took twenty minutes and converted a speculative dependency into a measured
one.

**4.3 Port the encoding only after identifying it exactly.** The natural port
target for encoding adequacy turned out to be inapplicable — the upstream file
says its cases have no auxiliary variables. The real match was the sequential
counter. Before porting we verified, clause for clause and variable allocation
included, that the deployed solver's at-least encoding *is* that counter applied
to negated literals: every `n` from 2 to 9, every bound, zero mismatches.

---

## 5. Measuring the computation rather than projecting it

Projections were replaced by measurement at every step.

| measurement | result | source |
| --- | --- | --- |
| first-pass closure on a stratified batch | 95 of 96 | our 96-case batch |
| first-pass closure, two large profiles | 76,967 of 99,450 (77.4%) | the full run |
| retry conversion | 2,298 of 2,402 (95.7%) | the full run |
| first-pass closure, seven small profiles | **0 of 98**, against 0/306 in the author's pilot | our probe |
| solver cost, first pass | 3.7 CPU-s per attempt | a 4,111-case shard |
| checker cost | 2.9 CPU-s per certificate | same shard |
| certificate size | 1.47 MB first pass, 7.4 MB retry | same shard / retry batch |
| scaling | 12 workers gave 1.6× the throughput of 4 | shard timings |

The small-profile probe is the most consequential. Three independent samples now
agree that those profiles close at essentially zero rate at the first-pass
budget, which means their cost is entirely in the retry tier and is unmeasured.

---

## 6. Enumerating the 113,179 cases

The cover is produced by: 11 degree profiles × 41 `(profile, kinds)` strata ×
1,764 families × support placements, quotient by palette and transport
symmetries.

**6.1 The enumeration is bound to the Lean development by content hash.** Case
identities are SHA-256 of the canonical JSON for family, placement and charge.
Regenerating all 113,179 identifiers from the Lean definitions reproduces the
frozen ledger's sorted-id digest
`c85190c6…0ff5`, and the ledger's own digest is `d34e8b27…62ed`.

**6.2 Five independent counts agree.**

| quantity | value |
| --- | ---: |
| frozen cases | 113,179 |
| raw placements before the quotient | 190,736 |
| omitted placements with explicit transports | 77,557 |
| families | 1,764 |
| support tables | 5,292 = 3 × 1,764 |
| indexed embedding words | 39,456 |

and 113,179 + 77,557 = 190,736 exactly.

**6.3 The quotient is checked with witnesses, not arguments.** Every omitted
placement carries an explicit vertex permutation of 58 labels and palette
permutation of 4 colours; 38,666,290 signed units were transported and checked
under those witnesses, and the whole finite replay was later repeated inside the
Lean kernel (1,764 families, 190,736 placements, 77,557 transports, 32 minutes).

**6.4 The residual gaps in the enumeration.**

- **401 rows** (214 whole-profile + 187 template exclusions) rest on arguments
  supplied outside the bundle, not on per-row certificates.
- **1,743 historical rows** are indexed and importable, but their proof bytes
  live in an 11.4 GB archive we do not hold.

---

## 7. The estimate for closing the computation

**7.1 Where the cover stands.**

| | cases |
| --- | ---: |
| cover total | 113,179 |
| closed by the run so far | ~98,000 |
| outstanding in the two large profiles | 20,185 at the last snapshot |
| never attempted (seven small profiles) | 11,585 |
| exclusions needing replacement | 401 |
| historical needing import | 1,743 |

**7.2 Cost per case, measured.** 3.7 CPU-s solving plus 2.9 CPU-s checking at the
first-pass budget; 22.4 s solving at the retry budget; 1.47 MB and 7.4 MB of
certificate respectively.

**7.3 The estimate.** For the two large profiles: ~445 CPU-hours and ~37–40 hours
wall on 12 cores, with ~260 GB of certificates. The wall-clock figure is itself
measured-limited: 12 workers deliver 1.6× the throughput of 4, so the machine is
bandwidth-bound, not core-bound.

**7.4 What the estimate excludes, and why it matters.** The seven small profiles
are not in that number. At the first-pass budget they close at zero; at the retry
budget their rate is unmeasured. Adding them at retry rates would add ~119
CPU-hours, but that figure is a guess where the rest are measurements. **The
honest statement is that the two large profiles are costed and the tail is not.**

---

## 8. What this methodology produced, and what it did not

**Produced:** a kernel-checked reduction (45 modules, `K58.Replay.frozenCover`,
no `sorry`, standard axioms only); a case enumeration verified five ways and
replayed in the kernel; a measured cost model; six defects in the supplied
package with fixes; and the reproducibility observation that reorganised the
evidence design.

**Not produced:** the bound. The reduction is done and the computation is not,
and no amount of formalisation substitutes for the missing refutations.
