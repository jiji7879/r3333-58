#!/usr/bin/env python3
"""Whole-byte, solver-independent audit and compact summary of this wall run."""
import hashlib
import json
from pathlib import Path

M = Path(__file__).resolve().parent.parent
R = M / 'results'
I = M / 'inputs'
EXPECTED_PARENT = '90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae'
EXPECTED_WORKING = '39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38'
EXPECTED_CAS = 'dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3'
EXPECTED_POOL = '723e017372164e731ffbe150c0884a7698b851e3ea63a115d08e49290ad56a85'
EXPECTED_CUBES = {(-1413, -1014), (-1413, 1014), (1413, -1417), (1413, 1417)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def read_cubes(path):
    answer = []
    for line in path.read_text().splitlines():
        fields = line.split()
        assert fields[0] == 'a' and fields[-1] == '0'
        answer.append(tuple(map(int, fields[1:-1])))
    return answer


def exact_query(base, cube):
    data = base.read_bytes()
    first, body = data.split(b'\n', 1)
    fields = first.split()
    assert fields[:2] == [b'p', b'cnf'] and len(fields) == 4
    variables, clauses = int(fields[2]), int(fields[3])
    header = f'p cnf {variables} {clauses + len(cube)}\n'.encode()
    units = ''.join(f'{literal} 0\n' for literal in cube).encode()
    return header + body + units


parent = I / 'run/parent.cnf'
working = I / 'run/working.cnf'
cas = I / 'run/cas.drat'
pool_path = I / 'arm-pool.json'
assert sha(parent) == EXPECTED_PARENT
assert sha(working) == EXPECTED_WORKING
assert sha(cas) == EXPECTED_CAS
assert sha(pool_path) == EXPECTED_POOL
pool = load(pool_path)
assert len(pool['variables']) == len(set(pool['variables'])) == 896
assert pool['profile'] == [16, 16, 14, 11]
assert pool['row'] == '06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06'

cube_path = R / 'wall-full20-s2.cubes'
cubes = read_cubes(cube_path)
assert len(cubes) == len(set(cubes)) == 4
assert set(cubes) == EXPECTED_CUBES  # independently fixes root 1413 and children 1014/1417
assert all(abs(v) in set(pool['variables']) for cube in cubes for v in cube)
assert cube_path.read_bytes() == (I / 'baseline/mcts-s2.cubes').read_bytes()
assert set(read_cubes(I / 'baseline/mcts-s10.cubes')) == EXPECTED_CUBES
cover_audit = load(R / 'wall-full20-s2-cover-audit.json')
assert cover_audit['valid_full_binary_cover'] and cover_audit['leaves'] == 4
assert cover_audit['cube_sha256'] == sha(cube_path)

metadata = load(R / 'wall-full20-s2.json')
assert metadata['depth'] == 2 and metadata['sims'] == 2
assert metadata['rollout_horizon'] == 'emitted depth + 20 (STEP_UPPER_BOUND_MCTS)'
assert metadata['pool'] == pool and metadata['leaves'] == 4
assert (M / '.scratch/AlphaMapleSAT/UPSTREAM_COMMIT').read_text().strip() == '215224bb04c46b8c220f413a4c3e64962741812b'

receipts = load(R / 'wall-full20-s2-leaves/receipts.json')
assert len(receipts) == 4 and {tuple(r['cube']) for r in receipts} == EXPECTED_CUBES
for receipt in receipts:
    index = receipt['index']
    cube = tuple(receipt['cube'])
    leaf = R / f'wall-full20-s2-leaves/leaf-{index}'
    parent_query = leaf / 'query-parent.cnf'
    working_query = leaf / 'query-working.cnf'
    # This compares every byte, including the sole header and final unit clauses.
    assert parent_query.read_bytes() == exact_query(parent, cube)
    assert working_query.read_bytes() == exact_query(working, cube)
    assert sha(parent_query) == receipt['query_parent_sha256']
    assert sha(working_query) == receipt['query_working_sha256']
    assert receipt['parent_sha256'] == EXPECTED_PARENT
    assert receipt['working_sha256'] == EXPECTED_WORKING
    assert receipt['cas_prefix_sha256'] == EXPECTED_CAS
    assert receipt['status'] == 'OPEN'
    assert receipt['conflicts_used'] >= 1_000_000
    assert receipt['budget'] == {'conflicts': 1_000_000, 'seconds': 180, 'proof': 'eager'}
    worker = load(leaf / 'worker.stdout')
    assert worker['status'] == 'OPEN' and worker['conflicts_used'] == receipt['conflicts_used']
    assert (leaf / 'worker.stderr').read_bytes() == b''
    assert not list(leaf.glob('*.drat')) and not list(leaf.glob('model.json'))
    assert 'strict_verified' not in receipt and 'proof_sha256' not in receipt
for path in R.rglob('*'):
    if path.is_file():
        assert path.stat().st_size <= 1_000_000_000, f'resource limit: {path}'

prior_shallow = load(I / 'baseline/prior-shallow-leaf-receipts.json')
assert {tuple(r['cube']) for r in prior_shallow} == EXPECTED_CUBES
assert all(r['status'] == 'OPEN' and r['budget']['conflicts'] == 1_000_000 for r in prior_shallow)
greedy = [load(p) for p in sorted((I / 'baseline/greedy-leaves').glob('*.json'))]
assert {tuple(r['cube']) for r in greedy} == {(-1413, -2206), (-1413, 2206), (1413, -1426), (1413, 1426)}
assert all(r['status'] == 'OPEN' and r['budget']['conflicts'] == 1_000_000 for r in greedy)

horizon = load(R / 'mcts-horizon-control.json')
assert horizon['pass'] and [r['max_depth_reached'] for r in horizon['runs']] == [1, 1]
assert horizon['runs'][0]['selected_actions'] == horizon['runs'][1]['selected_actions']
assert sha(M / '.scratch/AlphaMapleSAT/alphamaplesat/MCTS.py') == horizon['source_sha256']

prior_summary = load(I / 'baseline/prior-summary.json')
prior_shallow_cpu = sum(r['cpu_s'] for r in prior_shallow)
prior_shallow_elapsed = sum(r['elapsed_s'] for r in prior_shallow)
assert abs(prior_shallow_cpu - prior_summary['wall']['shallow_mcts']['search_cpu_s']) < 1e-6
greedy_cpu = sum(r['elapsed_s'] for r in greedy)  # old source-plan receipts report elapsed only
assert abs(greedy_cpu - prior_summary['wall']['greedy']['search_cpu_s']) < 1e-6
summary = {
    'schema': 'k58-wall-current-generic-full20-s2/v1',
    'scope': 'CNF decomposition and capped CNF performance only; no physical-colouring inference',
    'target': {
        'row': pool['row'], 'profile': [16, 16, 14, 11], 'charge': 7,
        'parent_sha256': EXPECTED_PARENT, 'working_sha256': EXPECTED_WORKING,
        'cas_prefix_sha256': EXPECTED_CAS, 'candidate_pool_sha256': EXPECTED_POOL,
        'candidate_pool_literals': 896,
    },
    'tools': {
        'k58_massive_solver_zip_sha256': 'cc78f1d9f6f7901615b264c9ceaa3319bd152cd4caccc381a74ed742538bdb6a',
        'baseline_worker_sha256': '5c4ef6727936fc30bd1b60074fd77ca110569a8117f163fdbc95168069645ff9',
        'baseline_worker': 'CaDiCaL 1.9.5 / python-sat 1.9.dev22; same bytes as k58-massive-solver color-resolved-wallcc worker',
        'adapter_sha256': sha(M / 'scripts/ams_tree.py'),
        'current_generic_commit': '215224bb04c46b8c220f413a4c3e64962741812b',
        'current_generic_tree': 'c95924b49d2f46800bf4d9b62ae197fbf8e5023c',
        'mcts_source_sha256': horizon['source_sha256'],
        'leaf_harness_sha256': sha(M / 'scripts/run_leaves.py'),
        'drat_trim_baseline_sha256': 'a9571deb08430a3d7f7a72074440f53e2ad48196dced50b146835052a18e9066',
    },
    'cubing': {
        'configuration': {'depth': 2, 'sims': 2, 'rollout_extra': 20, 'cpuct': 10.0,
                          'limit_top_3': True, 'varpen': 0.0},
        'timeout_cap_seconds': 1200, 'cover_emitted': True,
        'elapsed_s': metadata['elapsed_s'], 'leaves': 4,
        'cube_sha256': sha(cube_path), 'metadata_sha256': sha(R / 'wall-full20-s2.json'),
        'log_sha256': sha(R / 'wall-full20-s2.log'),
        'cover_audit_sha256': sha(R / 'wall-full20-s2-cover-audit.json'),
        'cubes': sorted([list(c) for c in cubes]),
        'same_bytes_as_prior_shallow_s2': True,
        'same_set_as_prior_shallow_s10': True,
    },
    'fresh_leaves': {
        'budget_per_leaf': {'conflicts': 1_000_000, 'seconds': 180, 'proof': 'eager'},
        'status_counts': {'OPEN': 4},
        'conflicts_used_total': sum(r['conflicts_used'] for r in receipts),
        'search_cpu_s_total': sum(r['cpu_s'] for r in receipts),
        'search_elapsed_s_total': sum(r['elapsed_s'] for r in receipts),
        'proofs_produced': 0, 'unsat_claims': 0, 'sat_claims': 0,
        'receipts_sha256': sha(R / 'wall-full20-s2-leaves/receipts.json'),
        'per_leaf': sorted(receipts, key=lambda r: r['cube']),
    },
    'baseline_comparison_at_same_conflict_cap': {
        'greedy_plan': {
            'cubes': sorted([list(r['cube']) for r in greedy]),
            'status_counts': {'OPEN': 4},
            'conflicts_used_total': sum(r['conflicts_used'] for r in greedy),
            'search_elapsed_s_total': greedy_cpu,
        },
        'shallow_mcts': {
            'same_cube_set_as_current': True,
            'status_counts': {'OPEN': 4},
            'conflicts_used_total': sum(r['conflicts_used'] for r in prior_shallow),
            'search_cpu_s_total': prior_shallow_cpu,
            'search_elapsed_s_total': prior_shallow_elapsed,
            'cubing_s2_elapsed_s': load(I / 'baseline/mcts-s2.json')['elapsed_s'],
            'cubing_s10_elapsed_s': load(I / 'baseline/mcts-s10.json')['elapsed_s'],
        },
        'interpretation': 'All three searches are budget-limited OPEN. Identical current/shallow cubes and equal conflict budgets show no decomposition or conflict reduction. Fresh CPU/elapsed differences are not a speedup claim on a shared VM.',
    },
    'structural_negative_result': {
        'statement': 'At a fresh root, two simulations cannot reach the configured 20-step MCTS horizon: simulation 1 initializes Ps and returns; simulation 2 evaluates only the two immediate children of one selected literal. The root choice uses Bsa argmax and has only the literal and its complement with nonzero visits.',
        'actual_log_evidence': 'WARNING:MCTS:NO EXPLORATION!!!!',
        'toy_control_sha256': sha(R / 'mcts-horizon-control.json'),
        'toy_control': 'actual current MCTS.py reached exactly depth 1 for terminal horizons 2 and 22 and chose identically',
        'wall_consequence': 'rollout_extra=20 did not alter root 1413 or either observed second split; full20-s2 cube bytes equal shallow-s2',
    },
    'not_established': [
        'No faster or easier wall decomposition: all new and baseline leaves exhausted the conflict cap.',
        'No per-leaf or parent CNF UNSAT certificate was obtained; no checker was run because no UNSAT proof existed.',
        'No SAT result or model was obtained.',
        'No inference about the exact selective five-leaf refinement beyond its disjoint prior status.',
        'No physical-colouring row closure, profile exclusion, Lemma L, or Ramsey bound. The first-tier parent remains a relaxation whose full semantic assembly is unfinished.',
    ],
}
assert summary['fresh_leaves']['conflicts_used_total'] == 4_000_002
assert sum(r['conflicts_used'] for r in prior_shallow) == 4_000_002
assert sum(r['conflicts_used'] for r in greedy) == 4_000_003
(R / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
print(json.dumps({
    'audit': 'PASS', 'valid_cover_leaves': 4, 'same_bytes_as_shallow_s2': True,
    'fresh_status': {'OPEN': 4}, 'fresh_conflicts': 4_000_002,
    'query_files_whole_byte_checked': 8, 'proofs': 0,
    'two_simulation_root_depth': 1, 'summary_sha256': sha(R / 'summary.json'),
}, sort_keys=True))
