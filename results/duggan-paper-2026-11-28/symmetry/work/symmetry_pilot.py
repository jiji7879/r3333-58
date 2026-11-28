#!/usr/bin/env python3
"""Partition-preserving Codish/Duggan sb* pilot on an exact historical K58 row.

Run with the repository's .scratch/k58/.venv Python. This writes only beside
this script. Subcommands: validate, build, run, certificate.
"""
import argparse
import hashlib
import itertools
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OLD = REPO / ".ultramath/smwp3xc7p/m3/w/k58-solver/k58"
KISSAT = REPO / ".scratch/satcheck/bin/kissat"
DRAT = REPO / ".scratch/satcheck/bin/drat-trim"
sys.path.insert(0, str(OLD))
from gluing import host, units  # noqa: E402
from joint_plan import cases  # noqa: E402


def legacy_lex_clauses(xrows, yrows, top):
    """Historical hm.py comparator, retained only as a negative control."""
    assert len(xrows) == len(yrows) and xrows
    clauses = []
    peq_prev = None
    peqs, lts = [], []
    for x, y in zip(xrows, yrows):
        top += 1
        lt = top
        for c in range(4):
            for c2 in range(c + 1, 4):
                clauses.append([-x[c], -y[c2], lt])
        lts.append(lt)
        top += 1
        peq = top
        if peq_prev is None:
            for c in range(4):
                clauses.append([-x[c], -y[c], peq])
        else:
            for c in range(4):
                clauses.append([-peq_prev, -x[c], -y[c], peq])
        peqs.append(peq)
        peq_prev = peq
    big = []
    for i, lt in enumerate(lts):
        top += 1
        p = top
        if i == 0:
            clauses.append([-lt, p])
        else:
            clauses.append([-peqs[i - 1], -lt, p])
        big.append(p)
    big.append(peqs[-1])
    clauses.append(big)
    return clauses, top


def lex_clauses(xrows, yrows, top):
    """Exact existential CNF for one-hot integer rows xrows <= yrows.

    L is less-than at a witness, E is prefix equality, and P witnesses a
    less-than position after an equal prefix. Both directions are encoded.
    The one-hot assumption is supplied by the host edge constraints.
    """
    assert len(xrows) == len(yrows) and xrows
    clauses = []
    peq_prev = None
    peqs, lts = [], []
    for x, y in zip(xrows, yrows):
        top += 1
        lt = top
        for c in range(4):
            for c2 in range(4):
                if c < c2:
                    clauses.append([-x[c], -y[c2], lt])
                else:
                    clauses.append([-lt, -x[c], -y[c2]])
        lts.append(lt)
        top += 1
        peq = top
        for c in range(4):
            prefix = [] if peq_prev is None else [-peq_prev]
            clauses.append([*prefix, -x[c], -y[c], peq])
            for c2 in range(4):
                if c != c2:
                    clauses.append([*prefix, -x[c], -y[c2], -peq])
        if peq_prev is not None:
            clauses.append([-peq, peq_prev])
        peqs.append(peq)
        peq_prev = peq
    big = []
    for i, lt in enumerate(lts):
        top += 1
        p = top
        if i == 0:
            clauses.append([-lt, p])
            clauses.append([-p, lt])
        else:
            clauses.append([-peqs[i - 1], -lt, p])
            clauses.append([-p, peqs[i - 1]])
            clauses.append([-p, lt])
        big.append(p)
    big.append(peqs[-1])
    clauses.append(big)
    return clauses, top


def add_lex(clauses, lit, u, v, n, top, encoder=lex_clauses):
    ws = [w for w in range(n) if w != u and w != v]
    xs = [[lit(min(u, w), max(u, w), c) for c in range(4)] for w in ws]
    ys = [[lit(min(v, w), max(v, w), c) for c in range(4)] for w in ws]
    extra, top = encoder(xs, ys, top)
    clauses.extend(extra)
    return top


def row(matrix, i, omitted=()):
    return tuple(matrix[i][j] for j in range(len(matrix)) if j not in omitted)


def sbstar(matrix, cells):
    for cell in cells:
        for i, j in itertools.combinations(cell, 2):
            if row(matrix, i, (i, j)) > row(matrix, j, (i, j)):
                return False
    return True


def permute_matrix(matrix, permutation):
    n = len(matrix)
    inverse = [0] * n
    for i, j in enumerate(permutation):
        inverse[j] = i
    return tuple(tuple(0 if i == j else matrix[inverse[i]][inverse[j]]
                       for j in range(n)) for i in range(n))


def flat(matrix):
    return tuple(x for line in matrix for x in line)


def partitions_group(cells):
    for choices in itertools.product(*(list(itertools.permutations(cell)) for cell in cells)):
        p = list(range(max(max(cell) for cell in cells) + 1))
        for cell, choice in zip(cells, choices):
            for i, j in zip(cell, choice):
                p[i] = j
        yield tuple(p)


