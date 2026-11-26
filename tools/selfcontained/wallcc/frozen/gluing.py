"""Enumerate and solve marked-root branches for four-color triangle Ramsey bounds.

Templates U and T are from Tatarevic, arXiv:2610.36648v2, as encoded in
formal/src/R4333Lean/CriticalTemplates.lean at commit 6c3f2fd.
A branch has all critical root cells fixed and one critical marked cell.
Local automorphisms preserve individual color names.
"""
import argparse
from dataclasses import dataclass
from functools import cache
from itertools import combinations, combinations_with_replacement, permutations, product
import json
from pathlib import Path
from time import process_time

DIFFERENCE_COLORS = (0, 0, 1, 1, 2, 2, 2, 1, 0, 2, 0, 1, 0, 1, 2, 0)
TRADE = {21, 22, 28, 31, 37, 38, 44, 47, 88, 91, 104, 107, 140, 143, 188, 191}


@cache
def template(size, kind):
    def color(u, v):
        rule = DIFFERENCE_COLORS[u ^ v]
        if kind == "T" and 16 * min(u, v) + max(u, v) in TRADE:
            return (0, 2, 1)[rule]
        return rule
    return tuple(tuple(color(u, v) for v in range(size)) for u in range(size))


@cache
def automorphisms(size, kind):
    matrix = template(size, kind)
    degrees = [tuple(sum(u != v and matrix[u][v] == c for v in range(size))
                     for c in range(3)) for u in range(size)]

    def extend(placement, unused):
        if not unused:
            yield placement
            return
        i = len(placement)
        for v in sorted(unused):
            if degrees[i] == degrees[v] and all(
                matrix[i][j] == matrix[v][w] for j, w in enumerate(placement)
            ):
                yield from extend(placement + (v,), unused - {v})

    result = tuple(extend((), set(range(size))))
    expected = {(16, "U"): 160, (16, "T"): 32, (15, "U"): 10, (15, "T"): 2}
    assert len(result) == expected[size, kind]
    return result


@cache
def positions(size, kind):
    if kind == "-":
        return (0,)
    group = automorphisms(size, kind)
    return tuple(i for i in range(size) if i == min(auto[i] for auto in group))


@cache
def named_template(size, kind, forbidden):
    palette = tuple(c for c in range(4) if c != forbidden)
    return tuple(tuple(palette[c] for c in row) for row in template(size, kind))


@cache
def support_embeddings(size, kind, forbidden, pattern):
    """Return one representative of each orbit of ordered embeddings."""
    k = {6: 4, 10: 5}[len(pattern)]
    if kind == "-":
        return (tuple(range(k)),)
    matrix = named_template(size, kind, forbidden)
    group = automorphisms(size, kind)
    required = dict(zip(combinations(range(k), 2), pattern))
    reps = []

    def extend(prefix, unused):
        if len(prefix) == k:
            if prefix == min(tuple(auto[v] for v in prefix) for auto in group):
                reps.append(prefix)
            return
        for v in sorted(unused):
            if all(matrix[w][v] == required[j, len(prefix)] for j, w in enumerate(prefix)):
                extend(prefix + (v,), unused - {v})

    extend((), set(range(size)))
    return tuple(reps)


@dataclass(frozen=True)
class Family:
    profile: tuple
    root_kinds: tuple
    arm: int
    mark_position: int
    marked_size: int
    marked_kind: str
    root_position: int


def profiles(order):
    return tuple(
        p for asc in combinations_with_replacement(range(order - 49, 17), 4)
        if sum(asc) == order - 1 for p in [asc[::-1]]
    )


def families(order, profile=None, root_kinds=None, arm=None):
    for p in profiles(order) if profile is None else (profile,):
        arms = range(4) if arm is None else (arm,)
        options = [("U", "T") if size >= 15 else ("-",) for size in p]
        for kinds in product(*options) if root_kinds is None else (root_kinds,):
            for a in arms:
                for q in positions(p[a], kinds[a]):
                    for s, t in product((15, 16), ("U", "T")):
                        for v in positions(s, t):
                            yield Family(p, kinds, a, q, s, t, v)


