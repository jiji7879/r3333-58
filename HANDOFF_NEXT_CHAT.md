# Handoff — the next chat starts here

Written at the end of the session of 21 November 2026 that measured the wall.
Read this first, then [README.md](README.md) for the map of the repository.
[HANDOFF.md](HANDOFF.md) is the earlier cold-start brief — bundle provenance,
the eight-direction audit, the Lean core — and its status tables are stale; a
dated block at its top says which numbers to ignore.

## Where the work stands

`R(3,3,3,3) ∈ [51, 62]` (Radziszowski DS1.18). **Nothing has moved the bound.**

**Latest speedup review and implementation.** An explicit opt-in native LRAT path is now in the C&C engine (`--engine native --lrat-trim PATH`), with exact query hashes, independently replayed CAS premises, checker/cache binding and 24/24 controls. Default DRAT is unchanged. It reduces ordinary checker CPU on H8, but raw LRAT is larger and leaf memory higher: no general solver-search claim. `lean/K58/EmittedBridge.lean` and `TargetUnits.lean` close the emitted coordinate-order gap, not `ChainReady`. A 26-test admission gate, preprocessing/memory measurements and the K15 negative result are packaged in [speedups.md](results/next-directions-2026-11-28/speedups.md). Further physical bridge work is preferred over more phase tuning; see [backend guidance](results/next-directions-2026-11-28/backend/ADOPTION.md).

**Latest 2026-11-28: literature-inspired experiments (`smx06hpp8`).** Five directions were accepted; FKR and SMS ended without formal submissions and were independently replayed as bounded results. `K58.cat58` and its attachment bounds, the finite 112-support catalogue, conditional physical transport, and exact readiness of all 15 emitted support steps are Lean-checked in the root build. Physical pinning, emitted atom-order identification, physical criticality, guard=`Sends`, and `ChainReady` remain open. LRAT replays use two independent but unverified checkers. KMT has exact allocation receipts but regresses CPU. The FKR early census reaches 31,712 cases, exceeding its 10,000 continuation gate; the one-colour SMS substitute has no demonstrated useful speedup. See the [experiment index](results/next-directions-2026-11-28/README.md) and the [checked FKR stop](results/next-directions-2026-11-28/attachment/README.md). No bound, wall-row status, production encoding default, or frozen ledger changed.

**Earlier update (bounded MCTS/counter/maximality follow-up: arm 3 gains and exact-parent conditional assembly).**
All eight directions of `smwzzs8qs` were accepted after independent replay.
MCTS remains negative: direct two-sim "full rollout" reaches only root depth 1
and reproduces shallow cubes; selective hybrid selection loses cap-normalised
cost comparison and all wall leaves stay OPEN. Conditional Sinz guarding is
equivalent and much stronger locally, but unconditional recurrence raises
propagation and CPU 1.333× geometric mean at two seeds. Configurable maximal-
colour finally gives a **positive encoding result**: arm 3 alone (45 safe edges,
+7,605 clauses/+2,520 witnesses) gives 399.1M vs 838.4M propagations and
120.766 s versus 222.721 s CPU at 2M conflicts on the exact parent, with OPEN
non-closure. Coordinator replay at 1M gives 48.027 s versus 65.614 s, both OPEN.
BCP residual form removes 465 parent-satisfied clauses without changing search
trajectories. This is fixed-budget throughput, not UNSAT or a wall sweep.
`targetParent_satisfiable_of_ready` is now kernel-checked with explicit physical
premises; all 3,493,016 parent bytes match exactly. The remaining obligations
are physical base/unit realization, candidate criticality, 112-support
membership, adjusted guard-set equalities and `ChainReady`. Newly added
`ConfigurableMaximal`, `SemanticAssembly`, `TargetSuffix`, `TargetParent` and
`TicketPremises` are in the integrated clean Lean build. Next bounded step:
arm-3/BCP on one retained hard leaf, preserving proof scope. See
[the complete proof report](research/ams-wall-followup/proof.md) and
[its evidence index](results/ams-wall-2026-11-28/README.md).

