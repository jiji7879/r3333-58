#!/usr/bin/env python3
"""arm.py -- classification of triangle-free 3-edge-colourings of K_n.

A 14-point arm of the (15,14,14,14) branch is a colour-1 independent 14-set, so
its internal edges are coloured with the three remaining colours under the rule
"no monochromatic triangle".  This script enumerates those colourings.

Pipeline (each step sound, none restrictive):
  1. geng: the colour-0 graph of such a colouring is triangle-free with
     colour-0 degrees in [n-1-10, 5]  (d_c <= 5 for all c, by R(3,3)=6).
  2. filter.c: alpha(G_0) <= 5, because a 6-set independent in colour 0 carries
     a triangle-free 2-colouring of K_6, which R(3,3)=6 forbids.
  3. here: all 2-colourings of the complement with no monochromatic triangle
     and colour-1/colour-2 degrees <= 5; then quotient by vertex permutations
     (and, separately, by the colour-2 <-> colour-3 swap).
"""
import sys, os, json, subprocess, itertools
from collections import defaultdict

DC = {1: 0, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 1,
      8: 0, 9: 2, 10: 0, 11: 1, 12: 0, 13: 1, 14: 2, 15: 0}
TRADE = {21, 22, 28, 31, 37, 38, 44, 47, 88, 91, 104, 107, 140, 143, 188, 191}
SWAP = {0: 0, 1: 2, 2: 1}


def template_matrix(n, twisted):
    """The Lean `K58.template n twisted` as a colour matrix (-1 on the diagonal)."""
    m = [[-1] * n for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            c = DC[u ^ v]
            if twisted and (16 * min(u, v) + max(u, v)) in TRADE:
                c = SWAP[c]
            m[u][v] = m[v][u] = c
    return m


# ---------------------------------------------------------------- graph6 ----
def parse_g6(s):
    n = ord(s[0]) - 63
    bits = []
    for ch in s[1:]:
        b = ord(ch) - 63
        for k in range(5, -1, -1):
            bits.append((b >> k) & 1)
    adj = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    return n, adj


def to_g6(adj):
    n = len(adj)
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append((adj[i] >> j) & 1)
    while len(bits) % 6:
        bits.append(0)
    out = [chr(n + 63)]
    for k in range(0, len(bits), 6):
        b = 0
        for t in range(6):
            b = (b << 1) | bits[k + t]
        out.append(chr(b + 63))
    return ''.join(out)


# ------------------------------------------------------------ enumeration ----
def enum_two_colourings(n, adj0, cap=5, node_cap=4_000_000):
    """All colourings of the complement of adj0 with colours 1,2, triangle-free,
    colour-degree <= cap.  Returns a list of matrices (colour 0 = adj0)."""
    edges = [(i, j) for i in range(n) for j in range(i + 1, n)
             if not (adj0[i] >> j) & 1]
    eidx = {e: k for k, e in enumerate(edges)}
    tris = []
    for a in range(n):
        for b in range(a + 1, n):
            if (adj0[a] >> b) & 1:
                continue
            for c in range(b + 1, n):
                if not (adj0[a] >> c) & 1 and not (adj0[b] >> c) & 1:
                    tris.append((a, b, c))
    edge_tris = defaultdict(list)
    for (a, b, c) in tris:
        edge_tris[(a, b)].append(((a, c), (b, c)))
        edge_tris[(a, c)].append(((a, b), (b, c)))
        edge_tris[(b, c)].append(((a, b), (a, c)))
    # most constrained edges first
    order = sorted(range(len(edges)), key=lambda k: -len(edge_tris[edges[k]]))
    val = [-1] * len(edges)
    deg = [[0] * n for _ in range(3)]   # deg[c][v]
    out = []
    nodes = [0]

    def dfs(pos):
        nodes[0] += 1
        if nodes[0] > node_cap:
            raise RuntimeError('node cap')
        if pos == len(order):
            m = [[0] * n for _ in range(n)]
            for i in range(n):
                m[i][i] = -1
            for i in range(n):
                for j in range(i + 1, n):
                    if (adj0[i] >> j) & 1:
                        m[i][j] = m[j][i] = 0
            for k, e in enumerate(edges):
                m[e[0]][e[1]] = m[e[1]][e[0]] = val[k]
            out.append(m)
            return
        k = order[pos]
        x, y = edges[k]
        for col in (1, 2):
            if deg[col][x] >= cap or deg[col][y] >= cap:
                continue
            ok = True
            for (e1, e2) in edge_tris[edges[k]]:
                k1, k2 = eidx[e1], eidx[e2]
                if val[k1] == col and val[k2] == col:
                    ok = False
                    break
            if not ok:
                continue
            val[k] = col
            deg[col][x] += 1
            deg[col][y] += 1
            dfs(pos + 1)
            deg[col][x] -= 1
            deg[col][y] -= 1
            val[k] = -1

    dfs(0)
    return out


# ---------------------------------------------------------- canonical form ----
def _refine(cells, mat, n):
    while True:
        changed = False
        new = []
        for cell in cells:
            if len(cell) <= 1:
                new.append(cell)
                continue
            buckets = {}
            for v in cell:
                sig = []
                for C in cells:
                    cnt = [0, 0, 0]
                    for u in C:
                        if u != v:
                            cnt[mat[v][u]] += 1
                    sig.append(tuple(cnt))
                buckets.setdefault(tuple(sig), []).append(v)
            if len(buckets) > 1:
                changed = True
                for s in sorted(buckets):
                    new.append(buckets[s])
            else:
                new.append(cell)
        cells = new
        if not changed:
            return cells


def canon_form(n, mat):
    """Canonical certificate of a colour matrix (vertex permutations only)."""
    cells = _refine([[v for v in range(n)]], mat, n)
    best = [None]

    def rec(cells):
        for i, c in enumerate(cells):
            if len(c) > 1:
                for v in c:
                    rest = [u for u in c if u != v]
                    nc = _refine(cells[:i] + [[v], rest] + cells[i + 1:], mat, n)
                    rec(nc)
                return
        order = [c[0] for c in cells]
        cert = tuple(tuple(mat[order[i]][order[j]] for j in range(n))
                     for i in range(n))
        if best[0] is None or cert < best[0]:
            best[0] = cert

    rec(cells)
    return best[0]


def invariant(n, mat):
    """Cheap invariant for bucketing before the exact canonical form."""
    prof = sorted(tuple(sum(1 for j in range(n) if mat[i][j] == c)
                        for c in range(3)) for i in range(n))
    tri = [0, 0, 0]
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                if mat[a][b] == mat[a][c] == mat[b][c]:
                    tri[mat[a][b]] += 1
    return (tuple(prof), tuple(tri))


def verify(n, mat):
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                if mat[a][b] == mat[a][c] == mat[b][c]:
                    return 'mono triangle %s' % ((a, b, c),)
    for i in range(n):
        for c in range(3):
            if sum(1 for j in range(n) if mat[i][j] == c) > 5:
                return 'degree > 5'
    return None


# ------------------------------------------------------------------ driver ----
def gen_candidates(n, workdir='.'):
    """Run geng + filter to get the sound candidate list of colour-0 graphs."""
    lo = max(0, n - 1 - 10)
    hi = min(5, n - 1)
    g6 = os.path.join(workdir, 'cand%d.g6' % n)
    if not os.path.exists(g6) or os.path.getsize(g6) == 0:
        geng = ('nauty-geng -t %s-D%d %d 2>/dev/null'
                % (('-d%d ' % lo) if lo > 0 else '', hi, n))
        flt = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'filter')
        with open(g6, 'w') as fh:
            p1 = subprocess.Popen(geng, shell=True, stdout=subprocess.PIPE)
            p2 = subprocess.Popen([flt], stdin=p1.stdout, stdout=fh)
            p1.stdout.close()
            p2.communicate()
    with open(g6) as fh:
        return [l.strip() for l in fh if l.strip() and not l.startswith('>')]


