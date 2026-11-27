# K58 adaptive-wall batch verification — 2026-11-27

## Verdict

**Scoped pass, not blanket verification. No wall row or Ramsey bound changes.**
The revised cover, signed symmetry reductions, owner implication, propagation
rules and 3,066 full representative closures were independently checked. Two
implementation/compliance defects remain, and the historical OPEN executions
cannot be authenticated from the supplied receipts alone.

In particular, **do not trust an imported `answer.json` on its status text
alone**. A corrupted cached parent with an unrecognized status can be promoted
to a false `VERIFIED_UNSAT_BY_COVER` without proof, model or children. This was
a synthetic negative-control reproduction, not a claim that the supplied normal
receipts are forged. The supplied official proof helpers also suppress warnings
with `-w`; the independent replays reported below use no `-w` instead.

## What I could not verify

1. **Historical execution of the cap128 sweep and all OPEN-only panels.** The
   receipts contain per-call statistics and an empty `decided` object, not raw
   per-call stdout/stderr, exit records or historical version/configuration
   identities. I verify the 1,101,974 receipt slots and current source-to-
   receipt formula bindings, not that all historical calls actually ran and
   returned UNKNOWN/OPEN. The same applies to 0/24 hard, 0/816 arm-leaf,
   0/24 adaptive, 0/48 child and 0/4 + 0/8 longer histories. No runtime ranking
   follows.
2. **Satisfiability or unsatisfiability of the remaining 983,774 parents.**
   OPEN is not a refutation, and a local complete-arm witness need not extend
   to a full K58 coloring. Every original root row still has a live
   representative; no ordinary wall row is closed by this batch.
3. **A full physical proof application for every representative.** Local rule
   queries were proved across all labels, and 2,469 selected full physical
   queries were replayed. That does not mean all 17,618,107 exclusions or all
   983,774 full-representative CNFs were individually replayed. The exporter can
   translate the rule to each indexed recipient; the physical checks are one
   selected recipient per label, not a physical replay of the whole live queue.
4. **External author/release provenance.** The archive manifests are unsigned
   and carried inside the same inputs. They establish internal byte integrity,
   not external authenticity, authorship, timestamp or an expected release
   digest. The attachments are gitignored rather than bound to repository HEAD.
  No earlier archive under these exact filenames was supplied, so a complete
  version history or immediate-ancestor relationship was not inferred.
5. **The `affected_edges` values for unselected domains.** Only selected-domain
   identities and their full proof/witness sets were independently checked.
   These unused statistics are not accepted as independently recomputed here,
   and they are not needed by the weighted totals below.
6. **Minimality of the 29-alternative owner explanation.** Its soundness is
   proved: every designated-pair coloring contains one of those 29 earlier
   alternatives. The single-assumption-deletion minimality checks were not
   rerun, and no deletion witnesses were supplied, so no stronger minimality
   claim is established.
7. **A first-principles rederivation of the whole frozen K58 encoding.** Local
   domain/owner CNFs were reconstructed independently. Full physical mappings
   use the supplied constructors, with their exact bytes, pins, guards, variable
   maps and first-tier semantic invariants audited. This does not constitute the
   separate formal semantic bridge for the original reduction, which remains
   outside this batch's proof.
8. **A source rebuild of Kissat.** Its supplied binary reports version 4.0.4
   and matches the archive manifest; source was not supplied. `setup.sh`
   performs no cryptographic `--require-hashes` installation, so the separate
   manifest checks are what bind the installed inputs.

The previous small joining-colour probe had the same fundamental limitation:
its eight timed candidate parent/child calls remained OPEN, with no SAT or UNSAT
proof. It also did not exercise an emergency worker kill or a SAT-model branch.
No behavior is inferred for those untested cases.

## Main findings and implementation issues

### 1. Cached unknown statuses fail open — reproduced

