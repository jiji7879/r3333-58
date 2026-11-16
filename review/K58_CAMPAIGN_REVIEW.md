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
median solve 3.0 s.

| profile | cases | certified |
| --- | ---: | ---: |
| (15,15,15,12) | 48 | 34 |
| (16,15,15,11) | 48 | 47 |

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
implement, and the arithmetic above checks out against the thresholds in the
ledger. The scheme is coherent. Whether it is *complete* depends on the orbit
quotients (`palette_quotient.py`, `gluing.orbit_data`) being genuine orbit
decompositions, and whether it is *sound* depends on every clause family added
by `marked_threshold` and `support_tables` being implied by the root
hypothesis. Those two questions are the audit, and neither is answered by
replaying certificates.

## 4. What is not in the bundle

* **The 1,743 historical closures have no proof bytes here.** The manifest
  files exist; the proofs are described as "in the original 34 compressed
  shards, available if the owner supplies the old evidence directory". Only
  five example certificates are included. A verifier therefore reports 2,144
  rows as `LEGACY_EVIDENCE_NEEDED`, and the campaign as shipped rests on
  author's word for 21% of the cover.
* **No Lean bridge for n = 58.** The pinned K60 repository has a real Lean
  development (296,081 formulas, classification checked, axioms
  `propext, Classical.choice, Quot.sound`), but it proves the n = 60 statement.
  `PROOF_PLAN.md` lists the n = 58 bridge as step 5 and as unfinished. Without
  it the campaign, even completed, yields "no colouring found", not a theorem.
* **The profile and template exclusions (401 rows) are arguments, not
  certificates**, and their arguments are not in the bundle either.
* **Referenced files that are absent**: `ledger.py`, `retry_open.py`,
  `check_new.sh`, `check_pilot_checkpoint.py`, `RUN_THE_COVER.md`, `RESULTS.md`.
  `PROOF_PLAN.md` instructs the reader to run them. The cover itself can be
  regenerated (`joint_plan.cases`), so this is recoverable, but the bundle is
  not the self-contained checkpoint its handoff text describes.

## 5. Cost, measured and extrapolated

Measured on this 4-CPU VM, 3 workers, first-pass budget:

| quantity | per closed case |
| --- | ---: |
| solver CPU | 4.9 s |
| checker CPU (trim + replay) | 2.9 s |
| retained certificate | 1.03 MB |

The 111,035 open cases therefore cost, *if every one closed at first pass*,
about **240 CPU-hours** and **114 GB** of compressed certificates. At 4
workers that is roughly 60-70 hours wall. The bundle's own projection (365
CPU-hours, 612 GB) is larger because it retains raw proofs and exact CNFs as
well; the certificate figure is the irreducible one.

That projection is optimistic, not conservative: 15 of 96 cases hit the 12 s
cap, and the pilot reported 0 closures in 306 sampled cases from the seven
smaller profiles. Retries run at 70 s / 2.4M conflicts on a changed encoding.
A realistic full campaign is several hundred CPU-hours and 150-250 GB.

**This VM has 185 GB free and 4 CPUs.** The whole cover cannot be closed and
stored here. A shard of a few thousand cases can be.

## 6. Judgement

The scheme is the right shape and is not naive: it reuses the K60 project's
Lean-checked classification of the 15- and 16-vertex neighbourhoods, and the
ticket/threshold reduction is the standard one. The engineering around it is
better than usual — pinned versions, case ids by content hash, trimmed proofs
replayed on regenerated CNFs, a manifest that binds the census.

Three things would stop me spending the 240 CPU-hours today:

1. **The reduction at n = 58 is new code and is not formalised.** The K60
   development proves the n = 60 boundaries; nothing in it covers the eleven
   n = 58 profiles, the per-arm thresholds, or the n = 58 marked cover. A
   completeness bug in `palette_quotient`/`orbit_data` would silently drop
   cases and every closure would still verify.
2. **The case split is not independently reproduced.** `audit_cover` compares
   the ledger with the same generators that produced it.
3. **21% of the claimed closed cases have no evidence in the bundle**, so even
   a complete run of the remaining 111k would leave the ledger's `CERTIFIED`
   column resting on trust.

If those clear, the campaign is a storage problem, not a mathematics problem,
and the natural division of labour is: this VM closes and publishes shards with
manifests; a machine with ~1 TB finishes the cover; the author supplies the
Lean bridge and the historical shards.

## 7. What was produced here

* 81 freshly certified cases with their compressed DRAT certificates and a
  release manifest, in `runs/2026-11-16-batch1/`.
* A throughput and storage measurement on the real pipeline, section 5.
* An eight-member audit of the reduction, encodings and orbit quotients,
  running separately; its findings are appended when it reports.

The honest one-line status: **the pipeline runs and its arithmetic is
consistent; the proof it is part of does not yet exist, and the part that
would make it a proof is the part nobody has checked.**
