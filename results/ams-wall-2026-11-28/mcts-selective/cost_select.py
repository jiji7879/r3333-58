#!/usr/bin/env python3
"""Pre-registered two-sided capped-conquest selection over an AMS shortlist.

Only variable ordering is heuristic. Both signs are always emitted/probed. No
proof or SAT/UNSAT conclusion is drawn from an OPEN probe.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def write_query(base, cube, out):
    with Path(base).open('rb') as src:
        first = src.readline().split()
        if len(first) != 4 or first[:2] != [b'p', b'cnf']:
            raise ValueError('expected a DIMACS header on line one')
        nv, nc = int(first[2]), int(first[3])
        with Path(out).open('wb') as dst:
            dst.write(f'p cnf {nv} {nc + len(cube)}\n'.encode())
            shutil.copyfileobj(src, dst, 1 << 20)
            for lit in cube:
                dst.write(f'{lit} 0\n'.encode())


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--label', required=True)
    p.add_argument('--upstream', type=Path, required=True)
    p.add_argument('--cnf', type=Path, required=True, help='working CNF')
    p.add_argument('--parent', type=Path, required=True, help='original parent, for binding only')
    p.add_argument('--pool-json', type=Path, required=True)
    p.add_argument('--worker', type=Path, required=True)
    p.add_argument('--prefix', required=True, help='comma-separated signed literals; empty allowed')
    p.add_argument('--mcts-choice', type=int, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--conflicts', type=int, default=20000)
    p.add_argument('--seconds', type=int, default=60)
    p.add_argument('--shortlist', type=int, default=3)
    p.add_argument('--max-literals', type=int, default=6612)
    args = p.parse_args()
    if args.shortlist != 3 or args.conflicts != 20000:
        raise ValueError('this reproduction implements the pre-registered top3/20000 policy')
    args.out.mkdir(parents=True, exist_ok=False)
    prefix = [] if not args.prefix else [int(x) for x in args.prefix.split(',')]
    if len({abs(x) for x in prefix}) != len(prefix) or any(x == 0 for x in prefix):
        raise ValueError('invalid prefix')
    if args.mcts_choice in prefix or -args.mcts_choice in prefix:
        raise ValueError('MCTS split is already fixed')
    upstream = args.upstream.resolve()
    source_dir = upstream / 'alphamaplesat'
    sys.path.insert(0, str(source_dir))
    # Offline stubs come from PYTHONPATH; no network logger is used.
    from pysat.formula import CNF
    from ksgraph.EvalVarCalc import MarchPysatPropagate, Node
    pool_doc = json.loads(args.pool_json.read_text())
    if pool_doc.get('schema') != 'ams-k58-split-pool/v1' or pool_doc['max_literals'] != args.max_literals:
        raise ValueError('wrong split-pool schema/action space')
    pool = pool_doc['variables']
    if len(pool) != len(set(pool)) or any(type(v) is not int or not 1 <= v <= args.max_literals for v in pool):
        raise ValueError('invalid pool')
    allowed = set(pool)

    def restricted_freevars(self, binary_implications):
        if self.m != args.max_literals:
            raise RuntimeError('unexpected action-space size')
        return list(pool)
    MarchPysatPropagate.construct_freevars = restricted_freevars

    structure_started = time.monotonic()
    cpu_before = resource.getrusage(resource.RUSAGE_SELF)
    cnf = CNF(from_file=str(args.cnf.resolve()))
    propagator = MarchPysatPropagate(cnf=cnf, m=args.max_literals)
    res, assigned, scores = propagator.propagate(Node(prior_actions=prefix[:]))
    if res != 1 or not scores:
        raise RuntimeError('prefix has no ordinary shortlist; not manufacturing a split')
    ranked = [v for v, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)]
    shortlist = ranked[:args.shortlist]
    if args.mcts_choice not in allowed:
        raise ValueError('MCTS choice outside recorded pool')
    candidates = [args.mcts_choice] + [v for v in shortlist if v != args.mcts_choice]
    if len(candidates) > 3 or args.mcts_choice not in shortlist:
        raise RuntimeError(f'MCTS choice {args.mcts_choice} not in its top3 shortlist {shortlist}')
    cpu_after = resource.getrusage(resource.RUSAGE_SELF)
    commit = subprocess.check_output(['git', '-C', str(upstream), 'rev-parse', 'HEAD'], text=True).strip()
    structure = {
        'schema': 'k58-capped-conquest-shortlist/v1', 'label': args.label,
        'prefix': prefix, 'shortlist_bcp_order': shortlist,
        'candidate_order_mcts_first': candidates, 'mcts_choice': args.mcts_choice,
        'scores_in_shortlist_order': {str(v): scores[v] for v in shortlist},
        'pool_size': len(pool), 'pool_sha256': sha(args.pool_json),
        'upstream_commit': commit, 'upstream_sha_note': 'unmodified current-generic source copied to this member directory',
        'working_sha256': sha(args.cnf), 'parent_sha256': sha(args.parent),
        'assigned_physical_literal_count_at_prefix': assigned,
        'structure_elapsed_s': time.monotonic() - structure_started,
        'structure_self_cpu_s': (cpu_after.ru_utime - cpu_before.ru_utime) + (cpu_after.ru_stime - cpu_before.ru_stime),
        'selection_key': '(OPEN child count, exact sum of conflicts_used, candidate order)',
        'probe': {'conflicts': args.conflicts, 'seconds_each': args.seconds, 'proof': 'off'},
    }
    (args.out / 'structure.json').write_text(json.dumps(structure, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'shortlist': shortlist, 'candidates': candidates, 'prefix': prefix}), flush=True)

    receipts = []
    for position, var in enumerate(candidates):
        for sign in (-1, 1):
            lit = sign * var
            cube = prefix + [lit]
            attempt = args.out / f'candidate-{position}-{lit}'
            attempt.mkdir()
            query = attempt / 'query-working.cnf'
            write_query(args.cnf, cube, query)
            cmd = [sys.executable, str(args.worker.resolve()), str(query.resolve()), str(attempt.resolve()),
                   str(args.conflicts), 'search']
            started = time.monotonic()
            before = resource.getrusage(resource.RUSAGE_CHILDREN)
            timed_out = False
            try:
                run = subprocess.run(cmd, capture_output=True, timeout=args.seconds)
            except subprocess.TimeoutExpired as exc:
                timed_out = True
                run = None
                stdout = exc.stdout or b''
                stderr = exc.stderr or b''
            after = resource.getrusage(resource.RUSAGE_CHILDREN)
            elapsed = time.monotonic() - started
            if run is not None:
                stdout, stderr = run.stdout, run.stderr
            (attempt / 'worker.stdout').write_bytes(stdout)
            (attempt / 'worker.stderr').write_bytes(stderr)
            if run is not None and run.returncode:
                raise RuntimeError(f'worker failed for {cube}: {stderr[-1000:]!r}')
            if timed_out:
                result = {'status': 'OPEN', 'conflicts_used': args.conflicts, 'reason': 'wall-time cap'}
            else:
                result = json.loads(stdout)
            proof = attempt / 'leaf.drat'
            if proof.exists():
                if proof.stat().st_size > 1_000_000_000:
                    raise RuntimeError('individual proof exceeded 1GB resource cap')
                proof.unlink()
            rec = {
                'label': args.label, 'candidate_position': position, 'split': var, 'literal': lit,
                'cube': cube, 'status': result['status'], 'conflicts_used': result['conflicts_used'],
                'elapsed_s': elapsed,
                'cpu_s': (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime),
                'query_working_sha256': sha(query), 'working_sha256': structure['working_sha256'],
                'parent_sha256': structure['parent_sha256'], 'proof_sha256': None,
                'evidence_scope': 'performance probe only; OPEN is neither SAT nor UNSAT',
                'budget': {'conflicts': args.conflicts, 'seconds': args.seconds, 'proof': 'off'},
            }
            if result['status'] == 'SAT':
                rec['status'] = 'SAT_UNVERIFIED'
            receipts.append(rec)
            (args.out / 'probe-receipts.json').write_text(json.dumps(receipts, indent=2, sort_keys=True) + '\n')
            print(json.dumps({k: rec[k] for k in ('split', 'literal', 'status', 'conflicts_used', 'elapsed_s', 'cpu_s')}), flush=True)

    evaluations = []
    for position, var in enumerate(candidates):
        rows = [r for r in receipts if r['split'] == var]
        if len(rows) != 2:
            raise RuntimeError('both signs were not probed')
        opens = sum(r['status'] == 'OPEN' for r in rows)
        cost = sum(r['conflicts_used'] for r in rows)
        evaluations.append({'split': var, 'candidate_position': position, 'open_children': opens,
                            'conflicts_sum': cost, 'elapsed_s': sum(r['elapsed_s'] for r in rows),
                            'cpu_s': sum(r['cpu_s'] for r in rows), 'key': [opens, cost, position]})
    winner = min(evaluations, key=lambda row: row['key'])
    selected = winner['split']
    children = [prefix + [-selected], prefix + [selected]]
    with (args.out / 'selected.cubes').open('w') as stream:
        for cube in children:
            stream.write('a ' + ' '.join(map(str, cube)) + ' 0\n')
    best_pair = min(row['key'][:2] for row in evaluations)
    tied = [row for row in evaluations if row['key'][:2] == best_pair]
    # Post-run display-only fix: the frozen run used 'winner position == 0'
    # here, which also marked a unique MCTS-candidate win as a tie. Selection
    # itself always used min(key) above and is unchanged. The exact run source
    # is preserved as inputs/cost-select-run.py.
    used_mcts_tiebreak = len(tied) > 1 and winner['candidate_position'] == 0
    result = {
        'schema': 'k58-capped-conquest-selection/v1', 'label': args.label,
        'prefix': prefix, 'candidates': candidates, 'selected_split': selected,
        'winner_key': winner['key'], 'evaluations': evaluations,
        'all_candidates_fully_open': all(row['open_children'] == 2 for row in evaluations),
        'tie_broken_by_preregistered_mcts_order': used_mcts_tiebreak,
        'probe_conflicts_total': sum(r['conflicts_used'] for r in receipts),
        'probe_elapsed_s_total': sum(r['elapsed_s'] for r in receipts),
        'probe_cpu_s_total': sum(r['cpu_s'] for r in receipts),
        'structure_elapsed_s': structure['structure_elapsed_s'],
        'structure_self_cpu_s': structure['structure_self_cpu_s'],
        'selected_cube_sha256': sha(args.out / 'selected.cubes'),
        'working_sha256': structure['working_sha256'], 'parent_sha256': structure['parent_sha256'],
        'upstream_commit': commit, 'mcts_choice': args.mcts_choice,
        'note': 'selection is a CNF-performance heuristic only; no physical-colouring conclusion',
    }
    (args.out / 'selection.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
