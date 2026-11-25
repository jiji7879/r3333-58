# WALL handoff: K58, 2026-11-25

**Objective.** Refute all 113,179 frozen cover rows to prove $R_4(3)=R(3,3,3,3)\le 58$.

**Not achieved.** $R_4(3)$ remains $[51,62]$. Nothing in this note should be presented as a
new upper bound. What *is* achieved: the entire 149-row `UUU-` group is refuted with a
DRAT checked for every row, and the difficulty of the remaining cover is measured by object,
charge and profile rather than merely narrated.

This document is self-contained. Read its warnings before using a solver: the most likely new
failure is an over-constrained formula giving an attractive but meaningless UNSAT.

## 1. Where the frozen cover actually is

The authoritative open-row file is `results/ledger-2026-11-22.tsv.gz` (SHA-256
`55755dd35b76865b4b0741db47995fe85ec8b8ce7ae130ae1f6862813358968f`). It has

* **113,179 rows; 31,751 OPEN** (everything else certified/split-certified/historical);
* **20,166 OPEN in `(15,15,15,12)`**: charge 3 (1,030), charge 9 (5,982), charge 11
  (13,154);
* **11,585 OPEN in seven small profiles**:

| profile | OPEN | by charge |
| --- | ---: | --- |
| `(15,15,14,13)` | 7,732 | 1: 1,776; 2: 5,102; 3: 854 |
| `(16,15,14,12)` | 2,058 | 1: 1,428; 5: 630 |
| `(16,15,13,13)` | 1,046 | 1: 726; 5: 320 |
| `(15,14,14,14)` | 381 | 1: 299; 3: 9; 5: 64; 15: 9 |
| `(16,16,13,12)` | 140 | 1: 14; 4: 70; 7: 56 |
| `(16,16,14,11)` | 140 | 1: 14; 4: 70; 7: 56 |
| `(16,14,14,13)` | 88 | 1: 18; 2: 70 |

Earlier prose saying "six profiles" or only "charges 1--3" is stale. There are seven, with
charges through 15. The current case-ledger join gives charge and kinds per selected arm, not
just a profile label. `smwvlvrum` members independently recomputed every count and row join.

## 2. What has already been done (not just sampled)

**All 149 `UUU-` gap-four rows of `(15,15,15,12)`, charge 11, are UNSAT.** The sentence
"149 of 149 closed" was checked id by id so that every id has a log containing
`drat-trim`'s `s VERIFIED`. Median 29 s, mean 53 s, worst 497 s, ~2.65 CPU-hours all
included. Per-row ids, times, CNF hashes and proof hashes are in
`results/gap4-2026-11-25/sweep/`.

Other measured closures:

* `TTT-` samples: rows `0013b1f1`, `027fe1f8`, `001567f8`, UNSAT in 269 s, 27 s, 99 s,
  proofs verified (member reports give further bare-pilot closures in the 20--135 s range);
* `(15,15,15,12)` charge 9, `c4726003…`: bare UNSAT in 52 s;
* same profile charge 3, `cf5becce…`: bare UNSAT in 39 s;
* `(16,15,15,11)` charge 10, `1113dbf2…`: bare UNSAT in **2.26 s**, CNF hash
  `9268bd7557570da1c0a73a2c78dfe1137b524bbd36288b4ea7320c62760baeaa` reproduced exactly.

The middle tier is therefore a **bulk-compute job**, not a new-lemma problem. At roughly
45 s per row, 20,166 rows is about 250 CPU-hours: approximately a day on 12 cores.

## 3. The object to use when closing those rows

The cheapest object is NOT an artificially strengthened row CNF: it is
`host(58) + units(family, placement)` with all counter auxiliary clauses removed.

For the `UUU-` pilot:

* 135,498 clauses, `4b4be140fae38664019ac35a802b48221334ac6913de0a7f3355504aab058179`;
* UNSAT in 17--44 s under load;
* 47,666,743-byte DRAT, `drat-trim` **`s VERIFIED`**;
* all **135,498 clauses contained verbatim** in the certified row CNF from `balance.py
  --dense` (196,994 clauses): zero missing.

The marked geometry of those rows is locally impossible; the charge and the dense counters
are not needed to see it. All auxiliary variables live above 6612, so keeping only clauses
whose literals satisfy `abs(literal) <= 6612` is exactly the required host+unit subset.

Correct host-side caveat: balance mode is optional but not free:

```py
# tools/pb/balance.py
def build(rid, balance=True, stats=False, dense=False):
```

