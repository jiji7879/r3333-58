"""Bounded whole-placement and sample tests of the new clauses."""
import subprocess,sys,tempfile,json,hashlib,re
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from cut_cnf import write,ROOT,BOARDS
def task(job):
    case,exe,budget=job
    with tempfile.TemporaryDirectory() as d:
        f=Path(d)/'in';proof=Path(d)/'p'
        stats,raw=write(case,f)
        # Save a proof-generating rerun separately in the event of an UNSAT result.
        tick=subprocess.run([exe,'-c',str(budget),f],capture_output=True)
        assert tick.returncode in (0,10,20)
        r=dict(case=case,sha256=hashlib.sha256(raw).hexdigest(),budget=budget,status={0:'OPEN',10:'SAT candidate',20:'UNSAT candidate'}[tick.returncode],**stats)
        if tick.returncode:
            (ROOT/'work'/f'{case}.result').write_bytes(tick.stdout)
            raise RuntimeError(f'{case} returned {tick.returncode}; verify solution or replay a proof before recording it')
        return r
def main():
    exe=str(Path(sys.argv[1]).resolve());budget=int(sys.argv[2])
    samples=sorted(set(BOARDS)-{'live-17'})
    jobs=[(k,exe,budget) for k in [*(f'placement-{i:02}' for i in range(1,25)),*samples]]
    results=[];target=ROOT/'results/full-probes.json'
    with ProcessPoolExecutor(4) as pool:
        for row in pool.map(task,jobs):
            results.append(row);target.write_text(json.dumps(results,indent=1)+'\n')
            print(row['case'],row['status'],row['fewest_rectangles_on_a_cut'],flush=True)
if __name__=='__main__':main()