**Updated 2026-11-28 (Duggan paper methods reviewed with k58-massive-solver as baseline).**
All eight directions of `smwzxq4fl` were independently accepted; no Ramsey bound,
wall row or profile closed. The most useful transfers are the native guarded-counter
and support-selector Lean extension theorems and a semantics-preserving
conditional-counter encoding: leave Sinz recurrence clauses unguarded and guard
only overflow clauses. A new configurable-edge maximal-colour normal form passed
807,936 small controls but was neutral at one million conflicts on the sampled
wall row. Proven dead ends: preferred-full-vertex catalogues at $K_{58}$ (deficit
at least 3,480, so no full vertex guaranteed), exact gray-edge generalisations of
critical links (all singleton), the old `hailmary-lex` comparator (vacuous), and
Duggan's pinned 2024 MCTS cuber (incompatible prior/action layout). Current MCTS,
corrected full static lex, full/pinned MCF and direct soft-constraint pilots all
failed to show material gains. `results/hailmary-lex/README.md` now carries the
withdrawal. New pure-kernel `LinkSaturation`, `FullVertexBudget` and
`EncoderExtensions` modules are registered in `lean/K58/Check.lean`; full
`lean/build.sh` passes. See [the main assessment](review/DUGGAN_PAPER_ASSESSMENT.md)
and [its checked proof record](research/duggan-methods-review/proof.md).
The recommended next step is one exact-parent Lean/DIMACS semantic assembly,
then one small boundary-counter A/B, not a production sweep.

**Updated 2026-11-28 (massive unified frontend; no new closure).**
A separate `dist/k58-massive-solver.zip` now unifies bounded stock,
colour and square-plus-colour jobs. Both earlier archives are unchanged.
`unified` and `store` are opt-in: stock `run`, `finalise` and `replay`
were not changed, no production cohort was launched, and the later
fourteen-row negative result is still negative.

`square-merge` is restricted to the fourteen checked ordinary rows on
first tier. It can compose square constraints with `off`, `counter`,
`escape`, or `color`, preserving the original body and auxiliary allocation;
verified composite parents get separate square/colour provenance rather
than a pretend original-parent certificate. The cohort runner has frozen
positive budgets (including checker and wall time), exact job/attempt keys,
resume verification, 1–16 concurrent workers, a total conflict reservation,
and no implicit retry-tier or stale-parent promotion. Complete covers need
outgoing proof export and replay, not merely leaf OPEN/status text. Models
are projected and re-evaluated on original clauses; external DIMACS jobs
remain explicitly outside stock-case provenance.

The content-addressed store deduplicates payloads without deduplicating
logical cases or upgrading byte adoption into evidence. Compressed carriers
and their decompressed proof hashes are kept separately. There is no GC.
Plan integrity tests include a wrong/weakened parent, an empty attempt set,
conflict-budget exhaustion, and a complete child-group timeout.

Four accepted reviews (`smwzsk4n0`) supplied 195 row-crosswalk checks,
12 scope guards, 90 scheduler checks, and 13 artifact-store tests. A fresh
archive passed offline-wheel setup, five stock example replays, and the full
deep modified smoke including a two-worker bounded mixed cohort and blob
integrity checks. Read [unified/README.md](tools/selfcontained/updated-solver/unified/README.md)
and [MASSIVE_VALIDATION.md](tools/selfcontained/updated-solver/MASSIVE_VALIDATION.md).
No Ramsey bound or wall-row closure is claimed and no general speedup was
measured. Full source and test controls live under
`tools/selfcontained/updated-solver/`; the handover ZIP stays out of Git.

**Updated 2026-11-28 (a self-contained modified solver archive).**
Copied `dist/k58-solver.zip` to a separate **49,739,924-byte**
`dist/k58-updated-solver.zip`; the stock archive and production paths are
unchanged. Its new commands are `square` (K15 verification, export and bounded
spoke solving), `color-wallcc` (optional physical-colour pivot), and `armcap`
(historical paired/transversal/two5/joint-support tools). They are explicitly
optional, not a new default search policy or a production-speedup theorem.
Strengthened and auxiliary-extended results keep their separate proof ceilings;
there is no production wall or Ramsey closure.

The clean archive passed offline-wheel setup, five stock example replays, the
deep modified smoke (all fourteen ordinary parents, K15 strict proof/models/
RUP, colour-pivot native derivations and controls), strict bundled-Kissat
false-cube certification plus truncated-proof rejection, and stock smoke
(three sample certificates/three replays/zero failures). One proof-checker bug
was fixed by deletion-stripping rather than `-w`; the stock CNF is rebound to
its named historical rank before certification. Rebuilding preserves all 644
member hashes and original binary executable bits. Build scripts and complete
limits are in [tools/selfcontained/updated-solver/README.md](tools/selfcontained/updated-solver/README.md),
and test details are in [VALIDATION.md](tools/selfcontained/updated-solver/VALIDATION.md).

