"""Reference-admitting supports inside a template, with an explicit labelling.

A support of size 5 for arm colour i (in the entrance palette `pal`) must
induce a good two-colouring of K5 in the two colours pal\\{i}, with the
*smaller* of the two colours forming a five-cycle (the campaign's reference
convention, imported from Tatarevic 3.1).  A support of size 4 must induce
complementary paths P4.

The labelling of a support is the reference order: the cycle order (size 5)
resp. the path order 0-1-2-3 (size 4) of the smaller colour.
"""
import itertools


def cycle_order(vertices, edges):
    """vertices: list; edges: set of frozensets forming a single cycle."""
    if len(vertices) == 1:
        return list(vertices)
    adj = {v: [] for v in vertices}
    for e in edges:
        a, b = tuple(e)
        adj[a].append(b)
        adj[b].append(a)
    if any(len(adj[v]) != 2 for v in vertices):
        return None
    start = min(vertices)
    order = [start, adj[start][0]]
    while len(order) < len(vertices):
        cur = order[-1]
        nxt = [w for w in adj[cur] if w != order[-2]]
        order.append(nxt[0])
    if set(order) != set(vertices):
        return None
    return order


def path_order(vertices, edges):
    adj = {v: [] for v in vertices}
    for e in edges:
        a, b = tuple(e)
        adj[a].append(b)
        adj[b].append(a)
    ends = [v for v in vertices if len(adj[v]) == 1]
    if len(ends) != 2 or any(len(adj[v]) not in (1, 2) for v in vertices):
        return None
    order = [min(ends)]
    prev = None
    while len(order) < len(vertices):
        cur = order[-1]
        nxt = [w for w in adj[cur] if w != prev]
        if not nxt:
            return None
        prev, = [cur] if False else [cur]
        order.append(nxt[0])
        prev = cur
    return order


def reference_labelling(colour_of, positions, i, pal):
    """Verify that `positions` carries the reference two-colouring for arm colour i.

    colour_of(u, v) gives the actual colour of the edge uv (both in `pal`).
    Returns the reference labelling (a list of positions) or None.
    """
    two = sorted(set(pal) - {i})
    lo, hi = two
    n = len(positions)
    if n not in (4, 5):
        return None
    lo_edges = {frozenset((u, v)) for u, v in itertools.combinations(positions, 2)
                if colour_of(u, v) == lo}
    for u, v in itertools.combinations(positions, 2):
        c = colour_of(u, v)
        if c not in two:
            return None
    if n == 5:
        order = cycle_order(list(positions), lo_edges)
        if order is None:
            return None
        # the reference puts lo on 0-1-2-3-4-0 and hi on the five diagonal pairs
        return order
    order = path_order(list(positions), lo_edges)
    if order is None:
        return None
    return order
