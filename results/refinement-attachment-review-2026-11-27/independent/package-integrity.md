# Independent package-integrity and checker audit (direction F)

## Verdict

The archives are internally consistent and the supplied quickstart proof bytes are good under the required strict checks. **The quickstart's own checker wrapper is nevertheless protocol-noncompliant:** it suppresses warnings with `-w`. This is a defect in its acceptance procedure, not a counterexample to the five actual certificates. The larger package's targeted verdict/normalization helpers passed their probes, and the coordinator's committed offline replay was independently reproduced.

No campaign search, exhaustive historical replay, Kissat rebuild, wall-row closure, or Ramsey inference was performed. All work stayed below `.ultramath/smwyob8l4/m2/`; coordinator files were read at the requested commit `a74f7c2915f4482f5f7906bb2ca451acd031de4d` with `git show`, without relying on the later moving worktree HEAD. The coordinator ZIP audited below is the captured `c0b731…158` snapshot used for the replay. At the final recheck, the shared ZIP had been externally replaced by `2a630735…4c`, which is **not** covered by this report; see [concurrent-mutation.log](audit/concurrent-mutation.log). The two newly supplied attachments retained their audited hashes.

Environment: CPython 3.12.14, x86-64, `cc (conda-forge gcc 16.2.0-7) 16.2.0`. Before execution I inspected the relevant Python and C entry points described below. The native checker was privately compiled from the quickstart's bundled `drat-trim.c` (source SHA-256 `d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee`), which is also the source digest named by the larger package's Kissat identity record. No second native checker implementation was used.

## 1. Archive integrity: verified

[zip_structure.py](audit/zip_structure.py) fully reads every member, checks CRC and SHA-256, and checks unsafe paths, duplicate normalized names, case-fold collisions, encryption, symlinks, and special file types. [check_archive_manifest.py](audit/check_archive_manifest.py) independently checks manifest syntax, exact nonmanifest membership, and every listed digest.

| Archive | ZIP entries | Nonmanifest hashes passing | Whole-ZIP SHA-256 |
| --- | ---: | ---: | --- |
| `K58_reviewer_quickstart.zip` | 25 | 24/24 | `57c572afbd7db2047facf614788a903924e01bb60ed3cb1f210922da1f5cff95` |
| `K58_cube_conquer_verification.zip` | 3,309 | 3,308/3,308 | `42b5c997dc6ad341e42b1af0dc76c5ffc49fadc55a01838f20bbbc183039f9de` |
| `K58_adaptive_wall_solver.zip` | 10,410 | 10,409/10,409 | `3324b778ea425dbcd48a3c7f19a38812820066d769581569f318b61108837b75` |
| `K58_wall_sweep_evidence.zip` | 19,926 | 19,925/19,925 | `47bd1aa500756d70dce15b7680f83a290ee13e81c618f8ecae62583ab6fbef7b` |
| coordinator `k58-refinement-pilot-audit.zip` | 496 | 495/495 | `c0b73190fd7884e5420aa198c2a33362386b6235fd6f83fb8c524630c2ace158` |

For these five archives, there were no unsafe paths, duplicate/case-colliding names, symlinks, encrypted members, special modes, or CRC failures. The two original campaign inputs contain 30,336 entries including their two manifests, hence **30,334 nonmanifest entries** as the new addendum says. Their campaign-relative file sets are disjoint, including the manifests. Exact outputs are in `audit/*.structure.log`, `audit/*.manifest-check.log`, and [original-overlap.log](audit/original-overlap.log).

The supplied `K58_cube_conquer_audit.md` and `K58_verification/REPORT.md` are byte-identical, SHA-256 `de8caf4afb26e4341f99d2181c4dff3beaf3b2fc270f1e4a2065fcd135f81099`.

These are internal integrity facts. The new ZIP manifests are unsigned and do not authenticate their producer.

## 2. Quickstart warning defect and actual strict replay

### Defect: warning suppression is active

`K58_review/formulas.py:175` invokes:

```text
drat-trim QUERY PROOF -i -w -U
```

and `README.md:15` recommends the same flags to external reviewers. Its acceptance condition is only return code zero plus a line containing `s VERIFIED`; it never checks for warnings. This violates the required strict-RUP protocol (`-i -U`, no `-w`, zero warnings).

A small complementary-unit diagnostic makes the consequence concrete. On a satisfiable-proof-irrelevant but already-UNSAT fixture, malformed proof byte `X` produces a wrong-binary-prefix warning: the unfiltered checker returns zero and prints `s VERIFIED`; with `-w`, the stock wrapper prints `STOCK WRAPPER ACCEPTED`. See [exposed log](audit/warning-probe/unit-bad-prefix-exposed.log), [suppressed log](audit/warning-probe/unit-bad-prefix-suppressed.log), and [stock-wrapper result](audit/warning-probe/unit-bad-prefix-stock-wrapper.log). This fixture tests diagnostics only; it is not offered as a refutation of a valid packaged proof.

