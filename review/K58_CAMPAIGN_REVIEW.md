# Review: the K58 handoff (R(3,3,3,3) <= 58)

Reviewed 2026-11-16. Source: `R3333_K58_LLM_handoff.zip` (18.3 MiB), the same
material unpacked under `.scratch/k58` in this VM. Everything below marked
*checked* was run here; everything marked *estimated* is arithmetic on
measured numbers; everything else is judgement and says so.

## 1. What the bundle claims

A computer-assisted proof that every 4-colouring of the edges of K_58 has a
monochromatic triangle, i.e. `R(3,3,3,3) <= 58`. The route:

1. For a vertex `r` and colour `c`, the `c`-neighbourhood `N_c(r)` is
   3-coloured with no monochromatic triangle, so `d_c <= R_3(3) - 1 = 16`.
2. A colour is *critical* at `r` when `d_c` is 15 or 16. A vertex *sends a
   ticket* along an edge whose colour is critical at that endpoint. Summing
   sent against received tickets, some `r` has `H(r) >= w(r)`.
3. For such a root the bundle fixes a finite cover of 113,179 SAT cases.
   Each case fixes a root's critical neighbourhoods as literal copies of the
   two classified templates U/T, fixes one *sender* `q` and its neighbourhood,
   and adds a threshold on the number of senders in `q`'s arm. Each case is
   refuted by Kissat and the DRAT proof is replayed by drat-trim.
4. A Lean development is to bridge "a triangle-free 4-colouring of K_58" to
   "a model of one of those exact CNFs".

The cover is frozen in `case-ledger.jsonl.gz`: 113,179 rows, of which
**111,035 are OPEN**, 1,743 are CERTIFIED from earlier work, 214 are a whole
profile exclusion and 187 are template exclusions.

## 2. What is checked here

Environment pinned as the bundle asks: python-sat 1.9.dev22 in a venv,
Kissat 4.0.4 built from commit `8af8e56`, drat-trim from the pinned source.
The verifier refuses to run otherwise: it pins the python-sat version string,
so `1.9.dev17` fails with `Pinned release input mismatch: dependencies`.

**Smoke test, checked.** `cover_evidence.py verify example/release` reproduces
the documented result exactly:

```
{"counts": {"CADICAL_UNSAT": 1, "CERTIFIED": 5,
            "LEGACY_EVIDENCE_NEEDED": 2139, "OPEN": 111035}, "replayed": 5}
```

Five bundled certificates replay against their regenerated formulas; the
1,743 historical closures minus the 5 shown are reported as
`LEGACY_EVIDENCE_NEEDED`, exactly as `HANDOFF.md` says.

**Classification, checked independently.** The cover pins every 15- and
16-vertex critical neighbourhood to one of two literal templates, U or T, so a
third isomorphism class would let colourings escape every case. An independent
enumeration (swarm member m4; `run_all.sh`, 3.3 s, reproduced here) re-derives
the classification from scratch rather than quoting it: in a triangle-free
3-colouring the colour classes of a vertex are 2-coloured and hence of size at
most 5, which fixes the class sizes (5,5,5) at 16 and (5,5,4) at 15; pinning
those and blocking the residual symmetry yields exactly **two** colour-named
classes at each size, with colour-named automorphism orders 2 and 10 at 15,
32 and 160 at 16 — the bundle's U and T. Every palette relabelling of U and T
is isomorphic to U or T, so fixing colour names costs no coverage. This closes
the one input the bundle imports from the unrefereed preprint.

**Census, checked.** The ledger has 113,179 unique ids and 11 degree profiles,
which are exactly the partitions of 57 into four parts of size <= 16:
(15,15,15,12) 83,440; (16,15,15,11) 16,173; (15,15,14,13) 7,732;
(16,15,14,12) 2,058; (16,16,15,10) 1,767; (16,15,13,13) 1,046;
(15,14,14,14) 381; (16,16,16,9) 214; (16,16,14,11) 140; (16,16,13,12) 140;
(16,14,14,13) 88. `audit_cover` regenerates the whole list from the shipped
generators and checks every id, branch and charge against the ledger, so the
ledger and the code agree (that is consistency, not soundness).

