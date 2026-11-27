# Direction A: quickstart reproduction and worked-refinement audit

## Verdict

**The guarded worked refinement reproduces, but the quickstart's default native-check acceptance path does not meet the required warning-free protocol.** A separate, untracked worktree strict wrapper repairs that path and passed here. Nothing in this result closes original representative 983585, a wall row, or a Ramsey case.

The Python execution paths and C entry points/options were source-inspected before execution. Extraction, builds, exports, and mutations stayed under `.ultramath/smwyob8l4/m4/`. The requested coordinator baseline was `a74f7c2915f4482f5f7906bb2ca451acd031de4d`, but the executed `tools/refinement/review_quickstart.py` is **not in that commit**: `git show a74f7c2:tools/refinement/review_quickstart.py` fails, `git status` marks it `??`, and no local commit contains the path. The exact worktree file run has SHA-256 `20a03e4c361ac1f449688acf4bcdc55a2e97a3f86f8000c36248ffee0eda5b68` (Git blob `de821bd3bf446935e5cc414d738b7e4c057b26f2`). Results below therefore distinguish that untracked helper from committed work at `a74f7c2`. No coordinator or campaign file was modified.

## What was independently checked

The exact parent is representative plus seven units, not the unguarded representative:

- representative SHA-256: `afbab09a68937e6674e23fbddc6905cdfd8a86372007c7f6713d64e9863b8afd`;
- parent SHA-256: `2c339aec5100b8cd5608968f7f7cc97ac30eac34246c10807f06cea11c773244`;
- appended pins: `5349,5445,5449,5628,5632,5709,5713`.

Removing those seven suffix units from the exported parent reconstructed the representative hash byte-for-byte. The physical `(32,43)` variables are `5353,5354,5355,5356`; the parent contains their four-way disjunction and every pairwise exclusion. Every child body is exactly the parent body followed by the stated one-unit clause, with the header clause count increased by one.

| Physical color | Exact child query SHA-256 | Result actually supported |
|---|---|---|
| 0 | `b841ae190fbe66819c1d552dd87c627468078654913556d167b3fa7af8a5af40` | UNSAT, strict transported RUP replay |
| 1 | `29f7a4c3d3f49eff39ac8d6607e446e2f015741b3d948d1ea452d98eb5320e46` | **OPEN_UNKNOWN**, no refutation/model supplied or established by this audit |
| 2 | `fd929a7053e2bcac8448ae0a0b3d2447093782fff045629ef7129f0dc3894a45` | UNSAT, independent input-clause unit propagation and strict empty-clause RUP |
| 3 | `180c5053f30718ffc1ebdf426bafeb14dd46176599419b355d1170061cc73a06` | UNSAT, independent input-clause unit propagation and strict empty-clause RUP |

The separate unit propagator reached conflicts after assigning 771 variables for color 2 and 1768 for color 3. It also directly checked color 2's root units `127,171` and triangle clause `-127 -171 -5355 0`.

The direct coverage query is exactly `parent + (-5354)` and has SHA-256 `364c1d632b8f220ebb185e7a43ad23b733abc62163f9b5032d79fa9611ec9b95`; its proof hash is `6a22c515098b6d0a2f095c2805edde6621302036372ad35a086a451459726632`. Thus the refutation of `P AND NOT color1` proves every model of this **guarded** parent must use color 1. Together with the other checked child refutations this justifies parent `REFINED` with sole continuation color 1 `OPEN_UNKNOWN`; it does not make the continuation SAT or UNSAT.

The local 14-arm query, color-0 child, color-2 child, color-3 child, and coverage all passed my `-i -U -t 300` wrapper with return code 0, exactly one `s VERIFIED`, and zero warnings. The same untracked worktree wrapper additionally reran the exported cover independently, also warning-free. The checker was my build of the bundled C source, not an independently sourced implementation (source `d834b649…2ee`, executable `8b2c77c7…fda2`).

## Concrete protocol defect and untracked-worktree comparison

