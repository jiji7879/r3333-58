#!/usr/bin/env python3
"""Independently check depth-two binary cube covers (no solver/status trust)."""
import argparse
import json
from pathlib import Path


def read_cubes(path):
    cubes = []
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        fields = line.split()
        if not fields or fields[0] != 'a' or fields[-1] != '0':
            raise ValueError(f'{path}:{lineno}: invalid cube line')
        cube = list(map(int, fields[1:-1]))
        if len(cube) != len({abs(v) for v in cube}) or any(v == 0 for v in cube):
            raise ValueError(f'{path}:{lineno}: repeated/contradictory variable')
        cubes.append(cube)
    return cubes


def audit(cubes, pool):
    allowed = set(pool)
    if any(v not in allowed for cube in cubes for v in map(abs, cube)):
        raise ValueError('cube variable outside recorded split pool')
    # Check a genuine full binary tree by recursive complementary partitioning.
    def visit(items, depth):
        if not items:
            raise ValueError('missing cube')
        if all(not cube for cube in items):
            if len(items) != 1:
                raise ValueError('duplicate leaf')
            return 1
        if any(not cube for cube in items):
            raise ValueError('leaf/internal node overlap')
        roots = {cube[0] for cube in items}
        positives = {v for v in roots if v > 0}
        if len(roots) != 2 or len(positives) != 1 or -next(iter(positives)) not in roots:
            raise ValueError('node children are not complementary literals')
        root = next(iter(positives))
        left = [cube[1:] for cube in items if cube[0] == root]
        right = [cube[1:] for cube in items if cube[0] == -root]
        return visit(left, depth + 1) + visit(right, depth + 1)
    leaves = visit(sorted(cubes), 0)
    if leaves != len(cubes):
        raise ValueError('cover leaf count mismatch')
    return {'schema': 'ams-k58-cover-audit/v1', 'valid_full_binary_cover': True,
            'leaves': leaves, 'depth': max(map(len, cubes)),
            'cubes': sorted(cubes)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('cubes', type=Path)
    p.add_argument('pool_json', type=Path)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    pool_doc = json.loads(args.pool_json.read_text())
    if pool_doc['schema'] != 'ams-k58-split-pool/v1':
        raise ValueError('wrong pool schema')
    result = audit(read_cubes(args.cubes), pool_doc['variables'])
    result['cube_sha256'] = __import__('hashlib').sha256(args.cubes.read_bytes()).hexdigest()
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'valid': True, 'leaves': result['leaves'], 'depth': result['depth']}))
if __name__ == '__main__':
    main()
