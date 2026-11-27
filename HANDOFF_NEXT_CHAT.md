# Handoff — the next chat starts here

Written at the end of the session of 21 November 2026 that measured the wall.
Read this first, then [README.md](README.md) for the map of the repository.
[HANDOFF.md](HANDOFF.md) is the earlier cold-start brief — bundle provenance,
the eight-direction audit, the Lean core — and its status tables are stale; a
dated block at its top says which numbers to ignore.

## Where the work stands

`R(3,3,3,3) ∈ [51, 62]` (Radziszowski DS1.18). **Nothing has moved the bound.**

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
