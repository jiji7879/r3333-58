# What is established, what is not, and where each thing lives

State of the campaign on **2026-11-23**, after the two swarms `smwsyh6tk` (cross-arm) and
`smwswz4x9` (zero-set multiplicity), both closed solved at 8 of 8.

> **The bound has not moved. `R_4(3) = R(3,3,3,3) ∈ [51, 62]`.** 31,751 of the 113,179 frozen
> cover rows are OPEN; all 381 rows of the `(15,14,14,14)` profile are OPEN. No row has been
> refuted, no colouring has been found, and no certificate exists for any row of that profile.

This file is an index, not a proof. Every claim below names the artefact that carries it. Where the
artefact is a computation, the check is named; where it is a Lean theorem, the module is named.
Nothing here should be quoted as established without following the pointer.

## 1. The frame

- `51 ≤ R_4(3) ≤ 62`. Lower bound Chung 1973 (Zbl 0258.05111); upper bound Fettes–Kramer–
  Radziszowski, Ars Combin. 72 (2004) 41–63 (Zbl 1075.05057). Both read off Radziszowski's survey
  DS1 rev. #18, 24 April 2026, p. 56 — not from memory. `results/literature-r3333-2026-11-23.md`.
- The survey warns that **Chung's printed matrix has a typo** (a triangle `(31,7,28)` in colour 1);
  the construction is correct, the printed matrix is not.
- arXiv:2610.36648v2 (Nov 2026) claims `≤ 60`; v1 claimed 61. Unrefereed, not independently
  DRAT-checked here, and used nowhere as a hypothesis.
- The survey does **not** state that 51 is conjectured; it calls it "the most studied and intriguing
  open case". The conjecture framing has no read primary source. Same file, §4.

## 2. The cover

- The frozen cover is complete: `K58.Replay.frozenCover`, unconditional, every balanced root of a
  triangle-free 4-colouring of `K₅₈` falls in one of the 113,179 ledger rows. 1,588 generated modules
  rebuilt from source, ending `Checked 1764 complete families, 190736 raw placements, 77557 omitted
  transports.` **It certifies the cover, not a refutation.**
- The kernel audit: `lean/K58/Check.lean` lists 367 declarations, every axiom list inside
  `[propext, Classical.choice, Quot.sound]`, no `sorry`, no `native_decide`, build green
  (`bash lean/build.sh`).

## 3. The zero-set multiplicity layer — charted to its arm-level bottom

- 48 arithmetic candidates for the profile of one ordinary arm; the packages exclude 4; **44 survive
  the incidence layer** (`smwswz4x9/m5`), and **only 33 are realised by some arm type**
  (`smwswz4x9/m4`). The 11 that die at the arm-realisation layer are listed in
  `results/judge-smwswz4x9-m4.md`. **The standing sentence "44 survive and no multiplicity argument
  removes a survivor" was true of the incidence layer only — it is superseded.**
- **37 of the 332 arm types admit no zero-set layer at all.** The judge confirmed that list is
  identical, entry for entry, to the campaign's own independently computed `excluded14.txt`
  (support-incidence equations).
- The no-singleton case is **compatible** with the whole layer, so that route is dead
  (`smwswz4x9/m8`); the design filter is decided for all 135 partitions, 53 with a design and 82
  without (`m6`); the forced-pentagon parent rule is kernel-checked (`m3`).
- Full board: `results/judge-smwswz4x9-m4.md`.

## 4. The cross-arm layer — decided three independent ways

- The package's theorem — a type-16 arm forces a singleton in every type-36 sibling — was proved
  without its (never-supplied) proof archive: one **2,541-core irredundant certificate** for all 192
  cases (`smwsyh6tk/m1`), and the judge replayed **all 2,733 proofs bit-identically** from the
  certificate data alone.
- The same 192 cases are decided twice more: a monolithic 784-variable CNF with 240 DRAT proofs and
  48 witness-checked models (`m3`), and a third encoder that also refutes them **under the union of
  both template rootings**, so the rooting convention does not matter, extending the test to the
  whole three-placement family — **1,152 instances, all UNSAT** (`m5`).
- Its **premises are now decided**: the template premise is kernel-checked unconditionally and the
  six-set classification is closed in the kernel (`m7`).
- Full board: `results/swarm-smwsyh6tk-cross-arm.md`. Judging record:
  `results/judge-smwsyh6tk-m1.md`.

