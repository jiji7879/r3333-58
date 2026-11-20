"""Direct graph encoding of a fixed binary crossing pattern and free outside vertices."""
from itertools import combinations
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
BOARDS=json.loads((ROOT/'data/boards.json').read_text())
H=json.loads((ROOT/'data/h42.json').read_text())


def write_cnf(path,n,clauses):
    with open(path,'w') as f:
        f.write(f'p cnf {n} {len(clauses)}\n')
        for c in clauses:f.write(' '.join(map(str,c))+' 0\n')


def graph(key, order=54, sort=True):
    b=BOARDS[key];fixed={}
    for side,p in enumerate(b['palettes']):
        for i,j in combinations(range(14),2):
            fixed[14*side+i,14*side+j]=p[H[i][j]]
    for i,row in enumerate(b['rows']):
        for j in range(14):
            if not(row>>j&1):fixed[i,14+j]=3
    x={};f=[];nv=0
    for i,j in combinations(range(order),2):
        if (i,j) in fixed:continue
        x[i,j]=tuple(range(nv+1,nv+5));nv+=4
        f.append(x[i,j]);f.extend((-v,-w) for v,w in combinations(x[i,j],2))
    for i,j,k in combinations(range(order),3):
        for c in range(4):
            cl=[]
            for e in ((i,j),(i,k),(j,k)):
                if e in x:cl.append(-x[e][c])
                elif fixed[e]!=c:break
            else:f.append(cl)
    if sort:
        for w in range(28,order-1):
            guard=[]
            for i in range(28):
                left=x[i,w];right=x[i,w+1]
                for c,d in combinations(range(4),2):f.append(guard+[-left[d],-right[c]])
                if i<27:
                    nv+=1
                    for c in range(4):f.append(guard+[-left[c],-right[c],nv])
                    guard=[-nv]
    return nv,f,fixed,x

if __name__=='__main__':
    import sys
    key=sys.argv[1];n=int(sys.argv[2]);v,f,*_=graph(key,n)
    write_cnf(ROOT/'cnfs'/f'graph-{key}-{n}.cnf',v,f)
