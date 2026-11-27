#!/usr/bin/env python3
"""Independent finite/model-extension checks for the guarded two5 encoding."""
import collections,hashlib,itertools,json,re,subprocess,sys
from pathlib import Path

R=Path(__file__).resolve().parents[3]
MEM=R/'.ultramath/smwziyz3b/m1'
CNF=R/'.scratch/arm-cap-research/m1-reproduced-r1300-two5.cnf'
BASE=R/'.scratch/arm-cap-research/rank1300-stock.cnf'
DRAT=R/'.scratch/glucose-reduction-v1/rebuild/bin/drat-trim'
CERT=MEM/'work/cert/r1300-s48'
checks={}
def sha(value):
 data = Path(value).read_bytes() if isinstance(value, (str, Path)) else value
 return hashlib.sha256(data).hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)

# Independent K5 sharpness and K6 exhaustive two-colour refutation.
def triangle_free(n,bits):
 for i,j,k in itertools.combinations(range(n),3):
  colors=[]
  for u,v in ((i,j),(i,k),(j,k)):
   a,b=sorted((u,v));idx=n*(n-1)//2-(n-a)*(n-a-1)//2+(b-a-1)
   colors.append((bits>>idx)&1)
  if colors[0]==colors[1]==colors[2]:return False
 return True
valid={n:sum(triangle_free(n,b) for b in range(1<<(n*(n-1)//2))) for n in (5,6)}
require(valid=={5:12,6:0},f'K5/K6 controls failed: {valid}')
checks['two_color_finite']={'K5_triangle_free_colorings':valid[5], 'K6_triangle_free_colorings':valid[6],
 'assignments_K6_checked':1<<15}

# Every attainable integer distribution has two full arms and all elementary bounds.
counts_by_total=collections.defaultdict(list)
for ns in itertools.product(range(6),repeat=3):
 if max(ns)<=5:
  counts_by_total[sum(ns)].append(ns)
  if sum(ns)>=14:
   require(sum(x==5 for x in ns)>=2,f'not two full arms: {ns}')
   require(min(ns)>=4 and min(a+b for a,b in itertools.combinations(ns,2))>=9,
           f'lower bounds fail: {ns}')
require(all(sum(x==5 for x in ns)<2 for ns in [(5,4,4)]),'sharpness example was not valid')
require((5,4,4) in counts_by_total[13],'13 has no one-full-arm counterexample')
# Explicit selector extension for all abstract models, including inactive guard.
extension_cases=0
for guard in (False,True):
 for ns in itertools.product(range(6),repeat=3):
  if guard and sum(ns)<14:continue
  full=[i for i,n in enumerate(ns) if n>=5]
  chosen=set(full[:2] if guard else [])
  q=[i in chosen for i in range(3)]
  require(all((not q[i]) or ns[i]>=5 for i in range(3)),'selector arm implication broken')
  if guard:
   require(all(q[i] or q[j] for i,j in itertools.combinations(range(3),2)),
           f'pair clauses broken: {ns}')
  extension_cases+=1
checks['distribution']={'integer_triples_0_to_5':6**3,'selector_extensions_checked':extension_cases,
 'total_13_counterexample':[5,4,4],'legal_totals_at_least_14':
 {str(t):v for t,v in sorted(counts_by_total.items()) if t>=14}}

# The regenerated formula preserves the exact original body and hashes.
raw=CNF.read_bytes();base=BASE.read_bytes()
head,rest=raw.split(b'\n',1);bhead,brest=base.split(b'\n',1)
_,_,nv,nc=head.split();_,_,bnv,bnc=bhead.split()
require(rest.startswith(brest),'original body not an exact prefix')
require(sha(raw)=='fe9de879d99b320c57c7d90582842a532a045da9c3d90c8df5880d96498eb9af','two5 hash mismatch')
require(sha(base)=='56ad3dc529f1b855e65fa3f3f5363e8275930a7cb6ea5b04dc01a112535b0837','base hash mismatch')
added=[tuple(map(int,l.split()[:-1])) for l in rest[len(brest):].decode().splitlines() if l]
require(len(added)+int(bnc)==int(nc),'added header count mismatch')
# Exactly 56*3 = 168 guarded three-literal selector relations appear.
pairs=[c for c in added if len(c)==3 and c[0]<0 and c[1]>int(bnv) and c[2]>int(bnv)]
require(len(pairs)==168,f'pair selector count {len(pairs)} != 168')
require(len({tuple(c) for c in pairs})==168,'duplicate pair selector clauses')
checks['generation']={'original_body_preserved':True,'base_sha256':sha(base),'augmented_sha256':sha(raw),
 'added_clauses':len(added),'pair_selector_clauses':len(pairs),
 'original_variables':int(bnv),'augmented_variables':int(nv),
 'coordinator_receipt':'work/m1-coordinator-r1300-two5.json'}

# Independent replay of the supplied representative original-parent arm lower bound.
request=json.loads((CERT/'request.json').read_text());query=CERT/'query.cnf';proof=CERT/'proof-nodeletions.drat'
qraw=query.read_bytes();qhead,qrest=qraw.split(b'\n',1)
require(sha(query)==request['query_sha256'],'query hash mismatch')
require(len(request['negating_units'])==10,'unexpected unit count')
require(qrest.startswith(brest),'query original-parent body mismatch')
praw=proof.read_bytes()
run=subprocess.run([str(DRAT),str(query),str(proof),'-i','-U','-W','-t','300'],capture_output=True)
text=(run.stdout+run.stderr).decode(errors='replace')
reads=[int(x) for x in re.findall(r'read (\d+) bytes from proof file',text)]
accepted=(run.returncode==0 and reads==[len(praw)] and [l for l in text.splitlines() if l.startswith('s ')]==['s VERIFIED']
          and 'WARNING' not in text.upper() and 'ERROR' not in text.upper() and '0 RAT lemmas in core' in text)
require(accepted,f'strict representative replay failed: {text[-1000:]}')
checks['original_parent_replay']={'accepted':accepted,'query_sha256':sha(query),'proof_sha256':sha(proof),
 'proof_bytes':len(praw),'full_read':reads,'flags':['-i','-U','-W','-t','300'],
 'clause_kind':'representative direct guarded per-arm lower bound; not a whole-row or full two5 proof'}

out=R/'research/k58-arm-cap-clauses/checks/two5-finite.json'
out.write_text(json.dumps(checks,indent=2,sort_keys=True)+'\n')
print(json.dumps(checks,indent=2,sort_keys=True))
