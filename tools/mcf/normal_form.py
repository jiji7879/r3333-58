#!/usr/bin/env python3
"""Strict DIMACS freezing and configurable maximal-colour CNF construction.

This module constructs an existence-preserving augmentation, not a DRAT
consequence of the input formula. The K58 row/bridge semantics live in the
caller; everything here is checked over explicit CNF objects.
"""
from __future__ import annotations

import hashlib
import itertools
from pathlib import Path


class McfError(ValueError):
    """An input, allocation, or provenance error; never silently fall back."""


def require(condition, message):
    if not condition:
        raise McfError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_dimacs(data):
    """Return (nv, clauses, body), requiring a first-line canonical header.

    The original body is returned byte-for-byte so query construction can never
    reorder, pretty-print, or simplify the retained parent.
    """
    require(isinstance(data, bytes), "DIMACS input must be bytes")
    require(b"\n" in data, "DIMACS input has no header newline")
    header, body = data.split(b"\n", 1)
    fields = header.split()
    require(len(fields) == 4 and fields[:2] == [b"p", b"cnf"],
            "first line must be: p cnf VARIABLES CLAUSES")
    try:
        nv, count = int(fields[2]), int(fields[3])
    except ValueError as exc:
        raise McfError("non-integer DIMACS header") from exc
    require(nv >= 0 and count >= 0, "negative DIMACS header size")
    require(body.endswith(b"\n") or not body, "DIMACS body must end in a newline")
    clauses, pending = [], []
    for line_number, line in enumerate(body.splitlines(), 2):
        stripped = line.strip()
        if not stripped or stripped.startswith(b"c"):
            continue
        require(not stripped.startswith(b"p"), f"second header at line {line_number}")
        for token in stripped.split():
            try:
                literal = int(token)
            except ValueError as exc:
                raise McfError(f"non-integer literal at line {line_number}") from exc
            if literal:
                require(abs(literal) <= nv,
                        f"literal {literal} exceeds variable bound {nv}")
                pending.append(literal)
            else:
                clauses.append(tuple(pending))
                pending = []
    require(not pending, "unterminated final DIMACS clause")
    require(len(clauses) == count,
            f"DIMACS header declares {count} clauses but body has {len(clauses)}")
    return nv, clauses, body


def parse_cube(text, nv):
    require(isinstance(text, str), "cube must be a comma-separated string")
    pieces = text.split(",") if text else []
    require(pieces and all(piece.strip() for piece in pieces),
            "cube must be a nonempty comma-separated literal list")
    cube = []
    for piece in pieces:
        try:
            literal = int(piece.strip(), 10)
        except ValueError as exc:
            raise McfError(f"invalid cube literal {piece!r}") from exc
        require(literal != 0 and abs(literal) <= nv,
                f"cube literal {literal} is zero or exceeds parent bound {nv}")
        require(literal not in cube, f"cube repeats literal {literal}")
        require(-literal not in cube, f"cube contains complementary literals {literal}, {-literal}")
        cube.append(literal)
    return cube


def encode_clauses(clauses):
    return b"".join((" ".join(map(str, clause)) + " 0\n").encode()
                    for clause in clauses)


def extend_body(base, additions, new_nv=None):
    """Replace only the header, retaining base body then exact extra clauses."""
    nv, clauses, body = read_dimacs(base)
    top = nv if new_nv is None else new_nv
    require(type(top) is int and top >= nv, "new variable bound decreases or is invalid")
    result = f"p cnf {top} {len(clauses) + len(additions)}\n".encode() + body
    result += encode_clauses(additions)
    out_nv, out_clauses, out_body = read_dimacs(result)
    require(out_nv == top and out_clauses == clauses + list(map(tuple, additions)),
            "DIMACS extension read-back differs")
    require(out_body[:len(body)] == body, "DIMACS extension changed original body")
    return result


def freeze_cube(base, cube):
    nv, _, _ = read_dimacs(base)
    require(isinstance(cube, (list, tuple)) and cube, "cube must be nonempty")
    canonical = parse_cube(",".join(map(str, cube)), nv)
    require(canonical == list(cube), "cube contains non-canonical integer objects")
    result = extend_body(base, [(lit,) for lit in canonical])
    expected_tail = b"".join(f"{lit} 0\n".encode() for lit in canonical)
    require(result.endswith(expected_tail), "appended units differ from retained cube")
    return result


def physical_lit(u, v, colour):
    require(u != v and 0 <= colour < 4, "invalid physical edge or colour")
    u, v = sorted((u, v))
    edge_id = (u * (2 * 58 - u - 1)) // 2 + (v - u - 1)
    return 4 * edge_id + colour + 1


def edge_of_lit(literal):
    return (abs(literal) - 1) // 4


