"""Both-polarity self-test for tools/pb/balance.py.

The campaign lost a session to a cardinality gadget that was tested in one
polarity only, so every gadget here is tested in both: it must forbid what it
should forbid and permit what it should permit.
"""
import sys
sys.path.insert(0, '.scratch/k58')
from gluing import host
from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Cadical195

sys.path.insert(0, 'tools/pb')
from balance import edge_lit, ORDER

fails = []


def solve(clauses, nv):
    c = CNF(); c.nv = nv; c.clauses = clauses
    with Cadical195(bootstrap_with=c.clauses) as s:
        return s.solve()


def cardinality_case(ntrue_forced, bound, want, name):
    """`bound` literals true and all the other 57-bound false: "at least bound of 57"
    must then be SAT exactly when ntrue_forced >= bound."""
    lits = list(range(1, 58))
    enc = CardEnc.atleast(lits=lits, bound=bound, top_id=57, encoding=EncType.seqcounter)
    clauses = [list(x) for x in enc.clauses]
    clauses += [[l] for l in lits[:ntrue_forced]]
    clauses += [[-l] for l in lits[ntrue_forced:]]
    got = solve(clauses, enc.nv)
    ok = (got == want)
    print('%-4s %-34s want %-5s got %-5s' % ('ok' if ok else 'FAIL', name, want, got))
    if not ok:
        fails.append(name)


# "at least 14 of 57" with the other literals false: UNSAT at 13 true, SAT at 14
cardinality_case(13, 14, False, 'atleast14, exactly 13 true: UNSAT')
cardinality_case(14, 14, True, 'atleast14, exactly 14 true: SAT')
cardinality_case(15, 14, True, 'atleast14, exactly 15 true: SAT')

# the same gadget at another bound, to catch a mis-threaded bound
cardinality_case(13, 15, False, 'atleast15, exactly 13 true: UNSAT')
cardinality_case(15, 15, True, 'atleast15, exactly 15 true: SAT')

# a wrong-polarity control: "at most 13 of 57" must be UNSAT with 14 true
def atmost_case(ntrue, bound, want, name):
    lits = list(range(1, 58))
    enc = CardEnc.atmost(lits=lits, bound=bound, top_id=57, encoding=EncType.seqcounter)
    clauses = [list(x) for x in enc.clauses]
    clauses += [[l] for l in lits[:ntrue]]
    clauses += [[-l] for l in lits[ntrue:]]
    got = solve(clauses, enc.nv)
    ok = (got == want)
    print('%-4s %-34s want %-5s got %-5s' % ('ok' if ok else 'FAIL', name, want, got))
    if not ok:
        fails.append(name)
atmost_case(14, 13, False, 'atmost13, exactly 14 true: UNSAT')
atmost_case(13, 13, True, 'atmost13, exactly 13 true: SAT')

# the edge literal map must agree with the frozen encoder's own map
_, _ = host(ORDER)
def frozen_lit(u, v, c, order=ORDER):
    from itertools import combinations
    edges = {e: 4 * i + 1 for i, e in enumerate(combinations(range(order), 2))}
    return edges[min(u, v), max(u, v)] + c
bad = [(u, v, c) for u in range(57) for v in range(u + 1, 58) for c in range(4)
       if edge_lit(u, v, c) != frozen_lit(u, v, c)]
print('%-4s %-34s %s' % ('ok' if not bad else 'FAIL', 'edge_lit matches gluing.host', len(bad)))
if bad:
    fails.append('edge_lit')

print()
if fails:
    print('SELFTEST FAILED:', ', '.join(fails)); sys.exit(1)
print('SELFTEST OK: the at-least-14 gadget is right in both polarities, and the literal map agrees with the frozen encoder')
