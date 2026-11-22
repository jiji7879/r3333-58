"""Cayley colouring machinery: groups, exact encoding, exact checking.

A *Cayley k-colouring of K_n over a group G of order n* is a map c : G\\{e} -> {1..k}
with c(d) = c(d^-1) (undirected edges) such that every triangle of K_n is
non-monochromatic.  Because the colouring is translation invariant, colour(x,y)
depends only on y - x, every triangle is a translate of (0, a, a+b) with
a, b, a+b != 0, and the three edges of that triangle carry differences
a, b, -(a+b).  So the constraints are

    for all a,b != 0 with a+b != 0 and all colours i:
        not ( c(cls a) = c(cls b) = c(cls(a+b)) = i )

where cls(x) = {x, x^-1}.

Group interface: a group of order n is represented by its full multiplication
table `mul` (n x n ints, row-major list) with identity element 0.
"""
import itertools


# ---------------------------------------------------------------- groups
class Group:
    def __init__(self, n, mul, name):
        self.n = n
        self.mul = mul          # mul[a][b] = a*b
        self.name = name

    def inv(self, a):
        for b in range(self.n):
            if self.mul[a][b] == 0:
                return b
        raise ValueError

    def __repr__(self):
        return f"Group({self.name}, order {self.n})"


def _tab(n, f, name):
    return Group(n, [[f(a, b) for b in range(n)] for a in range(n)], name)


def cyclic(n, name=None):
    return _tab(n, lambda a, b: (a + b) % n, name or f"Z_{n}")


def direct_product(g1, g2, name=None):
    n1, n2 = g1.n, g2.n
    n = n1 * n2
    def f(x, y):
        a1, a2 = divmod(x, n2)
        b1, b2 = divmod(y, n2)
        return g1.mul[a1][b1] * n2 + g2.mul[a2][b2]
    return _tab(n, f, name or f"{g1.name}x{g2.name}")


def dihedral(m, name=None):
    """D_m of order 2m, elements (i, eps) -> i*2+eps, mul (i,e)(j,h) = (i+(-1)^e j, e+h)."""
    n = 2 * m
    def f(x, y):
        i, e = divmod(x, 2)
        j, h = divmod(y, 2)
        ii = (i + (j if e == 0 else -j)) % m
        return ii * 2 + ((e + h) % 2)
    return _tab(n, f, name or f"D_{m}")


def semidirect(m, k, phi, name=None):
    """Z_m x| Z_k, phi[j] = unit mod m giving the action of the j-th generator power."""
    n = m * k
    def f(x, y):
        i, j = divmod(x, k)
        i2, j2 = divmod(y, k)
        return ((i + phi[j] * i2) % m) * k + ((j + j2) % k)
    return _tab(n, f, name or f"Z_{m}:Z_{k}")


def multiplication_by(a, m):
    return (lambda j: pow(a, j, m))


# ------------------------------------------------------- exact encoding
def inverse_classes(g):
    """Partition G\\{0} into {d, d^-1} classes; return (classes, cls_of_element)."""
    seen = [False] * g.n
    classes = []
    cls_of = [None] * g.n
    for d in range(1, g.n):
        if seen[d]:
            continue
        e = g.inv(d)
        members = sorted({d, e})
        for x in members:
            seen[x] = True
            cls_of[x] = len(classes)
        classes.append(members)
    return classes, cls_of


def triangle_constraints(g):
    """Return the set of class-multisets {cls a, cls b, cls(a+b)} over all triangles.

    A multiset of length 3 with a repeated entry means the corresponding clause has
    a repeated literal (so it is a binary/unit constraint after dedup).
    """
    classes, cls_of = inverse_classes(g)
    seen = set()
    for a in range(1, g.n):
        for b in range(1, g.n):
            ab = g.mul[a][b]
            if ab == 0:
                continue
            t = tuple(sorted((cls_of[a], cls_of[b], cls_of[ab])))
            seen.add(t)
    return classes, sorted(seen)


def cnf(g, k, profile=None, comment="", extra_fn=None):
    """DIMACS text for the Cayley k-colouring instance; returns (text, meta).

    profile: None, or a list of k target colour *degrees* (element counts).  This is
    the W2 profile when profile = [15,14,14,14] at order 58.
    """
    import card
    classes, tris = triangle_constraints(g)
    nc = len(classes)
    def var(i, c):                  # i = class index (0..nc-1), c = colour (0..k-1)
        return i * k + c + 1
    clauses = []
    for i in range(nc):
        clauses.append([var(i, c) for c in range(k)])                 # at least one
        for c1, c2 in itertools.combinations(range(k), 2):            # at most one
            clauses.append([-var(i, c1), -var(i, c2)])
    for t in tris:
        for c in range(k):
            cl = sorted({-var(i, c) for i in t})
            clauses.append(cl)
    top = nc * k
    if profile is not None:
        assert len(profile) == k
        for c in range(k):
            lw = [(var(i, c), len(classes[i])) for i in range(nc)]
            cl, top = card.weighted_equals(lw, profile[c], top)
            clauses.extend(cl)
    if extra_fn is not None:
        cl, top = extra_fn(top)
        clauses.extend(cl)
    head = f"p cnf {top} {len(clauses)}\n"
    body = "".join(" ".join(map(str, cl)) + " 0\n" for cl in clauses)
    meta = dict(name=g.name, n=g.n, k=k, classes=classes,
                n_classes=nc, n_triples=len(tris), n_clauses=len(clauses),
                n_vars=top, profile=profile, comment=comment)
    return head + body, meta


