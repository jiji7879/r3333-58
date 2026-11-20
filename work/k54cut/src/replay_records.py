"""Independently reconstruct the small refutations, packing frontiers and improved count CNFs."""
from pathlib import Path
from collections import Counter
from itertools import combinations
from functools import lru_cache
import gzip,json,subprocess,tempfile,hashlib
from template import ROOT
from pilot_test import graph
from pilot_columns import columns_for
from all_singletons import formula
def load(p):return json.loads(p.read_text())
def dimacs(n,f):return (f'p cnf {n} {len(f)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in f)).encode()
def trace(exe,cnf,pr):
    with tempfile.TemporaryDirectory() as folder:
        tmp=Path(folder);(tmp/'cnf').write_bytes(cnf);(tmp/'drat').write_bytes(gzip.decompress(pr.read_bytes()))
        ck=subprocess.run([exe,tmp/'cnf',tmp/'drat'],capture_output=True)
        assert ck.returncode==0 and b's VERIFIED' in ck.stdout.splitlines()
def main():
    exe=ROOT/'work/drat-trim';exe.parent.mkdir(exist_ok=True)
    subprocess.run(['cc','-O2','-std=gnu11',ROOT/'src/drat-trim.c','-lm','-o',exe],check=True)
    pack=ROOT/'results/packing';summary=load(pack/'summary.json');certificates=0
    E=set(load(ROOT/'results/saturated4.json'))
    for p,info in summary.items():
        p=int(p);possible=sorted(s for s in E if not s>>p&1)
        assert possible==info['allowed']
        for s in info['bad']:
            assert len(set(s))==len(s) and set(s)<=set(possible)
            nv,f=formula(p,s);tag=str(p)+'-'+'-'.join(map(str,s))
            trace(exe,dimacs(nv,f),pack/(tag+'.drat.gz'));certificates+=1
        candidates=[s for k in range(len(possible)+1) for s in combinations(possible,k) if all(not set(b)<=set(s) for b in info['bad'])]
        assert max(map(len,candidates))==info['overall']
        n,clauses=formula(p,info['largest_witness_masks'])
        assert len(info['largest_witness_masks'])==info['overall'] and set(info['largest_witness_masks'])<=set(possible)
        model=set(map(int,gzip.decompress((pack/f'pole-{p}-largest.model.gz').read_bytes()).split()))
        assert not any(-v in model for v in model) and all(any(v in model for v in c) for c in clauses)
        assert info['limits']==[max(sum(m>>i&1 for m in s) for s in candidates) for i in range(14)]
    print('Replayed',certificates,'packing proofs and all three upper bounds.')
    dest=ROOT/'results/pilots';data=ROOT/'data/pilots';H=load(ROOT/'data/h42.json')
    all_results=load(dest/'results.json');cards=load(dest/'re-solve.json')
    for board in ('local-15','live-07','live-14'):
        rows=[r for r in all_results if r['board']==board]
        cols=columns_for(board);prices=load(ROOT/f'data/prices/{board}.json')['side']
        slots=json.loads(gzip.decompress((data/f'{board}.counts.json.gz').read_bytes()));cuts=set()
        for r in rows:
            core=r['core'];mult=Counter(core);tag=f"{board}-{r['source']}-{r['side']}"
            old=dict(load(data/f"{board}-{r['source']}.counts.json"))
            assert r['verified'] and all(n<=old.get(i,0) and cols[i][1]==r['side'] for i,n in mult.items())
            n,f,_=graph(H,core,cols,prices,False);raw=dimacs(n,f)
            assert raw==gzip.decompress((dest/(tag+'.cnf.gz')).read_bytes()) and hashlib.sha256(raw).hexdigest()==r['sha256']
            trace(exe,raw,dest/(tag+'.drat.gz'))
            cuts.add(tuple(sorted(-slots[i][n-1] for i,n in mult.items())))
        raw=gzip.decompress((dest/f'{board}-after.cnf.gz').read_bytes());header,body=raw.split(b'\n',1)
        terms=body.splitlines(keepends=True);_,_,nv,nc=header.split();assert int(nc)==len(terms)
        assert [tuple(map(int,s.split()[:-1])) for s in terms[-len(cuts):]]==sorted(cuts)
        orig=f'p cnf {int(nv)} {int(nc)-len(cuts)}\n'.encode()+b''.join(terms[:-len(cuts)])
        for card in (c for c in cards if c['board']==board):
            assert card['input_sha256']==hashlib.sha256(orig).hexdigest() and card['strengthened_sha256']==hashlib.sha256(raw).hexdigest()
            key=f"{board}-{card['solver']}-after"
            model=set(map(int,gzip.decompress((dest/(key+'.model.gz')).read_bytes()).split()))
            assert not any(-v in model for v in model)
            assert all(any(int(v) in model for v in s.split()[:-1]) for s in terms)
            counts=[[i,n] for i,chain in enumerate(slots) if (n:=sum(v in model for v in chain))]
            assert counts==load(dest/(key+'.counts.json'))
        print(board,len(rows),'replayed local cuts and two checked strengthened count models.')
if __name__=='__main__':main()
