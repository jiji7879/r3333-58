"""The kernel-checked per-(u,y) rigidity, translated to a Cayley colouring.

`K58.model_pair_rigidity` (lean/K58/Model.lean, kernel-checked):
  G triangle-free, u a vertex, c a colour, |N_c(u)| >= 15, y in N_c(u), f != c
  ==>  4 <= |N_f(y) cap N_c(u)| <= 5,  and  = 5 if |N_c(u)| = 16.

At a transitive vertex with the W2 profile, |N_0(u)| = |S_0| = 15 for every u, so with
u = the identity and y = w in S_0 the statement reads

  for every w with colour(w) = 0 and every f in {1,2,3}:
      4 <= #{s : colour(s) = f and colour(w+s) = 0} <= 5.

The set identity  |N_f(w) cap N_0(e)| = #{s in S_f : w + s in S_0}  is pure group theory;
`check_translation` verifies it computationally on random colourings, so the only input
taken from the kernel is the 4..5 bound itself.
"""
import random

import card


def inverse_classes(g):
    seen = [False] * g.n
    classes, cls_of = [], [None] * g.n
    for d in range(1, g.n):
        if seen[d]:
            continue
        e = g.inv(d)
        for x in {d, e}:
            seen[x] = True
            cls_of[x] = len(classes)
        classes.append(sorted({d, e}))
    return classes, cls_of


def diff_colour(g, colour, cls_of):
    return {d: colour[cls_of[d]] for d in range(1, g.n)}


def counts_from_definitions(g, colour, cls_of, w, f):
    """|N_f(w) cap N_0(e)| from the edge colouring, no Cayley shortcut."""
    dc = diff_colour(g, colour, cls_of)
    def col(x, y):
        if x == y:
            return None
        return dc.get(g.mul[g.inv(x)][y])
    N0e = {v for v in range(g.n) if v != 0 and col(0, v) == 0}
    Nfw = {v for v in range(g.n) if v != w and col(w, v) == f}
    return len(Nfw & N0e)


def counts_from_differences(g, colour, cls_of, w, f):
    """#{s : colour(s) = f and colour(w+s) = 0}."""
    dc = diff_colour(g, colour, cls_of)
    tot = 0
    for s in range(1, g.n):
        ws = g.mul[w][s]
        if ws == 0:
            continue
        if dc[s] == f and dc.get(ws) == 0:
            tot += 1
    return tot


def check_translation(g, k, trials=3, seed=0):
    """On random colourings the two counts must agree for every w and f."""
    rng = random.Random(seed)
    classes, cls_of = inverse_classes(g)
    for _ in range(trials):
        colour = {i: rng.randrange(k) for i in range(len(classes))}
        for w in range(1, g.n):
            for f in range(k):
                a = counts_from_definitions(g, colour, cls_of, w, f)
                b = counts_from_differences(g, colour, cls_of, w, f)
                assert a == b, (g.name, w, f, a, b)
    return True


def rigidity_clauses(g, k, top, guard_colour=0, lo=4, hi=5):
    """Clauses for: colour(w) = guard_colour => lo <= count_f(w) <= hi, all f != guard.

    `top` is the highest variable index already in use.  Returns (clauses, new_top).
    """
    classes, cls_of = inverse_classes(g)
    nc = len(classes)
    def colour_lit(i, c):
        return i * k + c + 1
    clauses = []
    for w in range(1, g.n):
        guard = colour_lit(cls_of[w], guard_colour)
        for f in range(k):
            if f == guard_colour:
                continue
            lits = []
            for s in range(1, g.n):
                ws = g.mul[w][s]
                if ws == 0:
                    continue
                top += 1
                a = top
                cs = colour_lit(cls_of[s], f)
                cw = colour_lit(cls_of[ws], guard_colour)
                clauses.append([-a, cs])
                clauses.append([-a, cw])
                clauses.append([a, -cs, -cw])
                lits.append(a)
            sub = []
            r = card.seq_counter_atmost(sub, lits, hi, top)
            if r is not None:
                top = r[0]
            r = card.seq_counter_atmost(sub, [-x for x in lits], len(lits) - lo, top)
            if r is not None:
                top = r[0]
            for cl in sub:                      # vacuous unless colour(w) = guard
                clauses.append(cl + [-guard])
    return clauses, top