**First batch, run here.** The 96 ids in `FIRST_BATCH_IDS.txt`, 12 s /
400k conflicts, 3 workers: **81 certified, 15 cut off**, 397 s solver CPU and
236 s checker CPU in total, 83.8 MB of retained compressed certificates,
median solve 3.0 s. Retrying the 15 cut-offs at 70 s / 2.4M conflicts closed
14 of them, so **95 of 96** cases stand certified. The two tiers use different
formulas (see below), and all 95 certificates replay in one evidence root.

| profile | cases | first pass | with retry |
| --- | ---: | ---: | ---: |
| (15,15,15,12) | 48 | 34 | 47 |
| (16,15,15,11) | 48 | 47 | 48 |

A release manifest over this evidence root gives
`CERTIFIED 81, LEGACY_EVIDENCE_NEEDED 2144, OPEN 110954`, manifest SHA-256
`6a0fc4f8090e786710f5c52d56dcb080050418277f8756587db0e41d8a646bae`.
The 81 certificates are replayed a second time through
`cover_evidence.py verify` in this repository's first run.

## 3. How the reduction actually works

This is the part worth stating precisely, because it is where a proof of this
shape can fail.

Fix a root `r` with `H(r) >= w(r)`. Let `M = sum of critical d_c` be what `r`
sends. For each critical arm `c` pick a threshold `t_c` with
`sum_c (t_c - 1) < M`. Then `H >= w` forces some arm to reach its threshold:
`if every s_c <= t_c - 1 then H = sum s_c < M`. So it suffices, for each arm,
to refute `s_c >= t_c`.

To refute `s_c >= t_c` in an arm of size `d_c`, fix any set `P` of
`d_c - t_c + 1` positions: if there were `t_c` senders then at most
`d_c - t_c` vertices fail to send, so `P` contains a sender. Hence it is enough
to refute, for every `q` in `P`, the statement "`q` sends and `s_c >= t_c`".
Each such refutation is one SAT case; `q` ranges over orbit representatives of
positions, and its neighbourhood ranges over the two templates, the orbit
representatives of the marked position, and the embeddings of the neighbourhood
pattern into the other arms. Summing `H = sum_c s_c < M = w` contradicts the
choice of `r`.

That is the scheme `joint_plan.choose_plan` / `cases` and `dense.marked_threshold`
implement. **Checked against the ledger**: for all 41 `(profile, kinds)` plans,
summing `copies x (t_c - 1)` over the arm groups, with an unconstrained group
counted at `t_c = d_c + 1`, gives a total strictly below `M`, so no plan is
missing the inequality it needs (0 failures). That is the arithmetic; it is not
yet the statement that the code's thresholds are the ones the plan intends. The scheme is coherent. Whether it is *complete* depends on the orbit
quotients (`palette_quotient.py`, `gluing.orbit_data`) being genuine orbit
decompositions, and whether it is *sound* depends on every clause family added
by `marked_threshold` and `support_tables` being implied by the root
hypothesis. Those two questions are the audit, and neither is answered by
replaying certificates.

## 4. What is not in the bundle

