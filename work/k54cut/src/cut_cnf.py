"""Emit a full K54 placement or sampled graph with every certified crossing-cut clause."""
from pathlib import Path
import argparse,gzip,json
from itertools import combinations,product
from collections import defaultdict
from board import BOARDS,ROOT,graph
def instance(key):
    if key.startswith('placement-'):
        pl=json.loads((ROOT/'data/placements.json').read_text())[int(key.split('-')[1])-1]
        p,q=[pl[k][0] for k in 'ab']
        board=dict(poles=[p,q],palettes=[pl[k][1] for k in 'ab'],rows=[0 if i==p else 16383^(1<<q) for i in range(14)])
        BOARDS[key]=board
    return BOARDS[key]
def augment(key,mark=None):
    b=instance(key);cuts=json.loads((ROOT/'results/cover.json').read_text())['cuts_by_pole']
    n,f,fixed,edges=graph(key,54,sort=True)
    pairs=[list(combinations([i for i in range(14) if i!=p],2)) for p in b['poles']]
    witnesses=defaultdict(list);start_n=n;start_f=len(f)
    for row,col in product(*pairs):
        rectangle=[(i,14+j) for i in row for j in col]
        if any(e in fixed and fixed[e]==3 for e in rectangle):continue
        n+=1
        for e in rectangle:
            if e in edges:f.append([-n,-edges[e][3]])
        witnesses[0,row].append(n);witnesses[1,col].append(n)
    sizes=[]
    for side,pairs_s in enumerate(pairs):
        flags={}
        for pair in pairs_s:
            if witnesses[side,pair]:
                n+=1;flags[pair]=n
                f.append([-n]+witnesses[side,pair])
        for mask in cuts[str(b['poles'][side])]:
            marked=[(u,v) for u,v in flags if ((mask>>u)^(mask>>v))&1]
            f.append([flags[pair] for pair in marked])
            sizes.append(sum(len(witnesses[side,pair]) for pair in marked))
    if mark is not None:
        row,col,colors=mark
        for (u,v),c in zip(product(row,col),colors):
            f.append([edges[u,14+v][c]])
    return n,f,dict(variables_added=n-start_n,clauses_added=len(f)-start_f,number_of_cuts=len(sizes),fewest_rectangles_on_a_cut=min(sizes))
def write(key,path,mark=None):
    nv,clauses,stats=augment(key,mark)
    raw=(f'p cnf {nv} {len(clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses)).encode()
    path.write_bytes(gzip.compress(raw,compresslevel=2,mtime=0) if path.suffix=='.gz' else raw)
    return stats,raw
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('case');p.add_argument('path',type=Path);a=p.parse_args()
    print(write(a.case,a.path)[0])
