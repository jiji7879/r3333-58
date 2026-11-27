#!/usr/bin/env python3
"""Learn one conditional joint second-arm clause per exact case-0 branch.

The candidate C(w1,w2) is [-E(31,w1,2), -E(42,w1,1), -E(42,w2,1)].
I run the exact full branch plus its three opposite edge-colour units. UNSAT,
with strict DRAT replay, proves that the exact branch entails C. A SAT model
would negate the candidate; UNKNOWN is not used as a learned clause.

This deliberately does not claim a one-line RUP prefix, a wave-A transfer or
any full child/row refutation. The certificate is for C under the exact branch,
not a clause lifted to a different parent. Production state is never modified.
"""
import argparse
import hashlib
from itertools import combinations
import json
from pathlib import Path
import subprocess
import time

if not __debug__:
    raise RuntimeError('Assertions are required for proof handling')

from compare import without_deletions


def strip_four_units(raw):
    """Remove the four edge pins already audited in a packaged joint query."""
    header, body = raw.split(b'\n', 1)
    tag, cnf, nv, clauses = header.split()
    assert (tag, cnf) == (b'p', b'cnf')
    lines = body.splitlines()
    assert len(lines) >= 4
    return f'p cnf {int(nv)} {int(clauses)-4}\n'.encode() + b'\n'.join(lines[:-4]) + b'\n'


