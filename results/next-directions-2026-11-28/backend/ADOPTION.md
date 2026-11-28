# Adoption boundaries and the fail-closed admission contract

Companion to `README.md`. Everything here is derived from the receipts in this
directory; nothing in this file changes production. No file outside
`.ultramath/smx0er1f6/m6/` was modified (`git diff --stat` is empty, and
`.ultramath/` is git-ignored).

## 1. Trust table

| claim | evidence class | artefacts | can a coordinator rely on it? |
|---|---|---|---|
| `py195` reproduces the accepted KMT baseline counters on the retained cube | independent re-run, exact counter identity | `receipts/01-…`, `receipts/06-…` vs `results/next-directions-2026-11-28/kmt/bench/01-stock-s0.json` | yes, as a harness cross-check |
| All three engines are deterministic on these CNFs at fixed seed | repeated seed-0 runs, identical conflicts/decisions/propagations, in two separate time windows (phases 1→4) | `receipts/`, `receipts-phase2/`, `receipts-phase4/` | yes |
| `cad212` uses ~6.5 % less process CPU and ~42 % less peak RSS than `py195` on OPEN leaves at a matched 100k conflict cap | 7 leaves × paired runs, geometric mean 0.935, RSS lower on 7 of 7, drift-controlled | phases 1 and 3 | yes for the memory part; CPU part is above ±5 % noise only in the mean |
| `cad212` needs more conflicts than `py195` on closed leaves | H8 measured here (49,226 vs 32,316); H7 in the retained bank (23,143 vs 19,433) | `receipts/14-…`, `.scratch/k58-0404-word-search/H7-word0-result.json` | yes, both directions of the direction agree |
| `kis404` is not a portfolio win on this family | C1/C2/C3 computed, 8 matched cases | `receipts-phase2/`, `analysis.json` | yes, for this family at these caps |
| conflict caps are not a portable budget | 2.04× propagations per conflict | `refs phase 1` | yes |
| a cap-OPEN is seed-sensitive | 4 seeds × 2 cases × 2 engines; one seed fails to close what another closes at 14,492 | `receipts-phase4/` | yes, on H8; not on H7 |
| H7 and H8 are refuted | fresh proofs, `drat-trim` rc 0 + `s VERIFIED` + read-bytes == size, BCP non-vacuous | 30 verified receipts | yes, **for those two exact CNFs only** |

What this table does **not** establish: any engine ranking on the retained
request (it never closes), any closure of a wall profile, `ChainReady`, or a
Ramsey bound. `OPEN` at a cap is recorded as `OPEN` everywhere.

## 2. Fail-closed admission contract (proposed, no code change needed)

Any future backend/encoding/scoring proposal for this pipeline should be
admitted only with a receipt that satisfies all of:

1. **Byte identity.** The exact CNF (or the exact parent+cube) is pinned by
   sha256 and re-checked immediately before the run. A run on different bytes is
   a different experiment.
2. **Fresh artefact.** The proof/model must be created by that run; a file that
   already existed is not evidence, even if it verifies.
