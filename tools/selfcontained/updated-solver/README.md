# Modified self-contained K58 solver

Build **a new archive**, leaving the original `dist/k58-solver.zip` untouched:

```sh
python3 tools/selfcontained/updated-solver/build_updated.py \
  --base dist/k58-solver.zip \
  --square attachments/let-s-try-and-rbdv/K58_square_spoke_wall_test.zip \
  --out dist/k58-updated-solver.zip
```

The square source archive must have SHA-256
`08a1e2e9513ade7dffab4d8ff89fb5f2f5dc04e68d8928ff8cf54cded9093873`.
The build is read-only on the two supplied inputs, checks the complete square
source hash, leaves generated outputs to caller-chosen paths, preserves base
file bytes and executable permissions, records `modified-manifest.json`, and
atomically publishes only a nonempty ZIP whose CRC check passes. A destination
already present is refused; choose a new filename instead of overwriting a
previous candidate.

`MODIFIED_README.md` lists all new commands. In short:

* `square`: strict K15 validation, export, and bounded square-spoke solving on
  the fourteen audited first-tier ordinary-wall parents;
* `color-wallcc`: the separately certified optional physical-colour-pivot wall
  engine;
* `armcap`: historical hard1300 paired-arm, transversal, `two5`, joint-support
  discovery and strict bounded certification;
* `modified-smoke`: new-output, fail-closed combined checks, optionally with
  `--deep` for the independent K15 RUP engine.

`VALIDATION.md` records the complete clean-extraction, offline-setup, modified
and stock smoke results. No original receipt, ledger or timing data is changed
in a build. Source-only files live here; the ZIP stays in the gitignored `dist/`
as a handover archive, not a repository blob. The optional engines do not prove
a wall closure, a new Ramsey bound, or a general solver speedup.
