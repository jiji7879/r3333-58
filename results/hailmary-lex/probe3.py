import sys, subprocess, random
sys.path.insert(0,'/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwp3xc7p/m3/w/k58-solver/k58')
sys.path.insert(0,'.')
from gluing import host
from pysat.formula import CNF
from hm import lex_leader, twins, matching
K = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/kissat'
random.seed(5)
N = 20
lit, base = host(N)
N0 = 49
toks = [t for l in open('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/artifacts/k49_from_n48_m5.col') if l.strip() and not l.startswith('#') for t in l.split()]
M0 = [[int(toks[2 + i*N0 + j]) for j in range(N0)] for i in range(N0)]
M = [[M0[i][j] if i != j else None for j in range(N)] for i in range(N)]   # a good colouring of K_N
edges = [(i,j) for i in range(N) for j in range(i+1,N)]
edges = [e for e in edges if e[0] < 10 and e[1] < 10]
random.shuffle(edges)
pin = [lit(i,j,M[i][j]) for (i,j) in edges[:25]]
print('N', N, 'pinned', len(pin))
for tag, npairs in (('none',0), ('lex3',3), ('lex10',10)):
    cnf = CNF(from_clauses=base + [[p] for p in pin])
    tw = twins(lit, set(pin), nv=N)
    mt = matching(tw)[:npairs]
    for u,v in mt: lex_leader(cnf, lit, u, v, nv=N)
    cnf.to_file(f'p3_{tag}.cnf')
    r = subprocess.run([K,'-q','--time=120',f'p3_{tag}.cnf'], capture_output=True, text=True)
    st = 'SAT' if r.returncode==10 else ('UNSAT' if r.returncode==20 else 'UNKNOWN')
    print(f'{tag:5s} twin_pairs={len(tw):4d} used={len(mt):2d} vars={cnf.nv} -> {st}', flush=True)
