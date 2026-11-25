"""Independent encoder for the single-template (H42) outsider-support instances.

Model, written from the description in work/k54cut/README.md ("A sharper bound on
four-point supports"):

  * vertices 0..13 are the H42 template of one K54 side, edges fixed by H42
    with the three ordinary colours 0,1,2;
  * every further vertex is an outsider carrying a *prescribed c-support* S:
    its spoke to a template position lies in {c} if the position is in S and in
    {0,1,2} otherwise (c = 3, the fourth colour);
  * a spoke between two outsiders takes any of the four colours;
  * exactly one colour per spoke;
  * no monochromatic triangle on any triple meeting an outsider.  For a triple
    with two template vertices the template colour is forced, for a triple with
    one template vertex and two, or all three, outsiders every colour in the
    common domain gives a clause.

Variable numbering is the canonical one: pairs (a,b), a<b, in lexicographic
order, skipping pure-template pairs, colours in increasing order.
"""
import hashlib
import itertools
import json
from pathlib import Path

C = 3  # the fourth colour


def load_h42(path):
    return json.loads(Path(path).read_text())


def build(supports, H, free=False):
    """Return (nvars, clauses) for the template H plus one outsider per support.

    free=False: the support is prescribed exactly (the c-spokes are forced to c).
    free=True:  the support is only an upper bound -- the c-spokes may be c or
                ordinary, which is the "c-support contained in the set" reading
                used for the occupancy/tightness bound.
    """
    t = len(H)                      # 14
    n = t + len(supports)
    var = {}
    nv = 0
    for a in range(n):
        for b in range(a + 1, n):
            if b < t:
                continue
            if a >= t:
                dom = (0, 1, 2, 3)
            elif not supports[b - t] >> a & 1:
                dom = (0, 1, 2)
            elif free:
                dom = (0, 1, 2, 3)
            else:
                dom = (C,)
            var[a, b] = {}
            for c in dom:
                nv += 1
                var[a, b][c] = nv
    clauses = []
    for (a, b), d in var.items():
        clauses.append(sorted(d.values()))                     # at least one
        for u, v in itertools.combinations(sorted(d.values()), 2):
            clauses.append([-u, -v])                           # at most one
    for a, b, d in itertools.combinations(range(n), 3):
        if d < t:                                              # template only
            continue
        if b < t:
            col = H[a][b]
            if col in var[a, d] and col in var[b, d]:
                clauses.append([-var[a, d][col], -var[b, d][col]])
        else:
            for col in (var[a, b].keys() & var[a, d].keys() & var[b, d].keys()):
                clauses.append([-var[a, b][col], -var[a, d][col], -var[b, d][col]])
    return nv, clauses


def supports_for(pole, masks, t=14):
    """The masks plus the 13 singleton witnesses at every non-pole position."""
    return list(masks) + [1 << j for j in range(t) if j != pole]


def to_dimacs(nv, clauses):
    return ("p cnf %d %d\n" % (nv, len(clauses))
            + "".join(" ".join(map(str, cl)) + " 0\n" for cl in clauses)).encode()


def cnf(pole, masks, H):
    nv, clauses = build(supports_for(pole, masks), H)
    return nv, clauses, to_dimacs(nv, clauses)


def sha(b):
    return hashlib.sha256(b).hexdigest()


# --- exact-k support mode -----------------------------------------------------
# "Outsider i has exactly k c-neighbours on the template, freely chosen."  This
# turns the whole four-point packing bound into a single instance per pole
# instead of an enumeration over mask sets: 13 singleton witnesses plus r
# outsiders with exactly four c-neighbours.

def at_most_k(lits, k, nv, clauses):
    """Sinz sequential counter: at most k of `lits` are true.  Returns new nv."""
    n = len(lits)
    if k >= n:
        return nv
    if k == 0:
        for l in lits:
            clauses.append([-l])
        return nv
    s = []
    for i in range(n):
        row = []
        for j in range(k):
            nv += 1
            row.append(nv)
        s.append(row)
    # if lit i then s[i][0]
    clauses.append([-lits[0], s[0][0]])
    for j in range(1, k):
        clauses.append([-s[0][j]])
    for i in range(1, n):
        clauses.append([-lits[i], s[i][0]])
        clauses.append([-s[i - 1][0], s[i][0]])
        for j in range(1, k):
            clauses.append([-lits[i], -s[i - 1][j - 1], s[i][j]])
            clauses.append([-s[i - 1][j], s[i][j]])
        clauses.append([-lits[i], -s[i - 1][k - 1]])
    return nv


def build_exact_k(spec, H, want_map=False):
    """Template H plus one outsider per entry of `spec`; entry (A, k) means the
    outsider has exactly k c-neighbours inside its allowed set A, freely chosen."""
    allowed = [A for A, _ in spec]
    t = len(H)
    n = t + len(allowed)
    var = {}
    nv = 0
    for a in range(n):
        for b in range(a + 1, n):
            if b < t:
                continue
            if a >= t:
                dom = (0, 1, 2, 3)
            elif not allowed[b - t] >> a & 1:
                dom = (0, 1, 2)
            else:
                dom = (0, 1, 2, 3)
            var[a, b] = {}
            for c in dom:
                nv += 1
                var[a, b][c] = nv
    clauses = []
    for (a, b), d in var.items():
        clauses.append(sorted(d.values()))
        for u, v in itertools.combinations(sorted(d.values()), 2):
            clauses.append([-u, -v])
    for a, b, d in itertools.combinations(range(n), 3):
        if d < t:
            continue
        if b < t:
            col = H[a][b]
            if col in var[a, d] and col in var[b, d]:
                clauses.append([-var[a, d][col], -var[b, d][col]])
        else:
            for col in (var[a, b].keys() & var[a, d].keys() & var[b, d].keys()):
                clauses.append([-var[a, b][col], -var[a, d][col], -var[b, d][col]])
    # exactly k c-spokes per outsider
    for i, (A, k) in enumerate(spec):
        b = t + i
        lits = [var[a, b][C] for a in range(t) if (A >> a & 1) and C in var[a, b]]
        nv = at_most_k(lits, k, nv, clauses)
        nv = at_most_k([-x for x in lits], len(lits) - k, nv, clauses)
    if want_map:
        return nv, clauses, var
    return nv, clauses
