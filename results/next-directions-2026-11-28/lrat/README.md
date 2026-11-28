# LRAT pipeline reproduction (validated)

The coordinator ran:
`cd tools/lrat_pipeline && python3 run_pipeline.py`
with `LRAT_TRIM` pointing at the reviewed lrat-trim build (0.2.1-rc3).
All four already closed cases passed. See `receipt.json` for the submitted run,
`rehearsal-receipt.json` for the replay from `tools/lrat_pipeline/`, and
`coordinator-receipt.json` for the integrated replay at the earlier rehearsal,
and `report.md` for the detailed comparison and its limits. The latest fresh
coordinator replay is `coordinator-fresh-receipt.json`, with
`coordinator-fresh.log`; all four input, fresh-proof, trimmed-proof and search
counter identities again matched. Its CPU figures are a separate run. The
committed helper now pins all four inputs and all four fresh proof hashes.

This is an **opt-in experiment**, not a global solver option and not a proof that
lrat should replace every DRAT flow. H8/H7's plain native-LRAT trim pipeline is
faster and smaller byte-for-byte than incumbent DRAT replay, but including the
additional Python checker gives back most of that saving, slightly more on H8.
`lrat-trim` backward and forward replay and an independent Python RUP-only
checker all accepted the exact proofs. **Neither implementation is a formally
verified checker.** That is the truth boundary.

Native LRAT avoids fragile DRAT-to-LRAT **trimming**: untrimmed elaborated proofs
verify, but their trimmed variants needed `--relax` because deleted clauses can
disappear from those eliminations. The report never counts that relaxed check as
strict success. On two small heterogeneous examples, the dropped input-clause
ID list dominates trimming: LRAT can be larger than DRAT, not uniformly smaller.

## Tools actually used

- The repository's CaDiCaL 2.1.2, pinned by its existing SHA-256.
- The repository's existing drat-trim for the incumbent route.
- `lrat-trim` 0.2.1-rc3 from source commit
  `423194927df747528d5b7364806b5b77b2660c12`, source tar hash
  `e71af67672133ed0c6a0885fc2b1959682430fdd5fa8456ea692505d18f6cdd3`,
  binary hash `f1eb1a4486274c35f4accf7bc13b595cfdbcf2d7c9aa6b46fb281f19d0d52895`.
  Its 90 parsing, 1 regression, 39 trim, 9 failure, 20 check and 69 usage tests
  passed. The checked binary is outside Git, in the member's ignored scratch
  directory (source in `.ultramath/smx06hpp8/m5/.scratch/tools/`).
- `lrat_rup_check.py`, unverified source here, used as a second independent
  implementation of the LRAT/RUP semantics, not as a trusted checker.

## Rebuilding locally (only if needed)

Use the same reviewed upstream source, isolated under the project. Do not
silently use an unidentified executable. Check these exact source/binary hashes
and run its self-tests:

```sh
mkdir -p .scratch/lrat-trim-423194927df747528d5b7364806b5b77b2660c12
curl -fsSL \
  https://codeload.github.com/arminbiere/lrat-trim/tar.gz/423194927df747528d5b7364806b5b77b2660c12 \
  -o .scratch/lrat-trim.tar.gz
printf '%s  %s\n' \
  e71af67672133ed0c6a0885fc2b1959682430fdd5fa8456ea692505d18f6cdd3 \
  .scratch/lrat-trim.tar.gz | sha256sum -c -
tar -xf .scratch/lrat-trim.tar.gz \
  -C .scratch/lrat-trim-423194927df747528d5b7364806b5b77b2660c12 \
  --strip-components 1
cd .scratch/lrat-trim-423194927df747528d5b7364806b5b77b2660c12
./configure && make && make test
cd ../..
sha256sum .scratch/lrat-trim-423194927df747528d5b7364806b5b77b2660c12/lrat-trim
export LRAT_TRIM="$PWD/.scratch/lrat-trim-423194927df747528d5b7364806b5b77b2660c12/lrat-trim"
```

No global package install is needed. `run_pipeline.py` fails if the checker path
does not exist; it does not fall back to another checker or a status-only claim.
The repository-root calculation in the copied tools helper is
`HERE.parents[1]`, since the project root is its parent. The result-directory
copy uses `HERE.parents[2]`.

## Not available here

- `cake_lpr`: requires a CakeML/SML compiler, absent in this VM.
- `lrat_isa`: Boost headers and Clang/Isabelle-2024 are absent here.
  **No binary of either was downloaded.** So this experiment adds independent
  replay and trimming, not a formally verified checker.
- No wall sweep, no new open-parent search, no cube campaign, no production
  ledger modification or binding. R11 is one already closed leaf, with sibling
  leaves OPEN. N14/R11 only show different certificate-storage costs; they are
  not evidence of faster search on larger instances.

The normalized strict RUP-only replay of the separate Toeplitz control hit its
60-second cap; do not conflate that unverified event with the successful LRAT
pipeline here.
