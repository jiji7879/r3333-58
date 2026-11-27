#!/usr/bin/env python3
"""Revalidate and byte-reproduce the direct minimized stock augmentation."""
import argparse,collections,hashlib,itertools,json,time
from pathlib import Path
from pysat.formula import CNF
from pysat.solvers import Cadical195

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',required=True,type=Path);ap.add_argument('--minimized',required=True,type=Path);ap.add_argument('--conflicts',type=int,default=200000);a=ap.parse_args();run=a.run.resolve();md=a.minimized.resolve();assert Path.cwd().resolve() in run.parents and Path.cwd().resolve() in md.parents
 cpu0,wall0=time.process_time(),time.perf_counter();s=json.loads((run/'summary.json').read_text());ms=json.loads((md/'summary.json').read_text());records=json.loads((md/'minimized.json').read_text());raw=(run/'stock.cnf').read_bytes();assert sha(raw)==s['input_sha256'];stock=CNF(from_string=raw.decode());edges=list(itertools.combinations(range(58),2));physical=[cl for cl in stock.clauses if all(abs(l)<=4*len(edges) for l in cl)];profile=list(map(int,s['profile'].split(',')));starts=[1]
 for n in profile:starts.append(starts[-1]+n)
 unique={}
 for r in records:unique.setdefault(tuple(sorted(r['minimal_original_clause'])),r)
 assert len(unique)==ms['unique_minimized_clauses']==375
 grouped=collections.defaultdict(list)
 for cl,r in unique.items():grouped[r['sender'],r['color'],r['arm_a'],r['arm_b']].append((cl,r))
 accepted=[];answers=collections.Counter();relations=[]
 for key,rs in sorted(grouped.items()):
  x,c,ba,bb=key;A=list(range(starts[ba],starts[ba+1]));B=list(range(starts[bb],starts[bb+1]));V={0,x,*A,*B};ie=set(itertools.combinations(sorted(V),2));base=[cl for cl in physical if all(edges[(abs(l)-1)//4] in ie for l in cl)];counts=collections.Counter()
  with Cadical195(bootstrap_with=base) as sat:
   sat.configure({'seed':0});sat.conf_budget(a.conflicts)
   for cl,r in rs:
    ans=sat.solve_limited(assumptions=r['minimal_positive_spokes']);counts[str(ans)]+=1;answers[str(ans)]+=1
    if ans is False:accepted.append(cl)
   stats=sat.accum_stats()
  relations.append({'sender':x,'color':c,'arm_a':ba,'arm_b':bb,'queries':len(rs),'answers':dict(counts),'conflicts':stats['conflicts'],'propagations':stats['propagations']});print(key,dict(counts),flush=True)
 accepted=sorted(set(accepted));assert len(accepted)==375 and answers['False']==375 and sum(answers.values())==375,(len(accepted),answers)
 h,b=raw.split(b'\n',1);f=h.split();data=f'p cnf {int(f[2])} {int(f[3])+len(accepted)}\n'.encode()+b+b''.join(' '.join(map(str,c)).encode()+b' 0\n' for c in accepted);assert data==(md/'stock-minimal.cnf').read_bytes()
 out={'schema':'minimal-clause-revalidation/v1','rank':s['rank'],'row_id':s['row_id'],'parent_sha256':s['input_sha256'],'candidate_hints':len(records),'unique_candidates':len(unique),'accepted_unique':len(accepted),'answers':dict(answers),'query_conflicts':a.conflicts,'formula_sha256':sha(data),'full_formula_byte_identical':True,'clause_widths':dict(collections.Counter(map(len,accepted))),'cpu_seconds':time.process_time()-cpu0,'wall_seconds':time.perf_counter()-wall0,'relations':relations,'scope':'All unique direct clauses were freshly re-solved on an original-parent subset. Only UNSAT accepted. No SAT or OPEN result became a clause. The direct benchmark input is reproduced byte-for-byte.'}
 (md/'revalidation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='relations'},indent=2))
if __name__=='__main__':main()
