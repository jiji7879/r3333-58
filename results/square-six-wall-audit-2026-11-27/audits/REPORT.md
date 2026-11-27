# Direction A: short-rule semantics and bounded RUP audit

## Outcome and scope

The package implements **one conditional triangle-rule schema**, not six universal
rules.  In the branch-44 build it supplies **1,020 selected instances** of that
schema after unit simplification, together with **189 separate stock pentagon
clauses**.  The word *six* in the package title/README refers to six-vertex
obstructions.  The 384 longer selected goals (192 square and 192 six-site) are a
different, earlier encoding; they should not be conflated with the 1,020 short
clauses.

This audit establishes the local semantics, independently checks one real
selected clause against a small core of the original parent, and runs faithful
K4 positive and negative RUP controls.  It does **not** establish a global Ramsey
result, complete a row, replay all 1,020 short clauses or the stock prefix, or
run any of the 16 direct-wall searches.  UNKNOWN remains UNKNOWN.

Sources read before execution: package `README.md`, `general.py`, `verify.py`,
`build.py`, relevant option/propagation portions of `tools/drat-trim.c`, and the
JSON evidence files used below.  No package Python module was imported or run.

## The exact rule

Vertices $u,a,b,x$ must be distinct and $r,b$ must be two distinct colors among
the four physical colors.  The frozen triangle must satisfy
$$E_{ua,r}=E_{ub,r}=1,\qquad E_{ab,b}=1.$$
For an edge $xy$, define its *outside-pair* condition by
$$O_{xy}^{r,b}=\bigvee_{c\in\{0,1,2,3\}\setminus\{r,b\}} E_{xy,c}.$$
The raw short clause is
$$C(u,a,b;x,r,b)=\neg E_{xu,r}\lor O_{xa}^{r,b}\lor O_{xb}^{r,b}.$$
It therefore has $1+2+2=5$ literals before unit simplification; it is not
intrinsically a three-literal rule.

To verify the implication, falsify $C$.  Then $xu$ is red and the outside-pair
colors of $xa$ and $xb$ are false.  Since each physical edge has a color, $xa$
and $xb$ lie in $\{r,b\}$.  A red $xa$ would make $uax$ a red triangle, and a red
$xb$ would make $ubx$ a red triangle.  Hence both are blue, making $abx$ a blue
triangle, contrary to the parent constraints.  This is also the unit-propagation
chain for the usual direct four-literal at-least-one encoding of edge colors.

**Scope guards.** The two center spokes must both have the *same* red color;
the base has the distinct blue color; $x$ is outside the triangle; the two other
colors are exactly the complement of the chosen pair; and the parent must encode
at least one color per edge and forbid monochromatic triangles.  Logical validity
for an arbitrary auxiliary encoding is not enough: RUP must still be checked on
the actual CNF.

In `general.py`, the guards are explicit: `red != col(u,b)` enforces equal center
spokes, `red == blue` is rejected, `x in (u,a,b)` is rejected, and `other` is the
complement of the chosen pair.  A clause already satisfied by a root unit is
skipped; literals whose negations are root units are removed.  The selection-time
`raw.propagate` check uses the original base, not the stock-augmented database,
and requires conflict under falsification.  Stock is used to prefer new UP
consequences, not as a semantic substitute for the original-parent proof.

## Why two triangles give square/six-vertex obstructions

Take a second frozen triangle $vcd$ with $vc=vd=r$ and $cd=b$, and freeze $uv=b$.
If every spoke from $x$ into the union is in $\{r,b\}$, the one-triangle argument
forces $xu=b$ and $xv=b$.  Then $xuv$ is a blue triangle.  Consequently at least
one spoke into the union lies outside the pair.  With $2,1,0$ shared vertices in
$\{a,b\}$ and $\{c,d\}$, the union has $4,5,6$ vertices respectively.  Sharing
both outer vertices gives the red four-cycle with blue $uv$ and $ab$ diagonals;
disjoint outer pairs gives the stated six-vertex pattern.  This is a conditional
local obstruction, not a declaration that every wall node is covered.

## Real branch-44 witness: independent RUP core

Using zero-based vertices as in `wedges.json`, the README square witness is
$$(x,u,a,b,r,b)=(17,2,4,11,2,3).$$
The raw clause is
`[-511, 937, 938, 2309, 2310]`.  Original-parent units `-938` and `-2310`
make two literals false, yielding the stored selected clause
`[-511, 937, 2309]`.  This exactly matches the second `short_examples` record;
no already-true raw literal was found.

The audit parsed all original-parent clause rows and checked canonical literal
set membership for the following ten-clause core (all ten are present):

- units `459, 487, 916, -938, -2310`;
- red-triangle clauses `[-459,-511,-939]`, `[-487,-511,-2311]`;
- edge at-least-one clauses `[937,938,939,940]`,
  `[2309,2310,2311,2312]`;
- blue-triangle clause `[-916,-940,-2312]`.

