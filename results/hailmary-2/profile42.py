import sys, subprocess, time, random, json
sys.path.insert(0, '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwrmwgf7/m1')
import ladder
K = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/kissat'

def words_of(path, arm=1):
    W = []
    for line in open(path):
        t = line.split()
        if t and t[0] == 'word':
            W.append(tuple(int(v) for v in t[2:]))
    return W[14*(arm-1):14*arm]

def build_with_profile(profile, pin_words=None, arm_size=14):
    tpl = ladder.load_col(ladder.TPL_DEFAULT)
    cnf, cell, q, S, N = ladder.build(tpl, [14, 14, 14], xt=True)
    # arm 1 = slots 0..13; for each position a require exactly profile[a] of them cover a
    for a in range(15):
        col = [cell[x, a, 0] for x in range(arm_size)]
        need = profile[a]
        cnf.at_least(col, need, 'prof')
        cnf.at_most(col, need, 'prof')
    if pin_words:
        for x in range(len(pin_words)):
            for a in range(15):
                cnf.add([cell[x, a, pin_words[x][a]]], 'pin')
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
    W = words_of('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwrfgma5/m4/wit/a_14_14.wit')
    prof_w = [sum(1 for w in W if w[a] == 0) for a in range(15)]
    print('witness arm profile', prof_w, 'sum', sum(prof_w), flush=True)
    secs = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    random.seed(3)
    fives = list(range(15))
    tests = [('witness', prof_w)]
    for k in range(2):
        random.shuffle(fives)
        p = [5 if a in fives[:10] else 4 for a in range(15)]
        tests.append((f'rand{k}', p))
    for tag, p in tests:
        cnf = build_with_profile(p)
        st, wall = solve(cnf, f'prof_{tag}.cnf', secs)
        print(json.dumps(dict(tag=tag, profile=p, vars=cnf.nv, clauses=len(cnf.cl), status=st, wall=wall)), flush=True)
