"""Exhaust all size-four capacities, including the ceiling on repeated degree-four columns."""
import itertools,json,subprocess
from template import ROOT
def main():
    H=json.loads((ROOT/'data/h42.json').read_text())
    exe=ROOT/'work/cap';exe.parent.mkdir(exist_ok=True)
    subprocess.run(['g++','-O3','-std=c++20',str(ROOT/'src/cap.cpp'),'-o',exe],check=True)
    masks=[sum(1<<i for i in v) for v in itertools.combinations(range(14),4)]
    data='42 -1 0\n'+' '.join(str(x) for row in H for x in row)+'\n'+''.join(f'42 {m} 6\n' for m in masks)
    run=subprocess.run([exe],input=data,text=True,capture_output=True,check=True)
    vals={int(m):int(k) for i,m,w,k in (s.split() for s in run.stdout.splitlines())}
    assert set(vals)==set(masks) and max(vals.values())==5
    special=sorted(m for m,k in vals.items() if k==5)
    pole_counts=[sum(m>>i&1 for m in special) for i in range(14)]
    assert len(special)==12 and min(pole_counts)==3 and max(pole_counts)==4
    assert set(json.loads((ROOT/'results/saturated4.json').read_text()))==set(special)
    print('Four-set capacities:',{v:list(vals.values()).count(v) for v in set(vals.values())})
if __name__=='__main__':main()
