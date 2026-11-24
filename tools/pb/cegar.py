"""Decide a pb child with the codegree law (L4) added lazily.

The full CNF carries 1,653 codegree cardinality constraints, which are most of
its clauses and nearly all its auxiliary variables.  Instead: solve the child
with (L1)-(L3) only, read the red neighbourhoods out of the model, and add a
blocking clause for each pair that actually has 15 or more common red
neighbours.  A model that survives the check is a host (checked again from the
definition by check_matrix); if the loop runs out the instance is UNSAT only in
the limit, so this script never reports UNSAT - it reports SAT or UNDECIDED.

    python3 tools/pb/cegar.py ROW T MAXITER [SECONDS]
"""
import sys, os, time, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from encode import build, N, BLUE, GREEN, YELLOW, RED


def ev(a, b, c):
    if a > b: a, b = b, a
    return (a * N + b) * 4 + c + 1
from pysat.solvers import Cadical195


def matrix_of(model):
    val = {abs(l): l > 0 for l in model}
    rows = [['.'] * N for _ in range(N)]
    for a, b in itertools.combinations(range(N), 2):
        col = [c for c in (BLUE, GREEN, YELLOW, RED) if val.get(ev(a, b, c), False)]
        assert len(col) == 1, (a, b, col)
        rows[a][b] = rows[b][a] = str(col[0])
    return [''.join(r) for r in rows]


def red_neigh(rows):
    return [set(b for b in range(N) if b != a and rows[a][b] == str(RED)) for a in range(N)]


def main():
    row, t = sys.argv[1], int(sys.argv[2])
    maxiter = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    budget = float(sys.argv[4]) if len(sys.argv) > 4 else 1200.0
    from pbdata import ROWS
    M, D = [(m, d) for (nm, m, d) in ROWS if nm == row][0]
    cnf, _, _ = build(M, D, t, stats=True, strength=3, fp15=True, laws=(1, 2, 3))
    print('base clauses', len(cnf.clauses), 'vars', cnf.nv, flush=True)
    s = Cadical195(bootstrap_with=cnf.clauses, use_timer=True)
    t0 = time.time()
    for it in range(maxiter):
        if time.time() - t0 > budget:
            print('BUDGET: undecided after %d iterations' % it); return 2
        if not s.solve():
            print('UNSAT at iteration %d  <-- but (L4) is lazy, so this is NOT a verdict' % it)
            return 3
        rows = matrix_of(s.get_model())
        nr = red_neigh(rows)
        bad = [(a, b) for a, b in itertools.combinations(range(N), 2)
               if len(nr[a] & nr[b]) > 14]
        print('iter %d: %.1fs  max codeg %d  violations %d'
              % (it, time.time() - t0,
                 max(len(nr[a] & nr[b]) for a, b in itertools.combinations(range(N), 2)),
                 len(bad)), flush=True)
        if not bad:
            open('tools/pb/cegar_model_%s_t%d.txt' % (row, t), 'w').write('\n'.join(rows) + '\n')
            print('SAT: model written; check it with check_matrix.py')
            return 0
        for a, b in bad[:400]:
            W = sorted(nr[a] & nr[b])
            s.add_clause([-ev(a, w, RED) for w in W] + [-ev(b, w, RED) for w in W])
    print('MAXITER: undecided')
    return 2


if __name__ == '__main__':
    sys.exit(main())
