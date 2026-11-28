#!/usr/bin/env python3
"""Check saved hashes and status/control invariants without rerunning solvers."""
import hashlib, json
from pathlib import Path

summary=json.loads(Path('results/summary.json').read_text())
assert summary['proofs']==[] and summary['certification'].startswith('NONE:')
for path,want in summary['query_sha256'].items():
    got=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    assert got==want,(path,got,want)
runfiles=['results/cadical-1m.jsonl','results/cadical-2m.jsonl',
          'results/cadical-arm3-bcp-1m.jsonl','results/cadical-repeat-1m.jsonl']
by={}
for path in runfiles:
    for line in Path(path).read_text().splitlines():
        r=json.loads(line)
        assert r['answer'] is None and r['status']=='OPEN'
        assert r['conflicts_and_other_stats']['conflicts']==r['conflict_cap']
        assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['cnf_sha256']
        by[(path,r['label'])]=r
for path in ['results/audit-arm2.json','results/audit-arm3.json','results/audit-arm2_3.json',
             'results/verify-bcp-arm3.json','results/verify-bcp-arm2_3.json']:
    assert json.loads(Path(path).read_text())['result']=='PASS'
assert by[('results/cadical-1m.jsonl','arm3')]['conflicts_and_other_stats']==by[('results/cadical-arm3-bcp-1m.jsonl','arm3-bcp')]['conflicts_and_other_stats']
assert by[('results/cadical-1m.jsonl','union')]['conflicts_and_other_stats']==by[('results/cadical-1m.jsonl','union-bcp')]['conflicts_and_other_stats']
assert max(p.stat().st_size for p in Path('.').rglob('*') if p.is_file())<1_000_000_000
print(json.dumps({'result':'PASS','queries':len(summary['query_sha256']),
                  'runs':sum(1 for _ in by),'all_statuses':'OPEN','proofs':0,
                  'raw_bcp_search_statistics_identical':True},indent=2))