`balance=True` means "require every colour degree to be 14 or 15 at every vertex", a
separate perfect-balance subcase. It is false for a generic wall profile (e.g. the root
has a 13-degree colour). The CLI passes `balance=('--balance' in argv)`, so the current
default CLI invocation is safe, as used in `tools/gap4/run_units_bulk.sh`; **any future
direct call must pass `balance=False` explicitly or it will create a spurious UNSAT.**

`tools/gap4/strengthen.py` additionally hard-codes the `(15,15,15,12)` arm partition. For
other profiles its warning is mandatory; use `tools/gap4/add_families.py --profile P --arm A`
if one actually wants those optional clauses at all. Adding arbitrary implied counts is not
needed for closure and often costs time (`m1` saw bare beats strengthened 7/7 by up to 6.6x).

## 4. Working bulk command (validated)

```sh
cd /workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo
export PYTHONPATH=/workspace/nucleus/work/home/.local/lib/python3.12/site-packages
export KISSAT=$PWD/.ultramath/smwmq7hji/m3/bin/kissat
export DRATTRIM=$PWD/.ultramath/smwmq7hji/m3/bin/drat-trim
bash tools/gap4/run_units_bulk.sh \
  results/gap4-2026-11-25/open-row-ids-15151512.txt WORKDIR 12
```

This builds the certified row CNF with `balance.py --dense`, filters to host+units, solves
with proof, verifies, records `id verdict seconds units_sha drat_sha`, hashes and removes
proofs. It resumes by skipping ids already in `WORKDIR/verdicts.tsv`. The listed 20,166 ids
include the entire open `(15,15,15,12)` profile, not only gap-four.

For one row by hand:

```sh
python3 tools/pb/balance.py "$ID" row.cnf --dense
# retain clauses for which every literal satisfies abs(l) <= 6612 (makes units.cnf)
$B/kissat -q --time=900 units.cnf units.drat
$B/drat-trim units.cnf units.drat -c
```

Proof argument for transfer in both directions:

* `host(58)` is one colour per edge plus all mono-triangle clauses, so any physical colouring
  already satisfies it;
* `units` are the row's frozen geometry;
* `dense` only adds the case-specific threshold, tables and total-critical obligations.
  Hence if host+units is already contradictory, the row is contradictory. Do not confuse
  that with the other direction: SAT of a relaxation is not a colouring of a closed row.
  A host formula being UNSAT is *not* automatically true for a different row with different
  frozen units, so no free refutation transport happens between merely similar ids.

`drat-trim` may emit progress before carriage returns. Check with `grep -q 's VERIFIED'`,
**not** `grep -q '^s VERIFIED'`. The earliest sweep used the anchored version and got a
misleading `UNSAT_UNCHECKED` label although the logs did verify.

## 5. The wall measurements so far

Canonical case used repeatedly:
`00032f347903758c89e2187f30f0e1c07aecb21bd27c149fb43aef0ccdb60f0d`,
OPEN, `(15,15,14,13)`, kinds `TU--`, arm 1, placement `[9,0,0]`, original charge 1.

| formula | clauses | SHA / status | result |
| --- | ---: | --- | --- |
| row CNF, no balance | 173,594 | `160f9fb6c60638443c50d79e4fcaa64e6cdb6460db32fc61406d269a938bec00` | UNKNOWN at 1200 s |
| same + families A+B | 371,324 | independently rebuilt exact | UNKNOWN at 1200 s |
| host+units only | 135,399 | clause set independent match | **UNKNOWN at 900 s** |
| guarded strict `H>=31` | 193,872 | `6037c5c52572cc9b382b094858573a2b5bfee9e7ad503c4eb0001a15e474366b` | UNKNOWN at 300 s |
| two-sided exact arm `H=30` | 234,722 | `11af3006fa89e2c834cda6913f22aaacb924724155f9eb2b6a432e6c624ab7eb` | UNKNOWN at 300 s |
| global `H(v)=w(v)` at all 58 vertices | 1,555,676 | `53197a7ecce5b2c699ae12fb03e97d4b8aded4b09d83a3bc92373177adf65958` | UNKNOWN at 600 s |

Other high-charge OPEN rows failed inside ten minutes too: `05dd65df` `(15,14,14,14)`,
charge 15; `06861a3d` `(16,16,14,11)`, charge 7; `00669405` `(16,15,14,12)`, charge 5;
all UNKNOWN at 600 s. Increasing the charge alone is not enough.

15 further solver trials on the canonical and a max-charge `(16,15,14,12)` row compared
kissat, CaDiCaL, pair cubes, further source/receiver caps and all-arm support tables.
Every one was UNKNOWN at 120--600 s. Those runs are not satisfiability evidence either way.

