# K58 case 0 verification

## Verdict

The attachment's stated **scoped mathematical result checks out**. For physical
edge $(31,42)$, colors 1 and 2 are refuted. The third certificate proves that
**every model of the signed parent uses physical color 0 or color 3**. Both
remaining branches and the parent remain `OPEN_UNKNOWN`.

This is not a claim that branch 0 or branch 3 has a full K58 model. It is not a
single-survivor refinement, deletion of representative 0, a wall-row closure,
or a Ramsey-bound result.

## Exact child and cover claims

Let $P$ be the attached parent CNF. Its four physical pivot literals for colors
$0,1,2,3$ are $5249,5250,5251,5252$. The independently replayed native proofs
establish that $P\land5250$ and $P\land5251$ are UNSAT. The cover query is
$P\land
eg5249\land
eg5252$, which is also UNSAT. Hence

$$P\vdash (5249\lor5252).$$

Thus a complete parent model must use color 0 or color 3. The host's
at-least-one and pairwise at-most-one clauses make the two retained child queries
an exact, disjoint partition of parent models. Keeping both therefore loses no
parent model; it does not say that either query is satisfiable.

The third certificate is an implication about complete models, not a witness
for either model. With two unresolved children, the queue cannot reduce this
node to one continuation: retain the parent or represent both unresolved
branches subject to free slots (one additional slot if expanded).
Likewise, `cover.status: CLOSED` is an obligation/check status, not evidence
that the parent itself is closed. The hypothetical expansion by one slot is
not an actual queue mutation: the frozen count remains 983,774.

The three native replay receipts match these exact queries and proof files:

| Claim | Query SHA-256 | RUP additions checked in the LRAT path |
|---|---|---:|
| color 1 | `84ba8a7e6bb372c0d5e6c4485bee7e47c8ca5081277f4f8d8beabbe0d1fee33f` | 36 |
| color 2 | `858216a74117455646e51880ca1392e957da8800ccb95f5189870d67007ad83c` | 1 |
| cover | `30163e3ddaefb8241137b19bcdceafc7d1c9facfb85f0c76a239d53c71923a70` | 35 |

The supplied LRAT implementation uses explicit `require` exceptions and passed.
Its optional native wrapper suppresses warnings with `-i -w -U`; that path was
not used as the acceptance criterion. `tools/refinement/verify_case0.py`
replaces it with `-i -U -t 300`, exactly one success line, exit status zero,
and zero warnings. All three archived RUP proofs pass under that policy.

## Frozen-source regeneration

Using the audited initialized campaign in `.scratch/review-attachments-v1/audited-K58`,
the coordinator regenerated a byte-identical parent from index 0, without a
fresh solver call. The row is
`00032f347903758c89e2187f30f0e1c07aecb21bd27c149fb43aef0ccdb60f0d`, with:

- revised owner rank 0 and pair `00000/01022`;
- arm size 14, palette `[1,0,3]`, missing color 2;
- the same pentagon, nominated vertices, profile and recipe archive digest;
- ordinary row SHA-256
  `160f9fb6c60638443c50d79e4fcaa64e6cdb6460db32fc61406d269a938bec00`;
- representative/parent SHA-256
  `ae90931dc6cd482105153dd720209e602bbfc7cc0915e18c6e87023ee2659931`.

The strengthened search query has the different digest
`d69970e19ddadfad5057ffaf8ffbd1354f957a4003852dc2b6b8aeff63cb3004`.
The attached parent is therefore the base representative, not that
strengthened query. The verification does not conflate their assumptions.

The color-1 record also has a historical `search_query` field. The attachment
does not include enough material to identify that query's construction, and it
must not be identified with the current strengthened parent plus the pin. Its
archived role is not used for the exact physical proof queries reconstructed
and checked here.

The supplied `parent.cnf.gz` has 19,218 variables and 178,823 clauses. Its
exact bytes regenerate from the frozen row and revised owner circuit. The
attachment ZIP's SHA-256 is
`f08ec771eaf99c31d22cbe4d364ccd0ca80365f41a1395e1a152d067aabcf192`.

## Negative controls and provenance bounds

- A real empty-clause RUP proof against the wrong child query is rejected.
- Removing the final derived empty clause from the LRAT proof is rejected with
  `Proof did not derive the empty clause`.
- No new K58 search was launched; timestamps and conflict counters in the event
  are retained metadata, not fresh runtime measurements.

The computed `event.head` matches its hard-coded expected hash and records the
reported event-chain contents. It is a record-integrity commitment, not proof
of producer identity, event ordering beyond the supplied record, original
binary execution, or publication times. The supplied `PREDECESSOR` value alone
does not independently authenticate a longer history.

The `OPEN_UNKNOWN` status is also retained in metadata; no later search here
re-decides it. Nevertheless nothing in the artifact supplies a refutation or
model for the parent, and its recorded live count is the familiar 983,774.

## Independent review

All three swarm directions are accepted. `independent/proof-replay.md` checks all
strict native proofs and discriminating corruption controls;
`independent/formula-semantics.md` independently derives the pivot, exact
queries, guard and two-open queue partition; and
`independent/parent-regeneration.md` reproduces the parent from both pristine
recipe source/data and the audited initialized tree. Their machine receipts
and an actual semantic replay are in the same folder.

## Files

- `supplied-verify.log`: the three standalone LRAT passes and exact reported
  pivot, exclusions, unresolved branches and parent status.
- `strict-verify.log`, `native-receipts.json` and `native/`: strict native
  output and query/proof identities.
- `source-binding.json`: the full row, owner, palette, mapping and recipe
  binding.
- `controls/`: wrong-query and truncated-LRAT rejection evidence.
- `summary.json`: machine-readable outcome and scope.

External independent reviews under swarm `smwyronzn` are included separately
when judged; they do not expand the scope of this case-level result.
