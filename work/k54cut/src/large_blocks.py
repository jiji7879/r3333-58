"""Validate the weighted occupancy certificates for larger subsets."""
import gzip,json,random,sys
from itertools import combinations
from collections import Counter
from functools import lru_cache
from saturated import words
from template import ROOT
H=json.loads((ROOT/'data/h42.json').read_text())
group=json.loads((ROOT/'data/orbits.json').read_text())['group']
def image(s,g):return sum(1<<g[i] for i in range(14) if s>>i&1)
cert={r['mask']:r for r in map(json.loads,gzip.open(ROOT/'data/local_bounds.json.gz','rt'))}
@lru_cache(None)
def canonical(s):return min(image(s,g) for g in group)
def valid(s):
    return s.bit_count()<=3 or cert[canonical(s)]['bound']<=s.bit_count()
def check(s):
    if s.bit_count()<=3:return
    from itertools import permutations
    assert all(sorted(g)==list(range(14)) and any(all(H[g[i]][g[j]]==p[H[i][j]] for i,j in combinations(range(14),2)) for p in permutations(range(3))) for g in group)
    s=canonical(s);r=cert[s]
    ws=words(s) # ordinary responses on the complement, freely omit all positions of s
    costs=[0]*len(ws);total=0
    assert len(ws)==r['words']
    for weight,anchors in r['bins']:
        assert type(weight)==int and weight>0 and 1<=len(anchors)<=3
        assert len({a for a,c in anchors})==len(anchors)==len({c for a,c in anchors})
        assert all(0<=a<14 and 0<=c<3 and not s>>a&1 for a,c in anchors)
        cap=(0,16,5,2)[len(anchors)]-sum(all(H[v][a]==c for a,c in anchors) for v in range(14))
        assert cap>=0
        total+=cap*weight
        for k,w in enumerate(ws):
            if all(w[c]>>a&1 for a,c in anchors):costs[k]+=weight
    assert costs and min(costs)>0 and total//min(costs)==r['bound']<=s.bit_count()
