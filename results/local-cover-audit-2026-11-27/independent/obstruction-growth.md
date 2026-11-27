# Direction B audit: obstruction, exterior-spoke repair, and growth

## Verdict

The archive contains real, checkable **local** mathematics, but three different queries must not be conflated:

1. an original, fully pinned local witness may be impossible to extend;
2. a recolored local witness can avoid a specified family of exterior-spoke clashes;
3. a whole representative, physical row, or $K_{58}$ problem may still be unknown.

All three can be true simultaneously. Nothing here turns roster `UNKNOWN` into global SAT or UNSAT, closes a wall row, or improves a Ramsey bound.

I use `A/` below for `archive/K58_full_cover_local_witnesses/`, a private extraction of attachment SHA-256 `d9d5a68214d1692237b6b3cc332f2116b3d90064f1f178b5b00497138d70cf3d`.

## What I independently ran

After reading all relevant Python/C++ source, I ran `bounded_audit.py` with zero SAT searches and zero proof-checker calls. Receipts are in `bounded_audit_results.json` and `bounded_audit_stdout.txt`.

* Both `colorings.jsonl.gz` and `robust.jsonl.gz` contain exactly 19,048 non-null records over 41 geometries: 8,174 original and 10,874 revised normalized jobs in each file. I independently checked every monochromatic-triangle exclusion and every local degree-at-most-16 cap in all 38,096 strings. All passed at their indicated orders 22--26.
* Initial and robust records align on their complete `(geometry, scheme, owner/convention, color)` keys. Exactly 1,883 original and 2,770 revised **normalized job strings** changed, matching `robust_summary.json`. These are not 4,653 roster branches.
* All eight SAT strings in `growth.json` pass independent triangle/degree checks, preserve all 300 original projected edges, and satisfy every applicable signed host-edge unit available in the supplied case-0 parent CNF.
* Both `repairs.json` strings pass triangle/degree checks, satisfy the available signed units, and preserve exactly the nominated 14-vertex arm.
* For case 0, I decoded the actual physical spoke colors and gave a direct six-vertex proof below; this does not rely on believing a status field or replaying the archived RUP file.
* I compiled the already-inspected `A/match.cpp` and supplied a synthetic local model plus two exterior signatures. Three correctly matching, differently colored shared spokes returned byte `1`; removing one required spoke returned byte `0`. This is a discriminating control of the matcher, not a replay of roster geometry.

These are bounded checks only. I did **not** run the archive's Python replay, any fresh K58 search, or any RUP checker.

## 1. When a local witness is genuinely non-extendable

Fix anchors $a_1,a_2,a_3$, two projected vertices $u,v$, and one exterior vertex $x$. Suppose, for three distinct colors $c_1,c_2,c_3$,

$$c(a_i,u)=c(a_i,v)=c(a_i,x)=c_i\qquad(i=1,2,3).$$

Each anchor triangle forbids color $c_i$ on all three edges of $\{u,v,x\}$. Proper four-coloring therefore forces all of $uv$, $ux$, and $vx$ to have the fourth color, producing a monochromatic triangle. This is a complete refutation of those fixed spoke assignments; no SAT timeout or large search is involved.

`A/clashes.py::geometry` extracts precisely the positive signed spokes from a row into an exterior signature and retains signatures with at least three nonempty color masks. `A/match.cpp` searches a pair of projected vertices and tests whether they share matching anchors in at least three distinct colors. `A/avoid.cpp::collision` converts the same situation into a six-literal nogood: at least one of those six fixed spoke assignments must change.

### Case 0, checked concretely

`A/obstructions.json` selects physical vertices

$$\{1,5,10,12,43,44\}$$

and anchors $(1,10,12)$. Decoding both original strings in `A/case0.json` with the first record of `A/maps.jsonl.gz` shows that vertices 43 and 44 both have ordered colors $(3,2,1)$ toward those anchors. The supplied `K58_case0.zip` parent CNF has positive units for exactly the same ordered triple from exterior vertex 5. Its decompressed SHA-256 is `ae90931dc6cd482105153dd720209e602bbfc7cc0915e18c6e87023ee2659931`; the checker also recomputed all six `physical_edges` entries in the obstruction record.

Thus the three edges among $\{43,44,5\}$ must all be color 0, which is impossible. This independently proves that **each exact original case-0 assignment** cannot extend along vertex 5. It does not refute the corresponding owner or pivot-color branch after other projected edges are allowed to change.

