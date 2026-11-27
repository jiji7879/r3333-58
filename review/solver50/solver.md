# Direction A — solver, path, control and bounded-launch audit

## Verdict

At repository HEAD `d19284ac7a1698a3296197cf0c133c6d5c1331e6`, I independently regenerated and strictly replayed **all nine supplied three-second full-query UNSAT controls**. All nine pass `drat-trim -i` with no `-w`, against the exact original FIRST parent plus the stated physical cube and sorting/ownership clauses. A bad binary prefix and a valid-proof/wrong-query control both fail closed.

This establishes representative-level evidence only. It does **not** close any original row. All nine successes are already excluded by the supplied sorted-arm table, so they are useful controls but no additional label-level progress beyond that table. The three tested sorted controls not excluded by that table timed out, as did all six preferred and all six new-cover controls. There is therefore **no demonstrated three-second closure on the new 1,101,974-job cover**, and no basis for a whole-row or Ramsey-number claim.

I provide a fresh-process, eager-proof launcher with an inclusive three-second process-group cutoff and independent evidence validation. It was tested on shell timeout/process-tree controls and on a stored-proof validation fixture, **not launched on K58**. No SAT solver was run during this audit.

## Inputs and extraction

Only these member-local directories were written:

- `artifacts/K58_wall_50k/` — the supplied `K58_wall_50k_solver_and_proofs.zip`, built with its own `setup.sh`;
- `shared-artifacts/K58_shared_learning/` — the supplied `K58_shared_learning_solver(1).zip`, used read-only after hashing;
- the scripts, logs and reports named below.

Attachment SHA-256 values:

```text
310f391f61c2e298238abe12ded1e7a4b7380336329d6576bdfc87f586245e77  K58_wall_50k_handoff.md
897334cfcaceae03f13a0d242fb886c0633bc712d353a094373f7e5b5a539743  K58_wall_150000_representatives.tsv.gz
e8a9fe88fbc7b647d6dd37e5ec5c257cb13365fa4dfd18685a2e1a599c378496  K58_wall_50k_solver_and_proofs.zip
3019df96c5adf3d06569d3ba4d9fd3be7b25e43f8d17c883fe71dc83d97f7886  K58_shared_learning_solver(1).zip
```

`sha256sum -c SHA256SUMS` passed for the 50k package and `sha256sum -c SHA256-SOLVER` passed for every file listed by the shared package. The latter manifest omits the core/proof artifacts discussed below. `setup.sh` installed `python-sat==1.9.dev22`; `Cadical195` is the CaDiCaL 1.9.5 binding. The two packages have byte-identical `tools/drat-trim.c` (SHA-256 `d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee`). The newly compiled checker used here has SHA-256 `a9571deb08430a3d7f7a72074440f53e2ad48196dced50b146835052a18e9066`.

## Actual solver and timer configurations

### Supplied three-second full-representative controls

`artifacts/K58_wall_50k/timed50.py:53-77` is a **fresh, single-shot** PySAT `Cadical195(bootstrap_with=clauses, with_proof=True)` call on the already generated full representative CNF. It sets no CaDiCaL tuning option and no conflict cap. Its C++17 helper invokes the native `Solver::terminate` asynchronously after 3.0 seconds.

The timer starts at line 60, **after** `full_query`, DIMACS-to-PySAT conversion and solver initialization. Encoding and setup are separate receipt fields. Binary DRAT is flushed directly from `pysolvers`. The supplied checker command at line 71 is `drat-trim QUERY PROOF -i -w`; this audit deliberately does not use that acceptance command.

Across all 24 timed receipts:

| Receipt group | Tried | Stored UNSAT proof | OPEN |
| --- | ---: | ---: | ---: |
| `timed` (six sorted proofs + six preferred) | 12 | 6 | 6 |
| `timed-sorted` | 6 | 3 | 3 |
| `timed-new` | 6 | 0 | 6 |
| **Total** | **24** | **9** | **15** |

