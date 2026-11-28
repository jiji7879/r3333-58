# Optional native CaDiCaL engine

The existing default remains **CaDiCaL 1.9.5 through `python-sat 1.9.dev22`**. Nothing about the cube tree, parent formulas, or cover policy changes when `--engine native` is absent.

Use the bundled native CaDiCaL 2.1.2 executable explicitly:

```sh
./k58.sh color-wallcc run --cnf INPUT.cnf --out OUTPUT --tier first --cas off --depth 0 \
  --engine native --native-policy default \
  --conflicts 50000 --seconds 30 --jobs 1 --proof eager
```

`--native-policy default` uses the solver's normal preprocessing. `--native-policy search-only` additionally passes exactly:

```text
--elim=false --probe=false --vivify=false --subsume=false --ternary=false
--block=false --stabilize=false
```

These are alternatives, not a universally better policy. In an earlier direct parent experiment, search-only did 1.65× as many conflicts in the same 120-second budget without settling the parent. Conflicts are not a policy-invariant unit of work. In an independent matched 150,000-conflict comparison on two parents, native default was in the same range as the PySAT incumbent, while search-only used about half the wall time but made substantially different searches. This is a two-instance observation, not a closure or speed guarantee.

In the integrated $H=8$-child smoke, native default completed at **49,226 conflicts** with `VERIFIED_UNSAT` and a valid compact full-child DRAT; with the same child and cap, search-only remained OPEN at 50,000 conflicts. Thus policy is problem-dependent.

## Receipt and completion discipline

* The **binary's SHA-256**, `native`, and `native_policy` are in each native leaf's `budget`. Changing any of them invalidates the cached budget and re-runs the leaf. Default non-native budgets keep their original shape.
* The executable is pinned by hash, not merely by version string:
  `a4a6dc61458f4fbb86cd4084e0249b0e93aae239816d58c3fb707a0a0bc7e48b`.
* `native_leaf.py` is also on the unified runner's tracked-source digest list.
* Seconds and conflicts remain mandatory positive finite caps. Wall timeout is distinct from conflict exhaustion: native CaDiCaL gets its own slightly shorter `-t` cap, with the subprocess deadline as a backstop. This preserves its literal `c UNKNOWN` marker, exit code and conflict statistics on a wall stop. A SAT result still requires the ordinary full-parent model check; an UNSAT result still requires its replayed DRAT.
* Changing native engine, policy or binary forces a fresh solve even after a terminal result; unchanged PySAT receipt reuse is untouched. Receipts retain the native policy, literal status line and solver exit code.
* `COVER_READY` is not the final certificate. Require an explicit `verify` returning `VERIFIED_UNSAT`, then `export-drat` where whole-parent coverage is desired. Statuses never infer a missing satisfying assignment or another row's verdict.
* The replay wrapper now also accounts for the complete proof file. A valid prefix followed by extra bytes must not count as a valid complete DRAT: `check_trace` compares the checker's reported read byte count with the exact file length and returns failure on mismatch.

The raw checker may emit unit-deletion warnings. They are retained in logs; `check_trace` rejects caller-supplied `-w` and `-W`, because warning suppression can change parsing and verdict behaviour. Normalisation is a separate, explicit step when required. RAT and extension-variable steps have their proper proof-system meaning.

For a completed strength-enhanced parent's proof, the input hash identifies the strengthened CNF, not an unrestricted row or Ramsey closure. Resolution/discharge and original-parent composition are separate obligations.

Run the opt-in checks with the pinned environment:

```sh
.scratch/k58/.venv/bin/python tools/color-resolved-wallcc/test_native_leaf.py
.scratch/k58/.venv/bin/python tools/color-resolved-wallcc/selftest.py
.scratch/k58/.venv/bin/python tools/color-resolved-wallcc/leafcert_selftest.py
```
