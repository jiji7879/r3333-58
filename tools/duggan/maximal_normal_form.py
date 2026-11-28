#!/usr/bin/env python3
"""Existence-preserving maximal-colour normal form for a frozen K58 row.

Research prototype. The semantic normal form is not a DRAT implication of the
original parent. See the emitted JSON scope and the exhaustive finite control.
"""
import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path



def sha(data):
    return hashlib.sha256(data).hexdigest()


def family_of(row, Family):
    fields = dict(row['family'])
    for key in ('profile', 'root_kinds'):
        fields[key] = tuple(fields[key])
    return Family(**fields)


def lit_edge(lit):
    return (abs(lit) - 1) // 4


def build(row_id, arms, colour, output, package):
    package = package.resolve()
    sys.path.insert(0, str(package / 'color-resolved-wallcc'))
    sys.path.insert(0, str(package / 'color-resolved-wallcc/frozen'))
    from problem import lookup, row_formula, encode_clauses
    from gluing import Family, host, units
    from dense import marked_threshold
    row = lookup(row_id)
    family = family_of(row, Family)
    lit, base = host(58)
    fixed = units(family, row['placement'])
    extra = marked_threshold(family, fixed, row['charge'], tables=True,
                             total_critical=True, full_root=False)
    original = row_formula(row, 'first')
    maximum = max(4 * 58 * 57 // 2,
                  max((abs(x) for c in fixed + extra for x in c), default=0))
    reconstructed = (f'p cnf {maximum} {len(base) + len(fixed) + len(extra)}\n'.encode()
                     + encode_clauses(base + fixed + extra))
    assert reconstructed == original, 'semantic reconstruction differs from ordinary parent'

    fixed_edges = {lit_edge(c[0]) for c in fixed if len(c) == 1}
    # A fixed positive unit also fixes all other colours through the host
    # exactly-one constraints. Exclude any edge mentioned by a fixed unit.
    configurable = []
    start = 1
    groups = []
    for size in family.profile:
        groups.append(tuple(range(start, start + size)))
        start += size
    for a in arms:
        assert 0 <= a < 4
        for u, v in itertools.combinations(groups[a], 2):
            eid = lit_edge(lit(u, v, 0))
            if eid not in fixed_edges:
                configurable.append((a, u, v))
    assert len({(u, v) for _, u, v in configurable}) == len(configurable)
    modvars = {x for _, u, v in configurable for x in range(4 * lit_edge(lit(u, v, 0)) + 1,
                                                             4 * lit_edge(lit(u, v, 0)) + 5)}
    assert not any(abs(x) in modvars for c in fixed for x in c)
    assert not any(abs(x) in modvars for c in extra for x in c), \
        'normalisation would change a threshold/support clause'

    assert all(a != colour for a in arms), 'normalisation colour must differ from every selected arm'
    top = maximum
    additions = []
    receipt_rules = []
    # One target colour over the union of arms is essential: later recolouring
    # only adds colour-c paths and cannot invalidate an earlier normal form.
    c = colour
    for aa, u, v in configurable:
            a = aa
            witnesses = []
            for w in range(58):
                if w in (u, v):
                    continue
                top += 1
                y = top
                left, right = lit(u, w, c), lit(v, w, c)
                additions.extend(([-y, left], [-y, right], [y, -left, -right]))
                witnesses.append(y)
            additions.append([lit(u, v, c), *witnesses])
            receipt_rules.append({'arm': a, 'colour': c, 'edge': [u, v],
                                  'witness_variables': len(witnesses)})
    augmented = (f'p cnf {top} {len(base) + len(fixed) + len(extra) + len(additions)}\n'.encode()
                 + encode_clauses(base + fixed + extra + additions))
    # Removing the new header and new suffix must reproduce the exact baseline.
    assert augmented.split(b'\n', 1)[1][:len(original.split(b'\n', 1)[1])] == original.split(b'\n', 1)[1]
    output.write_bytes(augmented)
    meta = {
        'schema': 'k58-maximal-colour-normal-form-pilot/v1',
        'row': row['id'], 'profile': family.profile, 'arms': arms, 'colour': colour,
        'ordinary_parent_sha256': sha(original), 'ordinary_parent_bytes': len(original),
        'augmented_sha256': sha(augmented), 'augmented_path': str(output),
        'original_variables': maximum, 'augmented_variables': top,
        'original_clauses': len(base) + len(fixed) + len(extra),
        'added_clauses': len(additions), 'configurable_edges': len(configurable),
        'rules': receipt_rules,
        'semantic_invariants': [
            'fixed unit/threshold/support suffix contains no configurable-edge variable',
            'only internal edges of root arm a are recoloured, and only to c != a',
            'root profiles, cross edges and every sender-degree candidate are unchanged',
            'each recolouring has no global c-path, so no c-triangle is created',
            'other colour classes only lose edges, so they remain triangle-free',
            'a non-c configurable edge keeps any existing global c-path during later steps',
        ],
        'scope': ('research augmentation: equi-satisfiability follows from the separate '
                  'finite/normal-form argument, NOT from DRAT consequence; no original-row '
                  'closure is asserted by a timeout or by this builder'),
    }
    return meta


