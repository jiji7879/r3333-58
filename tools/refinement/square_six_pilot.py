#!/usr/bin/env python3
"""Bounded matched stock versus square-six direct-wall comparison."""
import argparse
import gzip
import hashlib
from itertools import combinations, product
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools/refinement'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def append_clauses(raw, clauses):
    header, body = raw.split(b'\n', 1)
    tag, cnf, variables, old_count = header.split()
    require((tag, cnf) == (b'p', b'cnf'), 'invalid DIMACS header')
    rows = ''.join(' '.join(map(str, clause)) + (' ' if clause else '') + '0\n'
                   for clause in clauses).encode()
    return f'p cnf {int(variables)} {int(old_count) + len(clauses)}\n'.encode() + body + rows


def append_units(raw, units):
    return append_clauses(raw, [[literal] for literal in units])


def strictly_verified(result):
    statuses = [line for line in result.stdout.splitlines() if line.startswith(b's ')]
    return (result.returncode == 0 and statuses == [b's VERIFIED']
            and b'WARNING' not in result.stdout.upper())


def cube_labels(plan):
    nodes = []
    for bits in product((0, 1), repeat=3):
        node = 'r'
        units = []
        for bit in bits:
            units.append(plan['splits'][node] * (1 if bit else -1))
            node += str(bit)
        nodes.append((node, units))
    require(len(nodes) == 8 and len({tuple(u) for _, u in nodes}) == 8, 'bad depth-three partition')
    return nodes


