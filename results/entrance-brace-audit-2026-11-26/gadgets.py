"""Sequential cardinality counters and exact criticality guards, with self-tests.

Everything here is written from scratch so that its correctness can be tested
independently of the campaign's pysat usage.
"""


def atmost(lits, bound, top):
    """sum(lits) <= bound.  Returns (clauses, new_top).  Sequential counter."""
    lits = list(lits)
    n = len(lits)
    if bound < 0:
        return [[]], top
    if bound >= n:
        return [], top
    if bound == 0:
        return [[-l] for l in lits], top
    idx = {}
    for i in range(n):
        for j in range(1, bound + 1):
            top += 1
            idx[i, j] = top
    clauses = []
    for i in range(n):
        clauses.append([-lits[i], idx[i, 1]])
        if i >= 1:
            for j in range(1, bound + 1):
                clauses.append([-idx[i - 1, j], idx[i, j]])
            clauses.append([-lits[i], -idx[i - 1, bound]])
            for j in range(2, bound + 1):
                clauses.append([-lits[i], -idx[i - 1, j - 1], idx[i, j]])
    return clauses, top


def atleast(lits, bound, top):
    """sum(lits) >= bound, by negating."""
    return atmost([-l for l in lits], len(list(lits)) - bound, top)


def exactly(lits, k, top):
    c1, top = atleast(lits, k, top)
    c2, top = atmost(lits, k, top)
    return c1 + c2, top


def guard_atleast(lits, needed, top, guard):
    """guard -> sum(lits) >= needed.  Returns (clauses, new_top)."""
    cs, top = atleast(lits, needed, top)
    return [[-guard] + c for c in cs], top


def guard_atmost(lits, bound, top, guard):
    """guard -> sum(lits) <= bound."""
    cs, top = atmost(lits, bound, top)
    return [[-guard] + c for c in cs], top


def exact_guard(lits, needed, top, guard):
    """guard <-> sum(lits) >= needed.  Returns (clauses, new_top)."""
    cs, top = guard_atleast(lits, needed, top, guard)
    cs2, top = guard_atmost(lits, needed - 1, top, -guard)
    return cs + cs2, top
