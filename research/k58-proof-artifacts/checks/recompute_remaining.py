"""Coordinator-only recomputation of supplied archive bindings and preserved receipts.

Does not accept an original-parent claim from a local UNSAT receipt.  Replays native
comparison receipts against their bound parent/source hashes and their independent
C LRAT-check logs; these are receipt audits, not extra runs of every large proof.
"""
from pathlib import Path
import csv, hashlib, json, subprocess, zipfile

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / 'research/k58-proof-artifacts'
M = ROOT / '.ultramath/smwzmjadv/m3/mining'
L = ROOT / '.ultramath/smwzmjadv/m4/logs'
ATT = ROOT / 'attachments/these-were-all-solved-xb5o'
parents = {}
rows = list(csv.DictReader((M/'hard1300.tsv').open(), delimiter='\t')) if (M/'hard1300.tsv').exists() else \
       list(csv.DictReader((ATT/'hard1300.tsv').open(), delimiter='\t'))
for row in rows:
    n = int(row['rank'])
    if 1294 <= n <= 1300 and (M/f'P{n}.parent.cnf.zst').exists():
        raw = subprocess.check_output(['zstd', '-q', '-dc', str(M/f'P{n}.parent.cnf.zst')])
        assert hashlib.sha256(raw).hexdigest() == row['input_sha256']
        bind = json.loads((M/f'P{n}.binding.json').read_text())
        assert bind['parent'] == row['input_sha256'] and bind['rank'] == n and bind['row'] == row['id']
        projection = subprocess.check_output(['zstd', '-q', '-dc', str(M/f'P{n}.cnf.zst')])
        assert bind['projection'] == hashlib.sha256(projection).hexdigest()
        parents[str(n)] = {'parent_matches_ledger': True, 'projection_matches_binding': True}

# For each local projection trace, distinguish the satisfying/UNSAT projection
# query from the original formula accepted by the final parent checker.
projection_sources = {}
with zipfile.ZipFile(ATT/'K58_rank1300_projection_proofs.zip') as z:
    for n in [1294, 1295, 1296, 1297, 1300]:
        stem = f'P{n}0'
        with z.open(stem+'.drat.zst') as inp:
            compressed = inp.read()
        source = subprocess.check_output(['zstd', '-q', '-dc'], input=compressed)
        cert = json.loads((M/f'{stem}.cert.json').read_text())
        bind = json.loads((M/f'P{n}.binding.json').read_text())
        run = json.loads((M/f'{stem}.json').read_text())
        assert cert['source_file'] == stem+'.drat'
        assert cert['source_sha256'] == run['proof_sha256'] == hashlib.sha256(source).hexdigest()
        assert cert['original'] == bind['parent'] and run['query_sha256'] == bind['projection']
        projection_sources[str(n)] = {'source_sha256': cert['source_sha256'],
          'source_bytes': len(source), 'projection_query_sha256': run['query_sha256'],
          'original_parent_sha256': cert['original'],
          'scope': 'local solver query, unrestricted-parent final refutation'}

# Every compressed source is independently read. The byte hash, local certificate,
# and independent replay receipt must all name the same source.
source_specs = {
 'A0': M/'A0.trim.zst',
 'A1': 'A1.trim.zst', 'B0': 'B0.trim.zst', 'B1': 'B1.trim.zst',
 'C0': 'C0.trim.zst', 'C1': 'C1.trim.zst', 'D0': 'D0.parent.trim.zst',
 'D1': 'D1.parent.trim.zst', 'K0': 'K0.drat.zst',
}
comparisons = {}
with zipfile.ZipFile(ATT/'K58_rank1300_comparison_proofs.zip') as z:
    for stem, spec in source_specs.items():
        replay = json.loads((L/f'{stem}-replay.json').read_text())
        cert = json.loads((M/f'{stem}.cert.json').read_text())
        if isinstance(spec, Path):
            source = subprocess.check_output(['zstd', '-q', '-dc', str(spec)])
        else:
            with z.open(spec) as inp:
                    compressed = inp.read()
            source = subprocess.check_output(['zstd', '-q', '-dc'], input=compressed)
        actual = hashlib.sha256(source).hexdigest()
        assert actual == cert['source_sha256'] == replay['source_sha256']
        assert cert['original'] == replay['original_sha256'] == json.loads((M/'P1300.binding.json').read_text())['parent']
        assert len(source) == replay['source_bytes']
        accepted = replay.get('visible_conversion', replay['conversion'])
        assert accepted['returncode'] == 0 and accepted['warning_count'] == 0
        assert accepted['contains_s_VERIFIED'] and not accepted['timed_out']
        ic = replay['independent_check']; scan = replay['binary_lrat_audit']
        assert ic['returncode'] == ic['converter_returncode'] == 0 and not ic['timed_out']
        assert ic['contains_c_VERIFIED'] and not ic['contains_NOT_VERIFIED'] and ic['warning_count'] == 0
        scan_vals = dict(line.split('=', 1) for line in scan['log'].splitlines())
        assert scan['returncode'] == 0 and not scan['timed_out']
        assert scan_vals['empty_clauses'] == '1' and scan_vals['additions_after_empty'] == '0'
        assert scan_vals['negative_hint_ids'] == '0'
        assert replay['lrat_matches_cert_hash'] == (stem != 'A0')
        if stem != 'A0':
            assert cert['lrat_sha256'] == replay['lrat_sha256']
        comparisons[stem] = {
          'source_sha256': actual, 'source_bytes': len(source),
          'original_parent_sha256': cert['original'],
          'lrat_bytes': replay['lrat_bytes'], 'lrat_sha256': replay['lrat_sha256'],
          'lrat_matches_original_certificate': replay['lrat_matches_cert_hash'],
          'fresh_lrat_check': 'PASS', 'full_binary_parse': 'PASS',
          'terminal_empty_clauses': 1, 'rat_hints': 0,
          'strict_W_conversion': {'rc': replay['conversion']['returncode'], 'accepted': False},
          'accepted_conversion': {'no_w': True, 'warning_count': accepted['warning_count'],
                                  'cpu_s': accepted['cpu_s']},
        }

