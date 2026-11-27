# Claim-to-artifact audit of `K58_square_spoke_wall_test.zip` (member m3, direction d4)

Scope of this direction: for each claimed bound/control result in the attachment, name the
artifact that witnesses it, state the strongest proposition that artifact supports, and state
what it does not support. No wall parent is regenerated here and no search is run; the only
computations are hash/set/count reconciliation, two model validations, one own-code strict-RUP
proof check of the shared K15 theorem, and one own-code re-derivation of the witness geometry.
Other members own template faithfulness (d1), parent regeneration/propagation (d3) and the
historical panel (d2); where a claim needs their work this file marks it **open**.

## 0. Package identity

| item | value |
|---|---|
| zip sha256 | `08a1e2e9513ade7dffab4d8ff89fb5f2f5dc04e68d8928ff8cf54cded9093873` — **matches the declared hash** |
| members | 155 files, 6,105,033 uncompressed bytes; `README.md` is byte-identical to `next/README.md` (md5 `a6a72d24bcc32c9e8d3ad094c9f5b4db`) |
| extracted copy used | `.ultramath/smwziqvco/m3/pkg/` (my directory; shared package untouched) |

Import wiring (checked, not assumed): `next/verify.py` reaches `hard-more/join.py` through
`next/neighbors.py:6` and `next/shorten.py:7` (`sys.path.insert(… 'hard-more')`), and
`hard-more/join.py:7` reaches `hard-study/probe.py`, which puts `hard-study/encoder` on the path.
So the documented replay line (`README.md:43`) does resolve with only the extracted top directory
in place — the package wires its own path — but only when all three directories are extracted
together; extracting `next/` alone fails, and `next/shorten.py` additionally needs
`hard-more/<rank>-wide-*.json` data files. I verified the import chain in isolation
(`import verify` succeeds, `probe` and `join` resolve to their shipped files) but did **not**
execute `verify.py verify`, because it regenerates the 14 parents (**open**, d3).

## 1. Claim-ceiling matrix

Legend: **W** = witness present in the archive and checked by me; **W-part** = witness present,
only partly checkable without parent regeneration; **open** = needs another direction's work.

