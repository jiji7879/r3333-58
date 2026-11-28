#!/usr/bin/env python3
"""Entrance cut: hypothesis-exact CNF projection of the certified
"no 16-vertex-brace entrance" theorem at a (16,16,13,12) root of K58.

Source theorem (swarm smwwdcyxb, member m2; results/entrance-brace-audit-2026-11-26):
for a triangle-free 4-colouring of K58 with a vertex r whose colour classes are
R0,R1,R2,R3 of sizes (16,16,13,12) and whose two 16-classes carry the critical
templates in the pairs (T,T) and (U,T), every point p of the small class named in
a COMPLETE family satisfies

    d_c(p) <= 15,  c = col(r,p),  i.e.  |{x outside R_c, x != r : col(p,x)=c}| <= 14.

Complete families after the erratum (results/verdict-correction-smwwdcyxb-m2.md):

    TT:2  600/600  -> pair (T,T), p in the 13-class
    UT:3  600/600  -> pair (U,T), the ledger's TU rows, p in the 12-class
    TT:3 443/600, UT:2 596/600, UU:2 591/600, UU:3 0/600 -> NOT covered

Geometry (ENTRANCE.md sec.1; independent of the solver campaign):
for p in R_c and i != c, every two points of S_i = N_c(p) cap R_i are joined by a
colour outside {c,i}: colour c closes a c-triangle through p, colour i one
through r.  So S_i carries a 2-colouring with no monochromatic triangle, hence
|S_i| <= 5 by R(3,3)=6, and S_i is empty for i = c.  Therefore
d_c(p) = 1 + sum_{i != c} |S_i| <= 16, with equality iff all three supports have
size 5 (the "(5,5,5) shape" refuted by the campaign).

Cut emitted here: three at-most-5 cardinality constraints |S_i| <= 5 plus one
ternary "not all three counters reach 5".  No hypothesis beyond the pinned root
data is used: no markedness, charge, reciprocity or balance.

Usage:
    entcap.py build PARENT.cnf OUT.cnf [--caps-only|--direct|--direct16]
    entcap.py check PARENT.cnf AUGMENTED.cnf [--caps-only|--direct]

Modes: full (default) = per-class caps + ternary; caps-only = drop the ternary;
direct = a single at-most-14 counter over the 44/45 point literals, i.e. exactly
d_c(p) <= 15 with no reliance on the familyA caps.
"""
import hashlib
import json
import os
import sys
import tempfile

ORDER = 58
PROFILE = (16, 16, 13, 12)

DIFFERENCE_COLORS = (0, 0, 1, 1, 2, 2, 2, 1, 0, 2, 0, 1, 0, 1, 2, 0)
TRADE = {21, 22, 28, 31, 37, 38, 44, 47, 88, 91, 104, 107, 140, 143, 188, 191}

CERTIFIED = {
    (('T', 'T'), 2): ('TT:2:5,5,5', 600, 600),
    (('U', 'T'), 3): ('UT:3:5,5,5', 600, 600),
    (('T', 'U'), 3): ('UT:3:5,5,5', 600, 600),
    (('T', 'T'), 3): ('TT:3:5,5,5', 443, 600),
    (('U', 'T'), 2): ('UT:2:5,5,5', 596, 600),
    (('T', 'U'), 2): ('UT:2:5,5,5', 596, 600),
    (('U', 'U'), 2): ('UU:2:5,5,5', 591, 600),
    (('U', 'U'), 3): ('UU:3:5,5,5', 0, 600),
}

EDGES = {}
_i = 0
for _x in range(ORDER):
    for _y in range(_x + 1, ORDER):
        EDGES[_x, _y] = 4 * _i + 1
        _i += 1

GROUPS = []
_start = 1
for _s in PROFILE:
    GROUPS.append(tuple(range(_start, _start + _s)))
    _start += _s


def lit(x, y, c):
    return EDGES[min(x, y), max(x, y)] + c


