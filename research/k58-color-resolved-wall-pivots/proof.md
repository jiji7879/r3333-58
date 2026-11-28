**Status: PROVED. The ledger gate accepts #13, with independent `compute` and `model` checks. This is a scoped audit result, not a wall-row completion or solver-improvement theorem.**

# Audit of `K58_color_resolved_wall_pivots.zip`

## Result

The archive supplies a sound, independently reconstructed **local rule library** on its exact frozen inputs. The comparator-counter definitions preserve original physical models, and the supplied target clauses are RUP consequences of the appropriate reconstructed parent plus counter definitions. All 11,585 bindings and all 240 local configurations checked. The ten claimed transported parent proofs checked.

It does **not** close a wall row, prove that a local minimum word extends to a complete $K_{58}$ coloring, or establish a solver speedup. All 48 unsplit benchmark runs remain **OPEN**. Partial proof traces were not retained for replay, and per-child proof certificates do not exist. This is an audit of mathematical validity and proof scope, not a new Ramsey-bound result.

## 1. Roster and local configurations

All 51 ZIP members match the extracted bytes. The archive is 7,943,004 bytes, SHA-256 `74a517db2c15f2b96c9834d4e4e135c86e62709cd0813b733c810936d411e020`.

An independent standard-library reconstruction generated the template graphs, their automorphisms, canonical support-embedding orbits and every feasible arm-local word. It then recomputed all ordered bindings and full configuration objects, with no package encoder imports. Every item matched:

| quantity | checked result |
|---|---:|
| frozen rows / unique row IDs | 11,585 / 11,585 |
| non-null / null pivots | 11,549 / 36 |
| complete configurations | 240 / 240 |
| feasible local physical words | 1,448,380 |
| branch minima / word counts / forced maps | all 720 branches match |
| unequal minima in old false physical colors | 1,347 |
| unequal minimizing-word counts | 9,518 |
| one-word false minimum at either / both | 6,176 / 348 |
| further nonpivot spoke forced at either false minimum | 9,229 |
| old-false minima of types $0,2$ and $3,4$ | 663 / 684 |

A separate geometry audit checked all 11,549 classified bindings: 174,535 arm sites, including 53,556 support sites with exactly the singleton marked color and 120,979 free sites with exactly the claimed three-color palette. All internal template edges and all sender domains matched.

The 36 null pivots are a limitation of the archived pivot-selection data. This audit did **not** prove that no other useful pivot can be selected on those rows.

## 2. Counter and clause semantics

For two comparator inputs $p,c$ and auxiliary wires $h,l$, the six defining clauses encode exactly

$$h=p\lor c,\qquad l=p\land c.$$

The network inserts each input into an already sorted unary prefix. After insertion its true values are ordered before its false values, so output $j$ means **at least $j+1$ inputs are true**. Each auxiliary value is uniquely fixed by earlier values. Hence every physical assignment has exactly one counter extension, without changing any original model.

For a pivot guard $P$, branch minimum $m$, threshold $T_j=(\mathrm{count}\ge j)$ and forced spoke color literal $E$, the rules are

$$\neg P\lor T_m\quad(m>0),$$
$$\neg P\lor T_{m+1}\lor E.$$

The first prohibits the below-minimum branch. The second forces $E$ at the minimum and leaves all above-minimum alternatives live through $T_{m+1}$. The pivot itself is fixed by $P$ and is omitted from auxiliary forced-site targets.

Individually reconstructed semantics were checked in four complementary ways:

* every input/output candidate of a comparator $p,c,h,l$ admits only the unique $(p\lor c,p\land c)$ extension for the given inputs;
* all 8,190 input words for network sizes $1$ through $12$ give the exact descending thresholds, with a separate coordinator check of 510 assignments for sizes $1$ through $8$;
* every one of the 1,448,380 physical local words satisfies every color target under its unique threshold extension;
* all 720 branch minima have explicit attaining local words, proving sharpness **on that arm**.

The baseline positive escape bank is separate from the 240 color-rule miters. Every local feasible word has an escape mask $h$, where a bit denotes an escape-colored spoke. A candidate mask $m$ defines a transversal exactly when $m\wedge h\ne0$ for every feasible $h$; each such $m$ gives the positive clause requiring at least one selected escape literal. The independent enumeration retained precisely its inclusion-minimal masks. This produced 4,510 configuration-local clauses. All 21,173 single-literal removals have an explicit feasible counterword, proving each retained literal necessary. On the six benchmark configurations the physical lists contain 15, 23, 16, 23, 17 and 0 clauses respectively, totaling 94. Together with the 97 color targets these account semantically for all 191 added baseline/color clauses in those batches.

## 3. Native proof construction and transport

For target clauses $C_i=\ell_{i1}\lor\cdots$, create fresh flags $f_i$ and the query

$$F\ \land\ \bigvee_i f_i\ \land\ \bigwedge_{i,j}(\neg f_i\lor\neg\ell_{ij}).$$

