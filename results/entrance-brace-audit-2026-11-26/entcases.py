"""Enumerate the marked-neighbourhood (brace) cases of an entrance, exactly.

An entrance at a (16,16,13,12) root r is a point p of one of the two small
classes with d_c(p) >= 15, c = c(rp).  Writing S = N_c(p), the case is: the
root partition, templates on the two 16-classes, the brace S as a set, and its
full internal colouring.

Coverage.  Up to the symmetries of the configuration we may
  * move p inside its own (template-free) class to a fixed vertex,
  * move the free support S_f, inside the third class, onto fixed vertices in
    its own reference order (the class carries no template),
  * move each foreign support S_i into an orbit representative under the
    automorphism group of the template on R_i, and
  * choose any brace template (U or T, or a deletion for |S| = 15) with r at
    any position and any reference labellings of the supports.
So the cases below are a complete cover provided every foreign support is
moved to a representative of its Aut-orbit and every (template, position,
labelling) triple is listed.  Redundant cases are harmless: they are
deduplicated by their fact set only.
"""
import itertools
import sys

REPO = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo'
sys.path.insert(0, REPO + '/.scratch/k58')
from gluing import host, named_template, template       # noqa: E402
import supports as S                                    # noqa: E402
from orbits import auts, support_sets, orbits           # noqa: E402

ORDER = 58
GROUPS = {0: tuple(range(1, 17)), 1: tuple(range(17, 33)),
          2: tuple(range(33, 46)), 3: tuple(range(46, 58))}


def dihedral(lab):
    """All relabellings of a reference cycle/path order."""
    n = len(lab)
    out = []
    for start in range(n):
        rot = lab[start:] + lab[:start]
        out.append(rot)
        out.append(tuple(reversed(rot)))
    return sorted(set(tuple(x) for x in out))


def case_facts(c_p, p_vertex, labellings, brace_kind, base):
    """Pinned edge literals of one brace case.

    `labellings` maps each actual colour d != c_p to the tuple of actual
    vertices carrying the reference colouring of support d, in reference
    order.  `brace_kind` in {'U','T'} and `base` is the template position of
    the root r.
    """
    lit, _ = host(ORDER)
    pal = sorted(set(range(4)) - {c_p})
    n = 1 + sum(len(v) for v in labellings.values())
    tsize = 16 if n == 16 else 15
    rho = template(tsize, brace_kind)
    cls = {j: [q for q in range(tsize) if q != base and rho[base][q] == j] for j in range(3)}
    if any(len(cls[j]) != len(labellings[pal[j]]) for j in range(3)):
        raise AssertionError('brace class sizes do not match the shape')
    ref = {}
    for j in range(3):
        verts = cls[j]
        two = sorted(set(range(3)) - {j})
        lo = two[0]
        lo_edges = {frozenset((u, v)) for u, v in itertools.combinations(verts, 2)
                    if rho[u][v] == lo}
        order = (S.cycle_order(verts, lo_edges) if len(verts) == 5
                 else (S.path_order(verts, lo_edges) if len(verts) == 4 else None))
        assert order is not None, 'brace class %d has %d vertices, not a cycle/path' % (j, len(verts))
        ref[j] = order
    pos2vert = {base: 0}
    for j in range(3):
        d = pal[j]
        lab = labellings[d]
        assert len(lab) == len(cls[j]), (d, len(lab), len(cls[j]))
        for q, v in zip(ref[j], lab):
            pos2vert[q] = v
    assert len(pos2vert) == tsize, (len(pos2vert), tsize)
    facts = []
    for i in range(tsize):
        for j in range(i + 1, tsize):
            facts.append(lit(pos2vert[i], pos2vert[j], pal[rho[i][j]]))
    brace = set(pos2vert.values())
    for v in brace:
        if v != p_vertex:
            facts.append(lit(p_vertex, v, c_p))
    for y in range(ORDER):
        if y != p_vertex and y not in brace:
            facts.append(-lit(p_vertex, y, c_p))
    return facts, sorted(brace), pal


def base_cnf(kinds, facts):
    lit, base = host(ORDER)
    clauses = [list(c) for c in base]
    for c in (0, 1):
        for x in GROUPS[c]:
            clauses.append([lit(0, x, c)])
        mat = named_template(16, kinds[c], c)
        for i, j in itertools.combinations(range(16), 2):
            clauses.append([lit(GROUPS[c][i], GROUPS[c][j], mat[i][j])])
    for c in (2, 3):
        for x in GROUPS[c]:
            clauses.append([lit(0, x, c)])
    for f in facts:
        clauses.append([f])
    return clauses


def consistent(clauses):
    """No edge pinned twice to different colours, and no edge pinned to a colour
    that contradicts the templates.  (Cheap syntactic check.)"""
    seen = {}
    for c in clauses:
        if len(c) == 1:
            l = c[0]
            idx = (abs(l) - 1) // 4
            col = (abs(l) - 1) % 4
            if idx in seen and seen[idx] != (col if l > 0 else None):
                prev = seen[idx]
                if prev is None or l < 0 or prev != col:
                    if prev is None and l < 0:
                        continue
                    if prev is None and l > 0:
                        seen[idx] = col
                        continue
                    if prev != col and l > 0:
                        return False
            if l > 0:
                seen[idx] = col
    return True


if __name__ == '__main__':
    # shape (5,5,5), p in R2 (the 13-class); supports S_0 in R0, S_1 in R1, free R3
    c_p = 2
    free = tuple(GROUPS[3][:5])
    reps = {}
    for c in (0, 1):
        ent = support_sets(kinds_ := 'T', c, (0, 1, 2))   # placeholder; replaced below
    print('loaded')