**Updated 2026-11-27 (K15 square/matching spokes on the ordinary wall).**
The shared K15 matching formula and its normalization are now exhaustively
checked, including all 144 pairs of labelled valid K5 pins and the exact
clause multiset. A strict native replay (full 470,852-byte read, no `-w`,
zero warnings/errors and zero RAT) and an independent addition-only RUP check
pass; the K15-path and K14 square/matching models are genuine boundaries. The
earlier “eight flavours” objection was a generator bug, not a missing graph
case.

Four accepted audits of `smwziqvco` bind **9,287 per-row-distinct rules**
(7,247 globally distinct) to fourteen first-tier parents with
`tables=True,total_critical=True,full_root=False`; there are **4,807**
falsifying cubes surviving original unit propagation across ten rows, and
**four zero-gain rows**, two each for $(15,14,14,14)$ and $(16,14,14,13)$.
This is a conditional clause inventory, not a row, representative or Ramsey
proof: ten full-parent cube calls remain OPEN at their nominal caps and no
full-parent DRAT was retained for them. The thirteen full-root historical
controls are a separate panel; their corrected counts are 939 seeds, 2,817
one-spoke neighbours, 1,918 with extra propagation and length-3/4/5 counts
353/151/18,528. Bound-exhaustion does not prove minimality. Important
provenance repairs: the K15 CNF hash is now explicitly pinned, local proof
hashes use decompressed bytes, and batch hashes use compressed JSON bytes.

Read [research/k58-square-spoke-wall-test/audit.md](research/k58-square-spoke-wall-test/audit.md)
and [its reproduction receipt](research/k58-square-spoke-wall-test/checks/reproduction.md).
The Siege gate is scoped to this finite and package verification, not the K58
wall. No production inputs, ledger or search queue were modified.

**Updated 2026-11-27 (wider paired-arm families and repaired strict replay).**
The extension has **176,136 four-literal clauses over every one of the 1,300
inputs**, separate **26,224 mixed** and **10,136 double-negative** signed
candidates, and no additional same-arm singleton rules in this tested regime.
Regenerated JSON matches the supplied bytes, all 1,300 full-root hashes match,
and all thirteen selected support intersections are independently evaluated.

For the wider family, **1,747** countercubes survive the older ternaries and
**939** survive older direct-plus-ternary propagation. This is a new
conditional-clause opportunity, not proof that four literals dominate ternaries
or that guards are always active. Both four-literal native examples verified;
the other eleven remain OPEN at 40,000 conflicts. The fourteen signed examples
are already closed by the older unit propagation, so their evidence should not
be conflated with the wider incremental opportunity.

The original unmodified strict replay **aborts on warnings** involving ignored
deletion of pseudo-unit clauses. Only deleting `d` records while retaining all
`a` additions gives strictly stronger RUP checks with warnings fatal, no
`-w`, whole proof streams consumed and zero RAT in core: **16/16 pass**. Original
proof hashes are preserved alongside the new normalised-proof hashes;
431,370 original bytes and 263,222 stripped bytes are tracked. This is a
verification repair, not mathematical refutation of the clauses or a licence to
hide warnings. Proven inputs and compact scripts are in
[research/k58-paired-arm-extensions/audit.md](research/k58-paired-arm-extensions/audit.md).
The six seed-zero 60,000-conflict benchmark calls remain OPEN on both policies.
No unrestricted solver completion, row closure, new bound or production-ledger
change follows.

**Updated 2026-11-27 (general paired-arm clauses on the 1,300 hard inputs).**
The proposed general clause form is correct as a **conditional** theorem on
these root encodings: if the sender guard requires at least 14 colour-$c$
neighbours outside its own arm and $H_i$ hits every feasible five-neighbourhood
in two selected other arms, then $\neg g_{a,c}\lor\bigvee_{v\in H_1\cup H_2}
E_{a,v,c}$ holds. The local cap of five follows from a two-colour Ramsey
argument, not from a template; all 32,768 $K_6$ edge colourings were checked,
as well as all 48 template/colour alternatives. Guard and physical-arm bindings
must be rebound per row. Cube-learned strengthenings need $\neg Q$ at parent
level and a fresh feasibility intersection, not an over-general transfer.

