# Independent recomputation (kind: compute)

## Coordinator script

`work/independent_check.py` is standard-library-only. It imports neither the supplied encoder nor the members' audit functions. It reconstructs all 1,653 physical edges, all 30,856 vertex triangles, and all four colour choices/forbidden monochromatic triangles, giving exactly 134,995 distinct physical host clauses as a set. It compares those clauses with every stored parent's initial segment, checks literal ranges, uniqueness, clause counts and unit witnesses, recomputes file hashes, and runs the native checker directly.

It identifies the exact mined $Q$ and $R$ literal sets in `.ultramath/smx04vulj/m3/replay/2c/core-lemmas.drat`, each with a unique occurrence. It then constructs the full-parent false-cube queries independently, using the original parent body and an explicitly incremented header count. No candidate clause is appended as an assumption. Its tiny written proofs are ASCII and checked with forced `-I`, warning-fatal `-W`, RUP-only `-U`, and plain `-p` flags; fresh raw solver streams are separate and binary with RAT enabled. Checker warnings are never suppressed with `-w`.

Final command and output:

```text
$ python3 research/k58-closed-case-mining/work/independent_check.py
{
  "verified_native_full_parent_proofs": 3,
  "verified_q_transfers": 3,
  "verified_pinned_transfers": 3,
  "required_rejections": 3,
  "receipt": ".../research/k58-closed-case-mining/work/receipt.json"
}

exit status 0
```

The receipt binds every source/destination parent, proof, query, check log and control clause. The accepted parent replays all have full input byte counts and `s VERIFIED`; the controls all have exit 1 and `s NOT VERIFIED`. In particular, the `6116d9150` fresh proof hash is independently recomputed as `5defe1b9aecff6a6874f2346e2622fc1e4f35a29fbfd0f030dba4c735cc15d31`, not inferred from its prefix.

The required omitted-host-witness parent was checked by an explicit single-line diff: it has one fewer clause and exactly `-1162 -1230 -4014` for the initial `6116…` role or `-510 -578 -3398` for the final `944f…` role. The final checks use `944f…` for the control because other geometry on `6116…` yields the target independently. The altered-clause control deletes the first positive literal, not a different palette literal, and runs on the original-only physical parent as in the member's claim. Those scopes are recorded in the script and receipt; an accepted dense-parent alteration would not refute the physical-only control.

All 60 nonmonochromatic three-edge colour words were enumerated. The fixed-pin and unpinned formulas were evaluated on three independent parents. The parent-level derivation is native RUP, not a SAT model or `OPEN` inference.

## Independent fork tests (unchanged solver code)

The plain system Python run of `tools/color-resolved-wallcc/selftest.py` failed at import time because it has no `pysat`; this was an invocation error, so the prescribed supplied environment was used instead.

```sh
.scratch/massive-clean-install/k58-solver/.venv/bin/python \
  tools/color-resolved-wallcc/selftest.py
# PASS K5/K6, split assignments, sharding, resume and proof/model controls

.scratch/massive-clean-install/k58-solver/.venv/bin/python \
  tools/color-resolved-wallcc/color_selftest.py \
  --checker tools/color-resolved-wallcc/bin/drat-trim \
  --out research/k58-closed-case-mining/work/color-selftest
# PASS counter (510 assignments), 2,914 physical local words,
# six benchmark derivations and tampering rejection: status PASS
```

These self-tests concern the existing fork and elementary local controls, **not** ordinary-wall completion. No new solver campaign or full parent SAT model was run. No Lean check was claimed: the relevant claim was submitted as native RUP/DRAT certificates, not a Lean statement. Native DRAT includes RAT in the three real case proofs, whereas the physical transfer checks deliberately disable RAT.