def classify(n, workdir='.', verbose=True):
    cands = gen_candidates(n, workdir)
    if verbose:
        print('n=%d: %d candidate colour-0 graphs' % (n, len(cands)), flush=True)
    classes = {}      # canonical form (vertex perms only) -> representative matrix
    per_graph = []
    bad = 0
    for gi, line in enumerate(cands):
        nn, adj0 = parse_g6(line)
        assert nn == n
        try:
            sols = enum_two_colourings(n, adj0)
        except RuntimeError:
            per_graph.append((line, 'NODECAP'))
            bad += 1
            continue
        per_graph.append((line, len(sols)))
        for m in sols:
            err = verify(n, m)
            if err:
                raise SystemExit('ENUMERATION ERROR: %s' % err)
            cf = canon_form(n, m)
            if cf not in classes:
                classes[cf] = m
        if verbose and (gi + 1) % 500 == 0:
            print('  %d/%d graphs, %d classes so far'
                  % (gi + 1, len(cands), len(classes)), flush=True)
    return classes, per_graph, bad


def orb_swap_colours(n, mat):
    return [[(-1 if mat[i][j] < 0 else SWAP[mat[i][j]]) for j in range(n)]
            for i in range(n)]


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'classify':
        n = int(sys.argv[2])
        workdir = sys.argv[3] if len(sys.argv) > 3 else '.'
        classes, per_graph, bad = classify(n, workdir)
        out = os.path.join(workdir, 'classes%d.json' % n)
        with open(out, 'w') as fh:
            json.dump({'n': n, 'count': len(classes), 'bad': bad,
                       'reps': list(classes.values())}, fh)
        print('n=%d: %d classes (vertex perms), %d graphs hit the node cap, -> %s'
              % (n, len(classes), bad, out))
    elif cmd == 'template':
        n = int(sys.argv[2])
        for t in (False, True):
            m = template_matrix(n, t)
            print('n=%d twisted=%s verify=%s' % (n, t, verify(n, m)))