All **1,300 full-root input hashes** and the complete **16,530** ternary
clauses in **1,236 rows** regenerate exactly, including the entire count vector
(maximum 33). Fourteen physical matched instances have strict full-byte native
proof replay, totaling 32,972 bytes, zero warnings/errors and no RAT lemmas in
core. This is a major **conditional preprocessing space**, not 1,300 solved
rows: six full parents at 60,000 conflicts and ranks 1200/1300 at 800,000 stay
OPEN for stock/direct/extended policies. The supplied historical byte total is
not locally available historical proof evidence, nor is this a solver speedup,
Ramsey proof, or proof that guards are always active. Ultramath remains off.

See [research/k58-hard1300-paired-arms/audit.md](research/k58-hard1300-paired-arms/audit.md)
for the proof, independent recomputation and scope limits.

**Updated 2026-11-27 (reusable spoke rules and twenty more case-0 cubes).**
Local auditing confirms three distinct packages of evidence in the latest
archive, without any new independent-model run (Ultramath was explicitly
turned off). First, the donor-36/40 cores produce **53** strict, replayed
transported exclusions across **27 wall rows**, including the donors. Each is
a conditional binary clause on its own named signed parent, not a closure of
an owner or a universal rule. Next, the geometric catalogue has **9,288**
distinct representative/clause pairs on **6,617 representatives and 6,489
rows**. Its placements all verify, with six canonical proofs and **eight**
full physical examples covering all six classes; it is not a 9,288-full-
parent-proof sweep. Finally, **20 direct case-0 arm exclusions** prove on the
full parent without trigger units: eleven 82-pin cubes and nine 13–16-pin
cubes.

All **91** native obligations passed strict full-byte replay: six canonical,
eight physical, 53 transfers, two pivot eliminations, two case-0 arm covers,
and twenty cubes. Reconstructed queries and hashes match the native receipts,
with no warnings/errors and no RAT lemmas. The exhaustive case-0 arm covers give
**1417/1417 OPEN at pivot 0** and **20 exclusions with 325/345 OPEN at pivot 3**.
All 57/36 old word-group sets still have surviving arms, so this does not close
pivot 3. The three strengthened three-second branch/parent controls stay OPEN;
the four control observations elsewhere are not an advertised speedup. Both
negative controls reject appropriately.

Read [research/k58-reusable-spoke-rules/audit.md](research/k58-reusable-spoke-rules/audit.md).
The manufacture of a reusable clause is not a representative or row closure,
and the upstream arm-classification/marking proof obligations remain outside
this local theorem-transfer audit. No production ledger or sweep was changed.

**Updated 2026-11-27 (the two trigger assumptions are now excluded on signed
case 0).** The 24-pattern package closes all remaining 7+17 words from the
preceding two-site checkpoint. There are 217 complete arm alternatives
(69/148), four direct word refutations and 203 arm refutations, plus exhaustive
arm-cover proofs. With the two eliminated pivot colours and the exact 7/17
prior covers, this gives the full signed-parent entailment
$P\Rightarrow\neg E_{31,13,0}\lor\neg E_{42,13,1}$, printed as
`-2721 -2766 0`. This is **not** an unconditional branch or representative
closure, a model, or a Ramsey result, and it does not transfer automatically
to other owners. Source archive and raw parent SHA-256 are checked against the
prior package.

All **236** component proofs passed strict replay, with whole proof files read,
one exact `s VERIFIED`, no warnings/errors and zero RAT lemmas. The separately
written DAG audit passed **2,113 assertions**, reconstructs every expected
query/hash and certifies the case-combination. The supplied verifier's final
conditional-clause loop is vacuous with no retained leaves, so the conclusion
rests on the explicit exhaustive/disjunctive argument, not on its printed
`OPEN=[]` or `Verified conditional clauses` line. One model's 8/28 versus 7/17
case-count confusion was caught and corrected before accepting its inherited
cover/composition review. A later submitted literal-fidelity report was read
independently; remaining swarm work was then stopped at the person’s request.
Satisfiable/unrelated-query and truncated-proof controls reject.

Proof, compute checks and receipts:
[research/k58-case0-24-patterns/proof.md](research/k58-case0-24-patterns/proof.md).
The Siege gate returns `PROVED #2` for this conditional implication, not a
wall closure or theorem about `R(3,3,3,3)`. No production ledger or sweep was
modified.