def maximal_rules(configurable, colour, order=58):
    """Validate deterministic configurable edges for the MCF construction."""
    require(type(order) is int and order >= 3, "graph order must be at least three")
    require(type(colour) is int and 0 <= colour < 4, "colour must be in 0..3")
    seen = set()
    for rule in configurable:
        require(isinstance(rule, (tuple, list)) and len(rule) == 3,
                "configurable edge must be an (arm, u, v) triple")
        arm, u, v = rule
        require(type(arm) is int and 0 <= arm < 4, "arm must be in 0..3")
        require(arm != colour, "normalisation colour must differ from selected arm")
        require(type(u) is int and type(v) is int and 0 <= u < v < order,
                "configurable endpoints must be ordered vertices")
        require((u, v) not in seen, f"duplicate configurable edge {(u, v)}")
        seen.add((u, v))
        yield arm, u, v


def augment_maximal(parent, configurable, colour, order=58):
    """Append MCF clauses above parent's declared maximum variable.

    Returns (augmented_bytes, rules, added_clauses). The caller separately
    proves non-host/cube disjointness before using this transformation.
    """
    parent_nv, _, _ = read_dimacs(parent)
    configurable = list(configurable)
    require(configurable, "no configurable edges selected; refusing a fake MCF success")
    additions, rules = [], []
    top = parent_nv
    for arm, u, v in maximal_rules(configurable, colour, order):
        witnesses, allocations = [], []
        for w in range(order):
            if w in (u, v):
                continue
            top += 1
            y = top
            left, right = physical_lit(u, w, colour), physical_lit(v, w, colour)
            require(left <= parent_nv and right <= parent_nv,
                    "physical path variable outside parent allocation")
            additions.extend(((-y, left), (-y, right), (y, -left, -right)))
            witnesses.append(y)
            allocations.append({"third_vertex": w, "witness": y,
                                "left": left, "right": right})
        additions.append((physical_lit(u, v, colour), *witnesses))
        rules.append({
            "arm": arm, "colour": colour, "edge": [u, v],
            "edge_variable": physical_lit(u, v, colour),
            "physical_variables": list(range(4 * edge_of_lit(physical_lit(u, v, colour)) + 1,
                                               4 * edge_of_lit(physical_lit(u, v, colour)) + 5)),
            "long_clause_literals": len(witnesses) + 1,
            "witnesses": allocations,
        })
    augmented = extend_body(parent, additions, top)
    return augmented, rules, additions


def configurable_variables(rules):
    return {variable for rule in rules for variable in rule["physical_variables"]}


def fresh_variables(rules):
    return [entry["witness"] for rule in rules for entry in rule["witnesses"]]


def assert_disjoint_and_allocated(parent, rules, suffix_clauses, cube, augmented):
    """Check every variable boundary used by the semantic reduction."""
    parent_nv, parent_clauses, parent_body = read_dimacs(parent)
    aug_nv, aug_clauses, aug_body = read_dimacs(augmented)
    changing = configurable_variables(rules)
    fresh = fresh_variables(rules)
    require(changing, "no configurable edges selected; refusing a fake MCF success")
    require(all(1 <= variable <= parent_nv for variable in changing),
            "configurable physical variable outside parent allocation")
    require(len(fresh) == len(set(fresh)), "fresh witness allocated more than once")
    require(fresh == list(range(parent_nv + 1, parent_nv + 1 + len(fresh))),
            "fresh witnesses are not contiguous immediately above parent maximum")
    require(aug_nv == parent_nv + len(fresh), "augmented maximum differs from fresh allocation")
    require(not changing.intersection(fresh), "physical/fresh variable collision")
    require(not any(abs(lit) in changing for clause in suffix_clauses for lit in clause),
            "actual non-host suffix contains a configurable physical variable")
    require(not any(abs(lit) in changing for lit in cube),
            "retained cube touches a configurable edge; leaf normal form is not preserved")
    require(not any(abs(lit) in fresh for clause in parent_clauses for lit in clause),
            "fresh variable collides with parent literal")
    require(len(aug_clauses) > len(parent_clauses), "augmentation has no clauses")
    require(aug_clauses[:len(parent_clauses)] == parent_clauses,
            "augmentation changed/reordered parent clauses")
    require(aug_body[:len(parent_body)] == parent_body,
            "augmentation changed original body bytes")


def normalise_colouring(matrix, configurable, colour):
    """Small independent semantic control over an explicit adjacency matrix."""
    n = len(matrix)
    require(all(len(row) == n for row in matrix), "colouring matrix is not square")
    before = [row[:] for row in matrix]
    configurable = list(maximal_rules(configurable, colour, n))
    for _, u, v in configurable:
        if matrix[u][v] == colour:
            continue
        witness = any(w not in (u, v) and matrix[u][w] == colour == matrix[v][w]
                      for w in range(n))
        if not witness:
            matrix[u][v] = matrix[v][u] = colour
    for arm, u, v in configurable:
        del arm
        require(matrix[u][v] == colour or
                any(w not in (u, v) and matrix[u][w] == colour == matrix[v][w]
                    for w in range(n)), "normal form not reached")
    for u, v, w in itertools.combinations(range(n), 3):
        require(not (matrix[u][v] == matrix[u][w] == matrix[v][w]),
                "normalisation created a monochromatic triangle")
    return before, matrix
