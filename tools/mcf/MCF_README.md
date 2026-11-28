# Opt-in `mcf-arm3` solver variant

## Status

This is an **experimental, explicitly opt-in CNF generator and benchmark
interface** for one retained hard leaf. It does not close the row, any profile,
any cover case, or either Ramsey bound.

Only the following configuration is accepted:

- row `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`,
  profile `(16,16,14,11)`, charge 7;
- frozen first-tier parent (`tables=True`, `total_critical=True`,
  `full_root=False`); the parent remains an ordinary semantic-row relaxation;
- raw arm 3, normalisation colour 0;
- cube `[-1413,1014]`: variable 1413 is negative and 1014 is positive.

These are deliberately not general full, pinned, or global maximality options.
The parent-BCP residual was independently verified and benchmarked but is not
silently selected by this raw-only interface.

## Opt-in installation

The required massive baseline is SHA-256
`cc78f1d9f6f7901615b264c9ceaa3319bd152cd4caccc381a74ed742538bdb6a`.
Check that archive before unpacking it. Create a **new copied** package; do not
apply the overlay to the production package:

```bash
tools/mcf/create_variant.sh \
  --stock .scratch/massive-clean-install/k58-solver \
  --out .scratch/k58-mcf-solver
```

The installer checks the baseline `k58.sh` hash, copies it without modifying the
source, and adds only `k58-mcf.sh`, `mcf/*.py`, and these instructions. It writes
no archive and modifies no production ledger. Run the ordinary package's
`setup` in the copy if it has no Python environment. Solver processes require
`python-sat==1.9.dev22` with `Cadical195`; the worker rejects another version.

## Prepare the exact leaf

The baseline directory must contain `plan.json`, `parent.cnf`, `working.cnf`,
and `cas.drat` for this retained row/tier. In this workspace that is
`.scratch/arm3-hard-leaf`.

```bash
PKG=.scratch/k58-mcf-solver
"$PKG/k58-mcf.sh" prepare \
  --baseline-run .scratch/arm3-hard-leaf \
  --out .scratch/mcf-run/prepared
```

`prepare` regenerates the frozen ordinary parent and working/CAS inputs, and
pins those bytes as well as the expected augmented result. Every generated
query must have these SHA-256 values:

| query | variables / clauses | SHA-256 |
|---|---:|---|
| ordinary parent | 19,533 / 184,335 | `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae` |
| parent + cube | 19,533 / 184,337 | `8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8` |
| raw arm-3 parent | 22,053 / 191,940 | `1bb7a7823b0ceac16d303de15c204b28b11d4354ec17fcf60dba7678754ff9d2` |
| raw arm-3 + cube | 22,053 / 191,942 | `fface1b819e26261736cb516be9063e7be2b1be120253875947a4400d4ac912a` |

There are 45 safe internal edges, 2,520 fresh Tseitin witnesses in the closed
range `19534..22053`, and 7,605 new clauses before the cube. The witnesses start
above the actual current parent maximum 19,533, not merely above 6,612. Every
four-literal colour block for every changing edge is absent from the actual
non-host suffix and from both cube literals. The original body and cube order
are preserved.

`normal-form.json` records each rule and allocation, file hashes, source
provenance, semantic status, and outstanding bridge obligations.
**Crucially, loading a prepared tree regenerates all rules and all query bytes
from the pristine frozen inputs.** Self-consistent receipt hashes are not enough
to bless a changed auxiliary gadget. A coordinated query/receipt mutation and a
query-only rehash are both rejected before the solver can start.

## Balanced solver comparison

```bash
"$PKG/k58-mcf.sh" run \
  --prepared .scratch/mcf-run/prepared \
  --out .scratch/mcf-run/comparison \
  --conflicts 1000000
```

The two jobs use fresh proof-enabled CaDiCaL 1.9.5 processes with the same
conflict cap and no search wall-time cutoff. Choose a cap appropriate to the
machine. `--check-seconds`, default 300, limits certificate checking only.
Small conflict-cap overshoots are retained verbatim rather than relabelled as a
completed search.

- **OPEN** means only that the cap was reached. No model or incomplete DRAT is
  retained.
- **SAT** requires re-evaluation of the complete returned model over the exact
  query. It does not produce a physical colouring or original-parent model.
- **UNSAT** requires independent complete parsing of CAS and leaf streams,
  valid deletion-record payloads, a joined addition stream ending in a real
  derived empty clause, and warning-fatal `-i -U -W` `drat-trim` replay against
  the exact augmented query. The reported whole-file byte read must equal the
  normalized proof length, with a RUP-only core (`0 RAT lemmas in core`). A
  working-plan/CAS replay is attempted separately, without pretending that MCF
  is parent-derived DRAT. A future target proof still requires the agreed
  independent second-verifier review before any broader certificate promotion.

The existence-preserving normal-form reduction is separate from the DRAT
proof. It has a kernel-checked Lean theorem; exact cube/non-host disjointness is
necessary. The ordinary-parent physical `hbase`/`hvars` bridge is now formalized
in `lean/K58/PhysicalBridge.lean` conditional on a physical expanded-row
realization. Candidate criticality, the 112-entry P4/C5 support geometry,
coded-plus-automatic sender-set equalities, and the induced `ChainReady` remain
open. No augmented source is admitted to stock `finalise`.

## Checks

To build a fresh package and run the bounded interface controls:

```bash
"$PKG/.venv/bin/python" "$PKG/mcf/package_controls.py" \
  --package "$PKG" \
  --baseline-run .scratch/arm3-hard-leaf \
  --out .scratch/mcf-run/controls
```

This runs preparation/readback, a one-conflict OPEN interface pair, a genuine
three-pigeon/two-hole UNSAT plus CAS+leaf replay, terminal-empty and malformed
DRAT rejection, ten primitive tests (including 807,936 exhaustive K4
normalisations), a generator-free schema audit, malformed inputs, both
rehashed-query tamper cases, and the ordinary wallcc 20/20 smoke suite.
It makes no target UNSAT or runtime claim.

## Measured retained-leaf outcome

At two million conflicts both parent+cube and raw arm3+cube remained **OPEN**,
with respectively 855,298,483 and 884,198,407 propagations and 209.925347 and
209.685391 solve-CPU seconds. At one million (reverse order) the counts were
381,196,308 and 385,980,874; both were OPEN. Three fresh 1M parent/residual
pairs reproduced deterministic counters; the coordinator's third pair took
62.374832 and 61.123102 solve-CPU seconds, again both OPEN. The residual
removes 465 parent-satisfied suffix clauses while preserving all 45 long MCF
clauses and every fresh witness, and is logically equivalent to the raw
augmentation in the presence of the parent. Neither variant supplied a proof
or a retained-leaf propagation improvement. The old no-cube throughput result
must not be quoted as performance on this leaf.
