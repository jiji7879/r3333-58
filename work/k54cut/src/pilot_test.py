"""Build a single-core graph from specified outsider count columns."""
from itertools import combinations
def graph(H,slots,columns,prices,gated):
    n=14+len(slots);cols={};f=[];top=0
    for i,j in combinations(range(n),2):
        if j<14:continue
        e=tuple(range(top+1,top+5));top+=4;cols[i,j]=e
        f.append(list(e));f.extend([-a,-b] for a,b in combinations(e,2))
    for i,j,k in combinations(range(n),3):
        if k<14:continue
        if j<14:
            c=H[i][j];f.append([-cols[i,k][c],-cols[j,k][c]])
        else:
            for c in range(4):f.append([-cols[i,j][c],-cols[i,k][c],-cols[j,k][c]])
    flags=[]
    for j,t in enumerate(slots,14):
        rect,side,signature,_=columns[t];mask=rect[side]
        prefix=[]
        if gated:top+=1;flags.append(top);prefix=[-top]
        for p in range(14):
            if not mask>>p&1:f.append(prefix+[-cols[p,j][3]])
        for b,(anchors,wt) in enumerate(prices[side]):
            items=[(p,h) for h,p in enumerate(anchors) if p!=14]
            if any(mask>>p&1 for p,h in items):
                assert not signature>>b&1
                continue
            lits=[cols[p,j][h] for p,h in items]
            if signature>>b&1:f.extend(prefix+[v] for v in lits)
            else:f.append(prefix+[-v for v in lits])
    return top,f,flags
