#!/usr/bin/env python3
"""Small, independent semantics/RUP controls for K58_square_six.

This does not import or execute the package's Python modules and does no SAT search.
It reads one archived parent only to decode the documented square example.  It
constructs K4 toys itself and invokes drat-trim in strict binary RUP-only mode.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import subprocess

PARENT_SHA = "33b7898ed58bd1a3a2e088f57d4bc9d01b5397e7b72f1f5f1449a7bf16f4a02a"
N = 4
RED, BLUE = 0, 1
OTHER = (2, 3)
U, A, B, X = 0, 1, 2, 3
EDGES4 = {e: i for i, e in enumerate(itertools.combinations(range(N), 2))}


def var4(i: int, j: int, color: int) -> int:
    return 1 + 4 * EDGES4[tuple(sorted((i, j)))] + color


def base_formula(ub_color: int = RED) -> list[list[int]]:
    """Exactly one of four colors per K4 edge, no monochromatic triangle."""
    clauses: list[list[int]] = []
    for i, j in EDGES4:
        vs = [var4(i, j, c) for c in range(4)]
        clauses.append(vs)                         # at least one color
        clauses.extend([[-p, -q] for p, q in itertools.combinations(vs, 2)])
    for tri in itertools.combinations(range(N), 3):
        es = list(itertools.combinations(tri, 2))
        for c in range(4):
            clauses.append([-var4(i, j, c) for i, j in es])
    clauses.extend(([var4(U, A, RED)], [var4(U, B, ub_color)],
                    [var4(A, B, BLUE)]))
    return clauses


def short_clause() -> list[int]:
    return ([-var4(X, U, RED)]
            + [var4(X, w, c) for w in (A, B) for c in OTHER])


def with_violation_selector(base: list[list[int]], goal: list[int],
                            selector: int = 25) -> list[list[int]]:
    # selector = true falsifies every goal literal through the binary clauses.
    return base + [[selector]] + [[-selector, -lit] for lit in goal]


def encode_lit(lit: int) -> bytes:
    value = 2 * lit if lit >= 0 else -2 * lit + 1
    out = bytearray()
    while value >= 128:
        out.append(128 | (value & 127))
        value >>= 7
    out.append(value)
    return bytes(out)


def binary_proof(clauses: list[list[int]]) -> bytes:
    return b"".join(b"a" + b"".join(map(encode_lit, c)) + b"\0" for c in clauses)


def write_cnf(path: Path, nvars: int, clauses: list[list[int]]) -> None:
    body = "".join(" ".join(map(str, clause)) + " 0\n" for clause in clauses)
    path.write_text(f"p cnf {nvars} {len(clauses)}\n" + body, encoding="ascii")


def formula_satisfied(assignment: set[int], clauses: list[list[int]]) -> bool:
    def true(lit: int) -> bool:
        return (abs(lit) in assignment) == (lit > 0)
    return all(any(true(lit) for lit in c) for c in clauses)


def rup_trail(base: list[list[int]], goal: list[int]) -> dict:
    """Naive independent unit propagation under the falsified candidate."""
    value: dict[int, bool] = {}
    reason: dict[int, str] = {}

    def put(lit: int, why: str) -> None:
        v = abs(lit)
        val = lit > 0
        if v in value and value[v] != val:
            raise AssertionError((v, value[v], val, why))
        if v not in value:
            value[v] = val
            reason[v] = why

    for unit in (c[0] for c in base if len(c) == 1):
        put(unit, "root unit")
    for lit in goal:
        put(-lit, "falsify candidate")

    conflict = None
    changed = True
    while changed and conflict is None:
        changed = False
        for c in base:
            unassigned = []
            satisfied = False
            for lit in c:
                v = abs(lit)
                if v not in value:
                    unassigned.append(lit)
                elif value[v] == (lit > 0):
                    satisfied = True
                    break
            if satisfied:
                continue
            if not unassigned:
                conflict = c
                break
            if len(unassigned) == 1:
                before = len(value)
                put(unassigned[0], "unit from " + str(c))
                changed |= len(value) != before
    return {
        "satisfied": conflict is None,
        "conflict_clause": conflict,
        "values": {str(v): value[v] for v in sorted(value)},
        "reasons": {str(v): reason[v] for v in sorted(value)},
    }


def run_checker(checker: Path, stem: Path, query: list[list[int]],
                proof: list[list[int]], expect_verified: bool) -> dict:
    cnf = stem.with_suffix(".cnf")
    drat = stem.with_suffix(".drat")
    log = stem.with_suffix(".log")
    write_cnf(cnf, 25, query)
    drat.write_bytes(binary_proof(proof))
    proc = subprocess.run([str(checker), str(cnf), str(drat), "-i", "-U"],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          check=False)
    log.write_bytes(proc.stdout)
    lines = proc.stdout.decode("utf-8", "replace").splitlines()
    status = [line for line in lines if line.startswith("s ")]
    warnings = [line for line in lines if "WARNING" in line.upper()]
    if expect_verified:
        assert proc.returncode == 0, proc.stdout
        assert status == ["s VERIFIED"], status
    else:
        assert proc.returncode != 0, proc.stdout
        assert status == ["s NOT VERIFIED"], status
    assert not warnings, warnings
    return {"argv": [str(checker), str(cnf), str(drat), "-i", "-U"],
            "exit": proc.returncode, "status_lines": status,
            "warning_count": len(warnings), "log": str(log)}


def countermodel() -> tuple[dict[tuple[int, int], int], set[int]]:
    # ua=red, ub=green (guard broken), ab=blue; xu=red, xa=blue, xb=red.
    # Every triangle is nonmonochromatic and the candidate clause is false.
    colors = {(U, A): RED, (U, B): 2, (A, B): BLUE,
              (U, X): RED, (A, X): BLUE, (B, X): RED}
    colors = {tuple(sorted(e)): c for e, c in colors.items()}
    assert len(colors) == 6
    for tri in itertools.combinations(range(N), 3):
        cs = [colors[tuple(sorted(e))] for e in itertools.combinations(tri, 2)]
        assert len(set(cs)) > 1, (tri, cs)
    assert colors[tuple(sorted((X, U)))] == RED
    assert colors[tuple(sorted((X, A)))] in (RED, BLUE)
    assert colors[tuple(sorted((X, B)))] in (RED, BLUE)
    assignment = {25} | {var4(i, j, c) for (i, j), c in colors.items()}
    return colors, assignment


def package_example(package: Path) -> dict:
    evidence = package / "evidence"
    parent_bytes = gzip.decompress((evidence / "parent.cnf.gz").read_bytes())
    assert hashlib.sha256(parent_bytes).hexdigest() == PARENT_SHA
    parent = parent_bytes.decode("ascii")
    units = {int(line.split()[0]) for line in parent.splitlines()[1:]
             if len(line.split()) == 2}
    edges58 = {e: i for i, e in enumerate(itertools.combinations(range(58), 2))}
    def var58(i: int, j: int, color: int) -> int:
        return 1 + 4 * edges58[tuple(sorted((i, j)))] + color
    x, u, a, b, red, blue = 17, 2, 4, 11, 2, 3
    raw = ([-var58(x, u, red)]
           + [var58(x, w, c) for w in (a, b)
              for c in range(4) if c not in (red, blue)])
    simplified = [lit for lit in raw if -lit not in units]
    assert not [lit for lit in raw if lit in units]
    wedges = json.loads((evidence / "wedges.json").read_text())
    example = next(r for r in wedges["short_examples"]
                   if r["rule"] == [x, u, a, b, red, blue])
    assert example["cl"] == simplified
    assert simplified in wedges["clauses"]
    for i, j, c in ((u, a, red), (u, b, red), (a, b, blue)):
        assert var58(i, j, c) in units
    assert raw == [-511, 937, 938, 2309, 2310]
    assert simplified == [-511, 937, 2309]
    removed = {str(lit): -lit in units for lit in raw if -lit in units}
    return {"vertex_convention": "zero-based",
            "rule_[x,u,a,b,red,blue]": [x, u, a, b, red, blue],
            "raw_clause": raw, "stored_clause": simplified,
            "removed_false_literals_with_negated_parent_units": removed,
            "selected_clause_count": len(wedges["clauses"]),
            "selected_length_histogram": dict(sorted(collections.Counter(
                map(len, wedges["clauses"])).items()))}


def package_real_rup(package: Path) -> dict:
    """A one-clause real-parent RUP core; no whole-prefix replay is claimed."""
    parent_bytes = gzip.decompress((package / "evidence/parent.cnf.gz").read_bytes())
    assert hashlib.sha256(parent_bytes).hexdigest() == PARENT_SHA
    lines = parent_bytes.decode("ascii").splitlines()
    original = {tuple(sorted(map(int, line.split()[:-1]))) for line in lines[1:]
                if line and line[0] not in "cp"}
    core = [[459], [487], [916], [-938], [-2310],
            [-459, -511, -939], [-487, -511, -2311],
            [937, 938, 939, 940], [2309, 2310, 2311, 2312],
            [-916, -940, -2312]]
    missing = [c for c in core if tuple(sorted(c)) not in original]
    assert not missing, missing
    goal = [-511, 937, 2309]
    trail = rup_trail(core, goal)
    assert trail["conflict_clause"] == [-916, -940, -2312], trail
    expected = {"511": True, "937": False, "938": False, "939": False,
                "940": True, "2309": False, "2310": False,
                "2311": False, "2312": True}
    assert all(trail["values"][v] == value for v, value in expected.items())
    return {"goal": goal, "parent_clauses_used": core,
            "all_are_exact_original_parent_clauses": True,
            "propagation_conflict": trail["conflict_clause"],
            "forced_key_values": expected,
            "scope": "one selected short clause only; not the full 1020-rule prefix"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True, type=Path)
    ap.add_argument("--checker", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    goal = short_clause()
    assert goal == [-9, 19, 20, 23, 24]
    proof = [goal, [-25], []]

    good = base_formula(RED)
    trail = rup_trail(good, goal)
    assert trail["conflict_clause"] == [-14, -18, -22], trail
    (args.out / "rup-trail.json").write_text(json.dumps(trail, indent=2) + "\n")
    expected = {-var4(A, X, RED): True, var4(A, X, BLUE): True,
                -var4(B, X, RED): True, var4(B, X, BLUE): True}
    assert all(trail["values"][str(abs(k))] == (k > 0) for k in expected)
    good_result = run_checker(args.checker, args.out / "good-rup",
                              with_violation_selector(good, goal), proof, True)

    bad = base_formula(2)
    colors, assignment = countermodel()
    bad_query = with_violation_selector(bad, goal)
    assert formula_satisfied(assignment, bad_query)
    bad_result = run_checker(args.checker, args.out / "bad-guard",
                             bad_query, proof, False)
    color_record = {f"{i}-{j}": c for (i, j), c in sorted(colors.items())}
    (args.out / "guard-countermodel.json").write_text(json.dumps({
        "colors_zero_based": color_record,
        "assignment_satisfies_selector_query": True,
        "candidate_clause_is_false": True}, indent=2) + "\n")

    example = package_example(args.package)
    real_core = package_real_rup(args.package)
    (args.out / "real-square-rup-core.json").write_text(
        json.dumps(real_core, indent=2) + "\n")
    result = {"package_example": example,
              "real_parent_single_clause_rup": real_core,
              "toy": {"vertices_[u,a,b,x]": [U, A, B, X],
                      "red_blue": [RED, BLUE], "other_colors": list(OTHER),
                      "candidate": goal,
                      "proof_clauses": proof,
                      "positive_rup": good_result,
                      "broken_guard_negative_control": bad_result}}
    text = json.dumps(result, indent=2) + "\n"
    (args.out / "results.json").write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
