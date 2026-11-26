"""Two-sided lookahead on physical edge-color literals and a checked binary cover."""
from itertools import islice
from pysat.solvers import Minisat22
from problem import ranked_variables, require


def propagator(clauses):
    # Capturing initial units as assumptions once exposes their consequences,
    # which Minisat otherwise omits from subsequent propagate() responses.
    solver = Minisat22()
    units = []
    for c in clauses:
        if len(c) == 1:
            units.append(c[0])
        else:
            solver.add_clause(c)
    ok, implied = solver.propagate(assumptions=units)
    for v in units:
        solver.add_clause([v])
    return solver, set(units).union(implied or ()), ok


def make_tree(clauses, limit, special, tables, depth, width, solver, fixed, feasible):
    ranked = ranked_variables(clauses, limit)
    splits = {}

    def choose(cube):
        ok, trail = solver.propagate(assumptions=cube)
        if not ok:
            return None
        here = fixed.union(trail, cube)
        def free(seq):
            return (v for v in seq if v not in here and -v not in here)
        scores = {}
        for table in tables:
            for v, score in table.candidates(here):
                scores[v] = max(scores.get(v, (-1, 0)), score)
        word_order = sorted(scores, key=lambda v: (-scores[v][0], -scores[v][1], v))
        # Give each available source a place in the shortlist before filling it.
        pool = {}
        sources = [word_order, special, ranked]
        for order in sources:
            for v in islice(free(order), max(1, width // 3)):
                pool[v] = None
        for order in sources:
            if len(pool) >= width:
                break
            for v in free(order):
                pool[v] = None
                if len(pool) >= width:
                    break
        best, winner = None, None
        for v in islice(pool, width):
            impacts = []
            failures = 0
            for lit in (v, -v):
                possible, ext = solver.propagate(assumptions=[*cube, lit])
                if not possible:
                    failures += 1
                impacts.append(max(0, len(ext or ()) - len(trail)))
            l, r = impacts
            score = (failures, (1+l)*(1+r), min(l,r), scores.get(v, (-1, 0)), -v)
            if best is None or score > best:
                best, winner = score, v
        return winner

    pending = [("r", [])] if feasible else []
    while pending:
        node, cube = pending.pop()
        if len(cube) >= depth:
            continue
        v = choose(cube)
        if v is not None:
            splits[node] = v
            pending.extend([(node + "1", [*cube, v]), (node + "0", [*cube, -v])])
    return splits


def cover(splits, limit, depth):
    require(isinstance(splits, dict), "invalid split tree")
    pending = [("r", ())]
    leaves, reached = [], set()
    while pending:
        node, cube = pending.pop()
        if node not in splits:
            leaves.append((node, cube))
            continue
        v = splits[node]
        require(type(v) is int and 1 <= v <= limit and len(cube) < depth
                and v not in cube and -v not in cube, f"invalid split at {node}")
        reached.add(node)
        pending.extend([(node + "1", (*cube, v)), (node + "0", (*cube, -v))])
    require(len(reached) == len(splits), "unreachable split in tree")
    return leaves
