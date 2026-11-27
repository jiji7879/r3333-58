#!/usr/bin/env python3
"""Independent finite guard/support audit of short and wide_delta clauses."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import generate_panel as gp


def additions(path, base_count):
    lines = path.read_bytes().splitlines()
    p, cnf, nv, nc = lines[0].split()
    assert (p, cnf) == (b"p", b"cnf")
    raw_values = [list(map(int, line.split())) for line in lines[1:] if line]
    assert len(raw_values) == int(nc) and all(v[-1] == 0 and 0 not in v[:-1]
                                              for v in raw_values)
    values = [v[:-1] for v in raw_values]
    return values[base_count:]


def all_options(f, row, x, c, edge, groups):
    fixed = {v for v, in gp.probe.units(f, row["placement"])}
    pos = {v for v in fixed if v > 0}
    neg = {-v for v in fixed if v < 0}
    known = {(v - 1) // 4 for v in pos}
    result = {}
    possible = fixed_count = 0
    for b, other in enumerate(groups):
        if b == c:
            continue
        spokes = [edge(x, y, c) for y in other]
        must = {i for i, lit in enumerate(spokes) if lit in pos}
        omit = {i for i, lit in enumerate(spokes)
                if lit in neg or ((lit - 1) // 4 in known and lit not in pos)}
        possible += len(spokes) - len(omit)
        fixed_count += len(must)
        if f.root_kinds[b] != "-":
            opts = tuple(set(p) for p in gp.probe.catalog(
                len(other), f.root_kinds[b], b, c)
                if must.issubset(p) and omit.isdisjoint(p))
            result[b] = (spokes, opts)
    return fixed_count, possible, result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--selection", type=Path, default=Path("selection-v1"))
    p.add_argument("--out", type=Path, default=Path("finite-audit.json"))
    a = p.parse_args()
    assert not a.out.exists()
    summaries = []
    edges = list(itertools.combinations(range(58), 2))
    negative_controls = []
    for rank in (1288, 1162):
        manifest = json.loads((a.selection / str(rank) / "manifest.json").read_text())
        record = gp.probe.rows[rank - 1]
        row = gp.probe.geometry[record["id"]]
        f = gp.probe.Family(**{k: tuple(v) if k in ("profile", "root_kinds") else v
                              for k, v in row["family"].items()})
        guards = {}
        raw, form, direct, extended = gp.probe.build(record, guards)
        assert gp.sha(raw) == record["input_sha256"]
        inverse = {g: (x, c) for x, (c, g) in guards.items()}
        groups = [list(range(1 + sum(f.profile[:i]), 1 + sum(f.profile[:i+1])))
                  for i in range(4)]
        group_of = {x: b for b, group in enumerate(groups) for x in group}
        edge, _ = gp.probe.host(58)
        ternary = gp.one(row, guards)
        four = [[-guards[x][1], *lits] for x, *lits in gp.wider(row)]
        prior = {frozenset(c) for c in gp.unique([list(c) for c in direct] + ternary)}
        expected = {
            "short": {frozenset(c) for c in gp.unique([list(c) for c in direct] + ternary + four)
                      if len(c) <= 4},
            "wide_delta": {frozenset(c) for c in gp.unique(four)
                           if frozenset(c) not in prior},
        }
        actual = {name: {frozenset(c) for c in additions(
            a.selection / str(rank) / (name + ".cnf"), len(form.clauses))}
                  for name in ("short", "wide_delta")}
        assert actual == expected, (rank, "selection mismatch")
        checked = {"short": 0, "wide_delta": 0}
        witnesses = {}
        for policy in ("short", "wide_delta"):
            for clause in sorted(actual[policy], key=lambda c: sorted(c)):
                values = sorted(clause)
                assert len(values) in (3, 4) and values[0] < 0
                assert -values[0] in inverse
                x, c = inverse[-values[0]]
                assert all(v > 0 for v in values[1:])
                targets = {}
                for lit in values[1:]:
                    assert (lit - 1) % 4 == c
                    u, v = edges[(lit - 1) // 4]
                    assert x in (u, v)
                    y = v if x == u else u
                    b = group_of[y]
                    assert b != c and f.root_kinds[b] != "-"
                    targets.setdefault(b, set()).add(y - groups[b][0])
                fixed_count, possible, options = all_options(f, row, x, c, edge, groups)
                assert fixed_count < 14 <= possible
                reasons = []
                if len(values) == 3 and len(targets) == 2:
                    ok = all(len(s) == 1 and next(iter(s)) in set.intersection(*options[b][1])
                             for b, s in targets.items())
                    if ok:
                        reasons.append("two singleton intersections")
                elif len(values) == 4 and len(targets) == 2:
                    for b, s in targets.items():
                        d, t = next((d, t) for d, t in targets.items() if d != b)
                        if len(s) == 1 and len(t) == 2:
                            left = next(iter(s)) in set.intersection(*options[b][1])
                            right = all(s2 & t for s2 in options[d][1])
                            if left and right:
                                reasons.append(f"singleton arm {b}; two-hit arm {d}")
                assert reasons, (rank, policy, values, "no support witness")
                checked[policy] += 1
                if policy == "wide_delta" and not witnesses:
                    # Deterministic guard-broken and support-broken negatives.
                    wrong_guard = [values[0] * -1, *values[1:]]
                    negative_controls.append({"rank": rank, "kind": "guard_sign_flipped",
                        "original": values, "broken": wrong_guard,
                        "rejected_by": "first literal must be the negated exact sender guard"})
                    pair_arm = next(b for b, s in targets.items() if len(s) == 2)
                    other_arm = next(b for b in targets if b != pair_arm)
                    bad_pair = None
                    for pair in itertools.combinations(range(len(groups[pair_arm])), 2):
                        if not any(s & set(pair) for s in options[pair_arm][1]):
                            continue
                        if not all(s & set(pair) for s in options[pair_arm][1]):
                            bad_pair = pair
                            witness = next(sorted(s) for s in options[pair_arm][1]
                                           if not s & set(pair))
                            break
                    assert bad_pair is not None
                    broken_targets = {other_arm: targets[other_arm], pair_arm: set(bad_pair)}
                    negative_controls.append({"rank": rank, "kind": "non_hitting_pair_substituted",
                        "original_targets": {str(b): sorted(s) for b, s in targets.items()},
                        "broken_targets": {str(b): sorted(s) for b, s in broken_targets.items()},
                        "compatible_five_set_avoiding_broken_pair": witness,
                        "rejected_by": "some compatible five-set is not hit by the substituted pair"})
                    witnesses[rank] = True
        summaries.append({"rank": rank, "id": record["id"],
            "input_sha256": record["input_sha256"], "clauses_checked": checked,
            "all_guards_rebound": True, "all_support_witnesses_valid": True,
            "selection_sets_exactly_regenerated": True})
    # The complete finite R(3,3)=6 fact underlying every arm cap.
    edge6 = list(itertools.combinations(range(6), 2))
    triangles = [sum(1 << edge6.index(e) for e in itertools.combinations(t, 2))
                 for t in itertools.combinations(range(6), 3)]
    assert all(any(mask & t in (0, t) for t in triangles) for mask in range(1 << 15))
    # Certified non-UP wide examples are members of both policies on their rows.
    certified = []
    for rank, clause in ((8, [-24663, 1056, 2428, 6024]),
                         (340, [-24652, 3908, 4832, 6028])):
        record = gp.probe.rows[rank - 1]
        guards = {}
        raw, form, direct, extended = gp.probe.build(record, guards)
        assert gp.sha(raw) == record["input_sha256"]
        row = gp.probe.geometry[record["id"]]
        ternary = gp.one(row, guards)
        four = [[-guards[x][1], *lits] for x, *lits in gp.wider(row)]
        prior = {frozenset(c) for c in gp.unique([list(c) for c in direct] + ternary)}
        assert frozenset(clause) in map(frozenset, four)
        assert frozenset(clause) not in prior
        certified.append({"rank": rank, "clause": clause,
                          "in_short": True, "in_wide_delta": True,
                          "previous_direct_and_ternaries_UP": False,
                          "parent_sha256": record["input_sha256"]})
    result = {"schema": "selection-finite-audit/v1", "rows": summaries,
              "binary_K6_colorings_exhaustively_checked": 32768,
              "negative_controls": negative_controls,
              "certified_representatives_waiting_for_replay": certified}
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
