#!/usr/bin/env python3
"""Strict original-parent certificate for a selected minimized direct clause."""
import argparse,hashlib,itertools,json,subprocess,time
from pathlib import Path
from pysat.formula import CNF
from pysat.solvers import Cadical195
import pysolvers

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',required=True,type=Path);ap.add_argument('--minimized',required=True,type=Path);ap.add_argument('--checker',required=True,type=Path);ap.add_argument('--refinement',required=True,type=Path);ap.add_argument('--width',type=int,default=2);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args();run=a.run.resolve();md=a.minimized.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);assert Path.cwd().resolve() in out.parents
 import sys;sys.path.insert(0,str(a.refinement.resolve()));from compare import without_deletions
 s=json.loads((run/'summary.json').read_text());raw=(run/'stock.cnf').read_bytes();stock=CNF(from_string=raw.decode());rec=next(r for r in json.loads((md/'minimized.json').read_text()) if len(r['minimal_positive_spokes'])==a.width);edges=list(itertools.combinations(range(58),2));profile=list(map(int,s['profile'].split(',')));starts=[1]
 for n in profile:starts.append(starts[-1]+n)
 x,c,ba,bb=rec['sender'],rec['color'],rec['arm_a'],rec['arm_b'];A=list(range(starts[ba],starts[ba+1]));B=list(range(starts[bb],starts[bb+1]));V={0,x,*A,*B};ie=set(itertools.combinations(sorted(V),2));base=[cl for cl in stock.clauses if all(abs(l)<=4*len(edges) and edges[(abs(l)-1)//4] in ie for l in cl)];units=rec['minimal_positive_spokes'];local=base+[[l] for l in units];t=time.perf_counter()
 with Cadical195(bootstrap_with=local,with_proof=True) as sat:
  sat.configure({'seed':0});sat.conf_budget(200000);answer=sat.solve_limited();stats=sat.accum_stats();assert answer is False,(answer,stats);pysolvers.flushpr(sat.prfp);sat.prfile.seek(0);proof=sat.prfile.read()
 clean,norm=without_deletions(proof);(out/'clean.drat').write_bytes(clean);h,b=raw.split(b'\n',1);f=h.split();full_data=f'p cnf {int(f[2])} {int(f[3])+len(units)}\n'.encode()+b+b''.join(f'{l} 0\n'.encode() for l in units);(out/'original-query.cnf').write_bytes(full_data);local_data=(f'p cnf {stock.nv} {len(local)}\n'.encode()+b''.join(' '.join(map(str,c)).encode()+b' 0\n' for c in local));(out/'local-query.cnf').write_bytes(local_data)
 def check(name,path,log_expected=None):
  runck=subprocess.run([str(a.checker.resolve()),str(path),str(out/'clean.drat'),'-i','-U','-W','-t','300'],capture_output=True);text=runck.stdout+runck.stderr;(out/(name+'.log')).write_bytes(text);status=[l for l in text.splitlines() if l.startswith(b's ')];assert runck.returncode==0 and status==[b's VERIFIED'] and b'WARNING' not in text.upper() and b'ERROR' not in text.upper();return {'exit':runck.returncode,'status':['s VERIFIED'],'warnings':0,'query_sha256':sha(path.read_bytes())}
 controls=[]
 for lit in units:
  remain=[l for l in units if l!=lit]
  with Cadical195(bootstrap_with=base+[[l] for l in remain]) as sat:
   ans=sat.solve();assert ans is True,(lit,ans);model=set(sat.get_model());assert all(any(l in model for l in cl) for cl in base+[[l] for l in remain]);cstats=sat.accum_stats()
  controls.append({'removed':lit,'remaining_units':remain,'answer':'SAT_LOCAL_ONLY','stats':cstats,'model_satisfies_query':True})
 result={'schema':'minimal-original-parent-certificate/v1','rank':s['rank'],'row_id':s['row_id'],'parent_sha256':s['input_sha256'],'record':rec,'minimal_clause':rec['minimal_original_clause'],'solver_stats':stats,'search_wall_seconds':time.perf_counter()-t,'raw_proof_sha256':sha(proof),'normalization':norm,'clean_proof_bytes':len(clean),'clean_proof_sha256':sha(clean),'local_replay':check('local-replay',out/'local-query.cnf'),'original_parent_replay':check('original-replay',out/'original-query.cnf'),'scope':'Local proof replayed against the full original parent plus exactly the false-cube units. Local SAT controls concern this original-parent subset only, not the UNSAT full parent.','single_literal_deletion_controls':controls,'flags':['-i','-U','-W','-t','300']}
 (out/'summary.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