`conquer.run` validates terminal cached `VERIFIED_SAT` and `VERIFIED_UNSAT`
artifacts, but other statuses take the sufficient-seconds cache-return path.
On the exact live-0 strengthened parent CNF (SHA-256
`d69970e19ddadfad5057ffaf8ffbd1354f957a4003852dc2b6b8aeff63cb3004`), I
inserted a synthetic cached receipt with status `VERIFIED_UNSAT_BY_COVER` and
no proof or model. The unmodified controller returned an answer with the same
top-level status, `children: {}` and no proof/model. The output is explicitly
marked negative control, not evidence.

Normal production receipts do not generate this parent status, and no supplied
normal receipt was shown forged. Wrong query, wrong parent/index, missing or
wrong models/proofs and missing model/proof files were correctly rejected by
other guards. Nevertheless, imported/stale/corrupted cache state is **not
fail-closed**. Restrict generic cache reuse to OPEN, reject every unrecognized
status, and require exact query identity plus strict replay/model checking for
each terminal claim. `coordinator/cache-defect-reproduction.json` records the
actual result.

### 2. Shipped official replay helpers suppress warnings

`cover_proofs.rup()` invokes `drat-trim -i -w ...`, with other `-w` sites in
`engine/compile.py`, `engine/arm_pairs.py`, `one_second.py`, `timed50.py` and
shared-engine verification/conquer paths. The supplied verify commands therefore
do not meet the no-warning-suppression protocol. This does not mathematically
invalidate a good certificate, but hides diagnostic warnings and makes raw
success text insufficient for my acceptance rule.

All principal proof families below were independently replayed with freshly
compiled supplied `drat-trim` source using `-i -U` for RUP additions, or `-i`
for unrestricted DRAT, with no `-w`. Positive runs had zero accepted warnings;
wrong-query and malformed inputs reached explicit `s NOT VERIFIED` where
expected. The supplied official eleven-step pipeline also returned zero on
all eleven steps, in 35 minutes 35 seconds; those results are recorded in
`official-logs/` but are **not** the sole basis for acceptance.

## What was independently verified

### Archive and queue arithmetic

* Solver ZIP: 49,189,895 bytes, SHA-256
  `3324b778ea425dbcd48a3c7f19a38812820066d769581569f318b61108837b75`;
  10,409 manifest hashes pass.
* Evidence ZIP: 43,795,162 bytes, SHA-256
  `47bd1aa500756d70dce15b7680f83a290ee13e81c618f8ecae62583ab6fbef7b`;
  19,925 manifest hashes pass.
* The 30,336 nonmanifest paths have no unsafe entries, duplicates or
  cross-archive path collisions. External live TSV is byte-identical to the
  campaign's live queue: SHA-256
  `ba7901a685cc87e6d00bc8f876cff9986e985b1706cd098985477d1b2b898dcd`.
* All 11,585 row IDs join to the wall, campaign and physical-binding rosters,
  with matching profiles, nominated arm sizes, revised labels and global
  contiguous interval ranks. Every live row remains nonempty.

| Queue or set | Count |
| --- | ---: |
| Original representatives | 1,101,974 |
| Revised pair set before row symmetry | 1,022,357 |
| Pair-set reduction | 79,617 |
| Reduction by revised-row symmetry | 35,517 |
| Revised representatives before exclusions | 986,840 |
| Original-to-revised reduction | 115,134 |
| Full representative exclusions | 3,066 |
| Live representatives | 983,774 |

Live counts by arm 11/12/13/14 are **14,584 / 139,304 / 485,432 / 344,454**.
The ledger has 3,066 distinct rows, revised indices, original-parent hashes and
full representative hashes. Every complete `live_ranks` vector equals revised
kept ranks with exactly the certified rank removed. These are revised indices,
not interchangeable live or original offsets. For example index 0 maps to
`00000/01021` in the original queue and `00000/01022` in revised/live.
`coordinator/queue-analysis.json` and m8's independent stdlib rerun agree.

### Replacement cover and owner implication

