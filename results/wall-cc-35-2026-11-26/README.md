# K58 cube-and-conquer for all 35 selected wall rows

**Final outcome: 35 declared depth-two plans / 140 attempted cubes / one
independently verified UNSAT leaf / 139 OPEN leaves. No whole row is closed.**

This is a completed bounded C&C campaign, not a whole-row or profile proof and
not a proof of $R(3,3,3,3)\le58$. Every selected row retains at least one
unresolved cube. The board ended with six finite reports accepted after artifact
checks; its state does not mean the Ramsey problem was solved.

## What was actually done

The selected rows are the same 35 from the previous direct-depth-zero pilot:
five rows in each of the seven profiles, chosen by ascending
`SHA256('wall5x300-v1|' + profile + '|' + full_row_id)`, with the profile
written in comma-separated form without parentheses or spaces. Full 64-hex IDs
and all per-profile splits are in `frontier.rows.tsv`; every leaf is in
`frontier.cubes.tsv`.

Each row used:

- original first-tier parent: `tables=True,total_critical=True,full_root=False`;
- declared `--depth 2 --arm-pair auto --arm-mode both`;
- up to four explicitly signed leaves, with the actual split nodes saved;
- `shared_conquer.py --no-reuse` in a new directory,
  350,000 conflicts per cube, 1,000 tail conflicts, 300 search seconds;
- fresh eager CaDiCaL leaf workers on the same plan,
  **300 seconds or 1,000,000 conflicts per leaf**, check limit 600 seconds;
- strict `wallcc.py verify` with the explicit original parent SHA-256.

The native conflict counter may slightly overshoot a cap (up to 1,000,006 here):
those records remained OPEN. There is no claim of unlimited search. All 35
shared passes ended OPEN at conflict limits; no shared pass hit its wall clock.
There were no reused certified cores, perfect-balance assumptions, unverified
H-rise clauses, blanket degree caps, historical lex inputs or parent exports.

The m2 physical audit checked every original parent for the full K58 host:
1,653 exact-one-colour clauses, six pairwise exclusions per edge, and four
monochromatic-triangle-forbidding clauses for every one of 30,856 unordered
vertex triples. That is 134,995 required physical clauses in every parent, with
zero missing (see `physical-parent-audit.json`). Hence these are whole K58
parents, not local three-arm or otherwise relaxed encodings.

## Result by profile

| profile | plans | leaf attempts | independently certified UNSAT | OPEN |
| --- | ---: | ---: | ---: | --- |
| `15,14,14,14` | 5 | 20 | 0 | 20 |
| `15,15,14,13` | 5 | 20 | **1** | 19 |
| `16,14,14,13` | 5 | 20 | 0 | 20 |
| `16,15,13,13` | 5 | 20 | 0 | 20 |
| `16,15,14,12` | 5 | 20 | 0 | 20 |
| `16,16,13,12` | 5 | 20 | 0 | 20 |
| `16,16,14,11` | 5 | 20 | 0 | 20 |

A certified cube is meaningful progress on its parent. It is **not** membership
in a verified complete cover. Five rows per profile do not eliminate a profile.
Conflict/time-limited OPEN records are not countermodels or UNSAT proofs.

## The sole certified leaf

| binding | value |
| --- | --- |
| full row ID | `3d443146013949bb1f01e907953c366c617e4178c4638cc2c8eb59d4e2745d1c` |
| profile / branch | `15,15,14,13` / 1347 |
| original parent SHA-256 | `d27d34c0d8336997d545c76120e040ff1aa0f448ef362d443502372d4c1a1ff2` |
| declared splits | `r=4262`, `r0=5104`, `r1=4645` |
| certified node / exact cube | `r11` / `[4262, 4645]` |
| retained ordinary binary leaf DRAT | 6,707 bytes |
| leaf DRAT SHA-256 | `1e605f06553a1152d358bccf16f49dcb7a4102da7ccb9d3adade9a2f662d3007` |
| matching CAS SHA-256 | `036ec2b03282f64d5ccdc1336210ef9b4f565c07abbc04138971ad340a08a95f` |
| ordinary replay | both independent binaries returned code 0 and `s VERIFIED` |

The coordinator rebuilt the exact original-parent-plus-unit-cube formula (no
other clauses or changed auxiliaries), joined the matching CAS prefix and leaf
proof, and ran ordinary plain `drat-trim -i -p` twice:

