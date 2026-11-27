#!/usr/bin/env python3
"""Joint choices at two vertices of another complete root-colour arm.

This is a local necessary-condition experiment, not a full K58 search. Every
reported local model is a complete assignment on root + two physical arms. The
nominated arm keeps its exact mapped owner CNF and the existing signed rule
bank. Wave A pattern generation is NOT claimed by this version. UNSAT is a
projection-specific, proof-checked status, not an original K58 verdict.
"""

import argparse
import csv
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import time

if not __debug__:
    raise RuntimeError('Do not disable assertions for proof-carrying tools')

from pysat.card import CardEnc
from pysat.formula import CNF
from pysat.solvers import Cadical195
import pysolvers


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def parse_cnf(data):
    lines = data.splitlines()
    header = lines[0].split()
    require(header[:2] == [b'p', b'cnf'], 'noncanonical CNF')
    clauses = [list(map(int, line.split()[:-1])) for line in lines[1:]
               if line and not line.startswith(b'c')]
    require(len(clauses) == int(header[3]), 'clause count mismatch')
    require(all(line[-1] == 0 for line in
                (list(map(int, line.split())) for line in lines[1:]
                 if line and not line.startswith(b'c'))), 'bad DIMACS terminator')
    return int(header[2]), clauses


def serialize(nv, clauses):
    return (f'p cnf {nv} {len(clauses)}\n'.encode() +
            b''.join(' '.join(map(str, c)).encode() + b' 0\n' for c in clauses))


def append_units(data, units):
    nv, clauses = parse_cnf(data)
    return serialize(nv, clauses + [[lit] for lit in units])


