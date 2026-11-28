# Color-resolved `wallcc` candidate

`color_pivot.py` is an isolated augmentation layer over the separately cloned
`wallcc` toolkit.  It uses the audited 240-configuration / 11,585-binding cache
in `color_cache/`.  No upstream toolkit, production queue, or ledger is read as
a writable output.  The copy candidate for `tools/color-resolved-wallcc` is the
whole directory containing this file; the directory `../original-wallcc` is only
a pristine comparison fixture and is not an installation dependency.

## Commands

Use the pinned Python with `python-sat==1.9.dev22` and the bundled checker.  In
the audited workspace that Python is `.scratch/k58/.venv/bin/python` relative to
the project root.  From the candidate directory, with `PY` set to that
executable:

```sh
# Generate original, counter-only, positive-escape, and full color CNFs.
"$PY" wallcc.py color-export --row 00032f347903 \
  --out /NEW/row0-export --checker "$PWD/bin/drat-trim"

# A normal frozen-row run is unchanged.  Explicit off is the same path.
"$PY" wallcc.py prepare --row 00032f347903 --tier first \
  --pivot-color off --depth 1 --out /NEW/baseline

# Certify and prepare a color-augmented parent; CAS remains available.
"$PY" wallcc.py prepare --row 00032f347903 --tier first --cas pentagon \
  --pivot-color color --depth 1 --out /NEW/color \
  --checker "$PWD/bin/drat-trim" --check-seconds 120

# Run bounded leaves, then independently replay both leaf evidence (if any)
# and the native augmentation derivation.  OPEN verify deliberately exits 2.
"$PY" wallcc.py run --row 00032f347903 --tier first --cas pentagon \
  --pivot-color color --depth 1 --out /NEW/color --jobs 1 \
  --seconds 5 --conflicts 100 --checker "$PWD/bin/drat-trim"
"$PY" wallcc.py verify /NEW/color --jobs 1 --checker "$PWD/bin/drat-trim"

# Executable controls; choose a new output directory.
"$PY" color_selftest.py --checker "$PWD/bin/drat-trim" --out /NEW/color-selftest
```

`color-export` refuses to overwrite differing artifacts.  `original.cnf` is the
byte-exact ordinary parent.  The other three files share one counter allocation:
`counter.cnf` adds only the comparator definitions, `escape.cnf` adds the
minimal positive escape transversals, and `color.cnf` adds both those clauses
and every guarded physical-pivot rule.  `color-receipt.json` records headers,
raw and body hashes, byte counts, exact definitions and added clauses,
thresholds, geometry, cache hashes, and the native query/proof hashes.
`color-query.cnf.gz` and `color-proof.drat.gz` are retained for direct replay:

```sh
# After decompressing the two files into NEW/replay:
bin/drat-trim NEW/replay/color-query.cnf NEW/replay/color-proof.drat \
  -I -f -W -U
```

`--pivot-color` requires `--row --tier first`.  A null-pivot row, retry-tier
recipe, or external DIMACS cannot silently enter this route; use `off` where the
ordinary toolkit supports that row/input.  Augmented splitting retains the
ordinary physical literal limit 6612, not the larger auxiliary top.

## Proof and model scope

For each original declared maximum `N`, fresh counter variables are allocated
contiguously above `N`.  The six comparator clauses at each node are exactly
`h = p OR c` and `l = p AND c`; consequently each original physical assignment
has precisely one extension.  The native miter proof derives every escape and
color target from the exact original parent plus those definitions.  A model of
an augmented parent projects to an original model, and every original model
extends to satisfy all derived additions.  The rules include all three physical
pivot guards.  Their `T_(m+1)` alternative retains each above-minimum branch;
only the exact-minimum alternative is forced.

A `VERIFIED_UNSAT` or `export-drat` result on an augmented run is a checked
refutation of the **aux-extended parent**, accompanied by this independently
replayed native derivation from the original plus definitions.  It is not
relabeled as a monolithic DRAT refutation of the original-only CNF.  OPEN,
capped, missing, or failed proofs never publish a parent closure.  The included
100-conflict smoke searches are intentionally only interface tests; they do not
measure a speedup or solve an ordinary wall row.

## Checks performed in the member workspace

The inherited K5/K6, cube-cover, sharding/resume, damaged model/proof, capped
retry, and both DRAT-export selftests passed.  The color selftest generated all
24 formulas on the six audited benchmark rows and matched every benchmark hash,
then passed all six native derivations.  It checked 510 network input words,
all 2,914 row-0 physical local words against all 36 targets, and obtained native
rejection after deleting the 122-step target derivation block.  One additional
non-benchmark binding also passed native transport/replay.  No full row closed.

## Native engines and proof warnings

The package also carries the exact supplied CaDiCaL 2.1.2 executable as
`bin/cadical-2.1.2`, SHA-256
`a4a6dc61458f4fbb86cd4084e0249b0e93aae239816d58c3fb707a0a0bc7e48b`.
Kissat 4.0.4 remains `bin/kissat`, SHA-256
`b77de62fb1945d2ffab165b1f05e25c9e8ae7fc43de3a4fb8346fc2c9954097f`.
The ordinary inherited wallcc worker continues to use its documented
CaDiCaL 1.9.5/python-sat backend; adding clauses does not silently change it.
For a direct native control on exactly the exported formula, use an explicit
engine and budget, for example:

```sh
"$PWD/bin/cadical-2.1.2" --seed=0 -c 2000000 --stats \
  /NEW/color.cnf /NEW/search.drat
# or:
"$PWD/bin/kissat" --seed=0 --conflicts=2000000 \
  /NEW/color.cnf /NEW/search.drat
```

Solver exit 0 or a conflict cap is **OPEN**, not unsatisfiable. A terminal
UNSAT is accepted only after `drat-trim` succeeds on the exact input (and, for a
cover, the cover and its composition are checked). A SAT answer needs an
independently checked model. If the raw proof produces backward-deletion
warnings, do not use `-w` to hide them. Instead remove only deletion records
with [helpers/strip_binary_drat.py](helpers/strip_binary_drat.py), and then run
`drat-trim` warnings-fatally as shown in that helper's README. These optional
binaries and helpers let the certifying lead and cross-check use different
engines without grafting new clauses into the native solver code itself.

The matched full-row experiments remained OPEN, so none of these commands is a
recommended promise of solving the wall. Do not make Glucose-style reducer mode
a default merely because it was supplied in an archive.
