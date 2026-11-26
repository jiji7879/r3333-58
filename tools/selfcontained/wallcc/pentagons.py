"""Enumerate rooted pentagon extensions and emit their RUP derivations."""
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, product

from problem import family_and_pins, host, require
from anchor_cuts import binary_prefix


@lru_cache(maxsize=256)
def local_words(internal, forbidden):
    colors = tuple(c for c in range(4) if c != forbidden)
    pairs = tuple(combinations(range(5), 2))
    return tuple(w for w in product(colors, repeat=5)
                 if all(w[i] != w[j] or w[i] != c for (i, j), c in zip(pairs, internal)))


@dataclass
class Table:
    edges: tuple
    masks: tuple
    all_words: int

    def candidates(self, true):
        alive = self.all_words
        for base, masks in zip(self.edges, self.masks):
            for c, mask in enumerate(masks):
                if base + c in true:
                    alive &= mask
                elif -(base + c) in true:
                    alive &= ~mask
        count = alive.bit_count()
        if count < 2:
            return
        for base, masks in zip(self.edges, self.masks):
            for c, mask in enumerate(masks):
                yes = (alive & mask).bit_count()
                if 0 < yes < count:
                    yield base + c, (min(yes, count-yes) / count, -count)


def resolution_tree(goal, variables):
    def visit(prefix):
        if len(prefix) < len(variables):
            v = variables[len(prefix)]
            yield from visit((*prefix, v))
            yield from visit((*prefix, -v))
        yield (*goal, *prefix)
    return list(visit(()))


def compile_cas(row, true):
    """true contains only root-level facts obtained from the frozen parent."""
    family, pins = family_and_pins(row)
    positive = set(v for v in pins if v > 0)
    edge, _ = host(58)
    groups = []
    start = 1
    for size in family.profile:
        groups.append(tuple(range(start, start + size)))
        start += size
    a = family.arm
    q = groups[a][family.mark_position]
    marked = tuple(x for x in range(58) if x != q and edge(q, x, a) in positive)
    require(len(marked) == family.marked_size and 0 in marked, "incomplete marked neighborhood")
    cuts, tables, trace = {}, [], bytearray()

    def derive(full, decisions):
        if any(v in true for v in full):
            return
        goal = tuple(sorted(v for v in full if -v not in true))
        if goal in cuts:
            return
        cuts[goal] = None
        proof = resolution_tree(goal, decisions)
        trace.extend(binary_prefix(proof))
        # Restore exactly the parent plus the new conclusions before CaDiCaL's trace.
        for clause in proof[:-1]:
            trace.extend(b"d" + binary_prefix([clause])[1:])

    for b, group in enumerate(groups):
        block = tuple(x for x in group if x in marked)
        if b == a or len(block) != 5:
            continue
        ordinary = tuple(c for c in range(4) if c not in (a, b))
        internal = []
        for u, v in combinations(block, 2):
            pinned = [c for c in ordinary if edge(u, v, c) in positive]
            require(len(pinned) == 1, "uncolored pentagon edge")
            internal.append(pinned[0])
        for x in block:
            for c in ordinary:
                require(sum(edge(x, y, c) in positive for y in block if y != x) == 2,
                        "support is not a pinned two-colored pentagon")
        for vertices, forbidden, hit in ((group, b, a), (marked, a, b)):
            words = local_words(tuple(internal), forbidden)
            require(all(hit in w for w in words), "unexpected two-color extension of a pentagon")
            masks = tuple(tuple(sum(1 << k for k, w in enumerate(words) if w[i] == c)
                                for c in range(4)) for i in range(5))
            single = []
            for p in range(5):
                single.append([w for w in words if w[p] == hit and w.count(hit) == 1])
                require(len(single[p]) == 1, "nonunique single-hit extension")
            for x in vertices:
                if x in block:
                    continue
                bases = tuple(edge(x, y, 0) for y in block)
                if all(any(v + c in true for c in range(4)) for v in bases):
                    continue
                tables.append(Table(bases, masks, (1 << len(words)) - 1))
                hits = tuple(v + hit for v in bases)
                decisions = tuple(v + ordinary[0] for v in bases)
                derive(hits, decisions)
                for p, (word,) in enumerate(single):
                    others = tuple(i for i in range(5) if i != p)
                    for j in others:
                        # If all four other positions miss, their colors are forced.
                        goal = tuple(hits[i] for i in others) + (bases[j] + word[j],)
                        derive(goal, tuple(decisions[i] for i in others if i != j))
    return list(cuts), bytes(trace), tables


def marked_variables(row):
    family, pins = family_and_pins(row)
    edge, _ = host(58)
    start = 1 + sum(family.profile[:family.arm])
    xs = range(start, start + family.profile[family.arm])
    q = start + family.mark_position
    positive = set(v for v in pins if v > 0)
    ys = [v for v in range(1, 58) if v != q and edge(q, v, family.arm) in positive]
    return [edge(x, y, family.arm) for x in xs if x != q for y in ys]
