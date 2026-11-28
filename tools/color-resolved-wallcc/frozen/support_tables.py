"""Optional redundant support constraints for critical marks in a fixed arm."""
from functools import cache
from itertools import combinations

from gluing import host, named_template


@cache
def allowed_supports(size, kind, target_arm, marked_color):
    matrix = named_template(size, kind, target_arm)
    allowed = []
    palette = [c for c in range(4) if c not in (target_arm, marked_color)]
    for order in (4, 5):
        for pts in combinations(range(size), order):
            if any(matrix[u][v] == marked_color for u, v in combinations(pts, 2)):
                continue
            degrees = sorted(sum(u != v and matrix[u][v] == palette[0] for v in pts)
                             for u in pts)
            if order == 5 and degrees == [2, 2, 2, 2, 2]:
                allowed.append(frozenset(pts))
            if order == 4 and degrees == [1, 1, 2, 2]:
                # At this degree sequence a simple graph on four vertices is a path.
                allowed.append(frozenset(pts))
    return tuple(allowed)


def support_clauses(family, x, guard, highest, positive, negative, known):
    """Enforce exact pentagons and four-vertex paths in classified target groups."""
    a = family.arm
    edge, _ = host(sum(family.profile) + 1)
    extra = []
    for b, (size, kind) in enumerate(zip(family.profile, family.root_kinds)):
        if b == a or kind == "-":
            continue
        start = sum(family.profile[:b]) + 1
        adjacent = [edge(x, start + j, a) for j in range(size)]
        must = {j for j, lit in enumerate(adjacent) if lit in positive}
        cannot = {j for j, lit in enumerate(adjacent)
                  if lit not in positive and (lit in negative or (lit - 1) // 4 in known)}
        selectors = []
        for possible in allowed_supports(size, kind, b, a):
            if not must <= possible or cannot & possible:
                continue
            highest += 1
            selector = highest
            selectors.append(selector)
            extra.extend([-selector, lit if j in possible else -lit]
                         for j, lit in enumerate(adjacent) if j not in must and j not in cannot)
        extra.append([-guard, *selectors])
    return highest, extra
