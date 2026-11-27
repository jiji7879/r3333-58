#!/usr/bin/env python3
"""Extract short physical learned clauses from the verified rank-1300 core."""
import collections,hashlib,itertools,json,sys
from pathlib import Path
sys.path.insert(0,'research/k58-arm-cap-clauses/work')
from strip_drat_deletions import decode
R=Path('.').resolve();raw=(R/'.scratch/arm-cap-research/rank1300-stock.cnf').read_bytes()
proof=(R/'.scratch/arm-cap-research/rank1300-glucose-stock-core.drat').read_bytes()
base_lines=[tuple(map(int,l.split()[:-1])) for l in raw.decode().splitlines() if l and l[0] not in 'pc']
canon=lambda c:tuple(sorted(c,key=lambda x:(abs(x),x)))
base_set={canon(c) for c in base_lines}
unique={};order=[]
for tag,cl in decode(proof):
 if len(cl)>3 or any(abs(x)>6612 for x in cl):continue
 c=canon(cl)
 if not c or c in base_set or c in unique or any(-x in cl for x in cl):continue
 unique[c]=len(order);order.append(c)

def edge(lit):
 v=abs(lit)-1;idx,c=divmod(v,4);n=0
 for i in range(58):
  for j in range(i+1,58):
   if n==idx:return i,j,c
   n+=1
 raise ValueError(idx)
def stats(clauses):
 out=collections.Counter()
 for cl in clauses:
  es=[edge(x) for x in cl]
  signs=''.join('+' if x>0 else '-' for x in cl)
  out['signs='+signs]+=1
  out['colors='+','.join(map(str,sorted({e[2] for e in es})))]+=1
  if len(cl)==2:
   (u,v,c),(x,y,d)=es
   out['adjacent='+str(len({u,v}&{x,y})>0)]+=1
   out['same_edge='+str((u,v,c)==(x,y,d))]+=1
   out['root_edges='+str((u==0)+(x==0))]+=1
 return dict(out)
# augment original DIMACS with unique learned clauses in proof order
head,body=raw.split(b'\n',1);_,_,nv,nc=head.split()
def write(name,clauses):
 data=(f'p cnf {int(nv)} {int(nc)+len(clauses)}\n'.encode()+body+
       b''.join((' '.join(map(str,c))+' 0\n').encode() for c in clauses))
 p=R/'.scratch/arm-cap-research'/name;p.write_bytes(data)
 return dict(path=str(p.relative_to(R)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),added=len(clauses))
summary=dict(original_sha256=hashlib.sha256(raw).hexdigest(),core_proof_sha256=hashlib.sha256(proof).hexdigest(),
 unique_new_by_length=dict(collections.Counter(map(len,order))),
 unique_total=len(order),binary_pattern_counts=stats([c for c in order if len(c)==2]),
 ternary_sign_counts={k:v for k,v in stats([c for c in order if len(c)==3]).items() if k.startswith('signs=')},
 formulas={
  'units':write('rank1300-learned-units.cnf',[c for c in order if len(c)==1]),
  'units_binary':write('rank1300-learned-units-binary.cnf',[c for c in order if len(c)<=2]),
  'learned_le3':write('rank1300-learned-le3.cnf',order)})
(R/'research/k58-arm-cap-clauses/work/rank1300-short-lemmas.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary,indent=2,sort_keys=True))
