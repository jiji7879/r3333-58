#!/usr/bin/env python3
"""Guard only the bound clauses of a Sinz at-least counter.

For g -> (sum(x) >= k), the repository's naive form prepends -g to every
clause. The boundary form leaves the recurrence untouched and prepends -g
only to overflow clauses. Both have exactly the projected Boolean relation
g -> (sum(x) >= k), but boundary has strictly stronger unit propagation.

Run from repository root:
  .scratch/k58/.venv/bin/python -B .ultramath/smwzxq4fl/m3/guarded_counter.py
"""
import itertools
import json
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.solvers import Minisat22

OUT = Path(__file__).with_name("guarded-counter-results.json")


def split_atleast(lits, k, top):
    """Return (recurrence, bound/overflow clauses, new_top).

    This is the staggered Sinz at-most counter on -lits, split by semantic
    role. For 1 < k < n its concatenation is exactly PySAT's at-least
    seqcounter (checked below). The direct cases k=1 and k=n have no
    recurrence and their PySAT clauses are bound clauses.
    """
    lits = list(lits)
    n = len(lits)
    if k <= 0:
        return [], [], top
    if k > n:
        return [], [[]], top
    if k == n:
        return [], [[x] for x in lits], top
    if k == 1:
        return [], [lits], top

    # At least k of x iff at most m=n-k of y=-x. Cell(d,j) denotes at least
    # j+1 true y's in the processed prefix. k rows by m columns.
    m = n - k

    def index(d, j):
        if d == 0:
            return 2 * j
        if d == 1:
            return 2 * j + 1
        return d * m + j

    def cell(d, j):
        return top + 1 + index(d, j)

    recurrence, bound = [], []
    y = [-x for x in lits]
    for d in range(n - m):
        for j in range(m):
            if j == 0:
                recurrence.append([-y[d + j], cell(d, j)])
            else:
                recurrence.append([-y[d + j], -cell(d, j - 1), cell(d, j)])
            if d + 1 < n - m:
                recurrence.append([-cell(d, j), cell(d + 1, j)])
        bound.append([-y[d + m], -cell(d, m - 1)])
    return recurrence, bound, top + (n - m) * m


def conditional_atleast(lits, k, guard, top, style="boundary"):
    """CNF for guard -> at-least(k,lits), with fresh variables above top."""
    if style not in ("naive", "boundary", "hard", "unsound-no-guard"):
        raise ValueError(style)
    recurrence, bound, new_top = split_atleast(lits, k, top)
    if k <= 0:
        return [], new_top
    if style in ("hard", "unsound-no-guard"):
        return recurrence + bound, new_top
    if style == "naive":
        return [[-guard] + c for c in recurrence + bound], new_top
    # Violating k>n must derive -guard, not the empty clause.
    return recurrence + [[-guard] + c for c in bound], new_top


def bcp(clauses, initial):
    """Small independent unit propagator. Returns (conflict, assignment)."""
    assigned = dict(initial)
    while True:
        changed = False
        for clause in clauses:
            unassigned = []
            satisfied = False
            for lit in clause:
                if abs(lit) not in assigned:
                    unassigned.append(lit)
                elif assigned[abs(lit)] == (lit > 0):
                    satisfied = True
                    break
            if satisfied:
                continue
            if not unassigned:
                return True, assigned
            if len(unassigned) == 1:
                lit = unassigned[0]
                var, value = abs(lit), lit > 0
                if var in assigned and assigned[var] != value:
                    return True, assigned
                if var not in assigned:
                    assigned[var] = value
                    changed = True
        if not changed:
            return False, assigned


def projected_models(n, k, partial):
    """All physical/guard completions of the exact relation, as dictionaries."""
    variables = list(range(1, n + 2))  # x_1..x_n, guard=n+1
    free = [v for v in variables if v not in partial]
    models = []
    for bits in itertools.product((False, True), repeat=len(free)):
        a = dict(partial)
        a.update(zip(free, bits))
        count = sum(a[x] for x in range(1, n + 1))
        if not a[n + 1] or count >= k:
            models.append(a)
    return models


def partial_assignments(n):
    variables = list(range(1, n + 2))
    for values in itertools.product((-1, False, True), repeat=n + 1):
        yield {v: value for v, value in zip(variables, values) if value != -1}


