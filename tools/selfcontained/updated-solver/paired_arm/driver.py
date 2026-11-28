#!/usr/bin/env python3
"""Experimental paired-arm tooling on the 1,300 historical full-root parents.

These are NOT the open K58 wall profiles.  Every generation requires an exact
hash match.  A generated CNF, SAT proof of an augmented formula or a local
benchmark is not silently promoted to an original-parent proof or a general
speedup.  Use `certify` to test one chosen false cube against the exact stock
parent with strict native original-parent replay.
"""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import sys

MODULE = Path(__file__).resolve().parent
ROOT = MODULE.parent
WORK = MODULE / 'work'
SOURCE = MODULE / 'source'
sys.path.insert(0, str(WORK))
PY = sys.executable


def require_new(path):
    path = path.resolve()
    if path.exists():
        raise ValueError(f'refusing to overwrite {path}')
    return path


def call(script, *args, cwd=None, extra_env=None):
    env = dict(os.environ)
    env['K58_HARD_STUDY'] = str(SOURCE / 'hard-study')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    if extra_env:
        env.update(extra_env)
    command = [PY, str(WORK / script), *map(str, args)]
    print('+', ' '.join(command), flush=True)
    import subprocess
    result = subprocess.run(command, cwd=cwd, env=env)
    if result.returncode:
        raise RuntimeError(f'{script} failed with exit {result.returncode}')


def finite_check():
    """Verify the abstract two5/cap model without reusing a research log."""
    triples = []
    for guard in (False, True):
        for support in itertools.product(range(6), repeat=3):
            if guard and sum(support) < 14:
                continue
            full = [i for i, n in enumerate(support) if n >= 5]
            q = set(full[:2] if guard else [])
            assert all((i not in q or support[i] >= 5) for i in range(3))
            if guard:
                assert all(q & {i, j} for i, j in itertools.combinations(range(3), 2))
            triples.append((guard, support))
    assert len([g for g, _ in triples if g]) == sum(
        1 for n in itertools.product(range(6), repeat=3) if sum(n) >= 14)
    k5 = k6 = 0
    edges = list(itertools.combinations(range(6), 2))
    triangles = list(itertools.combinations(range(6), 3))
    for bits in range(1 << 15):
        color = dict(zip(edges, [(bits >> i) & 1 for i in range(15)]))
        if all(len({color[tuple(sorted(e))] for e in itertools.combinations(t, 2)}) > 1
               for t in triangles):
            k6 += 1
    candidates = []
    for bits in range(1 << 10):
        color = dict(zip(list(itertools.combinations(range(5), 2)),
                         [(bits >> i) & 1 for i in range(10)]))
        if all(len({color[tuple(sorted(e))] for e in itertools.combinations(t, 2)}) > 1
               for t in itertools.combinations(range(5), 3)):
            k5 += 1
            if len([e for e, c in color.items() if c == 0]) == 5:
                candidates.append(color)
    assert k5 == 12 and k6 == 0 and candidates
    return {'status': 'PASS', 'K5_triangle_free_two_colourings': k5,
            'K6_triangle_free_two_colourings': k6,
            'K6_binary_colourings_checked': 32768,
            'abstract_selector_extensions': len(triples),
            'total_13_counterexample': (5, 4, 4),
            'scope': 'abstract/full historical guard cap; no cohort performance or production certificate claim'}


