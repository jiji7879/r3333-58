# Coordinator integration — new files only

Nothing in this directory modifies the tree. Everything below is additive and
opt-in; no default, ledger, encoder, `run`, `finalise` or frozen coverage is
touched, and the gate never starts a solver or touches the network.

## Files to add

| from (this directory) | to (repository) | sha256 at HEAD `e856d75` |
|---|---|---|
| `gate.py` | `tools/admission/gate.py` | see `receipts/file-hashes.txt` |
| `adapters.py` | `tools/admission/adapters.py` | idem |
| `run_audit.py` | `tools/admission/run_audit.py` | idem |
| `tests/test_gate.py` | `tools/admission/tests/test_gate.py` | idem |
| `POLICY.md` | `results/next-directions-2026-11-28/admission/POLICY.md` | idem |
| `RESULTS.md` | `results/next-directions-2026-11-28/admission/RESULTS.md` | idem |
| `receipts/*.json` | `results/next-directions-2026-11-28/admission/receipts/` | produced by the run below |

```sh
# from the repository root, with the member directory present
mkdir -p tools/admission/tests results/next-directions-2026-11-28/admission/receipts
cp .ultramath/smx0er1f6/m5/gate.py            tools/admission/gate.py
cp .ultramath/smx0er1f6/m5/adapters.py        tools/admission/adapters.py
cp .ultramath/smx0er1f6/m5/run_audit.py       tools/admission/run_audit.py
cp .ultramath/smx0er1f6/m5/tests/test_gate.py tools/admission/tests/test_gate.py
cp .ultramath/smx0er1f6/m5/POLICY.md          results/next-directions-2026-11-28/admission/
cp .ultramath/smx0er1f6/m5/RESULTS.md         results/next-directions-2026-11-28/admission/

sha256sum -c .ultramath/smx0er1f6/m5/receipts/file-hashes.txt   # pins what you copied
python3 tools/admission/tests/test_gate.py      # 26/26, stdlib only, <1 s
python3 tools/admission/run_audit.py --out results/next-directions-2026-11-28/admission/receipts
```

`run_audit.py` locates the repository root itself (it walks up for
`results/next-directions-2026-11-28` and `tools/color-resolved-wallcc`), so it
behaves the same in `tools/admission/` and in a member directory. It reads only
published receipts and writes only under `receipts/`.

## Merge rule (fail-closed)

An override is mergeable only if

1. its normalised record is committed under
   `results/next-directions-2026-11-28/admission/<name>.json`;
2. `python3 tools/admission/gate.py <record> --mode admission --out <verdict>`
   exits **0**. Exit 2 (`REJECT`) and exit 3 (`INCOMPLETE`) are both
   non-mergeable; a timeout, a missing artifact or an unpinned binary is
   `INCOMPLETE`, never a pass;
3. the verdict's `required_scope` is pasted verbatim into the result README;
4. the override is an explicit flag whose value is part of the cached leaf
   budget. `native_leaf.py` already implements this shape for
   `native`/`native_policy`/`native_sha256`; `campaign.py` re-runs a leaf whose
   budget changed. That is the mechanism rule `R7` requires — no new plumbing;
5. `tools/admission/tests/test_gate.py` passes.

`--mode audit` exists only for records already published before the policy; it
waives pre-registration alone. Do not use it to admit a new override.

## Deliberately not proposed

* No diff to `campaign.py`, `leafcert.py`, `native_leaf.py`, `wallcc.py`,
  `run`, `finalise`, the encoders or any ledger. The gate is a separate
  checker, not a stage in the pipeline, so a gate bug cannot corrupt a run.
* No change of defaults, no automatic engine/policy switch, no downloaded
  checker, no formal-verification claim.

## One patch worth considering later (untested, coordinator's call)

The KMT receipt pins the *formula* but not the solver binary: `pins.solver`
carries only `CaDiCaL 1.9.5 SAT solver.` and `pysat 1.9.dev22`, so the audit
records `R2_pins` incomplete for it even though its cost verdict is already
negative. If a future PySAT-arm record is ever meant to be admissible, its
budget should carry the solver identity the way the native path does — the
PySAT binding exposure plus a wheel/site-packages hash. I did not write that
patch: it changes a production receipt shape, and the present evidence says the
PySAT arms are not the ones being adopted.
