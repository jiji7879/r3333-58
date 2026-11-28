"""Generate redundant C-side clauses in RUP order, using physical variables only."""
from itertools import combinations, permutations, product

from gluing import data, host, units


def anchor_sets(family, placement):
    small = family.profile.index(min(family.profile))
    if small == family.arm or family.root_kinds[small] != "-":
        return None
    supports, options, _ = data(family)
    slot = next(i for i, (color, _) in enumerate(supports) if color == small)
    start = 1 + sum(family.profile[:small])
    anchor = tuple(sorted(start+p for p in options[slot][placement[slot]]))
    assert len(anchor) in (4, 5)
    residual = tuple(x for x in range(start,start+family.profile[small]) if x not in anchor)
    return small, anchor, residual


def cuts_for(family, placement):
    geometry = anchor_sets(family,placement)
    if geometry is None:
        return []
    small, anchor, residual = geometry
    a = family.arm
    b,c = (t for t in range(4) if t not in (a,small))
    edge, _ = host(58)
    unit = {row[0] for row in units(family,placement)}
    ordered = {}
    for u,v in combinations(anchor,2):
        assert (edge(u,v,b) in unit) != (edge(u,v,c) in unit)
    def emit(clause):
        key = tuple(sorted(set(clause)))
        if not any(-lit in key for lit in key):
            ordered.setdefault(key,list(clause))

    # For two residual vertices, a joint neighbor of each of the three
    # allowed colors forbids all three choices of their joining edge.
    for x,y in combinations(residual,2):
        for points in permutations(anchor,3):
            emit([-edge(v,p,t) for p,t in zip(points,(a,b,c)) for v in (x,y)])

    if len(anchor) != 5:
        return list(ordered.values())

    def legal(positions, word):
        return all(t!=u or edge(x,y,t) not in unit
                   for (x,t),(y,u) in combinations(zip(positions,word),2))

    def refute_two_colors(x, positions, goal, prefix=(), assigned=()):
        # Negating goal eliminates color a at positions; root edges
        # eliminate color d. Resolve the two candidate colors bottom up.
        if legal(positions,assigned):
            assert len(prefix)<len(positions), (x,positions,goal,assigned)
            point = positions[len(prefix)]
            for color in (b,c):
                refute_two_colors(x,positions,goal,
                                  (*prefix,-edge(x,point,color)),(*assigned,color))
        emit([*goal,*prefix])

    for x in residual:
        refute_two_colors(x,anchor,[edge(x,s,a) for s in anchor])

    for s in anchor:
        others = tuple(v for v in anchor if v!=s)
        (unique,) = tuple(w for w in product((b,c),repeat=4) if legal(others,w))
        absent = {x:[-edge(x,s,a),*(edge(x,v,a) for v in others)] for x in residual}
        for x in residual:
            for point, color in zip(others,unique):
                wrong = c if color==b else b
                positions = (point,*(v for v in others if v!=point))
                # Under negation, this point has the wrong color.
                refute_two_colors(x,positions,[*absent[x],edge(x,point,color)],
                                  (-edge(x,point,wrong),),(wrong,))
                emit([*absent[x],edge(x,point,color)])
        for x,y in combinations(residual,2):
            emit([*absent[x],*absent[y]])
    return list(ordered.values())


def binary_prefix(clauses):
    out=bytearray()
    for clause in clauses:
        out.append(ord("a"))
        for literal in clause:
            value=2*abs(literal)+(literal<0)
            while value>=128:
                out.append(128 | (value & 127))
                value >>=7
            out.append(value)
        out.append(0)
    return bytes(out)
