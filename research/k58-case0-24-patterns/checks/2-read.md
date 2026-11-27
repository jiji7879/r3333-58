# Reading check of the supplied 24-pattern certificate

I compared the [verbatim README](claim.md) with the physical artifacts and the
recorded case-cover semantics, independently of the conclusion printed by
`replay.py`. The result is a finite proof of the stated implication. No
stronger Ramsey, branch or model claim is either asserted or supported.

## Objects and signs

The parent hash matches `frontier.json.parent` and `event.parent.query`, and
is byte-identical to the previously audited parent. The signed CNF is
reconstructed, not inferred from gzip or manifest hashes. The physical edge
variable rule was independently regenerated. The trigger variables are 2721
for colour 0 on `(31,13)` and 2766 for colour 1 on `(42,13)`. The exported
negative two-literal clause therefore excludes exactly their conjunction; it
does not forbid reverse roles or either colour assumption alone.

The parent contains the physical exactly-one-colour clauses, including the
pivot clause and its pairwise exclusions, and the full negative triangle
families. This is what makes a complete four-way pivot listing exhaustive.

## Every case in the argument

- The two eliminated pivot colours are exactly 1 and 2. Both query formulas
  and proof digests match event children, not just a status string. The
  original pivot 0 and 3 records are `OPEN_UNKNOWN`; no full branch model or
  refutation is fabricated.
- Each of those two remaining pivots has a previous full-parent cover over
  its exact previous OPEN words. Newly recorded pattern words match these two
  sets explicitly. The proof bytes of both predecessor cover certificates
  also match the respective archived predecessor bytes.
- For each word, the same physical pivot, trigger and four signature literals
  are used in the direct query and in the arm-cover query. An arm is the
  complete 14-vertex K14 on 31–44: 91 positive colour literals make an
  explicit complete assignment. Blocking all them by negative 91-literal
  clauses leaves only the 217 listed alternatives under the appropriate
  parent hypotheses. These choices partition the case; they are not
  statistical samples or incompletely pinned local templates.
- Four words have direct full-parent refutations. In the other 20, every
  arm alternative has an independently named CLOSED proof on the full parent
  with its exact arm units. No unresolved subtree or group is retained by
  this input: all active `forced_groups` and split paths are absent/empty.
  Code that would handle more general splits is not evidence for those
  generic cases, but it does not produce an omitted case here.
- The case combination is ordinary propositional logic: previous pivot and
  word covers give exhaustive disjunctions, the new arm-cover gives an
  exhaustive disjunction within each word, and every resulting branch is
  refuted. Hence parent plus the trigger is unsatisfiable, equivalently
  `-2721 -2766` is entailed on that parent.

A proof on the full signed formula, rather than on `branch-h` with its extra
owner units, is crucial. The reconstructed terminal queries append only the
specified pivot/trigger/word and arm units; they contain no hidden extra
branch literals. Owner auxiliaries remain in the parent, so no relevant
clause is projected away.

## Scope, status labels, and overclaims

The earlier 12 search/unsplit proofs do not make the other 24 automatically
closed. The new certificate contributes a complete arm subdivision and
refutation of those 24. Conversely, the new discussion does not certify the
old statement that 11 live owner two-site consequences generalise across
owners or wall rows; it addresses only its own parent and two triggers.

`CLOSED_DIRECT` and `CLOSED` do not establish anything by being typed in JSON.
Every associated query and all 236 distinct proof files pass strict replay.
`OPEN`/`OPEN_UNKNOWN` in historical children stays OPEN, not SAT or UNSAT.
The 217 arm strings are assignments used by exhaustive covers, not claimed
K58 models.

Both pivots are closed only *under the trigger conjunction*. This is not full
representative exclusion: if it were, the assumption that every edge needs a
colour would incorrectly transform a conditional binary clause into an
unconditional unsatisfiability proof. The document deliberately makes no
Ramsey-bound assertion and no production transition.

Finally, using the package verifier in its stock `-w` substring mode is not
an adequate validation condition. It is the checker interpretation, not the
mathematical case analysis, that must be hardened. All actual calls pass when
warning suppression is removed; there is no warning-bearing certificate hidden
among the accepted ones.
