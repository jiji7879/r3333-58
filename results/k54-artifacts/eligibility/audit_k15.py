"""m3 / direction d8 -- independent check of the K15-completeness claim.

README: "The code verifies completeness of the two K15 templates by testing all
ordinary one-vertex extensions of the 115 K14 rows and finding an explicit
isomorphism to a K15 class for every completion."  results/global.json records
k15_extensions = {class 0: 2, class 1: 4}.

This script, from data/r333_14.mc and data/r333_15.mc only:
  1. decodes both catalogues and checks each is a 3-colouring of a complete
     graph with no monochromatic triangle;
  2. enumerates every ordinary one-vertex extension of every K14 row (a spoke
     colouring of the new vertex with no monochromatic triangle);
  3. tests each resulting K15 for isomorphism, up to colour permutation, with
     each of the 2 catalogue K15 classes and tallies the hits;
  4. cross-checks the count against results/global.json;
  5. reports, for every K15 class, which catalogue rows its 15 vertex deletions
     are (a consistency check on the 115-row catalogue).
"""
import argparse
import json
import sys
from itertools import permutations


def decode(line):
    n = ord(line[0]) - 63
    m = [[-1] * n for _ in range(n)]
    for k, (a, b) in enumerate((a, b) for b in range(n) for a in range(b)):
        m[a][b] = m[b][a] = ((ord(line[2 + k // 3]) - 63) >> (4 - 2 * (k % 3)) & 3) - 1
    return m


def well_formed(m):
    n = len(m)
    for u in range(n):
        for v in range(u + 1, n):
            if m[u][v] not in (0, 1, 2):
                return False
            if m[u][v] == m[v][u]:
                pass
    for u in range(n):
        for v in range(u + 1, n):
            for w in range(v + 1, n):
                if m[u][v] == m[u][w] == m[v][w]:
                    return False
    return True


def embeds(a, b):
    """a and b are 3-coloured complete graphs of the same order; is a
    isomorphic to b up to a permutation of the three colours?"""
    n = len(a)
    assert len(b) == n
    deg_a = [tuple(row.count(c) for c in range(3)) for row in a]
    deg_b = [tuple(row.count(c) for c in range(3)) for row in b]
    for p in permutations(range(3)):
        pinv = [0, 0, 0]
        for c in range(3):
            pinv[p[c]] = c
        opts = [[j for j in range(n) if deg_b[j] == tuple(deg_a[i][pinv[c]] for c in range(3))]
                for i in range(n)]
        order = sorted(range(n), key=lambda i: (len(opts[i]), i))
        img = {}
        used = set()

        def rec(k):
            if k == n:
                return True
            i = order[k]
            for j in opts[i]:
                if j in used:
                    continue
                if all(b[j][img[i2]] == p[a[i][i2]] for i2 in img):
                    img[i] = j
                    used.add(j)
                    if rec(k + 1):
                        return True
                    used.remove(j)
                    del img[i]
            return False

        if rec(0):
            return p
    return None


def extensions(M):
    """All spoke colourings of a new vertex adjacent to every vertex of M with
    no monochromatic triangle.  Backtracking in vertex order."""
    n = len(M)
    word = []

    def rec():
        i = len(word)
        if i == n:
            yield tuple(word)
            return
        for c in range(3):
            if any(word[j] == c and M[i][j] == c for j in range(i)):
                continue
            word.append(c)
            yield from rec()
            word.pop()

    yield from rec()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--archive', default=(
        '/workspace/nucleus/work/projects/'
        'p-764e12eeb9f34762ad544edb924f4680/repo/work/k54cut'))
    args = ap.parse_args()
    K = args.archive.rstrip('/') + '/'
    cat14 = [decode(s) for s in open(K + 'data/r333_14.mc').read().splitlines()]
    cat15 = [decode(s) for s in open(K + 'data/r333_15.mc').read().splitlines()]
    print('catalogue sizes:', len(cat14), len(cat15))
    for tag, cat in (('K14', cat14), ('K15', cat15)):
        for i, m in enumerate(cat):
            if not well_formed(m):
                print('FAIL: %s row %d is not a triangle-free 3-colouring' % (tag, i + 1))
                return 1
    # the catalogues must be pairwise non-isomorphic up to colour permutation
    for tag, cat in (('K14', cat14), ('K15', cat15)):
        for i in range(len(cat)):
            for j in range(i + 1, len(cat)):
                if embeds(cat[i], cat[j]) is not None:
                    print('FAIL: %s rows %d and %d are isomorphic' % (tag, i + 1, j + 1))
                    return 1
    print('each catalogue: complete, triangle-free, pairwise non-isomorphic '
          '(up to colour permutation)')

    tally = [0] * len(cat15)
    per_row = {}
    total = 0
    for r, M in enumerate(cat14):
        n_ext = 0
        for w in extensions(M):
            n_ext += 1
            total += 1
            G = [row + [w[i]] for i, row in enumerate(M)]
            G.append(list(w) + [-1])
            assert well_formed(G)
            hit = None
            for j, t in enumerate(cat15):
                if embeds(G, t) is not None:
                    hit = j
                    break
            if hit is None:
                print('FAIL: extension of K14 row %d is not isomorphic to either '
                      'K15 class; spokes %s' % (r + 1, w))
                return 1
            tally[hit] += 1
        if n_ext:
            per_row[r + 1] = n_ext
    print('one-vertex extensions found:', total, 'rows that extend:', per_row)
    print('per K15 class:', tally)
    stored = json.load(open(K + 'results/global.json'))['k15_extensions']
    stored = {int(k): v for k, v in stored.items()}
    print('stored k15_extensions:', stored)
    ok = (stored == {i: tally[i] for i in range(len(cat15))})
    if not ok:
        print('FAIL: extension tally differs from results/global.json')
    # which catalogue rows are the vertex deletions of the K15 classes?
    where = {}
    for j, t in enumerate(cat15):
        for v in range(15):
            sub = [[t[a][b] for b in range(15) if b != v] for a in range(15) if a != v]
            found = [i + 1 for i, M in enumerate(cat14) if embeds(sub, M) is not None]
            where.setdefault((j, v), found)
    hits = sum(1 for v in where.values() if v)
    print('K15 vertex deletions found in the K14 catalogue:', hits, 'of', len(where))
    missing = [(j, v) for (j, v), f in where.items() if not f]
    if missing:
        print('  (deletions not in the catalogue:', len(missing),
              'e.g.', missing[:5], ')')
    json.dump(dict(total=total, tally=tally, per_row=per_row,
                   stored=stored, ok=bool(ok)),
              open('k15_extensions.json', 'w'), indent=1)
    print('RESULT:', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
