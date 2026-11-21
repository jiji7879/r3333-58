# Paper outline

There is no manuscript yet. This records what a paper would claim, what it can
honestly claim today, and what each section needs.

## What the result is

**Target claim.** `R(3,3,3,3) ≤ 58`, by a formal reduction to 113,179 explicit
unsatisfiable formulas, in the shape of Tatarevic's `R ≤ 60`.

**What can be claimed today.** Not that. The reduction is complete and
kernel-checked; the computation is not. Concretely:

| component | state |
| --- | --- |
| the reduction, in Lean | complete: 45 modules, `K58.Replay.frozenCover` proved, no `sorry`, axioms ⊆ `[propext, Classical.choice, Quot.sound]` |
| every case realises a frozen formula's units | proved |
| units ⇒ the emitted CNF | one piece proved (`satisfiable_atLeast`), the assembly and the hash binding open |
| the 113,179 formulas are unsatisfiable | **incomplete**: ~20,000 in the two large profiles, 11,585 in seven small profiles never attempted, 401 exclusions unresolved, 1,743 historical proofs unimported |

So the paper is not blocked on mathematics. It is blocked on compute, plus one
formal layer.

## Possible papers, in order of what the evidence supports

**A — the method and the formal development.** "A formal reduction for the
four-colour triangle Ramsey bound at 58, with a partially discharged
computational premise." Defensible today: the Lean development stands on its
own, the audit results are real, the reproducibility result (certificates
bit-reproducible 10/10) is a genuine contribution. The honest weakness is that
it advances no bound.

**B — the full bound.** Needs the cover closed: all 113,179 cases, the 401
exclusions replaced, `AllUnsat` discharged, and the encoding layer finished.
Months of compute on a machine with ~300 GB, plus the remaining Lean.

**C — the audit and reproducibility methodology.** The eight-direction audit,
the six defects found in a supplied proof package, the bit-reproducibility
measurement, and the cost model. Publishable as tooling/experience, and useful
to anyone attempting a similar certified enumeration.

## Section plan for (A)

1. Introduction — the Ramsey problem, why 58, what a certified enumeration has
   to consist of.
2. The reduction: degrees, profiles, tickets, the plan, the marked case, the
   cover. Follow `PROOF_PLAN.md` and the review's §3, written for a reader
   rather than as a record.
3. The formal development: classification at 15 and 16 (ported catalogue with
   55 kernel-checked LRAT pairs), the marking lemma, the transport replay
   (1,764 families, 190,736 placements, 77,557 transports). State what is
   proved and what remains.
4. Encoding adequacy: why a unit-level theorem is not enough, PySAT's at-least
   encoding identified as the staggered counter (`verify_atleast_encoding.py`),
   `satisfiable_atLeast`, and what the assembly still needs.
5. The computation: measured cost, measured closure rates, what is done and
   what is not. This section has to be honest about the gap or the paper is not
   publishable.
6. Reproducibility: pinned toolchain, bit-reproducible certificates, the
   manifest design, the defects found in the supplied package.
7. Formal statement and computational boundary: the theorem as a Lean
   declaration with `AllUnsat` as its premise.

## What must be written before any of this

* A single narrative statement of the reduction. Today it exists as a proof
  plan, a review, and 45 Lean modules; nobody has written it as prose for a
  referee.
* Literature positioning: Chung's lower bound, Fettes–Kramer–Radziszowski's 62,
  Tatarevic's 60 (unrefereed), and what is new here.
* A decision on which claim to make. (A) can be written now; (B) cannot.
