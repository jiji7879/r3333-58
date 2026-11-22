import sys, subprocess, time, os
sys.path.insert(0, '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwrmwgf7/m1')
import ladder
K = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/kissat'

def witness_words(path, arm=1):
    word = {}
    for line in open(path):
        t = line.split()
        if not t or t[0].startswith('#'):
            continue
        if t[0] == 'word':
            word[int(t[1])] = tuple(int(v) for v in t[2:])
    lo = 14 * (arm - 1)
    return [word[x] for x in range(lo, lo + 14)]

W = witness_words('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwrfgma5/m4/wit/a_14_14.wit')
print('pinned words (arm 1 of a_14_14_lean.wit arm 1):', len(W), flush=True)

for tag, pin in (('base', False), ('pinned', True)):
    cnf, cell, q, S, N = ladder.build(ladder.load_col(ladder.TPL_DEFAULT),
                                      [14, 14, 14], xt=True)
    if pin:
        for x in range(14):
            for a in range(15):
                v = cell[x, a, W[x][a]]
                cnf.add([v], 'pin')
    path = f'pin42_{tag}.cnf'
    with open(path, 'w') as fh:
        fh.write('p cnf %d %d\n' % (cnf.nv, len(cnf.cl)))
        for cl in cnf.cl:
            fh.write(' '.join(map(str, cl)) + ' 0\n')
    t0 = time.monotonic()
    r = subprocess.run([K, '-q', '--time=120', path, f'pin42_{tag}.drat'], capture_output=True, text=True)
    st = 'UNSAT' if r.returncode == 20 else ('SAT' if r.returncode == 10 else 'UNKNOWN')
    print(f'{tag:7s} vars={cnf.nv} clauses={len(cnf.cl)} -> {st} in {time.monotonic()-t0:.1f}s', flush=True)