**Updated 2026-11-27 (two-site consequences audit; the earlier state used
 by the preceding 24-pattern continuation).** The supplied case-0
package now has a scoped, independently checked verdict: twelve word
refutations on the **full signed parent**, plus an exact conditional frontier
of 24 still-OPEN words under the two trigger pins $(31,13)=0,(42,13)=1$.
Both `search` and `unsplit` variants of all twelve proofs replayed cleanly.
The scope correction is essential: `unsplit` pins only trigger+word, **not the
pivot**, so these twelve exclusions hold whichever pivot colour is used. The
other 24 remain unresolved, not SAT; neither whole pivot branch, representative
0, a wall row, nor the Ramsey bound is closed.

All 196 calls of the supplied verifier passed through a proxy that removes
`-w` and requires an exact `s VERIFIED` with no warning. The package's stated
`-w`/substring acceptance itself is not trusted: a corrupted proof demonstrably
produces a warning-bearing `s VERIFIED` which that criterion hides and accepts.
The signed-parent full constraint families, eight local cover tables,
conditional frontier and all owner formulas were separately regenerated.
An independent checker passed **3,701 assertions and 42 strict replays**.
Both pivot projections contain **24,686** clauses including the formerly
missed 5,201 owner/auxiliary clauses; all 315 table witnesses and 157 owner
witnesses pass the complete projections with maximum mono-degree 15, still
only 30-vertex models.

On the single 47-variant row, 11 forcing indices have a local antecedent
witness and three antecedents are impossible. Exactly six live indices
(3,5,7,19,23,32) have a two-pin minimum, five need all three pins, and 33
`LOCAL_COUNTEREXAMPLE`s are only local models, not global counterexamples.
The 47 source formulas and owner cubes rebuild byte-identically from restored
`revised.py::export`. No transfer to the 11,585-row roster is justified.
Three accepted Ultramath audits cover closures, semantics and provenance;
the abandoned counting direction was replaced by the independent checker.
There are no new production searches or production-ledger changes.

Read [research/k58-two-site-consequences/proof.md](research/k58-two-site-consequences/proof.md)
for the provable statements and [its compute
checks](research/k58-two-site-consequences/checks/2-compute.md) while resuming.
The Siege gate returns `PROVED #2` **only for those literal package claims**.

**Updated 2026-11-27 (joint clause bank).** For the case-0 pivot $(31,42)$ and
first second-arm vertex $1$, the conditional clause
$\neg E_{31,w_1,2}\lor\neg E_{42,w_1,1}\lor\neg E_{42,w_2,1}$ is established at
**$w_2=2,9,11,13$, independently on each physical pivot branch (0 and 3)**:
eight full-parent negation queries are UNSAT with strict, warning-free replay.
This is semantic entailment from the falsifying assignment, not a claimed RUP
prefix or a generic Wave A transfer. Adding the four proven target clauses to
each exact branch leaves both strengthened full branches OPEN at three seconds;
the other 20 candidate hypotheses remain UNKNOWN, not invalid. The production
cover is unchanged. Report, compact audit and archive-native replay:
[results/joint-clause-case0-2026-11-27/REPORT.md](results/joint-clause-case0-2026-11-27/REPORT.md).

**Updated 2026-11-27 (joint second-arm choices).** A controlled case-0 test at
physical pivot $(31,42)$ and second-arm vertices $1,2$ found 56 checked local
models and 200 strict local UNSAT proofs **per pivot colour** (physical 0/3),
with 52 jointly feasible tuples common to both. The four shared product-level
incompatibilities are $(2,1)$ at the first vertex and $(c,1)$ at the other for
all $c$: each has a full signed-parent UNSAT query in both colours, proof-replayed
strictly. The ten one-vertex controls stayed UNKNOWN at two seconds. This is a
real joint condition, not a result on all 28 previously sampled parents and not
a branch or wall closure. The supplied Wave A JSON/proof digests remain absent;
its separate bare-arm bounds do not supply physical transfers. Reports, replay
and archive provenance: [results/wave-a-joint-case0-2026-11-27/REPORT.md](results/wave-a-joint-case0-2026-11-27/REPORT.md).

