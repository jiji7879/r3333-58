# What the full-cover local-witness file is doing

## Short answer

The package is a **local constraint-learning and repair** result. It verifies
explicit small colorings, finds assignment-specific obstructions, computes new
local models that avoid them, and measures how far conditional degree caps
apply. It is **not** a K58 coloring, a full representative refutation, or a new
Ramsey bound.

The word "cover" has three different meanings that should not be conflated:

- A local witness can cover **every edge inside a finite projection**.
- The saved inventory assigns one such local witness to **every enumerated
  normalized case/owner/color key** in its selected cover of cases.
- It does **not** exhaust every local model, give a single coherent global
  assignment, or prove/refute extensions for the complete $K_{58}$ graph.

Many branches are easy to finish locally, while remaining unknown on the
original full graph. This is exactly why the small-versus-global distinction
matters.

## Actual checks performed

Using the attachment's source code under the audited initialized campaign modules,
with all helper and engine paths absolute, the following passed:

| Replay/check | Result and limits |
| --- | --- |
| `replay.py --local` | 59 root-cap and 334 other degree-cap proof records, plus both case-0 repairs |
| `scale.py --verify` | 19,048 normalized local checks spanning 1,967,548 revised and 1,260,830 original branch incidences |
| `obstruction.py --verify` | The supplied six-vertex contradiction certificates |
| `lift.py --verify` | 51 original-owner UNSAT support queries; all 118 relaxed support models check |
| `avoid.py --verify` and `clashes.py --robust` | Zero residual clashes for the tested exterior-spoke family across all listed branch incidences |

Two additional independent programs checked all 38,096 initial/robust local
strings and all ten bounded case-0 assignments, including exact projection,
word/order, pivot, owner, palette, degree and sign conditions. The strict native
proof paths required a zero exit status, exactly one `s VERIFIED`, and no
warnings.

These are checks of the finite objects and reported local searches, not a fresh
full-wall execution or an independently reconstructed final Ramsey reduction.

## Three kinds of object, not one

### 1. Local projection witnesses

The 11,585 rows collapse to 41 normalized constraint geometries. Those yield
19,048 saved normalized case/owner/convention/color records. Projections contain
22–26 vertices. One saved local assignment is reused on many physical branch
incidences; it is not an independently constructed coloring of each whole graph.

Case 0 has 25 selected vertices and 300 assigned edges. K58 has 1,653 edges, so
there are 1,353 edges still to determine under the global constraints. Its two
stored branches are palette indices 1 and 2, mapping to physical colors 0 and 3.
Local 1/2 being candidates is not a new change of colors.

The retained `case0.json` examples also differ from the currently selected
initial/robust strings for that owner. They must not be silently treated as the
same assignments across versions.

### 2. A fixed local obstruction and its replacement

For the retained case-0 witnesses, vertices 43 and 44 each have ordered colors
$(3,2,1)$ toward anchors $(1,10,12)$. Vertex 5 has that same ordered color triple
under the signed row. Each pair among $\{43,44,5\}$ is consequently barred from
three colors and forced to the fourth, producing a monochromatic triangle.
That is a complete local contradiction of the **particular assignment**, not a
proof that the owner branch or entire representative is impossible.

The repair does not keep all 300 old edge colours. It preserves the nominated
14-vertex arm (91 edges) while changing 54 and 71 of the other 209 old non-arm
edges, respectively. It yields checked models on 26 vertices (325 edges), with
32 vertices and 1,328 other edges still unresolved.

These observations are compatible:

- this old fully pinned assignment cannot include vertex 5;
- another assignment preserving the arm can include it;
- that new partial model still need not extend globally.

Growing the fully pinned old witness and recoloring non-arm edges are different
operations. One cannot compare their success/failure records as if they were the
same constraint problem.

### 3. Conditional degree/support bounds

The root-cap query deletes a particular pivot-color unit while retaining the
revised owner constraints. The later 334 records additionally pin a branch color
and are separate, conditional hypotheses; one must not silently merge or add
the two coverage sets.

Exactly 51 original-owner UNSAT support payloads transfer to the original roster.
The 59 `words` and 59 `row` support models are compatible only with the named
relaxed local queries; they are checked finite witnesses, not complete row or
K58 models. Relaxing owner information does not justify transferring a cap to a
whole unsplit row.

The current banks cover selected owners and branches, not a common fixed target
uniformly across all owners. In fact, the census reports **zero rows with a
single common covered vertex across all owners**. That is a limitation of this
bank, not a proof that future cap lemmas cannot succeed. More broadly, a cap's
proof and its numerical degree interpretation/physical transfer must be justified
separately.

## Why growth does not finish the problem

`grow.py` freezes all 300 old edges. Its satisfiable returned strings are checked
partial models. Its false answers are recorded solver/domain verdicts, without a
retained independent proof object. Its null answer at 34 vertices is a timeout:
`OPEN_UNKNOWN`, not UNSAT. The bisection treats false and null alike, which is a
search heuristic, not a proof of a maximum prefix. Different vertex orders also
have different partial constraints.

Consequently it does not establish that either original case is impossible at
31, 34, 37, 51 or 58 vertices, and it does not decide the parent. SAT at 26 or 33
is not SAT at 58, and an unproved "UNSAT at 37" is not a completed structural
upper-bound certificate. The six-vertex example shows what a real finite
certificate for a fixed assignment looks like.

## What is the actual bottleneck?

A local record establishes, for a given branch and projection, a finite model.
It does not establish the existence of one full K58 assignment. In schematic
form:

$$\forall b\,\exists y_b\;\operatorname{Local}_b(y_b)
\quad\not\Rightarrow\quad
\exists X\;\operatorname{Global}(X).$$

For a global counterexample, one branch needs a compatible full assignment on
all 58 vertices. Its restriction would then induce a valid local model. For a
whole-row refutation, every required branch has to be refuted, with valid
composition/sign transfer. Hundreds of normalized records reused over a large
branch inventory address neither condition by themselves.

The useful progress is therefore **better local constraints and fewer bad local
choices**, on a much smaller shared normal form. The remaining work is global
compatibility: complete host clauses, joins, degree/ticket conditions and the
final graph-wide proof or search. No production ledger change or whole-row
closure follows from the local full cover, and `UNKNOWN` still means UNKNOWN.

## Unit-count clarification

Case 0 has 404 fixed row-edge unit literals. Its revised owner machinery adds ten
pin units and one auxiliary owner gate (`-19172`). The complete representative
therefore has 415 unit clauses. The two apparently different row-unit counts in
the reports are just different countable sets.

## Evidence files

- `replay-local.log`, `scale-verify.log`, `lift-verify.log`,
  `obstruction-verify.log`, `avoid-verify.log`, and `clashes-robust.log`;
- `bounded-obstruction-growth.log`, `independent-support.log`,
  `case0-witnesses.json`, and `summary.json`;
- `independent/`: the three accepted structural/projection, obstruction/growth,
  and degree-bank reviews.

The input archive SHA-256 is
`d9d5a68214d1692237b6b3cc332f2116b3d90064f1f178b5b00497138d70cf3d`.
