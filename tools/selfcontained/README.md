# K58 cover — self-contained runner

Everything needed to run the frozen 113,179-case cover of the `R(3,3,3,3) ≤ 58`
reduction on your own machine: the bundle, the pinned solvers, and the Python
environment (with offline wheels as a fallback).

## Requirements

Linux or macOS, x86-64 for the bundled binaries, Python 3.10–3.13, and a few GB
of free disk to start (see *Disk* below). On Apple Silicon or ARM, `bin/` will
not run — rebuild with `bash build_tools.sh` (needs git, a C compiler, `make`).

## Run it

```sh
unzip k58-solver.zip
cd k58-solver

./k58.sh setup      # creates .venv, installs python-sat 1.9.dev22
./k58.sh smoke      # end-to-end self test, ~1-2 min; must end "SMOKE TEST PASSED"
./k58.sh doctor     # checks versions and replays the 5 bundled certificates
./k58.sh test       # closes 5 real cases and verifies them (~2 min)
```

`doctor` must end with `example ok ... "replayed": 5`. `test` must end with a
line containing `"replayed": 5`. If both do, the machine is good.

Then the actual work:

```sh
./k58.sh run --profile 16,15,15,11 --shards 4 --shard 0
```

Rerun that identical command to resume — verified cases are skipped and OPEN
attempts are reused. Put shard 1, 2, 3 on other machines or run them in sequence.
When a shard finishes:

```sh
./k58.sh finalise --release release-s0
```

It writes the manifest, replays **every** certificate against its regenerated
CNF, and prints the `"replayed": N` line to quote alongside the manifest hash.

```sh
./k58.sh status     # how many closed, how much disk used, disk free
```

## What the smoke test checks

`./k58.sh smoke` runs five checks and fails loudly if any is wrong:

1. the toolchain is pinned and the five bundled certificates replay;
2. three real cases close end to end;
3. the manifest builds and every certificate replays in parallel;
4. a deliberately truncated certificate is **rejected** — a build that accepts
   it is not trustworthy, so this is the check that matters;
5. the batch driver builds its plan.

`./k58.sh smoke --keep` leaves the worked example in `smoke/` to inspect.

## What to run, in order

1. `--profile 16,15,15,11` — 16,090 open cases, ~13,000 close at the first-pass
   budget. This is the reliable work.
2. `--profile 15,15,15,12` — 83,360 open cases, roughly 70–85% close at the
   first-pass budget. Long but productive.
3. The seven small profiles — **skip them at the first-pass budget.** They
   closed 0 of 98 on my machine and 0 of 306 in the author's pilot. Use
   `--tier retry` if you want to measure them, and expect little:
   `./k58.sh run --profile 15,15,14,13 --tier retry --limit 40`

## Disk

Measured per closed case (gzip): **1.03 MB** at the first-pass budget, **7.4 MB**
at the retry budget. For the whole remaining cover plan on **150–350 GB**,
depending on how many cases need a retry. The seven small profiles add ~85 GB
if they close at all.

If that is too much: `./k58.sh finalise` after each shard and then delete
`evidence/<xx>/` directories you have already released — the certificates are
bit-reproducible, so they can be regenerated exactly.

## Options

```
./k58.sh run [--profile p,q,r,s] [--shards N --shard i] [--workers W]
             [--tier first|retry] [--limit N] [--seconds S] [--conflicts C]
             [--check-seconds N] [--out DIR]
```

Defaults: 4 workers, tier `first`, 12 s / 400,000 conflicts, evidence in
`./evidence`. One worker per core is right; more workers does not go faster.

`--check-seconds` (default 300, or the `K58_CHECK_SECONDS` environment
variable) is the certificate-checker cap. Every drat-trim call gets `-t N`,
because drat-trim's own default is 40,000 seconds: before this cap existed, one
hard certificate kept a worker busy for nine hours and looked exactly like a
stalled run. A certificate that does not check inside the cap writes
`CHECK_FAILED.json` in its case directory, keeps its formula and proof sizes in
that record, and leaves the case **OPEN** — the shard carries on instead of
dying on the exception.

## Is my run alive?

```sh
./k58.sh watch            # or: ./k58.sh watch path/to/evidence
```

Prints the per-case counters (attempt receipts, verified cases, checker
failures), the free disk, every running `kissat` and `drat-trim` with its
elapsed seconds, and how many files have been written in the last ten minutes.
A `drat-trim` older than the cap means that worker was started before the cap
existed; a `kissat` older than fifteen minutes means one hard instance, not a
stalled run; nothing written and nothing running means the run is stopped.

## Other commands

```sh
./k58.sh pin        # versioned encoding manifest: case id, recipe, encoder
                    # revision, expected CNF hash — the checker regenerates the
                    # CNF from this rather than trusting the certificate
python3 tools/lean_certify.py --help    # binary LRAT per case for cake_lpr
python3 tools/import_historical.py --help  # import the 1,743 historical proofs
```

