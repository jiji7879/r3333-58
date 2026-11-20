"""Produce or verify an exhaustive orbit cover by crossing a certified two-part cut."""
import argparse,json,gzip
from functools import lru_cache
from itertools import combinations
from template import ROOT
from large_blocks import valid,check
from orbits import stabilizer,act,actions_at,color_orbits
from board import H
check=lru_cache(None)(check)
def all_cuts(p,exc):
    full=16383^(1<<p)
    def locally_tight(s):
        k=s.bit_count()
        if k==4:return s not in exc
        return valid(s)
    ok=[False]*16384;ok[0]=True
    for s in range(1,16384):
        if s&~full:continue
        ok[s]=locally_tight(s) and all(ok[s^(1<<j)] for j in range(14) if s>>j&1)
    return [s for s in range(1,full) if s&~full==0 and s<(full^s) and ok[s] and ok[full^s]]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--build',action='store_true');args=parser.parse_args()
    placements=json.loads((ROOT/'data/placements.json').read_text())
    reps=json.loads(gzip.decompress((ROOT/'data/rect_reps.json.gz').read_bytes()))
    exc=set(json.loads((ROOT/'results/saturated4.json').read_text()))
    cuts={p:all_cuts(p,exc) for p in (0,2,4)}
    for p,masks in cuts.items():
        full=16383^(1<<p);assert masks
        for m in masks:
            for s in [m,full^m]:
                t=s
                while t:
                    if t.bit_count()>=5:check(t)
                    if t.bit_count()==4:assert t not in exc
                    t=(t-1)&s
    path=ROOT/'results/cover.json';omit=ROOT/'results/omitted_orbit_ids.json.gz'
    table=[];removed=[];saved={} if args.build else json.loads(path.read_text())
    for k,(pl,rs) in enumerate(zip(placements,reps),1):
        poles=[pl[t][0] for t in 'ab'];pal=[pl[t][1] for t in 'ab']
        pts=[[i for i in range(14) if i!=p] for p in poles]
        pairs=[list(combinations(v,2)) for v in pts];order=[{e:i for i,e in enumerate(P)} for P in pairs]
        perms=stabilizer(pl);seen=set();proj=[[],[]]
        for a,b,x,y,n,w in rs:
            R=((a,b),(14+x,14+y));imgs=[act(R,g) for g in perms];orb=set(imgs)
            assert len(orb)==n and not seen&orb;seen.update(orb)
            actions=actions_at(R,[g for g,z in zip(perms,imgs) if z==R])
            assert w==len(color_orbits(pal[0][H[a][b]],pal[1][H[x][y]],actions)[1])
            proj[0].append(sum(1<<order[0][e] for e in {r for r,c in orb}))
            proj[1].append(sum(1<<order[1][e] for e in {(u-14,v-14) for r,(u,v) in orb}))
        assert len(seen)==6084
        weights=[r[-1] for r in rs]
        candidates=[(s,m) for s in (0,1) for m in cuts[poles[s]]]
        if not args.build:
            entry=saved['placements'][k-1];candidates=[(entry['cut_side'],entry['first_part'])]
            assert candidates[0][1] in cuts[poles[candidates[0][0]]]
        best=-1
        for side,m in candidates:
            cross=sum(1<<i for i,(u,v) in enumerate(pairs[side]) if ((m>>u)^(m>>v))&1)
            drop=[i for i,p in enumerate(proj[side]) if not p&cross]
            score=sum(weights[i] for i in drop)
            if score>best:best=score;ids=drop;winner=(side,m,cross.bit_count())
        side,m,c=winner;removed.append(ids)
        table.append(dict(placement=k,cut_side=side,first_part=m,raw_permitted=78*c,old_marks=len(rs),kept_marks=len(rs)-len(ids),old_colored=sum(weights),kept_colored=sum(weights)-best))
    result=dict(cuts_by_pole={str(k):v for k,v in cuts.items()},placements=table,totals={key:sum(r[key] for r in table) for key in ('old_marks','kept_marks','old_colored','kept_colored')})
    if args.build:
        path.write_text(json.dumps(result,indent=1)+'\n');omit.write_bytes(gzip.compress(json.dumps(removed,separators=(',',':')).encode(),mtime=0))
    else:
        assert result==saved and removed==json.loads(gzip.decompress(omit.read_bytes()))
    print(result['totals'])
if __name__=='__main__':main()
