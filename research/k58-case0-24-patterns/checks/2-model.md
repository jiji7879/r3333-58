# Independent reviews used for the conditional-clause check

The four-member DeepSeek run `smwzfonp9` audited different aspects of the
package. The coordinator independently replayed every proof, reconstructed the
full case DAG, and wrote the scoped proof. Later, the person explicitly asked
to turn off Ultramath. The remaining run was stopped; there are no active
workers and no pending swarm verdict was invented after shutdown.

## Accepted prior-delta and case-composition report: m1/d4

Report: `.ultramath/smwzfonp9/m1/proof.md`, with
`cover_identity.json`, `deletion_free_gate.json`, `hash_matrix.json` and
`old_word_closures.json`.

The first submission was held for a specific error. It described the inherited
conditional-frontier covers as blocking 8 and 28 words, which confuses them
with the full earlier signature covers. The two actually inherited queries
block 7 and 17 words, exactly the prior OPEN words that this package refutes.
The member corrected the table and, more importantly, the instantiation
of the formal composition argument. Its new receipt reconstructs the two 7/17 queries and explicitly checks
word-for-word equality with the 24 patterns, while separately reconstructing
the distinct 8/28 full signature covers to prove they are not being confused.
Its local composition lemma is then correct:

1. \(P\) fixes exactly one colour on the pivot edge.
2. Full-parent refutations exclude physical pivot colours 1 and 2.
3. The inherited 7/17 covers restrict each remaining pivot/trigger case to
   exactly the corresponding new pattern words.
4. Once those 24 words have been refuted, \(P+T\) is unsatisfiable,
   equivalently the parent entails `-2721 -2766`.

This argument does not require the earlier 12 closed-word proofs or the
unsplit 24-word cover as premises. These are still included and verified in
the archive, but are redundant for the new conditional implication.

The report verifies that this is a strict extension of the old frontier:
exactly the same 24 previously OPEN words recur and only three proof
objects (the two conditional-frontier covers and the unsplit frontier) are
reused from the old package. It does not pretend that all 24 refutations
were replayed by that member; 231 of them are covered by independent replay.

One correction in the report was needed and obtained. After checking the
corrected receipt and comparing the argument to the coordinator's independent
DAG check, m1 was **accepted** through the proper Ultramath verdict.

## Submitted-before-shutdown literal-fidelity report: m3/d3

Report: `.ultramath/smwzfonp9/m3/report.md`; receipts under `work/`.

This member submitted its complete literal-fidelity and strict-replay report
at the time the person requested Ultramath be disabled. I stopped the run as
required and did not issue or simulate a swarm acceptance. Instead, I read
its completed report and directly compared it with the coordinator's
independent results.

Its checks are consistent with those results: same full parent and literal
numbering; at-least/at-most/negative-triangle families present; 236 independent
reconstructed queries and all full proofs read; 69/148 arm alternatives with
correct pivot/word agreement and no pinned-arm contradictions; no active
forced groups or tree nodes; consequence `-2721 -2766` and no broader claim.
Its propagation probes also distinguish non-vacuity from full satisfiability:
there is no propagation-level trigger contradiction, which is not a full-parent
SAT model. Alternative word/layout conventions do not match the archived
query hashes. These facts strengthen the semantic audit but do not change its
scope.

The report is used as an ordinary, checked external reading. It is **not**
described as a formally accepted second swarm solution, since it was stopped
before its verdict could be issued.

## Other directions, not miscounted

The coordinator had separately replayed all 236 obligations (115.724 checker
seconds) and checked every output's complete byte count, one exact status,
no warnings or errors and zero RAT lemmas. It also ran a 2,113-assertion
independent construction of every case and actual strict controls.

The negative-control direction m4 ended without submitting a solution and
remains `abandoned`. Its raw full-replay/negative-control table is consistent
with the coordinator's controls. Some deliberately altered queries still
verify because they become trivially UNSAT through an inconsistent or implied
extra pin. That is not a checker error; it shows why each intended case must be
rebuilt and hash-bound, not merely accepted from a surface status line. Those
raw directions are not counted as accepted independent reports.

The semantic direction m2 had reconstructed all obligations and its finding
matches the independent cover logic. It was stopped without a final submitted
solution and likewise is not counted as an accepted report.

## Net independent-check result

There is one formally accepted independent composition/scope audit, a manually
checked external literal/fidelity reading whose content agrees with the fully
replayed labels, and the coordinator's own full raw replay plus independent
case reconstruction. The absence of further swarm judgements is a consequence
of the explicit stop instruction, not a silent omission or failed proof.

The result remains a **conditional binary clause on one signed parent**. It
does not close unconditional pivot branches, the whole representative, any
other wall representative or the Ramsey bound. It is not a Lean theorem.
