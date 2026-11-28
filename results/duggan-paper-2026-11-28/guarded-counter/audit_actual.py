#!/usr/bin/env python3
"""Independent checks on the emitted rank-1300 two5 counter gadgets."""
import hashlib
import itertools
import json
import random
from pathlib import Path

from pysat.solvers import Minisat22
from guarded_counter import bcp, conditional_atleast

HERE = Path(__file__).resolve().parent
A = HERE / "actual"
ORIGINAL_VARS = 29942
ORIGINAL_CLAUSES = 211564
ORIGINAL_SHA256 = "56ad3dc529f1b855e65fa3f3f5363e8275930a7cb6ea5b04dc01a112535b0837"
NAIVE_SHA256 = "fe9de879d99b320c57c7d90582842a532a045da9c3d90c8df5880d96498eb9af"


def parse(path):
    raw = Path(path).read_bytes()
    first, body = raw.split(b"\n", 1)
    h = first.split()
    clauses = [list(map(int, line.split()[:-1])) for line in body.splitlines() if line]
    assert len(clauses) == int(h[3])
    assert max(abs(x) for c in clauses for x in c) == int(h[2])
    return raw, first, body, clauses


def masks(n, k):
    """Deterministic tight, violating, satisfying, and asymmetric controls."""
    out = {tuple(False for _ in range(n)), tuple(True for _ in range(n))}
    for t in range(n + 1):
        out.add(tuple(i < t for i in range(n)))
        out.add(tuple(i >= n - t for i in range(n)))
    out.add(tuple(i % 2 == 0 for i in range(n)))
    out.add(tuple(i % 2 == 1 for i in range(n)))
    rng = random.Random(1300 + 31 * n + k)
    for _ in range(4):
        out.add(tuple(bool(rng.getrandbits(1)) for _ in range(n)))
    return sorted(out)