def brute_cnf(clauses, nv, pinned=()):
    """Exhaust all non-pinned variables; used only for tiny controls."""
    pinned = dict(pinned)
    free = [v for v in range(1, nv + 1) if v not in pinned]
    for bits in itertools.product((False, True), repeat=len(free)):
        model = dict(pinned)
        model.update(zip(free, bits))
        if all(any(model[abs(x)] == (x > 0) for x in clause) for clause in clauses):
            return True
    return False


def validate():
    # All 256 pairs of two-witness, four-colour one-hot rows, exhausting all
    # six auxiliary assignments in each case.
    checked = 0
    legacy_bad = []
    for left in itertools.product(range(4), repeat=2):
        for right in itertools.product(range(4), repeat=2):
            xs = [[1 + 4 * w + c for c in range(4)] for w in range(2)]
            ys = [[9 + 4 * w + c for c in range(4)] for w in range(2)]
            clauses, top = lex_clauses(xs, ys, 16)
            pins = {}
            for rows, values in ((xs, left), (ys, right)):
                for edge, colour in zip(rows, values):
                    for literal in edge:
                        pins[literal] = (literal - 1) % 4 == colour
            actual = brute_cnf(clauses, top, pins)
            expected = left <= right
            assert actual == expected, (left, right, actual, expected, clauses)
            legacy, legacy_top = legacy_lex_clauses(xs, ys, 16)
            assert brute_cnf(legacy, legacy_top, pins)
            if not expected:
                legacy_bad.append((left, right))
            checked += 1
    assert checked == 256

    # Every 4-colouring of K4, for full S4 and two partition stabilizers.
    edges = list(itertools.combinations(range(4), 2))
    orbit_checks = []
    for cells in (((0, 1, 2, 3),), ((0, 1), (2, 3)), ((0, 1, 2), (3,))):
        accepted_orbits = set()
        canonical_orbits = set()
        for values in itertools.product(range(4), repeat=len(edges)):
            matrix = [[0] * 4 for _ in range(4)]
            for (i, j), colour in zip(edges, values):
                matrix[i][j] = matrix[j][i] = colour
            matrix = tuple(tuple(line) for line in matrix)
            orbit = {permute_matrix(matrix, p) for p in partitions_group(cells)}
            canonical = min(orbit, key=flat)
            assert sbstar(canonical, cells), (cells, values, canonical)
            canonical_orbits.add(flat(canonical))
            accepted_orbits.update(flat(a) for a in orbit if sbstar(a, cells))
        orbit_checks.append({"cells": cells, "canonical_orbits": len(canonical_orbits),
                             "accepted_matrices": len(accepted_orbits)})
    result = {"two_witness_row_pairs_checked": checked,
              "historical_comparator_nonlex_pairs_accepted": len(legacy_bad),
              "historical_comparator_first_bad_pair": legacy_bad[0],
              "matrices_per_partition": 4 ** 6,
              "integer_sbstar_checks": orbit_checks}
    (HERE / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


def exact_twin_data(lit, signed_units, n=58):
    edge = {lit(a, b, c): (a, b, c) for a, b in itertools.combinations(range(n), 2)
            for c in range(4)}
    signed_units = set(signed_units)
    twins = []
    for u, v in itertools.combinations(range(n), 2):
        def tr(x):
            return v if x == u else u if x == v else x
        mapped = set()
        for x in signed_units:
            a, b, c = edge[abs(x)]
            a, b = tr(a), tr(b)
            mapped.add((1 if x > 0 else -1) * lit(min(a, b), max(a, b), c))
        if mapped == signed_units:
            twins.append((u, v))

    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for u, v in twins:
        parent[find(u)] = find(v)
    groups = {}
    for v in range(n):
        groups.setdefault(find(v), []).append(v)
    cells = [tuple(g) for g in groups.values() if len(g) > 1]
    for cell in cells:
        assert list(cell) == list(range(cell[0], cell[-1] + 1))
        assert all(pair in twins for pair in itertools.combinations(cell, 2))
    return twins, cells


def matching(twins):
    used, result = set(), []
    for u, v in twins:
        if u not in used and v not in used:
            result.append((u, v))
            used.update((u, v))
    return result


def write_cnf(path, clauses, top):
    with path.open("w") as out:
        out.write(f"p cnf {top} {len(clauses)}\n")
        for clause in clauses:
            out.write(" ".join(map(str, clause)) + " 0\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_case(index):
    for k, (family, placement, _, charge) in enumerate(cases((16, 14, 14, 13))):
        if k == index:
            lit, base = host(58)
            raw = units(family, placement)
            assert all(len(c) == 1 for c in raw)
            signed_units = sorted({c[0] for c in raw})
            return family, placement, charge, lit, base, signed_units
    raise ValueError(index)


def build(indices):
    outputs = []
    for index in indices:
        family, placement, charge, lit, base, signed_units = load_case(index)
        twins, cells = exact_twin_data(lit, signed_units)
        mt = matching(twins)
        assert len(twins) == sum(math.comb(len(cell), 2) for cell in cells)
        for mode in ("bare", "historical", "matching", "full"):
            clauses = [list(c) for c in base] + [[x] for x in signed_units]
            top = 4 * 58 * 57 // 2
            pairs = [] if mode == "bare" else mt if mode in ("historical", "matching") else [
                pair for cell in cells for pair in itertools.combinations(cell, 2)]
            encoder = legacy_lex_clauses if mode == "historical" else lex_clauses
            for u, v in pairs:
                top = add_lex(clauses, lit, u, v, 58, top, encoder)
            path = HERE / f"case{index}-{mode}.cnf"
            digest = write_cnf(path, clauses, top)
            outputs.append({
                "case": index, "mode": mode, "path": path.name, "sha256": digest,
                "variables": top, "clauses": len(clauses), "lex_pairs": len(pairs),
                "profile": family.profile, "root_kinds": family.root_kinds,
                "arm": family.arm, "charge": charge, "placements": placement,
                "signed_units": len(signed_units), "negative_units": sum(x < 0 for x in signed_units),
                "exact_transpositions": len(twins), "cells": cells,
                "matching_factor": 2 ** len(mt),
                "generated_group_order": math.prod(math.factorial(len(cell)) for cell in cells),
            })
    (HERE / "built.json").write_text(json.dumps(outputs, indent=2) + "\n")
    print(json.dumps(outputs, indent=2))


def run(paths, conflicts, seeds):
    records = json.loads((HERE / "built.json").read_text())
    selected = {HERE / r["path"]: r for r in records}
    for path in paths:
        path = path.resolve()
        meta = selected[path]
        for seed in seeds:
            start = time.monotonic()
            job = subprocess.run([str(KISSAT), f"--conflicts={conflicts}", f"--seed={seed}",
                                  str(path)], capture_output=True, text=True)
            elapsed = time.monotonic() - start
            text = job.stdout + job.stderr
            status = "SAT" if job.returncode == 10 else "UNSAT" if job.returncode == 20 else "OPEN"
            assert status == "OPEN", (path, seed, status, text[-2000:])
            def number(name):
                found = re.search(rf"{name}:\s+(\d+)", text)
                return int(found.group(1)) if found else None
            record = {"case": meta["case"], "mode": meta["mode"], "seed": seed,
                      "status": status, "returncode": job.returncode,
                      "wall_seconds": elapsed, "conflicts": number("conflicts"),
                      "propagations": number("propagations"), "decisions": number("decisions"),
                      "variables": meta["variables"], "clauses": meta["clauses"],
                      "lex_pairs": meta["lex_pairs"]}
            print(json.dumps(record), flush=True)
            with (HERE / "timings.jsonl").open("a") as out:
                out.write(json.dumps(record) + "\n")


def certificate():
    # R(3,3)=6, expressed by forbidding colours 2 and 3 on every K6 edge.
    n = 6
    lit, base = host(n)
    signed_units = [-lit(i, j, c) for i, j in itertools.combinations(range(n), 2)
                    for c in (2, 3)]
    clauses = [list(c) for c in base] + [[x] for x in signed_units]
    top = 4 * n * (n - 1) // 2
    twins, cells = exact_twin_data(lit, signed_units, n)
    assert cells == [tuple(range(n))]
    for u, v in itertools.combinations(range(n), 2):
        top = add_lex(clauses, lit, u, v, n, top)
    cnf = HERE / "r33-k6-sbstar.cnf"
    proof = HERE / "r33-k6-sbstar.drat"
    write_cnf(cnf, clauses, top)
    job = subprocess.run([str(KISSAT), "-q", str(cnf), str(proof)])
    assert job.returncode == 20, job.returncode
    check = subprocess.run([str(DRAT), str(cnf), str(proof)], capture_output=True, text=True)
    output = check.stdout + check.stderr
    assert check.returncode == 0 and "s VERIFIED" in output and not re.search(r"(?i)warning|error", output), output
    result = {"solver_exit": job.returncode, "checker_exit": check.returncode,
              "checker_output": output.strip(), "proof_bytes": proof.stat().st_size,
              "variables": top, "clauses": len(clauses), "lex_pairs": 15}
    (HERE / "certificate.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    build_parser = sub.add_parser("build")
    build_parser.add_argument("indices", type=int, nargs="+", default=[7])
    run_parser = sub.add_parser("run")
    run_parser.add_argument("paths", type=Path, nargs="+")
    run_parser.add_argument("--conflicts", type=int, default=200000)
    run_parser.add_argument("--seeds", type=int, nargs="+", default=[0])
    sub.add_parser("certificate")
    args = parser.parse_args()
    if args.command == "validate":
        validate()
    elif args.command == "build":
        build(args.indices)
    elif args.command == "run":
        run(args.paths, args.conflicts, args.seeds)
    else:
        certificate()


if __name__ == "__main__":
    main()
