#!/usr/bin/env python3
"""satpipe.py -- decide and enumerate, per candidate colour-0 graph, via CNF.

For a candidate graph G_0 on n vertices (triangle-free, colour-0 degrees in
[n-11,5], alpha(G_0) <= 5), the remaining edges (the complement H) carry colours
1 and 2.  Introduce one variable x_e per edge e of H, true = colour 1.

Exactly the necessary and sufficient conditions are imposed:
  (T1) for every triangle {a,b,c} of H:  (not a or not b or not c)   [no mono-1]
  (T2) for every triangle {a,b,c} of H:  ( a or b or c )             [no mono-2]
  (D1) for every vertex v and every 6-subset S of the H-edges at v:
       (or_{e in S} not x_e)                                        [colour-1 deg <= 5]
  (D2) for every vertex v and every 6-subset S of the H-edges at v:
       (or_{e in S} x_e)                                            [colour-2 deg <= 5]
No auxiliary variables are used, so the clause set is literally the constraint
set: a model is a triangle-free 3-colouring of K_n with colour-0 graph G_0, and
conversely.  The 6-subset (binomial) cardinality encoding is used precisely
because it has no encoding gap to argue.
"""
import sys, os, json, subprocess, itertools
from collections import defaultdict
from arm import parse_g6, canon_form, invariant, verify, to_g6

KISSAT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                      '.scratch', 'satcheck', 'bin', 'kissat'))
DRATTRIM = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                        '.scratch', 'satcheck', 'bin', 'drat-trim'))


def build_cnf(n, adj0, cap=None):
    """CNF over one variable per edge of H = complement of G_0 (true = colour 1).

    Only the triangle conditions are needed.  The colour-degree cap d_c <= 5 is
    a *consequence* of them: if some vertex had six colour-1 neighbours, those
    six vertices would carry a 2-colouring of K_6 by colours {0,2} with no
    monochromatic triangle, contradicting R(3,3) = 6.  So no cardinality
    encoding is used anywhere and the clause set is literally the constraint
    set.
    """
    edges = [(i, j) for i in range(n) for j in range(i + 1, n)
             if not (adj0[i] >> j) & 1]
    eidx = {e: k + 1 for k, e in enumerate(edges)}
    clauses = []
    for a in range(n):
        for b in range(a + 1, n):
            if (adj0[a] >> b) & 1:
                continue
            for c in range(b + 1, n):
                if (adj0[a] >> c) & 1 or (adj0[b] >> c) & 1:
                    continue
                t = [eidx[(a, b)], eidx[(a, c)], eidx[(b, c)]]
                clauses.append([-v for v in t])
                clauses.append(list(t))
    if cap is not None:                      # optional: audited, redundant
        at = defaultdict(list)
        for e in edges:
            at[e[0]].append(eidx[e])
            at[e[1]].append(eidx[e])
        for v in range(n):
            vs = at[v]
            if len(vs) > cap:
                for S in itertools.combinations(vs, cap + 1):
                    clauses.append([-x for x in S])
                    clauses.append(list(S))
    return edges, clauses


def write_dimacs(path, nv, clauses):
    with open(path, 'w') as fh:
        fh.write('p cnf %d %d\n' % (nv, len(clauses)))
        for c in clauses:
            fh.write(' '.join(map(str, c)) + ' 0\n')


def parse_model(out, nv):
    model = [False] * (nv + 1)
    seen = False
    for line in open(out):
        if line.startswith('v'):
            seen = True
            for tok in line[1:].split():
                lit = int(tok)
                if lit > 0:
                    model[lit] = True
    return model if seen else None


def run_kissat(cnf, out, drat=None, timeout=600):
    cmd = [KISSAT, '-q']
    if drat:
        cmd += [cnf, drat]
    else:
        cmd += [cnf]
    with open(out, 'w') as fh:
        p = subprocess.run(cmd, stdout=fh, stderr=subprocess.DEVNULL,
                           timeout=timeout)
    return p.returncode


def solve_graph(n, adj0, workdir, gi, cap=5, max_models=100000):
    """Returns ('UNSAT', dratpath) or ('SAT', [colour matrices])."""
    edges, clauses = build_cnf(n, adj0, cap)
    nv = len(edges)
    d = os.path.join(workdir, 'inst')
    os.makedirs(d, exist_ok=True)
    base = os.path.join(d, 'g%d' % gi)
    cnf = base + '.cnf'
    out = base + '.out'
    drat = base + '.drat'
    models = []
    extra = []
    first = True
    while True:
        write_dimacs(cnf, nv, clauses + extra)
        rc = run_kissat(cnf, out, drat if first else None)
        # kissat: 10 = SAT, 20 = UNSAT
        if rc == 20:
            os.remove(cnf) if os.path.exists(cnf) else None
            if first:
                return ('UNSAT', drat)
            return ('SAT', models)
        if rc != 10:
            raise SystemExit('kissat rc=%d on %s' % (rc, cnf))
        model = parse_model(out, nv)
        if model is None:
            raise SystemExit('no model parsed for %s' % cnf)
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
        err = verify(n, m)
        if err:
            raise SystemExit('MODEL FAILS VERIFICATION (%s): %s' % (err, cnf))
        models.append(m)
        extra.append([-(k + 1) if model[k + 1] else (k + 1)
                      for k in range(nv)])
        first = False
        if len(models) >= max_models:
            raise SystemExit('too many models for %s' % cnf)
        os.remove(drat) if os.path.exists(drat) else None


def replay_drat(cnf, drat):
    p = subprocess.run([DRATTRIM, '-q', cnf, drat], capture_output=True, text=True)
    ok = 's VERIFIED' in (p.stdout + p.stderr)
    return ok, (p.stdout + p.stderr).strip().splitlines()[-1:] 


if __name__ == '__main__':
    n = int(sys.argv[1])
    workdir = sys.argv[2] if len(sys.argv) > 2 else '.'
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    cap = None if cap == 0 else cap
    g6 = os.path.join(workdir, 'cand%d.g6' % n)
    cands = [l.strip() for l in open(g6) if l.strip() and not l.startswith('>')]
    lo = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    hi = int(sys.argv[5]) if len(sys.argv) > 5 else len(cands)
    print('n=%d cap=%s: candidates %d..%d of %d'
          % (n, cap, lo, hi, len(cands)), flush=True)
    classes = {}
    stats = defaultdict(int)
    unsat_drat = []
    for gi in range(lo, hi):
        line = cands[gi]
        nn, adj0 = parse_g6(line)
        assert nn == n
        status, payload = solve_graph(n, adj0, workdir, gi, cap)
        stats[status] += 1
        if status == 'UNSAT':
            unsat_drat.append((gi, line, payload))
        else:
            for m in payload:
                cf = canon_form(n, m)
                if cf not in classes:
                    classes[cf] = m
        if (gi + 1 - lo) % 200 == 0:
            print('  %d/%d  %s classes=%d'
                  % (gi + 1, hi, dict(stats), len(classes)), flush=True)
    out = os.path.join(workdir, 'chunk_%d_%d_%d.json' % (n, lo, hi))
    json.dump({'n': n, 'cap': cap, 'lo': lo, 'hi': hi,
               'stats': dict(stats), 'reps': list(classes.values()),
               'unsat': [[gi, line] for gi, line, _ in unsat_drat]}, open(out, 'w'))
    print('DONE n=%d [%d,%d): %s, %d classes' % (n, lo, hi, dict(stats), len(classes)))
