#!/usr/bin/env python3
"""Append one colour of Duggan MCF above an exact K_n DIMACS parent.

Also report a conservative static audit using only physical one-hot and
triangle unit propagation. This is not a satisfiability or closure result.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from mcf_pilot import edge_list, mcf_cnf, read_dimacs


def dsha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parent", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--colour", type=int, required=True, choices=range(4))
    ap.add_argument("--pinned-only", action="store_true",
                    help="keep only unresolved fixed non-c obligations (a partial MCF)")
    args = ap.parse_args()
    raw = args.parent.read_bytes()
    lines = raw.splitlines(keepends=True)
    header = lines[0].split()
    assert header[:2] == [b"p", b"cnf"] and len(header) == 4
    nv, nc = map(int, header[2:])
    clauses = read_dimacs(args.parent)
    assert len(clauses) == nc and len(lines) == nc+1 and raw.endswith(b"\n")
    es = edge_list(args.n)
    physical = 4*len(es)
    def lit(u, v, c):
        if u > v:
            u, v = v, u
        return 4*es.index((u, v))+c+1

    # Conservative physical-only unit closure, seeded by real parent units.
    assigned = {}
    def put(literal):
        var, value = abs(literal), literal > 0
        if var > physical:
            return True
        if var in assigned:
            return assigned[var] == value
        assigned[var] = value
        return True
    for cl in clauses:
        if len(cl) == 1:
            assert put(cl[0]), "physical contradiction in parent units"
    propagation_rounds = 0
    changed = True
    while changed:
        propagation_rounds += 1
        before = len(assigned)
        for q in range(len(es)):
            opts = [4*q+c+1 for c in range(4)]
            if any(assigned.get(x) is True for x in opts):
                for x in opts:
                    if assigned.get(x) is not True:
                        assert put(-x)
            false = [x for x in opts if assigned.get(x) is False]
            if len(false) == 3:
                assert put(next(x for x in opts if assigned.get(x) is not False))
            assert len(false) < 4
        for i, j, k in itertools.combinations(range(args.n), 3):
            for c in range(4):
                tri = [lit(i, j, c), lit(i, k, c), lit(j, k, c)]
                true = [x for x in tri if assigned.get(x) is True]
                if len(true) == 2:
                    assert put(-next(x for x in tri if assigned.get(x) is not True))
                assert len(true) < 3
        changed = len(assigned) > before
        assert propagation_rounds <= physical+1

    c = args.colour
    static = {"physical_variables": physical,
              "physically_assigned_literals_after_limited_BCP": len(assigned),
              "physical_BCP_rounds": propagation_rounds,
              "fixed_c_edges": 0, "fixed_non_c_obligations": 0,
              "forced_witness_present": 0, "no_witness_possible": 0,
              "unresolved_pinned_obligations": 0, "edge_colour_unassigned": 0}
    requirements = {}
    for u, v in es:
        e = lit(u, v, c)
        if e not in assigned:
            static["edge_colour_unassigned"] += 1
            continue
        if assigned[e]:
            static["fixed_c_edges"] += 1
            continue
        static["fixed_non_c_obligations"] += 1
        possible, witnessed = 0, 0
        for w in range(args.n):
            if w in (u, v):
                continue
            a, b = lit(u, w, c), lit(v, w, c)
            if assigned.get(a) is True and assigned.get(b) is True:
                witnessed += 1
            if assigned.get(a) is not False and assigned.get(b) is not False:
                possible += 1
        if witnessed:
            static["forced_witness_present"] += 1
        else:
            # For partial MCF retain every third vertex here, even one already
            # proved impossible; this avoids any semantic simplification claim.
            requirements[u, v] = [w for w in range(args.n) if w not in (u, v)]
            if possible == 0:
                static["no_witness_possible"] += 1
            else:
                static["unresolved_pinned_obligations"] += 1

    if not args.pinned_only:
        top, extra = mcf_cnf(args.n, c, nv)
    else:
        # Partial MCF: only unresolved pinned non-c edges. Full MCF implies
        # every emitted obligation, but the converse and degree lemma fail.
        top = nv
        extra = []
        for (u, v), ws in requirements.items():
            ys = []
            for w in ws:
                top += 1
                y = top
                ys.append(y)
                a, b = lit(u, w, c), lit(v, w, c)
                extra.extend(([-y, a], [-y, b], [-a, -b, y]))
            extra.append([lit(u, v, c)]+ys)
    extra_blob = "".join(" ".join(map(str, cl))+" 0\n" for cl in extra).encode()
    result = f"p cnf {top} {nc+len(extra)}\n".encode()+b"".join(lines[1:])+extra_blob
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(result)
    assert result.split(b"\n", 1)[1].startswith(b"".join(lines[1:]))
    rec = {"parent": str(args.parent), "parent_sha256": dsha(raw),
           "output": str(args.output), "output_sha256": dsha(result),
           "parent_variables": nv, "parent_clauses": nc,
           "mcf_colour": c, "order": args.n, "pinned_only": args.pinned_only,
           "mcf_scope": ("partial_unresolved_pinned_obligations" if args.pinned_only
                         else "full_single_colour_MCF"),
           "retained_obligations": len(requirements) if args.pinned_only else len(es),
           "fresh_auxiliary_variables": top-nv, "output_variables": top,
           "extra_clauses": len(extra), "output_clauses": nc+len(extra),
           "static_physical_only_not_a_verdict": static}
    args.output.with_suffix(".json").write_text(json.dumps(rec, indent=2)+"\n")
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
