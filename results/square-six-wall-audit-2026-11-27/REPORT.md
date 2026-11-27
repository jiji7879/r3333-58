# Square/six-rule direct-wall experiment, 2026-11-27

## Result

**All sixteen fresh three-second searches returned UNKNOWN. No cube or original
wall row was closed, no SAT model was produced, and no Ramsey bound moved.**

The experiment compared stock with stock plus the 1,020 selected short
implications on branch 44 of `(16,16,14,11)`, row
`4a71c66153af2a1cb64fc609b92bdd3dc93714fb3983a687812849a19f1798b2`.
It used eight exhaustive, disjoint depth-three cubes on physical variables
294, 2846 and 2850, placing each cube's three literals in three unit clauses.
Both arms included exactly the same 189 stock pentagon clauses; the augmented
arm additionally included exactly the same 1,020 short clauses in fixed order.

| Arm | Calls | OPEN_UNKNOWN | VERIFIED UNSAT | Search seconds | Process-wall seconds | Conflicts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| stock | 8 | 8 | 0 | 24.018709 | 25.028238 | 660,787 |
| stock + 1,020 short | 8 | 8 | 0 | 24.041185 | 25.040885 | 744,144 |

Totals: 16 fresh calls, 48.059893 seconds of measured native search,
50.076460 seconds for the solver loop, 3,002,843 stock decisions and
4,890,619 augmented decisions, and 214,379,275 versus 180,985,441
propagations, respectively. There were no external cutoffs, launcher failures,
SAT models or native UNSAT results. Per-call and per-cube measured times are in
[pilot-summary.json](pilot-summary.json). Native deadlines nominally allow
small timer/scheduling overruns, hence the measured total slightly exceeds
48 seconds; this was not edited down to the nominal budget. The run is a single
matched low-budget sample, not a statistically supported speed comparison or a
reason to scale the search.

The final independent receipt audit pass is
[pilot-validation.json](pilot-validation.json). Its checks include every
summary record against its per-leaf receipt, every actual query and
original-parent proof target against the independent design-audit hashes, and
all paired timings/statistics. **No fresh solver UNSAT or SAT occurred, so the
new native-proof composition and model-checking branches were not exercised on
this panel.** The old package benchmarks are not substituted for this new run.

## What the “six rules” actually are

The supplied package describes **one guarded conditional-triangle schema**, not
six universal inference rules. If $x,u,a,b$ are distinct, $r$ and $b$ are
distinct colours, and the frozen colours $ua=ub=r$ and $ab=b$ hold, then

$$E_{xu,r}\ \Longrightarrow\
\left(E_{xa}\in\{r,b\}\ \Longrightarrow\ E_{xa}=b\right)$$

and similarly for $xb$. Red alternatives on either spoke would make red
triangles; together they would make $xab$ blue. Equivalently, the parent admits
one colour per edge, forbids monochromatic triangles, and entails the short
clause $\neg E_{xu,r}\lor O_{xa}\lor O_{xb}$, where $O$ asserts a colour outside
the pair. Joining two such patterns with $uv=b$ gives four-, five- and
six-vertex obstructions. The title's “six” refers to six-vertex patterns, not a
menu of six rules.

The branch-44 augmented formula uses 1,020 selected, unit-simplified instances:
364 of width 3, 306 of width 4 and 350 of width 5. The earlier 384 selected
direct goals (192 square and 192 six-site) are a different encoding and were
not added in this particular stock-versus-short pilot.

Three independent Ultramath audits in swarm `smwz646yy` were accepted after
independent reruns:

- [Rule semantics](audits/REPORT.md): checked the guarded implication, an
  explicit ten-clause RUP core in the original parent for the documented real
  selection, and faithful K4 positive and guard-broken controls. Reproduction
  returned exact `s VERIFIED` for the positive control and exact
  `s NOT VERIFIED` with an explicit physical countermodel for the broken guard.
- [Experiment design](audits/report.md): an independent 126-check script
  reproduced the zip/manifest, parent, clause serialization, proof-prefix
  shapes, exhaustive/disjoint cubes and all leaf hashes. Its important
  acceptance requirement was adopted: if a native suffix refutes a leaf, replay
  it against the exact native leaf and then after the *arm-appropriate* prefix
  against the original parent **plus the same three cube units**, not bare P or
  with the wrong prefix.
- [Catalog and finite template census](audits/catalog_audit.md): reproduced the
  four-template counts, every rim-colour cell (supplementing an omission in the
  packaged check), both documented examples and the marked-cycle arithmetic.
  Completeness is only for abstract two-color spokes on the supplied matrices;
  it is not physical parent or wall coverage.

These are scoped audits, not a solution of the Ramsey problem. A “solved”
swarm status here means the three requested audits were accepted.

## Exact parent and proof-prefix verification

The parent was independently regenerated using the audited initialized runtime's
`engine/problem.py::row_formula(row, "first")`. Its 3,487,573 bytes are
**byte-identical** to `evidence/parent.cnf.gz` decompressed, with SHA-256
`33b7898ed58bd1a3a2e088f57d4bc9d01b5397e7b72f1f5f1449a7bf16f4a02a`.
The original solver environment supplies this generator; this does not replace
the still-missing global semantic bridge for the K58 reduction.