1. the supplied driver's checker, SHA
   `a9571deb08430a3d7f7a72074440f53e2ad48196dced50b146835052a18e9066`;
2. a separately compiled checker, SHA
   `dc0fb03ed4a924d9721545baa215941d336d296719796f05747970ee63aac6de`.

The `-p` option is plain mode (ignore deletion metadata), not IDRUP or a
promise that an incomplete prefix proves a parent. The checker detects UNSAT by
unit propagation on the exact leaf. In the primary replay its core had 39 of
173,819 input clauses and 1 lemma/39 resolution steps, with 0 RAT lemmas.

The artifacts in `certified-leaf-3d443146-r11/` are the exact checked inputs,
input hashes and outputs, including:

- `original-parent.cnf`: original first-tier parent;
- `leaf.cnf`: original parent plus exactly `4262 0` and `4645 0`;
- `joined.drat`: the matching 214,311-byte CAS-plus-leaf proof;
- `receipt.json`: parent/cube/proof hashes and replay results;
- `driver-plain-replay.log` and `independent-plain-replay.log`: raw checker output.

**Control:** `wrong-r10.cnf` substitutes the other branch's literal `-4645`.
The same joined proof returns code 1 and `s NOT VERIFIED`, with raw log
`wrong-r10-control.log`. The uncertified sibling cubes are
`[-4262,-5104]`, `[-4262,5104]`, and `[4262,-4645]`. These three remain
OPEN, so `3d443146…` has no complete cover and cannot be reported as closed.
The shared incremental pass's internal `result=false` on this cube was kept
strictly separate from this later fresh ordinary leaf certificate.

## Independent assessment

All six roles, not just their own producers, were checked. Coordinator and m6
static audits independently reconstructed all parents and all four cubes per
plan. There were 35 distinct parent and plan hashes and no duplicate canonical
row directories. Original parent clauses were checked before direct solver and
verifier invocations. One wrong cube control and the source artifacts returned
by two separate checker binaries were validated, not inferred from receipt text.

`wallcc.py verify` was also independently rerun against all 35 original parents
(check limit 600). Its aggregate was `OPEN:139, VERIFIED_UNSAT:1`, so no parent
was eligible for parent-DRAT export. No parent export is a separate failure or
hidden closure: the required complete cover does not exist. There were no SAT
model files, so no decoding to 1,653 physical edges was claimed.

## Files and working data

- `coverage-result.json`: compact verified aggregate snapshot.
- `coverage-summary.md`, `frontier.rows.tsv`, `frontier.cubes.tsv`: independent
  row/leaf coverage, exact IDs, parent/plan hashes, per-cube counts/logs.
- `physical-parent-audit.json`: full physical K58 host containment checks.
- `coordinated-coverage.json`, `coordinated-shared.json`,
  `coordinated-wallcc-verify.json`: results regenerated by the coordinator
  using m6's audit programs and a fresh replay cache.
- `CB1.REPORT.md`: full CB1 block report, including the first certificate and
  all 40 of its exact cube outcomes.
- `certified-leaf-3d443146-r11/`: actual proof input and checked replay files.
- `SHA256SUMS`: hashes of the compact committed evidence directory.

The repo's `*.cnf` and `*.drat` ignores are deliberately respected: generated
raw inputs/proofs have not been force-added. They are preserved locally at the
named certificate path and under `.ultramath/smwxwbjk8/`, and their hashes are
in `receipt.json`. The committed package retains the report, exact metadata,
verification logs and all 35 declared trees, rather than those generated files.

The retained checked proof inventory is 35 CAS prefixes plus the one leaf
certificate. The raw full campaign store, plans, working CNFs and receipts are
under `.ultramath/smwxwbjk8/`. They are not interchangeable with historical
lex-augmented inputs and have not been pruned by this report. Unfinished OPEN
traces were not retained as evidence. The member directory size is a `du`
snapshot, not a cryptographic summary.

To recheck the sole leaf from the repository root, use the exact current files:

```bash
.scratch/shared-learning-pilot/K58_shared_learning/tools/drat-trim \
  results/wall-cc-35-2026-11-26/certified-leaf-3d443146-r11/leaf.cnf \
  results/wall-cc-35-2026-11-26/certified-leaf-3d443146-r11/joined.drat \
  -i -p -w
```

The required final verdict remains **OPEN for all 35 parents** pending further
explicitly authorised work on the unresolved cubes. There is no whole-row
closure, no profile collapse and no Ramsey bound from this phase.