All 15 OPEN receipts reached at least 3.0 search seconds. Maximum `search_s` was 3.015395140999317, a 15.395 ms overshoot. OPEN encoding added 0.047640975–1.430495463 seconds and solver setup another 0.085829734–0.250453125 seconds. Thus the handoff's “3 s” is a search-only limit, not a hard per-process total. Mechanical details and per-receipt values are in `control-accounting.json`; reproduction is `python3 control_accounting.py`.

### General shared-learning package

There are two distinct entry points:

1. `wallcc.py` uses a fresh `cadical_leaf.py` subprocess per pass. Defaults are depth 3, two workers, 60 seconds and 100,000 conflicts per SAT pass, and deferred proof mode. Deferred mode can spend one budget searching and a **second separate budget** reproducing UNSAT with tracing (`campaign.py:193-220`). The wall limit includes worker start/load, but it is per pass, not necessarily per leaf attempt.
2. `shared_conquer.py` uses one `Cadical195(with_proof=True)` state over a fixed `working.cnf`, visiting cubes by assumptions. Defaults are 350,000 conflicts per cube, 1,000 for the final unconditional call, and 300 seconds for the **entire SAT worker**, not per cube (`shared_conquer.py:38-65,122-148`). It flushes the native proof stream after every call and finally requires an empty-assumption UNSAT before constructing a root claim.

Its original `check` wrapper injects `-w` (`shared_conquer.py:67-69`), including physical-core and parent replay. Do not use that wrapper as the final acceptance path. The ordinary `campaign.check_trace` uses `-i -t` without `-w`, but cached `CHECKED_UNSAT`/`CHECKED_SAT` hits only rebind plan/cube and rehash the artifact (`campaign.py:172-200`); run/resume output is not a fresh proof replay. `wallcc verify` or an independent exact-target replay remains necessary.

## Original parent, row IDs and exact representative semantics

The shared package's `data/wall.jsonl.gz` and the new package's `inputs/wall.jsonl.gz` are byte-identical, SHA-256 `8d91ebc7d9fe6623bb04f6a0846953827a90265453c9dbcd51e3d1acf0c8bafd`. Their decompressed records are identical for all **11,585** IDs. `wallcc.py rows` reports 381 + 7,732 + 88 + 1,046 + 2,058 + 140 + 140 = 11,585 rows in the seven profiles (`roster-profiles.tsv`). Full 64-digit IDs are used for lookup; a prefix is accepted only if unique.

For origin `wall`/`case`, `campaign.inspect` requires the stored parent to equal `row_formula(row, tier)` regenerated from the frozen encoder (`campaign.py:99-124`). For `--cnf`, the supplied canonical DIMACS itself is the exact obligation; there is no implicit original-row regeneration. My launcher therefore passes the unmodified `representatives.py export` output directly to the worker and binds its SHA-256 in both launch and verdict receipts.

The query conventions are not interchangeable:

- `sorted`: original FIRST parent + mapped full-arm sorting clauses + ten physical spoke units;
- `preferred`/`round50`: original FIRST parent + occurrence/ownership guard clauses + ten physical units + ownership literals (a positive previous gate when needed and the negative current gate);
- joining-edge children additionally need their exact verified physical edge units.

Dropping the guard, treating an assumption hash as a formula hash, or replaying against the bare parent changes the obligation. The nine control replays below all matched parent, query, cube and proof hashes. Independently, the general shared encoder regenerated every one of their nine FIRST parents byte-for-byte (`shared-parent-check.json`).

## Full-chain strict replay: method and results

Run from this member directory:

```sh
artifacts/K58_wall_50k/.venv/bin/python replay_controls.py | tee replay-run.log
python3 control_accounting.py > control-accounting-run.log
```

`replay_controls.py` constructs no solver. For every stored UNSAT receipt it:

1. calls the original `full_query(row, w, z, scope)` and checks `parent_sha`, `query_sha`, the exact cube and ten physical literals;
2. checks the binary proof's decompressed SHA-256 and byte length;
3. writes the regenerated CNF/proof under `replay/`;
4. requires return code zero and an exact `s VERIFIED` line from `drat-trim CNF PROOF -i`, with no `-w`/`-W`, and rejects `s NOT VERIFIED`.