Supplied `formulas.py:172-178` runs `drat-trim -i -w -U` and accepts return code 0 plus a success line. This is not merely a hypothetical warning issue. My malformed stream `61 00 62` (`a NUL b`, a valid empty-clause addition followed by an invalid opcode) on the color-2 query produced:

- unsuppressed `-i -U`: return code 0, `WARNING: wrong binary prefix, stop reading proof`, and `s VERIFIED`; strict acceptance **rejects** it;
- supplied `-i -w -U`: return code 0 and `s VERIFIED`, with the warning hidden; the supplied acceptance predicate **accepts** it.

The valid prefix still proves this particular query UNSAT, so the control does not negate the mathematical refutation. It proves a helper-level protocol/integrity gap, not that the whole runner necessarily accepts an edited archive: the fixed manifest can reject archive edits earlier. See `work/quick_runs/m4-negative-controls-final/result.json` and both checker logs.

The untracked worktree `tools/refinement/review_quickstart.py:38-52` replaces only `check_native`, omits `-w`, and requires exactly one success line and no warnings. The exact hashed file identified above passed all five reconstruction checks and its sixth exported-cover check in my private run. This is an appropriate quickstart acceptance path, but it is auxiliary worktree code, not evidence committed at `a74f7c2`. No `-w` should be restored.

Five additional semantic mutations were independently rejected by the replayed-grant transition check: `CLOSED` parent with open survivor, omitted fourth color, survivor promoted with a sibling proof, wrong color-0 query hash, and omitted continuation. Exact rejection reasons are in `work/quick_runs/m4-capture/capture.json`. This tests only the quickstart event semantics, not every path in the larger package.

## Frozen total and boundary

The decompressed quickstart roster is byte-identical to `K58_live_983774.tsv.gz`, with SHA-256 `9c2d9245e031d8f2cc01ebfac0b6173ca18c5a24bf808e5efde33aa158e09afe`. Independent CSV counting gave **11,585 rows and 983,774 live representatives**. Representative index 983585 is still present at revised rank 46 with pair `21012/22101`. Ledger initial/final roster hashes are equal and `whole_representative_changes=[]`. Hence the worked operation leaves the frozen total unchanged and does not remove 983585 from the campaign queue.

## Timing and full-replay limits

On this 4-CPU VM (Python 3.12.14, GCC 16.2.0), measured wall times were **2.33 seconds** for the supplied default quick run and **2.05 seconds** for the untracked worktree strict wrapper. These are local measurements, not confirmation or refutation of a 13-second observation on another host, and imply no general runtime ranking.

The optional quickstart full replay was **not run**. Its documented `--full-from` path requires both original ZIPs. `K58_adaptive_wall_solver.zip` is present, but `K58_portable_learning.zip` is absent from the supplied attachments and does not appear under that name in the larger ZIP's file list. Consequently this audit provides no evidence for a five-worker/~12-minute full replay. The quickstart README's own example uses `--jobs 4`.

Also untested here: original per-class SAT-screen regeneration, exhaustive historical cap128 execution, the larger package's 3066/minimum-28/all-recipient claims, its aggregate event-log tamper paths, whole-row closure, and every Ramsey-bound inference. Quickstart census arithmetic was reaggregated by its runner from stored records; that is not historical regeneration.

## Artifacts and reproduction

Run commands from `.ultramath/smwyob8l4/m4/`; exact invocations are in `reports/commands.log`.

- `scripts/capture_quickstart.py`: strict export and semantic controls; output `work/quick_runs/m4-capture/capture.json`.
- `scripts/audit_worked.py`: package-independent DIMACS, propagation, roster, and status inspection; output `work/quick_runs/m4-independent-audit.json` and `.log`.
- `scripts/checker_controls.py`: warning-suppression counterexample; output `work/quick_runs/m4-negative-controls-final/result.json`.
- `work/quick_runs/coordinator-strict/strict-checks.log` and `independent-cover-check.log`: output from the untracked worktree strict wrapper (the directory name is only a run label).
- `reports/checksums.txt`, `reports/environment.txt`: artifact identities and environment.
- `reports/revision-attribution.txt`: exact `git show`, status, history, and hash output establishing the strict helper's untracked provenance.