def deletion_free(data):
    """Drop only complete binary d records; assert literal-byte canonicality."""
    from compare import without_deletions
    clean, info = without_deletions(data)
    if not info['deletions_removed']:
        require(clean == data, 'unexpected proof rewriting')
    else:
        require(clean != data, 'deletions claimed but proof bytes unchanged')
    return clean, info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', required=True, type=Path)
    parser.add_argument('--checker', required=True, type=Path)
    parser.add_argument('--index', type=int, default=0)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--seconds', type=float, default=2.0)
    parser.add_argument('--max-calls', type=int, default=512)
    parser.add_argument('--second-index', type=int, default=0)
    parser.add_argument('--resume', type=Path,
                        help='reuse only unchanged strict-UNSAT leaves from an earlier compatible query panel')
    args = parser.parse_args()
    require(__debug__, 'assertions are required')
    require(args.max_calls == 512 and args.index == 0,
            'this controlled pilot fixes case 0 and both surviving branch colors')

    runtime = args.runtime.resolve()
    checker = args.checker.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    require(checker.is_file() and checker.stat().st_mode & 0o111, 'checker missing/executable')
    import sys
    sys.path.insert(0, str(runtime))
    import campaign_solver
    from campaign_solver import live_at, strengthened
    from common import family, host, source, units
    from arm_catalog import decode
    from edge_domains import parent
    from new_names import labels
    from timed50 import timed_solve

    rid, pair = live_at(args.index)
    row, arm, T, O = source(rid)
    n = arm['size']
    f = family(row)
    starts = [1]
    for size in f.profile:
        starts.append(starts[-1] + size)
    A = tuple(T + O)
    a_index = next(i for i in range(4) if set(A) == set(range(starts[i], starts[i + 1])))
    require(n == len(A) and len(arm['palette']) == 3, 'wrong nominated physical arm')
    b_index = args.second_index
    require(0 <= b_index < 4 and b_index != a_index, 'second arm must be another root block')
    B = tuple(range(starts[b_index], starts[b_index + 1]))
    vertices = tuple(sorted((0,) + A + B))
    require(len(set(vertices)) == len(vertices), 'root/arms are not disjoint')
    edge, _ = host(58)
    edges = list(combinations(range(58), 2))
    local_edges = list(combinations(vertices, 2))
    edge_indices = {e for e in local_edges}
    local_units = []
    for literal, in units(f, row['placement']):
        e = edges[(abs(literal) - 1) // 4]
        if e in edge_indices:
            local_units.append(literal)

    all_calls = []
    branches = {}
    started = time.perf_counter()
    used = 0
    stopped = False
    old = json.loads(args.resume.read_text()) if args.resume else {'all_calls': []}
    old_by_tag = {r['tag']: r for r in old['all_calls']}
    fresh_local_solver_calls = 0
    rec = campaign_solver.rule(n, pair)
    local_colors = sorted(map(int, rec['branches']))
    require(len(local_colors) == 2, 'expect two surviving local-pivot colours')
    for local_color in local_colors:
        if stopped:
            break
        full, info = strengthened(rid, pair, local_color)
        require(info['row_id'] == rid and tuple(info['pair']) == pair, 'case identity mismatch')
        require(local_color in info['live_colors'] and len(info['live_colors']) == 2,
                'not a two-color live branch')
        original_top, whole = parse_cnf(full)
        whole_set = {frozenset(c) for c in whole}
        # Keep only physical clauses entirely on root+A+B; never truncate a
        # clause involving other vertices. Owner auxiliaries are mapped below.
        filtered = [c for c in whole if all(abs(l) <= 4 * len(edges) and
                                           edges[(abs(l) - 1) // 4] in edge_indices for l in c)]
        # Map the exact local parent through the campaign's verified physical map.
        top_local, local_clauses = parent(n, pair, 'revised')
        lit, image, _, original = __import__('campaign_solver').mapping(rid, n)
        local_map = lambda l: image[l] if l > 0 else -image[-l]
        mapped = [[local_map(l) for l in clause] for clause in local_clauses]
        missing = [c for c in mapped if frozenset(c) not in whole_set]
        require(len(missing) == n * (n - 1) // 2,
                ('unexpected nonliteral owner clauses', len(missing)))
        # The skipped clauses are exactly the three-color ALO rows on A. They
        # are implied by four-color ALO and triangle/root clauses: the root has
        # its missing-palette colour to both endpoints of every A edge.
        positive_units = {c[0] for c in whole if len(c) == 1}
        arm_edges = set(combinations(sorted(A), 2))
        inverse_arm = {image[k]: k for k in range(1, 3 * (n * (n - 1) // 2) + 1)}
        for c in missing:
            require(len(c) == 3 and all(l > 0 for l in c), 'unexpected missing owner/base row')
            require(all(edges[(l - 1) // 4] in arm_edges for l in c),
                    'three-color clause outside nominated arm')
            require(all(l in inverse_arm for l in c), 'not a local three-color variable')
            require(len({(inverse_arm[l] - 1) // 3 for l in c}) == 1 and
                    {(inverse_arm[l] - 1) % 3 for l in c} == {0, 1, 2},
                    'not exactly one local three-color ALO')
            uv = edges[(c[0] - 1) // 4]
            require(len(c) == 3 and all(edges[(l - 1) // 4] == uv for l in c),
                    'not one physical arm edge')
            for endpoint in uv:
                require(edge(0, endpoint, arm['missing_color']) in positive_units,
                        'missing root-triangle palette premise')
        clauses = filtered + [c for c in mapped if frozenset(c) in whole_set]
        top = max([original_top] + [abs(l) for c in clauses for l in c])
        # A local color-degree cap is necessary in a K58 triangle-free coloring,
        # since a color with 17 neighbours gives R(3,3,3)=17 a monochromatic tri.
        for v in vertices:
            for col in range(4):
                incident = [edge(v, w, col) for w in vertices if w != v]
                enc = CardEnc.atmost(incident, 16, top_id=top)
                top = enc.nv
                clauses.extend(enc.clauses)
        base = serialize(top, clauses)
        base_hash = sha(base)
        require(top >= original_top and len(clauses) > 0, 'bad local query')
        # Case-0 pivot: local vertices 0 and 11 map to physical 31,42.
        rec = campaign_solver.rule(n, pair)
        piv = rec['pivot']
        require(piv == [0, 11], ('unexpected pivot mapping', piv))
        pivot_u, pivot_v = A[piv[0]], A[piv[1]]
        require((pivot_u, pivot_v) == (31, 42), ('case 0 pivot mismatch', pivot_u, pivot_v))
        w1, w2 = B[:2]
        # Verify a base model and that its A projection really validates the
        # exact owner convention before any pair experiment.
        def solve(units_now, tag):
            nonlocal used, fresh_local_solver_calls
            require(used < args.max_calls, 'panel budget exceeded')
            used += 1
            query = append_units(base, units_now)
            qpath = out / f'{tag}.cnf'
            qpath.write_bytes(query)
            t0 = time.perf_counter()
            result = {'tag': tag, 'units': units_now, 'query': str(qpath),
                      'query_sha256': base_hash, 'full_query_sha256': sha(query),
                      'variables': top, 'clauses': len(clauses) + len(units_now),
                      'color_local': local_color, 'color_physical': arm['palette'][local_color],
                      'arm': n, 'second_arm': b_index,
                      'u': pivot_u, 'v': pivot_v,
                      'full_parent_sha256': sha(full), 'original_row_sha256': original}
            previous = old_by_tag.get(tag)
            if previous is not None and previous['status'] == 'UNSAT':
                require(previous['full_query_sha256'] == sha(query), 'reused query identity mismatch')
                old_query = Path(previous['query'])
                require(old_query.read_bytes() == query, 'reused query bytes changed')
                old_proof = old_query.with_suffix('.drat')
                require(sha(old_proof.read_bytes()) == previous['proof_sha256'], 'reused proof bytes changed')
                old_log = old_query.with_suffix('.check.log').read_bytes()
                require([line for line in old_log.splitlines() if line.startswith(b's ')] == [b's VERIFIED'] and
                        b'WARNING' not in old_log.upper(), 'reused proof log not strictly verified')
                previous['reused_strict_unsat'] = True
                previous['query'] = str(old_query)
                return previous, None
            fresh_local_solver_calls += 1
            with Cadical195(bootstrap_with=parse_cnf(query)[1], with_proof=True) as sat:
                answer = timed_solve(sat, args.seconds)
                result['seconds'] = time.perf_counter() - t0
                result['stats'] = sat.accum_stats()
                if answer is None:
                    result['status'] = 'UNKNOWN'
                    return result, None
                if answer:
                    model = set(sat.get_model())
                    require(model_ok(parse_cnf(query)[1], model), 'CNF model failed')
                    physical = {}
                    for i, j in local_edges:
                        vals = [c for c in range(4) if edge(i, j, c) in model]
                        require(len(vals) == 1, ('edge coloring not unique', i, j))
                        physical[i, j] = vals[0]
                    mat = lambda i, j: physical[min(i, j), max(i, j)]
                    for i, j, k in combinations(vertices, 3):
                        require(not (mat(i, j) == mat(i, k) == mat(j, k)), 'mono triangle')
                    for v in vertices:
                        for c in range(4):
                            require(sum(mat(v, w) == c for w in vertices if w != v) <= 16,
                                    'local degree cap failed')
                    # Decode local A through its exact local/id mapping and
                    # validate owner/order/pivot, not merely the triangle graph.
                    rawmodel = []
                    for local_id in range(1, 3 * (n * (n - 1) // 2) + 1):
                        val = image[local_id]
                        if val in model:
                            rawmodel.append(local_id)
                        elif -val in model:
                            rawmodel.append(-local_id)
                    arm_string = decode(n, rawmodel)
                    from edge_domains import valid
                    valid(n, pair, 'revised', arm_string)
                    result['arm_string'] = arm_string
                    result['status'] = 'SAT'
                    result['physical_colors'] = [[i, j, c] for (i, j), c in sorted(physical.items())]
                    model_file = out / f'{tag}.model.json'
                    model_file.write_text(json.dumps(result['physical_colors']) + '\n')
                    result['model_file'] = str(model_file)
                    return result, physical
                pysolvers.flushpr(sat.prfp)
                sat.prfile.seek(0)
                rawproof = sat.prfile.read()
                clean, info_proof = deletion_free(rawproof)
                proof_file = out / f'{tag}.drat'
                proof_file.write_bytes(clean)
                result['raw_proof_sha256'] = sha(rawproof)
                result['proof_sha256'] = sha(clean)
                result['proof_normalization'] = info_proof
                with qpath.with_suffix('.check.log').open('wb') as log:
                    check = subprocess.run([str(checker), str(qpath), str(proof_file), '-i', '-U', '-t', '300'],
                                           stdout=log, stderr=subprocess.STDOUT)
                text = qpath.with_suffix('.check.log').read_bytes()
                statuses = [line for line in text.splitlines() if line.startswith(b's ')]
                require(check.returncode == 0 and statuses == [b's VERIFIED'] and b'WARNING' not in text.upper(),
                        'strict proof replay failed')
                result['status'] = 'UNSAT'
                return result, None

        print('BASE PIVOT', pivot_u, pivot_v, 'two second-arm vertices', w1, w2, flush=True)
        base_result, _ = solve([], f'index{args.index}-color{local_color}-base')
        require(base_result.get('reused_strict_unsat') is not True, 'base model was not freshly validated')
        # Base model is optional for this compact pilot; its status still counts.
        # Do not count the extra base call in the declared 512 pair queries.
        used -= 1
        all_calls.append(base_result)
        if base_result['status'] != 'SAT':
            stopped = True
            branches[local_color] = {'base': base_result, 'pairs': []}
            continue
        branch_records = []
        for assigns in product(range(4), repeat=4):
            # (u,w1),(v,w1),(u,w2),(v,w2)
            assumptions = [edge(pivot_u, w1, assigns[0]), edge(pivot_v, w1, assigns[1]),
                           edge(pivot_u, w2, assigns[2]), edge(pivot_v, w2, assigns[3])]
            tag = f'index{args.index}-color{local_color}-{w1}-{w2}-' + ''.join(map(str, assigns))
            result, _ = solve(assumptions, tag)
            all_calls.append(result)
            branch_records.append({'assign': assigns, 'status': result['status'],
                                   'tag': tag, 'units': assumptions,
                                   'full_query_sha256': result['full_query_sha256']})
            if result['status'] == 'UNKNOWN':
                stopped = True
                break
        branches[local_color] = {'base': base_result, 'pairs': branch_records}
    summary = {'schema': 'joint-two-second-arm-vertices/v1',
               'row_id': rid, 'pair': list(pair), 'index': args.index,
               'second_arm_physical': list(B), 'nominated_arm_physical': list(A),
               'local_vertices': len(vertices), 'calls_so_far': used,
               'fresh_local_solver_calls': fresh_local_solver_calls,
               'reused_strict_unsat_calls': sum(bool(r.get('reused_strict_unsat')) for r in all_calls),
               'reused_from': str(args.resume) if args.resume else None,
               'harness_sha256': sha(Path(__file__).read_bytes()),
               'per_call_budget_seconds': args.seconds,
               'branches': branches,
               'all_calls': all_calls,
               'scope': 'Local necessary conditions on root + nominated arm + one other complete root-colour arm. No K58 or Ramsey verdict. Wave A pattern generation is not included; only the existing physical rule bank and owner map.',
               'warning': 'No full-row or global claim is allowed from local SAT or local UNSAT alone; UNSAT here refutes the stated local four-edge query only.'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'row': rid, 'pair': pair, 'calls': used,
                      'branches': {k: {s: sum(p['status'] == s for p in v['pairs'])
                                       for s in ('SAT', 'UNSAT', 'UNKNOWN')}
                                   for k, v in branches.items()}}, indent=2))


def model_ok(clauses, model):
    return all(any(l in model for l in c) for c in clauses)


if __name__ == '__main__':
    main()