def split_lit(l):
    idx, col = (abs(l) - 1) // 4, (abs(l) - 1) % 4
    u = 0
    while True:
        width = ORDER - u - 1
        if idx < width:
            return u, u + 1 + idx, col
        idx -= width
        u += 1


def template(size, kind):
    def colour(u, v):
        rule = DIFFERENCE_COLORS[u ^ v]
        if kind == 'T' and 16 * min(u, v) + max(u, v) in TRADE:
            return (0, 2, 1)[rule]
        return rule
    return tuple(tuple(colour(u, v) for v in range(size)) for u in range(size))


def named_template(size, kind, forbidden):
    palette = tuple(c for c in range(4) if c != forbidden)
    return tuple(tuple(palette[c] for c in row) for row in template(size, kind))


def parse_cnf(path):
    with open(path, 'rb') as f:
        header = f.readline().split()
        assert header[0] == b'p' and header[1] == b'cnf', header
        nv, nc = int(header[2]), int(header[3])
        body = []
        for line in f:
            t = line.split()
            if t:
                body.append([int(x) for x in t[:-1]])
    assert len(body) == nc, (len(body), nc)
    return nv, nc, body


def header_of(path):
    with open(path, 'rb') as f:
        h = f.readline().split()
    return int(h[2]), int(h[3])


def raw_body(path):
    with open(path, 'rb') as f:
        f.readline()
        return f.read()


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 22), b''):
            h.update(block)
    return h.hexdigest()


class RootError(Exception):
    pass


def root_data(clauses):
    units = set()
    for cl in clauses:
        if len(cl) == 1 and cl[0] > 0:
            units.add(cl[0])
    groups, assigned = {}, {}
    for x in range(1, ORDER):
        hits = [c for c in range(4) if lit(0, x, c) in units]
        if len(hits) != 1:
            raise RootError('vertex %d has %d pinned root colours' % (x, len(hits)))
        groups.setdefault(hits[0], []).append(x)
        assigned[x] = hits[0]
    sizes = tuple(len(groups.get(c, ())) for c in range(4))
    if sizes != PROFILE:
        raise RootError('root class sizes %r != %r' % (sizes, PROFILE))
    kinds = {}
    for c in (0, 1):
        blk = groups[c]
        want = {}
        for i, u in enumerate(blk):
            for v in blk[i + 1:]:
                hits = [d for d in range(4) if lit(u, v, d) in units]
                if len(hits) != 1:
                    raise RootError('edge (%d,%d) in R%d not uniquely pinned'
                                    % (u, v, c))
                want[u, v] = hits[0]
        found = [k for k in ('U', 'T')
                 if all(want[blk[i], blk[j]] == named_template(16, k, c)[i][j]
                        for i in range(16) for j in range(i + 1, 16))]
        if len(found) != 1:
            raise RootError('R%d template is %r, expected exactly one of U,T'
                            % (c, found))
        kinds[c] = found[0]
    return groups, (kinds[0], kinds[1]), units


def coverage(kinds):
    out = {}
    for c in (2, 3):
        key = (kinds, c)
        if key in CERTIFIED:
            fam, done, total = CERTIFIED[key]
            out[c] = (fam, done == total, '%d/%d certified cases' % (done, total))
        else:
            out[c] = (None, False, 'no family enumerated for this kind pair')
    return out


def atmost_seq(lits, k, top):
    """Sinz sequential counter for at most k of lits.
    Returns (clauses, top, full); full is true exactly when at least k are true
    (None when k >= len(lits))."""
    n = len(lits)
    if k < 0:
        return [[]], top, None
    if k >= n:
        return [], top, None
    if k == 0:
        return [[-l] for l in lits], top, None
    s = {}
    for i in range(1, n + 1):
        for j in range(1, k + 1):
            top += 1
            s[i, j] = top
    cl = [[-lits[0], s[1, 1]]]
    for i in range(2, n + 1):
        cl.append([-lits[i - 1], s[i, 1]])
        for j in range(2, k + 1):
            cl.append([-lits[i - 1], -s[i - 1, j - 1], s[i, j]])
    for i in range(2, n + 1):
        for j in range(1, k + 1):
            cl.append([-s[i - 1, j], s[i, j]])
    for i in range(1, n):
        cl.append([-s[i, k], -lits[i]])
    return cl, top, s[n, k]


