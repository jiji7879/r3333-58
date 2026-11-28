#!/usr/bin/env python3
"""Generator-free exact audit of the retained parent/arm3 leaf queries.

This is an integration-test oracle, not a SAT solver or physical-row proof.
It reconstructs the target CNF bytes directly from the frozen parent and the
DIMACS schema, without importing the MCF implementation under test.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

ROW = "06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06"
PARENT_SHA = "90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae"
EXPECTED_QUERY_SHA = {
    "parent": "8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8",
    "arm3": "fface1b819e26261736cb516be9063e7be2b1be120253875947a4400d4ac912a",
    "arm3-bcp": "ffcaa2f5c37509ba2e4df2c7dcce6d47f859fc9740c7e2ca8b0555cf8a0b6ea4",
}
CUBE = (-1413, 1014)
CUBE_BYTES = b"-1413 0\n1014 0\n"


class AuditError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    """Strictly parse the one-clause-per-line DIMACS used by this package."""
    require(isinstance_raw(raw), "DIMACS input is not bytes")
    lines = raw.splitlines()
    require(lines and lines[0].split()[:2] == [b"p", b"cnf"], "missing p cnf header")
    fields = lines[0].split()
    require(len(fields) == 4, "malformed header")
    try:
        nv, nc = int(fields[2]), int(fields[3])
    except ValueError as exc:
        raise AuditError("nonnumeric header") from exc
    require(nv >= 0 and nc >= 0, "negative header count")
    clauses = []
    for number, line in enumerate(lines[1:], 2):
        require(line and not line.startswith(b"c"), f"comment/empty line {number} not in retained schema")
        tokens = line.split()
        require(tokens and tokens[-1] == b"0", f"unterminated clause line {number}")
        require(tokens.count(b"0") == 1, f"multiple clauses/tokens on line {number}")
        try:
            clause = tuple(int(x) for x in tokens[:-1])
        except ValueError as exc:
            raise AuditError(f"noninteger literal on line {number}") from exc
        require(clause, f"empty clause line {number}")
        require(all(0 < abs(x) <= nv for x in clause), f"out-of-range literal on line {number}")
        clauses.append(clause)
    require(len(clauses) == nc, "header/body clause-count mismatch")
    require(raw.endswith(b"\n"), "missing final newline")
    return nv, clauses


def isinstance_raw(raw):
    return isinstance(raw, bytes)


def lit(u, v, colour=0):
    if u > v:
        u, v = v, u
    edge = u * (116 - u - 1) // 2 + (v - u - 1)
    return 4 * edge + colour + 1


def arm3_suffix(parent_nv, parent):
    # Host(K58, four colours): exactly-one per edge and four triangle blocks.
    host_count = 1653 * 7 + 30856 * 4
    require(host_count == 134995, "internal host-count error")
    forbidden = {abs(x) for clause in parent[host_count:] for x in clause}
    expected_edges = []
    for u, v in itertools.combinations(range(47, 58), 2):
        colors = {lit(u, v, c) for c in range(4)}
        if not colors & forbidden:
            expected_edges.append((u, v))
    require(len(expected_edges) == 45, "safe arm3 edge count is not 45")
    top = parent_nv
    suffix = []
    allocation = []
    for u, v in expected_edges:
        witnesses = []
        for w in range(58):
            if w in (u, v):
                continue
            top += 1
            y = top
            witnesses.append(y)
            left, right = lit(u, w), lit(v, w)
            suffix.extend([(-y, left), (-y, right), (y, -left, -right)])
            allocation.append((y, u, v, w, left, right))
        suffix.append((lit(u, v), *witnesses))
    require(top == 22053 and len(suffix) == 7605 and len(allocation) == 2520,
            "unexpected raw allocation")
    require(len({x[0] for x in allocation}) == 2520, "fresh allocation collision")
    require(all(x[0] > parent_nv for x in allocation), "parent/new-variable collision")
    return suffix, allocation


def encode_clause(clause):
    return (" ".join(map(str, clause)) + " 0\n").encode()


def assemble(parent_raw, output_nv, suffix):
    _, parent = parse(parent_raw)
    parent_body = parent_raw.split(b"\n", 1)[1]
    return f"p cnf {output_nv} {len(parent) + len(suffix) + 2}\n".encode() + parent_body + b"".join(map(encode_clause, suffix)) + CUBE_BYTES


def parent_closure(parent, nv):
    """Independent repeated-complete-scan unit closure (no watched literals)."""
    assignment = {}
    passes = 0
    while True:
        passes += 1
        changed = False
        for clause in parent:
            unknown = []
            satisfied = False
            for literal in clause:
                if abs(literal) not in assignment:
                    unknown.append(literal)
                elif assignment[abs(literal)] == (literal > 0):
                    satisfied = True
                    break
            if satisfied:
                continue
            require(unknown, "parent BCP conflict")
            if len(unknown) == 1:
                literal = unknown[0]
                assignment[abs(literal)] = literal > 0
                changed = True
        if not changed:
            break
        require(passes <= nv + 1, "BCP did not converge")
    require(len(assignment) == 1813, "unexpected parent closure size")
    return assignment, passes


def residual(raw_suffix, assignment):
    kept = []
    for clause in raw_suffix:
        remaining = []
        satisfied = False
        for literal in clause:
            value = assignment.get(abs(literal))
            if value is None:
                remaining.append(literal)
            elif value == (literal > 0):
                satisfied = True
                break
        if not satisfied:
            require(remaining, "empty augmented residual")
            kept.append(tuple(remaining))
    return kept


def construct_expected(parent_raw):
    parent_nv, parent = parse(parent_raw)
    require(sha(parent_raw) == PARENT_SHA, "wrong frozen parent hash")
    require(parent_nv == 19533 and len(parent) == 184335, "wrong frozen parent schema")
    raw_suffix, allocation = arm3_suffix(parent_nv, parent)
    expected = {}
    expected["parent"] = assemble(parent_raw, parent_nv, [])
    expected["arm3"] = assemble(parent_raw, 22053, raw_suffix)
    assignment, passes = parent_closure(parent, parent_nv)
    kept = residual(raw_suffix, assignment)
    require(len(kept) == 7140 and len(raw_suffix) - len(kept) == 465,
            "unexpected BCP residual count")
    used = {abs(x) for clause in kept for x in clause if abs(x) > parent_nv}
    require(len(used) == 2520, "BCP dropped a path witness variable")
    expected["arm3-bcp"] = assemble(parent_raw, 22053, kept)
    return expected, {"parent_bcp_units": len(assignment), "parent_bcp_scan_passes": passes,
                      "safe_edges": 45, "fresh_witnesses": len(allocation),
                      "raw_suffix_clauses": len(raw_suffix), "bcp_residual_suffix_clauses": len(kept)}


def audit(kind, query_raw, expected):
    require(kind in expected, "unknown query kind")
    nv, clauses = parse(query_raw)
    expected_raw = expected[kind]
    # This whole-byte check also binds original body order, header and cube order.
    require(query_raw == expected_raw, f"{kind} bytes differ from independently reconstructed query")
    require(sha(query_raw) == EXPECTED_QUERY_SHA[kind], f"{kind} pinned hash mismatch")
    require(clauses[-2:] == [(-1413,), (1014,)], "wrong cube signs/order")
    require(nv == (19533 if kind == "parent" else 22053), "wrong maximum variable")
    return {"result": "PASS", "kind": kind, "query_sha256": sha(query_raw),
            "variables": nv, "clauses": len(clauses), "cube": list(CUBE),
            "body_and_cube_byte_exact": True,
            "scope": "CNF identity/schema only; no SAT/UNSAT or physical-colouring verdict"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent", type=Path, required=True)
    ap.add_argument("--kind", choices=sorted(EXPECTED_QUERY_SHA))
    ap.add_argument("--query", type=Path)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    parent_raw = args.parent.read_bytes()
    expected, details = construct_expected(parent_raw)
    negative = []
    if args.selftest:
        # Positive controls for all three exact query constructors.
        for kind in EXPECTED_QUERY_SHA:
            audit(kind, expected[kind], expected)
        cases = [
            ("wrong root sign", "parent", expected["parent"].replace(b"-1413 0\n1014 0\n", b"1413 0\n1014 0\n")),
            ("wrong second sign", "parent", expected["parent"].replace(b"-1413 0\n1014 0\n", b"-1413 0\n-1014 0\n")),
            ("malformed header", "parent", expected["parent"].replace(b"p cnf ", b"p inccnf ", 1)),
            ("header clause drift", "arm3", expected["arm3"].replace(b"p cnf 22053 191942", b"p cnf 22053 191941", 1)),
            ("deleted raw suffix clause", "arm3", expected["arm3"].replace(encode_clause(parse(expected["arm3"])[1][-3]), b"", 1)),
            ("new/parent variable collision", "arm3", expected["arm3"].replace(b"-19534 ", b"-19533 ", 1)),
            ("out-of-range auxiliary", "arm3", expected["arm3"].replace(b"-19534 ", b"-22054 ", 1)),
            ("deleted BCP residual", "arm3-bcp", expected["arm3-bcp"].replace(encode_clause(parse(expected["arm3-bcp"])[1][-3]), b"", 1)),
        ]
        for name, kind, mutated in cases:
            require(mutated != expected[kind], f"mutation did not apply: {name}")
            try:
                audit(kind, mutated, expected)
            except AuditError:
                negative.append(name)
            else:
                raise AuditError(f"negative control accepted: {name}")
        require(len(negative) == len(cases), "missing negative control")
        for kind in EXPECTED_QUERY_SHA:
            (args.report.parent / f"selftest-{kind}.cnf").write_bytes(expected[kind])
    elif args.query:
        require(args.kind is not None, "--kind is required with --query")
        actual = audit(args.kind, args.query.read_bytes(), expected)
        details.update(actual)
    else:
        ap.error("supply --query/--kind or --selftest")
    receipt = {"result": "PASS", "row": ROW, "parent_sha256": PARENT_SHA,
               "expected_query_sha256": EXPECTED_QUERY_SHA, "negative_controls_rejected": negative,
               **details,
               "physical_closure_established": False, "augmented_cnf_unsat_established": False}
    args.report.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
