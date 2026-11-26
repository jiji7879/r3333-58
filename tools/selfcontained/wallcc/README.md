# `k58.sh wallcc`

Optional single-row cube-and-conquer for the K58 wall. This is a separate
frontend to the existing cover runner, not a replacement and not an assertion of
a new Ramsey bound.

## What it actually does

- `wallcc.py` prepares a frozen wall row from the pinned local recipe, or accepts
  a supplied DIMACS formula. The tier is explicit. Parent SHA-256 and the cube
  plan are immutable in a run directory.
- It splits by lookahead and can use the derived pentagon clauses. A frozen row's
  `--tier retry` includes its `full_root` floor; it does **not** impose perfect
  degree balance.
- Each leaf is solved as a fresh ordinary formula including its cube's unit
  literals, not as a certificate-taking assumption. `campaign.py` binds the
  plan, every leaf receipt and its local artifact by hash.
- Only a complete, checked cover allows export of a parent-level DRAT.
  `verify` replays every checked leaf again. `export-drat` additionally combines
  and verifies a whole-parent proof. OPEN cubes, MODEL_READY cubes and incomplete
  covers never receive a parent closure claim.
- It can reduce a formula with `rootreduce.py`, whose clause/witness trace is
  verified independently by `check_trace.py`. This preserves equivalence and
  is intended for output/protocol cost, not promised speedup.

Use the pinned Python 3.10–3.13 environment from `./k58.sh setup`, with
`python-sat==1.9.dev22`. The current smoke procedure uses PySAT's
`Cadical195` binding; the bundled `bin/kissat` remains available separately.
The incremental `p inccnf` path needs different assumptions: only complete
cube coverage with base-level DRAT should be accepted. IDRUP output and a trace
prefix are not automatically an ordinary leaf proof. `leafcert.py` supplies the
conservative per-leaf + exhaustiveness-check route.

The original toolkit lacks `smoke-results.json`. Hence running `selftest.py
--wall <row>` directly needs that external fixture. It is absent here and is
not fabricated. The ordinary `selftest.py` suite (K5/K6, branching, resume,
replay and proof exports) nevertheless passes; the wall pilot itself ran
successfully with real row preparation and local pentagon derivations.

## Commands

```sh
./k58.sh wallcc rows --profile 16,16,13,12 --limit 10

./k58.sh wallcc run --row <full/unique-row-prefix> --out runs/wallcc/my-row \
  --tier retry --depth 1 --jobs 2 --conflicts 100000 --seconds 120 \
  --checker "$PWD/bin/drat-trim"

./k58.sh wallcc resume runs/wallcc/my-row \
  --conflicts 400000 --seconds 180 --jobs 2 --checker "$PWD/bin/drat-trim"

./k58.sh wallcc verify runs/wallcc/my-row --jobs 2 --checker "$PWD/bin/drat-trim"
./k58.sh wallcc export-drat runs/wallcc/my-row parent.drat \
  --method compact --checker "$PWD/bin/drat-trim"

./k58.sh wallcc-smoke
```

`run` and `resume` use a run directory, normally `--out`; `verify` takes it as a
positional argument. A return of `COVER_READY` only prepares a cover. Require
`VERIFIED_UNSAT` from `verify` AND `export-drat` before calling that parent
closed. `OPEN` with conflict-limit receipts is still open, never an UNSAT
completion. `--again` deliberately reruns unchanged OPEN settings; otherwise a
new budget triggers a retry and completed checked leaves are reused.

For a different self-contained input:

```sh
./k58.sh wallcc run --cnf external.cnf --out runs/wallcc/external \
  --depth 1 --jobs 2 --conflicts 100000 --checker "$PWD/bin/drat-trim"
```

`--tier retry` or `--cas pentagon` require `--row`; they do not have a generic
meaning for a supplied arbitrary CNF. If external CNFs include auxiliaries, the
splitter may choose them, so branch policies can vary and are not per-cube
speed measurements.

## Entrance projection (optional)

`entcap.py` projects only the certified `(16,16,13,12)` entrance families:

- `TT--`: points of the 13-class;
- `TU--`: points of the 12-class;
- `UU--`: no cut.

With a real parent carrying the root's template pins, `entcap.py build
PARENT.cnf STRENGTHENED.cnf --direct` adds at-most-14 counters for non-own-class
literals of each eligible point, which is exact for degree $\le15$ in its root
colour. The `--direct16` form is a size-matched redundant control, not a fresh
strengthening. The `--caps-only` form omits the ternary of the `full` form.

Run that same file as the external CNF so it is not silently resubstituted by
its unaugmented frozen-row recipe. Keep baseline and augmented output dirs
separate, keep the old parent hash, and do not apply this to `UU--`, undecoded,
or otherwise unsupported roots. `--depth 1`/`--jobs` etc. work as usual.
The parent used in the measured experiment remained OPEN under both settings;
this is not a default preprocessing promise.

The four-row package's 518-degree-proof archive remains missing. No use of that
conditional degree-cover result as a proven theorem is licensed by this
integration.

## Provenance and scope

Core: the supplied `K58_wall_cube_conquer` toolkit. Entrance builder and
root-reducer: reviewed `smwx2syxr/m4` and `m3` work. Engine guard: `m2`.
Ordinary leaf/frozen proof semantics: `m6`. Pinned sequential-counter
semantics were independently checked by `m7`, and its auxiliary/cardinality
report is available alongside the source. Saturation and Ramsey-family
kernel proofs: `m1`, independent Lean source plus compilation receipts.

The ordinary ledger and its completed verified cases are untouched. The wall
pilot did not close any leaf, so there is no new bound to upload. All large
CNFs and generated proofs stay in run directories or `.scratch/`, not in the
Git repository just by installing this module.