3. **Full replay.** `drat-trim` exits 0, prints `s VERIFIED`, **and** reports
   parsing exactly the file's byte count. A valid prefix followed by junk is a
   failure. (`engine_conformance.certify_unsat` does not compare the byte count;
   the pipeline's `check_trace` does. Use the pair, or `panel.py::certify`.)
4. **Non-vacuity.** The CNF must not be closed by unit propagation alone
   (`bcp.py`); otherwise the certificate is vacuous and the run says nothing
   about search work.
5. **Determinism.** The same (engine, CNF, seed, cap) run twice must reproduce
   conflicts *and* decisions *and* propagations. Anything else is a sample, not
   a measurement.
6. **Currency.** Price in CPU (and peak RSS), not conflicts, unless the engines
   are shown to agree on propagations per conflict. Report both.
7. **Cap discipline.** A cap outcome is `OPEN`. It is never `UNSAT`, never
   "hard", and never a refutation of a sibling.
8. **Scope statement.** Every determined verdict carries the hash of the formula
   it refutes and one sentence saying what it does *not* imply.

`panel.py` implements 1–7 as executable checks: it refuses to run on a hash
mismatch, refuses to record UNSAT without a fresh, fully-read, non-vacuous
proof, records `UNSAT_UNPROVEN_NOT_COUNTED` when no proof was requested, and
writes every counter it used.

## 3. Concrete caller-side changes worth considering (not applied)

These are *policy* suggestions for whichever session owns the campaign knobs.
None of them touches `run`, `finalise`, encoders, ledgers or a default.

* **Re-seed before re-capping.** When a closure-critical leaf returns `OPEN` at
  the conflict cap, a second seed costs ~1–3 s and moved the incumbent from
  `OPEN at 60,002` to `14,492` on `H8-word0` (Phase 4). Raising the cap is the
  expensive version of the same experiment. Suggested shape: `seed ∈ {0,1,2}`
  under a fixed cap, stop at the first verified refutation, and record which seed
  closed — never merge the seeds' counters.
* **Prefer `--engine native` when memory is the binding constraint.** On the
  seven OPEN leaves measured here it is 0.935× the incumbent's CPU and 0.53–0.59×
  its peak RSS, with bit-identical counters on repeat. That is a memory policy,
  and it is what `NATIVE.md` may say with evidence. It is *not* a conflict-count
  or certificate-cost win, so it should not be promoted on those grounds.
* **Do not add Kissat behind the same conflict cap.** 2.04× the propagations per
  conflict means a shared cap is not a shared budget; if Kissat is ever added as
  a second opinion, its cap must be priced in CPU seconds. Keep its present role
  (independent oracle, smallest proofs) unless a closure-side experiment is
  pre-registered and passes C1–C3 with more than one case.
* **Record the seed in every leaf receipt.** Phase 1's seed-1 `OPEN` on an
  already-closed leaf is exactly the kind of record that makes a later "this leaf
  is hard" claim checkable.

## 4. Reproduction

All commands run from the repository root, sequentially, and write only inside
this member's directory:

```sh
M=.ultramath/smx0er1f6/m6
python3 -B $M/panel.py          # phase 1, 24 runs, ~65 s CPU (resumable: --resume)
python3 -B $M/phase2.py         # phase 2, 20 runs, ~65 s CPU
python3 -B $M/phase3.py         # phase 3,  8 runs, ~29 s CPU
python3 -B $M/phase4.py         # phase 4, 16 runs, ~23 s CPU
python3 -B $M/analyze.py        # recompute every rule outcome -> $M/analysis.json
```

Each script re-verifies the pinned sha256 of every executable and every CNF
before it launches anything, reuses an existing receipt only when explicitly
resumed, and stops launching new runs once its CPU guard is exceeded. Proofs and
solver logs are large and live in the ignored `.scratch/runs/`; the durable
receipts are the small JSON files in `receipts*/`.

`python3 -B $M/smoke.py` re-runs the 2,000-conflict plumbing control that
produced the early-trajectory comparison in `README.md` §Phase 1. It is a
plumbing check, not evidence about engines.

## 5. Files

| path | role |
|---|---|
| `PRE-REGISTRATION.md`, `PHASE2..4-PRE-REGISTRATION.md` | written before each phase; the rules the numbers are judged by |
| `panel.py` | harness: pinning, one-process-per-run, CPU/RSS, proof certification, budget guard |
| `phase2.py`, `phase3.py`, `phase4.py` | the three bounded extensions |
| `analyze.py`, `analysis.json` | every rule outcome computed from receipts |
| `receipts/`, `receipts-phase2/`, `receipts-phase3/`, `receipts-phase4/` | one JSON per run + `all-runs.json` |
| `smoke.py`, `receipts/smoke/` | 2,000-conflict plumbing control, not evidence of anything except trajectory identity |

Raw-artefact retention: the 30 proofs of the 30 refutations are kept under
`.scratch/runs/*.drat` and each was re-hashed against its receipt after pruning
(30/30 match). Proofs of runs that ended `OPEN` at the cap were deleted after
their sha256 and byte count were recorded, because a truncated trail carries no
verdict; those receipts still hold `proof_sha256`, `proof_bytes` and the solver
log. 197 MB total, no file above 18 MB.
