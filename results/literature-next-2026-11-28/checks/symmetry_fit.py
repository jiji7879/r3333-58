#!/usr/bin/env python3
"""Bounded, solver-free stabilizer inventory for the retained K58 parent."""
import argparse
import hashlib
import json
from itertools import combinations
from functools import cache
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
FROZEN = ROOT / "tools/color-resolved-wallcc/frozen"
sys.path.insert(0, str(FROZEN))
from gluing import Family, host, units
from dense import marked_threshold
from cover_evidence import formula_chunks

ROW_ID = "06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06"
CUBE = [-1413, 1014]


def load_row():
    import gzip
    with gzip.open(ROOT / "tools/color-resolved-wallcc/data/wall.jsonl.gz", "rt") as stream:
        for line in stream:
            row = json.loads(line)
            if row["id"] == ROW_ID:
                return row
    raise AssertionError("retained row absent")


@cache
def decode(n):
    v = abs(n) - 1
    rank, colour = divmod(v, 4)
    edges = list(combinations(range(58), 2))
    return (*edges[rank], colour, n > 0)


def vertex_permutation(a, b):
    permutation = list(range(58))
    permutation[a], permutation[b] = b, a
    return permutation


def literal_image(literal, permutation, inverse=False):
    if abs(literal) > 6612:
        return literal
    u, v, colour, _ = decode(literal)
    if inverse:
        permutation = [permutation.index(i) for i in range(58)]
    from gluing import host
    lit, _ = host(58)
    image = lit(permutation[u], permutation[v], colour)
    return image if literal > 0 else -image


def unit_set_image(fixed, permutation, inverse=False):
    return {literal_image(c[0], permutation, inverse) for c in fixed}


def assignment_set(fixed):
    return {c[0] for c in fixed}


def cells_and_pairs(fixed):
    # A common signed-unit column signature is also sufficient here: direct
    # application below checks every proposed transposition, not just a WL cell.
    lit, _ = host(58)
    assignment = {abs(c[0]): c[0] > 0 for c in fixed}
    signatures = []
    for u in range(58):
        signature = []
        for v in range(58):
            if u == v:
                continue
            for colour in range(4):
                variable = lit(u, v, colour)
                signature.append(assignment.get(variable))
        signatures.append(tuple(signature))
    cells = {}
    for vertex, signature in enumerate(signatures):
        cells.setdefault(signature, []).append(vertex)
    candidates = [cell for cell in cells.values() if len(cell) > 1]
    pairs = []
    for cell in candidates:
        for a, b in combinations(cell, 2):
            permutation = vertex_permutation(a, b)
            if unit_set_image(fixed, permutation) == assignment_set(fixed):
                pairs.append((a, b))
    return candidates, pairs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-cnf", action="store_true",
                        help="Also test exact clause-set invariance with all auxiliaries fixed")
    args = parser.parse_args()
    row = load_row()
    fields = dict(row["family"])
    for field in ("profile", "root_kinds"):
        fields[field] = tuple(fields[field])
    family = Family(**fields)
    fixed = units(family, row["placement"])
    cells, pairs = cells_and_pairs(fixed)
    cube_pairs = []
    for a, b in pairs:
        permutation = vertex_permutation(a, b)
        if {literal_image(x, permutation) for x in CUBE} == set(CUBE):
            cube_pairs.append((a, b))
    output = {
        "row": ROW_ID,
        "profile": family.profile,
        "root_kinds": family.root_kinds,
        "arm": family.arm,
        "fixed_units": len(fixed),
        "positive_units": sum(c[0] > 0 for c in fixed),
        "negative_units": sum(c[0] < 0 for c in fixed),
        "candidate_cells": cells,
        "verified_unit_transpositions": pairs,
        "cube_preserving_transpositions": cube_pairs,
        "cube": [decode(x) for x in CUBE],
    }
    if args.full_cnf:
        recipe = {"tables": True, "total_critical": True, "full_root": False}
        chunks = formula_chunks(row, recipe)
        data = b"".join(chunks)
        lines = data.decode().splitlines()
        clauses = []
        for line in lines[1:]:
            clause = tuple(sorted(map(int, line.split()[:-1]), key=lambda x: (abs(x), x < 0)))
            clauses.append(clause)
        clause_set = set(clauses)
        suffix = fixed + marked_threshold(family, fixed, row["charge"], **recipe)
        syntactic = []
        first_failure = None
        for a, b in pairs:
            permutation = vertex_permutation(a, b)
            valid = True
            for index, clause in enumerate(clauses, 1):
                image = tuple(sorted((literal_image(x, permutation) for x in clause),
                                     key=lambda x: (abs(x), x < 0)))
                if image not in clause_set:
                    if first_failure is None:
                        first_failure = dict(transposition=[a, b], clause_index=index,
                                             original=clause, image=image)
                    valid = False
                    break
            if valid:
                syntactic.append((a, b))
        output.update({
            "parent_sha256": hashlib.sha256(data).hexdigest(),
            "parent_header": lines[0],
            "distinct_clauses": len(clause_set),
            "suffix_clauses_including_units": len(suffix),
            "syntactic_symmetries_aux_fixed": syntactic,
            "syntactic_with_cube": [(a, b) for a, b in syntactic if (a, b) in cube_pairs],
            "first_syntactic_failure": first_failure,
            "parent_cube_sha256": hashlib.sha256(
                data.replace(lines[0].encode() + b"\n", b"p cnf 19533 184337\n", 1)
                + b"-1413 0\n1014 0\n").hexdigest(),
        })
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