@cache
def orbit_data(profile, root_kinds, arm, marked_size, marked_kind, root_position):
    """Build orbit actions on each support for the stabilizer of the marked root."""
    s, t, v = marked_size, marked_kind, root_position
    marked = named_template(s, t, arm)
    group = tuple(auto for auto in automorphisms(s, t) if auto[v] == v)
    supports, options, actions = [], [], []
    for c in range(4):
        if c == arm:
            continue
        source = tuple(i for i in range(s) if i != v and marked[v][i] == c)
        assert len(source) in (4, 5)
        pattern = tuple(marked[i][j] for i, j in combinations(source, 2))
        size, kind = profile[c], root_kinds[c]
        embs = support_embeddings(size, kind, c, pattern)
        supports.append((c, source))
        options.append(embs)
        if kind == "-":
            actions.append(tuple((0,) for _ in group))
            continue
        target_group = automorphisms(size, kind)
        indices = {emb: i for i, emb in enumerate(embs)}
        actions.append(tuple(
            tuple(indices[min(tuple(auto[emb[k]] for k in perm) for auto in target_group)]
                  for emb in embs)
            for perm in (tuple(source.index(g[i]) for i in source) for g in group)
        ))
    return tuple(supports), tuple(options), tuple(zip(*actions))


def data(family):
    return orbit_data(
        family.profile, family.root_kinds, family.arm, family.marked_size,
        family.marked_kind, family.root_position
    )


def counts(family):
    _, options, actions = data(family)
    raw = len(options[0]) * len(options[1]) * len(options[2])
    fixed = sum(
        sum(j == k for j, k in enumerate(g[0]))
        * sum(j == k for j, k in enumerate(g[1]))
        * sum(j == k for j, k in enumerate(g[2]))
        for g in actions
    )
    count, remainder = divmod(fixed, len(actions))
    assert not remainder
    return raw, count


def representatives(family):
    _, options, actions = data(family)
    for indices in product(*(range(len(option)) for option in options)):
        if all(indices <= tuple(action[i] for action, i in zip(g, indices)) for g in actions):
            yield indices


@cache
def host(order):
    edges = {e: 4 * i + 1 for i, e in enumerate(combinations(range(order), 2))}

    def lit(u, v, c):
        return edges[min(u, v), max(u, v)] + c

    clauses = []
    for start in edges.values():
        options = list(range(start, start + 4))
        clauses.append(options)
        clauses.extend([-x, -y] for x, y in combinations(options, 2))
    clauses.extend(
        [-lit(u, v, c), -lit(u, w, c), -lit(v, w, c)]
        for u, v, w in combinations(range(order), 3) for c in range(4)
    )
    return lit, clauses


