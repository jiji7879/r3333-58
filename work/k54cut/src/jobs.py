"""Enumerate retained coloured marks and emit a cut-strengthened K54 job."""
import argparse,gzip,json
from itertools import islice,product
from pathlib import Path
from board import ROOT,H
from orbits import stabilizer,act,actions_at,color_orbits
from cut_cnf import write
def catalogue(placement):
    if not 1<=placement<=24:raise ValueError('Placement must be in 1..24')
    p=placement-1
    pl=json.loads((ROOT/'data/placements.json').read_text())[p]
    reps=json.loads(gzip.decompress((ROOT/'data/rect_reps.json.gz').read_bytes()))[p]
    excluded=set(json.loads(gzip.decompress((ROOT/'results/omitted_orbit_ids.json.gz').read_bytes()))[p])
    return pl,reps,excluded,stabilizer(pl)
def marks(data,only=None):
    pl,reps,excluded,group=data
    for index in (range(len(reps)) if only is None else (only,)):
        if not 0<=index<len(reps):raise ValueError('Unknown mark ID')
        if index in excluded:continue
        u,v,x,y,_,weight=reps[index];R=((u,v),(14+x,14+y))
        actions=actions_at(R,[g for g in group if act(R,g)==R])
        _,options=color_orbits(pl['a'][1][H[u][v]],pl['b'][1][H[x][y]],actions)
        assert len(options)==weight
        for k,(word,_) in enumerate(options):
            yield (index,k,((u,v),(x,y),word))
def main():
    a=argparse.ArgumentParser(description=__doc__);s=a.add_subparsers(dest='cmd',required=True)
    p=s.add_parser('list');p.add_argument('placement',type=int);p.add_argument('--limit',type=int)
    p=s.add_parser('cnf');p.add_argument('placement',type=int);p.add_argument('mark_id',type=int);p.add_argument('color_id',type=int);p.add_argument('path',type=Path)
    o=a.parse_args();data=catalogue(o.placement)
    if o.cmd=='list':
        for i,k,(_,_,w) in islice(marks(data),o.limit):print(o.placement,i,k,*w)
    else:
        chosen=next((m for i,k,m in marks(data,o.mark_id) if k==o.color_id),None)
        if chosen is None:a.error('This mark was omitted by the certified cover, or the colour ID is outside the orbit list')
        print(write(f'placement-{o.placement:02}',o.path,chosen)[0])
if __name__=='__main__':main()
