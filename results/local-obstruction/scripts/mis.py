"""Exact maximum independent set on a small bitset graph.

Independent set in G = clique in the complement, so we run the classic
colouring-bound clique search (Tomita/MCQ style) on the complement.
The bound: greedily partition the candidate set into cliques of the
*complement* (= independent sets of G); a clique of the complement meets an
independent set of G in at most one vertex, so the number of classes bounds it.

Validated against brute force in `selftest()`.
"""


def _greedy_classes(adjc, P):
    """Greedy partition of mask P into classes each independent in adjc."""
    order, bounds = [], []
    U = P
    k = 0
    while U:
        k += 1
        Q = U
        while Q:
            b = Q & -Q
            v = b.bit_length() - 1
            order.append(v)
            bounds.append(k)
            U &= ~b
            Q &= ~b
            Q &= ~adjc[v]
    return order, bounds


def max_inset(adj, n):
    """Maximum independent set of the graph on 0..n-1 with adjacency masks `adj`."""
    # complement adjacency
    allmask = (1 << n) - 1
    adjc = [allmask & ~adj[v] & ~(1 << v) for v in range(n)]
    best = [0, 0]

    def expand(size, P, R):
        if P == 0:
            if size > best[0]:
                best[0] = size
                best[1] = R
            return
        order, bounds = _greedy_classes(adjc, P)
        for i in range(len(order) - 1, -1, -1):
            if size + bounds[i] <= best[0]:
                return
            v = order[i]
            b = 1 << v
            if not (P & b):
                continue
            Q = P & adjc[v]
            if Q == 0:
                if size + 1 > best[0]:
                    best[0] = size + 1
                    best[1] = R | b
            else:
                expand(size + 1, Q, R | b)
            P &= ~b
            if P == 0:
                return

    expand(0, allmask, 0)
    return best[0], best[1]


def all_insets(adj, n, target, cap=10 ** 7):
    """All independent sets of size exactly `target` (list of masks)."""
    allmask = (1 << n) - 1
    adjc = [allmask & ~adj[v] & ~(1 << v) for v in range(n)]
    out = []

    def expand(size, P, R):
        if len(out) > cap:
            raise RuntimeError("cap exceeded")
        if size == target:
            out.append(R)
            return
        if P == 0:
            return
        order, bounds = _greedy_classes(adjc, P)
        for i in range(len(order) - 1, -1, -1):
            if size + bounds[i] < target:
                return
            v = order[i]
            b = 1 << v
            if not (P & b):
                continue
            expand(size + 1, P & adjc[v], R | b)
            P &= ~b
            if P == 0:
                return

    expand(0, allmask, 0)
    return out


def selftest(trials=400, seed=1):
    import random, itertools
    rng = random.Random(seed)
    for t in range(trials):
        n = rng.randint(1, 9)
        p = rng.random()
        adj = [0] * n
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < p:
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
        a, mask = max_inset(adj, n)
        # brute force
        best = 0
        for s in range(1 << n):
            ok = True
            for u in range(n):
                if (s >> u) & 1 and (adj[u] & s):
                    ok = False
                    break
            if ok:
                best = max(best, s.bit_count())
        assert a == best, (n, adj, a, best)
        # mask must be independent of the claimed size
        assert mask.bit_count() == a
        for u in range(n):
            if (mask >> u) & 1:
                assert adj[u] & mask == 0
        # enumeration
        got = all_insets(adj, n, a) if a <= n else []
        assert len(got) == sum(1 for s in range(1 << n)
                               if s.bit_count() == a and all(not ((s >> u) & 1 and (adj[u] & s)) for u in range(n))), (n, adj)
    return trials


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        print("selftest OK on", selftest(), "random graphs")
