"""A search CNF for a marked K58 case and its binary DRAT lifting prefix."""
from collections import defaultdict
from functools import cache
from pathlib import Path
from shutil import copyfileobj

from pysat.solvers import Minisat22

from anchor_cuts import binary_prefix
from dense import marked_threshold
from gluing import Family, data, host, units

PROFILE = (15, 14, 14, 14)
PHYSICAL = 4 * (58 * 57 // 2)


def dimacs(clause):
    return (" ".join(map(str, clause)) + " 0\n").encode()


@cache
def physical_index():
    base = host(58)[1]
    occurrence = defaultdict(list)
    for i, clause in enumerate(base):
        for lit in clause:
            occurrence[lit].append(i)
    # One instance per worker process. propagate() retracts all assumptions.
    return base, list(map(dimacs, base)), occurrence, Minisat22(bootstrap_with=base)


def family_of(row):
    fields = dict(row["family"])
    for field in ("root_kinds", "profile"):
        fields[field] = tuple(fields[field])
    return Family(**fields)


def dispensable_counts(family, row, recipe):
    # The marked sender in a 14-arm supplies the only required ticket.
    return (family.profile == PROFILE and family.arm == 1 and row["charge"] == 1
            and not recipe["full_root"])


def pentagon_hits(family, placement, true):
    """A bichromatic pentagon cannot acquire a sixth vertex in its two colors."""
    edge = host(58)[0]
    groups = []
    start = 1
    for size in family.profile:
        groups.append(tuple(range(start, start + size)))
        start += size
    supports, options, _ = data(family)
    mark_neighbors = [0]
    blocks = []
    for (b, _), choices, pick in zip(supports, options, placement):
        block = tuple(groups[b][i] for i in choices[pick])
        blocks.append((b, block))
        mark_neighbors.extend(block)
    for b, block in blocks:
        if len(block) != 5:
            continue
        a = family.arm
        first, second = (c for c in range(4) if c not in (a, b))
        # Independent of the classification: check the pinned two-color C5.
        for x in block:
            if any(sum(edge(x, y, c) in true for y in block if y != x) != 2
                   for c in (first, second)):
                raise ValueError("support is not a pinned bichromatic pentagon")
        for vertices, hit in ((groups[b], a), (mark_neighbors, b)):
            for x in vertices:
                if x in block:
                    continue
                full = [edge(x, y, hit) for y in block]
                if any(lit in true for lit in full):
                    continue
                goal = tuple(lit for lit in full if -lit not in true)
                decisions = tuple(edge(x, y, first) for y in block)
                yield goal, decisions


def decision_proof(goal, variables):
    """Resolve a binary decision tree bottom-up to derive the hit clause."""
    def visit(prefix):
        if len(prefix) < len(variables):
            literal = variables[len(prefix)]
            yield from visit(prefix + (literal,))
            yield from visit(prefix + (-literal,))
        yield goal + prefix
    return list(visit(()))


def build(row, recipe, path, *, hits=False, proof_prefix=None):
    """Write a search input. With proof_prefix, also emit its DRAT derivation."""
    family = family_of(row)
    fixed = units(family, row["placement"])
    base, encoded, occurrence, propagator = physical_index()
    pins = [c[0] for c in fixed]
    consistent, propagated = propagator.propagate(assumptions=pins)
    if not consistent:
        raise ValueError("unexpected conflict in pinned host")
    given = set(pins)
    true = set(propagated) | given
    removed = {i for lit in true for i in occurrence[lit]}
    shortened = {i for lit in true for i in occurrence[-lit]} - removed
    rows = encoded.copy()
    for i in removed:
        rows[i] = b""
    changed = []
    for i in sorted(shortened):
        clause = [lit for lit in base[i] if -lit not in true]
        rows[i] = dimacs(clause)
        if proof_prefix is not None:
            changed.append(clause)
    count = len(base) - len(removed)
    skip = dispensable_counts(family, row, recipe)
    top = PHYSICAL
    dropped_aux = []
    if not skip or proof_prefix is not None:
        extra = marked_threshold(family, fixed, row["charge"], **recipe)
        if skip:
            # Setting every auxiliary false satisfies this entire suffix.
            if not all(any(lit < -PHYSICAL for lit in c) for c in extra):
                raise ValueError("ticket counters were required")
            dropped_aux = extra
        else:
            for original in extra:
                if any(lit in true for lit in original):
                    if proof_prefix is not None:
                        dropped_aux.append(original)
                    continue
                clause = [lit for lit in original if -lit not in true]
                rows.append(dimacs(clause))
                if clause:
                    top = max(top, max(map(abs, clause)))
                count += 1
                if proof_prefix is not None and len(clause) != len(original):
                    changed.append(clause)
                    dropped_aux.append(original)
    cuts = dict(pentagon_hits(family, row["placement"], true)) if hits else {}
    rows.extend(dimacs(c) for c in cuts)
    count += len(cuts)
    with Path(path).open("wb") as out:
        out.write(f"p cnf {top} {count}\n".encode())
        out.write(b"".join(rows))
    if proof_prefix is not None:
        with Path(proof_prefix).open("wb") as out:
            # All original pins are units. Each new unit follows by host UP.
            out.write(binary_prefix([[lit] for lit in propagated if lit not in given]))
            out.write(binary_prefix(changed))
            for goal, variables in cuts.items():
                tree = decision_proof(goal, variables)
                out.write(binary_prefix(tree))
                for helper in tree[:-1]:
                    delete(out, helper)
            # The remaining database equals the working clauses plus units on
            # variables absent from them. Those units cannot affect a RAT pivot.
            for i in sorted(removed | shortened):
                delete(out, base[i])
            for clause in dropped_aux:
                delete(out, clause)
    return dict(clauses=count, max_variable=top, propagated=len(true),
                skipped_ticket_suffix=skip, pentagon_hits=len(cuts), bytes=Path(path).stat().st_size)


def delete(out, clause):
    out.write(b"d" + binary_prefix([clause])[1:])


def lift(prefix, raw, lifted):
    with Path(lifted).open("wb") as out:
        for path in (prefix, raw):
            with Path(path).open("rb") as source:
                copyfileobj(source, out)
