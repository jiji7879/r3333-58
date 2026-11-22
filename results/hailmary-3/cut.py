#!/usr/bin/env python3
"""The 116-cell pattern as a sound cut on the 42-slot branch instance.

Pattern (external package, verified): ten partial rows; no uniform-branch object
places all ten injectively in arm B. Cut: for every subset T of the ten rows,
at least |T| arm-B slots match some row of T. Any subset of Hall's conditions is
sound; the pruning comes from the larger ones.
"""
import sys, json, itertools, subprocess, time
sys.path.insert(0, '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwrmwgf7/m1')
import ladder
K = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/kissat'
HM = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/hmproof/Hail_Mary_Proof'

def load_pattern():
    words = {}
    for line in open(f'{HM}/source.wit'):
        t = line.split()
        if t and t[0] == 'word':
            words[int(t[1])] = list(map(int, t[2:]))
    p = json.load(open(f'{HM}/pattern7.json'))
    rows = [(rid, cols) for rid, cols in p['rows']]
    return [(cols, [words[rid][a] for a in cols]) for rid, cols in rows]

def add_cut(cnf, cell, rows, arm_slots=range(0, 14)):
    """SOUND direction: the theorem says no injective placement exists, so in any
    valid object SOME Hall condition fails:  OR_T  |N(T)| < |T|.
    (Asserting all of them would assert a matching exists -- the negation.)"""
    nr = len(rows)
    m = {}
    for i, (cols, vals) in enumerate(rows):
        for s in arm_slots:
            v = cnf.new()
            m[i, s] = v
            cnf.add([-cell[s, a, val] for a, val in zip(cols, vals)] + [v], 'patdef')
            for a, val in zip(cols, vals):
                cnf.add([-v, cell[s, a, val]], 'patdef')
    subsets = [T for k in range(1, nr + 1) for T in itertools.combinations(range(nr), k)]
    fails = []
    for T in subsets:
        ns = []
        for s in arm_slots:
            n = cnf.new()
            ns.append(n)
            for i in T:
                cnf.add([-m[i, s], n], 'or')
            cnf.add([-n] + [m[i, s] for i in T], 'or')
        h = cnf.new()
        fails.append(h)
        cnf.at_most(ns + [-h], len(T) - 1, 'hall')     # h -> |N(T)| <= |T|-1
    cnf.add(fails, 'hallfails')                       # some subset fails
    return cnf, len(subsets)


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
    rows = load_pattern()
    print('pattern rows', len(rows), 'cells', sum(len(c) for c, _ in rows), flush=True)
    for tag, use_cut in (('base', False), ('cut', True)):
        tpl = ladder.load_col(ladder.TPL_DEFAULT)
        cnf, cell, q, S, N = ladder.build(tpl, [14, 14, 14], xt=True)
        n_sub = 0
        if use_cut:
            cnf, n_sub = add_cut(cnf, cell, rows)
        st, wall = solve(cnf, f'cut_{tag}.cnf', secs)
        print(json.dumps(dict(tag=tag, status=st, wall=wall, vars=cnf.nv,
                              clauses=len(cnf.cl), hall_subsets=n_sub)), flush=True)
