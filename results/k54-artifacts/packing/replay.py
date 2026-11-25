"""Replay the 39 stored packing refutations of work/k54cut/results/packing.

For every set listed under "bad" in results/packing/summary.json:
  * rebuild the CNF with enc.py (byte-identical to the handoff's own generator,
    checked separately),
  * check the stored DRAT with build/drat-trim (exit 0 and "s VERIFIED"),
  * solve the same CNF again with pysat CaDiCaL (second, independent route).

Writes pack/replay.json.
"""
import gzip
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import enc

ARCH = Path('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/work/k54cut')
BUILD = Path('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/work/k54/build')
DRAT = BUILD / 'drat-trim'
HERE = Path(__file__).resolve().parent


def solve_unsat(nv, clauses):
    from pysat.solvers import Cadical153
    with Cadical153(bootstrap_with=clauses) as s:
        res = s.solve()
    return res


def main():
    H = enc.load_h42(ARCH / 'data/h42.json')
    summary = json.loads((ARCH / 'results/packing/summary.json').read_text())
    packing = ARCH / 'results/packing'
    out = []
    tmp = Path(tempfile.mkdtemp(dir=HERE, prefix='tmp-'))
    for pole in sorted(summary, key=int):
        d = summary[pole]
        for sel in d['bad']:
            nv, clauses, raw = enc.cnf(int(pole), sel, H)
            cnf = tmp / 'f.cnf'
            cnf.write_bytes(raw)
            tag = '%s-%s' % (pole, '-'.join(map(str, sel)))
            proof_gz = packing / (tag + '.drat.gz')
            rec = dict(pole=int(pole), masks=sel, nv=nv, nclauses=len(clauses),
                       cnf_sha256=enc.sha(raw),
                       proof_sha256=enc.sha(proof_gz.read_bytes()),
                       proof_bytes=None, drat=None, drat_stdout='', solve=None)
            pr = tmp / 'p.drat'
            pr.write_bytes(gzip.decompress(proof_gz.read_bytes()))
            rec['proof_bytes'] = pr.stat().st_size
            run = subprocess.run([str(DRAT), str(cnf), str(pr)],
                                 capture_output=True, text=True)
            rec['drat_rc'] = run.returncode
            rec['drat_verdict'] = [l for l in run.stdout.splitlines() if l.startswith('s ')]
            rec['drat'] = ('s VERIFIED' in run.stdout.splitlines()) and run.returncode == 0
            rec['solve'] = 'UNSAT' if solve_unsat(nv, clauses) is False else 'SAT'
            assert rec['drat'], (tag, rec)
            assert rec['solve'] == 'UNSAT', (tag, rec)
            out.append(rec)
            print(tag, 'VERIFIED', rec['cnf_sha256'][:16], rec['proof_bytes'], 'bytes',
                  flush=True)
    (HERE / 'replay.json').write_text(json.dumps(out, indent=1) + '\n')
    print('replayed', len(out), 'refutations; all DRAT verified, all re-solved UNSAT')
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()


if __name__ == '__main__':
    main()
