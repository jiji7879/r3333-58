# Solver improvement: what transfers, and what did not work

## Bottom line

The verified Ultramath branch work supplies useful **clauses and protocol
machinery**, but it does not justify replacing the existing solver defaults.
The best immediate imports are the degree/support encoders, exact criticality
guards, structural cube choices, and ordinary per-leaf DRAT certificates.

A direct first experiment on your **four-row `81e8` native whole-row input** did
**not** show a speedup from adding all degree caps. That negative measurement is
more informative than claiming a generic improvement from successful local
cases. Do not enable the blanket cap indiscriminately.

Tested profile: `(16,16,13,12)`, the existing `81e8` row. No work on the excluded
`(15,14,14,14)` profile. No perfect-degree balance was assumed.

## Matched CaDiCaL checks

Baseline input, rebuilt byte-identically to the supplied native record:

- SHA-256: `f12e25ceed77a47b1548eca0277bbc0c76d5f3f8814e4f85e6dc77f8aabb1c54`
- variables: 21,433; clauses: 191,940; bytes: 3,632,375
- engine: `/opt/lean/bin/cadical`, **2.1.2**
- nominal budget: **100,000 conflicts per input**, with a 120-second external
  wall watchdog. Every run returned `UNKNOWN`; no incomplete DRAT was retained
  and no closure or satisfiability result is inferred.

| input | added clauses | solver CPU s | wall s | max RSS KiB | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| baseline (first comparison) | 0 | 4.698 | 4.728 | 46,340 | UNKNOWN |
| all 232 degree-cap constraints | 310,184 | 8.754 | 8.782 | 126,264 | UNKNOWN |
| baseline (targeted comparison) | 0 | 5.060 | 6.034 | 46,280 | UNKNOWN |
| unit-aware degree-cap constraints | 242,834 | 10.587 | 11.653 | 111,076 | UNKNOWN |

Thus the blanket form was about **1.86× baseline CPU** in the first comparison.
The unit-aware form reduced added clauses by **22%** (310,184 to 242,834) and
reduced peak memory compared with the blanket form, but remained slower in this
small test. The two baseline runs also differ; these are matched short pilot
runs, not claims of universal overhead ratios or proof impossibility.

Capture: `benchmark.jsonl`, `targeted/benchmark.jsonl`, and the corresponding
solver logs. The watchdog did not save incomplete proof files.

## What is worth retaining

### 1. Degree caps and support structure, with correct source hypotheses

`tools/cc/global_degree_caps.py` appends $d_c(v)\le16$ for each of the 232
vertex/colour pairs. This is an **unconditional physical consequence** of
triangle-freeness and $R(3,3,3)\le17$: the colour-$c$ neighbourhood must be
triangle-free in the other three colours. It is not a local claim that
$|N_c(x)\cap A_c|\le5$. That last statement is false in general.

The file supports two encodings:

- the ordinary full 57-literal-per-colour form, for reproduction;
- `--unit-aware`, which removes edge literals already fixed by parent units and
  offsets the threshold by forced positives. This is a logical reformulation for
  satisfying assignments of that parent, not an extra row assumption.

Input must use the frozen host(58) literals `4*edge_index + colour + 1`, and its
declared variable maximum must match its largest clause literal. Fresh
sequential-counter variables start above that maximum. The original clause
block is preserved byte-for-byte. `tools/cc/validate_degree_caps.py`
independently reconstructs the complete appended family, including the
unit-aware form.

There is one **positive control**: the encoded ordinary cap parent reproduces
the existing, independently certified m6 `n017` CNF byte-for-byte, SHA-256
`eb37b0697699c0a20213b906f305e6a86fda44dcfd4c776fb2a43729e526889a`. A negative
control rejects an undeclared parent variable before creating an output.
`tools/cc/test_degree_caps.py` covers those checks and a unit-aware suffix.

The Ultramath results motivate this material because the augmented leaf
closures needed degree/support structure. They do **not** establish that
sticking every clause on every parent is cheaper. Apply the additional support
families only where the source-criticality premises hold; in particular,
mixed/equal-kind clone-cap semantics differ, and the $c=q$ support-cap trap must
not be reintroduced.

### 2. Exact ticket guards and balanced cases

m2's `guardrow.py` and its successful counter tests supply two-sided guards
$g_x \leftrightarrow (d_c(x)\ge15)$, with $H(r)=\sum_xg_x$ and $w(r)=32$ on the
target profile. This is sound for strict/mixed/balanced cell construction,
whereas reusing a one-sided flag on a relaxed parent may not give the stated
hypothesis. The balanced active/inactive refinements have also been reproduced
in full.