## 5. What the one-hour runs measured

Four cases, one per small profile, at 3600 s and 200 M conflicts each: **0 of 4 closed, all OPEN.**
Each used only ~1,500 CPU-s of 3,600 s wall (41.6 %) because four cases and two swarms shared four
cores. The certificate stream reached 3.0 / 3.4 / 3.1 / **5.6 GB** at 45 minutes and was still
growing, so a closure at that depth would need ~30–40 minutes of `drat-trim` against the harness's
**300 s checker cap** — the cap, not the solver, is what would discard such a closure.
`results/wall-hour-2026-11-23/README.md`.

## 6. Dead routes (do not re-open)

Clause-level interventions (nine of them; best −6 %, and the 116-cell cut is structurally minimal);
word cubes at depth 2; the `(14,k)+XT` ladder (SAT at k = 6/7); pinning the coverage profile; the
some-six pair level (SAT); **the partition-design screen and the cube filter** (both inert on the
real queue — the first was a parent-budget artefact, the second never fires and its showcase is
vacuous); codegree counting against the no-singleton case; the multiplicity layer as a way to pin an
arm; the matching law and the confinement ladder as constraints (both are theorems of the instance).
`research/r3333-58/notes.md` §13 and the swarm records.

## 7. Errata found in the shipped packages

1. One of the seven missing-neighbour certificates does not carry its board: the fourth order-30
   board survives every one-vertex test and needs a two-vertex certificate (`smwsyh6tk/m6`).
2. The cube filter is inert (`m8`).
3. Six defects in the handoff tooling from the previous session, written up in `review/ERRATA.md`.

Neither of the first two affects the 192 cross-arm cases.

## 8. What is open

- **The structural lemma.** The critical path, unwritten: no vertex of a triangle-free 4-colouring of
  K₅₈ with two colour-degrees ≤ 14 would empty all 11,585 wall rows at once.
- **31,751 cover rows**, of which the seven small profiles (11,585 rows) are the wall.
- **Cross-arm depth**: the test decides a *pair* of arms, so it says nothing about the third arm and
  nothing about a full K₅₈ colouring. Type 16's other 17 placements against type 36 are untouched
  (4,032 cases); a complete type-level census is 1.15 G cases (~130 compute-years by measurement),
  and the cheapest complete family is 20,736 cases at ~21 h.
- **The encoding-adequacy bridge** (`review/LEAN_ENCODING_ADEQUACY.md`): `satisfiable_atLeast` is
  proved; what remains is guarded constraints, the support-selector family, assembly, and binding the
  Lean clause families to the emitted DIMACS by hash.

## 9. Where things are

| file | what it is |
|---|---|
| `PROOFS.md` | this index |
| `REPORT_2026-11-23.md` | the narrative report of the three 2026-11-23 swarms and the five bundles |
| `research/r3333-58/` | the siege folder: `problem.md`, `notes.md` (13 steps), `proof.md`, and the append-only ledger whose gate prints `NOT YET: the goal #1 is open` |
| `results/literature-r3333-2026-11-23.md` | the literature check, with Zbl ids and query dates |
| `results/wall-hour-2026-11-23/README.md` | the one-hour measurement |
| `results/wall-sample/README.md` | the 42-row first-pass sample |
| `results/judge-*.md`, `results/swarm-*.md` | the judging record and the two 2026-11-23 swarm boards |
| `results/pair-glue-2026-11-23/README.md` | the 19-spoke bundle: what replays, and the five negative results about it |
| `results/spoke19-2026-11-23/README.md` | the twenty-spoke add-on: 14 witnesses verified, and where a bound of 20 could live |
| `results/wall-incidence-2026-11-23/README.md` | the 381 certified wall cuts and the 64 K50 barrier witnesses |
| `results/longrun-2026-11-23/README.md` | two hours at 170 M conflicts on one wall row |
| `.ultramath/<swarm>/<member>/REPORT.md` | each member's own report for the swarms `smwtqk6ku`, `smwsyh6tk`, `smwswz4x9` |
| `results/skill-health-2026-11-23.md` | which skills were executed and which self-tests pass |
| `lean/` | the kernel tree; `lean/K58/Check.lean` is the axiom-check list |
| `review/` | the long-form reviews (campaign, errata, decisions, Lean end-to-end) |