Falsifying the stored goal assumes `511,-937,-2309`.  The two red clauses force
`-939` and `-2311`.  The at-least-one clauses then force `940` and `2312` (the
blue spokes), and `[-916,-940,-2312]` is falsified.  This proves RUP for this
one selected clause from an explicit original-parent core.  It does **not**
verify the other 1,019 clauses, their serialization, or the full prefix.

## Executed positive and negative toy controls

`rule_semantics_audit.py` independently constructs all exactly-one-color K4 edge
constraints and all four-color non-monochromatic-triangle constraints.  With
$(u,a,b,x)=(0,1,2,3)$, $r=0$, $b=1$, and other colors $2,3$, the candidate is
`[-9,19,20,23,24]`.  An independent unit propagator reports conflict
`[-14,-18,-22]` with the expected two forced blue spokes.

A violation-selector query and a deletion-free binary DRAT proof were then
checked using only `-i -U`, with the wrapper requiring exit 0, exactly one status
line equal to `s VERIFIED`, and zero lines containing `WARNING`.  The result was
**exit 0, `s VERIFIED`, zero warnings, zero RAT lemmas**.  The real-parent core
above was independently propagated; the strict checker was used on this compact
faithful toy rather than represented as a full-parent replay.

The negative control changes $ub$ from red to color 2 while retaining the same
candidate.  The explicit physical coloring (zero-based edges) is
$$ua=0,\ ub=2,\ ab=1,\ ux=0,\ ax=1,\ bx=0.$$
Every K4 edge has one color, every K4 triangle is non-monochromatic, the selector
query is satisfied, and the candidate is false.  Its replay correctly gave
**exit 1, `s NOT VERIFIED`, zero warnings**.  Removing the identical-center-spokes
guard is invalid, not merely a different notation.

The supplied `tools/drat-trim` lacked execute permission in the extracted zip.
It was not chmodded or modified.  Its read C source was compiled with the system
C compiler into this member's `audit-bin/drat-trim`; no external solver or SAT
search was used.

## Selected data and interpretation limits

`evidence/wedges.json` contains exactly 1,020 final clauses with lengths
**364 of length 3, 306 of length 4, and 350 of length 5**.  These are selected
unit-simplified instances, not six rules and not a claim of universal coverage.
The 235/917 targeted-probe ratio and older search OPEN statuses in the package
were not treated as proofs or extrapolated to new cube results.

## Certificate-control issue

`verify.py::check_proof` invokes `drat-trim ... -i -U -w`.  In the bundled C
source, `-w` sets `NOWARNING`; it suppresses warning text.  Therefore the helper
cannot support an independent assertion that no warning occurred.  It also uses
a substring test for `s VERIFIED`, rather than the strict status-line test used
by this audit.  For the requested acceptance protocol, run the normal checker
without `-w`, require exit 0, exactly `s VERIFIED`, and inspect the complete
output for zero warnings (or separately enforce hard warnings).  This is an
instrumentation caveat, not a counterexample to the local implication.

## Required controls for the direct-wall use

1. Preserve the exact guarded pattern and variable/row identity for every short
   clause; do not synthesize another six-rule set from the ambiguous request.
2. Keep the original parent as the semantic base.  Stock and short clauses may
   aid search, but must not be justified from a status/learned-clause cache.
3. Bind every appended goal to deletion-free proof bytes accepted under strict
   binary RUP `-i -U` on the intended formula; bind the complete prefix to the
   original parent when replaying a native leaf proof.
4. Count setup separately from search, treat each 3-second timeout as OPEN, and
   check any native SAT assignment against every clause and physical edge/triangle
   coloring.  No local template census or one-clause core fills a whole row.
5. Do not let `-w` substitute for a zero-warning check.

## Artifacts and reproduction

- `rule_semantics_audit.py`: deterministic generator, independent UP checks,
  real-core membership checks, binary proof encoder, and checker wrapper.
- `audit-run.json` and `audit-out/results.json`: normal-mode summary output.
- `audit-out/real-square-rup-core.json`: all real parent core clauses and trail.
- `audit-out/rup-trail.json`: detailed positive toy propagation reasons.
- `audit-out/guard-countermodel.json`: explicit negative-control coloring.
- `audit-out/good-rup.{cnf,drat,log}` and
  `audit-out/bad-guard.{cnf,drat,log}`: strict checker inputs and raw outputs.
- `SHA256SUMS`: hashes of the report/script/test evidence.

From this member directory, reproduction uses an absolute package path and an
owned executable/output path:

```sh
PKG=/absolute/path/to/.scratch/square-six-v1/src/K58_square_six
cc -O2 "$PKG/tools/drat-trim.c" -o "$PWD/audit-bin/drat-trim"
python3 "$PWD/rule_semantics_audit.py" \
  --package "$PKG" --checker "$PWD/audit-bin/drat-trim" \
  --out "$PWD/audit-out" > "$PWD/audit-run.json"
```

The last successful run exited 0.  No full `verify.py`, benchmark, cube,
propagator-based search, or general row compiler was run.
