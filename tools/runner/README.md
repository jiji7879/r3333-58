# K58 cover — local runner

Runs the frozen 113,179-case cover on your own machine, with the pinned
toolchain, resumable shards, and a release manifest that a reviewer can replay.

You need the handoff bundle (`R3333_K58_LLM_handoff.zip`) unpacked somewhere;
everything here calls into it. `bin/` carries Linux x86-64 builds of the pinned
solvers; on another platform `./build_tools.sh` rebuilds them from source at the
pinned commits.

## 1. Check the machine

```sh
./build_tools.sh                       # clones + builds kissat 4.0.4 and drat-trim
./doctor.sh /path/to/K58               # versions, disk, and a 5-case replay of the bundled example
```

`doctor.sh` must print `bundled example ok: {"replayed": 5}`. It also checks the
python-sat version — the verifier pins **1.9.dev22** and refuses anything else,
because it regenerates every CNF through `pysat.card.CardEnc`.

## 2. Run a shard

```sh
./run_shard.sh --bundle /path/to/K58 --out evidence \
               --profile 16,15,15,11 --shards 4 --shard 0 --workers 4
```

* `--profile` limits to one degree profile; omit it to run everything.
* `--shards`/`--shard` split by case hash, so several machines can run
  disjoint shards against the same recipe.
* Rerun the **identical** command to resume: verified cases are skipped, and
  OPEN receipts are reused.
* Budget, measured here: 1.03 MB of certificate per closed case at the 12 s
  tier, 7.4 MB at the retry tier, ~7.8 CPU-s per closure including checking.
  The two large profiles project to ~206 CPU-hours and ~194 GB; the seven small
  profiles closed 0 of 98 at the first-pass budget, so give them the retry tier
  (`--tier retry`) or expect nothing.

## 3. Finalise

```sh
./finalise.sh --bundle /path/to/K58 --out evidence --release release-1
```

Builds the manifest and replays **every** certificate against its regenerated
CNF. Quote the manifest hash together with the `"replayed": N` line — the hash
alone certifies nothing, because `manifest` performs no checking.

## 3b. Pin the encoding (before any release)

```sh
python3 pin_manifest.py make   --bundle /path/to/K58 --out encodings-v1.json
python3 pin_manifest.py verify --bundle /path/to/K58 --manifest encodings-v1.json
```

Records case id, recipe, encoder revision and expected CNF hash for every case.
`verify` regenerates each CNF from the manifest's own recipe, so a recipe the
generator does not reproduce fails here. The encoder revision is a hash of the
generator sources, so a changed encoder invalidates old manifests.

## 4. Optional: Lean-consumable certificates

```sh
python3 lean_certify.py --bundle /path/to/K58 --ids ids.txt --out certs --work work
```

For each case: regenerate the CNF, solve, convert DRAT → LRAT with
`drat-trim -L`, compress, and delete the CNF, the DRAT and the raw LRAT. What
remains is what an LRAT checker (in principle the Lean kernel) can consume.

Binary LRAT by default (`drat-trim -L -C`), the format `cake_lpr` consumes.
Measured: **15.2 MB per case** compressed, 8.4 % below text LRAT and still 4-5x
the DRAT certificate. The full cover would be ~1.7 TB, so export per case on
demand; the decision is to retain DRAT and not build a second permanent archive.
Add `--lpr-check /path/to/cake_lpr` to replay each certificate with a verified
checker as it is produced, and `--resume` to skip cases already recorded.

## 5. Optional: the 1,743 historical closures

```sh
python3 import_historical.py check --bundle /path/to/K58
python3 import_historical.py run --bundle /path/to/K58 --store /path/to/r58_evidence_store \
        --out evidence --checker bin/drat-trim
```

`check` needs only the bundle, or a ZIP of reconstructed parts passed as
`--index` (the ZIP must contain an `index.jsonl` with `path` and `sha256` per
line). It confirms that a proof is archived for every certified row
(1,743 of 1,743). `run` restores each proof from the `.tar.zst`
store and imports it. Apply `cover_evidence_full_root.patch` to the bundle's
`cover_evidence.py` first — otherwise `import-legacy` dies on the 569 campaign
rows that predate the `full_root` flag.

## Warnings

* A timeout is not evidence. Only a DRAT replay against the exact regenerated
  CNF counts, which is what `finalise.sh` does.
* Do not lower `python-sat` or swap the solver if you want comparable numbers:
  the proof bytes and the CNF bytes both depend on the pins.
* Keep `--publication`: without it the runner keeps loose CNFs and raw proofs
  and checks nothing on the way out.