### Positive result: all five actual native checks pass strictly

[strict_quick_replay.py](audit/strict_quick_replay.py) leaves the quick package unchanged, regenerates its formulas/proofs, preserves all queries and proofs, and replaces only `check_native`. Each call uses `-i -U`, captures stdout and stderr, requires exactly `s VERIFIED`, return code zero, and no warning lines.

| Regenerated check | Query SHA-256 | Result with no `-w` |
| --- | --- | --- |
| generic 14-arm rule | `baf5ba5fac6c4c3553486ae6a98e50a48e0785f024fbd65e85f1c39ea10e1ff8` | pass, 0 warnings |
| physical color 0 | `b841ae190fbe66819c1d552dd87c627468078654913556d167b3fa7af8a5af40` | pass, 0 warnings |
| physical color 2 | `fd929a7053e2bcac8448ae0a0b3d2447093782fff045629ef7129f0dc3894a45` | pass, 0 warnings |
| physical color 3 | `180c5053f30718ffc1ebdf426bafeb14dd46176599419b355d1170061cc73a06` | pass, 0 warnings |
| parent excluding color 1 | `364c1d632b8f220ebb185e7a43ad23b733abc62163f9b5032d79fa9611ec9b95` | pass, 0 warnings |

The full proof hashes, byte counts, commands, and logs are in [strict summary](audit/strict-quick/summary.json). Colors 2 and 3 use the two-byte empty-clause RUP proof; color 0 and the cover use the transported proof. The color-1 child remains `OPEN_UNKNOWN`, with query hash `29f7a4c3…320e46` and no proof receipt. The cover refutes the strengthened parent together with `¬5354`; therefore every model of **that guarded parent** uses physical color 1. This does not generalize to an unguarded representative or a wall row.

The stock run also completed successfully, rejected all nine altered event records, reconstructed parent `REFINED`, retained one continuation, and produced identical initial/final roster hash `9c2d9245…fe09afe` with no whole-representative changes. Its printed census has 983,774 live representatives on 11,585 rows. The run printed 2.20 seconds (shell elapsed 2,236 ms); the strict driver took 1.456 seconds using already-built tools. These are single local observations, not validation of a general runtime or of the alleged 12-minute five-worker full replay. See [stock output](audit/quick-stock.stdout) and [strict output](audit/strict-quick.stdout).

## 3. Larger package: checker diagnostics and additions-only handling

A source search of the merged installed tree found no active quoted `-w` checker argument. The three occurrences are the suppression guards in `cover_proofs.py` and `engines/shared/campaign.py`, plus a deliberate negative-control call. `proof_status.clean_verdict` requires one exact success and rejects warnings; `check_trace` and `cover_proofs.rup` reject attempts to pass `-w`.

[proof_status_probe.py](audit/proof_status_probe.py) directly tested the standalone helper:

- ordinary exact success accepted;
- warning-bearing output, multiple statuses, `s VERIFIED extra`, and success only on stderr rejected;
- malformed `X` binary proof rejected with `invalid binary DRAT tag`;
- on the coordinator's two raw arm-14 proofs, `write_additions` preserved every addition and the final empty clause and reproduced the committed normalized files **byte-for-byte**.

The normalized SHA-256 values are `467a694a…6067e` (guard parent, 190,532 additions, 277,775 deletions removed) and `4a9dcd4b…fa37c` (refined child, 237,831 additions, 342,749 deletions removed). See [normalization summary](audit/normalization-probe/summary.json). These are fresh transformations and freshly replayed artifacts, not cached-status inheritance.

The source makes the mode distinction correctly in the reviewed paths: ordinary imported/native DRAT uses `-i` without `-U` and without warning suppression; the local transport checker calls `-i -f -U`. Fresh producer conversion sites replay the generated additions-only candidate on the exact CNF before accepting it. The full set of 2,469 transport certificates was **not** run in this direction. The larger package's live `audit_controls.py`, complete `audit_batch.py`, and all campaign panels were also not run; those remain separate obligations, not facts established by these helper probes.

## 4. Provenance: verified versus merely attested

The standard-library installer and `audit_provenance.py` both passed. The latter reconstructed the pinned public commit, three trees, three audit blobs, and the upstream Kissat Git tree from the included tarball. [external_provenance.py](audit/external_provenance.py) then checked live primary-service metadata:

- GitHub API: project commit `76f93b4d95712a20b7098a89650f123431cd115d`, tree `d82effa0a5ec46144c6130e3ac835f44a99f2726`; `verified: false`, `reason: "unsigned"`.
- GitHub API: Kissat commit `8af8e56f174b778aef3aa45af9f739b2a5f492c2`, tree `81c120d5304b5ea5c66cc1b9bceed25e10436df9`, matching the offline source-tree reconstruction.
- Official PyPI JSON: both wheel filenames, upload timestamps, and hashes match (`six` `4721f391…0586c3274`; `python-sat` `882687f8…7d81b4c2`).

Exact results and downloaded metadata are in [external-provenance.stdout](audit/external-provenance.stdout) and `audit/external/`; offline outputs are [install](audit/full-install.stdout) and [provenance](audit/full-provenance.stdout).

**Not established by those checks:** original producer identity, original publication time, immediate archive ancestry, or signatures on the new packages. The shipped/rebuilt executable hashes matching `identity.json` is internal binding, not a source-to-binary proof. I did not build Kissat, run its banner, reproduce either build log, or reproduce the claimed second-build 10,535,211-byte owner proof. Those build assertions and `tar-build-check.json` remain attested inputs here. Offline wheel hashes alone would also have been internal; the separate live PyPI check is what verifies their external reference.

## 5. Coordinator comparison at `a74f7c2`

The committed coordinator already treats warning diagnostics correctly: `verify_release.py` uses `-i -U`, no `-w`, rejects warnings, and explicitly tests the malformed-prefix control. The quickstart's suppression therefore does not preserve the coordinator's strict acceptance semantics.

I freshly extracted all 496 coordinator bundle members and ran its standard-library-only `verify_release.py` with my privately compiled checker. This is proof replay only, not a solver search. It passed:

- **78/78 strict positive checks**, **42 distinct query/proof pairs**;
- 31 cohort, 9 sibling exclusions, 9 complete covers, 27 stock transports, and 2 fresh deletion-free conditional proofs;
- malformed control returned zero and printed `s VERIFIED`, but was rejected by the warning policy;
- independent log scan: 78 exact success lines, zero warnings, zero other status lines.

Wall time was 18.982 seconds. The generated replay summary is **byte-identical** to the pinned `a74f7c2` summary, both SHA-256 `94f8be61dbf5ea96e8c6adc72da263a924370af9b78566e228d7d5f049dc9c44`. See [stdout](audit/coordinator-replay.stdout), [summary](audit/coordinator-replay/replay-summary.json), and [diagnostic scan](audit/coordinator-log-scan.log). This verifies the coordinator bundle's replay diagnostics; it is not a new semantic audit of all nine replacements, whose guarded scope remains unchanged.

## 6. Explicitly untested commitments

This direction does **not** independently establish: the 12-minute five-worker/full quick replay; fresh execution of 1,101,974 cap128 calls; the 3,066-parent exhaustive replay; minimum 28 or the standalone LRAT run; the full 2,469-certificate transport family or all-recipient encoding; all 11,585 first-tier reconstructions; satisfiability/unsatisfiability of any surviving OPEN case; altered-CLOSED-parent ledger semantics; any whole-row or Ramsey result; or any general runtime comparison. Package reports and stored receipts asserting those items were not promoted to execution facts merely because their hashes matched.

### Reproduction entry points

```bash
python3 audit/zip_structure.py INPUT.zip NEW-output.json
python3 audit/check_archive_manifest.py INVENTORY.json INPUT.zip ROOT/SHA256SUMS
python3 audit/strict_quick_replay.py
python3 audit/proof_status_probe.py
python3 audit/external_provenance.py
```

The native build commands are recorded in [quick-build.log](audit/quick-build.log). The exact larger-package offline commands used were:

```bash
TMPDIR="$PWD/scratch" PYTHONDONTWRITEBYTECODE=1 \
python3 extracted/full/K58_verification/install_audit.py \
  --solver ../../../attachments/let-s-try-and-rbdv/K58_adaptive_wall_solver.zip \
  --evidence ../../../attachments/let-s-try-and-rbdv/K58_wall_sweep_evidence.zip \
  --out "$PWD/installed/full-audit"
python3 installed/full-audit/audit_provenance.py
```

The coordinator replay command was:

```bash
TMPDIR="$PWD/scratch" PYTHONDONTWRITEBYTECODE=1 \
python3 audit/coordinator/verify_release.py \
  --cohort extracted/coordinator/k58-refinement-pilot/cohort \
  --assembled extracted/coordinator/k58-refinement-pilot/assembled \
  --comparison extracted/coordinator/k58-refinement-pilot/comparison \
  --checker tools/drat-trim --out audit/coordinator-replay
```

[environment.log](audit/environment.log) records interpreter/compiler details and the later externally advanced HEAD; the coordinator comparisons themselves use the requested immutable commit above.
