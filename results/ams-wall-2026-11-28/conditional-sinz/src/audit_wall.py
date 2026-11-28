#!/usr/bin/env python3
"""Independent clause/projection audit of the exact retained-wall Sinz A/B."""
import hashlib
import itertools
import json
import random
from pathlib import Path

from pysat.solvers import Minisat22
from guarded_counter import bcp

M = Path(__file__).resolve().parent.parent
R = M / "results"
PARENT_SHA = "90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae"
ROW = "06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06"
NV = 19533
NC = 184335


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse(path):
    raw = path.read_bytes()
    first, body = raw.split(b"\n", 1)
    fields = first.split()
    assert fields[:2] == [b"p", b"cnf"] and len(fields) == 4
    clauses = [list(map(int, line.split()[:-1])) for line in body.splitlines() if line]
    assert len(clauses) == int(fields[3])
    assert all(line.split()[-1:] == [b"0"] for line in body.splitlines() if line)
    assert max(abs(x) for c in clauses for x in c) <= int(fields[2])
    return raw, first, body, clauses


def masks(n, k):
    """Exhaust small inputs; use deterministic boundary/random controls above 8."""
    if n <= 8:
        return list(itertools.product((False, True), repeat=n))
    out = {tuple(False for _ in range(n)), tuple(True for _ in range(n))}
    for t in range(n + 1):
        out.add(tuple(i < t for i in range(n)))
        out.add(tuple(i >= n - t for i in range(n)))
    out.add(tuple(i % 2 == 0 for i in range(n)))
    out.add(tuple(i % 2 == 1 for i in range(n)))
    rng = random.Random(861 + 31 * n + k)
    for _ in range(8):
        out.add(tuple(bool(rng.getrandbits(1)) for _ in range(n)))
    return sorted(out)


def main():
    parent_raw, _, parent_body, parent = parse(M / "inputs" / "parent.cnf")
    assert sha(parent_raw) == PARENT_SHA and len(parent) == NC
    rawn, hn, bodyn, cn = parse(R / "wall-two5-naive.cnf")
    rawb, hb, bodyb, cb = parse(R / "wall-two5-boundary.cnf")
    mn = json.loads((R / "wall-two5-naive.json").read_text())
    mb = json.loads((R / "wall-two5-boundary.json").read_text())
    assert mn["id"] == mb["id"] == ROW
    assert mn["original_sha256"] == mb["original_sha256"] == PARENT_SHA
    assert sha(rawn) == mn["augmented_sha256"]
    assert sha(rawb) == mb["augmented_sha256"]
    assert bodyn.startswith(parent_body) and bodyb.startswith(parent_body)
    assert cn[:NC] == cb[:NC] == parent
    addedn, addedb = cn[NC:], cb[NC:]
    assert len(addedn) == len(addedb) == mn["added_clauses"] == mb["added_clauses"]
    assert len(addedn) == 4916
    comparable = lambda m: [{k: v for k, v in s.items() if k != "first"}
                            for s in m["specifications"]]
    assert comparable(mn) == comparable(mb)
    specs = mn["specifications"]
    offsets = []
    at = 0
    for spec in specs:
        offsets.append(at)
        at += spec["clauses"]
    assert at == len(addedn)

    check = {
        "row": ROW,
        "parent_sha256": PARENT_SHA,
        "naive_sha256": sha(rawn),
        "boundary_sha256": sha(rawb),
        "parent_body_preserved": True,
        "counter_gadgets": 0,
        "selector_clauses": 0,
        "exhaustive_gadgets": 0,
        "sat_assignment_checks": 0,
        "violating_gadget_assignments": 0,
        "boundary_backprop": 0,
        "naive_backprop": 0,
        "unsound_projection_results": 0,
        "recurrence_clauses_unguarded": 0,
        "per_clause_mismatches": 0,
    }
    for spec, off in zip(specs, offsets):
        count = spec["clauses"]
        sn = addedn[off:off + count]
        sb = addedb[off:off + count]
        if "selector_clause" in spec:
            assert sn == sb == [spec["selector_clause"]]
            check["selector_clauses"] += 1
            continue
        check["counter_gadgets"] += 1
        guard = spec["guard"]
        assert len(sn) == len(sb)
        # PySAT's naive clause order is not the recurrence-then-bound order of
        # split_atleast. Compare multisets, removing unchanged clauses first.
        from collections import Counter
        cntn = Counter(map(tuple, sn))
        cntb = Counter(map(tuple, sb))
        common = cntn & cntb
        resn = cntn - common
        resb = cntb - common
        expected_n = Counter()
        for clause, multiplicity in resb.items():
            expected_n[tuple([-guard] + list(clause))] += multiplicity
        assert resn == expected_n, (spec, resn, resb)
        shortened = sum(resb.values())
        check["recurrence_clauses_unguarded"] += shortened
        variables_n = {abs(x) for c in sn for x in c}
        variables_b = {abs(x) for c in sb for x in c}
        assert variables_n == variables_b
        physical = sorted(v for v in variables_n if v <= NV)
        assert len(physical) == spec["optional"], (spec, len(physical))
        assert guard not in physical
        auxiliary = variables_n - set(physical) - {guard}
        assert not auxiliary or min(auxiliary) > NV
        assert max((abs(x) for c in sn + sb for x in c), default=0) <= 22362
        bits = masks(len(physical), spec["need"])
        check["exhaustive_gadgets"] += len(physical) <= 8
        with Minisat22(bootstrap_with=sn) as satn, Minisat22(bootstrap_with=sb) as satb:
            for values in bits:
                expected_count = sum(values)
                assumptions = [x if bit else -x for x, bit in zip(physical, values)]
                for gv in (False, True):
                    ass = assumptions + [guard if gv else -guard]
                    expected = (not gv) or expected_count >= spec["need"]
                    an, ab = satn.solve(assumptions=ass), satb.solve(assumptions=ass)
                    if not (an == ab == expected):
                        check["unsound_projection_results"] += 1
                    assert an == ab == expected, (spec, values, gv, an, ab)
                    check["sat_assignment_checks"] += 1
                if expected_count < spec["need"]:
                    initial = dict(zip(physical, values))
                    conflict_n, got_n = bcp(sn, initial)
                    conflict_b, got_b = bcp(sb, initial)
                    assert not conflict_n and not conflict_b
                    check["violating_gadget_assignments"] += 1
                    check["naive_backprop"] += got_n.get(guard) is False
                    check["boundary_backprop"] += got_b.get(guard) is False
    assert check["counter_gadgets"] == 93
    assert check["selector_clauses"] == 93
    assert check["boundary_backprop"] == check["violating_gadget_assignments"]
    assert check["unsound_projection_results"] == 0
    litn = sum(map(len, addedn))
    litb = sum(map(len, addedb))
    assert litn - litb == check["recurrence_clauses_unguarded"]
    check["added_literals"] = {"naive": litn, "boundary": litb,
                               "removed_guard_occurrences": litn - litb}
    check["naive_backprop_rate"] = (check["naive_backprop"] /
                                    check["violating_gadget_assignments"])
    check["boundary_backprop_rate"] = 1.0
    (R / "audit.json").write_text(json.dumps(check, indent=2, sort_keys=True) + "\n")
    print(json.dumps(check, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
