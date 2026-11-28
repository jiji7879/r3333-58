#!/usr/bin/env python3
"""Direct structural audit of results/hailmary-lex/hm.py (no model search)."""
import hashlib
import itertools
import json
import sys
from pathlib import Path
from pysat.formula import CNF

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCE = REPO / "results/hailmary-lex/hm.py"
sys.path.insert(0, str(SOURCE.parent))
import hm

# n=4, u=0, v=3 leaves two witnesses. Reserve all 96 physical variables.
n, u, v = 4, 0, 3
edges = {e: 4 * i + 1 for i, e in enumerate(itertools.combinations(range(n), 2))}
def lit(a, b, c):
    return edges[min(a, b), max(a, b)] + c
physical_top = 4 * n * (n - 1) // 2
cnf = CNF(from_clauses=[list(range(1, physical_top + 1))])
hm.lex_leader(cnf, lit, u, v, nv=n)
added = cnf.clauses[1:]
assert len(added) == 23
assert all(any(x > physical_top for x in clause) for clause in added)
# Consequently the all-TRUE auxiliary assignment satisfies every added clause,
# irrespective of the physical assignment. Check that statement explicitly for
# both physical polarities on every physical variable.
for physical_bit in (False, True):
    def value(x):
        truth = True if abs(x) > physical_top else physical_bit
        return truth if x > 0 else not truth
    assert all(any(value(x) for x in clause) for clause in added)

# Apply the same structural test to the regenerated exact case-7 historical CNF.
path = HERE / "case7-historical.cnf"
with path.open() as stream:
    header = stream.readline().split()
    nv, nc = int(header[2]), int(header[3])
    base_count, physical_top58 = 135333, 6612
    appended_positive = 0
    for index, line in enumerate(stream):
        clause = [int(x) for x in line.split()[:-1]]
        if index >= base_count:
            assert any(x > physical_top58 for x in clause), (index, clause)
            appended_positive += 1
assert (nv, nc, appended_positive) == (8628, 142737, 7404)
result = {
    "source": "results/hailmary-lex/hm.py::lex_leader",
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "n4_comparator_clauses": len(added),
    "n4_every_clause_has_positive_fresh_aux": True,
    "all_aux_true_extends_every_physical_assignment": True,
    "case7_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    "case7_added_clauses": appended_positive,
    "case7_every_added_clause_has_positive_fresh_aux": True,
}
(HERE / "vacuity.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
