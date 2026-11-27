# Scoped audit of `K58_reusable_spoke_rules.zip`

## Outcome

The supplied package passes its native proof obligations under a stricter
warning-free replay gate. The independently reconstructed query/proof receipt
set matches all **91 native calls**, each with the whole proof stream consumed,
one exact `s VERIFIED`, no warnings/errors, and no RAT lemmas in core.

The substantive representative-0 result is **20 further direct exclusions on
its signed parent**. They remove 20 of the 345 exhaustively covered pivot-3
arm assignments. This is partial progress, **not a representative, branch,
row or Ramsey closure**. No full K58 model was obtained.

This report deliberately keeps the stronger 53-transfer claim, the 9,288-row
geometric catalogue and the representative-0 cubes separate. They use
different support and must not be grouped as “9,341 globally solved cases”.

The ZIP hash is
`2a22f91d881ae39ac99bcd3a8d44e8fd55783f00b0255df44088f57970af6108`.
All 150 manifest entries pass over 151 files (including the manifest). No new
SAT/SLS search or production mutation was performed. Independent-model review
through Ultramath was skipped as explicitly requested.

## 1. What the 53 transferred clauses actually prove

The donor core at owner 36 has 26 instances and the donor core at owner 40 has
27 instances, **including the two donors themselves**. The 53 records span
**27 distinct wall rows**, not 53 rows.

For each recipient, the audit reconstructs its signed formula from the
byte-prefix/suffix data, checks its recorded SHA-256, reconstructs the
vertex/colour/auxiliary-variable mapping and rewrites the donor proof binary.
It then verifies that:

- the vertex map is an injection and the four colours are a permutation;
- the two renamed antecedent literals equal the record's physical pins;
- those pins mean exactly the two named colours on the two named edges;
- the recipient signer/cube belongs to the stated owner pair in the frozen
  983,774-member revised-owner roster;
- the transformed proof hashes and full recipient formula-plus-two-unit query
  hashes match the supplied records.

Strict native replay then confirms the formula under the two assumptions is
contradictory. It proves the corresponding disjunction of their negations
**on that recipient's signed parent**, which is the clause whose hash and
parent identity are written in `proof-transfers.tsv`. It does not close that
signed representative, let alone the ordinary row or all faces of the palette.

The proof is not accepted merely because a map passes an injection test. The
actual transformed proof must verify on the actual reconstructed recipient and
those exact assumptions. A different map need not work, and the supplied
search is only a sufficient-condition search: further embeddings are possible,
so this is not an exhaustive enumeration of all reusable instances.

## 2. The geometry catalogue, with its correct proof strength

The catalogue contains **9,288 distinct `(representative, negative-literal-pair)`
entries**, on **6,617 representatives and 6,489 wall rows**. The path and owner
metadata are rebuilt deterministically from the frozen physical-bindings and
queue data rather than taken as an arbitrary export.

For a row, let \(u\) be pentagon site 0, \(a\) site 4, and \(v\) the appropriate
arm vertex (zero-based site \(n-3\)). With the checked palette convention, ua
has colour \(\alpha\), while the canonical local proof forces av to colour
\(\beta\) (local palette colour 0). For a selected outside vertex \(x\), the
binary clause is

$$
\neg(xu=\alpha)\ \lor\ \neg(xv=\beta).
$$

Behind it is a literal four-colour triangle argument. Every colour of \(xa\)
creates a monochromatic triangle under the two antecedents:

| possible colour of \(xa\) | contradiction used |
| --- | --- |
| \(\alpha\) | \(xua\), using the antecedent \(xu=\alpha\) and fixed \(ua=\alpha\) |
| \(\beta\) | \(xva\), using the antecedent \(xv=\beta\) and the canonical fact \(av=\beta\) |
| \(\delta\) | \(xya\), with both \(\delta\) path edges \(xy,ya\) checked in the frozen source units |
| \(\gamma\) | \(xwa\), with both \(\gamma\) path edges \(xw,wa\) checked there |

The six distinct vertices are checked, so these really are nondegenerate
triangles. The original four physical colours exhaust the possible colours of
the edge. The required \(u,v,a,x,y,w\), palette and source-unit relationships
are checked individually for the exported placements.

The six local canonical `a–v` forced-edge obligations are themselves replayed
against their provided base CNFs. The older arm-domain exclusion of local
colours 1 and 2 on that edge is checked against the matching frozen records.
The **eight full physical proofs** cover all six owner classes attested by
`canonical/rules.json`. This connects the mathematical placement argument to
the supplied physical encodings, rather than relying on palette words alone.

**Important limitation:** the catalogue has 9,288 checked mathematical
placements, not a new independently replayed K58 proof for each entry. Exactly
six canonical and eight physical examples are directly replayed for this family.
This proof audit does not reprove the entire upstream arm-classification or
turn the catalogue into a universal transfer to arbitrary owners. Each valid
clause remains scoped by the given physical representatives and frozen source
geometry.

