#!/usr/bin/env python3
"""verify.py -- regenerate every UNSAT instance from its colour-0 graph and
replay its DRAT proof with rupcheck (RUP steps); a random sample is additionally
replayed with drat-trim.  Re-checks every witness colouring.

Usage: python3 verify.py n workdir [lo hi] [--sample K]
"""
import sys, os, json, subprocess, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arm import parse_g6, verify as vcol
from satpipe import build_cnf, write_dimacs, DRATTRIM

ROOT = os.path.dirname(os.path.abspath(__file__))
RUP = os.path.join(ROOT, 'rupcheck')


def regen(n, adj0, cap, path):
    edges, clauses = build_cnf(n, adj0, cap)
    write_dimacs(path, len(edges), clauses)
    return len(clauses)


def main(n, workdir='.', lo=0, hi=None, sample=200):
    res = json.load(open(os.path.join(workdir, 'classes_sat%d.json' % n)))
    cands = [l.strip() for l in open(os.path.join(workdir, 'cand%d.g6' % n))
             if l.strip() and not l.startswith('>')]
    uns = [u for u in res['unsat'] if lo <= u[0] < (hi if hi is not None else 10 ** 9)]
    d = os.path.join(ROOT, workdir, 'verify')
    os.makedirs(d, exist_ok=True)
    cnf = os.path.join(d, 'cur.cnf')
    ok = 0
    fails = []
    for gi, line in uns:
        nn, adj0 = parse_g6(line)
        assert nn == n and cands[gi] == line
        regen(n, adj0, res.get('cap'), cnf)
        drat = os.path.join(ROOT, workdir, 'inst', 'g%d.drat' % gi)
        p = subprocess.run([RUP, cnf, drat], capture_output=True, text=True)
        if 's VERIFIED' in p.stdout:
            ok += 1
        else:
            fails.append(gi)
    print('rupcheck: %d/%d UNSAT replayed (regenerated CNFs); fails=%s'
          % (ok, len(uns), fails[:5]))
    if sample:
        random.seed(12345)
        pick = random.sample(uns, min(sample, len(uns)))
        ok2 = 0
        for gi, line in pick:
            nn, adj0 = parse_g6(line)
            regen(n, adj0, res.get('cap'), cnf)
            drat = os.path.join(ROOT, workdir, 'inst', 'g%d.drat' % gi)
            p = subprocess.run([DRATTRIM, cnf, drat], capture_output=True, text=True)
            if 's VERIFIED' in p.stdout + p.stderr:
                ok2 += 1
        print('drat-trim cross-check on %d random instances: %d verified'
              % (len(pick), ok2))
    bad = [(i, e) for i, m in enumerate(res['reps']) for e in [vcol(n, m)] if e]
    print('witnesses: %d classes, all valid: %s' % (len(res['reps']), not bad))
    return ok, len(uns), fails


if __name__ == '__main__':
    a = sys.argv[1:]
    n = int(a[0]); wd = a[1] if len(a) > 1 else '.'
    lo, hi, sample = 0, None, 200
    rest = [x for x in a[2:] if not x.startswith('--')]
    if len(rest) >= 2:
        lo, hi = int(rest[0]), int(rest[1])
    if '--sample' in a:
        sample = int(a[a.index('--sample') + 1])
    main(n, wd, lo, hi, sample)