def units(family, indices):
    order = sum(family.profile) + 1
    lit, _ = host(order)
    groups = []
    start = 1
    for size in family.profile:
        groups.append(tuple(range(start, start + size)))
        start += size
    result = {lit(0, x, c) for c, block in enumerate(groups) for x in block}

    def fix_template(vertices, kind, forbidden):
        matrix = named_template(len(vertices), kind, forbidden)
        for i, j in combinations(range(len(vertices)), 2):
            result.add(lit(vertices[i], vertices[j], matrix[i][j]))

    for c, (block, kind) in enumerate(zip(groups, family.root_kinds)):
        if kind != "-":
            fix_template(block, kind, c)
    supports, options, _ = data(family)
    marked = [None] * family.marked_size
    marked[family.root_position] = 0
    for (c, source), choices, i in zip(supports, options, indices):
        for u, p in zip(source, choices[i]):
            marked[u] = groups[c][p]
    assert None not in marked and len(marked) == len(set(marked))
    fix_template(marked, family.marked_kind, family.arm)
    q = groups[family.arm][family.mark_position]
    for x in range(1, order):
        if x != q:
            result.add((1 if x in marked else -1) * lit(q, x, family.arm))
    assert all(-x not in result for x in result)
    positives = sorted(x for x in result if x > 0)
    assert len(positives) == len({(x - 1) // 4 for x in positives})
    return [[x] for x in sorted(result)]


def cheapest_ticket_arms(profile, arm_costs):
    sent = sum(size for size in profile if size >= 15)
    max_misses = sum(profile) - sent
    candidates = (
        (sum(arm_costs[i] for i in arms), arms)
        for k in range(1, 5) for arms in combinations(range(4), k)
        if sum(profile[i] for i in arms) > max_misses
    )
    return min(candidates, default=(0, ()))


def normalized_kinds(profile, kinds):
    return all(profile[i] != profile[i + 1] or kinds[i] <= kinds[i + 1]
               for i in range(3))


def cheapest_ticket_orbits(profile, kinds, costs):
    """Find the cheapest union of marked-position orbits that must contain a sender."""
    sent = sum(size for size in profile if size >= 15)
    if sent == 0:
        return 0, ()
    need = sum(profile) - sent + 1
    best = {0: (0, ())}
    for (arm, q), cost in sorted(costs.items()):
        size, kind = profile[arm], kinds[arm]
        weight = size if kind == "-" else len({
            auto[q] for auto in automorphisms(size, kind)
        })
        for covered, (previous_cost, chosen) in tuple(best.items()):
            target = min(need, covered + weight)
            candidate = (previous_cost + cost, (*chosen, (arm, q)))
            best[target] = min(candidate, best.get(target, candidate))
    return best[need]


def print_counts():
    print("order profile marked_15 marked_16 full_cover arm_cover orbit_cover")
    for n in (60, 59, 58, 57, 56):
        grand = arm_total = orbit_total = 0
        for p in profiles(n):
            by_size = {15: 0, 16: 0}
            arm_costs = {}
            normalized_costs = {}
            for f in families(n, p):
                count = counts(f)[1]
                by_size[f.marked_size] += count
                arm_costs.setdefault(f.root_kinds, [0] * 4)[f.arm] += count
                if normalized_kinds(p, f.root_kinds):
                    position_costs = normalized_costs.setdefault(f.root_kinds, {})
                    key = f.arm, f.mark_position
                    position_costs[key] = position_costs.get(key, 0) + count
            full = sum(by_size.values())
            arms = sum(cheapest_ticket_arms(p, costs)[0] for costs in arm_costs.values())
            orbits = sum(cheapest_ticket_orbits(p, kinds, costs)[0]
                         for kinds, costs in normalized_costs.items())
            grand += full
            arm_total += arms
            orbit_total += orbits
            print(n, p, by_size[15], by_size[16], full, arms, orbits, flush=True)
        print(n, "TOTAL", grand, arm_total, orbit_total, flush=True)


def ticket_units(family, fixed, scope):
    """Enforce incoming >= outgoing at this root, or its consequence for the selected arm."""
    from pysat.card import CardEnc

    n = sum(family.profile) + 1
    lit, _ = host(n)
    highest = 4 * n * (n - 1) // 2
    positive = {clause[0] for clause in fixed if clause[0] > 0}
    negative = {-clause[0] for clause in fixed if clause[0] < 0}
    known_color = {(l - 1) // 4: (l - 1) % 4 for l in positive}
    root_colors = [c for c, d in enumerate(family.profile) for _ in range(d)]
    sent = sum(d for d in family.profile if d >= 15)
    bound = sent
    if scope == "arm":
        bound -= n - 1 - family.profile[family.arm]
    if bound <= 0:
        return []
    vertices = [(x, c) for x, c in enumerate(root_colors, 1)
                if scope == "all" or c == family.arm]
    extra, selectors = [], []
    for x, c in vertices:
        candidates = []
        needed = 14  # The edge to the root already supplies one.
        for y, b in enumerate(root_colors, 1):
            if c == b:  # Includes x. A color-c edge here would complete a triangle.
                continue
            e = lit(x, y, c)
            if e in positive:
                needed -= 1
            elif e not in negative and (e - 1) // 4 not in known_color:
                candidates.append(e)
        if needed <= 0:
            bound -= 1
        elif needed <= len(candidates):
            highest += 1
            guard = highest
            selectors.append(guard)
            threshold = CardEnc.atleast(candidates, bound=needed, top_id=highest)
            highest = max(highest, threshold.nv)
            extra.extend([-guard, *clause] for clause in threshold.clauses)
    if bound > len(selectors):
        return [[]]
    if bound > 0:
        extra.extend(CardEnc.atleast(selectors, bound=bound, top_id=highest).clauses)
    return extra


def run(args):
    from pysat.formula import CNF
    from pysat.solvers import Solver

    profile = tuple(map(int, args.profile.split(",")))
    kinds = tuple(args.kinds)
    order = sum(profile) + 1
    assert profile in profiles(order)
    assert all((t in "UT") if size >= 15 else t == "-" for t, size in zip(kinds, profile))
    _, clauses = host(order)
    index = 0
    selection = set(map(int, args.pick.split(","))) if args.pick else None
    for f in families(order, profile, kinds, args.arm):
        if args.marked_size and f.marked_size != args.marked_size:
            continue
        if args.marked_kind and f.marked_kind != args.marked_kind:
            continue
        reps = tuple(representatives(f))
        assert len(reps) == counts(f)[1]
        for indices in reps:
            branch = index
            index += 1
            if selection is not None and branch not in selection:
                continue
            if branch % args.shards != args.shard:
                continue
            if args.limit and branch >= args.limit:
                return
            fixed = units(f, indices)
            if args.tickets:
                fixed.extend(ticket_units(f, fixed, args.tickets))
            start = process_time()
            with Solver(name=args.solver, bootstrap_with=clauses + fixed,
                        with_proof=args.proofs is not None) as solver:
                solver.conf_budget(args.budget)
                answer = solver.solve_limited()
                elapsed = process_time() - start
                stat = solver.accum_stats()
                if answer is True:
                    model = set(solver.get_model())
                    assert all(any(lit in model for lit in clause) for clause in clauses + fixed)
                if answer is False and args.proofs is not None:
                    output = Path(args.proofs)
                    output.mkdir(parents=True, exist_ok=True)
                    CNF(from_clauses=clauses + fixed).to_file(str(output / f"{branch}.cnf"))
                    (output / f"{branch}.drup").write_text("\n".join(solver.get_proof()) + "\n")
            print(json.dumps({
                "branch": branch, "order": order, "family": vars(f), "placements": indices,
                "status": "UNSAT" if answer is False else "SAT" if answer else "OPEN",
                "conflicts": stat["conflicts"], "cpu_seconds": round(elapsed, 4),
            }), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("count")
    sample = sub.add_parser("run")
    sample.add_argument("profile")
    sample.add_argument("kinds")
    sample.add_argument("--arm", type=int, default=0)
    sample.add_argument("--marked-size", type=int, choices=(15, 16))
    sample.add_argument("--marked-kind", choices=("U", "T"))
    sample.add_argument("--budget", type=int, default=100000)
    sample.add_argument("--solver", default="cadical195")
    sample.add_argument("--shards", type=int, default=1)
    sample.add_argument("--shard", type=int, default=0)
    sample.add_argument("--limit", type=int, default=0)
    sample.add_argument("--proofs")
    sample.add_argument("--pick")
    sample.add_argument("--tickets", choices=("arm", "all"))
    args = parser.parse_args()
    if args.command == "count":
        print_counts()
    else:
        run(args)


if __name__ == "__main__":
    main()
