# Independent audit: supplied pentagon certificate for the 0404 reciprocal root

Date: 2026-11-25.

## Verdict

**The supplied certificate closes the augmented reciprocal/common-pair root of row
`0404c3a224626a202cbfa4355bb0b19513ec815d182050440c580208861f2296`.**
Consequently it closes every cube in the existing C&C tree, including the four leaves
that had remained open (`n017`, `n022`, `n024`, `n025`), not merely the supplied
`n025`/`n026`/`n027` continuation.

It eliminates the reciprocal branch of this one frozen row, subject to the already
checked row-to-CNF and template scope of the campaign. It does **not** close the
strict, mixed, or balanced-nonreciprocal branches, does **not** close the frozen row,
and does **not** reduce the profile OPEN count or prove `R(3,3,3,3) <= 58`.

## Independently executed checks

- Source archive: `attachments/let-s-try-and-rbdv/K58_n025_pentagon_certificate.zip`,
  SHA-256 `325981b645164cad7521b4a21a457f926c3f949c38835e1409ce10667e2e1467`.
- Every entry in its `SHA256SUMS` passed after extraction to
  `.scratch/attachment-audit/n025/`.
- The engine bundle's `SHA256SUMS` passed.
- Ran the supplied standard-library verifier against the exact original engine inputs.
  It rebuilt all seven forbidden pentagon formulas, the at-most-14 counter comparison,
  all four strengthened inputs, and the ordinary-row prefix.
- **Full run: 24.75 s; every proof returned `s VERIFIED`.** Complete output:
  `supplied-verifier-replay.log`.

The exact source hashes rechecked were:

| Input | SHA-256 | Strengthened-input SHA-256 |
|---|---|---|
| root | `aa23de814810dc2b5515955a0aa318eab72df81c4541006fde253b39c48d2b44` | `a9bb080f20e3f8ba0ce34a0b73da5cf8b2f8e2ef41cecc1d51a5e1c417e804a2` |
| n025 | `eb19101a3def5e5769d2b12977b34742e3c32b1d97219fd8327b5a081030669a` | `89eda3d123166724878583a8fbf462f55cab7ada1c14ffbf809939d89d7ab2ab` |
| n026 | `d57c75469fed06d21452c7552ff8c603142ec425c09fc21ecbb818c83a341ff6` | `e9dbfca16cd931265615af2f56a1030ce1964d9899cd1d51640fe4feb75fb980` |
| n027 | `acd96e2ff90ee47afeb82edd385968a3e902244ac8d4b7de7e2f351c3dc2a255` | `b5d2950276aef3c9a21ab2ca8590c84c38ab1b507a08aed8f51e9818b92cc075` |

The common core DRAT has SHA-256
`800fe2a73cb9590c05e692cc5c78838070c67ec1de7a18b4787f237418e8fdb1`.
The independent Kissat and CaDiCaL proofs on strengthened `n025` also replayed as
`s VERIFIED` (proof hashes `c2e526d88b…` and `4a24c9cc26…` respectively).

A separate parsing check confirmed:
- root arms have 16/16/13/12 vertices;
- all nine degree guards are positive unit clauses in each exact input;
- `n025` adds exactly the six literals recorded in the continuation;
- `n026` and `n027` add the same base cube with opposite signs of `305483`;
- no original root unit is lost in any child.

## Why the compositional proof is used

The final core proof is not incorrectly treated as a proof on the uncut root. The 94
added clauses are first justified by the separately replayed finite pentagon lemma.
For each supplied attachment, the verifier checks the physical centre/pentagon/neighbour
edges, all pentagon pin colours, the missing colour, and every exported clause. The
counter proof and source guard/counter clauses establish that the nine listed degrees
are at least 15. The core DRAT is checked only after this composition.

The ordinary frozen-row prefix also has the independently confirmed SHA-256
`a062b827b34fa73ccd610b2a932e007e48ba217d85c7dea00f9a1a73dbdb62fe`.
Its certified consequence is a disjunction: at least one of the nine listed
vertex-colour pairs has degree at most 14. The reciprocal/common-pair root asserts the
opposite at all nine, hence is UNSAT. This is a necessary condition on ordinary-row
extensions, not an ordinary-row refutation.

## Scope and ancestry check

`results/cc-reciprocal-0404-2026-11-25/root.json` binds the root to:
1. parent `b07fed49d2898b07a141d6dd55e5be1adfeb66b70dd32c17768de5c55cdc7691`,
   the frozen parent plus reciprocal and proved common-pair constraints;
2. `.ultramath/smwvx4uzm/m6/ReciprocalTwo16.lean`, which proves reciprocity exactly
   equivalent to the common critical pair `{0,1}` at this root; and
3. 64,416 certified mixed cap-8 clauses, with fresh selectors above the parent maximum.

The root therefore contains only established consequences of the reciprocal branch.
Since the root itself is proved UNSAT, continuing the old C&C tree is unnecessary.
Its historical proofs remain useful but no longer define the residual frontier.

The 57-flag inactive formula is **not** refuted by this certificate. A direct map check
showed that the nine pairs use different colour/vertex combinations from the inactive
root-incidence flags. No active/inactive conclusion is imported without a new proof.

## Reproduction

```sh
cd .scratch/attachment-audit/n025/K58_n025_pentagon_certificate
python3 verify.py /workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/package-final-test/k58-cc-engines
```

For portability, replace the absolute engine path with the unpacked engine bundle.
The verifier does `-i` because the supplied traces are binary DRAT, not to weaken the
outer refutation check. Each log contains `s VERIFIED` and a detected empty clause.
