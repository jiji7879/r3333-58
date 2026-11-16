# Handoff — `R(3,3,3,3) ≤ 58`

**Provenance.** The K58 bundle (`R3333_K58_LLM_handoff.zip`, 113,179-case cover)
was produced by ChatGPT and handed over for continuation. This document is the
state after a session of verification, an eight-direction audit, and a Lean
formalisation of the reduction core. It is written to be read cold, by a
language-model session or a person, without re-deriving anything.

**Headline.** No bound has moved. `R(3,3,3,3) ∈ [51, 62]` (Radziszowski DS1.18);
the `≤ 60` claim is the unrefereed arXiv:2610.36648 with its own Lean
development. The K58 reduction is sound on every axis we could test, but it is
not a proof: there is no Lean bridge at n = 58, 2,144 ledger rows have no proof
bytes, and 111,035 cases are open. What is new here: 95 certified cases, a
measured cost model, six reproduced defects in the bundle, and a kernel-checked
Lean core of the reduction.

## 1. Status

| item | state |
| --- | --- |
| frozen cover | 113,179 cases: 111,035 OPEN, 1,743 CERTIFIED, 214 PROFILE_EXCLUSION, 187 TEMPLATE_EXCLUSION |
| proof bytes for the 1,743 | **absent** from the bundle (5 example certificates only) |
| cases closed in this session | **95** (81 at 12 s, 14 at retry), all replayed twice |
| measured cost per 96 cases | 711 s solver CPU, 187 MB certificates |
| full-cover projection | ~230 CPU-hours, ~216 GB; this VM has 185 GB free |
| reduction audit | 8 directions, 8 accepted, no unsoundness found |
| defects found | 6 (section 9) |
| Lean core | 10 theorems, kernel-checked, axioms `[propext, Classical.choice, Quot.sound]` |
| **what is missing for a theorem** | **the marking lemma**, the profile enumeration, and the 113,179-UNSAT premise |

## 2. What is verified (with the reproducing artefact)

1. **The pipeline works.** Pinned toolchain (Kissat 4.0.4 @ `8af8e56`, drat-trim
   @ `2e3b2dc`, python-sat **1.9.dev22**; the verifier refuses other versions).
   The bundled example replays exactly: `{"CERTIFIED": 5, "LEGACY_EVIDENCE_NEEDED": 2139, "OPEN": 111035}, "replayed": 5`.
2. **95 cases certified.** `runs/2026-11-16-batch1/`: manifest `cd112445…`,
   `verification.json` with `"replayed": 95`. 81 at the 12 s tier, 14 at the
   retry tier, 1 still open.
3. **The seven small profiles do not close cheaply.** `runs/2026-11-16-small-probe/`:
   **0 of 98** fresh cases closed at 12 s / 400k, reproducing the pilot's 0/306.
4. **The census is the planner's output.** All 41 `(profile, kinds)` groups of the
   ledger equal `joint_plan.cases()` (0 mismatching, branch numbers included).
5. **The pigeonhole is exhaustive.** All 592,023 sender-count vectors with
   `H ≥ M` hit some arm's threshold; none escapes.
6. **The symmetry quotient is sound.** All 20,617 palette-dropped cases carry an
   explicit (colour, vertex) permutation onto an emitted case, chain length 0.
7. **The classification is true and faithful.** `nauty-geng`: 388 triangle-free
   5-regular graphs on 16 vertices, exactly one completes, 72 colourings =
   12 U + 60 T, none outside the catalogue. K15: exact count 1,036,800 =
   172,800 + 864,000.
8. **The encoder does not over-constrain.** Calibrated on genuine colourings at
   n = 31 and n = 41; `full_root` rejects exactly the colourings with `H < w`.
9. **The historical formulas are exact.** All 1,743 receipts regenerate the
   recorded `formula_sha256` (973 also `formula_bytes`); only the proofs are missing.
10. **No case is vacuous** through the encoder's empty-clause return (all 2,144
    closed rows, all eight recipes).

## 3. What is blocking