A true flag forces every literal of its own target false; the positive disjunction requires a violation of at least one target. This query does **not** insert the targets as assumptions. The trace derives the targets, refutes the corresponding flags, and closes the positive flag disjunction. This distinguishes an actual RUP implication proof from a bare-parent refutation or a proof checked against a query that assumes its answers.

All 240 independently reconstructed cached local-query and trace hashes matched. Native `drat-trim -I -f -W -U`, without `-w`, returned 0 with `s VERIFIED`, no warning and no empty stderr on all 240: 4,196 color targets, 20,852 cached proof steps, 1,235,379 query bytes and 406,943 trace bytes. Negative controls omitted target/case-split lemmas and substituted a false pivot unit target; both were rejected with `s NOT VERIFIED`. The coordinator independently evaluated small miter assignments and observed a positive check plus the expected failure of a deliberately unsupported proof step.

On the six complete benchmark batches, all target clauses occur explicitly in the RUP prefix. All six parent/query/trace triples passed strict native checks on byte-identical regenerated stored parents. Substantive controls showed that removing target lemmas is rejected, omitting the refutation suffix yields only a derivation, and changing a target literal invalidates the proof.

Exactly ten claimed $(\mathrm{parent}+\mathrm{definitions})\rightarrow\mathrm{targets}$ transport queries were reconstructed and checked against every `transport.json` identity. All 159 clauses and ten parent proofs passed on ten configurations spanning all seven eligible profiles. An actual `apply.py` gap export and batch-0 CLI export were separately rerun by the coordinator, matching the exact declared hashes, including `ce69e196ae302f0cb00d3ee4c7d3114f401c21ba4633e1616438a20b43fb091d` for the 3,353,247-byte gap export and `66cde0ddb0556a76a73244981976aff09d9928788a9dbf59f1a56779049efa50` for the 3,328,774-byte batch-0 color variant. Arbitrary and non-contiguous variable-renaming controls passed.

There are two provenance qualifications. Six of these parents have stored archived CNFs and were regenerated byte-for-byte. The remaining four used the bundled encoder: their whole ordinary K58 body and every fixed physical unit were independently rebuilt, but their threshold suffix was not independently reimplemented. They certify consequences relative to the reconstructed encoder parents, not a fresh audit of that suffix. Only ten configurations received full-parent replay; the other 230 received complete local enumeration and local proof checks.

Thus, for reconstructed six-parent exact byte matches and for the stated encoder-parent reconstructions, the derived consequences preserve exactly the original models on the original variables. This does **not** show that the parent is SAT or UNSAT, and does not show that a locally attaining arm word extends globally.

## 4. Performance evidence actually present

All 24 distinct benchmark variant formulas were reconstructed and their hash values matched both seed receipts. The 48 runs comprise six rows, four variants and two seeds. None completed, and the retained terminal-proof bytes are all zero.

| variant | conflicts | solve CPU-s | solve wall-s | partial trace bytes |
|---|---:|---:|---:|---:|
| original | 480,013 | 43.431247 | 43.547189 | 130,161,177 |
| counter | 480,012 | 40.873760 | 40.906383 | 124,882,696 |
| escape | 480,006 | 43.895359 | 43.994683 | 125,073,969 |
| color | 480,015 | 40.746612 | 40.828388 | 129,884,777 |
| total | 1,920,046 | 168.946978 | 169.276643 | 510,002,619 |

The color/original CPU ratio is 0.938187, but these are concurrent capped OPEN trials. Partial traces and the exact standalone benchmark solver binary were not supplied for independent replay. Therefore this is descriptive arithmetic, **not a full-row speedup**, and cannot imply a full-row SAT or UNSAT result.

The selected child-cube records show 114 conflicts without and zero with the color batch over 16 selected cases in each treatment. These are deliberately selected small cubes, with no retained per-child native proofs. They demonstrate the intended local purging effect, not a closed wall row or a general search advantage. Likewise, 135 minimum words on ten mapped parents were not refuted by unit propagation; this is an undetermined UP status, **not SAT**.

Even the timing boundaries are incomplete. The six archived batch `total_s` sum to 4.010449 s and `replay_s` to 1.868089 s, but `total_s` stops before persistent CNF/proof/JSON writes. The solver `materialize_s` field ends before the solver input file is written. Candidate generation, proof production, recording and solving therefore are not one fully timed cold pipeline. No amortized claim follows.

## 5. Checks and residual limits

The three independently written reports, reconstruction code and native receipts are retained under `.ultramath/smwznkmmj/m1`, `m2` and `m3`. All three were individually accepted by the coordinator.

Coordinator checks include [counter/miter semantics](checks/counter-control.json), [archive identity](checks/archive-identity.json), [complete binding reconstruction](checks/binding-receipt.json), [all sender geometries](checks/geometry-receipt.json), [actual gap transport](checks/004097-transport-receipt.json), [actual batch-0 export](checks/panel-0-color.json), and [benchmark arithmetic](checks/benchmark-scope.json).

No pure-kernel Lean check was requested or performed; the proof gate here is native DRAT/RUP checking and independently reconstructed mathematical semantics. No production ledger, queue, campaign or wall-row status was changed. No new performance solving, full parent SAT search or 1,300-row campaign was run.
