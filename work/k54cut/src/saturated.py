"""Test small c-supports of an extra outsider in the presence of one singleton at every support position."""
from itertools import combinations
from functools import lru_cache
from template import ROOT
import json
H=json.loads((ROOT/'data/h42.json').read_text())
@lru_cache(None)
def words(s):
    n=len(H);adj=[[sum(1<<j for j,x in enumerate(r) if x==c) for c in range(3)] for r in H]
    masks=[0,0,0,s];out=[]
    def gen(i):
        if i==n:out.append(tuple(masks));return
        if s>>i&1:gen(i+1);return
        for c in range(3):
            if not masks[c]&adj[i][c]:
                masks[c]^=1<<i;gen(i+1);masks[c]^=1<<i
    gen(0);return out
def compatible(ws,allow):
    n=len(ws);edges=list(combinations(range(n),2));assigned={}
    def extend(k):
        if k==len(edges):return dict(assigned)
        i,j=edges[k]
        for c in allow(ws[i],ws[j]):
            if any(assigned.get((a,i))==c==assigned.get((a,j)) for a in range(i)):continue
            assigned[i,j]=c
            res=extend(k+1)
            if res is not None:return res
            del assigned[i,j]
        return None
    return extend(0)
def witness(s):
    from itertools import product
    def allow(a,b):return [c for c in range(4) if not a[c]&b[c]]
    single=[words(1<<i) for i in range(14) if s>>i&1]
    for w in words(s):
        # All w-to-singleton edges must be ordinary. Discard impossible choices before taking products.
        opts=[[x for x in group if allow(x,w)] for group in single]
        for ws in product(*opts):
            family=(w,)+ws
            assignment=compatible(family,allow)
            if assignment is not None:return family
    return None
if __name__=='__main__':
    S=[sum(1<<i for i in t) for t in combinations(range(14),4)]
    good=[]
    for s in S:
        if witness(s):good.append(s)
    print('Four-point supports compatible with the four designated singleton outsiders:',len(good),good,flush=True)
    (ROOT/'results/saturated4.json').write_text(json.dumps(good)+'\n')