1. **The Lean bridge at n = 58 does not exist.** The pinned repository has
   `UniformK60` and `UniformK61` — one development per order — and nothing for
   58. In particular the *marking lemma* (section 5.1) is unwritten: a sender in
   an arm that reached its threshold must be shown to realise one of the emitted
   cases, which requires the U/T classification, the palette quotient and the
   support embeddings in Lean.
2. **2,144 rows have no proof bytes.** The formulas regenerate, so restoring the
   proofs is mechanical — but the bytes live in 34 shards that are not here.
3. **111,035 open cases**, ~230 CPU-hours and ~216 GB against 185 GB free.
   Storage, not CPU, is the binding constraint.
4. **The tail.** 11,585 cases in seven profiles close at essentially zero rate at
   the first-pass budget; their retry cost is unmeasured for six of the seven.
5. **The release machinery is not self-certifying** (section 9, items 3–4).
   A manifest hash alone certifies nothing.
6. **The cover is audited, not formalised.** Eight audits are not a proof.

## 4. The Lean development (`lean/`)

Build: `cd lean && ./build.sh` (21 s, Lean 4.33.1 + Mathlib), then it prints the
axioms of every theorem. There is no `sorry`, no `native_decide`, no new axiom.

| theorem | content |
| --- | --- |
| `two_colour_six` | `R(3,3) ≤ 6` |
| `three_colour_seventeen` | `R(3,3,3) ≤ 17` |
| `deg_le_sixteen` | every colour degree of a triangle-free 4-colouring is ≤ 16 |
| `sum_w_eq_sum_H`, `exists_root` | tickets sent = received, so some root has `H ≥ w` |
| `w_eq_sum_critical`, `H_eq_sum_armSenders` | `w` = Σ critical degrees, `H` = Σ senders over the four arms |
| `profile_sum` | at any vertex of a triangle-free `K_58`: `Σ deg = 57`, each `≤ 16` |
| `exists_arm_reaches` | any threshold plan with `Σ (t a − 1) < Σ critical degrees` at every profile has some arm reaching its threshold |
| `plans_ok`, `plans_feasible` | the 41 frozen plans satisfy that inequality, and no threshold exceeds its arm |

A structural fact worth keeping: `exists_arm_reaches` does **not** use
triangle-freeness. The threshold step is pure double counting; triangle-freeness
enters only through the degree cap and the classification. The per-arm
thresholds therefore cannot be where the cover fails.

## 5. What to do next, in order

### 5.1 The marking lemma (the whole game)

Statement to formalise: *if `G` is a triangle-free 4-colouring of `K_58`, `r` is a
root and arm `a` reaches its threshold `t`, then `G` satisfies the unit clauses of
one of the emitted cases for that `(profile, kinds, arm)`.*

Decomposition, in dependency order:

1. **Classification.** Every triangle-free 3-colouring of `K_15` / `K_16` is
   isomorphic (up to colour renaming) to `U` or `T`. Two routes: port
   `R4333Lean.CriticalCatalogues` from the pinned K60 repository (it has
   `k16CriticalCatalogue_complete` and `k15CriticalCatalogue_complete`, with 55
   CNF/LRAT pairs), or re-prove it the way the audit did — `nauty` lists 388
   graphs at 16, one completes; K15 by the exact count identity. Porting is
   cheaper if the K60 development builds.
2. **Root normalisation.** A root's critical arms can be pinned to literal
   copies of the templates, because each is a classified 15/16-block. This is
   `gluing.units`.
3. **The marked sender.** The arm has `t` senders, and any set of `d − t + 1`
   positions meets one of them; pick `q`, and pin `q`'s neighbourhood (a second
   classified block sharing `r`) — this is `gluing.orbit_data` and
   `support_embeddings`. The audit checked all 20,617 palette drops and the
   support embeddings exhaustively; the formal version has to reproduce that
   argument, not the computation.
4. **Assembly.** Combine with `exists_arm_reaches` to get: a counterexample
   realises the units of an emitted case.

### 5.2 The profile enumeration (small, self-contained)

