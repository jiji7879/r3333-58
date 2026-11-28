#!/usr/bin/env python3
"""Independently re-run every retained positive K58/K6 proof with a second binary."""
import hashlib,json,subprocess
from pathlib import Path

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
sources=[('greedy',Path('results/control-greedy-leaves')),
         ('shallow',Path('results/control-mcts-leaves')),
         ('full20',Path('results/control-mcts-full20-new-leaves')),
         ('K6',Path('results/k6-control-leaves-fixed'))]
checker=Path('../../../.scratch/satcheck/bin/drat-trim')
out=Path('results/second-replay');out.mkdir(exist_ok=True)
results=[]
for family,folder in sources:
 for index,receipt in enumerate(json.loads((folder/'receipts.json').read_text())):
  leaf=folder/f'leaf-{index}'
  assert receipt['status']=='CHECKED_UNSAT'
  query=leaf/'query.cnf';proof=leaf/'joined.additions-only.drat'
  assert sha(query)==receipt['query_sha256'] and sha(proof)==receipt['normalized_proof_sha256']
  run=subprocess.run([str(checker.resolve()),str(query),str(proof),'-i','-U','-t','300'],capture_output=True,timeout=302)
  log=(run.stdout+run.stderr).replace(b'\r',b'\n')
  (out/f'{family}-{index}.log').write_bytes(log)
  lines=log.decode(errors='replace').splitlines()
  clean=not any('WARNING' in x or 'ERROR' in x or 'NOT VERIFIED' in x for x in lines)
  passed=run.returncode==0 and lines.count('s VERIFIED')==1 and clean
  results.append({'family':family,'index':index,'query_sha256':receipt['query_sha256'],
                  'proof_sha256':receipt['normalized_proof_sha256'],'passed':passed,
                  'returncode':run.returncode,'clean':clean})
  print(family,index,'PASS' if passed else 'FAIL',flush=True)
summary={'schema':'independent-second-drattrim-replay/v1','checker_sha256':sha(checker),
         'count':len(results),'passed':sum(r['passed'] for r in results),'failures':sum(not r['passed'] for r in results),'results':results}
Path('results/second-checker-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
assert summary['failures']==0
