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
