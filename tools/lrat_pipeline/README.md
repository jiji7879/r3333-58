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

## Standalone per-case adapter (opt in)

`native_solve.py` supplies one hash-pinned formula to native CaDiCaL 2.1.2,
trims its native LRAT proof, and retains `leaf.lrat` only after lrat-trim
backward and forward replay and the separate Python RUP checker. It measures
native processing and the additional ASCII/second-checker work separately.

From the repository root:

```sh
export LRAT_TRIM=/absolute/path/to/reviewed/lrat-trim
python3 tools/lrat_pipeline/native_solve.py \
  --cnf .scratch/k58-0404-word-search/H8-word0.cnf \
  --expect-sha256 e8cc97847a6cab9c277933d2dd0d6112c79b061bebb5af221d57df5d6d6a2229 \
  --expected-outcome UNSAT \
  --out .scratch/native-lrat-my-case \
  --checker "$LRAT_TRIM"
```

The checker, CaDiCaL and Python checker pins are checked before solving. Choose
a fresh output directory. On accidental SAT or unexpected OPEN, the command
fails; a requested OPEN can be tested with `--conflicts N --expected-outcome
OPEN`. OPEN never returns a proof. The adapter cannot be dropped into the
cube-and-conquer cover runner: that runner composes leaf DRAT proofs with a CAS
prefix, and this adapter does not compose a parent-CNF LRAT certificate.

The test is an integration control, not a wall search:

```sh
python3 tools/lrat_pipeline/test_native_solve.py
```

It requires the closed input and reviewed binary above to be already present.
Missing inputs cause an explicit SKIP, not success. It checks the exact raw and
trimmed proof identities, capped OPEN, wrong expected outcome, bad input hash,
and output-path collision, removing temporary proofs after replay. Its compact
receipt is `results/next-directions-2026-11-28/lrat/adapter-test-receipt.json`.
A test retained 6,503,105 bytes from 14,594,230 native bytes; 1.990 native CPU
seconds became 2.987 seconds including the additional Python verification.
Those are one-case measurements, not a blanket search or pipeline speedup.