**Updated 2026-11-27 (square/six-rule direct-wall pilot).** The package has one
conditional-triangle schema, not six universal rules. Three independently
replayed audits accepted its local semantics, input design and finite-template
catalog scope. Its “six” refers to six-vertex obstructions. All 384 direct and
1,020 short additions, plus the complete 1,209-clause
prefix, passed strict warning-unsuppressed original-parent verification. The
matched direct run on branch 44 used stock versus stock + 1,020 short clauses
on eight depth-three cubes: **16/16 fresh three-second calls returned UNKNOWN**.
There is no new cube or row closure, no model, no certified comparison of speed,
and no basis to scale. No further search was started. Full input identities,
exact timings, audit reproductions and limitations:
[results/square-six-wall-audit-2026-11-27/REPORT.md](results/square-six-wall-audit-2026-11-27/REPORT.md).

**Updated 2026-11-27 (preferred-pair cover).** Four accepted audits verified the
608 local cover proofs, all row symmetry premises, preferred-owner semantics,
original-parent/export identities and complete next-queue permutation. The
result is an exact root decision cover of 3,604,436 representative jobs, useful
as a local preprocessor, not a reduction of the 11,585 OPEN wall rows. C's
solver timings are not matched comparisons; the new disjoint cap-512 batch is
10,000/10,000 OPEN with zero fallback calls. Do not scale the preferred search
on the present evidence. Full assessment and reproduction:
[results/preferred-wall-2026-11-26/REVIEW.md](results/preferred-wall-2026-11-26/REVIEW.md).

**Updated 2026-11-27 (three-second representatives).** Direct CaDiCaL
produced four independently replayed full-representative UNSAT proofs on a new
24-case cohort. All four are already locally excluded; a fixed 12-job locally
surviving cohort remained OPEN in both direct and shared executions. There is
no general solver winner and no target-row or wall closure. The shared/direct
comparison checks query and proof identities and is not described as a speedup.
Read [results/solver50-3s-2026-11-27/THREE_SECOND_RESULTS.md](results/solver50-3s-2026-11-27/THREE_SECOND_RESULTS.md).

**Updated 2026-11-27 (mandatory joining-colour children).** Four genuinely
unprobed new-cover representatives were tested against their sole unrefuted
joining children, with exact, independently replayed refutations of every
other physical colour branch. Eight parent/child CaDiCaL calls all remained
OPEN at three seconds; two fresh positive controls produced replayed DRAT
proofs. There are zero new representative or row closures and no basis to
scale this mechanism. Read
[results/solver50-joining3s-2026-11-27/RESULTS.md](results/solver50-joining3s-2026-11-27/RESULTS.md).

**Updated 2026-11-27 (adaptive-wall batch audit).** The revised cover and
signed symmetries reduce 1,101,974 representatives to 986,840, and 3,066 exact
full-representative RUP proofs have been independently replayed, leaving
**983,774 live representatives on all 11,585 wall rows**. All 2,469 selected
physical rules and all 4,858 local domain/propagation proofs replay without
`-w`, with full proof-sharing identities checked. This does not close a wall
row or validate historical OPEN solver executions. The supplied batch's
`conquer.py` also has a reproduced fail-open path for unknown cached statuses,
and its official proof helpers suppress warnings. This cache defect is separate
from the earlier hardened adaptive-wall tooling below. Full report, including
all eight accepted Ultramath audits and what remains unverified:
[results/wall-983774-2026-11-27/REPORT.md](results/wall-983774-2026-11-27/REPORT.md).

**Updated 2026-11-26 (adaptive-cache integrity).** Cached native proofs/models
and persisted tree verdicts are now revalidated before reuse/export; malformed
artifacts stay nonterminal, DRAT replay does not use warning suppression, and
models must be total. The independent 29-case matrix has zero mismatches, the
full campaign verifier and all 1,000 manifest hashes pass, and all 11,585 small
profiles remain OPEN. No solver speedup or wall closure was measured. Read
[results/adaptive-wall-2026-11-26/CACHE_FAIL_CLOSED.md](results/adaptive-wall-2026-11-26/CACHE_FAIL_CLOSED.md)
and [tools/adaptive_wall/README.md](tools/adaptive_wall/README.md) before using
the adaptive campaign. The older campaign priorities and measurements below
are otherwise unchanged.

