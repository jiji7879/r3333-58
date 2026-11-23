import sys, subprocess, time, json
sys.path.insert(0, '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwrmwgf7/m1')
import ladder
K = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/kissat'
def build(bound):
    tpl = ladder.load_col(ladder.TPL_DEFAULT)
    cnf, cell, q, S, N = ladder.build(tpl, [14, 14, 14], xt=True)
    ext = {}
    for x in range(N):
        es = []
        for f in (1, 2, 3):
            e = cnf.new(); es.append(e)
            for a in range(15): cnf.add([-e, -cell[x, a, f]], 'edef')
            cnf.add([e] + [cell[x, a, f] for a in range(15)], 'edef')
        ex = cnf.new(); ext[x] = ex
        for e in es: cnf.add([-e, ex])
        cnf.add([-ex] + es)
    if bound is not None:
        for arm in range(3):
            cnf.at_most([ext[x] for x in range(14*arm, 14*arm+14)], bound, 'armext')
    return cnf
def solve(cnf, path, secs):
    with open(path, 'w') as fh:
        fh.write('p cnf %d %d\n' % (cnf.nv, len(cnf.cl)))
        for cl in cnf.cl: fh.write(' '.join(map(str, cl)) + ' 0\n')
    t0 = time.monotonic()
    r = subprocess.run([K, '-q', '--time=%d' % secs, path], capture_output=True, text=True)
    st = 'UNSAT' if r.returncode == 20 else ('SAT' if r.returncode == 10 else 'UNKNOWN')
    return st, round(time.monotonic() - t0, 1)
if __name__ == '__main__':
    secs = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    cnf = build(3)
    st, wall = solve(cnf, 'om3.cnf', secs)
    print(json.dumps(dict(bound='<=3 per arm', status=st, wall=wall, vars=cnf.nv, clauses=len(cnf.cl))), flush=True)
