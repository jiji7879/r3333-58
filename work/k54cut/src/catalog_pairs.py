"""Rooted pairs under independent vertex labels, common color labels and side swap."""
from pathlib import Path
from itertools import permutations,combinations_with_replacement
from collections import Counter
import json,argparse
ROOT=Path(__file__).resolve().parent
PERMS=list(permutations(range(3)))
def compose(p,q):return tuple(p[i] for i in q)
def decode(s):
    n=ord(s[0])-63;m=[[-1]*n for _ in range(n)]
    for k,(i,j) in enumerate((i,j) for j in range(n) for i in range(j)):
        m[i][j]=m[j][i]=((ord(s[2+k//3])-63)>>(4-2*(k%3))&3)-1
    return m
def autos(m,colors):
    n=len(m);mapping=[-1]*n
    d=[tuple(row.count(c) for c in range(3)) for row in m]
    options=[[j for j in range(n) if all(d[j][colors[c]]==d[i][c] for c in range(3))] for i in range(n)]
    def walk(assigned,remaining,used):
        if not remaining:
            yield tuple(mapping);return
        def choices(i):return [j for j in options[i] if j not in used and all(colors[m[i][a]]==m[j][mapping[a]] for a in assigned)]
        i,opts=min(((i,choices(i)) for i in remaining),key=lambda x:len(x[1]))
        for j in opts:
            mapping[i]=j
            yield from walk(assigned+[i],remaining-{i},used|{j})
        mapping[i]=-1
    yield from walk([],set(range(n)),set())

def setup(size):
    mats=[decode(s) for s in (ROOT/'data'/f'r333_{size}.mc').read_text().splitlines()]
    who={}; reps=[]
    for idx,m in enumerate(mats):
        aut=[(tuple(g.index(i) for i in range(3)),mapping) for g in PERMS for mapping in autos(m,g)]
        for r in range(size):
            for p in PERMS:
                if (idx,r,p) in who:continue
                k=len(reps);reps.append((idx,r,p))
                for inv,mapping in aut:
                    t=idx,mapping[r],compose(p,inv)
                    assert t not in who or who[t]==k
                    who[t]=k
    acts=[[who[idx,r,compose(g,p)] for idx,r,p in reps] for g in PERMS]
    return reps,acts
def count(size,save=None):
    reps,acts=setup(size)
    fixed=[]
    for g in acts:
        f=sum(g[i]==i for i in range(len(g)))
        two=sum(g[i]!=i and g[g[i]]==i for i in range(len(g)))//2
        fixed.append(f*(f+1)//2+two)
    assert sum(fixed)%6==0
    sizepairs=sum(fixed)//6
    print(size,len(reps),sizepairs,'fixed by permutations',fixed,flush=True)
    if save:
        rows=[]
        for i,j in combinations_with_replacement(range(len(reps)),2):
            if (i,j)==min(tuple(sorted((g[i],g[j]))) for g in acts):
                rows.append([reps[i],reps[j]])
        assert len(rows)==sizepairs
        save.write_text(json.dumps(rows,indent=1)+'\n')
    return sizepairs
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('size',type=int);p.add_argument('--save',type=Path)
    a=p.parse_args();count(a.size,a.save)