All **304/304** replacement-cover queries and **718/718** revised local
symmetry queries passed independent strict RUP replay. The revised pair lists
have 401/232/150/47 labels by arm, down from 425/246/164/50. Every edit history
reconstructs its final list exactly. The normalized-arm cover argument supplies
a least available pair before ordering the other outside vertices.

The arm-13 owner `21012/22100` is revised rank 147. Its short unordered
expression uses 29 earlier alternatives and only 8 of 10 pair-pin conditions;
under that pair, every valid arm must contain an earlier pair. The exact
revised empty-owner query also contains all ten pins, remainder sorting and
owner guards. Both owner-layer queries pass strict replay. The 29 suffice for
soundness; minimisation was not independently checked.

By contrast, all **160/160** original-owner local colorings for this pair
validate with original ownership. Every one has an earlier revised owner: 83
first own `01021/10020` and 77 `10022/12200`. Thus the original owner's local
SAT witness and the revised owner's UNSAT refutation describe different
hypotheses, not a contradiction.

### Signed symmetries and encoder invariance

All **11,585 rows**, **1,412 nonidentity signed maps** and **12,997 physical
permutations** (those maps plus an anonymous re-sort per row) were checked.
This includes exact full signed-unit preservation, root/template automorphism
constraints, marked/root positions, group closure, anonymous-site
interchangeability, candidate/cardinality guards and support-selector sets.
The encoder evidence covers 392,605 candidate sets and 182,909 support-selector
sets containing 15,425,339 individual selectors. The first-tier `dense.py`
conditions permit ordered gate/auxiliary reassignment; no bare renumbering is
assumed.

The **1,483 final local symmetry proofs** (718 revised + 765 original) plus
**707 intermediate original proofs** all passed strict replay: **2,190/2,190**
with zero warnings. All **1,084 KEEP witnesses** validate their full local
coloring and least owner over identity and signed moves. Twenty-seven proper
satisfiable wrong-query controls reached `s NOT VERIFIED`.

Accordingly, revised row symmetry removes **35,517** occurrences under retained
SAT-equivalence, leaving 986,840. The separate original-convention reduction
suppresses **38,259** occurrences on 1,108 rows, retaining **1,063,715**, with
**1,063,715 + 38,259 = 1,101,974**. It is not added to the revised subtraction.
The intermediate layer independently accounts for 34,088 occurrences, followed
by 4,171 compact-symmetry occurrences.

### Closed representatives and positive-control panel

All **3,066/3,066** full revised K58 representatives were regenerated with exact
original parent, owner pins and auxiliary mapping and passed strict binary RUP
replay. They share only **69 distinct lifted proofs**, but every one of the
**3,066 distinct full queries** was regenerated and replayed. No duplicate proof
was allowed to stand for an unexamined query. Profile counts are
**2,082 / 16 / 896 / 72**.

The reusable empty-owner proof works on a different ordering convention only
through this explicit revision-and-transport argument. A local proof on the
original-owner query is rejected. This is not a whole-root-row closure: each of
the 3,066 affected rows still has other live representatives.

The biased known-refuted 24-parent panel has **23 direct-CaDiCaL + 23 Kissat +
24 shared = 70/70 supplied DRAT certificates verified** on exact regenerated
queries. Direct and Kissat each have one OPEN receipt-only record, on the same
revised index **391,574**. All 24 are closed by the reusable lifted certificate
as well. These selections cannot estimate survivor closure rates or certify
which historical engine produced or timed a proof.

### Propagation, domains and physical checks

All **885** original and **830** revised selected-edge records were rechecked:
every surviving color has a triangle-free complete local arm witness, exact
ordered word ownership and correct pivot/domain partition. All **829** nonempty
live labels have binary pivots. Root and child exclusions are respectively
proved by single-violation-disjunction queries; pinned child assignments and
their witnesses match the computed domains.