All nine checks passed:

| Full row ID | Words | Control selection | Exact query SHA-256 |
| --- | --- | --- | --- |
| `780e9154eef19eca715e973fdbff8db63754056bb31a2208e9d71e15ec3391cc` | `00220/02101` | prior-sorted-128-open | `df48e21a02f5058af3607b45ce0a3fbba106933eec901ca521ea4355c5652676` |
| `0846a190f9be96f1ce9830219fbe4f2437be4aeb5e785d009dea1b8ffe3f7e66` | `00101/02201` | prior-sorted-128-open | `e6a279e93a8699138e5e73b67749373ce9b0d84c03b1e83ebe61d4be9ecd6328` |
| `09c39c0fe78964677625d74cb48e5de05ed4a0be954bc6877212b4949b03a1a9` | `00101/01021` | prior-sorted-128-open | `656eb4a7c556489a811a987e87a55d8d91187fcf61e250c43691b7b8823b81f7` |
| `ae7554f6482e75bd1036241b4477ffc1ef529e50bdc7475ca2abe9d57dd0f401` | `00210/01200` | prior-sorted-128-open | `1c37919f181002338e7c7a2e41991873ec9db88ff98915efbce094c924a958b6` |
| `79bcd36d02ae3b84368cd585e8101e01c895871e3856e435b8dfe9ed3d2ee9c7` | `01012/02101` | prior-sorted-128-closed | `26316d253ef1d067519186e39c980bcf0bc30dab71d16c055e0eef8337a68d2f` |
| `9debc8a5f8a17f73f71ffdd779b9ea250bc2c416d616c9f9685186fc14d5b570` | `00012/02000` | prior-sorted-128-closed | `51a9e9a8e01974a5f1caeef6a2a9e1cf826fd734b3b1d81cef66fca25267c9e1` |
| `90085700bed34f6c9c51f5a733ef26e3cc3a2d529afbddc92e0d8610b971c53e` | `00022/01200` | fresh-sorted-128-open | `62508b8b14eb7dba0b78d00c17e7bc2f728854da3b6314422e69b848f709556a` |
| `b8854af690d6b7024fe2a2bbaf1d0aabcc601aeec4ff8cfc945807bd0ac82b08` | `01001/02201` | fresh-sorted-128-open | `ab2578b4e79755dc361c139b5d4420a3fe205e7b2d5cbb76ceef9dda09ac6b3b` |
| `83be510af81bbabe07cdc45f1ff4840dcfb98cc967c30007f6800a52b99e32fb` | `00121/01200` | fresh-sorted-128-open | `9575d37ee9f0350d683ffd2f9d12e8f32b7df22d7072369a2e3e0a859881f06d` |

The three fresh controls' supplied search times were 0.077701461, 0.012800687 and 0.051260806 seconds respectively. These are the strongest measured full-formula architecture in this small, biased control set, not evidence of a general solver preference or expected closure rate.

Every one of the nine `(arm,w,z)` triples is `REFUTATION_CANDIDATE`, not SAT, in `results/sorted-outcomes.tsv.gz`; `control-accounting.json` records this cross-check. The other three sorted timed controls were not locally excluded and remained OPEN. Hence none of the nine proof replays advances beyond the exact local arm table.

Two negative controls also behaved correctly:

- changing the first binary tag of `timed-0.drat` to `X` gives return code 1, `WARNING: wrong binary prefix`, `ERROR: no conflict`, `s NOT VERIFIED` (`replay/negative-bad-prefix.strict.log`);
- checking that valid `timed-0` proof against the distinct `timed-1` CNF gives return code 1, `conflict claimed, but not detected`, `s NOT VERIFIED` (`replay/negative-wrong-query.strict.log`).

The complete bindings, commands, return codes, log hashes and artifacts are in `replay/summary.json`.

