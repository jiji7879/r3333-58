import sys, glob
def load(p):
    t=[l.split() for l in open(p) if l.strip() and not l.startswith('#')]
    n=int(t[0][0]); M=[[int(x) for x in row] for row in t[1:1+n]]
    return n,M
def max_indep(n, adj):
    best=0
    order=sorted(range(n), key=lambda v: bin(adj[v]).count('1'))
    def rec(i, cur, cnt):
        nonlocal best
        if cnt + (n-i) <= best: return
        if i==n:
            best=max(best,cnt); return
        v=order[i]
        if not (adj[v] & cur): rec(i+1, cur | (1<<v), cnt+1)
        rec(i+1, cur, cnt)
    rec(0,0,0); return best
for p in sorted(glob.glob('artifacts/*.col')):
    n,M=load(p)
    if n < 44: continue
    al=[]
    for c in range(4):
        adj=[0]*n
        for i in range(n):
            for j in range(i+1,n):
                if M[i][j]==c: adj[i]|=1<<j; adj[j]|=1<<i
        al.append(max_indep(n,adj))
    print(f'{p.split("/")[-1]:45s} n={n:3d} alpha={al}')
