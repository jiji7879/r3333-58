#!/usr/bin/env python3
"""Independent receipt/byte audit and arithmetic for the frozen A/B."""
import hashlib
import json
from pathlib import Path
import re

from audit_cubes import audit, read_cubes

ROOT = Path('.')
OUT = ROOT / 'results'
EXPECTED = {
    'wall_parent': '90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae',
    'wall_working': '39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38',
    'wall_cas': 'dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3',
    'control_parent': '50a187c65b7a5a9c839a95053a7e1133bbf697aa3806790d87b83bd1e7a65530',
    'control_working': '356fd5ce1472e9ef078288032f7a1e3ceb885cc32af331abc766a6fea92bc269',
    'control_cas': 'ce64dbfe40c45bc82c8aa742e3caba5e50b6200dec62648f414598f6f64da856',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def expected_query(base, cube):
    data = Path(base).read_bytes()
    first, rest = data.split(b'\n', 1)
    fields = first.split()
    assert len(fields) == 4 and fields[:2] == [b'p', b'cnf']
    header = f'p cnf {int(fields[2])} {int(fields[3]) + len(cube)}\n'.encode()
    return header + rest + b''.join(f'{lit} 0\n'.encode() for lit in cube)


def check_query(base, cube, query, expected_hash):
    actual = Path(query).read_bytes()
    assert actual == expected_query(base, cube), f'query bytes differ: {query}'
    assert hashlib.sha256(actual).hexdigest() == expected_hash
    return len(actual)


def time_file(path):
    text = Path(path).read_text()
    match = re.search(r'elapsed=([0-9.]+) cpu_user=([0-9.]+) cpu_sys=([0-9.]+)', text)
    assert match, path
    elapsed, user, system = map(float, match.groups())
    return {'command_elapsed_s': elapsed, 'command_cpu_s': user + system}


def normalized_selection(folder):
    selection = load(Path(folder) / 'selection.json')
    rows = load(Path(folder) / 'probe-receipts.json')
    cap = 20000
    evaluated = []
    for position, var in enumerate(selection['candidates']):
        children = [r for r in rows if r['split'] == var]
        assert len(children) == 2 and {r['literal'] for r in children} == {var, -var}
        opens = sum(r['status'] == 'OPEN' for r in children)
        # At an OPEN cap, conflicts_used is not a conquest measurement. Replace
        # scheduler-dependent cap overshoot by the same cap for every child.
        cost = sum(cap if r['status'] == 'OPEN' else r['conflicts_used'] for r in children)
        evaluated.append({'split': var, 'candidate_position': position,
                          'open_children': opens, 'normalized_conflicts_sum': cost,
                          'key_without_order': [opens, cost]})
    best_pair = min(r['key_without_order'] for r in evaluated)
    tied = [r for r in evaluated if r['key_without_order'] == best_pair]
    winner = tied[0]
    return {
        'diagnostic_status': 'post-hoc correction of cap-overshoot metric; not a replacement for raw frozen run',
        'normalization': 'OPEN child cost = exactly 20000; decided child cost = conflicts_used',
        'evaluations': evaluated, 'selected_split': winner['split'],
        'mcts_tie_break_used': len(tied) > 1 and winner['candidate_position'] == 0,
        'tied_candidates_at_best_key': [r['split'] for r in tied],
        'raw_frozen_selected_split': selection['selected_split'],
        'raw_probe_conflicts_total': selection['probe_conflicts_total'],
    }


def main():
    # Exact original inputs and the target-unit working input.
    bindings = {
        'wall_parent': Path('inputs/source-plan/parent.cnf'),
        'wall_working': Path('inputs/source-plan/working.cnf'),
        'wall_cas': Path('inputs/source-plan/cas.drat'),
        'control_parent': Path('inputs/control/parent.cnf'),
        'control_working': Path('inputs/control/working.cnf'),
        'control_cas': Path('inputs/control/cas.drat'),
    }
    for name, path in bindings.items():
        assert sha(path) == EXPECTED[name]
    target = Path('inputs/wall-target/working.cnf')
    assert target.read_bytes() == expected_query(bindings['wall_working'], [1413, -1417])
    target_sha = sha(target)

    byte_checks = {'final_queries': [], 'probe_queries': [], 'proofs': []}
    control_run = Path('inputs/control')
    control_rows = load('results/control-cost20k-final-leaves/receipts.json')
    assert len(control_rows) == 4
    for i, rec in enumerate(control_rows):
        leaf = Path(f'results/control-cost20k-final-leaves/leaf-{i}')
        assert rec['status'] == 'CHECKED_UNSAT' and rec['strict_verified'] is True
        assert rec['parent_sha256'] == EXPECTED['control_parent']
        assert rec['working_sha256'] == EXPECTED['control_working']
        size = check_query(control_run / 'parent.cnf', rec['cube'], leaf / 'query.cnf', rec['query_sha256'])
        byte_checks['final_queries'].append({'cube': rec['cube'], 'bytes': size, 'sha256': rec['query_sha256']})
        for field, name in [('proof_sha256', 'leaf.drat'), ('joined_sha256', 'joined.drat'),
                            ('normalized_proof_sha256', 'joined.additions-only.drat')]:
            path = leaf / name
            assert path.stat().st_size <= 1_000_000_000
            assert sha(path) == rec[field]
            byte_checks['proofs'].append({'cube': rec['cube'], 'name': name,
                                          'bytes': path.stat().st_size, 'sha256': rec[field]})
        log = (leaf / 'strict-replay.log').read_bytes().replace(b'\r', b'\n')
        lines = log.decode(errors='strict').splitlines()
        assert rec['checker_returncode'] == 0
        assert lines.count('s VERIFIED') == 1 and 's NOT VERIFIED' not in lines
        assert not any('WARNING' in line or 'ERROR' in line for line in lines)
        assert any(re.search(r'\bc 0 RAT lemmas in core;', line) for line in lines)
        assert rec['checker_warning_or_error'] is False

    wall_by_policy = {}
    for policy, row_label in [('cost20k', 'wall-positive-cost20k'), ('shallow', 'wall-positive-shallow-s10')]:
        rows = load(f'results/wall-positive-recube/{policy}-final-leaves/receipts.json')
        assert len(rows) == 2
        for i, rec in enumerate(rows):
            assert rec['label'] == row_label and rec['status'] == 'OPEN'
            assert rec['parent_sha256'] == EXPECTED['wall_parent'] and rec['working_sha256'] == target_sha
            leaf = Path(f'results/wall-positive-recube/{policy}-final-leaves/leaf-{i}')
            size = check_query('inputs/source-plan/parent.cnf', rec['cube'], leaf / 'query.cnf', rec['query_sha256'])
            byte_checks['final_queries'].append({'cube': rec['cube'], 'bytes': size, 'sha256': rec['query_sha256']})
            assert not (leaf / 'leaf.drat').exists()
        wall_by_policy[policy] = rows

    for label, base in [('control-neg-cost20k', bindings['control_working']),
                        ('control-pos-cost20k', bindings['control_working']),
                        ('wall-positive-cost20k', target)]:
        folder = {'control-neg-cost20k': 'results/control-cost20k/neg',
                  'control-pos-cost20k': 'results/control-cost20k/pos',
                  'wall-positive-cost20k': 'results/wall-positive-recube/cost20k'}[label]
        rows = load(Path(folder) / 'probe-receipts.json')
        assert len(rows) == 6
        for rec in rows:
            assert rec['label'] == label and rec['proof_sha256'] is None
            query = Path(folder) / f"candidate-{rec['candidate_position']}-{rec['literal']}" / 'query-working.cnf'
            size = check_query(base, rec['cube'], query, rec['query_working_sha256'])
            byte_checks['probe_queries'].append({'label': label, 'cube': rec['cube'],
                                                'bytes': size, 'sha256': rec['query_working_sha256']})

    # Independent re-audit of the exact full binary covers.
    cover_checks = {}
    for name, cubes, pool in [
        ('control-cost20k', 'results/control-cost20k-selected.cubes', 'inputs/control/arm-pool.json'),
        ('wall-cost20k', 'results/wall-positive-recube/cost20k-frontier.cubes', 'inputs/prior/arm-pool.json'),
        ('wall-shallow', 'results/wall-positive-recube/shallow-frontier.cubes', 'inputs/prior/arm-pool.json')]:
        parsed = read_cubes(Path(cubes))
        report = audit(parsed, load(pool)['variables'])
        assert report['valid_full_binary_cover']
        cover_checks[name] = {'leaves': len(parsed), 'depth': max(map(len, parsed)),
                              'cube_sha256': sha(cubes), 'valid_full_binary_cover': True}

    normalized = {
        'control-negative': normalized_selection('results/control-cost20k/neg'),
        'control-positive': normalized_selection('results/control-cost20k/pos'),
        'wall-positive': normalized_selection('results/wall-positive-recube/cost20k'),
    }
    assert normalized['control-negative']['selected_split'] == 4937
    assert normalized['control-positive']['selected_split'] == 4149
    assert normalized['wall-positive']['selected_split'] == 1426
    assert normalized['wall-positive']['raw_frozen_selected_split'] == 2744

    neg, pos = load('results/control-cost20k/neg/selection.json'), load('results/control-cost20k/pos/selection.json')
    final_conflicts = sum(r['conflicts_used'] for r in control_rows)
    final_elapsed = sum(r['elapsed_s'] for r in control_rows)
    final_cpu = sum(r['cpu_s'] for r in control_rows)
    prior = load('inputs/prior-results/summary.json')
    mcts2_cubing = load('inputs/control/mcts-full20-s2-original-metadata.json')['elapsed_s']
    structure_elapsed = neg['structure_elapsed_s'] + pos['structure_elapsed_s']
    structure_cpu = neg['structure_self_cpu_s'] + pos['structure_self_cpu_s']
    probe_elapsed = neg['probe_elapsed_s_total'] + pos['probe_elapsed_s_total']
    probe_cpu = neg['probe_cpu_s_total'] + pos['probe_cpu_s_total']
    probe_conflicts = neg['probe_conflicts_total'] + pos['probe_conflicts_total']
    prep = mcts2_cubing + structure_elapsed + probe_elapsed
    control_summary = {
        'parent_sha256': EXPECTED['control_parent'], 'working_sha256': EXPECTED['control_working'],
        'cas_sha256': EXPECTED['control_cas'], 'selected_splits': {'negative': 4937, 'positive': 4149},
        'cover': cover_checks['control-cost20k'],
        'fresh_final': {'leaves': 4, 'status': '4/4 CHECKED_UNSAT', 'conflicts': final_conflicts,
                        'search_elapsed_s_component_sum': final_elapsed, 'search_cpu_s': final_cpu,
                        'strict_replay': '4/4 return 0, one s VERIFIED, no warnings/errors, zero RAT'},
        'new_preparation': {'cached_actual_full20_two_sim_cubing_elapsed_s': mcts2_cubing,
                            'new_shortlist_elapsed_s': structure_elapsed, 'new_shortlist_cpu_s': structure_cpu,
                            'new_probe_elapsed_s': probe_elapsed, 'new_probe_cpu_s': probe_cpu,
                            'new_probe_conflicts': probe_conflicts, 'total_elapsed_s_component_sum': prep},
        'new_preparation_plus_final_search_elapsed_s': prep + final_elapsed,
        'all_capped_probe_plus_final_conflicts': probe_conflicts + final_conflicts,
        'old_greedy': {'prepare_s': 0.72, 'final_conflicts': 226881,
                       'search_cpu_s': prior['control']['greedy']['search_cpu_s'],
                       'search_elapsed_s': prior['control']['greedy']['search_elapsed_s']},
        'old_actual_full20_two_sim': {'cubing_s': mcts2_cubing, 'final_conflicts': 309710,
                                      'tree': '4793/4149', 'search_cpu_s': prior['control']['shallow_mcts']['search_cpu_s'],
                                      'search_elapsed_s': prior['control']['shallow_mcts']['search_elapsed_s']},
        'old_actual_full20_ten_sim': {'cubing_s': 306.4564173449762, 'final_conflicts': 284528,
                                      'tree': '4937/4149', 'search_cpu_s': prior['control']['full20_mcts']['search_cpu_s'],
                                      'search_elapsed_s': prior['control']['full20_mcts']['search_elapsed_s']},
        'derived': {
            'final_conflicts_vs_greedy': final_conflicts / 226881,
            'final_conflict_reduction_vs_actual_two_sim': 1 - final_conflicts / 309710,
            'preparation_speedup_vs_actual_ten_sim': 306.4564173449762 / prep,
            'caveat': 'component sums combine separately measured runs; one control instance, all policy and checking costs must be considered'},
    }

    shallow_cubing = load('results/wall-positive-recube/shallow-s10.json')['elapsed_s']
    full_cubing = load('results/wall-positive-recube/full20-s2.json')['elapsed_s']
    wall_selection = load('results/wall-positive-recube/cost20k/selection.json')
    raw_final_elapsed = sum(r['elapsed_s'] for r in wall_by_policy['cost20k'])
    raw_final_cpu = sum(r['cpu_s'] for r in wall_by_policy['cost20k'])
    shallow_final_elapsed = sum(r['elapsed_s'] for r in wall_by_policy['shallow'])
    shallow_final_cpu = sum(r['cpu_s'] for r in wall_by_policy['shallow'])
    raw_prep = full_cubing + wall_selection['structure_elapsed_s'] + wall_selection['probe_elapsed_s_total']
    raw_command_cpu = sum(time_file(p)['command_cpu_s'] for p in [
        'results/wall-positive-recube/full20-s2.time', 'results/wall-positive-recube/cost20k.time',
        'results/wall-positive-recube/cost20k-final.time'])
    shallow_command_cpu = sum(time_file(p)['command_cpu_s'] for p in [
        'results/wall-positive-recube/shallow.time', 'results/wall-positive-recube/shallow-final.time'])
    wall_summary = {
        'row': '06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06',
        'profile': [16, 16, 14, 11], 'charge': 7, 'subtree_prefix': [1413, -1417],
        'parent_sha256': EXPECTED['wall_parent'], 'original_working_sha256': EXPECTED['wall_working'],
        'cas_sha256': EXPECTED['wall_cas'], 'target_working_sha256': target_sha,
        'upstream_commit': '215224bb04c46b8c220f413a4c3e64962741812b',
        'cubing': {'shallow_ten_sim': {'split': 1426, 'elapsed_s': shallow_cubing},
                   'full20_two_sim': {'split': 1426, 'elapsed_s': full_cubing, 'completed_cover': True}},
        'raw_frozen_cost_policy': {
            'shortlist_bcp_order': [2744, 1222, 1426], 'candidate_order_mcts_first': [1426, 2744, 1222],
            'all_six_probe_children': 'OPEN', 'selected_split_only_by_cap_overshoot': 2744,
            'probe_conflicts': 120002, 'preparation_elapsed_s_component_sum': raw_prep,
            'final': {'status': '2/2 OPEN at 1000000 conflicts', 'search_elapsed_s': raw_final_elapsed,
                      'search_cpu_s': raw_final_cpu},
            'preparation_plus_final_elapsed_s': raw_prep + raw_final_elapsed,
            'whole_command_cpu_s_including_cubing_and_final': raw_command_cpu,
            'cover': cover_checks['wall-cost20k']},
        'matched_shallow_policy': {
            'split': 1426, 'preparation_elapsed_s': shallow_cubing,
            'final': {'status': '2/2 OPEN at 1000000 conflicts', 'search_elapsed_s': shallow_final_elapsed,
                      'search_cpu_s': shallow_final_cpu},
            'preparation_plus_final_elapsed_s': shallow_cubing + shallow_final_elapsed,
            'whole_command_cpu_s_including_cubing_and_final': shallow_command_cpu,
            'cover': cover_checks['wall-shallow']},
        'single_run_mixed_timing': {
            'raw_end_to_end_elapsed_ratio_over_shallow': (raw_prep + raw_final_elapsed) / (shallow_cubing + shallow_final_elapsed),
            'raw_final_cpu_ratio_over_shallow': raw_final_cpu / shallow_final_cpu,
            'raw_whole_cpu_ratio_over_shallow': raw_command_cpu / shallow_command_cpu,
            'interpretation': 'no repeatable speedup established; all outcomes capped OPEN'},
        'post_hoc_cap_normalization_selects': normalized['wall-positive']['selected_split'],
        'semantic_scope': 'ordinary-parent CNF performance only; no per-leaf wall proof and no physical-colouring result',
    }

    measured_command_files = [
        'results/control-cost20k/neg.time', 'results/control-cost20k/pos.time',
        'results/control-cost20k-final.time', 'results/wall-positive-recube/shallow.time',
        'results/wall-positive-recube/full20-s2.time', 'results/wall-positive-recube/cost20k.time',
        'results/wall-positive-recube/cost20k-final.time', 'results/wall-positive-recube/shallow-final.time']
    measured = [time_file(path) for path in measured_command_files]
    resource_summary = {
        'measured_experimental_command_elapsed_s_component_sum': sum(r['command_elapsed_s'] for r in measured),
        'measured_experimental_command_cpu_s_component_sum': sum(r['command_cpu_s'] for r in measured),
        'wall_probe_plus_final_conflicts': 120002 + 2000002 + 2000002,
        'control_probe_plus_final_conflicts': probe_conflicts + final_conflicts,
        'note': 'Eight completed measured commands; static inspection/audits and one immediate missing-NumPy startup failure are excluded. Component sum, not one uninterrupted session.'}
    two_sim_scope = {
        'configured_setting': 'rollout-extra=20, sims=2',
        'effective_mcts_expansion_depth_at_fresh_node_at_most': 1,
        'reason': 'simulation 1 initializes root Ps; simulation 2 expands root actions and initializes child Ps; no simulation remains to expand a child action',
        'source': '.scratch/AlphaMapleSAT/alphamaplesat/MCTS.py getActionProb/search',
        'source_sha256': sha('.scratch/AlphaMapleSAT/alphamaplesat/MCTS.py'),
        'scope_note': 'This is not evidence against deeper/higher-simulation MCTS. The actual new rollouts here are fresh capped CDCL conquest probes.'}
    wall_summary['two_simulation_scope'] = two_sim_scope
    control_summary['two_simulation_scope'] = two_sim_scope
    summary = {'schema': 'k58-selective-cost-rollout-ab/v1', 'input_sha256': EXPECTED,
               'target_working_sha256': target_sha, 'control': control_summary, 'wall': wall_summary,
               'normalized_selection_diagnostic': normalized, 'resource_observations': resource_summary,
               'hash_algorithm': 'SHA-256 over whole files', 'no_proof_file_over_1GB': True}
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    (OUT / 'normalized-selection.json').write_text(json.dumps(normalized, indent=2, sort_keys=True) + '\n')
    verification = {
        'schema': 'k58-selective-cost-independent-byte-audit/v1', 'passed': True,
        'final_query_count': len(byte_checks['final_queries']),
        'probe_query_count': len(byte_checks['probe_queries']),
        'proof_file_count': len(byte_checks['proofs']),
        'strict_unsat_leaf_count': 4, 'open_wall_leaf_count': 4,
        'cover_checks': cover_checks, 'input_sha256': EXPECTED,
        'target_working_sha256': target_sha, 'byte_checks': byte_checks,
        'note': 'This checks CNF bytes/hash bindings and retained DRAT receipts; it does not supply physical-colouring semantics.'}
    (OUT / 'independent-byte-audit.json').write_text(json.dumps(verification, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'passed': True, 'control_final_conflicts': final_conflicts,
                      'control_prep_plus_search_s': prep + final_elapsed,
                      'wall_raw_selected': 2744, 'wall_normalized_selected': 1426,
                      'wall_status': 'all four final children OPEN',
                      'final_queries_checked': len(byte_checks['final_queries']),
                      'probe_queries_checked': len(byte_checks['probe_queries']),
                      'proof_files_hashed': len(byte_checks['proofs'])}, indent=2))


if __name__ == '__main__':
    main()
