#!/usr/bin/env python3
"""Normalize all finite K4/K5 alternatives to the literal shipped K15 CNF.

No SAT search is used. python-sat is needed only to import next/block.py.
Usage: normalization.py EXTRACTED_SOURCE_DIR OUTPUT_JSON
"""
from collections import Counter
import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT / "next"))
import block

EDGES = list(itertools.combinations(range(15), 2))
GROUPS = (tuple(range(1, 5)), tuple(range(5, 10)), tuple(range(10, 15)))
SQUARE_CYCLE = (0, 2, 1, 3)
SQUARE = {frozenset((SQUARE_CYCLE[i], SQUARE_CYCLE[(i + 1) % 4])) for i in range(4)}


def var(edge, colour):
    return 1 + 3 * EDGES.index(tuple(sorted(edge))) + colour


def pin(edge, colour):
    return (var(edge, colour),)


def colourings(n):
    """Every triangle-free 2-colouring of the labelled K_n."""
    edges = list(itertools.combinations(range(n), 2))
    for values in itertools.product((0, 1), repeat=len(edges)):
        spec = dict(zip(edges, values))
        if all(len({spec[tuple(sorted(e))] for e in itertools.combinations(t, 2)}) > 1
               for t in itertools.combinations(range(n), 3)):
            yield spec


def cycle_order(spec, edge_colour, start):
    vertices = sorted({v for edge in spec for v in edge})
    adj = {v: [] for v in vertices}
    for (u, v), c in spec.items():
        if c == edge_colour:
            adj[u].append(v)
            adj[v].append(u)
    assert all(len(adj[v]) == 2 for v in vertices)
    out, prev, current = [], None, start
    for _ in vertices:
        out.append(current)
        a, b = adj[current]
        prev, current = current, a if a != prev else b
    assert len(set(out)) == len(vertices) and current == start
    return out


def renumber(clause, vmap, cmap):
    result = []
    for literal in clause:
        i, colour = divmod(abs(literal) - 1, 3)
        u, v = EDGES[i]
        new = var((vmap[u], vmap[v]), cmap[colour])
        result.append(new if literal > 0 else -new)
    return tuple(sorted(result))


def palette(group):
    return tuple(c for c in range(3) if c != group)


def base_formula():
    """Total 3-colouring, triangle freedom, and root-edge units only."""
    clauses = []
    for u, v in EDGES:
        edge = [var((u, v), c) for c in range(3)]
        clauses.append(tuple(edge))
        clauses.extend(tuple(sorted((-a, -b))) for a, b in itertools.combinations(edge, 2))
    for u, v, w in itertools.combinations(range(15), 3):
        for colour in range(3):
            clauses.append(tuple(sorted((-var((u, v), colour),
                                         -var((v, w), colour),
                                         -var((u, w), colour)))))
    for group, vertices in enumerate(GROUPS):
        clauses.extend(pin((0, v), group) for v in vertices)
    return clauses


def internal_pins(spec, group, four_spec=None):
    vertices = GROUPS[group]
    if group == 0:
        # four_spec is already in colours 1, 2.
        for (u, v), colour in four_spec.items():
            yield pin((vertices[u], vertices[v]), colour)
    else:
        pal = palette(group)
        for (u, v), local_colour in spec.items():
            yield pin((vertices[u], vertices[v]), pal[local_colour])


def formula(base, one, two, four_spec):
    return sorted(base + list(internal_pins(one, 1)) + list(internal_pins(two, 2))
                  + list(internal_pins(one, 0, four_spec)))