All 38 packaged manifest payload hashes match both zip members and extraction.
The direct formula hashes are:

- stock: `cb2df48f63eb7ba91d3bdb92a92cc830e5f0826d89366b52d68af80e221d33dd`;
- stock + 1,020 short: `6267a8fe7ee242ac6aabf18a440cc19686505ea78e269f465ec263a5636d856d`;
- combined stock + short prefix:
  `6bcc793f59fc3a4e3f4e04c751be03c8bddfc71208fe7f409b7934856d0d3936`.

`tools/refinement/verify_square_six.py` strengthens the packaged wrapper: it
removes warning suppression, requires exit 0, exactly one `s VERIFIED` status
line and no warnings, and retains the full output. Its three successful replays
against the frozen original parent (using selectors for the violation
obligations as the package specifies) were:

| Obligation | Proof bytes | SHA-256 |
| --- | ---: | --- |
| 384 direct consequences | 24,752 | `bbfe14c5a30eaa7879718da67c83866700f2b486e8121accb8e06b62bfb543fa` |
| 1,020 short consequences | 15,274 | `99b764cd7f73df68ff3f87e2f58f5bbf06fcc6af99ec476329490058d2ecc929` |
| complete 1,209-clause exact solver prefix | 126,127 | `ca0ca3f9f336b0cf98b61e45e1d7d4e5e822cac706294ec725bfb710e1df739e` |

The exact command was ordinary binary RUP checking without `-w`, with flags
`-i -U -t 300`; receipts and full logs are under [prefix/](prefix/run.log).
The package's normal verifier uses `-w` (warning suppression in its bundled C
source), so package logs alone do not satisfy this zero-warning gate. This
experiment did not trust them for that purpose.

## Selection and coverage limits

The catalog is not an exhaustive physical-wall reduction. The stored candidate
counts are 8,546 four-site and 4,736 six-site, capped at 192 selected cuts each;
their original generation/scoring implementation is absent. All 192 selected
six-site direct goals come from the 15T arm and only 16 outside vertices (none
from 16T or 16U). The square selection is distributed 6, 54 and 132 over
16T, 16U and 15T. These observations do not invalidate other candidates. They
mean that neither selection nor the template-local census can be called a
whole-row cover. The 1,020 selected short rules have separate original-parent
RUP evidence, as verified above.

Six-site two-triangle obstructions, supports admitting a monochromatic rim, and
marked six-cycles are also distinct objects and must not be counted as if they
were interchangeable.

No global claim follows from these results: the case remains OPEN, all 11,585
small-profile wall rows remain OPEN, and the established range stays
$51\le R(3,3,3,3)\le62$. The unreviewed 2026 upper-bound literature claim is
not treated as theorem here.

## Reproduction and trusted artifacts

The completed experiment is preserved rather than merely summarized:

- [pilot-summary.json](pilot-summary.json): byte-for-byte copy of all 16 native
  receipts and aggregate observations;
- [input-manifest.json](input-manifest.json) and
  [leaf-hashes.tsv](leaf-hashes.tsv): exact paired-query and original-parent
  identities;
- [pilot.log](pilot.log): visible final output;
- [parent-regeneration.json](parent-regeneration.json): byte-identity check;
- [build.json](build.json): augmentation receipt;
- [prefix/](prefix/receipts.json): strict prefix receipts and logs;
- [audits/](audits/report.md): accepted audit reports, scripts and test outputs.

The solver is CaDiCaL 1.9.5 with proof logging through python-sat `1.9.dev22`,
using the native deadline library and fresh process for every call. The leaf
worker is unchanged at SHA-256
`5ba044da68f398d3b50bea245105a304490343371ede385876a3edf4e718d850`.
The final pilot harness is `7b98b4872aef92dcda7d2fe612719ec094a75efc0b6389c0adc38e48c9b34539`.
The checked binary was rebuilt from the package's `drat-trim.c` with
`cc -std=c99 -D_GNU_SOURCE -O2`; its SHA-256 is
`039f9cc08cc094519bc1413d960c3229143597e27a69f7c4e7e313821c8cd7ab`.

The exact launched command was:

```sh
export PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.scratch/square-six-v1/tmp"
python3 -B tools/refinement/square_six_pilot.py \
  --package "$PWD/.scratch/square-six-v1/src/K58_square_six" \
  --augmented "$PWD/.scratch/square-six-v1/buildcase/branch44.cnf" \
  --prefix "$PWD/.scratch/square-six-v1/buildcase/prefix.drat" \
  --runtime "$PWD/.scratch/review-attachments-v1/audited-K58" \
  --checker "$PWD/.scratch/square-six-v1/bin/drat-trim" \
  --out "$PWD/.scratch/square-six-v1/direct-3s-v1"
```

A repeat creates a new output directory; the harness refuses to overwrite or
silently reuse an existing run. `--prepare-only` serializes and hashes inputs
without launching a solver. This was used before launch. All sixteen actual
queries and all eight original-parent proof targets match the independent
hashes. Several harness errors were caught and fixed in prepare-only mode;
none of those launches counted as a search and none supplied a result.

No larger-budget run or further wall search was started after this outcome.
