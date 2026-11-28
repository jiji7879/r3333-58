#!/usr/bin/env python3
"""Abstract the actual counter calls and test their permutation equivariance."""
from collections import Counter
import json
import symmetry_fit as s
import dense
import support_tables
from pysat.card import CardEnc

row = s.load_row()
fields = {k: tuple(v) if k in ('profile', 'root_kinds') else v
          for k, v in row['family'].items()}
family = s.Family(**fields)
fixed = s.units(family, row['placement'])
log, supports = [], []
original_atleast = CardEnc.atleast
original_support = support_tables.support_clauses

class Fake:
    def __init__(self, nv):
        self.nv = nv
        self.clauses = []

def atleast(lits, bound, top_id):
    log.append((tuple(lits), bound))
    return Fake(top_id)

def support(fam, x, guard, highest, positive, negative, known):
    supports.append((x, guard, highest))
    return original_support(fam, x, guard, highest, positive, negative, known)

CardEnc.atleast = staticmethod(atleast)
support_tables.support_clauses = support
recipe = dict(tables=True, total_critical=True, full_root=False)
dense.marked_threshold(family, fixed, row['charge'], **recipe)
CardEnc.atleast = original_atleast
support_tables.support_clauses = original_support

abstract = Counter((tuple(sorted(lits)), b) for lits, b in log)
positive = {c[0] for c in fixed if c[0] > 0}
negative = {-c[0] for c in fixed if c[0] < 0}
known = {(c[0]-1)//4 for c in fixed if c[0] > 0}
all_support_literals = set()
for x, guard, highest in supports:
    _, clauses = original_support(family, x, guard, highest, positive, negative, known)
    all_support_literals.update(abs(lit) for clause in clauses for lit in clause)

results = []
for a, b in s.cells_and_pairs(fixed)[1]:
    perm = s.vertex_permutation(a, b)
    image = Counter((tuple(sorted(s.literal_image(x, perm) for x in lits)), bound)
                    for lits, bound in log)
    support_ok = all(s.literal_image(lit, perm) == lit for lit in all_support_literals)
    results.append(dict(transposition=[a, b], counter_spec_equal=abstract == image,
                        support_literals_fixed=support_ok))

out = dict(counter_calls=len(log),
           sender_counter_calls=sum(lits and max(map(abs, lits), default=0) <= 6612 for lits, _ in log),
           final_selector_counter_calls=sum(lits and max(map(abs, lits), default=0) > 6612 for lits, _ in log),
           support_calls=len(supports), support_sender_vertices=sorted({x for x, _, _ in supports}),
           tests=results,
           passed=sum(t["counter_spec_equal"] and t["support_literals_fixed"] for t in results))
print(json.dumps(out, indent=2, sort_keys=True))