| Quantity | Verified total |
| --- | ---: |
| Local domain/owner/propagation proofs | 4,858 |
| Revised physical consequence queries | 2,469 |
| Original-owner physical checks | 31 |
| Root exclusions, weighted by live multiplicity | 17,618,107 |
| Root-forced edges | 2,399,187 |
| Parents with a forced edge | 856,935 |
| Children gaining further exclusions | 1,966,300 |
| Further child exclusions | 24,921,805 |
| Both children gain exclusions | 982,526 |
| Exactly one child gains exclusions | 1,248 |
| New conditional forced edges | 6,262,071 |

The original selected-edge totals are 943,118 forced, 158,856 binary and
2,045,092 color exclusions. **2,045,052** exclusions count as surviving
`propagate` without a conflict and requiring RUP reinforcement; that is not a
count scheduled as trivial unit-propagation refutations. Revised propagation
confirms 1,154 selected-edge exclusions. All **12,438** pivot-side propagation
scores/tie-breaks reproduce.

Every one of **4,858** reconstructed local queries passes `-i -U` with no
warnings. All **2,469 distinct** revised physical query hashes pass as well;
there are **2,119 distinct lifted proof streams**, so this is a check count,
not 2,469 independent proof bytes. All **31** original-owner physical checks
also pass. All variable maps, ten signed spoke pins, owner tails and binary
prefixes match the physical receipts, including an independently regenerated
original cap-receipt parent hash for every recipient.

Wrong-domain, wrong-row/index, wrong-arm and incorrect-owner controls fail as
required. A legitimate proof can occasionally verify against another
satisfiability-equivalent query; a retained observation notes this and does
not pretend byte difference alone invalidates a proof.

### Receipts, formula bindings and live-index execution

The complete original index map contains 1,101,974 unique records. Its hashes
are:

* uncompressed TSV `47df39a98622968dc28446c7ce092a7b3a9508b148468ec4c60076751363b312`;
* compressed TSV.GZ `5dfeea976c2566c1d841528d0d20c237b619950934a93daea9dcbb00069cdaa1`.

At receipt-ledger level, conflict values range from 128 to 191. All four
statistics match the packaged summary: 142,061,920 conflicts,
1,335,188,169 decisions, 35,089,528,161 propagations and
16,950,171,638 call microseconds; summed row CPU is 13,786.527207892977 s;
ordered row-receipt digest is
`8fed5c9b08f758811febb612a6142e0dc1b0cbf1c346c233840201d7cb282bde`.

All **11,585** parent/shared/ordered-cube hash triples regenerate from current
source, covering all original ordered cubes. All 39 official and 36 additional
original full-query samples match after appending the checked cubes to their
shared CNFs. Bounded checks also match 72 hard-base/table/table-capacity
queries, 816 physical-arm-leaf cubes, 24 positive revised queries, 96 adaptive
queries and 16 deeper live queries. These are current-source bindings, not
proof of past engine activity.

For live index 0, the exact row and pair are
`00032f347903…`, arm 14, `00000/01022`. The representative is SHA-256
`ae90931dc6cd482105153dd720209e602bbfc7cc0915e18c6e87023ee2659931`. Its
strengthened parent adds 23 exclusions; child 1 adds 31 (23 + pivot + 7), and
child 2 adds 34 (23 + pivot + 10). Their hashes respectively start `d69970e1`,
`f7e6f5b2`, `e85234ab`. The fourth palette color is eliminated and the checked
pivot `[0,11]` has exhaustive colors 1 and 2. A four-second adaptive run gave
parent/child budgets 2/1/1 s, all **OPEN**, with the exact exported hashes.
The root/child physical proof lifts verify; no binary-cover closure follows.

The first divergence is an explicit crosswalk: live 241 equals revised 242,
not revised 241. Index and invalid-color/out-of-range guards reject the tested
controls.

## Ultramath report

Swarm **`smwyfnpf0`**, eight members, `moonshotai/kimi-k3.1-pro`, maximum
reasoning effort, 180-minute limit, 100 model calls per member / 1,600 total.
All eight directions finished with accepted scoped solutions. The board's
`solved` state means these audit tasks succeeded, **not** that a wall row,
global SAT search or Ramsey bound is solved. I, as coordinator, independently
reran their material checks and compared identities, checker outcomes and
receipt artifacts before accepting them.