**Updated 2026-11-25.** The owner ran the whole cover on their own machine and
closed 18,858 more rows: **98,142 of 113,179 are certified and replayed**
(`{"checked": 98142, "replayed": 98142, "failed": 0}`, manifest
`98d82268ff4c277820f00cbed3405c625dbb53d3603610e45eacc73b562b19f9`), with
12,893 OPEN and 2,144 legacy. The bundle audit — case index and ledger match byte
for byte, twelve sampled rows rebuild to their recorded CNF hashes, the proofs
themselves were not sent here — is
[results/k58-full-cover-run-2026-11-25/](results/k58-full-cover-run-2026-11-25/).
What is left: 1,288 retry-tail rows of `(15,15,15,12)`, 20 split certificates of
`(16,15,15,11)`, and all 11,585 of the seven small profiles. The wall is
untouched; the bound is where it was.

The counts below are the state before that run and are kept because the prose
after them refers to them:

| status | rows (2026-11-22) |
| --- | ---: |
| `CERTIFIED` (single DRAT, replayed) | 79,264 |
| `SPLIT_CERTIFIED` (split argument, not replayable here) | 20 |
| `LEGACY_HISTORICAL` (proof bytes in an archive not held here) | 1,743 |
| `LEGACY_EXCLUSION` (profile/template exclusion, an argument) | 401 |
| `OPEN` | 31,751 |

The per-case ledger is [results/ledger-2026-11-22.tsv.gz](results/ledger-2026-11-22.tsv.gz),
rebuilt by [tools/ledger_state.py](tools/ledger_state.py) from the release index
plus the hard-tail binding. Run the tool rather than editing the file.

## What the last two sessions settled

1. **The wall is all 11,585 cases, not the 469 the earlier note was measured
   on.** The seven small profiles close at no budget tried: 0/98 at 12 s
   ([runs/2026-11-16-small-probe/](runs/2026-11-16-small-probe/)), 0/68 at
   70 s / 2.4M conflicts over the five two-critical profiles
   ([runs/2026-11-21-two-critical-probe/](runs/2026-11-21-two-critical-probe/)),
   0/51 at 60 s and 0/9 at 300 s on the one-critical pair. Every one of the 68
   consumed its whole budget (CPU 70.0 s on all 68), so there is no fast tail a
   better sample would find.
2. **`(16,15,15,11)` is finished as far as solving goes**: 16,070 certified,
   20 refuted as split certificates, 83 historical. The 20 are bookkeeping, not
   work.
3. **Certificate volume is ~10× the earlier sizing.** The index's own byte
   counts: first tier 76,967 certificates at 5.6 MB mean (429 GB), retry tier
   2,297 at 28.6 MB mean (66 GB). A retry pass over `(15,15,15,12)` emits
   ~480 GB of DRAT. `--publication` deletes each proof after hashing it, which
   is how a 495 GB campaign fits in a 16 MB release index.
4. The documentation had drifted three orders of magnitude (README still said
   81 certified). It is current as of `01d5ad2`; if you change state, change it,
   and update the dated block in `HANDOFF.md` rather than its body.

## What is open, in the order I would take it

**A. Decide what to do about the wall — this is the campaign's real question.**
11,585 cases in seven profiles, each pinning one or two rigid blocks and
leaving 27 or 42 of 57 vertices free. Refuting one is close to the original
problem. The only way through is structural, not computational: a lemma that
makes whole profiles vacuous. The sharpest version, which would kill all
11,585 at once, is that no triangle-free 4-colouring of `K_58` has a vertex with
two colour-degrees `≤ 14` (equivalently: at least three of the four degrees at
every vertex are `≥ 15`). Note what that would imply — the only surviving
profiles would be `(15,15,15,12)`, `(16,15,15,11)`, `(16,16,15,10)` and
`(16,16,16,9)` — exactly the four the campaign already treats as reachable
(two closed by computation, two carried entirely by historical evidence). It is
a conjecture, unmeasured and unproved, and the three verified K_50 colourings
in `artifacts/` have profiles like `(16,11,11,11)`, so its naive generalisation
is false at n = 50. Treat it as the thing to test, not the thing to assume.

**B. The throughput pass, if the person wants a bigger number.**
20,166 cases in `(15,15,15,12)`; the retry tier closed 14/15 and 8/10 in
samples. 20,166 × 70 s ≈ 390 CPU-h ≈ 33 h wall on 12 cores, emitting ~480 GB of
DRAT (deleted as it goes). Exact command in README under that bullet. This
takes the cover to ~85% and moves no bound.

**C. The two missing proof stores.** 1,743 historical rows need the 34 shards;
401 exclusions need their scope arguments written down. Both were asked of the
person and never answered. `tools/import_historical.py` is tested only against a
synthetic index.

