# Wall toolkit integrated into `k58-solver`

The available **`K58_wall_cube_conquer`** toolkit is now integrated into the
self-contained package and exposed as **`./k58.sh wallcc`**. This is the
wall-cube toolkit bundled with the four-row solver. The separate
`K58_shared_learning_solver.zip` is not among the attached files; if that exact
archive is the intended other solver, it still has to be supplied. Nothing was
adopted from a missing archive or invented from its receipts.

Package and runtime version: **`2026-11-26-wallcc`**.
The ready archive is **`dist/k58-solver.zip`**, SHA-256
**`d5d34e99c17a08fdc7240dc2062d38d5bd72aad624703c3af185bd11a75fdb0e`**.
`dist/SHA256SUMS` is updated to the same hash. The archive is for handing over
through the conversation, not committing as repository history.

## What was added

- **Frozen-row worker:** `run`, `resume`, `verify`, `export-drat` on the pinned
  wall roster, with registered parent SHA-256. Uses pentagon derivations when
  available. `--row`, `--tier first|retry` and exact input/proof receipts are
  required by the workflow. A supplied CNF can also be used as an external input.
- **Simultaneous row discovery:** `wallcc rows --profile ... --limit ...`.
- **Per-leaf proof path:** fresh leaf CNF = parent + unit clauses of its cube.
  Each receipt is bound to the immutable plan and leaf artifact hash. A checked
  cover is replayed again before parent DRAT export. Incomplete covers and SAT
  branches cannot produce a parent UNSAT certificate.
- **Root reduction:** `rootreduce.py` + `check_trace.py`. This shrinks a formula
  by unit propagation with reconstruction/witness certificates, but has no
  speedup guarantee and should be used for smaller protocol/tool inputs rather
  than sold as faster CDCL in every case.
- **Optional entrance projection:** `entcap.py`. Applies only to
  `(16,16,13,12)` and only to the proven entrances: T/T at the 13-class and
  mixed T/U at the 12-class. `UU--` and partial families receive no cut. Use
  `--direct` for the actual theorem (outside-class count at most 14), never for
  arbitrary roots or as an unconditional new global cap.
- **Protocol helpers:** an ordinary per-leaf `leafcert.py` with cube
  exhaustiveness + two-sided proof checks, and a stricter engine adapter. The
  package’s `bin` contains the expected Kissat and DRAT binaries.
- **Self-tests:** `k58.sh wallcc-smoke` now runs both ordinary wall controls and
  the conservative per-leaf harness controls. A missing optional
  `smoke-results.json` is explicitly reported; direct `selftest.py --wall ...`
  still requires that original fixture.

No `run_cover.py` recipes were replaced and existing completed cover
certificates remain separate. No automatic full-cover launch was added and no
excluded `(15,14,14,14)` row was selected in these pilots. The 518 degree-cover
proof archives remain unavailable, so no conditional four-row degree closure is
silently promoted into a trusted cut family.

## What I actually tested on the unpacked final package

- `./k58.sh doctor`: python-sat 1.9.dev22, Kissat 4.0.4, bundled example replay 5/5.
- `./k58.sh smoke`: **SMOKE TEST PASSED** — three real cases closed, all replayed,
  corrupted/truncated certificate rejected, batch plan built.
- `./k58.sh wallcc-smoke`: K5/K6, split multiplicity, sharding and resume, missing
  sibling stays open, damaged proofs/models rejected, both parent DRAT exports;
  then the separate per-leaf harness **20/20 checks**, including an exhaustive
  all-closed leaf coverage replay.
- A real retry-tier row through `k58.sh wallcc run`, followed by `verify`. With a
  deliberately tiny cap for the final pipeline test, it reports **OPEN**, as
  expected, not an erroneous closed certificate or bogus proof.
- Entrance and control guards: all counter hypotheses, root/template mutation
  rejection, byte-identical reproduction, NULL/partial scope behaviour, and
  aux-variable range checks were tested.
- Kernel statement guard: m1's saturation/Ramsey-family discharges rebuilt with
  the three standard axioms only; m7 checked the full large cardinality-circuit
  layer, explicitly without pretending to prove its declared bounds.
- Root reduction: **1,058,750 to 649,327 clauses**, with an independently
  replayed reconstruction and all seven negative controls rejected. That is a
  verified preprocessing equivalence, not a new wall refutation.

