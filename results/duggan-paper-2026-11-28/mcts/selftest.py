#!/usr/bin/env python3
import json
from pathlib import Path
from audit_cubes import audit
from run_leaves import without_deletions, write_query

pool = list(range(1, 20))
valid_ragged = [[-1, -2], [-1, 2, -3], [-1, 2, 3], [1, -4], [1, 4]]
a = audit(valid_ragged, pool)
assert a['valid_full_binary_cover'] and a['leaves'] == 5 and a['depth'] == 3
for bad in (
    [[-1, -2], [-1, 2], [1]],                         # unequal depth is fine
    [[-1, -2], [-1, 2], [1, -3]],                   # missing positive sibling
    [[-1, -2], [-0 if False else 1, 2]],            # only one root sign
    [[-1, -2], [-1, 2], [1, 99]],                   # outside pool
    [[-1], [-1], [1]],                                # duplicate negative leaf
):
    try:
        audit(bad, pool)
    except ValueError:
        pass
    else:
        # The first case is a valid depth-2 tree and is checked positively below.
        if bad != [[-1, -2], [-1, 2], [1]]:
            raise AssertionError(f'invalid cover accepted: {bad}')
assert audit([[-1, -2], [-1, 2], [1]], pool)['leaves'] == 3

# The raw positive K6 proof contains four deletions and 25 additions.  Its
# addition-only form is exactly the artifact that two checkers accepted.
raw = Path('results/k6-control-leaves-fixed/leaf-0/joined.drat').read_bytes()
normalized, info = without_deletions(raw)
assert info == {'additions_preserved': 25, 'deletions_removed': 4}
assert normalized == Path('results/k6-control-leaves-fixed/leaf-0/joined.additions-only.drat').read_bytes()
for bad in (b'a\x80', b'x\x00'):
    try:
        without_deletions(bad)
    except (ValueError, IndexError):
        pass
    else:
        raise AssertionError('malformed binary proof accepted')

# Regression for the duplicated-header bug: exactly one header, all parent
# clauses, and no extra non-cube clauses.
out = Path('.scratch/query-regression.cnf')
write_query(Path('results/k6-control-run/parent.cnf'), [1, -2], out)
lines = out.read_text().splitlines()
assert lines[0] == 'p cnf 15 42'
assert sum(x.startswith('p cnf') for x in lines) == 1
assert lines[-2:] == ['1 0', '-2 0']
assert lines[1:-2] == Path('results/k6-control-run/parent.cnf').read_text().splitlines()[1:]

summary = json.loads(Path('results/summary.json').read_text())
assert summary['control']['full20_mcts']['conflicts'] == 284528
assert summary['control']['greedy']['conflicts'] == 226881
assert summary['control']['full20_mcts']['status_counts'] == {'CHECKED_UNSAT': 4}
assert summary['wall']['shallow_mcts']['status_counts'] == {'OPEN': 4}
assert summary['wall']['selective_recube']['status_counts'] == {'OPEN': 2}
second = json.loads(Path('results/second-checker-summary.json').read_text())
assert second['count'] == second['passed'] == 11 and second['failures'] == 0
assert json.loads(Path('results/wall-refined-frontier-audit.json').read_text())['leaves'] == 5
print('PASS: valid/ragged and invalid covers, proof normalization, query encoding, totals, 11 second-checker receipts')