**D. The Lean side.** `lean/build.sh` is green in 20 s and every public theorem
is axiom-clean (`[propext, Classical.choice, Quot.sound]`). The threshold layer
is finished: `root_plan_arm` is unconditional at every balanced root of a
triangle-free 4-colouring of `K_58`. What is missing is the **marking lemma**
(root pinning, palette quotient, support embeddings, assembly) and the semantic
bridge at n = 58, which the pinned upstream repository does not have — it ships
`UniformK60`/`UniformK61` only. `Templates.Classified n` is stated, not proved.
The marking lemma is months of work and remains the critical path to a theorem.

## Traps that cost real time here

* **The shell runs with `errexit`.** `cmd; rc=$?` aborts the script on a
  non-zero exit. Use `cmd || rc=$?`, and `{ ls dir || true; }` for probes.
* **Every bundle script resolves `case-ledger.jsonl.gz` relative to cwd.**
  Pass `--ledger` and `--root` explicitly or it dies with `FileNotFoundError`.
* **`run_cover.py --tier retry` needs a saved *first* receipt** with status
  OPEN; a never-attempted case is skipped as `NO_OPEN_FIRST_ATTEMPT`. Use
  `--tier both` for fresh cases.
* **drat-trim has no default time limit** (40000 s). A hard case can stall a
  shard for hours on a multi-hundred-MB proof. Patch with
  `tools/patch_run_cover_timeout.py <bundle>/run_cover.py` (adds `-t 300` and
  lets a failed check leave the case OPEN).
* **The python-sat pin is load-bearing** (`1.9.dev22`): the CNF is regenerated
  through `pysat.card.CardEnc`. Use `.scratch/k58/.venv`.
* **Only a replayed DRAT against the regenerated CNF counts.** A timeout, a
  budget exhaustion, a min-conflicts failure, or a plausible argument is not
  evidence. Lean: no kernel check, no claim; `native_decide` drags in axioms.
* `.scratch/` is a cache that ages out — put nothing there you need tomorrow.
  `.scratch/k58` currently holds the unpacked bundle and a patched `run_cover.py`.
* **Disk.** 135 GB free, but 57 GB of the repository directory is earlier
  work: `.ultramath/` 40 GB (five old swarm directories, the largest
  `smwikrjou` at 17 GB) and `.scratch/` 17 GB (`k60ref` 7.6 GB, `circ` 6.4 GB).
  None of it is needed to run anything here; none of it is yours to delete
  without asking. `.git` is 405 MB because an early commit carried evidence
  trees.

## How to work here

The person cares about the work being right more than about it being finished,
and the two places that has bitten are overclaiming and padding. Concretely:

* **Lead with the outcome.** If the number did not move, the first sentence says
  so. No warm-up.
* **Quote numbers from the artefact**, with the file or command that produced
  them, and keep the units honest (CPU-s vs wall, "no certificate" vs "no
  closure").
* **Say what you did not run.** In the reply, not a footnote. "The tests did not
  run" belongs in the answer.
* **When an earlier conclusion was measured on a subset, test the rest before
  repeating it.** Both of the last two sessions found the previous claim
  overreaching in exactly that way — 469 cases generalised to 12,054, and a
  certificate-size figure carried over from easy cases by 10×.
* **Correct yourself in public, in the file and in the reply.** The README's
  storage estimate was wrong by 10×; fixing it was worth more than the
  measurement that found it.
* **No cheerleading, no "great question", no summary of what you are about to
  do.** One sentence of "this worked" when it works, then the next thing.
* **A decision that is theirs stays theirs**: compute spend, direction, risk,
  anything that costs days or disk. Put it as one clear question and stop;
  don't start a 33-hour run to be helpful.
* **Commit and push as you go**, so work leaves the context window. Archives go
  to the person in chat, never into the repository. Never rewrite history on
  this repo; never force-push.
* When something is genuinely interesting, say so once and briefly. It is
  rarely the thing you have just done.

## Open questions put to the person, still unanswered

1. Which way on the wall — spend the 33 h on `(15,15,15,12)`, or attack the
   structural lemma? (Most recent, open.)
2. Supply the 34 historical shards, or their path, so `import_historical.py run`
   can execute.
3. The scope of the 401 exclusions.
4. Whether to rewrite history to drop the evidence blobs that make `.git` 405 MB.
5. Certificate format for a public release: DRAT only, LRAT, or regenerate.
