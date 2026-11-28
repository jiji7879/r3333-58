"""Generic FKR-style attachment census: marked colourings and two-seed overlaps.

The machinery is the exact two-layer decomposition used in overlaps_strong.py:

  layer 1 (strong, colour-preserving) classes of
      * marked colourings (seed, marked subset S),
      * overlap objects (two seed copies glued along S);
  layer 2 the S_3 action permuting the three seed colours, applied to the whole
      object, which produces exactly the weak (colour-permutation) classes.

Works for any triangle-free 3-coloured seed: order 16 (U, T), order 15
(U^-, T^-), which are the CAT58 template families at K58.

Every emitted class comes with a transport witness: a whole-seed automorphism
(or weak automorphism) mapping the concrete object onto the retained
canonical representative.  Witnesses are re-verified independently.
"""
import itertools
import json

IDENT3 = (0, 1, 2)
S3 = list(itertools.permutations(range(3)))


def mask_image(bit_table, m):
    out = 0
    x = m
    while x:
        low = x & -x
        out |= bit_table[low.bit_length() - 1]
        x ^= low
    return out


def permutation_inverse(p):
    inv = [0] * len(p)
    for i, q in enumerate(p):
        inv[q] = i
    return tuple(inv)


def compose(p, q):
    """p after q."""
    return tuple(p[q[i]] for i in range(len(p)))


def group_generators(elements, n):
    if not elements:
        return []
    ident = tuple(range(n))
    gens, closure = [], {ident}
    for g in elements:
        if g in closure:
            continue
        gens.append(g)
        closure, frontier = {ident}, [ident]
        while frontier:
            nxt = []
            for x in frontier:
                for h in gens:
                    y = compose(x, h)
                    if y not in closure:
                        closure.add(y)
                        nxt.append(y)
            frontier = nxt
    return gens


def weak_group(col):
    """[(vertex perm, colour perm)] with pi(col[u][v]) == col[phi u][phi v]."""
    n = len(col)

    def isos(relabelled):
        d1 = [tuple(sum(1 for v in range(n) if u != v and relabelled[u][v] == c)
                     for c in range(3)) for u in range(n)]
        d2 = [tuple(sum(1 for v in range(n) if u != v and col[u][v] == c)
                     for c in range(3)) for u in range(n)]
        if sorted(d1) != sorted(d2):
            return []
        cand = [[v for v in range(n) if d2[v] == d1[u]] for u in range(n)]
        out = []

        def rec(assign, used):
            if len(assign) == n:
                out.append(tuple(assign[i] for i in range(n)))
                return
            best, bestc = None, None
            for u in range(n):
                if u in assign:
                    continue
                cs = [v for v in cand[u] if v not in used and
                      all(relabelled[u][w] == col[v][assign[w]] for w in assign)]
                if bestc is None or len(cs) < len(bestc):
                    best, bestc = u, cs
                    if not cs:
                        break
            if not bestc:
                return
            for v in bestc:
                assign[best] = v
                used.add(v)
                rec(assign, used)
                used.discard(v)
                del assign[best]

        rec({}, set())
        return out

    out = []
    for pi in S3:
        rel = tuple(tuple(pi[col[u][v]] for v in range(n)) for u in range(n))
        for phi in isos(rel):
            out.append((phi, pi))
    return out


class Seed:
    """One triangle-free 3-coloured template with its symmetry data."""

    def __init__(self, name, col):
        self.name = name
        self.col = tuple(tuple(r) for r in col)
        self.n = len(self.col)
        self.weak = weak_group(self.col)
        self.aut = sorted(phi for phi, pi in self.weak if pi == IDENT3)
        self.allbit = {phi: tuple(1 << phi[i] for i in range(self.n))
                       for phi, _ in self.weak}
        self.aut_gens = group_generators(self.aut, self.n)
        self.gbit = [self.allbit[g] for g in self.aut_gens]
        self.pis = {}
        for phi, pi in self.weak:
            self.pis.setdefault(pi, []).append(phi)
        self.strong = self._strong_classes_with_witness()

    def _strong_classes_with_witness(self):
        """Strong (Aut_named) classes of nonempty subsets, with transport witnesses.

        witness[S] is a vertex permutation g of the seed with g(S) = class rep, and
        check_witnesses() re-verifies both that g preserves the named colouring and
        that it really maps S onto the stored representative.
        """
        n = self.n
        seen = bytearray(1 << n)
        self.witness = {}
        self.rep_of = {}
        out = {}
        for mask in range(1, 1 << n):
            if seen[mask]:
                continue
            g_of = {mask: tuple(range(n))}
            frontier = [mask]
            while frontier:
                m = frontier.pop()
                g = g_of[m]
                for gen in self.aut_gens:
                    mm = mask_image(self.allbit[gen], m)
                    if mm not in g_of:
                        g_of[mm] = compose(gen, g)
                        frontier.append(mm)
            rep = min(g_of)
            g_rep = g_of[rep]                       # g_rep(mask) = rep
            for mm, g_m in g_of.items():
                seen[mm] = 1
                # g_rep after inverse(g_m): maps mm to rep
                self.witness[mm] = compose(g_rep, permutation_inverse(g_m))
                self.rep_of[mm] = rep
            pos = tuple(i for i in range(n) if rep >> i & 1)
            idx = {v: i for i, v in enumerate(pos)}
            stab = [phi for phi in self.aut if all(phi[a] in idx for a in pos)]
            posperms = [tuple(idx[phi[a]] for a in pos) for phi in stab]
            out.setdefault(len(pos), []).append({
                "mask": rep, "pos": pos, "posperms": posperms,
                "gens": group_generators(posperms, len(pos)) if posperms else [],
            })
        return out

    def check_witnesses(self):
        """Re-verify every transport witness: a seed automorphism carrying S onto rep."""
        failures = []
        for mask, g in self.witness.items():
            ok = all(self.col[u][v] == self.col[g[u]][g[v]]
                     for u in range(self.n) for v in range(u + 1, self.n))
            if not ok:
                failures.append(("not_automorphism", mask))
                continue
            if mask_image(self.allbit[g], mask) != self.rep_of[mask]:
                failures.append(("wrong_image", mask))
        return failures

    def reps(self):
        return {c["mask"] for k in self.strong for c in self.strong[k]}