But the measured 15-ticket cut already slowed the supplied comparison, and no
unsound perfect-balance patch should be introduced. A 30-ticket extension is
meaningful only under the separately stated vertexwise-ticket-balance
hypothesis; it must not be spread across a weaker inactive/reciprocal parent.

### 3. Structural C&C, with raw certificates

The verified m7 tree gives selector-guided reductions, while m6 demonstrates
that degree/support families can actually close stronger leaf inputs. The
useful combination is **structural cubes + relevant certified clauses + fresh
per-leaf DRAT**. It is not proof from longer timeouts, pure forcing literals, or
monolithic incremental solver status.

Preserved blocking clauses/assumption conversion from CaDiCaL-inccnf must be
checked on the ordinary parent. The four-row solver already has this machinery;
it is worth keeping the common proof/cube receipt format rather than throwing
away its best tested control path. Different engines must have their exit codes
normalized explicitly.

The corresponding `tools/cc` sources and the current protocol work of the new
swarm are intended to make these operations reusable, not to imply that a
reciprocal C&C tree closes a whole frozen row.

### 4. Proof reuse and deletions, not named-template reuse

The 0404 shared-frontier bundle verifies 256 exclusions among 726 assignments,
leaving 470. This is a useful candidate queue for the current open branch. The
Tatarević deletion-and-lift mechanism preserves core/source/unit maps and
replays them on the actual target parents. Its six checked local case IDs were
already certified elsewhere; exact unchanged-unit reuse on the current 1,288-row
retry tail yielded zero candidates. Those mechanisms can be reused, but their
counts must not be resold as new coverage.

K15/K16 classification and automorphism/orbit counts are load-bearing for
correct normalization, not an automatic CDCL speedup. The two zero-clone
33-vertex physical models and the feasible counting-layer witnesses are useful
warnings against spending the next experiment on clone/count bounds that
cannot supply the desired contradiction.

## Certification boundary of the supplied four-row solver

The four-row native package's scope computation, native control formulas and
two fresh controls checked previously, but its central 518-proof degree-cover
store is incomplete in the available attachment. Its named bundles
`K58_degree_certificates_1.zip` and `_2.zip` (eight inner proof shards) and the
inherited source queue are still needed to accept the whole-row degree bound as
an independently verified theorem. A two-byte final reciprocity DRAT is the
last contradiction after the bound, not evidence of that bound.

Therefore the present A/B test is an **encoder/solver experiment on the existing
parent**, not acceptance of that conditional claim and not a frozen-row proof.
Likewise, an UNSAT of a sound relaxation can transfer; SAT or a timeout gives
no full-row model or absence proof. A complete physical K58 countermodel would
need all triangles, degrees and units checked.

## Reproducing the helper checks

```sh
PY=.scratch/k58/.venv/bin/python
"$PY" tools/cc/test_degree_caps.py
"$PY" tools/cc/global_degree_caps.py PARENT.cnf OUT.cnf
"$PY" tools/cc/global_degree_caps.py PARENT.cnf OUT-unit.cnf --unit-aware
"$PY" tools/cc/validate_degree_caps.py PARENT.cnf OUT.cnf
"$PY" tools/cc/validate_degree_caps.py PARENT.cnf OUT-unit.cnf --unit-aware
```

Use the pinned `python-sat` interpreter. The helper tests do not solve the
open row. Rebuilding the original `81e8` parent uses the unpackaged four-row
solver's `cli.py emit 81e8 whole ...`; large generated CNFs are build artifacts,
not a proposed new repository evidence archive.

## Practical synthesis for the existing solver

1. **Keep the current baseline controller.** Earlier controller comparison
   favoured it over extra probe overhead.
2. **Add degree/support clauses selectively**, when the actual branch has the
   source criticality and a branch/cube can exploit the information. Use
   budget-matched conflicts and report wall and CPU separately.
3. **Retain protocol and proof discipline.** Ordinary parent per-leaf DRAT,
   parent/cube hash pinning, blocking-clause recovery, and a checked non-model
   are prerequisites, not optional bookkeeping.
4. **Prefer a compact local geometric cut next** to another broad cardinality
   augmentation. The helper and measured cap overhead are captured here so the
   next trial tests a different mechanism rather than assuming caps are free.

A live 8-member run is checking the structural-cut, policy, incremental-proof,
semantic-guard, and engine-protocol directions separately. Their reports will
be reviewed before being promoted to solver defaults.