## What the 12,835 bulk cells do—and do not—prove

`results/round50-cheap-sorted.tsv.gz` contains 37,165 OPEN and 12,835 `UNSAT_SORTED_ARM` cells. In `cheap.py:64-73`, `certify(..., ordered=True)` returns `UNSAT_SORTED_ARM` from the local sorted-arm certificate **before** constructing `full_query` or a full parent. This is not a full-representative DRAT receipt and must not be relabeled as one.

Similarly, the incremental 128-conflict block probes reuse a solver only inside a fresh group/block. Their group formula and assumptions must not be confused with a byte-for-byte original parent. OPEN/conflict counters are observations, not closure evidence. The nine independently replayed DRAT artifacts above are the only full-representative closures accepted by this direction.

## Shared-learning transport and cache boundaries

### Within one shared run

`shared_conquer.search` loads one immutable `working.cnf`. After UNSAT under cube assumptions it checks that the returned assumption core is a subset of that cube, adds its negation to the solver and appends the clause to the proof stream. This may settle a sibling, but it is not portable evidence for a different parent, guard or working formula. The only sound root ending is the final empty-assumption UNSAT followed by a strict replay against the exact parent, including the CAS prefix where applicable. A per-cube UNSAT, a capped final call or a leaf label alone remains OPEN.

For a direct exported representative with CAS off, no additional CAS derivation is needed: all sorting/ownership clauses are already in the exact exported query, and the final proof is checked directly against that query.

### Old physical-core registry

The supplied shared ZIP/install contains nine `cases/*` directories but **zero** `core.cnf` and **zero** `trim.drat` files. `shared_conquer.reused` skips each case at lines 86-89. Despite `README.md` describing these artifacts, they are absent and unlisted in `SHA256-SOLVER`; verification of the old eight cases cannot be reproduced from this solver ZIP alone.

`matches.json` has eight `(15,15,15,12)` targets and none is in the current 11,585-row roster. Those labels cannot prove current jobs. Also note that the code's direct pin-containment path does not require a `matches.json` entry; if real core/proof artifacts were restored, every match would still require signed-core validation, transport (when claimed), and fresh strict target replay. Eight labeled `examples` files or verdicts are not substitutes for those missing bytes. External `--cnf` plans skip this registry altogether (`shared_conquer.py:72-74`).

### Cache freshness

The general run key binds plan/node/cube and artifact hash, but run/resume does not replay cached terminal artifacts. OPEN at an identical budget is skipped; `--again` repeats it, and larger budgets probe again. Use a separate output directory for any formula, guard, split, proof-mode, worker or solver change. The new `cheap.py` block cache likewise must not be shared across those changes; its output-name discipline is necessary, not an optional optimization. The supplied old runs are different cohorts, formulas and timers and provide no reusable closure for the new jobs.

My launcher refuses every pre-existing attempt directory and imports no receipt, cache, physical core or learned state. This deliberately trades away unverified cross-job reuse for exact query identity.

## Exact safe per-process three-second coordinator recipe

Files:

- `bounded_exec.py` — starts a fresh process group, starts timing before `Popen`, kills the entire group with SIGKILL at the deadline, stores actual argv, query hash, return code, elapsed time and stdout/stderr hashes;
- `certify_attempt.py` — accepts only the exact eager `cadical_leaf.py QUERY ATTEMPT 100000 trace` shape; independently checks UNSAT with strict `-i`, or SAT with a total model over every declared variable and every query clause;
- original unmodified worker `shared-artifacts/K58_shared_learning/cadical_leaf.py` (SHA-256 `5c4ef6727936fc30bd1b60074fd77ca110569a8117f163fdbc95168069645ff9`).

Use one worker at a time and a small finite control set. Run these commands from `.ultramath/smwydhgx1/m4/` (or set `M` to its absolute path). For example, this repeats the existing `b885…` **positive-control job**, not a new search. Choose a new job directory:

