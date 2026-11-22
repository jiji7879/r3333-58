#!/usr/bin/env python3
"""Baseline vs +degree-cap on the cover's per-case CNFs.

For each selected case: host(58) + units(family, placement), optionally plus
  (DC) for every vertex v and colour c: at most 16 of v's 57 edges have colour c
which is R(3,3,3)=17 and therefore implied by triangle-freeness -- so it can only
help or hurt propagation, never soundness.
"""
import sys, os, json, gzip, subprocess, time
sys.path.insert(0, '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwp3xc7p/m3/w/k58-solver/k58')
from joint_plan import cases
from gluing import host, units
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType

KISSAT = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/kissat'
ORDER = 58

def build(profile, idx, degcap):
    it = cases(tuple(int(x) for x in profile))
    for k, (f, pl, i, ch) in enumerate(it):
        if k == idx:
            break
    else:
        raise SystemExit('index out of range')
    _, base = host(ORDER)
    cnf = CNF(from_clauses=base + sorted(units(f, pl)))
    if degcap:
        vp = IDPool(start_from=cnf.nv + 1)
        # edge (u,v) colour c  ==  lit(u,v,c); rebuild the map
        from itertools import combinations
        lit = {}
        for e_i, (u, v) in enumerate(combinations(range(ORDER), 2)):
            for c in range(4):
                lit[(u, v, c)] = 4 * e_i + 1 + c
        for v in range(ORDER):
            for c in range(4):
                lits = [lit[(min(v, u), max(v, u), c)] for u in range(ORDER) if u != v]
                card = CardEnc.atmost(lits=lits, bound=16, vpool=vp, encoding=EncType.seqcounter)
                cnf.extend(card.clauses)
    return f, cnf

def run(cnf, path, conflicts, secs):
    cnf.to_file(path)
    drat = path.replace('.cnf', '.drat')
    if os.path.exists(drat):
        os.unlink(drat)
    t0 = time.monotonic()
    p = subprocess.run([KISSAT, '-q', '--conflicts=%d' % conflicts, '--time=%d' % secs, path, drat],
                       capture_output=True, text=True)
    wall = time.monotonic() - t0
    status = 'UNSAT' if p.returncode == 20 else ('SAT' if p.returncode == 10 else 'UNKNOWN')
    size = os.path.getsize(drat) if status == 'UNSAT' and os.path.exists(drat) else 0
    return status, wall, size, cnf.nv, len(cnf.clauses)

def main():
    profile = sys.argv[1].split(',')
    ids = [int(x) for x in sys.argv[2].split(',')]
    conflicts = int(sys.argv[3]); secs = int(sys.argv[4])
    out = []
    for idx in ids:
        for tag, degcap in (('base', False), ('dc', True)):
            f, cnf = build(profile, idx, degcap)
            st, wall, size, nv, nc = run(cnf, f'{tag}_{idx}.cnf', conflicts, secs)
            row = dict(case=idx, arm=tag, status=st, wall=round(wall, 1), drat=size, vars=nv, clauses=nc)
            print(json.dumps(row), flush=True)
            out.append(row)
    json.dump(out, open('results.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