def main():
    k4 = list(colourings(4))
    k5 = list(colourings(5))
    k6 = list(colourings(6))
    assert (len(k4), len(k5), len(k6)) == (18, 12, 0)

    subsets = []
    for spec in k5:
        for sub in itertools.combinations(range(5), 4):
            induced = {e: c for e, c in spec.items() if set(e) <= set(sub)}
            degrees = {c: sorted(sum(induced[tuple(sorted((v, w)))] == c
                                      for w in sub if w != v) for v in sub)
                       for c in (0, 1)}
            counts = Counter(induced.values())
            assert sorted(counts.values()) == [3, 3]
            assert all(degrees[c] == [1, 1, 2, 2] for c in (0, 1))
            subsets.append(induced)
    assert len(subsets) == 12 * 5

    square_specs = []
    for spec0 in k4:
        counts = Counter(spec0.values())
        if sorted(counts.values()) == [2, 4]:
            matching_colour = next(c for c in (0, 1) if counts[c] == 2)
            matching = [e for e, c in spec0.items() if c == matching_colour]
            assert len({v for edge in matching for v in edge}) == 4
            square_specs.append({edge: colour + 1 for edge, colour in spec0.items()})
    assert len(square_specs) == 6

    # A literal permutation preserves the shape but not the incidental order
    # inside clauses; compare canonical literal and clause order throughout.
    shipped = sorted(tuple(sorted(c)) for c in block.formula(True).clauses)
    base = base_formula()
    assert len(base) == 1799 and len(shipped) == 1825
    four_canonical = {(i, j): (2 if frozenset((i, j)) in SQUARE else 1)
                      for i, j in itertools.combinations(range(4), 2)}
    four_alternative = {edge: (1 if colour == 2 else 2)
                        for edge, colour in four_canonical.items()}

    pentagon_cases = 0
    # Fix one arbitrary square/matching on S. The twelve valid labelled K5
    # colourings already place actual colour 0 on either the cycle or its
    # complement according to the labelled colouring, and the cycle can have
    # any cyclic order/direction. Both groups have palette[0] equal to actual
    # colour 0 (palettes (0,2) and (0,1) respectively). Walking that actual
    # colour-0 C5 gives exactly the canonical pins on all ten internal edges.
    # There is no extra local colour swap here: trying to walk colour 1 in
    # group 2 while relabelling it to palette[0]=0 would change colour names.
    for spec1 in k5:
        for spec2 in k5:
            raw = formula(base, spec1, spec2, four_canonical)
            o1 = cycle_order(spec1, 0, 0)
            o2 = cycle_order(spec2, 0, 0)
            vmap = {v: v for v in range(15)}
            for i, v in enumerate(o1):
                vmap[GROUPS[1][v]] = GROUPS[1][i]
            for i, v in enumerate(o2):
                vmap[GROUPS[2][v]] = GROUPS[2][i]
            assert all(vmap[v] == v for v in GROUPS[0] + (0,))
            image = sorted(renumber(c, vmap, {0: 0, 1: 1, 2: 2}) for c in raw)
            assert image == shipped
            pentagon_cases += 1

    # Exhaust each of the six labelled square/matching assignments. Order its
    # square along the canonical cycle 0-2-1-3-0; its two remaining edges are
    # exactly the opposite diagonals, i.e. the canonical matching.
    four_cases = 0
    for spec in square_specs:
        square_colour = 1 if Counter(spec.values())[1] == 4 else 2
        local = {edge: colour - 1 for edge, colour in spec.items()}
        walk = cycle_order(local, square_colour - 1, 0)
        vmap = {v: v for v in range(15)}
        for actual, canonical in zip(walk, SQUARE_CYCLE):
            vmap[GROUPS[0][actual]] = GROUPS[0][canonical]
        # A fixed canonical pentagon pattern supplies the other groups' pins.
        one = {(i, j): 0 if j - i in (1, 4) else 1
               for i, j in itertools.combinations(range(5), 2)}
        raw = formula(base, one, one, spec)
        # Walking canonical C5 'one' needs no further vertex map in either
        # five-vertex group. If square colour 1 is used instead of 2, also
        # swap colours 1/2 globally together with their two root groups.
        cmap = {0: 0, 1: 1, 2: 2}
        if square_colour == 1:
            for a, b in zip(GROUPS[1], GROUPS[2]):
                vmap[a], vmap[b] = b, a
            cmap = {0: 0, 1: 2, 2: 1}
        assert sorted(renumber(c, vmap, cmap) for c in raw) == shipped
        four_cases += 1

    # The remaining binary choice (matching colour 1 versus 2) is a global swap
    # of colours 1/2 together with the root's corresponding five-vertex groups.
    vmap = {v: v for v in range(15)}
    for a, b in zip(GROUPS[1], GROUPS[2]):
        vmap[a], vmap[b] = b, a
    one = {(i, j): 0 if j - i in (1, 4) else 1
           for i, j in itertools.combinations(range(5), 2)}
    alternative = formula(base, one, one, four_alternative)
    assert sorted(renumber(c, vmap, {0: 0, 1: 2, 2: 1}) for c in alternative) == shipped

    text = 'p cnf %d %d\n' % (block.formula(True).nv, len(shipped)) + ''.join(
        ' '.join(map(str, c)) + ' 0\n' for c in block.formula(True).clauses)
    receipt = {
        'K4_triangle_free_two_colourings': len(k4),
        'K5_triangle_free_two_colourings': len(k5),
        'K6_triangle_free_two_colourings': len(k6),
        'K5_induced_four_subsets_path_plus_path': len(subsets),
        'four_site_raw_square_matchings_normalized': four_cases,
        'both_groups_all_labelled_K5_and_cycle_colour_cases_normalized': pentagon_cases,
        'matching_square_colour_swap_is_canonical': True,
        'normalization_uses_vertex_permutations_only_for_five_groups': True,
        'root_and_cross_group_edges_unchanged_for_five_groups': True,
        'canonical_variables': block.formula(True).nv,
        'canonical_clauses': len(shipped),
        'canonical_sha256': hashlib.sha256(text.encode()).hexdigest(),
    }
    assert receipt['canonical_sha256'] == '9fb32091685b9e3adf1e7e670c3d4333f35b0d12ed6990e968a44b83fb180b01'
    Path(sys.argv[2]).write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