# Core comparisons use two separately named equivalence relations. Order of
# literals in a clause is semantically immaterial, and two valid trims need not
# choose the same subset of the same input formula.
def clauses(path):
    lines = path.read_text().splitlines()
    h = lines[0].split()
    clauses = [line.split()[:-1] for line in lines[1:] if line.strip()]
    assert int(h[3]) == len(clauses)
    assert all(c and c[-1] != '0' for c in clauses)
    literal_lines = {tuple(c) for c in clauses}
    normalized = {tuple(sorted(map(int, c))) for c in clauses}
    assert len(literal_lines) == len(normalized) == len(clauses)
    return literal_lines, normalized, hashlib.sha256(path.read_bytes()).hexdigest()
old = clauses(ROOT/'.scratch/arm-cap-research/rank1300-original-core.cnf')
new = clauses(M/'A0.core')
assert len(old[0]) == 5245 and len(new[0]) == 5250
assert new[2] == hashlib.sha256((ROOT/'.scratch/new-proofs-v1/K.cnf').read_bytes()).hexdigest()
core = {
 'old': {'clauses': len(old[0]), 'sha256': old[2]},
 'new_A0_and_K': {'clauses': len(new[0]), 'sha256': new[2]},
 'exact_literal_line_intersection': len(old[0] & new[0]),
 'canonical_clause_intersection': len(old[1] & new[1]),
 'exact_old_only': len(old[0] - new[0]), 'canonical_old_only': len(old[1] - new[1]),
 'exact_A0_only': len(new[0] - old[0]), 'canonical_A0_only': len(new[1] - old[1]),
 'explanation': 'The old 1.9.5 and new 2.1.2 proofs have different backward cores; the 4,359 versus 5,094 values are exact-line versus literal-order-normalized intersections.',
}

metrics = json.loads((L/'metrics.json').read_text())
# Recompute the decisive comparison directly from log-parsed measured values.
by_run = {r['run']: r for r in metrics['runs']}
perf = {}
for mode in 'ABCD':
    perf[mode] = {}
    for field in ['conflicts', 'receipt_cpu_s', 'raw_drat_bytes_log']:
        perf[mode][field] = by_run[mode+'0'][field] + by_run[mode+'1'][field]
    if mode != 'A':
        perf[mode]['percent'] = {field: 100*(perf[mode][field]/perf['A'][field]-1)
          for field in ['conflicts', 'receipt_cpu_s', 'raw_drat_bytes_log']}
perf['overhead_scope'] = 'Two seeds, one historical rank-1300 row. Baseline solve+trim+selection is 196.492309 mixed CPU/wall seconds (not a cold wall estimate), versus 17.421048 measured CPU seconds saved on two repeated D solves; extraction and full checking are not fully priced. No amortized or cohort-wide win follows.'

out = {'status': 'PASS scoped comparison receipt and binding recomputation',
       'projection_parent_and_binding_hashes': parents,
       'projection_proof_sources': projection_sources,
       'comparison_streams': comparisons, 'core_comparison': core,
       'performance_recomputation': perf,
       'not_a_second_full_replay': 'Coordinator used members full native streams plus own prior A0/C0/D0/K0/P13000 replays; the other streams are receipt-and-byte audits here.',
       'chief_metadata_defect': 'A0 native trim is listed under convert_to_lrat_wall_s; do not sum these fields uniformly.',
       'no_scope_expansion': 'No unresolved wall profile, SAT extension, overall cohort speedup, or Ramsey-bound change follows.'}
(D/'checks/remaining-recomputation.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps({'streams': len(comparisons), 'parents': len(parents), 'core': core,
                  'D_CPU_percent': perf['D']['percent']['receipt_cpu_s']}, indent=2))
