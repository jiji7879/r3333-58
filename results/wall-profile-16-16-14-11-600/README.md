# `(16,16,14,11)` pilots and the shared-learning handoff

## Scope

The verified current wall roster has **140** rows in this profile, not 88. Ten
minutes per row would be about 23.3 CPU-hours (at least 11.7 wall-hours on two
cores), before proof replay.

Two preliminary whole-row trials were run concurrently. They used the ordinary
frozen first-tier CNFs, `tables=True,total_critical=True,full_root=False`, no
perfect-degree balancing, no new CAS cuts, no conflict cap, and no unverified
H-rise clauses. Neither closed its row or produced a model.

| full row ID | engine | parent SHA-256 | conflicts | measured wall s | user CPU s | verdict |
| --- | --- | ---: | ---: | ---: | --- |
| `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06` | Kissat 4.0.4 | `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae` | 10,349,282 | 600.0534 | 599.162 | OPEN |
| `33307b6cfda2211ecc745d5651b0cdf4d5ecdbf40202e6637f58fa48022e8ffd` | CaDiCaL 2.1.2 | `1e484fef1e21268cc04fc826e30cadc7fa7d627a12070185a5d4cbdc59524eca` | 5,231,078 | 600.0361 | 598.633 | OPEN |

Both processes retained separate raw inputs/logs; unfinished DRAT was deleted.
A mistaken one-second foreground launcher produced no result and is not counted.
The successful runs used the solver's own 600-second timers under a
single 720-second concurrent supervisor.

## Requested shared-learning row: `06861a3df60c…`

`<ROW_ID>` was a placeholder in the attached instructions. The first of the two
profile pilot rows was selected explicitly:

```text
06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06
profile (16,16,14,11), branch 38, tier first
parent 90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae
19,533 variables / 184,335 clauses
```

The supplied general archive has SHA-256
`3019df96c5adf3d06569d3ba4d9fd3be7b25e43f8d17c883fe71dc83d97f7886`.
Its CRC and all `SHA256-SOLVER` entries passed. Its offline wheels supplied
`python-sat==1.9.dev22` in a scratch virtual environment. The driver was run
with `--no-reuse`: no companion proof archive or foreign certified core was
used. The attached H-rise bounds were **not** imported; no new contact bound is
claimed, so there are no derived physical high/low site labels to report.

### First-tier depth-two plan

```sh
wallcc.py prepare --row "$ROW" --tier first --out "$PLAN" \
  --depth 2 --arm-pair auto --arm-mode both
```

The plan has four cubes, 315 CAS cuts, 15 tables, and `arm_units=[]`.
These are derived CAS clauses, not 315 arm failed-literal units. The split
literals are `1413`, `2206` and `1426`. Its working-formula SHA-256 is
`39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38`.
The compact exact plan is `06861-plan.json`.

### Shared search

```sh
shared_conquer.py "$PLAN" "$ANSWER" --no-reuse \
  --conflicts 350000 --tail-conflicts 1000 --seconds 300 --check-seconds 600
```

The successful shared search took about 99.5 wall seconds and ended OPEN at
its conflict limits (not because it consumed its entire 300-second limit):

| cube | output | conflicts | verdict |
| --- | --- | ---: | --- |
| `r00` | `(-1413,-2206)` | 350,000 | OPEN |
| `r01` | `(-1413,+2206)` | 350,001 | OPEN |
| `r10` | `(+1413,-1426)` | 350,001 | OPEN |
| `r11` | `(+1413,+1426)` | 350,002 | OPEN |
| tail | no cube assumptions | 1,003 | OPEN |

The shared receipt is `06861-shared-350k-no-reuse.json`. A first 25-second tool
launch was aborted before a receipt was written; its 52.9 MB unfinished shared
trace was removed and never used in or continued by this run.

### Resumable leaf workers and verification

```sh
wallcc.py resume "$PLAN" --jobs 4 --proof eager \
  --seconds 300 --conflicts 1000000 --check-seconds 600
wallcc.py verify "$PLAN" --jobs 4 --check-seconds 600
```

Four ordinary leaf proofs were attempted concurrently. All reached essentially
one million conflicts rather than deriving UNSAT:

| cube | conflicts | elapsed wall s | status |
| --- | ---: | ---: | --- |
| `r00` | 1,000,000 | 68.584 | OPEN |
| `r01` | 1,000,000 | 69.521 | OPEN |
| `r10` | 1,000,003 | 67.200 | OPEN |
| `r11` | 1,000,000 | 67.324 | OPEN |

The verifier reconstructed the parent and full split tree and returned
`counts: {OPEN: 4}`, `leaves: 4`, exit code 2. There are **zero checked UNSAT
leaves** and no complete cover. OPEN receipts and their plan/hash bindings are
preserved under `06861-leaf-*.json`. A significantly different leaf budget is a
fresh leaf experiment, not a continuation/proof of the previous OPEN state.
No parent DRAT was exported, and no whole-row or profile closure follows.

## Reproduction boundaries

Raw `parent.cnf`, `working.cnf`, `cas.drat`, full leaf attempts, virtual
environment, and any completed future proof remain under:

```text
.scratch/shared-learning-pilot/K58_shared_learning/runs/
  06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06/
```

The original frozen-row CNFs used by the two preliminary runs are under
`.scratch/wall-profile-16-16-14-11-600/`.
This compact results directory contains the copied exact plan, receipts and
logs, not the raw large solver formulas or unfinished proof artifacts.
