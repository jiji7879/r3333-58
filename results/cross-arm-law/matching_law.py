import itertools, collections
def load(p):
    toks=[t for l in open(p) if l.strip() and not l.startswith('#') for t in l.split()]
    n=int(toks[0]); M=[[int(toks[2+i*n+j]) for j in range(n)] for i in range(n)]
    return n,M
for p in ['artifacts/k15_template_Tminus_aut2_m4.col','artifacts/k15_template_Uminus_aut10_m4.col']:
    n,M=load(p); seen=collections.Counter()
    for rho in range(n):
        N={c:[v for v in range(n) if v!=rho and M[rho][v]==c] for c in range(3)}
        for i,j in itertools.combinations(range(3),2):
            I,J=N[i],N[j]; cnt=collections.Counter()
            for a in I:
                for b in J: cnt[M[a][b]]+=1
            seen[(len(I),len(J),tuple(cnt[c] for c in range(3)))]+=1
    print('==',p.split('/')[-1])
    for key,c in sorted(seen.items()):
        print('  |I|,|J|=%s counts=%s seen %d' % (key[:2],key[2],c))
