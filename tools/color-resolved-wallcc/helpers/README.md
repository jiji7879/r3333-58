# Proof helpers

`strip_binary_drat.py` handles the native **binary DRAT** deletion commands used
by CaDiCaL or Kissat. It completely parses the input, drops only `d` commands,
keeps every `a` addition byte exactly, and requires a single empty addition.
Its JSON receipt binds the input/output bytes and hashes and records all command
and literal counts. It does not parse ASCII DRAT or a different proof format.

```sh
python3 helpers/strip_binary_drat.py raw.drat clean.drat normalization.json
bin/drat-trim exact.cnf clean.drat -i -W -U
```

Dropping deletion commands is sound for RUP: it retains the additions and keeps
all original clauses active, which can only strengthen unit propagation. It is
not a way to accept a malformed proof, suppress a checker warning, or pretend a
derivation is a refutation. The checker must still return `s VERIFIED` with no
warning. A wrong parent, missing terminal empty addition or an unrelated solver
exit is not closure.

This utility is a verbatim copy of the independently reviewed projection-proof
normalizer. It was exercised on both supplied native engine builds on a tiny
UNSAT control whose raw proof emitted a backward-deletion warning.