`A/obstruction.py` offers a RUP certificate for this six-vertex contradiction. Its search is illustrative rather than exhaustive: it tests singleton additions and the specified pair `[2,3]`, then minimizes a returned core heuristically. It is not an enumeration proving every owner UNSAT. I did not replay its RUP files.

### What the large clash counts mean

`A/clashes.py` applies the same necessary-condition matcher to one selected saved coloring per normalized job and then expands through the row maps.

* The initial revised count is 574,213 of 1,967,548 branch incidences (29.1842%); the original count is 348,236 of 1,260,830 (27.6196%). These are clashes of **selected assignments**, not that many globally refuted branches.
* For 124,363 revised representatives (12.6414% of 983,774), every allowed-color **saved witness** has a clash. This still does not show that every possible local coloring, much less the full representative, is UNSAT. `parents_at_least_one_hit` is 449,850, also a statement about selected witnesses.
* Conversely, an unhit initial witness is merely a partial local coloring that passed this test, not a global model.

The phrase “full cover” in `A/scale.py` means that the enumerated normalized roster jobs each receive one full coloring **on their own projection**. It does not mean enumeration of all local colorings, a simultaneous choice across rows, a covering of all $\binom{58}{2}=1653$ edges by one assignment, or global extension.

## 2. What the exterior-spoke repair actually certifies

There are two related but distinct repair artifacts.

### Roster-wide normalized repair: `avoid.py` / `robust.jsonl.gz`

`A/avoid.py` starts with the original local model. Whenever `avoid.cpp` finds a collision, it adds the corresponding six-literal clause and asks the local SAT solver for another model, subject to the stored arm witnesses for that geometry/owner/color. The process stops at a string with no collision against any signature collected for that normalized geometry.

`A/robust_summary.json` records 5,776 learned clauses, empty `unknown`, and the changed-job counts. Important scope details follow from the code:

* The 5,776 clauses are a **generation mechanism**, not the certificate that must ultimately be trusted. The clause list itself is not serialized in this archive, and the count is not necessarily a count of globally unique mathematical facts.
* `avoid.py --verify` does not regenerate those clauses or validate the number 5,776. It directly tests each saved robust string against every regenerated exterior signature and calls the ordinary local checker. This is sufficient for the replacement claim if those checks pass; the learned-clause count becomes provenance metadata.
* The advertised replay does not compare the stored `robust_summary.json` with a regenerated summary. My independent alignment did verify its two `changed` counts and the absence of null robust models, but not the historical clause count.
* Here `unknown={}` and my scan found exactly **19,048** concrete robust strings and zero nulls. More generally, `avoid.py` uses `None` for failed replacement synthesis, not as evidence of global UNSAT.

A validated robust replacement therefore satisfies the ordinary projection constraints and avoids **this one family** of one-exterior-vertex/two-projected-vertex triangle obstructions at every applicable physical placement. It does not test every possible multi-exterior interaction or extend a coloring to all 58 vertices. Independently chosen replacements need not be mutually consistent.

### Specific case-0 repair: `repair.py` / `repairs.json`

`A/repair.py` adds vertex 5 while holding the **nominated arm** fixed. The nominated arm has 14 vertices and $\binom{14}{2}=91$ edges. It does not keep all 300 edges of the original 25-vertex witness fixed.

My direct comparison found that, among the 209 old projected edges outside that arm, the two repaired strings respectively change **54 and 71** edge colors. This is why “the original fully pinned witness cannot grow” and “an arm-preserving repaired witness exists” are compatible statements. The two `repairs.json` models have 26 vertices and 325 checked edges, not 58 vertices and 1,653 checked edges.

## 3. `growth.json`: exact statuses and the timeout/bisection trap

`A/grow.py` is a separate exploratory query. Unlike `repair.py`, it freezes **every one of the 300 edges** in the original 25-vertex witness. Its `build` routine combines those pins with available signed row constraints, triangles, and local degree caps. `check_answer` verifies returned models.

The timeout dependency `timed50.timed_solve` returns `sat.solve_limited()`: true is SAT with a retrievable model, false is solver UNSAT, and null is resource-limited UNKNOWN. `grow.py` also emits false with zero seconds when its deterministic propagation empties a domain. No UNSAT proof object is saved in `growth.json`, and `replay.py` does not replay `grow.py` or validate `growth.json`.

The chronological records, identical in status pattern for physical pivot colors 0 and 3, are:

| Order | Recorded sequence (`vertices:status`) |
|---|---|
| critical-first | 31:FALSE/domain-empty, 28:FALSE, 26:SAT, 27:FALSE |
| small-arm-first | 31:SAT, 37:FALSE, 34:NULL/timeout at two seconds, 32:SAT, 33:SAT |

Consequences must be stated carefully:

* A true record supplies only the listed partial model. My checks validate the saved true strings, including every old pin. SAT at 33 is not SAT at 58.
* A valid UNSAT at 37 on a nested prefix would rule out every larger extension of that **same fully pinned original witness**. Adding vertices cannot restore satisfiability. The independent case-0 six-vertex proof already gives a separate fixed-witness refutation, so no global conclusion depends on trusting this unreplayed growth result.
* NULL at 34 is not UNSAT. It remains unknown even though a constrained 37-vertex superset was reported UNSAT: a non-timed-out UNSAT on a superset implies nothing about whether the 34-vertex subset was SAT or UNSAT.
* The code responds to either false **or null** by setting `hi=target-1` and bisecting downward. For a proved false this follows logical monotonicity; for null it is only a search heuristic. It cannot yield a certified maximal prefix or upper bound. In particular, the run stops with a 33-vertex SAT model after the 34-vertex timeout without deciding 34, 35, 36, or 58.
* Different orders choose different physical vertex sets. SAT at 26 in one order and SAT at 33 in another are not conflicting saturation bounds, and neither is a maximization over all subsets.

The status sequence is logically consistent. Within one nested order SAT sets shrink monotonically as constraints are added; solver **knowledge**, represented by SAT/UNSAT/UNKNOWN, need not appear monotone in a timed search. The error would be to turn the timeout or bisection bookkeeping into a mathematical bound.

## 4. Replay boundary and strict acceptance

The target ZIP is not a standalone complete replay environment. `A/replay.py` requires the earlier `K58_three_seconds` package and imports `run.check_inputs`, `exclusive`, and `prepare_local`; the other scripts additionally require its source/data modules and PySAT. The archive itself does not contain that package, and the documented/default locations `$HOME/K58_three_seconds`, repository `K58_three_seconds`, and `tools/K58_three_seconds` are absent. `replay.py --local` is not dependency-free either.

Therefore I can claim the bounded raw-data checks above, but **not** regeneration of all row maps/signatures, complete local arm/word validation, roster-wide zero-clash replay, or native RUP replay. I did not use cached statuses as a substitute. No proof checker was run; in particular I issued no `-w` invocation and claim no `s VERIFIED` receipt.

A future proof acceptance must regenerate the exact query, bind its physical vertices and pins, invoke the native checker with `-i -U`, require exit 0, exactly one `s VERIFIED`, and zero warnings. The supplied `obstruction.py` internal call uses only `-U`, so its ordinary replay should not silently be relabeled as satisfying that stricter receipt policy.

## Acceptance criteria for interpreting this pipeline

| Object | What must be checked | What it establishes |
|---|---|---|
| Verified local witness | Exact geometry/map, complete edge domains, every projected signed edge, triangles, four degree caps, arm words/order and selected pivot | A model of that finite projection only |
| Refuted fixed witness | Exact witness pins plus necessary physical constraints and a direct checked contradiction or strict UNSAT certificate | This assignment cannot extend; not owner/branch UNSAT |
| Validated robust replacement | All local-witness checks **and** zero matches against every applicable regenerated exterior signature | The selected local coloring avoids this tested exterior-spoke family |
| Case-0 validated repair | 26-vertex model, signed constraints and local checks, correct 91 arm pins | A one-vertex arm-preserving recoloring, not unchanged growth or full extension |
| Growth SAT | Exact listed vertex set, all old pins, full local model checks | That partial CSP is SAT |
| Growth UNSAT | Independently checked proof for the exact listed CSP | No larger extension of those same pins |
| Growth NULL/UNKNOWN | Resource receipt only | No SAT or UNSAT conclusion |
| Whole branch/row closure | Full-formula UNSAT, or a proved exhaustive branch decomposition with every full branch refuted | A scoped global result, not obtainable from the local records alone |

Useful progress here is the removal of a systematic defect in the **saved local witnesses**: the archive supplies explicit replacements for the tested normalized jobs and explains the original case-0 obstruction. The hard bottleneck remains global consistency and full-formula proof/search. The frozen live roster status is unchanged by these local constructions.