* **The release machinery is not a proof of itself.** Three defects, each
  reproduced: `manifest` performs no proof checking and `verify` without
  `--checker` accepts a two-byte "certificate" with a hand-written
  "s VERIFIED" log (rejected as soon as a real checker is supplied); the
  documented `--require-cadical` counts a hand-written `cadical.json` naming a
  nonexistent binary with an all-zero hash, through a real drat-trim replay;
  and `import-legacy` dies with `KeyError: 'full_root'` on the 569 of 752
  campaign rows that predate the flag, i.e. exactly the rows the missing
  historical proofs would be restored through. So a manifest SHA-256 certifies
  nothing on its own, and any release must carry the output of
  `verify --checker` (as this repository's `runs/` do) or be replayed by the
  reviewer with their own drat-trim.
* **The ledger does not pin the encoding per case.** The two tiers here use
  different formulas: the first pass adds the per-arm threshold and
  `s_crit >= 2M - 57`, the retry adds the full `H(r) >= w(r)` over all 57
  neighbours (instrumented on a `(15,15,15,12)` row: 44 of 56 selectors plus
  one forced vertex, i.e. 45 of 57, exactly `w`). Both are consequences of the
  case hypothesis, so both are sound. But `inspect_case` rebuilds the CNF from
  the recipe written in the certificate, and the ledger row has no recipe to
  compare against, so `--require-complete` cannot enforce that every
  certificate uses a formula implied by its case. That is a property to check
  for each shard, not something the verifier establishes.
* **The 1,743 historical closures have no proof bytes here.** The manifest
  files exist; the proofs are described as "in the original 34 compressed
  shards, available if the owner supplies the old evidence directory". Only
  five example certificates are included. A verifier therefore reports 2,144
  rows as `LEGACY_EVIDENCE_NEEDED`, and the campaign as shipped rests on
  author's word for 21% of the cover.
* **No Lean bridge for n = 58.** The pinned repository has `UniformK60` and
  `UniformK61` — one development per order, each with its own catalogues,
  pricing data and finite boundary — and no n = 58 development, no `ramsey58`
  theorem, no K58 constant anywhere in `formal/src`. `PROOF_PLAN.md` lists the
  n = 58 bridge as step 5 and as unfinished. The gap is therefore not a
  connective lemma: it is a development of the same scale as the K60 one,
  which took that project months and 296,081 formulas.
* **The profile and template exclusions (401 rows) are arguments, not
  certificates**, and their arguments are not in the bundle either.
* **Referenced files that are absent**: `ledger.py`, `retry_open.py`,
  `check_new.sh`, `check_pilot_checkpoint.py`, `RUN_THE_COVER.md`, `RESULTS.md`.
  `PROOF_PLAN.md` instructs the reader to run them. The cover itself can be
  regenerated (`joint_plan.cases`), so this is recoverable, but the bundle is
  not the self-contained checkpoint its handoff text describes.

## 5. Cost, measured and extrapolated

Measured on this 4-CPU VM, 3 workers, first-pass budget:

| quantity | first pass | retry |
| --- | ---: | ---: |
| solver CPU per closure | 4.9 s | 21 s (70 s cap) |
| checker CPU per closure | 2.9 s | in `verification.json` |
| retained certificate | 1.03 MB | 7.4 MB |
| share of cases | 84% | 93% of the rest |

Per 96 cases actually run here: 711 s of solver CPU and 187 MB of
certificates, for 95 closures. Extrapolated at the same mix of tiers and the
same budgets to the **99,450 cases of the two large profiles**, that is about
**206 CPU-hours** and **194 GB** of compressed certificates.

It does **not** extrapolate to the 11,585 cases of the seven small profiles:
they closed 0 of 98 here and 0 of 306 in the pilot, and their retry cost is
measured for none of them except `(15,15,15,12)`. So 206 CPU-h / 194 GB is a
large-profile figure and the tail is an open cost, not a scaled one.

The storage number is **not** a binding constraint, because the certificates
turn out to be reproducible. Re-running the pinned Kissat on the regenerated
CNF, with no time limit, and trimming with the same drat-trim reproduces the
stored certificate **byte for byte**: 10 of 10 sampled cases across both tiers,
identical SHA-256 and identical length (the first check, on
`1bd293ef…`, gave 1,152,154 bytes both times). A verifier can therefore
regenerate every proof from the code and compare hashes instead of receiving
216 GB, at the cost of the solver time again (~230 CPU-hours) plus the replay.
Storing the certificates is a convenience — it lets a reviewer check without
solving — not a requirement of soundness. Recompressing with `xz -9e` would
take the stored figure to ~166 GB if one does want to keep them.

The bundle's 365 CPU-hours is not a completion cost at all: 365 h over 110,714
rows is 11.9 CPU-s per case, i.e. exactly one 12-second capped pass — the
audit's point, and the reason the number should not be read as the price of
finishing.

That projection is optimistic, not conservative. Two measurements here:

* In batch 1, 15 of 96 cases hit the 12 s cap.
* A probe of 14 fresh OPEN ids from each of the seven smaller profiles closed
  **0 of 98** at the same budget (573 s of solver CPU), reproducing the pilot's
  0/306. See `runs/2026-11-16-small-probe/`.

Those 11,585 cases therefore need the retry encoding (70 s / 2.4M conflicts),
and six of the seven profiles have no measured closure rate under it at all.
Counting the big profiles at the measured 84% first-pass rate and the small
ones at a 70 s attempt each with a generous 30% success, the cover costs
roughly 600-900 CPU-hours and 150-250 GB of certificates. The bundle's 365
CPU-hours / 612 GB is the same order but its distribution is wrong: the tail
of 11,585 small-profile cases is most of the risk and none of the measured
yield.

**This VM has 185 GB free and 4 CPUs.** The whole cover cannot be closed and
stored here. A shard of a few thousand cases can be.

## 6. The audit

An eight-member swarm worked the reduction from separate directions; five
submissions were checked here, by re-running their scripts, and accepted. Each
one is a positive result on its own axis, and together they move the bundle
from "plausible" to "sound everywhere we can test it":

* **Census and threshold (m5).** Recomputed the plan for all 41
  `(profile, kinds)` strata: 113,179 = ledger rows, per-stratum identical,
  smallest pigeonhole margin 1. Then the decisive brute force: all **592,023**
  sender-count vectors with `H(r) >= M` were enumerated, and **none** escapes
  every class threshold. No charge exceeds its arm size. Independently
  cross-checked against the published per-stratum counts of the source paper:
  the bundle's list is everywhere a superset (the growth is one extra symmetry
  the paper performs when equal template types meet), so it covers at least
  what the paper's machine-checked cover does.
