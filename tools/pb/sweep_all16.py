"""Decide the sub-case 'every shared site has red degree 16' for every row and t.

For each child: build the CNF, run Kissat, and if UNSAT replay the DRAT proof with
drat-trim against the same file.  Writes a TSV ledger.
"""
import sys, os, subprocess, hashlib, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from encode import build
from pbdata import ROWS

BIN = '.ultramath/smwmq7hji/m3/bin'
OUT = sys.argv[1] if len(sys.argv) > 1 else '.scratch/pb/all16'
os.makedirs(OUT, exist_ok=True)
led = open(os.path.join(OUT, 'ledger.tsv'), 'w')
led.write('row\tt\tstrength\tstatus\tcnf_sha256\tproof_bytes\tproof_sha256\tchecker\tseconds\n')
for nm, M, D in ROWS:
    for t in range(1, 6):
        for strength in (1, 3):
            tag = '%s_t%d_s%d' % (nm, t, strength)
            cnf, _, _ = build(M, D, t, strength=strength, all16=True, footprint=False)
            cpath = os.path.join(OUT, tag + '.cnf')
            ppath = os.path.join(OUT, tag + '.drat')
            cnf.to_file(cpath)
            h = hashlib.sha256(open(cpath, 'rb').read()).hexdigest()
            t0 = time.time()
            r = subprocess.run([BIN + '/kissat', '-q', cpath, ppath],
                               capture_output=True, text=True, timeout=3600)
            st = 'UNSAT' if 'UNSATISFIABLE' in r.stdout else ('SAT' if 'SATISFIABLE' in r.stdout else 'OPEN')
            chk = ''
            if st == 'UNSAT':
                v = subprocess.run([BIN + '/drat-trim', cpath, ppath],
                                   capture_output=True, text=True, timeout=3600)
                chk = 'VERIFIED' if 's VERIFIED' in v.stdout else 'NOT VERIFIED'
            pb = os.path.getsize(ppath) if os.path.exists(ppath) else 0
            ph = hashlib.sha256(open(ppath, 'rb').read()).hexdigest() if pb else ''
            led.write('%s\t%d\t%d\t%s\t%s\t%d\t%s\t%s\t%.1f\n' % (nm, t, strength, st, h, pb, ph, chk, time.time() - t0))
            led.flush()
            print('%-9s t=%d s=%d %-6s %s %5d B %5.1fs' % (nm, t, strength, st, chk, pb, time.time() - t0), flush=True)
            if st == 'UNSAT' and chk == 'VERIFIED':
                os.remove(ppath)
led.close()
