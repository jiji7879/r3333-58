#!/usr/bin/env python3
"""Independent Minisat22 conformance check for the small BCP implementation."""
import json
from pathlib import Path
from pysat.solvers import Minisat22
from guarded_counter import conditional_atleast, partial_assignments

out = {"cases": 0, "mismatches": [], "scope": "all partial guard/input assignments, n=2..5, every nontrivial bound, both styles"}
for n in range(2, 6):
    for k in range(1, n + 1):
        for style in ("naive", "boundary"):
            clauses, top = conditional_atleast(range(1, n + 1), k, n + 1, n + 1, style)
            from guarded_counter import bcp
            with Minisat22(bootstrap_with=clauses) as solver:
                for partial in partial_assignments(n):
                    conflict, expected = bcp(clauses, partial)
                    status, literals = solver.propagate(
                        assumptions=[v if bit else -v for v, bit in partial.items()])
                    got = dict(partial)
                    if status:
                        for lit in literals:
                            got[abs(lit)] = lit > 0
                    variables = set(range(1, top + 1))
                    mismatch = (status == conflict or
                                (status and any(got.get(v) != expected.get(v)
                                                for v in variables if v in expected or v in got)))
                    if mismatch and len(out["mismatches"]) < 10:
                        out["mismatches"].append({"n": n, "k": k, "style": style,
                                                  "partial": partial, "expected": expected,
                                                  "solver_status": status, "solver_literals": literals})
                    out["cases"] += 1
path = Path(__file__).with_name("propagation-conformance.json")
path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print(json.dumps(out, indent=2, sort_keys=True))
assert not out["mismatches"]