`tools/cover_evidence_full_root.patch` fixes a `KeyError: 'full_root'` in the
bundle's `import-legacy` (569 of 752 campaign rows). Apply it before importing
historical proofs:

```sh
patch -p0 -d k58 < tools/cover_evidence_full_root.patch
```

## Warnings

* A timeout is not evidence. Only the replay in `finalise` counts.
* Do not change the python-sat version or the solver: the CNF bytes and the
  proof bytes both depend on the pins, and the verifier refuses other versions.
* Never edit `verified.json` or a certificate. If one is wrong, delete the case
  directory and rerun it.
* A run can look stalled while one worker sits inside drat-trim on a large
  certificate, and one shard prints progress only every hundred cases. Before
  concluding anything, `./k58.sh watch`: it shows each solver and checker
  process with its elapsed seconds, plus how many files were written in the
  last ten minutes.

## Unattended: run the rest of the cover

`./k58-batch.sh` drives the remaining work in order and survives interruption —
rerun it and it picks up where it stopped.

```sh
./k58-batch.sh plan                       # list the jobs, no work
./k58-batch.sh run    --shards 4          # first pass, both large profiles
./k58-batch.sh retry  --shards 4          # retry tier over whatever stayed OPEN
./k58-batch.sh finish                     # manifest, replay, RUN_SUMMARY.md
# or all three in sequence:
./k58-batch.sh all --shards 4
```

Options: `--workers W` (default 4), `--min-free-gb G` (default 20; the batch
stops cleanly when the disk drops below it), `--include-small` (adds the seven
small profiles), `--limit N` (testing), `--dry-run`.

The retry pass needs no case list: the runner retries exactly the cases whose
first attempt is recorded OPEN and skips everything already verified, so it is
safe to run repeatedly.

Progress lands in `batch-state/batch.log`; the final summary in `RUN_SUMMARY.md`.
Upload `release/manifest.json`, `release/cases.jsonl.gz` and the summary; the
certificates in `evidence/` stay on disk.

## Selecting rows by ledger status (added 2026-11-25, version 2026-11-25)

`./k58.sh run` takes `--status`, a comma list of the frozen ledger's statuses, and
defaults to `OPEN`. That is how the rows which carry only historical evidence get a
direct certificate instead of an imported one:

    ./k58.sh run --status CERTIFIED,PROFILE_EXCLUSION,TEMPLATE_EXCLUSION \
                 --seconds 900 --conflicts 20000000 --workers 12

selects 2,144 rows - 1,743 whose certificates live in an archive that is not here, and
401 that rest on profile/template exclusion arguments. Everything else is unchanged:
`--publication` keeps compressed certificates, the runner skips any case that already has
a `verified.json`, and `./k58-batch.sh finish` then rebuilds the manifest over the whole
evidence directory. `k58-batch.sh finish` also reads `release/manifest.json` where
`finalise` writes it now, so the summary no longer dies after a finished replay.

`dist/k58-solver.zip` of this build is
`36d8830af6b62e4ff5dc42ef9796a615a69b4d132d7cb4e071b691da2a790991`, version `2026-11-25b`
(the earlier `2026-11-25` build was `b5ddba18…`).

Version `2026-11-25b` adds `--retry-seconds`, `--retry-conflicts` and `--case-ids-file` to
`./k58.sh run`. The first two matter because the retry tier applies the `full_root`
strengthening and used to be stuck at 70 s / 2.4M conflicts, which is the budget the
remaining tail has already survived. Checked end to end here: a first attempt at 5 s came
back OPEN, the retry at `--retry-seconds 20 --retry-conflicts 200000` wrote
`retry/20s-200000/T---_0_0.jsonl` with `status OPEN, full_root True, seconds 20`, and
`--case-ids-file` selected the same row from a one-line file. The retry tier also reports
`NO_OPEN_FIRST_ATTEMPT` for rows it is told to retry that have no first receipt, so a
profile-wide retry sweep is safe on a fresh evidence directory.

Checked on a clean unpack before handing it over: `doctor` clean (python-sat 1.9.dev22,
Kissat 4.0.4, drat-trim, example replay 5/5), `smoke` 5/5 in 1m13s, and one real legacy row
through the new selector - case `d603199fef0f` of `(16,15,15,11)`, `VERIFIED`, 0.689 s
solver CPU, 0.793 s replay CPU, 163 KB certificate, receipt
`first/TTT-_1_232.jsonl`. That replay time is a third of the ~2.2 CPU-s per case measured
on the 95-case evidence, so the 10-14 h finalise estimate for a 100k-case evidence
directory stays on the conservative side.