def check_physical_model(path):
    values = set(map(int, Path(path).read_text().split()))
    colors = {}
    for (u, v) in combinations(range(58), 2):
        hits = [color for color in range(4) if 4 * (u * (115 - u) // 2 + v - u - 1) + color + 1 in values]
        require(len(hits) == 1, ('physical edge missing exactly one colour', u, v))
        colors[u, v] = hits[0]
    for a, b, c in combinations(range(58), 3):
        require(not (colors[a, b] == colors[a, c] == colors[b, c]),
                ('monochromatic physical triangle', a, b, c))


def main():
    require(__debug__, 'use Python with assertions for proof validation')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, type=Path)
    parser.add_argument('--augmented', required=True, type=Path)
    parser.add_argument('--prefix', required=True, type=Path)
    parser.add_argument('--runtime', required=True, type=Path)
    parser.add_argument('--checker', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--prepare-only', action='store_true',
                        help='serialize and hash exact inputs without launching a solver or checker')
    args = parser.parse_args()
    package = args.package.resolve()
    augmented = args.augmented.resolve()
    prefix = args.prefix.resolve()
    runtime = args.runtime.resolve()
    checker = args.checker.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    python = runtime / '.venv/bin/python'
    leaf = REPO / 'tools/refinement/cadical_leaf.py'
    require(all(p.is_file() for p in (python, leaf, checker, prefix, augmented)),
            'required interpreter/checker/prefix/formula missing')
    require(os.access(checker, os.X_OK), 'checker is not executable')
    stock_prefix = (package / 'evidence/stock-prefix.drat').read_bytes()
    require(prefix.read_bytes() == stock_prefix + (package / 'evidence/wedges-prefix.drat').read_bytes(),
            'combined prefix differs from stock-prefix + wedges-prefix')
    require(sha(prefix.read_bytes()) == '6bcc793f59fc3a4e3f4e04c751be03c8bddfc71208fe7f409b7934856d0d3936',
            'wrong combined prefix')
    require(sha(augmented.read_bytes()) == '6267a8fe7ee242ac6aabf18a440cc19686505ea78e269f465ec263a5636d856d',
            'wrong augmented formula')

    original = gzip.decompress((package / 'evidence/parent.cnf.gz').read_bytes())
    study = json.loads((package / 'evidence/study.json').read_text())
    wedges = json.loads((package / 'evidence/wedges.json').read_text())
    plan = json.loads((package / 'evidence/stock-plan.json').read_text())
    require(sha(original) == '33b7898ed58bd1a3a2e088f57d4bc9d01b5397e7b72f1f5f1449a7bf16f4a02a', 'wrong parent')
    require(plan['parent_sha256'] == sha(original), 'wrong cube plan parent')
    short = augmented.read_bytes()
    expected = append_clauses(original, study['stock'] + wedges['clauses'])
    require(short == expected, 'augmentation differs from stock+short formula')
    require(len(study['stock']) == 189 and len(wedges['clauses']) == 1020, 'wrong rule counts')

    queries = []
    (out / 'queries').mkdir()
    for cube, units in cube_labels(plan):
        parent_target = out / 'queries' / f'{cube}-parent.cnf'
        parent_target.write_bytes(append_units(original, units))
        for kind, raw in (('stock', append_clauses(original, study['stock'])), ('short', short)):
            target = out / 'queries' / f'{cube}-{kind}.cnf'
            target.write_bytes(append_units(raw, units))
            queries.append({'cube': cube, 'kind': kind, 'path': target,
                            'parent_path': parent_target,
                            'parent_query_sha256': sha(parent_target.read_bytes()),
                            'query_sha256': sha(target.read_bytes()), 'units': units})
    require(len(queries) == 16 and len({q['query_sha256'] for q in queries}) == 16, 'query duplication')
    input_manifest = [{k: str(v) if isinstance(v, Path) else v for k, v in query.items()}
                      for query in queries]
    (out / 'input-manifest.json').write_text(json.dumps(input_manifest, indent=2) + '\n')
    if args.prepare_only:
        print(json.dumps({'queries': len(queries), 'fresh_physical_calls': 0,
                          'query_directory': str(out / 'queries')}, indent=2))
        return

    records = []
    started = time.perf_counter()
    for index, query in enumerate(queries, 1):
        target = out / f'{index:02d}-{query["cube"]}-{query["kind"]}'
        target.mkdir()
        strict_query = query['path']
        command = [str(python), str(leaf), str(strict_query), str(target / 'leaf'), '3.0', str(runtime)]
        process_started = time.perf_counter()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        cut_off = False
        try:
            output, _ = process.communicate(timeout=25)
        except subprocess.TimeoutExpired:
            cut_off = True
            os.killpg(process.pid, signal.SIGKILL)
            output, _ = process.communicate()
        (target / 'worker.log').write_bytes(output)
        document = {'cube': query['cube'], 'kind': query['kind'], 'units': query['units'],
                    'query': str(strict_query), 'query_sha256': query['query_sha256'],
                    'original_parent_query': str(query['parent_path']),
                    'original_parent_query_sha256': query['parent_query_sha256'],
                    'cut_off': cut_off, 'returncode': process.returncode,
                    'process_wall_seconds': time.perf_counter() - process_started,
                    'command': command, 'worker_output': output.decode(errors='replace')}
        if cut_off:
            document['status'] = 'OPEN_UNKNOWN'
        else:
            require(process.returncode == 0, (index, process.returncode, document['worker_output'][-500:]))
            receipt = json.loads((target / 'leaf/leaf.json').read_text())
            require(receipt['query_sha256'] == query['query_sha256'], 'leaf/input identity mismatch')
            document.update(receipt)
            if receipt['status'] == 'UNKNOWN':
                require(receipt['decision_unknown_after_budget'], 'unexplained UNKNOWN verdict')
                document['status'] = 'OPEN_UNKNOWN'
            elif receipt['status'] == 'SAT':
                require(receipt['model_satisfies_query'], 'model is not a full CNF model')
                model_file = target / 'leaf/model.txt'
                assert model_file.is_file()
                check_physical_model(model_file)
                document['status'] = 'VERIFIED_SAT'
            else:
                require(receipt['status'] == 'UNSAT', 'unexpected solver status')
                proof_file = target / 'leaf/proof.drat'
                require(proof_file.is_file(), 'UNSAT result has no proof bytes')
                from compare import without_deletions
                raw_proof = proof_file.read_bytes()
                normalized, info = without_deletions(raw_proof)
                checked_proof = target / 'leaf/proof-nodeletions.drat'
                checked_proof.write_bytes(normalized)
                document['proof_normalization'] = {
                    'raw_proof_sha256': sha(raw_proof), 'raw_proof_bytes': len(raw_proof),
                    'normalized_proof_sha256': sha(normalized),
                    'normalized_proof_bytes': len(normalized), **info}
                require(info['deletions_removed'] == 0 or raw_proof != normalized,
                        'proof deletion normalization unexpectedly preserved bytes')
                checks = []
                for label, cnf, candidate in (
                        ('exact-leaf', strict_query, normalized),
                        ('original-parent', query['parent_path'],
                         (stock_prefix if query['kind'] == 'stock' else prefix.read_bytes()) + normalized)):
                    check_file = target / f'{label}.drat'
                    check_file.write_bytes(candidate)
                    t = time.perf_counter()
                    completed = subprocess.run([str(checker), str(cnf), str(check_file), '-i', '-U', '-t', '300'],
                                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=310)
                    good = strictly_verified(completed)
                    (target / f'{label}-check.log').write_bytes(completed.stdout)
                    checks.append({'label': label, 'verified': good,
                                   'status_lines': [line.decode(errors='replace') for line in completed.stdout.splitlines()
                                                    if line.startswith(b's ')],
                                   'warning_count': completed.stdout.upper().count(b'WARNING'),
                                   'returncode': completed.returncode,
                                   'flags': ['-i', '-U', '-t', '300'],
                                   'seconds': time.perf_counter() - t,
                                   'query_sha256': sha(cnf.read_bytes()),
                                   'proof_sha256': sha(check_file.read_bytes())})
                document['strict_checks'] = checks
                require(all(c['verified'] for c in checks), ('strict leaf/original proof failed', checks))
                document['status'] = 'VERIFIED_UNSAT'
        (target / 'receipt.json').write_text(json.dumps(document, indent=2, sort_keys=True) + '\n')
        records.append(document)
        print(index, query['cube'], query['kind'], document['status'], flush=True)

    statuses_by_kind = {
        kind: {status: sum(record['kind'] == kind and record['status'] == status
                           for record in records)
               for status in sorted({record['status'] for record in records})}
        for kind in ('stock', 'short')}
    summary = {'schema': 'square-six-wall-pilot/v1', 'row': plan['origin']['id'],
               'parent_sha256': sha(original), 'augmented_sha256': sha(short),
               'stock_prefix_sha256': sha(stock_prefix),
               'prefix_sha256': sha(prefix.read_bytes()),
               'checker_sha256': sha(checker.read_bytes()), 'leaf_sha256': sha(leaf.read_bytes()),
               'input_manifest_sha256': sha((out / 'input-manifest.json').read_bytes()),
               'fresh_physical_calls': len(records),
               'per_call_search_seconds': 3.0, 'declared_search_seconds_total': 48.0,
               'actual_search_seconds_total': sum(record.get('search_seconds', 0.0) for record in records),
               'actual_process_wall_seconds_total': sum(record['process_wall_seconds'] for record in records),
               'actual_wall_seconds_total': time.perf_counter() - started,
               'statuses_by_kind': statuses_by_kind,
               'whole_row_closed_by_eight_verified_cubes': {
                   kind: sum(record['kind'] == kind and record['status'] == 'VERIFIED_UNSAT'
                             for record in records) == 8
                   for kind in ('stock', 'short')},
               'records': records,
               'scope': 'Matched per-cube 3-second observations, not a supported speedup claim. Every unfinished or failed leaf blocks whole-row UNSAT; OPEN means UNKNOWN, not a proof verdict or a Ramsey conclusion.'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'calls': len(records), 'actual_search_seconds': summary['actual_search_seconds_total'],
                      'statuses': {status: sum(record['status'] == status for record in records)
                                   for status in sorted({record['status'] for record in records})}}, indent=2))


if __name__ == '__main__':
    main()