# ------------------------------------------------------- exact checking
def check_colouring(g, colour, k):
    """colour: dict class-index -> colour.  Verify exhaustively on all C(n,3) triangles.

    Returns (ok, n_triangles_checked, first_violation or None).
    """
    classes, cls_of = inverse_classes(g)
    # difference colour
    dcol = [None] * g.n
    for d in range(1, g.n):
        dcol[d] = colour[cls_of[d]]
    bad = None
    ntri = 0
    for x, y, z in itertools.combinations(range(g.n), 3):
        ntri += 1
        # y-x, z-y, x-z
        c1 = dcol[g.mul[g.inv(x)][y]]
        c2 = dcol[g.mul[g.inv(y)][z]]
        c3 = dcol[g.mul[g.inv(z)][x]]
        if c1 == c2 == c3:
            bad = (x, y, z, c1)
            break
    return (bad is None), ntri, bad


def model_to_colour(g, k, trueset):
    classes, _ = inverse_classes(g)
    colour = {}
    for i in range(len(classes)):
        got = [c for c in range(k) if (i * k + c + 1) in trueset]
        if len(got) != 1:
            raise ValueError(f"class {i} has colours {got}")
        colour[i] = got[0]
    return colour


# ------------------------------------------------------- group catalogue
def factorise(n):
    f, d = [], 2
    while d * d <= n:
        while n % d == 0:
            f.append(d)
            n //= d
        d += 1
    if n > 1:
        f.append(n)
    return f


def _partitions(m):
    """All partitions of the integer m as sorted-descending tuples."""
    if m == 0:
        return [()]
    out = []
    for first in range(m, 0, -1):
        for rest in _partitions(m - first):
            if not rest or rest[0] <= first:
                out.append((first,) + rest)
    return out


def abelian_groups(n):
    """Every abelian group of order n, as (cyclic-of-prime-power) direct products."""
    primes = {}
    for p in factorise(n):
        primes[p] = primes.get(p, 0) + 1
    keys = sorted(primes)
    choices = [_partitions(primes[p]) for p in keys]
    out = []
    for combo in itertools.product(*choices):
        factors = []                       # list of orders of cyclic factors
        for p, part in zip(keys, combo):
            factors.extend(p ** e for e in part)
        g = cyclic(factors[0])
        for f in factors[1:]:
            g = direct_product(g, cyclic(f))
        import math
        pairwise = all(math.gcd(x, y) == 1
                       for i, x in enumerate(factors) for y in factors[i + 1:])
        if pairwise:
            g.name = f"Z_{n}"
        else:
            g.name = "Z_" + "xZ_".join(str(f) for f in sorted(factors, reverse=True))
        out.append(g)
    # dedupe (identical tables)
    uniq, seen = [], set()
    for g in out:
        key = tuple(tuple(r) for r in g.mul)
        if key not in seen:
            seen.add(key)
            uniq.append(g)
    return uniq


def groups_of_order(n):
    """All groups of order n this file decides, plus a completeness flag.

    complete=True  <=>  the list is every group of order n (up to isomorphism):
        n = 53 prime; n = 51, 55, 57 (p*q, p nmid q-1); n = 58 = 2*29 (cyclic and
        dihedral only, p odd prime); n = 5, 7, 17 prime; n = 6 (=2*3).
    Otherwise the list is every abelian group plus the dihedral group (n even).
    """
    out = list(abelian_groups(n))
    complete = False
    if n == 58:
        out.append(dihedral(29))
        complete = True
    elif n in (51, 53, 55, 57):
        complete = True
    elif n == 6:
        out = [cyclic(6), dihedral(3)]
        complete = True
    elif n in (5, 7, 17):
        out = [cyclic(n)]
        complete = True
    elif n % 2 == 0 and n >= 6:
        out.append(dihedral(n // 2))
    uniq, seen = [], set()
    for g in out:
        key = tuple(tuple(r) for r in g.mul)
        if key not in seen:
            seen.add(key)
            uniq.append(g)
    return uniq, complete
