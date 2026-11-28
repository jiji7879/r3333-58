# Reproduction

Working proof and source controls, no phase guessing and no large archive:

```sh
# Existing source and checker required; no global installs.
python3 tools/color-resolved-wallcc/test_native_leaf.py
python3 -B results/next-directions-2026-11-28/lrat-optin/tests/run_tests.py
```

Expected completed-test outputs:
- `PASS native SAT, UNSAT replay, corrupt-proof rejection, bounded OPEN,
  unknown/invalid policies, resume budget binding and unchanged PySAT defaults.`
- `24 checks passed, 0 failed` in `tests/replay.log` and
  `acceptance-replay.json` / `receipts/optin-tests.json`.

The full harness copies tools and fixtures and writes temporary outputs under
`.scratch/lrat-optin-integrated-tests`. It first hashes the integrated/tested
source copy, so it supports both (i) applying the candidate to a stock tree and
(ii) rerunning after the option was already merged. It then exercises ordinary
LRAT evaluation, auditing, corrupted/truncated artifacts, cut-premises,
checker/cache binding and OPEN handling. The current direct test command was
repeated after modifying paths for this package and returned exit 0.

`patched/` preserves the tested three-file source adaptation;
`src/lrat_optin.py` is the opt-in helper; `patches/0001-lrat-optin.patch`
preserves the patch. The production versions are in `tools/color-resolved-wallcc/`.

## Timing comparison

Read `acceptance-replay.json`; do not substitute a single log summary for an
entire-engine rank. On this H8 run check CPU was 0.899 s (DRAT) vs 0.079 s
(LRAT) while raw artifacts were 9,529,642 B versus 14,594,230 B. Optional full
binary structure auditing cost 1.332 s. Leaf CPU/RSS were 2.460 s/156,036 KiB
versus 2.748 s/86,228 KiB. These values are specific to the replayed case and
are not evidence of a general solver, memory or byte advantage.

Native backend and preprocessing reports are in `../backend/` and
`../preprocessing/`; neither is silently combined with this LRAT option.
Their speeds and costs are independently scoped and need a fresh matched
experiment before combining paths.
