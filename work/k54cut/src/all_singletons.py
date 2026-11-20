"""Decide coexistence of an exact four-support outsider with all 13 singleton slots."""
from itertools import combinations
from pathlib import Path
import sys,subprocess,json,gzip,tempfile
from template import ROOT
def formula(p,mask):
    H=json.loads((ROOT/'data/h42.json').read_text())
    support=(list(mask) if isinstance(mask,(list,tuple)) else [mask])+[1<<j for j in range(14) if j!=p]
    n=14+len(support)
    f=[];top=0;edges={}
    for a,b in combinations(range(n),2):
        if b<14:continue
        cs=range(4) if a>=14 else ([3] if support[b-14]>>a&1 else range(3))
        lits={}
        for c in cs:top+=1;lits[c]=top
        f.append(list(lits.values()));f.extend([-u,-v] for u,v in combinations(lits.values(),2));edges[a,b]=lits
    for a,b,d in combinations(range(n),3):
        if d<14:continue
        if b<14:
            c=H[a][b]
            if c in edges[a,d] and c in edges[b,d]:f.append([-edges[a,d][c],-edges[b,d][c]])
        else:
            for c in edges[a,b].keys() & edges[a,d].keys() & edges[b,d].keys():
                f.append([-edges[a,b][c],-edges[a,d][c],-edges[b,d][c]])
    return top,f
def main():
    from orbits import side_maps,P
    H=json.loads((ROOT/'data/h42.json').read_text());masks=json.loads((ROOT/'results/saturated4.json').read_text())
    cadical=Path(sys.argv[1]).resolve();checker=Path(sys.argv[2]).resolve()
    groups={g for p in P for q in range(14) for g in side_maps((0,1,2),(0,1,2),0,q,p,H)}
    all_cases={(p,m) for m in masks for p in range(14) if not m>>p&1}
    out=ROOT/'results/singletons';out.mkdir(exist_ok=True)
    rows=[]
    while all_cases:
        p,m=min(all_cases)
        orb=sorted({(g[p],sum(1<<g[i] for i in range(14) if m>>i&1)) for g in groups})
        assert set(orb)<=all_cases
        all_cases.difference_update(orb)
        nv,f=formula(p,m);raw=(f'p cnf {nv} {len(f)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in f)).encode()
        tag=f'{p}-{m}'
        with tempfile.TemporaryDirectory() as d:
            cnf=Path(d)/'f';pr=Path(d)/'p';cnf.write_bytes(raw)
            run=subprocess.run([cadical,'-c','25000',cnf,pr],capture_output=True)
            status={20:'UNSAT',10:'SAT',0:'OPEN'}[run.returncode]
            if status=='SAT':
                model={int(v) for s in run.stdout.splitlines() if s.startswith(b'v ') for v in s.split()[1:] if int(v)}
                assert all(any(v in model for v in cl) for cl in f)
                (out/(tag+'.model.gz')).write_bytes(gzip.compress(' '.join(map(str,sorted(model,key=abs))).encode(),mtime=0))
            elif status=='UNSAT':
                ck=subprocess.run([checker,cnf,pr],capture_output=True);assert ck.returncode==0 and b's VERIFIED' in ck.stdout.splitlines()
                (out/(tag+'.drat.gz')).write_bytes(gzip.compress(pr.read_bytes(),mtime=0))
        rows.append(dict(pole=p,mask=m,orbit=orb,status=status))
        print(tag,len(orb),status,flush=True)
        (out/'cases.json').write_text(json.dumps(rows,indent=1)+'\n')
if __name__=='__main__':main()
