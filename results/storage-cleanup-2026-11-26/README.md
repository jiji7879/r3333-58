# Expanded storage cleanup — 2026-11-26

## Outcome

- Free bytes before: **31,002,316,800**.
- Free bytes after: **54,808,825,856**.
- Increase: **23,806,509,056 bytes (22.172 GiB)**.
- `df -h` changed from **29 GiB available / 89% used** to **52 GiB available / 80% used**.
- RAM: 15 GiB total, 13 GiB available, without swap. No project background jobs were active.

`measurement.json` is the direct record. The selected directories sum to
**23,758,282,887 bytes (22.127 GiB)** by `du -sb`.
The free-space increase is 48,226,169 bytes larger.
Those quantities are not equated: the filesystem-wide difference also includes
small incidental filesystem activity outside the directory-total calculation.
An interim chat estimate of 18.97 GB was an arithmetic error; the measured
sum here supersedes it.

## Deleted paths

| Path | `du -sb` bytes before deletion |
| --- | ---: |
| `.ultramath/smwwdcyxb/m2/.scratch` | 2,780,399,876 |
| `.ultramath/smwp3xc7p/m8/scratch` | 3,283,110,478 |
| `.ultramath/smwwdcyxb/m7/cc/run10/c021_030` | 40,359,793 |
| `.ultramath/smwwdcyxb/m7/cc/run10/c021_031` | 83,043,963 |
| `.ultramath/smwwdcyxb/m7/cc/run10/c021_032` | 2,074,592,822 |
| `.scratch/smwu1x5uy` | 6,841,019,385 |
| `.scratch/smwtqk6ku` | 6,194,311,380 |
| `.scratch/d4work` | 2,461,445,190 |

The `.ultramath` additions are m2's own `.scratch`, m8's raw scratch from
`smwp3xc7p`, and the three superseded `run10/c021_030`, `c021_031` and
`c021_032` worker directories. Before deleting the latter, every current
`merged-tree.json` node's `source` was checked not to name them. The worker
`run10/c485_032` that *is* referenced remains. The three `.scratch` roots are
old scratch solver work, including their raw formulas, solver output and
cached core data.

## Preservation

A bounded text/source archive, **not a full backup of the deleted roots**, is
at `dist/legacy-scratch-text-2026-11-26.tar.gz`:

- 2,765,326 bytes compressed;
- SHA-256 `5787069cc5f22801a74f0d3964c61d46229bba50def7a71b82e0811dc2c75375`;
- 8,386 small scripts, code, reports and receipts;
- `retained-source-sha256.json` has each retained path, byte count and SHA-256.
- `archive-verification.json`: every archived entry was extracted and hashed,
  8,386 checks passed, 0 failures. The extraction cache was removed afterwards.
- Selected suffixes: `.md`, `.py`, `.lean`, `.c`, `.h`, `.sh`, `.json`,
  `.jsonl`, `.txt`, `.tsv`, `.csv`, `.yaml`, `.yml`, `.toml`, `.col`,
  `.proof`, `.cert`, `.log`, each at most 2 MiB.

Raw DRAT/CNF/model/binary contents in the deleted scratch locations were not
silently claimed to have been archived with this text selection.

## Explicitly retained

- `.ultramath/smwwdcyxb/m2/proofs/`: the full primary entrance-proof store,
  still 8.1 GiB by `du -sh`; m2's separate `.scratch` was the target.
- The externally verified large DRAT files in
  `smwwdcyxb/m7/cc/run4/core017`, `run5/r5_core024-001`,
  `run5/r5_n025a-015`, `run6/n025b_core`, and `run11/c485_028`.
  Their `failed/` names reflect original checker timeouts; external
  verification later succeeded and is recorded in `COVERAGE.md` and
  `external_verifications.json`.
- `smwwdcyxb/m7/cc/run10/c485_032`, referenced by the current merged cover.
  No proof replay was needed or claimed after deleting different directories.
- All of the accepted `smwx2syxr` working tree.
- **`.ultramath/smwtqk6ku/m6/cnf/`**: initially considered, then explicitly
  retained because it contains DRAT files as well as CNFs.
- `attachments/`, original solver archives and the release
  `dist/k58-solver.zip` (hash rechecked as
  `eedbf3da50edae0054e278a89f822b1d3a9f2bbf55df42a6f3fa082525276428`).

No Git-tracked source file was deleted. Other untracked work was left alone.
The preservation archive lives beside the distribution archives rather than
being committed; the small metadata and this report are committed.
