"""Auxiliary: weighted exact-cardinality clauses (colour class *element sizes*).

The W2 profile at a transitive vertex: for a Cayley colouring of K_n, the colour
degree at the identity is |S_c| = sum over the inverse classes of colour c of
their size (1 for an involution, 2 otherwise).  So "profile (15,14,14,14)" is a
weighted exact-cardinality constraint, one per colour.

Encoding: sequential counter over the weighted sum.  For a class of size w the
item is counted w times; we implement that by feeding w copies of the same
literal into a sequential counter.  Copies of one literal are sound because the
counter only requires "number of true literals = bound", and duplicating a
literal counts it twice iff it is true.

The counter is validated against brute force in selfcheck.py before it is used.
"""


def seq_counter_atmost(clauses, lits, k, top, out_final=None):
    """At most k of `lits` true.  Registers clauses; returns the index of the
    last partial counter variable (or None when the constraint is trivial)."""
    if k < 0:
        clauses.append([])                      # unsat
        return None
    if len(lits) <= k:
        return None
    if k == 0:
        for lit in lits:
            clauses.append([-lit])
        return None
    # s[i][j] : among lits[:i+1] at least j+1 are true.  j in 0..k
    s = []
    for i in range(len(lits)):
        row = []
        for j in range(k):
            top += 1
            row.append(top)
        s.append(row)
    # lits[0] -> s[0][0]
    clauses.append([-lits[0], s[0][0]])
    for j in range(1, k):
        clauses.append([-s[0][j]])
    for i in range(1, len(lits)):
        clauses.append([-lits[i], s[i][0]])
        clauses.append([-s[i - 1][0], s[i][0]])
        for j in range(1, k):
            clauses.append([-lits[i], -s[i - 1][j - 1], s[i][j]])
            clauses.append([-s[i - 1][j], s[i][j]])
        clauses.append([-lits[i], -s[i - 1][k - 1]])     # cannot overflow
    return top, s[-1][k - 1]


def weighted_equals(lits_weights, bound, top):
    """Clauses for  sum(w_i * x_i) == bound, weights positive ints.

    Returns (clauses, top)."""
    expanded = []
    for lit, w in lits_weights:
        for _ in range(w):
            expanded.append(lit)
    clauses = []
    n = len(expanded)
    if bound > n:
        return [[]], top
    r = seq_counter_atmost(clauses, expanded, bound, top)
    top_after = r[0] if r else top
    # at least bound: at most (n - bound) of the negations
    negs = [-lit for lit in expanded]
    r2 = seq_counter_atmost(clauses, negs, n - bound, top_after)
    top_final = r2[0] if r2 else top_after
    return clauses, top_final
