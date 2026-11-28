"""Consistency check of the accepted four-direction audit receipts."""
import csv
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
D = ROOT/'research/k58-proof-artifacts'
S = ROOT/'.ultramath/smwzmjadv'
spoke = json.loads((S/'m1/receipts/replay-summary.json').read_text())
assert spoke['bindings_PASS']==4 and spoke['valid_RUP_obligations_PASS']==8
assert spoke['native_negative_controls_FAIL_as_expected']==8
assert spoke['valid_RAT_lemmas']==spoke['valid_warnings_or_errors']==spoke['timeouts']==0
mined = json.loads((S/'m2/receipt-summary.json').read_text())
assert (mined['native_log_files'],mined['verified_log_files'],mined['expected_failure_log_files']) == (148,137,11)
assert mined['transfer_bindings']==7 and mined['unexpected_failures']==0
comparison = json.loads((S/'m4/logs/replay-summary.json').read_text())
assert comparison['all_8_PASS'] is True
assert comparison['decompressed_source_bytes']==419793932
assert comparison['lrat_bytes']==1084173458
projection = json.loads((S/'m3/audit_summary.json').read_text())
tots = projection['totals']
assert len(projection['runs'])==5
assert all(r['status']=='PASS_DELETION_FREE_RUP_AND_LRAT_FULL_ORIGINAL_PARENT' for r in projection['runs'].values())
assert (tots['source_drat_bytes'],tots['normalized_additions_bytes'],tots['clean_lrat_bytes']) == (669859010,336193354,1375316158)
coord = json.loads((D/'checks/remaining-recomputation.json').read_text())
assert coord['core_comparison']['exact_literal_line_intersection']==4359
assert coord['core_comparison']['canonical_clause_intersection']==5094
# Validate all seven physical parent/projection bindings from the rebuilt record.
# Re-read all seven physical parent/projection bindings from the independently rebuilt record.
geom = json.loads((S/'m3/projection_audit.json').read_text())['rows']
hard = {int(r['rank']):r for r in csv.DictReader((ROOT/'attachments/these-were-all-solved-xb5o/hard1300.tsv').open(),delimiter='\t')}
assert len(geom)==7
for rank,r in geom.items():
    assert r['rebuilt_byte_identical'] and r['ordered_strict_parent_subsequence']
    assert r['kinds']==hard[int(rank)]['kinds']
assert [geom[str(n)]['kinds'] for n in range(1294,1301)] == ['TTT-','TTT-','TTT-','TTT-','TTU-','TTT-','TTT-']
for n,wrong in [(1298,1318),(1299,1287)]:
    m=geom[str(n)]['local_model']
    assert m['projection_check']['satisfied'] and not m['same_values_on_full_parent']['satisfied']
    assert m['same_values_on_full_parent']['falsified_clause_count']==wrong
wallperf = json.loads((S/'m1/receipts/performance.json').read_text())
assert all(s=='OPEN' for r in wallperf['paired_runs'] for s in r['statuses'])
perfsum = coord['performance_recomputation']
assert perfsum['A']['conflicts']==1845186 and perfsum['D']['conflicts']==1680786
result={'status':'PASS scoped aggregate consistency',
 'spoke_native_PASS':8,'spoke_no_helper_expected_FAIL':8,
 'mined_transfer_bindings':mined['transfer_bindings'],'mined_native_receipts_TOTAL_PASS_FAIL':[148,137,11],
 'comparison_SOURCE_LRAT_BYTES':[comparison['decompressed_source_bytes'],comparison['lrat_bytes']],
 'projection_RAW_ADDITION_LRAT_BYTES':[tots['source_drat_bytes'],tots['normalized_additions_bytes'],tots['clean_lrat_bytes']],
 'projection_kinds_corrected':{n:geom[str(n)]['kinds'] for n in range(1294,1301)},
 'local_model_parent_falsifications':{'1298':1318,'1299':1287},
 'D_vs_A_percent':perfsum['D']['percent'],
 'P13000_vs_A0':projection['rank1300_projection_vs_original_A0_descriptive'],
 'core_overlap_exact_vs_canonical':[4359,5094],
 'ordinary_wall_cpu':wallperf['independent_totals']['cpu_s'],
 'not_a_full_replay':'Receipt reconciliation supplements directly executed native spot replays, projection reconstruction and source/hash recomputation; it does not independently repeat every already checked full stream.',
 'scope':'No new wall closure, full-parent model for ranks 1298/1299, or end-to-end speedup.'}
(D/'checks/final-compute.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