| Direction / member | Result after coordinator verification |
| --- | --- |
| A / m8 | Archive integrity, version/source comparisons, full queue/index arithmetic. Standard-library reproductions byte-identical. External provenance remains unverified. |
| B / m1 | All 304 replacement-cover, 718 revised-local-symmetry and 2 owner-layer checks; 12 stratified full parents plus a wrong-pin rejection. All 1,036 positive checks rerun without warning. |
| C / m3 | All 3,066 full physical closures and all 70 control DRATs rerun; 69 vs 3,066 proof/query identities distinguished. Direct/Kissat OPEN remains history only. |
| D / m4 | All 4,858 local proofs, 2,469 revised physical, 31 original physical and all propagation/pivot/geometry checks rerun. Both negative controls pass. |
| E / m7 | All 2,190 intermediate/final symmetry proofs, 1,084 KEEP witnesses, all row and encoder maps and 27 wrong-query controls rerun. |
| F / m6 | All 1,227,685 receipt checks, complete cap128 map, every original ordered cube and all bounded bindings rerun; all 70 control DRATs plus wrong-query rejection rerun. Historical execution remains unauthenticated. |
| G / m5 | Exact live-0 formula and binary split, strict physical checks, executable controls and the fail-open cache defect confirmed. Unrecognized cached statuses may propagate without evidence. |
| H / m2 | 79 positive integration checks, all 31 original-owner physical checks and three proper negative controls rerun; proof-sharing versus query identity correctly separated. |

The official eleven-step run was done separately as job `jmwyfqifx` and
completed all commands. Independent reruns were additional work, not a
repetition of only the top-level summaries. Proof counts are intentionally
reported per query family and are **not** added into a misleading global unique-
certificate total: families overlap and some checks reshare byte-identical
proofs.

### Judge-error record

I initially issued an erroneous `PLACEHOLDER` rejection to m7. This was my
tooling mistake, not a mathematical finding. Its strengthened submission was
then independently checked and accepted through the additional 707 intermediate
proofs and 1,084 KEEP witnesses. The board retains one false rejection flag for
m7. I also recorded and corrected two small transcript-only count/comparison
errors before acceptance; no proof artifact had those errors.

### Producer-summary error in m4

m4's exhaustive physical producer completed its 2,469 checks before exiting on
a summary-only `KeyError`. Its persisted raw ledger was independently
revalidated, and the full producer was separately run to completion during my
audit. The final accepted 2,469-query ledger has 2,119 lifted proof streams
and no warning.

## Files and evidence

This directory contains `summary.json`, this report, official command logs, the
queue arithmetic, live-0 receipts, cache-defect reproduction and the 16-case
stratified full-parent strict-sample summary. The archive
`dist/k58-wall-983774-audit.zip` additionally contains the accepted member
reports, auditor scripts, raw result ledgers, reproduction notes and
`SHA256SUMS` for every packaged file. It complements the supplied solver and
evidence ZIPs; it does not replace them. Some member scripts resolve inputs
relative to this repository layout. For arbitrary extraction directories, use
the source-bundle symlink layout documented in `HANDOVER.md` rather than
assuming all member scripts are path-independent.

`tools/wall983774/replay_closed_sample.py` is the coordinator's independently
compiled-checker sampler. The archive contains the members' complete exhaustive
auditors as well; no claim depends on the 16-case sample instead of their full
checks.

## Bottom line

Within the explicitly documented local/physical semantics, the revised cover,
owner implication, symmetry transformations and 3,066 closed representatives
hold. This produces **983,774 live representative parents on all 11,585 rows**,
exactly as the handoff says. None of those remaining representatives or rows is
established unsatisfiable by this batch. Historical OPEN executions and archive
provenance are not independently established, and imported cached outputs need
evidence outside their status text because the unknown-status cache path is
fail-open.
