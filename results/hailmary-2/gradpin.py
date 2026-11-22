import sys, subprocess, time
sys.path.insert(0, '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwrmwgf7/m1')
import ladder
K = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/kissat'
W = []
for line in open('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwrfgma5/m4/wit/a_14_14.wit'):
    t = line.split()
    if t and t[0] == 'word':
        W.append(tuple(int(v) for v in t[2:]))
W = W[:14]
tpl = ladder.load_col(ladder.TPL_DEFAULT)
for k in (1, 2, 4, 8, 14):
    cnf, cell, q, S, N = ladder.build(tpl, [14, 14, 14], xt=True)
    for x in range(k):
        for a in range(15):
            cnf.add([cell[x, a, W[x][a]]], 'pin')
    path = f'gp_{k}.cnf'
    with open(path, 'w') as fh:
        fh.write('p cnf %d %d\n' % (cnf.nv, len(cnf.cl)))
        for cl in cnf.cl:
            fh.write(' '.join(map(str, cl)) + ' 0\n')
    t0 = time.monotonic()
    r = subprocess.run([K, '-q', '--time=60', path, f'gp_{k}.drat'], capture_output=True, text=True)
    st = 'UNSAT' if r.returncode == 20 else ('SAT' if r.returncode == 10 else 'UNKNOWN')
    print(f'pinned {k:2d} words -> {st} in {time.monotonic()-t0:.1f}s', flush=True)
