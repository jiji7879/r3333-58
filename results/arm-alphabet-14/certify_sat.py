#!/usr/bin/env python3
"""certify_sat.py -- close the enumeration for the SAT candidates.

For a candidate whose instance is satisfiable, completeness of the model list is
established by the final UNSAT call once every model found so far is blocked.
That call needs its own certificate, which the main run did not keep.  This
script re-enumerates the models of each SAT candidate, rebuilds the blocked
instance, obtains a DRAT for it, and replays it with rupcheck.  It also re-checks
that the models are valid colourings and that the union of their canonical forms
is what the classification recorded.

Usage: python3 certify_sat.py n workdir
"""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arm import parse_g6, canon_form, verify as vcol
from satpipe import build_cnf, write_dimacs, run_kissat, parse_model, KISSAT

ROOT = os.path.dirname(os.path.abspath(__file__))


def enumerate_models(n, adj0, cap, d):
    edges, clauses = build_cnf(n, adj0, cap)
    nv = len(edges)
    cnf = os.path.join(d, 'c.cnf')
    out = os.path.join(d, 'c.out')
    drat = os.path.join(d, 'c.drat')
    extra = []
    models = []
    while True:
        write_dimacs(cnf, nv, clauses + extra)
        rc = run_kissat(cnf, out, drat if not models else None)
        if rc == 20:
            return edges, clauses, models, extra, (drat if not models else drat)
        if rc != 10:
            raise SystemExit('kissat rc=%d' % rc)
        model = parse_model(out, nv)
        m = [[0] * n for _ in range(n)]
        for i in range(n):
            m[i][i] = -1
        for i in range(n):
            for j in range(i + 1, n):
                if (adj0[i] >> j) & 1:
                    m[i][j] = m[j][i] = 0
        for k, e in enumerate(edges):
            c = 1 if model[k + 1] else 2
            m[e[0]][e[1]] = m[e[1]][e[0]] = c
        assert vcol(n, m) is None, 'invalid model'
        models.append(m)
        extra.append([-(k + 1) if model[k + 1] else (k + 1) for k in range(nv)])


def main(n, workdir='.', lo=0, hi=10**9):
    res = json.load(open(os.path.join(workdir, 'classes_sat%d.json' % n)))
    cands = [l.strip() for l in open(os.path.join(workdir, 'cand%d.g6' % n))
             if l.strip() and not l.startswith('>')]
    cap = res.get('cap')
    unsat_idx = {u[0] for u in res['unsat']}
    sat = [gi for gi in range(len(cands)) if gi not in unsat_idx]
    print('SAT candidates:', len(sat))
    d = os.path.join(ROOT, workdir, 'cert')
    os.makedirs(d, exist_ok=True)
    ok = 0
    fails = []
    known = {canon_form(n, m) for m in res['reps']}
    covered = set()
    sat = [gi for gi in sat if lo <= gi < hi]
    print('this slice:', len(sat), flush=True)
    for k, gi in enumerate(sat):
        nn, adj0 = parse_g6(cands[gi])
        edges, clauses, models, extra, drat = enumerate_models(n, adj0, cap, d)
        print('  cand %d: %d models' % (gi, len(models)), flush=True)
        # the final blocked instance must be UNSAT, with a proof
        cnf = os.path.join(d, 'final.cnf')
        write_dimacs(cnf, len(edges), clauses + extra)
        out = os.path.join(d, 'final.out')
        rc = run_kissat(cnf, out, drat)
        if rc != 20:
            fails.append(gi)
            continue
        p = subprocess.run([os.path.join(ROOT, 'rupcheck'), cnf, drat],
                           capture_output=True, text=True)
        if 's VERIFIED' not in p.stdout:
            fails.append(gi)
            continue
        ok += 1
        for m in models:
            covered.add(canon_form(n, m))
    print('blocked-completion certificates: %d/%d verified; fails=%s'
          % (ok, len(sat), fails[:5]))
    print('canonical forms from SAT candidates: %d, all among the recorded %d: %s'
          % (len(covered), len(known), covered <= known))


if __name__ == '__main__':
    lo = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    hi = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
    main(int(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else '.', lo, hi)