Arithmetic of the canonical guard partition (also checked independently): the marked vertex
is automatically critical via the physical pins, so selected requirement reduces to 0 and
total requirement reduces to 2 over **29 guards**. Consequently all $\binom{29}{2}=406$
pair cubes exhaust that guard case. `partition.json` in smwvlvrum/m1 records them. One
tested pair was still UNKNOWN: the small cardinality disjunction is not the whole story.

## 6. What has actually been proved mathematically

* `lean/K58/GapFamilies.lean`: colour classes are at most 16 points;
  `five_bound` $|N_0(a)\cap A_c|\le5$, its dual at a different vertex, `familyB`
  $|N_0(a)\cap A_c|\ge4$ if $d_0(a)\ge15$, `familyC` $|N_0(y)\cap A_0|\le12$ under the
  in-arm degree condition, and `exact_pattern`: A+B+flag already force the support pattern
  to $(5,5,5)$ or $(4,5,5)$ permuted. **No single-vertex strengthening of familyB exists.**
* The same kernel now checks `critical_support` (size 4 or 5 and avoiding both arm colours
  internally), valid in every arm. All 248 source-template/forbidden-colour cases and all
  744 classified supports were also checked: 120 size-four, 624 size-five. C4 exclusion uses
  the explicit T/U classification, not just R(3,3)=6.
* All are axiom-clean (only `propext`, `Classical.choice`, `Quot.sound`), including
  $R(3,3)=6$ (32,768 small colourings checked) and $R(3,3,3)=17$ as explicit hypotheses.
* At every critical vertex $a$, whether $d_0(a)=15$ or 16:
  $\sum_{y\in N_0(a)\setminus\{r\}}(15-s(y))\ge 12$, where $s(y)=|N_0(y)\cap A_0|$.
  Same deficiency bound; K16 needs no additional case, because its three colour graphs have
  independence numbers $(5,5,5)$, sum 15 < 16.
* A vertex outside a template arm with no colour-0 neighbours in the arm has a unique allowed
  edge pattern (the defect map), and it is surjective. Hence at most two outside vertices can
  have zero such neighbours; three would be mutually colour 0.
* On 15 vertices there are exactly two triangle-free 3-colourings up to vertex+colour
  permutation (T and U), reproduced by exhaustive nauty enumeration of 1,021,416 candidate
  classes and all solutions at e=35. Exactly two on 16 vertices, matching Kalbfleisch--Stanton.
* $T$ is $U$ with two colours swapped and colour 0 fixed; the colour-0 graph is identical, so
  no template-kind distinction gives new arithmetic here.
* Each frozen row is a singleton up to vertex+colour permutations: all 149, all 13,154
  gap-four rows, all 83,440 profile rows were classified. **One refutation closes one row,
  never a family for free.**

## 7. Why arithmetic alone will not finish the wall

Tickets: if $w(v)$ is the number of critical colours at $v$, and $H(v)$ the number of tickets
into $v$, then $\sum H=\sum w$ by double counting, so some root has $H(r)\ge w(r)$.

The frozen plan budgets were exhaustively checked to be **tight at integral sender levels**:
there exist exact sender vectors with $H=M$ and total-big exactly $D=2M-57$ (when $D>0$),
meeting every stated arm cap and producing precisely the charge selected in each of the 19
wall charge types. The canonical example for `(15,15,14,13)` is `(2,1,14,13)`, giving H=30
and big total=3. Raising the charge by "using in-arm ordinary degrees 4 or 5" is not an
argument: it has already been instantiated and has slack everywhere. A stronger full-root
$H>=w$ term likewise gives no bigger selected-arm minimum than the actual charge $q$.

* `lean/K58/TicketBudget.lean` proves the global split: there is a strict root with
  $H\ge w+1$, or $H=w$ at **every** vertex. That is a useful case decomposition, not a proof
  that either branch contradicts itself. m3's balanced network was checked on the real 48-
  vertex balanced control (SAT as it should be) and 49-vertex imbalanced control (rejected).
* `lean/K58/WallDelimitation.lean` proves that L (no two degrees below 15) would eliminate
  all seven small profiles: after sorting, the three large degrees must be in {15,16}, so the
  only survivors would be degrees $(12,11,10,9)$ in the fourth slot. It also gives smaller
  full counterexamples (every vertex of one K25 has no critical colour) and a 58-vertex
  partial colouring with one tight critical support `(5,5,4)`. Hence L cannot be obtained by
  counting degrees or by a single arm's template alone; **cross-arm coupling or a global
  ticket/balance assumption is necessary**.