def main():
    result = {"encoding": "guard only Sinz overflow clauses", "checks": {}}

    # Clause-for-clause agreement with the library used by the live encoder.
    hard_comparisons = 0
    for n in range(2, 13):
        for k in range(1, n + 1):
            rec, bound, top = split_atleast(range(1, n + 1), k, n)
            py = CardEnc.atleast(list(range(1, n + 1)), bound=k, top_id=n,
                                 encoding=EncType.seqcounter)
            assert sorted(map(tuple, rec + bound)) == sorted(map(tuple, py.clauses)), (n, k)
            assert top == py.nv, (n, k, top, py.nv)
            hard_comparisons += 1
    result["checks"]["pysat_hard_clause_equality"] = hard_comparisons

    # Independent SAT projection check, including impossible and trivial bounds.
    semantic_cases = 0
    for n in range(1, 9):
        inputs = list(range(1, n + 1))
        guard = n + 1
        for k in range(0, n + 2):
            forms = {}
            for style in ("naive", "boundary"):
                clauses, top = conditional_atleast(inputs, k, guard, guard, style)
                solver = Minisat22(bootstrap_with=clauses)
                forms[style] = (solver, clauses, top)
            try:
                for bits in itertools.product((False, True), repeat=n + 1):
                    assumptions = [i + 1 if bit else -(i + 1) for i, bit in enumerate(bits)]
                    expected = (not bits[-1]) or sum(bits[:-1]) >= k
                    answers = {name: solver.solve(assumptions=assumptions)
                               for name, (solver, _, _) in forms.items()}
                    assert answers["naive"] == answers["boundary"] == expected, (n, k, bits, answers)
                    semantic_cases += 1
            finally:
                for solver, _, _ in forms.values():
                    solver.delete()
    result["checks"]["sat_projection_assignments"] = semantic_cases

    # Exhaustive partial-assignment consequences for n<=6. Compare BCP with
    # every literal forced by the exact projected relation (not by aux choice).
    stats = {s: {"partial_assignments": 0, "forced_literals": 0,
                 "missed_forced_literals": 0, "missed_conflicts": 0,
                 "unsound_conflicts": 0}
             for s in ("naive", "boundary")}
    examples = []
    for n in range(2, 7):
        inputs = list(range(1, n + 1))
        guard = n + 1
        for k in range(1, n + 1):
            enc = {}
            for style in stats:
                clauses, _ = conditional_atleast(inputs, k, guard, guard, style)
                enc[style] = clauses
            for partial in partial_assignments(n):
                models = projected_models(n, k, partial)
                expected = {}
                if not models:
                    expected["conflict"] = True
                else:
                    for v in range(1, n + 2):
                        if v not in partial:
                            values = {m[v] for m in models}
                            if len(values) == 1:
                                expected[v] = values.pop()
                for style, clauses in enc.items():
                    rec = stats[style]
                    rec["partial_assignments"] += 1
                    conflict, got = bcp(clauses, partial)
                    if conflict and models:
                        rec["unsound_conflicts"] += 1
                    if not models and not conflict:
                        rec["missed_conflicts"] += 1
                    for key, value in expected.items():
                        if key == "conflict":
                            continue
                        rec["forced_literals"] += 1
                        if got.get(key) != value:
                            rec["missed_forced_literals"] += 1
                            if style == "naive" and len(examples) < 8:
                                examples.append({"n": n, "k": k, "partial": partial,
                                                 "missed": {str(key): value},
                                                 "naive_assignment": {str(a): b for a, b in got.items()
                                                                      if a <= n + 1}})
    result["checks"]["partial_propagation"] = stats
    result["naive_miss_examples"] = examples
    assert all(v["unsound_conflicts"] == 0 for v in stats.values())
    # The boundary encoding is meant to remove all of these projection-UP gaps.
    boundary = stats["boundary"]
    assert boundary["missed_forced_literals"] == 0, boundary
    assert boundary["missed_conflicts"] == 0, boundary

    # Every full violating input assignment must explicitly derive -guard.
    back = {s: {"violating_assignments": 0, "derived_not_guard": 0} for s in stats}
    for n in range(2, 11):
        for k in range(1, n + 1):
            for bits in itertools.product((False, True), repeat=n):
                if sum(bits) >= k:
                    continue
                partial = {i + 1: bit for i, bit in enumerate(bits)}
                for style in back:
                    clauses, _ = conditional_atleast(range(1, n + 1), k, n + 1, n + 1, style)
                    conflict, got = bcp(clauses, partial)
                    assert not conflict
                    back[style]["violating_assignments"] += 1
                    back[style]["derived_not_guard"] += (got.get(n + 1) is False)
    result["checks"]["full_violation_backpropagation"] = back
    assert back["boundary"]["derived_not_guard"] == back["boundary"]["violating_assignments"]

    # Negative control: dropping the guard is genuinely unsound.
    clauses, _ = conditional_atleast([1, 2, 3], 2, 4, 4, "unsound-no-guard")
    with Minisat22(bootstrap_with=clauses) as solver:
        assert not solver.solve(assumptions=[-4, 1, -2, -3])
    result["checks"]["negative_no_guard_rejected"] = True

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
