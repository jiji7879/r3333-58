# Native LRAT for the C&C engine — tested opt-in

**Implemented:** `--lrat-trim` on `tools/color-resolved-wallcc/wallcc.py`, with the
implementation in `native_leaf.py`, `campaign.py`, and `lrat_optin.py`.

This is an explicit experimental proof format, not a new default engine,
encoding, closure claim or production-ledger format. Ordinary DRAT remains the
default and its code path and cached budget are unchanged.

## What it does

With `--engine native`, `native_leaf` records the exact hash of the CNF the
solver reads and writes binary LRAT. `lrat_optin` rejects leaf LRAT unless it
checks against **those exact bytes** with the caller's checker and, optionally,
its declared SHA-256.

A leaf's local UNSAT does not prove all of `parent+cube`: `working.cnf` can
contain appended CAS cuts. `campaign.execute` therefore establishes once per
run that every appended cut is derivable from the parent:

1. independently replay `cas.drat` plus the flag selection proof in forward
   RUP-only mode;
2. bind its exact formula/trace hashes into the leaf's cached budget;
3. replay the local leaf against its own bytes with the caller's `lrat-trim`;
4. replay each stored `leaf.lrat` again in `verify`, with full binary LRAT
   structure parsing, including a derived empty final addition and no forward
   reference IDs.

The verifier binds the checker identity and the cut-derivation receipt, so an
old leaf cannot be reused under a different checker or premise. If the checker
is missing, wrong, changed, or returns anything other than a full verified
refutation, the run fails closed. `--lrat-trim` on the PySAT arm is refused.
`--lrat-trim-sha256` requires `--lrat-trim`.

The `verify` result distinguishes leaf status from tree status. The 357-cut test
has `CHECKED_UNSAT` at r11 and `OPEN` at r00/r01/r10. Its overall exit is 2 =
OPEN; it is not a tree closure.

## Independent checks run by the coordinator

- **24/24 acceptance tests passed**, 22.3 s wall, including H8, the 357-cut
  case, corrupt/truncated proof rejection, forged/missing CAS premise
  rejection, wrong-query rejection, capped-OPEN handling and cache binding.
- **Default/native regression** (`test_native_leaf.py`) still passes: SAT,
  UNSAT replay, corrupt-proof rejection, bounded OPEN, invalid policies,
  resumes, cache binding and unchanged PySAT defaults.
- A regenerated patch has the same bytes as the accepted candidate and as the
  integrated source (`native_leaf.py` 48b08bc39a…, `campaign.py` 47b521be70…,
  `wallcc.py` 83792b3c4a…, `lrat_optin.py` 83b9f29d1d…).

The runner in `tests/run_tests.py` reproduces all 24 cases from a copy of the
current sources, in `.scratch/lrat-optin-integrated-tests`. It never edits a
production run directory. It uses the already supplied binary and local
python-sat packages; no package is installed and no checker is downloaded.
Large formulas and proofs are never committed. The raw acceptance output is
`optin-tests.json`.

## Cost: benefit boundary, not a blanket speedup

Coordinator replay on the already-closed H8 case:

| item | incumbent DRAT | native LRAT |
|---|---:|---:|
| checker process CPU | 0.899 s (`drat-trim -i`) | **0.079 s** (`lrat-trim`) |
| checker max RSS | 86,228 KiB | **44,112 KiB** |
| stored proof | 9,529,642 B | **14,594,230 B** |
| leaf process CPU | 2.748 s | 2.460 s |
| leaf max RSS | 86,228 KiB | **156,036 KiB** |

Both paths give 49,226 conflicts and `s VERIFIED`. The checker is cheaper here,
but the raw LRAT is **53% larger** and leaf memory is higher. A whole-artifact
binary structure parse on `verify` additionally cost **1.332 s** in this case.
The leaf timing difference is not proof of a search-speed difference: the
search counters are identical. Neither checker is formally verified. Do not
extrapolate these numbers to storage, RAM use, other formulas or wall rows.

If retained bytes matter, use the standalone adapter
`tools/lrat_pipeline/native_solve.py`, which keeps a **strictly replayed
trimmed** proof. Trim size is instance-dependent and cannot be assumed to be
smaller. Do not delete LRAT deletion IDs to make a file smaller: that can
invalidate the proof.

## Typical call

Always use a fresh run directory (or a fresh copy). The option changes accepted
artifact and cached-budget types.

```sh
export LRAT_TRIM=/absolute/path/to/reviewed/lrat-trim
export LRAT_TRIM_SHA=f1eb1a4486274c35f4accf7bc13b595cfdbcf2d7c9aa6b46fb281f19d0d52895
PY=/path/to/pinned/python-sat-1.9.dev22/python
"$PY" tools/color-resolved-wallcc/wallcc.py resume "$RUN" \
  --engine native --proof eager --conflicts 50000 --seconds 45 \
  --lrat-trim "$LRAT_TRIM" --lrat-trim-sha256 "$LRAT_TRIM_SHA"
"$PY" tools/color-resolved-wallcc/wallcc.py verify "$RUN" \
  --lrat-trim "$LRAT_TRIM" --lrat-trim-sha256 "$LRAT_TRIM_SHA"
```

Caller-supplied binary identity is locally verified; `--lrat-trim-sha256`
optionally pins it explicitly. The checker and native CaDiCaL must already
exist. No fallback upgrades a failed check. Both checker implementations used
in the broader experiment are unverified programs; no Lean/kernel-checked
certificate is claimed.

## Production boundary

This patch **does not update `finalise`** or claim a release composed of LRAT
leaves. Use the existing DRAT route for current automatic release collection.
A mixed-mode release must not feed `leaf.lrat` to a DRAT-only export or
finalisation step. The optional branch is for exact local C&C and independent
replay, not a way to relabel a timeout or cap as a refutation.

No wall profile, `ChainReady`, or accepted Ramsey interval is changed.
