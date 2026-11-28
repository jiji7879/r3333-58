# Opt-in native LRAT pipeline

Read the measured result and reproduction guide at
[`../../results/next-directions-2026-11-28/lrat/README.md`](../../results/next-directions-2026-11-28/lrat/README.md).

From the repository root:

```sh
export LRAT_TRIM=/path/to/reviewed/lrat-trim
python3 tools/lrat_pipeline/run_pipeline.py --out results/next-directions-2026-11-28/lrat/rehearsal-receipt.json
```

The four example cases are already closed; no open wall case is selected.
`LRAT_TRIM` must point to the reviewed lrat-trim binary, whose parent directory
must also contain that source build's `test/` suites. Those tests must pass
before the experiment starts.
There is no checker fallback and no global package installation by this helper.

`lrat_rup_check.py` is a second unverified Python RUP-only checker, not a formal
verified checker. An untrimmed elaborated DRAT and a *trimmed* one are not
interchangeable: strict replay may require unmodified native-LRAT trimming,
not `--relax`. `UPSTREAM_LICENSE` is preserved in LICENSE from the upstream
lrat-trim source; generated proof/binary artifacts do not belong in git.
