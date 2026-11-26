# Ultramath core reports and storage retirement — 2026-11-26

## Outcome and trust boundary

**20,364 unretained raw files were deleted, freeing 108.111 GiB as measured
on the filesystem.** `.ultramath/` is approximately **17 GiB** (17,640,452,096
allocated bytes across the mount), and `df -h` reports **158 GiB available**
rather than 50 GiB before this archival phase. The live audit `smwx73ni9`
was never included in pruning.

This is a **bounded source/text archive plus selected certificate retention**,
not a backup of every proof. Historical summaries establish neither a new
Ramsey bound nor a local replay of deleted evidence. All 140 target
`(16,16,13,12)` rows remain OPEN; $R_4(3) \le 58$ was not proved here. A
platform `solved` label denotes accepted finite submissions, never that
Ramsey result.

## Read first

- [Curated core points](CORE_POINTS.md): the results worth preserving and the
  main traps not to repeat.
- [Storage inventory](INVENTORY.md): byte totals and DRAT totals for all 33
  completed non-live swarms. This is **not** an acceptance table.
- [Audited reports](audited/): six detailed retention reports, accepted in the
  separate audit swarm (m1 for A, m4 for D):
  - [smwwdcyxb](audited/smwwdcyxb.md), [smwx2syxr](audited/smwx2syxr.md)
  - [smwr3llof](audited/smwr3llof.md), [smwp3xc7p](audited/smwp3xc7p.md),
    [smwvg1m43](audited/smwvg1m43.md), [smwswz4x9](audited/smwswz4x9.md)
- [Audit/verdict corrections](AUDIT_NOTES.md): authoritative acceptance and
  limitations that must survive any shortening of those reports.

The other two audit members stopped without producing group reports. The
other old swarms have **not** been given a fresh mathematical acceptance audit
here. Their reports and source material were preserved where selected by the
archive's explicit rules; their historical mathematical claims are not freshly
certified by this cleanup.

## Preservation archive

[`dist/ultramath-source-2026-11-26.tar.gz`](../../dist/ultramath-source-2026-11-26.tar.gz)
contains **59,380** small source/report/witness files, **1,826,554,796 bytes**,
and has SHA-256:

```
277ddd914adaa82d1aade0f0f860f2e6fd97cd7016f1d7d038c9e125b161c445
```

The archive is in `dist/`, not committed to Git. Files were selected from 33
completed swarms by known text suffixes, at most **4 MiB per file**, excluding
raw DRAT/LRAT and binary contents. It includes reports, code, ledger and
receipt material, but its existence must not be used to claim preservation of
the discarded raw proof bytes. `preservation.json` records the exact selection.

`raw-file-index.jsonl.gz` has **98,294** original file records, including size,
allocated size, kind and whether a file was preserved. Original paths in that
index are **not assertions that those paths still exist**. `inventory.json`
contains per-swarm aggregates.

## Locally retained certificate trees

The explicit policy is [`retention-policy.json`](retention-policy.json). It
keeps the primary entrance proof store, K15/K16 classification material, the
unique four Lean modules of the recent engineering work and their environment,
the compact clone/cross-support family, selected incidence/design certificates,
the circulant proof, and the release manifest for the 1,018 newly certified
cover cases. In particular, these were **not** pruned:

- `.ultramath/smwwdcyxb/m2/proofs/` — the full 8.62 GB primary entrance store.
  Its file count is not the proof count: the canonical record is 2,830 verified
  stored proofs, with TT:2 and UT:3 (600+600) the only complete families.
- `.ultramath/smwwdcyxb/m1/k16-regular/` and its complete `m3/` classification
  material.
- `.ultramath/smwx2syxr/m1/`, containing `Saturation.lean`, `Discharge.lean`
  and the corresponding construction. Those modules were not added to the
  repository's central build order by this cleanup.
- `.ultramath/smwvx4uzm/`, `.ultramath/smwswz4x9/m5/work/dec/`,
  `.ultramath/smwswz4x9/m6/certs/`, `.ultramath/smwr3llof/m8/`, and
  `.ultramath/smwp3xc7p/m3/w/k58-solver/release-final/`.

Other large raw solver evidence was dropped when not included in the selected
source archive. Consequently, many old worker directories are **not resumable
proof-building workspaces**. A historical script or manifest referring to a
deleted `.drat`/CNF path can require regeneration and a new DRAT check. Do
not turn the absence of those bytes into a new mathematical open gap or into
an assertion that the old statement was invalid.

## Checks actually performed

- Archive creation re-read and hash-checked **59,380/59,380** members.
- The pruner checked **50,782/50,782** non-protected source files against
  those hashes immediately before pruning; **0 mismatches**.
- It removed only indexed, non-symlinked ordinary files under `.ultramath/`,
  excluding live and protected prefixes, and verified all **20,364** resulting
  paths absent while every protected prefix remained present.
- Fixture tests exercised dry-run, apply, protected/live exclusion, size and
  equal-length hash tampering, and refusal when an unindexed file enters a
  protected tree. A path-index inefficiency found during check-only execution
  was fixed before the actual run.
- Retained proof checks now replayed **1/1** circulant DRAT and **4/4** small
  incidence DRATs to `s VERIFIED`; logs are in `certificate-checks/`. Some
  non-fatal duplicate-literal warnings remain in the circulant log.
- No full 2,830-proof replay, exhaustive old-swarm correctness audit, full-row
  closure, solver speed result, or formal Ramsey-bound proof was performed.

For fine-grained byte truth, use `prune-measurement.json`: free bytes increased
from **52,687,007,744 to 168,770,531,328**, a gain of **116,083,523,584 bytes**.
The deletion entries' allocated bytes sum to 116,092,264,448; these measures
differ slightly and are not incorrectly equated.

## Tooling

`tools/archive_ultramath_history.py` builds and validates a bounded archive and
index; it never deletes input. `tools/prune_ultramath_history.py` defaults to
check-only and requires explicit `--apply` plus `allow_raw_discard` in the
retention policy. Its fixture tests were run before use. Large archives stay
out of Git; the reports, indices and compact measurement metadata are committed.
