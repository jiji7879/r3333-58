"""SymPy permutation-group quotient of the forced marked rectangles of seed 12."""
from itertools import combinations,permutations,product
from functools import lru_cache
from collections import Counter
from sympy.combinatorics import Permutation, PermutationGroup
from board import ROOT,H
import json
P=list(permutations(range(3)))


def side_maps(source,target,p,q,pal,matrix=H):
    # All vertex bijections preserving the rooted palette action.
    candidates=[]
    for u in range(14):
        candidates.append([v for v in range(14) if (u==p)==(v==q) and
                           all(matrix[u].count(c)==matrix[v].count(target.index(pal[source[c]])) for c in range(3))])
    maps=[];assigned={};used=set()
    def grow():
        if len(assigned)==14:
            maps.append(tuple(assigned[i] for i in range(14)));return
        v,opts=min(((i,[j for j in candidates[i] if j not in used and
                         all(target[matrix[j][w]]==pal[source[matrix[i][u]]] for u,w in assigned.items())])
                    for i in range(14) if i not in assigned),key=lambda pair:len(pair[1]))
        for j in opts:
            assigned[v]=j;used.add(j);grow();used.remove(j);del assigned[v]
    grow();return maps


def stabilizer(pl):
    ps=[pl[k][0] for k in ('a','b')];cs=[pl[k][1] for k in ('a','b')]
    maps=set()
    for pal in P:
        for sw in (0,1):
            af=side_maps(cs[0],cs[sw],ps[0],ps[sw],pal)
            bf=side_maps(cs[1],cs[1-sw],ps[1],ps[1-sw],pal)
            for a,b in product(af,bf):
                maps.add(tuple(x+14*sw for x in a)+tuple(x+14*(1-sw) for x in b)+tuple(28+x for x in pal))
    group=PermutationGroup([Permutation(list(g)) for g in sorted(maps)])
    actual={tuple(g.array_form) for g in group.generate_schreier_sims()}
    assert actual==maps and group.order()==len(maps)
    return sorted(maps)


def act(R,g):
    a,b=R
    l=tuple(sorted(g[i] for i in a));r=tuple(sorted(g[i] for i in b))
    return (r,l) if l[0]>=14 else (l,r)


@lru_cache(None)
def color_orbits(c,d,actions):
    valid={w for w in product(range(3),repeat=4) if all(w[j]!=c or w[j+2]!=c for j in (0,1))
           and all(w[2*i]!=d or w[2*i+1]!=d for i in (0,1))}
    seen=set();reps=[]
    for w in sorted(valid):
        if w in seen:continue
        orbit=set()
        for pos,pal in actions:
            z=[None]*4
            for i in range(4):z[pos[i]]=pal[w[i]]
            orbit.add(tuple(z))
        assert orbit<=valid and not (orbit&seen)
        seen.update(orbit);reps.append((w,len(orbit)))
    assert seen==valid
    return len(valid),reps


def actions_at(R,gs):
    edges=[(i,j) for i in R[0] for j in R[1]]
    return tuple(sorted({(tuple(edges.index(tuple(sorted((g[i],g[j])))) for i,j in edges),
                          tuple(g[i]-28 for i in (28,29,30))) for g in gs}))


def analyze(idx,pl):
    ps=[pl[k][0] for k in ('a','b')];cs=[pl[k][1] for k in ('a','b')]
    gs=stabilizer(pl)
    left=list(combinations([i for i in range(14) if i!=ps[0]],2))
    right=list(combinations([i+14 for i in range(14) if i!=ps[1]],2))
    seen=set();raw=unique=0;reps=[];example=None
    for R in product(left,right):
        if R in seen:continue
        images=[act(R,g) for g in gs];orbit=set(images)
        assert not (seen&orbit);seen.update(orbit)
        stab=[g for im,g in zip(images,gs) if im==R]
        (a,b),(x,y)=R;c=cs[0][H[a][b]];d=cs[1][H[x-14][y-14]]
        legal,C=color_orbits(c,d,actions_at(R,stab))
        raw+=legal*len(orbit);unique+=len(C)
        reps.append([a,b,x-14,y-14,len(orbit),len(C)])
        if example is None:example=[a,b,x-14,y-14,list(C[0][0])]
    assert len(seen)==6084 and sum(t[-2] for t in reps)==6084
    return dict(placement=idx,group=len(gs),raw_rect=len(seen),rect=len(reps),raw_colored=raw,colored=unique,example=example),reps

if __name__=='__main__':
    pls=json.loads((ROOT/'data/placements.json').read_text());summary=[];out=[]
    for ix,pl in enumerate(pls,1):
        item,blocks=analyze(ix,pl);summary.append(item);out.append(blocks)
    import gzip
    (ROOT/'results/orbits.json').write_text(json.dumps(summary,indent=1)+'\n')
    (ROOT/'data/rect_reps.json.gz').write_bytes(gzip.compress(json.dumps(out,separators=(',',':')).encode(),mtime=0))
    print({k:sum(r[k] for r in summary) for k in ['raw_rect','rect','raw_colored','colored']},flush=True)
