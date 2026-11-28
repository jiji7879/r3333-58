#!/usr/bin/env python3
"""Isolate Sinz guard removal from the legacy-versus-split clause-order change."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from pysat.solvers import Minisat22
from audit_wall import parse, masks, sha, NV, NC, PARENT_SHA, ROW

M = Path(__file__).resolve().parent.parent
R = M / "results"


def main():
    names = ("naive", "naive-split", "boundary")
    parsed = {name: parse(R / f"wall-two5-{name}.cnf") for name in names}
    meta = {name: json.loads((R / f"wall-two5-{name}.json").read_text()) for name in names}
    parent_raw, _, parent_body, parent = parse(M / "inputs" / "parent.cnf")
    assert sha(parent_raw) == PARENT_SHA
    added = {}
    for name in names:
        raw, _, body, clauses = parsed[name]
        assert sha(raw) == meta[name]["augmented_sha256"]
        assert body.startswith(parent_body)
        assert clauses[:NC] == parent
        added[name] = clauses[NC:]
        assert len(added[name]) == 4916
    specs = meta["naive"]["specifications"]
    comparable = lambda name: [{k: v for k, v in s.items() if k != "first"}
                               for s in meta[name]["specifications"]]
    assert comparable("naive") == comparable("naive-split") == comparable("boundary")
    offsets, at = [], 0
    for spec in specs:
        offsets.append(at)
        at += spec["clauses"]
    assert at == 4916
    check = {"row": ROW, "parent_sha256": PARENT_SHA,
             "sha256": {name: sha(parsed[name][0]) for name in names},
             "legacy_vs_split_clause_multiset_mismatches": 0,
             "split_vs_boundary_positional_mismatches": 0,
             "recurrence_guards_removed": 0,
             "counter_gadgets": 0, "selector_clauses": 0,
             "split_projection_assignment_checks": 0,
             "unsound_split_projection_results": 0}
    for spec, off in zip(specs, offsets):
        size = spec["clauses"]
        forms = {name: added[name][off:off + size] for name in names}
        if "selector_clause" in spec:
            assert all(forms[name] == [spec["selector_clause"]] for name in names)
            check["selector_clauses"] += 1
            continue
        check["counter_gadgets"] += 1
        if Counter(map(tuple, forms["naive"])) != Counter(map(tuple, forms["naive-split"])):
            check["legacy_vs_split_clause_multiset_mismatches"] += 1
        assert Counter(map(tuple, forms["naive"])) == Counter(map(tuple, forms["naive-split"]))
        guard = spec["guard"]
        shortened = 0
        for a, b in zip(forms["naive-split"], forms["boundary"]):
            if a == b:
                continue
            if a != [-guard] + b:
                check["split_vs_boundary_positional_mismatches"] += 1
            assert a == [-guard] + b, (spec, a, b)
            shortened += 1
        check["recurrence_guards_removed"] += shortened
        variables = {abs(x) for c in forms["naive-split"] for x in c if abs(x) <= NV}
        physical = sorted(variables)
        bits = masks(len(physical), spec["need"])
        with Minisat22(bootstrap_with=forms["naive-split"]) as sat:
            for values in bits:
                assumptions = [x if bit else -x for x, bit in zip(physical, values)]
                for gv in (False, True):
                    ass = assumptions + [guard if gv else -guard]
                    expected = (not gv) or sum(values) >= spec["need"]
                    got = sat.solve(assumptions=ass)
                    check["unsound_split_projection_results"] += got != expected
                    assert got == expected, (spec, values, gv, got)
                    check["split_projection_assignment_checks"] += 1
    assert check["counter_gadgets"] == check["selector_clauses"] == 93
    assert check["legacy_vs_split_clause_multiset_mismatches"] == 0
    assert check["split_vs_boundary_positional_mismatches"] == 0
    assert check["unsound_split_projection_results"] == 0
    audit = json.loads((R / "audit.json").read_text())
    assert check["recurrence_guards_removed"] == audit["recurrence_clauses_unguarded"] == 4560
    (R / "audit-order.json").write_text(json.dumps(check, indent=2, sort_keys=True) + "\n")
    print(json.dumps(check, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
