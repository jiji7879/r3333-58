#!/usr/bin/env python3
"""Bounded direct check of the quartic-residue template on F_49.

The model is F_7[i]/(i^2+1), not a solver instance.  It tests whether the
four multiplicative cosets of <g^4>, coloured additively on differences,
already contain monochromatic triangles on K_49.
"""
from itertools import combinations
import json

P = 7
ZERO = (0, 0)
ONE = (1, 0)


def add(x, y):
    return ((x[0] + y[0]) % P, (x[1] + y[1]) % P)


def neg(x):
    return ((-x[0]) % P, (-x[1]) % P)


def sub(x, y):
    return add(x, neg(y))


def mul(x, y):
    return ((x[0] * y[0] - x[1] * y[1]) % P,
            (x[0] * y[1] + x[1] * y[0]) % P)


def power(x, n):
    out = ONE
    while n:
        if n & 1:
            out = mul(out, x)
        x = mul(x, x)
        n >>= 1
    return out


elements = [(a, b) for a in range(P) for b in range(P)]
nonzero = [x for x in elements if x != ZERO]
primitive = next(x for x in nonzero
                 if power(x, 48) == ONE and power(x, 24) != ONE and power(x, 16) != ONE)
log = {}
x = ONE
for k in range(48):
    assert x not in log
    log[x] = k
    x = mul(x, primitive)
assert len(log) == 48 and x == ONE
assert log[neg(ONE)] % 4 == 0  # all four colours are undirected

def colour(x, y):
    return log[sub(x, y)] % 4

counts = [0, 0, 0, 0]
first = None
for a, b, c in combinations(elements, 3):
    ab, ac, bc = colour(a, b), colour(a, c), colour(b, c)
    if ab == ac == bc:
        counts[ab] += 1
        if first is None:
            first = [list(a), list(b), list(c), ab]
summary = {
    "field": "F_7[i]/(i^2+1)",
    "primitive_element": list(primitive),
    "primitive_power_24": list(power(primitive, 24)),
    "primitive_power_16": list(power(primitive, 16)),
    "minus_one_log_mod_4": log[neg(ONE)] % 4,
    "class_sizes": [sum(v % 4 == c for v in log.values()) for c in range(4)],
    "monochromatic_triangles_by_colour": counts,
    "first_monochromatic_triangle": first,
    "seed_is_good": sum(counts) == 0,
}
print(json.dumps(summary, indent=2))