def entrance_constraints(clauses):
    groups, kinds, units = root_data(clauses)
    cov = coverage(kinds)
    by_vertex = {}
    for c in range(4):
        for x in groups.get(c, ()):
            by_vertex[x] = c
    points = {}
    for c in (2, 3):
        fam, ok, note = cov[c]
        if not ok:
            continue
        for p in groups[c]:
            supports = {i: [lit(p, y, c) for y in groups[i]]
                        for i in range(4) if i != c}
            points[p] = (c, fam, supports)
    return {'groups': groups, 'kinds': kinds, 'units': units,
            'coverage': cov, 'points': points, 'class_of': by_vertex}


def build(src, dst, mode='full'):
    nv, nc, clauses = parse_cnf(src)
    data = entrance_constraints(clauses)
    top = nv
    added, ternaries = [], []
    if mode in ('direct', 'direct16'):
        # 'direct'   = the theorem:  d_c(p) = 1 + count <= 15  (count <= 14)
        # 'direct16' = size-matched redundant control: count <= 15, i.e. d <= 16,
        #              which the familyA caps already imply.  Same clause shape
        #              and size, no new content.
        bound = 14 if mode == 'direct' else 15
        for p in sorted(data['points']):
            c, fam, supports = data['points'][p]
            lits = [l for i in sorted(supports) for l in supports[i]]
            cs, top, _ = atmost_seq(lits, bound, top)
            added.extend(cs)
        ternaries = []
    else:
        do_caps, do_tern = {'full': (True, True),
                            'caps-only': (True, False)}[mode]
        for p in sorted(data['points']):
            c, fam, supports = data['points'][p]
            fulls = []
            for i in sorted(supports):
                cs, top, full = atmost_seq(supports[i], 5, top)
                added.extend(cs)
                fulls.append(full)
            if do_tern and all(f is not None for f in fulls):
                ternaries.append([-f for f in fulls])
    added.extend(ternaries)
    blob = ('p cnf %d %d\n' % (top, nc + len(added))).encode() + raw_body(src) + \
        b''.join((' '.join(map(str, cl)) + ' 0\n').encode() for cl in added)
    with open(dst, 'wb') as f:
        f.write(blob)
    return {'parent': str(src), 'out': str(dst), 'parent_clauses': nc,
            'parent_vars': nv, 'clauses': nc + len(added), 'variables': top,
            'added': len(added), 'ternaries': len(ternaries), 'mode': mode,
            'kinds': ''.join(data['kinds']), 'points': len(data['points']),
            'coverage': {str(c): list(v) for c, v in data['coverage'].items()},
            'sha256': hashlib.sha256(blob).hexdigest()}


def check(parent, augmented, mode='full'):
    fd, tmp = tempfile.mkstemp(suffix='.cnf')
    os.close(fd)
    try:
        meta = build(parent, tmp, mode)
        got = open(tmp, 'rb').read()
    finally:
        os.unlink(tmp)
    return meta, got == open(augmented, 'rb').read()


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    cmd, mode, rest = argv[1], 'full', []
    for a in argv[2:]:
        if a.startswith('--'):
            mode = a[2:]
        else:
            rest.append(a)
    if cmd == 'build':
        print(json.dumps(build(rest[0], rest[1], mode), indent=1))
    elif cmd == 'check':
        meta, same = check(rest[0], rest[1], mode)
        print('mode=%s clauses=%d vars=%d points=%d ternaries=%d identical=%s'
              % (mode, meta['clauses'], meta['variables'], meta['points'],
                 meta['ternaries'], same))
        return 0 if same else 1
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
