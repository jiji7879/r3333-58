"""m3 / direction d8 -- independent check of the 48,880 three-point bounds.

README: "The small-set enumeration also verifies 48,880 bounds on 104 catalogue
rows: every subset of at most three points is tight, including the empty subset."

A subset P of a template is tight when at most |P| outsiders can have their
whole c-support inside P.  For |P| <= 3 this is decided exactly here: an
outsider whose c-support lies in P is described by a *word*, one colour in
{0,1,2,3} per template vertex, with 3 (the crossing colour c) allowed only on P,
colour classes independent in the corresponding colour graphs (one clause per
monochromatic triangle through the outsider), and a family of outsiders is
realisable when their mutual edges can be coloured so that no triangle on three
of them is monochromatic.  Two words are compatible on the mutual edge with
colour k only when no template vertex carries colour k in both words.

For every one of the 104 admissible catalogue rows and every subset P of size at
most three the script searches for a family of |P|+1 compatible words.  Finding
one refutes tightness of P; the count of (row, P) pairs is asserted to be
48,880, and the empty mask is reported separately.
"""
import argparse
import json
import sys
import time
from itertools import combinations

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from audit_k15 import decode

REGULAR_EXCLUDED = {17, 19, 20, 22, 23, 24, 25, 40, 69, 70, 77}


def adjmasks(M):
    return [tuple([sum(1 << u for u in range(14) if u != v and M[v][u] == c)
                   for c in range(3)] + [0]) for v in range(14)]


def words(adj, P):
    out = []
    w = [0, 0, 0, 0]

    def rec(i):
        if i == 14:
            out.append(tuple(w))
            return
        for c in range(4):
            if c == 3 and not (P >> i & 1):
                continue
            if w[c] & adj[i][c]:
                continue
            w[c] ^= 1 << i
            rec(i + 1)
            w[c] ^= 1 << i

    rec(0)
    return out


def has_clique(ws, target, node_cap=2_000_000):
    """Necessary condition for a realisable family: `target` words that are
    pairwise compatible.  Bitset backtracking with an early exit."""
    n = len(ws)
    if target == 0:
        return True, 0
    if target > n:
        return False, 0
    compat = [0] * n
    for i in range(n):
        a = ws[i]
        m = 0
        for j in range(n):
            if i == j:
                continue
            b = ws[j]
            # compatible when at least one of the four colours is unshared
            if not (a[0] & b[0] and a[1] & b[1] and a[2] & b[2] and a[3] & b[3]):
                m |= 1 << j
        compat[i] = m
    nodes = [0]

    def rec(P, size):
        nodes[0] += 1
        if nodes[0] > node_cap:
            raise RuntimeError('cap')
        if size == target:
            return True
        while P:
            if size + bin(P).count('1') < target:
                return False
            v = (P & -P).bit_length() - 1
            P &= ~(1 << v)
            if rec(P & compat[v], size + 1):
                return True
        return False

    try:
        return rec((1 << n) - 1, 0), nodes[0]
    except RuntimeError:
        return None, nodes[0]


def family_exists(ws, target, node_cap=4_000_000):
    """Is there a set of `target` words whose mutual edges can be coloured so
    that no triangle on three of them is monochromatic?  Returns (bool, nodes)."""
    n = len(ws)
    if target == 0:
        return True, 0
    if target > n:
        return False, 0
    opt = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            m = 15
            for c in range(4):
                if ws[i][c] & ws[j][c]:
                    m &= ~(1 << c)
            opt[i][j] = opt[j][i] = m
    chosen = []
    col = {}
    nodes = [0]

    def assign(k, idx):
        if k == len(chosen) - 1:
            return rec(idx + 1)
        u = chosen[k]
        om = opt[u][idx]
        for c in range(4):
            if not (om >> c) & 1:
                continue
            ok = True
            for p in range(k):
                v = chosen[p]
                if col[(v, idx)] == c and col[(v, u)] == c:
                    ok = False
                    break
            if not ok:
                continue
            col[(u, idx)] = c
            if assign(k + 1, idx):
                return True
            del col[(u, idx)]
        return False

    def rec(start):
        nodes[0] += 1
        if nodes[0] > node_cap:
            raise RuntimeError('node cap')
        if len(chosen) == target:
            return True
        need = target - len(chosen)
        for idx in range(start, n):
            if n - idx < need:
                return False
            if any(opt[c][idx] == 0 for c in chosen):
                continue
            chosen.append(idx)
            if assign(0, idx):
                return True
            chosen.pop()
        return False

    try:
        res = rec(0)
    except RuntimeError:
        return None, nodes[0]
    return res, nodes[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--archive', default=(
        '/workspace/nucleus/work/projects/'
        'p-764e12eeb9f34762ad544edb924f4680/repo/work/k54cut'))
    ap.add_argument('--json', default='cap_bounds.json')
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()
    K = args.archive.rstrip('/') + '/'
    cat14 = [decode(s) for s in open(K + 'data/r333_14.mc').read().splitlines()]
    regular = sorted(set(range(1, 116)) - REGULAR_EXCLUDED)
    if args.limit:
        regular = regular[:args.limit]
    masks = [0]
    for k in range(1, 4):
        masks += [sum(1 << v for v in c) for c in combinations(range(14), k)]
    print('pairs to test:', len(regular), 'x', len(masks), '=', len(regular) * len(masks))
    assert len(regular) * len(masks) == 48880 or args.limit

    violations = []
    undecided = []
    tested = 0
    worstnodes = 0
    t0 = time.time()
    per_row = {}
    for r in regular:
        adj = adjmasks(cat14[r - 1])
        worst = 0
        for P in masks:
            tested += 1
            ws = words(adj, P)
            k = P.bit_count()
            if not ws:
                continue
            cl, cnodes = has_clique(ws, k + 1)
            worstnodes = max(worstnodes, cnodes)
            if cl is False:
                worst = max(worst, len(ws))
                continue
            res, nodes = family_exists(ws, k + 1)
            worstnodes = max(worstnodes, nodes)
            if res is None:
                undecided.append((r, P, len(ws), nodes))
                print('UNDECIDED (node cap) row %d mask %d words %d' % (r, P, len(ws)),
                      flush=True)
            elif res:
                violations.append((r, P, len(ws)))
                print('VIOLATION row %d mask %d (%d bits): %d words admit a family of %d'
                      % (r, P, k, len(ws), k + 1), flush=True)
            worst = max(worst, len(ws))
        per_row[r] = worst
        if r % 10 == 0:
            print('  rows done up to', r, '%.1fs' % (time.time() - t0), flush=True)
    print('tested:', tested, 'violations:', len(violations), 'undecided:', len(undecided),
          'max search nodes:', worstnodes, 'time %.1fs' % (time.time() - t0))
    json.dump(dict(tested=tested, violations=violations, undecided=undecided,
                   max_nodes=worstnodes, ok=not violations and not undecided),
              open(args.json, 'w'), indent=1)
    return 0 if not violations and not undecided else 1


if __name__ == '__main__':
    sys.exit(main())