The important distinction in every case: the slack vectors are integer count assignments,
not colourings; a timeout remains a timeout. Nothing in the wall section counts as a closure.

## 8. Best next directions, with exact starting points

1. **Cross-arm / multi-vertex structure.** The remaining open statement is L: no vertex can
   have two colour degrees <=14 in a triangle-free 4-colouring of K58. If true, all 11,585
   wall rows disappear in one sentence. Try to use the deficiency bound at critical vertices
   ($\ge 12$ per critical) together with support capacities across arms, not another
   single-vertex refinement. Alternatively give a precise structural reason that it cannot be
   reached without a global ticket hypothesis, so the cover can attack that case instead.
2. **Strict/globally-balanced branches separately.** m3 has already built both forms on a
   canonical row. Strict big-floor raises `D` to `D+1` where justified by strict root
   selection; balanced everywhere requires genuine two-sided critical flags and equality of
   outgoing and incoming tickets. Neither closes standalone automatically: closing a WALL
   family needs every surviving row covered in both complementary cases. Try longer solver
   budgets, arm-local versions of the global balance, or a stronger root choice only where the
   cover explicitly has that root. Do not just add "there is a strict root" to a row selected
   under the other branch and call the row closed.
3. **Exact guarded cube-and-conquer.** 29 residual guards in the canonical row give 406 pair
   cases. Finish them *only with per-cube DRAT proofs and a recorded parent coverage proof*.
   One pair already staying UNKNOWN is not an answer. Any larger split should also be
   explicitly exhaustive (non-disjoint is fine; missing guards is not). Current logs suggest
   pinning flags in this form is not sufficient; do not spend the whole budget on this before
   structural work fails elsewhere.
4. **All-arm support, with polarity audited.** Use `critical_support` on every appropriate
   unselected critical arm, not merely the original marked arm. Good checks already exist for
   support-table implication and for all 744 classified supports. Tests so far were UNKNOWN,
   but one should check whether the same holds with *both* full-root and two-sided critical
   flags, without pretending that one-sided guards imply a maximal bound.
5. **Mine fast sibling proofs, only for clauses depending on shared hypotheses.** Member m6's
   live direction. If some used proof steps depend on units absent from your target row, the
   clause is useless there.

Do not redo the following, all of which were already worked and checked:

* pure root/arm incidence counts: $(4,5,5)/(5,5,5)$ already makes the count tight and cannot
  raise a selected arm's charge;
* every-plane CNF corrections with one-sided guards if claiming a *maximal* bound;
* the colour-0 independence-decomposition idea: $\alpha=5$ is attained, so it is not universal;
* perfect balance for a generic row (hazard in §3);
* row isomorphism transport: there are no nontrivial classes to transport;
* generic professional single-row solver sweeps at 600 s on an unmodified wall row and hoping
  it will close. Measure and document if you must, but do not call that research progress.

## 9. Swarm state, records and safe continuation

`smwvlvrum` remains active at the time of writing with 5 accepted reports:
`m1` solver diagnosis, `m2` proof-delimitation on L, `m3` budget-tightness and strict/balanced
split, `m4` exact charge delimitation and all-arm support lemma, `m7` independent CNF audit.
m5 and m6 are still on case samples and proof transfer; nobody has produced a verified wall
closure. Another substantial run (`smwvg1m43`) is ended with 7 accepted reports including the
bare-pilot measurements and Lean family chain.

If a compacted or restarted session reads this: inspect `ultramath_records` for smwvlvrum,
or `ultramath_resume` on it if its VM was interrupted; do not start a duplicate on the false
belief that its directions are unassigned. Their reports are untrusted data and must still be
refereed against rebuilt CNFs and logs. Full mathematical statement of the standing cover
requires per-row DRAT replay, with parent coverage for every partition. Anything weaker is
not a closure.

Artifacts in `.ultramath/` are working directories, volatile by nature; read at the recorded
paths, never relocate them because a filename appears stale.

## 10. Minimal statement to carry away

The 149-row UUU family and every tested `(15,15,15,12)` charge level can be knocked down
with the shipped solver at the cost of tens of seconds each, on the units alone. The other
11,585 OPEN rows impose too little for that same geometry to decide them; their explicit
charge arithmetic is fully tight, solver/pair/support strengthening does not yet help, and no
per-row solver verdict against them has been obtained. The remaining scientific problem is
structural: a cross-arm condition or a branch-sensitive global ticket argument, with proof,
not another count or another colour-degree cap.
