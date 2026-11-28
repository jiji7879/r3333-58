#!/usr/bin/env python3
"""Directly re-evaluate the two local models, their clause sets and root groups."""
import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT / 'next'))
import block
import sharp

records = {}
for name, formula, module, n, filename in [
        ('K15_path_boundary', block.formula(False), block, 15, 'path-model.json'),
        ('K14_square_sharpness', sharp.small(), sharp, 14, 'matching-K14.json')]:
    source = module.HERE / filename
    raw_bytes = source.read_bytes()
    values = json.loads(raw_bytes)
    if name.startswith('K14'):
        model = {module.lit(u, v, c) for u, v, c in values}
    else:
        model = set(values)
    assert all(any(literal in model if literal > 0 else -literal not in model
                   for literal in clause)
               for clause in formula.clauses)
    edges = list(itertools.combinations(range(n), 2))
    colours = {edge: next(c for c in range(3) if module.lit(*edge, c) in model)
               for edge in edges}
    assert all(colours[a, b] != colours[b, c] or colours[a, b] != colours[a, c]
               for a, b, c in itertools.combinations(range(n), 3))
    groups = [range(1, 5), range(5, 10), range(10, 15)] if n == 15 else [
        range(1, 5), range(5, 9), range(9, 14)]
    for colour, group in enumerate(groups):
        assert all(colours[tuple(sorted((0, v)))] == colour for v in group)
    if name.startswith('K14'):
        values = json.loads(raw_bytes)
        assert len(values) == n * (n - 1) // 2
        assert {(u, v) for u, v, c in values} == set(edges)
        assert all(c in range(3) for u, v, c in values)
    sites = {1, 2, 3, 4}
    degrees = {colour: sorted(sum(colours[tuple(sorted((v, w)))] == colour
                                 for w in sites if v != w)
                               for v in sites)
               for colour in range(3)}
    per_site_degrees = {colour: [sum(colours[tuple(sorted((v, w)))] == colour
                                    for w in sites if v != w)
                                 for v in sites]
                         for colour in range(3)}
    assert {sum(per_site_degrees[c][i] for c in range(3)) for i in range(4)} == {3}
    degrees = {colour: sorted(per_site_degrees[colour]) for colour in range(3)}
    print(name, 'computed_degrees', degrees)
    assert degrees[0] == [0, 0, 0, 0]
    if name.startswith('K14'):
        assert degrees[1] == [1, 1, 1, 1]
        assert degrees[2] == [2, 2, 2, 2]
    records[name] = {
        'sha256': hashlib.sha256(raw_bytes).hexdigest(),
        'model_literal_count': len(model),
        'edge_count': len(edges),
        'every_clause_of_exact_formula_satisfied': True,
        'full_edge_colour_map_reconstructed': True,
        'triangle_free': True,
        'root_group_sizes': [len(group) for group in groups],
        'root_group_colours_verified': True,
        'designated_four_site_degrees_by_colour': degrees,
    }

proof_bytes = (block.HERE / 'matching.drat.gz').read_bytes()
proof = __import__('gzip').decompress(proof_bytes)
records['shared_K15_matching_proof'] = {
    'sha256': hashlib.sha256(proof).hexdigest(),
    'raw_bytes': len(proof),
    'warning_suppressed_checker_used': False,
    'status': 'one exact s VERIFIED, zero warnings/errors, RAT lemma count zero',
    'proof_bytes_fully_read': True,
}
assert records['shared_K15_matching_proof']['sha256'] == '4ca7a5d302ceadc4afb5d8d54e4f9c3d5613f48cf08681fe0461a05acb6085d7'
assert len(proof) == 470852
Path(sys.argv[2]).write_text(json.dumps(records, indent=1) + '\n')
print(json.dumps(records, indent=1))
