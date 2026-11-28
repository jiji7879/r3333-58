"""Corrected negative controls for the independent RUP checker.

Unlike the first draft, the final empty clause is *checked* here, not merely
noticed.  A refutation attempt is reported VERIFIED only if every addition,
the empty clause included, is RUP.
"""
import gzip
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PKG = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(PKG / 'next'))
import block
import sharp
from rup_check import Propagator, parse_binary_drat

raw = gzip.decompress((PKG / 'next' / 'matching.drat.gz').read_bytes())
recs = parse_binary_drat(raw)
adds = [l for k, l in recs if k == 'a']


def run(formula, trace, label, show_first=False):
    prop = Propagator(formula.clauses, formula.nv)
    bad = []
    for i, cl in enumerate(trace, 1):
        if not prop.rup(cl):
            bad.append((i, cl[:6]))
            break
        if cl:
            prop.add(cl)
    if bad:
        where = f'first failure at addition #{bad[0][0]} {bad[0][1]}'
    else:
        where = ('all %d additions RUP including the empty clause -- REFUTED'
                 % len(trace))
    print(f'{label}: {where}')
    return not bad


print('== micro sanity checks of the propagation engine ==')
p = Propagator([[1, 2], [-1, 2], [1, -2]], 2)
print('  [[1,2],[-1,2],[1,-2]]  rup([-1]) =', p.rup([-1]), '(expect False)')
print('  [[1,2],[-1,2],[1,-2]]  rup([1])  =', p.rup([1]), '(expect True)')
assert p.rup([1]) and not p.rup([-1])
q = Propagator([[1], [-1, 2], [-2, 3], [-3]], 3)
print('  chain units ending in contradiction: rup([]) =', q.rup([]), '(expect True)')
print('  satisfiable [1,2] alone: rup([-3]) =', Propagator([[1, 2]], 3).rup([-3]), '(expect False)')

print('== formula-level controls ==')
print('  matching template, rup([]) with no additions:',
      Propagator(block.formula(True).clauses, 315).rup([]), '(expect False)')
print('  path template,     rup([]) with no additions:',
      Propagator(block.formula(False).clauses, 315).rup([]), '(expect False)')
print('  K14 sharpness,     rup([]) with no additions:',
      Propagator(sharp.small().clauses, sharp.small().nv).rup([]), '(expect False)')
print('  matching template, rup([fresh unused var 400+1=401]):',
      Propagator(block.formula(True).clauses, 401).rup([401]), '(expect False)')

print('== full trace against each formula, empty clause checked ==')
pos = run(block.formula(True), adds, 'matching template')
neg1 = run(block.formula(False), adds, 'path template  ')
neg2 = run(sharp.small(), adds, 'K14 sharpness  ')
ok = pos and not neg1 and not neg2
print('RESULT', 'positive verified and both negatives rejected' if ok else 'CONTROL PROBLEM')
sys.exit(0 if ok else 1)