The first example on representative 38 gives `x=13`, `u=31`, `a=34`, `v=42`,
`alpha=0`, `beta=1`, with two distinct intermediates 15 and 10 for the other
colours. It yields `-2721 -2766`, matching the separately audited spoke-clause
shape, and is not evidence that unrelated edge pairs share the same rule.

## 3. Direct representative-0 exclusions and the remaining front

The 20 final exclusions in `case0/exclusions.json` reconstruct as signed
parent plus only their listed arm units. There are no hidden trigger units in
these final proof queries, and `pure_query` is not substituted for the final
query. Their actual cube-size distribution is:

| pins per cube | number |
| --- | ---: |
| 13 | 1 |
| 14 | 4 |
| 15 | 3 |
| 16 | 1 |
| 82 | 11 |

Thus eleven use the documented 82 pins and nine use 13–16 pins. All twenty
are direct full-parent proofs, so a previous two-spoke lemma used during
their discovery is not silently required as an extra assumption of the final
export. The clause export recreates exactly these negative pin sets under
`p cnf 19218 20`.

Both arm-cover queries exclude all listed complete K14 assignments on the full
signed parent and hence exhaust the relevant arm possibilities. All model
strings have 91 physical edge colours, respect the nominated pivot and contain
no monochromatic triangle. Independently recomputing the subset matching and
word groups gives:

| branch | exhaustive arm assignments | excluded by the 20 cubes | surviving OPEN | surviving old word groups |
| --- | ---: | ---: | ---: | ---: |
| pivot 0 | 1417 | 0 | **1417** | 57 |
| pivot 3 | 345 | 20 | **325** | 36 |

Both prior unguarded word-group sets match the surviving sets exactly, including
pivot 3's claimed 36 four-edge signatures. These surviving arms are not full
K58 models. The two surviving pivot colours are also not thereby ruled out;
the supplied strengthened three-second searches remain OPEN, including the
unpivoted parent control. Pivot colours 1 and 2 remain excluded by the older
proofs replayed here.

## 4. Native replay and two controls

The direct and reconstructed obligations sum to:

| kind | calls |
| --- | ---: |
| canonical forced edges | 6 |
| full physical geometry examples | 8 |
| transported two-spoke exclusions | 53 |
| pivot-colour-1/2 eliminations | 2 |
| case-0 arm covers | 2 |
| case-0 direct exclusions | 20 |
| **total** | **91** |

The complete supplied run took **48.665 s checker time**. Its output is:

```text
Verified ownership and path witnesses for 9288 clauses on 6617 representatives.
Replayed six arm proofs, eight full examples, and 53 transferred proofs on full signed formulas.
Case 0, pivot 0 arm colorings 1417 excluded 0 open 1417
Case 0, pivot 3 arm colorings 345 excluded 20 open 325
All checks passed.
```

The independent gate requires return code 0, one exact `s VERIFIED`, zero
warnings/errors, `0 RAT lemmas in core`, and a reported read count equal to
the complete proof-stream length. This includes **all 91**, not just samples.
The stock `-w`/warning-suppressing acceptance is not used as evidence.

Additionally, a deliberately satisfiable pin-units-only formula rejects a
genuine physical example proof with return code 1 and no verified line. The
same genuine proof truncated halfway also rejects, with return code 1. These
are controls on refutation checking, not new solver statements or claims about
how every conceivable mutated query should behave. An erroneous extra pin can
make a query trivially contradictory while technically verifying; for this
reason the intended queries are independently reconstructed and hashed first.

See [the independent replay receipt](checks/2-compute.json), [reproduction
commands](checks/2-compute.md) and [controls](checks/negative-controls.json).

## 5. What was not established

- No unconditional spoke theorem on all owners or all wall rows. The 53 clauses
  are attached to their named signed parents, while the geometry placements
  use specified frozen family/owner relations.
- No full K58 SAT or UNSAT result, representative-0 closure, new production
  row closure, or new bound on the Ramsey number.
- No exhaustive 9,288-full-parent proof sweep; it is a checked geometric
  derivation supported by the six arm proofs and eight physical examples, not
  that many completed native case refutations.
- No conclusion of a solver speedup from the matched controls: representative
  36 still times out at 3 seconds while the three other cited controls return
  UNSAT. Those timings are empirical only and independent transfer proofs carry
  the logical content.
- No proof that the delivered lists exhaust every possible embedding or every
  reusable spoke rule. The map search was sufficient, not complete.

Most importantly for the preceding case-0 checkpoint, the new twenty cubes
**retain 325 pivot-3 arms and all 36 four-edge signatures**. They must not be
misread as closing the physical pivot branch that had 345 candidates.
