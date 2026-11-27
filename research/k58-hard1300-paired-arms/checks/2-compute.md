# Complete finite recomputation and replay record

## Input and environment

Input ZIP SHA-256:
`fa34f7aa29445eb93f52ec7d42de0705e3a01f978db03d9ced1566c808134815`.
All 56 archive members passed CRC validation. The archive has no global
`SHA256SUMS`; the strong identities are the per-record query/proof hashes,
row geometry identifiers and the 1,300 full-root CNF hash matches.

The attached source's `probe.py`, `census.py`, `check.py`, `verify.py`,
`certify.py`, `export.py`, `completion.py`, `short_panel.py` and relevant
`dense.py`, `cover_evidence.py`, `gluing.py` encoder functions were inspected
first. The pinned existing `.scratch/k58/.venv` interpreter reports
`pysat 1.9.dev22`, the same version called for by the supplied `setup.sh`.
No package/network installation was needed. `setup.sh` itself was not run,
so no new `.venv` or binary files were created in the supplied package.

## Full 1,300-root and clause census regeneration

Because generation can overwrite measured JSON files, the directory was first
copied to `.scratch/hard1300-paired-arm-v1/reproduction`. Read-only original
artifacts stay under `src/`.

```sh
ROOT="$PWD"
P="$ROOT/.scratch/hard1300-paired-arm-v1/src/hard-study"
D="$ROOT/.scratch/hard1300-paired-arm-v1/reproduction"
mkdir -p "$D"
cp -a "$P/." "$D/"
PY="$ROOT/.scratch/k58/.venv/bin/python"
cd "$D"
"$PY" -B check.py > regeneration-check.out
"$PY" -B census.py > regeneration-census.out
```

This foreground job took **45.479 seconds wall time** and exited 0. Its audit:

```text
{'hash_matches': Counter({'full_root': 1300}),
 'template_color_combinations': 48,
 'binary_K6_colorings': 32768}
```

`census.py` produced:

```text
1300 1236 16530 0 33
```

Another program compared the resulting JSON **object-for-object** with the
supplied `ternary-counts.json`, not just the totals: equality is `True`.
There are 1,300 per-row values, 1,236 nonzero rows, 16,530 total ternary
clauses, with per-row counts in 0..33. `audit.json` records the same
full_root count of 1300, 48 finite template-colour checks and 32,768 exhaustively
checked binary K6 colourings. No search timed out or was treated as evidence.

## Strict physical replays

The supplied `verify.py` was executed against a fresh drat-trim build through
the same strict wrapper used in the earlier packages. It removes `-w`, adds
a timeout, and accepts only exit 0 plus exactly one status line `s VERIFIED`
and no warnings. Since this package calls binary DRAT checker mode `-i` only,
the replay is not misreported as an original stock `-U` invocation. Its checked
core nevertheless reports 0 RAT lemmas for each of the 14 calls.

```sh
P="$ROOT/.scratch/hard1300-paired-arm-v1/reproduction"
D="$ROOT/.scratch/hard1300-paired-arm-v1/strict-replay"
cc -std=c99 -D_GNU_SOURCE -O2 "$P/tools/drat-trim.c" -o "$D/bin/drat-trim"
# ... export AUDIT_ROOT=$D, AUDIT_REAL_DRAT_TRIM=$D/bin/drat-trim, TMPDIR=$D/tmp
cd "$P"
"$ROOT/.scratch/k58/.venv/bin/python" -B verify.py "$D/tools/strict-drat-wrap.py" \
  > "$D/verify.out"
```

Actual output:

```text
Replayed 14 signed implications
```

All 14 raw logs are independently checked for a proof-read byte count equal to
the corresponding recorded complete proof length, one exact status, no
warnings/errors and zero RAT lemmas. Total proof bytes = **32,972**. The rank
list is `1,8,28,146,522,636,677,708,728,747,924,959,1121,1231`. Supplied
search-conflict counts sum to **840**; these are not independently re-timed
search runs and are not offered as a solver performance comparison.

The copied summary receipt is [2-compute.json](2-compute.json). It includes
all 14 query/proof hashes, native replay facts, the entire per-row count vector,
and the supplied long-search results marked as not retimed.

## Source identity and query semantics checked by inspection

`cover_evidence::formula_chunks` constructs `units(family,placement)` plus
`marked_threshold(...)`, and the hash identity is recomputed from exactly the
same family, placement and charge fields. `marked_threshold` excludes the root,
uses candidate literals of colour `c` in other arms, and generates an explicit
at-least-14 guard. `probe.build` binds these guard variables to their physical
senders before deriving additional clauses or replaying a physical pattern.

For each physical record, `verify.py` reads `-g,e1,e2` then adds the **negative
of each stored clause literal**, so the proof obligation is really the counter
example `g, -e1, -e2`. This is the correct sign direction throughout.

## What was not run

There was no independent Ultramath review because it was explicitly disabled.
No new SAT production sweep, no claim of Lean-kernel certification and no
800,000-conflict scale-up were used. The existing six 60k-parent runs, short
ternary-only panel and two long 800k rows remain at their recorded limits.
No actual model or full parent solution is inferred from them, no theorem is
imported that every guard is forced on, and no Ramsey bound is claimed changed.
