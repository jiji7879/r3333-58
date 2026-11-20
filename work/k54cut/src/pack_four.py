"""Certify upper bounds on simultaneous four-support outsiders at a saturated pole."""
from itertools import combinations
from pathlib import Path
import sys,subprocess,json,gzip,tempfile
from all_singletons import formula
from template import ROOT
def main():
    exe=Path(sys.argv[1]).resolve();chk=Path(sys.argv[2]).resolve()
    dest=ROOT/'results/packing';dest.mkdir(exist_ok=True)
    exceptional=json.loads((ROOT/'results/saturated4.json').read_text())
    result={}
    for pole in (0,2,4):
        allowed=sorted(m for m in exceptional if not m>>pole&1);bad=[];models=[];records=[]
        for k in range(2,len(allowed)+1):
            for sel in combinations(allowed,k):
                if any(set(b)<=set(sel) for b in bad):continue
                nv,f=formula(pole,sel);raw=(f'p cnf {nv} {len(f)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in f)).encode()
                tag=f'{pole}-'+'-'.join(map(str,sel))
                with tempfile.TemporaryDirectory() as d:
                    cnf=Path(d)/'f';pr=Path(d)/'p';cnf.write_bytes(raw)
                    run=subprocess.run([exe,'-c','12000',cnf,pr],capture_output=True)
                    status={20:'UNSAT',10:'SAT',0:'OPEN'}[run.returncode]
                    if status=='UNSAT':
                        ck=subprocess.run([chk,cnf,pr],capture_output=True);assert ck.returncode==0 and b's VERIFIED' in ck.stdout.splitlines()
                        (dest/(tag+'.drat.gz')).write_bytes(gzip.compress(pr.read_bytes(),mtime=0));bad.append(sel)
                    if status=='SAT':
                        model={int(v) for l in run.stdout.splitlines() if l.startswith(b'v ') for v in l.split()[1:] if int(v)}
                        assert all(any(v in model for v in c) for c in f)
                        models.append(sel)
                records.append([sel,status])
            if not any(len(s)==k for s in models) and k>=2:
                # A budget stop remains admissible in all upper-bound computations.
                if all(r[1]!='OPEN' for r in records):break
        possible=[s for k in range(len(allowed)+1) for s in combinations(allowed,k) if not any(set(b)<=set(s) for b in bad)]
        limits=[max(sum(m>>i&1 for m in s) for s in possible) for i in range(14)]
        overall=max(map(len,possible))
        largest=next(sel for sel in models if len(sel)==overall)
        nv,f=formula(pole,largest)
        with tempfile.TemporaryDirectory() as d:
            cnf=Path(d)/'w';cnf.write_text(f'p cnf {nv} {len(f)}'+chr(10)+''.join(' '.join(map(str,c))+' 0'+chr(10) for c in f))
            run=subprocess.run([exe,cnf],capture_output=True);assert run.returncode==10
            model={int(v) for line in run.stdout.splitlines() if line.startswith(b'v ') for v in line.split()[1:] if int(v)}
            assert all(any(v in model for v in cl) for cl in f)
            (dest/f'pole-{pole}-largest.model.gz').write_bytes(gzip.compress(' '.join(map(str,sorted(model,key=abs))).encode(),mtime=0))
        result[pole]=dict(allowed=allowed,bad=bad,records=records,overall=overall,limits=limits,largest_witness_masks=largest)
        print(pole,len(records),len(bad),result[pole]['overall'],limits,flush=True)
        (dest/'summary.json').write_text(json.dumps(result,indent=1)+'\n')
if __name__=='__main__':main()