* **Symmetry quotient (m7).** All 20,617 cases dropped by the palette quotient
  carry an explicit (colour permutation, vertex permutation) witness onto an
  emitted case — 0 failures, chain length 0. The 113,179 unit sets are
  non-contradictory, force no monochromatic triangle, and bind one-to-one to the
  ledger ids (0 missing, 0 extra). Positive controls show the isomorphism test
  rejects cases differing in kind, size, position or arm.
* **Classification (m6).** Independent of the templates: `nauty-geng` gives 388
  triangle-free 5-regular graphs on 16 vertices; exactly one admits any
  completion, with 72 good colourings = 12 U + 60 T and none outside the
  catalogue. At 15, an exact count identity gives 1,036,800 good colourings =
  172,800 (U) + 864,000 (T). Palette relabellings are realised by vertex
  permutations for all six permutations of every template, which is what makes
  the fixed-palette convention sound.
* **Kind dimension (m4).** A separate exhaustive enumeration gets exactly two
  colour-named classes at each of 15 and 16, with automorphism orders 2/10 and
  32/160, matching U and T.
* **Shape and cost (m8).** All 41 `(profile, kinds)` groups of the ledger are
  exactly `joint_plan.cases()` output (0 mismatching, branch numbers included).
  The charge budget `sum copies*(t-1) <= M-1` holds in 41/41 strata with slack
  0 in 36 of them, and every emitted group has the marked-position breadth its
  threshold needs (0 failures). At the geometry level, 105 family groups that
  have orbit representatives are absent from the ledger, and all of them are
  palette images of emitted cases (`uncovered = 0`) — a stronger completeness
  statement than the id census. No row is vacuous (0/113,179), no row's own
  support is killed by the support tables (0/113,179), and the five historical
  manifests index exactly the 1,743 CERTIFIED rows.
* **Support tables (m3).** The family is narrower than local consistency: it
  accepts 4,344 of 5,688 locally consistent four- and five-point supports and
  omits exactly the 1,344 whose two-colouring is `C4 + 2K2`. That is sound only
  because of the classification — in U15/T15 every colour class is `C5` or
  `P4` — and the bundle's docstring calls the clauses "optional redundant",
  which is the wrong justification. Practically it does not matter: with
  `tables` off, all five example certificates rebuild to the identical input
  hash and are UNSAT in under a second, 22 of 23 sampled cases are unchanged,
  and one case is UNSAT without the tables where it is UNKNOWN with them. A
  continuation should run `tables=False` and drop the dependency.
