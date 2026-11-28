import json,resource,subprocess,sys,time
from pathlib import Path
repo=Path.cwd()
work=repo/'.scratch/checkproof-panel'
work.mkdir(exist_ok=True)
checker=repo/'.ultramath/smx06hpp8/m5/.scratch/tools/lrat-trim-423194927df747528d5b7364806b5b77b2660c12/lrat-trim'
cases=[
 ('H8', repo/'.scratch/k58-0404-word-search/H8-word0.cnf', 'e8cc97847a6cab9c277933d2dd0d6112c79b061bebb5af221d57df5d6d6a2229'),
 ('H7', repo/'.scratch/k58-0404-word-search/H7-word0.cnf', '2286ae68e1419cdbc751e1804ec9ca79b05874b759b75ed9c6cd3ebe1a31225f')]
protocol={'preregistration':{
 'created_before_first_run':True,'cases':['H8','H7'],'arms':[3,0],
 'orders':['3-then-0','0-then-3'],'seeds':[0],
 'cap_conflicts':50000,'cap_wall_seconds':20,
 'metrics':['solver child CPU','native pipeline CPU excluding mandatory second checker','total including mandatory second checker'],
 'external_replay_is_mandatory':True,
 'same_search_counters_required':['conflicts','decisions','propagations','restarts'],
 'scope':'standalone exact-CNF certificate processing only; no CDCL speedup or wall/profile inference',
 'source':'CaDiCadL rel-2.1.2 Internal::check connects LratChecker only when checkproof > 1 (src/proof.cpp)'}}
(work/'preregistration.json').write_text(json.dumps(protocol,indent=2,sort_keys=True)+'\n')
records=[]
for order_index, arm_sequence in enumerate(((3,0),(0,3))):
 for case,cnf,sha in cases:
  for arm in arm_sequence:
   out = work/case/(('' if order_index==0 else f'attempt-{order_index}/') + f'checkproof-{arm}')
   if out.exists():
    receipt=json.loads((out/'receipt.json').read_text())
    assert receipt['validation']['state']=='VERIFIED_UNSAT_BY_TWO_UNVERIFIED_LRAT_CHECKERS'
    cmd=['reuse-of-already-checked-output']
   else:
    cmd=[sys.executable,'-B',str(repo/'tools/lrat_pipeline/native_solve.py'),
         '--cnf',str(cnf),'--expect-sha256',sha,'--out',str(out),
         '--checker',str(checker),'--conflicts','50000','--seconds','20',
         '--expected-outcome','UNSAT','--internal-checkproof',str(arm)]
    started=time.monotonic(); before=resource.getrusage(resource.RUSAGE_CHILDREN)
    result=subprocess.run(cmd,capture_output=True,text=True)
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    assert result.returncode==0,(case,arm,result.stderr,result.stdout[-2000:])
    receipt=json.loads((out/'receipt.json').read_text())
   records.append({'case':case,'order_index':order_index,'arm':arm,'receipt':receipt,
                    'command':cmd})
   print(case,arm,'solver',receipt['solver']['child_cpu_seconds'],
         'native',receipt['native_processing_cpu_seconds'],
         'all',receipt['total_cpu_seconds'],cmd[0],flush=True)

def fingerprint(receipt):
 return {k:receipt['solver']['stats'][k] for k in ('conflicts','decisions','propagations','restarts')}

for case,_,_ in cases:
 rows=[r for r in records if r['case']==case]
 assert len(rows)==4, (case,len(rows))
 cells={(r['order_index'],r['arm']):r for r in rows}
 assert set(cells)=={(0,3),(0,0),(1,3),(1,0)},(case,set(cells))
 for arm in (3,0):
  assert fingerprint(cells[0,arm]['receipt'])==fingerprint(cells[1,arm]['receipt']),case+f' repeated {arm} counters differ'
 for base_key,variant_key in (((0,3),(1,0)),((1,3),(0,0))):
  base=cells[base_key]['receipt']; variant=cells[variant_key]['receipt']
  assert fingerprint(base)==fingerprint(variant),(case,base_key,'mode changes search')
  ratio=variant['solver']['child_cpu_seconds']/base['solver']['child_cpu_seconds']
  print(case,base_key,variant_key,'mode 0 versus 3 ratio',ratio,
        'raw matches',base['raw_proof']['sha256']==variant['raw_proof']['sha256'],
        'trim matches',base['artifact']['sha256']==variant['artifact']['sha256'],flush=True)
  assert variant['validation']['state']=='VERIFIED_UNSAT_BY_TWO_UNVERIFIED_LRAT_CHECKERS'
(work/'raw-panel.json').write_text(json.dumps(records,indent=2,sort_keys=True)+'\n')
print('all independent proof validations passed')