```sh
M=$PWD
N=$M/artifacts/K58_wall_50k
S=$M/shared-artifacts/K58_shared_learning
JOB=$M/.scratch/b885-launch-control       # must not already exist
mkdir "$JOB"

# Original exporter: FIRST parent + exact sorting clauses + physical cube.
(cd "$N" && .venv/bin/python representatives.py export \
  --row b8854af690d6b7024fe2a2bbaf1d0aabcc601aeec4ff8cfc945807bd0ac82b08 \
  --words 01001 02201 --convention sorted \
  --out "$JOB/representative.cnf") | tee "$JOB/export.log"
printf '%s  %s\n' \
  ab2578b4e79755dc361c139b5d4420a3fe205e7b2d5cbb76ceef9dda09ac6b3b \
  "$JOB/representative.cnf" | sha256sum -c -

# Inclusive Python import + DIMACS load + initialization + search + proof flush.
python3 bounded_exec.py --seconds 3 --directory "$JOB/attempt" \
  --query "$JOB/representative.cnf" -- \
  "$N/.venv/bin/python" "$S/cadical_leaf.py" \
  "$JOB/representative.cnf" '{directory}' 100000 trace

# Run only when bounded_exec returns 0. Its 124 means TIMEOUT/OPEN.
python3 certify_attempt.py --query "$JOB/representative.cnf" \
  --attempt "$JOB/attempt" --check-seconds 30
```

Return/status contract:

- `bounded_exec = 124`: `TIMEOUT`; skip certification and retain OPEN. Late/partial proof files are never accepted.
- `certify_attempt = 0` with `VERIFIED_REPRESENTATIVE_UNSAT`: closure of the exact exported representative only, witnessed by strict proof replay.
- `VERIFIED_REPRESENTATIVE_SAT`: a checked model of that representative, not an UNSAT closure.
- `certify_attempt = 2`: OPEN (conflict cap or checker timeout); no closure.
- nonzero other status / `PROOF_REJECTED` / launch `ERROR`: no closure; inspect artifacts.

Eager tracing avoids the hidden second deferred solve. The 100,000-conflict backstop matches the general worker's ordinary finite cap; actual conflicts are retained, including any small CaDiCaL overshoot. The three-second limit is stronger and different from the supplied search-only timer, so resulting timings must not be compared as if they were the same budget. Formula export occurs before the solver process and is logged separately. Proof checking has its own separately reported 30-second budget; neither checking NOR formula export is silently counted as search time.

Launcher checks actually executed here:

```text
normal shell command: LAUNCH_COMPLETED, rc=0
3 s shell + spawned sleep: coordinator rc=124, TIMEOUT, worker rc=-9,
  elapsed_s=3.003913992084563, spawned child confirmed dead
certifier on TIMEOUT: refused, no verdict.json
stored-proof validator fixture: exact-query strict replay passed, no solver invoked
```

See `launcher-tests/summary.json`, its launch receipts and `commands.txt`. This validates control plumbing, not K58 runtime or a new closure rate. A coordinator should first use a handful of the nine known control jobs, then only explicitly selected still-OPEN representatives. It must not extrapolate these selected controls to the new cover or any row.

## Files and checks to hand over

- `SOLVER_AUDIT.md` — this report;
- `replay_controls.py`, `replay-run.log`, `replay/summary.json`, `replay/*.strict.log` — full-chain replay and negative controls;
- `control_accounting.py`, `control-accounting.json`, `control-accounting-run.log` — timer/status/local-table accounting;
- `shared-parent-check.json`, `roster-profiles.tsv` — encoder/all-row binding;
- `bounded_exec.py`, `certify_attempt.py`, `launcher-tests/` — bounded launcher and executed non-SAT controls;
- `launcher-sha256.txt` — final launcher/worker and shared-input hashes.

Not done: no K58 search, no new representative closure, no whole-row composition, no audit of the 1,101,974-job cover or 304/35 mathematical certificates, and no runtime benchmark of the new launcher on K58. Old core verification was impossible from the shared solver ZIP because its proof/core bytes are absent. All 11,585 original rows remain OPEN in this audit.