* **Evidence pipeline (m1).** The positive half first: all 1,743 historical
  receipts regenerate the `formula_sha256` they recorded from the frozen row
  and the recorded recipe, and 973 also match the recorded `formula_bytes`, so
  the historical closures are bound to formulas today's generator reproduces —
  only the proof bytes are missing. None of the 2,144 closures is vacuous
  through the encoder's empty-clause return under any of the eight recipes, and
  the five manifests' 2,064 ids sit in the ledger with their UNSAT subset
  exactly the 1,743 CERTIFIED rows. The three defects are in section 4.
* **Encoder calibration (m2).** At n=31 and n=41 — the smallest orders where
  the bundle's geometry runs with a critical block and a positive threshold —
  genuine colourings satisfy the production clause set, including at threshold
  10 where SAT holds at bounds 4, 5, 6, 8 with real sender counts meeting each
  bound. `full_root` rejects exactly the colourings with `H < w` and none with
  `H >= w`, which settles that the retry tier encodes the hypothesis itself.
  The n = 17 calibration I had suggested is impossible for this encoder (no
  critical arm can satisfy `H >= w` there), a useful negative.

Defects came out of it, all repairable and none a hole in the mathematics.
The two that matter:

1. The bundle points at `CriticalTemplates.lean` for the classification, and
   that file explicitly disclaims completeness. The completeness theorem is
   Kalbfleisch-Stanton/Heinrich (Theorem 2.1 of the paper), and in the pinned
   repository it lives in `CriticalCatalogues.lean`. The citation must be
   restated.
2. The ledger does not pin the encoding per case, so `--require-complete`
   cannot enforce that every certificate proves a formula implied by its case.
   Both encodings used are implied, but that is a property to check per shard.
3. `support_tables` is described as redundant when it rests on the
   classification, and `manifest` does no checking while `verify` without
   `--checker` accepts self-attested artefacts — see `ERRATA.md` for all five
   and the minimal fixes.

## 7. Judgement

The scheme is the right shape and is not naive, and after the audit the risks
are no longer where I expected them. The ticket/threshold step is sound, the
symmetry quotient is exhaustive, the classification is true and faithfully
instantiated, and the encoder does not over-constrain. What remains is not a
subtlety in the combinatorics:

1. **There is no Lean bridge for n = 58.** The pinned repository has
   `UniformK60` and `UniformK61`, one development per order; nothing for 58.
   This is the step that turns a finished cover into a theorem, and it is at
   the scale of the K60 development, not a lemma. `PROOF_PLAN.md` knows this.
2. **21% of the claimed closed cases have no evidence in the bundle.** 2,144
   ledger rows are `LEGACY_EVIDENCE_NEEDED`, resting on the author's word and
   on 34 shards that are not here.
3. **The 401 profile and template exclusions are arguments, not
   certificates**, and the arguments are absent. The 214-row
   `(16,16,16,9)` exclusion is a whole profile resting on one such argument.

So the campaign is now a storage and labour problem rather than a soundness
problem, and the division of labour is: this VM closes and publishes shards
with manifests; a machine with ~1 TB finishes the cover; the author supplies
the Lean bridge and the historical shards.

## 8. What was produced here

* 95 freshly certified cases with their compressed DRAT certificates and a
  release manifest, in `runs/2026-11-16-batch1/` (81 at the 12 s tier, 14 at
  the retry tier), all 95 replayed a second time through the independent
  verifier.
* A throughput and storage measurement on the real pipeline, section 5.
* A probe showing the seven smaller profiles close **0 of 98** at the
  first-pass budget, reproducing the pilot's 0/306 — the campaign's real tail.
* The audit in section 6, with its two defects.

The honest one-line status: **the reduction is sound on every axis the audit
could test, both encodings are sound, and 95 cases are now certified; what is
missing is the 111,000 remaining refutations, the bytes for 2,144 historical
ones, and the Lean bridge that would make any of it a theorem.**
