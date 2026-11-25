"""Replay every certified unit cut: regenerate the CNF, check its sha256, and replay the
stored DRAT with drat-trim (expecting 's VERIFIED').

usage: python3 src/ours/replay_cuts.py [board ...]
"""
import sys, json, csv, hashlib, subprocess
from pathlib import Path
sys.path.insert(0,'src/ours')
from pairlib import Board, cnf_bytes, DRAT
import unitcuts as U

def main(boards):
    rows=list(csv.DictReader(open('results/cuts.tsv'),delimiter='\t'))
    ok=bad=0
    for b in boards:
        B=Board(b); U.B=B
        B.chainlen=[len(ch) for ch in json.loads(Path(f'src/pilot/cnfs/{b}.counts.json').read_text())]
        mine=[r for r in rows if r['board']==b]
        for r in mine:
            k=int(r['k']); m=int(r['cut_m'])
            raw=cnf_bytes(B.n, U.witness_clauses(B,[k]*m))
            path=Path('out/replay.cnf')
            if hashlib.sha256(raw).hexdigest()!=r['cnf_sha256']:
                print('SHA MISMATCH',b,k,m,flush=True); bad+=1; continue
            path.write_bytes(raw)
            v=subprocess.run([DRAT,str(path),r['proof']],capture_output=True,text=True)
            if 's VERIFIED' in v.stdout: ok+=1
            else: print('PROOF FAILED',b,k,m,flush=True); bad+=1
        print(b,'replayed',len(mine),'ok so far',ok,'bad',bad,flush=True)
    print('TOTAL verified',ok,'bad',bad)
    return 0 if bad==0 else 1

if __name__=='__main__':
    main(sys.argv[1:] or ['local-15','live-07','live-14'])
