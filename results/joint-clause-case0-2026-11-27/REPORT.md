# Case 0: clause learning from joint second-arm constraints

## Result

The joint pattern found on case 0 can be expressed as a **branch-corrected
pruning clause**, and the same candidate is established on three additional
second-arm positions.

For the original physical pivot $u=31,v=42$ and $w_1=1$, consider

$$C(w_2):=\neg E_{31,w_1,2}\ \lor\ \neg E_{42,w_1,1}\ \lor\ \neg E_{42,w_2,1}.$$

For **each exact pivot branch**, the following target clauses were established:

| Branch | Physical pivot colour | $w_2$ values for which $C(w_2)$ is established |
| --- | ---: | --- |
| local 1 | 0 | $2,9,11,13$ |
| local 2 | 3 | $2,9,11,13$ |

Thus there are **eight branch-correct clauses in total**. They were checked
against 14 choices of $w_2$, in each branch, covering all remaining second-arm
vertices 2–15. The other **20 branch/pair hypotheses remained UNKNOWN at one
second per query** and are not in the learned bank. This is a scoped result, not
a proof that all similar pairs obey the same rule.

## Clause semantics and proof

The relevant fact is not a three-second timeout or the solver's word. For each
candidate clause $C=[-l_1,-l_2,-l_3]$, I formed its negation by placing positive
units $l_1,l_2,l_3$ (each in its own clause) on the exact full case-0 branch.
UNSAT of that formula proves

$$P\models (-l_1)\lor(-l_2)\lor(-l_3)=C.$$

Every one of the eight negation queries produced a native UNSAT trace, checked
with binary RUP flags `-i -U -t 300`, zero warnings, exit code 0, and exactly
one `s VERIFIED` line. Their native search statistics have zero conflicts.
This is not a claimed one-line RUP prefix for $C$ and not a Wave A transfer
certificate. The formal-entailment interpretation is precisely the proof that
the exact full branch plus $C$'s falsifying assignment is impossible.

The two original parent identities are:

- physical colour 0:
  `f7e6f5b2cb5a95bf65c16c730f7c4e10bd359b3d413d031bcbf9dd180dd5ff8d`;
- physical colour 3:
  `e85234ab42705601f1b83a2e6127ecb89dea669ba78865f35ea57e47815ece7a`.

All eight final proofs were replayed again independently. The separate
[clause audit](clause-audit.json) reconstructs the goal literal using the
physical edges, strips the three negating units back to the original parent,
and checks both query and proof identities. Parent/conditional structure is
part of every certificate; these must not be lifted onto a different pivot,
parent or unexamined branch.

## Using the clauses on the exact branches

I added the four proved target clauses to each corresponding exact branch,
producing:

| branch | strengthened full-query SHA-256 | result |
| --- | --- | --- |
| 0 | `1c8ea2ba60dcacc2e6d2e3dddc028790e844592e90e5f097293206698cd467d0` | OPEN at 3 seconds |
| 3 | `8555945565d41680e1eb8bdf069ffad20c0b82706131809d28da8349041a4b91` | OPEN at 3 seconds |

Native search took 3.001955 s and 3.002071 s respectively. There was no SAT
model, no branch refutation and no new certificate for the strengthened branch
itself. The augmented queries are **not** presented as faster, and neither color
is eliminated or now shown feasible at all 58 vertices. Production SQL ledgers
were not modified and production sweeping remains paused.

## Why this generalization is informative but limited

The original $w_2=2$ incompatibility was therefore not an isolated single pair,
but the same pattern could be certified at $w_2=9,11,13$ as well, consistently
in both surviving pivot colors. Nevertheless, a **UNKNOWN on another location is
not a countermodel of that location's clause**. It is simply no clause learned
under this budget. Likewise, certified clauses for $w_1=1$ cannot promote
different first vertices, different case indices or whole wall profiles without
their own proof.

The physical Wave A JSON/source maps and original replay digests were not
available. They were not substituted for the present certificate. Nothing here
changes the Ramsey bound, the 11,585 wall-row statuses or the production cover.

## Evidence and replay

The accompanying archive
[k58-joint-clause-evidence.zip](k58-joint-clause-evidence.zip)
is supplied in chat and is not committed to Git. It contains:

- each exact branch CNF and its exact positive negating units;
- all eight normalized native proofs and the corrected literal manifests;
- the two correctly compounded strengthened query CNFs;
- the bounded UNKNOWN ledger for the other 20 candidates;
- the learner and an archive-native verifier (`verify_clause_bank.py`),
  with `drat-trim` source and executable.

After extracting the archive:

```sh
python3 verify_clause_bank.py
```

For another platform, first compile:

```sh
cc -std=c99 -D_GNU_SOURCE -O2 tools/drat-trim.c -o tools/drat-trim
```

The verifier says nothing about global Ramsey truth: it establishes eight
branch-correct implications and preserves the two UNKNOWN strengthened statuses.
The original experiment and raw proof assets are under the project’s
`.scratch` directory; source, compact receipts and this report are committed.