def induced(col, pos):
    return tuple(tuple(col[u][v] for v in pos) for u in pos)


def named_isos(s1, s2):
    k = len(s1)
    if k == 0:
        return [()]
    d1 = [tuple(sum(1 for v in range(k) if u != v and s1[u][v] == c) for c in range(3))
          for u in range(k)]
    d2 = [tuple(sum(1 for v in range(k) if u != v and s2[u][v] == c) for c in range(3))
          for u in range(k)]
    if sorted(d1) != sorted(d2):
        return []
    cand = [[v for v in range(k) if d2[v] == d1[u]] for u in range(k)]
    out = []

    def rec(assign, used):
        if len(assign) == k:
            out.append(tuple(assign[i] for i in range(k)))
            return
        best, bestc = None, None
        for u in range(k):
            if u in assign:
                continue
            cs = [v for v in cand[u] if v not in used and
                  all(s1[u][w] == s2[v][assign[w]] for w in assign)]
            if bestc is None or len(cs) < len(bestc):
                best, bestc = u, cs
                if not cs:
                    break
        for v in bestc:
            assign[best] = v
            used.add(v)
            rec(assign, used)
            used.discard(v)
            del assign[best]

    rec({}, set())
    return out


def orbit_min(theta0, pa_gens, pb_gens, k):
    """Minimum of the orbit of theta0 under the linking action (no membership test)."""
    idk = tuple(range(k))
    moves = [(pa, pb) for pa in pa_gens + [idk] for pb in pb_gens + [idk]]
    seen = {theta0}
    frontier = [theta0]
    best = theta0
    while frontier:
        th = frontier.pop()
        for pa, pb in moves:
            nt = compose(compose(pb, th), permutation_inverse(pa))
            if nt not in seen:
                seen.add(nt)
                frontier.append(nt)
                if nt < best:
                    best = nt
    return best


def theta_orbits(thetas, pa_gens, pb_gens, k):
    thetas = set(thetas)
    idk = tuple(range(k))
    moves = [(pa, pb) for pa in pa_gens + [idk] for pb in pb_gens + [idk]]
    seen, reps = set(), []
    for th0 in sorted(thetas):
        if th0 in seen:
            continue
        seen.add(th0)
        orbit = [th0]
        frontier = [th0]
        while frontier:
            th = frontier.pop()
            for pa, pb in moves:
                nt = compose(compose(pb, th), permutation_inverse(pa))
                assert nt in thetas
                if nt not in seen:
                    seen.add(nt)
                    orbit.append(nt)
                    frontier.append(nt)
        reps.append(min(orbit))
    return reps