def model_is_valid(receipt, model_file):
    values = set(map(int, model_file.read_text().split()))
    colors = {}
    for u, v in combinations(range(58), 2):
        found = [c for c in range(4) if 4*(u*(115-u)//2+v-u-1)+c+1 in values]
        assert len(found) == 1
        colors[u,v] = found[0]
    assert len(colors) == 1653
    for u,v,w in combinations(range(58), 3):
        assert not (colors[u,v] == colors[u,w] == colors[v,w])
    return True


def strict(checker, query, proof):
    with proof.with_suffix('.log').open('wb') as f:
        run = subprocess.run([str(checker), str(query), str(proof), '-i', '-U', '-t', '300'],
                             stdout=f, stderr=subprocess.STDOUT, timeout=310)
    text = proof.with_suffix('.log').read_bytes()
    status = [line for line in text.splitlines() if line.startswith(b's ')]
    assert run.returncode == 0 and status == [b's VERIFIED'] and b'WARNING' not in text.upper(), \
        ('proof replay failed', proof, text[-500:])
    return {'query_sha256': hashlib.sha256(query.read_bytes()).hexdigest(), 'proof_sha256': hashlib.sha256(proof.read_bytes()).hexdigest(),
            'flags': ['-i', '-U', '-t', '300'], 'status_lines': ['s VERIFIED'], 'warnings': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', required=True, type=Path)
    parser.add_argument('--child-cnfs', required=True, type=Path,
                        help='directory containing the audited physical full-parent inputs color1-0.cnf/color2-0.cnf')
    parser.add_argument('--checker', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--seconds', type=float, default=1.0)
    parser.add_argument('--all-second-vertices', action='store_true')
    args = parser.parse_args()
    assert args.seconds <= 1.0, 'keep initial bounded clause-learning tests at at most one second each'
    base = args.child_cnfs.resolve()
    assert base.is_dir()
    args.out.mkdir(parents=True, exist_ok=False)
    args.checker = args.checker.resolve()
    assert args.checker.is_file() and (args.checker.stat().st_mode & 0o111)
    runtime = args.runtime.resolve()
    import sys
    sys.path.insert(0, str(runtime))
    from common import host, sha, source
    from campaign_solver import live_at
    leaf = Path(__file__).with_name('cadical_leaf.py').absolute()
    rid, pair = live_at(0)
    row, arm, pentagon, outside = source(rid)
    A = tuple(pentagon + outside)
    assert arm['size'] == 14 and A[0] == 31 and A[11] == 42 and arm['palette'] == [1,0,3]
    literal, _ = host(58)
    u, v = A[0], A[11]
    second_arm = list(range(1, 16))
    candidates = [(1, w) for w in second_arm if w != 1] if args.all_second_vertices else [(1, 2)]
    records = []
    events = args.out / 'ledger.jsonl'
    started = time.perf_counter()
    for local_color, expected_hash in (
        (1, 'f7e6f5b2cb5a95bf65c16c730f7c4e10bd359b3d413d031bcbf9dd180dd5ff8d'),
        (2, 'e85234ab42705601f1b83a2e6127ecb89dea669ba78865f35ea57e47815ece7a')):
        source_cnf = base / f'color{local_color}-0.cnf'
        parent = strip_four_units(source_cnf.read_bytes())
        assert sha(parent) == expected_hash, ('exact case 0 child identity mismatch', local_color)
        for w1, w2 in candidates:
            assert w1 != w2 and w1 in second_arm and w2 in second_arm
            goal = [-literal(u,w1,2), -literal(v,w1,1), -literal(v,w2,1)]
            hypothesis = [-lit for lit in goal]
            header, body = parent.split(b'\n', 1)
            _, _, nv, nc = header.split()
            query_data = f'p cnf {int(nv)} {int(nc)+3}\n'.encode() + body + b''.join(
                f'{lit} 0\n'.encode() for lit in hypothesis)
            tag = f'branch{local_color}-w1-{w1}-w2-{w2}'
            query = args.out / (tag + '.cnf')
            query.write_bytes(query_data)
            record = {'tag': tag, 'row_id': rid, 'pair': list(pair), 'u': u, 'v': v,
                      'w1': w1, 'w2': w2, 'branch_local_color': local_color,
                      'physical_pivot_color': arm['palette'][local_color],
                      'goal_clause': goal, 'negating_units': hypothesis,
                      'parent_sha256': sha(parent), 'query_sha256': sha(query_data),
                      'scope': 'Clause C is entailed if its negation is verified UNSAT on this exact branch; scoped logical entailment, not a prefix or global rule.'}
            target = args.out / (tag + '-leaf')
            t0 = time.perf_counter()
            cmd = [str(runtime/'.venv/bin/python'), str(leaf), str(query), str(target), str(args.seconds), str(runtime)]
            run = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
            record['process_wall_seconds'] = time.perf_counter() - t0
            record['worker_output'] = run.stdout + run.stderr
            assert run.returncode == 0 and (target/'leaf.json').is_file(), record
            receipt = json.loads((target/'leaf.json').read_text())
            assert receipt['query_sha256'] == record['query_sha256']
            record['receipt'] = str(target/'leaf.json')
            if receipt['status'] == 'UNKNOWN':
                record['status'] = 'OPEN_UNKNOWN'
                record['search_seconds'] = receipt['search_seconds']
            elif receipt['status'] == 'SAT':
                assert receipt['model_satisfies_query'] and model_is_valid(receipt, target/'model.txt')
                record['status'] = 'CANDIDATE_REFUTED_BY_FULL_PARENT_MODEL'
                record['search_seconds'] = receipt['search_seconds']
                record['model'] = str(target/'model.txt')
            else:
                assert receipt['status'] == 'UNSAT'
                raw = (target/'proof.drat').read_bytes()
                normalized, info = without_deletions(raw)
                clean = target/'proof-nodeletions.drat'
                clean.write_bytes(normalized)
                record['proof_normalization'] = {'raw_proof_sha256': sha(raw), **info}
                record['check'] = {'clean_proof_sha256': sha(clean.read_bytes())}
                record['strict_replay'] = strict(args.checker, query, clean)
                record['status'] = 'VERIFIED_CLAUSE_ENTAILED'
                record['search_seconds'] = receipt['search_seconds']
            for key in ('stats',):
                record[key] = receipt.get(key)
            with events.open('a') as f:
                f.write(json.dumps(record, sort_keys=True) + '\n')
            records.append(record)
            print(tag, record['status'], 'conflicts', receipt['stats']['conflicts'], flush=True)
            # A concrete model would disprove the candidate clause; do not continue
            # promoting that candidate family without examining it.
            if record['status'] == 'CANDIDATE_REFUTED_BY_FULL_PARENT_MODEL':
                break
    summary = {'schema': 'joint-clause-learning/v1', 'row_id': rid,
               'case_scope': 'exact case-0 full branch plus the three named negating units; no model or closure of unstrengthened parent inferred',
               'clause_schema': '[-E(u,w1,2), -E(v,w1,1), -E(v,w2,1)], u=31,v=42; w1,w2 second-arm vertices, distinct',
               'per_call_seconds': args.seconds, 'records': records,
               'actual_wall_seconds': time.perf_counter()-started,
               'counts': {s:sum(r['status']==s for r in records) for s in sorted({r['status'] for r in records})},
               'whole_branch_closed': False}
    (args.out/'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'calls':len(records), 'counts':summary['counts'],
                      'actual_search_seconds': sum(r['search_seconds'] for r in records),
                      'wall_seconds': summary['actual_wall_seconds']}, indent=2))


if __name__ == '__main__':
    main()
