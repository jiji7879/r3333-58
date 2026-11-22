#!/usr/bin/env python3
"""Item 3: re-encode each slot's colour-f part as ONE variable over the
independent sets of that colour graph (317 sets), instead of 15 edge cells.

The selectors are *definitional* (sel <-> AND of its cells), so the formula is
logically unchanged -- this measures only whether the clause structure helps
propagation, which is exactly the claim being tested.
"""
import sys, itertools, subprocess, time, json
sys.path.insert(0, '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwrmwgf7/m1')
import ladder
K = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/kissat'

def indep_sets(tpl, c):
    n = len(tpl)
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if tpl[i][j] == c]
    out = []
    for S in range(1 << n):
        if all(not ((S >> i) & 1 and (S >> j) & 1) for i, j in edges):
            out.append([i for i in range(n) if (S >> i) & 1])
    return out

def build(with_sets):
    tpl = ladder.load_col(ladder.TPL_DEFAULT)
    cnf, cell, q, S, N = ladder.build(tpl, [14, 14, 14], xt=True)
    if with_sets:
        for f in (1, 2, 3):
            for I in indep_sets(tpl, f - 1):
                if not I:
                    continue
                for x in range(N):
                    sel = cnf.new()
                    for a in I:
                        cnf.add([-sel, cell[x, a, f]], 'seldef')          # sel -> cells
                    cnf.add([sel] + [-cell[x, a, f] for a in I], 'seldef')  # cells -> sel
    return cnf

def solve(cnf, path, secs):
    with open(path, 'w') as fh:
        fh.write('p cnf %d %d\n' % (cnf.nv, len(cnf.cl)))
        for cl in cnf.cl:
            fh.write(' '.join(map(str, cl)) + ' 0\n')
    t0 = time.monotonic()
    r = subprocess.run([K, '-q', '--time=%d' % secs, path, path.replace('.cnf', '.drat')],
                       capture_output=True, text=True)
    st = 'UNSAT' if r.returncode == 20 else ('SAT' if r.returncode == 10 else 'UNKNOWN')
    return st, round(time.monotonic() - t0, 1)

if __name__ == '__main__':
    secs = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    for tag, ws in (('cell', False), ('sets', True)):
        cnf = build(ws)
        st, wall = solve(cnf, f'set_{tag}.cnf', secs)
        print(json.dumps(dict(enc=tag, status=st, wall=wall, vars=cnf.nv, clauses=len(cnf.cl))), flush=True)
