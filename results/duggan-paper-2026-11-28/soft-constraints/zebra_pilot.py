#!/usr/bin/env python3
"""Literal Duggan zebra constraints x_(i,j),c <=> z_(j-i),c: Toeplitz, not circulant."""
from pathlib import Path
import itertools
import json
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
class Zebra:
    def __init__(self,n,k):
        self.n=n; self.k=k; self.edges=list(itertools.combinations(range(n),2)); self.m=len(self.edges)
        self.eid={e:i for i,e in enumerate(self.edges)}
    def x(self,e,c): return self.eid[tuple(sorted(e))]*self.k+c+1
    def z(self,d,c): return self.m*self.k+(d-1)*self.k+c+1
    def build(self):
        cs=[]
        for e in self.edges:
            xs=[self.x(e,c) for c in range(self.k)]; cs.append(xs)
            cs += [[-xs[c],-xs[d]] for c in range(self.k) for d in range(c+1,self.k)]
        for i,j,l in itertools.combinations(range(self.n),3):
            for c in range(self.k): cs.append([-self.x((i,j),c),-self.x((i,l),c),-self.x((j,l),c)])
        for d in range(1,self.n):
            zs=[self.z(d,c) for c in range(self.k)]; cs.append(zs)
            cs += [[-zs[c],-zs[h]] for c in range(self.k) for h in range(c+1,self.k)]
        for i,j in self.edges:
            d=j-i
            for c in range(self.k):
                x=self.x((i,j),c); z=self.z(d,c)
                cs.append([-x,z]); cs.append([x,-z])
        return cs
    def witness_colours(self,text):
        values=[]
        for line in text.splitlines():
            if line.startswith('v '): values += [int(x) for x in line[2:].split() if x!='0']
        true=set(x for x in values if x>0); colours=[]
        for d in range(1,self.n):
            active=[c for c in range(self.k) if self.z(d,c) in true]
            if len(active)!=1: raise ValueError(f'distance {d}: expected one colour, got {active}')
            colours.append(active[0])
        return colours
    def matrix(self,colours):
        a=[[0]*self.n for _ in range(self.n)]
        for i,j in self.edges: a[i][j]=a[j][i]=colours[j-i-1]
        return a

def defects(a):
    return [(i,j,l,a[i][j]) for i,j,l in itertools.combinations(range(len(a)),3)
            if a[i][j]==a[i][l]==a[j][l]]
def write_cnf(path,I,cs,extra=()):
    with path.open('w') as f:
        f.write(f'p cnf {I.m*I.k+(I.n-1)*I.k} {len(cs)+len(extra)}\n')
        for cl in list(cs)+list(extra): f.write(' '.join(map(str,cl))+' 0\n')
def solve(path):
    return subprocess.run(['cadical','-q',str(path)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
def brute(n,k):
    ans=0
    for c in itertools.product(range(k),repeat=n-1):
        a=[[0]*n for _ in range(n)]
        for i,j in itertools.combinations(range(n),2): a[i][j]=a[j][i]=c[j-i-1]
        if not defects(a): ans+=1
    return ans

def selftest():
    I=Zebra(4,4); cs=I.build(); path=HERE/'zebra_n4_control.cnf'; extra=[]; got=[]
    while True:
        write_cnf(path,I,cs,extra); p=solve(path)
        if p.returncode==20: break
        assert p.returncode==10,p.stdout
        colours=I.witness_colours(p.stdout); assert not defects(I.matrix(colours)); got.append(tuple(colours))
        extra.append([-I.z(d,c) for d,c in enumerate(colours,1)])
    expected=brute(4,4)
    assert expected==48 and len(got)==expected and len(set(got))==expected,(len(got),expected)
    print(json.dumps({'test':'literal_zebra_exact_enumeration','n':4,'k':4,'models':len(got),'brute_force':expected,'pass':True}))

def run51(conflicts=50000,timeout=15):
    I=Zebra(51,4); cs=I.build(); assert len(cs)==102775
    cnf=HERE/'toeplitz_k51.cnf'; drat=HERE/'toeplitz_k51.drat'; witness=HERE/'toeplitz_k51.solution'
    write_cnf(cnf,I,cs)
    cmd=['cadical','-q','-c',str(conflicts),'-t',str(timeout),'--binary=true',str(cnf),str(drat),'-w',str(witness)]
    with (HERE/'toeplitz_k51_solver.log').open('w') as out:
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        out.write('COMMAND: cadical -q -c 50000 -t 15 --binary=true toeplitz_k51.cnf toeplitz_k51.drat -w toeplitz_k51.solution\n')
        out.write(p.stdout);out.write(f'EXIT: {p.returncode}\n')
    result={'n':51,'k':4,'variables':5300,'clauses':len(cs),'conflict_cap':conflicts,'timeout':timeout,
            'solver_exit':p.returncode,'status':{0:'UNKNOWN',10:'SAT',20:'UNSAT'}[p.returncode],
            'scope':'literal Toeplitz zebra family only; not K51 base'}
    if p.returncode==10:
        text=witness.read_text(); colours=I.witness_colours(text); a=I.matrix(colours)
        assert not defects(a)
        model=HERE/'toeplitz_k51_candidate.col'
        with model.open('w') as f:
            f.write('51 4\n');f.writelines(' '.join(map(str,r))+'\n' for r in a)
        result.update(model=str(model.name),model_defects=0,candidate_requires_independent_check=True)
    elif p.returncode==20:
        clean=HERE/'toeplitz_k51_additions.drat'; metafile=HERE/'toeplitz_k51_normalization.json'
        normalizer=ROOT/'tools/color-resolved-wallcc/helpers/strip_binary_drat.py'
        subprocess.run(['python3',str(normalizer),str(drat),str(clean),str(metafile)],check=True,stdout=(HERE/'toeplitz_k51_normalization.stdout').open('w'))
        checker=ROOT/'tools/color-resolved-wallcc/bin/drat-trim'
        p2=subprocess.run([str(checker),str(cnf),str(clean),'-i','-U','-W','-t','60'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        (HERE/'toeplitz_k51_strict.log').write_text(p2.stdout+f'EXIT: {p2.returncode}\n')
        assert p2.returncode==0 and p2.stdout.splitlines().count('s VERIFIED')==1,p2.stdout
        assert not any(x in p2.stdout.upper() for x in ('WARNING','ERROR')),p2.stdout
        assert f'read {clean.stat().st_size} bytes from proof file' in p2.stdout,p2.stdout
        result.update(strict_verified=True,normalized_drat_bytes=clean.stat().st_size)
    else:
        result.update(no_family_exclusion=True,no_model=True)
    (HERE/'toeplitz_k51_result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':
    if len(sys.argv)==2 and sys.argv[1]=='selftest': selftest()
    elif len(sys.argv)==2 and sys.argv[1]=='run51': run51()
    else: raise SystemExit('usage: zebra_pilot.py selftest | run51')