def main():
    raw_n, head_n, body_n, clauses_n = parse(A / "r1300-naive.cnf")
    raw_b, head_b, body_b, clauses_b = parse(A / "r1300-boundary.cnf")
    meta_n = json.loads((A / "r1300-naive.json").read_text())
    meta_b = json.loads((A / "r1300-boundary.json").read_text())
    assert hashlib.sha256(raw_n).hexdigest() == NAIVE_SHA256
    assert meta_n["original_sha256"] == meta_b["original_sha256"] == ORIGINAL_SHA256
    assert meta_n["specifications"] != meta_b["specifications"]  # first clauses differ
    comparable = lambda m: [{k: v for k, v in s.items() if k != "first"}
                            for s in m["specifications"]]
    assert comparable(meta_n) == comparable(meta_b)
    # The complete original byte body is common, untouched, and equal to the
    # independently retained stock input. The naive augmentation also matches
    # the separately retained published artifact byte-for-byte.
    root = HERE.parents[2]
    base_raw = (root / ".scratch/arm-cap-research/rank1300-stock.cnf").read_bytes()
    published_raw = (root / ".scratch/arm-cap-research/m1-reproduced-r1300-two5.cnf").read_bytes()
    assert hashlib.sha256(base_raw).hexdigest() == ORIGINAL_SHA256
    assert raw_n == published_raw
    base_lines = base_raw.splitlines(keepends=True)
    original_lines_n = body_n.splitlines(keepends=True)[:ORIGINAL_CLAUSES]
    original_lines_b = body_b.splitlines(keepends=True)[:ORIGINAL_CLAUSES]
    assert original_lines_n == original_lines_b == base_lines[1:]
    added_n = clauses_n[ORIGINAL_CLAUSES:]
    added_b = clauses_b[ORIGINAL_CLAUSES:]

    # Block-starts recorded by the original spec stream, including pair clauses.
    specs = meta_n["specifications"]
    offsets = []
    at = 0
    for spec in specs:
        offsets.append(at)
        at += spec["clauses"]
    assert at == len(added_n) == len(added_b) == 8533

    check = {"counter_gadgets": 0, "selector_clauses": 0,
             "sat_assignment_checks": 0, "boundary_backprop": 0,
             "naive_backprop": 0, "violating_gadget_assignments": 0,
             "aux_collision_failures": 0, "base_body_preserved": True,
             "naive_full_sha256": hashlib.sha256(raw_n).hexdigest(),
             "boundary_full_sha256": hashlib.sha256(raw_b).hexdigest()}
    literal_n = sum(map(len, added_n))
    literal_b = sum(map(len, added_b))
    check["added_literals"] = {"naive": literal_n, "boundary": literal_b,
                               "removed_guard_occurrences": literal_n - literal_b}

    for spec, off in zip(specs, offsets):
        count = spec["clauses"]
        cn = added_n[off:off + count]
        cb = added_b[off:off + count]
        if "selector_clause" in spec:
            assert cn == cb == [spec["selector_clause"]]
            check["selector_clauses"] += 1
            continue
        check["counter_gadgets"] += 1
        guard = spec["guard"]
        variables_n = {abs(x) for c in cn for x in c}
        variables_b = {abs(x) for c in cb for x in c}
        assert variables_n == variables_b
        physical = sorted(v for v in variables_n if v <= ORIGINAL_VARS)
        assert len(physical) == spec["optional"], (spec, len(physical))
        assert guard not in physical and guard > ORIGINAL_VARS
        # All auxiliary variables stay above the original parent and no gadget
        # may borrow the other encoding's variables.
        auxiliary = variables_n - set(physical) - {guard}
        if auxiliary:
            assert min(auxiliary) > ORIGINAL_VARS
        else:
            assert spec["need"] == 1  # PySAT's direct one-wide OR has no auxiliaries.
        bits = masks(len(physical), spec["need"])
        with Minisat22(bootstrap_with=cn) as sn, Minisat22(bootstrap_with=cb) as sb:
            for values in bits:
                expected_count = sum(values)
                assumptions = [x if bit else -x for x, bit in zip(physical, values)]
                for gv in (False, True):
                    ass = assumptions + [guard if gv else -guard]
                    expected = (not gv) or expected_count >= spec["need"]
                    an, ab = sn.solve(assumptions=ass), sb.solve(assumptions=ass)
                    assert an == ab == expected, (spec, values, gv, an, ab)
                    check["sat_assignment_checks"] += 1
                # With q/g unassigned, a complete violating support assignment
                # must refute its selector/guard by BCP in the boundary form.
                if expected_count < spec["need"]:
                    initial = dict(zip(physical, values))
                    conflict_n, got_n = bcp(cn, initial)
                    conflict_b, got_b = bcp(cb, initial)
                    assert not conflict_n and not conflict_b
                    check["violating_gadget_assignments"] += 1
                    check["naive_backprop"] += (got_n.get(guard) is False)
                    check["boundary_backprop"] += (got_b.get(guard) is False)
    assert check["counter_gadgets"] == 168
    assert check["selector_clauses"] == 168
    assert check["boundary_backprop"] == check["violating_gadget_assignments"]

    # The crucial two5 composition: no arm can supply five, so each selector q
    # is false. The three pair clauses then refute the original guard g.
    # Prefixing every recurrence clause loses this entire chain under UP.
    physical = list(range(1, 19))  # three disjoint groups of six
    qs = [19, 20, 21]
    guard = 22
    composition = {}
    for style in ("naive", "boundary"):
        top = guard
        clauses = [[-guard, qs[i], qs[j]] for i, j in itertools.combinations(range(3), 2)]
        for arm, q in enumerate(qs):
            c, top = conditional_atleast(physical[6 * arm:6 * arm + 6], 5, q, top, style)
            clauses.extend(c)
        conflict, got = bcp(clauses, {x: False for x in physical})
        composition[style] = {"conflict": conflict, "not_guard_derived": got.get(guard) is False,
                              "selectors_derived_false": all(got.get(q) is False for q in qs)}
        assert not conflict
    assert composition["boundary"]["not_guard_derived"]
    assert not composition["naive"]["not_guard_derived"]
    check["two5_all_empty_composition"] = composition

    # Literal saving comes only from recurrence clauses, not deleted semantics.
    assert literal_n - literal_b == 7913
    out = HERE / "actual" / "audit.json"
    out.write_text(json.dumps(check, indent=2, sort_keys=True) + "\n")
    print(json.dumps(check, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