`profile_sum` gives `Σ deg = 57`, each `≤ 16`; the eleven profiles follow. A
naive `decide` over `Fin 17 × Fin 17 × Fin 17 × Fin 17` exceeds Lean's recursion
depth (`set_option maxRecDepth` does not rescue it). The route that will work:
state the lemma over sorted tuples `a ≤ b ≤ c ≤ d`, derive `9 ≤ a ≤ 14` and
`b, c ≤ 16` by `omega`, then `interval_cases` on `a, b, c` (a few hundred cases,
each closed by `decide`), with `d` determined. Then transport along
`List.mergeSort` sortedness.

### 5.3 The computation premise

All 113,179 emitted formulas unsatisfiable, as one explicit hypothesis in the
shape of `UniformK60.ExactInputs.AllUnsat`. This needs the full evidence run
(section 7) with `verify --require-complete --checker <own drat-trim>`.

## 6. Where things are

```
review/K58_CAMPAIGN_REVIEW.md   the review: claims, checks, cost, judgement
review/ERRATA.md                six defects in the bundle, with minimal fixes
PLAN.md                         options (shard / tail / Lean) with commands
lean/                           the kernel-checked reduction core
runs/2026-11-16-batch1/         95 certificates, manifest, verification
runs/2026-11-16-small-probe/    0/98 at the first-pass budget
```

The bundle itself is not in this repository. It is
`R3333_K58_LLM_handoff.zip`; unpack it, and the runner is `run_cover.py`.

## 7. Commands

```sh
# environment (the verifier pins the python-sat version string)
python3 -m venv .venv && . .venv/bin/activate
pip install python-sat==1.9.dev22
export KISSAT=/path/to/kissat-4.0.4     # commit 8af8e56
export DRAT=/path/to/drat-trim          # commit 2e3b2dc
# drat-trim does NOT build with its Makefile here: gcc -std=c99 -D_GNU_SOURCE -O2

# one shard of a large profile (resumable; evidence root is shared and locked)
python3 run_cover.py --publication --tier first --kissat "$KISSAT" --checker "$DRAT" \
  --output work/evidence --workers 3 --seconds 12 --conflicts 400000 \
  --profile 16,15,15,11 --shards 4 --shard 0

# release + the only check that means anything
python3 cover_evidence.py --root work/evidence manifest work/release
python3 cover_evidence.py --root work/evidence verify work/release \
  --manifest-sha256 <printed> --checker "$DRAT"          # add --require-complete at the end

# Lean core
cd lean && ./build.sh
```

## 8. Traps

* **A timeout is not evidence.** A min-conflicts or capped-solver failure proves
  nothing; only a DRAT replay against the exact regenerated CNF counts.
* **A manifest hash alone certifies nothing.** `manifest` does no checking and
  `verify` without `--checker` accepts a two-byte "certificate". Always pass a
  checker and quote `"replayed": N` with the hash.
* **`--require-cadical` is producer-attested.** It counts a hand-written
  `cadical.json` naming a nonexistent binary with an all-zero hash.
* **The retry tier is a different formula** (`full_root = True`), and it is the
  *stronger* one: it encodes `H(r) ≥ w(r)` itself. Its certificates are valid
  closures, but they must be reported separately — and the ledger does not pin
  the recipe, so a release cannot enforce which encoding a certificate used.
* **`--tables` is dispensable and rests on the classification.** Turning it off
  costs nothing measurable and removes an obligation.
* **Do not re-run the 12 s pass on the seven small profiles** expecting
  closures: 0/98 here, 0/306 in the pilot.
* **The python-sat pin is load-bearing**, not decorative: `verify` regenerates
  every CNF through `pysat.card.CardEnc`.

## 9. Errata for the bundle (all reproduced; details in `review/ERRATA.md`)

1. The classification citation points at `CriticalTemplates.lean`, which
   explicitly disclaims completeness; the theorem is Kalbfleisch–Stanton /
   Heinrich via Theorem 2.1, in `CriticalCatalogues.lean`.
2. `import-legacy` dies with `KeyError: 'full_root'` on 569 of 752 campaign rows.
   Fix: `row.get(name, False)`.
3. `--require-cadical` never runs or hashes CaDiCaL.
4. `manifest` / `verify` without `--checker` accept self-attested artefacts.
5. `support_tables` is documented as "optional redundant"; it is implied by the
   classification instead (and can simply be switched off).
6. The ledger does not pin the encoding per case.
