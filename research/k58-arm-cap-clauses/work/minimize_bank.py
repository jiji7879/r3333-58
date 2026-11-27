#!/usr/bin/env python3
"""Greedily weaken hinted joint clauses using only fresh local UNSAT answers."""
import argparse,collections,hashlib,itertools,json,time
from pathlib import Path
from pysat.formula import CNF
from pysat.solvers import Cadical195

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--conflicts',type=int,default=20000);ap.add_argument('--max-relations',type=int);a=ap.parse_args();run=a.run.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);assert Path.cwd().resolve() in out.parents
 cpu0,wall0=time.process_time(),time.perf_counter();s=json.loads((run/'summary.json').read_text());hints=json.loads((run/'exclusions.json').read_text());raw=(run/'stock.cnf').read_bytes();assert sha(raw)==s['input_sha256'];stock=CNF(from_string=raw.decode());edges=list(itertools.combinations(range(58),2));physical=[cl for cl in stock.clauses if all(abs(l)<=4*len(edges) for l in cl)];profile=list(map(int,s['profile'].split(',')));starts=[1]
 for n in profile:starts.append(starts[-1]+n)
 grouped=collections.defaultdict(list)
 for h in hints:grouped[h['sender'],h['color'],h['arm_a'],h['arm_b']].append(h)
 minimized=[];relations=[]
 for ri,(key,hs) in enumerate(sorted(grouped.items())):
  if a.max_relations is not None and ri>=a.max_relations:break
  x,c,ba,bb=key;A=list(range(starts[ba],starts[ba+1]));B=list(range(starts[bb],starts[bb+1]));V={0,x,*A,*B};ie=set(itertools.combinations(sorted(V),2));base=[cl for cl in physical if all(edges[(abs(l)-1)//4] in ie for l in cl)];counts=collections.Counter();dropped=0
  with Cadical195(bootstrap_with=base) as sat:
   sat.configure({'seed':0});sat.conf_budget(a.conflicts)
   for h in hs:
    current=list(h['positive_spokes'])
    for lit in list(current):
     if len(current)<=1:break
     trial=[l for l in current if l!=lit];ans=sat.solve_limited(assumptions=trial);counts[str(ans)]+=1
     if ans is False:current=trial;dropped+=1
    assert len(current)<=len(h['positive_spokes'])
    z=dict(h);z['minimal_positive_spokes']=current;z['minimal_original_clause']=[-l for l in current];z['dropped_literals']=len(h['positive_spokes'])-len(current);minimized.append(z)
   stats=sat.accum_stats()
  relations.append({'sender':x,'color':c,'arm_a':ba,'arm_b':bb,'candidates':len(hs),'queries':sum(counts.values()),'answers':dict(counts),'dropped':dropped,'widths':dict(collections.Counter(len(z['minimal_positive_spokes']) for z in minimized if (z['sender'],z['color'],z['arm_a'],z['arm_b'])==key)),'conflicts':stats['conflicts'],'propagations':stats['propagations']});print(key,relations[-1],flush=True)
 clauses=sorted({tuple(sorted(z['minimal_original_clause'])) for z in minimized});h,b=raw.split(b'\n',1);f=h.split();data=f'p cnf {int(f[2])} {int(f[3])+len(clauses)}\n'.encode()+b+b''.join(' '.join(map(str,c)).encode()+b' 0\n' for c in clauses);(out/'stock-minimal.cnf').write_bytes(data)
 outdata={'schema':'greedy-local-clause-weakening/v1','rank':s['rank'],'row_id':s['row_id'],'parent_sha256':s['input_sha256'],'input_exclusions':len(minimized),'unique_minimized_clauses':len(clauses),'widths':dict(collections.Counter(map(len,clauses))),'max_relations':a.max_relations,'query_conflicts':a.conflicts,'cpu_seconds':time.process_time()-cpu0,'wall_seconds':time.perf_counter()-wall0,'formula_sha256':sha(data),'relations':relations,'scope':'Each kept clause is the negation of a spoke subset freshly proved UNSAT on a subset of the original parent. SAT and OPEN both prevent dropping. Greedy deletion is inclusion-minimal only with respect to completed answers; it is not claimed cardinality-minimal.'}
 (out/'summary.json').write_text(json.dumps(outdata,indent=2,sort_keys=True)+'\n');(out/'minimized.json').write_text(json.dumps(minimized,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in outdata.items() if k!='relations'},indent=2))
if __name__=='__main__':main()
