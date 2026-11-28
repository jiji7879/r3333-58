"""Cross-check the accepted component receipts and the independent benchmark arithmetic."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / 'research/k58-color-resolved-wall-pivots'
BASE = ROOT / '.scratch/color-wall-v1/base'

bench = json.loads((BASE/'bench.json').read_text())['runs']
assert len(bench) == 48
totals = {}
for variant in ('original','counter','escape','color'):
    rr = [r for r in bench if r['variant'] == variant]
    assert len(rr) == 12 and all(r['result'] == 'OPEN' and r['retained_terminal_proof_bytes']==0 for r in rr)
    totals[variant] = {'cpu_s':sum(r['cpu_s'] for r in rr), 'conflicts':sum(r['conflicts'] for r in rr),
                      'partial_trace_bytes':sum(r['partial_trace_bytes'] for r in rr)}
children = json.loads((BASE/'children.json').read_text())
child = {mode:sum(r['conflicts'] for r in children if r['mode']==mode) for mode in ('B','C')}
assert child == {'B':114, 'C':0}
batches = [json.loads((BASE/f'{name}.batch.json').read_text()) for name in ('0','370','762','15533','gap1','gap2')]
bt = [sum(len(row[key]) for row in batches) for key in ('B','C_extra')]
assert bt == [94,97]

binding = json.loads((D/'checks/binding-receipt.json').read_text())
geometry = json.loads((D/'checks/geometry-receipt.json').read_text())
archive = json.loads((D/'checks/archive-identity.json').read_text())
assert (binding['rows'],binding['unique_row_ids'],binding['configurations_compared_exactly'],binding['null_pivots']) == (11585,11585,240,36)
assert binding['bindings_compared_exactly']==binding['rows']==11585
assert binding['summary']['classified']==11549
assert geometry['pivot_rows_checked']==11549 and geometry['arm_sites_checked']==174535
assert archive['files_checked']==51

m1 = ROOT / '.ultramath/smwznkmmj/m1'
enum = json.loads((m1/'enumeration-receipt.json').read_text())
native = json.loads((m1/'native-receipt.json').read_text())
baseline = json.loads((m1/'baseline-receipt.json').read_text())
transport = json.loads((m1/'transport-receipt.json').read_text())
probe = json.loads((m1/'extension-receipt.json').read_text())
assert enum['total_cases']==240 and enum['total_physical_local_words']==1448380
assert native['tested_configurations']==native['pass_count']==240
assert all(r['returncode']==0 for r in native['records'])
assert all(r['returncode']!=0 and 's NOT VERIFIED' in r['stdout'] and 'WARNING' not in r['stdout'] for r in native['negative_controls'])
assert (baseline['reconstructed_minimal_positive_clauses'],baseline['literal_removal_counterexamples']) == (4510,21173)
assert transport['transported_rows_tested']==transport['pass_count']==10
assert sum(r['targets'] for r in transport['records'])==159
assert probe['not_up_refuted_words']==135 and probe['sat_solve_performed'] is False

result = {'status':'PASS component consistency; not a new SAT/UNSAT or speedup result',
          'by_variant':totals,'child_conflicts':child,
          'archived_batch_clauses':{'baseline':bt[0],'color':bt[1]},
          'row_geometry_checked':11549,'local_words_checked':1448380,'local_native_pass':240,
          'baseline_clauses':4510,'literal_deletion_counterexamples':21173,
          'transported_parent_proofs':10,'conditional_clauses':159,'UP_not_refuted_not_SAT':135,
          'bounded_claim':'models preserve under unique counter extension and derived clauses; no global extension or completed wall-row search'}
(D/'checks/final-compute.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