## Actual wall attempt, not a proof of a new bound

### `d11c` — `(16,16,14,11)`

Full id:
`d11c492f44d336da0a00a697f8bebdb7cb1e752785432a49d680e229aff8e728`.
Parent SHA-256: `718149b11bf7ba27ac760804f8ced16f0362c52fa0cb0aa1e6de4c728f6e2761`.
The parent is a retry/input with **28,847 variables, 202,554 clauses and 315
local pentagon cuts**.

At depth 1 and 100,000 conflicts, both ±294 leaves reached the limit
(elapsed 6.918 and 6.878 s) and remained **OPEN**.

At depth 2 and 400,000 conflicts, all four branches remained **OPEN**:

| leaf | literal cube | conflicts | elapsed seconds |
| --- | --- | ---: | ---: |
| `r00` | `-294, -2846` | 400,007 | 34.288 |
| `r01` | `-294, +2846` | 400,000 | 31.525 |
| `r10` | `+294, -2846` | 400,000 | 31.679 |
| `r11` | `+294, +2846` | 400,000 | 31.799 |

No `CHECKED_SAT`, no `CHECKED_UNSAT` set for the whole cover, and no legitimate
parent DRAT export. A parent OPEN is precisely the current result, not an absence
proof. In relation both runs used 100,000 conflicts: here it is approximately
100,000 due to the engine's completion semantics, and those counts are recorded
from each actual receipt.

### `95c7` — `(16,16,13,12)`

Full id:
`95c7de5e1875afea2972703c547d5ea57407d6e4ccdbb378b1711da74622a12c`.
The recorded root kinds are `T/U`, so the optional cut is valid on its 12-class
points. Baseline SHA-256:
`04ba3caa5e458e73cd52374fbdf547e3be4a1f80f7ddf6f9ba074a8f58aad4d2`.
Baseline size: **28,903 variables, 202,662 clauses**.

Applying the optional entrance projection added **15,324 clauses** to 12 point
instances and allocated **7,560 fresh auxiliary variables**. The strengthened
formula has **36,463 variables, 217,986 clauses**, SHA-256
`523e1110d2fb8b38d97e7d2f37f0b169c10c83095ed924bac84eb599b73db3e7`.
Its parent body is unchanged. No `UU--` or restricted class was capped.

At depth 1 and 100,000 conflicts the baseline and strengthened inputs both had
both leaves OPEN:

| variant | negative child | positive child | note |
| --- | --- | --- | --- |
| baseline | 4.619 s | 4.267 s | split on 294 |
| strengthened | 4.434 s | 4.631 s | split on 27490 |

The splitter may choose a different auxiliary literal when augmentation changes
the parent, so these are **not per-cube performance measurements** and should
not be read as a speed win by subtraction. Neither refutation closed either leaf.

## Practical use

Start with a bounded targeted run, not the full cover:

```sh
unzip k58-solver.zip
cd k58-solver
./k58.sh setup
./k58.sh smoke
./k58.sh wallcc-smoke

./k58.sh wallcc rows --profile 16,16,13,12 --limit 5
./k58.sh wallcc run --row <unique-hex-prefix> --out runs/wallcc/trial \
  --tier retry --depth 1 --jobs 2 --conflicts 100000 \
  --seconds 120 --checker "$PWD/bin/drat-trim"
./k58.sh wallcc verify runs/wallcc/trial --jobs 2 \
  --checker "$PWD/bin/drat-trim"
```

Only with a full checked cover:

```sh
./k58.sh wallcc export-drat runs/wallcc/trial parent.drat \
  --method compact --checker "$PWD/bin/drat-trim"
```

To augment with the optional certified cut, build it using a parent with the
actual connected root/template pins, then pass the augmented file via `--cnf` to
the same frontend. It is explicitly not enabled silently across every row.

The wall pilot shows that this pipeline can be run and verified honestly. It has
**not** cracked the wall at the tested conflict budgets. The remaining next
lever is physical structural input or a more judicious branch/budget choice, not
a blanket degree cap, IDRUP promotion, or an unbounded solver sweep. The
platform calls “solved” on accepted reports does not mean the K58 target or the
wall has been solved.
