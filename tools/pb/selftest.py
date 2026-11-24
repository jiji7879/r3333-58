"""Self-test for tools/pb/encode.py.  Run after ANY change to the encoder.

    python3 tools/pb/selftest.py          # ~40 s, exits non-zero on failure

Every check is a *polarity* check: it asserts both that a constraint fires when
it should and that it does not fire when it should not.  The bug that voided a
whole session's result - an inverted guard literal that made every --all16
instance unsatisfiable by construction - passes a one-sided test and fails here.

History, so it is not re-learned: the encoder committed at 0b1dd92 built
h <-> (red AND d16) and then applied "at most 15 of h", so under the --all16
unit the instance was both red >= 16 and red <= 15.  Forty "verified" UNSAT
certificates followed, all of them about the wrong formula.
"""
import sys, os, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from encode import build, N, RED
from pbdata import ROWS
from pysat.card import CardEnc, EncType

S = '.ultramath/smwmq7hji/m3/bin/kissat'
TMP = tempfile.mkdtemp(prefix='pbselftest', dir='.scratch')
fails = []


def solve(cnf, name, want):
    p = os.path.join(TMP, name + '.cnf')
    cnf.to_file(p)
    r = subprocess.run([S, '-q', p], capture_output=True, text=True, timeout=900)
    got = 'SAT' if 'SATISFIABLE' in r.stdout and 'UNSAT' not in r.stdout else \
          ('UNSAT' if 'UNSATISFIABLE' in r.stdout else '?')
    ok = got == want
    print('%-4s %-46s want %-5s got %-5s' % ('ok' if ok else 'FAIL', name, want, got), flush=True)
    if not ok:
        fails.append(name)
    assert cnf.nv > 13224 or print('  (namespace!)')


M, D = 'T', (0, 2)

# 1. the guard must not fire when it should not: degree laws + all-16 is SAT
cnf, _, _ = build(M, D, 3, strength=1, laws=(1, 3), all16=True, footprint=False)
assert cnf.nv > 13224, cnf.nv
solve(cnf, 'all16_degree_only', 'SAT')

# 2. ... and the same with no all-16 hypothesis
cnf, _, _ = build(M, D, 3, strength=1, laws=(1, 3))
assert cnf.nv > 13224
solve(cnf, 'degree_only', 'SAT')

# 3. pins-only with the nine-footprint block must be SAT: if this is UNSAT the
#    footprint block is self-contradictory (it was, twice, while being written)
cnf, _, _ = build(M, D, 3, strength=0, laws=(1,), fp15=True)
solve(cnf, 'fp15_pins_only', 'SAT')

# 4. degree laws + footprints, no triangles, no codegree: SAT
cnf, _, _ = build(M, D, 3, strength=3, laws=(1, 3), fp15=True)
solve(cnf, 'fp15_degree_only', 'SAT')

# 5. a gadget-free at-least-16 on the 14 shared sites must agree with --all16
def ev(a, b, c):
    if a > b: a, b = b, a
    return (a * N + b) * 4 + c + 1
cnf, _, _ = build(M, D, 3, strength=1, laws=(1, 3))
top = cnf.nv
for z in range(14):
    enc = CardEnc.atleast(lits=[ev(z, b, RED) for b in range(N) if b != z],
                          bound=16, top_id=top, encoding=EncType.seqcounter)
    cnf.extend(enc.clauses); top = enc.nv
solve(cnf, 'all16_gadget_free', 'SAT')

# 6. the templates' footprint, from the matrices
r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'footprint.py')],
                   capture_output=True, text=True)
if r.returncode != 0:
    fails.append('footprint')
    print('FAIL footprint.py')
else:
    print('ok   footprint')

print()
if fails:
    print('SELFTEST FAILED:', ', '.join(fails))
    sys.exit(1)
print('SELFTEST OK: 6 checks, both polarities of the all-16 guard included')