def colourings4():
    edges = list(itertools.combinations(range(4), 2))
    for values in itertools.product(range(4), repeat=len(edges)):
        M = [[0] * 4 for _ in range(4)]
        for (u, v), c in zip(edges, values):
            M[u][v] = M[v][u] = c
        good = all(not (M[u][v] == M[u][w] == M[v][w])
                   for u, v, w in itertools.combinations(range(4), 3))
        if good:
            yield edges, M


def normalise_small(M, edges, fixed, arms, c):
    M = [row[:] for row in M]
    before = [row[:] for row in M]
    F = [(u, v) for u, v in edges if u != 0 and v != 0
         and before[0][u] == before[0][v] and before[0][u] in arms
         and (u, v) not in fixed]
    for u, v in F:
        if M[u][v] == c:
            continue
        witness = any(w not in (u, v) and M[u][w] == c == M[v][w] for w in range(4))
        if not witness:
            M[u][v] = M[v][u] = c
    for u, v, w in itertools.combinations(range(4), 3):
        assert not (M[u][v] == M[u][w] == M[v][w]), 'created a monochromatic triangle'
    for u, v in edges:
        if (u, v) in fixed or (u, v) not in F:
            assert M[u][v] == before[u][v], 'changed an immutable edge'
    for u, v in F:
        assert M[u][v] == c or any(w not in (u, v) and M[u][w] == c == M[v][w]
                                  for w in range(4)), 'normal form not reached'
    # Sender degrees in every relevant root-arm colour are unchanged.
    for x in range(1, 4):
        a = before[0][x]
        if a in arms:
            assert sum(M[x][y] == a for y in range(4) if y != x) == \
                   sum(before[x][y] == a for y in range(4) if y != x)
    return F


def exhaustive_control():
    checked_models = 0
    checked_runs = 0
    configurable = 0
    for edges, M in colourings4():
        checked_models += 1
        for mask in range(1 << len(edges)):
            fixed = {e for i, e in enumerate(edges) if mask >> i & 1}
            for c in range(4):
                arms = tuple(a for a in range(4) if a != c)
                F = normalise_small(M, edges, fixed, arms, c)
                configurable += len(F)
                checked_runs += 1
    return {'order': 4, 'good_colourings': checked_models,
            'fixed_assignment_subsets_per_model': 64,
            'normalisation_runs': checked_runs,
            'configurable_edges_processed': configurable,
            'result': 'PASS'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--package', type=Path, help='unpacked k58-massive-solver directory')
    ap.add_argument('--row', default='06861a3df60c')
    ap.add_argument('--arms', default='2,3')
    ap.add_argument('--colour', type=int, default=0)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--metadata', type=Path)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        result = exhaustive_control()
        print(json.dumps(result, indent=2))
        return
    assert args.output and args.metadata and args.package, \
        '--package, --output and --metadata are required unless --selftest is used'
    arms = [int(x) for x in args.arms.split(',')]
    meta = build(args.row, arms, args.colour, args.output, args.package)
    args.metadata.write_text(json.dumps(meta, indent=2) + '\n')
    short = dict(meta)
    short.pop('rules')
    print(json.dumps(short, indent=2))


if __name__ == '__main__':
    main()
