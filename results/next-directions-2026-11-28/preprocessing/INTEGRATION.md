# Integration proposal (not applied)

Coordinator-facing. Nothing in the tree was edited. Two products:

* `prep.py` — writes a reduced CNF + a binary DRAT prefix + a JSON receipt for
  one constant host CNF. Fail-closed: `--expect-sha256` pins the host, internal
  re-checks must all pass (`"verdict": "ok"`), and it exits 3 instead of writing
  a "reduced" formula when the host is already refuted at the root.
* `check_prefix.py` — verifies a prefix against a host with MiniSat 2.2's
  propagation and the exact multiset identity
  `host − deletions + additions = reduced`.

## Why the change is small

`tools/color-resolved-wallcc/campaign.py::replay` already joins
`cas.drat ++ leaf_proof` and checks the join against `parent.cnf` extended with
the cube literals, with `drat-trim -i`. That is exactly the object and the
direction the prefix is designed for: the certificate still belongs to the host
cube formula, so `finalise`, the ledger and the frozen coverage do not change.

The only two facts a leaf needs to record are the extra hashes:

```
leaf_proof = prefix.bdrat ++ leaf.bdrat          # same binary format, one concat
leaf_solver_input_sha256 = sha256(reduced.cnf)   # what the solver actually read
leaf_prefix_sha256       = sha256(prefix.bdrat)
host_cube_sha256         = unchanged from today
```

## Proposed diff against `tools/color-resolved-wallcc/native_leaf.py` (sketch)

```diff
 def solve(parent, temp, cube, args, traced):
     started = monotonic()
     query = parent
     if cube:
         query = temp / "native.cnf"
         extend_dimacs(parent, query, [(lit,) for lit in cube])
+    # opt-in, off by default; never touches the default recipe
+    prefix = None
+    if getattr(args, "preprocess", "off") != "off":
+        reduced = temp / "reduced.cnf"
+        raw = temp / "prefix.bdrat"
+        receipt = temp / "prefix.json"
+        require(subprocess.run([sys.executable, str(PREP), "--cnf", str(query),
+                                "--out", str(reduced), "--proof", str(temp / "prefix.drat"),
+                                "--proof-binary", str(raw),
+                                "--receipt", str(receipt)]).returncode in (0, 3),
+                "preprocessing of the leaf CNF failed")
+        if (json.loads(receipt.read_text()).get("verdict") == "ok"):
+            query, prefix = reduced, raw
     ...
     if traced:
         command.append(str(temp / "leaf.drat"))
+    if traced and prefix is not None:
+        (temp / "leaf-with-prefix.bdrat").write_bytes(
+            prefix.read_bytes() + (temp / "leaf.drat").read_bytes())
+        # the caller stores temp/"leaf-with-prefix.bdrat" as the leaf proof
```

New CLI flag next to `--native-policy`:

```diff
+    cmd.add_argument("--preprocess", choices=("off", "up-closure"), default="off",
+                     help="off preserves today's behaviour; up-closure is opt-in and "
+                          "adds the checkable DRAT prefix to the leaf proof")
```

## Fail-closed conditions a patch must keep

1. `--preprocess` defaults to `off`; no default formula, recipe or threshold
   changes.
2. Refuse the leaf if the receipt verdict is not `ok`, if the host hash differs,
   or if the reduced CNF hash differs from the receipt.
3. A **SAT** leaf from the reduced formula is not a model of the host. The prefix
   records `forced_units` and (if enabled) `pure_assignment`; the model must be
   extended by them and then re-checked by the physical checker before anything
   is recorded. `replay`/`check_model` must keep seeing the host cube formula.
4. The stored proof must be `prefix ++ leaf_proof`, binary, concatenated in that
   order; `check_trace` already forbids `-w`/`-W`, which must stay forbidden.
5. If the checker or the prefix is missing, fall back to today's path — never
   record a proof that has not been checked against the host.
6. Do not delete host unit clauses in a future revision of `prep.py`: `drat-trim`
   ignores unit deletions in backward mode, so the checker silently keeps them
   and a real replay hazard stays hidden (this was found by
   `c WARNING: backward mode ignores deletion of (pseudo) unit clause`).

## Measured cost of adopting it

| | host | reduced |
|---|---|---|
| CNF bytes | 3 493 031 | 2 172 405 |
| clauses / literals | 184 337 / 529 030 | 119 343 / 321 850 |
| parse+bootstrap CPU (per leaf) | 0.0766 s | 0.0496 s |
| RSS | 96 MiB | 84–87 MiB |
| capped-search CPU, 4 seeds | 1.00 | 0.929 geomean (0.719–1.145) |
| prefix size | — | 698 340 B binary |
| prefix check | — | 0.9 s (independent engine) |
| drat-trim replay of the composed proof (H7, closed) | 0.75 s | host proof 0.83 s |

The `--preprocess` switch therefore buys a reproducible −12 % RSS and −35 %
parse/startup CPU per leaf, costs a 0.7 MB prefix and 0.9 s of checking, and
gives no defensible search-CPU win. Recommendation: **do not enable it for
search throughput**; enable it only if leaf RSS or CNF parse time is the binding
constraint, and never without the composition and the model-lift rules above.
