import sys, subprocess, time, re, os, json
sys.argv = ['x']
exec(open('exp.py').read().split("def main()")[0])
K = KISSAT
def run2(cnf, path, conflicts, secs):
    cnf.to_file(path)
    drat = path.replace('.cnf', '.drat')
    t0 = time.monotonic()
    p = subprocess.run([K, '--conflicts=%d' % conflicts, '--time=%d' % secs, path, drat],
                       capture_output=True, text=True)
    wall = time.monotonic() - t0
    m = re.search(r'conflicts:\s+(\d+)', p.stdout + p.stderr)
    st = 'UNSAT' if p.returncode == 20 else ('SAT' if p.returncode == 10 else 'UNKNOWN')
    return st, wall, int(m.group(1)) if m else -1, (os.path.getsize(drat) if st == 'UNSAT' and os.path.exists(drat) else 0)
out = []
for idx in (0, 1):
    for tag, dc in (('base', False), ('dc', True)):
        f, cnf = build(['16','14','14','13'], idx, dc)
        st, wall, conf, size = run2(cnf, f'hard_{tag}_{idx}.cnf', 3000000, 60)
        row = dict(case=idx, arm=tag, status=st, wall=round(wall,1), conflicts=conf, drat=size, vars=cnf.nv, clauses=len(cnf.clauses))
        print(json.dumps(row), flush=True); out.append(row)
json.dump(out, open('hard.json','w'), indent=1)
