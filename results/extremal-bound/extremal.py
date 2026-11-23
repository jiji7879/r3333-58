#!/usr/bin/env python3
"""Encode the new bound 'at most 12 of the 42 slots omit a colour' on the
42-slot instance, and measure whether it buys anything.

A slot x is omitting (extremal) when some ordinary part M_f(x) is empty.
    e_f(x)  <->  AND over a in A of  not cell[x,a,f]
    ext(x)  <->  OR over f of e_f(x)
    at_most 12 of the 42 ext(x)
All three are implied by the branch, so the encoding is sound either way; the
question is whether it helps the search.
"""
import sys, subprocess, time, json
sys.path.insert(0, '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwrmwgf7/m1')
import ladder
K = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/kissat'

def build(bound):
    tpl = ladder.load_col(ladder.TPL_DEFAULT)
    cnf, cell, q, S, N = ladder.build(tpl, [14, 14, 14], xt=True)
    if bound is not None:
        ext = []
        for x in range(N):
            es = []
            for f in (1, 2, 3):
                e = cnf.new(); es.append(e)
                for a in range(15):
                    cnf.add([-e, -cell[x, a, f]], 'edef')      # e -> empty
                cnf.add([e] + [cell[x, a, f] for a in range(15)], 'edef')  # nonempty -> not e
            ex = cnf.new(); ext.append(ex)
            for e in es: cnf.add([-e, ex])
            cnf.add([-ex] + es)
        cnf.at_most(ext, bound, 'extbound')
    return cnf

def solve(cnf, path, secs):
    with open(path, 'w') as fh:
        fh.write('p cnf %d %d\n' % (cnf.nv, len(cnf.cl)))
        for cl in cnf.cl: fh.write(' '.join(map(str, cl)) + ' 0\n')
    t0 = time.monotonic()
    r = subprocess.run([K, '-q', '--time=%d' % secs, path, path.replace('.cnf', '.drat')],
                       capture_output=True, text=True)
    st = 'UNSAT' if r.returncode == 20 else ('SAT' if r.returncode == 10 else 'UNKNOWN')
    return st, round(time.monotonic() - t0, 1)

if __name__ == '__main__':
    secs = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    for tag, b in (('base', None), ('ext12', 12)):
        cnf = build(b)
        st, wall = solve(cnf, f'ext_{tag}.cnf', secs)
        print(json.dumps(dict(enc=tag, status=st, wall=wall, vars=cnf.nv, clauses=len(cnf.cl))), flush=True)