def overlap_census(sa, sb, same_seed):
    """Weak overlap classes for the family (sa,sb); same_seed allows copy swap."""
    ind = {(s.name, c["mask"]): induced(s.col, c["pos"])
           for s in (sa, sb) for k in s.strong for c in s.strong[k]}

    def stabiliser_data(seed, mask):
        """Position-permutation generators of Stab_Aut(mask) on the sorted positions."""
        pos = tuple(v for v in range(seed.n) if mask >> v & 1)
        idx = {v: i for i, v in enumerate(pos)}
        perms = []
        for g in seed.aut:
            if all(g[a] in idx for a in pos):
                perms.append(tuple(idx[g[a]] for a in pos))
        return pos, perms, group_generators(perms, len(pos)) if perms else []

    def transport(seed, mask, target):
        """Position perm A -> target induced by the first automorphism carrying mask to target."""
        pos = tuple(v for v in range(seed.n) if mask >> v & 1)
        for g in seed.aut:
            if mask_image(seed.allbit[g], mask) == target:
                pos2 = tuple(sorted(g[v] for v in pos))
                idx2 = {v: i for i, v in enumerate(pos2)}
                return tuple(idx2[g[v]] for v in pos)
        raise AssertionError("target must be the minimal image")

    def canon_oriented(fa, fb, A, B, theta):
        """Canonical key of a triple in the given orientation of the two copies.

        Fix one transport of A to its minimal image and one of B, push theta
        through, then minimise over the stabiliser orbit at the canonical
        representatives.  The result does not depend on the transports chosen
        because a different transport changes theta by an element of that orbit.
        """
        k = len(theta)
        best_A = min(mask_image(fa.allbit[g], A) for g in fa.aut)
        best_B = min(mask_image(fb.allbit[g], B) for g in fb.aut)
        p1 = transport(fa, A, best_A)
        p2 = transport(fb, B, best_B)
        inv1 = permutation_inverse(p1)
        theta0 = tuple(p2[theta[inv1[t]]] for t in range(k))
        _, _, gensA = stabiliser_data(fa, best_A)
        _, _, gensB = stabiliser_data(fb, best_B)
        best = orbit_min(theta0, gensA, gensB, k)
        return (best_A, best_B, best)

    def canon(fa, fb, A, B, theta):
        first = canon_oriented(fa, fb, A, B, theta)
        if not same_seed:
            return (first,)
        second = canon_oriented(fb, fa, B, A, permutation_inverse(theta))
        return tuple(min(first, second))

    # Every (class pair, theta) triple is a labelled strong object; the canonical
    # key below is invariant under the residual group (and under the copy swap
    # when the two copies come from the same seed), so distinct keys are exactly
    # the strong isomorphism classes of overlaps.
    keys = {}
    pairs = linked = 0
    for k in range(1, min(sa.n, sb.n) + 1):
        items_a, items_b = sa.strong.get(k, []), sb.strong.get(k, [])
        for ai in range(len(items_a)):
            ca = items_a[ai]
            for bi in range(ai if same_seed else 0, len(items_b)):
                cb = items_b[bi]
                pairs += 1
                thetas = named_isos(ind[sa.name, ca["mask"]], ind[sb.name, cb["mask"]])
                if not thetas:
                    continue
                linked += 1
                for th in thetas:
                    key = canon(sa, sb, ca["mask"], cb["mask"], th)
                    if key not in keys:
                        keys[key] = (k, sa.name, ca["mask"], sb.name, cb["mask"], th)
    assert len(set(keys)) == len(keys)

    def sigma_image(key, sigma):
        k, na, A, nb, B, theta = keys[key]
        phi1 = sa.pis[sigma][0]
        phi2 = sb.pis[sigma][0]
        posA = tuple(v for v in range(sa.n) if A >> v & 1)
        posB = tuple(v for v in range(sb.n) if B >> v & 1)
        A2 = mask_image(sa.allbit[phi1], A)
        B2 = mask_image(sb.allbit[phi2], B)
        idxA2 = {v: n for n, v in enumerate(sorted(phi1[v] for v in posA))}
        idxB2 = {v: n for n, v in enumerate(sorted(phi2[v] for v in posB))}
        perm1 = tuple(idxA2[phi1[v]] for v in posA)
        perm2 = tuple(idxB2[phi2[v]] for v in posB)
        inv1 = permutation_inverse(perm1)
        newth = tuple(perm2[theta[inv1[t]]] for t in range(k))
        return canon(sa, sb, A2, B2, newth)

    parent = {key: key for key in keys}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for key in keys:
        for sigma in S3:
            if sigma not in sa.pis or sigma not in sb.pis:
                continue
            img = sigma_image(key, sigma)
            assert img in keys
            ra, rb = find(key), find(img)
            if ra != rb:
                parent[rb] = ra
    weak = {}
    roots = set()
    for key in keys:
        r = find(key)
        if r in roots:
            continue
        roots.add(r)
        weak[keys[key][0]] = weak.get(keys[key][0], 0) + 1
    strong_per_order = {}
    for key in keys:
        strong_per_order[keys[key][0]] = strong_per_order.get(keys[key][0], 0) + 1
    return {"keys": keys, "weak": weak, "strong_per_order": strong_per_order,
            "pairs": pairs, "linked": linked,
            "strong_total": len(keys), "weak_total": sum(weak.values())}


def marked_census(seed):
    """Weak classes of marked colourings (seed, S != empty) plus per-order counts."""
    counts = {k: len(v) for k, v in seed.strong.items()}
    keys = {}
    for k in seed.strong:
        for c in seed.strong[k]:
            keys[c["mask"]] = k
    # S_3 action on strong subset classes; images are re-canonicalised under
    # Aut_named, which is exactly how a strong class is represented.
    def canon_mask(m):
        return min(mask_image(seed.allbit[g], m) for g in seed.aut)

    parent = {m: m for m in keys}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for m in keys:
        for sigma in S3:
            if sigma not in seed.pis:
                continue
            m2 = canon_mask(mask_image(seed.allbit[seed.pis[sigma][0]], m))
            ra, rb = find(m), find(m2)
            if ra != rb:
                parent[rb] = ra
    weak = {}
    roots = set()
    for m in keys:
        r = find(m)
        if r in roots:
            continue
        roots.add(r)
        weak[keys[m]] = weak.get(keys[m], 0) + 1
    return {"strong": counts, "weak": weak, "weak_total": sum(weak.values())}
