"""Self-tests: the counters and exact guards behave as their names claim.

We test by fixing every input literal and asking a solver whether the guard
subsystem is satisfiable, for random input subsets and every relevant size.
"""
import random
import subprocess
import sys
import tempfile
import os
from gadgets import atmost, atleast, exact_guard

CADICAL = '/opt/lean/bin/cadical'


def solve(nv, clauses):
    """SAT check via cadical.  Returns True/False."""
    with tempfile.NamedTemporaryFile('w', suffix='.cnf', delete=False) as f:
        f.write('p cnf %d %d\n' % (nv, len(clauses)))
        for c in clauses:
            f.write(' '.join(str(x) for x in c) + ' 0\n')
        name = f.name
    try:
        r = subprocess.run([CADICAL, '-q', name], capture_output=True, text=True)
        out = r.stdout
        if r.returncode == 10 or 's SATISFIABLE' in out:
            return True
        if r.returncode == 20 or 's UNSATISFIABLE' in out:
            return False
        raise SystemExit('cadical failed rc=%d out=%r' % (r.returncode, out[-300:]))
    finally:
        os.unlink(name)


def check_bound(name, encoder, n=9):
    """encoder(lits, k, top) must encode the exactly-stated sum constraint."""
    for trial in range(60):
        k = random.randrange(0, n + 1)
        S = random.sample(range(1, n + 1), random.randrange(0, n + 1))
        clauses, top = encoder(list(range(1, n + 1)), k, n)
        fixed = [[v] if v in S else [-v] for v in range(1, n + 1)]
        got = solve(top, clauses + fixed)
        if name == 'atmost':
            want = len(S) <= k
        elif name == 'atleast':
            want = len(S) >= k
        else:
            raise AssertionError(name)
        assert got == want, (name, n, k, sorted(S), got, want)
    print('  %-8s ok (%d random cases)' % (name, 60))


def check_exact_guard(n=9):
    for trial in range(60):
        needed = random.randrange(1, n + 1)
        S = random.sample(range(1, n + 1), random.randrange(0, n + 1))
        g = n + 1
        clauses, top = exact_guard(list(range(1, n + 1)), needed, g, g)
        fixed = [[v] if v in S else [-v] for v in range(1, n + 1)]
        want = len(S) >= needed
        for gval in (True, False):
            got = solve(top, clauses + fixed + ([[g]] if gval else [[-g]]))
            assert got == (want == gval), (needed, sorted(S), gval, got, want)
    print('  exact_guard ok (60 random cases, both polarities)')


if __name__ == '__main__':
    random.seed(20261125)
    print('selftest gadgets')
    check_bound('atmost', atmost)
    check_bound('atleast', atleast)
    check_exact_guard()
    print('ALL OK')