| # | claim (README line) | witnessing artifact | strongest thing it establishes | what it does not establish |
|---|---|---|---|---|
| 1 | shared K15 theorem: the three-colour K15 formula with a square+matching on the four sites is UNSAT (`L11`) | `next/block.py:formula(True)` + `next/matching.drat.gz` + `next/verify.py:verify_local` | **W**: the generated CNF (315 vars, 1825 clauses, sha256 `9fb32091…80b01`) is UNSAT. I re-checked every one of the 11,868 additions by my own strict-RUP engine with all 12,516 deletion records ignored — all RUP, empty clause reached. Negative controls reject the trace on the path variant (#27) and on the K14 formula (#1) | not that this CNF *is* the K58 local configuration. The archive pins the proof bytes but **not** `block.py`; the query is unpinned by any recorded hash, so faithfulness is separate (**open**, d1) |
| 2 | path variant is feasible (`L11`, `L13`) | `next/path-model.json` | **W**: the saved model is a genuine 3-colouring of K15 with no monochromatic triangle, root groups 4/5/5, the two size-5 groups each split into two pentagons, and the four sites carrying path+path (`chk_models.py`) | does not show *which* K58 situation realises the path case; it is a feasibility statement for the template only |
| 3 | sharp threshold: at order 14 a triangle-free 3-colouring with square+matching and root groups 4,4,5 exists (`L13`) | `next/matching-K14.json` (91 edges) | **W**: direct validation of the colour matrix — no mono triangle, groups 4/4/5, sites = size-4 group with colour 1 a matching and colour 2 a square (`chk_models.py`) | nothing about K58: it only bounds this *neighbourhood* argument at degree 14, exactly as `L13` says |
| 4 | the 14 panels are first-tier, unsplit, `tables=True,total_critical=True,full_root=False`; no representative/pivot/spoke assumptions (`L17`) | `wall-rows.json` rows are pure geometry (`branch, charge, family, placement, id`), and `next/wall.py:bind` hard-codes `dict(tables=True,total_critical=True,full_root=False)` | **W-part**: `id == sha256(canonical{family,placement,charge})` for all 14 rows; no representative/pivot field exists in a row, so none can leak; the recipe key set is asserted (`cover_evidence.py:100`) | the *tier itself* is a constant in shipped code, not a recorded attribute: batches only say `tier:"first"`. Nothing in the archive contradicts `full_root=True`. Equality of `sha256(parent)` with the full_root=False regeneration is **open** (d3) |
| 5 | the 14 parents are not the earlier 1,300 full-root parents | `hard-study/hard1300.tsv` (`input_sha256`, `id`) vs the 14 recorded `parent` hashes | **W**: 14/14 parent hashes distinct; disjoint from all 1,300 `input_sha256`; the 14 row ids are also disjoint from the 1,300 ids and none appears in `hard-study/geometry.json` (which holds exactly the 1,300) | freshness is shown at hash level only; it cannot show the 14 parents belong to *this* wall ledger rather than to some other tier — the earlier selection is not shipped |
| 6 | `9,287` clauses; `4,807` surviving cubes across ten rows; two profiles with zero gain (`L19`) | `next/batch-*.json.gz` (14 files), `next/batches.json`, `next/wall-screen.json` | **W**: sum of per-row rules = 9,287; per-row duplicate-free; `batches.json` sha256-of-compressed-bytes matches 14/14; sum of `novel` = 4,807; zero-novel rows are exactly the two (15,14,14,14) and two (16,14,14,13) rows | `novel` is 4,807 only because of pysat's `propagate` semantics in this exact version (see §2.3). **9,287 is a sum of per-row distinct clauses; across the 14 rows the same literal set recurs 2,040 times, so the global union has 7,247 distinct clauses.** No claim about search value follows |
| 7 | "adding the clauses refutes those cubes by unit propagation" (`L19`) | `wall-screen.json:physical_run` / `verify.py` | **W, but vacuous**: each cube is the negation of its own clause (verified: `set(-l for l in cl[1:]) == required - pins`, and all 9,287 clauses have length 5, so all four spokes are free), so a conflict after adding the clause is immediate in every case | it is not evidence of strength; the informative quantity is the 4,807 count in #6 |
| 8 | the ten nominated cubes stay OPEN at a nominal 12,000 conflicts on the plain parent (`L19`) | `wall-screen.json:physical_run` for the 10 rows with `novel>0` | **W**: 10/10 `result:"OPEN"`, recorded conflicts 12,000–12,003, `proof_bytes: 0`, no proof/file key anywhere (so "no direct full-parent DRAT was produced" is accurate) | OPEN is not hardness and not UNSAT; and the exclusion of those cubes rests *only* on #1 plus the faithfulness of #1 to K58 (**open**, d1) |
| 9 | 8 bounded CaDiCaL runs at a nominal 40,000-conflict cap, all OPEN (`L21`,`L30`) | `next/wall-bench.json` | **W**: 8 records, `make_span 10.435 s`, CPU 2.698/4.442, 2.853/3.884, 2.773/2.773, 2.839/3.115 (README table rounds exactly right); matching overhead 0.0089+0.0071+0.0043+0.0140 = 0.0344 s ("about 0.034"); peak worker RSS 122,156 KiB | "the cap" is nominal: recorded conflicts are 40,000–40,003. Time-to-cap is not search strength (`L30` says so). "122 MiB" is 119.3 MiB in MiB units |
| 10 | historical controls: 939 seeds → 2,817 neighbours, 1,918 with extra propagated literals, all OPEN; 28 proper subcubes at 3,000 conflicts; 353/151/18,528 square-rule instances (`L34`,`L36`) | `next/neighbors.json`, `next/shorten-8.json`, `next/shorten-340.json`, `next/pathcuts.json` | **W (record reconciliation only)**: sums are exactly 939 / 2,817 / 1,918; 14+14 subcube records, all `OPEN`, conflicts 3,000–3,003; `new_by_length` sums to 353 / 151 / 18,528 | these are the *recorded* numbers; independent recomputation is d2. Nothing here proves minimality (`L34` says so) and nothing extends to K58 |
| 11 | batch binding: row, parent hash, tier, empty cube, physical palette, shared theorem-proof hash, gz bytes (`L46`) | batch headers + `batches.json` | **W**: `id`/`parent`/`tier="first"`/`cube=[]`/`palette=[0,1,2,3]` present in 14/14; `local_proof = sha256(decompressed proof) = 4ca7a5d3…85d7` in 14/14; `batches.json` = `[index, sha256(gz bytes), novel]` and matches 14/14 | the *file* hash of `matching.drat.gz` is `63db62ec…c4e3`, **not** the recorded value: the recorded digest is over decompressed bytes, so an independent replay must hash after gunzip. The query CNF carries no recorded hash at all |
| 12 | witness geometry "consists entirely of units in the original wall parent" (`L9`) | batch witnesses `[x, c, b, sites]` + `wall-rows.json` + `verify.py` per-rule asserts | **W-part**: all 9,287 sites are distinct, lie inside the stated arm's slot range, the sender is neither root nor site, no internal edge carries `b` or `c`, and the six internal edges split into a square and a matching, re-derived by my own code from the named template (`chk_witness.py`, 0 failures) | that the parent actually *pins* those edges, and that the guard literal is the parent's own selector, need the regenerated parent (**open**, d3) |
| 13 | guard semantics: "at least 14 color-c spokes from x in addition to xr", so four spokes force deg_c ≤ 14 (`L5`,`L9`) | `hard-study/encoder/dense.py:79-139` | **W (code reading)**: `needed = 14` is decremented only by already-pinned c-spokes, candidate spokes are `lit(x,y,c)` over non-root `y` with `arm(y) != c`, and `xr` is excluded because the loop starts at `y=1`; same-arm spokes are dropped but are implied false by the mono-triangle clauses. So `g` ⇒ at least 14 c-spokes outside x's arm, none of them the root edge ⇒ `deg_c(x) ≥ 15`, and four further spokes contradict `g` | that a wall row ever *satisfies* `g`; guard arity 14 is a code constant, not a documented derivation. Whether the 15-vertex case split covers every realisable degree-≥15 neighbourhood is d1's business |
| 14 | "Accept a terminal wall closure only after the full original-input proof or full model passes the publication verifier" (`L46`) | — | **W as a scope statement**: correctly refuses to promote any bounded run to a closure | nothing in this archive constitutes a wall closure; the package is an experiment on one clause family |

## 2. Independent checks performed (all in this directory)

### 2.1 Strict-RUP check of the shared theorem (`rup_check.py`, `logs/rup_check.log`)
Own implementation: binary-DRAT parser + stamp-based unit-propagation engine, deletion records
ignored (the strictly stronger addition-only check). Result: **11,868/11,868 additions RUP,
empty clause derived**, 315 vars, 1,825 base clauses, max proof variable 313. Query bytes pinned:
`sha256(pysat to_file of block.formula(True)) = 9fb32091685b9e3adf1e7e670c3d4333f35b0d12ed6990e968a44b83fb180b01`
(26,960 bytes; my in-memory rendering is byte-identical). Path variant `7f038425…6fd9b1`.

Proof shape: binary DRAT (leading `a`), 24,384 records, 12,516 deletions, **no deleted unit
clause** (so no pseudo-unit-deletion hazard here), exactly one empty clause, last record.

### 2.2 Negative controls (`rup_negative2.py`, `logs/rup_negative.log`)
The first two drafts of my checker were *unsound* (they accepted everything); the shipped
version is the third. Controls now enforced before trusting the result:
`rup([])` with no additions is False on all three formulas; the same trace fails at addition #27
on `block.formula(False)` and #1 on `sharp.small()`; the trace without its final empty clause is
not accepted. So "0 non-RUP additions" here is not an artifact of a vacuous engine. The two
engine defects found by these controls (missing seeding of database unit clauses; scanning
clauses containing `l` instead of `¬l`; inverting "literal is false") are the reason the micro
tests in that file exist.

### 2.3 Version-specific solver semantics (`wallscreen` interpretation)
`4,807` tags the cubes that **survive** unit propagation. That is the opposite of what the usual
SAT-library convention suggests, so it matters that `pysat 1.9.dev22` documents
`solvers.py:1308-1360`: "The status is `True` if no conflict arised". `wall.py:work` and
`verify.py:main` both take index `[0]` of `propagate(...)` and name it `novel`/`uncaught`;
with this version that is "not caught by propagation", and the recorded sum 4,807 agrees with
`README.md:19`. On a PySAT version with the opposite polarity the same code would count the
complement (4,480) and silently invert the headline number. The pinned wheel in
`hard-study/wheels` is the same 1.9.dev22, so the archive is self-consistent; it is not
version-robust.

### 2.4 Artifact binding and set reconciliation
* 14/14 `sha256(batch-N.json.gz)` equal `batches.json` entries; 14/14 `local_proof` equal the
  decompressed proof digest; 14/14 `id` equal `identity(row)`.
* 14 distinct parent hashes, disjoint from the 1,300 `input_sha256` and from the 1,300 ids.
* per-row rule lists duplicate-free; 9,287 total; 2,040 cross-row repeats (7,247 globally).
* README arithmetic reproduced from the artifacts: 2.698→2.70, 4.442→4.44, 2.853→2.85,
  3.884→3.88, 2.773→2.77, 2.839→2.84, 3.115→3.11, makespan 10.43, matching 0.0344,
  939/2,817/1,918, 28 subcubes, 353/151/18,528.

### 2.5 Witness geometry (`chk_witness.py`)
9,287/9,287 clauses: sites distinct and inside the declared arm range; sender ≠ root and not a
site; no internal edge in `b` or `c`; one of the remaining colours a 4-cycle, the other a
perfect matching. 0 failures.

## 3. Defects, gaps and imprecise statements

1. **Unpinned query.** The batches commit to the *proof* digest but no artifact commits to
   `block.py` or to the CNF it generates. Someone who edits `block.py` changes the theorem
   statement without changing any recorded hash. Repair: record
   `sha256(to_file(block.formula(True))) = 9fb32091…80b01` (pinned here) alongside `local_proof`.
2. **Tier is a code constant, not data.** `batches.json`/headers record `tier:"first"` only;
   `wall.py:bind` always passes `full_root=False`. A batch cannot be distinguished from a
   `full_root=True` one by anything stored. Repair: store the three booleans in the header.
3. **Digest convention.** `local_proof` is over decompressed bytes while the batch digest is over
   the `.gz`. Two different conventions in one header; both are implemented correctly, but the
   README does not say so and "binds the compressed bytes" applies to batches only.
4. **"9,287 distinct"** is per-row distinct; the global union is 7,247. Minor, but the phrase
   reads as a global count.
5. **"Adding the clauses refutes those cubes by unit propagation"** (`L19`) is a tautology (each
   cube negates its own clause); it should not be read as a strength measurement.
6. **Conflict caps are nominal.** 40,000-cap runs recorded 40,000–40,003 conflicts; the
   12,000-cap runs 12,000–12,003. "Reached the cap" means the budget was exhausted, not an exact
   count.
7. **RSS units.** 122,156 KiB = 119.3 MiB, not "about 122 MiB".
8. **Verifier completeness gap.** `verify.py` re-checks each rule's shape and re-derives `novel`,
   but it does **not** re-derive `pathcuts(row, guards)`; the emitted set is only tied to
   `wall-screen.json` through `len(batch['rules']) == r['clauses']`. An omitted clause replaced by
   another well-formed one with the same count would pass. Soundness of added clauses is
   unaffected; the *completeness* claim (all 9,287) rests on the builder, not on the verifier.
9. **"at least 14 … in addition to xr"** is correct but only because the candidate loop starts at
   `y=1` and excludes same-arm vertices; the refinement ("only c-spokes into other arms count")
   makes the guard stronger than the prose suggests. Not an error; worth stating.
10. **Historical panel provenance** (`L34`): the 13 rows and their "already solved" status come
    from earlier ledgers that are not in this archive; nothing here re-establishes them (d2).

## 4. What this audit does *not* establish

* It does not establish that the K15 template faithfully represents every realisable
  degree-≥15 neighbourhood in a K58 4-colouring — d1's case analysis is required, and until then
  #1's UNSAT result is a statement about the generated CNF, not about K58.
* It does not verify any wall parent (hash, tier, units, guard binding) by regeneration — d3.
* It does not re-derive the historical panel — d2.
* OPEN is never read as SAT or UNSAT here, and no local graph lemma is promoted to a global row
  proof. Nothing in the archive amounts to a wall closure.