def parent_for_generated(rank, generated):
    """Identify the exact source object(s) stored by a selection or two5 build."""
    rank = int(rank)
    generated = generated.resolve()
    if generated.suffix == '.json' and generated.name == 'manifest.json':
        data = json.loads(generated.read_text())
        return data['input_sha256'], 'paired-arm historical full_root parent'
    with generated.with_suffix('.json').open() as stream:
        data = json.load(stream)
    assert data['rank'] == rank
    return data['original_sha256'], 'hash-bound guarded-support lower-bound parent'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('export-stock', help='export one exact historical stock parent for certification')
    e.add_argument('--rank', type=int, required=True)
    e.add_argument('--out', type=Path, required=True)
    b = sub.add_parser('build', help='generate a named augmented parent')
    b.add_argument('--family', choices=('short', 'wide_delta', 'four_only', 'transversal',
                                        'two5', 'arm', 'pair', 'distribution', 'joint-support'), required=True)
    b.add_argument('--rank', type=int, required=True)
    b.add_argument('--out', type=Path, required=True)
    b.add_argument('--max-width', type=int, default=6)
    b.add_argument('--sender-color', type=int, default=3)
    b.add_argument('--query-conflicts', type=int, default=200000)
    b.add_argument('--scope', choices=('all', 'marked', 'critical'), default='all')
    t = sub.add_parser('run', help='bounded wallcc on an explicitly supplied generated CNF')
    t.add_argument('--cnf', type=Path, required=True)
    t.add_argument('--out', type=Path, required=True)
    t.add_argument('--depth', type=int, default=1)
    t.add_argument('--jobs', type=int, default=1)
    t.add_argument('--conflicts', type=int, default=200000)
    t.add_argument('--seconds', type=int, default=60)
    v = sub.add_parser('verify-selection', help='finite guard/support tests on a short/wide-delta panel')
    v.add_argument('--selection', type=Path, required=True)
    v.add_argument('--out', type=Path, required=True)
    sub.add_parser('finite-check', help='independent K5/K6 and selector extension controls')
    c = sub.add_parser('certify', help='strict original-parent replay of a chosen clause false cube')
    c.add_argument('--rank', type=int, required=True)
    c.add_argument('--clause', required=True)
    c.add_argument('--stock', type=Path, required=True)
    c.add_argument('--out', required=True)
    c.add_argument('--checker', type=Path, required=True)
    c.add_argument('--cadical', type=Path)
    c.add_argument('--engine', choices=('cadical', 'kissat'), default='kissat')
    c.add_argument('--conflicts', type=int, default=60000)
    c.add_argument('--seconds', type=int, default=280)
    args = ap.parse_args()
    if getattr(args, 'ranks', None) is not None:
        assert all(1 <= int(r) <= 1300 for r in args.ranks.split(','))
    assert 1 <= getattr(args, 'rank', 1) <= 1300
    if args.cmd == 'export-stock':
        call('export_original.py', '--rank', args.rank, '--out', args.out)
        return
    if args.cmd == 'finite-check':
        print(json.dumps(finite_check(), indent=2, sort_keys=True))
        return
    if args.cmd == 'verify-selection':
        call('audit_selection.py', '--selection', args.selection, '--out', args.out)
        return
    if args.cmd == 'certify':
        call('certify_clause.py', '--rank', args.rank, '--clause=' + args.clause,
             '--stock', args.stock, '--out', args.out, '--checker', args.checker,
             '--conflicts', args.conflicts,
             '--seconds', args.seconds, '--engine', args.engine)
        return
    if args.cmd == 'run':
        assert args.depth >= 1 and args.jobs >= 1 and args.conflicts >= 1 and args.seconds >= 1
        import subprocess
        env = dict(os.environ)
        env['PYTHONPATH'] = str(ROOT / 'wallcc' / 'frozen')
        env['TMPDIR'] = str(args.out.resolve().parent / (args.out.name + '-tmp'))
        args.out.resolve().parent.mkdir(parents=True, exist_ok=True)
        Path(env['TMPDIR']).mkdir(parents=True, exist_ok=True)
        command = [PY, str(ROOT / 'wallcc' / 'wallcc.py'), 'run', '--cnf',
                   str(args.cnf.resolve()), '--out', str(args.out.resolve()),
                   '--depth', str(args.depth), '--jobs', str(args.jobs),
                   '--conflicts', str(args.conflicts), '--seconds', str(args.seconds),
                   '--proof', 'deferred', '--checker', str(ROOT / 'bin/drat-trim')]
        result = subprocess.run(command, env=env)
        if result.returncode:
            raise RuntimeError(f'bounded external wallcc failed with exit {result.returncode}')
        return
    out = require_new(args.out)
    rank, family = args.rank, args.family
    if family in ('short', 'wide_delta', 'four_only'):
        call('generate_selection.py', '--ranks', rank, '--out', out)
        manifest = json.loads((out / str(rank) / 'manifest.json').read_text())
        query = manifest['files'][family]
        print(json.dumps({'rank': rank, 'family': family,
                          'input_sha256': manifest['input_sha256'],
                          'query': str(out / str(rank) / (family + '.cnf')),
                          'query_sha256': query['sha256'],
                          'scope': 'conditional original-variable paired clauses; solve this with bounded wallcc/DIMACS, no whole-row inference'}, indent=2))
    elif family == 'joint-support':
        assert args.query_conflicts > 0 and -1 <= args.sender_color <= 3
        out.mkdir(parents=True)
        call('joint_support.py', '--package', SOURCE / 'hard-study', '--rank', rank,
             '--sender-color', args.sender_color, '--query-conflicts', args.query_conflicts,
             '--out', out / str(rank))
        info = json.loads((out / str(rank) / 'summary.json').read_text())
        print(json.dumps({'rank': rank, 'family': family, 'id': info['row_id'],
                          'original_parent_sha256': info['regenerated_parent_sha256'],
                          'new_original_variable_clauses': info['new_original_variable_clauses'],
                          'query_totals': info['query_totals'],
                          'scope': 'induced-parent UNSAT counts only; SAT/OPEN discarded; no template universality'}, indent=2))
    elif family == 'transversal':
        out.mkdir(parents=True)
        assert args.max_width >= 1
        call('transversal_encoding.py', '--source', SOURCE / 'hard-study', '--ranks', rank, '--out', out / 'all')
        call('filter_transversals.py', '--source', SOURCE, '--transversals', out / 'all',
             '--out', out / 'filtered', '--ranks', rank, '--max-width', args.max_width,
             '--propagation-solver', 'minisat')
        info = json.loads((out / 'filtered' / str(rank) / 'filter.json').read_text())
        print(json.dumps({'rank': rank, 'family': family, 'output': str(out / 'filtered'),
                          'scope': 'historical parent with published plus UP-surviving short transversals; no universal speedup', **info['queries']}, indent=2))
    else:
        mode = 'two5' if family == 'two5' else family
        args.cnf = out / f'{rank}-{family}.cnf'
        call('two5_encoder.py', rank, '--mode', mode, '--encoding', 'seq',
             '--scope', args.scope, '--out', args.cnf)
        info = json.loads(args.cnf.with_suffix('.json').read_text())
        print(json.dumps({'rank': rank, 'family': family, 'query': str(args.cnf),
                          'augmented_sha256': info['augmented_sha256'],
                          'original_sha256': info['original_sha256'],
                          'scope': 'aux-extended historical parent; not a monolithic original-parent proof'}, indent=2))


if __name__ == '__main__':
    main()
